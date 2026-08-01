"""Rate-limited HTTP clients with persistent accountability (GUIDE §4).

`HttpClient` is the shared base: request pacing, a per-client persistent
daily budget (counted from fetch_log.db so restarts can't reset it),
per-attempt logging with secret redaction, Retry-After obedience (integer
and HTTP-date forms), exponential backoff, and honest User-Agent.

`GovinfoClient` adds govinfo specifics: api.data.gov key injection (and
its redaction), API-base URL resolution, nextPage pagination, and the
server-remaining halt floor.

`AgencyClient` (GUIDE §3 agency newsrooms) adds robots.txt enforcement —
robots files are fetched through the client itself (paced, budgeted,
logged), parsed with protego (RFC 9309), 4xx treated as allow and 5xx as
temporary disallow; crawl-delay is honored when longer than our own
pacing. No WAF evasion of any kind.
"""

import datetime as dt
import email.utils
import logging
import sqlite3
import time
from urllib.parse import urlencode, urlsplit

import requests
from protego import Protego

from . import config

logger = logging.getLogger("fapd.client")

# Distinguishes "nothing cached" from a cached "this host has no robots.txt",
# which is a real verdict (RFC 9309: 4xx means allow).
_MISS = object()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS fetch_log (
    id INTEGER PRIMARY KEY,
    ts_utc TEXT NOT NULL,
    url TEXT NOT NULL,
    status INTEGER,
    bytes INTEGER NOT NULL DEFAULT 0,
    elapsed_ms INTEGER,
    attempt INTEGER NOT NULL,
    error TEXT
);
CREATE TABLE IF NOT EXISTS robots_cache (
    host       TEXT PRIMARY KEY,
    body       TEXT,          -- NULL: no robots.txt / 4xx -> allow (RFC 9309)
    fetched_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fetch_log_ts ON fetch_log (ts_utc);
"""


class BudgetExceededError(RuntimeError):
    """The self-imposed daily request budget (GUIDE.md §4) would be exceeded."""


class RateLimitFloorError(RuntimeError):
    """Server-reported remaining quota fell below MIN_SERVER_REMAINING."""


class RobotsDisallowedError(RuntimeError):
    """robots.txt disallows this URL for our user agent (GUIDE §3)."""


class HttpClient:
    """Shared pacing/budget/logging base. Subclasses set CLIENT_NAME and
    may override _daily_budget, _redacted_params, and _post_response."""

    CLIENT_NAME = "http"

    def __init__(self, db_path=None, session=None, sleep=time.sleep,
                 monotonic=time.monotonic, reserve_exempt=False):
        # reserve_exempt: only the end-of-day finalizer sets this, so the
        # reserve it spends is the one the collectors were kept out of.
        self.reserve_exempt = reserve_exempt
        self._db_path = db_path or config.FETCH_LOG_DB
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self._db_path)
        self._db.execute("PRAGMA busy_timeout = 30000")  # one writer per host worker
        self._db.executescript(_SCHEMA)
        self._migrate()
        self._session = session or requests.Session()
        self._sleep = sleep
        self._monotonic = monotonic
        self._last_request_at = None
        self._halt_reason = None

    def _migrate(self):
        # Additive only: historical rows (client IS NULL) belong to govinfo.
        cols = {r[1] for r in self._db.execute("PRAGMA table_info(fetch_log)")}
        if "client" not in cols:
            self._db.execute("ALTER TABLE fetch_log ADD COLUMN client TEXT")
            self._db.commit()

    # -- subclass hooks ------------------------------------------------------

    def _daily_budget(self):
        return config.MAX_REQUESTS_PER_DAY

    def _effective_daily_budget(self):
        """The budget THIS client may spend. Continuous collectors stop
        short of the full daily figure so the end-of-day finalizer always
        has requests left to sync the day it is finalizing; a client
        constructed with reserve_exempt=True (the finalizer) may spend it
        all. Added 2026-07-31 after collectors spent all 2,000 govinfo
        requests on backlog and the finalizer could not run."""
        budget = self._daily_budget()
        if self.reserve_exempt:
            return budget
        return int(budget * (1.0 - config.EOD_BUDGET_RESERVE_FRACTION))

    def _redacted_params(self, params):
        """What the fetch log is allowed to record of a request's query.

        `api_key` is stripped for EVERY client, not just the ones that
        currently send one (GUIDE §4: nothing bypasses logging, and the
        key is never in the log). This lives in the base because the rule
        is about the secret, not about which subclass happens to carry
        it: the agency client began sending an api.data.gov key on
        2026-07-31 for Congress.gov, and a subclass-local redaction would
        have leaked it until someone remembered to override this."""
        return {k: v for k, v in (params or {}).items() if k != "api_key"}

    def _post_response(self, resp):
        """Called on non-retried responses before returning."""

    # -- public API ----------------------------------------------------------

    def get(self, url, params=None, headers=None, min_interval=None):
        """GET an absolute URL. Returns a 2xx/304 Response or raises."""
        if self._halt_reason:
            raise RateLimitFloorError(self._halt_reason)
        qp = dict(params or {})
        shown_url = self._redacted_url(url, qp)
        req_headers = {"User-Agent": config.USER_AGENT}
        if headers:
            req_headers.update(headers)

        for attempt in range(1, config.MAX_ATTEMPTS + 1):
            self._check_daily_budget()
            self._check_hourly_ceiling()
            self._pace(min_interval)
            logger.debug("GET %s (attempt %d/%d)", shown_url, attempt, config.MAX_ATTEMPTS)
            started = self._monotonic()
            try:
                resp = self._session.get(
                    url, params=qp, headers=req_headers, timeout=config.REQUEST_TIMEOUT,
                )
            except requests.RequestException as exc:
                self._log(shown_url, None, 0, None, attempt, error=repr(exc))
                if attempt == config.MAX_ATTEMPTS:
                    logger.error("GET %s failed after %d attempts: %r", shown_url, attempt, exc)
                    raise
                delay = self._backoff(attempt)
                logger.warning("GET %s: %r — backing off %.0fs before retry",
                               shown_url, exc, delay)
                self._sleep(delay)
                continue

            elapsed_ms = int((self._monotonic() - started) * 1000)
            nbytes = len(resp.content or b"")
            self._log(shown_url, resp.status_code, nbytes, elapsed_ms, attempt)
            logger.info(
                "GET %s -> %d (%d B, %d ms) [today/%s: %d/%d]",
                shown_url, resp.status_code, nbytes, elapsed_ms,
                self.CLIENT_NAME, self.requests_today(), self._daily_budget(),
            )

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt == config.MAX_ATTEMPTS:
                    logger.error("GET %s: HTTP %d, out of attempts", shown_url, resp.status_code)
                    resp.raise_for_status()
                delay = self._retry_delay(resp, attempt)
                source = "Retry-After" if "Retry-After" in resp.headers else "backoff"
                logger.warning(
                    "GET %s: HTTP %d — waiting %.0fs (%s) before retry %d/%d",
                    shown_url, resp.status_code, delay, source,
                    attempt + 1, config.MAX_ATTEMPTS,
                )
                self._sleep(delay)
                continue

            self._post_response(resp)
            if resp.status_code == 304:
                return resp  # conditional GET: not-modified is a success
            resp.raise_for_status()
            return resp

        raise RuntimeError("unreachable: retry loop exited without return or raise")

    def requests_today(self):
        (n,) = self._db.execute(
            "SELECT COUNT(*) FROM fetch_log WHERE ts_utc >= ?"
            " AND (client = ? OR (? = 'govinfo' AND client IS NULL))",
            (self._utc_day_start(), self.CLIENT_NAME, self.CLIENT_NAME),
        ).fetchone()
        return n

    def close(self):
        self._db.close()
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # -- internals -----------------------------------------------------------

    @staticmethod
    def _utc_day_start():
        return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT00:00:00")

    def requests_last_hour(self):
        since = (dt.datetime.now(dt.UTC)
                 - dt.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        (n,) = self._db.execute(
            "SELECT COUNT(*) FROM fetch_log WHERE ts_utc >= ?"
            " AND (client = ? OR (? = 'govinfo' AND client IS NULL))",
            (since, self.CLIENT_NAME, self.CLIENT_NAME),
        ).fetchone()
        return n

    def _hourly_ceiling(self):
        """The per-hour ceiling for this class, or None for no ceiling."""

    def _check_hourly_ceiling(self):
        ceiling = self._hourly_ceiling()
        if ceiling is None:
            return
        n = self.requests_last_hour()
        if n >= ceiling:
            logger.error(
                "hourly %s ceiling reached: %d/%d in the last 60 minutes"
                " — refusing", self.CLIENT_NAME, n, ceiling)
            raise BudgetExceededError(
                f"{n} {self.CLIENT_NAME} requests in the last hour; the"
                f" hourly ceiling is {ceiling} per GUIDE.md §4 (half of the"
                " publisher's documented allowance)")

    def _check_daily_budget(self):
        n = self.requests_today()
        if n >= self._effective_daily_budget():
            logger.error(
                "daily %s budget exhausted: %d/%d requests (UTC day)%s — refusing",
                self.CLIENT_NAME, n, self._effective_daily_budget(),
                "" if self.reserve_exempt else " [collector share]",
            )
            raise BudgetExceededError(
                f"{n} {self.CLIENT_NAME} requests already made today (UTC);"
                f" budget is {self._effective_daily_budget()} per GUIDE.md §4"
            )

    def _pace(self, min_interval=None):
        interval = max(min_interval or 0.0, 1.0 / config.MAX_REQUESTS_PER_SECOND)
        if self._last_request_at is not None:
            elapsed = self._monotonic() - self._last_request_at
            if elapsed < interval:
                wait = interval - elapsed
                # long crawl-delay waits are operationally interesting; plain
                # 1 req/s pacing is noise
                logger.log(logging.INFO if wait >= 30 else logging.DEBUG,
                           "pacing: sleeping %.2fs%s", wait,
                           " (host crawl-delay)" if wait >= 30 else "")
                self._sleep(wait)
        self._last_request_at = self._monotonic()

    @staticmethod
    def _backoff(attempt):
        return config.BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))

    def _retry_delay(self, resp, attempt):
        retry_after = (resp.headers.get("Retry-After") or "").strip()
        if retry_after.isdigit():
            return float(retry_after)
        if retry_after:  # HTTP-date form
            try:
                when = email.utils.parsedate_to_datetime(retry_after)
                delta = (when - dt.datetime.now(dt.UTC)).total_seconds()
                if delta > 0:
                    return delta
            except (TypeError, ValueError):
                pass
        return self._backoff(attempt)

    def _redacted_url(self, url, params):
        shown = self._redacted_params(params)
        return url + (f"?{urlencode(shown)}" if shown else "")

    def _log(self, logged_url, status, nbytes, elapsed_ms, attempt, error=None):
        self._db.execute(
            "INSERT INTO fetch_log (ts_utc, url, status, bytes, elapsed_ms,"
            " attempt, error, client) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds"),
                logged_url, status, nbytes, elapsed_ms, attempt, error,
                self.CLIENT_NAME,
            ),
        )
        self._db.commit()


class GovinfoClient(HttpClient):
    CLIENT_NAME = "govinfo"

    def get(self, path, params=None):
        url = path if path.startswith("http") else f"{config.API_BASE}/{path.lstrip('/')}"
        qp = dict(params or {})
        qp["api_key"] = config.api_key()
        return super().get(url, qp)

    def get_json(self, path, params=None):
        return self.get(path, params).json()

    def paginate(self, path, params=None):
        """Yield parsed JSON pages, following the service's nextPage links."""
        params = dict(params or {})
        params.setdefault("offsetMark", "*")
        params.setdefault("pageSize", 100)
        while True:
            page = self.get_json(path, params)
            yield page
            next_url = page.get("nextPage")
            if not next_url:
                return
            from urllib.parse import parse_qsl

            parts = urlsplit(next_url)
            params = dict(parse_qsl(parts.query))
            params.pop("api_key", None)  # get() re-adds it; never trust echoed keys
            path = f"{parts.scheme}://{parts.netloc}{parts.path}"

    def _hourly_ceiling(self):
        return config.MAX_GOVINFO_REQUESTS_PER_HOUR

    def _post_response(self, resp):
        remaining = (resp.headers.get("X-RateLimit-Remaining") or "").strip()
        if remaining.isdigit() and int(remaining) < config.MIN_SERVER_REMAINING:
            self._halt_reason = (
                f"server reports only {remaining} requests remaining (floor:"
                f" {config.MIN_SERVER_REMAINING}); halting — our usage pattern"
                " should never get near the server limit"
            )
            logger.error("HALT: %s", self._halt_reason)


class AgencyClient(HttpClient):
    """Client for agency newsrooms (GUIDE §3): robots-enforced, conditional-
    GET capable, honestly identified. Never evades blocks."""

    CLIENT_NAME = "agency"
    ROBOTS_TTL_SECONDS = 24 * 3600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._robots = {}  # host -> (Protego|None(=allow)|False(=temp disallow), fetched_monotonic)
        self._delay_announced = set()  # hosts whose crawl-delay we've logged

    def _daily_budget(self):
        return config.MAX_AGENCY_REQUESTS_PER_DAY

    def _robots_from_db(self, host):
        """The cached parser, None for a known-absent robots.txt, or
        _MISS when we have nothing fresh enough to use."""
        row = self._db.execute(
            "SELECT body, fetched_at FROM robots_cache WHERE host = ?",
            (host,)).fetchone()
        if not row:
            return _MISS
        body, fetched_at = row
        if (time.time() - fetched_at) >= self.ROBOTS_TTL_SECONDS:
            return _MISS
        if body is None:
            return None
        try:
            return Protego.parse(body)
        except Exception:  # noqa: BLE001 — a corrupt cache re-fetches
            return _MISS

    def _store_robots(self, host, body):
        self._db.execute(
            "INSERT INTO robots_cache (host, body, fetched_at) VALUES (?, ?, ?)"
            " ON CONFLICT (host) DO UPDATE SET body = excluded.body,"
            " fetched_at = excluded.fetched_at",
            (host, body, time.time()))
        self._db.commit()

    def get(self, url, params=None, headers=None):
        verdict, crawl_delay = self._robots_verdict(url)
        if verdict is False:
            self._log(self._redacted_url(url, params), None, 0, None, 1,
                      error="robots disallowed")
            logger.info("robots.txt disallows %s — skipped, not fetched", url)
            raise RobotsDisallowedError(url)
        host = urlsplit(url).netloc
        if crawl_delay and crawl_delay > 1.0 and host not in self._delay_announced:
            self._delay_announced.add(host)
            logger.info("%s robots.txt sets crawl-delay %.0fs — honoring it"
                        " (one request per %.0fs to this host)",
                        host, crawl_delay, crawl_delay)
        return super().get(url, params, headers=headers, min_interval=crawl_delay)

    def _robots_verdict(self, url):
        """(allowed, crawl_delay). Fail-open on 4xx per RFC 9309; fail-closed
        temporarily on 5xx/network errors.

        The cache is persisted (finding F-007). It used to live only on the
        instance, and the collector builds a fresh client every cycle — so
        the 24-hour TTL never survived one poll and every cycle re-asked
        permission it already had. At hourly polling across 22 hosts that
        is 528 robots fetches a day where 22 will do, roughly half of the
        class budget spent on a question already answered."""
        host = urlsplit(url).netloc
        cached = self._robots.get(host)
        if cached and (self._monotonic() - cached[1]) < self.ROBOTS_TTL_SECONDS:
            parser = cached[0]
        else:
            parser = self._robots_from_db(host)
            if parser is _MISS:
                parser, body = self._fetch_robots(host)
                # A temporary disallow (5xx/network) is deliberately not
                # persisted: it is a statement about this moment, not about
                # the host, and outliving the outage would be wrong.
                if parser is not False:
                    self._store_robots(host, body)
            self._robots[host] = (parser, self._monotonic())
        if parser is None:  # no robots.txt / 4xx: allow (RFC 9309)
            return True, None
        if parser is False:  # 5xx/unreachable: temporary disallow-all
            return False, None
        allowed = parser.can_fetch(url, config.USER_AGENT)
        delay = parser.crawl_delay(config.USER_AGENT)
        return allowed, float(delay) if delay else None

    def _fetch_robots(self, host):
        """(verdict, body). body is the text to cache, or None when the
        verdict itself is 'no robots.txt here'."""
        robots_url = f"https://{host}/robots.txt"
        try:
            resp = HttpClient.get(self, robots_url)  # paced, budgeted, logged
        except requests.HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            if status is not None and 400 <= status < 500:
                return None, None  # 4xx: treat as allow-all (RFC 9309)
            return False, None  # 5xx after retries: temporary disallow
        except requests.RequestException:
            return False, None  # network failure: temporary disallow
        if resp.status_code == 304 or not resp.text:
            return None, None
        return Protego.parse(resp.text), resp.text

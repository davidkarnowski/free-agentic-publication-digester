"""Rate-limited govinfo API client.

GUIDE.md §4 enforced as code, not discipline:
- paces requests to MAX_REQUESTS_PER_SECOND
- refuses to exceed MAX_REQUESTS_PER_DAY (counted from a persistent log,
  so restarts can't reset the budget)
- logs every request (API key redacted) for self-audit
- honors Retry-After exactly; exponential backoff on other 5xx
- halts entirely if the server reports our remaining quota below
  MIN_SERVER_REMAINING — that would mean our usage pattern is broken
"""

import datetime as dt
import sqlite3
import time
from urllib.parse import parse_qsl, urlencode, urlsplit

import requests

from . import config

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
CREATE INDEX IF NOT EXISTS idx_fetch_log_ts ON fetch_log (ts_utc);
"""


class BudgetExceededError(RuntimeError):
    """The self-imposed daily request budget (GUIDE.md §4) would be exceeded."""


class RateLimitFloorError(RuntimeError):
    """Server-reported remaining quota fell below MIN_SERVER_REMAINING."""


class GovinfoClient:
    def __init__(self, db_path=None, session=None, sleep=time.sleep, monotonic=time.monotonic):
        self._db_path = db_path or config.FETCH_LOG_DB
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self._db_path)
        self._db.executescript(_SCHEMA)
        self._session = session or requests.Session()
        self._sleep = sleep
        self._monotonic = monotonic
        self._last_request_at = None
        self._halt_reason = None

    # -- public API ----------------------------------------------------------

    def get(self, path, params=None):
        """GET an API path (or absolute URL). Returns a 2xx Response or raises."""
        if self._halt_reason:
            raise RateLimitFloorError(self._halt_reason)

        url = path if path.startswith("http") else f"{config.API_BASE}/{path.lstrip('/')}"
        qp = dict(params or {})
        qp["api_key"] = config.api_key()

        for attempt in range(1, config.MAX_ATTEMPTS + 1):
            self._check_daily_budget()
            self._pace()
            started = self._monotonic()
            try:
                resp = self._session.get(
                    url,
                    params=qp,
                    headers={"User-Agent": config.USER_AGENT},
                    timeout=config.REQUEST_TIMEOUT,
                )
            except requests.RequestException as exc:
                self._log(url, qp, None, 0, None, attempt, error=repr(exc))
                if attempt == config.MAX_ATTEMPTS:
                    raise
                self._sleep(self._backoff(attempt))
                continue

            elapsed_ms = int((self._monotonic() - started) * 1000)
            self._log(url, qp, resp.status_code, len(resp.content or b""), elapsed_ms, attempt)

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt == config.MAX_ATTEMPTS:
                    resp.raise_for_status()
                self._sleep(self._retry_delay(resp, attempt))
                continue

            self._check_server_remaining(resp)
            resp.raise_for_status()
            return resp

        raise RuntimeError("unreachable: retry loop exited without return or raise")

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
            parts = urlsplit(next_url)
            params = dict(parse_qsl(parts.query))
            params.pop("api_key", None)  # get() re-adds it; never trust echoed keys
            path = f"{parts.scheme}://{parts.netloc}{parts.path}"

    def requests_today(self):
        (n,) = self._db.execute(
            "SELECT COUNT(*) FROM fetch_log WHERE ts_utc >= ?", (self._utc_day_start(),)
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

    def _check_daily_budget(self):
        n = self.requests_today()
        if n >= config.MAX_REQUESTS_PER_DAY:
            raise BudgetExceededError(
                f"{n} requests already made today (UTC); daily budget is "
                f"{config.MAX_REQUESTS_PER_DAY} per GUIDE.md §4"
            )

    def _pace(self):
        if self._last_request_at is not None:
            min_interval = 1.0 / config.MAX_REQUESTS_PER_SECOND
            elapsed = self._monotonic() - self._last_request_at
            if elapsed < min_interval:
                self._sleep(min_interval - elapsed)
        self._last_request_at = self._monotonic()

    @staticmethod
    def _backoff(attempt):
        return config.BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))

    def _retry_delay(self, resp, attempt):
        retry_after = resp.headers.get("Retry-After", "")
        if retry_after.strip().isdigit():
            return float(retry_after)
        return self._backoff(attempt)

    def _check_server_remaining(self, resp):
        remaining = resp.headers.get("X-RateLimit-Remaining", "")
        if remaining.strip().isdigit() and int(remaining) < config.MIN_SERVER_REMAINING:
            self._halt_reason = (
                f"server reports only {remaining} requests remaining (floor: "
                f"{config.MIN_SERVER_REMAINING}); halting — our usage pattern "
                "should never get near the server limit"
            )

    def _log(self, url, params, status, nbytes, elapsed_ms, attempt, error=None):
        shown = {k: v for k, v in (params or {}).items() if k != "api_key"}
        logged_url = url + (f"?{urlencode(shown)}" if shown else "")
        self._db.execute(
            "INSERT INTO fetch_log (ts_utc, url, status, bytes, elapsed_ms, attempt, error)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds"),
                logged_url,
                status,
                nbytes,
                elapsed_ms,
                attempt,
                error,
            ),
        )
        self._db.commit()

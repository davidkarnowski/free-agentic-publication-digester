"""Per-source ingestion statistics and health classification (GUIDE §2
completeness accounting; §5 derived-output rules).

What this module reports is **our observation of our own ingestion** —
how many items we recorded from a source, how long they were, when the
last one arrived, and how the source's server answered our requests. It
reports nothing about the publisher. "No response on 12 of 40 requests"
is a fact we recorded; "unreliable agency" is an opinion and is not
computable from anything here, so no label in this module carries one.
Where a number could be read as blame, the caller is expected to render
the mechanical reason alongside it: an HTTP 503 is the server declining
to answer, which may be load, scheduled maintenance, on-demand
generation, or throttling — we cannot tell which from the outside and
do not guess.

Everything is mechanical: SQL over the two databases the pipeline
already keeps, read-only, zero LLM calls (docs/code-standards.md §2
rule 5). Missing databases are not an error — a fresh clone or a CI run
has no `data/`, and the site must still build. In that case
``source_health`` returns a record whose ``available`` is False and
whose ``unavailable_reason`` says which file was missing.
"""

import logging
import sqlite3
import statistics
from pathlib import Path
from urllib.parse import urlsplit

from . import config
from .sync import publication_date, utc_now_iso

logger = logging.getLogger("fapd.health")


# ---------------------------------------------------------------------------
# Thresholds — the whole classification, in one place, as named constants
# ---------------------------------------------------------------------------
# These are policy, not tuning knobs: every published health label must be
# checkable by a reader against the numbers rendered beside it, so each
# constant below has to be stateable in one sentence on the page.

#: Trailing window for volume, content length, and request counts. Two
#: weeks spans ten federal business days plus two weekends, so a source
#: that only publishes on weekdays is measured over a whole number of its
#: own publication cycles rather than over an arbitrary slice.
HEALTH_WINDOW_DAYS = 14

#: How far back "most recent item" and "last successful request" may look.
#: Wider than the window so a quiet source shows its real last delivery
#: date instead of an empty cell; bounded so the queries stay cheap.
RECENCY_LOOKBACK_DAYS = 180

#: A source with no item for this many days is `quiet`. Longer than a
#: weekend plus a federal holiday, so a normal Friday-to-Tuesday gap is
#: never reported as an interruption.
QUIET_AFTER_DAYS = 7

#: Share of requests that returned no content (4xx, 5xx, or no response at
#: all) at or above which ingestion is `degraded`. One request in ten is
#: far enough above ordinary transport noise to be worth a reader's
#: attention, and low enough to catch a host declining a meaningful slice
#: of our traffic before it declines all of it.
DEGRADED_ERROR_RATE = 0.10

#: Below this many requests in the window, a percentage is noise — one
#: failure out of two is 50% and means nothing. Under this count the rate
#: is still displayed but never on its own promotes a source to
#: `degraded`.
MIN_ATTEMPTS_FOR_RATE = 5

#: Consecutive failed collector cycles at or above which ingestion is
#: `degraded` even if the request numbers look ordinary — the collector
#: itself is telling us it is not completing.
DEGRADED_CONSECUTIVE_ERRORS = 3

#: The govinfo sync client talks to the API host; the registry entries
#: point at the human-facing collection pages on www.govinfo.gov, which
#: we never request. Fetch health for a govinfo collection is therefore
#: attributed to the host we actually call.
GOVINFO_API_HOST = "api.govinfo.gov"

DELIVERING = "delivering"
QUIET = "quiet"
DEGRADED = "degraded"
NO_RESPONSE = "no-response"
NO_DATA = "no-data"

#: Display order, worst-observed first — a summary reads top-down as
#: "here is where to look".
HEALTH_ORDER = (NO_RESPONSE, DEGRADED, QUIET, DELIVERING, NO_DATA)

#: Every label defined in terms of what we observed, never in terms of the
#: publisher. Rendered verbatim on the page and in the JSON surface, so a
#: reader can check any label against the numbers shown beside it.
HEALTH_LABELS = {
    DELIVERING: (
        "items arrived within the last {quiet} day(s) and our requests "
        "to this source's server were answered"
    ),
    QUIET: (
        "our requests were answered, but no item has arrived in the last "
        "{quiet} day(s) — the source may simply not have published"
    ),
    DEGRADED: (
        "at least {rate}% of our requests in the window returned no "
        "content, or the collector recorded {errs} or more consecutive "
        "failed cycles"
    ),
    NO_RESPONSE: (
        "we made requests in the window and none of them returned content"
    ),
    NO_DATA: (
        "no items and no requests were recorded for this source in the "
        "window — nothing observed either way"
    ),
}

#: Stated once wherever a fetch table is rendered. A status code is what
#: the server sent; why it sent it is not visible from here.
FETCH_DISCLAIMER = (
    "Counts are of our own requests, retries included. A 4xx or 5xx is "
    "the server declining to return content — that may be load, "
    "maintenance, on-demand generation, or a limit the publisher sets, "
    "and we cannot tell which from outside. Nothing here is a "
    "measurement of the publisher."
)

#: Email sources are delivered to us; we never request them.
EMAIL_FETCH_NOTE = (
    "Bulletins from this source are delivered to the project mailbox, so "
    "there are no requests to report. Its health is read from delivery "
    "recency alone."
)

#: The registry records how much of an item's text a channel gives us.
DELIVERY_MODES = {
    "full": "full article text, fetched from the item's own page",
    "feed-only": "the feed's own summary — the source publishes no more "
                 "than this through this channel",
    "feed-fallback": "the feed's summary, used because the article page "
                     "could not be read",
    "extract-fallback": "the feed's summary, used because the article "
                        "page yielded no extractable text",
    "email-full": "the bulletin carried the full item text",
    "email-teaser": "the bulletin carried a short teaser, not the full item",
}


def label_definitions():
    """The label glossary with the thresholds substituted in — so the
    page and the JSON both state the live constants, never a copy that
    can drift from them."""
    return {
        name: text.format(quiet=QUIET_AFTER_DAYS,
                          rate=round(DEGRADED_ERROR_RATE * 100),
                          errs=DEGRADED_CONSECUTIVE_ERRORS)
        for name, text in HEALTH_LABELS.items()
    }


def thresholds():
    """Every constant the classification uses, for the machine surface."""
    return {
        "window_days": HEALTH_WINDOW_DAYS,
        "recency_lookback_days": RECENCY_LOOKBACK_DAYS,
        "quiet_after_days": QUIET_AFTER_DAYS,
        "degraded_error_rate_pct": round(DEGRADED_ERROR_RATE * 100, 1),
        "degraded_consecutive_errors": DEGRADED_CONSECUTIVE_ERRORS,
        "min_attempts_for_rate": MIN_ATTEMPTS_FOR_RATE,
    }


# ---------------------------------------------------------------------------
# Registry entry -> how the pipeline identifies that source
# ---------------------------------------------------------------------------

def source_key(entry):
    """``(kind, key)`` locating this registry entry's rows in the pipeline
    database. govinfo collections are stored under their collection code
    (``packages.collection``); every other class carries its registry id
    in ``extracted_texts.metadata -> $.source_id``. ``(None, None)`` when
    the entry has no ingestion identity at all."""
    if entry.get("type") == "govinfo-collection":
        url = (entry.get("urls") or {}).get("collection", "")
        code = url.rstrip("/").rsplit("/", 1)[-1].strip().upper()
        return ("collection", code) if code else (None, None)
    return ("source_id", entry["id"])


def fetch_host(entry):
    """The host our client actually requests for this entry, or None when
    we make no requests for it (email is delivered to us)."""
    if entry.get("type") == "email":
        return None
    if entry.get("type") == "govinfo-collection":
        return GOVINFO_API_HOST
    urls = entry.get("urls") or {}
    for key in ("feed", "index", "collection", "home"):
        if urls.get(key):
            host = urlsplit(urls[key]).netloc.lower()
            if host:
                return host
    return None


def collector_worker(entry):
    """The `collector_state.worker` row that runs this entry, if one does.
    Mirrors `collect.Supervisor._build_workers`: one govinfo worker, one
    email worker, and one worker per RSS feed host."""
    kind = entry.get("type")
    if kind == "govinfo-collection":
        return "govinfo"
    if kind == "email":
        return "email"
    if kind == "rss":
        feed = (entry.get("urls") or {}).get("feed") or ""
        host = urlsplit(feed).netloc.lower()
        return f"host:{host}" if host else None
    return None


# ---------------------------------------------------------------------------
# Read-only database access
# ---------------------------------------------------------------------------

def _ro(path):
    """Read-only connection. Raises sqlite3.Error if the file is absent —
    callers turn that into a disclosed 'not available', never a crash."""
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _shift(date, days):
    import datetime as _dt

    return (_dt.date.fromisoformat(date) - _dt.timedelta(days=days)).isoformat()


def _days_between(earlier, later):
    import datetime as _dt

    try:
        return (_dt.date.fromisoformat(later)
                - _dt.date.fromisoformat(earlier)).days
    except (TypeError, ValueError):
        return None


_WINDOW_ROWS_SQL = """
SELECT p.collection AS collection,
       json_extract(e.metadata, '$.source_id') AS source_id,
       e.char_count AS char_count,
       json_extract(e.metadata, '$.mode') AS mode
FROM extracted_texts e
JOIN packages p USING (package_id)
WHERE p.date_issued >= ? AND p.date_issued <= ?
"""

_RECENCY_SQL = """
SELECT p.collection AS collection,
       json_extract(e.metadata, '$.source_id') AS source_id,
       MAX(p.date_issued) AS last_date,
       COUNT(*) AS items
FROM extracted_texts e
JOIN packages p USING (package_id)
WHERE p.date_issued >= ? AND p.date_issued <= ?
GROUP BY 1, 2
"""


def _collect_volume(conn, window_start, window_end, recency_start):
    """{(kind, key): {...volume and content-length facts...}}, keyed the
    same way `source_key` keys a registry entry. One detail query over the
    short window (we need every char_count to take a median) and one
    aggregate over the longer recency range (we need only a max)."""
    stats = {}

    def bucket(collection, source_id):
        # An item carries a registry source_id only for the agency and
        # email classes; govinfo rows are found by collection code.
        key = ("source_id", source_id) if source_id else ("collection", collection)
        return stats.setdefault(key, {
            "chars": [], "modes": {}, "last_item_date": None, "recent_items": 0,
        })

    for row in conn.execute(_WINDOW_ROWS_SQL, (window_start, window_end)):
        rec = bucket(row["collection"], row["source_id"])
        rec["chars"].append(row["char_count"] or 0)
        if row["mode"]:
            rec["modes"][row["mode"]] = rec["modes"].get(row["mode"], 0) + 1
    for row in conn.execute(_RECENCY_SQL, (recency_start, window_end)):
        rec = bucket(row["collection"], row["source_id"])
        rec["last_item_date"] = row["last_date"]
        rec["recent_items"] = row["items"]
    return stats


# Host is parsed in SQL rather than in Python so the whole fetch log never
# has to cross the process boundary: a busy fortnight is tens of thousands
# of rows, and all we want from them is five counters per host.
_FETCH_SQL = """
WITH parsed AS (
    SELECT substr(url, instr(url, '//') + 2) AS rest, status
    FROM fetch_log
    WHERE ts_utc >= ? AND ts_utc < ?
)
SELECT lower(CASE WHEN instr(rest, '/') > 0
                  THEN substr(rest, 1, instr(rest, '/') - 1)
                  ELSE rest END) AS host,
       CASE WHEN status IS NULL THEN 'no_response'
            WHEN status < 400 THEN 'answered'
            WHEN status < 500 THEN 'client_error'
            ELSE 'server_error' END AS class,
       COUNT(*) AS n
FROM parsed
GROUP BY 1, 2
"""

_FETCH_LAST_OK_SQL = """
WITH parsed AS (
    SELECT substr(url, instr(url, '//') + 2) AS rest, ts_utc
    FROM fetch_log
    WHERE ts_utc >= ? AND status IS NOT NULL AND status < 400
)
SELECT lower(CASE WHEN instr(rest, '/') > 0
                  THEN substr(rest, 1, instr(rest, '/') - 1)
                  ELSE rest END) AS host,
       MAX(ts_utc) AS last_ok
FROM parsed
GROUP BY 1
"""

_CLASSES = ("answered", "client_error", "server_error", "no_response")


def _collect_fetch(conn, window_start, window_end_exclusive, recency_start):
    """{host: {attempts, answered, client_error, server_error, no_response,
    error_rate, last_ok_at}} over the window. Timestamps in the fetch log
    are UTC; the item window is in publication (Eastern) days, so the two
    edges differ by a few hours. That is immaterial to a trailing count
    and is stated rather than papered over."""
    hosts = {}
    for row in conn.execute(_FETCH_SQL,
                            (window_start, window_end_exclusive)):
        rec = hosts.setdefault(row["host"], dict.fromkeys(_CLASSES, 0))
        rec[row["class"]] = rec[row["class"]] + row["n"]
    for row in conn.execute(_FETCH_LAST_OK_SQL, (recency_start,)):
        if row["host"] in hosts:
            hosts[row["host"]]["last_ok_at"] = row["last_ok"]
    for rec in hosts.values():
        attempts = sum(rec[c] for c in _CLASSES)
        unanswered = attempts - rec["answered"]
        rec["attempts"] = attempts
        rec["unanswered"] = unanswered
        rec["error_rate"] = (unanswered / attempts) if attempts else 0.0
        rec["error_rate_pct"] = round(100 * rec["error_rate"], 1)
        rec.setdefault("last_ok_at", None)
    return hosts


def _collect_collectors(conn):
    try:
        return {r["worker"]: {"worker": r["worker"],
                             "last_ok_at": r["last_ok_at"],
                             "last_cycle_at": r["last_cycle_at"],
                             "consecutive_errors": r["consecutive_errors"]}
                for r in conn.execute(
                    "SELECT worker, last_ok_at, last_cycle_at,"
                    " consecutive_errors FROM collector_state")}
    except sqlite3.Error:
        # A pipeline database from before the continuous-ingestion schema
        # has no collector_state; that is an absent fact, not a failure.
        return {}


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify(*, items, last_item_date, days_since_item, fetch, collector,
             is_email=False):
    """``(label, reason)`` for one source. Every branch's reason names the
    exact numbers that produced it, because the page prints those numbers
    beside the label and a reader must be able to check the work.

    Order is worst-observed first: a source whose requests all failed is
    reported that way even if it also happens to be quiet."""
    attempts = (fetch or {}).get("attempts", 0)
    answered = (fetch or {}).get("answered", 0)
    rate_pct = (fetch or {}).get("error_rate_pct", 0.0)
    unanswered = (fetch or {}).get("unanswered", 0)
    errs = (collector or {}).get("consecutive_errors", 0) or 0
    host = (fetch or {}).get("host")

    if not items and not attempts and not is_email:
        return NO_DATA, (
            f"No items recorded and no requests made in the last "
            f"{HEALTH_WINDOW_DAYS} days.")
    if is_email and not items and days_since_item is None:
        return NO_DATA, (
            f"No bulletin recorded from this source in the last "
            f"{RECENCY_LOOKBACK_DAYS} days.")

    if attempts >= MIN_ATTEMPTS_FOR_RATE and answered == 0:
        return NO_RESPONSE, (
            f"None of {attempts} request(s) to {host} in the last "
            f"{HEALTH_WINDOW_DAYS} days returned content.")

    if errs >= DEGRADED_CONSECUTIVE_ERRORS:
        return DEGRADED, (
            f"The collector for this source has recorded {errs} "
            f"consecutive failed cycles (threshold "
            f"{DEGRADED_CONSECUTIVE_ERRORS}).")
    if (attempts >= MIN_ATTEMPTS_FOR_RATE
            and (fetch or {}).get("error_rate", 0.0) >= DEGRADED_ERROR_RATE):
        return DEGRADED, (
            f"{unanswered} of {attempts} request(s) to {host} returned no "
            f"content ({rate_pct}%, at or above the "
            f"{round(DEGRADED_ERROR_RATE * 100)}% mark).")

    if days_since_item is None:
        return QUIET, (
            f"No item recorded from this source in the last "
            f"{RECENCY_LOOKBACK_DAYS} days.")
    if days_since_item > QUIET_AFTER_DAYS:
        return QUIET, (
            f"Most recent item {last_item_date}, {days_since_item} days "
            f"ago (quiet past {QUIET_AFTER_DAYS} days).")

    if is_email:
        return DELIVERING, (
            f"{items} item(s) in the last {HEALTH_WINDOW_DAYS} days; most "
            f"recent {last_item_date}, delivered by email.")
    return DELIVERING, (
        f"{items} item(s) in the last {HEALTH_WINDOW_DAYS} days; most "
        f"recent {last_item_date}; {unanswered} of {attempts} request(s) "
        f"to {host} returned no content.")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def _unavailable(reason, today, window_days):
    return {
        "available": False,
        "unavailable_reason": reason,
        "generated": utc_now_iso(),
        "window_days": window_days,
        "window_start": _shift(today, window_days - 1),
        "window_end": today,
        "thresholds": thresholds(),
        "label_definitions": label_definitions(),
        "sources": {},
        "summary": {},
    }


def source_health(entries, *, pipeline_db=None, fetch_db=None, today=None,
                  window_days=HEALTH_WINDOW_DAYS):
    """Per-source ingestion statistics for every registry entry, plus a
    whole-directory summary.

    Health is computed for `active` entries only: a `planned`,
    `unavailable`, or `evaluated-excluded` source is not ingested by
    definition, and reporting "no data" against it would read as an
    interruption rather than as a registry status. Those entries appear
    in the result with ``measured: False``.

    Degrades disclosed (docs/code-standards.md §2 rule 9): with no
    databases on disk this returns ``available: False`` and an empty
    ``sources`` map, and every caller renders "not available" rather than
    inventing a number."""
    today = today or publication_date()
    window_days = max(1, int(window_days))
    window_start = _shift(today, window_days - 1)
    recency_start = _shift(today, RECENCY_LOOKBACK_DAYS)
    # The fetch log is stamped UTC and its window is half-open on the
    # right, so "today" is included whole however far the day has run.
    fetch_end = _shift(today, -1)

    pipeline_path = Path(pipeline_db or config.PIPELINE_DB)
    fetch_path = Path(fetch_db or config.FETCH_LOG_DB)
    if not pipeline_path.exists():
        return _unavailable(
            f"pipeline database not present ({pipeline_path.name})",
            today, window_days)

    try:
        conn = _ro(pipeline_path)
    except sqlite3.Error as exc:
        logger.warning("health: pipeline database unreadable: %s", exc)
        return _unavailable(f"pipeline database unreadable: {exc}",
                            today, window_days)
    try:
        volume = _collect_volume(conn, window_start, today, recency_start)
        collectors = _collect_collectors(conn)
    except sqlite3.Error as exc:
        logger.warning("health: pipeline query failed: %s", exc)
        return _unavailable(f"pipeline database unreadable: {exc}",
                            today, window_days)
    finally:
        conn.close()

    hosts, fetch_available = {}, False
    if fetch_path.exists():
        try:
            fconn = _ro(fetch_path)
            try:
                hosts = _collect_fetch(fconn, window_start, fetch_end,
                                       recency_start)
                fetch_available = True
            finally:
                fconn.close()
        except sqlite3.Error as exc:
            logger.warning("health: fetch log unreadable: %s", exc)

    # How many registered sources share each host, so a card can say that
    # its request figures are host-wide rather than its own.
    host_sources = {}
    for entry in entries:
        host = fetch_host(entry)
        if host and entry["status"] == "active":
            host_sources[host] = host_sources.get(host, 0) + 1

    sources = {}
    for entry in entries:
        sources[entry["id"]] = _one_source(
            entry, volume, hosts, collectors, host_sources,
            today=today, window_days=window_days,
            fetch_available=fetch_available)

    return {
        "available": True,
        "generated": utc_now_iso(),
        "window_days": window_days,
        "window_start": window_start,
        "window_end": today,
        "recency_lookback_days": RECENCY_LOOKBACK_DAYS,
        "fetch_log_available": fetch_available,
        "thresholds": thresholds(),
        "label_definitions": label_definitions(),
        "fetch_disclaimer": FETCH_DISCLAIMER,
        "sources": sources,
        "summary": summarize(sources, window_days),
    }


def _one_source(entry, volume, hosts, collectors, host_sources, *, today,
                window_days, fetch_available):
    key = source_key(entry)
    stats = volume.get(key, {})
    chars = stats.get("chars", [])
    modes = stats.get("modes", {})
    last_item_date = stats.get("last_item_date")
    host = fetch_host(entry)
    is_email = entry.get("type") == "email"

    fetch = None
    if host and not is_email:
        counters = hosts.get(host)
        fetch = {"host": host, "shared_with_sources": host_sources.get(host, 1)}
        if counters:
            fetch.update({k: counters[k] for k in _CLASSES})
            fetch.update({
                "attempts": counters["attempts"],
                "unanswered": counters["unanswered"],
                "error_rate": counters["error_rate"],
                "error_rate_pct": counters["error_rate_pct"],
                "last_ok_at": counters["last_ok_at"],
            })
        else:
            fetch.update(dict.fromkeys(_CLASSES, 0))
            fetch.update({"attempts": 0, "unanswered": 0, "error_rate": 0.0,
                          "error_rate_pct": 0.0, "last_ok_at": None})

    worker = collector_worker(entry)
    collector = collectors.get(worker) if worker else None

    record = {
        "id": entry["id"],
        "name": entry["name"],
        "status": entry["status"],
        "type": entry["type"],
        "branch": entry["branch"],
        "tier": entry["tier"],
        "parent_org": entry["parent_org"],
        "identified_by": {"kind": key[0], "key": key[1]},
        "measured": entry["status"] == "active",
        "window_days": window_days,
        "items": len(chars),
        "items_per_day": round(len(chars) / window_days, 2),
        "avg_chars": round(statistics.mean(chars)) if chars else None,
        "median_chars": round(statistics.median(chars)) if chars else None,
        "min_chars": min(chars) if chars else None,
        "max_chars": max(chars) if chars else None,
        "last_item_date": last_item_date,
        "days_since_item": _days_between(last_item_date, today),
        "delivery_mode": (max(modes, key=lambda m: (modes[m], m))
                          if modes else None),
        "fetch": fetch,
        "fetch_note": EMAIL_FETCH_NOTE if is_email else None,
        "collector": collector,
    }
    record["delivery_mode_note"] = DELIVERY_MODES.get(record["delivery_mode"])

    if not record["measured"]:
        record["health"] = None
        record["health_reason"] = (
            f"Not ingested: the registry status of this source is "
            f"{entry['status']}.")
        return record

    if fetch is not None and not fetch_available:
        # The fetch log is missing but the pipeline database is not: say
        # so instead of reading zero requests as a total outage.
        record["fetch"] = None
        record["fetch_note"] = ("Request statistics are not available in "
                                "this build.")
        fetch = None

    record["health"], record["health_reason"] = classify(
        items=record["items"], last_item_date=last_item_date,
        days_since_item=record["days_since_item"], fetch=fetch,
        collector=collector, is_email=is_email)
    return record


def summarize(sources, window_days=HEALTH_WINDOW_DAYS):
    """Directory-wide totals: what a reader should take in before reading
    any individual card."""
    measured = [s for s in sources.values() if s["measured"]]
    counts = {label: sum(1 for s in measured if s["health"] == label)
              for label in HEALTH_ORDER}
    items = sum(s["items"] for s in measured)
    with_errors = sorted({
        s["fetch"]["host"] for s in measured
        if s["fetch"] and s["fetch"]["unanswered"] > 0})
    # Request counts are per HOST, and several sources can share one (all
    # five govinfo collections are read from api.govinfo.gov). Summing the
    # per-source figures would count that host's traffic five times.
    by_host = {s["fetch"]["host"]: s["fetch"]["attempts"]
               for s in measured if s["fetch"]}
    return {
        "window_days": window_days,
        "sources_registered": len(sources),
        "sources_measured": len(measured),
        "health_counts": counts,
        "delivering": counts[DELIVERING],
        "items_window": items,
        "items_per_day": round(items / window_days, 1) if window_days else 0.0,
        "sources_with_fetch_errors": sum(
            1 for s in measured if s["fetch"] and s["fetch"]["unanswered"] > 0),
        "hosts_with_fetch_errors": with_errors,
        "hosts_measured": len(by_host),
        "requests_window": sum(by_host.values()),
    }

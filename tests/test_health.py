"""Source health and statistics tests (fapd.health).

Every figure this module publishes is an observation of OUR ingestion, so
the tests pin two things at once: that the arithmetic is right, and that
each classification boundary lands where the documented constant says it
does — a label a reader cannot check against the numbers beside it is the
failure mode this surface most has to avoid.

The suite builds its own SQLite databases under tmp_path (no `data/`
exists in a worktree or in CI), which is also how the graceful-degradation
contract gets exercised honestly.
"""

import sqlite3

import pytest

from fapd import db, health

# ---------------------------------------------------------------------------
# Fixtures: registry entries and throwaway databases
# ---------------------------------------------------------------------------

TODAY = "2026-07-31"
NOW = "2026-07-31T12:00:00Z"   # the injected clock for the 24-hour window


def entry(sid, **over):
    base = {
        "id": sid, "name": f"Name of {sid}", "branch": "executive",
        "parent_org": "Some Department", "description": "A description.",
        "type": "rss", "tier": 1,
        "urls": {"feed": "https://feeds.example.gov/press.xml",
                 "home": "https://www.example.gov/news"},
        "method": "conditional GET", "status": "active",
        "added": "2026-07-01", "notes": "gate-3 evaluated",
    }
    base.update(over)
    return base


GOVINFO = entry(
    "govinfo-fr", type="govinfo-collection", branch="executive",
    urls={"collection": "https://www.govinfo.gov/app/collection/FR"})
WEB = entry("justice-newsroom")
EMAIL = entry("usattorneys-email", type="email",
              urls={"signup": "https://public.govdelivery.com/x"},
              sender="news@example.gov")


def make_pipeline_db(tmp_path, rows=(), collectors=()):
    """A real pipeline database with the real DDL. `rows` are
    (package_id, collection, date_issued, char_count, metadata_json
    [, first_seen_at]) — the observation stamp defaults to midnight of
    TODAY, inside every recent window the suite uses."""
    path = tmp_path / "fapd.db"
    conn = db.connect(path)
    for row in rows:
        package_id, collection, date_issued, chars, metadata = row[:5]
        first_seen = row[5] if len(row) > 5 else "2026-07-31T00:00:00Z"
        conn.execute(
            "INSERT OR IGNORE INTO packages (package_id, collection,"
            " date_issued, last_modified, first_seen_at)"
            " VALUES (?, ?, ?, '2026-07-31T00:00:00Z', ?)",
            (package_id, collection, date_issued, first_seen))
        conn.execute(
            "INSERT INTO extracted_texts (package_id, granule_id, collection,"
            " metadata, text, char_count, extracted_at, extractor_version)"
            " VALUES (?, '', ?, ?, '', ?, '2026-07-31T00:00:00Z', 1)",
            (package_id, collection, metadata, chars))
    for worker, last_ok, errors in collectors:
        conn.execute(
            "INSERT INTO collector_state (worker, last_cycle_at, last_ok_at,"
            " consecutive_errors) VALUES (?, '2026-07-31T00:00:00Z', ?, ?)",
            (worker, last_ok, errors))
    conn.commit()
    conn.close()
    return path


def make_fetch_db(tmp_path, rows=()):
    """`rows` are (ts_utc, url, status[, client]) — status None means no
    response; client defaults to NULL, which is how historical (and
    govinfo) traffic is labeled."""
    path = tmp_path / "fetch_log.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE fetch_log (id INTEGER PRIMARY KEY, ts_utc TEXT NOT NULL,"
        " url TEXT NOT NULL, status INTEGER, bytes INTEGER NOT NULL DEFAULT 0,"
        " elapsed_ms INTEGER, attempt INTEGER NOT NULL DEFAULT 1, error TEXT,"
        " client TEXT)")
    conn.executemany(
        "INSERT INTO fetch_log (ts_utc, url, status, attempt, client)"
        " VALUES (?, ?, ?, 1, ?)",
        [r if len(r) == 4 else (*r, None) for r in rows])
    conn.commit()
    conn.close()
    return path


def meta(source_id=None, mode=None):
    import json

    payload = {}
    if source_id:
        payload["source_id"] = source_id
    if mode:
        payload["mode"] = mode
    return json.dumps(payload, sort_keys=True)


def run(tmp_path, entries, rows=(), fetches=(), collectors=(), today=TODAY,
        with_fetch_db=True, now=None):
    pipeline = make_pipeline_db(tmp_path, rows, collectors)
    fetch = make_fetch_db(tmp_path, fetches) if with_fetch_db else (
        tmp_path / "absent.db")
    return health.source_health(entries, pipeline_db=pipeline,
                                fetch_db=fetch, today=today, now=now)


# ---------------------------------------------------------------------------
# Identity mapping: registry entry -> pipeline rows, host, collector worker
# ---------------------------------------------------------------------------

def test_source_key_maps_each_class_to_how_the_pipeline_stores_it():
    # govinfo rows carry no registry id; they are found by collection code
    assert health.source_key(GOVINFO) == ("collection", "FR")
    assert health.source_key(WEB) == ("source_id", "justice-newsroom")
    assert health.source_key(EMAIL) == ("source_id", "usattorneys-email")


def test_fetch_host_uses_the_host_we_actually_call():
    # the registry points at the human collection page; the sync client
    # talks to the API host, and health must attribute the requests there
    assert health.fetch_host(GOVINFO) == health.GOVINFO_API_HOST
    assert health.fetch_host(WEB) == "feeds.example.gov"
    assert health.fetch_host(EMAIL) is None  # delivered to us, never requested


def test_collector_worker_mirrors_the_supervisor():
    assert health.collector_worker(GOVINFO) == "govinfo"
    assert health.collector_worker(EMAIL) == "email"
    assert health.collector_worker(WEB) == "host:feeds.example.gov"
    assert health.collector_worker(entry("x", type="html-index")) is None


# ---------------------------------------------------------------------------
# Per-source aggregation
# ---------------------------------------------------------------------------

def test_per_source_aggregation(tmp_path):
    """Counts, rate, mean, median, extremes, most recent date and delivery
    mode, all keyed the way the pipeline actually stores each class."""
    rows = [
        ("PR-justice-1", "AGENCYPR", "2026-07-31", 300,
         meta("justice-newsroom", "feed-only")),
        ("PR-justice-2", "AGENCYPR", "2026-07-30", 400,
         meta("justice-newsroom", "feed-only")),
        ("PR-justice-3", "AGENCYPR", "2026-07-29", 1100,
         meta("justice-newsroom", "full")),
        ("FR-2026-07-31", "FR", "2026-07-31", 16000, meta()),
        # outside the 14-day window: counted for recency, not for volume
        ("PR-justice-old", "AGENCYPR", "2026-07-01", 9999,
         meta("justice-newsroom", "feed-only")),
    ]
    out = run(tmp_path, [WEB, GOVINFO], rows)
    web = out["sources"]["justice-newsroom"]
    assert web["items"] == 3
    assert web["items_per_day"] == round(3 / 14, 2)
    assert web["avg_chars"] == 600          # (300 + 400 + 1100) / 3
    assert web["median_chars"] == 400
    assert web["min_chars"] == 300
    assert web["max_chars"] == 1100
    assert web["last_item_date"] == "2026-07-31"
    assert web["days_since_item"] == 0
    # the mode the source mostly delivers in, not the last one seen
    assert web["delivery_mode"] == "feed-only"
    assert web["delivery_mode_note"] == health.DELIVERY_MODES["feed-only"]
    # govinfo is keyed by collection code, so the FR row lands on it
    assert out["sources"]["govinfo-fr"]["items"] == 1
    assert out["sources"]["govinfo-fr"]["avg_chars"] == 16000
    assert out["sources"]["govinfo-fr"]["delivery_mode"] is None


def test_window_edges_are_inclusive(tmp_path):
    """The window is the last HEALTH_WINDOW_DAYS days INCLUDING today, so
    the oldest day inside it is today minus (window - 1)."""
    oldest = health._shift(TODAY, health.HEALTH_WINDOW_DAYS - 1)
    just_outside = health._shift(TODAY, health.HEALTH_WINDOW_DAYS)
    rows = [("A", "AGENCYPR", oldest, 100, meta("justice-newsroom")),
            ("B", "AGENCYPR", just_outside, 100, meta("justice-newsroom")),
            ("C", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))]
    out = run(tmp_path, [WEB], rows)
    assert out["window_start"] == oldest
    assert out["window_end"] == TODAY
    assert out["sources"]["justice-newsroom"]["items"] == 2


def test_fetch_counts_bucket_by_host_and_status_class(tmp_path):
    fetches = [
        ("2026-07-31T01:00:00Z", "https://feeds.example.gov/press.xml", 200),
        ("2026-07-31T02:00:00Z", "https://feeds.example.gov/press.xml", 304),
        ("2026-07-31T03:00:00Z", "https://feeds.example.gov/a", 403),
        ("2026-07-31T04:00:00Z", "https://feeds.example.gov/b", 503),
        ("2026-07-31T05:00:00Z", "https://feeds.example.gov/c", None),
        # another host entirely — must not leak into this source's numbers
        ("2026-07-31T06:00:00Z", "https://other.example.gov/z", 500),
        # before the window
        ("2026-07-01T06:00:00Z", "https://feeds.example.gov/press.xml", 500),
    ]
    rows = [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))]
    out = run(tmp_path, [WEB], rows, fetches)
    fetch = out["sources"]["justice-newsroom"]["fetch"]
    assert fetch["host"] == "feeds.example.gov"
    assert fetch["attempts"] == 5
    assert fetch["answered"] == 2          # 200 and 304 both returned to us
    assert fetch["client_error"] == 1
    assert fetch["server_error"] == 1
    assert fetch["no_response"] == 1
    assert fetch["unanswered"] == 3
    assert fetch["error_rate_pct"] == 60.0
    assert fetch["last_ok_at"] == "2026-07-31T02:00:00Z"


def test_shared_host_is_disclosed_not_divided(tmp_path):
    """All five govinfo collections are read from one host. The figures
    are host-wide and every card that shows them says so."""
    a = entry("govinfo-fr", type="govinfo-collection",
              urls={"collection": "https://www.govinfo.gov/app/collection/FR"})
    b = entry("govinfo-crec", type="govinfo-collection",
              urls={"collection": "https://www.govinfo.gov/app/collection/CREC"})
    fetches = [("2026-07-31T01:00:00Z",
                f"https://{health.GOVINFO_API_HOST}/collections/FR", 200)] * 3
    out = run(tmp_path, [a, b], fetches=fetches)
    for sid in ("govinfo-fr", "govinfo-crec"):
        assert out["sources"][sid]["fetch"]["shared_with_sources"] == 2
        assert out["sources"][sid]["fetch"]["attempts"] == 3
    # ...and the directory total counts that host's traffic exactly once
    assert out["summary"]["requests_window"] == 3
    assert out["summary"]["hosts_measured"] == 1


# ---------------------------------------------------------------------------
# Probe exclusion — availability probes are not ingestion traffic
# ---------------------------------------------------------------------------

def test_probe_requests_are_excluded_from_every_figure(tmp_path):
    """client='probe' rows (source-pages plan 2026-08-03) measure
    reachability, not ingestion: they must not inflate volume, must not
    read as degradation, and must not supply last_ok_at. NULL-client
    (historical) traffic still counts."""
    pipeline = make_pipeline_db(
        tmp_path, [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))])
    fetch = make_fetch_db(tmp_path, [
        ("2026-07-31T01:00:00Z", "https://feeds.example.gov/press.xml", 200,
         "agency"),
        ("2026-07-31T02:00:00Z", "https://feeds.example.gov/press.xml", 200,
         None),
        ("2026-07-31T03:00:00Z", "https://feeds.example.gov/a", 503, "agency"),
        # probe traffic — a failure AND a later success, both invisible
        ("2026-07-31T04:00:00Z", "https://feeds.example.gov/x", None, "probe"),
        ("2026-07-31T05:00:00Z", "https://feeds.example.gov/x", 200, "probe"),
    ])
    out = health.source_health([WEB], pipeline_db=pipeline, fetch_db=fetch,
                               today=TODAY, now=NOW)
    f = out["sources"]["justice-newsroom"]["fetch"]
    assert f["attempts"] == 3
    assert f["answered"] == 2
    assert f["no_response"] == 0           # the probe's timeout is invisible
    assert f["last_ok_at"] == "2026-07-31T02:00:00Z"   # not the probe's 05:00
    rec = out["sources"]["justice-newsroom"]["recent"]
    assert (rec["requests"], rec["ok"], rec["failed"]) == (3, 2, 1)
    life = health.fetch_stats_all_time(fetch_db=fetch)["feeds.example.gov"]
    assert life == {"requests": 3, "ok": 2, "failures": 1,
                    "first_seen": "2026-07-31T01:00:00Z"}


def test_fetch_log_without_client_column_still_reports(tmp_path):
    """A snapshot from before the client column existed degrades to
    counting everything — never to erroring the fetch section away."""
    path = tmp_path / "old_fetch.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE fetch_log (id INTEGER PRIMARY KEY, ts_utc TEXT,"
        " url TEXT, status INTEGER, attempt INTEGER)")
    conn.execute(
        "INSERT INTO fetch_log (ts_utc, url, status, attempt) VALUES"
        " ('2026-07-31T01:00:00Z', 'https://feeds.example.gov/press.xml',"
        " 200, 1)")
    conn.commit()
    conn.close()
    pipeline = make_pipeline_db(
        tmp_path, [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))])
    out = health.source_health([WEB], pipeline_db=pipeline, fetch_db=path,
                               today=TODAY, now=NOW)
    assert out["fetch_log_available"] is True
    assert out["sources"]["justice-newsroom"]["fetch"]["attempts"] == 1
    assert health.fetch_stats_all_time(
        fetch_db=path)["feeds.example.gov"]["requests"] == 1


# ---------------------------------------------------------------------------
# The trailing-24-hour `recent` block — displayed, never classified on
# ---------------------------------------------------------------------------

def test_recent_window_is_the_trailing_24_hours(tmp_path):
    """`recent` counts by the clock from the injected `now`, over UTC
    observation stamps — item arrival (first_seen_at), not the
    publication day the item belongs to."""
    rows = [
        # arrived 23h before NOW: inside
        ("IN", "AGENCYPR", TODAY, 100, meta("justice-newsroom"),
         "2026-07-30T13:00:00Z"),
        # arrived 25h before NOW: outside, though well inside 14 days
        ("OUT", "AGENCYPR", "2026-07-30", 100, meta("justice-newsroom"),
         "2026-07-30T11:00:00Z"),
    ]
    fetches = [
        ("2026-07-30T13:00:00Z", "https://feeds.example.gov/press.xml", 200),
        ("2026-07-31T09:00:00Z", "https://feeds.example.gov/press.xml", 503),
        # outside 24h, inside the 14-day window
        ("2026-07-30T11:00:00Z", "https://feeds.example.gov/press.xml", 200),
    ]
    out = run(tmp_path, [WEB], rows, fetches, now=NOW)
    rec = out["sources"]["justice-newsroom"]["recent"]
    assert rec == {"hours": 24, "requests": 2, "ok": 1, "failed": 1,
                   "items": 1}
    # the 14-day figures are untouched by the new window
    assert out["sources"]["justice-newsroom"]["fetch"]["attempts"] == 3
    assert out["sources"]["justice-newsroom"]["items"] == 2
    assert out["recent_window_hours"] == 24


def test_recent_figures_never_move_the_label(tmp_path):
    """The label stays on the 14-day window by design: below the
    statistical floor a percentage is noise, and a label that flaps
    daily is worse than a stable one. Every recent request failing must
    not reclassify a source whose fortnight is fine."""
    rows = [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))]
    fetches = ([("2026-07-20T01:00:00Z",
                 "https://feeds.example.gov/press.xml", 200)] * 20
               + [("2026-07-31T09:00:00Z",
                   "https://feeds.example.gov/press.xml", 503)])
    out = run(tmp_path, [WEB], rows, fetches, now=NOW)
    rec = out["sources"]["justice-newsroom"]
    assert rec["recent"] == {"hours": 24, "requests": 1, "ok": 0,
                             "failed": 1, "items": 1}
    assert rec["health"] == health.DELIVERING       # 1 of 21 is under 10%


def test_recent_request_counts_are_none_where_fetch_is_none(tmp_path):
    """Email sources make no requests, and a missing fetch log must not
    read as zero traffic — in both cases the recent request figures are
    None while the item count still reports."""
    rows = [("PR-em-1", "AGENCYPR", TODAY, 310,
             meta("usattorneys-email", "email-teaser"))]
    out = run(tmp_path, [EMAIL], rows, now=NOW)
    rec = out["sources"]["usattorneys-email"]["recent"]
    assert rec == {"hours": 24, "requests": None, "ok": None, "failed": None,
                   "items": 1}
    rows = [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))]
    out = run(tmp_path / "nolog", [WEB], rows, with_fetch_db=False, now=NOW)
    rec = out["sources"]["justice-newsroom"]["recent"]
    assert rec["requests"] is None and rec["items"] == 1


def test_unmeasured_sources_carry_no_recent_block(tmp_path):
    out = run(tmp_path, [entry("planned-src", status="planned", notes="")],
              now=NOW)
    assert out["sources"]["planned-src"]["recent"] is None


# ---------------------------------------------------------------------------
# Classification boundaries — one test per documented constant
# ---------------------------------------------------------------------------

def ok_fetch(n=20, unanswered=0):
    answered = n - unanswered
    return {"host": "h", "attempts": n, "answered": answered,
            "client_error": 0, "server_error": unanswered, "no_response": 0,
            "unanswered": unanswered,
            "error_rate": (unanswered / n) if n else 0.0,
            "error_rate_pct": round(100 * unanswered / n, 1) if n else 0.0,
            "last_ok_at": None}


def test_delivering_when_items_are_recent_and_requests_are_answered():
    label, reason = health.classify(
        items=12, last_item_date=TODAY, days_since_item=0,
        fetch=ok_fetch(), collector=None)
    assert label == health.DELIVERING
    assert "12 item(s)" in reason


def test_quiet_boundary_is_the_documented_day_count():
    """At exactly QUIET_AFTER_DAYS a source is still delivering; one day
    past it, it is quiet. A weekend plus a holiday must never register."""
    on_the_line = health.classify(
        items=1, last_item_date="2026-07-24",
        days_since_item=health.QUIET_AFTER_DAYS, fetch=ok_fetch(),
        collector=None)
    past_it = health.classify(
        items=0, last_item_date="2026-07-23",
        days_since_item=health.QUIET_AFTER_DAYS + 1, fetch=ok_fetch(),
        collector=None)
    assert on_the_line[0] == health.DELIVERING
    assert past_it[0] == health.QUIET
    assert f"quiet past {health.QUIET_AFTER_DAYS} days" in past_it[1]


def test_degraded_at_exactly_the_error_rate_threshold():
    """10 of 100 is the documented mark, so it classifies; 9 of 100 does
    not. The reason names both numbers and the threshold."""
    at = health.classify(items=5, last_item_date=TODAY, days_since_item=0,
                         fetch=ok_fetch(100, 10), collector=None)
    under = health.classify(items=5, last_item_date=TODAY, days_since_item=0,
                            fetch=ok_fetch(100, 9), collector=None)
    assert at[0] == health.DEGRADED
    assert "10 of 100 request(s)" in at[1]
    assert "10.0%" in at[1]
    assert under[0] == health.DELIVERING


def test_a_tiny_sample_never_promotes_to_degraded():
    """One failure out of two is 50% and means nothing. Below
    MIN_ATTEMPTS_FOR_RATE the rate is displayed but never classifies."""
    few = health.classify(
        items=3, last_item_date=TODAY, days_since_item=0,
        fetch=ok_fetch(health.MIN_ATTEMPTS_FOR_RATE - 1,
                       health.MIN_ATTEMPTS_FOR_RATE - 1),
        collector=None)
    assert few[0] == health.DELIVERING


def test_consecutive_collector_errors_classify_on_their_own():
    at = health.classify(
        items=5, last_item_date=TODAY, days_since_item=0, fetch=ok_fetch(),
        collector={"consecutive_errors": health.DEGRADED_CONSECUTIVE_ERRORS})
    under = health.classify(
        items=5, last_item_date=TODAY, days_since_item=0, fetch=ok_fetch(),
        collector={"consecutive_errors":
                   health.DEGRADED_CONSECUTIVE_ERRORS - 1})
    assert at[0] == health.DEGRADED
    assert "consecutive failed cycles" in at[1]
    assert under[0] == health.DELIVERING


def test_no_response_when_nothing_we_asked_for_came_back():
    label, reason = health.classify(
        items=0, last_item_date=None, days_since_item=None,
        fetch=ok_fetch(40, 40), collector=None)
    assert label == health.NO_RESPONSE
    assert "None of 40 request(s)" in reason


def test_no_data_when_nothing_was_observed_either_way():
    label, reason = health.classify(
        items=0, last_item_date=None, days_since_item=None, fetch=None,
        collector=None)
    assert label == health.NO_DATA
    assert "no requests" in reason


def test_worst_observation_wins_over_quiet():
    """A source whose every request failed is reported that way even
    though it is also, trivially, quiet."""
    label, _ = health.classify(
        items=0, last_item_date="2026-01-01", days_since_item=200,
        fetch=ok_fetch(40, 40), collector=None)
    assert label == health.NO_RESPONSE


def test_no_label_names_the_publisher():
    """Editorial gate: labels describe our ingestion. Nothing in the
    vocabulary may read as a verdict on an agency (GUIDE §2)."""
    forbidden = ("unreliable", "failing", "poor", "broken", "worst",
                 "negligent", "irresponsible", "unhealthy")
    text = " ".join(list(health.label_definitions().values())
                    + list(health.HEALTH_ORDER)
                    + [health.FETCH_DISCLAIMER, health.EMAIL_FETCH_NOTE]).lower()
    assert not [w for w in forbidden if w in text]
    # and the disclaimer states the thing a 5xx does and does not mean
    assert "cannot tell which" in health.FETCH_DISCLAIMER
    assert "measurement of the publisher" in health.FETCH_DISCLAIMER


# ---------------------------------------------------------------------------
# The email path — no requests to report, health from delivery recency
# ---------------------------------------------------------------------------

def test_email_sources_report_delivery_not_requests(tmp_path):
    rows = [("PR-em-1", "AGENCYPR", TODAY, 310,
             meta("usattorneys-email", "email-teaser"))]
    out = run(tmp_path, [EMAIL], rows)
    rec = out["sources"]["usattorneys-email"]
    assert rec["fetch"] is None            # never an empty table of zeroes
    assert rec["fetch_note"] == health.EMAIL_FETCH_NOTE
    assert rec["health"] == health.DELIVERING
    assert "delivered by email" in rec["health_reason"]
    # the registry's own mode is surfaced: a 310-char teaser is not an
    # article, and the page must be able to say so
    assert rec["delivery_mode"] == "email-teaser"
    assert "teaser" in rec["delivery_mode_note"]


def test_email_source_with_no_bulletins_is_no_data_not_no_response(tmp_path):
    out = run(tmp_path, [EMAIL])
    rec = out["sources"]["usattorneys-email"]
    assert rec["health"] == health.NO_DATA
    assert rec["fetch"] is None


def test_email_source_goes_quiet_on_recency_alone(tmp_path):
    rows = [("PR-em-old", "AGENCYPR", "2026-07-01", 310,
             meta("usattorneys-email", "email-teaser"))]
    out = run(tmp_path, [EMAIL], rows)
    rec = out["sources"]["usattorneys-email"]
    assert rec["health"] == health.QUIET
    assert "2026-07-01" in rec["health_reason"]


# ---------------------------------------------------------------------------
# Non-active entries, summary, and graceful degradation
# ---------------------------------------------------------------------------

def test_non_active_entries_are_not_measured(tmp_path):
    planned = entry("planned-src", status="planned", notes="")
    blocked = entry("blocked-src", status="unavailable", notes="")
    out = run(tmp_path, [planned, blocked, WEB])
    for sid in ("planned-src", "blocked-src"):
        assert out["sources"][sid]["measured"] is False
        assert out["sources"][sid]["health"] is None
        assert "Not ingested" in out["sources"][sid]["health_reason"]
    assert out["summary"]["sources_registered"] == 3
    assert out["summary"]["sources_measured"] == 1


def test_summary_counts_every_label_and_the_aggregate_volume(tmp_path):
    other = entry("other-src",
                  urls={"feed": "https://other.example.gov/f.xml"})
    rows = [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom")),
            ("B", "AGENCYPR", TODAY, 100, meta("justice-newsroom")),
            ("C", "AGENCYPR", "2026-07-02", 100, meta("other-src"))]
    # the second host answers most of the time but declines a fifth of
    # our requests — degraded, which is a different observation from the
    # host that answers nothing at all
    fetches = ([("2026-07-31T01:00:00Z",
                 "https://feeds.example.gov/press.xml", 200)] * 10
               + [("2026-07-31T01:00:00Z",
                   "https://other.example.gov/f.xml", 200)] * 8
               + [("2026-07-31T01:00:00Z",
                   "https://other.example.gov/f.xml", 503)] * 2)
    out = run(tmp_path, [WEB, other], rows, fetches)
    summary = out["summary"]
    assert summary["health_counts"][health.DELIVERING] == 1
    assert summary["health_counts"][health.DEGRADED] == 1
    assert summary["delivering"] == 1
    assert summary["items_window"] == 2       # C is outside the window
    assert summary["items_per_day"] == round(2 / 14, 1)
    assert summary["sources_with_fetch_errors"] == 1
    assert summary["hosts_with_fetch_errors"] == ["other.example.gov"]
    assert summary["requests_window"] == 20
    assert set(summary["health_counts"]) == set(health.HEALTH_ORDER)


def test_missing_databases_degrade_disclosed(tmp_path):
    out = health.source_health([WEB], pipeline_db=tmp_path / "nope.db",
                               fetch_db=tmp_path / "nope2.db", today=TODAY)
    assert out["available"] is False
    assert "not present" in out["unavailable_reason"]
    assert out["sources"] == {}
    # the thresholds and glossary are still published: they describe the
    # method, which does not depend on there being data
    assert out["thresholds"]["window_days"] == health.HEALTH_WINDOW_DAYS
    assert set(out["label_definitions"]) == set(health.HEALTH_ORDER)


def test_missing_fetch_log_omits_requests_rather_than_reading_zero(tmp_path):
    """A missing request log must not be indistinguishable from a host
    that answered nothing — that would invent an outage."""
    rows = [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))]
    out = run(tmp_path, [WEB], rows, with_fetch_db=False)
    rec = out["sources"]["justice-newsroom"]
    assert out["fetch_log_available"] is False
    assert rec["fetch"] is None
    assert "not available" in rec["fetch_note"]
    assert rec["health"] == health.DELIVERING


def test_pipeline_db_without_collector_state_still_reports(tmp_path):
    """An older database predating continuous ingestion has no
    collector_state; an absent fact is not a failure."""
    path = tmp_path / "bare.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE packages (package_id TEXT PRIMARY KEY,"
                 " collection TEXT, date_issued TEXT)")
    conn.execute("CREATE TABLE extracted_texts (package_id TEXT,"
                 " metadata TEXT, char_count INTEGER)")
    conn.execute("INSERT INTO packages VALUES ('A', 'AGENCYPR', ?)", (TODAY,))
    conn.execute("INSERT INTO extracted_texts VALUES ('A', ?, 250)",
                 (meta("justice-newsroom"),))
    conn.commit()
    conn.close()
    out = health.source_health([WEB], pipeline_db=path,
                               fetch_db=tmp_path / "absent.db", today=TODAY)
    assert out["available"] is True
    assert out["sources"]["justice-newsroom"]["items"] == 1
    assert out["sources"]["justice-newsroom"]["collector"] is None


def test_collector_errors_reach_the_source_record(tmp_path):
    rows = [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))]
    out = run(tmp_path, [WEB], rows,
              collectors=[("host:feeds.example.gov", None, 4)])
    rec = out["sources"]["justice-newsroom"]
    assert rec["collector"]["consecutive_errors"] == 4
    assert rec["health"] == health.DEGRADED


def test_label_definitions_state_the_live_thresholds():
    """The page prints these sentences verbatim, so they must interpolate
    the constants rather than restate them — a copy can drift."""
    defs = health.label_definitions()
    assert f"{health.QUIET_AFTER_DAYS} day(s)" in defs[health.QUIET]
    assert (f"{round(health.DEGRADED_ERROR_RATE * 100)}%"
            in defs[health.DEGRADED])
    assert (str(health.DEGRADED_CONSECUTIVE_ERRORS)
            in defs[health.DEGRADED])
    assert "{" not in "".join(defs.values())   # every field substituted


# ---------------------------------------------------------------------------
# Persisted label state — transitions a downstream layer can react to
# ---------------------------------------------------------------------------

def _measured(label, measured=True):
    return {"measured": measured, "health": label}


def test_health_state_upserts_and_marks_transitions(tmp_path):
    """last_checked always moves; label+since move ONLY on a label
    change — `since` is the transition edge the assessment layer
    regenerates on. A first observation counts as a change."""
    conn = db.connect(tmp_path / "state.db")
    sources = {"a": _measured(health.DELIVERING),
               "b": _measured(health.QUIET),
               "planned": _measured(None, measured=False)}
    t1, t2, t3 = ("2026-07-31T01:00:00Z", "2026-07-31T02:00:00Z",
                  "2026-07-31T03:00:00Z")
    assert health.record_health_state(conn, sources, now=t1) == ["a", "b"]
    state = health.health_state(conn)
    assert state["a"] == {"label": health.DELIVERING,
                          "since": t1, "last_checked": t1}
    assert "planned" not in state          # unmeasured is never persisted

    # same label re-affirmed: last_checked moves, since must not
    assert health.record_health_state(conn, sources, now=t2) == []
    state = health.health_state(conn)
    assert state["a"]["since"] == t1
    assert state["a"]["last_checked"] == t2

    # a transition moves label and since together, and is reported
    sources["a"] = _measured(health.DEGRADED)
    assert health.record_health_state(conn, sources, now=t3) == ["a"]
    state = health.health_state(conn)
    assert state["a"] == {"label": health.DEGRADED,
                          "since": t3, "last_checked": t3}
    assert state["b"] == {"label": health.QUIET,
                          "since": t1, "last_checked": t3}
    conn.close()


def test_health_state_reader_survives_a_pre_migration_db(tmp_path):
    """A database from before source_health_state existed yields no
    facts, not a failure — the _collect_collectors contract."""
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE packages (package_id TEXT PRIMARY KEY)")
    assert health.health_state(conn) == {}
    conn.close()


# ---------------------------------------------------------------------------
# All-time fetch statistics (per-source pages)
# ---------------------------------------------------------------------------

def test_fetch_stats_all_time_counts_the_whole_log(tmp_path):
    fetch = make_fetch_db(tmp_path, [
        ("2026-05-01T01:00:00Z", "https://feeds.example.gov/press.xml", 200),
        ("2026-06-15T01:00:00Z", "https://feeds.example.gov/press.xml", 503),
        ("2026-07-31T01:00:00Z", "https://feeds.example.gov/press.xml", None),
        ("2026-07-31T02:00:00Z", "https://other.example.gov/f.xml", 304),
    ])
    stats = health.fetch_stats_all_time(fetch_db=fetch)
    assert stats["feeds.example.gov"] == {
        "requests": 3, "ok": 1, "failures": 2,
        "first_seen": "2026-05-01T01:00:00Z"}
    assert stats["other.example.gov"]["ok"] == 1


def test_fetch_stats_all_time_missing_log_degrades_to_empty(tmp_path):
    assert health.fetch_stats_all_time(fetch_db=tmp_path / "nope.db") == {}


@pytest.mark.parametrize("days", [1, 7, 30])
def test_window_size_is_injectable(tmp_path, days):
    rows = [("A", "AGENCYPR", TODAY, 100, meta("justice-newsroom"))]
    out = run(tmp_path, [WEB], rows)
    assert out["window_days"] == health.HEALTH_WINDOW_DAYS
    pipeline = make_pipeline_db(tmp_path / f"w{days}", rows)
    got = health.source_health([WEB], pipeline_db=pipeline,
                               fetch_db=tmp_path / "absent.db", today=TODAY,
                               window_days=days)
    assert got["window_days"] == days
    assert got["window_start"] == health._shift(TODAY, days - 1)
    assert got["sources"]["justice-newsroom"]["window_days"] == days

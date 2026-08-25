"""Collector-core tests: journal reconciliation, analyze triggers, the
/today data contract, collector state. Pure logic against tmp SQLite —
no network, no threads, no LLM."""

import datetime as dt
import functools
import json
import sqlite3

from conftest import DATE, LONG_TEXT, install_digest_day_default, seed_corpus, seed_item

from fapd import collect, config
from fapd.sync import publication_date

NOW = dt.datetime(2026, 7, 30, 12, 0, tzinfo=dt.UTC)


def seed_email_item(conn, package_id, granule_id):
    seed_item(conn, package_id, granule_id, "AGENCYPR", "PRESS",
              metadata={"channel": "email", "source_id": "treasury-email"})


def seed_summary_for(conn, package_id, granule_id, created="2026-07-23T01:00:00Z"):
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " inclusion_rule, summary, created_at)"
        " VALUES (?, ?, ?, 'official', 'FR-SEL-01', 'A summary.', ?)",
        (package_id, granule_id, config.PROMPT_VERSION, created),
    )
    conn.commit()


# ------------------------------------------------------------- journaling --


def test_journal_new_is_class_scoped_and_idempotent(conn):
    seed_corpus(conn)                                   # govinfo classes
    seed_item(conn, "AGENCYPR-web-1", "", "AGENCYPR", "PRESS",
              metadata={"source_id": "gao-reports"})    # agency (web)
    seed_email_item(conn, "AGENCYPR-mail-1", "")        # email channel

    assert collect.journal_new(conn, "agency", "c1") == 1
    assert collect.journal_new(conn, "email", "c1") == 1
    n_gov = collect.journal_new(conn, "govinfo", "c1")
    assert n_gov > 10  # the corpus spans every rule

    # reconciliation is idempotent — a second cycle inserts nothing
    assert collect.journal_new(conn, "agency", "c2") == 0
    assert collect.journal_new(conn, "govinfo", "c2") == 0

    by_class = dict(conn.execute(
        "SELECT source_class, COUNT(*) FROM item_journal GROUP BY 1"))
    assert by_class["agency"] == 1 and by_class["email"] == 1
    row = conn.execute(
        "SELECT source_id, digest_date FROM item_journal"
        " WHERE package_id = 'AGENCYPR-mail-1'").fetchone()
    assert row["source_id"] == "treasury-email" and row["digest_date"] == DATE


def test_journal_model_events_after_summaries(conn):
    seed_corpus(conn)
    collect.journal_new(conn, "govinfo", "c1")
    seed_summary_for(conn, "FR-2026-07-23", "2026-10003")
    assert collect.journal_model_events(conn, "c2") == 1
    assert collect.journal_model_events(conn, "c3") == 0  # idempotent
    row = conn.execute(
        "SELECT source_class, digest_date FROM item_journal"
        " WHERE event = 'summarized'").fetchone()
    assert row["source_class"] == "govinfo" and row["digest_date"] == DATE


# ---------------------------------------------------------------- trigger --


def test_trigger_fires_on_full_batch(conn):
    seed_corpus(conn)  # 13 selected, 0 summarized -> >= 6 pending
    assert collect.trigger_fires(conn, DATE, now=NOW) is True


def test_trigger_holds_below_batch_until_age_bound(conn):
    # one pending item, freshly extracted -> hold
    seed_item(conn, "CREC-2026-07-23", "PgS1", "CREC", "SENATE", LONG_TEXT)
    conn.execute("UPDATE extracted_texts SET extracted_at = ?",
                 (NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),))
    conn.commit()
    assert collect.trigger_fires(conn, DATE, now=NOW) is False
    # same item, older than the latency bound -> fire
    late = NOW + dt.timedelta(minutes=config.ANALYZE_MAX_LATENCY_MIN + 5)
    assert collect.trigger_fires(conn, DATE, now=late) is True


def test_trigger_respects_min_interval_spacing(conn):
    seed_corpus(conn)
    collect.record_state(conn, "analyze", ok=True)   # cycle just ran (real now)
    soon = dt.datetime.now(dt.UTC) + dt.timedelta(
        minutes=config.ANALYZE_MIN_INTERVAL_MIN - 5)
    assert collect.trigger_fires(conn, DATE, now=soon) is False
    later = dt.datetime.now(dt.UTC) + dt.timedelta(
        minutes=config.ANALYZE_MIN_INTERVAL_MIN + 5)
    assert collect.trigger_fires(conn, DATE, now=later) is True


def test_trigger_never_fires_with_nothing_pending(conn):
    seed_item(conn, "FR-2026-07-23", "2026-10003", "FR", "PRORULE",
              metadata={"summary": "A proposed rule."})
    seed_summary_for(conn, "FR-2026-07-23", "2026-10003")
    assert collect.trigger_fires(conn, DATE, now=NOW) is False


def test_dates_with_pending(conn):
    seed_corpus(conn)
    collect.journal_new(conn, "govinfo", "c1")
    # the corpus is a fixed historical date, so ask without the age bound
    assert DATE in collect.dates_with_pending(conn, max_age_days=10_000)


def test_analyze_scope_excludes_days_we_will_never_publish(conn):
    """We do not publish post-dated digests, so a day past the window is
    left pending and disclosed rather than bought: on 2026-07-30 the
    worker wrote 184 summaries across eleven dates back to 2024-06-18
    while the digest day itself received none."""
    seed_corpus(conn)
    collect.journal_new(conn, "govinfo", "c1")
    assert collect.dates_with_pending(conn) == []          # DATE is historical

    today = publication_date()
    conn.execute(
        "INSERT INTO item_journal (observed_at, source_class, package_id,"
        " granule_id, collection, digest_date, event) VALUES"
        " ('x', 'govinfo', 'P-NEW', 'G', 'FR', ?, 'ingested')", (today,))
    conn.commit()
    assert collect.dates_with_pending(conn) == [today]


# ------------------------------------------------------------ today_status --


def test_today_status_contract(conn):
    seed_corpus(conn)
    collect.journal_new(conn, "govinfo", "c1")
    seed_summary_for(conn, "FR-2026-07-23", "2026-10003")

    status = collect.today_status(conn, DATE)
    assert status["date"] == DATE
    assert status["last_observed_at"] is not None
    assert status["counts"]["FR/PRORULE"] == 1
    by_key = {(i["package_id"], i["granule_id"]): i for i in status["items"]}
    summarized = by_key[("FR-2026-07-23", "2026-10003")]
    assert summarized["summary"] == "A summary."
    assert summarized["summary_method"] == "official"
    unsummarized = by_key[("CREC-2026-07-23", "PgS1")]
    assert unsummarized["summary"] is None
    assert status["pending_llm"] == 12  # 13 selected - 1 summarized


def test_today_status_empty_day(conn):
    status = collect.today_status(conn, "2020-01-01")
    assert status["items"] == [] and status["pending_llm"] == 0
    assert status["last_observed_at"] is None


# ------------------------------------------------------------ record_state --


def _noop_ctx():
    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    return _Ctx()


def make_supervisor(tmp_path, monkeypatch, *, llm_enabled=False, poll=None,
                    registry=None, today_builder=None):
    from fapd import db

    db_path = tmp_path / "meta.db"

    def conn_factory():
        return install_digest_day_default(db.connect(db_path))

    # /today writes must never leave the test sandbox.
    monkeypatch.setattr(config, "SITE_DIR", tmp_path / "site")
    if today_builder is None:
        def today_builder(conn, *, date=None):
            return {"date": date, "items": 0, "pending_llm": 0,
                    "out_dir": None}

    monkeypatch.setattr(config, "IMAP_HOST", "x")
    monkeypatch.setattr(config, "IMAP_USER", "x")
    monkeypatch.setattr(config, "IMAP_PASSWORD", "x")
    sup = collect.Supervisor(
        registry=registry or list,
        conn_factory=conn_factory,
        govinfo_factory=_noop_ctx, agency_factory=_noop_ctx,
        wayback_factory=_noop_ctx, mailbox_factory=_noop_ctx,
        poll=poll or (lambda mbox, c, e: []),
        llm_factory=_noop_ctx, llm_enabled=llm_enabled,
        today_builder=today_builder,
    )
    return sup, conn_factory


def test_supervisor_run_once_cycles_every_worker(tmp_path, monkeypatch):
    # Stub the govinfo cycle's internals (sync/extract are heavy); email
    # and analyze run their real cycle logic against fakes.
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    monkeypatch.setattr(collect.GovinfoWorker, "cycle",
                        lambda self, conn, cid: {"stubbed": True})
    results = sup.run_once()
    assert results["govinfo"] == {"stubbed": True}
    assert results["email"]["configured"] is True
    assert results["analyze"] == {"dates": 0, "summarized": 0, "plain": 0}
    conn = conn_factory()
    workers = {r["worker"]: r for r in conn.execute("SELECT * FROM collector_state")}
    assert {"govinfo", "email", "analyze", "render"} <= set(workers)
    assert all(w["consecutive_errors"] == 0 for w in workers.values())
    conn.close()


def test_supervisor_worker_failure_is_contained(tmp_path, monkeypatch):
    def broken_poll(mbox, c, e):
        raise ConnectionError("imap down")

    sup, conn_factory = make_supervisor(tmp_path, monkeypatch, poll=broken_poll)
    monkeypatch.setattr(collect.GovinfoWorker, "cycle",
                        lambda self, conn, cid: {})
    results = sup.run_once()   # must not raise
    assert results["email"] is None
    assert results["analyze"] is not None  # later workers still ran
    conn = conn_factory()
    row = conn.execute(
        "SELECT consecutive_errors, last_result FROM collector_state"
        " WHERE worker = 'email'").fetchone()
    assert row["consecutive_errors"] == 1
    assert "imap down" in row["last_result"]
    conn.close()


def test_supervisor_builds_one_worker_per_agency_host(tmp_path, monkeypatch):
    def registry():
        return [
            {"id": "a", "status": "active", "type": "rss",
             "urls": {"feed": "https://www.gao.gov/rss.xml"}},
            {"id": "b", "status": "active", "type": "rss",
             "urls": {"feed": "https://www.nasa.gov/rss.xml"}},
            {"id": "c", "status": "planned", "type": "rss",
             "urls": {"feed": "https://x.gov/rss.xml"}},      # not active: no worker
            {"id": "d", "status": "active", "type": "email",
             "sender": "x@x.gov", "urls": {"home": "https://x.gov"}},  # email: no host worker
        ]
    sup, _ = make_supervisor(tmp_path, monkeypatch, registry=registry)
    host_workers = [w.name for w in sup.workers if w.name.startswith("host:")]
    assert len(host_workers) == 2
    assert any("gao.gov" in n for n in host_workers)


def test_agency_backpressure_doubles_interval(tmp_path, monkeypatch):
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    worker = collect.AgencyHostWorker(sup, "www.gao.gov", [], 60)
    conn = conn_factory()
    monkeypatch.setattr(sup, "agency_requests_today", lambda: 0)
    assert worker.interval_min(conn) == 60
    monkeypatch.setattr(
        sup, "agency_requests_today",
        lambda: int(config.MAX_AGENCY_REQUESTS_PER_DAY
                    * config.BUDGET_BACKPRESSURE_FRACTION))
    assert worker.interval_min(conn) == 120
    conn.close()


def test_analyze_worker_no_llm_mode_does_nothing(tmp_path, monkeypatch):
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch, llm_enabled=False)
    conn = conn_factory()
    seed_corpus(conn)
    collect.journal_new(conn, "govinfo", "c1")
    conn.close()
    worker = next(w for w in sup.workers if w.name == "analyze")
    stats = worker.run_cycle()
    assert stats == {"dates": 0, "summarized": 0, "plain": 0}


# ------------------------------------------------------------- EODWorker --


def test_eod_worker_absent_unless_enabled(tmp_path, monkeypatch):
    sup, _ = make_supervisor(tmp_path, monkeypatch)
    assert not any(w.name == "eod" for w in sup.workers)


def test_eod_fires_when_the_publication_day_ends_once_per_day(tmp_path,
                                                             monkeypatch):
    """EOD_ET_HOUR = 0 (operator, 2026-07-30): finalize a publication day
    as soon as it closes in Washington, and only once."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()

    # 00:05 ET on Jul 31 (= 04:05 UTC): Jul 30 has just ended
    just_after_midnight_et = dt.datetime(2026, 7, 31, 4, 5, tzinfo=dt.UTC)
    assert worker.eod_due(conn, now=just_after_midnight_et) == "2026-07-30"

    # 23:55 ET on Jul 30 (= 03:55 UTC Jul 31): Jul 30 is still open, so the
    # day on offer is the one before it, not Jul 30
    still_jul30_et = dt.datetime(2026, 7, 31, 3, 55, tzinfo=dt.UTC)
    assert worker.eod_due(conn, now=still_jul30_et) == "2026-07-29"

    collect.record_state(conn, "eod", ok=True,
                         stats={"ran": True, "date": "2026-07-30"})
    assert worker.eod_due(conn, now=just_after_midnight_et) is None
    assert worker.eod_due(
        conn, now=just_after_midnight_et + dt.timedelta(days=1)) == "2026-07-31"
    conn.close()


def test_eod_hour_gate_is_read_on_washingtons_clock(tmp_path, monkeypatch):
    """The gate is Eastern, not UTC — otherwise a fixed UTC hour would
    drift by an hour at every DST change."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()
    monkeypatch.setattr(config, "EOD_ET_HOUR", 6)   # 6am in Washington

    # 09:00 UTC = 05:00 EDT — before the gate in Eastern terms
    assert worker.eod_due(
        conn, now=dt.datetime(2026, 7, 31, 9, 0, tzinfo=dt.UTC)) is None
    # 11:00 UTC = 07:00 EDT — past it
    assert worker.eod_due(
        conn, now=dt.datetime(2026, 7, 31, 11, 0, tzinfo=dt.UTC)) == "2026-07-30"
    conn.close()


def test_eod_cycle_pauses_runs_finalizer_and_resumes(tmp_path, monkeypatch):
    calls = []
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: (
        calls.append(("finalize", date)) or 0)
    sup.evidence_runner = lambda: calls.append("evidence") or 0
    monkeypatch.setattr(config, "EVIDENCE_PUSH", True)
    worker = collect.EODWorker(sup, 10)
    paused_during = []
    sup.finalizer_runner = lambda date=None: (
        paused_during.append(sup.pause_event.is_set()),
        calls.append(("finalize", date)))[0] or 0

    conn = conn_factory()
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-07-29")
    stats = worker.cycle(conn, "c1")
    assert stats == {"ran": True, "date": "2026-07-29",
                     "finalized": "2026-07-29", "pushed": True}
    # the finalizer renders the day EOD chose, never one of its own
    assert ("finalize", "2026-07-29") in calls
    assert paused_during == [True]          # collectors were paused during finalize
    assert not sup.pause_event.is_set()     # and resumed after
    assert "evidence" in calls
    conn.close()


def test_eod_cycle_failure_resumes_and_records_error(tmp_path, monkeypatch):
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 1   # validation failed -> exit 1
    sup.evidence_runner = lambda: (_ for _ in ()).throw(AssertionError("must not push"))
    monkeypatch.setattr(config, "EVIDENCE_PUSH", True)
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-07-29")
    stats = worker.run_cycle()              # contained like any worker failure
    assert stats is None
    assert not sup.pause_event.is_set()     # resumed even on failure
    conn2 = conn_factory()
    row = conn2.execute(
        "SELECT consecutive_errors FROM collector_state WHERE worker='eod'").fetchone()
    assert row["consecutive_errors"] == 1
    conn2.close()
    conn.close()


def test_record_state_tracks_errors_and_recovery(conn):
    collect.record_state(conn, "email", ok=False, error="imap down")
    collect.record_state(conn, "email", ok=False, error="imap down")
    row = conn.execute("SELECT * FROM collector_state WHERE worker='email'").fetchone()
    assert row["consecutive_errors"] == 2 and row["last_ok_at"] is None
    assert json.loads(row["last_result"])["error"] == "imap down"

    collect.record_state(conn, "email", ok=True, stats={"items": 3})
    row = conn.execute("SELECT * FROM collector_state WHERE worker='email'").fetchone()
    assert row["consecutive_errors"] == 0 and row["last_ok_at"] is not None
    assert json.loads(row["last_result"]) == {"items": 3}


def _seed_today_journal(conn_factory, date):
    conn = conn_factory()
    conn.execute(
        "INSERT INTO item_journal (observed_at, source_class, package_id,"
        " granule_id, collection, digest_date, event) VALUES"
        " (?, 'govinfo', 'CREC-X', 'PgS1', 'CREC', ?, 'ingested')",
        (f"{date}T10:00:00Z", date))
    conn.commit()
    conn.close()


def test_render_worker_rebuilds_once_then_skips(tmp_path, monkeypatch):
    """The /today watermark contract: rebuild when the journal moved,
    skip when nothing new arrived (zero tokens either way)."""
    calls = []

    def builder(conn, *, date=None):
        (config.SITE_DIR).mkdir(parents=True, exist_ok=True)
        (config.SITE_DIR / "today.html").write_text("stub")
        calls.append(date)
        return {"date": date, "items": 1, "pending_llm": 0, "out_dir": None}

    sup, conn_factory = make_supervisor(tmp_path, monkeypatch,
                                        today_builder=builder)
    today = publication_date()   # the ET publication day, not UTC's
    _seed_today_journal(conn_factory, today)

    worker = next(w for w in sup.workers if w.name == "render")
    first = worker.run_cycle()
    assert first["rebuilt"] is True and calls == [today]
    second = worker.run_cycle()
    assert second["rebuilt"] is False and calls == [today]  # no new journal

    # a new journal row moves the watermark -> rebuild fires again
    conn = conn_factory()
    conn.execute(
        "INSERT INTO item_journal (observed_at, source_class, package_id,"
        " granule_id, collection, digest_date, event) VALUES"
        " (?, 'agency', 'AGENCYPR-Y', '', 'AGENCYPR', ?, 'ingested')",
        (f"{today}T11:00:00Z", today))
    conn.commit()
    conn.close()
    third = worker.run_cycle()
    assert third["rebuilt"] is True and len(calls) == 2


def test_render_worker_rebuilds_when_artifact_missing(tmp_path, monkeypatch):
    """A wiped site volume (F-009 territory) must not leave /today dead:
    matching watermark with no today.html on disk still rebuilds."""
    calls = []

    def builder(conn, *, date=None):
        calls.append(date)  # deliberately does NOT create today.html
        return {"date": date, "items": 0, "pending_llm": 0, "out_dir": None}

    sup, _conn_factory = make_supervisor(tmp_path, monkeypatch,
                                         today_builder=builder)
    worker = next(w for w in sup.workers if w.name == "render")
    worker.run_cycle()
    worker.run_cycle()
    assert len(calls) == 2  # every cycle rebuilds while the file is absent


def test_eod_targets_the_publication_day_that_just_closed(conn):
    """The finalizer's target is computed from Eastern, so it finalizes
    the publication day that actually closed — and a DST shift cannot
    move it. At 09:00 UTC (05:00 ET) on Jul 31, that day is Jul 30."""
    worker = collect.EODWorker.__new__(collect.EODWorker)
    at_9utc = dt.datetime(2026, 7, 31, 9, 0, tzinfo=dt.UTC)
    assert worker.eod_due(conn, at_9utc) == "2026-07-30"

    # winter (EST): 09:00 UTC is 04:00 ET, same reasoning
    assert worker.eod_due(
        conn, dt.datetime(2026, 1, 15, 9, 0, tzinfo=dt.UTC)) == "2026-01-14"

    # once recorded, the same day does not refire
    collect.record_state(conn, "eod", ok=True,
                         stats={"ran": True, "date": "2026-07-30"})
    assert worker.eod_due(conn, at_9utc) is None


def test_our_own_budget_pause_is_not_a_collector_error(tmp_path, monkeypatch):
    """Hitting a limit we imposed on ourselves is the policy working.
    Recorded as an error it inflated the worker's backoff and — once the
    source-health page began reading consecutive_errors — published the
    publisher as degraded because we were pacing ourselves."""
    from fapd.client import BudgetExceededError

    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)

    def refuse(self, conn, cycle_id):
        raise BudgetExceededError("501 govinfo requests in the last hour")

    monkeypatch.setattr(collect.GovinfoWorker, "cycle", refuse)
    worker = next(w for w in sup.workers if w.name == "govinfo")
    assert worker.run_cycle() == {"paused": "budget"}

    conn = conn_factory()
    row = conn.execute(
        "SELECT consecutive_errors, last_ok_at, last_result FROM"
        " collector_state WHERE worker = 'govinfo'").fetchone()
    assert row["consecutive_errors"] == 0        # not a failure
    assert row["last_ok_at"] is not None         # the worker is alive
    assert json.loads(row["last_result"])["paused"] == "budget"
    conn.close()

    # a real fault still counts
    monkeypatch.setattr(collect.GovinfoWorker, "cycle",
                        lambda self, c, i: (_ for _ in ()).throw(
                            ConnectionError("socket")))
    worker.run_cycle()
    conn = conn_factory()
    assert conn.execute(
        "SELECT consecutive_errors FROM collector_state WHERE worker='govinfo'"
    ).fetchone()[0] == 1
    conn.close()


def test_source_health_refreshes_on_a_clock_not_the_journal(tmp_path,
                                                            monkeypatch):
    """A source that starts failing journals nothing, so the watermark
    trigger that drives /today would refresh health for every case except
    the one the page exists to show. Health runs on its own clock."""
    calls = []
    sup, _conn_factory = make_supervisor(
        tmp_path, monkeypatch, today_builder=lambda c, date=None: {
            "date": date, "items": 0, "pending_llm": 0, "out_dir": None})
    monkeypatch.setattr(sup, "sources_builder",
                        lambda: calls.append(1) or {"built": True})
    worker = next(w for w in sup.workers if w.name == "render")

    first = worker.run_cycle()
    assert first["health_refreshed"] is True and len(calls) == 1

    # a second cycle with nothing new in the journal still must not
    # refresh again immediately — the clock, not the watermark, governs
    second = worker.run_cycle()
    assert second["health_refreshed"] is False and len(calls) == 1
    assert second["health_at"] == first["health_at"]   # stamp carried over

    # ...but once the interval elapses it refreshes even though the
    # journal never moved, which is the whole point
    monkeypatch.setattr(config, "SOURCE_HEALTH_REFRESH_MIN", 0)
    third = worker.run_cycle()
    assert third["health_refreshed"] is True and len(calls) == 2


def test_health_refresh_failure_never_costs_the_live_page(tmp_path,
                                                          monkeypatch):
    """Reporting on our own health is the least important thing the
    render worker does; it must not be able to break the page."""
    sup, _ = make_supervisor(
        tmp_path, monkeypatch, today_builder=lambda c, date=None: {
            "date": date, "items": 3, "pending_llm": 0, "out_dir": None})

    def boom():
        raise RuntimeError("two databases walked into a bar")

    monkeypatch.setattr(sup, "sources_builder", boom)
    worker = next(w for w in sup.workers if w.name == "render")
    out = worker.run_cycle()
    assert out["rebuilt"] is True and out["items"] == 3   # page still built
    assert out["health_refreshed"] is False


def test_render_worker_persists_health_labels(tmp_path, monkeypatch):
    """Each health refresh upserts the label into source_health_state —
    the table a downstream assessment layer watches for transitions
    ('health-change'). Wired through the render worker's own clock, on
    the same writable connection the worker already holds."""
    from fapd import health

    reg_entry = {
        "id": "justice-newsroom", "name": "DOJ newsroom", "status": "active",
        "type": "rss", "branch": "executive", "tier": 1,
        "parent_org": "Department of Justice",
        "urls": {"feed": "https://feeds.example.gov/press.xml"},
    }
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch,
                                        registry=lambda: [reg_entry])
    # health reads the pipeline/fetch DBs by path; point both inside the
    # sandbox (meta.db is the very database the worker writes state to)
    monkeypatch.setattr(config, "PIPELINE_DB", tmp_path / "meta.db")
    monkeypatch.setattr(config, "FETCH_LOG_DB", tmp_path / "absent-fetch.db")
    monkeypatch.setattr(sup, "sources_builder", lambda: {"built": True})
    worker = next(w for w in sup.workers if w.name == "render")
    out = worker.run_cycle()
    assert out["health_refreshed"] is True

    conn = conn_factory()
    state = health.health_state(conn)
    conn.close()
    # nothing ingested and nothing requested in the sandbox: NO_DATA —
    # a label like any other, and now a persisted, transition-detectable one
    assert state["justice-newsroom"]["label"] == health.NO_DATA
    assert (state["justice-newsroom"]["since"]
            == state["justice-newsroom"]["last_checked"])


def test_health_state_persistence_failure_never_costs_the_page(tmp_path,
                                                               monkeypatch):
    """Persisting labels is bookkeeping; it must never break the render
    cycle or the page, exactly like the health refresh itself."""
    from fapd import health

    sup, conn_factory = make_supervisor(
        tmp_path, monkeypatch,
        registry=lambda: [{"id": "x", "status": "active", "type": "rss",
                           "name": "X", "branch": "executive", "tier": 1,
                           "parent_org": "X", "urls": {}}],
        today_builder=lambda c, date=None: {"date": date, "items": 3,
                                            "pending_llm": 0, "out_dir": None})
    monkeypatch.setattr(sup, "sources_builder", lambda: {"built": True})

    def boom(*a, **k):
        raise RuntimeError("the databases are on fire")

    monkeypatch.setattr(health, "source_health", boom)
    worker = next(w for w in sup.workers if w.name == "render")
    out = worker.run_cycle()
    assert out["rebuilt"] is True and out["items"] == 3
    assert out["health_refreshed"] is True   # the page refresh still counted

    conn = conn_factory()
    assert health.health_state(conn) == {}   # nothing persisted, no crash
    conn.close()


def test_an_item_we_keep_failing_stops_being_pending_work(conn):
    """GUIDE §6 r14's ceiling was per RUN, and the collector runs analyze
    every 15 minutes per pending date — so an unsummarizable item was
    retried forever. Measured 2026-07-31 before this fix: 1,345 single
    retries, 39,712,610 input tokens, 60% of the day's spend."""
    seed_corpus(conn)
    before = collect.pending_map_items(conn, DATE)
    assert before, "corpus should offer pending work"
    item = before[0]

    for n in range(1, config.MAX_ITEM_SUMMARY_ATTEMPTS + 1):
        conn.execute(
            "INSERT INTO summary_attempts (package_id, granule_id,"
            " prompt_version, layer, attempts, last_at)"
            " VALUES (?, ?, ?, 'map', ?, 'x')"
            " ON CONFLICT (package_id, granule_id, prompt_version, layer)"
            " DO UPDATE SET attempts = excluded.attempts",
            (item["package_id"], item["granule_id"], config.PROMPT_VERSION, n))
        conn.commit()
        still = {(i["package_id"], i["granule_id"])
                 for i in collect.pending_map_items(conn, DATE)}
        key = (item["package_id"], item["granule_id"])
        if n < config.MAX_ITEM_SUMMARY_ATTEMPTS:
            assert key in still, f"attempt {n} should still be retried"
        else:
            assert key not in still, "at the ceiling it becomes a disclosed gap"

    # the rest of the day is untouched — one stuck item must not stall others
    assert len(collect.pending_map_items(conn, DATE)) == len(before) - 1


def test_eod_does_not_forget_that_it_finalized(tmp_path, monkeypatch):
    """run_cycle records whatever cycle() returns, so a bare
    {"ran": False} erased the proof that the day was finalized — eod_due
    then saw no date and re-ran the whole pipeline. Measured 2026-08-02:
    four full runs and four duplicate evidence commits in three hours."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 0
    sup.evidence_runner = lambda: 0
    worker = next(w for w in sup.workers if w.name == "eod") \
        if any(w.name == "eod" for w in sup.workers) else collect.EODWorker(sup, 10)
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-07-29")
    first = worker.run_cycle()
    assert first["ran"] is True and first["finalized"] == "2026-07-29"

    # a later cycle with nothing due must PRESERVE the marker
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: None)
    second = worker.run_cycle()
    assert second["ran"] is False
    assert second["finalized"] == "2026-07-29", \
        "the no-op cycle erased the proof the day was finalized"

    conn = conn_factory()
    import json as _json
    stored = _json.loads(conn.execute(
        "SELECT last_result FROM collector_state WHERE worker='eod'"
    ).fetchone()[0])
    assert stored["finalized"] == "2026-07-29"
    conn.close()


def test_eod_is_not_due_again_after_a_no_op_cycle(tmp_path, monkeypatch):
    """The real regression: finalize, idle, then ask again. Before the
    fix the idle cycle wiped the marker and the day re-fired."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 0
    sup.evidence_runner = lambda: 0
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()

    at = dt.datetime(2026, 8, 1, 4, 5, tzinfo=dt.UTC)   # 00:05 ET Aug 1
    assert worker.eod_due(conn, at) == "2026-07-31"
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-07-31")
    worker.run_cycle()
    monkeypatch.undo()

    worker2 = collect.EODWorker(sup, 10)
    worker2.run_cycle()                       # an idle cycle in between
    assert worker2.eod_due(conn, at) is None, "the day re-fired after idling"
    conn.close()


def test_eod_marker_survives_the_error_path(tmp_path, monkeypatch):
    """Review D5, the incident's remaining half: record_state(ok=False)
    replaces last_result wholesale, exactly as the no-op return used to.
    The finalized marker now lives in its own column, so a later FAILING
    cycle must not erase the proof that an earlier day was finalized."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 0
    sup.evidence_runner = lambda: 0
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()

    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-07-31")
    worker.run_cycle()                                  # 07-31 finalized
    monkeypatch.undo()

    sup.finalizer_runner = lambda date=None: 1          # now everything fails
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-08-01")
    assert worker.run_cycle() is None                   # error path taken
    monkeypatch.undo()

    at = dt.datetime(2026, 8, 1, 4, 5, tzinfo=dt.UTC)   # 00:05 ET Aug 1
    assert worker.eod_due(conn, at) is None, \
        "the error write erased the finalized marker for 07-31"
    row = conn.execute("SELECT finalized_date FROM collector_state"
                       " WHERE worker = 'eod'").fetchone()
    assert row["finalized_date"] == "2026-07-31"
    # and the failing day is still retried — one failure is not a halt
    at2 = dt.datetime(2026, 8, 2, 4, 5, tzinfo=dt.UTC)  # 00:05 ET Aug 2
    assert worker.eod_due(conn, at2) == "2026-08-01"
    conn.close()


def test_eod_hard_stop_after_repeated_finalizer_failures(
        tmp_path, monkeypatch, caplog):
    """Review D5: a digest that persistently fails must not buy a full
    pipeline run every backoff interval forever. At the attempt ceiling
    the day halts as a loudly disclosed gap."""
    import logging as _logging

    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 1
    sup.evidence_runner = lambda: 0
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()
    at = dt.datetime(2026, 8, 2, 4, 5, tzinfo=dt.UTC)   # 00:05 ET Aug 2

    with caplog.at_level(_logging.ERROR, logger="fapd.collect"):
        for _ in range(config.EOD_MAX_FINALIZE_ATTEMPTS):
            assert worker.eod_due(conn, at) == "2026-08-01", \
                "still due before the ceiling"
            monkeypatch.setattr(worker, "eod_due",
                                lambda c, now=None: "2026-08-01")
            worker.run_cycle()
            monkeypatch.undo()

    assert worker.eod_due(conn, at) is None, "the ceiling did not halt the day"
    assert "HALTED" in caplog.text, "the halt must be loudly disclosed"
    row = conn.execute(
        "SELECT finalize_target, finalize_attempts, finalized_date"
        " FROM collector_state WHERE worker = 'eod'").fetchone()
    assert row["finalize_target"] == "2026-08-01"
    assert row["finalize_attempts"] == config.EOD_MAX_FINALIZE_ATTEMPTS
    assert row["finalized_date"] is None, "a halted day is not a finalized day"

    # The halt is per target day: the next day still gets its fair try.
    at3 = dt.datetime(2026, 8, 3, 4, 5, tzinfo=dt.UTC)  # 00:05 ET Aug 3
    assert worker.eod_due(conn, at3) == "2026-08-02"
    conn.close()


def test_eod_success_clears_the_attempt_ladder(tmp_path, monkeypatch):
    """A failure followed by a success resets the ladder and writes the
    durable marker — a transient outage must not creep toward the halt."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.evidence_runner = lambda: 0
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()

    sup.finalizer_runner = lambda date=None: 1
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-08-01")
    worker.run_cycle()                                  # one failure
    sup.finalizer_runner = lambda date=None: 0
    worker.run_cycle()                                  # then success
    monkeypatch.undo()

    row = conn.execute(
        "SELECT finalized_date, finalize_target, finalize_attempts"
        " FROM collector_state WHERE worker = 'eod'").fetchone()
    assert row["finalized_date"] == "2026-08-01"
    assert row["finalize_target"] is None
    assert row["finalize_attempts"] == 0
    conn.close()


def test_eod_reads_pre_migration_json_marker(tmp_path, monkeypatch):
    """A row written before the column migration carries the marker only
    in last_result JSON; it must still count as finalized."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()
    conn.execute(
        "INSERT INTO collector_state (worker, last_result) VALUES ('eod', ?)",
        (json.dumps({"ran": True, "date": "2026-07-31"}),))
    conn.commit()
    at = dt.datetime(2026, 8, 1, 4, 5, tzinfo=dt.UTC)   # 00:05 ET Aug 1
    assert worker.eod_due(conn, at) is None
    conn.close()


def test_connect_migrates_pre_column_collector_state(tmp_path):
    """db.connect's additive micro-migration: a database created before
    the finalized_date columns gains them on connect, with existing rows
    intact (the IF NOT EXISTS DDL alone never alters an existing table)."""
    import sqlite3

    from fapd import db

    path = tmp_path / "old.db"
    raw = sqlite3.connect(path)
    raw.execute(
        "CREATE TABLE collector_state ("
        " worker TEXT PRIMARY KEY, last_cycle_at TEXT, last_ok_at TEXT,"
        " last_result TEXT, consecutive_errors INTEGER NOT NULL DEFAULT 0)")
    raw.execute(
        "INSERT INTO collector_state (worker, last_result)"
        " VALUES ('eod', '{\"finalized\": \"2026-07-31\"}')")
    raw.commit()
    raw.close()

    conn = db.connect(path)
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(collector_state)")}
    assert {"finalized_date", "finalize_target", "finalize_attempts"} <= cols
    row = conn.execute("SELECT last_result, finalized_date, finalize_attempts"
                       " FROM collector_state WHERE worker = 'eod'").fetchone()
    assert json.loads(row["last_result"])["finalized"] == "2026-07-31"
    assert row["finalized_date"] is None
    assert row["finalize_attempts"] == 0
    conn.close()


def test_journal_files_items_under_digest_day(tmp_path):
    """journal_new writes item_journal.digest_date from the package's
    digest_day (observation filing), so /today and the day views agree
    with the digest about what a day carries."""
    from fapd import db

    conn = install_digest_day_default(db.connect(tmp_path / "j.db"))
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued,"
        " last_modified, first_seen_at, digest_day) VALUES"
        " ('CREC-2026-08-04', 'CREC', '2026-08-04', 'x',"
        "  '2026-08-05T11:42:42Z', '2026-08-05')")
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, metadata, text, char_count, extracted_at,"
        " extractor_version) VALUES ('CREC-2026-08-04', 'g1', 'CREC',"
        " 'SENATE', '{}', 'body', 4, '2026-08-05T12:00:00Z', 1)")
    conn.commit()
    collect.journal_new(conn, "govinfo", "cycle-t")
    row = conn.execute(
        "SELECT digest_date FROM item_journal WHERE package_id="
        "'CREC-2026-08-04' AND event='ingested'").fetchone()
    assert row["digest_date"] == "2026-08-05"   # observation day, not 08-04


def test_every_adapter_collection_is_journaled_by_some_class():
    """A collection an adapter can produce must be classified in
    _CLASS_WHERE, or its items are ingested and never journaled — and
    /today, the day views and the journal accounting all read the
    journal. That is exactly what happened to PRESACT on 2026-08-06: 60
    rows stored, 0 journaled, the White House's executive orders
    invisible on the live page while sitting in the corpus.

    The old govinfo clause was a denylist, so a new collection silently
    fell into whichever class polled first and nothing failed. This test
    is the guard that was missing."""
    from fapd import agencies

    declared = {a.COLLECTION for a in agencies.ADAPTERS.values()}
    agency_class = set(collect._AGENCY_CLASS_COLLECTIONS)
    missing = declared - agency_class
    assert not missing, (
        f"adapter collections not classified as agency-class: {missing} — "
        "add them to _AGENCY_CLASS_COLLECTIONS or their items will never "
        "be journaled")


def test_agency_class_collections_are_not_also_govinfo():
    """The two classes must partition, not overlap: an item journaled
    twice would double-count in the coverage statement."""
    import re

    gov = collect._CLASS_WHERE["govinfo"]
    for coll in collect._AGENCY_CLASS_COLLECTIONS:
        assert re.search(rf"'{coll}'", gov), (
            f"{coll} is agency-class but the govinfo clause does not "
            "exclude it — it would be journaled by both workers")


def test_presact_items_are_journaled_as_agency_class(tmp_path):
    """The regression itself, pinned end to end."""
    from fapd import db

    conn = install_digest_day_default(db.connect(tmp_path / "p.db"))
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued,"
        " last_modified, first_seen_at, digest_day) VALUES"
        " ('PA-1','PRESACT','2026-08-06','x','2026-08-06T21:07:00Z','2026-08-06')")
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, title, metadata, text, char_count, extracted_at,"
        " extractor_version) VALUES ('PA-1','','PRESACT','EO',"
        " 'Ending Birth Tourism', '{\"source_id\":\"whitehouse-presidential-actions\"}',"
        " 'body', 4, '2026-08-06T21:10:00Z', 1)")
    conn.commit()
    assert collect.journal_new(conn, "agency", "cycle-t") == 1
    row = conn.execute(
        "SELECT collection, digest_date FROM item_journal"
        " WHERE package_id='PA-1' AND event='ingested'").fetchone()
    assert row["collection"] == "PRESACT"
    assert row["digest_date"] == "2026-08-06"
    # And the govinfo pass must NOT claim it a second time.
    assert collect.journal_new(conn, "govinfo", "cycle-t2") == 0


# ------------------------------------------- CREC titles on the live page --
# F-022 (2026-08-07): every CREC granule's <title> in the GPO ZIP is the
# ISSUE's own boilerplate, so parsers.crec._clean_title returns None for
# the whole collection and extracted_texts.title is NULL for every row.
# today_status selected only e.title and never joined granules, so the
# live page fell through to package_id — which for CREC is the issue,
# identical across the day: 155 items all reading "CREC-2026-08-06".


def _seed_crec_without_extracted_title(conn, granule_id, granule_title):
    """Reproduce the production shape: extracted title NULL, granules
    row carrying the real heading from the govinfo granules API."""
    seed_item(conn, "CREC-2026-07-23", granule_id, "CREC", "EXTENSIONS")
    conn.execute(
        "UPDATE extracted_texts SET title = NULL"
        " WHERE package_id = 'CREC-2026-07-23' AND granule_id = ?",
        (granule_id,))
    conn.execute(
        "INSERT OR REPLACE INTO granules"
        " (package_id, granule_id, granule_class, title, first_seen_at)"
        " VALUES ('CREC-2026-07-23', ?, 'EXTENSIONS', ?, '2026-07-24T00:00:00Z')",
        (granule_id, granule_title))
    conn.commit()


def test_today_status_falls_back_to_the_granule_title(conn):
    _seed_crec_without_extracted_title(
        conn, "PgE9", "HONORING THE SERVICE OF SAMUEL DOUGHERTY")
    collect.journal_new(conn, "govinfo", "c1")

    item = next(i for i in collect.today_status(conn, DATE)["items"]
                if i["granule_id"] == "PgE9")
    assert item["title"] == "HONORING THE SERVICE OF SAMUEL DOUGHERTY"


def test_today_status_prefers_the_extracted_title_when_there_is_one(conn):
    """granules.title is the fallback, not an override — collections that
    parse a title keep theirs."""
    seed_item(conn, "FR-2026-07-23", "2026-10001", "FR", "RULE")
    conn.execute(
        "INSERT OR REPLACE INTO granules"
        " (package_id, granule_id, granule_class, title, first_seen_at)"
        " VALUES ('FR-2026-07-23', '2026-10001', 'RULE', 'granule side',"
        " '2026-07-24T00:00:00Z')")
    conn.commit()
    collect.journal_new(conn, "govinfo", "c1")

    item = next(i for i in collect.today_status(conn, DATE)["items"]
                if i["granule_id"] == "2026-10001")
    assert item["title"] == "title of 2026-10001"


def test_today_status_title_is_none_when_no_record_carries_one(conn):
    """Honest null rather than a fabricated label — the presentation
    layer decides what to show, and today.json stays truthful."""
    seed_item(conn, "CREC-2026-07-23", "PgE8", "CREC", "EXTENSIONS")
    conn.execute("UPDATE extracted_texts SET title = NULL"
                 " WHERE granule_id = 'PgE8'")
    conn.commit()
    collect.journal_new(conn, "govinfo", "c1")

    item = next(i for i in collect.today_status(conn, DATE)["items"]
                if i["granule_id"] == "PgE8")
    assert item["title"] is None


# ------------------------------------------- evidence-push durable state --
# F-021 (2026-08-07): the push failed and nothing recorded it. The eod row
# read finalize_attempts=0 — a clean success by every durable measure —
# while the digest served all day and the repository never received it.


def _eod_row(conn):
    return conn.execute(
        "SELECT * FROM collector_state WHERE worker = 'eod'").fetchone()


def _push_worker(tmp_path, monkeypatch, *, push_rc):
    """A worker whose finalizer succeeds and whose evidence push returns
    push_rc, with FAPD_EVIDENCE_PUSH on."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 0
    sup.evidence_runner = lambda: push_rc
    monkeypatch.setattr(config, "EVIDENCE_PUSH", True)
    return collect.EODWorker(sup, 10), conn_factory()


def test_a_failed_evidence_push_is_recorded_durably(tmp_path, monkeypatch):
    worker, conn = _push_worker(tmp_path, monkeypatch, push_rc=4)
    worker.cycle(conn, "c1")

    row = _eod_row(conn)
    assert row["evidence_push_error"] == "exit 4"   # the rebase-conflict code
    assert row["evidence_push_attempts"] == 1
    assert row["evidence_pushed_at"] is None
    conn.close()


def test_the_day_is_still_finalized_when_the_push_fails(tmp_path, monkeypatch):
    """Finalizing and publishing to the repository are separate gates. The
    digest is rendered, validated and live — re-finalizing would re-render
    and re-spend tokens for a day already paid for."""
    worker, conn = _push_worker(tmp_path, monkeypatch, push_rc=5)
    worker.cycle(conn, "c1")

    row = _eod_row(conn)
    assert row["finalized_date"] is not None
    assert row["finalize_attempts"] == 0
    assert row["evidence_push_error"] == "exit 5"
    conn.close()


def test_a_pending_push_retries_on_the_next_cycle(tmp_path, monkeypatch):
    """eod_due returns None once the day is finalized, so before this the
    next attempt was the NEXT DAY's EOD — which failed identically."""
    worker, conn = _push_worker(tmp_path, monkeypatch, push_rc=5)
    worker.cycle(conn, "c1")
    assert _eod_row(conn)["evidence_push_attempts"] == 1

    calls = []
    worker.sup.evidence_runner = lambda: calls.append("push") or 0

    def _must_not_finalize(date=None):
        raise AssertionError("the retry must push, never re-run the finalizer")

    worker.sup.finalizer_runner = _must_not_finalize
    result = worker.cycle(conn, "c2")

    assert calls == ["push"]
    assert result["pushed"] is True
    row = _eod_row(conn)
    assert row["evidence_push_error"] is None
    assert row["evidence_push_attempts"] == 0
    assert row["evidence_pushed_at"] is not None
    conn.close()


def test_the_evidence_retry_ladder_stops_and_stays_disclosed(tmp_path,
                                                             monkeypatch):
    worker, conn = _push_worker(tmp_path, monkeypatch, push_rc=5)
    worker.cycle(conn, "c1")                    # attempt 1, on the finalize
    for i in range(6):
        worker.cycle(conn, f"r{i}")

    row = _eod_row(conn)
    assert row["evidence_push_attempts"] == config.EVIDENCE_PUSH_MAX_ATTEMPTS
    # a halt discloses; it does not clear the reason
    assert row["evidence_push_error"] == "exit 5"
    conn.close()


def test_a_clean_push_leaves_no_error_behind(tmp_path, monkeypatch):
    worker, conn = _push_worker(tmp_path, monkeypatch, push_rc=0)
    worker.cycle(conn, "c1")

    row = _eod_row(conn)
    assert row["evidence_pushed_at"] is not None
    assert row["evidence_push_error"] is None
    assert row["evidence_push_attempts"] == 0
    conn.close()


def test_the_retry_is_not_a_back_door_when_pushes_are_disabled(tmp_path,
                                                               monkeypatch):
    """The dev stack runs with FAPD_EVIDENCE_PUSH unset."""
    worker, conn = _push_worker(tmp_path, monkeypatch, push_rc=5)
    worker.cycle(conn, "c1")

    monkeypatch.setattr(config, "EVIDENCE_PUSH", False)

    def _must_not_push():
        raise AssertionError("must not push with evidence pushes disabled")

    worker.sup.evidence_runner = _must_not_push
    assert worker.cycle(conn, "c2") == {
        "ran": False, "finalized": _eod_row(conn)["finalized_date"]}
    conn.close()


# ---------------------------------------------- the mechanical floor (r15) --
# 2026-08-24: eight of ten finalizers halted on a provider quota, all three
# ladder rungs spent before the quota reset, and nine hand-rendered days
# never pushed because run_pipeline.py records nothing.


def test_eod_retry_spacing_is_the_ladder_not_the_error_doubling(tmp_path, monkeypatch):
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 1
    sup.evidence_runner = lambda: 0
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()
    monkeypatch.setattr(config, "EOD_FINALIZE_RETRY_MINUTES", (15, 60, 200))
    monkeypatch.setattr(config, "EOD_MAX_FINALIZE_ATTEMPTS", 4)

    assert worker.interval_min(conn) == 10, "idle: the base poll interval"
    assert worker.backoff_on_errors is False
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-08-21")
    seen = []
    for _ in range(4):
        worker.run_cycle()
        seen.append(worker.interval_min(conn))
    assert seen == [15, 60, 200, 200], "rungs, then the last rung repeats"
    conn.close()


def test_analyze_worker_leaves_finalized_days_alone(tmp_path, monkeypatch):
    """No backfill into a frozen day (operator ruling 2026-08-24): a
    summary paid for after the freeze would sit unpublished (F-013)."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch, llm_enabled=True)
    ran = []

    class _LLM:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    sup.llm_factory = _LLM
    monkeypatch.setattr(collect, "dates_with_pending",
                        lambda conn: ["2026-08-24", "2026-08-23", "2026-08-22"])
    monkeypatch.setattr(collect, "trigger_fires", lambda conn, date: True)
    from fapd import analyze
    monkeypatch.setattr(analyze, "run", lambda conn, c, date: (
        ran.append(date) or {"llm_summarized": 0, "official": 0}))
    monkeypatch.setattr(analyze, "run_plain", lambda conn, c, date: {"plain_written": 0})
    monkeypatch.setattr(collect, "journal_model_events", lambda conn, cid: 0)

    conn = conn_factory()
    collect.EODWorker(sup, 10)._record_finalized(conn, "2026-08-23")
    collect.AnalyzeWorker(sup, 15).cycle(conn, "c1")
    assert ran == ["2026-08-24"], "08-23 and earlier are frozen"
    conn.close()


def test_the_finalized_marker_only_moves_forward(tmp_path, monkeypatch):
    """A manual --finalize of an older day (a recovered HALT) must not
    rewind the marker, or every day in between comes due again."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()
    worker._record_finalized(conn, "2026-08-23")
    worker._record_finalized(conn, "2026-08-21")
    assert collect.last_finalized_date(conn) == "2026-08-23"
    worker._record_finalized(conn, "2026-08-24")
    assert collect.last_finalized_date(conn) == "2026-08-24"
    conn.close()


def test_finalize_now_runs_the_full_eod_path_for_the_named_day(tmp_path, monkeypatch):
    calls = []
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: calls.append(("finalize", date)) or 0
    sup.evidence_runner = lambda: calls.append("push") or 0
    monkeypatch.setattr(config, "EVIDENCE_PUSH", True)

    conn = conn_factory()
    # a halted ladder for that day does not block the operator
    w = collect.EODWorker(sup, 10)
    for _ in range(config.EOD_MAX_FINALIZE_ATTEMPTS):
        w._record_finalize_failure(conn, "2026-08-21")
    conn.close()

    result = sup.finalize_now("2026-08-21")
    assert result == {"ran": True, "date": "2026-08-21",
                      "finalized": "2026-08-21", "pushed": True}
    assert calls == [("finalize", "2026-08-21"), "push"]
    conn = conn_factory()
    row = conn.execute("SELECT * FROM collector_state WHERE worker='eod'").fetchone()
    assert row["finalized_date"] == "2026-08-21"
    assert row["finalize_attempts"] == 0 and row["finalize_target"] is None
    assert row["evidence_pushed_at"] is not None
    assert not sup.pause_event.is_set()
    conn.close()


def test_finalize_now_failure_is_recorded_not_raised(tmp_path, monkeypatch):
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: 1
    assert sup.finalize_now("2026-08-21") is None
    conn = conn_factory()
    row = conn.execute("SELECT * FROM collector_state WHERE worker='eod'").fetchone()
    assert row["finalize_target"] == "2026-08-21" and row["finalize_attempts"] == 1
    assert row["finalized_date"] is None
    conn.close()


def test_a_finalized_day_that_was_never_pushed_gets_pushed(tmp_path, monkeypatch):
    """The second shape of 'not in the repository': the marker is set,
    evidence_pushed_at is NULL, error is NULL — the row reads clean."""
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    monkeypatch.setattr(config, "EVIDENCE_PUSH", True)
    calls = []
    sup.evidence_runner = lambda: calls.append("push") or 0
    sup.finalizer_runner = lambda date=None: (_ for _ in ()).throw(
        AssertionError("must not re-run the finalizer"))
    worker = collect.EODWorker(sup, 10)
    conn = conn_factory()
    worker._record_finalized(conn, "2026-08-21")
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: None)
    result = worker.cycle(conn, "c1")
    assert calls == ["push"]
    assert result["pushed"] is True
    assert _eod_row(conn)["evidence_pushed_at"] is not None
    # and not again once it has been pushed
    result = worker.cycle(conn, "c2")
    assert calls == ["push"] and "pushed" not in result
    conn.close()


def test_supervisor_passes_no_llm_through_to_the_finalizer(tmp_path, monkeypatch):
    seen = {}

    def fake_run(cmd, cwd, check):
        seen["cmd"] = cmd
        return type("P", (), {"returncode": 0})()

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)
    sup, _ = make_supervisor(tmp_path, monkeypatch)
    sup.llm_enabled = False
    sup.finalizer_runner = functools.partial(collect._run_finalizer, no_llm=True)
    assert sup.finalizer_runner("2026-08-24") == 0
    assert seen["cmd"][-3:] == ["--date", "2026-08-24", "--no-llm"]
    sup.finalizer_runner = functools.partial(collect._run_finalizer, no_llm=False)
    sup.finalizer_runner("2026-08-24")
    assert "--no-llm" not in seen["cmd"]


# ------------------------------------------ a worker thread never dies --


def test_run_cycle_survives_a_connect_failure(tmp_path, monkeypatch, caplog):
    import logging as _logging

    sup, _ = make_supervisor(tmp_path, monkeypatch)
    worker = collect.EmailWorker(sup, 5)

    def boom():
        raise sqlite3.OperationalError("duplicate column name: extract_attempts")

    sup.conn_factory = boom
    with caplog.at_level(_logging.ERROR, logger="fapd.collect"):
        assert worker.run_cycle() is None
    assert "could not open the database" in caplog.text


def test_loop_survives_anything_and_keeps_going(tmp_path, monkeypatch, caplog):
    """The 2026-08-25 shape: an exception on the first iteration must not
    end the thread — the next iteration runs after the base interval."""
    import logging as _logging
    import threading

    sup, _ = make_supervisor(tmp_path, monkeypatch)
    worker = collect.EmailWorker(sup, 5)
    calls = []
    stop = threading.Event()

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("first iteration explodes")
        stop.set()
        return {}

    monkeypatch.setattr(worker, "run_cycle", flaky)
    monkeypatch.setattr(stop, "wait", lambda seconds: None)   # no real sleeping
    with caplog.at_level(_logging.ERROR, logger="fapd.collect"):
        worker.loop(stop)
    assert len(calls) == 2, "the loop ran again after the failure"
    assert "loop iteration failed" in caplog.text

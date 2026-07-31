"""Collector-core tests: journal reconciliation, analyze triggers, the
/today data contract, collector state. Pure logic against tmp SQLite —
no network, no threads, no LLM."""

import datetime as dt
import json

from conftest import DATE, LONG_TEXT, seed_corpus, seed_item

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
        return db.connect(db_path)

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
    sup.finalizer_runner = lambda: calls.append("finalize") or 0
    sup.evidence_runner = lambda: calls.append("evidence") or 0
    monkeypatch.setattr(config, "EVIDENCE_PUSH", True)
    worker = collect.EODWorker(sup, 10)
    paused_during = []
    sup.finalizer_runner = lambda: (
        paused_during.append(sup.pause_event.is_set()), calls.append("finalize"))[0] or 0

    conn = conn_factory()
    monkeypatch.setattr(worker, "eod_due", lambda c, now=None: "2026-07-29")
    stats = worker.cycle(conn, "c1")
    assert stats == {"ran": True, "date": "2026-07-29", "pushed": True}
    assert paused_during == [True]          # collectors were paused during finalize
    assert not sup.pause_event.is_set()     # and resumed after
    assert "evidence" in calls
    conn.close()


def test_eod_cycle_failure_resumes_and_records_error(tmp_path, monkeypatch):
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda: 1        # validation failed -> exit 1
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

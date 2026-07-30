"""Collector-core tests: journal reconciliation, analyze triggers, the
/today data contract, collector state. Pure logic against tmp SQLite —
no network, no threads, no LLM."""

import datetime as dt
import json

from conftest import DATE, LONG_TEXT, seed_corpus, seed_item

from fapd import collect, config

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
    assert DATE in collect.dates_with_pending(conn)


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
                    registry=None):
    from fapd import db

    db_path = tmp_path / "meta.db"

    def conn_factory():
        return db.connect(db_path)

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
    assert {"govinfo", "email", "analyze"} <= set(workers)
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

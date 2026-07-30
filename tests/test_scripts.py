"""First tests for the scripts/ layer (importable via conftest's sys.path
insert): digest.default_date and run_pipeline's stage wiring. Everything
external is stubbed — no network, no mailbox, no LLM."""

import datetime as dt
from pathlib import Path

import digest
import run_pipeline
from conftest import seed_item

from fapd import config

TODAY = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")


# ------------------------------------------------------------ default_date --


def test_default_date_picks_newest_complete_day(conn):
    seed_item(conn, "CREC-A", "Pg1", "CREC", "SENATE", date="2026-07-27")
    seed_item(conn, "CREC-B", "Pg1", "CREC", "SENATE", date="2026-07-28")
    assert digest.default_date(conn) == "2026-07-28"


def test_default_date_excludes_today(conn):
    # Today's record is incomplete until the day ends (worklog 2026-07-25):
    # a run must digest the newest day strictly before today.
    seed_item(conn, "CREC-A", "Pg1", "CREC", "SENATE", date="2026-07-28")
    seed_item(conn, "CREC-B", "Pg1", "CREC", "SENATE", date=TODAY)
    assert digest.default_date(conn) == "2026-07-28"


def test_default_date_empty_db_returns_none(conn):
    assert digest.default_date(conn) is None


def test_default_date_requires_extracted_data(conn):
    # A package without extracted text does not make a day digestible.
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued,"
        " last_modified, first_seen_at)"
        " VALUES ('CREC-X', 'CREC', '2026-07-28', 'x', 'x')")
    conn.commit()
    assert digest.default_date(conn) is None


# ------------------------------------------------------------- stage_email --


class FakeMailbox:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_stage_email_skips_when_unconfigured(conn, monkeypatch):
    monkeypatch.setattr(config, "IMAP_HOST", "")
    calls = []
    stats = run_pipeline.stage_email(conn, mailbox_factory=lambda: calls.append(1))
    assert stats["configured"] is False and stats["error"] is None
    assert calls == []  # the mailbox is never touched


def test_stage_email_aggregates_poll_results(conn, monkeypatch):
    for key in ("IMAP_HOST", "IMAP_USER", "IMAP_PASSWORD"):
        monkeypatch.setattr(config, key, "x")
    entries = [{"id": "a-email"}, {"id": "b-email"}]
    results = [{"messages": 2, "items": 3, "administrative": 1},
               {"messages": 1, "items": 1, "administrative": 0}]
    stats = run_pipeline.stage_email(
        conn, entries=entries, mailbox_factory=FakeMailbox,
        poll=lambda mbox, c, e: results)
    assert stats == {"configured": True, "subscriptions": 2, "bulletins": 3,
                     "items": 4, "administrative": 1, "error": None}


def test_stage_email_outage_reported_not_raised(conn, monkeypatch):
    # The pinned contract: a mailbox outage must not cost the rest of the
    # run — the gap is reported, not hidden, and no exception escapes.
    for key in ("IMAP_HOST", "IMAP_USER", "IMAP_PASSWORD"):
        monkeypatch.setattr(config, key, "x")

    def broken_poll(mbox, c, e):
        raise ConnectionError("imap down")

    stats = run_pipeline.stage_email(
        conn, entries=[], mailbox_factory=FakeMailbox, poll=broken_poll)
    assert stats["configured"] is True
    assert "imap down" in stats["error"]


# ------------------------------------------------------- main() wiring smoke --


def test_main_runs_stages_in_order_and_keys_exit_on_out_path(monkeypatch, tmp_path):
    order = []

    def rec(name, result=None):
        def _f(*a, **kw):
            order.append(name)
            return result
        return _f

    class FakeConn:
        def close(self):
            order.append("close")

    monkeypatch.setattr(run_pipeline.db, "connect", lambda: FakeConn())
    monkeypatch.setattr(run_pipeline.logging_setup, "setup", lambda **kw: None)
    monkeypatch.setattr(run_pipeline, "stage_sync", rec("sync", 42))
    monkeypatch.setattr(run_pipeline, "stage_agencies", rec("agencies", {}))
    monkeypatch.setattr(run_pipeline, "stage_email", rec("email", {}))
    monkeypatch.setattr(run_pipeline, "stage_extract", rec("extract", {}))
    monkeypatch.setattr(run_pipeline, "default_date", rec("date", "2026-07-28"))
    monkeypatch.setattr(
        run_pipeline, "stage_analyze",
        rec("analyze", {"before": (0, 0, 0), "after": (9, 9, 9)}))
    monkeypatch.setattr(
        run_pipeline, "stage_render",
        rec("render", (tmp_path / "2026-07-28.md", "PASSED")))
    monkeypatch.setattr(run_pipeline, "stage_site", rec("site", {"out_dir": tmp_path}))
    monkeypatch.setattr(run_pipeline, "detail_report", rec("report"))

    assert run_pipeline.main([]) == 0
    assert order == ["sync", "agencies", "email", "extract", "date",
                     "analyze", "render", "site", "report", "close"]


def test_main_exit_1_when_validation_fails(monkeypatch):
    class FakeConn:
        def close(self):
            pass

    monkeypatch.setattr(run_pipeline.db, "connect", lambda: FakeConn())
    monkeypatch.setattr(run_pipeline.logging_setup, "setup", lambda **kw: None)
    for name in ("stage_sync", "stage_agencies", "stage_email", "stage_extract"):
        monkeypatch.setattr(run_pipeline, name, lambda *a, **kw: {})
    monkeypatch.setattr(
        run_pipeline, "stage_analyze",
        lambda *a: {"before": (0, 0, 0), "after": (0, 0, 0)})
    monkeypatch.setattr(
        run_pipeline, "stage_render", lambda *a: (None, "FAILED: bad citation"))
    monkeypatch.setattr(run_pipeline, "stage_site", lambda: {"out_dir": Path(".")})
    monkeypatch.setattr(run_pipeline, "detail_report", lambda **kw: None)

    assert run_pipeline.main(["--date", "2026-07-28"]) == 1
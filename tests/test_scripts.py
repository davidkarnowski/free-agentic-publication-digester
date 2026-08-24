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

    class FakeLLMClient:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(run_pipeline.db, "connect", lambda: FakeConn())
    monkeypatch.setattr(run_pipeline.logging_setup, "setup", lambda **kw: None)
    monkeypatch.setattr(run_pipeline.llm, "LLMClient", lambda *a, **kw: FakeLLMClient())
    for name in ("stage_sync", "stage_agencies", "stage_email", "stage_extract"):
        monkeypatch.setattr(run_pipeline, name, lambda *a, **kw: {})
    monkeypatch.setattr(
        run_pipeline, "stage_analyze",
        lambda *a: {"before": (0, 0, 0), "after": (0, 0, 0)})
    monkeypatch.setattr(
        run_pipeline, "stage_render", lambda *a, **kw: (None, "FAILED: bad citation"))
    monkeypatch.setattr(run_pipeline, "stage_site", lambda: {"out_dir": Path(".")})
    monkeypatch.setattr(run_pipeline, "detail_report", lambda **kw: None)

    assert run_pipeline.main(["--date", "2026-07-28"]) == 1


# --------------------------------- stage_render / lexicon correction (r14a) --
# report.render()/find_lexicon_violation and analyze.correct_lexicon_violation
# are exercised directly in test_report.py / test_analyze.py; these pin
# stage_render's OWN orchestration — which of the two render() attempts and
# the correction call fire, in what order, and the fallback shape when a
# violation isn't attributable to an item. Everything is stubbed so this
# tests control flow only, not the underlying mechanics.


def test_stage_render_recovers_via_correction(conn, monkeypatch):
    calls = {"render": 0}

    def fake_render(c, date):
        calls["render"] += 1
        if calls["render"] == 1:
            raise run_pipeline.report.ValidationError(
                "banned term 'extreme' in generated prose")
        return Path("digests/2026-07-23.md")

    violation = {"package_id": "CREC-X", "granule_id": "G1",
                 "layer": "map", "term": "extreme"}
    corrected_with = {}
    monkeypatch.setattr(run_pipeline.report, "render", fake_render)
    monkeypatch.setattr(run_pipeline.report, "find_lexicon_violation",
                        lambda c, date: violation)
    monkeypatch.setattr(
        run_pipeline.analyze, "correct_lexicon_violation",
        lambda c, llm_client, **kw: corrected_with.update(kw) or {"outcome": "corrected"})

    out_path, validation = run_pipeline.stage_render(conn, "2026-07-23", llm_client=object())
    assert validation == "PASSED"
    assert out_path == Path("digests/2026-07-23.md")
    assert calls["render"] == 2  # the retry after correction
    assert corrected_with == violation


def test_stage_render_falls_back_when_violation_not_attributable(conn, monkeypatch):
    """A validation failure find_lexicon_violation can't pin to an item —
    compose-level prose, or a non-lexicon failure entirely — behaves
    exactly as before: no correction attempted, single render() call."""
    def fake_render(c, date):
        raise run_pipeline.report.ValidationError("bad citation")

    called = []
    monkeypatch.setattr(run_pipeline.report, "render", fake_render)
    monkeypatch.setattr(run_pipeline.report, "find_lexicon_violation",
                        lambda c, date: None)
    monkeypatch.setattr(run_pipeline.analyze, "correct_lexicon_violation",
                        lambda *a, **kw: called.append(1))

    out_path, validation = run_pipeline.stage_render(conn, "2026-07-23", llm_client=object())
    assert out_path is None
    assert validation == "FAILED: bad citation"
    assert called == []


def test_stage_render_no_correction_without_llm_client(conn, monkeypatch):
    """digest.py's standalone render path calls stage_render with no
    llm_client — correction must never fire there (analysis stays an
    optional, lazily-imported dependency of a report-only run)."""
    def fake_render(c, date):
        raise run_pipeline.report.ValidationError(
            "banned term 'extreme' in generated prose")

    called = []
    monkeypatch.setattr(run_pipeline.report, "render", fake_render)
    monkeypatch.setattr(
        run_pipeline.report, "find_lexicon_violation",
        lambda c, date: {"package_id": "X", "granule_id": "Y",
                         "layer": "map", "term": "extreme"})
    monkeypatch.setattr(run_pipeline.analyze, "correct_lexicon_violation",
                        lambda *a, **kw: called.append(1))

    out_path, _validation = run_pipeline.stage_render(conn, "2026-07-23")
    assert out_path is None
    assert called == []


def test_stage_render_reports_failure_when_correction_does_not_resolve_it(conn, monkeypatch):
    """A withdrawn (or still-corrected-elsewhere) item can leave the
    render failing for a different reason on the second attempt — this
    is reported exactly as an ordinary failure, not looped further (only
    ONE retry: no third render() call)."""
    calls = {"render": 0}

    def fake_render(c, date):
        calls["render"] += 1
        raise run_pipeline.report.ValidationError(
            "banned term 'extreme' in generated prose")

    monkeypatch.setattr(run_pipeline.report, "render", fake_render)
    monkeypatch.setattr(
        run_pipeline.report, "find_lexicon_violation",
        lambda c, date: {"package_id": "X", "granule_id": "Y",
                         "layer": "map", "term": "extreme"})
    monkeypatch.setattr(run_pipeline.analyze, "correct_lexicon_violation",
                        lambda *a, **kw: {"outcome": "withdrawn"})

    out_path, validation = run_pipeline.stage_render(conn, "2026-07-23", llm_client=object())
    assert out_path is None
    assert validation == "FAILED: banned term 'extreme' in generated prose"
    assert calls["render"] == 2  # the one bounded retry, then stop — no loop


# ---------------------------------------------------------- collect.py CLI --


def test_collect_once_exit_codes(monkeypatch):
    import collect as collect_cli

    class FakeSup:
        def __init__(self, results):
            self._results = results

        def run_once(self):
            return self._results

    monkeypatch.setattr(collect_cli, "Supervisor",
                        lambda **kw: FakeSup({"govinfo": {"ok": 1}, "email": {}}))
    monkeypatch.setattr(collect_cli.logging_setup, "setup", lambda **kw: None)
    assert collect_cli.main(["--once", "--no-llm"]) == 0

    monkeypatch.setattr(collect_cli, "Supervisor",
                        lambda **kw: FakeSup({"govinfo": None}))  # a failed worker
    assert collect_cli.main(["--once"]) == 1


def test_collect_cli_passes_flags_to_supervisor(monkeypatch):
    import collect as collect_cli

    captured = {}

    def fake_supervisor(**kw):
        captured.update(kw)

        class S:
            def run_once(self):
                return {}
        return S()

    monkeypatch.setattr(collect_cli, "Supervisor", fake_supervisor)
    monkeypatch.setattr(collect_cli.logging_setup, "setup", lambda **kw: None)
    collect_cli.main(["--once", "--no-llm", "--interval-email", "5"])
    assert captured["llm_enabled"] is False
    assert captured["intervals"] == {"email": 5}


# --------------------------------------------- federal publication day (§3) --


def test_publication_day_is_washingtons_not_utcs():
    """GUIDE §3 (amended 2026-07-30). Midnight UTC is 8pm Eastern, so a
    release observed at 20:20 ET on July 30 belongs to July 30 — dating
    it by UTC filed it under July 31, a day the government had not yet
    started."""
    import datetime as dt

    from fapd.sync import publication_date, publication_date_of

    evening = dt.datetime(2026, 7, 31, 0, 20, tzinfo=dt.UTC)   # 20:20 EDT 7/30
    assert evening.strftime("%Y-%m-%d") == "2026-07-31"         # what UTC said
    assert publication_date(evening) == "2026-07-30"            # what we now say

    # just after Eastern midnight the day does roll
    assert publication_date(
        dt.datetime(2026, 7, 31, 4, 1, tzinfo=dt.UTC)) == "2026-07-31"
    # winter: EST is UTC-5, so 05:00 UTC is still the previous day
    assert publication_date(
        dt.datetime(2026, 1, 15, 4, 30, tzinfo=dt.UTC)) == "2026-01-14"

    assert publication_date_of("2026-07-31T00:20:00Z") == "2026-07-30"
    assert publication_date_of("2026-07-31T00:20:00+00:00") == "2026-07-30"
    assert publication_date_of("not a stamp") is None
    assert publication_date_of("") is None


def test_default_date_uses_washingtons_day_not_utcs(monkeypatch):
    """Between 20:00 ET and midnight ET, UTC has already rolled over. This
    function was written when UTC *was* the day boundary and the 2026-07-30
    Eastern amendment missed it — so for four hours every day it treated
    the day still in progress as complete. On 2026-08-02 that published an
    Aug 1 digest at 22:39 ET on Aug 1."""
    import datetime as dt
    import tempfile
    from pathlib import Path

    import digest

    from fapd import db

    # a tiny corpus: one package per day
    tmp = Path(tempfile.mkdtemp())
    conn = db.connect(tmp / "m.db")
    for d in ("2026-07-31", "2026-08-01"):
        conn.execute("INSERT INTO packages (package_id, collection, date_issued,"
                     " last_modified, first_seen_at) VALUES (?, 'FR', ?, 'x', 'x')",
                     (f"P-{d}", d))
        conn.execute("INSERT INTO extracted_texts (package_id, granule_id,"
                     " collection, text, char_count, extracted_at,"
                     " extractor_version) VALUES (?, '', 'FR', 'b', 1, 'x', 1)",
                     (f"P-{d}",))
    conn.commit()

    # 02:39 UTC on Aug 2 == 22:39 ET on Aug 1: Aug 1 has NOT ended
    class FakeDT(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return dt.datetime(2026, 8, 2, 2, 39, tzinfo=dt.UTC)

    monkeypatch.setattr("fapd.sync.dt.datetime", FakeDT)
    assert digest.default_date(conn) == "2026-07-31", \
        "digested a publication day that had not ended"
    conn.close()


# ------------------------------------------ the mechanical floor (r15) --


def test_no_llm_flag_makes_every_client_the_null_backend(monkeypatch):
    from fapd import llm as _llm

    monkeypatch.setattr(run_pipeline, "NO_LLM", True)
    with run_pipeline.llm_client() as client:
        assert isinstance(client._backend, _llm.NullBackend)
        assert client.status()["unavailable"] == "disabled by operator"
    monkeypatch.setattr(run_pipeline, "NO_LLM", False)
    monkeypatch.setattr(run_pipeline.llm, "LLMClient", lambda *a, **kw: "real")
    assert run_pipeline.llm_client() == "real"


def test_stage_analyze_never_raises_for_a_provider(conn, monkeypatch):
    """One LLMError used to be exit 1 before render (2026-08-15..23)."""
    from fapd import finalize
    from fapd import llm as _llm

    class _Client:
        def __init__(self):
            self.unavailable = None

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def tokens_today(self):
            return (0, 0, 0)

        def status(self):
            return {"backend": "fake", "unavailable": self.unavailable,
                    "models_used": []}

    client = _Client()

    def fn_for(name):
        if name == "map":
            def _fail(conn, c, date):
                c.unavailable = "quota exhausted"
                raise _llm.ProviderUnavailableError("quota exhausted")
            return _fail
        return lambda conn, c, date: {"x": 1}

    monkeypatch.setattr(finalize, "_layer_fn", fn_for)
    out = run_pipeline.stage_analyze(conn, "2026-08-24", llm_client_factory=lambda: client)
    assert out["layers"]["map"] == "failed"
    assert out["layers"]["tags"] == "skipped"
    assert out["map"] is None and out["before"] == (0, 0, 0)


def test_main_accepts_no_llm(monkeypatch, tmp_path):
    class FakeConn:
        def close(self):
            pass

    monkeypatch.setattr(run_pipeline.db, "connect", lambda: FakeConn())
    monkeypatch.setattr(run_pipeline.logging_setup, "setup", lambda **kw: None)
    for name in ("stage_sync", "stage_agencies", "stage_email", "stage_extract",
                 "stage_day_view", "stage_source_text", "stage_insight"):
        monkeypatch.setattr(run_pipeline, name, lambda *a, **kw: {})
    monkeypatch.setattr(run_pipeline, "stage_analyze",
                        lambda *a, **kw: {"before": (0, 0, 0), "after": (0, 0, 0)})
    monkeypatch.setattr(run_pipeline, "stage_render",
                        lambda *a, **kw: (tmp_path / "d.md", "PASSED"))
    monkeypatch.setattr(run_pipeline, "stage_site", lambda: {"out_dir": tmp_path})
    monkeypatch.setattr(run_pipeline, "detail_report", lambda **kw: None)
    assert run_pipeline.main(["--date", "2026-08-24", "--no-llm"]) == 0
    assert run_pipeline.NO_LLM is True
    run_pipeline.NO_LLM = False

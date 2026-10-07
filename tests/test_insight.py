"""Developer-insight report tests (fapd.insight, GUIDE §3a dev-facing
surface): mechanical gathering from the three databases, deterministic
rendering, the labeled model-suggestions section, and the never-fail
wiring contract in run_pipeline."""

import datetime as dt
import json
import sqlite3

from conftest import DATE

from fapd import config, insight
from fapd.llm import LLMError


class FakeLLM:
    def __init__(self, reply=None):
        self.calls = []
        self.reply = reply if reply is not None else json.dumps(
            ["Investigate the 42% retry share on the map layer.",
             "Confirm the email worker's last_ok_at recovers overnight."])

    def complete(self, prompt, **kw):
        self.calls.append({"prompt": prompt, **kw})
        return {"text": self.reply, "input_tokens": 500, "output_tokens": 60,
                "model": "fake-haiku"}


def seed_ops(conn, tmp_path):
    """Journal + collector rows in the main DB, plus throwaway fetch and
    ledger DBs with today's traffic. Returns (fetch_db, ledger_db)."""
    conn.execute(
        "INSERT INTO item_journal (observed_at, source_class, package_id,"
        " granule_id, digest_date, event) VALUES"
        " ('x', 'govinfo', 'P1', 'G1', ?, 'ingested'),"
        " ('x', 'govinfo', 'P1', 'G1', ?, 'summarized'),"
        " ('x', 'agency',  'P2', '',   ?, 'ingested')", (DATE, DATE, DATE))
    conn.execute(
        "INSERT INTO collector_state (worker, last_ok_at, consecutive_errors)"
        " VALUES ('govinfo', '2026-07-23T09:00:00Z', 0), ('email', NULL, 3)")
    conn.commit()

    # Inside DATE's work window: the Eastern publication day plus the
    # finalizer grace. 18:00Z is 2 p.m. in Washington on DATE. Stamped
    # explicitly rather than with "now" — the report windows on the day
    # it reports, so seeding at wall-clock time would land outside it
    # for any DATE but today, which is exactly the bug this replaced.
    now = f"{DATE}T18:00:00Z"
    fetch_db = tmp_path / "fetch_log.db"
    f = sqlite3.connect(fetch_db)
    f.execute("CREATE TABLE fetch_log (ts_utc TEXT, client TEXT, status INTEGER)")
    f.execute("INSERT INTO fetch_log VALUES (?, 'govinfo', 200), (?, 'agency', 403)",
              (now, now))
    f.commit(); f.close()

    ledger_db = tmp_path / "llm_ledger.db"
    ldb = sqlite3.connect(ledger_db)
    ldb.execute("CREATE TABLE llm_calls (ts_utc TEXT, purpose TEXT,"
                " input_tokens INTEGER, output_tokens INTEGER, error TEXT)")
    ldb.execute(
        "INSERT INTO llm_calls VALUES (?, 'map:batch1', 30000, 900, NULL),"
        " (?, 'map:retry-single', 30000, 600, NULL),"
        " (?, 'compose:day', 2000, 300, 'LLMError: boom')", (now, now, now))
    ldb.commit(); ldb.close()
    return fetch_db, ledger_db


def test_gather_is_mechanical_and_complete(conn, tmp_path):
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    m = insight.gather(conn, DATE, fetch_db=fetch_db, ledger_db=ledger_db)
    assert m["digest_date"] == DATE
    assert {r["client"] for r in m["requests"]} == {"govinfo", "agency"}
    assert m["tokens"]["input_total"] == 62000
    assert m["tokens"]["retry_input"] == 30000
    assert m["tokens"]["retry_share_pct"] == 48.4
    assert m["llm_errors"][0]["error"].startswith("LLMError")
    # model events carry no digest_date of their own; the count has to go
    # through each item's ingest row (the old query read zero here)
    assert m["coverage"] == [
        {"date": DATE, "ingested": 2, "summarized": 1, "plain": 0}]
    # errors sort first so a sick worker tops the table
    assert m["collectors"][0] == {
        "worker": "email", "last_ok_at": None, "consecutive_errors": 3}


def test_render_without_suggestions_has_no_model_section(conn, tmp_path):
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    m = insight.gather(conn, DATE, fetch_db=fetch_db, ledger_db=ledger_db)
    text = insight.render_report(m)
    assert f"# Operations report — digest {DATE}" in text
    assert "retries consumed 30,000 input tokens (48.4% of input)" in text
    assert "| map:retry-single | 1 | 30,000 | 600 |" in text
    assert "Suggested next steps" not in text
    assert text == insight.render_report(m)  # deterministic


def test_run_with_llm_labels_suggestions(conn, tmp_path):
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    fake = FakeLLM()
    path = insight.run(conn, fake, DATE, out_dir=tmp_path / "runs",
                       fetch_db=fetch_db, ledger_db=ledger_db)
    assert path.name == f"insight-{DATE}.md"
    text = path.read_text()
    assert "model output (insight prompt v" in text
    assert f"insight prompt v{config.INSIGHT_PROMPT_VERSION}" in text
    assert "1. Investigate the 42% retry share on the map layer." in text
    [call] = fake.calls
    assert call["purpose"] == "insight:suggestions"
    assert call["model"] == config.MAP_MODEL
    assert "48.4" in call["prompt"]  # metrics travel into the prompt


def test_run_without_llm_skips_the_call(conn, tmp_path):
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    path = insight.run(conn, None, DATE, out_dir=tmp_path / "runs",
                       fetch_db=fetch_db, ledger_db=ledger_db)
    assert "Suggested next steps" not in path.read_text()


def test_malformed_suggestions_degrade_to_mechanical_report(conn, tmp_path):
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    path = insight.run(conn, FakeLLM(reply="not json {"), DATE,
                       out_dir=tmp_path / "runs",
                       fetch_db=fetch_db, ledger_db=ledger_db)
    text = path.read_text()
    # section renders with the label but an explicit empty marker
    assert "(no suggestions returned)" in text
    assert "# Operations report" in text


def test_security_sweep_is_private_not_in_the_public_report(conn, tmp_path):
    """CLAUDE.md §13, operator ruling 2026-09-29: the host security sweep
    is recorded privately on the server, never in the public insight
    report under provenance/runs/. The public report keeps only a neutral
    pointer that leaks no VPS security posture; the private file carries
    the full sweep."""
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    sweep = {
        "generated_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "window_hours": 24,
        "thresholds": {"tls_warn_days": 21, "campaign_min_ips": 3},
        "probing": {"events": 51, "distinct_ips": 20, "by_family": {}, "findings": []},
        "refusals": {"by_status": {}, "probes_served_2xx": 0},
        "auth": {"failed_ssh": 3, "failed_ssh_distinct_ips": 1,
                 "failed_ssh_alltime": 54, "failed_ssh_alltime_distinct_ips": 29},
        "patch": {"host_security_pending": 3},
        "integrity": {"unhealthy": 0},
        "tls": [{"cert": "fapd.info", "days": 29}, {"cert": "other.example", "days": 81}],
        "verdicts": [], "escalate": False, "stage_errors": [],
    }
    sweep_path = tmp_path / "security-sweep.json"
    sweep_path.write_text(json.dumps(sweep))
    sec_dir = tmp_path / "ops-security"

    path = insight.run(conn, None, DATE, out_dir=tmp_path / "runs",
                       fetch_db=fetch_db, ledger_db=ledger_db,
                       sweep_path=sweep_path, security_dir=sec_dir)

    public = path.read_text()
    for leak in ("tls_warn_days", "campaign_min_ips", "host security packages",
                 "failed SSH", "other.example", "probe requests"):
        assert leak not in public, f"public report leaked {leak!r}"
    assert "recorded privately" in public

    private = (sec_dir / f"security-{DATE}.md").read_text()
    assert "Security sweep (private)" in private
    assert "host security packages pending | 3" in private
    assert "failed SSH attempts (window) | 3" in private
    assert "tls_warn_days=21" in private
    assert "other.example 81d" in private


def test_a_missing_sweep_stays_loud_in_the_private_file(conn, tmp_path):
    """The F-021 shape survives the move: a sweep that did not run is a
    visible gap in the PRIVATE report, not a silent clean bill."""
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    sec_dir = tmp_path / "ops-security"
    insight.run(conn, None, DATE, out_dir=tmp_path / "runs",
                fetch_db=fetch_db, ledger_db=ledger_db,
                sweep_path=tmp_path / "nope.json", security_dir=sec_dir)
    private = (sec_dir / f"security-{DATE}.md").read_text()
    assert "unavailable" in private
    assert "gap in the record" in private


def test_suggest_caps_at_five_and_drops_nonstrings():
    fake = FakeLLM(reply=json.dumps(["a", "b", "c", "d", "e", "f", 7, "  "]))
    got = insight.suggest(fake, {"digest_date": DATE})
    assert got == ["a", "b", "c", "d", "e"]


def test_failed_suggestions_call_still_writes_the_report(conn, tmp_path):
    """The 2026-08-04 failure, pinned. A zero-billed CLI failure raised
    LLMError out of suggest() and took the whole mechanical report with
    it — insight-2026-08-03.md was never written and nothing noticed.
    The malformed-*reply* path was covered; the failed-*call* path was
    not. The report is the product; the suggestions are a garnish."""
    fetch_db, ledger_db = seed_ops(conn, tmp_path)

    class ZeroBilled:
        def complete(self, *a, **kw):
            raise LLMError("cli backend failed (insight:suggestions)"
                           " — zero tokens billed")

    path = insight.run(conn, ZeroBilled(), DATE, out_dir=tmp_path / "runs",
                       fetch_db=fetch_db, ledger_db=ledger_db)
    text = path.read_text()
    assert path.exists()
    assert "# Operations report" in text
    assert "## HTTP requests" in text          # mechanical sections intact
    assert "(no suggestions returned)" in text  # and the loss is visible


def test_window_is_the_eastern_day_not_the_utc_day():
    """DATE is in July, so Eastern is UTC-4: the publication day starts
    at 04:00Z, not 00:00Z, and runs to the next 04:00Z plus the
    finalizer grace. Windowing on the UTC day measured ~5 of 24 hours."""
    start, end = insight._work_window(
        DATE, now=dt.datetime(2100, 1, 1, tzinfo=dt.UTC))
    assert start == f"{DATE}T04:00:00"
    assert end == "2026-07-24T10:00:00"        # 04:00Z + 6h grace
    # Bounds carry no offset suffix on purpose: stored stamps use both
    # 'Z' and '+00:00', which sort against each other wrongly.
    assert "+" not in start and not start.endswith("Z")


def test_window_ends_at_now_while_the_day_is_still_closing():
    """During the real EOD run the grace bound is in the future, so the
    window stops at now rather than reaching past it."""
    now = dt.datetime(2026, 7, 24, 5, 30, tzinfo=dt.UTC)
    _, end = insight._work_window(DATE, now=now)
    assert end == "2026-07-24T05:30:00"


def test_zero_billed_calls_are_counted_separately(conn, tmp_path):
    """A zero-billed failure can carry no error string, so counting only
    `error IS NOT NULL` hid the class that cost 2026-08-04 fifteen
    calls while the report said there were no errors."""
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    ldb = sqlite3.connect(ledger_db)
    ldb.execute("INSERT INTO llm_calls VALUES (?, 'source-desc:batch8',"
                " 0, 0, NULL)", (f"{DATE}T18:05:00Z",))
    ldb.commit(); ldb.close()

    m = insight.gather(conn, DATE, fetch_db=fetch_db, ledger_db=ledger_db)
    assert m["zero_billed"] == [{"purpose": "source-desc:batch8", "calls": 1}]
    text = insight.render_report(m)
    assert "source-desc:batch8" in text
    assert "no tokens billed" in text


def test_zero_billed_section_renders_when_there_are_none(conn, tmp_path):
    """Reported on its own terms, including when it is zero — a silent
    absence is what made the class invisible in the first place."""
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    m = insight.gather(conn, DATE, fetch_db=fetch_db, ledger_db=ledger_db)
    assert m["zero_billed"] == []
    assert "every call in the window billed tokens" in insight.render_report(m)


def test_stage_insight_never_fails_the_run(conn, tmp_path):
    """The wiring contract: an insight failure is reported, not raised —
    the digest is already validated by the time this stage runs."""
    import run_pipeline

    class Boom:
        def complete(self, *a, **kw):
            raise RuntimeError("backend down")

    # Whether gather() fails first (no fetch db in CI) or suggest()
    # raises through the always-failing client, the stage returns None
    # instead of raising.
    assert run_pipeline.stage_insight(conn, DATE, llm_client=Boom()) is None


def test_provider_availability_shows_the_refusal_span():
    """plan-2026-09-27-inference-fallback T4: an outage reads as a span per
    backend, not as the last five error lines."""
    providers = [
        {"backend": "cli", "calls": 68, "billed": 11, "refused": 57,
         "short_circuit": 0, "first_refusal": "2026-09-26T00:24:01.000+00:00",
         "last_refusal": "2026-09-26T11:00:59.185+00:00"},
        {"backend": "gemini", "calls": 18, "billed": 18, "refused": 0,
         "short_circuit": 0, "first_refusal": None, "last_refusal": None}]
    reserve = {"backend": "gemini", "daily_calls": 20, "collector_share": 0.5,
               "collector_budget": 10, "used_24h": 18}
    text = "\n".join(insight.render_providers(providers, reserve))
    assert "| cli | 68 | 11 | 57 | 0 | 2026-09-26T00:24 .. 2026-09-26T11:00 |" in text
    assert "| gemini | 18 | 18 | 0 | 0 | — |" in text
    assert "18 call(s) in the 24 h" in text and "may use 10 (50%)" in text


def test_provider_metrics_from_a_real_ledger(tmp_path, monkeypatch):
    import sqlite3

    from fapd import config, llm
    monkeypatch.setattr(config, "LLM_BACKEND_FALLBACK", "gemini")
    monkeypatch.setattr(config, "LLM_FALLBACK_DAILY_CALLS", 20)
    monkeypatch.setattr(config, "LLM_FALLBACK_COLLECTOR_SHARE", 0.5)
    db = sqlite3.connect(tmp_path / "ledger.db")
    db.executescript(llm._SCHEMA)
    rows = [("2026-09-26T00:24:00", "cli", 0, "CLI error envelope: disabled"),
            ("2026-09-26T11:00:00", "cli", 0, "provider unavailable: x"),
            ("2026-09-26T11:00:01", "cli", 0, "provider unavailable: x (short-circuit)"),
            ("2026-09-26T12:00:00", "cli", 900, None),
            ("2026-09-26T03:00:00", "gemini", 400, None)]
    db.executemany("INSERT INTO llm_calls (ts_utc, backend, model, purpose,"
                   " input_tokens, error) VALUES (?, ?, 'm', 'map:batch1', ?, ?)", rows)
    out = insight._provider_metrics(db, "2026-09-26T00:00:00", "2026-09-27T00:00:00")
    cli = next(p for p in out["providers"] if p["backend"] == "cli")
    assert (cli["calls"], cli["billed"], cli["refused"], cli["short_circuit"]) == (4, 1, 2, 1)
    assert cli["first_refusal"].startswith("2026-09-26T00:24")
    assert cli["last_refusal"].startswith("2026-09-26T11:00:00")
    assert out["fallback_reserve"]["used_24h"] == 1
    assert out["fallback_reserve"]["collector_budget"] == 10


def test_run_withholds_an_ungrounded_security_summary_and_keeps_a_record(conn, tmp_path):
    """2026-10-07: the private report leads with Action today, a summary
    naming what the sweep does not (v1 said "Examplenet-hosted") is
    withheld, and the night leaves a small record for the next to compare."""
    fetch_db, ledger_db = seed_ops(conn, tmp_path)
    sweep = {"generated_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
             "window_hours": 24, "probing": {"events": 0, "findings": []},
             "verdicts": [{"key": "patch.host", "severity": "high", "detail": "7 pending",
                           "escalate": False}],
             "escalate": False, "stage_errors": []}
    sweep_path = tmp_path / "security-sweep.json"
    sweep_path.write_text(json.dumps(sweep))
    sec = tmp_path / "sec"

    class SecLLM(FakeLLM):
        def complete(self, prompt, **kw):
            if kw.get("purpose") == "security:summary":
                self.calls.append({"prompt": prompt, **kw})
                return {"text": "Nothing to do. Examplenet probes were refused."}
            return super().complete(prompt, **kw)

    llm = SecLLM()
    insight.run(conn, llm, DATE, out_dir=tmp_path / "runs", fetch_db=fetch_db,
                ledger_db=ledger_db, sweep_path=sweep_path, security_dir=sec)
    report = (sec / f"security-{DATE}.md").read_text()
    assert "Model summary withheld: it named Examplenet" in report
    assert report.index("## Action today") < report.index("## Security sweep")
    assert "`patch.host`" in report
    assert (sec / f"security-{DATE}.record.json").exists()
    assert "=== TRIAGE ===" in llm.calls[-1]["prompt"]

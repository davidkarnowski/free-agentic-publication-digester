"""Developer-insight report tests (fapd.insight, GUIDE §3a dev-facing
surface): mechanical gathering from the three databases, deterministic
rendering, the labeled model-suggestions section, and the never-fail
wiring contract in run_pipeline."""

import json
import sqlite3

from conftest import DATE

from fapd import config, insight


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

    import time
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
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


def test_suggest_caps_at_five_and_drops_nonstrings():
    fake = FakeLLM(reply=json.dumps(["a", "b", "c", "d", "e", "f", 7, "  "]))
    got = insight.suggest(fake, {"digest_date": DATE})
    assert got == ["a", "b", "c", "d", "e"]


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

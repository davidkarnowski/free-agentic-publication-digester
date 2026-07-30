"""Map-stage and plain-speak tests (analyze.py). The selection-rule
registry's own tests live in test_rules.py; the shared corpus fixtures
(conn, seed_item, seed_corpus, EXPECTED_RULES) in conftest.py. No real
LLM calls: the client is faked; the metadata DB is real SQLite at tmp."""

import json
import re

from conftest import DATE, EXPECTED_RULES, LONG_TEXT, seed_corpus, seed_item

from fapd import analyze, config


class FakeLLM:
    """Stand-in for llm.LLMClient. Scripted replies are consumed first;
    afterwards it auto-answers with valid strict JSON covering every key in
    the prompt."""

    def __init__(self, scripted=()):
        self.scripted = list(scripted)
        self.prompts = []
        self.purposes = []

    def complete(self, prompt, *, purpose, model=None, package_id=None, granule_id=None):
        self.prompts.append(prompt)
        self.purposes.append(purpose)
        if self.scripted:
            text = self.scripted.pop(0)
        else:
            keys = re.findall(r"DOCUMENT key=(\S+) ", prompt)
            text = json.dumps({k: f"Factual summary of {k}." for k in keys})
        return {"text": text, "input_tokens": 600, "output_tokens": 60, "model": "fake-haiku"}



def seed_two_llm_items(conn):
    seed_item(conn, "CREC-2026-07-23", "G1", "CREC", "SENATE", LONG_TEXT)
    seed_item(conn, "CREC-2026-07-23", "G2", "CREC", "HOUSE", LONG_TEXT)
    return ["CREC-2026-07-23|G1", "CREC-2026-07-23|G2"]


def test_official_vs_llm_split(conn):
    seed_corpus(conn)
    fake = FakeLLM()
    stats = analyze.run(conn, fake, DATE)
    assert stats["selected"] == 13
    assert stats["official"] == 3
    assert stats["llm_summarized"] == 10
    assert stats["skipped_existing"] == 0
    assert stats["failed_items"] == []
    rows = conn.execute(
        "SELECT * FROM summaries ORDER BY package_id, granule_id"
    ).fetchall()
    assert len(rows) == 13
    by_key = {(r["package_id"], r["granule_id"]): r for r in rows}
    # No summary row for the counted-only NOTICE, even though it has one.
    assert ("FR-2026-07-23", "2026-10005") not in by_key
    for key, rule_id in EXPECTED_RULES.items():
        assert by_key[key]["inclusion_rule"] == rule_id
        assert by_key[key]["prompt_version"] == config.PROMPT_VERSION
    official = by_key[("FR-2026-07-23", "2026-10003")]
    assert official["method"] == "official"
    assert official["model"] is None
    assert (official["input_tokens"], official["output_tokens"]) == (0, 0)
    assert official["summary"] == "A proposed rule."
    llm_row = by_key[("CREC-2026-07-23", "PgS1")]
    assert llm_row["method"] == "llm"
    assert llm_row["model"] == "fake-haiku"


def test_official_summary_normalized_and_truncated(conn):
    seed_corpus(conn)
    analyze.run(conn, FakeLLM(), DATE)
    short = conn.execute(
        "SELECT summary FROM summaries WHERE granule_id='2026-10002'"
    ).fetchone()["summary"]
    assert short == "An agency rule. It does X."  # whitespace-normalized verbatim
    note = " [official summary truncated; see source]"
    long = conn.execute(
        "SELECT summary FROM summaries WHERE granule_id='2026-10001'"
    ).fetchone()["summary"]
    assert long.endswith(note)
    body = long.removesuffix(note)
    assert body.endswith("amendments.")  # cut at a sentence boundary, not mid-word
    assert len(body) <= 1200


def test_batching_at_most_six_items_per_call(conn):
    seed_corpus(conn)
    fake = FakeLLM()
    stats = analyze.run(conn, fake, DATE)
    assert stats["llm_calls"] == 2  # 10 llm items -> 6 + 4, not 10 calls
    per_call = [len(re.findall(r"DOCUMENT key=(\S+) ", p)) for p in fake.prompts]
    assert per_call == [6, 4]
    assert all(p.startswith("map:batch") for p in fake.purposes)
    # Tokens split evenly across a call's items (600 in / 60 out per call).
    first_batch_row = conn.execute(
        "SELECT input_tokens, output_tokens FROM summaries"
        " WHERE package_id='BILLS-119hr1enr'"
    ).fetchone()
    assert tuple(first_batch_row) == (100, 10)
    second_batch_row = conn.execute(
        "SELECT input_tokens, output_tokens FROM summaries WHERE granule_id='2026-10004'"
    ).fetchone()
    assert tuple(second_batch_row) == (150, 15)


def test_six_items_make_exactly_one_call(conn):
    for i in range(6):
        seed_item(conn, "CREC-2026-07-23", f"Pg{i}", "CREC", "SENATE", LONG_TEXT)
    fake = FakeLLM()
    stats = analyze.run(conn, fake, DATE)
    assert stats["llm_calls"] == 1
    assert len(fake.prompts) == 1
    assert len(re.findall(r"DOCUMENT key=(\S+) ", fake.prompts[0])) == 6


def test_prompt_truncates_long_source_text(conn):
    seed_item(conn, "CREC-2026-07-23", "G1", "CREC", "SENATE", "y" * 20000)
    fake = FakeLLM()
    analyze.run(conn, fake, DATE)
    assert "[truncated for summarization; full text in source]" in fake.prompts[0]
    assert "y" * 12001 not in fake.prompts[0]


def test_idempotent_rerun_makes_zero_llm_calls(conn):
    seed_corpus(conn)
    analyze.run(conn, FakeLLM(), DATE)
    fake2 = FakeLLM()
    stats2 = analyze.run(conn, fake2, DATE)
    assert fake2.prompts == []  # ZERO llm calls on rerun
    assert stats2["llm_calls"] == 0
    assert stats2["skipped_existing"] == 13
    assert stats2["official"] == 0 and stats2["llm_summarized"] == 0
    assert conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0] == 13


def test_missing_item_recovered_by_a_group_retry(conn):
    """Missing items are retried in a group first — one call, not one per
    item. Every call re-pays the backend's fixed prompt overhead, so
    single-item retries are the expensive last resort, not the first move."""
    k1, k2 = seed_two_llm_items(conn)
    fake = FakeLLM(scripted=[json.dumps({k1: "Summary one."})])  # k2 missing
    stats = analyze.run(conn, fake, DATE)
    assert fake.purposes == ["map:batch1", "map:retry-group"]
    assert k2.split("|")[1] in fake.prompts[1]  # retry carries the missing item
    assert stats["llm_summarized"] == 2
    assert stats["llm_calls"] == 2
    assert stats["failed_items"] == []


def test_group_retry_recovers_many_items_in_one_call(conn):
    """The whole point: N missing items cost one retry call, not N."""
    keys = seed_two_llm_items(conn)
    fake = FakeLLM(scripted=["not JSON {"])  # both items missing from batch 1
    analyze.run(conn, fake, DATE)
    assert fake.purposes == ["map:batch1", "map:retry-group"]  # not two singles
    assert all(k.split("|")[1] in fake.prompts[1] for k in keys)


def test_garbage_reply_retries_every_item_of_the_call(conn):
    seed_two_llm_items(conn)
    fake = FakeLLM(scripted=["this is not JSON {"])
    stats = analyze.run(conn, fake, DATE)
    assert fake.purposes == ["map:batch1", "map:retry-group"]
    assert stats["llm_summarized"] == 2
    assert stats["failed_items"] == []


def test_map_shortfall_and_unmatched_keys_are_logged(conn, caplog):
    """F-010: the VPS backlog grind burned ~4M tokens invisibly because the
    map layer had no shortfall logging. Short responses log the covered/
    requested counts; response keys that match no requested item warn with
    a sample (right-count-wrong-keys is otherwise indistinguishable)."""
    k1, _k2 = seed_two_llm_items(conn)
    fake = FakeLLM(scripted=[json.dumps({k1: "Summary one.", "BOGUS|key": "x"})])
    with caplog.at_level("INFO", logger="fapd.analyze"):
        analyze.run(conn, fake, DATE)
    assert "map: response covered 1 of 2 requested items" in caplog.text
    assert "match no requested item" in caplog.text
    assert "BOGUS|key" in caplog.text


def test_markdown_fenced_json_is_accepted(conn):
    keys = seed_two_llm_items(conn)
    fenced = "```json\n" + json.dumps({k: f"Summary of {k}." for k in keys}) + "\n```"
    fake = FakeLLM(scripted=[fenced])
    stats = analyze.run(conn, fake, DATE)
    assert stats["llm_calls"] == 1  # no retry needed
    assert stats["llm_summarized"] == 2


def test_failed_items_recorded_and_never_written(conn):
    seed_two_llm_items(conn)
    fake = FakeLLM(scripted=["garbage"] * 10)  # batch, group and singles fail
    stats = analyze.run(conn, fake, DATE)
    # escalation: batch -> one group retry -> per-item isolation
    assert fake.purposes == ["map:batch1", "map:retry-group",
                             "map:retry-single", "map:retry-single"]
    assert stats["llm_summarized"] == 0
    assert stats["failed_items"] == [
        {"package_id": "CREC-2026-07-23", "granule_id": "G1", "rule_id": "CREC-SEL-01"},
        {"package_id": "CREC-2026-07-23", "granule_id": "G2", "rule_id": "CREC-SEL-01"},
    ]
    # Banned outcome: a summaries row is never written for a failed item.
    assert conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0] == 0
    # And because nothing was written, a later rerun will attempt them again.
    fake2 = FakeLLM()
    stats2 = analyze.run(conn, fake2, DATE)
    assert stats2["llm_summarized"] == 2 and stats2["failed_items"] == []


# ---------------------------------------------------------------------------
# Plain-speak pass (run_plain)
# ---------------------------------------------------------------------------


class PlainFakeLLM:
    """Returns a strict-JSON mapping covering every key found in the prompt."""

    def __init__(self, garbage_first=False, omit_keys=()):
        self.calls = []
        self.garbage_first = garbage_first
        self.omit_keys = set(omit_keys)

    def complete(self, prompt, **kw):
        self.calls.append({"prompt": prompt, **kw})
        if self.garbage_first:
            self.garbage_first = False
            return {"text": "not json", "input_tokens": 100, "output_tokens": 5,
                    "model": kw.get("model", "x")}
        import json as _json
        import re as _re

        keys = _re.findall(r"key=([^\s]+)", prompt)
        reply = {k: f"plain for {k}" for k in keys if k not in self.omit_keys}
        return {"text": _json.dumps(reply), "input_tokens": 1000, "output_tokens": 200,
                "model": kw.get("model", "x")}


def seed_summary(conn, pid, gid, summary="An official summary.", date="2026-07-23"):
    conn.execute(
        "INSERT OR IGNORE INTO packages (package_id, collection, last_modified,"
        " first_seen_at, date_issued, fetch_status)"
        " VALUES (?, 'FR', 'x', 'x', ?, 'fetched')",
        (pid, date),
    )
    conn.execute(
        "INSERT OR IGNORE INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, title, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, ?, 'FR', 'RULE', 'A title', 'body', 4, 'x', 1)",
        (pid, gid),
    )
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " inclusion_rule, summary, created_at)"
        " VALUES (?, ?, ?, 'official', 'FR-SEL-01', ?, 'x')",
        (pid, gid, config.PROMPT_VERSION, summary),
    )
    conn.commit()


def test_run_plain_batches_and_stores(conn):
    for i in range(30):  # more than one batch at MAX_PLAIN_BATCH_ITEMS=25
        seed_summary(conn, "FR-2026-07-23", f"2026-{i:05d}")
    llm = PlainFakeLLM()
    stats = analyze.run_plain(conn, llm, "2026-07-23")
    assert stats["plain_pending"] == 30
    assert stats["plain_written"] == 30
    assert stats["llm_calls"] == 2  # 25 + 5, not 30 calls
    row = conn.execute(
        "SELECT plain, plain_version, source_prompt_version FROM plain_summaries LIMIT 1"
    ).fetchone()
    assert row["plain"].startswith("plain for ")
    assert row["plain_version"] == config.PLAIN_PROMPT_VERSION
    assert row["source_prompt_version"] == config.PROMPT_VERSION


def test_run_plain_idempotent(conn):
    seed_summary(conn, "FR-2026-07-23", "2026-1")
    analyze.run_plain(conn, PlainFakeLLM(), "2026-07-23")
    llm2 = PlainFakeLLM()
    stats = analyze.run_plain(conn, llm2, "2026-07-23")
    assert stats["plain_pending"] == 0 and not llm2.calls


def test_run_plain_retry_then_honest_failure(conn):
    seed_summary(conn, "FR-2026-07-23", "2026-1")
    seed_summary(conn, "FR-2026-07-23", "2026-2")
    # First call garbage -> both items retried singly; retry omits one key.
    llm = PlainFakeLLM(garbage_first=True, omit_keys={"FR-2026-07-23|2026-2"})
    stats = analyze.run_plain(conn, llm, "2026-07-23")
    assert stats["plain_written"] == 1
    assert stats["failed_items"] == [
        {"package_id": "FR-2026-07-23", "granule_id": "2026-2"}
    ]
    # Failed item has NO row (never fabricated) and is retried on rerun.
    n = conn.execute("SELECT COUNT(*) FROM plain_summaries").fetchone()[0]
    assert n == 1
    stats2 = analyze.run_plain(conn, PlainFakeLLM(), "2026-07-23")
    assert stats2["plain_pending"] == 1 and stats2["plain_written"] == 1


def test_run_plain_uses_cheap_tier_and_purpose(conn):
    seed_summary(conn, "FR-2026-07-23", "2026-1")
    llm = PlainFakeLLM()
    analyze.run_plain(conn, llm, "2026-07-23")
    call = llm.calls[0]
    assert call["model"] == config.PLAIN_MODEL
    assert call["purpose"] == "plain:batch1"
    assert "An official summary." in call["prompt"]  # input is the STORED summary


def seed_keys(conn):
    return [f"{r['package_id']}|{r['granule_id']}" for r in conn.execute(
        "SELECT package_id, granule_id FROM extracted_texts ORDER BY granule_id")]


def test_plain_retries_batch_before_isolating(conn):
    """Plain-speak retries escalate the same way. Measured 2026-07-29:
    single-item retries burned 645,778 input tokens (42% of the day) to
    recover items the first pass had merely truncated away."""
    seed_two_llm_items(conn)
    analyze.run(conn, FakeLLM(scripted=[json.dumps(
        {k: f"Summary of {k}." for k in seed_keys(conn)})]), DATE)
    fake = FakeLLM(scripted=["not JSON {"])  # nothing parses in batch 1
    analyze.run_plain(conn, fake, DATE)
    assert fake.purposes[0] == "plain:batch1"
    assert fake.purposes[1] == "plain:retry-group"
    assert "plain:retry-group" in fake.purposes
    # the group call carries every missing item, rather than one call each
    assert fake.purposes.count("plain:retry-group") == 1

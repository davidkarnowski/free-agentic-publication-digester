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


# ---------------------------------------------------------------------------
# Lexicon-correction (GUIDE §6 rule 14a)
# ---------------------------------------------------------------------------


def _seed_bad_summary(conn, package_id, granule_id, *,
                      summary="A sweeping change to floor procedures."):
    seed_item(conn, package_id, granule_id, "CREC", "SENATE", LONG_TEXT)
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " model, inclusion_rule, summary, created_at)"
        " VALUES (?, ?, ?, 'llm', 'fake-haiku', 'CREC-SEL-01', ?, 'x')",
        (package_id, granule_id, config.PROMPT_VERSION, summary),
    )
    conn.commit()


def test_correct_lexicon_violation_fixes_and_updates_row(conn):
    _seed_bad_summary(conn, "CREC-2026-07-23", "G1")
    fake = FakeLLM(scripted=[json.dumps(
        {"CREC-2026-07-23|G1": "A change to floor procedures."})])
    result = analyze.correct_lexicon_violation(
        conn, fake, package_id="CREC-2026-07-23", granule_id="G1",
        layer="map", term="sweeping")
    assert result == {"outcome": "corrected"}
    assert fake.purposes == ["map:lexicon-correction"]
    row = conn.execute(
        "SELECT summary, model FROM summaries WHERE package_id=? AND granule_id=?"
        " AND prompt_version=?",
        ("CREC-2026-07-23", "G1", config.PROMPT_VERSION)).fetchone()
    assert row["summary"] == "A change to floor procedures."  # same row, in place
    assert row["model"] == "fake-haiku"
    corr = conn.execute(
        "SELECT layer, term, outcome FROM lexicon_corrections").fetchone()
    assert (corr["layer"], corr["term"], corr["outcome"]) == ("map", "sweeping", "corrected")
    attempts = conn.execute(
        "SELECT attempts FROM summary_attempts WHERE package_id=? AND granule_id=?"
        " AND prompt_version=? AND layer='map-correction'",
        ("CREC-2026-07-23", "G1", config.PROMPT_VERSION)).fetchone()
    assert attempts["attempts"] == 1


def test_correct_lexicon_violation_withdraws_after_ceiling(conn):
    _seed_bad_summary(conn, "CREC-2026-07-23", "G1")
    conn.execute(
        "INSERT INTO plain_summaries (package_id, granule_id, plain_version,"
        " source_prompt_version, plain, created_at) VALUES (?, ?, ?, ?, ?, 'x')",
        ("CREC-2026-07-23", "G1", config.PLAIN_PROMPT_VERSION, config.PROMPT_VERSION,
         "A sweeping plain line."))
    conn.commit()
    # Every corrective attempt still contains the banned word.
    fake = FakeLLM(scripted=[
        json.dumps({"CREC-2026-07-23|G1": "Another sweeping change."}),
        json.dumps({"CREC-2026-07-23|G1": "Still a sweeping change."}),
    ])
    result = analyze.correct_lexicon_violation(
        conn, fake, package_id="CREC-2026-07-23", granule_id="G1",
        layer="map", term="sweeping")
    assert result == {"outcome": "withdrawn"}
    assert fake.purposes == ["map:lexicon-correction", "map:lexicon-correction"]
    assert config.MAX_LEXICON_CORRECTION_ATTEMPTS == 2  # pins the test's attempt count
    assert conn.execute(
        "SELECT COUNT(*) FROM summaries WHERE package_id=? AND granule_id=?",
        ("CREC-2026-07-23", "G1")).fetchone()[0] == 0
    # Withdrawing a MAP row deletes the dependent plain row too — nothing
    # orphaned lingers behind a summary that no longer exists.
    assert conn.execute(
        "SELECT COUNT(*) FROM plain_summaries WHERE package_id=? AND granule_id=?",
        ("CREC-2026-07-23", "G1")).fetchone()[0] == 0
    corr = conn.execute("SELECT outcome FROM lexicon_corrections").fetchone()
    assert corr["outcome"] == "withdrawn"
    attempts = conn.execute(
        "SELECT attempts FROM summary_attempts WHERE package_id=? AND granule_id=?"
        " AND prompt_version=? AND layer='map-correction'",
        ("CREC-2026-07-23", "G1", config.PROMPT_VERSION)).fetchone()
    assert attempts["attempts"] == config.MAX_LEXICON_CORRECTION_ATTEMPTS


def test_withdrawn_item_never_reenters_ordinary_pending(conn):
    """The closure-guard pin: without it, a withdrawn item's absent row
    looks like fresh pending work again and the very next run() would
    re-summarize it with the uncorrected prompt, reproducing the
    violation and defeating the whole feature."""
    seed_item(conn, "CREC-2026-07-23", "G1", "CREC", "SENATE", LONG_TEXT)
    bad = FakeLLM(scripted=[json.dumps(
        {"CREC-2026-07-23|G1": "A sweeping change to floor procedures."})])
    analyze.run(conn, bad, DATE)
    assert conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0] == 1

    still_bad = FakeLLM(scripted=[
        json.dumps({"CREC-2026-07-23|G1": "Another sweeping change."}),
        json.dumps({"CREC-2026-07-23|G1": "Still sweeping."}),
    ])
    result = analyze.correct_lexicon_violation(
        conn, still_bad, package_id="CREC-2026-07-23", granule_id="G1",
        layer="map", term="sweeping")
    assert result == {"outcome": "withdrawn"}
    assert conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0] == 0

    fresh = FakeLLM()
    stats = analyze.run(conn, fresh, DATE)
    assert fresh.prompts == []  # zero LLM calls -- the closure guard
    assert stats["skipped_lexicon_withdrawn"] == 1
    assert conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0] == 0


def test_correction_self_gate_exempts_the_item_own_title_quote(conn):
    """The 'context aware' edge case: a corrective reply that legitimately
    quotes the item's own official title verbatim -- and that title
    itself contains a banned word -- must be accepted, not rejected."""
    seed_item(conn, "CREC-2026-07-23", "G1", "CREC", "SENATE", LONG_TEXT)
    conn.execute(
        "UPDATE extracted_texts SET title = 'Landmark Legal Foundation v. EPA'"
        " WHERE package_id='CREC-2026-07-23' AND granule_id='G1'")
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " model, inclusion_rule, summary, created_at)"
        " VALUES ('CREC-2026-07-23', 'G1', ?, 'llm', 'fake-haiku', 'CREC-SEL-01',"
        " 'A sweeping change to floor procedures.', 'x')",
        (config.PROMPT_VERSION,))
    conn.commit()
    fake = FakeLLM(scripted=[json.dumps({
        "CREC-2026-07-23|G1": "The Senate cited Landmark Legal Foundation v. EPA"
                              " while debating floor procedures.",
    })])
    result = analyze.correct_lexicon_violation(
        conn, fake, package_id="CREC-2026-07-23", granule_id="G1",
        layer="map", term="sweeping")
    assert result == {"outcome": "corrected"}
    row = conn.execute(
        "SELECT summary FROM summaries WHERE package_id='CREC-2026-07-23'"
        " AND granule_id='G1'").fetchone()
    assert "Landmark Legal Foundation v. EPA" in row["summary"]


def test_correct_lexicon_violation_plain_layer(conn):
    seed_item(conn, "CREC-2026-07-23", "G1", "CREC", "SENATE", LONG_TEXT)
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " model, inclusion_rule, summary, created_at)"
        " VALUES ('CREC-2026-07-23', 'G1', ?, 'llm', 'fake-haiku', 'CREC-SEL-01',"
        " 'A clean summary of floor procedures.', 'x')",
        (config.PROMPT_VERSION,))
    conn.execute(
        "INSERT INTO plain_summaries (package_id, granule_id, plain_version,"
        " source_prompt_version, plain, created_at) VALUES (?, ?, ?, ?, ?, 'x')",
        ("CREC-2026-07-23", "G1", config.PLAIN_PROMPT_VERSION, config.PROMPT_VERSION,
         "A sweeping plain-language line."))
    conn.commit()
    fake = FakeLLM(scripted=[json.dumps({
        "CREC-2026-07-23|G1": "A plain-language line about floor procedures.",
    })])
    result = analyze.correct_lexicon_violation(
        conn, fake, package_id="CREC-2026-07-23", granule_id="G1",
        layer="plain", term="sweeping")
    assert result == {"outcome": "corrected"}
    assert fake.purposes == ["plain:lexicon-correction"]
    row = conn.execute(
        "SELECT plain FROM plain_summaries WHERE package_id='CREC-2026-07-23'"
        " AND granule_id='G1'").fetchone()
    assert row["plain"] == "A plain-language line about floor procedures."
    # A plain-layer correction must never touch the (clean) map summary.
    map_row = conn.execute(
        "SELECT summary FROM summaries WHERE package_id='CREC-2026-07-23'"
        " AND granule_id='G1'").fetchone()
    assert map_row["summary"] == "A clean summary of floor procedures."


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


# ---------------------------------------------------------------------------
# GUIDE §6 rule 14 attempt accounting on the finalizer path (2026-08-24)
# ---------------------------------------------------------------------------


def _set_attempts(conn, pid, gid, layer, n):
    conn.execute(
        "INSERT INTO summary_attempts (package_id, granule_id, prompt_version,"
        " layer, attempts, last_at) VALUES (?, ?, ?, ?, ?, 'x')",
        (pid, gid, config.PROMPT_VERSION, layer, n))
    conn.commit()


def _attempts(conn, pid, gid, layer):
    row = conn.execute(
        "SELECT attempts FROM summary_attempts WHERE package_id=? AND granule_id=?"
        " AND prompt_version=? AND layer=?",
        (pid, gid, config.PROMPT_VERSION, layer)).fetchone()
    return row["attempts"] if row else 0


class RaisingLLM:
    """Every call raises the given exception — a 429 storm or an outage."""

    def __init__(self, exc):
        self.exc = exc
        self.calls = 0

    def complete(self, prompt, **kw):
        self.calls += 1
        raise self.exc


def test_run_skips_items_at_the_per_item_ceiling(conn):
    """The collector's trigger honored MAX_ITEM_SUMMARY_ATTEMPTS; the
    finalizer path did not, so an exhausted item was re-bought nightly."""
    seed_two_llm_items(conn)
    _set_attempts(conn, "CREC-2026-07-23", "G1", "map", config.MAX_ITEM_SUMMARY_ATTEMPTS)
    fake = FakeLLM()
    stats = analyze.run(conn, fake, DATE)
    assert stats["exhausted"] == 1
    assert stats["llm_summarized"] == 1
    assert "CREC-2026-07-23|G1" not in fake.prompts[0]
    assert "CREC-2026-07-23|G2" in fake.prompts[0]


def test_run_plain_skips_items_at_the_per_item_ceiling(conn):
    """Backlog D4: the plain layer recorded attempts but never read them."""
    seed_summary(conn, "FR-2026-07-23", "2026-1")
    seed_summary(conn, "FR-2026-07-23", "2026-2")
    _set_attempts(conn, "FR-2026-07-23", "2026-1", "plain", config.MAX_ITEM_SUMMARY_ATTEMPTS)
    llm = PlainFakeLLM()
    stats = analyze.run_plain(conn, llm, "2026-07-23")
    assert stats["exhausted"] == 1
    assert stats["plain_pending"] == 1 and stats["plain_written"] == 1
    assert "FR-2026-07-23|2026-1" not in llm.calls[0]["prompt"]


def test_a_batch_that_raises_advances_every_item_in_it(conn):
    """Before this, attempts were recorded only for items still queued at
    the end of a layer — a raising call recorded nothing, so a 429 storm
    left every item's ladder untouched."""
    from fapd import llm as _llm

    seed_two_llm_items(conn)
    fake = RaisingLLM(_llm.LLMError("cli backend failed (map:batch1): boom"))
    try:
        analyze.run(conn, fake, DATE)
    except _llm.LLMError:
        pass
    else:
        raise AssertionError("a plain LLMError still propagates")
    assert fake.calls == 1
    assert _attempts(conn, "CREC-2026-07-23", "G1", "map") == 1
    assert _attempts(conn, "CREC-2026-07-23", "G2", "map") == 1

    seed_summary(conn, "FR-2026-07-23", "2026-1")
    try:
        analyze.run_plain(conn, RaisingLLM(_llm.LLMError("boom")), "2026-07-23")
    except _llm.LLMError:
        pass
    assert _attempts(conn, "FR-2026-07-23", "2026-1", "plain") == 1


def test_a_provider_outage_advances_no_item(conn):
    """GUIDE §6 r15: the provider failed, not the item — burning item
    ceilings on a vendor outage would turn an outage into permanent gaps."""
    from fapd import llm as _llm

    seed_two_llm_items(conn)
    fake = RaisingLLM(_llm.ProviderUnavailableError("quota exhausted"))
    try:
        analyze.run(conn, fake, DATE)
    except _llm.ProviderUnavailableError:
        pass
    else:
        raise AssertionError("ProviderUnavailableError must propagate")
    assert conn.execute("SELECT COUNT(*) FROM summary_attempts").fetchone()[0] == 0
    # ...and it is still an LLMError for callers that catch the base class
    assert issubclass(_llm.ProviderUnavailableError, _llm.LLMError)

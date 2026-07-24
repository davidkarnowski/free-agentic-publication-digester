"""Tests for the selection-rule registry (rules.py) and the map stage
(analyze.py). No real `claude` CLI calls: the LLM is faked; the metadata DB
is real SQLite at a tmp path."""

import json
import re

import pytest

from info_intel import analyze, config, db, rules

DATE = "2026-07-23"
LONG_TEXT = ("floor debate " * 1200)[:16000]  # above the 15000-char threshold
SENATE_VOTE_TEXT = (
    "The result was announced--yeas 47, nays 45, as follows:\n\n"
    "                  [Rollcall Vote No. 207 Leg.]\n\n"
    "                                YEAS--47\n\n     Alsobrooks\n     Baldwin\n\n"
    "                                NAYS--45\n\n     Barrasso\n     Blackburn\n"
)
HOUSE_VOTE_TEXT = (
    "and there were--yeas 214, nays 208, not voting 9, as follows:\n\n"
    "                             [Roll No. 282]\n\n"
    "                               YEAS--214\n\n     Adams\n\n"
    "                               NAYS--208\n\n     Aderholt\n"
)
# A demanded-but-postponed vote: narrative "yeas and nays", no recorded result.
POSTPONED_VOTE_TEXT = (
    "Ms. CHU. Mr. Speaker, on that I demand the yeas and nays.\n"
    "The yeas and nays were ordered.\n"
    "The SPEAKER pro tempore. Pursuant to clause 8 of rule XX, further\n"
    "proceedings on this question will be postponed.\n"
)


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


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "meta.db")
    yield c
    c.close()


def seed_item(conn, package_id, granule_id, collection, doc_type, text="body text",
              *, metadata=None, date=DATE):
    conn.execute(
        "INSERT OR IGNORE INTO packages"
        " (package_id, collection, date_issued, last_modified, first_seen_at)"
        " VALUES (?, ?, ?, '2026-07-24T00:00:00Z', '2026-07-24T00:00:00Z')",
        (package_id, collection, date),
    )
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, '2026-07-24T00:00:00Z', 1)",
        (package_id, granule_id, collection, doc_type,
         f"title of {granule_id or package_id}", json.dumps(metadata or {}),
         text, len(text)),
    )
    conn.commit()


LONG_OFFICIAL = "The Commission adopts rule amendments. " * 40  # ~1559 chars normalized


def seed_corpus(conn):
    """Fixture set spanning every selection rule, both exclusion classes,
    threshold boundaries, and official-vs-LLM FR splits."""
    crec = "CREC-2026-07-23"
    seed_item(conn, crec, "PgS1", "CREC", "SENATE", LONG_TEXT)             # SEL-01
    seed_item(conn, crec, "PgS2", "CREC", "SENATE", SENATE_VOTE_TEXT)      # SEL-02 (short)
    seed_item(conn, crec, "PgH1", "CREC", "HOUSE", ("x" * 15000))          # SEL-01 boundary
    seed_item(conn, crec, "PgH2", "CREC", "HOUSE", ("x" * 14999))          # EX-01 boundary
    seed_item(conn, crec, "PgH3", "CREC", "HOUSE",
              LONG_TEXT + HOUSE_VOTE_TEXT)                                 # SEL-01 wins over SEL-02
    seed_item(conn, crec, "PgH4", "CREC", "HOUSE", POSTPONED_VOTE_TEXT)    # EX-01, not a vote
    seed_item(conn, crec, "PgE1", "CREC", "EXTENSIONS")                    # EX-02
    seed_item(conn, crec, "PgD1", "CREC", "DAILYDIGEST")                   # EX-02
    seed_item(conn, "BILLS-119hr1enr", "", "BILLS", "Enrolled-Bill")       # BILLS-SEL-01 stage
    seed_item(conn, "BILLS-119s2pcs", "", "BILLS", "pcs")                  # BILLS-SEL-01 code
    seed_item(conn, "BILLS-119hr3ih", "", "BILLS", "Introduced-in-House")  # unselected
    fr = "FR-2026-07-23"
    seed_item(conn, fr, "2026-10001", "FR", "RULE",
              metadata={"summary": LONG_OFFICIAL})                         # official, truncated
    seed_item(conn, fr, "2026-10002", "FR", "RULE",
              metadata={"summary": "An  agency\n  rule.\tIt does X."})     # official, normalized
    seed_item(conn, fr, "2026-10003", "FR", "PRORULE",
              metadata={"summary": "A proposed rule."})                    # official
    seed_item(conn, fr, "2026-10004", "FR", "PRESDOCU")                    # llm (no SUMMARY)
    seed_item(conn, fr, "2026-10005", "FR", "NOTICE",
              metadata={"summary": "A notice."})                           # FR-EX-01, never stored
    seed_item(conn, fr, "2026-10006", "FR", "RULE")                        # llm (RULE, no SUMMARY)
    seed_item(conn, "FR-2026-07-22", "2026-09999", "FR", "RULE",
              date="2026-07-22")                                           # other date, ignored


EXPECTED_RULES = {
    ("CREC-2026-07-23", "PgS1"): "CREC-SEL-01",
    ("CREC-2026-07-23", "PgS2"): "CREC-SEL-02",
    ("CREC-2026-07-23", "PgH1"): "CREC-SEL-01",
    ("CREC-2026-07-23", "PgH3"): "CREC-SEL-01",
    ("BILLS-119hr1enr", ""): "BILLS-SEL-01",
    ("BILLS-119s2pcs", ""): "BILLS-SEL-01",
    ("FR-2026-07-23", "2026-10001"): "FR-SEL-01",
    ("FR-2026-07-23", "2026-10002"): "FR-SEL-01",
    ("FR-2026-07-23", "2026-10006"): "FR-SEL-01",
    ("FR-2026-07-23", "2026-10003"): "FR-SEL-02",
    ("FR-2026-07-23", "2026-10004"): "FR-SEL-03",
}


def seed_two_llm_items(conn):
    seed_item(conn, "CREC-2026-07-23", "G1", "CREC", "SENATE", LONG_TEXT)
    seed_item(conn, "CREC-2026-07-23", "G2", "CREC", "HOUSE", LONG_TEXT)
    return ["CREC-2026-07-23|G1", "CREC-2026-07-23|G2"]


# ---------------------------------------------------------------- rules.py


def test_selection_rule_assignment_and_no_duplicates(conn):
    seed_corpus(conn)
    items = rules.select_items(conn, DATE)
    got = {(i["package_id"], i["granule_id"]): i["rule_id"] for i in items}
    assert got == EXPECTED_RULES
    assert len(items) == len(got)  # one row per item — no duplicates
    for item in items:
        assert set(item) == {"package_id", "granule_id", "collection",
                             "doc_type", "title", "rule_id"}


def test_exclusion_counts(conn):
    seed_corpus(conn)
    assert rules.exclusion_counts(conn, DATE) == {
        "FR-EX-01": 1,      # the NOTICE, official summary notwithstanding
        "CREC-EX-01": 2,    # PgH2 (14999 chars) and PgH4 (postponed vote)
        "CREC-EX-02": 2,    # EXTENSIONS + DAILYDIGEST
    }


def test_exclusion_counts_empty_day_has_all_keys(conn):
    assert rules.exclusion_counts(conn, DATE) == {
        "FR-EX-01": 0, "CREC-EX-01": 0, "CREC-EX-02": 0,
    }


def test_every_rule_has_a_description():
    for registry in (rules.RULES, rules.EXCLUSIONS):
        for spec in registry.values():
            assert spec["description"]


# -------------------------------------------------------------- analyze.py


def test_official_vs_llm_split(conn):
    seed_corpus(conn)
    fake = FakeLLM()
    stats = analyze.run(conn, fake, DATE)
    assert stats["selected"] == 11
    assert stats["official"] == 3
    assert stats["llm_summarized"] == 8
    assert stats["skipped_existing"] == 0
    assert stats["failed_items"] == []
    rows = conn.execute(
        "SELECT * FROM summaries ORDER BY package_id, granule_id"
    ).fetchall()
    assert len(rows) == 11
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
    assert stats["llm_calls"] == 2  # 8 llm items -> 6 + 2, not 8 calls
    per_call = [len(re.findall(r"DOCUMENT key=(\S+) ", p)) for p in fake.prompts]
    assert per_call == [6, 2]
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
    assert tuple(second_batch_row) == (300, 30)


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
    assert stats2["skipped_existing"] == 11
    assert stats2["official"] == 0 and stats2["llm_summarized"] == 0
    assert conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0] == 11


def test_missing_key_retried_once_in_single_item_call(conn):
    k1, k2 = seed_two_llm_items(conn)
    fake = FakeLLM(scripted=[json.dumps({k1: "Summary one."})])  # k2 missing
    stats = analyze.run(conn, fake, DATE)
    assert fake.purposes == ["map:batch1", "map:retry"]
    assert k2.split("|")[1] in fake.prompts[1]  # retry carries the missing item
    assert stats["llm_summarized"] == 2
    assert stats["llm_calls"] == 2
    assert stats["failed_items"] == []
    row = conn.execute(
        "SELECT summary, input_tokens FROM summaries WHERE granule_id='G2'"
    ).fetchone()
    assert row["summary"] == f"Factual summary of {k2}."
    assert row["input_tokens"] == 600  # single-item retry keeps the whole call


def test_garbage_reply_retries_every_item_of_the_call(conn):
    seed_two_llm_items(conn)
    fake = FakeLLM(scripted=["this is not JSON {"])
    stats = analyze.run(conn, fake, DATE)
    assert fake.purposes == ["map:batch1", "map:retry", "map:retry"]
    assert stats["llm_summarized"] == 2
    assert stats["failed_items"] == []


def test_markdown_fenced_json_is_accepted(conn):
    keys = seed_two_llm_items(conn)
    fenced = "```json\n" + json.dumps({k: f"Summary of {k}." for k in keys}) + "\n```"
    fake = FakeLLM(scripted=[fenced])
    stats = analyze.run(conn, fake, DATE)
    assert stats["llm_calls"] == 1  # no retry needed
    assert stats["llm_summarized"] == 2


def test_failed_items_recorded_and_never_written(conn):
    seed_two_llm_items(conn)
    fake = FakeLLM(scripted=["garbage"] * 10)  # batch and both retries fail
    stats = analyze.run(conn, fake, DATE)
    assert fake.purposes == ["map:batch1", "map:retry", "map:retry"]
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

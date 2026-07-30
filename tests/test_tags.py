"""Section-tag layer tests (GUIDE §6 r12a): mechanical derivation, the
batched discovery-key call, idempotence, and the labeled read shape."""

import json

from conftest import DATE, seed_corpus

from fapd import config, tags


class FakeLLM:
    def __init__(self, reply=None):
        self.calls = []
        self.reply = reply

    def complete(self, prompt, **kw):
        self.calls.append({"prompt": prompt, **kw})
        if self.reply is None:
            import re
            keys = re.findall(r"SECTION key=(\S+)", prompt)
            self.reply = json.dumps({k: [f"{k} topic", "policy"] for k in keys})
        return {"text": self.reply, "input_tokens": 900, "output_tokens": 80,
                "model": "fake-haiku"}


def seed_summaries(conn):
    seed_corpus(conn)
    for pid, gid, rule in (
        ("CREC-2026-07-23", "PgS1", "CREC-SEL-01"),
        ("FR-2026-07-23", "2026-10003", "FR-SEL-02"),
        ("USCOURTS-ca9-26-01234", "USCOURTS-ca9-26-01234-0", "USCOURTS-SEL-01"),
    ):
        conn.execute(
            "INSERT INTO summaries (package_id, granule_id, prompt_version,"
            " method, inclusion_rule, summary, created_at)"
            " VALUES (?, ?, ?, 'official', ?, 'A summary.', 'x')",
            (pid, gid, config.PROMPT_VERSION, rule))
    conn.commit()


def test_mechanical_tags_branch_and_fr_agencies(conn):
    seed_summaries(conn)
    conn.execute("UPDATE extracted_texts SET agency = 'Environmental Protection"
                 " Agency' WHERE collection = 'FR'")
    conn.commit()
    mech = tags.mechanical_section_tags(conn, DATE)
    assert mech["senate"] == ["legislative"]
    assert mech["judicial"] == ["judicial"]
    assert mech["proposed"][0] == "executive"
    assert "environmental protection agency" in mech["proposed"]


def test_run_writes_both_layers_and_is_idempotent(conn):
    seed_summaries(conn)
    llm = FakeLLM()
    stats = tags.run(conn, llm, DATE)
    assert stats["mechanical"] >= 3 and stats["llm"] > 0
    assert len(llm.calls) == 1

    # rerun: mechanical refreshed, llm layer skipped — zero calls
    llm2 = FakeLLM()
    stats2 = tags.run(conn, llm2, DATE)
    assert stats2["llm"] == 0 and stats2["skipped_existing"] > 0
    assert llm2.calls == []


def test_get_section_tags_separates_methods(conn):
    seed_summaries(conn)
    tags.run(conn, FakeLLM(), DATE)
    got = tags.get_section_tags(conn, DATE)
    assert got["senate"]["mechanical"] == ["legislative"]
    assert "senate topic" in got["senate"]["llm"]


def test_run_caps_and_sanitizes_keys(conn):
    seed_summaries(conn)
    reply = json.dumps({"senate": ["ONE", "two  words", "three", "four", 5],
                        "judicial": ["x" * 60]})
    tags.run(conn, FakeLLM(reply=reply), DATE)
    got = tags.get_section_tags(conn, DATE)
    assert got["senate"]["llm"] == ["one", "three", "two words"]  # ≤3, lowered
    assert got.get("judicial", {}).get("llm", []) == []           # >40 chars dropped


def test_empty_day_no_call(conn):
    llm = FakeLLM()
    stats = tags.run(conn, llm, "2020-01-01")
    assert stats == {"mechanical": 0, "llm": 0, "skipped_existing": 0}
    assert llm.calls == []

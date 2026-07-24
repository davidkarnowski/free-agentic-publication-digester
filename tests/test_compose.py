"""Compose stage tests: idempotency, input construction, storage."""

import pytest

from info_intel import compose, config, db


class FakeLLM:
    def __init__(self, text="Para one.\n\nPara two."):
        self.calls = []
        self.text = text

    def complete(self, prompt, **kw):
        self.calls.append({"prompt": prompt, **kw})
        return {"text": self.text, "input_tokens": 30000, "output_tokens": 150,
                "model": kw.get("model", "x")}


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "meta.db")
    c.execute(
        "INSERT INTO packages (package_id, collection, last_modified, first_seen_at,"
        " date_issued, fetch_status) VALUES ('FR-2026-07-23','FR','x','x','2026-07-23','fetched')"
    )
    c.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, text, char_count, extracted_at, extractor_version)"
        " VALUES ('FR-2026-07-23','2026-1','FR','RULE','A rule title','body',4,'x',1)"
    )
    c.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " inclusion_rule, summary, created_at)"
        " VALUES ('FR-2026-07-23','2026-1',?, 'official','FR-SEL-01','Official summary text.','x')",
        (config.PROMPT_VERSION,),
    )
    c.commit()
    yield c
    c.close()


def test_composes_from_summaries_and_counts(conn):
    llm = FakeLLM()
    stats = compose.compose_day(conn, llm, "2026-07-23")
    assert stats["composed"] == 1
    prompt = llm.calls[0]["prompt"]
    assert "Official summary text." in prompt
    assert "FR/RULE" in prompt  # mechanical counts included
    assert llm.calls[0]["model"] == config.COMPOSE_MODEL
    stored = compose.get_day_summary(conn, "2026-07-23")
    assert stored["summary"] == "Para one.\n\nPara two."


def test_idempotent_second_call_makes_no_llm_call(conn):
    llm = FakeLLM()
    compose.compose_day(conn, llm, "2026-07-23")
    stats = compose.compose_day(conn, llm, "2026-07-23")
    assert stats == {"composed": 0, "skipped_existing": 1,
                     "input_tokens": 0, "output_tokens": 0}
    assert len(llm.calls) == 1


def test_no_items_no_call(conn):
    llm = FakeLLM()
    stats = compose.compose_day(conn, llm, "2020-01-01")
    assert stats["composed"] == 0 and not llm.calls
    assert compose.get_day_summary(conn, "2020-01-01") is None

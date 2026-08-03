"""Source-page model layers (GUIDE §3a source surfaces): regeneration
triggers, the storage-time lexicon gate (a banned term stores NOTHING),
mechanical word bounds, batching, read helpers, and the failure posture
(LLMError absorbed; the budget-pause types propagate)."""

import datetime as dt
import json

import pytest

from fapd import assess, config
from fapd.llm import LLMError, PromptSizeError, TokenBudgetExceededError

# ~300 words, lexicon-clean, sentence-shaped.
GOOD_DESC = ("The agency publishes official documents each business day. "
             "Readers can verify every citation against the record. " * 30)
GOOD_SUMMARY = "An official federal publication source."
GOOD_ASSESS = ("Our ingestion has seen RSS deliveries on weekdays; requests "
               "in the window were answered and no incident is recorded in "
               "the registry notes.")


def entry(sid="test-source", **over):
    e = {
        "id": sid,
        "name": "Test Source",
        "branch": "executive",
        "parent_org": "Test Department",
        "description": "An example source used by the assess-layer tests.",
        "type": "rss",
        "tier": 2,
        "urls": {"feed": "https://example.gov/feed.xml"},
        "method": "feed poll",
        "status": "active",
        "added": "2026-07-26",
        "notes": "Coverage (gate 3): the feed carries every release.",
    }
    e.update(over)
    return e


class FakeLLM:
    """Injected in place of LLMClient (the runner-seam discipline: a test
    that could spend a real token is a defect)."""

    def __init__(self, reply=None, exc=None):
        self.calls = []
        self.reply = reply
        self.exc = exc

    def complete(self, prompt, **kw):
        self.calls.append({"prompt": prompt, **kw})
        if self.exc is not None:
            raise self.exc
        if callable(self.reply):
            text = self.reply(prompt)
        else:
            text = self.reply
        return {"text": text, "input_tokens": 1000, "output_tokens": 200,
                "model": "fake-haiku"}


def desc_reply(prompt):
    import re
    keys = re.findall(r"SOURCE key=(\S+)", prompt)
    return json.dumps({k: {"summary": GOOD_SUMMARY, "description": GOOD_DESC}
                       for k in keys})


def assess_reply(prompt):
    import re
    keys = re.findall(r"SOURCE key=(\S+)", prompt)
    return json.dumps({k: GOOD_ASSESS for k in keys})


def days_ago_iso(days):
    return (dt.datetime.now(dt.UTC)
            - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


# ----------------------------------------------------------- descriptions --


def test_description_generated_stored_and_readable(conn):
    llm = FakeLLM(reply=desc_reply)
    stats = assess.refresh_descriptions(conn, llm, [entry()])
    assert stats["generated"] == 1 and stats["rejected"] == 0
    assert len(llm.calls) == 1
    assert llm.calls[0]["model"] == config.MAP_MODEL
    assert llm.calls[0]["purpose"] == "source-desc:batch1"

    row = assess.latest_description(conn, "test-source")
    assert row["summary"] == GOOD_SUMMARY
    assert row["description"].startswith("The agency publishes")
    assert row["prompt_version"] == config.SOURCE_DESC_PROMPT_VERSION
    assert row["registry_hash"] == assess.registry_hash(entry())
    assert row["model"] == "fake-haiku"


def test_description_skips_existing_version_hash_pair(conn):
    assess.refresh_descriptions(conn, FakeLLM(reply=desc_reply), [entry()])
    llm2 = FakeLLM(reply=desc_reply)
    stats = assess.refresh_descriptions(conn, llm2, [entry()])
    assert stats == {"generated": 0, "skipped": 1, "rejected": 0,
                     "clipped": 0, "failed": 0, "llm_calls": 0}
    assert llm2.calls == []  # an untouched entry costs zero calls forever


def test_description_regenerates_on_registry_edit(conn):
    assess.refresh_descriptions(conn, FakeLLM(reply=desc_reply), [entry()])
    edited = entry(notes="Coverage (gate 3): the feed dropped its GUIDs.")
    stats = assess.refresh_descriptions(
        conn, FakeLLM(reply=desc_reply), [edited])
    assert stats["generated"] == 1 and stats["skipped"] == 0
    # both rows kept; the read helper returns the newest
    n = conn.execute("SELECT COUNT(*) FROM source_descriptions").fetchone()[0]
    assert n == 2


def test_description_regenerates_on_version_bump(conn, monkeypatch):
    assess.refresh_descriptions(conn, FakeLLM(reply=desc_reply), [entry()])
    monkeypatch.setattr(config, "SOURCE_DESC_PROMPT_VERSION",
                        config.SOURCE_DESC_PROMPT_VERSION + 1)
    stats = assess.refresh_descriptions(
        conn, FakeLLM(reply=desc_reply), [entry()])
    assert stats["generated"] == 1


def test_banned_term_description_not_stored(conn):
    bad = GOOD_DESC[:-1] + " The change was historic and sweeping."
    reply = json.dumps({"test-source":
                        {"summary": GOOD_SUMMARY, "description": bad}})
    stats = assess.refresh_descriptions(conn, FakeLLM(reply=reply), [entry()])
    assert stats["rejected"] == 1 and stats["generated"] == 0
    assert assess.latest_description(conn, "test-source") is None
    assert conn.execute(
        "SELECT COUNT(*) FROM source_descriptions").fetchone()[0] == 0


def test_banned_term_summary_rejects_whole_row(conn):
    reply = json.dumps({"test-source":
                        {"summary": "A landmark newsroom.",
                         "description": GOOD_DESC}})
    stats = assess.refresh_descriptions(conn, FakeLLM(reply=reply), [entry()])
    assert stats["rejected"] == 1 and stats["generated"] == 0
    assert assess.latest_description(conn, "test-source") is None


def test_short_description_rejected_not_padded(conn):
    reply = json.dumps({"test-source":
                        {"summary": GOOD_SUMMARY,
                         "description": "Too short to orient anyone."}})
    stats = assess.refresh_descriptions(conn, FakeLLM(reply=reply), [entry()])
    assert stats["rejected"] == 1 and stats["generated"] == 0
    assert assess.latest_description(conn, "test-source") is None


def test_long_description_clipped_to_bound(conn):
    long = ("This sentence pads the orientation with additional words. "
            * 120)  # ~1080 words
    reply = json.dumps({"test-source":
                        {"summary": GOOD_SUMMARY, "description": long}})
    stats = assess.refresh_descriptions(conn, FakeLLM(reply=reply), [entry()])
    assert stats["generated"] == 1 and stats["clipped"] == 1
    row = assess.latest_description(conn, "test-source")
    body = row["description"].removesuffix(assess._TRUNCATION_NOTE)
    assert len(body.split()) <= assess.DESC_MAX_WORDS
    assert body.rstrip().endswith(".")  # sentence boundary
    assert row["description"].endswith(assess._TRUNCATION_NOTE)


def test_descriptions_batched_many_sources_per_call(conn):
    entries = [entry(f"src-{i:02d}") for i in range(assess.MAX_SOURCE_BATCH + 1)]
    llm = FakeLLM(reply=desc_reply)
    stats = assess.refresh_descriptions(conn, llm, entries)
    assert stats["generated"] == len(entries)
    assert len(llm.calls) == 2  # 8 + 1, not one call per source


def test_description_llm_failure_does_not_raise(conn):
    llm = FakeLLM(exc=LLMError("backend down"))
    stats = assess.refresh_descriptions(conn, llm, [entry()])
    assert stats["failed"] == 1 and stats["generated"] == 0


def test_description_malformed_reply_counts_failed(conn):
    stats = assess.refresh_descriptions(
        conn, FakeLLM(reply="not json at all"), [entry()])
    assert stats["failed"] == 1
    assert assess.latest_description(conn, "test-source") is None


def test_budget_pause_types_propagate(conn):
    with pytest.raises(TokenBudgetExceededError):
        assess.refresh_descriptions(
            conn, FakeLLM(exc=TokenBudgetExceededError("throttle")), [entry()])
    with pytest.raises(PromptSizeError):
        assess.refresh_assessments(
            conn, FakeLLM(exc=PromptSizeError("too big")), [entry()],
            {}, {}, {})


# ----------------------------------------------------------- assessments --


def seed_assessment(conn, sid="test-source", generated_at=None):
    conn.execute(
        "INSERT INTO source_assessments (source_id, prompt_version,"
        " generated_at, model, trigger_reason, assessment)"
        " VALUES (?, ?, ?, 'fake-haiku', 'initial', ?)",
        (sid, config.SOURCE_ASSESS_PROMPT_VERSION,
         generated_at or days_ago_iso(1), "An earlier assessment."))
    conn.commit()


def test_assessment_initial_trigger(conn):
    llm = FakeLLM(reply=assess_reply)
    stats = assess.refresh_assessments(
        conn, llm, [entry()], {"test-source": {"items_30d": 12}},
        {"test-source": "delivering"}, {"test-source": "delivering"})
    assert stats["generated"] == 1
    assert llm.calls[0]["purpose"] == "source-assess:batch1"
    row = assess.latest_assessment(conn, "test-source")
    assert row["trigger_reason"] == "initial"
    assert row["assessment"] == GOOD_ASSESS
    # the block carried the registry entry and the measured stats
    assert "items_30d" in llm.calls[0]["prompt"]
    assert "Test Source" in llm.calls[0]["prompt"]


def test_assessment_fresh_row_skips_zero_calls(conn):
    seed_assessment(conn)
    llm = FakeLLM(reply=assess_reply)
    stats = assess.refresh_assessments(
        conn, llm, [entry()], {}, {"test-source": "delivering"},
        {"test-source": "delivering"})
    assert stats == {"generated": 0, "skipped": 1, "rejected": 0,
                     "failed": 0, "llm_calls": 0}
    assert llm.calls == []


def test_assessment_age_trigger(conn):
    seed_assessment(conn, generated_at=days_ago_iso(
        config.SOURCE_ASSESS_MAX_AGE_DAYS + 1))
    llm = FakeLLM(reply=assess_reply)
    stats = assess.refresh_assessments(
        conn, llm, [entry()], {}, {"test-source": "delivering"},
        {"test-source": "delivering"})
    assert stats["generated"] == 1
    row = assess.latest_assessment(conn, "test-source")
    assert row["trigger_reason"] == "age-30d"
    # the previous assessment rode in the prompt (what-changed input)
    assert "An earlier assessment." in llm.calls[0]["prompt"]


def test_assessment_health_change_trigger(conn):
    seed_assessment(conn)  # fresh — age alone would skip
    llm = FakeLLM(reply=assess_reply)
    stats = assess.refresh_assessments(
        conn, llm, [entry()], {}, {"test-source": "degraded"},
        {"test-source": "delivering"})
    assert stats["generated"] == 1
    row = assess.latest_assessment(conn, "test-source")
    assert row["trigger_reason"] == "health-change"


def test_banned_term_assessment_not_stored(conn):
    reply = json.dumps(
        {"test-source": "Our crackdown on unprecedented delivery quirks."})
    stats = assess.refresh_assessments(
        conn, FakeLLM(reply=reply), [entry()], {}, {}, {})
    assert stats["rejected"] == 1 and stats["generated"] == 0
    assert assess.latest_assessment(conn, "test-source") is None


def test_assessment_llm_failure_does_not_raise(conn):
    stats = assess.refresh_assessments(
        conn, FakeLLM(exc=LLMError("backend down")), [entry()], {}, {}, {})
    assert stats["failed"] == 1 and stats["generated"] == 0


def test_latest_helpers_return_newest_and_batch_forms_agree(conn):
    old, new = days_ago_iso(10), days_ago_iso(2)
    seed_assessment(conn, generated_at=old)
    seed_assessment(conn, generated_at=new)
    newest = assess.latest_assessment(conn, "test-source")
    assert newest["generated_at"] == new
    batch = assess.latest_assessments(conn)
    assert batch["test-source"] == newest
    assert assess.latest_assessment(conn, "absent") is None
    assert assess.latest_descriptions(conn) == {}


def test_registry_hash_is_order_insensitive_and_content_sensitive():
    a = entry()
    b = dict(reversed(list(entry().items())))
    assert assess.registry_hash(a) == assess.registry_hash(b)
    assert assess.registry_hash(a) != assess.registry_hash(
        entry(notes="edited"))


def test_prompts_carry_full_banned_list_and_no_placeholder():
    for prompt in (assess._ASSESS_PROMPT, assess._DESC_PROMPT):
        low = prompt.lower()
        assert all(t in low for t in config.BANNED_TERMS)
        assert "{banned}" not in prompt

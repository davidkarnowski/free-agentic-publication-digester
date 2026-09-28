"""Compose stage tests: idempotency, input construction, storage — for
both LLM layers: the Day in Review (compose_day) and the per-section
quick-read synopses (compose_sections)."""

import json

import pytest
from conftest import install_digest_day_default

from fapd import compose, config, db


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
    c = install_digest_day_default(db.connect(tmp_path / "meta.db"))
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
        " VALUES ('FR-2026-07-23','2026-1',?, 'official','FR-SEL-01','Official summary text.','2026-07-23T00:00:00Z')",
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


def test_recomposes_when_newer_summaries_arrive(conn, monkeypatch):
    clock = iter(["2026-07-23T10:00:00Z", "2026-07-23T12:00:00Z"])
    monkeypatch.setattr(compose, "utc_now_iso", lambda: next(clock))
    llm = FakeLLM()
    compose.compose_day(conn, llm, "2026-07-23")  # stored at 10:00
    # Late-arriving item (e.g. Record published after first digest run)
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, text, char_count, extracted_at, extractor_version)"
        " VALUES ('FR-2026-07-23','2026-2','FR','RULE','Late title','body',4,'x',1)"
    )
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " inclusion_rule, summary, created_at)"
        " VALUES ('FR-2026-07-23','2026-2',?, 'official','FR-SEL-01',"
        " 'Late-arriving summary.','2026-07-23T11:00:00Z')",
        (config.PROMPT_VERSION,),
    )
    conn.commit()
    llm2 = FakeLLM(text="Refreshed synthesis.")
    stats = compose.compose_day(conn, llm2, "2026-07-23")
    assert stats["composed"] == 1
    assert "Late-arriving summary." in llm2.calls[0]["prompt"]
    assert compose.get_day_summary(conn, "2026-07-23")["summary"] == "Refreshed synthesis."
    # And it settles: a further rerun with nothing new skips again.
    llm3 = FakeLLM()
    assert compose.compose_day(conn, llm3, "2026-07-23")["skipped_existing"] == 1
    assert not llm3.calls


def test_day_prompt_version_scoped(conn):
    # A stored composition at a different prompt version must not satisfy
    # the idempotency check — version bumps regenerate.
    conn.execute(
        "INSERT INTO day_summaries (date, prompt_version, model, summary,"
        " input_tokens, output_tokens, created_at)"
        " VALUES ('2026-07-23', 999, 'x', 'old prose', 0, 0, '2026-07-23T09:00:00Z')"
    )
    conn.commit()
    llm = FakeLLM()
    assert compose.compose_day(conn, llm, "2026-07-23")["composed"] == 1
    assert len(llm.calls) == 1


def test_mechanical_counts_groups_by_collection_and_doc_type(conn):
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, text, char_count, extracted_at, extractor_version)"
        " VALUES ('FR-2026-07-23','2026-3','FR','RULE','Another rule','body',4,'x',1)"
    )
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, text, char_count, extracted_at, extractor_version)"
        " VALUES ('FR-2026-07-23','2026-4','FR',NULL,'Typeless','body',4,'x',1)"
    )
    conn.commit()
    assert compose._mechanical_counts(conn, "2026-07-23") == {
        "FR/RULE": 2, "FR/?": 1}
    assert compose._mechanical_counts(conn, "2020-01-01") == {}


# ---------------------------------------------------------------------------
# Section quick-read synopses (compose_sections)
# ---------------------------------------------------------------------------


def seed_section_summary(conn, pid, gid, rule, collection="BILLS",
                         doc_type="Enrolled-Bill", created="2026-07-23T00:00:00Z"):
    conn.execute(
        "INSERT OR IGNORE INTO packages (package_id, collection, last_modified,"
        " first_seen_at, date_issued, fetch_status)"
        " VALUES (?, ?, 'x', 'x', '2026-07-23', 'fetched')",
        (pid, collection),
    )
    conn.execute(
        "INSERT OR IGNORE INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, title, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, ?, ?, ?, 'A title', 'body', 4, 'x', 1)",
        (pid, gid, collection, doc_type),
    )
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " inclusion_rule, summary, created_at) VALUES (?, ?, ?, 'official', ?,"
        " 'A stored summary.', ?)",
        (pid, gid, config.PROMPT_VERSION, rule, created),
    )
    conn.commit()


def test_compose_sections_writes_synopses(conn):
    # conn fixture seeds one FR-SEL-01 summary -> section key "rules"
    llm = FakeLLM(text=json.dumps({"rules": "One final rule was published."}))
    stats = compose.compose_sections(conn, llm, "2026-07-23")
    assert stats["composed"] == 1
    assert "SECTION key=rules (1 items)" in llm.calls[0]["prompt"]
    assert llm.calls[0]["model"] == config.PLAIN_MODEL
    assert compose.get_section_synopses(conn, "2026-07-23") == {
        "rules": "One final rule was published."}


def test_compose_sections_skip_existing(conn):
    llm = FakeLLM(text=json.dumps({"rules": "A sentence."}))
    compose.compose_sections(conn, llm, "2026-07-23")
    stats = compose.compose_sections(conn, llm, "2026-07-23")
    assert stats == {"composed": 0, "skipped_existing": 1,
                     "input_tokens": 0, "output_tokens": 0}
    assert len(llm.calls) == 1


def test_compose_sections_empty_day_no_call(conn):
    llm = FakeLLM()
    stats = compose.compose_sections(conn, llm, "2020-01-01")
    assert stats["composed"] == 0 and not llm.calls


def test_compose_sections_recomposes_on_newer_summary(conn, monkeypatch):
    # utc_now_iso is called once per written section row: 1 on the first
    # compose, 2 on the refresh.
    clock = iter(["2026-07-23T10:00:00Z",
                  "2026-07-23T12:00:00Z", "2026-07-23T12:00:00Z"])
    monkeypatch.setattr(compose, "utc_now_iso", lambda: next(clock))
    llm = FakeLLM(text=json.dumps({"rules": "First pass."}))
    compose.compose_sections(conn, llm, "2026-07-23")  # stored at 10:00
    seed_section_summary(conn, "BILLS-119hr1enr", "", "BILLS-SEL-01",
                         created="2026-07-23T11:00:00Z")  # newer than 10:00
    llm2 = FakeLLM(text=json.dumps({"rules": "Refreshed.", "legislation": "One bill."}))
    stats = compose.compose_sections(conn, llm2, "2026-07-23")
    assert stats["composed"] == 2
    assert compose.get_section_synopses(conn, "2026-07-23") == {
        "rules": "Refreshed.", "legislation": "One bill."}
    # Settles: nothing newer than the freshly-written 12:00 rows.
    llm3 = FakeLLM()
    assert compose.compose_sections(conn, llm3, "2026-07-23")["skipped_existing"] == 1


def test_compose_sections_fenced_json_recovered(conn):
    fenced = "```json\n" + json.dumps({"rules": "Fenced sentence."}) + "\n```"
    llm = FakeLLM(text=fenced)
    assert compose.compose_sections(conn, llm, "2026-07-23")["composed"] == 1
    assert compose.get_section_synopses(conn, "2026-07-23")["rules"] == "Fenced sentence."


def test_compose_sections_regex_fallback_recovers_embedded_json(conn):
    llm = FakeLLM(text='Here are the synopses: {"rules": "Embedded."} Hope that helps!')
    assert compose.compose_sections(conn, llm, "2026-07-23")["composed"] == 1
    assert compose.get_section_synopses(conn, "2026-07-23")["rules"] == "Embedded."


def test_compose_sections_partial_write_when_model_omits_a_key(conn):
    seed_section_summary(conn, "BILLS-119hr1enr", "", "BILLS-SEL-01")
    llm = FakeLLM(text=json.dumps({"rules": "Only this one."}))  # legislation omitted
    stats = compose.compose_sections(conn, llm, "2026-07-23")
    assert stats["composed"] == 1  # written < grouped, no crash, no fabrication
    assert compose.get_section_synopses(conn, "2026-07-23") == {
        "rules": "Only this one."}


def test_section_items_skip_crec_votes_and_group_by_doc_type(conn):
    seed_section_summary(conn, "CREC-2026-07-23", "PgS1", "CREC-SEL-01",
                         collection="CREC", doc_type="SENATE")
    seed_section_summary(conn, "CREC-2026-07-23", "PgS2", "CREC-SEL-02",
                         collection="CREC", doc_type="SENATE")  # vote: own subsection
    grouped = compose._section_items(conn, "2026-07-23")
    assert [r["inclusion_rule"] for r in grouped["senate"]] == ["CREC-SEL-01"]
    assert "house" not in grouped  # no HOUSE doc_type seeded
    assert [r["inclusion_rule"] for r in grouped["rules"]] == ["FR-SEL-01"]


# ---------------------------------------------------------------------------
# The short Day in Review (GUIDE §3a, amended 2026-09-28)
# ---------------------------------------------------------------------------

QUIET = "2026-09-27"  # a Sunday: the day that prompted the rule


def _package(c, package_id, collection, day=QUIET):
    c.execute(
        "INSERT INTO packages (package_id, collection, last_modified, first_seen_at,"
        " date_issued, fetch_status, digest_day) VALUES (?, ?, 'x', 'x', ?, 'fetched', ?)",
        (package_id, collection, day, day),
    )


def _text(c, package_id, granule_id, collection, doc_type, title, metadata, body="body"):
    c.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'x', 1)",
        (package_id, granule_id, collection, doc_type, title,
         metadata.pop("agency", None), json.dumps(metadata), body, len(body)),
    )


@pytest.fixture
def quiet(conn):
    """A Sunday like 2026-09-27: district opinions (counted, never
    summarized), one agency release the agency dated today (listed), and
    one it dated to an earlier day (counted under AGENCYPR-EX-01, never
    listed)."""
    for n, court in enumerate(["District of Connecticut", "District of Connecticut",
                               "Northern District of Texas"]):
        pid = f"USCOURTS-d{n}-26-0000{n}"
        _package(conn, pid, "USCOURTS")
        _text(conn, pid, f"{pid}-0", "USCOURTS", "DISTRICT", f"Doe{n} v. Roe{n}",
              {"court_name": f"United States District Court for the {court}"},
              body=f"SECRET-OPINION-BODY-{n}")
    _package(conn, "AGENCYPR-cisa-1", "AGENCYPR")
    _text(conn, "AGENCYPR-cisa-1", "", "AGENCYPR", "PRESS",
          "CISA Adds Two Known Exploited Vulnerabilities to Catalog",
          {"agency": "CISA Cybersecurity Advisories",
           "claimed_published_at": f"{QUIET}T09:00:00", "url": "https://example.gov/a"})
    _package(conn, "AGENCYPR-va-old", "AGENCYPR")
    _text(conn, "AGENCYPR-va-old", "", "AGENCYPR", "PRESS", "An older VA story",
          {"agency": "VA News Releases",
           "claimed_published_at": "2026-09-20T09:00:00", "url": "https://example.gov/b"})
    conn.commit()
    return conn


def _row(c, date=QUIET):
    return c.execute("SELECT * FROM day_summaries WHERE date = ?", (date,)).fetchone()


def test_a_day_where_nothing_qualified_gets_a_short_review(quiet):
    llm = FakeLLM(text="A short review today.")
    stats = compose.compose_day(quiet, llm, QUIET)
    assert stats["composed"] == 1 and stats["short"] == 1
    assert len(llm.calls) == 1
    call = llm.calls[0]
    assert call["purpose"] == "compose:short-review"
    assert call["model"] == config.COMPOSE_MODEL
    row = _row(quiet)
    assert row["kind"] == "short"
    assert row["kind_version"] == config.SHORT_REVIEW_PROMPT_VERSION
    assert row["prompt_version"] == config.COMPOSE_PROMPT_VERSION
    assert compose.get_day_summary(quiet, QUIET)["kind"] == "short"


def test_the_short_review_sees_counts_and_listed_titles_only(quiet):
    """§6 r4: the model sees what the digest lists and counts, never an
    excluded document's text or case name."""
    llm = FakeLLM()
    compose.compose_day(quiet, llm, QUIET)
    prompt = llm.calls[0]["prompt"]
    assert '"CISA Adds Two Known Exploited Vulnerabilities to Catalog"' in prompt
    assert "CISA Cybersecurity Advisories" in prompt
    # Counted under AGENCYPR-EX-01, never listed as today's news.
    assert "An older VA story" not in prompt
    # District opinions arrive as counts by court, nothing more.
    assert "District of Connecticut (district): 2" in prompt
    assert "Northern District of Texas (district): 1" in prompt
    assert "SECRET-OPINION-BODY" not in prompt and "Doe0 v. Roe0" not in prompt
    assert '"USCOURTS/DISTRICT": 3' in prompt
    # The listed collection's raw count (which includes the backfill
    # release) is not restated beside its listed titles.
    assert "AGENCYPR/PRESS" not in prompt
    # The Sunday is explained in fedcal's own words.
    assert "Sunday is not a federal business day" in prompt


def test_a_short_review_rerun_makes_no_call(quiet):
    compose.compose_day(quiet, FakeLLM(), QUIET)
    llm = FakeLLM()
    stats = compose.compose_day(quiet, llm, QUIET)
    assert stats["skipped_existing"] == 1 and not llm.calls


def test_no_short_review_when_documents_qualified_but_went_unsummarized(quiet):
    """An appellate opinion passed USCOURTS-SEL-01 but has no summary:
    that is a missing layer, not a quiet day, and "nothing met the
    summary rules" would be false."""
    _package(quiet, "USCOURTS-ca2-26-00001", "USCOURTS")
    _text(quiet, "USCOURTS-ca2-26-00001", "USCOURTS-ca2-26-00001-0", "USCOURTS",
          "APPELLATE", "Smith v. Jones",
          {"court_name": "United States Court of Appeals for the Second Circuit"})
    quiet.commit()
    llm = FakeLLM()
    stats = compose.compose_day(quiet, llm, QUIET)
    assert stats["composed"] == 0 and not llm.calls
    assert _row(quiet) is None


def test_a_short_review_is_withdrawn_once_something_qualifies(quiet):
    compose.compose_day(quiet, FakeLLM(), QUIET)
    _package(quiet, "USCOURTS-ca2-26-00001", "USCOURTS")
    _text(quiet, "USCOURTS-ca2-26-00001", "USCOURTS-ca2-26-00001-0", "USCOURTS",
          "APPELLATE", "Smith v. Jones",
          {"court_name": "United States Court of Appeals for the Second Circuit"})
    quiet.commit()
    # Qualified but not yet summarized: the short review's claim is now
    # false, so it goes, and nothing replaces it yet.
    llm = FakeLLM()
    assert compose.compose_day(quiet, llm, QUIET)["composed"] == 0
    assert not llm.calls and _row(quiet) is None
    # Once the summary exists, the ordinary Day in Review is composed.
    quiet.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method, model,"
        " inclusion_rule, summary, created_at) VALUES (?, ?, ?, 'llm', 'haiku',"
        " 'USCOURTS-SEL-01', 'The court affirmed.', '2026-09-28T01:00:00Z')",
        ("USCOURTS-ca2-26-00001", "USCOURTS-ca2-26-00001-0", config.PROMPT_VERSION),
    )
    quiet.commit()
    llm = FakeLLM(text="Full synthesis.")
    assert compose.compose_day(quiet, llm, QUIET)["composed"] == 1
    assert llm.calls[0]["purpose"] == "compose:day-in-review"
    assert _row(quiet)["kind"] == "full"


def test_a_short_review_that_fails_the_lexicon_gate_is_not_stored(quiet):
    """Gated before storage: a failing review is dropped and the digest
    renders without a Day in Review, so it can never block the day."""
    llm = FakeLLM(text="A short review of a landmark Sunday.")
    stats = compose.compose_day(quiet, llm, QUIET)
    assert stats["composed"] == 0 and stats["gated"] == 1
    assert stats["input_tokens"] == 30000, "spent tokens stay visible in stats"
    assert _row(quiet) is None


def test_a_banned_word_inside_a_quoted_official_title_passes_the_gate(quiet):
    """The §2 phrase-scoped exemption applies at storage exactly as at
    render: quoting the agency's own title is not our adjective."""
    _package(quiet, "AGENCYPR-nps-1", "AGENCYPR")
    _text(quiet, "AGENCYPR-nps-1", "", "AGENCYPR", "PRESS",
          "Historic Preservation Grants Announced",
          {"agency": "NPS News Releases",
           "claimed_published_at": f"{QUIET}T10:00:00", "url": "https://example.gov/c"})
    quiet.commit()
    llm = FakeLLM(text='NPS News Releases published "Historic Preservation Grants Announced."')
    assert compose.compose_day(quiet, llm, QUIET)["composed"] == 1
    assert _row(quiet)["kind"] == "short"

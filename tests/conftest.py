"""Shared test infrastructure.

Two jobs:
1. Put scripts/ on sys.path so tests can import the CLI modules
   (run_pipeline, digest) — they are plain modules with no package.
2. Hold the fixtures shared by the rules and analyze suites (the corpus
   spans every selection rule, so both test files assert against it).
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from fapd import db

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
LONG_OFFICIAL = "The Commission adopts rule amendments. " * 40  # ~1559 chars normalized


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
    seed_item(conn, "USCOURTS-ca9-26-01234", "USCOURTS-ca9-26-01234-0",
              "USCOURTS", "APPELLATE", "The court affirmed the judgment. " * 20,
              metadata={"court_code": "ca9",
                        "court_name": "United States Court of Appeals"
                                      " for the Ninth Circuit",
                        "case_number": "26-01234",
                        "date_filed": DATE})                               # USCOURTS-SEL-01
    seed_item(conn, "USCOURTS-cit-26-00099", "USCOURTS-cit-26-00099-0",
              "USCOURTS", "NATIONAL", "Judgment entered for the plaintiff. " * 20,
              metadata={"court_code": "cit",
                        "court_name": "United States Court of International Trade",
                        "case_number": "26-00099",
                        "date_filed": DATE})                               # USCOURTS-SEL-02
    seed_item(conn, "USCOURTS-txnd-26-00777", "USCOURTS-txnd-26-00777-0",
              "USCOURTS", "DISTRICT", "The motion is denied. " * 20)      # USCOURTS-EX-01
    seed_item(conn, "USCOURTS-nysb-26-00888", "USCOURTS-nysb-26-00888-0",
              "USCOURTS", "BANKRUPTCY", "The claim is allowed. " * 20)    # USCOURTS-EX-02


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
    ("USCOURTS-ca9-26-01234", "USCOURTS-ca9-26-01234-0"): "USCOURTS-SEL-01",
    ("USCOURTS-cit-26-00099", "USCOURTS-cit-26-00099-0"): "USCOURTS-SEL-02",
}

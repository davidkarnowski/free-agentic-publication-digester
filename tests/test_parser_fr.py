"""Tests for the FR parser: a synthetic issue covering all four document
types, FRDOC/graphics quirks, and a smoke pass over the real raw archive."""

from collections import Counter
from pathlib import Path

import pytest

from fapd.parsers import fr

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "FR"

# Mirrors real-archive structure: labeled preamble sections with <HD> labels,
# a NEWPART-nested PRESDOCS section, a PRESDOCU whose <FRDOC> is truncated by
# a sibling <FILED>, and both substantive and boilerplate <GPH><GID> entries.
ISSUE_XML = """<?xml version="1.0"?>
<FEDREG>
<VOL>91</VOL><NO>139</NO><DATE>Thursday, July 23, 2026</DATE>
<RULES>
 <RULE>
  <PREAMB>
   <PRTPAGE P="1000"/>
   <AGENCY TYPE="F">DEPARTMENT OF TESTING</AGENCY>
   <SUBAGY>Test Administration</SUBAGY>
   <CFR>14 CFR Part 39</CFR>
   <CFR>14 CFR Part 71</CFR>
   <SUBJECT>Airworthiness Directives; Example Aircraft</SUBJECT>
   <AGY><HD SOURCE="HED">AGENCY:</HD><P>Test Administration (TA), DOT.</P></AGY>
   <ACT><HD SOURCE="HED">ACTION:</HD><P>Final rule.</P></ACT>
   <SUM><HD SOURCE="HED">SUMMARY:</HD><P>This rule requires an example inspection.</P></SUM>
   <DATES><HD SOURCE="HED">DATES:</HD><P>Effective August 24, 2026.</P></DATES>
  </PREAMB>
  <SUPLINF>
   <P>Rule body text with an equation.</P>
   <GPH DEEP="12" SPAN="1"><GID>EN23JY26.004</GID></GPH>
   <GPH DEEP="24" SPAN="1"><GID>Example.EPS</GID></GPH>
   <PRTPAGE P="1003"/>
  </SUPLINF>
  <FRDOC>[FR Doc. 2026-11111 Filed 7-22-26; 8:45 am]</FRDOC>
  <BILCOD>BILLING CODE 4910-13-P</BILCOD>
 </RULE>
</RULES>
<PRORULES>
 <PRORULE>
  <PREAMB>
   <PRTPAGE P="1100"/>
   <AGENCY TYPE="F">DEPARTMENT OF PROPOSALS</AGENCY>
   <CFR>40 CFR Part 52</CFR>
   <SUBJECT>Proposed Example Standards</SUBJECT>
   <AGY><HD SOURCE="HED">AGENCY:</HD><P>Proposal Agency (PA).</P></AGY>
   <ACT><HD SOURCE="HED">ACTION:</HD><P>Proposed rule.</P></ACT>
   <SUM><HD SOURCE="HED">SUMMARY:</HD><P>PA proposes an example standard.</P></SUM>
   <EFFDATE><HD SOURCE="HED">DATES:</HD>
    <P>Comments must be received on or before September 1, 2026.</P></EFFDATE>
  </PREAMB>
  <SUPLINF><P>Proposal body.</P></SUPLINF>
  <FRDOC>[FR Doc. 2026-22222 Filed 7-22-26; 8:45 am]</FRDOC>
  <BILCOD>BILLING CODE 6560-50-P</BILCOD>
 </PRORULE>
</PRORULES>
<NOTICES>
 <NOTICE>
  <PREAMB>
   <PRTPAGE P="1200"/>
   <AGENCY TYPE="F">DEPARTMENT OF NOTICES</AGENCY>
   <SUBJECT>Example Advisory Board; Meeting</SUBJECT>
   <AGY><HD SOURCE="HED">AGENCY:</HD><P>Notice Service, DON.</P></AGY>
   <ACT><HD SOURCE="HED">ACTION:</HD><P>Notice of meeting.</P></ACT>
  </PREAMB>
  <FRDOC>[FR Doc. 2026-33333 Filed 7-22-26; 8:45 am]</FRDOC>
  <BILCOD>BILLING CODE 3411-15-P</BILCOD>
 </NOTICE>
</NOTICES>
<NEWPART>
 <PTITLE><PRTPAGE P="1300"/><PARTNO>Part II</PARTNO><PRES>The President</PRES></PTITLE>
 <PRESDOCS>
  <PRESDOCU>
   <PROCLA>
    <TITLE3>Title 3&#8212;</TITLE3>
    <PRES>The President</PRES>
    <PROC>Proclamation 99999 of July 20, 2026</PROC>
    <HD SOURCE="HD1">Example Observance Week, 2026</HD>
    <FP>NOW, THEREFORE, an example proclamation body.</FP>
    <PRTPAGE P="1301"/>
    <GPH DEEP="18" SPAN="1"><GID>Example.EPS</GID></GPH>
    <PSIG>Example Signature</PSIG>
    <FRDOC>[FR Doc. 2026-44444</FRDOC>
    <FILED>Filed 7-22-26; 11:15 am]</FILED>
    <BILCOD>Billing code 3395-F4-P</BILCOD>
   </PROCLA>
  </PRESDOCU>
 </PRESDOCS>
</NEWPART>
</FEDREG>
"""

PACKAGE = {"package_id": "FR-2026-07-23", "collection": "FR", "date_issued": "2026-07-23"}


@pytest.fixture
def records(tmp_path):
    path = tmp_path / "FR-2026-07-23.xml"
    path.write_text(ISSUE_XML, encoding="utf-8")
    return list(fr.parse(path, PACKAGE))


def _by_type(records, doc_type):
    return next(r for r in records if r["doc_type"] == doc_type)


def test_yields_all_four_doc_types(records):
    assert len(records) == 4
    assert {r["doc_type"] for r in records} == {"RULE", "PRORULE", "NOTICE", "PRESDOCU"}
    for rec in records:
        assert set(rec) == {
            "granule_id",
            "doc_type",
            "title",
            "agency",
            "metadata",
            "text",
            "graphics_substantive",
            "graphics_boilerplate",
        }


def test_rule_record(records):
    rec = _by_type(records, "RULE")
    assert rec["granule_id"] == "2026-11111"
    assert rec["title"] == "Airworthiness Directives; Example Aircraft"
    assert rec["agency"] == "DEPARTMENT OF TESTING"
    md = rec["metadata"]
    assert md["cfr"] == "14 CFR Part 39; 14 CFR Part 71"
    assert md["action"] == "Final rule."
    assert md["summary"] == "This rule requires an example inspection."
    assert md["dates"] == "Effective August 24, 2026."
    assert md["billing_code"] == "4910-13-P"
    assert md["pages"] == {"first": "1000", "last": "1003"}
    # Verbatim text, whitespace-normalized, with GID filenames excluded.
    assert "Rule body text with an equation." in rec["text"]
    assert "EN23JY26.004" not in rec["text"]
    assert "Example.EPS" not in rec["text"]
    # Labels are stripped from labeled sections but kept in the full text.
    assert "SUMMARY:" in rec["text"]


def test_rule_graphics_classification(records):
    rec = _by_type(records, "RULE")
    assert rec["graphics_substantive"] == 1  # EN23JY26.004 (rule FR-GPH-01)
    assert rec["graphics_boilerplate"] == 1  # Example.EPS


def test_prorule_effdate_variant(records):
    rec = _by_type(records, "PRORULE")
    assert rec["granule_id"] == "2026-22222"
    assert rec["metadata"]["dates"] == (
        "Comments must be received on or before September 1, 2026."
    )
    assert rec["metadata"]["cfr"] == "40 CFR Part 52"
    assert rec["graphics_substantive"] == 0
    assert rec["graphics_boilerplate"] == 0


def test_notice_without_optional_fields(records):
    rec = _by_type(records, "NOTICE")
    assert rec["granule_id"] == "2026-33333"
    assert rec["title"] == "Example Advisory Board; Meeting"
    assert rec["agency"] == "DEPARTMENT OF NOTICES"
    md = rec["metadata"]
    assert "cfr" not in md
    assert "summary" not in md
    assert "dates" not in md
    assert md["action"] == "Notice of meeting."


def test_presdocu_nested_in_newpart(records):
    rec = _by_type(records, "PRESDOCU")
    # FRDOC truncated by the sibling <FILED> element still parses.
    assert rec["granule_id"] == "2026-44444"
    assert rec["title"] == "Example Observance Week, 2026"
    assert rec["agency"] is None
    assert rec["metadata"]["billing_code"] == "3395-F4-P"
    assert rec["metadata"]["pages"] == {"first": "1301", "last": "1301"}
    assert rec["graphics_substantive"] == 0
    assert rec["graphics_boilerplate"] == 1
    assert "example proclamation body" in rec["text"]


def test_metadata_is_json_serializable(records):
    import json

    for rec in records:
        json.dumps(rec["metadata"])


# --- Smoke tests against the real archive -----------------------------------

REAL_FILES = sorted(DATA_DIR.glob("*/FR-*.xml")) if DATA_DIR.is_dir() else []


@pytest.mark.skipif(not REAL_FILES, reason="no raw FR archive on disk")
@pytest.mark.parametrize("path", REAL_FILES, ids=lambda p: p.stem)
def test_real_issue_smoke(path):
    package = {
        "package_id": path.stem,
        "collection": "FR",
        "date_issued": path.stem.removeprefix("FR-"),
    }
    records = list(fr.parse(path, package))
    assert len(records) > 0
    import re

    for rec in records:
        # Corrections to already-published documents carry a C<n>- prefix
        # (first seen in FR-2026-07-29: C1-2026-13124). Real-issue shape,
        # not an anomaly.
        assert re.fullmatch(r"(C\d+-)?\d{4}-\d+", rec["granule_id"])
        assert rec["doc_type"] in {"RULE", "PRORULE", "NOTICE", "PRESDOCU"}
        assert rec["text"]
    counts = Counter(r["doc_type"] for r in records)
    # Plausibility: notices dominate every real issue in the archive.
    assert counts["NOTICE"] > 0
    assert counts["NOTICE"] == max(counts.values())


@pytest.mark.skipif(
    not (DATA_DIR / "2026-07-23" / "FR-2026-07-23.xml").is_file(),
    reason="FR-2026-07-23 not on disk",
)
def test_real_issue_graphics_totals():
    path = DATA_DIR / "2026-07-23" / "FR-2026-07-23.xml"
    records = list(fr.parse(path, PACKAGE))
    assert sum(r["graphics_substantive"] for r in records) == 46
    assert sum(r["graphics_boilerplate"] for r in records) == 8

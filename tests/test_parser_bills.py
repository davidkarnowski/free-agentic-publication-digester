"""Tests for the BILLS parser: synthetic <bill>/<resolution> fixtures,
package-id parsing table, and a smoke pass over the real raw archive."""

from pathlib import Path

import pytest

from fapd.parsers import bills

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "BILLS"

BILL_XML = """<?xml version="1.0"?>
<!DOCTYPE bill PUBLIC "-//US Congress//DTDs/bill.dtd//EN" "bill.dtd">
<bill bill-stage="Introduced-in-House" public-private="public" stage-count="1">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dublinCore>
<dc:title>119 HR 9599 IH: Example Modernization Act</dc:title>
<dc:publisher>U.S. House of Representatives</dc:publisher>
<dc:rights>this file is not subject to copyright protection</dc:rights>
</dublinCore>
</metadata>
<form>
<legis-num display="yes">H. R. 9599</legis-num>
<current-chamber>IN THE HOUSE OF REPRESENTATIVES</current-chamber>
<action><action-desc><sponsor name-id="P000608">Mr. Peters</sponsor> (for himself,
<cosponsor name-id="J000302">Mr. Joyce of Pennsylvania</cosponsor>, and
<cosponsor name-id="A000148">Mr. Auchincloss</cosponsor>) introduced the following
bill</action-desc></action>
<official-title display="yes">To modernize an example program.</official-title>
</form>
<legis-body>
<section><enum>1.</enum><header>Short title</header>
<text>This Act may be cited as the <quote>Example Modernization Act</quote>.</text>
</section>
</legis-body>
</bill>
"""

RESOLUTION_XML = """<?xml version="1.0"?>
<resolution resolution-stage="Agreed-to-Senate" public-private="public">
<form>
<legis-num>S. RES. 811</legis-num>
<current-chamber>IN THE SENATE OF THE UNITED STATES</current-chamber>
<official-title>Expressing support for an example designation.</official-title>
</form>
<resolution-body>
<section><enum>1.</enum><text>That the Senate supports the example.</text></section>
</resolution-body>
</resolution>
"""


def _parse_one(tmp_path, name, xml, package_id):
    path = tmp_path / name
    path.write_text(xml, encoding="utf-8")
    package = {"package_id": package_id, "collection": "BILLS", "date_issued": "2026-07-06"}
    records = list(bills.parse(path, package))
    assert len(records) == 1
    return records[0]


def test_bill_fixture(tmp_path):
    rec = _parse_one(tmp_path, "BILLS-119hr9599ih.xml", BILL_XML, "BILLS-119hr9599ih")
    assert rec["granule_id"] == ""
    assert rec["doc_type"] == "Introduced-in-House"
    assert rec["title"] == "119 HR 9599 IH: Example Modernization Act"
    assert rec["agency"] is None
    assert rec["graphics_substantive"] == 0
    assert rec["graphics_boilerplate"] == 0

    md = rec["metadata"]
    assert md["congress"] == 119
    assert md["bill_type"] == "hr"
    assert md["bill_number"] == 9599
    assert md["bill_version"] == "ih"
    assert md["chamber"] == "House"
    assert md["stage"] == "Introduced-in-House"
    assert md["legis_num"] == "H. R. 9599"
    assert md["sponsors"] == ["Mr. Peters", "Mr. Joyce of Pennsylvania", "Mr. Auchincloss"]

    text = rec["text"]
    assert "This Act may be cited as the Example Modernization Act ." in text
    assert "To modernize an example program." in text
    # dublinCore block is boilerplate, not bill text.
    assert "copyright" not in text
    assert "U.S. House of Representatives" not in text
    # Whitespace-normalized: no newlines, no runs of spaces.
    assert "\n" not in text
    assert "  " not in text


def test_resolution_fixture(tmp_path):
    rec = _parse_one(tmp_path, "BILLS-119sres811ats.xml", RESOLUTION_XML, "BILLS-119sres811ats")
    assert rec["granule_id"] == ""
    assert rec["doc_type"] == "Agreed-to-Senate"
    # No dublinCore block: title falls back to <official-title>.
    assert rec["title"] == "Expressing support for an example designation."

    md = rec["metadata"]
    assert md["congress"] == 119
    assert md["bill_type"] == "sres"
    assert md["bill_number"] == 811
    assert md["bill_version"] == "ats"
    assert md["chamber"] == "Senate"
    assert md["stage"] == "Agreed-to-Senate"
    assert md["legis_num"] == "S. RES. 811"
    assert md["sponsors"] == []

    assert "That the Senate supports the example." in rec["text"]


def test_doc_type_falls_back_to_version_code(tmp_path):
    xml = BILL_XML.replace(' bill-stage="Introduced-in-House"', "")
    rec = _parse_one(tmp_path, "BILLS-119hr8888enr.xml", xml, "BILLS-119hr8888enr")
    assert rec["doc_type"] == "enr"
    assert rec["metadata"]["stage"] is None


@pytest.mark.parametrize(
    ("package_id", "expected"),
    [
        # Longest-type-first matching: hres/hconres must not be eaten by "hr".
        ("BILLS-119hr8888enr", (119, "hr", 8888, "enr")),
        ("BILLS-119hres1449ih", (119, "hres", 1449, "ih")),
        ("BILLS-119hconres55eh", (119, "hconres", 55, "eh")),
        ("BILLS-119hjres105ih", (119, "hjres", 105, "ih")),
        ("BILLS-119s1234is", (119, "s", 1234, "is")),
        ("BILLS-119sres811ats", (119, "sres", 811, "ats")),
        ("BILLS-119sjres74is", (119, "sjres", 74, "is")),
        ("BILLS-119sconres37enr", (119, "sconres", 37, "enr")),
        ("BILLS-118hr1118rfs", (118, "hr", 1118, "rfs")),
        ("BILLS-119hr123pcs", (119, "hr", 123, "pcs")),
    ],
)
def test_parse_package_id(package_id, expected):
    ids = bills.parse_package_id(package_id)
    assert ids is not None
    congress, bill_type, number, version = expected
    assert ids["congress"] == congress
    assert ids["bill_type"] == bill_type
    assert ids["bill_number"] == number
    assert ids["version"] == version


@pytest.mark.parametrize(
    "bad",
    ["", "BILLS-119hr8888", "BILLS-hr8888enr", "CREC-2026-07-06", "BILLS-119xyz1ih"],
)
def test_parse_package_id_rejects_non_bills(bad):
    assert bills.parse_package_id(bad) is None


@pytest.mark.skipif(not DATA_DIR.is_dir(), reason="raw BILLS archive not present")
def test_real_corpus_smoke():
    files = sorted(DATA_DIR.rglob("*.xml"))
    assert files, "archive directory exists but holds no XML"

    doc_types = set()
    congresses = set()
    for path in files:
        package = {
            "package_id": path.stem,
            "collection": "BILLS",
            "date_issued": path.parent.name,
        }
        records = list(bills.parse(path, package))
        assert len(records) == 1, path.name
        rec = records[0]
        assert rec["granule_id"] == ""
        assert rec["text"], path.name
        assert rec["doc_type"], path.name
        assert isinstance(rec["metadata"]["congress"], int), path.name
        doc_types.add(rec["doc_type"])
        congresses.add(rec["metadata"]["congress"])

    # Archive is the 119th Congress plus a couple of stray 118th files
    # (data/raw/BILLS/2024-04-05/).
    assert 119 in congresses
    assert congresses <= {118, 119}
    assert len(doc_types) >= 5, doc_types

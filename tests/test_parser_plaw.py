"""PLAW USLM parser tests."""

USLM = b"""<?xml version="1.0"?>
<pLaw xmlns="http://schemas.gpo.gov/xml/uslm" xmlns:dc="http://purl.org/dc/elements/1.1/">
<meta><dc:title>Public Law 119-101: To increase the supply of housing.</dc:title>
<dc:type>Public Law</dc:type><docNumber>101</docNumber>
<citableAs>Public Law 119-101</citableAs><citableAs>140 Stat. 846</citableAs>
<approvedDate>2026-07-11</approvedDate></meta>
<main><longTitle>An Act to increase the supply of housing in America.</longTitle>
<section>Be it enacted by the Senate and House...</section></main></pLaw>"""


def test_uslm_law_record(tmp_path):
    from info_intel.parsers import plaw

    f = tmp_path / "PLAW-119publ101.xml"
    f.write_bytes(USLM)
    recs = list(plaw.parse(f, {"package_id": "PLAW-119publ101", "title": "x"}))
    assert len(recs) == 1
    r = recs[0]
    assert r["doc_type"] == "PUBLIC"
    assert r["title"].startswith("Public Law 119-101")
    assert r["metadata"]["law_number"] == "101"
    assert "140 Stat. 846" in r["metadata"]["citations"]
    assert r["metadata"]["approved_date"] == "2026-07-11"
    assert "Be it enacted" in r["text"]


def test_txt_fallback(tmp_path):
    from info_intel.parsers import plaw

    f = tmp_path / "PLAW-119pvtl1.txt"
    f.write_bytes(b"An Act for the relief of a private party.")
    recs = list(plaw.parse(f, {"package_id": "PLAW-119pvtl1", "title": "Relief Act"}))
    assert recs[0]["doc_type"] == "PRIVATE"
    assert recs[0]["text"].startswith("An Act")

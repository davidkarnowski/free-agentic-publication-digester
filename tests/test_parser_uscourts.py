"""Tests for the USCOURTS parser: synthetic case ZIPs (built in memory with a
real pypdf blank-page PDF) covering per-PDF record yield, granule IDs,
court-category derivation, and mods metadata; plus a smoke pass over the real
raw archive."""

import io
import json
import zipfile
from collections import Counter
from pathlib import Path

import pytest
from pypdf import PdfWriter

from info_intel.parsers import uscourts

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "USCOURTS"

RECORD_KEYS = {
    "granule_id",
    "doc_type",
    "title",
    "agency",
    "metadata",
    "text",
    "graphics_substantive",
    "graphics_boilerplate",
}

# Mirrors the real mods.xml layout: MODS namespace, case-level <extension>
# with court/case fields, and one <relatedItem type="constituent"> per
# opinion carrying its own dateIssued and free-text docketText (which is the
# only place a precedential designation ever appears).
MODS_TEMPLATE = """<?xml version="1.0"?>
<mods xmlns="http://www.loc.gov/mods/v3" version="3.3">
  <titleInfo>
    <title>{title}</title>
    <partNumber>{case_number}</partNumber>
  </titleInfo>
  <extension>
    <docClass>USCOURTS</docClass>
    <accessId>{package_id}</accessId>
    {court_type}
    <courtCode>{court_code}</courtCode>
    <caseNumber>{case_number}</caseNumber>
    <caseType>civil</caseType>
  </extension>
  {constituents}
</mods>
"""

CONSTITUENT_TEMPLATE = """
  <relatedItem type="constituent" ID="id-{access_id}">
    <titleInfo><title>{title}</title><partNumber>{seq}</partNumber></titleInfo>
    <originInfo><dateIssued>{date}</dateIssued></originInfo>
    <extension>
      <courtName>{court_name}</courtName>
      <accessId>{access_id}</accessId>
      <sequenceNumber>{seq}</sequenceNumber>
      <dateIssued>{date}</dateIssued>
      <docketText>{docket_text}</docketText>
    </extension>
  </relatedItem>
"""


def blank_pdf_bytes() -> bytes:
    """A tiny real PDF; text extraction of a blank page yields "" (low-text path)."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def build_mods(package_id, court_code, opinions, court_type="District", title="Doe v. Roe"):
    case_number = "2:26-cv-00001"
    constituents = "".join(
        CONSTITUENT_TEMPLATE.format(
            access_id=f"{package_id}-{i}",
            title=title,
            seq=i,
            date=op["date"],
            court_name="United States Test Court",
            docket_text=op["docket_text"],
        )
        for i, op in enumerate(opinions)
    )
    court_type_el = f"<courtType>{court_type}</courtType>" if court_type else ""
    return MODS_TEMPLATE.format(
        title=title,
        case_number=case_number,
        package_id=package_id,
        court_type=court_type_el,
        court_code=court_code,
        constituents=constituents,
    )


def build_zip(tmp_path, package_id, mods_xml, n_pdfs):
    path = tmp_path / f"{package_id}.zip"
    pdf = blank_pdf_bytes()
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(f"{package_id}/dip.xml", "<dip/>")
        zf.writestr(f"{package_id}/premis.xml", "<premis/>")
        if mods_xml is not None:
            zf.writestr(f"{package_id}/mods.xml", mods_xml)
        for i in range(n_pdfs):
            zf.writestr(f"{package_id}/pdf/{package_id}-{i}.pdf", pdf)
    return path


def parse_zip(tmp_path, package_id, mods_xml, n_pdfs):
    path = build_zip(tmp_path, package_id, mods_xml, n_pdfs)
    package = {"package_id": package_id, "collection": "USCOURTS", "date_issued": "2026-07-23"}
    return list(uscourts.parse(path, package))


PKG_ID = "USCOURTS-tsd-2_26-cv-00001"
OPINIONS = [
    {"date": "2026-07-20", "docket_text": "OPINION AND ORDER signed by Judge Jane Roe (abc)"},
    {"date": "2026-07-23", "docket_text": "JUDGMENT entered. Nonprecedential Opinion. (abc)"},
]


@pytest.fixture
def records(tmp_path):
    mods = build_mods(PKG_ID, "tsd", OPINIONS)
    return parse_zip(tmp_path, PKG_ID, mods, n_pdfs=2)


def test_one_record_per_pdf_with_exact_keys(records):
    assert len(records) == 2
    for rec in records:
        assert set(rec) == RECORD_KEYS
        assert rec["agency"] is None
        assert rec["graphics_substantive"] == 0
        assert rec["graphics_boilerplate"] == 0
        json.dumps(rec["metadata"])


def test_granule_id_is_pdf_stem_in_sequence_order(records):
    assert [r["granule_id"] for r in records] == [f"{PKG_ID}-0", f"{PKG_ID}-1"]


def test_title_and_metadata_from_mods(records):
    first, second = records
    for rec in records:
        assert rec["title"] == "Doe v. Roe"
        assert rec["doc_type"] == "DISTRICT"  # from mods <courtType>District</courtType>
        assert rec["metadata"]["court_code"] == "tsd"
        assert rec["metadata"]["court_name"] == "United States Test Court"
        assert rec["metadata"]["case_number"] == "2:26-cv-00001"
        assert rec["metadata"]["case_type"] == "civil"
    # date_filed is per-opinion, not the package date.
    assert first["metadata"]["date_filed"] == "2026-07-20"
    assert second["metadata"]["date_filed"] == "2026-07-23"
    assert first["metadata"]["docket_text"].startswith("OPINION AND ORDER")
    # Precedential designation exists only as docketText free text.
    assert "precedential" not in first["metadata"]
    assert second["metadata"]["precedential"] is False


def test_blank_page_pdf_yields_empty_text_without_error(records):
    for rec in records:
        assert rec["text"] == ""
        assert "extraction_note" not in rec["metadata"]


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("ca9", "APPELLATE"),
        ("alnd", "DISTRICT"),
        ("idb", "BANKRUPTCY"),
        ("cit", "NATIONAL"),
        ("ca13", "APPELLATE"),  # Federal Circuit's real-archive code
        ("caDC", "APPELLATE"),  # mixed case, as in the real archive
    ],
)
def test_court_category_fallback_from_package_id(tmp_path, code, expected):
    package_id = f"USCOURTS-{code}-26-00001"
    # mods without courtType (and without courtCode) forces the package_id path.
    mods = build_mods(package_id, "", [OPINIONS[0]], court_type=None)
    mods = mods.replace("<courtCode></courtCode>", "")
    records = parse_zip(tmp_path, package_id, mods, n_pdfs=1)
    assert len(records) == 1
    assert records[0]["doc_type"] == expected


def test_mods_court_type_wins_over_code(tmp_path):
    package_id = "USCOURTS-tsd-26-00002"
    mods = build_mods(package_id, "tsd", [OPINIONS[0]], court_type="Appellate")
    records = parse_zip(tmp_path, package_id, mods, n_pdfs=1)
    assert records[0]["doc_type"] == "APPELLATE"


def test_precedential_positive_designation(tmp_path):
    package_id = "USCOURTS-ca13-26-00003"
    opinions = [{"date": "2026-07-23", "docket_text": "PRECEDENTIAL OPINION Coram: ROE (xyz)"}]
    mods = build_mods(package_id, "ca13", opinions, court_type="Appellate")
    records = parse_zip(tmp_path, package_id, mods, n_pdfs=1)
    assert records[0]["metadata"]["precedential"] is True


def test_missing_mods_degrades_without_aborting(tmp_path):
    package_id = "USCOURTS-alnd-26-00004"
    records = parse_zip(tmp_path, package_id, None, n_pdfs=1)
    assert len(records) == 1
    rec = records[0]
    assert rec["granule_id"] == f"{package_id}-0"
    assert rec["doc_type"] == "DISTRICT"  # package_id fallback
    assert rec["title"] is None
    assert "mods.xml missing" in rec["metadata"]["extraction_note"]


def test_corrupt_pdf_member_yields_noted_record(tmp_path):
    package_id = "USCOURTS-tsd-26-00005"
    path = tmp_path / f"{package_id}.zip"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(f"{package_id}/mods.xml", build_mods(package_id, "tsd", [OPINIONS[0]]))
        zf.writestr(f"{package_id}/pdf/{package_id}-0.pdf", b"not a pdf at all")
    package = {"package_id": package_id, "collection": "USCOURTS", "date_issued": "2026-07-23"}
    records = list(uscourts.parse(path, package))
    assert len(records) == 1
    assert records[0]["text"] == ""
    assert "unreadable pdf" in records[0]["metadata"]["extraction_note"]


# --- Smoke tests against the real archive -----------------------------------

REAL_ZIPS = sorted(DATA_DIR.glob("*/USCOURTS-*.zip"))[:30] if DATA_DIR.is_dir() else []


@pytest.mark.skipif(len(REAL_ZIPS) < 25, reason="no raw USCOURTS archive on disk")
def test_real_archive_smoke():
    all_records = []
    for path in REAL_ZIPS:
        package_id = path.stem
        package = {
            "package_id": package_id,
            "collection": "USCOURTS",
            "date_issued": path.parent.name,
        }
        records = list(uscourts.parse(path, package))
        assert records, f"{package_id}: no records"
        for rec in records:
            assert set(rec) == RECORD_KEYS
            assert rec["granule_id"].startswith(package_id)
            assert rec["doc_type"] in {"APPELLATE", "DISTRICT", "BANKRUPTCY", "NATIONAL"}
            assert rec["title"]
            assert rec["metadata"].get("case_number")
            assert rec["metadata"].get("date_filed")
        all_records.extend(records)
    # Opinions are text-based PDFs; scanned outliers are tolerated but rare.
    with_text = sum(1 for r in all_records if len(r["text"]) >= 100)
    assert with_text / len(all_records) >= 0.90
    # Doc-type distribution: this slice of the archive spans court categories.
    counts = Counter(r["doc_type"] for r in all_records)
    assert counts["APPELLATE"] > 0
    assert counts["DISTRICT"] > 0

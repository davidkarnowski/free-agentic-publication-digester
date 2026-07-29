"""Tests for fapd.graphics: FR <GPH> inventory and image asset extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from fapd.graphics import extract_assets, inventory

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "FR"

requires_data = pytest.mark.skipif(
    not DATA_DIR.is_dir(), reason="real FR data not present under data/raw/FR"
)

# Mirrors the real structure: GPH with/without nested PRTPAGE, PRTPAGE as
# sibling or inside unrelated elements, substantive and boilerplate GIDs.
SYNTHETIC_XML = b"""<?xml version="1.0"?>
<FEDREG>
  <VOL>91</VOL>
  <SECTION>
    <GPH DEEP="30" SPAN="2">
      <GID>EN23JY26.004</GID>
    </GPH>
    <PRTPAGE P="100"/>
    <GPH DEEP="15">
      <GID>Trump.EPS</GID>
    </GPH>
    <P>some text<PRTPAGE P="101"/></P>
    <GPH DEEP="379">
      <PRTPAGE P="205"/>
      <GID>ER12AB25.123</GID>
    </GPH>
    <GPH>
      <GID>EN23JY26</GID>
    </GPH>
  </SECTION>
</FEDREG>
"""


# ---------------------------------------------------------------------------
# inventory(): synthetic XML
# ---------------------------------------------------------------------------


def test_inventory_document_order():
    gids = [item["gid"] for item in inventory(SYNTHETIC_XML)]
    assert gids == ["EN23JY26.004", "Trump.EPS", "ER12AB25.123", "EN23JY26"]


def test_inventory_classification_fr_gph_01():
    by_gid = {item["gid"]: item["classification"] for item in inventory(SYNTHETIC_XML)}
    assert by_gid["EN23JY26.004"] == "substantive"
    assert by_gid["ER12AB25.123"] == "substantive"
    # Signature/seal-style GID: boilerplate.
    assert by_gid["Trump.EPS"] == "boilerplate"
    # Near miss (no .NNN suffix): the pattern must not loosely match.
    assert by_gid["EN23JY26"] == "boilerplate"


def test_inventory_page_from_nested_prtpage():
    items = inventory(SYNTHETIC_XML)
    assert items[2]["gid"] == "ER12AB25.123"
    assert items[2]["page"] == "205"  # nested PRTPAGE wins over preceding "101"


def test_inventory_page_from_preceding_prtpage():
    items = inventory(SYNTHETIC_XML)
    assert items[1]["page"] == "100"  # most recent preceding sibling
    assert items[3]["page"] == "205"  # nested PRTPAGE of the prior GPH still counts


def test_inventory_page_none_before_any_prtpage():
    assert inventory(SYNTHETIC_XML)[0]["page"] is None


def test_inventory_deep_attribute():
    deeps = [item["deep"] for item in inventory(SYNTHETIC_XML)]
    assert deeps == [30, 15, 379, None]


def test_inventory_no_graphics():
    assert inventory(b"<FEDREG><VOL>91</VOL></FEDREG>") == []


# ---------------------------------------------------------------------------
# extract_assets(): behavior that needs no PDF
# ---------------------------------------------------------------------------


def test_extract_assets_all_skipped_without_touching_pdf(tmp_path):
    items = [
        {"gid": "Trump.EPS", "classification": "boilerplate", "page": "100", "deep": 5},
    ]
    results = extract_assets(tmp_path / "does-not-exist.pdf", items, tmp_path / "out")
    assert results == [
        {"gid": "Trump.EPS", "page": "100", "asset_path": None, "status": "skipped"}
    ]
    assert (tmp_path / "out").is_dir()


def test_extract_assets_substantive_without_page_fails_gracefully(tmp_path):
    items = [{"gid": "EN23JY26.004", "classification": "substantive", "page": None, "deep": 1}]
    (result,) = extract_assets(tmp_path / "missing.pdf", items, tmp_path / "out")
    assert result["status"] == "failed"
    assert result["asset_path"] is None
    assert "note" in result


def test_extract_assets_unreadable_pdf_fails_per_item(tmp_path):
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_bytes(b"not a pdf")
    items = [{"gid": "EN23JY26.004", "classification": "substantive", "page": "100", "deep": 1}]
    (result,) = extract_assets(bad_pdf, items, tmp_path / "out")
    assert result["status"] == "failed"
    assert "note" in result


# ---------------------------------------------------------------------------
# Real data
# ---------------------------------------------------------------------------


def _issues_with_pdf() -> list[tuple[Path, Path]]:
    pairs = []
    for issue_dir in sorted(DATA_DIR.iterdir()):
        xml = next(issue_dir.glob("FR-*.xml"), None)
        pdf = next(issue_dir.glob("FR-*.pdf"), None)
        if xml and pdf:
            pairs.append((xml, pdf))
    return pairs


@requires_data
def test_inventory_real_issue_2026_07_23():
    xml = DATA_DIR / "2026-07-23" / "FR-2026-07-23.xml"
    if not xml.exists():
        pytest.skip("FR-2026-07-23.xml not present")
    items = inventory(xml.read_bytes())
    assert len(items) == 54
    substantive = [item for item in items if item["classification"] == "substantive"]
    boilerplate = [item for item in items if item["classification"] == "boilerplate"]
    assert len(substantive) == 46
    assert len(boilerplate) == 8
    assert all(item["gid"] == "Trump.EPS" for item in boilerplate)
    # Every substantive graphic in this issue resolves to a printed page.
    assert all(item["page"] for item in substantive)


@requires_data
def test_extract_assets_smoke_smallest_issue(tmp_path):
    candidates = [
        (xml, pdf)
        for xml, pdf in _issues_with_pdf()
        if any(i["classification"] == "substantive" for i in inventory(xml.read_bytes()))
    ]
    if not candidates:
        pytest.skip("no graphics-bearing issue with a companion PDF")
    xml, pdf = min(candidates, key=lambda pair: pair[1].stat().st_size)

    items = inventory(xml.read_bytes())
    # Ensure the boilerplate path is exercised even if this issue has none.
    items.append({"gid": "Trump.EPS", "classification": "boilerplate", "page": "1", "deep": 3})

    results = extract_assets(pdf, items, tmp_path / "assets")

    assert len(results) == len(items)
    assert {r["status"] for r in results} <= {"extracted", "failed", "skipped"}

    extracted = [r for r in results if r["status"] == "extracted"]
    assert extracted, f"no graphic extracted from {pdf.name}"
    for r in extracted:
        path = Path(r["asset_path"])
        assert path.is_file()
        assert path.stat().st_size > 0
        assert path.stem == r["gid"]

    boilerplate_results = [r for r in results if r["gid"] == "Trump.EPS"]
    assert boilerplate_results
    assert all(r["status"] == "skipped" for r in boilerplate_results)
    assert all(r["asset_path"] is None for r in boilerplate_results)

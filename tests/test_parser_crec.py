"""CREC parser tests: synthetic in-memory ZIPs for the parsing contract,
plus a real-archive smoke test (skipped when data/raw/CREC is absent)."""

import io
import zipfile
from pathlib import Path

import pytest

from info_intel.parsers import crec

PKG = {
    "package_id": "CREC-2026-07-23",
    "collection": "CREC",
    "date_issued": "2026-07-23",
}

BOILERPLATE_TITLE = "Congressional Record, Volume 172 Issue 121 (Thursday, July 23, 2026)"

GPO_LINE = (
    "From the Congressional Record Online through the Government Publishing "
    'Office [<a href="https://www.gpo.gov">www.gpo.gov</a>]'
)


def granule_html(body: str, title: str | None = BOILERPLATE_TITLE, header: bool = True) -> str:
    title_tag = f"<title>{title}</title>\n" if title is not None else ""
    header_block = (
        "[Congressional Record Volume 172, Number 121 (Thursday, July 23, 2026)]\n"
        "[Senate]\n"
        "[Pages S4241-S4242]\n"
        f"{GPO_LINE}\n\n\n"
        if header
        else ""
    )
    return (
        f"<html>\n<head>\n{title_tag}</head>\n"
        f"<body><pre>\n{header_block}{body}\n</pre></body>\n</html>"
    )


def make_zip(members: dict[str, str]) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    buf.seek(0)
    return buf


def parse_all(members: dict[str, str]) -> list[dict]:
    return list(crec.parse(make_zip(members), PKG))


def test_non_granule_members_are_skipped():
    records = parse_all(
        {
            "CREC-2026-07-23/dip.xml": "<dip/>",
            "CREC-2026-07-23/mods.xml": "<mods/>",
            "CREC-2026-07-23/premis.xml": "<premis/>",
            "CREC-2026-07-23/pdf/CREC-2026-07-23-pt1-PgS4241.pdf": "%PDF-fake",
            "CREC-2026-07-23/html/CREC-2026-07-23.htm": granule_html("whole issue"),
            "CREC-2026-07-23/html/CREC-2026-07-23-senate.htm": granule_html("section file"),
            "CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgS4241.htm": granule_html("real one"),
            "CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgS4241-2.htm": granule_html("real two"),
        }
    )
    assert [r["granule_id"] for r in records] == [
        "CREC-2026-07-23-pt1-PgS4241",
        "CREC-2026-07-23-pt1-PgS4241-2",
    ]


@pytest.mark.parametrize(
    ("stem", "doc_type"),
    [
        ("CREC-2026-07-23-pt1-PgS4101", "SENATE"),
        ("CREC-2026-07-23-pt1-PgH5181", "HOUSE"),
        ("CREC-2026-07-23-pt1-PgE733", "EXTENSIONS"),
        ("CREC-2026-07-23-pt1-PgD774", "DAILYDIGEST"),
        ("CREC-2026-07-23-pt1-PgQ999", None),
    ],
)
def test_doc_type_from_page_prefix(stem, doc_type):
    [record] = parse_all({f"CREC-2026-07-23/html/{stem}.htm": granule_html("x")})
    assert record["doc_type"] == doc_type


def test_record_shape_and_metadata():
    [record] = parse_all(
        {"CREC-2026-07-23/html/CREC-2026-07-23-pt2-PgS4101-7.htm": granule_html("x")}
    )
    assert set(record) == {
        "granule_id",
        "doc_type",
        "title",
        "agency",
        "metadata",
        "text",
        "graphics_substantive",
        "graphics_boilerplate",
    }
    assert record["metadata"] == {"page": "S4101", "part": 2, "sequence": 7}
    assert record["agency"] is None
    assert record["graphics_substantive"] == 0
    assert record["graphics_boilerplate"] == 0


def test_metadata_without_sequence():
    [record] = parse_all(
        {"CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgD774.htm": granule_html("x")}
    )
    assert record["metadata"] == {"page": "D774", "part": 1}


def test_html_stripping_preserves_lines_and_drops_boilerplate():
    body = (
        "        A CENTERED HEADING\n"
        "\n"
        "\n"
        "\n"
        "  Mr. SMITH. Mr. President, AT&amp;T is <b>bold</b> text.\n"
        "\n"
        "[[Page S4242]]\n"
        "\n"
        "  Second paragraph line.\n"
    )
    [record] = parse_all(
        {"CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgS4241.htm": granule_html(body)}
    )
    text = record["text"]
    assert "<" not in text and ">" not in text  # tags gone
    assert "From the Congressional Record Online" not in text  # GPO line gone
    assert "[Congressional Record Volume" not in text  # header block gone
    assert "[Senate]" not in text and "[Pages S4241-S4242]" not in text
    assert "[[Page S4242]]" in text  # mid-text page markers kept
    assert "AT&T" in text  # entities decoded
    assert text.splitlines()[0] == "        A CENTERED HEADING"  # indentation kept
    assert text == (
        "        A CENTERED HEADING\n"
        "\n"
        "  Mr. SMITH. Mr. President, AT&T is bold text.\n"
        "\n"
        "[[Page S4242]]\n"
        "\n"
        "  Second paragraph line."
    )


def test_title_pure_boilerplate_is_none():
    [record] = parse_all(
        {"CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgS4241.htm": granule_html("x")}
    )
    assert record["title"] is None


def test_title_boilerplate_prefix_is_stripped():
    html = granule_html("x", title=f"{BOILERPLATE_TITLE} - TRIBUTE TO A CONSTITUENT")
    [record] = parse_all({"CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgE733.htm": html})
    assert record["title"] == "TRIBUTE TO A CONSTITUENT"


def test_title_without_boilerplate_kept_and_missing_title_none():
    records = parse_all(
        {
            "CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgH5181.htm": granule_html(
                "x", title="MORNING-HOUR DEBATE"
            ),
            "CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgH5182.htm": granule_html(
                "x", title=None
            ),
        }
    )
    by_id = {r["granule_id"]: r for r in records}
    assert by_id["CREC-2026-07-23-pt1-PgH5181"]["title"] == "MORNING-HOUR DEBATE"
    assert by_id["CREC-2026-07-23-pt1-PgH5182"]["title"] is None


def test_frontmatter_pseudo_page():
    [record] = parse_all(
        {
            "CREC-2026-07-23/html/CREC-2026-07-23-pt1-PgS-FrontMatter-2.htm": granule_html(
                "S E N A T E"
            )
        }
    )
    assert record["granule_id"] == "CREC-2026-07-23-pt1-PgS-FrontMatter-2"
    assert record["doc_type"] == "SENATE"
    assert record["metadata"]["page"] == "S-FrontMatter"
    assert record["metadata"]["sequence"] == 2


# --- Real-archive smoke test -------------------------------------------------

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "CREC"
REAL_ZIPS = sorted(DATA_DIR.glob("*/CREC-*.zip")) if DATA_DIR.is_dir() else []


@pytest.mark.skipif(not REAL_ZIPS, reason="no real CREC archive under data/raw/CREC")
def test_real_day_smoke():
    zip_path = REAL_ZIPS[-1]
    package_id = zip_path.stem  # e.g. CREC-2026-07-23
    package = {
        "package_id": package_id,
        "collection": "CREC",
        "date_issued": package_id.removeprefix("CREC-"),
    }
    records = list(crec.parse(zip_path, package))

    assert len(records) > 50  # light session days (e.g. Monday pro forma) run ~120
    assert all(r["text"] for r in records), "every granule must yield non-empty text"
    assert all(r["granule_id"].startswith(package_id) for r in records)
    typed = sum(1 for r in records if r["doc_type"] is not None)
    assert typed / len(records) > 0.90

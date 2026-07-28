"""Parser for PLAW (Public and Private Laws) USLM XML packages.

One record per package: an enacted law. USLM (uslm-2.x) carries the
citation, approval date, and official title in its meta block; the body
text is extracted verbatim (GUIDE §2)."""

import xml.etree.ElementTree as ET

_USLM = "{http://schemas.gpo.gov/xml/uslm}"
_DC = "{http://purl.org/dc/elements/1.1/}"


def _all_text(elem):
    return " ".join(" ".join(elem.itertext()).split())


def parse(raw_path, package):
    body = raw_path.read_bytes()
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        # txt fallback (rare: pre-USLM or txtLink download)
        text = " ".join(body.decode("utf-8", errors="replace").split())
        yield {
            "granule_id": "",
            "doc_type": "PUBLIC" if "publ" in package["package_id"] else "PRIVATE",
            "title": package.get("title"),
            "agency": None,
            "metadata": {"format": "txt"},
            "text": text,
            "graphics_substantive": 0,
            "graphics_boilerplate": 0,
        }
        return

    meta = root.find(f"{_USLM}meta")
    title = citations = approved = doc_number = law_type = None
    if meta is not None:
        title = (meta.findtext(f"{_DC}title") or "").strip() or None
        law_type = (meta.findtext(f"{_DC}type") or "").strip() or None
        doc_number = (meta.findtext(f"{_USLM}docNumber") or "").strip() or None
        approved = (meta.findtext(f"{_USLM}approvedDate") or "").strip() or None
        citations = [
            (c.text or "").strip()
            for c in meta.findall(f"{_USLM}citableAs") if (c.text or "").strip()
        ]

    yield {
        "granule_id": "",
        "doc_type": ("PRIVATE" if (law_type or "").lower().startswith("private")
                     or "pvtl" in package["package_id"] else "PUBLIC"),
        "title": title or package.get("title"),
        "agency": None,
        "metadata": {
            "law_number": doc_number,
            "citations": citations or [],
            "approved_date": approved,
            "law_type": law_type,
        },
        "text": _all_text(root),
        "graphics_substantive": 0,
        "graphics_boilerplate": 0,
    }

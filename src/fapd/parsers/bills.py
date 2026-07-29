"""Parser for BILLS (Congressional Bills) packages — GUIDE §5 stage 2 (EXTRACT).

Each BILLS package is a single bill-text XML document (root element varies:
``<bill>``, ``<resolution>``, ``<amendment-doc>``, ...) carrying a dublinCore
metadata block and the full legislative text. Bills are whole-package
documents, so :func:`parse` yields exactly one record with ``granule_id: ""``.

Extraction is verbatim: element text is concatenated and whitespace-normalized,
never summarized. Bills are pure text (measured across our archive), so both
graphics counters are 0.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path

_DC_TITLE = ".//dublinCore/{http://purl.org/dc/elements/1.1/}title"

# Bill types, longest first: a regex alternation tries branches in order, so
# "hr" before "hres" would truncate "hres1449ih" into type "hr" + number-less
# garbage. Sorting by length descending makes the longest candidate win.
_BILL_TYPES = sorted(
    ("hr", "s", "hres", "sres", "hjres", "sjres", "hconres", "sconres"),
    key=len,
    reverse=True,
)

# BILLS-{congress}{type}{number}{version}, e.g. BILLS-119hjres105ih.
_PACKAGE_ID_RE = re.compile(
    r"^BILLS-(?P<congress>\d+)(?P<bill_type>" + "|".join(_BILL_TYPES) + r")"
    r"(?P<number>\d+)(?P<version>[a-z]+)$"
)

# Subtrees whose text is publication boilerplate, not bill text.
_SKIP_TEXT_TAGS = {"metadata", "dublinCore"}


def parse_package_id(package_id: str) -> dict | None:
    """Split a BILLS package id into its components.

    Returns ``{"congress": int, "bill_type": str, "bill_number": int,
    "version": str}``, or None if the id does not match the BILLS pattern.
    """
    m = _PACKAGE_ID_RE.match(package_id or "")
    if m is None:
        return None
    return {
        "congress": int(m.group("congress")),
        "bill_type": m.group("bill_type"),
        "bill_number": int(m.group("number")),
        "version": m.group("version"),
    }


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _collect_text(elem: ET.Element, parts: list[str]) -> None:
    """Depth-first text collection, skipping the metadata/dublinCore subtree."""
    if elem.tag in _SKIP_TEXT_TAGS:
        return
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        _collect_text(child, parts)
        if child.tail:
            parts.append(child.tail)


def _element_text(elem: ET.Element | None) -> str | None:
    if elem is None:
        return None
    text = _normalize("".join(elem.itertext()))
    return text or None


def parse(raw_path: Path, package: dict) -> Iterator[dict]:
    """Yield exactly one normalized record for a bill-text XML file.

    ``package`` is the stored package row: a dict with at least
    ``package_id``, ``collection``, and ``date_issued``.
    """
    root = ET.parse(raw_path).getroot()

    ids = parse_package_id(package.get("package_id", "")) or parse_package_id(raw_path.stem)

    # Stage attribute name tracks the root element (bill-stage,
    # resolution-stage, amend-stage, ...) — match the suffix, not the tag.
    stage = next((v for k, v in root.attrib.items() if k.endswith("-stage")), None)

    # doc_type: the human-readable stage when present, else the version code
    # from the package id (e.g. BILLS-119hr8888enr -> "enr").
    doc_type = stage or (ids["version"] if ids else None)

    title = _element_text(root.find(_DC_TITLE)) or _element_text(root.find(".//official-title"))

    sponsors: list[str] = []
    for elem in root.iter():
        if elem.tag in ("sponsor", "cosponsor"):
            name = _element_text(elem)
            if name and name not in sponsors:
                sponsors.append(name)

    bill_type = ids["bill_type"] if ids else None
    chamber = None
    if bill_type:
        chamber = "House" if bill_type.startswith("h") else "Senate"

    metadata = {
        "congress": ids["congress"] if ids else None,
        "bill_type": bill_type,
        "bill_number": ids["bill_number"] if ids else None,
        "bill_version": ids["version"] if ids else None,
        "chamber": chamber,
        "stage": stage,
        "legis_num": _element_text(root.find(".//legis-num")),
        "sponsors": sponsors,
    }

    parts: list[str] = []
    _collect_text(root, parts)

    yield {
        "granule_id": "",
        "doc_type": doc_type,
        "title": title,
        "agency": None,
        "metadata": metadata,
        "text": _normalize(" ".join(parts)),
        "graphics_substantive": 0,
        "graphics_boilerplate": 0,
    }

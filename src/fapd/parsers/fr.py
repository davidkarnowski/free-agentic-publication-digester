"""Parser for FR (Federal Register) daily-issue packages — GUIDE §5 stage 2.

An FR issue is one XML file with root ``<FEDREG>`` containing the day's
documents grouped in section elements. :func:`parse` yields one record per
document element: ``<RULE>``, ``<PRORULE>``, ``<NOTICE>``, ``<PRESDOCU>``.

Structure quirks observed in the real archive (data/raw/FR/*/FR-*.xml):

- Sections are not strictly top-level. Besides ``<RULES>``, ``<PRORULES>``,
  ``<NOTICES>``, the root contains ``<NEWPART>`` wrappers whose children are
  *nested* ``<PRORULES>``/``<PRESDOCS>`` sections, and presidential documents
  arrive as top-level ``<PRESDOC>`` wrappers each holding one ``<PRESDOCU>``.
  We therefore walk the whole tree for document tags instead of trusting the
  top-level layout. (Verified: per file, document count == ``<FRDOC>`` count,
  so no document tag appears in the table of contents or anywhere else.)
- ``<FRDOC>`` normally reads ``[FR Doc. 2026-14825 Filed 7-22-26; 8:45 am]``,
  but in PRESDOCU the closing half lives in a sibling ``<FILED>`` element, so
  the text is just ``[FR Doc. 2026-14990`` — the doc number is extracted by
  regex, not by stripping a fixed wrapper.
- RULE/PRORULE/NOTICE carry a ``<PREAMB>`` with ``<AGENCY>`` (all-caps
  heading), ``<SUBJECT>`` (the document title), and labeled sections
  (``<AGY>``, ``<ACT>``, ``<SUM>``, ``<DATES>`` or ``<EFFDATE>``) whose first
  child is an ``<HD>`` label ("AGENCY:", "SUMMARY:", ...) we strip.
  ``<DATES>`` and ``<EFFDATE>`` are alternatives; no real document has both.
- PRESDOCU has no PREAMB. Its body is a ``<PROCLA>``, ``<EXECORD>``, or
  ``<PRNOTICE>`` container; the document title is the first ``<HD>`` and
  there is no ``<AGENCY>``/``<AGY>`` heading (agency is None).
- A handful of documents carry more than one ``<CFR>``; texts are joined.
- Extraction is verbatim (GUIDE §2): element text is concatenated and
  whitespace-normalized, never summarized. ``<GID>`` graphic filenames are
  excluded from ``text`` (they are inventory, not prose).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path

# Document container tags; the tag itself is the record's doc_type.
_DOC_TAGS = ("RULE", "PRORULE", "NOTICE", "PRESDOCU")

# Doc number inside <FRDOC>, e.g. "[FR Doc. 2026-14825 Filed ...]" or the
# PRESDOCU truncated form "[FR Doc. 2026-14990".
_FRDOC_RE = re.compile(r"FR\s+Doc\.?\s+([^\s\]]+)")

# Rule FR-GPH-01 (GUIDE §6): section-coded GIDs (e.g. EN23JY26.004) are
# substantive content graphics; anything else (Trump.EPS signatures, seals)
# is boilerplate. Same pattern as sync.classify_graphics, kept local so the
# parser stays standalone.
_SUBSTANTIVE_GID_RE = re.compile(r"^E[A-Z]\d{2}[A-Z]{2}\d{2}\.\d+$")

_BILLING_LABEL_RE = re.compile(r"^billing\s+code:?\s*", re.IGNORECASE)


def _normalize(text: str) -> str | None:
    joined = " ".join(text.split())
    return joined or None


def _collect_text(elem: ET.Element, parts: list[str]) -> None:
    """Append elem's text content to parts, skipping <GID> filenames.

    A skipped element's tail still belongs to the surrounding flow; tails are
    appended by the parent loop, so only the filename itself is dropped.
    """
    if elem.tag == "GID":
        return
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        _collect_text(child, parts)
        if child.tail:
            parts.append(child.tail)


def _text_of(elem: ET.Element | None) -> str | None:
    if elem is None:
        return None
    parts: list[str] = []
    _collect_text(elem, parts)
    return _normalize(" ".join(parts))


def _labeled_text(elem: ET.Element | None) -> str | None:
    """Text of a labeled preamble section minus its <HD> label line."""
    if elem is None:
        return None
    parts: list[str] = [elem.text or ""]
    for child in elem:
        if child.tag != "HD":
            _collect_text(child, parts)
        if child.tail:
            parts.append(child.tail)
    return _normalize(" ".join(parts))


def _granule_id(doc: ET.Element) -> str | None:
    frdoc = _text_of(next(doc.iter("FRDOC"), None))
    if not frdoc:
        return None
    m = _FRDOC_RE.search(frdoc)
    if m is None:
        return None
    return m.group(1).rstrip("].,;")


def _metadata(doc: ET.Element, preamb: ET.Element | None) -> dict:
    """Cheaply available metadata; keys present only when the source has them."""
    md: dict = {}
    if preamb is not None:
        cfrs = [t for t in (_text_of(e) for e in preamb.findall("CFR")) if t]
        if cfrs:
            md["cfr"] = "; ".join(cfrs)
        action = _labeled_text(preamb.find("ACT"))
        if action:
            md["action"] = action
        # <DATES> and <EFFDATE> are alternative spellings of the same
        # "DATES:" preamble section (both observed in the archive).
        dates_el = preamb.find("DATES")
        if dates_el is None:
            dates_el = preamb.find("EFFDATE")
        dates = _labeled_text(dates_el)
        if dates:
            md["dates"] = dates
        summary = _labeled_text(preamb.find("SUM"))
        if summary:
            md["summary"] = summary
    bilcod = _text_of(next(doc.iter("BILCOD"), None))
    if bilcod:
        md["billing_code"] = _BILLING_LABEL_RE.sub("", bilcod)
    pages = [p.attrib["P"] for p in doc.iter("PRTPAGE") if p.attrib.get("P")]
    if pages:
        md["pages"] = {"first": pages[0], "last": pages[-1]}
    return md


def _graphics_counts(doc: ET.Element) -> tuple[int, int]:
    substantive = boilerplate = 0
    for gph in doc.iter("GPH"):
        for gid in gph.iter("GID"):
            # _collect_text skips GID by design; read the filename directly.
            name = " ".join("".join(gid.itertext()).split())
            if _SUBSTANTIVE_GID_RE.match(name):
                substantive += 1
            else:
                boilerplate += 1
    return substantive, boilerplate


def _parse_doc(doc: ET.Element) -> dict | None:
    granule_id = _granule_id(doc)
    if granule_id is None:
        # Never observed in the real archive (every document has exactly one
        # FRDOC); a document we cannot cite is skipped rather than guessed.
        return None
    preamb = doc.find("PREAMB")
    if doc.tag == "PRESDOCU":
        title = _text_of(next(doc.iter("HD"), None))
        agency = None
    else:
        title = _text_of(preamb.find("SUBJECT")) if preamb is not None else None
        agency = None
        if preamb is not None:
            agency = _text_of(preamb.find("AGENCY")) or _labeled_text(preamb.find("AGY"))
    substantive, boilerplate = _graphics_counts(doc)
    return {
        "granule_id": granule_id,
        "doc_type": doc.tag,
        "title": title,
        "agency": agency,
        "metadata": _metadata(doc, preamb),
        "text": _text_of(doc) or "",
        "graphics_substantive": substantive,
        "graphics_boilerplate": boilerplate,
    }


def parse(raw_path: Path, package: dict) -> Iterator[dict]:
    """Yield one record per FR document in the issue XML at ``raw_path``.

    ``package`` (package_id, collection, date_issued) is accepted for the
    common parser interface; every field here comes from the document itself.
    """
    del package  # issue-level context is carried by the caller, not the record
    root = ET.parse(raw_path).getroot()
    for elem in root.iter():
        if elem.tag in _DOC_TAGS:
            record = _parse_doc(elem)
            if record is not None:
                yield record

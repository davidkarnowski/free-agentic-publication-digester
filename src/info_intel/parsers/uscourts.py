"""Parser for USCOURTS case packages — GUIDE §5 stage 2, Phase J1.

A USCOURTS package is one *case* delivered as a ZIP containing
``<packageId>/mods.xml`` plus one PDF per opinion/order under
``<packageId>/pdf/<packageId>-N.pdf`` (``dip.xml`` and ``premis.xml`` are
delivery bookkeeping and are ignored). :func:`parse` yields one record per
opinion PDF; the record's ``granule_id`` is the PDF stem, which equals the
govinfo granule ID used for citation links.

Structure observed in the real archive (data/raw/USCOURTS/*/*.zip, 353
packages / 1,264 opinion granules inspected):

- Case-level metadata lives in root ``<extension>`` blocks (duplicated
  verbatim twice per file): ``courtType`` (``Appellate`` | ``District`` |
  ``Bankruptcy``), ``courtCode``, ``courtCircuit``, ``caseNumber``,
  ``caseType``, parties. The case name is the root ``<titleInfo><title>``.
- Per-opinion metadata lives in ``<relatedItem type="constituent">`` blocks,
  one per PDF: ``extension/accessId`` (equals the PDF stem in every real
  package), ``extension/dateIssued`` (the opinion's own filing date — present
  on all 1,264 constituents and distinct per opinion within a case),
  ``extension/docketText`` (free-text docket entry; ``subTitle`` repeats it),
  and ``extension/courtName``.
- Court-code quirks: the Federal Circuit arrives as ``ca13`` (with
  ``courtCircuit=Federal``) and the D.C. Circuit as mixed-case ``caDC`` —
  code matching must be case-insensitive and accept ``ca13``.
- There is **no structured precedential element and no structured judge or
  opinion-type element**. Precedential designations appear only as free text
  inside ``docketText`` ("PRECEDENTIAL OPINION", "Nonprecedential Opinion",
  "NOT PRECEDENTIAL PER CURIAM OPINION"); we surface that designation as a
  boolean only when the text carries one — a mechanical pattern, GUIDE §2.
  Judges appear only inside docket prose and are not extracted.
- Extraction is verbatim (GUIDE §2): PDF page texts are concatenated with
  newlines and whitespace-normalized per line, never summarized. A scanned
  or corrupt PDF never aborts the package: the record is still yielded with
  whatever text there is, plus an ``extraction_note`` in ``metadata``.
"""

from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Iterator
from pathlib import Path

from pypdf import PdfReader

_NS = {"m": "http://www.loc.gov/mods/v3"}

# Fallback court-category derivation from the court code embedded in the
# package_id (USCOURTS-<code>-<docket>). Appellate codes: ca1..ca11 plus the
# quirks ca13 (Federal Circuit) and caDC (matched case-insensitively).
_APPELLATE_CODE_RE = re.compile(r"ca(\d{1,2}|dc|fc)")
_NATIONAL_CODES = {"cit", "uscfc", "cofc", "jpml"}
_COURT_TYPE_MAP = {
    "appellate": "APPELLATE",
    "district": "DISTRICT",
    "bankruptcy": "BANKRUPTCY",
    "national": "NATIONAL",
}

# Precedential designation is free text inside docketText; "Nonprecedential",
# "Non-Precedential", and "NOT PRECEDENTIAL" all occur in the real archive.
_NONPRECEDENTIAL_RE = re.compile(r"\bnon-?precedential\b|\bnot\s+precedential\b", re.IGNORECASE)
_PRECEDENTIAL_RE = re.compile(r"\bprecedential\b", re.IGNORECASE)


def _court_code_from_package_id(package_id: str) -> str | None:
    parts = package_id.split("-")
    if len(parts) >= 2 and parts[0] == "USCOURTS" and parts[1]:
        return parts[1]
    return None


def _court_category(court_type: str | None, court_code: str | None) -> str | None:
    """APPELLATE | DISTRICT | BANKRUPTCY | NATIONAL from mods, else from code."""
    if court_type:
        mapped = _COURT_TYPE_MAP.get(court_type.strip().lower())
        if mapped:
            return mapped
    if not court_code:
        return None
    code = court_code.lower()
    if _APPELLATE_CODE_RE.fullmatch(code):
        return "APPELLATE"
    if code in _NATIONAL_CODES:
        return "NATIONAL"
    if code.endswith("b"):
        return "BANKRUPTCY"
    return "DISTRICT"


def _precedential(docket_text: str) -> bool | None:
    if _NONPRECEDENTIAL_RE.search(docket_text):
        return False
    if _PRECEDENTIAL_RE.search(docket_text):
        return True
    return None


def _normalize_pdf_text(raw: str) -> str:
    """Whitespace-normalize each line; keep paragraph (blank-line) structure."""
    lines: list[str] = []
    blank_pending = False
    for line in raw.splitlines():
        norm = " ".join(line.split())
        if norm:
            if blank_pending and lines:
                lines.append("")
            lines.append(norm)
            blank_pending = False
        else:
            blank_pending = True
    return "\n".join(lines)


def _extract_pdf_text(pdf_bytes: bytes) -> tuple[str, str | None]:
    """(normalized text, extraction note). Per-page failures degrade, never raise."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as exc:  # noqa: BLE001 — corrupt member: record-level note, not an abort
        return "", f"unreadable pdf: {type(exc).__name__}: {exc}"
    pages: list[str] = []
    note = None
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception as exc:  # noqa: BLE001 — one bad page must not kill the record
            pages.append("")
            note = f"page extraction failed: {type(exc).__name__}: {exc}"
    return _normalize_pdf_text("\n".join(pages)), note


def _case_level(root: ET.Element) -> dict:
    """Case-wide fields from the root of mods.xml."""
    return {
        "title": root.findtext("m:titleInfo/m:title", namespaces=_NS),
        "court_type": root.findtext("m:extension/m:courtType", namespaces=_NS),
        "court_code": root.findtext("m:extension/m:courtCode", namespaces=_NS),
        "case_number": root.findtext("m:extension/m:caseNumber", namespaces=_NS),
        "case_type": root.findtext("m:extension/m:caseType", namespaces=_NS),
    }


def _constituents(root: ET.Element) -> dict[str, dict]:
    """Per-opinion metadata keyed by accessId (== PDF stem in every real package)."""
    out: dict[str, dict] = {}
    for item in root.findall('m:relatedItem[@type="constituent"]', _NS):
        access_id = item.findtext("m:extension/m:accessId", namespaces=_NS)
        if not access_id:
            continue
        date_filed = item.findtext("m:extension/m:dateIssued", namespaces=_NS) or item.findtext(
            "m:originInfo/m:dateIssued", namespaces=_NS
        )
        out[access_id] = {
            "date_filed": date_filed,
            "docket_text": item.findtext("m:extension/m:docketText", namespaces=_NS),
            "court_name": item.findtext("m:extension/m:courtName", namespaces=_NS),
        }
    return out


def _sequence_key(stem: str) -> tuple[int, str]:
    """Sort PDFs by their numeric granule sequence suffix (…-N)."""
    tail = stem.rsplit("-", 1)[-1]
    return (int(tail), stem) if tail.isdigit() else (1 << 30, stem)


def parse(raw_path: Path, package: dict) -> Iterator[dict]:
    """Yield one record per opinion PDF in the case ZIP at ``raw_path``.

    ``package`` must carry ``package_id`` (``collection``/``date_issued`` are
    accepted for the common parser interface). A missing or malformed
    mods.xml degrades to package_id-derived fields; a bad PDF member yields a
    record with an ``extraction_note`` — neither aborts the package.
    """
    package_id = package["package_id"]
    case: dict = {}
    constituents: dict[str, dict] = {}
    mods_note = None
    with zipfile.ZipFile(raw_path) as zf:
        names = zf.namelist()
        mods_name = next((n for n in names if n.endswith("/mods.xml")), None)
        if mods_name is None:
            mods_note = "mods.xml missing from package"
        else:
            try:
                root = ET.fromstring(zf.read(mods_name))
                case = _case_level(root)
                constituents = _constituents(root)
            except (ET.ParseError, zipfile.BadZipFile) as exc:
                mods_note = f"mods.xml unreadable: {type(exc).__name__}: {exc}"
        doc_type = _court_category(
            case.get("court_type"),
            case.get("court_code") or _court_code_from_package_id(package_id),
        )
        pdf_names = [n for n in names if "/pdf/" in n and n.lower().endswith(".pdf")]
        pdf_names.sort(key=lambda n: _sequence_key(n.rsplit("/", 1)[-1][:-4]))
        for name in pdf_names:
            granule_id = name.rsplit("/", 1)[-1][:-4]
            try:
                text, note = _extract_pdf_text(zf.read(name))
            except Exception as exc:  # noqa: BLE001 — unreadable ZIP member: note, don't abort
                text, note = "", f"unreadable zip member: {type(exc).__name__}: {exc}"
            opinion = constituents.get(granule_id, {})
            metadata: dict = {}
            if case.get("court_code"):
                metadata["court_code"] = case["court_code"]
            if opinion.get("court_name"):
                metadata["court_name"] = opinion["court_name"]
            if case.get("case_number"):
                metadata["case_number"] = case["case_number"]
            if case.get("case_type"):
                metadata["case_type"] = case["case_type"]
            if opinion.get("date_filed"):
                metadata["date_filed"] = opinion["date_filed"]
            docket_text = opinion.get("docket_text")
            if docket_text:
                metadata["docket_text"] = docket_text
                precedential = _precedential(docket_text)
                if precedential is not None:
                    metadata["precedential"] = precedential
            if mods_note:
                metadata["extraction_note"] = mods_note
            elif note:
                metadata["extraction_note"] = note
            yield {
                "granule_id": granule_id,
                "doc_type": doc_type,
                "title": case.get("title"),
                "agency": None,
                "metadata": metadata,
                "text": text,
                "graphics_substantive": 0,
                "graphics_boilerplate": 0,
            }

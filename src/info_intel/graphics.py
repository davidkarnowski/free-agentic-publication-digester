"""Federal Register graphics: inventory flagged <GPH> elements, extract image assets.

Implements the EXTRACT-stage graphics handling from GUIDE.md section 5 under the
token rules of section 6:

- Rule 1 / FR-GPH-01: whole PDFs never reach a model. Graphics are extracted as
  *individual* image files so the analysis layer can send single images to a
  vision model. GIDs matching the section-coded pattern (e.g. ``EN23JY26.004``)
  are substantive content graphics; anything else (e.g. ``Trump.EPS``) is
  boilerplate -- never fetched, never analyzed, never embedded.
- Rule 9: extracted assets are plain files on disk so digests can embed them as
  cited evidence.

Public API:

- ``inventory(xml_bytes)``   -- every GPH in document order, classified, with the
  printed page it appears on.
- ``extract_assets(pdf_path, items, out_dir)`` -- write each substantive
  graphic's embedded PDF image to ``out_dir/<gid>.<ext>``.

Implementation notes (measured against the issues under ``data/raw/FR``):

- FR issue PDFs carry no ``/PageLabels`` tree, so printed page numbers are
  recovered by scanning each PDF page's header text ("46240 Federal Register /
  Vol. ..."). A constant offset is not enough: unnumbered part-divider pages are
  interleaved mid-issue.
- FR graphics are stored one embedded image XObject per graphic, encoded with
  ``CCITTFaxDecode`` (Group 4) or ``FlateDecode`` (1-bit gray). Both are wrapped
  into standard containers here with only the standard library: CCITT streams
  get a hand-built TIFF header, Flate bitmaps a PNG. pypdf's own helpers are
  unusable for this: ``page.images`` requires Pillow (not a dependency), and
  ``get_data()`` on CCITT streams emits a malformed TIFF whose IFD lacks the
  4-byte next-IFD terminator (image data overlaps it), which real decoders
  reject (verified: macOS ImageIO refuses every such file from our issues).
"""

from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from pypdf import PdfReader

__all__ = ["SUBSTANTIVE_GID_RE", "extract_assets", "inventory"]

#: Rule FR-GPH-01: section-coded GIDs are substantive; everything else is boilerplate.
SUBSTANTIVE_GID_RE = re.compile(r"^E[A-Z]\d{2}[A-Z]{2}\d{2}\.\d+$")

# Printed page number adjacent to the running head, e.g.
#   "46240 Federal Register / Vol. 91 ..."   (regular pages)
#   "Rules and Regulations Federal Register\n46239 \nVol. 91 ..." (section starts)
_HEADER_NUM_BEFORE = re.compile(r"(\d{1,6})\s*\n?\s*Federal Register")
_HEADER_NUM_AFTER = re.compile(r"Federal Register\s*\n?\s*(\d{1,6})\b")

_DO_OPERATOR = re.compile(rb"/([^\s/<>\[\]()]+)\s+Do\b")


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


def inventory(xml_bytes: bytes) -> list[dict[str, Any]]:
    """Return every ``<GPH>`` graphic in the issue XML, in document order.

    Each entry: ``{"gid", "classification", "page", "deep"}`` where
    ``classification`` is ``"substantive"`` or ``"boilerplate"`` (rule
    FR-GPH-01), ``page`` is the printed Federal Register page (nearest
    ``<PRTPAGE P="...">``: one nested inside the GPH is preferred, else the
    most recent one preceding it in the document; ``None`` if neither exists),
    and ``deep`` is the integer ``DEEP`` attribute (``None`` if absent).
    """
    root = ElementTree.fromstring(xml_bytes)
    items: list[dict[str, Any]] = []
    last_page: str | None = None
    for el in root.iter():
        if el.tag == "PRTPAGE":
            # Also visited for PRTPAGEs nested in a GPH (after the GPH itself),
            # which keeps ``last_page`` correct for the *next* graphic.
            last_page = el.get("P", last_page)
        elif el.tag == "GPH":
            nested = el.find(".//PRTPAGE")
            page = (nested.get("P") if nested is not None else None) or last_page
            gid = (el.findtext("GID") or "").strip()
            try:
                deep: int | None = int(el.get("DEEP", ""))
            except ValueError:
                deep = None
            items.append(
                {
                    "gid": gid,
                    "classification": (
                        "substantive" if SUBSTANTIVE_GID_RE.match(gid) else "boilerplate"
                    ),
                    "page": page,
                    "deep": deep,
                }
            )
    return items


# ---------------------------------------------------------------------------
# Asset extraction
# ---------------------------------------------------------------------------


def extract_assets(
    pdf_path: str | Path, items: list[dict[str, Any]], out_dir: str | Path
) -> list[dict[str, Any]]:
    """Extract each substantive graphic in ``items`` from ``pdf_path``.

    ``items`` is ``inventory()`` output (or a subset). Boilerplate items are
    never touched (status ``"skipped"``, rule FR-GPH-01). For each substantive
    item with a known printed page, the PDF page with that page number is
    located, its embedded image XObjects are read, and the image is written to
    ``out_dir/<gid>.<ext>``. When several graphics share a printed page, images
    are assigned to GIDs in order of appearance (content-stream paint order).

    Returns one dict per input item, in order:
    ``{"gid", "page", "asset_path": str | None, "status":
    "extracted" | "failed" | "skipped"}`` -- failures carry the reason in a
    ``"note"`` key and never raise for a single bad item.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    # (result index, gid) queued per printed page, preserving document order.
    queue: dict[str, list[tuple[int, str]]] = {}
    for item in items:
        entry: dict[str, Any] = {
            "gid": item.get("gid"),
            "page": item.get("page"),
            "asset_path": None,
            "status": "skipped",
        }
        results.append(entry)
        if item.get("classification") != "substantive":
            continue
        page = item.get("page")
        if not page:
            entry["status"] = "failed"
            entry["note"] = "no printed page in inventory"
            continue
        entry["status"] = "failed"  # upgraded to "extracted" on success
        queue.setdefault(str(page), []).append((len(results) - 1, entry["gid"]))

    if not queue:
        return results

    try:
        reader = PdfReader(pdf_path)
        page_map = _printed_page_map(reader, needed=set(queue))
    except Exception as exc:  # noqa: BLE001 — unreadable PDF: fail every queued item, once
        for pending in queue.values():
            for idx, _ in pending:
                results[idx]["note"] = f"could not read PDF: {exc!r}"
        return results

    for page, pending in queue.items():
        if page not in page_map:
            for idx, _ in pending:
                results[idx]["note"] = f"printed page {page} not found in PDF"
            continue
        pdf_page = reader.pages[page_map[page]]
        try:
            images = _page_images(pdf_page)
        except Exception as exc:  # noqa: BLE001 — one bad page must not kill the run
            for idx, _ in pending:
                results[idx]["note"] = f"could not list page images: {exc!r}"
            continue
        if len(images) < len(pending):
            note = f"page {page} has {len(images)} image(s) for {len(pending)} graphic(s)"
            for idx, _ in pending[len(images) :]:
                results[idx]["note"] = note
        for (idx, gid), image_obj in zip(pending, images):
            try:
                data, ext = _image_bytes(image_obj)
                asset_path = out_dir / f"{_safe_name(gid)}{ext}"
                asset_path.write_bytes(data)
            except Exception as exc:  # noqa: BLE001 — isolation per graphic (contract: never raise)
                results[idx]["note"] = f"{type(exc).__name__}: {exc}"
                continue
            results[idx]["asset_path"] = str(asset_path)
            results[idx]["status"] = "extracted"
    return results


# ---------------------------------------------------------------------------
# Printed page -> PDF page index
# ---------------------------------------------------------------------------


def _printed_page_map(reader: PdfReader, needed: set[str]) -> dict[str, int]:
    """Map printed Federal Register page numbers to 0-based PDF page indices.

    Prefers real PDF page labels; FR issue PDFs ship without a ``/PageLabels``
    tree, so the fallback scans each page's extracted header text for the
    printed number. The scan stops early once every ``needed`` page is found.
    """
    mapping: dict[str, int] = {}
    try:
        if "/PageLabels" in reader.trailer["/Root"]:
            for index, label in enumerate(reader.page_labels):
                mapping.setdefault(str(label), index)
            return mapping
    except Exception:  # noqa: BLE001 — malformed label tree: fall back to header scan
        mapping.clear()

    remaining = set(needed)
    for index, page in enumerate(reader.pages):
        if not remaining:
            break
        try:
            text = (page.extract_text() or "")[:1500]
        except Exception:  # noqa: BLE001, S112 — a page that won't extract simply stays unmapped
            continue
        match = _HEADER_NUM_BEFORE.search(text) or _HEADER_NUM_AFTER.search(text)
        if match:
            label = match.group(1)
            mapping.setdefault(label, index)
            remaining.discard(label)
    return mapping


# ---------------------------------------------------------------------------
# Image access
# ---------------------------------------------------------------------------


def _page_images(page: Any) -> list[Any]:
    """Image XObjects on a page, in order of appearance.

    Paint order is taken from ``Do`` operators in the content stream; any image
    resource never painted (or an unparsable stream) falls back to resource
    dictionary order. ``page.images`` is not used because it requires Pillow.
    """
    resources = page.get("/Resources")
    xobjects = resources.get("/XObject") if resources else None
    if not xobjects:
        return []
    image_names = [
        name
        for name in xobjects
        if xobjects[name].get_object().get("/Subtype") == "/Image"
    ]
    ordered: list[str] = []
    try:
        contents = page.get_contents()
        stream = contents.get_data() if contents is not None else b""
        for match in _DO_OPERATOR.finditer(stream):
            name = "/" + match.group(1).decode("latin-1")
            if name in image_names and name not in ordered:
                ordered.append(name)
    except Exception:  # noqa: BLE001, S110 — unparsable content stream: dict order fallback
        pass
    ordered.extend(name for name in image_names if name not in ordered)
    return [xobjects[name].get_object() for name in ordered]


def _image_bytes(obj: Any) -> tuple[bytes, str]:
    """Decode one image XObject to (file bytes, extension) without Pillow.

    CCITT fax streams are wrapped in a hand-built TIFF header (pypdf's own
    wrapper is malformed, see module docstring). DCTDecode/JPXDecode pass
    through ``get_data()`` as ready-to-write JPEG/JP2. Anything else is a raw
    bitmap, wrapped into a PNG (1/2/4/8-bit DeviceGray and 8-bit RGB).
    """
    filters = obj.get("/Filter")
    filters = filters.get_object() if hasattr(filters, "get_object") else filters
    names = [str(f) for f in (filters if isinstance(filters, list) else [filters]) if f]
    if names and names[-1] == "/CCITTFaxDecode":
        return _tiff_from_ccitt(obj, names), ".tif"
    data = obj.get_data()
    for magic, ext in (
        (b"\xff\xd8", ".jpg"),
        (b"II*\x00", ".tif"),
        (b"MM\x00*", ".tif"),
        (b"\x89PNG", ".png"),
        (b"\x00\x00\x00\x0cjP", ".jp2"),
    ):
        if data.startswith(magic):
            return data, ext
    return _png_from_raw(obj, data), ".png"


def _tiff_from_ccitt(obj: Any, filter_names: list[str]) -> bytes:
    """Wrap a raw CCITT fax stream in a minimal single-strip TIFF header.

    The G4/G3 payload is stored verbatim (TIFF compression 4/3 uses the same
    bit stream), so no fax decoding is needed. Photometric 0 (white-is-zero)
    is the fax convention regardless of the PDF ``BlackIs1`` sample flag.
    """
    raw = obj._data  # encoded stream bytes; get_data() would mangle CCITT
    for name in filter_names[:-1]:  # apply any filters stacked before the fax coding
        if name == "/FlateDecode":
            raw = zlib.decompress(raw)
        else:
            raise ValueError(f"unsupported filter {name} before CCITTFaxDecode")

    parms = obj.get("/DecodeParms")
    parms = parms.get_object() if hasattr(parms, "get_object") else parms
    if isinstance(parms, list):  # parallel to the filter array; fax parms come last
        parms = parms[-1].get_object() if parms else None
    parms = parms or {}
    if parms.get("/EncodedByteAlign"):
        raise ValueError("CCITT EncodedByteAlign has no TIFF equivalent")
    k = int(parms.get("/K", 0))
    width = int(obj["/Width"])
    height = int(obj["/Height"])

    entries = [  # (tag, type, value); type 3 = SHORT, 4 = LONG
        (256, 4, width),  # ImageWidth
        (257, 4, height),  # ImageLength
        (258, 3, 1),  # BitsPerSample
        (259, 3, 4 if k < 0 else 3),  # Compression: Group 4 / Group 3
        (262, 3, 0),  # PhotometricInterpretation: white is zero
        (273, 4, None),  # StripOffsets (patched to header size below)
        (277, 3, 1),  # SamplesPerPixel
        (278, 4, height),  # RowsPerStrip
        (279, 4, len(raw)),  # StripByteCounts
    ]
    if k >= 0:
        entries.append((292, 4, 1 if k > 0 else 0))  # T4Options: 2-D coding flag
    entries.sort()
    header_size = 8 + 2 + 12 * len(entries) + 4
    parts = [struct.pack("<2sHIH", b"II", 42, 8, len(entries))]
    for tag, typ, value in entries:
        if value is None:
            value = header_size
        parts.append(struct.pack("<HHII", tag, typ, 1, value))
    parts.append(struct.pack("<I", 0))  # no next IFD (pypdf omits this terminator)
    return b"".join(parts) + raw


def _png_from_raw(obj: Any, raw: bytes) -> bytes:
    """Wrap a decoded raw PDF bitmap in a PNG container (stdlib only)."""
    width = int(obj["/Width"])
    height = int(obj["/Height"])
    bits = 1 if obj.get("/ImageMask") else int(obj.get("/BitsPerComponent", 8))
    colorspace = obj.get("/ColorSpace")
    colorspace = colorspace.get_object() if hasattr(colorspace, "get_object") else colorspace

    if obj.get("/ImageMask") or str(colorspace) == "/DeviceGray":
        if bits not in (1, 2, 4, 8):
            raise ValueError(f"unsupported gray bit depth {bits}")
        color_type, stride = 0, (width * bits + 7) // 8
    elif str(colorspace) == "/DeviceRGB" and bits == 8:
        color_type, stride = 2, width * 3
    else:
        raise ValueError(f"unsupported raw image: colorspace={colorspace!r} bits={bits}")

    if len(raw) < stride * height:
        raise ValueError(f"raw bitmap truncated: {len(raw)} < {stride * height} bytes")

    decode = obj.get("/Decode")
    if decode and list(decode)[:2] == [1, 0]:  # inverted samples
        if bits == 1:
            raw = bytes(b ^ 0xFF for b in raw)
        elif bits == 8 and color_type == 0:
            raw = bytes(255 - b for b in raw)

    scanlines = b"".join(
        b"\x00" + raw[row * stride : (row + 1) * stride] for row in range(height)
    )

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(">I", zlib.crc32(tag + payload))
        )

    header = struct.pack(">IIBBBBB", width, height, bits, color_type, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(scanlines, 9))
        + chunk(b"IEND", b"")
    )


def _safe_name(gid: str) -> str:
    """GID as a safe filename component (defensive; real GIDs are already safe)."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", gid) or "graphic"

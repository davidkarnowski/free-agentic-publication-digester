"""CREC (Congressional Record, daily edition) parser.

Input: the govinfo daily ZIP (``data/raw/CREC/<date>/CREC-<date>.zip``),
which contains one ``.htm`` file per granule under ``CREC-<date>/html/``
(the govinfo docs say ``htm/``; the ZIPs on disk use ``html/`` — we match
by filename pattern, not directory name). Granule stems are govinfo
granule IDs, e.g. ``CREC-2026-07-23-pt1-PgS4241-8``.

Output: one record dict per granule htm (see ``parse``). Extraction is
verbatim per GUIDE §2 — tags are stripped and GPO online-edition header
boilerplate is dropped, but the Record text itself is never altered or
summarized. Pure function per docs/schema.md: no database access.

Stdlib only (zipfile + html.parser).
"""

import re
import zipfile
from collections.abc import Iterator
from html.parser import HTMLParser

# Granule-ID shape: CREC-<date>-pt<part>-Pg<page>[-<seq>].
# <page> may be a printed page ("S4241") or a pseudo-page ("S-FrontMatter").
_GRANULE_ID_RE = re.compile(
    r"^(?P<issue>CREC-\d{4}-\d{2}-\d{2})"
    r"-pt(?P<part>\d+)"
    r"-Pg(?P<page>.+?)"
    r"(?:-(?P<seq>\d+))?$"
)

# Section by page-number prefix (mechanical, per govinfo granuleClass).
_DOC_TYPES = {
    "S": "SENATE",
    "H": "HOUSE",
    "E": "EXTENSIONS",
    "D": "DAILYDIGEST",
}

# <title> boilerplate: "Congressional Record, Volume 172 Issue 121
# (Thursday, July 23, 2026)" — optionally followed by a real heading.
_TITLE_BOILERPLATE_RE = re.compile(
    r"^Congressional Record\b[^()]*(?:\([^)]*\))?[\s,:;–—-]*",
    re.IGNORECASE,
)

# GPO online-edition header lines dropped from text: bracketed issue/section/
# page lines at the very top, and the "From the Congressional Record
# Online..." attribution line wherever it appears.
_HEADER_BRACKET_RE = re.compile(r"^\[.*\]$")
_GPO_ATTRIBUTION = "From the Congressional Record Online"


class _TextExtractor(HTMLParser):
    """Collects <title> content and body text; skips script/style."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._body: list[str] = []
        self._title: list[str] = []
        self._in_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "title":
            self._in_title = True
        elif tag in ("script", "style"):
            self._skip_depth += 1
        elif tag == "br":
            self._body.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag in ("script", "style") and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title.append(data)
        elif not self._skip_depth:
            self._body.append(data)

    @property
    def title(self) -> str:
        return "".join(self._title)

    @property
    def body(self) -> str:
        return "".join(self._body)


def _decode(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _is_granule_htm(member_name: str) -> bool:
    """True for per-granule htm members; excludes pdf/, mods/premis/dip
    metadata, and whole-issue htm files (no ``-pt<n>-Pg`` in the stem)."""
    basename = member_name.rsplit("/", 1)[-1]
    if not basename.lower().endswith(".htm"):
        return False
    return _GRANULE_ID_RE.match(basename[: -len(".htm")]) is not None


def _clean_title(raw_title: str) -> str | None:
    """<title> content minus the leading "Congressional Record ..."
    boilerplate; None when nothing (or only boilerplate) remains."""
    title = " ".join(raw_title.split())
    if not title:
        return None
    stripped = _TITLE_BOILERPLATE_RE.sub("", title).strip()
    return stripped or None


def _normalize_text(body: str) -> str:
    """Whitespace normalization that preserves line structure.

    - line breaks kept (floor transcripts are line-oriented); leading
      indentation kept (centered headings, quoted material)
    - trailing whitespace stripped per line; NBSP -> space
    - the GPO attribution line and the leading bracketed header block
      ("[Congressional Record Volume ...]", "[Senate]", "[Pages ...]")
      dropped; mid-text "[[Page Sxxxx]]" break markers are kept
    - runs of blank lines collapsed to one; no leading/trailing blanks
    """
    text = body.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    lines = [line.rstrip() for line in text.split("\n")]

    # Drop the leading header block: blanks and full-line [...] entries
    # up to the first real content line.
    start = 0
    while start < len(lines):
        line = lines[start].strip()
        if line and not _HEADER_BRACKET_RE.match(line):
            break
        start += 1
    lines = lines[start:]

    out: list[str] = []
    for line in lines:
        if line.strip().startswith(_GPO_ATTRIBUTION):
            continue
        if not line and (not out or not out[-1]):
            continue  # collapse blank runs; no leading blanks
        out.append(line)
    while out and not out[-1]:
        out.pop()
    return "\n".join(out)


def _granule_sort_key(member_name: str) -> tuple:
    """Issue order: part, then page string, then sequence (the unsuffixed
    granule is sequence 1; lexicographic sort would put "-2" before it)."""
    stem = member_name.rsplit("/", 1)[-1][: -len(".htm")]
    match = _GRANULE_ID_RE.match(stem)
    return (match["issue"], int(match["part"]), match["page"], int(match["seq"] or 1))


def parse(raw_path, package: dict) -> Iterator[dict]:
    """Yield one record per granule htm in a CREC daily ZIP.

    ``raw_path``: path to (or open binary file of) the package ZIP.
    ``package``: dict with package_id / collection / date_issued (unused
    beyond the contract; the ZIP is self-describing).
    """
    with zipfile.ZipFile(raw_path) as zf:
        members = sorted(
            (name for name in zf.namelist() if _is_granule_htm(name)),
            key=_granule_sort_key,
        )
        for name in members:
            granule_id = name.rsplit("/", 1)[-1][: -len(".htm")]
            match = _GRANULE_ID_RE.match(granule_id)  # guaranteed by filter
            page = match["page"]
            metadata: dict = {"page": page, "part": int(match["part"])}
            if match["seq"] is not None:
                metadata["sequence"] = int(match["seq"])

            extractor = _TextExtractor()
            extractor.feed(_decode(zf.read(name)))
            extractor.close()

            yield {
                "granule_id": granule_id,
                "doc_type": _DOC_TYPES.get(page[:1]),
                "title": _clean_title(extractor.title),
                "agency": None,
                "metadata": metadata,
                "text": _normalize_text(extractor.body),
                "graphics_substantive": 0,  # CREC is pure text (measured)
                "graphics_boilerplate": 0,
            }

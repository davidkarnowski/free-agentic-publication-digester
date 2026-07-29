"""Provenance layer for mutable sources (GUIDE §7).

Every observation is an assertion: captures store the exact bytes served
to our identified client (content-addressed by sha256), attempts that
yielded no content (304s, robots refusals, errors) are recorded too, and
each UTC day's events are exported to a committed manifest whose header
chains to the previous manifest's hash — so days can't be silently
dropped or reordered without the files themselves showing it.

Honest limits are documented in PROVENANCE.md: hashes prove what was
served to us; timestamps are backed by git/GitHub ordering and Wayback
corroboration, not third-party notarization.
"""

import datetime as dt
import hashlib
import json
import logging
import re
from html.parser import HTMLParser

from . import config
from .sync import utc_now_iso

logger = logging.getLogger("fapd.provenance")

# Response headers preserved as forensic context (server's own claims).
_HEADER_KEEP = (
    "Date", "Server", "ETag", "Last-Modified", "Content-Type",
    "Content-Encoding", "Age", "X-Cache", "CF-Ray", "Via",
)

_CHARSET_RE = re.compile(rb'charset=["\']?([A-Za-z0-9_-]+)', re.IGNORECASE)


class _TextExtractor(HTMLParser):
    _SKIP = frozenset({"script", "style", "noscript", "template"})

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data):
        if not self._skip_depth:
            self.parts.append(data)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_body(body: bytes, content_type: str | None) -> str:
    """Deterministic charset decoding: header charset, else <meta> charset,
    else UTF-8 with replacement (recorded via NORMALIZER_VERSION)."""
    charset = None
    if content_type and "charset=" in content_type:
        charset = content_type.split("charset=")[-1].split(";")[0].strip()
    if not charset:
        m = _CHARSET_RE.search(body[:4096])
        charset = m.group(1).decode("ascii", "ignore") if m else None
    for candidate in (charset, "utf-8"):
        if not candidate:
            continue
        try:
            return body.decode(candidate)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", errors="replace")


def normalize_text(body: bytes, content_type: str | None) -> str:
    """Normalized text for text_sha256: tags stripped, whitespace collapsed.
    Comparable only within one config.NORMALIZER_VERSION."""
    text = decode_body(body, content_type)
    if content_type and "html" in content_type:
        parser = _TextExtractor()
        parser.feed(text)
        text = " ".join(parser.parts)
    return " ".join(text.split())


def store_bytes(body: bytes) -> str:
    """Content-addressed write; returns sha256. Identical bytes dedupe."""
    digest = sha256_hex(body)
    path = config.CAPTURE_DIR / digest[:2] / f"{digest}.bin"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    return digest


def get_or_create_document(conn, source_id, stable_id, url, title=None,
                           claimed_published_at=None):
    row = conn.execute(
        "SELECT id FROM documents WHERE source_id = ? AND stable_id = ?",
        (source_id, stable_id),
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO documents (source_id, stable_id, url, title,"
        " claimed_published_at, first_seen_at) VALUES (?, ?, ?, ?, ?, ?)",
        (source_id, stable_id, url, title, claimed_published_at, utc_now_iso()),
    )
    conn.commit()
    return cur.lastrowid


def _latest_capture(conn, document_id):
    return conn.execute(
        "SELECT * FROM captures WHERE document_id = ?"
        " AND content_sha256 IS NOT NULL ORDER BY id DESC LIMIT 1",
        (document_id,),
    ).fetchone()


def record_attempt(conn, document_id, url, change_kind, *, http_status=None,
                   note=None, response_headers=None):
    """Non-content events: 304s, robots refusals, errors, missing/removed.
    Absence must be an assertion (GUIDE §7)."""
    prev = _latest_capture(conn, document_id)
    conn.execute(
        "INSERT INTO captures (document_id, ts_utc, url, http_status,"
        " change_kind, prev_capture_id, note, response_headers, normalizer_version)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (document_id, utc_now_iso(), url, http_status, change_kind,
         prev["id"] if prev else None, note,
         json.dumps(response_headers, sort_keys=True) if response_headers else None,
         config.NORMALIZER_VERSION),
    )
    conn.commit()


def capture(conn, document_id, url, resp):
    """Record a content-bearing response. Returns the captures row id and
    the computed change_kind."""
    body = resp.content or b""
    content_type = resp.headers.get("Content-Type")
    content_sha = store_bytes(body)
    text_sha = sha256_hex(normalize_text(body, content_type).encode())
    headers = {k: v for k, v in resp.headers.items() if k in _HEADER_KEEP}
    prev = _latest_capture(conn, document_id)

    if prev is None:
        kind = "new"
    elif prev["content_sha256"] == content_sha:
        kind = "unchanged"
    elif (prev["text_sha256"] == text_sha
          and prev["normalizer_version"] == config.NORMALIZER_VERSION):
        kind = "bytes_changed"  # template noise; words identical
    else:
        kind = "modified"

    cur = conn.execute(
        "INSERT INTO captures (document_id, ts_utc, url, final_url, http_status,"
        " content_sha256, text_sha256, normalizer_version, content_type, bytes,"
        " response_headers, change_kind, prev_capture_id)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (document_id, utc_now_iso(), url, getattr(resp, "url", None),
         resp.status_code, content_sha, text_sha, config.NORMALIZER_VERSION,
         content_type, len(body), json.dumps(headers, sort_keys=True), kind,
         prev["id"] if prev else None),
    )
    conn.commit()
    if kind in ("modified", "bytes_changed"):
        logger.info("capture: document %d %s (content %s… -> %s…)",
                    document_id, kind,
                    (prev["content_sha256"] or "")[:12], content_sha[:12])
    return cur.lastrowid, kind


def set_wayback(conn, capture_id, wayback_url, status):
    conn.execute(
        "UPDATE captures SET wayback_url = ?, wayback_status = ? WHERE id = ?",
        (wayback_url, status, capture_id),
    )
    conn.commit()


def _prev_manifest_sha(date):
    config.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    earlier = sorted(
        p for p in config.MANIFEST_DIR.glob("*.jsonl") if p.stem < date
    )
    if not earlier:
        return None
    return sha256_hex(earlier[-1].read_bytes())


def export_manifest(conn, date=None):
    """Write the committed daily manifest: one header line (chained to the
    previous day's manifest hash) + one line per capture attempt that UTC
    day. Deterministic given the database."""
    date = date or dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
    rows = conn.execute(
        """
        SELECT c.ts_utc, d.source_id, c.url, c.final_url, c.http_status,
               c.content_sha256, c.text_sha256, c.normalizer_version,
               c.change_kind, c.wayback_url, c.note
        FROM captures c JOIN documents d ON d.id = c.document_id
        WHERE substr(c.ts_utc, 1, 10) = ? ORDER BY c.id
        """,
        (date,),
    ).fetchall()
    header = {
        "manifest": date,
        "prev_manifest_sha256": _prev_manifest_sha(date),
        "normalizer_version": config.NORMALIZER_VERSION,
        "entries": len(rows),
        "note": "one line per fetch attempt incl. 304s/refusals/errors;"
                " hashes are of content as served to our identified client",
    }
    lines = [json.dumps(header, sort_keys=True)]
    lines += [json.dumps(dict(r), sort_keys=True) for r in rows]
    config.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = config.MANIFEST_DIR / f"{date}.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("manifest %s: %d entr%s written", date, len(rows),
                "y" if len(rows) == 1 else "ies")
    return path


def verify_stored(content_sha256):
    """Recompute a stored capture's hash; True iff bytes match the address."""
    path = config.CAPTURE_DIR / content_sha256[:2] / f"{content_sha256}.bin"
    return path.exists() and sha256_hex(path.read_bytes()) == content_sha256

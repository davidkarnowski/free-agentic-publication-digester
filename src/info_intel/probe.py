"""Source viability + content probe (GUIDE §3 onboarding).

For each registry source this verifies the WHOLE ingestion chain, not just
liveness: robots verdict → fetch feed/index (captured through the
provenance layer — these are evidentiary observations) → format sniffing
→ RSS/Atom autodiscovery on HTML pages → item enumeration with field
inventory → one sample article fetched, captured, and text-extracted, so
"retrieving and ingesting properly" is demonstrated end to end. Findings
are structured JSON per source; nothing is ever guessed: a blocked or
broken source records exactly what was observed.
"""

import json
import logging
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import requests

from . import config, provenance
from .client import RobotsDisallowedError
from .sync import utc_now_iso

logger = logging.getLogger("info_intel.probe")

_ATOM_NS = "{http://www.w3.org/2005/Atom}"


class _FeedLinkFinder(HTMLParser):
    """RSS/Atom autodiscovery: <link rel="alternate" type="application/rss+xml">."""

    def __init__(self):
        super().__init__()
        self.feeds = []

    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        a = dict(attrs)
        if (a.get("rel", "").lower() == "alternate"
                and "xml" in (a.get("type") or "")
                and a.get("href")):
            self.feeds.append(a["href"])


def _absolute(base, href):
    from urllib.parse import urljoin

    return urljoin(base, href)


def parse_feed(body: bytes):
    """Minimal RSS/Atom item enumeration. Returns (format, items) where
    each item has title/link/guid/claimed_date/description_chars."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return None, []
    items = []
    if root.tag in ("rss", "rdf:RDF") or root.tag.endswith("rss"):
        for it in root.iter("item"):
            items.append({
                "title": (it.findtext("title") or "").strip()[:200],
                "link": (it.findtext("link") or "").strip(),
                "guid": (it.findtext("guid") or "").strip() or None,
                "claimed_date": (it.findtext("pubDate") or "").strip() or None,
                "description_chars": len((it.findtext("description") or "").strip()),
                "description": (it.findtext("description") or "").strip(),
            })
        return "rss", items
    if root.tag == f"{_ATOM_NS}feed":
        for it in root.iter(f"{_ATOM_NS}entry"):
            link = ""
            for ln in it.iter(f"{_ATOM_NS}link"):
                if ln.get("rel") in (None, "alternate"):
                    link = ln.get("href") or ""
                    break
            items.append({
                "title": (it.findtext(f"{_ATOM_NS}title") or "").strip()[:200],
                "link": link.strip(),
                "guid": (it.findtext(f"{_ATOM_NS}id") or "").strip() or None,
                "claimed_date": (it.findtext(f"{_ATOM_NS}updated") or "").strip() or None,
                "description_chars": len(
                    (it.findtext(f"{_ATOM_NS}summary")
                     or it.findtext(f"{_ATOM_NS}content") or "").strip()
                ),
                "description": (it.findtext(f"{_ATOM_NS}summary")
                                or it.findtext(f"{_ATOM_NS}content") or "").strip(),
            })
        return "atom", items
    return None, []


def _capture_probe(conn, source_id, url, resp):
    doc_id = provenance.get_or_create_document(
        conn, source_id, f"probe:{url}", url, title=f"probe fetch of {url}"
    )
    return provenance.capture(conn, doc_id, url, resp)


def _fetch(client, conn, source_id, url, findings):
    """One probed fetch: outcome recorded in findings, body captured."""
    event = {"url": url, "outcome": None, "status": None}
    findings["fetches"].append(event)
    try:
        resp = client.get(url)
    except RobotsDisallowedError:
        event["outcome"] = "robots_refused"
        doc_id = provenance.get_or_create_document(
            conn, source_id, f"probe:{url}", url)
        provenance.record_attempt(conn, doc_id, url, "robots_refused")
        return None
    except requests.HTTPError as exc:
        status = getattr(exc.response, "status_code", None)
        event["outcome"] = "http_error"
        event["status"] = status
        doc_id = provenance.get_or_create_document(
            conn, source_id, f"probe:{url}", url)
        provenance.record_attempt(conn, doc_id, url, "error",
                                  http_status=status, note="probe fetch failed")
        return None
    except requests.RequestException as exc:
        event["outcome"] = "network_error"
        event["error"] = type(exc).__name__
        return None
    event["outcome"] = "ok"
    event["status"] = resp.status_code
    event["content_type"] = resp.headers.get("Content-Type", "")
    event["bytes"] = len(resp.content or b"")
    _capture_probe(conn, source_id, url, resp)
    return resp


def probe_source(client, conn, entry):
    """Probe one registry entry end-to-end. Returns structured findings."""
    findings = {
        "id": entry["id"],
        "probed_at": utc_now_iso(),
        "declared_type": entry["type"],
        "fetches": [],
        "feed": None,
        "sample_item": None,
        "verdict": None,
    }
    urls = entry.get("urls") or {}
    start_url = urls.get("feed") or urls.get("index") or urls.get("home")
    if not start_url:
        findings["verdict"] = "no-url"
        return findings

    resp = _fetch(client, conn, entry["id"], start_url, findings)
    if resp is None:
        findings["verdict"] = findings["fetches"][-1]["outcome"]
        return findings

    body = resp.content or b""
    ctype = resp.headers.get("Content-Type", "")
    fmt, items = parse_feed(body)

    # HTML page: try feed autodiscovery once.
    if fmt is None and "html" in ctype:
        finder = _FeedLinkFinder()
        finder.feed(provenance.decode_body(body, ctype))
        if finder.feeds:
            feed_url = _absolute(str(getattr(resp, "url", start_url)), finder.feeds[0])
            findings["autodiscovered_feed"] = feed_url
            resp2 = _fetch(client, conn, entry["id"], feed_url, findings)
            if resp2 is not None:
                fmt, items = parse_feed(resp2.content or b"")

    if fmt:
        findings["feed"] = {
            "format": fmt,
            "items": len(items),
            "with_guid": sum(1 for i in items if i["guid"]),
            "with_date": sum(1 for i in items if i["claimed_date"]),
            "avg_description_chars": (
                sum(i["description_chars"] for i in items) // len(items) if items else 0
            ),
            "newest": items[0] if items else None,
        }
        # Verify the full ingestion chain with ONE sample article.
        sample = next((i for i in items if i["link"]), None)
        if sample:
            art = _fetch(client, conn, entry["id"], sample["link"], findings)
            if art is not None:
                text = provenance.normalize_text(
                    art.content or b"", art.headers.get("Content-Type"))
                findings["sample_item"] = {
                    "title": sample["title"],
                    "url": sample["link"],
                    "text_chars": len(text),
                    "text_head": text[:400],
                }
        findings["verdict"] = "feed-ok" if items else "feed-empty"
    elif "html" in ctype:
        text = provenance.normalize_text(body, ctype)
        findings["html_index"] = {"text_chars": len(text)}
        findings["verdict"] = "html-only"
    else:
        findings["verdict"] = f"unrecognized:{ctype.split(';')[0]}"
    return findings


def run(client, conn, entries, out_dir=None):
    out_dir = out_dir or (config.DATA_DIR / "probe" / utc_now_iso()[:10])
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for entry in entries:
        logger.info("probing %s (%s)", entry["id"], entry["type"])
        try:
            findings = probe_source(client, conn, entry)
        except Exception as exc:  # noqa: BLE001 — one source never kills the sweep
            findings = {"id": entry["id"], "verdict": "probe-crash",
                        "error": repr(exc)[:300], "probed_at": utc_now_iso()}
            logger.warning("%s: probe crashed: %r", entry["id"], exc)
        (out_dir / f"{entry['id']}.json").write_text(
            json.dumps(findings, indent=1, sort_keys=True), encoding="utf-8")
        summary.append({"id": findings["id"], "verdict": findings.get("verdict")})
    (out_dir / "_summary.json").write_text(
        json.dumps(summary, indent=1), encoding="utf-8")
    provenance.export_manifest(conn)
    return out_dir, summary


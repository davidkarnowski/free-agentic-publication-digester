"""Agency newsroom ingestion (S2 pilot; GUIDE §3 agency newsrooms).

RSS-first, through the robots-enforcing AgencyClient with conditional
GETs, every response captured into the provenance layer, every new
capture submitted to the Wayback Machine (its own budget; failures never
block). Items enter the standard packages/extracted model under the
AGENCYPR pseudo-collection so the digest, coverage accounting, and site
machinery apply unchanged. Zero LLM calls in the pilot: the digest lists
attributed titles (GUIDE §2 attributed-speech rule).
"""

import hashlib
import logging
from urllib.parse import parse_qs, urlsplit, urlunsplit

import requests

from . import config, provenance
from .client import HttpClient, RobotsDisallowedError
from .probe import parse_feed
from .sync import publication_date, utc_now_iso

logger = logging.getLogger("fapd.agencies")

class SourceAdapter:
    """Per-source ingestion strategy (GUIDE §3 "Source adapters").

    A registry entry may name an adapter (field `adapter`; default "rss")
    to handle unique publication interfaces without touching the shared
    poll loop. The loop owns everything that must never vary per source —
    conditional requests, robots enforcement, pacing/budgets, provenance
    capture, Wayback corroboration, storage. An adapter owns exactly five
    decisions, called in this order:

    0. items(body, content_type) — index/feed bytes -> the item list.
    1. stable_id(item)  — what makes two sightings the same document.
    2. wants_article()  — fetch the article page, or feed metadata only.
    3. extract_text(body, content_type, item) — served bytes -> plain text.
    4. fallback_text(item) — what to store when no article is available.

    AN INDEX IS NOT A FEED. A feed carries recent items; an index can
    carry an entire session (the Senate's vote menu lists every vote of
    the Congress). An items() implementation reading an index MUST bound
    itself to config.INDEX_LOOKBACK_DAYS before returning, or first
    activation spends hundreds of requests fetching articles the §3
    dating rule then excludes as backfill. The default below reads feeds,
    which are already bounded by the publisher.

    IDENTITY IS A COMPATIBILITY CONTRACT. package ids are derived from
    stable_id's output (PR-<source>-<sha8 of stable_id>), and dedupe keys
    on them. Changing what stable_id returns for an already-seen item —
    including "harmless" normalization of the default's raw-URL fallback —
    re-mints every such identity and re-ingests history as duplicates.
    As of 2026-07-28, 67 of 231 stored documents carry raw-URL identities
    from the default fallback, so the default below is frozen byte-for-byte.
    New adapters may normalize freely (UspsAdapter does) because they start
    with no history; changing an ACTIVE source's adapter, or this default,
    requires a migration story first.

    Error posture: extract_text may raise — the poll loop degrades that
    item to fallback_text with mode "extract-fallback" and moves on (the
    raw capture is already stored either way, so evidence survives).
    stable_id and fallback_text must not raise; they run before any
    storage exists for the item."""

    def items(self, body, content_type):
        """(format_name, [item]) from the fetched index/feed bytes.

        Items carry the probe.parse_feed shape: title, link, guid,
        claimed_date, description. `claimed_date` must be RFC 822 or
        ISO-8601-prefixed or report._claimed_day cannot read it and the
        item is dated by observation instead (GUIDE §3 dating rule).

        Returning (None, []) marks the response unparsable — the loop
        records that and discloses it. Must not raise: it runs before any
        storage exists, like stable_id and fallback_text."""
        return parse_feed(body)

    def stable_id(self, item):
        # Frozen: see IDENTITY IS A COMPATIBILITY CONTRACT above.
        return item.get("guid") or item["link"]

    def wants_article(self):
        return True

    def extract_text(self, body, content_type, item):
        return provenance.normalize_text(body, content_type)

    def fallback_text(self, item):
        parts = [item.get("title") or ""]
        if item.get("description"):
            parts.append(provenance.normalize_text(
                item["description"].encode(), "text/html"))
        return " — ".join(p for p in parts if p)


class FeedOnlyAdapter(SourceAdapter):
    """For sources whose feed is open but whose article pages block
    identified clients (probe finding: defense.gov) — feed metadata only,
    never fetching what we'd be refused. Also the right choice on budget
    grounds alone: a host with a large robots crawl-delay (gao.gov: 420s)
    prices each article fetch at minutes of wall clock, and a source whose
    feed descriptions already carry the substance may not be worth that
    price. Ingestion mode is disclosed per item ("feed-only") so the
    digest's mutability/completeness statements stay honest."""

    def wants_article(self):
        return False


class UspsAdapter(SourceAdapter):
    """USPS Newsroom (probe 2026-07-26; captured bytes re-examined 2026-07-28).

    What the captured bytes actually showed: the feed's 668 items have
    zero GUIDs, and every <link> routes through
    /newsroom/rssrequest.htm?nr=<article-path> — a 1.8 KB JavaScript
    interstitial (capture 86d65e1c…) that redirects via window.location
    to '/newsroom/' + nr. The interstitial embeds NO article content:
    no JSON-LD, no framework state blob — its entire visible text is
    "RSS Feed Request" (the probe's 16-char extraction). The real
    article pages were never served to our client, so whether they
    extract is unknown; establishing that requires a re-probe of a
    resolved direct URL (operator's call).

    Consequences implemented here:
    - stable_id statically resolves the interstitial (mirroring the
      redirect arithmetic present in the served bytes — parsing, not
      browser execution) to the canonical article URL, then normalizes:
      lowercase scheme/host, query/fragment stripped, trailing slash
      stripped. Identity survives URL noise (GUIDE §7 T5) without
      collapsing distinct items whose only identity lives in nr=.
    - wants_article() is False: fetching a feed link yields the known
      contentless interstitial; a request per item for bytes known to
      carry no article text fails §4.
    - extract_text never raises and is defensive: interstitial or empty
      input falls back to feed metadata; other HTML gets the standard
      extractor. Stored text is therefore title + ~270-char lede
      description, disclosed via mode ("feed-only") and char_count.
    """

    _INTERSTITIAL_PATH = "/newsroom/rssrequest.htm"

    def _resolve_interstitial(self, url):
        """rssrequest.htm?nr=<path> -> the article URL the page's own
        JavaScript redirects to ('/newsroom/' + nr). Static parsing of
        served bytes' documented behavior; no execution, no evasion."""
        parts = urlsplit(url)
        if parts.path.lower() == self._INTERSTITIAL_PATH:
            nr = (parse_qs(parts.query).get("nr") or [""])[0].strip()
            if nr:
                return urlunsplit((parts.scheme, parts.netloc,
                                   "/newsroom/" + nr.lstrip("/"), "", ""))
        return url

    def stable_id(self, item):
        parts = urlsplit(self._resolve_interstitial(item.get("link") or ""))
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                           parts.path.rstrip("/") or "/", "", ""))

    def wants_article(self):
        return False  # feed links serve a contentless JS redirect page

    def extract_text(self, body, content_type, item):
        try:
            text = super().extract_text(body, content_type, item)
        except Exception:  # noqa: BLE001 — never raise; disclose via length
            text = ""
        if not text.strip() or text.strip().lower() == "rss feed request":
            return self.fallback_text(item)  # interstitial carries no article
        return text


ADAPTERS = {
    "rss": SourceAdapter,
    "rss-feed-only": FeedOnlyAdapter,
    "usps": UspsAdapter,
}


# The registry key an entry publishes from. Feeds use `feed`; index and
# API entries use `index`/`collection`. poll_source and host_groups must
# resolve identically or a source would be grouped under one host and
# fetched from another, breaking the one-client-per-host pacing promise.
def source_url(entry):
    urls = entry.get("urls") or {}
    return urls.get("feed") or urls.get("index") or urls.get("collection")


# Registry types the agency poll loop can ingest. Widened as adapters
# arrive; kept here so the three call sites cannot drift apart.
INGESTIBLE_TYPES = ("rss",)


def adapter_for(entry):
    name = entry.get("adapter") or "rss"
    try:
        return ADAPTERS[name]()
    except KeyError:
        raise ValueError(
            f"source {entry.get('id', '<no id>')!r}: unknown adapter {name!r} "
            f"(known: {', '.join(ADAPTERS)}) — registry validation should have "
            f"caught this"
        ) from None


class WaybackClient(HttpClient):
    """Save-Page-Now submissions: own budget bucket, same accountability."""

    CLIENT_NAME = "wayback"
    SAVE_BASE = "https://web.archive.org/save/"

    def _daily_budget(self):
        return config.MAX_WAYBACK_REQUESTS_PER_DAY

    def save(self, url):
        """Submit a URL; returns the snapshot URL or None. Never raises."""
        try:
            resp = self.get(self.SAVE_BASE + url)
        except Exception as exc:  # noqa: BLE001 — corroboration is best-effort
            logger.info("wayback: submission failed for %s: %r", url, exc)
            return None
        loc = resp.headers.get("Content-Location")
        if loc:
            return f"https://web.archive.org{loc}"
        final = str(getattr(resp, "url", "") or "")
        return final if "/web/" in final else None


def _package_id(source_id, stable_id):
    digest = hashlib.sha256(stable_id.encode()).hexdigest()[:8]
    return f"PR-{source_id}-{digest}"


def _already_ingested(conn, package_id):
    return conn.execute(
        "SELECT 1 FROM packages WHERE package_id = ?", (package_id,)
    ).fetchone() is not None


def _store_item(conn, entry, item, package_id, text, mode, capture_id, wayback_url):
    now = utc_now_iso()
    # The publication day is Washington's, not UTC's (GUIDE §3, amended
    # 2026-07-30): an 8:30pm-Eastern release belongs to that day, not to
    # the next one UTC had already started. Observation stamps stay UTC.
    issued = publication_date()
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " title, package_link, first_seen_at, fetch_status, fetched_at)"
        " VALUES (?, 'AGENCYPR', ?, ?, ?, ?, ?, 'fetched', ?)",
        (package_id, issued, now, item["title"], item["link"], now, now),
    )
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, '', 'AGENCYPR', 'PRESS', ?, ?, ?, ?, ?, ?, 1)",
        (
            package_id, item["title"], entry["name"],
            _metadata_json(entry, item, mode, capture_id, wayback_url),
            text, len(text), now,
        ),
    )
    conn.commit()


def _metadata_json(entry, item, mode, capture_id, wayback_url):
    import json

    return json.dumps({
        "source_id": entry["id"],
        "url": item["link"],
        "claimed_published_at": item.get("claimed_date"),
        "mode": mode,
        "capture_id": capture_id,
        "wayback_url": wayback_url,
    }, sort_keys=True)


def poll_source(client, wayback, conn, entry):
    """One conditional poll of one active source. Returns stats."""
    stats = {"id": entry["id"], "feed_status": None, "new_items": 0,
             "articles_fetched": 0, "wayback_submitted": 0, "errors": 0}
    feed_url = source_url(entry)
    if not feed_url:
        stats["feed_status"] = "no-feed-url"
        return stats

    state = conn.execute(
        "SELECT etag, last_modified FROM feed_state WHERE source_id = ?",
        (entry["id"],),
    ).fetchone()
    headers = {}
    if state and state["etag"]:
        headers["If-None-Match"] = state["etag"]
    if state and state["last_modified"]:
        headers["If-Modified-Since"] = state["last_modified"]

    try:
        resp = client.get(feed_url, headers=headers or None)
    except (RobotsDisallowedError, requests.RequestException) as exc:
        stats["feed_status"] = f"error:{type(exc).__name__}"
        stats["errors"] += 1
        return stats

    conn.execute(
        "INSERT INTO feed_state (source_id, etag, last_modified, last_polled_at)"
        " VALUES (?, ?, ?, ?) ON CONFLICT(source_id) DO UPDATE SET"
        " etag = COALESCE(excluded.etag, feed_state.etag),"
        " last_modified = COALESCE(excluded.last_modified, feed_state.last_modified),"
        " last_polled_at = excluded.last_polled_at",
        (entry["id"], resp.headers.get("ETag"),
         resp.headers.get("Last-Modified"), utc_now_iso()),
    )
    conn.commit()

    if resp.status_code == 304:
        stats["feed_status"] = "not-modified"
        return stats
    adapter = adapter_for(entry)
    fmt, items = adapter.items(resp.content or b"",
                               resp.headers.get("Content-Type"))
    if fmt is None:
        stats["feed_status"] = "unparsable"
        stats["errors"] += 1
        return stats
    stats["feed_status"] = f"{fmt}:{len(items)}"
    pending, seen = [], set()
    for item in items:
        if not item["link"]:
            continue
        stable_id = adapter.stable_id(item)
        package_id = _package_id(entry["id"], stable_id)
        if package_id in seen or _already_ingested(conn, package_id):
            continue
        seen.add(package_id)
        pending.append((item, stable_id, package_id))
    logger.info("%s: feed has %d items; %d new to ingest%s", entry["id"],
                len(items), len(pending),
                "" if adapter.wants_article() else " (feed-metadata only)")
    for position, (item, stable_id, package_id) in enumerate(pending, 1):
        doc_id = provenance.get_or_create_document(
            conn, entry["id"], stable_id, item["link"], title=item["title"],
            claimed_published_at=item.get("claimed_date"),
        )
        capture_id = wayback_url = None
        if adapter.wants_article():
            try:
                art = client.get(item["link"])
            except (RobotsDisallowedError, requests.RequestException) as exc:
                provenance.record_attempt(
                    conn, doc_id, item["link"], "error",
                    note=f"article fetch failed: {type(exc).__name__}")
                stats["errors"] += 1
                text = adapter.fallback_text(item)  # ingested, disclosed
                mode_used = "feed-fallback"
            else:
                capture_id, _kind = provenance.capture(conn, doc_id, item["link"], art)
                stats["articles_fetched"] += 1
                try:
                    text = adapter.extract_text(
                        art.content or b"", art.headers.get("Content-Type"), item)
                    mode_used = "full"
                except Exception as exc:  # noqa: BLE001 — one bad page must not
                    # cost the source's remaining items; the capture is already
                    # stored, so the evidence survives even when extraction fails
                    logger.warning("%s: extract_text failed for %s: %r — "
                                   "storing feed metadata instead",
                                   entry["id"], item["link"], exc)
                    stats["errors"] += 1
                    text = adapter.fallback_text(item)
                    mode_used = "extract-fallback"
                if not text.strip():
                    # Empty extraction (challenge interstitials, blank shells)
                    # must never be stored as mode "full" — that would launder
                    # a degraded fetch into looking complete (2026-07-28: DOJ
                    # served Akamai bm-verify pages that extracted to nothing).
                    logger.warning("%s: empty extraction for %s — storing feed"
                                   " metadata instead", entry["id"], item["link"])
                    stats["errors"] += 1
                    text = adapter.fallback_text(item)
                    mode_used = "extract-fallback"
                if wayback is not None:
                    wayback_url = wayback.save(item["link"])
                    if wayback_url:
                        provenance.set_wayback(conn, capture_id, wayback_url, "saved")
                        stats["wayback_submitted"] += 1
        else:
            text = adapter.fallback_text(item)
            mode_used = "feed-only"
        _store_item(conn, entry, item, package_id, text, mode_used,
                    capture_id, wayback_url)
        stats["new_items"] += 1
        logger.info("%s: [%d/%d] ingested %r (%s)", entry["id"], position,
                    len(pending), item["title"][:70], mode_used)
    logger.info("%s: done — %d new, %d articles fetched, %d wayback, %d errors",
                entry["id"], stats["new_items"], stats["articles_fetched"],
                stats["wayback_submitted"], stats["errors"])
    return stats


def _poll_isolated(client, wayback, conn, entry):
    """poll_source with per-source crash isolation."""
    try:
        return poll_source(client, wayback, conn, entry)
    except Exception as exc:  # noqa: BLE001
        logger.warning("%s: poll crashed: %r", entry["id"], exc)
        return {"id": entry["id"], "feed_status": "crash", "new_items": 0,
                "articles_fetched": 0, "wayback_submitted": 0, "errors": 1}


def run(client, wayback, conn, entries):
    """Poll every entry serially; manifest exported at the end."""
    results = [_poll_isolated(client, wayback, conn, entry) for entry in entries]
    provenance.export_manifest(conn)
    return results


def host_groups(entries):
    """Group entries by feed host. Politeness is a promise made to each
    server individually (GUIDE §4): sources sharing a host must share one
    worker, one client, and therefore one pacing clock."""
    groups = {}
    for entry in entries:
        groups.setdefault(
            urlsplit(source_url(entry) or "").netloc.lower(), []).append(entry)
    return groups


def run_concurrent(entries, max_workers=8, client_factory=None,
                   wayback_factory=None, conn_factory=None):
    """Poll host groups in parallel (GUIDE §4 concurrency-across-hosts rule).

    Each group runs in its own worker with its own AgencyClient/WaybackClient
    (own pacing clock and crawl-delay obedience — every host is treated as if
    it were the only source) and its own DB connection (SQLite WAL +
    busy_timeout). Daily budgets stay global: every client counts from the
    shared fetch log. The manifest is exported once, after all workers join,
    so one day's attempts land in one manifest regardless of worker count."""
    from concurrent.futures import ThreadPoolExecutor

    from . import db
    from .client import AgencyClient

    client_factory = client_factory or AgencyClient
    wayback_factory = wayback_factory or WaybackClient
    conn_factory = conn_factory or db.connect
    groups = host_groups(entries)
    if not groups:
        return []

    logger.info("concurrent ingest: %d sources across %d hosts (%d workers,"
                " per-host pacing per GUIDE §4)", len(entries), len(groups),
                min(max_workers, len(groups)))

    def poll_group(host_and_group):
        host, group = host_and_group
        logger.info("worker[%s]: starting — %d source(s): %s", host or "?",
                    len(group), ", ".join(e["id"] for e in group))
        conn = conn_factory()
        try:
            with client_factory() as client, wayback_factory() as wayback:
                out = [_poll_isolated(client, wayback, conn, e) for e in group]
        finally:
            conn.close()
        logger.info("worker[%s]: finished — %d new item(s), %d error(s)",
                    host or "?", sum(r["new_items"] for r in out),
                    sum(r["errors"] for r in out))
        return out

    # Open the main connection BEFORE spawning workers: the first connect to a
    # fresh database runs DDL and the delete->WAL journal switch, and a
    # concurrent WAL switch can return SQLITE_BUSY without consulting the busy
    # handler. Serializing first-connect makes workers join an already-WAL DB.
    conn = conn_factory()
    try:
        with ThreadPoolExecutor(max_workers=min(max_workers, len(groups))) as pool:
            results = [r for group in pool.map(poll_group, groups.items())
                       for r in group]
        provenance.export_manifest(conn)
    finally:
        conn.close()
    return results

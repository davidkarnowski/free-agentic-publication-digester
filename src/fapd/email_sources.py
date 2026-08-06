"""Email-distributed source ingestion (GUIDE §3 "Email-distributed sources").

The consent-maximal channel: the publisher transmits each item to a project
mailbox that subscribed through the publisher's own signup form. Nothing is
requested from an agency server here — we read our own inbox — so §4's
request budgets do not apply, though every processed message is logged and
lands in the daily manifest like any other attempt.

Rules enforced in code (GUIDE §3; docs/email-sources.md):

- **Registry-driven allowlist, applied before download.** Only the message
  *headers* are fetched first; a message whose From address maps to no
  registered `type: email` source has its body left on the server, never
  downloaded and never parsed. Personal mail in a shared mailbox is
  untouched by construction.
- **The raw RFC-5322 bytes are the capture** — content-addressed and
  hashed exactly like a web capture. Email is immutable once sent, so
  `change_kind` is expected to be `new`; the shared machinery is reused
  for the two hashes, the evidence store, and the manifest chain.
- **DKIM verified at ingest, with the verifying key archived** beside the
  capture. Selectors rotate, and an unarchived key makes the signature
  uncheckable later. A failing signature never drops official content —
  it is recorded as a fact and excluded from tamper-evidence claims.
- **The publisher's date is a claim; receipt is our observation.** Both
  stored, never conflated (§7 T3/T4).
- **A bulletin is not permission to crawl.** Item URLs are recorded as
  citations. Nothing here fetches them — several point at hosts that
  refuse our client, and receiving an email does not change that answer.

Parsing was built against captured bulletins (2026-07-29), not assumption.
What the evidence showed: GovDelivery bulletins are frequently *multi-item
digests* — one U.S. Attorneys message carried fourteen district releases —
so one message maps to many items. The plain-text part carries clean
canonical .gov URLs but runs titles and summaries together with no reliable
delimiter; the HTML part carries the exact per-item title as anchor text
and the canonical URL percent-encoded inside the platform's tracking
wrapper. Decoding that wrapper is static parsing of bytes the publisher
sent us — the same technique the USPS adapter uses, and emphatically not a
redirect fetch.
"""

import email
import email.policy
import email.utils
import imaplib
import json
import logging
import re
import time
from urllib.parse import unquote, urlsplit, urlunsplit

from . import config, provenance
from .sync import publication_date, utc_now_iso

logger = logging.getLogger("fapd.email_sources")

COLLECTION = "AGENCYPR"

# Platform link-tracking wrapper: https://links-N.govdelivery.com/CL0/<pct-encoded-url>/...
_TRACKING_RE = re.compile(r"^https?://links[^/]*\.govdelivery\.com/\w+/(.+?)(?:/\d+/|$)", re.IGNORECASE)
_ANCHOR_RE = re.compile(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
# Per-item date as rendered in the plain-text part: 07/29/2026 08:00 AM EDT
_ITEM_DATE_RE = re.compile(r"(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s*[AP]M\s+[A-Z]{2,4})")
# Boilerplate the platform adds around the publisher's own words.
_BOILERPLATE = re.compile(
    r"^(you are subscribed to|you have received this e-?mail|manage your subscriptions|"
    r"govdel header|update your subscriptions|this email was sent to|unsubscribe|"
    r"subscriber services:|questions\?|contact us at|view (this )?as a web ?page|"
    r"bookmark and share|share this|having trouble viewing|follow us|"
    r"stay connected|to view this|click here to)", re.IGNORECASE)
# Plain-text link markers: "Title [ https://... ]" — the URL is captured as the
# item's citation, so leaving it inline only adds noise to the stored prose.
_INLINE_LINK = re.compile(r"\s*\[\s*https?://[^\]]*\]")
# Subscription administrivia the platform sends on signup and preference
# changes. These are not publications and never become digest items; they are
# counted and disclosed, not silently dropped (GUIDE §2 no-silent-omission).
_ADMIN_SUBJECT = re.compile(
    r"^\s*(\(please confirm your email\)\s*)?"
    r"(welcome\b|subscription (change )?confirmation|new user confirmation|"
    r"your (email )?subscriptions? (have|has) changed|"
    r"your subscription update is confirmed|please confirm your email|"
    r"thank you for sign|you are now subscribed|stay connected with)", re.IGNORECASE)
# Chrome that is never a publication in its own right.
_GENERIC_TITLE = re.compile(
    r"^(contact us|home|privacy|unsubscribe|follow us|read more|click here|"
    r"learn more|subscribe|manage |view (this|in)|www\.|https?://|"
    r"visit |download |share |print)", re.IGNORECASE)
_SELF_SERVICE = re.compile(
    r"(govdelivery\.com|/subscriber/new|preferences=true|unsubscribe|"
    r"twitter\.com|facebook\.com|instagram\.com|linkedin\.com|youtube\.com)", re.IGNORECASE)


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def decode_tracking_url(href):
    """Recover the publisher's canonical URL from a platform tracking link.

    Static decode of bytes we were sent (the canonical URL is embedded,
    percent-encoded, in the wrapper path). Never a request: following the
    wrapper would be a fetch to the platform and then to a host that may
    refuse us. Returns the input unchanged when it is not a wrapper."""
    m = _TRACKING_RE.match(href or "")
    if not m:
        return href
    inner = unquote(m.group(1))
    return inner if inner.lower().startswith(("http://", "https://")) else href


def normalize_url(url):
    """Lowercase scheme/host, drop query and fragment, strip trailing slash."""
    parts = urlsplit(url or "")
    if not parts.netloc:
        return url or ""
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                       parts.path.rstrip("/") or "/", "", ""))


def _clean(text):
    return " ".join((text or "").split())


def _is_publisher_url(url):
    host = urlsplit(url or "").netloc.lower()
    return host.endswith((".gov", ".mil")) and not _SELF_SERVICE.search(url or "")


def _body_part(msg, subtype):
    part = msg.get_body(preferencelist=(subtype,))
    if part is None:
        return ""
    try:
        return part.get_content()
    except Exception:  # noqa: BLE001 — malformed MIME must not lose the message
        payload = part.get_payload(decode=True) or b""
        return payload.decode("utf-8", "replace")


def strip_boilerplate(text):
    """Drop platform chrome and everything after the footer rule, leaving the
    publisher's own words. Deterministic; no inference (GUIDE §3)."""
    lines = []
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if set(line) == {"_"} and len(line) > 20:
            break  # footer separator observed in captured bulletins
        if not line or _BOILERPLATE.match(line):
            continue
        lines.append(_INLINE_LINK.sub("", line).strip())
    return "\n".join(ln for ln in lines if ln)


def is_administrative(msg):
    """True for signup and preference-change mail from the platform itself.

    The publisher sends these to a subscriber, not to the public; they carry
    no official action. Recording them as publications would put subscription
    plumbing in a digest of government activity."""
    return bool(_ADMIN_SUBJECT.match(_clean(str(msg["subject"] or ""))))


def parse_bulletin(msg):
    """Return the items a bulletin carries: [{title, url, claimed_date, summary}].

    Two shapes exist, and telling them apart matters (learned from captured
    bulletins, 2026-07-29):

    * **Digest** — many syndicated releases in one message. The platform
      renders each as ``Title [ url ] MM/DD/YYYY HH:MM AM/PM TZ`` in the
      plain-text part. That date marker is the discriminator: it appears for
      syndicated items and never for a link inside an article's body.
    * **Single release** — one article, whose body may cite several other
      pages. Treating those inline citations and footer links as separate
      publications would fabricate items, so the whole cleaned body is one
      item instead.
    """
    html = _body_part(msg, "html")
    plain = _body_part(msg, "plain")
    subject = _clean(str(msg["subject"] or "")) or "(untitled bulletin)"
    msg_date = str(msg["date"] or "") or None

    seen, anchors = set(), []
    for href, inner in _ANCHOR_RE.findall(html):
        title = _clean(_TAG_RE.sub(" ", inner))
        url = decode_tracking_url(href)
        if not title or _GENERIC_TITLE.match(title) or not _is_publisher_url(url):
            continue
        key = normalize_url(url)
        if key in seen:
            continue
        seen.add(key)
        anchors.append({"title": title, "url": url, "claimed_date": msg_date,
                        "summary": ""})

    items = [a for a in anchors if _is_syndicated_item(plain, a["title"])]
    if items:
        _attach_summaries(items, plain, msg_date)
        return items

    return [{"title": subject,
             "url": _release_url(subject, anchors),
             "claimed_date": msg_date,
             "summary": _clean(strip_boilerplate(plain))}]


def _significant(text):
    return {w for w in re.findall(r"[a-z]{5,}", (text or "").lower())}


def _release_url(subject, anchors):
    """The citation for a single-release bulletin: an anchor that plainly
    refers to this release, or nothing.

    An article body cites other pages, and picking one of those would
    attribute the item to a document it is not (GUIDE §2 requires the
    citation to resolve to *this* item). No citation is honest; a wrong one
    is not — items without one carry the captured bulletin as their source
    of record instead."""
    subject_words = _significant(subject)
    if not subject_words:
        return None
    best, best_score = None, 0
    for anchor in anchors:
        score = len(subject_words & _significant(anchor["title"]))
        if score > best_score:
            best, best_score = anchor, score
    return best["url"] if best_score >= 2 else None


def _is_syndicated_item(plain, title):
    """True when the plain-text part renders this title as a syndicated item
    (``Title [ url ] date``) rather than as a link inside an article."""
    at = plain.find(title)
    if at == -1:
        return False
    window = plain[at + len(title):at + len(title) + 240]
    return bool(re.match(r"\s*\[[^\]]*\]", window)
                and _ITEM_DATE_RE.search(window[:220]))


def _attach_summaries(items, plain, msg_date):
    """Split the plain-text body on the titles the HTML gave us — the only
    reliable delimiter, since the text runs summaries and the next title
    together on one line."""
    if not plain:
        return
    positions = []
    for idx, item in enumerate(items):
        at = plain.find(item["title"])
        if at == -1:  # title not rendered identically in the text part
            continue
        positions.append((at, idx))
    positions.sort()
    for n, (at, idx) in enumerate(positions):
        end = positions[n + 1][0] if n + 1 < len(positions) else len(plain)
        chunk = plain[at + len(items[idx]["title"]):end]
        date_match = _ITEM_DATE_RE.search(chunk[:200])
        if date_match:
            items[idx]["claimed_date"] = _parse_item_date(date_match.group(1)) or msg_date
            chunk = chunk[date_match.end():]
        chunk = re.sub(r"^\s*\[[^\]]*\]", "", chunk.strip())  # the [ url ] marker
        items[idx]["summary"] = _clean(strip_boilerplate(chunk))


def _parse_item_date(raw):
    """'07/29/2026 08:00 AM EDT' -> ISO-8601. The publisher's claim, parsed —
    never trusted over our separately stored observation."""
    for fmt in ("%m/%d/%Y %I:%M %p", "%m/%d/%Y %I:%M%p"):
        try:
            stamp = time.strptime(" ".join(raw.split()[:3]), fmt)
        except ValueError:
            continue
        return time.strftime("%Y-%m-%dT%H:%M:%S", stamp)
    return None


# --------------------------------------------------------------------------
# DKIM (GUIDE §7 corroboration layer)
# --------------------------------------------------------------------------

def verify_dkim(raw):
    """Verify the signature and archive the key that verified it.

    Returns a record always — verification is evidence, and its absence or
    failure is evidence too. Honest limit (§7): this proves the publisher's
    distributor signed these bytes, not that the agency's own site said the
    same thing."""
    out = {"result": "none", "domain": None, "selector": None, "key_record": None}
    header = None
    m = re.search(rb"^DKIM-Signature:(.*?)(?=\r?\n[A-Za-z-]+:|\r?\n\r?\n)", raw,
                  re.DOTALL | re.MULTILINE | re.IGNORECASE)
    if m:
        header = " ".join(m.group(1).decode("utf-8", "replace").split())
        d = re.search(r"\bd=([^;]+)", header)
        s = re.search(r"\bs=([^;]+)", header)
        out["domain"] = d.group(1).strip() if d else None
        out["selector"] = s.group(1).strip() if s else None
    if header is None:
        return out
    try:
        import dkim
    except ImportError:
        out["result"] = "unavailable"
        return out
    try:
        out["result"] = "pass" if dkim.verify(raw) else "fail"
    except Exception as exc:  # noqa: BLE001 — a broken signature is a finding
        out["result"] = f"error:{type(exc).__name__}"
    if out["domain"] and out["selector"]:
        out["key_record"] = _fetch_dkim_key(out["selector"], out["domain"])
    return out


def _fetch_dkim_key(selector, domain):
    """The published public key, stored with the capture so the signature
    stays checkable after the selector rotates out of DNS."""
    try:
        from dkim.dnsplug import get_txt
        record = get_txt(f"{selector}._domainkey.{domain}".encode())
    except Exception as exc:  # noqa: BLE001 — best effort; absence is recorded
        logger.info("dkim: key lookup failed for %s._domainkey.%s: %r",
                    selector, domain, exc)
        return None
    if isinstance(record, bytes):
        record = record.decode("utf-8", "replace")
    return record


# --------------------------------------------------------------------------
# Mailbox access
# --------------------------------------------------------------------------

class MailboxClient:
    """Read-only IMAP access to the project mailbox.

    The folder is selected `readonly` and every fetch uses BODY.PEEK, so
    nothing on the server is modified or marked seen — our own processed
    watermark lives in the database, not in the mailbox's flags."""

    def __init__(self, host=None, user=None, password=None, folder="INBOX",
                 sleep=time.sleep):
        self.host = host or config.IMAP_HOST
        self.user = user or config.IMAP_USER
        self.password = password or config.IMAP_PASSWORD
        self.folder = folder
        self._sleep = sleep
        self._box = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.close()

    def connect(self):
        logger.info("mailbox: connecting to %s as %s (IMAPS, read-only)",
                    self.host, self.user)
        self._box = imaplib.IMAP4_SSL(self.host)
        self._box.login(self.user, self.password)
        self._box.select(self.folder, readonly=True)
        return self

    def close(self):
        if self._box is not None:
            try:
                self._box.logout()
            except Exception as exc:  # noqa: BLE001 — best-effort cleanup
                logger.debug("mailbox: logout %r", exc)
            self._box = None

    def uid_validity(self):
        _status, data = self._box.status(self.folder, "(UIDVALIDITY)")
        m = re.search(rb"UIDVALIDITY (\d+)", data[0] or b"")
        return int(m.group(1)) if m else None

    def uids_since(self, last_uid):
        _status, data = self._box.uid("SEARCH", None, f"UID {int(last_uid) + 1}:*")
        uids = [int(u) for u in (data[0] or b"").split()]
        return [u for u in uids if u > int(last_uid)]

    def headers(self, uid):
        """Envelope only — this is what the allowlist is judged on, before
        any message body leaves the server."""
        _status, data = self._box.uid(
            "FETCH", str(uid),
            "(BODY.PEEK[HEADER.FIELDS (FROM DATE SUBJECT MESSAGE-ID)])")
        if not data or not data[0]:
            return None
        return email.message_from_bytes(data[0][1], policy=email.policy.default)

    def raw(self, uid):
        _status, data = self._box.uid("FETCH", str(uid), "(BODY.PEEK[])")
        if not data or not data[0]:
            return None
        return data[0][1]


def _state(conn, mailbox):
    row = conn.execute("SELECT * FROM mailbox_state WHERE mailbox = ?",
                       (mailbox,)).fetchone()
    return (row["last_uid"], row["uid_validity"]) if row else (0, None)


def _save_state(conn, mailbox, last_uid, uid_validity):
    conn.execute(
        "INSERT INTO mailbox_state (mailbox, uid_validity, last_uid, last_polled_at)"
        " VALUES (?, ?, ?, ?) ON CONFLICT(mailbox) DO UPDATE SET"
        " uid_validity = excluded.uid_validity, last_uid = excluded.last_uid,"
        " last_polled_at = excluded.last_polled_at",
        (mailbox, uid_validity, last_uid, utc_now_iso()))
    conn.commit()


# --------------------------------------------------------------------------
# Storage
# --------------------------------------------------------------------------

class _MessageResponse:
    """Presents a raw message to provenance.capture() the way an HTTP
    response is presented, so email reuses the two-hash content-addressed
    evidence store and the manifest chain without duplicating any of it."""

    def __init__(self, raw):
        self.content = raw
        self.status_code = None
        self.headers = {"Content-Type": "message/rfc822"}
        self.url = None


def _sender_map(entries):
    allow = {}
    for entry in entries:
        sender = entry.get("sender")
        if not sender:
            continue
        for addr in ([sender] if isinstance(sender, str) else sender):
            allow[addr.strip().lower()] = entry
    return allow


def _from_address(msg):
    raw = str(msg["from"] or "")
    _name, addr = email.utils.parseaddr(raw)
    return (addr or raw).strip().lower()


def _package_id(source_id, stable_id):
    import hashlib
    digest = hashlib.sha256(stable_id.encode()).hexdigest()[:8]
    return f"PR-{source_id}-{digest}"


def _already_ingested(conn, package_id):
    return conn.execute("SELECT 1 FROM packages WHERE package_id = ?",
                        (package_id,)).fetchone() is not None


def _url_seen_elsewhere(conn, url):
    """First-recorded-wins across channels (docs/email-sources.md §5): an item
    already ingested from a web feed is not duplicated by its email copy."""
    if not url:
        return None
    row = conn.execute(
        "SELECT package_id FROM extracted_texts WHERE collection = ?"
        " AND metadata LIKE ? LIMIT 1",
        (COLLECTION, f'%"url": "{url}"%')).fetchone()
    return row["package_id"] if row else None


def _store_item(conn, entry, item, package_id, text, mode, capture_id, dkim):
    now = utc_now_iso()
    # Publication day in Washington (GUIDE §3, amended 2026-07-30).
    issued = publication_date()
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " title, package_link, first_seen_at, fetch_status, fetched_at, digest_day)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, 'fetched', ?, ?)",
        # digest_day = issued: the email class files under the mailbox
        # publication day (GUIDE §3 email class; cover policy).
        (package_id, COLLECTION, issued, now, item["title"], item.get("url"),
         now, now, issued))
    metadata = json.dumps({
        "source_id": entry["id"],
        "url": item.get("url"),
        "claimed_published_at": item.get("claimed_date"),
        "mode": mode,
        "channel": "email",
        "capture_id": capture_id,
        "dkim": dkim,
        "wayback_url": None,
    }, sort_keys=True)
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, '', ?, 'PRESS', ?, ?, ?, ?, ?, ?, 1)",
        (package_id, COLLECTION, item["title"], entry["name"], metadata,
         text, len(text), now))
    conn.commit()


# --------------------------------------------------------------------------
# Poll loop
# --------------------------------------------------------------------------

def process_message(conn, entry, raw, dkim_verifier=verify_dkim):
    """Capture one bulletin and store the items it carries. Returns stats."""
    stats = {"items": 0, "duplicates": 0, "administrative": 0}
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    message_id = _clean(str(msg["message-id"] or "")) or provenance.sha256_hex(raw)
    if is_administrative(msg):
        stats["administrative"] = 1
        logger.info("%s: subscription administrivia, not ingested (%s)",
                    entry["id"], _clean(str(msg["subject"] or ""))[:60])
        return stats

    dkim = dkim_verifier(raw)
    doc_id = provenance.get_or_create_document(
        conn, entry["id"], message_id, item_url(msg) or message_id,
        title=_clean(str(msg["subject"] or "")),
        claimed_published_at=str(msg["date"] or "") or None)
    capture_id, _kind = provenance.capture(
        conn, doc_id, message_id, _MessageResponse(raw))
    if dkim.get("result") != "pass":
        logger.info("%s: dkim %s for %s", entry["id"], dkim.get("result"), message_id)

    for item in parse_bulletin(msg):
        url = normalize_url(item.get("url") or "")
        stable_id = url or f"{message_id}#{stats['items']}"
        package_id = _package_id(entry["id"], stable_id)
        if _already_ingested(conn, package_id):
            continue
        other = _url_seen_elsewhere(conn, item.get("url"))
        if other:
            stats["duplicates"] += 1
            logger.info("%s: already ingested via another channel (%s) — skipped",
                        entry["id"], other)
            continue
        summary = item.get("summary") or ""
        mode = "email-full" if len(summary) >= 80 else "email-teaser"
        text = f"{item['title']} — {summary}".strip(" —") if summary else item["title"]
        _store_item(conn, entry, item, package_id, text, mode, capture_id, dkim)
        stats["items"] += 1
    return stats


def item_url(msg):
    """First publisher URL in a message, used as the document's url field."""
    html = _body_part(msg, "html")
    for href, _text in _ANCHOR_RE.findall(html):
        url = decode_tracking_url(href)
        if _is_publisher_url(url):
            return url
    return None


def poll_mailbox(client, conn, entries, *, limit=None, dkim_verifier=verify_dkim):
    """Poll the project mailbox once; returns per-source stats.

    Only registered senders are downloaded: the allowlist is applied to
    headers, so unregistered mail is never fetched, never parsed, and never
    stored (docs/email-sources.md §2)."""
    allow = _sender_map(entries)
    if not allow:
        logger.info("mailbox: no registered email sources — nothing to poll")
        return []

    mailbox = client.folder
    last_uid, saved_validity = _state(conn, mailbox)
    validity = client.uid_validity()
    if saved_validity is not None and validity != saved_validity:
        logger.warning("mailbox: UIDVALIDITY changed (%s -> %s) — rescanning from 0",
                       saved_validity, validity)
        last_uid = 0

    uids = client.uids_since(last_uid)
    if limit:
        uids = uids[:limit]
    logger.info("mailbox: %d message(s) after UID %d; %d registered sender(s)",
                len(uids), last_uid, len(allow))

    per_source, ignored, highest = {}, 0, last_uid
    for uid in uids:
        head = client.headers(uid)
        if head is None:
            continue
        entry = allow.get(_from_address(head))
        if entry is None:
            ignored += 1
            highest = max(highest, uid)
            continue
        raw = client.raw(uid)
        if raw is None:
            continue
        try:
            result = process_message(conn, entry, raw, dkim_verifier=dkim_verifier)
        except Exception as exc:  # noqa: BLE001 — one bad bulletin must not
            # cost the rest of the poll; the failure is recorded, not hidden.
            logger.warning("%s: message UID %s failed: %r", entry["id"], uid, exc)
            stats = per_source.setdefault(entry["id"], _blank(entry["id"]))
            stats["errors"] += 1
            highest = max(highest, uid)
            continue
        stats = per_source.setdefault(entry["id"], _blank(entry["id"]))
        stats["messages"] += 1
        stats["items"] += result["items"]
        stats["duplicates"] += result["duplicates"]
        stats["administrative"] += result["administrative"]
        highest = max(highest, uid)
        logger.info("%s: UID %s -> %d item(s)", entry["id"], uid, result["items"])

    _save_state(conn, mailbox, highest, validity)
    provenance.export_manifest(conn)
    results = sorted(per_source.values(), key=lambda s: s["id"])
    logger.info("mailbox: %d ignored (sender not registered; body never fetched)",
                ignored)
    return results


def _blank(source_id):
    return {"id": source_id, "messages": 0, "items": 0, "duplicates": 0,
            "administrative": 0, "errors": 0}

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
- **The only mailbox write is post-ingest filing, and it is opt-in**
  (`config.IMAP_FILE_TO`; docs/email-sources.md §3a). Unset, the mailbox is
  never modified. Set, a registered-sender message the poll has already
  handled — after the watermark is committed — is marked read and moved out
  of INBOX into ``<prefix>/Ingested`` or ``<prefix>/Admin``. Never a delete,
  never an expunge, never unregistered mail, never a message whose
  processing failed (it stays in INBOX where the operator will see it).
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

# Subfolders (Gmail: nested labels) under the IMAP_FILE_TO prefix.
FILED_INGESTED = "Ingested"
FILED_ADMIN = "Admin"
# UIDs per STORE/MOVE command — keeps command lines well under server limits
# when the one-time sweep files thousands of messages.
_FILE_CHUNK = 200


def _quote_mailbox(name):
    return '"' + name.replace("\\", "\\\\").replace('"', '\\"') + '"'


class MailboxClient:
    """IMAP access to the project mailbox — read-only unless filing is on.

    The folder is selected `readonly` and every fetch uses BODY.PEEK, so
    reading never modifies the server or marks anything seen — our own
    processed watermark lives in the database, not in the mailbox's flags.
    `file_messages` is the one write path, used only when `file_to` is set
    (default `config.IMAP_FILE_TO`); it reselects read-write for exactly
    one mark-read-and-MOVE and drops straight back to read-only."""

    def __init__(self, host=None, user=None, password=None, folder="INBOX",
                 sleep=time.sleep, file_to=None):
        self.host = host or config.IMAP_HOST
        self.user = user or config.IMAP_USER
        self.password = password or config.IMAP_PASSWORD
        self.folder = folder
        self.file_to = config.IMAP_FILE_TO if file_to is None else file_to
        self._sleep = sleep
        self._box = None
        self._known_folders = set()

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
            "(BODY.PEEK[HEADER.FIELDS (FROM DATE SUBJECT MESSAGE-ID"
            " LIST-UNSUBSCRIBE LIST-ID)])")
        if not data or not data[0]:
            return None
        return email.message_from_bytes(data[0][1], policy=email.policy.default)

    def raw(self, uid):
        _status, data = self._box.uid("FETCH", str(uid), "(BODY.PEEK[])")
        if not data or not data[0]:
            return None
        return data[0][1]

    def junk_folder(self):
        """The server's junk folder by its RFC 6154 \\Junk attribute (Gmail:
        "[Gmail]/Spam"), or None. Found by attribute, never by name."""
        _status, data = self._box.list()
        for line in data or []:
            if isinstance(line, bytes) and b"\\Junk" in line.split(b")")[0]:
                m = re.search(rb'"([^"]+)"\s*$', line) or re.search(rb"(\S+)\s*$", line)
                if m:
                    return m.group(1).decode()
        return None

    def use_folder(self, folder):
        """Switch the polled folder (read-only select)."""
        self._box.select(_quote_mailbox(folder), readonly=True)
        self.folder = folder

    def all_uids(self):
        _status, data = self._box.uid("SEARCH", None, "ALL")
        return [int(u) for u in (data[0] or b"").split()]

    def headers_many(self, uids, chunk=500):
        """{uid: From/Subject headers} for many messages in few round trips —
        the one-time sweep's read. Envelope only; no body leaves the server."""
        out, uids = {}, sorted(int(u) for u in uids)
        for at in range(0, len(uids), chunk):
            uid_set = ",".join(str(u) for u in uids[at:at + chunk])
            _status, data = self._box.uid(
                "FETCH", uid_set,
                "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT LIST-UNSUBSCRIBE LIST-ID)])")
            for part in data or []:
                if not isinstance(part, tuple):
                    continue
                m = re.search(rb"UID (\d+)", part[0])
                if m:
                    out[int(m.group(1))] = email.message_from_bytes(
                        part[1], policy=email.policy.default)
        return out

    def supports_move(self):
        _status, data = self._box.capability()
        return b"MOVE" in (data[0] or b"").upper().split()

    def _ensure_folder(self, name):
        if name in self._known_folders:
            return
        _status, data = self._box.list('""', _quote_mailbox(name))
        if not data or data[0] is None:
            status, data = self._box.create(_quote_mailbox(name))
            if status != "OK":
                raise imaplib.IMAP4.error(f"CREATE {name}: {data!r}")
            logger.info("mailbox: created folder %s", name)
        self._known_folders.add(name)

    def file_messages(self, uids, dest):
        """Mark read and MOVE (RFC 6851) out of the polled folder. Returns
        the number filed.

        MOVE only: without it the answer is to file nothing, never the
        COPY + \\Deleted + EXPUNGE emulation — on Gmail that path can send a
        message to Trash depending on account settings."""
        uids = sorted({int(u) for u in uids})
        if not uids:
            return 0
        if not self.supports_move():
            logger.warning("mailbox: server lacks MOVE — %d message(s) left in %s",
                           len(uids), self.folder)
            return 0
        self._ensure_folder(dest)
        self._box.select(self.folder, readonly=False)
        filed = 0
        try:
            for at in range(0, len(uids), _FILE_CHUNK):
                uid_set = ",".join(str(u) for u in uids[at:at + _FILE_CHUNK])
                status, data = self._box.uid("STORE", uid_set, "+FLAGS.SILENT",
                                             r"(\Seen)")
                if status != "OK":
                    raise imaplib.IMAP4.error(f"STORE: {data!r}")
                status, data = self._box.uid("MOVE", uid_set, _quote_mailbox(dest))
                if status != "OK":
                    raise imaplib.IMAP4.error(f"MOVE: {data!r}")
                filed += len(uids[at:at + _FILE_CHUNK])
        finally:
            self._box.select(self.folder, readonly=True)
        return filed


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
    stats = {"items": 0, "duplicates": 0, "administrative": 0, "no_url": 0,
             "dkim": None}
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    message_id = _clean(str(msg["message-id"] or "")) or provenance.sha256_hex(raw)
    if is_administrative(msg):
        stats["administrative"] = 1
        logger.info("%s: subscription administrivia, not ingested (%s)",
                    entry["id"], _clean(str(msg["subject"] or ""))[:60])
        return stats

    dkim = dkim_verifier(raw)
    stats["dkim"] = dkim.get("result")
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
        if not item.get("url"):
            stats["no_url"] += 1
    return stats


def item_url(msg):
    """First publisher URL in a message, used as the document's url field."""
    html = _body_part(msg, "html")
    for href, _text in _ANCHOR_RE.findall(html):
        url = decode_tracking_url(href)
        if _is_publisher_url(url):
            return url
    return None


# Government list mail (docs/schema.md `mailbox_messages`): a government
# sender domain AND a list header. The list header is what keeps a person
# writing from a .gov address out of the log.
_GOV_SENDER_DOMAIN = re.compile(r"(\.gov|\.mil|(^|\.)govdelivery\.com)$", re.IGNORECASE)


def is_government_list(head, sender):
    domain = (sender or "").rpartition("@")[2]
    return bool(_GOV_SENDER_DOMAIN.search(domain)
                and (head["list-unsubscribe"] or head["list-id"]))


def _record(conn, mailbox, validity, uid, outcome, *, source_id=None,
            sender=None, result=None, dkim=None):
    """One mailbox_messages row. Committed with the watermark."""
    result = result or {}
    conn.execute(
        "INSERT OR REPLACE INTO mailbox_messages (mailbox, uid_validity, uid,"
        " observed_at, source_id, sender, outcome, items, duplicates,"
        " no_url_items, dkim) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (mailbox, validity or 0, uid, utc_now_iso(), source_id, sender, outcome,
         result.get("items", 0), result.get("duplicates", 0),
         result.get("no_url", 0), dkim if dkim is not None else result.get("dkim")))


def _outcome(result):
    if result["administrative"]:
        return "administrative"
    if result["items"]:
        return "ingested"
    return "duplicate" if result["duplicates"] else "empty"


def poll_mailbox(client, conn, entries, *, limit=None, dkim_verifier=verify_dkim):
    """Poll the project mailbox once; returns per-source stats.

    Only registered senders are downloaded: the allowlist is applied to
    headers, so unregistered mail is never fetched, never parsed, and never
    stored (docs/email-sources.md §2). The junk folder is polled after the
    polled folder when the server has one and `config.IMAP_POLL_JUNK` is on
    — under a stricter rule, since a From header is trivially forged."""
    allow = _sender_map(entries)
    if not allow:
        logger.info("mailbox: no registered email sources — nothing to poll")
        return []
    per_source = _poll_folder(client, conn, allow, limit=limit,
                              dkim_verifier=dkim_verifier)
    junk = (client.junk_folder()
            if config.IMAP_POLL_JUNK and hasattr(client, "junk_folder") else None)
    if junk and junk != client.folder:
        home = client.folder
        client.use_folder(junk)
        try:
            extra = _poll_folder(client, conn, allow, limit=limit,
                                 dkim_verifier=dkim_verifier, junk=True)
        finally:
            client.use_folder(home)
        for source_id, stats in extra.items():
            into = per_source.setdefault(source_id, _blank(source_id))
            for key, value in stats.items():
                if key != "id":
                    into[key] += value
    return sorted(per_source.values(), key=lambda s: s["id"])


def dkim_aligned(dkim, from_addr):
    """True when the signature verified AND the signing domain belongs to
    the sender's organizational domain (DMARC relaxed alignment). The
    junk-folder gate: a spoofed From address cannot produce it."""
    def org(domain):
        return ".".join((domain or "").lower().rstrip(".").split(".")[-2:])
    sender_domain = (from_addr or "").rpartition("@")[2]
    return (dkim.get("result") == "pass" and bool(dkim.get("domain"))
            and org(dkim["domain"]) == org(sender_domain))


def _poll_folder(client, conn, allow, *, limit, dkim_verifier, junk=False):
    mailbox = client.folder
    last_uid, saved_validity = _state(conn, mailbox)
    validity = client.uid_validity()
    if junk and (saved_validity is None or validity != saved_validity):
        # A junk folder is read from the present forward: its backlog is
        # not a publication queue, and it is never backfilled.
        start = max(client.uids_since(0), default=0)
        _save_state(conn, mailbox, start, validity)
        logger.info("mailbox: %s watermark set at UID %d; earlier mail not ingested",
                    mailbox, start)
        return {}
    if saved_validity is not None and validity != saved_validity:
        logger.warning("mailbox: UIDVALIDITY changed (%s -> %s) — rescanning from 0",
                       saved_validity, validity)
        last_uid = 0

    uids = client.uids_since(last_uid)
    if limit:
        uids = uids[:limit]
    logger.info("mailbox: %s: %d message(s) after UID %d; %d registered sender(s)",
                mailbox, len(uids), last_uid, len(allow))

    per_source, ignored, highest = {}, 0, last_uid
    to_file = {FILED_INGESTED: [], FILED_ADMIN: []}
    for uid in uids:
        head = client.headers(uid)
        if head is None:
            continue
        sender = _from_address(head)
        entry = allow.get(sender)
        if entry is None:
            ignored += 1
            highest = max(highest, uid)
            if is_government_list(head, sender):
                _record(conn, mailbox, validity, uid, "unregistered", sender=sender)
            continue
        raw = client.raw(uid)
        if raw is None:
            continue
        verifier = dkim_verifier
        if junk:
            dkim = dkim_verifier(raw)
            if not dkim_aligned(dkim, sender):
                # Left where the provider put it; not stored, not filed.
                logger.info("%s: junk-folder UID %s refused (dkim %s, d=%s)",
                            entry["id"], uid, dkim.get("result"), dkim.get("domain"))
                per_source.setdefault(entry["id"], _blank(entry["id"]))["refused"] += 1
                _record(conn, mailbox, validity, uid, "refused", source_id=entry["id"],
                        sender=sender, dkim=dkim.get("result"))
                highest = max(highest, uid)
                continue
            verifier = lambda _raw, _dkim=dkim: _dkim  # verified once above
        try:
            result = process_message(conn, entry, raw, dkim_verifier=verifier)
        except Exception as exc:  # noqa: BLE001 — one bad bulletin must not
            # cost the rest of the poll; the failure is recorded, not hidden.
            logger.warning("%s: message UID %s failed: %r", entry["id"], uid, exc)
            stats = per_source.setdefault(entry["id"], _blank(entry["id"]))
            stats["errors"] += 1
            _record(conn, mailbox, validity, uid, "error", source_id=entry["id"],
                    sender=sender)
            highest = max(highest, uid)
            continue
        stats = per_source.setdefault(entry["id"], _blank(entry["id"]))
        stats["messages"] += 1
        stats["items"] += result["items"]
        stats["duplicates"] += result["duplicates"]
        stats["administrative"] += result["administrative"]
        highest = max(highest, uid)
        _record(conn, mailbox, validity, uid, _outcome(result), source_id=entry["id"],
                sender=sender, result=result)
        sub = FILED_ADMIN if result["administrative"] else FILED_INGESTED
        to_file[sub].append((uid, entry["id"]))
        logger.info("%s: UID %s -> %d item(s)", entry["id"], uid, result["items"])

    _save_state(conn, mailbox, highest, validity)
    provenance.export_manifest(conn)
    # Filing runs only after the watermark and captures are committed: the
    # evidence is durable before the mailbox is touched.
    _file_handled(client, to_file, per_source)
    logger.info("mailbox: %s: %d ignored (sender not registered; body never fetched)",
                mailbox, ignored)
    return per_source


def filing_folder(head, allow):
    """Where a message is filed, judged on headers alone: the registry
    allowlist on the From address, the administrivia pattern on Subject.
    None means not ours — it is never touched. Deterministic; no body, no
    model."""
    entry = allow.get(_from_address(head))
    if entry is None:
        return None, None
    return (FILED_ADMIN if is_administrative(head) else FILED_INGESTED), entry


def sweep_plan(client, entries, through_uid):
    """The one-time backlog sweep (scripts/file_mailbox.py): which messages
    at or below `through_uid` would be filed where. Returns
    ({subfolder: [(uid, source_id)]}, ignored_count).

    The ceiling is the safety rule: the poll reads INBOX only, so filing a
    message it has not reached yet would hide it from ingestion."""
    allow = _sender_map(entries)
    uids = [u for u in client.all_uids() if u <= int(through_uid)]
    plan, ignored = {FILED_INGESTED: [], FILED_ADMIN: []}, 0
    for uid, head in sorted(client.headers_many(uids).items()):
        sub, entry = filing_folder(head, allow)
        if sub is None:
            ignored += 1
            continue
        plan[sub].append((uid, entry["id"]))
    return plan, ignored


def unregistered_government_lists(client, entries, folders):
    """{sender: {"messages", "name", "subject", "account", "folders"}} for
    government LIST mail from senders the registry does not know, across
    `folders` — the operator's review of what to register next. Headers
    only; printed to the operator's terminal, never stored or published."""
    allow = _sender_map(entries)
    home, found = client.folder, {}
    try:
        for folder in folders:
            client.use_folder(folder)
            for _uid, head in sorted(client.headers_many(client.all_uids()).items()):
                sender = _from_address(head)
                if sender in allow or not is_government_list(head, sender):
                    continue
                rec = found.setdefault(sender, {
                    "messages": 0, "name": email.utils.parseaddr(
                        str(head["from"] or ""))[0],
                    "subject": "", "account": "", "folders": set()})
                rec["messages"] += 1
                rec["folders"].add(folder)
                if not rec["subject"] and not is_administrative(head):
                    rec["subject"] = _clean(str(head["subject"] or ""))[:70]
                m = re.search(r"accounts/([A-Za-z0-9_]+)",
                              str(head["list-unsubscribe"] or ""))
                if m and not rec["account"]:
                    rec["account"] = m.group(1)
    finally:
        client.use_folder(home)
    return found


def _file_handled(client, to_file, per_source):
    """Mark read and move the messages this poll handled. A filing failure
    is logged and never fails the poll — the watermark has already passed
    those messages, so they simply stay in INBOX (scripts/file_mailbox.py
    sweeps them later)."""
    prefix = getattr(client, "file_to", "")
    if not prefix:
        return
    for sub, pairs in to_file.items():
        if not pairs:
            continue
        dest = f"{prefix}/{sub}"
        try:
            filed = client.file_messages([uid for uid, _ in pairs], dest)
        except Exception as exc:  # noqa: BLE001 — filing is housekeeping
            logger.warning("mailbox: filing %d message(s) to %s failed: %r",
                           len(pairs), dest, exc)
            continue
        if filed == len(pairs):
            for _uid, source_id in pairs:
                per_source[source_id]["filed"] += 1
        logger.info("mailbox: filed %d message(s) to %s", filed, dest)


def _blank(source_id):
    return {"id": source_id, "messages": 0, "items": 0, "duplicates": 0,
            "administrative": 0, "errors": 0, "filed": 0, "refused": 0}

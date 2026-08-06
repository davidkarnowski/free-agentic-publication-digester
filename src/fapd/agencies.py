"""Agency newsroom ingestion (S2 pilot; GUIDE §3 agency newsrooms).

RSS-first, through the robots-enforcing AgencyClient with conditional
GETs, every response captured into the provenance layer, every new
capture submitted to the Wayback Machine (its own budget; failures never
block). Items enter the standard packages/extracted model under the
AGENCYPR pseudo-collection so the digest, coverage accounting, and site
machinery apply unchanged. Zero LLM calls in the pilot: the digest lists
attributed titles (GUIDE §2 attributed-speech rule).
"""

import datetime as dt
import hashlib
import json
import logging
import re
import types
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import parse_qs, urljoin, urlsplit, urlunsplit

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

    0. request_params() — the query the index URL is fetched with.
    1. items(body, content_type) — index/feed bytes -> the item list.
    2. stable_id(item)  — what makes two sightings the same document.
    3. wants_article()  — fetch the article page, or feed metadata only.
    4. extract_text(body, content_type, item) — served bytes -> plain text.
    5. fallback_text(item) — what to store when no article is available.

    plus three class attributes naming what the source publishes:
    COLLECTION (default "AGENCYPR"), DOC_TYPE (default "PRESS") and
    DATED_BY_PUBLISHER (default False). They live on the adapter, not on
    the registry entry, so an entry can never declare a collection its
    adapter does not actually produce — a roll-call vote misfiled as
    AGENCYPR would enter the agency dating rule, the agency accounting,
    and the executive-branch tagging, all of which GUIDE §3 forbids for
    legislative record.

    DATED_BY_PUBLISHER answers "which day does this document belong to".
    The default is the agency-newsroom answer (GUIDE §3 dating rule): the
    federal publication day we observed it, because a newsroom publishes
    same-day and a claimed date is the agency's assertion about mutable
    web content. True is the govinfo answer, used where the publisher
    prints an authoritative date and then publishes the record LATER:
    Congress.gov posts a day's bill actions the following morning, so
    dating those by observation would file every action under a day on
    which nothing happened, and the section would be permanently empty.
    Setting it True means a digest for an earlier day gains items when
    re-rendered — exactly what CREC, FR and USCOURTS already do, and it
    is disclosed the same way.

    STRUCTURED DETAIL CHANNEL. An adapter may put a JSON-serializable dict
    in item["extra"]; the loop stores it under metadata["details"], nested
    so it can never collide with a loop-owned key (collect.py keys web-vs-
    email on the ABSENCE of `channel`). items() should populate whatever
    the index alone establishes; extract_text may replace it with a
    richer dict built from the article bytes — it runs before _store_item,
    so a successful extraction's details are what get stored. Report
    renderers read those fields instead of re-parsing stored prose
    (GUIDE §6 rule 2: what SQL can answer is not a parsing problem).

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

    COLLECTION = "AGENCYPR"
    DOC_TYPE = "PRESS"
    DATED_BY_PUBLISHER = False

    def doc_type_for(self, item):
        """This item's document type. Defaults to the class constant.

        The seam exists (added 2026-08-06) for sources whose publisher
        declares a per-item class the digest renders on — whitehouse.gov
        tags each presidential action "Executive Orders", "Proclamations"
        or "Presidential Memoranda". A per-ITEM answer is the adapter's
        to give for the same reason COLLECTION and DOC_TYPE are: the
        registry describes a source, the adapter reads its documents."""
        return self.DOC_TYPE

    def request_params(self):
        """Query parameters for the index/feed fetch; empty by default.

        Feeds take none. An API-backed source returns its page size, sort
        order and credential here — and ONLY here: HttpClient redacts
        `api_key` from what the fetch log records of a request's
        parameters (GUIDE §4), while a key concatenated into the URL
        string would be logged verbatim. Must not raise for reasons the
        loop can handle; a missing key raises loudly by design
        (code-standards §2 r9) and per-source crash isolation records it."""
        return {}

    def __init__(self, entry=None):
        """The registry entry being polled, or None.

        Added 2026-07-31 for HtmlIndexAdapter, which needs two things no
        other hook supplies: the index URL (a listing page's hrefs are
        relative, and items() is handed bytes, not a URL) and the entry's
        optional `index_item_path` hint. adapter_for passes it; direct
        construction without an entry stays valid, so every existing
        adapter and test is unaffected."""
        self.entry = entry or {}

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


_MONTH_ABBR = {abbr: n for n, abbr in enumerate(
    ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), start=1)}


def _xml_text(element, tag):
    """Whitespace-normalized child text, or "" — the Senate's XML pads
    element text with newlines and spaces ("On the Resolution\\n    ")."""
    return " ".join((element.findtext(tag) or "").split())


class SenateVotesAdapter(SourceAdapter):
    """Senate roll-call votes (GUIDE §3 "Recorded votes"; evidence 2026-07-31).

    Two documents, both officially published XML, both verified live
    through this client on 2026-07-31:

    - the session menu (``vote_menu_<congress>_<session>.xml``, 123 KB):
      217 <vote> elements — the WHOLE session — each carrying
      vote_number, vote_date, issue, question, result and title. Its
      <vote_tally> element is present and EMPTY on every one of the 217;
      the tally exists only in the per-vote file.
    - the per-vote record
      (``roll_call_votes/vote<congress><session>/vote_<c>_<s>_<NNNNN>.xml``),
      carrying the question text, the result with tally, and all 100
      member positions.

    AN INDEX IS NOT A FEED, and this is the source that proves it: an
    unbounded items() would return 217 votes and buy 217 article fetches
    on first activation, of which the §3 dating rule would list at most a
    day's worth. Bounded to config.INDEX_LOOKBACK_DAYS the same menu
    yielded 8 votes on 2026-07-31 — one index fetch plus eight.

    DATES MUST BE PARSEABLE. The menu writes "30-Jul" with NO YEAR;
    report._claimed_day reads RFC 822 or an ISO-8601 prefix and nothing
    else, so a raw menu date would silently date every vote by
    observation instead of by when the Senate actually voted. The year
    comes from the menu's own <congress_year>, and the month abbreviation
    is mapped from a fixed table rather than strptime("%b"), which reads
    the process's LC_TIME locale and would make the render
    machine-dependent. A vote whose date cannot be built is skipped
    rather than dated by observation: claiming the Senate voted today
    when the record does not say so is worse than not listing it, and the
    count is logged.
    """

    COLLECTION = "VOTES"
    DOC_TYPE = "ROLLCALL"
    CHAMBER = "United States Senate"
    FORMAT = "senate-vote-menu"

    VOTE_URL = ("https://www.senate.gov/legislative/LIS/roll_call_votes/"
                "vote{congress}{session}/vote_{congress}_{session}_{number}.xml")

    # Roster ordering in the extracted text: the positions the Senate
    # itself tallies first, then anything else alphabetically.
    _POSITION_ORDER = ("Yea", "Nay", "Present", "Not Voting")

    def items(self, body, content_type):
        try:
            return self._parse_menu(body)
        except Exception as exc:  # noqa: BLE001 — items() must not raise
            logger.warning("senate votes: vote menu unparsable: %r", exc)
            return None, []

    def _parse_menu(self, body):
        root = ET.fromstring(body)
        if root.tag != "vote_summary":
            logger.warning("senate votes: unexpected menu root %r", root.tag)
            return None, []
        congress = _xml_text(root, "congress")
        session = _xml_text(root, "session")
        year = _xml_text(root, "congress_year")
        if not (congress and session):
            logger.warning("senate votes: menu names no congress/session")
            return None, []

        today = dt.date.fromisoformat(publication_date())
        oldest = today - dt.timedelta(days=config.INDEX_LOOKBACK_DAYS)
        out, undated, out_of_window = [], 0, 0
        for vote in root.iter("vote"):
            number = _xml_text(vote, "vote_number")
            if not number:
                continue
            day = self._vote_day(_xml_text(vote, "vote_date"), year)
            if day is None:
                undated += 1
                continue
            if not oldest <= day <= today:
                out_of_window += 1
                continue
            out.append(self._menu_item(congress, session, number, day, vote))
        out.sort(key=lambda item: item["extra"]["vote_number"])
        logger.info("senate votes: menu lists %d vote(s) in window, %d outside"
                    " the %d-day lookback%s", len(out), out_of_window,
                    config.INDEX_LOOKBACK_DAYS,
                    f", {undated} with no readable date (skipped)" if undated else "")
        return self.FORMAT, out

    def _menu_item(self, congress, session, number, day, vote):
        padded = number.zfill(5)
        issue = _xml_text(vote, "issue")
        question = _xml_text(vote, "question")
        title = _xml_text(vote, "title")
        subject = " — ".join(p for p in (issue, question) if p)
        return {
            "title": title or subject or f"Senate roll call vote {padded}",
            "link": self.VOTE_URL.format(congress=congress, session=session,
                                         number=padded),
            "guid": f"senate-vote-{congress}-{session}-{padded}",
            # ISO-8601 so report._claimed_day can read it (see class docstring).
            "claimed_date": day.isoformat(),
            "description": subject,
            "description_chars": len(subject),
            "extra": {
                "chamber": self.CHAMBER,
                "congress": congress,
                "session": session,
                "vote_number": padded,
                "issue": issue,
                "question": question,
                "result": _xml_text(vote, "result"),
            },
        }

    @staticmethod
    def _vote_day(raw, year):
        """'30-Jul' + congress_year '2026' -> date(2026, 7, 30); None if
        the menu's own fields cannot produce a real calendar day."""
        parts = (raw or "").split("-")
        if len(parts) != 2 or not year.isdigit():
            return None
        month = _MONTH_ABBR.get(parts[1][:3].title())
        if month is None or not parts[0].isdigit():
            return None
        try:
            return dt.date(int(year), month, int(parts[0]))
        except ValueError:
            return None

    def extract_text(self, body, content_type, item):
        """Per-vote XML -> the readable record: question, measure, result,
        tally, and every member's position. May raise (the loop degrades
        the item to menu metadata with mode "extract-fallback" and the raw
        capture survives either way); never returns blank."""
        root = ET.fromstring(body)
        if root.tag != "roll_call_vote":
            raise ValueError(f"unexpected vote root element {root.tag!r}")
        details = dict(item.get("extra") or {})
        counts = self._counts(root)
        positions = self._positions(root)
        details.update({
            "question": _xml_text(root, "question") or details.get("question", ""),
            "result": _xml_text(root, "vote_result_text")
                      or _xml_text(root, "vote_result") or details.get("result", ""),
            "measure": _xml_text(root, "vote_title") or details.get("issue", ""),
            "recorded_at": _xml_text(root, "vote_date"),
            "tally": counts,
        })
        text = self._prose(root, details, counts, positions)
        if not text.strip():  # defensive: the loop must never store blank
            return self.fallback_text(item)
        item["extra"] = details  # assigned only once the whole parse succeeded
        return text

    @staticmethod
    def _counts(root):
        """The Senate's published <count>. An absent position is written as
        an empty element (<present/>) rather than a zero, so blank reads as
        zero; _prose corroborates that against the member roster and
        discloses any disagreement rather than picking a winner silently."""
        count = root.find("count")
        out = {}
        for tag, label in (("yeas", "Yea"), ("nays", "Nay"),
                           ("present", "Present"), ("absent", "Not Voting")):
            raw = _xml_text(count, tag) if count is not None else ""
            out[label] = int(raw) if raw.isdigit() else 0
        return out

    def _positions(self, root):
        """{position: [member label, ...]} from the per-member records."""
        groups = {}
        for member in root.iter("member"):
            position = _xml_text(member, "vote_cast") or "Position not stated"
            label = _xml_text(member, "member_full") or _xml_text(member, "last_name")
            if label:
                groups.setdefault(position, []).append(label)
        for names in groups.values():
            names.sort(key=str.lower)
        return groups

    def _prose(self, root, details, counts, positions):
        congress = details.get("congress") or _xml_text(root, "congress")
        session = details.get("session") or _xml_text(root, "session")
        number = details.get("vote_number", "").lstrip("0") or "0"
        lines = [
            (f"{self.CHAMBER} roll call vote {number} — "
             f"Congress {congress}, session {session}."),
        ]
        for label, value in (("Question", details.get("question")),
                             ("Measure", details.get("measure")),
                             ("Description", _xml_text(root, "vote_document_text")),
                             ("Result", details.get("result")),
                             ("Recorded", details.get("recorded_at"))):
            if value:
                lines.append(f"{label}: {value}")
        lines.append("Tally: " + "; ".join(f"{k} {v}" for k, v in counts.items()))
        ordered = [p for p in self._POSITION_ORDER if p in positions]
        ordered += sorted(p for p in positions if p not in self._POSITION_ORDER)
        for position in ordered:
            names = positions[position]
            lines.append(f"{position} ({len(names)}): " + ", ".join(names))
            published = counts.get(position)
            if published is not None and published != len(names):
                lines.append(
                    f"Note: the published count records {published} {position},"
                    f" the member list {len(names)}; both are reported as served.")
        return "\n".join(lines)


# The chambers' own short forms, matching how the Senate's vote records
# and the Congressional Record write a measure ("S.J.Res. 181"), and the
# congress.gov URL slug for each. A bill type absent from these tables is
# skipped rather than guessed at: a wrong slug is a citation that 404s.
_BILL_DESIGNATIONS = {
    "HR": "H.R.", "HJRES": "H.J.Res.", "HCONRES": "H.Con.Res.", "HRES": "H.Res.",
    "S": "S.", "SJRES": "S.J.Res.", "SCONRES": "S.Con.Res.", "SRES": "S.Res.",
}
_BILL_SLUGS = {
    "HR": "house-bill", "HJRES": "house-joint-resolution",
    "HCONRES": "house-concurrent-resolution", "HRES": "house-resolution",
    "S": "senate-bill", "SJRES": "senate-joint-resolution",
    "SCONRES": "senate-concurrent-resolution", "SRES": "senate-resolution",
}
# Listing order within a day: House measures, then Senate, each in the
# conventional bill-then-resolution sequence. It is a stable clerical
# ordering, not a ranking — GUIDE §3 forbids a rule that prefers one
# measure over another.
BILL_TYPE_ORDER = tuple(_BILL_SLUGS)


def _ordinal(n):
    """119 -> '119th' (congress.gov's URL form). 11-13 take 'th'."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


class CongressBillActionsAdapter(SourceAdapter):
    """Bill actions from the Congress.gov API (GUIDE §3 "Bill actions";
    evidence gathered live through this client, 2026-07-31).

    The endpoint (``/v3/bill``) enumerates the whole corpus — 429,331
    records — newest-updated first, 250 to a page (the documented
    maximum). Each record carries the measure's identity and its
    ``latestAction``: a date and one sentence of plain legislative
    English ("Committee on Finance. Ordered to be reported", "Motion to
    proceed to consideration of measure rejected in Senate"). That
    sentence IS the content, which is why wants_article() is False —
    and, separately, why it must be: www.congress.gov answers 403 to our
    identified client (verified 2026-07-31 on three bill pages), so
    fetching the page we cite is refused. We ingest what the API offers
    and never force what the website refuses (GUIDE §3 access hierarchy).
    The cited link is still the human bill page, because a citation is
    for a reader with a browser; the API URL would demand a key.

    THREE THINGS ABOUT DATES, ALL MEASURED:

    - ``updateDate`` is when the RECORD changed; ``actionDate`` is when
      the thing happened. Of 250 records all updated 2026-07-31, actions
      ranged from 1997 to 2026-07-30. Dating by updateDate would claim a
      1997 action as today's news, so items() dates by ``actionDate``
      and bounds itself to config.INDEX_LOOKBACK_DAYS.
    - The record is published the morning AFTER the action: on
      2026-07-31 the newest action anywhere on the page was 07-30 (97 of
      them) and the bulk of a day's actions entered the API between
      08:00 and 12:00 UTC the next day. Hence DATED_BY_PUBLISHER — see
      the base class; dating these by observation would file every
      action under a day on which nothing happened.
    - ``sort`` is not optional and not safely defaulted. Sent as
      ``updateDate+desc`` pre-encoded (so requests escapes the plus) the
      service silently returned ASCENDING order — the oldest records in
      the corpus, from 1995. It is passed here with a literal space so
      urlencode produces the ``+`` the service means, and the resulting
      order is asserted by reading the dates, never assumed.

    IDENTITY is ``{bill}:{actionDate}``: a re-poll of an unchanged
    record is the same item, a new action on the same bill is a new one.
    The known cost, disclosed rather than papered over: the endpoint
    exposes only the LATEST action, so two actions on the same bill on
    the same day collapse to one item. The alternative — hashing the
    action text into the identity — trades that under-count for the
    risk of listing one event twice when the record's text is amended
    (the Congressional Record citation is appended to action text after
    the fact), and over-counting is the worse editorial failure."""

    COLLECTION = "BILLACTIONS"
    DOC_TYPE = "BILLACTION"
    DATED_BY_PUBLISHER = True
    FORMAT = "congress-bill-actions"
    PUBLISHER = "Library of Congress"

    # The documented maximum. One page per poll is the whole request
    # cost: 749 bill records were updated across 2026-07-30 and 350 by
    # 19:20 ET on 07-31, so a page of 250 carries roughly eight times the
    # per-hour update rate the collector's hourly poll has to cover, and
    # the loop's dedupe accumulates the day across polls. Walking the
    # corpus is never worth a request — it is 1,717 pages of history the
    # lookback window would discard.
    PAGE_LIMIT = 250

    BILL_PAGE = "https://www.congress.gov/bill/{congress}-congress/{slug}/{number}"

    def request_params(self):
        return {
            "api_key": config.api_key(),  # redacted from the fetch log by the client
            "format": "json",
            "limit": self.PAGE_LIMIT,
            # A literal space, NOT "+": urlencode writes the plus the
            # service expects, and a pre-encoded "%2B" made it sort ascending.
            "sort": "updateDate desc",
        }

    def wants_article(self):
        return False  # the action sentence is the content; the page 403s us

    def items(self, body, content_type):
        try:
            return self._parse(body)
        except Exception as exc:  # noqa: BLE001 — items() must not raise
            logger.warning("congress bill actions: payload unparsable: %r", exc)
            return None, []

    def _parse(self, body):
        payload = json.loads((body or b"").decode("utf-8", "replace"))
        bills = payload.get("bills") if isinstance(payload, dict) else None
        if not isinstance(bills, list):
            logger.warning("congress bill actions: response names no bill list")
            return None, []

        today = dt.date.fromisoformat(publication_date())
        oldest = today - dt.timedelta(days=config.INDEX_LOOKBACK_DAYS)
        out, skipped, out_of_window, seen = [], 0, 0, set()
        for bill in bills:
            built = self._item(bill) if isinstance(bill, dict) else None
            if built is None:
                skipped += 1
                continue
            day, item = built
            if not oldest <= day <= today:
                out_of_window += 1
                continue
            if item["guid"] in seen:
                continue  # one page can carry a measure twice; identity decides
            seen.add(item["guid"])
            out.append(item)
        out.sort(key=self._sort_key)
        logger.info("congress bill actions: %d of %d record(s) carry an action in"
                    " the %d-day window, %d outside it%s", len(out), len(bills),
                    config.INDEX_LOOKBACK_DAYS, out_of_window,
                    f", {skipped} unreadable (skipped)" if skipped else "")
        return self.FORMAT, out

    @staticmethod
    def _sort_key(item):
        extra = item["extra"]
        raw = str(extra.get("bill_number") or "")
        return (extra.get("action_date") or "",
                BILL_TYPE_ORDER.index(extra["bill_type"]),
                int(raw) if raw.isdigit() else 0, raw)

    def _item(self, bill):
        """(date, item) for one API record, or None if the record does not
        establish a measure, an action and a readable action date. A record
        we cannot date is skipped, never dated by observation: claiming
        Congress acted today when the record does not say so is worse than
        not listing it."""
        action = bill.get("latestAction")
        if not isinstance(action, dict):
            return None
        bill_type = str(bill.get("type") or "").strip().upper()
        number = str(bill.get("number") or "").strip()
        congress = str(bill.get("congress") or "").strip()
        text = " ".join(str(action.get("text") or "").split())
        if bill_type not in _BILL_SLUGS or not (number and congress.isdigit() and text):
            return None
        try:
            day = dt.date.fromisoformat(str(action.get("actionDate") or "").strip())
        except ValueError:
            return None

        designation = f"{_BILL_DESIGNATIONS[bill_type]} {number}"
        title = " ".join(str(bill.get("title") or "").split())
        link = self.BILL_PAGE.format(congress=_ordinal(int(congress)),
                                     slug=_BILL_SLUGS[bill_type], number=number)
        return day, {
            "title": f"{designation} — {title}" if title else designation,
            "link": link,
            "guid": f"congress-action-{congress}-{bill_type.lower()}-{number}"
                    f":{day.isoformat()}",
            # Already ISO — report._claimed_day reads it, and it is the day
            # this document is filed under (DATED_BY_PUBLISHER).
            "claimed_date": day.isoformat(),
            "description": text,
            "description_chars": len(text),
            "extra": {
                "publisher": self.PUBLISHER,
                "congress": congress,
                "bill_type": bill_type,
                "bill_number": number,
                "designation": designation,
                "bill_title": title,
                "origin_chamber": str(bill.get("originChamber") or "").strip(),
                "action_date": day.isoformat(),
                "action_time": str(action.get("actionTime") or "").strip(),
                "action_text": text,
                "api_url": str(bill.get("url") or "").split("?")[0],
                "record_updated": str(bill.get("updateDate") or "").strip(),
            },
        }

    def fallback_text(self, item):
        """The stored record. wants_article() is False, so this is what the
        loop stores for every item, disclosed as mode "feed-only". Must not
        raise and must never come back blank."""
        extra = item.get("extra") or {}
        lines = [item.get("title") or extra.get("designation") or "Bill action"]
        for label, value in (
            ("Congress", extra.get("congress")),
            ("Originating chamber", extra.get("origin_chamber")),
            ("Action recorded", " ".join(p for p in (extra.get("action_date"),
                                                     extra.get("action_time")) if p)),
            ("Action", extra.get("action_text") or item.get("description")),
            ("Record updated", extra.get("record_updated")),
        ):
            if value:
                lines.append(f"{label}: {value}")
        lines.append(f"Source: {self.PUBLISHER} bill record via the Congress.gov API"
                     f" ({extra.get('api_url') or item.get('link') or ''})".rstrip())
        return "\n".join(lines)


_MONTH_NUMBERS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12, "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
    "jul": 7, "aug": 8, "sept": 9, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
# Longest-first alternation so "June" is not read as "Jun" + a stray "e",
# and an explicit table rather than strptime("%b"): %b reads the process's
# LC_TIME, which would make what the digest lists depend on the locale of
# the machine that rendered it (Phase 2 finding, 2026-07-31).
_MONTH_NAME = "|".join(sorted(_MONTH_NUMBERS, key=len, reverse=True))
_DATE_PATTERNS = (
    # (kind, regex, field order) — kind is stored in metadata so an auditor
    # can see which syntax produced a listed date.
    ("iso", re.compile(r"\b(20\d\d)-(\d{2})-(\d{2})\b"), "ymd"),
    ("month-day-year", re.compile(
        rf"\b({_MONTH_NAME})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(20\d\d)\b",
        re.IGNORECASE), "mdy"),
    ("day-month-year", re.compile(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH_NAME})\.?,?\s+(20\d\d)\b",
        re.IGNORECASE), "dmy"),
    # US ordering. Every source in this registry is a US federal publisher
    # writing for a US audience; a European d/m/y reading would silently
    # transpose 07/08 dates. Stated here so the assumption is auditable.
    ("slash", re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d|\d\d)\b"), "mdy-slash"),
)


def _iso_day(value):
    """An ISO-8601-prefixed string -> date, or None. Used for <time
    datetime="..."> attributes, which may carry a full timestamp."""
    match = re.match(r"^(20\d\d)-(\d{2})-(\d{2})", (value or "").strip())
    if not match:
        return None
    try:
        return dt.date(*(int(g) for g in match.groups()))
    except ValueError:
        return None


def claimed_day_from_text(raw):
    """'YYYY-MM-DD' for a publisher date string the RFC 822 and ISO
    readers cannot parse, or None.

    The third tier of the dating rule (GUIDE §3, added 2026-08-06). RSS
    specifies RFC 822 pubDates and most publishers comply, but Drupal
    sites — 16 of the registry's planned sources — emit their site date
    format instead: NIH sends 'Wed, 08/05/2026 - 08:00', TSA sends
    'July 17, 2026'. Both look plausible and both defeat
    email.utils.parsedate_to_datetime.

    Why that mattered enough to fix: an unreadable claimed date falls
    back to the observed day, which the dating split treats as TODAY.
    NIH's feed spans seven weeks, so activating it unparsed would have
    published seven weeks of releases as today's news — the 2026-07-31
    failure in a new form. Found by probe, 2026-08-06.

    Deliberately reuses _find_dates: the patterns, the locale-safe month
    table, and the audited US-ordering assumption for m/d/Y already exist
    and are exercised by the html-index adapter. A second date parser
    would be a second place for that assumption to drift.

    Ambiguity is resolved, not guessed: _DATE_PATTERNS is ordered, so an
    ISO or month-name form wins over the slash form when a string states
    both. A string stating no valid calendar date returns None, and None
    keeps its existing meaning — we could not read it."""
    dates = _find_dates((raw or "").strip())
    return dates[0][0].isoformat() if dates else None


def _find_dates(text):
    """[(date, kind, matched text)] for every calendar date the string
    states, in the order the patterns are declared. Never raises."""
    found = []
    for kind, pattern, order in _DATE_PATTERNS:
        for match in pattern.finditer(text):
            a, b, c = match.groups()
            try:
                if order == "ymd":
                    day = dt.date(int(a), int(b), int(c))
                elif order == "mdy":
                    day = dt.date(int(c), _MONTH_NUMBERS[a.lower()], int(b))
                elif order == "dmy":
                    day = dt.date(int(c), _MONTH_NUMBERS[b.lower()], int(a))
                else:
                    year = int(c)
                    day = dt.date(year + 2000 if year < 100 else year,
                                  int(a), int(b))
            except (ValueError, KeyError):
                continue
            found.append((day, kind, match.group(0)))
    return found


class _ListingParser(HTMLParser):
    """One structural pass over a listing page, stdlib only.

    Records three things in document order: every anchor (href, its link
    text, the element that contains it), every date the page states (in a
    <time datetime> attribute or in running text), and every element's own
    text. Elements are kept as a parent-pointer tree so the adapter can
    ask the only question that matters — which anchor and which date
    belong to the same listing entry — structurally rather than by
    scanning bytes for a nearby-looking string.

    Malformed markup is the normal case on these pages: an unmatched
    </div> pops nothing, an unclosed <li> is closed by its successor's
    close, and text inside <script>/<style>/<svg> never counts. None of
    that raises; a listing that confuses the parser yields fewer items,
    which the adapter reports rather than papering over."""

    _VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img",
                       "input", "link", "meta", "param", "source", "track",
                       "wbr"})
    _SKIP = frozenset({"script", "style", "noscript", "template", "svg", "head"})
    # Deep pathological nesting is a parser problem, not a publisher one.
    _MAX_DEPTH = 200

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parents = [-1]          # node 0 is the synthetic document root
        self.tags = [""]
        self.skipped = [False]
        self.stack = [0]
        self.anchors = []            # {href, text, node, order}
        self.dates = []              # {day, kind, raw, node, order}
        self.texts = []              # (node, order, text)
        self._order = 0
        self._skip_depth = 0
        self._open_anchor = None
        self._buffers = {}           # node -> [first order, [chunks]]

    # -- tree -----------------------------------------------------------
    def _push(self, tag):
        self.parents.append(self.stack[-1])
        self.tags.append(tag)
        self.skipped.append(tag in self._SKIP)
        self.stack.append(len(self.parents) - 1)

    def _pop(self, node):
        self._flush(node)
        if self.skipped[node]:
            self._skip_depth = max(0, self._skip_depth - 1)
        if self._open_anchor is not None and self._open_anchor["node"] == node:
            self._close_anchor()

    def _flush(self, node):
        entry = self._buffers.pop(node, None)
        if not entry:
            return
        order, chunks = entry
        text = " ".join("".join(chunks).split())
        if not text:
            return
        self.texts.append((node, order, text))
        for day, kind, raw in _find_dates(text):
            self.dates.append({"day": day, "kind": kind, "raw": raw,
                               "node": node, "order": order})

    # -- anchors --------------------------------------------------------
    def _close_anchor(self):
        anchor = self._open_anchor
        self._open_anchor = None
        anchor["text"] = " ".join("".join(anchor["parts"]).split())
        del anchor["parts"]
        self.anchors.append(anchor)

    # -- HTMLParser hooks -----------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag in self._VOID:
            return
        if len(self.stack) > self._MAX_DEPTH:
            return
        self._push(tag)
        node = self.stack[-1]
        if self.skipped[node]:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        values = dict(attrs)
        if tag == "a":
            if self._open_anchor is not None:  # unclosed <a>; the outer wins
                self._close_anchor()
            self._open_anchor = {"href": (values.get("href") or "").strip(),
                                 "node": node, "order": self._order,
                                 "parts": []}
        elif tag == "time":
            day = _iso_day(values.get("datetime"))
            if day is not None:
                # A machine-written attribute beats prose: it is the
                # publisher's own statement of the day, unambiguous.
                self.dates.append({"day": day, "kind": "time-attribute",
                                   "raw": values.get("datetime", ""),
                                   "node": node, "order": self._order})

    def handle_startendtag(self, tag, attrs):
        if tag not in self._VOID:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self._VOID:
            return
        for depth in range(len(self.stack) - 1, 0, -1):
            if self.tags[self.stack[depth]] != tag:
                continue
            for _ in range(len(self.stack) - depth):
                self._pop(self.stack.pop())
            return
        # No matching open tag: a stray close. Ignore it, as a browser does.

    def handle_data(self, data):
        self._order += 1
        if self._skip_depth or not data.strip():
            return
        if self._open_anchor is not None:
            self._open_anchor["parts"].append(data)
        buffer = self._buffers.setdefault(self.stack[-1], [self._order, []])
        buffer[1].append(data)

    def close(self):
        super().close()
        while len(self.stack) > 1:
            self._pop(self.stack.pop())
        self._flush(0)


class HtmlIndexAdapter(SourceAdapter):
    """Listing pages that carry no usable feed (probe 2026-07-31: 33 of 42
    web sources answered 200, robots permitting, and advertised none).

    AN INDEX PAGE IS NOT A FEED, AND THE DATING RULE IS WHY. GUIDE §3 lets
    a feed item with no parseable date fall back to the observed date —
    honest, because a feed carries what the publisher just published. A
    listing page carries 20-50 entries reaching back months. Observation-
    dating those would file dozens of old releases into today's digest AS
    TODAY'S NEWS, and the backfill exclusion (AGENCYPR-EX-01) could not
    catch a single one, because their claimed day would equal the digest
    day. So this adapter inverts the feed rule: **an entry whose date this
    parser cannot read is skipped, not observation-dated**, and the number
    skipped is logged on every poll. A source that mostly yields skips is
    a source we should not have activated; the log is how that shows up.

    HOW AN ENTRY IS FOUND. One stdlib pass builds a parent-pointer tree of
    the page (_ListingParser). For each plausible article anchor the
    adapter walks up to the innermost ancestor whose subtree states any
    date — the listing entry's own block. That block is accepted as the
    entry only if it looks like one entry rather than the whole list:
    either it holds at most MAX_BLOCK_ANCHORS links, or every date under
    it names the same day (the date-headed grouping OFAC's Recent Actions
    uses). The chosen date must also sit within MAX_DATE_DISTANCE text
    runs of the anchor. Those two guards are what stop the failure mode
    that would be worst: nrc.gov's listing states no per-entry dates at
    all, only "Page Last Reviewed/Updated Tuesday, January 06, 2026" in
    its footer — a naive nearest-date parser would stamp that footer date
    onto 40 links, and this one returns nothing at all instead.

    NO ARTICLE FETCHES. wants_article() is False, for budget before
    access: the agency class holds 500 requests a day and hit that ceiling
    on 2026-07-31. A listing carries what section 6 actually renders — an
    attributed title, a URL, an agency-stated date (report._agency_lines
    reads nothing else) — so an article fetch would multiply this class's
    request count by the item count to enrich stored text nothing
    currently reads. Mode is disclosed per item as "feed-only"; if a
    source later needs full text, that is a separate adapter and a
    separate budget decision, not a default.

    PER-SOURCE HINT. The optional registry field `index_item_path`
    restricts entries to anchors whose URL path starts with that string —
    the one hint that repeatedly separates releases from the navigation
    around them, and deliberately not a selector language. Everything else
    is heuristic and identical across sources.

    IDENTITY. These sources have no ingestion history, so URLs are
    normalized freely (GUIDE §7 T5, docs/adding-sources.md): lowercased
    scheme and host, fragment dropped, trailing slash dropped, query kept
    — some listings identify an entry only by ?id=, and dropping the query
    would collapse distinct releases into one."""

    FORMAT = "html-index"
    # A listing entry block holding more links than this is the list, not
    # an entry — unless every date under it agrees, which is the shape of
    # a date-headed group, and even then not past MAX_GROUP_ANCHORS.
    MAX_BLOCK_ANCHORS = 4
    MAX_GROUP_ANCHORS = 12
    # A link repeated this often is furniture, not an entry: whitehouse.gov
    # tags every release with its category ("Presidential Actions") and
    # OFAC tags every action "Sanctions List Updates", both linked, both
    # inside the entry's own block, and both otherwise indistinguishable
    # from a release. A release is linked once, occasionally twice
    # (thumbnail and headline).
    MAX_LINK_REPEATS = 2
    # ...and however tidy the markup looks, the date must be near the link
    # in reading order. Counted in text runs, not characters.
    MAX_DATE_DISTANCE = 60
    # Belt and braces on a mis-parse: with wants_article() False this costs
    # no requests, but it bounds what one bad page can push into a digest.
    MAX_ITEMS = 60
    # Titles shorter than this are navigation ("More", "Read", "News").
    MIN_TITLE_CHARS = 12

    def wants_article(self):
        return False

    def items(self, body, content_type):
        try:
            return self._parse(body, content_type)
        except Exception as exc:  # noqa: BLE001 — items() must not raise
            logger.warning("%s: html index unparsable: %r",
                           self.entry.get("id", "html-index"), exc)
            return None, []

    # -- parsing --------------------------------------------------------
    def _parse(self, body, content_type):
        base = source_url(self.entry) or ""
        parser = _ListingParser()
        parser.feed(provenance.decode_body(body, content_type))
        parser.close()

        anchors = [a for a in parser.anchors if self._is_article_anchor(a, base)]
        anchors = self._drop_repeats(anchors, base)
        if not anchors:
            logger.info("%s: listing page yielded no article links",
                        self.entry.get("id", "html-index"))
            return self.FORMAT, []

        ancestry = _AncestryIndex(parser.parents)
        anchor_counts, dates_by_node = ancestry.tally(anchors, parser.dates)
        today = dt.date.fromisoformat(publication_date())
        oldest = today - dt.timedelta(days=config.INDEX_LOOKBACK_DAYS)

        out, seen, undated, outside = [], set(), 0, 0
        for anchor in anchors:
            dated = self._date_for(anchor, ancestry, anchor_counts, dates_by_node)
            if dated is None:
                undated += 1
                continue
            block, date_event = dated
            if not oldest <= date_event["day"] <= today:
                outside += 1
                continue
            link = urljoin(base, anchor["href"])
            key = self._normalize(link)
            if key in seen:
                continue
            seen.add(key)
            out.append(self._item(anchor, link, key, block, date_event,
                                  ancestry, parser))
        truncated = max(0, len(out) - self.MAX_ITEMS)
        logger.info(
            "%s: listing has %d article link(s); %d dated inside the %d-day"
            " lookback, %d dated outside it, %d skipped for no readable date%s",
            self.entry.get("id", "html-index"), len(anchors), len(out),
            config.INDEX_LOOKBACK_DAYS, outside, undated,
            f", {truncated} dropped over the {self.MAX_ITEMS}-item cap"
            if truncated else "")
        return self.FORMAT, out[:self.MAX_ITEMS]

    def _is_article_anchor(self, anchor, base):
        href = anchor["href"]
        if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
            return False
        if len(anchor["text"]) < self.MIN_TITLE_CHARS or " " not in anchor["text"]:
            return False
        link = urljoin(base, href)
        parts, base_parts = urlsplit(link), urlsplit(base)
        if parts.scheme not in ("http", "https"):
            return False
        # Offsite links on a newsroom page are other people's publications;
        # this project cites the agency's own record (GUIDE §1).
        if base_parts.netloc and parts.netloc.lower() != base_parts.netloc.lower():
            return False
        if parts.path.rstrip("/") == base_parts.path.rstrip("/"):
            return False  # the listing linking to itself (pagination, "current")
        hint = (self.entry.get("index_item_path") or "").strip()
        return not hint or parts.path.startswith(hint)

    def _drop_repeats(self, anchors, base):
        counts = {}
        for anchor in anchors:
            key = self._normalize(urljoin(base, anchor["href"]))
            counts[key] = counts.get(key, 0) + 1
        return [a for a in anchors
                if counts[self._normalize(urljoin(base, a["href"]))]
                <= self.MAX_LINK_REPEATS]

    def _date_for(self, anchor, ancestry, anchor_counts, dates_by_node):
        """(block node, date event) for the entry this anchor belongs to,
        or None when the page states no date that is credibly this
        entry's. None is the honest answer, and the common one."""
        for node in ancestry.chain(anchor["node"]):
            events = dates_by_node.get(node)
            if not events:
                continue
            count = anchor_counts.get(node, 0)
            if count > self.MAX_BLOCK_ANCHORS and (
                    count > self.MAX_GROUP_ANCHORS
                    or len({e["day"] for e in events}) > 1):
                return None  # this is the list, not one of its entries
            best = min(events, key=lambda e: (abs(e["order"] - anchor["order"]),
                                              e["kind"] != "time-attribute"))
            if abs(best["order"] - anchor["order"]) > self.MAX_DATE_DISTANCE:
                return None  # a page-furniture date (footer "last reviewed")
            return node, best
        return None

    def _item(self, anchor, link, key, block, date_event, ancestry, parser):
        description = self._description(anchor, block, ancestry, parser)
        return {
            "title": anchor["text"],
            "link": link,
            # No listing page publishes GUIDs; the normalized URL is the
            # publisher's own identifier for the entry.
            "guid": key,
            # ISO-8601 so report._claimed_day can read it. Anything else
            # would silently date the item by observation instead.
            "claimed_date": date_event["day"].isoformat(),
            "description": description,
            "description_chars": len(description),
            "extra": {
                "index_url": source_url(self.entry) or "",
                # How we dated it, and from what text — the audit trail for
                # the one decision this adapter makes that could mislead.
                "date_syntax": date_event["kind"],
                "date_text": date_event["raw"],
            },
        }

    def _description(self, anchor, block, ancestry, parser):
        """The listing entry's own text minus its title — the teaser, when
        the publisher writes one. This is what gets stored (wants_article
        is False), so it is the item's content, not decoration."""
        parts = []
        for node, _order, text in parser.texts:
            if node == anchor["node"] or not ancestry.contains(block, node):
                continue
            if ancestry.contains(anchor["node"], node):
                continue  # markup inside the title link
            if text not in parts:
                parts.append(text)
        return " ".join(parts)[:800].strip()

    def _normalize(self, url):
        parts = urlsplit(url)
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                           parts.path.rstrip("/") or "/", parts.query, ""))

    def stable_id(self, item):
        # No history to preserve (activated 2026-07-31), so identity is the
        # normalized URL from the start — see IDENTITY in the class docstring.
        return item.get("guid") or self._normalize(item.get("link") or "")

    def fallback_text(self, item):
        """Title plus the listing's own teaser. Never raises, never blank
        for an item that reached here: items() only emits titled anchors."""
        parts = [item.get("title") or "", item.get("description") or ""]
        return " — ".join(p for p in parts if p) or (item.get("link") or "")


class _AncestryIndex:
    """Parent-pointer walks, memoized. The listing parser produces one
    parent array; every question the adapter asks of the tree ("which
    block contains this anchor", "is this text inside that block") is a
    walk up it, and the same walks repeat across dozens of anchors."""

    def __init__(self, parents):
        self._parents = parents
        self._chains = {}

    def chain(self, node):
        """(node, its parent, ..., root) — the node itself first."""
        cached = self._chains.get(node)
        if cached is None:
            chain, current = [], node
            while current >= 0:
                chain.append(current)
                current = self._parents[current]
            cached = self._chains[node] = tuple(chain)
        return cached

    def contains(self, ancestor, node):
        return ancestor in self.chain(node)

    def tally(self, anchors, dates):
        """(anchors per subtree, date events per subtree) for every node
        that has any — one pass up from each leaf, not a tree walk."""
        anchor_counts, dates_by_node = {}, {}
        for anchor in anchors:
            for node in self.chain(anchor["node"]):
                anchor_counts[node] = anchor_counts.get(node, 0) + 1
        for event in dates:
            for node in self.chain(event["node"]):
                dates_by_node.setdefault(node, []).append(event)
        return anchor_counts, dates_by_node


class PresidentialActionsAdapter(SourceAdapter):
    """whitehouse.gov's presidential-action feeds (GUIDE §3; activated
    2026-08-06). An ordinary RSS source in every mechanical respect —
    the feed is well-formed, every item carries pubDate and guid, and
    the article page is fetched because the feed's <description> is a
    400-700 character teaser, not the document.

    Two things differ, both of them the publisher's doing rather than
    ours. It gets its OWN collection because its documents are the
    President's instruments, not agency announcements, and a digest that
    filed an executive order under "Agency Announcements" would
    misdescribe it. And its document type is per item, read from the
    <category> element the feed already states: we never infer whether
    something is an order or a proclamation when whitehouse.gov declares
    it.

    Editorial register is unchanged from every other agency source: the
    §2 attributed-speech rule applies in full (operator, 2026-08-06), so
    the digest's own prose about these documents attributes. What is
    never altered is the source's words — titles and any quoted text are
    published verbatim, as GUIDE §2's scope amendment requires."""

    COLLECTION = "PRESACT"
    DOC_TYPE = "PRESACTION"          # fallback when the feed states no class
    DATED_BY_PUBLISHER = False        # the §3 dating rule, as for every feed

    # The publisher's taxonomy -> our document type. Deliberately an
    # explicit table and not a slug transform: an unrecognized category
    # falls back to PRESACTION and still renders, rather than inventing a
    # type the rules and the coverage statement have never heard of.
    CATEGORY_DOC_TYPES = types.MappingProxyType({
        "executive orders": "EO",
        "proclamations": "PROCLAMATION",
        "presidential memoranda": "MEMORANDUM",
        "nominations & appointments": "NOMINATION",
        "nominations and appointments": "NOMINATION",
    })

    def doc_type_for(self, item):
        for category in item.get("categories") or ():
            mapped = self.CATEGORY_DOC_TYPES.get(category.strip().lower())
            if mapped:
                return mapped
        return self.DOC_TYPE


ADAPTERS = {
    "rss": SourceAdapter,
    "rss-feed-only": FeedOnlyAdapter,
    "usps": UspsAdapter,
    "senate-votes": SenateVotesAdapter,
    "congress-bill-actions": CongressBillActionsAdapter,
    "html-index": HtmlIndexAdapter,
    "presidential-actions": PresidentialActionsAdapter,
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
INGESTIBLE_TYPES = ("rss", "xml-index", "api", "html-index")


def adapter_for(entry):
    name = entry.get("adapter") or "rss"
    try:
        return ADAPTERS[name](entry)
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


def _issue_day(item, dated_by_publisher):
    """The publication day this document belongs to.

    Default: the federal publication day we observed it (GUIDE §3, amended
    2026-07-30) — Washington's day, not UTC's, so an 8:30pm-Eastern release
    belongs to that day and not to the next one UTC had already started.
    Observation stamps stay UTC regardless.

    DATED_BY_PUBLISHER adapters use the publisher's own date instead, the
    way every govinfo collection does, because their publisher prints an
    authoritative date and posts the record later. The ISO check mirrors
    report._claimed_day's ISO branch exactly; a claim we cannot read falls
    back to observation, which is the same honest fallback the dating rule
    itself specifies."""
    if dated_by_publisher:
        raw = (item.get("claimed_date") or "").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", raw[:10]):
            return raw[:10]
        # Same third tier report._claimed_day gained 2026-08-06, kept in
        # step here because this docstring promises the two mirror each
        # other — a publisher-dated source emitting a Drupal date must
        # not silently fall through to observation while the digest's
        # own split reads it fine.
        readable = claimed_day_from_text(raw)
        if readable:
            return readable
    return publication_date()


def _store_item(conn, entry, item, package_id, text, mode, capture_id, wayback_url,
                collection="AGENCYPR", doc_type="PRESS", dated_by_publisher=False):
    now = utc_now_iso()
    issued = _issue_day(item, dated_by_publisher)
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " title, package_link, first_seen_at, fetch_status, fetched_at, digest_day)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, 'fetched', ?, ?)",
        # digest_day = issued: AGENCYPR is cover-filed (GUIDE §3 agency
        # dating rule, unchanged by the 2026-08-06 filing amendment).
        (package_id, collection, issued, now, item["title"], item["link"], now, now,
         issued),
    )
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, '', ?, ?, ?, ?, ?, ?, ?, ?, 1)",
        (
            package_id, collection, doc_type, item["title"], entry["name"],
            _metadata_json(entry, item, mode, capture_id, wayback_url),
            text, len(text), now,
        ),
    )
    conn.commit()


def _metadata_json(entry, item, mode, capture_id, wayback_url):
    meta = {
        "source_id": entry["id"],
        "url": item["link"],
        "claimed_published_at": item.get("claimed_date"),
        "mode": mode,
        "capture_id": capture_id,
        "wayback_url": wayback_url,
    }
    extra = item.get("extra")
    if extra:
        # Adapter-supplied structured fields, nested under one key so they
        # can never collide with a loop-owned one — collect.py keys
        # web-vs-email on the ABSENCE of `channel`.
        meta["details"] = extra
    return json.dumps(meta, sort_keys=True)


def poll_source(client, wayback, conn, entry):
    """One conditional poll of one active source. Returns stats."""
    stats = {"id": entry["id"], "feed_status": None, "new_items": 0,
             "articles_fetched": 0, "wayback_submitted": 0, "errors": 0}
    feed_url = source_url(entry)
    if not feed_url:
        stats["feed_status"] = "no-feed-url"
        return stats
    # Resolved before the fetch, not after: an API-backed source's query
    # (page size, sort, credential) is the adapter's to state.
    adapter = adapter_for(entry)

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
        resp = client.get(feed_url, params=adapter.request_params(),
                          headers=headers or None)
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
                    capture_id, wayback_url,
                    collection=adapter.COLLECTION,
                    doc_type=adapter.doc_type_for(item),
                    dated_by_publisher=adapter.DATED_BY_PUBLISHER)
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

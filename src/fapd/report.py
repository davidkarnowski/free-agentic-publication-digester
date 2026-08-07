"""REPORT stage (GUIDE §5 stage 4): deterministic digest rendering.

Reads only stored artifacts — summaries, extracted_texts, packages,
granules, graphic_assets, sync_state — and writes ``digests/<date>.md``
following ``digests/TEMPLATE.md``. Zero LLM calls (GUIDE §6 rule 2: an LLM
call that could have been a SQL query is a bug); every mechanical figure in
the digest is computed here with SQL.

The rendered document is validated (:func:`validate`) before the file is
written: every govinfo citation must resolve to a stored record, the
Coverage Statement must reconcile against the database, generated prose
must clear the banned-lexicon scan (verbatim official summaries are masked
first — they are quoted source text, not our prose), and every item must
state its inclusion rule. A digest that fails validation is never written.

Embedded source graphics (GUIDE §6 rule 9) are copied as PNGs under
``digests/assets/<date>/`` so the published digest is self-contained; items
whose remaining graphics are not rendered disclose the count with a link to
the source PDF — the no-silent-omission rule applies to images too.
"""

from __future__ import annotations

import datetime as dt
import email.utils
import json
import re
import subprocess
from pathlib import Path

from PIL import Image

from . import config, fedcal
from .rules import CREC_FLOOR_CHAR_THRESHOLD
from .sync import publication_date

__all__ = ["RULE_DESCRIPTIONS", "ValidationError", "render", "validate"]

# Human descriptions of the mechanical selection/exclusion rules recorded in
# summaries.inclusion_rule (ruleset lives in rules.py; these are the digest's
# reader-facing one-liners).
RULE_DESCRIPTIONS = {
    "CREC-SEL-01": "floor item ≥ threshold floor time",
    "CREC-SEL-02": "recorded vote (all recorded votes are listed)",
    "BILLS-SEL-01": "reached stage: reported/enrolled/calendar",
    "FR-SEL-01": "document type: final rule (all listed)",
    "FR-SEL-02": "document type: proposed rule (all listed)",
    "FR-SEL-03": "presidential document (all listed)",
    "PLAW-SEL-01": "enacted into law (all public and private laws are listed)",
    "AGENCYPR-SEL-01": "official agency release dated this day by the agency"
                       " (all such releases from active sources are listed;"
                       " titles only in the pilot)",
    "VOTES-SEL-01": "recorded vote of this day in a chamber's own roll-call"
                    " record (every recorded vote is listed, in vote-number"
                    " order; selection is by existence, not importance)",
    "BILLACTIONS-SEL-01": "action the Library of Congress's bill-status record"
                          " dates on this day (every bill action in the window is"
                          " listed, in bill-designation order; selection is by"
                          " existence, not importance)",
    "USCOURTS-SEL-01": "appellate court opinion (all listed)",
    "USCOURTS-SEL-02": "national court opinion (all listed)",
    "FR-EX-01": "notices counted, not individually summarized",
    "CREC-EX-01": "floor granule below floor-time threshold",
    "CREC-EX-02": "extensions/daily-digest sections (counted)",
    "USCOURTS-EX-01": "district court opinions counted, not individually summarized",
    "USCOURTS-EX-02": "bankruptcy court opinions counted, not individually summarized",
    "AGENCYPR-EX-01": "release dated outside this day by the agency (feed"
                      " backfill / newly activated source) — counted, not listed",
    "VOTES-EX-01": "recorded vote the chamber dates on another day (inside the"
                   " index lookback window) — counted, not listed",
    "PRESACT-SEL-01": "executive order published by the White House (all listed)",
    "PRESACT-SEL-02": "presidential proclamation published by the White House"
                      " (all listed)",
    "PRESACT-SEL-03": "presidential memorandum or determination published by the"
                      " White House (all listed)",
    "PRESACT-SEL-04": "other presidential action published by the White House"
                      " (all listed)",
    "PRESACT-EX-01": "presidential action the White House dated outside this day"
                     " (feed backfill / newly activated source) — counted, not"
                     " listed",
}

# GUIDE §6 rule 9: at most this many graphics embedded per summarized item;
# the rest are disclosed with a source-PDF link.
MAX_GRAPHICS_PER_ITEM = 2

_DETAILS_BASE = "https://www.govinfo.gov/app/details"
_PDF_URL = "https://www.govinfo.gov/content/pkg/{pid}/pdf/{pid}.pdf"

# Banned lexicon (GUIDE §2): loaded adjectives and motive attribution never
# appear in generated prose. Word-boundary, case-insensitive; multi-word
# Compiled from THE canonical list (config.BANNED_TERMS, review D8) so the
# validator and every prompt enforce the identical lexicon. Phrases are
# joined word-by-word: re.escape escapes SPACES too (they are special
# under re.VERBOSE), so the old `.replace(" ", r"\s+")` ran on the
# escaped string and produced a literal backslash — every multi-word
# phrase ("red tape", "in an attempt to") was silently unmatchable from
# the gate's creation until 2026-08-02, found by the D8 drift test.
_BANNED_RE = re.compile(
    r"\b(?:"
    + "|".join(r"\s+".join(re.escape(w) for w in t.split())
               for t in config.BANNED_TERMS)
    + r")\b",
    re.IGNORECASE,
)

_DETAILS_RE = re.compile(
    r"https://www\.govinfo\.gov/app/details/([^/()\s]+)(?:/([^/()\s]+))?"
)

_STAGE_SQL = """
SELECT CASE
         WHEN dt IN ('ih', 'is') OR dt LIKE 'introduced%' THEN 'Introduced'
         WHEN dt IN ('rh', 'rs') OR dt LIKE '%reported%' THEN 'Reported'
         WHEN dt IN ('eh', 'es') OR dt LIKE '%engrossed%' THEN 'Engrossed'
         WHEN dt = 'enr' OR dt LIKE '%enrolled%' THEN 'Enrolled'
         ELSE 'Other'
       END AS stage, COUNT(*)
FROM (
    SELECT lower(COALESCE(e.doc_type, '')) AS dt
    FROM extracted_texts e
    JOIN packages p USING (package_id)
    WHERE e.collection = 'BILLS' AND p.digest_day = ?
)
GROUP BY stage
"""


class ValidationError(ValueError):
    """The rendered digest violates the output contract; nothing is written."""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _scalar(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


def _one_line(text):
    return " ".join((text or "").split())


def _truncate(text, limit=120):
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _first_nonempty_line(text):
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return None


def _utc_now():
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_short():
    """Short commit hash of the repo, or "unknown" outside a working checkout."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=config.PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    out = proc.stdout.strip()
    return out if proc.returncode == 0 and out else "unknown"


def _source_line(package_id, granule_id=""):
    if granule_id:
        return (
            f"  - Source: [{package_id} / {granule_id}]"
            f"({_DETAILS_BASE}/{package_id}/{granule_id})"
        )
    return f"  - Source: [{package_id}]({_DETAILS_BASE}/{package_id})"


def _included_line(item):
    rule_id = item["inclusion_rule"]
    desc = RULE_DESCRIPTIONS.get(rule_id, "selection rule")
    line = f"  - Included because: {rule_id} — {desc}"
    if rule_id == "CREC-SEL-01":
        line += f" ({(item.get('char_count') or 0):,} characters)"
    # Observation-day filing (GUIDE §3, amended 2026-08-06): when the
    # document's own date differs from the digest day it filed under,
    # say so mechanically, in place — the reader never has to infer
    # which clock a section is keeping.
    issued = item.get("date_issued")
    if issued and item.get("digest_day") and issued != item["digest_day"]:
        line += f" (document dated {issued})"
    return line


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_items(conn, date):
    """Summarized items for the date at the current prompt version."""
    rows = conn.execute(
        """
        SELECT s.package_id, s.granule_id, s.method, s.inclusion_rule, s.summary,
               COALESCE(e.collection, p.collection) AS collection,
               p.date_issued, p.digest_day,
               e.doc_type, e.title, e.agency, e.metadata, e.char_count,
               substr(e.text, 1, 400) AS text_head,
               g.title AS granule_title,
               ps.plain AS plain
        FROM summaries s
        JOIN packages p ON p.package_id = s.package_id
        LEFT JOIN extracted_texts e
               ON e.package_id = s.package_id AND e.granule_id = s.granule_id
        LEFT JOIN granules g
               ON g.package_id = s.package_id AND g.granule_id = s.granule_id
        LEFT JOIN plain_summaries ps
               ON ps.package_id = s.package_id AND ps.granule_id = s.granule_id
              AND ps.plain_version = ? AND ps.source_prompt_version = s.prompt_version
        WHERE s.prompt_version = ? AND p.digest_day = ?
        ORDER BY s.package_id, s.granule_id
        """,
        (config.PLAIN_PROMPT_VERSION, config.PROMPT_VERSION, date),
    ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        try:
            item["metadata"] = json.loads(item["metadata"] or "{}")
        except (TypeError, ValueError):
            item["metadata"] = {}
        items.append(item)
    return items


def _graphics_by_package(conn, date):
    rows = conn.execute(
        """
        SELECT ga.package_id, ga.granule_id, ga.gid, ga.page, ga.asset_path
        FROM graphic_assets ga
        JOIN packages p USING (package_id)
        WHERE p.digest_day = ? AND ga.status = 'extracted'
        ORDER BY ga.id
        """,
        (date,),
    ).fetchall()
    by_package: dict[str, list[dict]] = {}
    for row in rows:
        by_package.setdefault(row["package_id"], []).append(dict(row))
    return by_package


def _coverage(conn, date):
    """Per-collection accounting, all SQL (GUIDE §2 completeness accounting).

    Unit of account: extracted documents for CREC/FR (granule level),
    published packages for BILLS (whole-package documents), extracted
    opinions for USCOURTS. "Counted only" is the remainder so the table
    always names every unit; the exclusion rules list carries the per-rule
    mechanical counts.
    """
    pv = config.PROMPT_VERSION
    cov = {}
    for coll in ("CREC", "BILLS", "FR", "USCOURTS", "PLAW", "AGENCYPR", "VOTES",
                 "BILLACTIONS", "PRESACT"):
        cov[coll] = {
            "packages": _scalar(
                conn,
                "SELECT COUNT(*) FROM packages WHERE collection = ? AND digest_day = ?",
                (coll, date),
            ),
            "units": _scalar(
                conn,
                "SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)"
                " WHERE e.collection = ? AND p.digest_day = ?",
                (coll, date),
            ),
            "summarized": _scalar(
                conn,
                "SELECT COUNT(*) FROM summaries s JOIN packages p USING (package_id)"
                " WHERE p.collection = ? AND p.digest_day = ? AND s.prompt_version = ?",
                (coll, date, pv),
            ),
        }

    ex01 = _scalar(
        conn,
        """
        SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'CREC' AND p.digest_day = ?
          AND e.doc_type IN ('HOUSE', 'SENATE') AND e.char_count < ?
          AND NOT EXISTS (SELECT 1 FROM summaries s
                          WHERE s.package_id = e.package_id
                            AND s.granule_id = e.granule_id
                            AND s.prompt_version = ?)
        """,
        # Threshold imported from rules.py — the ruleset is the single source
        # (the render-time copy drifted-by-luck-only until 2026-08-06).
        (date, CREC_FLOOR_CHAR_THRESHOLD, pv),
    )
    ex02 = _scalar(
        conn,
        "SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)"
        " WHERE e.collection = 'CREC' AND p.digest_day = ?"
        " AND e.doc_type IN ('EXTENSIONS', 'DAILYDIGEST')",
        (date,),
    )
    crec = cov["CREC"]
    crec["excluded"] = ex01
    crec["counted"] = crec["units"] - crec["summarized"] - ex01
    crec["rules"] = {"CREC-EX-01": ex01, "CREC-EX-02": ex02}

    bills = cov["BILLS"]
    bills["excluded"] = 0
    bills["counted"] = bills["packages"] - bills["summarized"]
    bills["rules"] = {}

    plaw = cov["PLAW"]
    plaw["excluded"] = 0
    plaw["counted"] = plaw["units"] - plaw["summarized"]
    plaw["rules"] = {}

    agencypr = cov["AGENCYPR"]
    _, agency_backfill = _agency_rows(conn, date)
    agencypr["excluded"] = len(agency_backfill)  # AGENCYPR-EX-01 (dating rule)
    agencypr["counted"] = (agencypr["units"] - agencypr["summarized"]
                           - agencypr["excluded"])
    agencypr["rules"] = {"AGENCYPR-EX-01": len(agency_backfill)}

    votes = cov["VOTES"]
    _, votes_backfill = _votes_rows(conn, date)
    votes["excluded"] = len(votes_backfill)  # VOTES-EX-01 (dating rule)
    votes["counted"] = votes["units"] - votes["summarized"] - votes["excluded"]
    votes["rules"] = {"VOTES-EX-01": len(votes_backfill)}

    presact = cov["PRESACT"]
    _, presact_backfill = _presact_rows(conn, date)
    presact["excluded"] = len(presact_backfill)  # PRESACT-EX-01 (dating rule)
    presact["counted"] = (presact["units"] - presact["summarized"]
                          - presact["excluded"])
    presact["rules"] = {"PRESACT-EX-01": len(presact_backfill)}

    # Bill actions carry no exclusion rule at all. Every action inside the
    # lookback window is listed, and the collection is dated by the
    # publisher (GUIDE §3 "Bill actions"), so a stored row's action date IS
    # the day it is filed under — there is no observed-here-but-dated-there
    # remainder for a rule to name. Anything older than the window was never
    # ingested and is disclosed by the section's window statement, not by
    # the accounting.
    billactions = cov["BILLACTIONS"]
    billactions["excluded"] = 0
    billactions["counted"] = billactions["units"] - billactions["summarized"]
    billactions["rules"] = {}

    notices = _scalar(
        conn,
        "SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)"
        " WHERE e.collection = 'FR' AND p.digest_day = ? AND e.doc_type = 'NOTICE'",
        (date,),
    )
    fr = cov["FR"]
    fr["counted"] = notices
    fr["excluded"] = fr["units"] - fr["summarized"] - notices
    fr["rules"] = {"FR-EX-01": notices}

    us_counts = dict(
        conn.execute(
            "SELECT e.doc_type, COUNT(*) FROM extracted_texts e"
            " JOIN packages p USING (package_id)"
            " WHERE e.collection = 'USCOURTS' AND p.digest_day = ?"
            " GROUP BY e.doc_type",
            (date,),
        )
    )
    district = us_counts.get("DISTRICT", 0)
    bankruptcy = us_counts.get("BANKRUPTCY", 0)
    uscourts = cov["USCOURTS"]
    uscourts["counted"] = district + bankruptcy
    uscourts["excluded"] = uscourts["units"] - uscourts["summarized"] - uscourts["counted"]
    uscourts["rules"] = {"USCOURTS-EX-01": district, "USCOURTS-EX-02": bankruptcy}
    return cov


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------


def _journal_first_day(conn):
    """The earliest publication day the item journal covers, or None when
    it has never recorded an ingestion. The single source for "does a
    frozen day view exist for this date" — the digest's header link and
    `publish.build_day`'s absent state both read it, so the two can never
    disagree about which days have an observed listing (GUIDE §5,
    amended 2026-08-03: days before the journal existed have no day
    view; the gap is disclosed, not backfilled)."""
    row = conn.execute(
        "SELECT MIN(digest_date) FROM item_journal WHERE event = 'ingested'"
    ).fetchone()
    return row[0] if row else None


def _header_lines(conn, date, git_short):
    marks = dict(
        conn.execute("SELECT collection, last_modified_watermark FROM sync_state")
    )
    watermark = " · ".join(f"{c}: {marks.get(c, '—')}" for c in config.COLLECTIONS)
    lines = [
        f"# Daily Digest — {date}",
        "",
        "| | |",
        "|---|---|",
        f"| **Digest date** | {date} |",
        f"| **Data date range** | {date} to {date} |",
        f"| **Generated at** | {_utc_now()} (UTC) |",
        f"| **Pipeline version** | {git_short} |",
        f"| **Source watermarks** | {watermark} |",
        "",
    ]
    # Mechanical calendar context (GUIDE §5, amended 2026-08-03): a
    # weekend or federal-holiday digest states so in its header — the
    # SAME fedcal sentence the live page shows, through the same shared
    # function, so the two surfaces can never explain a quiet day
    # differently. Absent (not faked) on ordinary business days.
    day_context = fedcal.reduced_publishing(date)
    if day_context:
        label = ("Weekend note" if day_context["kind"] == "weekend"
                 else "Federal holiday note")
        lines += [f"**{label}:** {day_context['note']}", ""]
    # The frozen day view (GUIDE §5, amended 2026-08-03): the digest
    # links its day's complete observed listing when one exists — only
    # days the item journal covers have one, so the link is emitted
    # exactly for those.
    first = _journal_first_day(conn)
    if first and date >= first:
        lines += [
            (f"[Full observed listing for this day](day/{date}.html) — "
             "every item our collectors observed for this publication "
             "day, mechanical rules applied, frozen at end of day. This "
             "digest is the canonical record."),
            "",
        ]
    lines += [
        "All items below cite the govinfo package (and granule, where applicable) they",
        "summarize. Selection is mechanical; each item states the rule that included",
        "it. See the Coverage Statement at the end for a full accounting of what was",
        "published, what was summarized, and what was excluded and why.",
        "",
        "---",
        "",
    ]
    return lines


def _plain_line(item):
    """The labeled plain-language rendering (GUIDE §2): omitted entirely
    when no plain restatement exists — never fabricated."""
    plain = item.get("plain")
    if not plain:
        return []
    return [f"  - *In plain terms:* {_one_line(plain)}"]


# Display-only case normalization for ALL-CAPS source headings (disclosed in
# the Methodology section). Tokens with digits/periods and known acronyms
# keep their casing; everything else is title-cased with small words lowered.
_SMALL_WORDS = {
    "of", "the", "to", "for", "and", "in", "on", "a", "an", "or",
    "with", "from", "within", "against", "by", "at", "as",
}
_ACRONYMS = {
    "US", "USA", "USMCA", "NDAA", "FY", "FAA", "EPA", "NRC", "ERISA", "NASA",
    "FEMA", "FCC", "FDA", "FERC", "DOD", "DOE", "DHS", "HHS", "IRS", "VA",
    "AI", "II", "III", "IV", "COVID", "GAO", "CBO", "NATO", "UN", "EO",
}



def _claimed_day(meta):
    """Agency-claimed publication day as 'YYYY-MM-DD' (Eastern), or None.
    Feeds use RFC 822 pubDates; some sources emit ISO. The claimed date is
    the agency's assertion (GUIDE §7 T3/T4) — parsed, never trusted over
    the separately stored observation date.

    Zone-aware claims resolve to the federal publication day (GUIDE §3:
    the calendar date in Washington, D.C.) via the same helper that files
    `date_issued` — a 20:30 -0400 pubDate belongs to that Eastern day,
    not the UTC day that has already rolled over (review D1: the UTC
    comparison misfiled evening releases as backfill). A zoneless claim
    is taken at face value, matching agencies._issue_day's ISO branch:
    with no zone stated there is nothing honest to convert."""
    raw = (meta.get("claimed_published_at") or "").strip()
    if not raw:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        parsed = None
    if parsed is not None:
        if parsed.tzinfo is not None:
            return publication_date(parsed)
        return parsed.strftime("%Y-%m-%d")
    if re.match(r"^\d{4}-\d{2}-\d{2}", raw):
        return raw[:10]
    # Third tier (GUIDE §3, added 2026-08-06): publisher formats neither
    # reader handles — Drupal sites emit their site date format in
    # <pubDate> ("Wed, 08/05/2026 - 08:00", "July 17, 2026"). Imported
    # inside the function on purpose: agencies pulls the HTTP stack, and
    # a report-only render must keep working even when the fetch layer
    # cannot import (the same reason scripts/digest.py defers analysis).
    from .agencies import claimed_day_from_text
    return claimed_day_from_text(raw)


def _normalize_official_url(url):
    """One document's identity across ingestion channels (GUIDE §3
    corroboration amendment, 2026-08-03): scheme dropped (http/https
    collapse), host lowercased with a leading www. removed, fragment
    dropped, utm_* tracking parameters dropped, trailing slash
    stripped. Deliberately conservative: two URLs normalize together
    only when the publisher's own host, path, and substantive query are
    identical — title similarity NEVER merges anything (measured
    2026-08-03: three DOJ job postings shared one title across three
    distinct URLs). Returns None for absent or non-HTTP URLs, which
    therefore never merge."""
    from urllib.parse import parse_qsl, urlencode, urlsplit

    if not url:
        return None
    parts = urlsplit(str(url).strip())
    if parts.scheme.lower() not in ("http", "https"):
        return None
    host = parts.netloc.lower().removeprefix("www.")
    if not host:
        return None
    path = parts.path.rstrip("/")
    query = urlencode([(k, v)
                       for k, v in parse_qsl(parts.query,
                                             keep_blank_values=True)
                       if not k.lower().startswith("utm_")])
    return f"{host}{path}" + (f"?{query}" if query else "")


def corroborate(entries, *, url_of, is_email):
    """Group same-day entries that share a normalized official URL: one
    document observed through more than one ingestion channel (GUIDE §3
    amendment, 2026-08-03 — operator: de-duplicate the presentation, and
    mark the document as corroborated by multiple ingestion sources).

    Returns ``[(primary, [corroborating entries])]`` preserving the
    input order at each group's first appearance. The primary is the
    first non-email entry (the publisher's own page carries the
    canonical full text; a bulletin may carry a teaser), falling back to
    the first entry seen. Entries without a normalizable URL pass
    through untouched — absence of a URL never merges. The SAME helper
    serves the digest, the live page, and the day view, so the three
    surfaces can never answer "is this one document?" differently."""
    keys = [_normalize_official_url(url_of(e)) for e in entries]
    groups, order = {}, []
    for entry, key in zip(entries, keys):
        if key is None:
            order.append(entry)
        elif key in groups:
            groups[key].append(entry)
        else:
            groups[key] = [entry]
            order.append(key)
    out = []
    for slot in order:
        if isinstance(slot, str) and slot in groups:
            group = groups[slot]
            primaries = [e for e in group if not is_email(e)] or group
            primary = primaries[0]
            out.append((primary, [e for e in group if e is not primary]))
        else:
            out.append((slot, []))
    return out


def _agency_rows(conn, date):
    """(listed, backfill) for digest day `date` (GUIDE §3 dating rule):
    listed = claimed publication day == date, or no parseable claimed date
    and first observed on date; backfill = observed on date but agency-dated
    another day (AGENCYPR-EX-01) — counted, never listed as today's news."""
    rows = [dict(r) for r in conn.execute(
        """
        SELECT e.title, e.agency, e.metadata
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'AGENCYPR' AND p.digest_day = ?
        ORDER BY e.agency, e.title
        """,
        (date,),
    )]
    listed, backfill = [], []
    for r in rows:
        meta = json.loads(r["metadata"] or "{}")
        claimed = _claimed_day(meta)
        r["_meta"], r["_claimed_day"] = meta, claimed
        (listed if claimed == date or claimed is None else backfill).append(r)
    return listed, backfill


def _agency_lines(conn, date):
    """Section 6: attributed agency release titles (GUIDE §2 attributed
    speech; §3 mutable-source disclosure + dating rule). Zero LLM in the
    pilot."""
    rows, backfill = _agency_rows(conn, date)
    # One document, several channels (GUIDE §3 corroboration amendment,
    # 2026-08-03): a release whose canonical URL arrived through more
    # than one ingestion channel is listed once and marked corroborated;
    # every capture stays preserved and counted.
    merged = corroborate(rows,
                         url_of=lambda r: r["_meta"].get("url"),
                         is_email=lambda r: r["_meta"].get("channel") == "email")
    rows = []
    corroborated_total = 0
    for primary, dups in merged:
        primary["_corroborators"] = dups
        if dups:
            corroborated_total += 1
        rows.append(primary)
    lines = [
        "## 6. Agency Announcements",
        "",
        "Official press releases and statements the agencies themselves date",
        f"on {date} (sources listed in the source guide). These are the",
        "agencies' own announcements — official advocacy, quoted and",
        "attributed, not findings of this digest. Agency web content can be",
        "edited or removed without notice; captures and hashes are preserved",
        "per the provenance policy.",
        "",
    ]
    if not rows:
        lines += [("No releases dated this day were observed from active"
                   " sources."), ""]
    by_agency = {}
    for r in rows:
        by_agency.setdefault(r["agency"] or "(unattributed)", []).append(r)
    for agency in sorted(by_agency, key=str.lower):
        lines += [f"#### {agency}", ""]
        for r in by_agency[agency]:
            meta = r["_meta"]
            # The parsed UTC day, not a truncated raw header: slicing an
            # RFC-822 date rendered "Tue, 28 Jul 2026 ..." as "Tue, 28 Jul 26 1",
            # which misstates the year.
            claimed = r.get("_claimed_day") or _claimed_day(meta)
            title = _one_line(r["title"])
            url = meta.get("url")
            # An email bulletin sometimes carries a release that names no
            # canonical page. Citing an unrelated link would be worse than
            # citing none: the captured message is the source of record.
            head = (f"- **[{title}]({url})**" if url else f"- **{title}**")
            if claimed:
                head += f" — dated {claimed} by the agency"
            else:
                head += " — dated by first observation (no agency date given)"
            lines += [
                head,
                "  - Included because: AGENCYPR-SEL-01 — "
                + RULE_DESCRIPTIONS["AGENCYPR-SEL-01"],
            ]
            if meta.get("channel") == "email":
                dkim = (meta.get("dkim") or {}).get("result")
                signed = ("DKIM-verified" if dkim == "pass"
                          else f"DKIM {dkim}" if dkim else "unsigned")
                lines.append(
                    "  - Source: agency email bulletin to this project's"
                    f" subscription, captured and {signed}"
                    + ("" if url else " (the bulletin named no canonical page)")
                )
            elif meta.get("wayback_url"):
                lines.append(
                    f"  - Source: agency newsroom (above) · "
                    f"[independent archive]({meta['wayback_url']})"
                )
            for dup in r.get("_corroborators") or ():
                dmeta = dup["_meta"]
                if dmeta.get("channel") == "email":
                    dkim = (dmeta.get("dkim") or {}).get("result")
                    via = ("the agency's email bulletin to this project's"
                           " subscription"
                           + (", DKIM-verified" if dkim == "pass"
                              else f", DKIM {dkim}" if dkim else ""))
                else:
                    via = "the agency's newsroom feed"
                lines.append(
                    "  - Corroborated: the same release (same canonical"
                    f" URL) also arrived via {via} — one document"
                    " received through two ingestion channels; listed"
                    " once, both captures preserved."
                )
        lines.append("")
    if corroborated_total:
        lines += [
            (f"{corroborated_total} release(s) above arrived through more"
             " than one ingestion channel and are each listed once, marked"
             " \"Corroborated\" in place. Every arrival is captured,"
             " hashed, and counted in the Coverage Statement — the merge"
             " is presentation, not omission."),
            "",
        ]
    if backfill:
        lines += [
            (f"Also observed this day, not listed above: {len(backfill)}"
             " release(s) the agencies date on other days (feed backfill from"
             " newly activated sources). Excluded under AGENCYPR-EX-01;"
             " counted in the Coverage Statement; captures preserved."),
            "",
        ]
    lines += ["---", ""]
    return lines


def _votes_rows(conn, date):
    """(listed, backfill) for digest day `date`. Same shape and the same
    dating rule as :func:`_agency_rows`: a vote belongs to the day the
    chamber records it, not the day we happened to read the index. A vote
    the chamber dates elsewhere inside the lookback window is counted
    under VOTES-EX-01, never listed as today's."""
    rows = [dict(r) for r in conn.execute(
        """
        SELECT e.title, e.agency, e.metadata
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'VOTES' AND p.digest_day = ?
        """,
        (date,),
    )]
    listed, backfill = [], []
    for r in rows:
        try:
            meta = json.loads(r["metadata"] or "{}")
        except (TypeError, ValueError):
            meta = {}
        r["_meta"] = meta
        r["_details"] = meta.get("details") or {}
        claimed = _claimed_day(meta)
        (listed if claimed == date or claimed is None else backfill).append(r)
    return listed, backfill


def _vote_sort_key(row):
    """Chamber, then vote number ascending — the chambers' own ordering
    (GUIDE §3: vote-number order, no rule that ranks one question above
    another). Unnumbered rows sort last within their chamber."""
    details = row["_details"]
    raw = str(details.get("vote_number") or "")
    return (details.get("chamber") or row["agency"] or "",
            0 if raw.isdigit() else 1,
            int(raw) if raw.isdigit() else 0,
            _one_line(row["title"] or ""))


# The order the chambers themselves report a tally in.
_TALLY_ORDER = ("Yea", "Nay", "Present", "Not Voting")


def _vote_item_lines(row):
    details = row["_details"]
    url = row["_meta"].get("url")
    number = str(details.get("vote_number") or "").lstrip("0")
    subject = ": ".join(
        p for p in (details.get("issue"), details.get("question")) if p)
    label = f"Vote {number}" if number else "Vote"
    if subject:
        label += f" — {subject}"
    head = f"- **[{label}]({url})**" if url else f"- **{label}**"
    if details.get("result"):
        head += f" — {_one_line(details['result'])}."
    lines = [head]
    title = _one_line(row["title"] or "")
    if title and title != subject:
        lines.append(f"  - {title}")
    tally = details.get("tally") or {}
    if tally:
        # Fixed order, not the stored dict's: metadata is serialized with
        # sort_keys, which would print "Nay … Yea" — alphabetical order of
        # positions is not how a chamber reports a vote.
        ordered = [p for p in _TALLY_ORDER if p in tally]
        ordered += sorted(p for p in tally if p not in _TALLY_ORDER)
        lines.append("  - Tally: "
                     + " · ".join(f"{p} {tally[p]}" for p in ordered))
    lines.append("  - Included because: VOTES-SEL-01 — "
                 + RULE_DESCRIPTIONS["VOTES-SEL-01"])
    source = "  - Source: the chamber's own roll-call record (linked above)"
    if row["_meta"].get("wayback_url"):
        source += f" · [independent archive]({row['_meta']['wayback_url']})"
    lines.append(source)
    return lines


def _votes_lines(conn, date):
    """Section 7: roll-call votes from the chambers' own XML records
    (GUIDE §3 "Recorded votes"). Zero LLM: every figure here is read from
    the published record. Appended as section 7 under the GUIDE §2
    append-only numbering rule — sections 1-6 keep their numbers because
    a reader who cited one must find the same subject there tomorrow."""
    rows, backfill = _votes_rows(conn, date)
    lines = [
        "## 7. Recorded Votes",
        "",
        f"Roll-call votes the chambers themselves record on {date}, in",
        "vote-number order. Every recorded vote in the window is listed:",
        "selection is by existence, not by importance, and no rule here",
        "prefers one question over another. Tallies and member positions",
        "come from the chamber's own published vote record, captured and",
        "hashed like every other source. This is the chambers' vote record",
        "itself; section 1.3 lists the Congressional Record granules in",
        "which votes were printed.",
        "",
    ]
    if not rows:
        lines += ["No recorded votes dated this day were observed.", ""]
    by_chamber: dict = {}
    for row in sorted(rows, key=_vote_sort_key):
        by_chamber.setdefault(
            row["_details"].get("chamber") or row["agency"] or "(chamber not stated)",
            []).append(row)
    for chamber, group in by_chamber.items():
        lines += [f"#### {chamber}", ""]
        for row in group:
            lines += _vote_item_lines(row)
        lines.append("")
    if backfill:
        lines += [
            (f"Also observed this day, not listed above: {len(backfill)}"
             " recorded vote(s) the chambers date on other days (the index"
             " lookback window reaches back further than one day). Excluded"
             " under VOTES-EX-01; counted in the Coverage Statement;"
             " captures preserved."),
            "",
        ]
    lines += ["---", ""]
    return lines


def _billaction_sort_key(row):
    """House measures then Senate, bill before resolution, by number —
    the clerical ordering of a chamber's own calendar. It ranks nothing
    (GUIDE §3: no rule may prefer one measure over another); rows whose
    type the adapter did not recognise sort last, deterministically."""
    from .agencies import BILL_TYPE_ORDER

    details = row["_details"]
    bill_type = str(details.get("bill_type") or "")
    number = str(details.get("bill_number") or "")
    order = (BILL_TYPE_ORDER.index(bill_type) if bill_type in BILL_TYPE_ORDER
             else len(BILL_TYPE_ORDER))
    return (order, 0 if number.isdigit() else 1,
            int(number) if number.isdigit() else 0,
            _one_line(row["title"] or ""))


def _billaction_item_lines(row):
    from .agencies import _ordinal

    details = row["_details"]
    url = row["_meta"].get("url")
    title = _one_line(row["title"] or "") or details.get("designation") or "Bill action"
    head = f"- **[{title}]({url})**" if url else f"- **{title}**"
    lines = [head]
    action = _one_line(details.get("action_text") or "")
    if action:
        lines.append(f"  - Action: {action}")
    chamber = _one_line(details.get("origin_chamber") or "")
    congress = _one_line(str(details.get("congress") or ""))
    context = []
    if congress.isdigit():
        context.append(f"{_ordinal(int(congress))} Congress")
    if chamber:
        context.append(f"originated in the {chamber}")
    if context:
        lines.append("  - " + " · ".join(context))
    lines.append("  - Included because: BILLACTIONS-SEL-01 — "
                 + RULE_DESCRIPTIONS["BILLACTIONS-SEL-01"])
    source = ("  - Source: the Library of Congress's bill-status record via the"
              " Congress.gov API; the bill page is linked above")
    if row["_meta"].get("wayback_url"):
        source += f" · [independent archive]({row['_meta']['wayback_url']})"
    lines.append(source)
    return lines


def _presact_rows(conn, date):
    """(listed, backfill) presidential actions for the digest day.

    The same GUIDE §3 dating split section 6 applies to agency releases:
    an action the White House dated on another day is counted under
    PRESACT-EX-01, never listed as today's news. That matters most on
    first activation, when the feeds carry months of history."""
    rows = [dict(r) for r in conn.execute(
        """
        SELECT e.title, e.doc_type, e.metadata
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'PRESACT' AND p.digest_day = ?
        ORDER BY e.doc_type, e.title
        """,
        (date,),
    )]
    listed, backfill = [], []
    for r in rows:
        meta = json.loads(r["metadata"] or "{}")
        claimed = _claimed_day(meta)
        r["_meta"], r["_claimed_day"] = meta, claimed
        (listed if claimed == date or claimed is None else backfill).append(r)
    return listed, backfill


# The publisher's classes, in the order section 9 renders them. Kept here
# rather than derived from the rules so the section's reading order is a
# presentation decision, not an accident of registry order.
_PRESACT_SUBSECTIONS = (
    ("9.1", "EO", "Executive Orders", "executive order"),
    ("9.2", "PROCLAMATION", "Proclamations", "proclamation"),
    ("9.3", "MEMORANDUM", "Presidential Memoranda", "presidential memorandum"),
    ("9.4", "PRESACTION", "Other Presidential Actions", "presidential action"),
    ("9.5", "NOMINATION", "Nominations and Appointments", "nomination"),
)


def _presact_lines(conn, date):
    """Section 9: presidential actions as the White House itself
    published them (GUIDE §3; activated 2026-08-06). Appended as section
    9 under the §2 append-only numbering rule; sections 1-8 keep their
    numbers.

    Register: GUIDE §2's attributed-speech rule applies here in full
    (operator, 2026-08-06) — the digest's own prose attributes. Titles
    are the publisher's words and render verbatim, never reworded, per
    §2's scope amendment."""
    rows, backfill = _presact_rows(conn, date)
    # One document through two channels: both whitehouse.gov feeds carry
    # executive orders, and an order in both arrives twice with the same
    # canonical URL. The standing corroboration rule (GUIDE §3, 2026-08-03)
    # lists it once and marks it — the same helper the other sections use,
    # so no surface can answer "is this one document?" differently.
    merged = corroborate(rows,
                         url_of=lambda r: r["_meta"].get("url"),
                         is_email=lambda r: r["_meta"].get("channel") == "email")
    rows, corroborated_total = [], 0
    for primary, dups in merged:
        primary["_corroborators"] = dups
        if dups:
            corroborated_total += 1
        rows.append(primary)

    lines = [
        "## 9. Presidential Actions",
        "",
        "Source: the Executive Office of the President, as published on",
        f"whitehouse.gov and observed {date}. These are the President's own",
        "instruments — executive orders, proclamations, memoranda — carried",
        "here as the White House published them, days before the Federal",
        "Register compiles them into section 3.",
        "",
        ("Register (GUIDE §2): titles are the publisher's words and appear"
         " verbatim; any prose of ours about them is attributed, exactly as"
         " it is for agency releases. This section states what the White"
         " House published, never whether it was significant."),
        "",
    ]
    if corroborated_total:
        lines += [
            (f"{corroborated_total} action(s) below arrived through both"
             " whitehouse.gov feeds; each is listed once and marked"
             " corroborated, with every observation preserved."),
            "",
        ]
    if not rows:
        lines += [
            ("No presidential actions dated this day were observed. The White"
             " House publishes on its own schedule; an action taken today may"
             " appear in a later digest, and one dated earlier is counted"
             " under PRESACT-EX-01 rather than listed as today's news."),
            "",
        ]
    for number, doc_type, heading, _word in _PRESACT_SUBSECTIONS:
        group = [r for r in rows if r["doc_type"] == doc_type]
        if not group and not rows:
            continue          # an empty day says so once, above
        lines += [f"### {number} {heading}", ""]
        if not group:
            lines += [f"No {heading.lower()} were observed this day.", ""]
            continue
        for row in group:
            lines += _presact_item_lines(row)
        lines.append("")
    if backfill:
        lines += [
            (f"{len(backfill)} presidential action(s) the White House dates on"
             " another day were observed today and are counted under"
             " PRESACT-EX-01 in the Coverage Statement, not listed above."),
            "",
        ]
    lines += ["---", ""]
    return lines


def _presact_item_lines(row):
    """One presidential action. The title is the publisher's, verbatim."""
    meta, url = row["_meta"], (row["_meta"].get("url") or "")
    title = row["title"] or "(untitled)"
    head = f"- **{title}**" if not url else f"- **[{title}]({url})**"
    lines = [head]
    rule = {
        "EO": "PRESACT-SEL-01",
        "PROCLAMATION": "PRESACT-SEL-02",
        "MEMORANDUM": "PRESACT-SEL-03",
    }.get(row["doc_type"], "PRESACT-SEL-04")
    claimed = row.get("_claimed_day")
    if claimed:
        lines.append(f"  - Published by the White House {claimed}")
    lines.append(f"  - Included because: {rule} — {RULE_DESCRIPTIONS[rule]}")
    if row.get("_corroborators"):
        lines.append(f"  - Corroborated: also observed through"
                     f" {len(row['_corroborators'])} other White House feed(s)")
    if meta.get("wayback_url"):
        lines.append(f"  - [independent archive]({meta['wayback_url']})")
    return lines


def _billactions_lines(conn, date):
    """Section 8: bill actions from the Library of Congress's bill-status
    record (GUIDE §3 "Bill actions"). Zero LLM — the action sentence is the
    publisher's own. Appended as section 8 under the GUIDE §2 append-only
    numbering rule; sections 1-7 keep their numbers."""
    rows = [dict(r) for r in conn.execute(
        """
        SELECT e.title, e.agency, e.metadata
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'BILLACTIONS' AND p.digest_day = ?
        """,
        (date,),
    )]
    for row in rows:
        try:
            meta = json.loads(row["metadata"] or "{}")
        except (TypeError, ValueError):
            meta = {}
        row["_meta"] = meta
        row["_details"] = meta.get("details") or {}
    lines = [
        "## 8. Bill Actions",
        "",
        f"What the chambers did with individual measures on {date}, as the",
        "Library of Congress's own bill-status record states it. Every action",
        "in the ingestion window is listed, in bill-designation order:",
        "selection is by existence, not by importance, and no rule here",
        "prefers one measure over another. Section 2 lists the text of bills",
        "published this day; this section lists what happened to them.",
        "",
        ("Publication lag: the record dates an action by the day the chamber"
         " took it and publishes it the following morning, so this section"
         " fills in after the day it describes has ended — the same lag the"
         " judicial section carries, and it is restated under Known gaps."),
        "",
    ]
    if not rows:
        lines += ["No bill actions dated this day were observed.", ""]
    for row in sorted(rows, key=_billaction_sort_key):
        lines += _billaction_item_lines(row)
    if rows:
        lines.append("")
    lines += ["---", ""]
    return lines


def _recase_word(word):
    """Title-case one ALL-CAPS word, respecting internal punctuation.

    The naive ``word[:1].upper() + word[1:].lower()`` mangles the two
    shapes the Congressional Record's Extensions of Remarks are full of:
    quoted nicknames — '"SAM"' became '"sam"', because the first
    character is the quote mark, not a letter — and apostrophised
    surnames, where "O'ROURKE" became "O'rourke". Both were latent until
    the live page started titling every CREC granule (F-022): the digest
    only ever fed this function floor-debate headings, which carry
    neither shape.

    Capitalize the first LETTER, and any letter following an apostrophe
    or hyphen — except a trailing possessive s, so "SAMUEL'S" stays
    "Samuel's" and does not become "Samuel'S".
    """
    out, seen_letter = [], False
    for i, ch in enumerate(word):
        if not ch.isalpha():
            out.append(ch)
            continue
        prev = word[i - 1] if i else ""
        # a letter after an apostrophe/hyphen starts a new name part —
        # but a trailing "'s" is a possessive, not a part
        after_break = prev in "'\u2019-" and not (
            prev in "'\u2019" and i == len(word) - 1)
        out.append(ch.upper() if not seen_letter or after_break else ch.lower())
        seen_letter = True
    return "".join(out)


def _display_title(raw):
    text = _one_line(raw)
    letters = [c for c in text if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) / len(letters) < 0.8:
        return text  # mixed-case source titles pass through untouched
    words = []
    for i, word in enumerate(text.split()):
        if any(ch.isdigit() for ch in word) or "." in word or word in _ACRONYMS:
            words.append(word)
        elif word.lower() in _SMALL_WORDS and i != 0:
            words.append(word.lower())
        else:
            words.append(_recase_word(word))
    return " ".join(words)


def _crec_item_lines(item):
    raw = item["granule_title"] or _first_nonempty_line(item["text_head"]) or item["granule_id"]
    title = _truncate(_display_title(raw))
    return [
        f"- **{title}** — {_one_line(item['summary'])}",
        *_plain_line(item),
        _included_line(item),
        _source_line(item["package_id"], item["granule_id"]),
    ]


def _crec_lines(conn, date, items):
    total = _scalar(
        conn,
        "SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)"
        " WHERE e.collection = 'CREC' AND p.digest_day = ?",
        (date,),
    )
    unselected = dict(
        conn.execute(
            """
            SELECT e.doc_type, COUNT(*)
            FROM extracted_texts e JOIN packages p USING (package_id)
            WHERE e.collection = 'CREC' AND p.digest_day = ?
              AND NOT EXISTS (SELECT 1 FROM summaries s
                              WHERE s.package_id = e.package_id
                                AND s.granule_id = e.granule_id
                                AND s.prompt_version = ?)
            GROUP BY e.doc_type
            """,
            (date, config.PROMPT_VERSION),
        )
    )
    crec_items = [i for i in items if i["collection"] == "CREC"]
    floor = [
        i
        for i in crec_items
        if i["inclusion_rule"].startswith("CREC-SEL") and i["inclusion_rule"] != "CREC-SEL-02"
    ]
    votes = [i for i in crec_items if i["inclusion_rule"] == "CREC-SEL-02"]

    # Observation-day filing (GUIDE §3, amended 2026-08-06): the issues
    # in this section are the ones OBSERVED on the digest day; each
    # names its own proceedings date and, where available, the
    # publisher's stamp — the three clocks, disclosed in place.
    issues = conn.execute(
        "SELECT package_id, date_issued, last_modified, first_seen_at"
        " FROM packages WHERE collection = 'CREC' AND digest_day = ?"
        " ORDER BY date_issued",
        (date,),
    ).fetchall()

    lines = ["## 1. Congressional Floor Activity", ""]
    if issues:
        for iss in issues:
            pub = (f" Published by govinfo {iss['last_modified']};"
                   if iss["last_modified"] else "")
            lines.append(
                f"Source: Congressional Record (CREC), issue observed {date}, "
                f"covering proceedings of {iss['date_issued']}.{pub} "
                f"observed by our collector {iss['first_seen_at']}. "
                f"Total issue size: {total} granule(s)."
            )
        lines.append("")
    else:
        lines += [
            (
                "No Congressional Record issue was observed on this day. "
                "The Record for a day's proceedings is typically published "
                "by govinfo the following morning; it appears in the digest "
                "for the day it is observed "
                "([how our clocks work](faq.html#fapds-three-clocks))."
            ),
            "",
        ]
    for number, doc_type, heading, word in (
        ("1.1", "SENATE", "Senate", "Senate"),
        ("1.2", "HOUSE", "House of Representatives", "House"),
    ):
        lines += [f"### {number} {heading}", ""]
        chamber = sorted(
            (i for i in floor if i["doc_type"] == doc_type), key=lambda i: i["granule_id"]
        )
        if chamber:
            for item in chamber:
                lines += _crec_item_lines(item)
            lines.append("")
        else:
            lines += [
                (
                    f"No {word} floor items met the selection thresholds. "
                    f"{unselected.get(doc_type, 0)} floor granule(s) are accounted for in "
                    "the Coverage Statement."
                ),
                "",
            ]
    lines += ["### 1.3 Recorded Votes", ""]
    if votes:
        for item in sorted(votes, key=lambda i: i["granule_id"]):
            lines += _crec_item_lines(item)
        lines.append("")
    else:
        lines += [
            "No recorded votes were published in this issue of the Congressional Record.",
            "",
        ]
    lines += ["---", ""]
    return lines


def _bills_lines(conn, date, items):
    counts = dict(conn.execute(_STAGE_SQL, (date,)))
    total = sum(counts.values())
    selected = sorted(
        (
            i
            for i in items
            if i["collection"] == "BILLS" and i["inclusion_rule"].startswith("BILLS-SEL")
        ),
        key=lambda i: i["package_id"],
    )
    lines = [
        "## 2. Legislation",
        "",
        f"Source: Congressional Bills (BILLS), text versions published {date} to {date}.",
        "",
        "### 2.1 Counts by Stage",
        "",
        "| Stage (bill text version) | Count |",
        "|---|---|",
        f"| Introduced (ih/is) | {counts.get('Introduced', 0)} |",
        f"| Reported (rh/rs) | {counts.get('Reported', 0)} |",
        f"| Engrossed (eh/es) | {counts.get('Engrossed', 0)} |",
        f"| Enrolled (enr) | {counts.get('Enrolled', 0)} |",
        f"| Other versions | {counts.get('Other', 0)} |",
        f"| **Total bill texts published** | **{total}** |",
        "",
        "### 2.2 Bills Listed by Mechanical Rule",
        "",
        "Bills below are listed because they matched at least one listing rule; the",
        "matching rule is stated per item. All other bill texts are counted above and",
        "accounted for in the Coverage Statement.",
        "",
    ]
    if selected:
        for item in selected:
            metadata = item["metadata"]
            label = metadata.get("legis_num") or item["package_id"]
            version = metadata.get("bill_version") or item["doc_type"] or "?"
            title = _one_line(item["title"]) or "(untitled)"
            lines += [
                f"- **{label} ({version}) — {title}** — {_one_line(item['summary'])}",
                *_plain_line(item),
                _included_line(item),
                _source_line(item["package_id"]),
            ]
        lines.append("")
    else:
        lines += [
            f"No bill texts published in this range matched a listing rule; all {total} are",
            "accounted for in the Coverage Statement.",
            "",
        ]
    lines += ["---", ""]
    return lines


def _item_graphics(assets, pages):
    """Graphic assets whose printed page falls in the item's page range."""
    if not pages:
        return []
    try:
        first, last = int(pages["first"]), int(pages["last"])
    except (KeyError, TypeError, ValueError):
        return []
    matched = []
    for asset in assets:
        try:
            page = int(asset["page"])
        except (TypeError, ValueError):
            continue
        if first <= page <= last:
            matched.append(asset)
    matched.sort(key=lambda a: (int(a["page"]), a["gid"]))
    return matched


def _convert_asset(asset, date, out_dir):
    """Copy one extracted asset (TIFF/PNG/...) as a PNG under assets/<date>/."""
    src_rel = asset.get("asset_path")
    if not src_rel:
        return None
    src = Path(src_rel)
    if not src.is_absolute():
        src = config.PROJECT_ROOT / src
    dest_dir = out_dir / "assets" / date
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{asset['gid']}.png"
        with Image.open(src) as img:
            if img.mode == "1":
                img = img.convert("L")
            img.save(dest, format="PNG")
    except (OSError, ValueError):
        return None
    return dest


def _fr_item_lines(item, date, out_dir, assets):
    package_id, granule_id = item["package_id"], item["granule_id"]
    metadata = item["metadata"]
    paren = granule_id
    if metadata.get("cfr"):
        paren += f"; {metadata['cfr']}"
    title = _one_line(item["title"]) or "(untitled)"
    head = f"- **{title}** ({paren}) — {_one_line(item['summary'])}"
    for key, label in (("action", "Action"), ("dates", "Dates")):
        value = metadata.get(key)
        if value:
            head += f" {label}: {_one_line(value).rstrip('.')}."
    lines = [head, *_plain_line(item), _included_line(item),
             _source_line(package_id, granule_id)]

    matched = _item_graphics(assets, metadata.get("pages"))
    total = len(matched)
    embedded = 0
    for position, asset in enumerate(matched[:MAX_GRAPHICS_PER_ITEM], start=1):
        dest = _convert_asset(asset, date, out_dir)
        if dest is None:
            continue
        embedded += 1
        lines.append(
            f"  - ![Graphic from {granule_id} (printed page {asset['page']})]"
            f"(assets/{date}/{dest.name}) "
            f"*Source graphic {position} of {total} from {granule_id}.*"
        )
    if total > embedded:
        pdf_url = _PDF_URL.format(pid=package_id)
        lines.append(
            f"  - *Graphics not rendered here: {total - embedded} of {total} — "
            f"see the [source PDF]({pdf_url}).*"
        )
    return lines, embedded


def _by_agency(subset):
    """Yield (agency heading, items) alphabetically; unstated agency last."""
    groups: dict = {}
    for item in subset:
        groups.setdefault(item["agency"] or None, []).append(item)
    for agency in sorted((a for a in groups if a), key=str.lower):
        yield agency, sorted(groups[agency], key=lambda i: i["granule_id"])
    if None in groups:
        yield "(agency not stated)", sorted(groups[None], key=lambda i: i["granule_id"])


def _fr_lines(conn, date, items, out_dir):
    type_counts = dict(
        conn.execute(
            "SELECT e.doc_type, COUNT(*) FROM extracted_texts e"
            " JOIN packages p USING (package_id)"
            " WHERE e.collection = 'FR' AND p.digest_day = ? GROUP BY e.doc_type",
            (date,),
        )
    )
    total = sum(type_counts.values())
    graphics = _graphics_by_package(conn, date)
    fr_items = [i for i in items if i["collection"] == "FR"]
    rules = [i for i in fr_items if i["inclusion_rule"] == "FR-SEL-01"]
    proposed = [i for i in fr_items if i["inclusion_rule"] == "FR-SEL-02"]
    presidential = [i for i in fr_items if i["inclusion_rule"] == "FR-SEL-03"]
    embedded_total = 0

    lines = [
        "## 3. Federal Register",
        "",
        f"Source: Federal Register (FR), issue of {date}.",
        "",
        "### 3.1 Counts by Document Type",
        "",
        "| Document type | Count |",
        "|---|---|",
        f"| Rules | {type_counts.get('RULE', 0)} |",
        f"| Proposed rules | {type_counts.get('PRORULE', 0)} |",
        f"| Notices | {type_counts.get('NOTICE', 0)} |",
        f"| Presidential documents | {type_counts.get('PRESDOCU', 0)} |",
        f"| **Total FR documents** | **{total}** |",
        "",
    ]
    for heading, subset, none_line in (
        ("### 3.2 Rules Published", rules, "No rules were published in this issue."),
        (
            "### 3.3 Proposed Rules Published",
            proposed,
            "No proposed rules were published in this issue.",
        ),
    ):
        lines += [heading, ""]
        if subset:
            for agency, group in _by_agency(subset):
                lines += [f"#### {agency}", ""]
                for item in group:
                    item_lines, embedded = _fr_item_lines(
                        item, date, out_dir, graphics.get(item["package_id"], [])
                    )
                    lines += item_lines
                    embedded_total += embedded
                lines.append("")
        else:
            lines += [none_line, ""]

    lines += [
        "### 3.4 Notices and Presidential Documents",
        "",
        "Notices are summarized only when they match a listing rule; all are counted",
        "in 3.1 and in the Coverage Statement. Presidential documents in the FR are",
        "always listed.",
        "",
    ]
    if presidential:
        for item in sorted(presidential, key=lambda i: i["granule_id"]):
            item_lines, embedded = _fr_item_lines(
                item, date, out_dir, graphics.get(item["package_id"], [])
            )
            lines += item_lines
            embedded_total += embedded
        lines.append("")
    else:
        lines += ["No notices or presidential documents matched a listing rule.", ""]
    lines += ["---", ""]
    return lines, embedded_total


def _plaw_lines(conn, date, items):
    laws = sorted((i for i in items if i["inclusion_rule"] == "PLAW-SEL-01"),
                  key=lambda i: i["package_id"])
    lines = ["## 4. Enacted Laws", "",
             f"Source: Public and Private Laws (PLAW) published {date}.", ""]
    if laws:
        for item in laws:
            metadata = item["metadata"]
            cite = (metadata.get("citations") or [item["package_id"]])[0]
            head = f"- **{cite} — {_one_line(item['title'] or '(untitled)')}** — " \
                   f"{_one_line(item['summary'])}"
            if metadata.get("approved_date"):
                head += f" Approved: {metadata['approved_date']}."
            lines += [head, *_plain_line(item), _included_line(item),
                      _source_line(item["package_id"])]
        lines.append("")
    else:
        lines += ["No laws were published in this range.", ""]
    lines += ["---", ""]
    return lines


def _by_court(subset):
    """Yield (court heading, opinions) alphabetically; unstated court last."""
    groups: dict = {}
    for item in subset:
        groups.setdefault(item["metadata"].get("court_name") or None, []).append(item)

    def _ordered(group):
        return sorted(group, key=lambda i: (i["package_id"], i["granule_id"]))

    for court in sorted((c for c in groups if c), key=str.lower):
        yield court, _ordered(groups[court])
    if None in groups:
        yield "(court not stated)", _ordered(groups[None])


def _uscourts_item_lines(item):
    metadata = item["metadata"]
    title = _one_line(item["title"]) or "(untitled)"
    details = []
    if metadata.get("case_number"):
        details.append(f"No. {metadata['case_number']}")
    if metadata.get("date_filed"):
        details.append(f"filed {metadata['date_filed']}")
    head = f"- **{title}**"
    if details:
        head += f" ({'; '.join(details)})"
    head += f" — {_one_line(item['summary'])}"
    return [
        head,
        *_plain_line(item),
        _included_line(item),
        _source_line(item["package_id"], item["granule_id"]),
    ]


def _uscourts_lines(conn, date, items):
    """Section 5 — judicial branch (Phase J1). Carries the MANDATORY standing
    completeness disclosure (GUIDE §3): USCOURTS is participation-based and
    is not the complete federal judicial record."""
    cat_counts = dict(
        conn.execute(
            "SELECT e.doc_type, COUNT(*) FROM extracted_texts e"
            " JOIN packages p USING (package_id)"
            " WHERE e.collection = 'USCOURTS' AND p.digest_day = ?"
            " GROUP BY e.doc_type",
            (date,),
        )
    )
    total = sum(cat_counts.values())
    skipped = _scalar(
        conn,
        "SELECT COUNT(*) FROM packages"
        " WHERE collection = 'USCOURTS' AND fetch_status = 'skipped'",
    )
    selected = [
        i
        for i in items
        if i["collection"] == "USCOURTS"
        and (i["inclusion_rule"] or "").startswith("USCOURTS-SEL")
    ]
    lines = [
        "## 5. Judicial Activity",
        "",
        f"Source: United States Courts Opinions (USCOURTS): opinions observed {date}",
        "by our collector; each opinion states its own issue date beside its",
        "listing ([how our clocks work](faq.html#fapds-three-clocks)).",
        "",
        "Completeness disclosure (standing): USCOURTS carries opinions from",
        "approximately 140 participating appellate, district, bankruptcy, and",
        "national federal courts. Unlike the Congressional Record and the Federal",
        "Register, which are the complete official record of their branches,",
        "USCOURTS is participation-based and is NOT the complete federal judicial",
        "record. Courts post opinions with delay — typically over several days —",
        "so a day's digest carries the opinions that became available that day,",
        "whatever date each was issued.",
        "",
        "### 5.1 Appellate and National Court Opinions",
        "",
        "Appellate and national court opinions are summarized; district and",
        "bankruptcy opinions are counted in 5.2 and in the Coverage Statement.",
        "",
    ]
    if selected:
        for court, group in _by_court(selected):
            lines += [f"#### {court}", ""]
            for item in group:
                lines += _uscourts_item_lines(item)
            lines.append("")
    else:
        lines += [
            "No appellate or national court opinions matched a listing rule for this",
            "date; all opinions are counted in 5.2 and accounted for in the Coverage",
            "Statement.",
            "",
        ]
    lines += [
        "### 5.2 Counts by Court Category",
        "",
        "| Court category | Opinions |",
        "|---|---|",
        f"| Appellate | {cat_counts.get('APPELLATE', 0)} |",
        f"| District | {cat_counts.get('DISTRICT', 0)} |",
        f"| Bankruptcy | {cat_counts.get('BANKRUPTCY', 0)} |",
        f"| National | {cat_counts.get('NATIONAL', 0)} |",
        f"| **Total opinions extracted** | **{total}** |",
        "",
        (
            f"Archive-window disclosure (rule USCOURTS-FETCH-01): {skipped} USCOURTS"
            " package(s) have been listed in delta syncs but fell outside the"
            f" {config.USCOURTS_FETCH_WINDOW_DAYS}-day archive window and were not"
            " fetched (global running count across all syncs, not limited to this"
            " date)."
        ),
        "",
        "---",
        "",
    ]
    return lines


def _coverage_lines(conn, date, cov, embedded_total):
    sync_rows = conn.execute(
        "SELECT collection, last_sync_completed_at FROM sync_state ORDER BY collection"
    ).fetchall()
    if sync_rows:
        parts = " · ".join(
            f"{r['collection']}: completed {r['last_sync_completed_at'] or '—'}"
            for r in sync_rows
        )
        sync_line = f"**Sync summary:** {parts}; last watermarks as listed in the header."
    else:
        sync_line = (
            "**Sync summary:** no sync state recorded; watermarks as listed in the header."
        )

    rows = []
    for coll in ("CREC", "BILLS", "FR", "USCOURTS", "PLAW", "AGENCYPR", "VOTES",
                 "BILLACTIONS", "PRESACT"):
        d = cov[coll]
        units = "—" if coll == "BILLS" else str(d["units"])
        rows.append(
            f"| {coll} | {d['packages']} | {units} | {d['summarized']} |"
            f" {d['counted']} | {d['excluded']} |"
        )

    rule_counts: dict = {}
    for coll in cov.values():
        rule_counts.update(coll["rules"])
    # Derived from rule_counts, not a hand-kept tuple: the tuple omitted
    # AGENCYPR-EX-01 while the Coverage Statement promised every exclusion
    # names its rule (review D2), and the next collection added would have
    # repeated the omission. Insertion order follows _coverage's collection
    # order, so the render stays deterministic.
    fired = [
        f"- {rid}: {RULE_DESCRIPTIONS[rid]} — {n} item(s)"
        for rid, n in rule_counts.items()
        if n
    ]
    if not fired:
        fired = ["- No exclusion rules fired today."]

    graphic_counts = dict(
        conn.execute(
            "SELECT ga.classification, COUNT(*) FROM graphic_assets ga"
            " JOIN packages p USING (package_id) WHERE p.digest_day = ?"
            " GROUP BY ga.classification",
            (date,),
        )
    )
    substantive = graphic_counts.get("substantive", 0)
    boilerplate = graphic_counts.get("boilerplate", 0)

    gaps = []
    unfetched = _scalar(
        conn,
        "SELECT COUNT(*) FROM packages WHERE digest_day = ? AND fetch_status != 'fetched'",
        (date,),
    )
    if unfetched:
        gaps.append(f"{unfetched} package(s) were not fetched and are not covered above")
    unextracted = _scalar(
        conn,
        "SELECT COUNT(*) FROM packages p WHERE p.digest_day = ?"
        " AND p.fetch_status = 'fetched'"
        " AND NOT EXISTS (SELECT 1 FROM extracted_texts e"
        "                 WHERE e.package_id = p.package_id)",
        (date,),
    )
    if unextracted:
        gaps.append(
            f"{unextracted} fetched package(s) have no extracted records"
            " (extraction failed or pending)"
        )
    graphics_failed = _scalar(
        conn,
        "SELECT COUNT(*) FROM graphic_assets ga JOIN packages p USING (package_id)"
        " WHERE p.digest_day = ? AND ga.status = 'failed'",
        (date,),
    )
    if graphics_failed:
        gaps.append(
            f"{graphics_failed} graphic asset(s) failed extraction; see the source PDFs"
        )
    # Standing judicial publication-lag disclosure (GUIDE §3 date semantics):
    # rendered whenever USCOURTS data exists for the date or the collection
    # is synced at all.
    uscourts_cov = cov.get("USCOURTS", {})
    uscourts_synced = (
        conn.execute(
            "SELECT 1 FROM sync_state WHERE collection = 'USCOURTS'"
        ).fetchone()
        is not None
    )
    if uscourts_cov.get("packages") or uscourts_cov.get("units") or uscourts_synced:
        gaps.append(
            "courts post opinions with delay; opinions filed on this date may"
            " appear in later syncs"
        )
    # Standing bill-action publication-lag disclosure (GUIDE §3 "Bill
    # actions"): measured on activation, a day's actions enter the
    # Congress.gov record the following morning, so a digest rendered at
    # the end of its own day carries fewer of them than a later re-render.
    if cov.get("BILLACTIONS", {}).get("units"):
        gaps.append(
            "the Library of Congress publishes a day's bill actions the"
            " following morning; actions taken on this date may appear in"
            " later polls"
        )
    known_gaps = "; ".join(gaps) + "." if gaps else "none identified."

    return [
        "## Coverage Statement",
        "",
        "*This section is mandatory and appears in every digest, including days with",
        "no publications. It accounts for every package observed on this digest day",
        "(GUIDE \u00a73, observation-day filing); each package's own date may differ",
        'and is stated where it does. "Excluded" always names the mechanical rule;',
        "there are no unexplained omissions.*",
        "",
        sync_line,
        "",
        (
            "| Collection | Packages observed | Granules/documents | Summarized |"
            " Counted only | Excluded by rule |"
        ),
        "|---|---|---|---|---|---|",
        *rows,
        "",
        "**Exclusion rules applied today:**",
        "",
        *fired,
        "",
        (
            f"**Source graphics:** {substantive + boilerplate} graphic(s) flagged across"
            f" today's documents: {substantive} content graphic(s) (equations, forms, maps,"
            f" annex pages) and {boilerplate} boilerplate (signatures/seals, excluded by rule"
            " FR-GPH-01). Of the content graphics, 0 were analyzed via vision pass"
            f" (vision pass not yet implemented) and {embedded_total} embedded above; the"
            " remainder are viewable in the cited source PDFs."
        ),
        "",
        f"**Known gaps:** {known_gaps}",
        "",
        "*Verification: any item above can be checked against its source in one click",
        "via its govinfo link. Totals in this table are reproducible from the stored",
        f"extraction records for {date}.*",
        "",
        "---",
        "",
    ]


# Static, repo-versioned plain definitions of procedural terms (GUIDE §2
# method transparency). Neutral register — these pass the lexicon scan like
# all generated prose. Keys are matched case-insensitively on word
# boundaries against the rendered document body.
_GLOSSARY = {
    "cloture": "a Senate vote to end debate so a final vote can happen",
    "motion to proceed": "a Senate vote on whether to start considering a bill",
    "engrossed": "the official text of a bill as passed by one chamber",
    "enrolled": "the final text of a bill passed by both chambers, sent to the President",
    "interim final rule": (
        "a rule that takes effect without waiting for public comment,"
        " though comments are still accepted"
    ),
    "direct final rule": (
        "a rule that takes effect automatically unless significant objections arrive"
    ),
    "proposed rule": "a draft regulation published for public comment before adoption",
    "concurrent resolution": (
        "a measure passed by both chambers that does not go to the President"
        " and does not have the force of law"
    ),
    "joint resolution": "a measure that, like a bill, becomes law if passed and signed",
    "incorporation by reference": (
        "making an outside document legally part of a rule without reprinting it"
    ),
    "state implementation plan": (
        "a state's federally-approved plan for meeting national air quality standards"
    ),
    "certificate of compliance": (
        "an official approval that a specific design meets regulatory requirements"
    ),
    "notice of proposed rulemaking": "the formal announcement of a draft regulation",
    "discharge": "a motion to pull a measure out of committee for floor consideration",
    "safety zone": "a temporary area of water that vessels may not enter without permission",
}


def _glossary_lines(body_markdown):
    """'Terms Used Today' — only terms that actually appear in the body.
    Zero tokens: static definitions, mechanical detection."""
    present = [
        term for term in sorted(_GLOSSARY)
        if re.search(rf"\b{re.escape(term)}\b", body_markdown, re.IGNORECASE)
    ]
    if not present:
        return []
    lines = ["## Terms Used Today", ""]
    # Italic terms, not bold: `- **` is the item-block marker that the
    # inclusion-rule validator keys on; glossary entries are not items.
    lines += [f"- *{term}* — {_GLOSSARY[term]}" for term in present]
    lines += ["", "---", ""]
    return lines


def _methodology_lines(date, git_short):
    return [
        "## Methodology",
        "",
        "Selection rules, summarization prompts, and thresholds are versioned in this",
        f"repository and identified by the pipeline version in the header ({git_short}).",
        "Editorial principles — primary sources only, opinion-agnostic prose, mechanical",
        "party-blind selection, full coverage accounting — are defined in",
        (
            "[GUIDE.md](../GUIDE.md) §2. Ruleset in effect: prompt version"
            f" {config.PROMPT_VERSION}; plain-language version"
            f" {config.PLAIN_PROMPT_VERSION}. To reproduce this digest: re-run the"
        ),
        f"report stage against the extracted records for {date}; no upstream re-fetch",
        "is required (GUIDE.md §5).",
        "",
        "*Filing note (2026-08-06, standing): digests from 2026-08-06 file",
        "govinfo packages under their day of first observation — FAPD's three",
        "clocks are explained in the [FAQ](faq.html#fapds-three-clocks). The",
        "Federal Register files under its cover date, on which it is legally",
        "published. Digests before 2026-08-06 filed by each document's own",
        "date; the two Congressional Record issues observed 2026-08-04/05",
        "(proceedings of 08-03/08-04) fell between the freeze and this change",
        "and appear in no digest — disclosed here, not backfilled.*",
        "",
        '*"In plain terms" lines are model-generated restatements of the stored',
        "summaries, derived only from the summary text shown beside them; items",
        "without one had no usable restatement. ALL-CAPS source headings are",
        "case-normalized for display; original casing is preserved at the source",
        "link. Term definitions above are static, repo-versioned prose.*",
        "",
        "License: this digest's compilation and prose are",
        "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (credit",
        "\"FAPD — Free Agentic Publication Digester\"); quoted official",
        "government text is public domain (17 U.S.C. § 105).",
    ]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_citations(markdown, conn):
    for match in _DETAILS_RE.finditer(markdown):
        package_id, granule_id = match.group(1), match.group(2)
        if not conn.execute(
            "SELECT 1 FROM packages WHERE package_id = ?", (package_id,)
        ).fetchone():
            raise ValidationError(f"citation references unknown package {package_id!r}")
        if granule_id and not conn.execute(
            "SELECT 1 FROM extracted_texts WHERE package_id = ? AND granule_id = ?",
            (package_id, granule_id),
        ).fetchone():
            raise ValidationError(
                f"citation references unknown granule {package_id}/{granule_id}"
            )


def _validate_coverage(markdown, conn, date):
    if "## Coverage Statement" not in markdown:
        raise ValidationError("Coverage Statement section is missing")
    section = markdown.split("## Coverage Statement", 1)[1]
    cov = _coverage(conn, date)
    for coll in ("CREC", "BILLS", "FR", "USCOURTS", "PLAW", "AGENCYPR", "VOTES",
                 "BILLACTIONS", "PRESACT"):
        match = re.search(rf"^\| {coll} \| (.+) \|$", section, re.MULTILINE)
        if match is None:
            raise ValidationError(f"coverage row for {coll} is missing")
        cells = [c.strip() for c in match.group(1).split("|")]
        if len(cells) != 5:
            raise ValidationError(f"coverage row for {coll} is malformed")
        try:
            packages = int(cells[0])
            summarized, counted, excluded = (int(c) for c in cells[2:5])
            units = int(cells[1]) if cells[1] != "—" else None
        except ValueError as exc:
            raise ValidationError(f"coverage row for {coll} is not numeric") from exc
        total = units if units is not None else packages
        if summarized + counted + excluded != total:
            raise ValidationError(
                f"coverage arithmetic does not reconcile for {coll}: "
                f"{summarized} + {counted} + {excluded} != {total}"
            )
        expected = cov[coll]
        stated = {"packages": packages, "summarized": summarized,
                  "counted": counted, "excluded": excluded}
        if units is not None:
            stated["units"] = units
        for key, value in stated.items():
            if value != expected[key]:
                raise ValidationError(
                    f"coverage row for {coll} does not match stored records:"
                    f" {key} is {value}, expected {expected[key]}"
                )


def _validate_lexicon(markdown, conn, date):
    """GUIDE §2: the banned lexicon binds OUR prose only — official source
    text renders verbatim and is never gated (scope amendment 2026-08-02).

    The exemption is POSITIONAL (reviews D21/D8): a banned term passes
    only where it sits inside an exact occurrence of an official string —
    a title from any collection ("Landmark Legal Foundation v. EPA", the
    "National Historic Preservation Act"), an official summary, a quoted
    action sentence. This closes both failure directions at once: an
    official case caption can no longer block the digest (D21 — five
    collections' titles were unmasked), and a short official title can no
    longer blind the gate to a violation in surrounding prose the way the
    old global str.replace masking did (D8). It also implements the §2
    official-name exemption: model prose may name a statute or case whose
    official name contains a banned word, verbatim; the same word outside
    such a span still fails. Known honest boundary: a title that falls
    back to the text head's first line is not collected here."""
    officials = [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT s.summary FROM summaries s JOIN packages p USING (package_id)"
            " WHERE s.method = 'official' AND s.prompt_version = ? AND p.digest_day = ?",
            (config.PROMPT_VERSION, date),
        )
    ]
    # Titles are the publisher's own text in EVERY section — bill and law
    # titles, FR document titles, case captions, agency release and
    # measure titles, CREC granule headings. All eight collections, both
    # title tables (GUIDE §2: "Titles quoted verbatim are quoted, not
    # endorsed"). The gate polices our prose, not the government's.
    officials += [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT et.title FROM extracted_texts et"
            " JOIN packages p USING (package_id)"
            " WHERE p.digest_day = ?",
            (date,),
        )
    ]
    officials += [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT g.title FROM granules g"
            " JOIN packages p USING (package_id) WHERE p.digest_day = ?",
            (date,),
        )
    ]
    officials += [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT title FROM packages WHERE digest_day = ?",
            (date,),
        )
    ]
    # Presidential-action titles are the White House's own words, rendered
    # verbatim (GUIDE §2 scope amendment): an order titled with a banned
    # term is still titled that, and the gate binds our prose, not the
    # publisher's.
    officials += [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT et.title FROM extracted_texts et"
            " JOIN packages p USING (package_id)"
            " WHERE et.collection = 'PRESACT' AND p.digest_day = ?",
            (date,),
        )
    ]
    # The action sentence is quoted verbatim too, and it quotes measure
    # titles in turn ("Providing for consideration of H.R. …").
    officials += [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT json_extract(et.metadata, '$.details.action_text')"
            " FROM extracted_texts et JOIN packages p USING (package_id)"
            " WHERE et.collection = 'BILLACTIONS' AND p.digest_day = ?",
            (date,),
        )
    ]
    # URLs are citations, not prose — link slugs echo source headlines
    # (".../historic-multinational-medical-team...") and must not trip the
    # gate. Strip markdown link destinations before scanning.
    scan = re.sub(r"\]\(([^)\s]+)\)", "]( )", markdown)
    exempt = _official_spans(scan, officials)
    for match in _BANNED_RE.finditer(scan):
        if not any(a <= match.start() and match.end() <= b for a, b in exempt):
            raise ValidationError(
                f"banned term {match.group(0)!r} in generated prose")


def _official_spans(scan, officials):
    """Character ranges of `scan` covered by an exact occurrence of an
    official string, in any form it renders: raw, whitespace-normalized
    (_one_line), or display-cased (_display_title re-cases ALL-CAPS
    source titles). Only strings that themselves contain a banned term
    can exempt anything, so the search stays cheap — a typical day has a
    handful of such titles among thousands of official strings."""
    spans = []
    seen = set()
    for text in officials:
        if not text:
            continue
        for form in {text, _one_line(text), _display_title(text)}:
            if not form or form in seen or not _BANNED_RE.search(form):
                continue
            seen.add(form)
            start = scan.find(form)
            while start != -1:
                spans.append((start, start + len(form)))
                start = scan.find(form, start + 1)
    return spans


def _validate_inclusion_lines(markdown):
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("- **"):
            continue
        cursor = index + 1
        found = False
        while cursor < len(lines) and lines[cursor].startswith("  "):
            if "Included because:" in lines[cursor]:
                found = True
            cursor += 1
        if not found:
            raise ValidationError(
                f"item without an 'Included because:' line: {line[:80]!r}"
            )


def validate(markdown, conn, date):
    """Raise :class:`ValidationError` unless the digest meets the contract.

    Checks: (a) every govinfo details citation resolves to stored records;
    (b) the Coverage Statement reconciles and matches the database;
    (c) generated prose contains no banned-lexicon terms (official text —
    titles, official summaries — is exempted positionally: quoted, not
    endorsed, and never gated); (d) every rendered item states its
    inclusion rule.
    """
    _validate_citations(markdown, conn)
    _validate_coverage(markdown, conn, date)
    _validate_lexicon(markdown, conn, date)
    _validate_inclusion_lines(markdown)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _day_in_review_lines(conn, date):
    """The composed synthesis (digests/TEMPLATE.md "Day in Review").

    LLM prose from day_summaries — deliberately NOT masked in the
    banned-lexicon scan; the compose pass gets the strictest scrutiny.
    Omitted entirely when no composition exists (render stays zero-LLM)."""
    from .compose import get_day_summary

    day = get_day_summary(conn, date)
    if not day:
        return []
    return [
        "## Day in Review",
        "",
        day["summary"].strip(),
        "",
        "*Composed from the summarized items below and the day's mechanical",
        "counts; all specifics are cited in their sections.*",
        "",
        "---",
        "",
    ]



# ---------------------------------------------------------------------------
# Post-processing: section quick-reads + table of contents
# ---------------------------------------------------------------------------

# Heading line -> section_summaries key (compose.SECTION_KEYS).
_BLURB_HEADINGS = {
    "### 1.1 Senate": "senate",
    "### 1.2 House of Representatives": "house",
    "### 2.2 Bills Listed by Mechanical Rule": "legislation",
    "### 3.2 Rules Published": "rules",
    "### 3.3 Proposed Rules Published": "proposed",
    "### 3.4 Notices and Presidential Documents": "presidential",
    "## 4. Enacted Laws": "laws",
    "### 5.1 Appellate and National Court Opinions": "judicial",
}


def _inject_section_blurbs(lines, synopses, tags=None):
    """Insert the stored quick-read synopsis and the section's Tags line
    directly under each section heading (LLM prose and discovery keys:
    linted un-masked like all generated text — GUIDE §6 r12a). Sections
    without stored data render unchanged — never fabricated."""
    if not synopses and not tags:
        return lines
    synopses = synopses or {}
    tags = tags or {}
    out = []
    for line in lines:
        out.append(line)
        key = _BLURB_HEADINGS.get(line.strip())
        if key and tags.get(key):
            parts = " · ".join(tags[key]["mechanical"])
            if tags[key]["llm"]:  # model-derived, labeled in place (GUIDE §2)
                parts += " · model keys: " + " · ".join(tags[key]["llm"])
            if parts:
                out += ["", f"Tags: {parts}"]
        if key and synopses.get(key):
            out += ["", f"*In plain terms: {_one_line(synopses[key])}*"]
    return out


def _slug(heading):
    text = re.sub(r"[^\w\s-]", "", heading.lower())
    return re.sub(r"[\s]+", "-", text).strip("-")


def _inject_toc(lines):
    """Clickable Contents block leading the digest (before Day in Review).
    Anchors follow the python-markdown/GitHub slug convention."""
    headings = [ln[3:] for ln in lines if ln.startswith("## ") and ln != "## Contents"]
    if not headings:
        return lines
    toc = ["## Contents", ""]
    toc += [f"- [{h}](#{_slug(h)})" for h in headings]
    toc += ["", "---", ""]
    first = next(i for i, ln in enumerate(lines) if ln.startswith("## "))
    return lines[:first] + toc + lines[first:]


def render(conn, date, out_dir=None):
    """Render the digest for ``date`` and return the written path.

    Deterministic given the database contents (only the generation timestamp
    varies); performs zero LLM calls. The document is validated before the
    file is written — a digest that fails validation raises
    :class:`ValidationError` and leaves no ``.md`` behind.
    """
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(date)):
        raise ValueError(f"date must be YYYY-MM-DD, got {date!r}")
    out_dir = Path(out_dir) if out_dir is not None else Path(config.DIGEST_DIR)
    git_short = _git_short()

    items = _load_items(conn, date)
    lines = _header_lines(conn, date, git_short)
    lines += _day_in_review_lines(conn, date)
    lines += _crec_lines(conn, date, items)
    lines += _bills_lines(conn, date, items)
    fr_lines, embedded_total = _fr_lines(conn, date, items, out_dir)
    lines += fr_lines
    lines += _plaw_lines(conn, date, items)
    lines += _uscourts_lines(conn, date, items)
    lines += _agency_lines(conn, date)
    lines += _votes_lines(conn, date)
    lines += _billactions_lines(conn, date)
    lines += _presact_lines(conn, date)
    lines += _glossary_lines("\n".join(lines))
    lines += _coverage_lines(conn, date, _coverage(conn, date), embedded_total)
    lines += _methodology_lines(date, git_short)

    from .compose import get_section_synopses
    from .tags import get_section_tags

    lines = _inject_section_blurbs(lines, get_section_synopses(conn, date),
                                   get_section_tags(conn, date))
    lines = _inject_toc(lines)

    markdown = "\n".join(lines) + "\n"
    validate(markdown, conn, date)

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{date}.md"
    path.write_text(markdown, encoding="utf-8")
    return path

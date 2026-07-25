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
import json
import re
import subprocess
from pathlib import Path

from PIL import Image

from . import config

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
    "FR-EX-01": "notices counted, not individually summarized",
    "CREC-EX-01": "floor granule below floor-time threshold",
    "CREC-EX-02": "extensions/daily-digest sections (counted)",
}

# CREC-EX-01 mechanical evidence threshold (characters of extracted floor text).
CREC_FLOOR_THRESHOLD_CHARS = 15000

# GUIDE §6 rule 9: at most this many graphics embedded per summarized item;
# the rest are disclosed with a source-PDF link.
MAX_GRAPHICS_PER_ITEM = 2

_DETAILS_BASE = "https://www.govinfo.gov/app/details"
_PDF_URL = "https://www.govinfo.gov/content/pkg/{pid}/pdf/{pid}.pdf"

# Banned lexicon (GUIDE §2): loaded adjectives and motive attribution never
# appear in generated prose. Word-boundary, case-insensitive; multi-word
# phrases tolerate any whitespace between words.
_BANNED_TERMS = (
    "landmark",
    "controversial",
    "historic",
    "unprecedented",
    "sweeping",
    "radical",
    "extreme",
    "momentous",
    "alarming",
    "in an attempt to",
    "aims to appease",
    # Plain-register evaluative framing (the plain-speak layer's failure
    # modes) — GUIDE §2 plain-language rules.
    "red tape",
    "crackdown",
    "cracks down",
    "slams",
    "loophole",
)
_BANNED_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(t).replace(" ", r"\s+") for t in _BANNED_TERMS) + r")\b",
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
    WHERE e.collection = 'BILLS' AND p.date_issued = ?
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
        WHERE s.prompt_version = ? AND p.date_issued = ?
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
        WHERE p.date_issued = ? AND ga.status = 'extracted'
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
    published packages for BILLS (whole-package documents). "Counted only"
    is the remainder so the table always names every unit; the exclusion
    rules list carries the per-rule mechanical counts.
    """
    pv = config.PROMPT_VERSION
    cov = {}
    for coll in ("CREC", "BILLS", "FR"):
        cov[coll] = {
            "packages": _scalar(
                conn,
                "SELECT COUNT(*) FROM packages WHERE collection = ? AND date_issued = ?",
                (coll, date),
            ),
            "units": _scalar(
                conn,
                "SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)"
                " WHERE e.collection = ? AND p.date_issued = ?",
                (coll, date),
            ),
            "summarized": _scalar(
                conn,
                "SELECT COUNT(*) FROM summaries s JOIN packages p USING (package_id)"
                " WHERE p.collection = ? AND p.date_issued = ? AND s.prompt_version = ?",
                (coll, date, pv),
            ),
        }

    ex01 = _scalar(
        conn,
        """
        SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE e.collection = 'CREC' AND p.date_issued = ?
          AND e.doc_type IN ('HOUSE', 'SENATE') AND e.char_count < ?
          AND NOT EXISTS (SELECT 1 FROM summaries s
                          WHERE s.package_id = e.package_id
                            AND s.granule_id = e.granule_id
                            AND s.prompt_version = ?)
        """,
        (date, CREC_FLOOR_THRESHOLD_CHARS, pv),
    )
    ex02 = _scalar(
        conn,
        "SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)"
        " WHERE e.collection = 'CREC' AND p.date_issued = ?"
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

    notices = _scalar(
        conn,
        "SELECT COUNT(*) FROM extracted_texts e JOIN packages p USING (package_id)"
        " WHERE e.collection = 'FR' AND p.date_issued = ? AND e.doc_type = 'NOTICE'",
        (date,),
    )
    fr = cov["FR"]
    fr["counted"] = notices
    fr["excluded"] = fr["units"] - fr["summarized"] - notices
    fr["rules"] = {"FR-EX-01": notices}
    return cov


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------


def _header_lines(conn, date, git_short):
    marks = dict(
        conn.execute("SELECT collection, last_modified_watermark FROM sync_state")
    )
    watermark = " · ".join(f"{c}: {marks.get(c, '—')}" for c in config.COLLECTIONS)
    return [
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
        "All items below cite the govinfo package (and granule, where applicable) they",
        "summarize. Selection is mechanical; each item states the rule that included",
        "it. See the Coverage Statement at the end for a full accounting of what was",
        "published, what was summarized, and what was excluded and why.",
        "",
        "---",
        "",
    ]


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
            words.append(word[:1].upper() + word[1:].lower())
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
        " WHERE e.collection = 'CREC' AND p.date_issued = ?",
        (date,),
    )
    unselected = dict(
        conn.execute(
            """
            SELECT e.doc_type, COUNT(*)
            FROM extracted_texts e JOIN packages p USING (package_id)
            WHERE e.collection = 'CREC' AND p.date_issued = ?
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

    lines = [
        "## 1. Congressional Floor Activity",
        "",
        (
            f"Source: Congressional Record (CREC), daily edition for {date}. "
            f"Total issue size: {total} granule(s)."
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
            " WHERE e.collection = 'FR' AND p.date_issued = ? GROUP BY e.doc_type",
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


_SECTION4_LINES = [
    "## 4. Enacted Laws",
    "",
    "Source: Public and Private Laws (PLAW). PLAW is not yet ingested by this",
    "pipeline version; enacted laws are not covered in this digest.",
    "",
    "---",
    "",
]


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
    for coll in ("CREC", "BILLS", "FR"):
        d = cov[coll]
        units = "—" if coll == "BILLS" else str(d["units"])
        rows.append(
            f"| {coll} | {d['packages']} | {units} | {d['summarized']} |"
            f" {d['counted']} | {d['excluded']} |"
        )

    rule_counts: dict = {}
    for coll in cov.values():
        rule_counts.update(coll["rules"])
    fired = [
        f"- {rid}: {RULE_DESCRIPTIONS[rid]} — {n} item(s)"
        for rid in ("CREC-EX-01", "CREC-EX-02", "FR-EX-01")
        if (n := rule_counts.get(rid, 0))
    ]
    if not fired:
        fired = ["- No exclusion rules fired today."]

    graphic_counts = dict(
        conn.execute(
            "SELECT ga.classification, COUNT(*) FROM graphic_assets ga"
            " JOIN packages p USING (package_id) WHERE p.date_issued = ?"
            " GROUP BY ga.classification",
            (date,),
        )
    )
    substantive = graphic_counts.get("substantive", 0)
    boilerplate = graphic_counts.get("boilerplate", 0)

    gaps = []
    unfetched = _scalar(
        conn,
        "SELECT COUNT(*) FROM packages WHERE date_issued = ? AND fetch_status != 'fetched'",
        (date,),
    )
    if unfetched:
        gaps.append(f"{unfetched} package(s) were not fetched and are not covered above")
    unextracted = _scalar(
        conn,
        "SELECT COUNT(*) FROM packages p WHERE p.date_issued = ?"
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
        " WHERE p.date_issued = ? AND ga.status = 'failed'",
        (date,),
    )
    if graphics_failed:
        gaps.append(
            f"{graphics_failed} graphic asset(s) failed extraction; see the source PDFs"
        )
    known_gaps = "; ".join(gaps) + "." if gaps else "none identified."

    return [
        "## Coverage Statement",
        "",
        "*This section is mandatory and appears in every digest, including days with",
        "no publications. It accounts for every package the sync observed in the data",
        'date range. "Excluded" always names the mechanical rule; there are no',
        "unexplained omissions.*",
        "",
        sync_line,
        "",
        (
            "| Collection | Packages published | Granules/documents | Summarized |"
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
        '*"In plain terms" lines are model-generated restatements of the stored',
        "summaries, derived only from the summary text shown beside them; items",
        "without one had no usable restatement. ALL-CAPS source headings are",
        "case-normalized for display; original casing is preserved at the source",
        "link. Term definitions above are static, repo-versioned prose.*",
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
    for coll in ("CREC", "BILLS", "FR"):
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
    officials = [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT s.summary FROM summaries s JOIN packages p USING (package_id)"
            " WHERE s.method = 'official' AND s.prompt_version = ? AND p.date_issued = ?",
            (config.PROMPT_VERSION, date),
        )
    ]
    scan = markdown
    for text in officials:
        if not text:
            continue
        # Official summaries are quoted verbatim source text, not our prose:
        # mask both the raw and the whitespace-normalized rendering.
        scan = scan.replace(text, " ").replace(_one_line(text), " ")
    match = _BANNED_RE.search(scan)
    if match:
        raise ValidationError(f"banned term {match.group(0)!r} in generated prose")


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
    (c) generated prose contains no banned-lexicon terms (verbatim official
    summaries are masked before scanning); (d) every rendered item states
    its inclusion rule.
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
    lines += _SECTION4_LINES
    lines += _glossary_lines("\n".join(lines))
    lines += _coverage_lines(conn, date, _coverage(conn, date), embedded_total)
    lines += _methodology_lines(date, git_short)

    markdown = "\n".join(lines) + "\n"
    validate(markdown, conn, date)

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{date}.md"
    path.write_text(markdown, encoding="utf-8")
    return path

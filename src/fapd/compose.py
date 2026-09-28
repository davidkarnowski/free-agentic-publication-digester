"""Compose stage: one strong-model pass producing the digest's Day in
Review — a factual synthesis of the day's official activity.

Input is already-compressed material only (stored item summaries plus
mechanical counts — GUIDE §6 rule 6); the corpus is never re-read. Output
is stored in day_summaries so re-rendering a digest costs zero tokens.
The result is LLM prose and is linted un-masked by the report validator.
"""

import json
import logging

from . import config, rules
from .sync import utc_now_iso

logger = logging.getLogger("fapd.compose")

# The complete §2 lexicon, restated verbatim from the canonical constant
# (review D8: this prompt hand-listed 10 of 16 terms — the strongest model
# in the pipeline produced prose the gate then rejected, for a constraint
# it was never given). Substituted with str.replace, not .format, because
# the prompts carry runtime {placeholders} of their own.
_BANNED_CLAUSE = ", ".join(f'"{t}"' for t in config.BANNED_TERMS)

_PROMPT = """You are writing the "Day in Review" opening of a daily digest of official
US government publications. Your ONLY inputs are the item summaries and
mechanical counts below — do not add outside knowledge, do not speculate.

Hard rules (non-negotiable):
- Strictly factual and opinion-agnostic: describe what was published, said,
  or enacted. Never whether it was good, bad, or significant.
- Banned terms — the complete list, enforced verbatim by the render-time
  gate (your prose is rejected if any appears): {banned}. Also banned:
  motive attribution and predictions of outcomes.
- Party-blind, neutral register, plain prose.
- The counts and items are what was OBSERVED on this digest day; a
  document may carry an earlier date of its own (stated per item).
  State counts as observations ("the digest carries N district court
  opinions"), never as totals of what was issued or published that day
  ("N opinions were issued today" overclaims and is wrong).
- Up to 3 short paragraphs (~130-220 words total): first the congressional
  floor picture (both chambers, recorded votes); then the
  executive/regulatory picture (rules, proposed rules, presidential
  documents); then, ONLY when judicial items appear below, the judicial
  picture (appellate/national court opinions — name the courts and what
  each ruling decided, factually). Omit any paragraph whose branch has no
  items. Weave in the counts naturally.
- No headers, no bullet lists, no citations (items below carry their own).

Reply with the paragraphs only.

=== MECHANICAL COUNTS ===
{counts}

=== ITEM SUMMARIES ===
{items}
""".replace("{banned}", _BANNED_CLAUSE)

# The short Day in Review (GUIDE §3a, amended 2026-09-28): the day observed
# documents but none passed a summary rule, so there are no item summaries
# to synthesize. Its inputs are counts and the titles the digest itself
# lists — never a document's text (§6 r4).
_SHORT_PROMPT = """You are writing a short "Day in Review" opening for a daily digest of
official US government publications, on a day when none of the observed
documents met the digest's summary rules. Your ONLY inputs are the
calendar note, mechanical counts, and listed titles below — do not add
outside knowledge, do not speculate, and do not describe what any
document says beyond its title.

Hard rules (non-negotiable):
- Open by saying plainly that this is a short review: few publications
  were observed for this digest day and none met the digest's summary
  rules, so there are no item summaries to draw on. When a calendar note
  is given, give its reason in its own terms (for example, that Sunday
  is not a federal business day).
- Never say or imply that the day's publications were minor, routine,
  unimportant, or insignificant — and never the opposite. Volume is a
  count; significance is not yours to judge.
- Strictly factual and opinion-agnostic. Banned terms — the complete
  list, enforced verbatim by the render-time gate (your prose is
  rejected if any appears): {banned}. Also banned: motive attribution
  and predictions of outcomes.
- Party-blind, neutral register, plain prose.
- The counts are what was OBSERVED on this digest day; state them as
  observations ("the digest carries 225 district court opinions"), never
  as totals of what was issued or published that day.
- Listed titles are the publishers' own words. When you mention one,
  attribute it to its publisher and quote the title exactly, in
  quotation marks; never restate a title as a claim of fact.
- Court opinions appear only as counts by court; name no case.
- One paragraph, about 60-110 words. No headers, no bullet lists, no
  citations.

Reply with the paragraph only.

=== CALENDAR NOTE ===
{calendar}

=== MECHANICAL COUNTS ===
{counts}

=== OPINIONS BY COURT ===
{courts}

=== LISTED TITLES ===
{titles}
""".replace("{banned}", _BANNED_CLAUSE)

#: Collections the digest lists by title under a listing rule
#: (AGENCYPR-SEL-01, VOTES-SEL-01, BILLACTIONS-SEL-01). The short review
#: receives their listed titles, so their raw counts — which include
#: items dated to another day and counted, not listed — are left out of
#: the counts block rather than stated twice with different numbers.
_LISTED_COLLECTIONS = ("AGENCYPR", "VOTES", "BILLACTIONS")

#: Per-class cap on titles handed to the short review: a paragraph of
#: ~100 words cannot use more, and the prompt stays bounded on a heavy
#: listing day.
_SHORT_TITLE_CAP = 12


def compose_day(conn, llm, date):
    """Create (or refresh) the Day in Review for a date. Idempotent by
    (date, PROMPT_VERSION) — but a stored composition is invalidated when
    any item summary for the date is newer than it (late-arriving data,
    e.g. a Record issue published after the first digest run, must never
    leave the synthesis stale against its own items). Returns stats dict."""
    existing = conn.execute(
        "SELECT created_at, kind FROM day_summaries WHERE date = ? AND prompt_version = ?",
        (date, config.COMPOSE_PROMPT_VERSION),
    ).fetchone()
    if existing and existing["kind"] == "short":
        # A short review says nothing passed a summary rule. Once
        # something has, that sentence is false: drop it and compose (or
        # not) from what the day now holds.
        if not rules.select_items(conn, date):
            return {"composed": 0, "skipped_existing": 1,
                    "input_tokens": 0, "output_tokens": 0}
        conn.execute(
            "DELETE FROM day_summaries WHERE date = ? AND prompt_version = ?",
            (date, config.COMPOSE_PROMPT_VERSION),
        )
        logger.info("%s: documents now pass a summary rule — short review withdrawn", date)
    elif existing:
        # Timestamp formats differ in suffix (Z vs +00:00); compare the
        # common YYYY-MM-DDTHH:MM:SS prefix.
        newer = conn.execute(
            """
            SELECT 1 FROM summaries s JOIN packages p ON p.package_id = s.package_id
            WHERE p.digest_day = ? AND s.prompt_version = ?
              AND substr(s.created_at, 1, 19) > substr(?, 1, 19)
            LIMIT 1
            """,
            (date, config.PROMPT_VERSION, existing["created_at"]),
        ).fetchone()
        if not newer:
            return {"composed": 0, "skipped_existing": 1,
                    "input_tokens": 0, "output_tokens": 0}
        conn.execute(
            "DELETE FROM day_summaries WHERE date = ? AND prompt_version = ?",
            (date, config.COMPOSE_PROMPT_VERSION),
        )
        logger.info("%s: newer item summaries found — recomposing Day in Review", date)

    counts = _mechanical_counts(conn, date)
    items = conn.execute(
        """
        SELECT s.package_id, s.granule_id, s.inclusion_rule, s.summary,
               e.doc_type, e.title, e.agency, e.collection
        FROM summaries s
        JOIN extracted_texts e USING (package_id, granule_id)
        JOIN packages p ON p.package_id = s.package_id
        WHERE p.digest_day = ? AND s.prompt_version = ?
        ORDER BY e.collection, e.doc_type, s.package_id, s.granule_id
        """,
        (date, config.PROMPT_VERSION),
    ).fetchall()
    if not items:
        return _compose_short(conn, llm, date)

    item_lines = [
        f"- [{r['collection']}/{r['doc_type'] or '?'}] "
        f"{(r['title'] or '').strip()[:120]}: {r['summary'][:400]}"
        for r in items
    ]
    prompt = _PROMPT.format(
        counts=json.dumps(counts, indent=1, sort_keys=True),
        items="\n".join(item_lines),
    )
    result = llm.complete(
        prompt, purpose="compose:day-in-review", model=config.COMPOSE_MODEL,
        package_id=f"DIGEST-{date}",
    )
    _store_day(conn, date, result, kind="full")
    logger.info("%s: Day in Review composed (%d in / %d out tokens)",
                date, result["input_tokens"], result["output_tokens"])
    _narrate(date, result["text"])
    return {"composed": 1, "skipped_existing": 0,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"]}


def _store_day(conn, date, result, *, kind, kind_version=None):
    conn.execute(
        "INSERT INTO day_summaries (date, prompt_version, model, summary,"
        " input_tokens, output_tokens, created_at, kind, kind_version)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (date, config.COMPOSE_PROMPT_VERSION, result["model"], result["text"],
         result["input_tokens"], result["output_tokens"], utc_now_iso(),
         kind, kind_version),
    )
    conn.commit()


def _narrate(date, text):
    try:
        from fapd.tts import get_tts_service
        audio_path = config.SITE_DIR / "assets" / "audio" / f"digest-{date}.mp3"
        get_tts_service().generate_audio(text, audio_path)
    except Exception as e:  # noqa: BLE001
        logger.warning("%s: Day in Review TTS narration failed: %s", date, e)


def _compose_short(conn, llm, date):
    """The short Day in Review (GUIDE §3a, amended 2026-09-28), for a day
    with observed documents of which none passed a summary rule.

    Two days get nothing, as before: a day that observed nothing at all,
    and a day where documents DID pass a rule but no summary exists —
    that is a missing layer, disclosed as one, not a quiet day, and a
    review saying "nothing met the summary rules" would be false.

    The text clears the render's own lexicon gate BEFORE storage; a
    review that fails is not stored and the digest renders without a Day
    in Review, so a short review can never block a day's publication."""
    zero = {"composed": 0, "skipped_existing": 0, "input_tokens": 0, "output_tokens": 0}
    if rules.select_items(conn, date):
        logger.info("%s: documents passed a summary rule but none is summarized"
                    " — no Day in Review composed", date)
        return zero
    inputs = _short_review_inputs(conn, date)
    if inputs is None:
        logger.info("%s: nothing observed — no Day in Review composed", date)
        return zero

    prompt = _SHORT_PROMPT.format(**inputs)
    result = llm.complete(
        prompt, purpose="compose:short-review", model=config.COMPOSE_MODEL,
        package_id=f"DIGEST-{date}",
    )
    spent = {"input_tokens": result["input_tokens"],
             "output_tokens": result["output_tokens"]}

    from .report import ValidationError, _validate_lexicon
    try:
        _validate_lexicon(result["text"], conn, date)
    except ValidationError as exc:
        logger.warning("%s: short review not stored — %s", date, exc)
        return {**zero, **spent, "gated": 1}

    _store_day(conn, date, result, kind="short",
               kind_version=config.SHORT_REVIEW_PROMPT_VERSION)
    logger.info("%s: short Day in Review composed (%d in / %d out tokens)",
                date, result["input_tokens"], result["output_tokens"])
    _narrate(date, result["text"])
    return {**zero, **spent, "composed": 1, "short": 1}


def _short_review_inputs(conn, date):
    """The short review's prompt fields, or None when nothing was observed.

    Titles come from the report's own listing helpers (the §3 dating rule
    and the corroboration merge), so the review can only name what the
    digest itself lists under the same rules — never a second answer to
    the same editorial question."""
    from . import fedcal, report

    counts = _mechanical_counts(conn, date)
    if not counts:
        return None
    unlisted = {k: n for k, n in counts.items()
                if k.split("/", 1)[0] not in _LISTED_COLLECTIONS}

    courts = {}
    for row in conn.execute(
        "SELECT e.doc_type, e.metadata FROM extracted_texts e"
        " JOIN packages p USING (package_id)"
        " WHERE e.collection = 'USCOURTS' AND p.digest_day = ?",
        (date,),
    ):
        try:
            name = json.loads(row["metadata"] or "{}").get("court_name")
        except (TypeError, ValueError):
            name = None
        key = f"{name or 'court not stated'} ({(row['doc_type'] or '?').lower()})"
        courts[key] = courts.get(key, 0) + 1

    agency, _ = report._agency_rows(conn, date)
    merged = report.corroborate(
        agency, url_of=lambda r: r["_meta"].get("url"),
        is_email=lambda r: r["_meta"].get("channel") == "email")
    votes, _ = report._votes_rows(conn, date)
    actions = [dict(r) for r in conn.execute(
        "SELECT e.title, e.metadata FROM extracted_texts e"
        " JOIN packages p USING (package_id)"
        " WHERE e.collection = 'BILLACTIONS' AND p.digest_day = ?"
        " ORDER BY e.title",
        (date,),
    )]

    def capped(label, lines):
        out = [f"{label} ({len(lines)} listed):"] + lines[:_SHORT_TITLE_CAP]
        if len(lines) > _SHORT_TITLE_CAP:
            out.append(f"- ... and {len(lines) - _SHORT_TITLE_CAP} more")
        return out

    titles = []
    agency_lines = [f'- {p["agency"] or "agency not stated"}: "{report._one_line(p["title"])}"'
                    for p, _dups in merged]
    if agency_lines:
        titles += capped("Agency releases dated this day by the agency", agency_lines)
    vote_lines = []
    for r in votes:
        d = r["_details"]
        subject = ": ".join(x for x in (d.get("issue"), d.get("question")) if x)
        text = subject or report._one_line(r["title"] or "")
        result = f" — {report._one_line(d['result'])}" if d.get("result") else ""
        vote_lines.append(f'- {r["agency"] or "chamber not stated"}: "{text}"{result}')
    if vote_lines:
        titles += capped("Recorded votes dated this day by the chamber", vote_lines)
    action_lines = []
    for r in actions:
        try:
            d = json.loads(r["metadata"] or "{}").get("details") or {}
        except (TypeError, ValueError):
            d = {}
        act = report._one_line(d.get("action_text") or "")
        action_lines.append(f'- "{report._one_line(r["title"] or "")}"'
                            + (f" — action: \"{act}\"" if act else ""))
    if action_lines:
        titles += capped("Bill actions dated this day by the Library of Congress",
                         action_lines)

    context = fedcal.reduced_publishing(date)
    return {
        "calendar": context["note"] if context else "(an ordinary federal business day)",
        "counts": json.dumps(unlisted, indent=1, sort_keys=True) if unlisted else "(none)",
        "courts": "\n".join(f"- {k}: {n}" for k, n in sorted(courts.items())) or "(none)",
        "titles": "\n".join(titles) or "(none)",
    }



def _mechanical_counts(conn, date):
    rows = conn.execute(
        """
        SELECT e.collection, COALESCE(e.doc_type, '?') AS doc_type, COUNT(*) AS n
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE p.digest_day = ? GROUP BY 1, 2 ORDER BY 1, 2
        """,
        (date,),
    ).fetchall()
    return {f"{r['collection']}/{r['doc_type']}": r["n"] for r in rows}


def get_day_summary(conn, date):
    row = conn.execute(
        "SELECT summary, model, kind FROM day_summaries WHERE date = ? AND prompt_version = ?",
        (date, config.COMPOSE_PROMPT_VERSION),
    ).fetchone()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Section quick-read synopses (GUIDE §2 plain-language rules apply)
# ---------------------------------------------------------------------------

# Digest section -> (inclusion-rule prefix test, optional doc_type filter).
SECTION_KEYS = {
    "senate": ("CREC-SEL", "SENATE"),
    "house": ("CREC-SEL", "HOUSE"),
    "legislation": ("BILLS-SEL", None),
    "rules": ("FR-SEL-01", None),
    "proposed": ("FR-SEL-02", None),
    "presidential": ("FR-SEL-03", None),
    "laws": ("PLAW-SEL", None),
    "judicial": ("USCOURTS-SEL", None),
}

_SECTION_PROMPT = """You are writing one-sentence "quick-read" synopses for sections of a daily
digest of official US government publications. For EACH section below,
write ONE sentence (max ~30 words) in plain everyday English saying what
that section contains today, weaving in the count naturally.

Hard rules (non-negotiable):
- Use ONLY facts present in the item summaries given. Add nothing.
- Strictly factual and opinion-agnostic; NO evaluative framing, NO motive
  attribution, NO predictions. Banned terms, enforced verbatim by the
  render-time gate: {banned}.
- Name the one or two most concrete specifics, then characterize the rest
  plainly (for example: "5 final rules, led by X; the rest are routine
  safety zones and aviation updates").

Output format: STRICT JSON, one object mapping each section key to its
one-sentence synopsis. No markdown fences, no other keys.

{sections}
""".replace("{banned}", _BANNED_CLAUSE)


def _section_items(conn, date):
    rows = conn.execute(
        """
        SELECT s.inclusion_rule, s.summary, e.doc_type, e.title
        FROM summaries s
        JOIN packages p ON p.package_id = s.package_id
        LEFT JOIN extracted_texts e USING (package_id, granule_id)
        WHERE p.digest_day = ? AND s.prompt_version = ?
        ORDER BY s.package_id, s.granule_id
        """,
        (date, config.PROMPT_VERSION),
    ).fetchall()
    grouped = {}
    for r in rows:
        for key, (prefix, doc_type) in SECTION_KEYS.items():
            if r["inclusion_rule"].startswith(prefix) and (
                doc_type is None or r["doc_type"] == doc_type
            ):
                if r["inclusion_rule"] == "CREC-SEL-02" and key in ("senate", "house"):
                    continue  # votes render in their own subsection
                grouped.setdefault(key, []).append(r)
                break
    return grouped


def compose_sections(conn, llm, date):
    """One batched call producing per-section quick-read synopses. Idempotent
    by (date, key, SECTION_PROMPT_VERSION); invalidated when any item summary
    for the date is newer than the stored synopses."""
    existing = conn.execute(
        "SELECT MIN(created_at) AS oldest FROM section_summaries"
        " WHERE date = ? AND prompt_version = ?",
        (date, config.SECTION_PROMPT_VERSION),
    ).fetchone()
    if existing and existing["oldest"]:
        newer = conn.execute(
            """
            SELECT 1 FROM summaries s JOIN packages p ON p.package_id = s.package_id
            WHERE p.digest_day = ? AND s.prompt_version = ?
              AND substr(s.created_at, 1, 19) > substr(?, 1, 19) LIMIT 1
            """,
            (date, config.PROMPT_VERSION, existing["oldest"]),
        ).fetchone()
        if not newer:
            return {"composed": 0, "skipped_existing": 1,
                    "input_tokens": 0, "output_tokens": 0}
        conn.execute(
            "DELETE FROM section_summaries WHERE date = ? AND prompt_version = ?",
            (date, config.SECTION_PROMPT_VERSION),
        )
        logger.info("%s: newer summaries — recomposing section synopses", date)

    grouped = _section_items(conn, date)
    if not grouped:
        return {"composed": 0, "skipped_existing": 0,
                "input_tokens": 0, "output_tokens": 0}
    blocks = []
    for key, rows in grouped.items():
        lines = "\n".join(
            f"- {(r['title'] or '').strip()[:100]}: {r['summary'][:250]}" for r in rows
        )
        blocks.append(f"=== SECTION key={key} ({len(rows)} items) ===\n{lines}")
    result = llm.complete(
        _SECTION_PROMPT.format(sections="\n\n".join(blocks)),
        purpose="sections:quick-read", model=config.PLAIN_MODEL,
        package_id=f"DIGEST-{date}",
    )
    import re as _re

    text = result["text"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rstrip().removesuffix("```")
    try:
        mapping = json.loads(text)
    except ValueError:
        mapping = {}
        m = _re.search(r"\{.*\}", text, _re.DOTALL)
        if m:
            try:
                mapping = json.loads(m.group(0))
            except ValueError:
                pass
    written = 0
    share = result["input_tokens"] // max(len(grouped), 1)
    for key in grouped:
        synopsis = mapping.get(key)
        if isinstance(synopsis, str) and synopsis.strip():
            conn.execute(
                "INSERT INTO section_summaries (date, section_key, prompt_version,"
                " model, synopsis, input_tokens, output_tokens, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (date, key, config.SECTION_PROMPT_VERSION, result["model"],
                 " ".join(synopsis.split()), share,
                 result["output_tokens"] // max(len(grouped), 1), utc_now_iso()),
            )
            written += 1
    conn.commit()
    logger.info("%s: %d/%d section synopses written", date, written, len(grouped))
    return {"composed": written, "skipped_existing": 0,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"]}


def get_section_synopses(conn, date):
    return {
        r["section_key"]: r["synopsis"]
        for r in conn.execute(
            "SELECT section_key, synopsis FROM section_summaries"
            " WHERE date = ? AND prompt_version = ?",
            (date, config.SECTION_PROMPT_VERSION),
        )
    }

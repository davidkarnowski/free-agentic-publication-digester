"""Compose stage: one strong-model pass producing the digest's Day in
Review — a factual synthesis of the day's official activity.

Input is already-compressed material only (stored item summaries plus
mechanical counts — GUIDE §6 rule 6); the corpus is never re-read. Output
is stored in day_summaries so re-rendering a digest costs zero tokens.
The result is LLM prose and is linted un-masked by the report validator.
"""

import json
import logging

from . import config
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


def compose_day(conn, llm, date):
    """Create (or refresh) the Day in Review for a date. Idempotent by
    (date, PROMPT_VERSION) — but a stored composition is invalidated when
    any item summary for the date is newer than it (late-arriving data,
    e.g. a Record issue published after the first digest run, must never
    leave the synthesis stale against its own items). Returns stats dict."""
    existing = conn.execute(
        "SELECT created_at FROM day_summaries WHERE date = ? AND prompt_version = ?",
        (date, config.COMPOSE_PROMPT_VERSION),
    ).fetchone()
    if existing:
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
        logger.info("%s: no summarized items — no Day in Review composed", date)
        return {"composed": 0, "skipped_existing": 0, "input_tokens": 0, "output_tokens": 0}

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
    conn.execute(
        "INSERT INTO day_summaries (date, prompt_version, model, summary,"
        " input_tokens, output_tokens, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (date, config.COMPOSE_PROMPT_VERSION, result["model"], result["text"],
         result["input_tokens"], result["output_tokens"], utc_now_iso()),
    )
    conn.commit()
    logger.info("%s: Day in Review composed (%d in / %d out tokens)",
                date, result["input_tokens"], result["output_tokens"])

    try:
        from fapd.tts import get_tts_service
        audio_path = config.SITE_DIR / "assets" / "audio" / f"digest-{date}.mp3"
        get_tts_service().generate_audio(result["text"], audio_path)
    except Exception as e:
        logger.warning("%s: Day in Review TTS narration failed: %s", date, e)

    return {"composed": 1, "skipped_existing": 0,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"]}



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
        "SELECT summary, model FROM day_summaries WHERE date = ? AND prompt_version = ?",
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

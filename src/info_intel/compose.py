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

logger = logging.getLogger("info_intel.compose")

_PROMPT = """You are writing the "Day in Review" opening of a daily digest of official
US government publications. Your ONLY inputs are the item summaries and
mechanical counts below — do not add outside knowledge, do not speculate.

Hard rules (non-negotiable):
- Strictly factual and opinion-agnostic: describe what was published, said,
  or enacted. Never whether it was good, bad, or significant.
- Banned: loaded adjectives (landmark, controversial, historic,
  unprecedented, sweeping, radical, extreme, momentous, alarming), motive
  attribution ("in an attempt to"), predictions of outcomes.
- Party-blind, neutral register, plain prose.
- 2 short paragraphs maximum (~120-180 words total): first the
  congressional floor picture (both chambers, recorded votes), then the
  executive/regulatory picture (rules, proposed rules, presidential
  documents). Weave in the counts naturally.
- No headers, no bullet lists, no citations (items below carry their own).

Reply with the two paragraphs only.

=== MECHANICAL COUNTS ===
{counts}

=== ITEM SUMMARIES ===
{items}
"""


def compose_day(conn, llm, date):
    """Create (or reuse) the Day in Review for a date. Idempotent by
    (date, PROMPT_VERSION). Returns stats dict."""
    existing = conn.execute(
        "SELECT 1 FROM day_summaries WHERE date = ? AND prompt_version = ?",
        (date, config.PROMPT_VERSION),
    ).fetchone()
    if existing:
        return {"composed": 0, "skipped_existing": 1, "input_tokens": 0, "output_tokens": 0}

    counts = _mechanical_counts(conn, date)
    items = conn.execute(
        """
        SELECT s.package_id, s.granule_id, s.inclusion_rule, s.summary,
               e.doc_type, e.title, e.agency, e.collection
        FROM summaries s
        JOIN extracted_texts e USING (package_id, granule_id)
        JOIN packages p ON p.package_id = s.package_id
        WHERE p.date_issued = ? AND s.prompt_version = ?
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
        (date, config.PROMPT_VERSION, result["model"], result["text"],
         result["input_tokens"], result["output_tokens"], utc_now_iso()),
    )
    conn.commit()
    logger.info("%s: Day in Review composed (%d in / %d out tokens)",
                date, result["input_tokens"], result["output_tokens"])
    return {"composed": 1, "skipped_existing": 0,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"]}


def _mechanical_counts(conn, date):
    rows = conn.execute(
        """
        SELECT e.collection, COALESCE(e.doc_type, '?') AS doc_type, COUNT(*) AS n
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE p.date_issued = ? GROUP BY 1, 2 ORDER BY 1, 2
        """,
        (date,),
    ).fetchall()
    return {f"{r['collection']}/{r['doc_type']}": r["n"] for r in rows}


def get_day_summary(conn, date):
    row = conn.execute(
        "SELECT summary, model FROM day_summaries WHERE date = ? AND prompt_version = ?",
        (date, config.PROMPT_VERSION),
    ).fetchone()
    return dict(row) if row else None

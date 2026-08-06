"""Section tags (GUIDE §6 rule 12a): mechanical branch/agency tags at
zero tokens, plus up to three model-generated one-to-three-word
discovery keys per section — one batched cheap-tier call per digest
day, independently versioned (TAG_PROMPT_VERSION), ledgered, and linted
by the digest's banned-lexicon gate because the tags render in it.
Tags are navigational metadata, never judgments."""

import json
import logging
import re

from . import config
from .sync import utc_now_iso

logger = logging.getLogger("fapd.tags")

# Section key -> branch tag (mechanical; mirrors compose.SECTION_KEYS).
SECTION_BRANCH = {
    "senate": "legislative",
    "house": "legislative",
    "legislation": "legislative",
    "laws": "legislative",
    "rules": "executive",
    "proposed": "executive",
    "presidential": "executive",
    "judicial": "judicial",
    "agency": "executive",
    "votes": "legislative",
    "billactions": "legislative",
}

_TAG_PROMPT = """For EACH digest section below, produce up to three short tags
(one to three words each, lowercase) that describe the section's subject
matter for search and retrieval. Use ONLY facts present in the summaries.
Plain descriptive nouns only — no loaded adjectives, no judgments, no
predictions. Banned terms (complete list, enforced verbatim by the
render-time gate): {banned}.

Output format: STRICT JSON, one object mapping each section key to an
array of tag strings. No markdown fences, no other keys.

{sections}
""".replace(
    "{banned}", ", ".join(f'"{t}"' for t in config.BANNED_TERMS))


def mechanical_section_tags(conn, date):
    """Branch tag per populated section, plus agency tags for the FR and
    agency sections (from item metadata / registry-derived source ids).
    Zero tokens; derived entirely from stored records."""
    from .compose import _section_items

    grouped = _section_items(conn, date)
    tags = {}
    for key in grouped:
        out = [SECTION_BRANCH.get(key, "cross-branch")]
        tags[key] = out
    # FR sections: top agencies by document count on the day.
    agency_rows = conn.execute(
        """
        SELECT e.agency, COUNT(*) AS n FROM extracted_texts e
        JOIN packages p USING (package_id)
        WHERE p.digest_day = ? AND e.collection = 'FR' AND e.agency IS NOT NULL
        GROUP BY 1 ORDER BY n DESC LIMIT 3
        """,
        (date,),
    ).fetchall()
    fr_agencies = [r["agency"].strip().lower() for r in agency_rows if r["agency"]]
    for key in ("rules", "proposed", "presidential"):
        if key in tags:
            tags[key] += fr_agencies[:2]
    return tags


def run(conn, llm, date):
    """Write section_tags for `date`: mechanical always; discovery keys
    via one batched call over stored synopses/summaries. Idempotent by
    (date, TAG_PROMPT_VERSION) for the llm layer; mechanical rows are
    refreshed each run. Returns stats."""
    from .compose import _section_items, get_section_synopses

    mech = mechanical_section_tags(conn, date)
    now = utc_now_iso()
    conn.execute(
        "DELETE FROM section_tags WHERE date = ? AND method = 'mechanical'", (date,))
    for key, values in mech.items():
        for tag in dict.fromkeys(values):  # dedupe, keep order
            conn.execute(
                "INSERT OR IGNORE INTO section_tags (date, section_key, tag,"
                " method, created_at) VALUES (?, ?, ?, 'mechanical', ?)",
                (date, key, tag, now))
    conn.commit()

    existing = conn.execute(
        "SELECT COUNT(*) FROM section_tags WHERE date = ? AND method = 'llm'"
        " AND prompt_version = ?", (date, config.TAG_PROMPT_VERSION)).fetchone()[0]
    if existing:
        return {"mechanical": sum(len(v) for v in mech.values()),
                "llm": 0, "skipped_existing": existing}

    grouped = _section_items(conn, date)
    if not grouped:
        return {"mechanical": sum(len(v) for v in mech.values()),
                "llm": 0, "skipped_existing": 0}
    synopses = get_section_synopses(conn, date)
    blocks = []
    for key, rows in grouped.items():
        lead = synopses.get(key, "")
        lines = "\n".join(
            f"- {(r['title'] or '').strip()[:80]}: {r['summary'][:150]}"
            for r in rows[:8])
        blocks.append(f"=== SECTION key={key} ===\n{lead}\n{lines}")
    result = llm.complete(
        _TAG_PROMPT.format(sections="\n\n".join(blocks)),
        purpose="tags:discovery-keys", model=config.MAP_MODEL,
        package_id=f"DIGEST-{date}")

    text = result["text"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rstrip().removesuffix("```")
    try:
        mapping = json.loads(text)
    except ValueError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        mapping = json.loads(match.group(0)) if match else {}

    written = 0
    for key in grouped:
        keys = mapping.get(key) or []
        for tag in keys[:3]:
            if isinstance(tag, str) and 0 < len(tag.strip()) <= 40:
                conn.execute(
                    "INSERT OR IGNORE INTO section_tags (date, section_key,"
                    " tag, method, prompt_version, model, created_at)"
                    " VALUES (?, ?, ?, 'llm', ?, ?, ?)",
                    (date, key, " ".join(tag.lower().split()),
                     config.TAG_PROMPT_VERSION, result["model"], now))
                written += 1
    conn.commit()
    logger.info("%s: %d discovery key(s) written across %d section(s)",
                date, written, len(grouped))
    return {"mechanical": sum(len(v) for v in mech.values()),
            "llm": written, "skipped_existing": 0}


def get_section_tags(conn, date):
    """{section_key: {"mechanical": [...], "llm": [...]}} — kept separate
    so renderers can label the model-derived keys in place (GUIDE §2)."""
    out = {}
    for row in conn.execute(
        "SELECT section_key, tag, method FROM section_tags WHERE date = ?"
        " AND (prompt_version IS NULL OR prompt_version = ?)"
        " ORDER BY CASE method WHEN 'mechanical' THEN 0 ELSE 1 END, tag",
        (date, config.TAG_PROMPT_VERSION),
    ):
        bucket = out.setdefault(
            row["section_key"], {"mechanical": [], "llm": []})
        bucket[row["method"]].append(row["tag"])
    return out

"""Source-page model layers (GUIDE §3a source surfaces, 2026-08-03).

Two reader-facing prose layers for the per-source pages, both cheap-tier,
batched (many sources per call — the CLI backend's ~25K-token fixed
per-call overhead makes call COUNT the design variable), ledgered under
distinct purposes, and banned-lexicon-scanned BEFORE storage:

- **Assessments** (``source_assessments``): prose restating OUR measured
  ingestion relationship with a source — formats seen, cadence, delivery
  quirks, incident history from the registry notes, what changed since
  the last assessment. Input is the registry entry and caller-supplied
  measured stats ONLY; the health-page law binds it (our observations of
  our own ingestion, never an opinion about the publisher). Regenerated
  when none exists, at ``SOURCE_ASSESS_MAX_AGE_DAYS`` of age, or when
  the source's health label changed.
- **Descriptions** (``source_descriptions``): what the source IS — a 1–2
  sentence ``summary`` and a 250–500 word ``description``. The ONE
  surface licensed to draw on the model's general knowledge of public
  institutions; the license's price is stated in the prompt (factual,
  opinion-agnostic about the institution, no current-events claims,
  grounded in the registry entry's facts where they exist). Keyed
  ``(source_id, prompt_version, registry_hash)`` and regenerated ONLY
  when that pair has no row — an edited registry entry regenerates, an
  untouched one never does; no timer.

Storage-time gate: every generated text is scanned by the render gate's
compiled regex (``report._BANNED_RE`` — the same object, so the two
enforcement layers cannot drift) before INSERT. A failing text stores
NOTHING (logged, counted in the returned stats); the page renders
without that block. The gates are never loosened for these surfaces.

Failure posture (the insight.py idiom): an ``LLMError`` never raises out
of a refresh — logged, counted, returned. The budget-pause types are the
exception and propagate deliberately: ``TokenBudgetExceededError`` (a
``BudgetExceededError`` — workers record it paused-not-failed) and
``PromptSizeError`` (the per-call size guard is standing policy).
"""

import datetime as dt
import hashlib
import json
import logging

from . import config
from .llm import LLMError, PromptSizeError
from .report import _BANNED_RE
from .sync import utc_now_iso

logger = logging.getLogger("fapd.assess")

# Sources per call. Descriptions are output-heavy (up to ~500 words
# each), so the batch is smaller than analyze's input-heavy MAX_BATCH_
# ITEMS reasoning would allow; eight keeps one reply comfortably inside
# the response cap while still amortizing the fixed per-call overhead.
MAX_SOURCE_BATCH = 8

# Description word bounds (GUIDE §3a: "250–500 word orientation").
# Enforcement is deliberately asymmetric:
# - OVER 500 words is a mechanical overage of text we already paid for —
#   clipped back to the bound at a sentence boundary and stored.
# - UNDER the floor is missing content we must never pad or fabricate —
#   rejected, not stored, logged. The floor is 200, not 250: the task's
#   bound is "~250–500", and discarding a 240-word orientation to
#   regenerate a marginally longer one buys nothing; below 200 words the
#   reply is not the orientation the prompt asked for.
DESC_MAX_WORDS = 500
DESC_MIN_WORDS = 200
# The summary is "1–2 sentences"; sentence counting is not mechanical,
# so the guard is a character cap with sentence-boundary truncation
# (the analyze._official_summary pattern). An empty summary rejects.
SUMMARY_MAX_CHARS = 400
_TRUNCATION_NOTE = " [truncated]"

# GUIDE §2 restated verbatim from the canonical constant (review D8) —
# substituted via str.replace so runtime placeholders stay untouched.
_BANNED_CLAUSE = ", ".join(f'"{t}"' for t in config.BANNED_TERMS)

_ASSESS_PROMPT = """\
You are writing short ingestion-assessment notes for the per-source pages
of a daily digest of official United States government publications. Each
SOURCE block below carries one source's registry entry, our measured
ingestion statistics for it, and (when one exists) our previous
assessment. For EACH source, write one plain prose paragraph (under about
200 words) restating our measured ingestion relationship with the source:
the formats we have seen, the delivery cadence we have observed, delivery
quirks, incident history recorded in the registry notes, and what changed
since the previous assessment when one is shown.

Rules (mandatory, non-negotiable):
- Report ONLY our own observations of our own ingestion, using ONLY the
  data in the block. NO outside knowledge, NO speculation, NO
  predictions.
- Never state or imply an opinion about the publisher. NO quality
  judgments of an agency, ever. A failed request is our request that
  returned no content — that may be load, maintenance, or a limit the
  publisher sets, and we cannot tell which from outside.
- NO banned terms -- the complete list, enforced verbatim by the
  storage-time gate: {banned}.
- NO motive attribution. Plain, neutral register.

Output format: reply with STRICT JSON and nothing else -- a single JSON
object mapping each source's key (the exact string after "key=" in its
header) to that source's assessment paragraph string. No markdown fences,
no commentary, no keys other than the source keys.
""".replace("{banned}", _BANNED_CLAUSE)

_DESC_PROMPT = """\
You are writing reader-facing orientation text for the per-source pages
of a daily digest of official United States government publications. Each
SOURCE block below is one source's registry entry. For EACH source,
write:
- "summary": 1-2 sentences stating what the source is.
- "description": a 250-500 word orientation for a general reader — what
  the institution or publication is, where it sits in the federal
  structure, what it publishes, and what kinds of documents a reader
  will see from it in this digest.

This surface may draw on general knowledge of public institutions (a
registry entry cannot say what an agency is), and that license carries
rules (mandatory, non-negotiable):
- Factual and opinion-agnostic about the institution: describe what it
  is and does, never whether it does it well or badly, and never take a
  side on any matter it handles.
- NO claims about specific current events, recent or pending actions,
  or named current officeholders. Institutional facts only.
- Where the registry entry states a fact (what is published, format,
  cadence, coverage), stay grounded in it; general knowledge fills in
  what the entry cannot say and never contradicts it.
- NO banned terms -- the complete list, enforced verbatim by the
  storage-time gate: {banned}.
- NO motive attribution, NO predictions. Plain, neutral register.

Output format: reply with STRICT JSON and nothing else -- a single JSON
object mapping each source's key (the exact string after "key=" in its
header) to an object with exactly two string fields, "summary" and
"description". No markdown fences, no commentary, no keys other than the
source keys.
""".replace("{banned}", _BANNED_CLAUSE)


def registry_hash(entry):
    """sha256 of the canonical serialization of one registry entry
    (JSON, sorted keys, compact separators). Any edit to the entry —
    including notes, the incident-history field — changes the hash and
    so regenerates the description; a byte-identical entry never does."""
    canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _parse_reply(text):
    """Strict-JSON reply parsing with markdown-fence tolerance (the
    analyze/tags idiom). Returns the key -> value mapping, or {} when
    the reply is unusable — every source of the call then counts as
    failed; there is no ad-hoc parsing fallback."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        t = t.rstrip().removesuffix("```")
    try:
        obj = json.loads(t)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def _scan(text, source_id, surface, stats):
    """True when `text` clears the storage-time lexicon gate. A hit is
    logged with the term and counted; the caller stores nothing."""
    match = _BANNED_RE.search(text)
    if match:
        logger.warning(
            "%s for %s rejected: banned term %r in generated prose — "
            "not stored", surface, source_id, match.group(0))
        stats["rejected"] += 1
        return False
    return True


def _sentence_clip(text, limit_chars):
    """Cut at `limit_chars`, backed up to a sentence boundary when one
    exists (the analyze._official_summary pattern)."""
    cut = text[:limit_chars]
    boundary = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    if boundary > 0:
        cut = cut[: boundary + 1]
    return cut


def _batches(seq, size=MAX_SOURCE_BATCH):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


# --------------------------------------------------------------- layer 1 --


def _assess_trigger(conn, source_id, health_label, prev_health_label):
    """The regeneration trigger for one source, or None to skip.

    Computed against the newest stored row at the CURRENT prompt
    version — a version bump therefore reads as 'initial' and
    regenerates the layer, the §3a versioned-surface semantics.
    Precedence: initial > health-change > age.
    """
    row = conn.execute(
        "SELECT generated_at FROM source_assessments"
        " WHERE source_id = ? AND prompt_version = ?"
        " ORDER BY generated_at DESC LIMIT 1",
        (source_id, config.SOURCE_ASSESS_PROMPT_VERSION)).fetchone()
    if row is None:
        return "initial"
    if (health_label is not None and prev_health_label is not None
            and health_label != prev_health_label):
        return "health-change"
    generated = dt.datetime.fromisoformat(row["generated_at"])
    age = dt.datetime.now(dt.UTC) - generated
    if age.days >= config.SOURCE_ASSESS_MAX_AGE_DAYS:
        return "age-30d"
    return None


def _assess_block(conn, entry, measured):
    """One SOURCE block: registry entry + measured stats + the previous
    assessment when one exists (so 'what changed' is answerable)."""
    sid = entry["id"]
    lines = [f"=== SOURCE key={sid} ===",
             "registry entry:",
             json.dumps(entry, indent=1, sort_keys=True),
             "measured ingestion statistics:",
             json.dumps(measured or {}, indent=1, sort_keys=True)]
    prev = conn.execute(
        "SELECT generated_at, assessment FROM source_assessments"
        " WHERE source_id = ? ORDER BY generated_at DESC LIMIT 1",
        (sid,)).fetchone()
    if prev is not None:
        lines += [f"previous assessment ({prev['generated_at']}):",
                  prev["assessment"]]
    lines.append("=== END SOURCE ===")
    return "\n".join(lines)


def refresh_assessments(conn, llm, entries, stats_by_source,
                        health_state, prev_health_state):
    """Regenerate source assessments whose trigger fires; store nothing
    for the rest (zero LLM calls when nothing fires).

    Parameters:
    - ``entries``: validated registry entries (``sources.load_registry``
      shape); the caller scopes this list — typically active sources.
    - ``stats_by_source``: ``{source_id: dict}`` of measured ingestion
      stats, caller-supplied (mechanical numbers; this module never
      queries the fetch log itself). A missing id contributes ``{}``.
    - ``health_state`` / ``prev_health_state``: ``{source_id: label}``,
      current and previous health labels as plain dicts — a differing
      pair fires the 'health-change' trigger.

    Returns ``{"generated", "skipped", "rejected", "failed",
    "llm_calls"}``. ``rejected`` counts texts that failed the lexicon
    gate (not stored); ``failed`` counts sources whose call failed or
    whose reply omitted or mangled them (no row, no fabrication).
    ``LLMError`` is absorbed per batch; ``TokenBudgetExceededError`` and
    ``PromptSizeError`` propagate — the budget-pause path.
    """
    stats = {"generated": 0, "skipped": 0, "rejected": 0, "failed": 0,
             "llm_calls": 0}
    pending = []
    for entry in entries:
        sid = entry["id"]
        trigger = _assess_trigger(
            conn, sid, health_state.get(sid), prev_health_state.get(sid))
        if trigger is None:
            stats["skipped"] += 1
        else:
            pending.append((entry, trigger))

    for batch_no, batch in enumerate(_batches(pending), 1):
        blocks = [_assess_block(conn, entry, stats_by_source.get(entry["id"]))
                  for entry, _ in batch]
        prompt = _ASSESS_PROMPT + "\n" + "\n\n".join(blocks) + "\n"
        try:
            result = llm.complete(
                prompt, purpose=f"source-assess:batch{batch_no}",
                model=config.MAP_MODEL, package_id="SOURCES")
        except PromptSizeError:
            raise
        except LLMError as exc:
            logger.warning("source-assess batch %d failed (%d source(s)):"
                           " %s", batch_no, len(batch), exc)
            stats["failed"] += len(batch)
            continue
        stats["llm_calls"] += 1
        mapping = _parse_reply(result["text"])
        now = utc_now_iso()
        for entry, trigger in batch:
            sid = entry["id"]
            text = mapping.get(sid)
            if not isinstance(text, str) or not text.strip():
                logger.warning("source-assess: no usable reply for %s", sid)
                stats["failed"] += 1
                continue
            text = text.strip()
            if not _scan(text, sid, "assessment", stats):
                continue
            conn.execute(
                "INSERT INTO source_assessments (source_id, prompt_version,"
                " generated_at, model, trigger_reason, assessment)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (sid, config.SOURCE_ASSESS_PROMPT_VERSION, now,
                 result["model"], trigger, text))
            stats["generated"] += 1
        conn.commit()
    return stats


# --------------------------------------------------------------- layer 2 --


def _bounded_description(text, source_id, stats):
    """Mechanical word bounds. Returns the (possibly clipped) text, or
    None when rejected — see the DESC_* constants for the asymmetry."""
    words = text.split()
    if len(words) < DESC_MIN_WORDS:
        logger.warning(
            "description for %s rejected: %d words is under the %d-word"
            " floor — not stored", source_id, len(words), DESC_MIN_WORDS)
        stats["rejected"] += 1
        return None
    if len(words) > DESC_MAX_WORDS:
        joined = " ".join(words[:DESC_MAX_WORDS])
        clipped = _sentence_clip(joined, len(joined)) + _TRUNCATION_NOTE
        stats["clipped"] += 1
        return clipped
    return text


def refresh_descriptions(conn, llm, entries):
    """Generate descriptions for every entry whose ``(source_id,
    SOURCE_DESC_PROMPT_VERSION, registry_hash)`` has no stored row —
    the ONLY regeneration condition (no timer; an untouched entry costs
    zero calls forever).

    ``entries`` are validated registry entries; the caller scopes the
    list. Returns ``{"generated", "skipped", "rejected", "clipped",
    "failed", "llm_calls"}`` with the same semantics and error posture
    as :func:`refresh_assessments` (both the summary and the
    description are lexicon-scanned; either failing stores nothing).
    """
    stats = {"generated": 0, "skipped": 0, "rejected": 0, "clipped": 0,
             "failed": 0, "llm_calls": 0}
    pending = []
    for entry in entries:
        h = registry_hash(entry)
        exists = conn.execute(
            "SELECT 1 FROM source_descriptions WHERE source_id = ?"
            " AND prompt_version = ? AND registry_hash = ?",
            (entry["id"], config.SOURCE_DESC_PROMPT_VERSION, h)).fetchone()
        if exists:
            stats["skipped"] += 1
        else:
            pending.append((entry, h))

    for batch_no, batch in enumerate(_batches(pending), 1):
        blocks = [
            f"=== SOURCE key={entry['id']} ===\n"
            + json.dumps(entry, indent=1, sort_keys=True)
            + "\n=== END SOURCE ==="
            for entry, _ in batch]
        prompt = _DESC_PROMPT + "\n" + "\n\n".join(blocks) + "\n"
        try:
            result = llm.complete(
                prompt, purpose=f"source-desc:batch{batch_no}",
                model=config.MAP_MODEL, package_id="SOURCES")
        except PromptSizeError:
            raise
        except LLMError as exc:
            logger.warning("source-desc batch %d failed (%d source(s)): %s",
                           batch_no, len(batch), exc)
            stats["failed"] += len(batch)
            continue
        stats["llm_calls"] += 1
        mapping = _parse_reply(result["text"])
        now = utc_now_iso()
        for entry, h in batch:
            sid = entry["id"]
            obj = mapping.get(sid)
            if (not isinstance(obj, dict)
                    or not isinstance(obj.get("summary"), str)
                    or not isinstance(obj.get("description"), str)
                    or not obj["summary"].strip()
                    or not obj["description"].strip()):
                logger.warning("source-desc: no usable reply for %s", sid)
                stats["failed"] += 1
                continue
            summary = " ".join(obj["summary"].split())
            if len(summary) > SUMMARY_MAX_CHARS:
                summary = _sentence_clip(summary, SUMMARY_MAX_CHARS) \
                    + _TRUNCATION_NOTE
            description = _bounded_description(
                obj["description"].strip(), sid, stats)
            if description is None:
                continue
            if not (_scan(summary, sid, "description summary", stats)
                    and _scan(description, sid, "description", stats)):
                continue
            conn.execute(
                "INSERT INTO source_descriptions (source_id, prompt_version,"
                " registry_hash, generated_at, model, summary, description)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (sid, config.SOURCE_DESC_PROMPT_VERSION, h, now,
                 result["model"], summary, description))
            stats["generated"] += 1
        conn.commit()
    return stats


# ---------------------------------------------------------- read helpers --


def latest_assessment(conn, source_id):
    """Newest stored assessment for one source at the current prompt
    version, as a dict, or None. The renderer labels it model-derived
    with its date, model, version, and trigger (GUIDE §2)."""
    row = conn.execute(
        "SELECT source_id, prompt_version, generated_at, model,"
        " trigger_reason, assessment FROM source_assessments"
        " WHERE source_id = ? AND prompt_version = ?"
        " ORDER BY generated_at DESC LIMIT 1",
        (source_id, config.SOURCE_ASSESS_PROMPT_VERSION)).fetchone()
    return dict(row) if row else None


def latest_description(conn, source_id):
    """Newest stored description for one source at the current prompt
    version, ANY registry hash — so the page keeps rendering the prior
    text in the window between a registry edit and the next refresh —
    as a dict, or None."""
    row = conn.execute(
        "SELECT source_id, prompt_version, registry_hash, generated_at,"
        " model, summary, description FROM source_descriptions"
        " WHERE source_id = ? AND prompt_version = ?"
        " ORDER BY generated_at DESC LIMIT 1",
        (source_id, config.SOURCE_DESC_PROMPT_VERSION)).fetchone()
    return dict(row) if row else None


def latest_assessments(conn):
    """Batch form: {source_id: newest assessment dict} at the current
    prompt version — one query for a renderer walking every source."""
    rows = conn.execute(
        "SELECT source_id, prompt_version, generated_at, model,"
        " trigger_reason, assessment FROM source_assessments a"
        " WHERE prompt_version = ? AND generated_at = ("
        "   SELECT MAX(generated_at) FROM source_assessments b"
        "   WHERE b.source_id = a.source_id AND b.prompt_version ="
        "   a.prompt_version)",
        (config.SOURCE_ASSESS_PROMPT_VERSION,)).fetchall()
    return {r["source_id"]: dict(r) for r in rows}


def latest_descriptions(conn):
    """Batch form: {source_id: newest description dict} at the current
    prompt version, any registry hash."""
    rows = conn.execute(
        "SELECT source_id, prompt_version, registry_hash, generated_at,"
        " model, summary, description FROM source_descriptions a"
        " WHERE prompt_version = ? AND generated_at = ("
        "   SELECT MAX(generated_at) FROM source_descriptions b"
        "   WHERE b.source_id = a.source_id AND b.prompt_version ="
        "   a.prompt_version)",
        (config.SOURCE_DESC_PROMPT_VERSION,)).fetchall()
    return {r["source_id"]: dict(r) for r in rows}

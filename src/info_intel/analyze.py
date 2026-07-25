"""Map stage: per-item summarization of rule-selected documents (GUIDE §5
stage 3, §6).

Discipline, in order:
- No model sees an item that a rules.py selection rule did not promote
  (§6 rule 4).
- Official summaries first (§6 rule 3): FR documents carrying an agency
  SUMMARY preamble are stored verbatim at zero token cost.
- Summaries are durable, keyed by (package, granule, prompt_version):
  reruns skip existing rows and make zero LLM calls (§6 rule 5).
- LLM work is batched: the CLI backend carries roughly 25K tokens of fixed
  overhead per call, so up to MAX_BATCH_ITEMS items share one call, and a
  partial day's work is resumable because every stored summary is committed
  immediately (§6 rule 10).
- Failed items are recorded, never fabricated: no summaries row is written
  for an item the model did not summarize.
"""

import datetime as dt
import json

from . import config, rules

# Amortizes the CLI backend's ~25K-token fixed per-call overhead.
MAX_BATCH_ITEMS = 6
# Chars of source text per item inside a map prompt.
ITEM_TEXT_LIMIT = 12000
# Official FR summaries longer than this are cut at a sentence boundary.
OFFICIAL_SUMMARY_MAX_CHARS = 1200
_OFFICIAL_TRUNCATION_NOTE = " [official summary truncated; see source]"
_TEXT_TRUNCATION_NOTE = "\n[truncated for summarization; full text in source]"

# GUIDE §2, restated verbatim in intent: opinion-agnostic output, no loaded
# adjectives, no motive attribution, no predictions, no opinions.
_PREAMBLE = """\
You are writing summaries of official United States government documents
for a citation-bound daily digest. For EACH document block below, write a
strictly factual summary of 2-3 sentences describing what the document
says or does.

Editorial constraints (mandatory, non-negotiable):
- Describe what was published, said, or enacted -- never whether it was
  good or bad.
- NO loaded adjectives (such as "controversial", "landmark", "extreme").
- NO motive attribution (such as "in an attempt to ...").
- NO predictions of political outcomes.
- NO opinions of any kind. Plain, neutral register.

Output format: reply with STRICT JSON and nothing else -- a single JSON
object mapping each document's key (the exact string after "key=" in its
header) to that document's summary string. No markdown fences, no
commentary, no keys other than the document keys.
"""


def _key(item):
    return f"{item['package_id']}|{item['granule_id']}"


def _parse_reply(text):
    """Strict-JSON reply parsing with markdown-fence tolerance. Returns the
    key -> summary mapping, or {} when the reply is unusable (every item of
    the call then goes to the retry path)."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        t = t.rstrip().removesuffix("```")
    try:
        obj = json.loads(t)
    except ValueError:
        return {}
    return obj if isinstance(obj, dict) else {}


def _official_summary(raw):
    """Whitespace-normalized official summary, sentence-truncated when it
    exceeds OFFICIAL_SUMMARY_MAX_CHARS."""
    s = " ".join(raw.split())
    if len(s) <= OFFICIAL_SUMMARY_MAX_CHARS:
        return s
    cut = s[:OFFICIAL_SUMMARY_MAX_CHARS]
    boundary = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    if boundary > 0:
        cut = cut[: boundary + 1]
    return cut + _OFFICIAL_TRUNCATION_NOTE


def _build_prompt(entries):
    """entries: list of (item, text) pairs, at most MAX_BATCH_ITEMS."""
    blocks = []
    for item, text in entries:
        if len(text) > ITEM_TEXT_LIMIT:
            text = text[:ITEM_TEXT_LIMIT] + _TEXT_TRUNCATION_NOTE
        blocks.append(
            f"=== DOCUMENT key={_key(item)} ===\n"
            f"collection: {item['collection']}  doc_type: {item['doc_type']}\n"
            f"title: {item['title'] or ''}\n\n"
            f"{text}\n"
            f"=== END DOCUMENT ==="
        )
    return _PREAMBLE + "\n" + "\n\n".join(blocks) + "\n"


def _summary_exists(conn, item):
    return (
        conn.execute(
            "SELECT 1 FROM summaries"
            " WHERE package_id = ? AND granule_id = ? AND prompt_version = ?",
            (item["package_id"], item["granule_id"], config.PROMPT_VERSION),
        ).fetchone()
        is not None
    )


def _store(conn, item, *, method, summary, model=None, input_tokens=0, output_tokens=0):
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method,"
        " model, inclusion_rule, summary, input_tokens, output_tokens, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            item["package_id"],
            item["granule_id"],
            config.PROMPT_VERSION,
            method,
            model,
            item["rule_id"],
            summary,
            input_tokens,
            output_tokens,
            dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        ),
    )
    conn.commit()  # durable per item — a partial day is resumable (§6 rule 10)


def _harvest(conn, stats, entries, mapping, result):
    """Store every entry whose key has a usable summary in mapping; return
    the entries that are still missing. Call tokens are split evenly across
    the call's items for the per-summary columns."""
    share_in = result["input_tokens"] // len(entries)
    share_out = result["output_tokens"] // len(entries)
    missing = []
    for item, text in entries:
        summary = mapping.get(_key(item))
        if isinstance(summary, str) and summary.strip():
            _store(
                conn, item, method="llm", summary=summary.strip(),
                model=result["model"], input_tokens=share_in, output_tokens=share_out,
            )
            stats["llm_summarized"] += 1
        else:
            missing.append((item, text))
    return missing


def _call(llm, stats, entries, purpose):
    result = llm.complete(
        _build_prompt(entries),
        purpose=purpose,
        package_id=",".join(sorted({item["package_id"] for item, _ in entries})),
        granule_id=entries[0][0]["granule_id"] or None if len(entries) == 1 else None,
    )
    stats["llm_calls"] += 1
    stats["input_tokens"] += result["input_tokens"]
    stats["output_tokens"] += result["output_tokens"]
    return _parse_reply(result["text"]), result


# GUIDE §2/§6 rule 9: plain-language restatement of STORED summaries only —
# derived text checkable against the adjacent summary; adds no facts.
_PLAIN_PREAMBLE = """\
You are restating summaries of official United States government documents
in plain everyday English for a labeled "In plain terms" line. For EACH
item below, restate its summary in ONE sentence (at most ~35 words).

Hard constraints (mandatory, non-negotiable):
- Use ONLY facts present in the given summary. Add nothing. You may drop
  qualifiers, but never numbers or dates in a way that changes meaning.
- Expand procedural jargon into ordinary words (for example, "interim
  final rule" -> "a rule that takes effect now while public comments are
  still accepted"; "cloture" -> "a vote to end debate").
- Keep effective dates and comment deadlines when the summary states them.
- Strictly factual and opinion-agnostic: never whether something is good
  or bad. NO loaded adjectives (such as "controversial", "landmark",
  "extreme"), NO evaluative framing (such as "cuts red tape",
  "crackdown"), NO motive attribution (such as "in an attempt to ..."),
  NO predictions, NO opinions.

Output format: reply with STRICT JSON and nothing else -- a single JSON
object mapping each item's key (the exact string after "key=" in its
header) to its one-sentence plain restatement. No markdown fences, no
commentary, no other keys.
"""


def _build_plain_prompt(entries):
    """entries: list of summaries-row dicts with package_id, granule_id,
    summary, doc_type, title."""
    blocks = [
        f"=== ITEM key={_key(row)} ===\n"
        f"doc_type: {row['doc_type'] or ''}  title: {row['title'] or ''}\n"
        f"summary: {row['summary']}\n"
        f"=== END ITEM ==="
        for row in entries
    ]
    return _PLAIN_PREAMBLE + "\n" + "\n\n".join(blocks) + "\n"


def _store_plain(conn, row, *, plain, model, input_tokens=0, output_tokens=0):
    conn.execute(
        "INSERT INTO plain_summaries (package_id, granule_id, plain_version,"
        " source_prompt_version, model, plain, input_tokens, output_tokens, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            row["package_id"],
            row["granule_id"],
            config.PLAIN_PROMPT_VERSION,
            config.PROMPT_VERSION,
            model,
            plain,
            input_tokens,
            output_tokens,
            dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        ),
    )
    conn.commit()


def _plain_call(llm, stats, entries, purpose):
    result = llm.complete(
        _build_plain_prompt(entries),
        purpose=purpose,
        model=config.PLAIN_MODEL,
        package_id=",".join(sorted({row["package_id"] for row in entries})),
    )
    stats["llm_calls"] += 1
    stats["input_tokens"] += result["input_tokens"]
    stats["output_tokens"] += result["output_tokens"]
    return _parse_reply(result["text"]), result


def _harvest_plain(conn, stats, entries, mapping, result):
    share_in = result["input_tokens"] // len(entries)
    share_out = result["output_tokens"] // len(entries)
    missing = []
    for row in entries:
        plain = mapping.get(_key(row))
        if isinstance(plain, str) and plain.strip():
            _store_plain(
                conn, row, plain=" ".join(plain.split()), model=result["model"],
                input_tokens=share_in, output_tokens=share_out,
            )
            stats["plain_written"] += 1
        else:
            missing.append(row)
    return missing


def run_plain(conn, llm, date):
    """Plain-speak pass: restate the date's stored summaries (all methods)
    as one-sentence plain lines. Idempotent by (package, granule,
    PLAIN_PROMPT_VERSION, PROMPT_VERSION); reruns make zero calls. A failed
    item simply has no plain line — presentation aid, never fabricated."""
    stats = {
        "plain_pending": 0,
        "plain_written": 0,
        "llm_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "failed_items": [],
    }
    pending = [
        dict(r)
        for r in conn.execute(
            """
            SELECT s.package_id, s.granule_id, s.summary, e.doc_type, e.title
            FROM summaries s
            JOIN packages p ON p.package_id = s.package_id
            LEFT JOIN extracted_texts e USING (package_id, granule_id)
            WHERE p.date_issued = ? AND s.prompt_version = ?
              AND NOT EXISTS (
                  SELECT 1 FROM plain_summaries ps
                  WHERE ps.package_id = s.package_id
                    AND ps.granule_id = s.granule_id
                    AND ps.plain_version = ?
                    AND ps.source_prompt_version = s.prompt_version)
            ORDER BY s.package_id, s.granule_id
            """,
            (date, config.PROMPT_VERSION, config.PLAIN_PROMPT_VERSION),
        ).fetchall()
    ]
    stats["plain_pending"] = len(pending)

    retry_queue = []
    for start in range(0, len(pending), config.MAX_PLAIN_BATCH_ITEMS):
        batch = pending[start : start + config.MAX_PLAIN_BATCH_ITEMS]
        batch_no = start // config.MAX_PLAIN_BATCH_ITEMS + 1
        mapping, result = _plain_call(llm, stats, batch, f"plain:batch{batch_no}")
        retry_queue.extend(_harvest_plain(conn, stats, batch, mapping, result))

    for row in retry_queue:
        mapping, result = _plain_call(llm, stats, [row], "plain:retry")
        if _harvest_plain(conn, stats, [row], mapping, result):
            stats["failed_items"].append(
                {"package_id": row["package_id"], "granule_id": row["granule_id"]}
            )
    return stats


def run(conn, llm, date):
    """Summarize every rule-selected document for the date. Idempotent:
    items already summarized under config.PROMPT_VERSION are skipped before
    any LLM work, so a rerun makes zero calls."""
    stats = {
        "selected": 0,
        "official": 0,
        "llm_summarized": 0,
        "llm_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "skipped_existing": 0,
        "failed_items": [],
    }
    items = rules.select_items(conn, date)
    stats["selected"] = len(items)

    pending = []  # (item, text) still needing an LLM summary
    for item in items:
        if _summary_exists(conn, item):
            stats["skipped_existing"] += 1
            continue
        row = conn.execute(
            "SELECT text, metadata FROM extracted_texts"
            " WHERE package_id = ? AND granule_id = ?",
            (item["package_id"], item["granule_id"]),
        ).fetchone()
        official = None
        if item["collection"] == "FR":
            try:
                official = json.loads(row["metadata"]).get("summary")
            except (TypeError, ValueError):
                official = None
        if isinstance(official, str) and official.strip():
            _store(conn, item, method="official", summary=_official_summary(official))
            stats["official"] += 1
        else:
            pending.append((item, row["text"]))

    retry_queue = []
    for start in range(0, len(pending), MAX_BATCH_ITEMS):
        batch = pending[start : start + MAX_BATCH_ITEMS]
        batch_no = start // MAX_BATCH_ITEMS + 1
        mapping, result = _call(llm, stats, batch, f"map:batch{batch_no}")
        retry_queue.extend(_harvest(conn, stats, batch, mapping, result))

    # One single-item retry per missing/unparsable item; still-failing items
    # are recorded and skipped — never fabricated. They surface as known
    # gaps in the Coverage Statement, not as silent omissions (GUIDE §2).
    for entry in retry_queue:
        mapping, result = _call(llm, stats, [entry], "map:retry")
        if _harvest(conn, stats, [entry], mapping, result):
            item = entry[0]
            stats["failed_items"].append(
                {
                    "package_id": item["package_id"],
                    "granule_id": item["granule_id"],
                    "rule_id": item["rule_id"],
                }
            )
    return stats

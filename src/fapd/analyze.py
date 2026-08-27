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
import logging

from . import config, rules
from .llm import LLMError, ProviderUnavailableError
from .report import _BANNED_RE, _official_spans
from .sync import utc_now_iso

logger = logging.getLogger("fapd.analyze")

# Amortizes the CLI backend's ~25K-token fixed per-call overhead.
MAX_BATCH_ITEMS = 6
# Chars of source text per item inside a map prompt.
ITEM_TEXT_LIMIT = 12000
# Official FR summaries longer than this are cut at a sentence boundary.
OFFICIAL_SUMMARY_MAX_CHARS = 1200
_OFFICIAL_TRUNCATION_NOTE = " [official summary truncated; see source]"
_TEXT_TRUNCATION_NOTE = "\n[truncated for summarization; full text in source]"

# GUIDE §2, restated verbatim: opinion-agnostic output, with the complete
# banned-term list generated from the canonical constant (review D8) —
# substituted via str.replace so runtime placeholders stay untouched.
_BANNED_CLAUSE = ", ".join(f'"{t}"' for t in config.BANNED_TERMS)

_PREAMBLE = """\
You are writing summaries of official United States government documents
for a citation-bound daily digest. For EACH document block below, write a
strictly factual summary of 2-3 sentences describing what the document
says or does.

Editorial constraints (mandatory, non-negotiable):
- Describe what was published, said, or enacted -- never whether it was
  good or bad.
- NO banned terms -- the complete list, enforced verbatim by the
  render-time gate: {banned}.
- NO motive attribution, NO predictions of political outcomes.
- NO opinions of any kind. Plain, neutral register.
- EXCEPTION: a document's own official title or name may be quoted
  verbatim even when it contains a banned word (a case caption, a statute
  like the National Historic Preservation Act) -- quote it exactly; never
  reuse such words in your own phrasing.

Output format: reply with STRICT JSON and nothing else -- a single JSON
object mapping each document's key (the exact string after "key=" in its
header) to that document's summary string. No markdown fences, no
commentary, no keys other than the document keys.
""".replace("{banned}", _BANNED_CLAUSE)

# GUIDE §6 rule 14a: prepended to _PREAMBLE/_PLAIN_PREAMBLE (never sent
# standalone) for a corrective rewrite of a summary that already exists
# but tripped the render-time lexicon gate. Names the SPECIFIC term(s)
# a prior attempt used, on top of the full list the base preamble
# already restates -- error-informed, not a blind identical retry.
_CORRECTION_NOTICE = """\
CORRECTION NOTICE: your previous summary of this document used at least
one word this digest never uses in its own voice: {terms}. Write a full
replacement from scratch using the source text below -- do not simply
delete or swap the flagged word. Avoid the ENTIRE banned list restated
below, not just the term(s) named here. If the flagged word appears only
because it is part of the document's own official title, case caption,
or the name of a law, you may still quote that exact title/name verbatim
per the exception below -- but if it appeared in your own descriptive
sentence, it must not reappear in the new text, in any form.

"""


def _key(item):
    return f"{item['package_id']}|{item['granule_id']}"


def _normalize_key(key):
    """Canonical spelling of a response key. The prompt presents a
    package-level item (granule_id = '': PLAW, PRESACT, BILLS) as
    'PLAW-119publ93|' — a trailing pipe every model reads as punctuation
    and drops, so the reply comes back keyed 'PLAW-119publ93'. Measured
    2026-08-25/26: every PLAW and PRESACT item fell through the whole
    retry ladder (7-11 map:retry-single calls, 258K-416K input tokens a
    day) although the model summarized it every time. A bare id is read
    as the granule-less key; whitespace is stripped; a key that already
    carries a pipe is left alone, so 'CREC-x' can never be taken for
    'CREC-x|G1' (a batch may hold several granules of one package)."""
    k = key.strip()
    return k if "|" in k else f"{k}|"


def _match_key(mapping, item):
    """The reply value for item: the exact key first, then any response
    key whose normalized spelling equals it. Returns (value, response_key);
    response_key is None when nothing matched."""
    key = _key(item)
    if key in mapping:
        return mapping[key], key
    for resp_key, value in mapping.items():
        if isinstance(resp_key, str) and _normalize_key(resp_key) == key:
            return value, resp_key
    return None, None


def _match_replies(layer, stats, items, mapping):
    """Reply values aligned with items (None where absent). Keys accepted
    only after normalization are counted in stats['keys_normalized'] and
    logged at INFO — an accepted spelling, not a fault; keys matching no
    item at all still warn (right-count-wrong-keys is otherwise
    indistinguishable from truncation, F-010)."""
    values, used, normalized = [], set(), 0
    for item in items:
        value, resp_key = _match_key(mapping, item)
        values.append(value)
        if resp_key is not None:
            used.add(resp_key)
            if resp_key != _key(item):
                normalized += 1
    if normalized:
        stats["keys_normalized"] = stats.get("keys_normalized", 0) + normalized
        logger.info("%s: %d response key(s) matched after normalization"
                    " (bare package id or stray whitespace for the canonical"
                    " 'package|granule' key)", layer, normalized)
    unmatched = set(mapping) - used
    if unmatched:
        logger.warning("%s: %d response key(s) match no requested item,"
                       " e.g. %r", layer, len(unmatched), sorted(unmatched)[:3])
    return values


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
    values = _match_replies("map", stats, [item for item, _ in entries], mapping)
    for (item, text), summary in zip(entries, values):
        if isinstance(summary, str) and summary.strip():
            _store(
                conn, item, method="llm", summary=summary.strip(),
                model=result["model"], input_tokens=share_in, output_tokens=share_out,
            )
            stats["llm_summarized"] += 1
        else:
            missing.append((item, text))
    if missing:
        logger.info("map: response covered %d of %d requested items"
                    " (short response — likely truncation)",
                    len(entries) - len(missing), len(entries))
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
  or bad. NO banned terms -- the complete list, enforced verbatim by the
  render-time gate: {banned}. NO motive attribution, NO predictions,
  NO opinions. A document's own official name may be quoted verbatim even
  when it contains a banned word; never reuse such words in your own
  phrasing.

Output format: reply with STRICT JSON and nothing else -- a single JSON
object mapping each item's key (the exact string after "key=" in its
header) to its one-sentence plain restatement. No markdown fences, no
commentary, no other keys.
""".replace("{banned}", _BANNED_CLAUSE)


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


def _record_attempts(conn, layer, items):
    """Count a failed summarization attempt per item (GUIDE §6 r14).

    The per-run retry ceiling resets every cycle, and the collector runs
    analyze every 15 minutes for every pending date — so without a
    durable count an item that cannot be summarized is retried forever.
    Measured 2026-07-31 before this existed: 1,345 single retries,
    39,712,610 input tokens, 60% of the day."""
    now = utc_now_iso()
    for pid, gid in items:
        conn.execute(
            "INSERT INTO summary_attempts (package_id, granule_id,"
            " prompt_version, layer, attempts, last_at)"
            " VALUES (?, ?, ?, ?, 1, ?)"
            " ON CONFLICT (package_id, granule_id, prompt_version, layer)"
            " DO UPDATE SET attempts = attempts + 1, last_at = excluded.last_at",
            (pid, gid, config.PROMPT_VERSION, layer, now))
    conn.commit()
    if items:
        logger.info("%s: recorded a failed attempt for %d item(s); items reaching"
                    " %d attempts are left unsummarized and disclosed",
                    layer, len(items), config.MAX_ITEM_SUMMARY_ATTEMPTS)


def _attempts_exhausted(conn, package_id, granule_id, layer):
    """True when the item has already used its MAX_ITEM_SUMMARY_ATTEMPTS
    for `layer` (GUIDE §6 r14). The same predicate collect.pending_items
    applies for the collector's trigger accounting — until 2026-08-24
    only that path honored the ceiling, so the finalizer (and any manual
    run) re-attempted every exhausted item at full batch cost."""
    row = conn.execute(
        "SELECT attempts FROM summary_attempts WHERE package_id = ?"
        " AND granule_id = ? AND prompt_version = ? AND layer = ?",
        (package_id, granule_id, config.PROMPT_VERSION, layer),
    ).fetchone()
    return bool(row) and row["attempts"] >= config.MAX_ITEM_SUMMARY_ATTEMPTS


def _recording(conn, layer, keys_of, call):
    """Wrap a batch call so a raised LLMError still advances every item
    in the batch on the r14 ladder before propagating. Before this,
    attempts were recorded only for items still queued at the END of a
    layer, so a call that raised (a 429 storm, a CLI outage) recorded
    nothing and the same items came back untouched next cycle.

    A ProviderUnavailableError is the provider's failure, not the
    item's (GUIDE §6 r15): recording it would burn item ceilings on a
    vendor outage, so it propagates without a mark."""
    def guarded(llm, stats, entries, purpose):
        try:
            return call(llm, stats, entries, purpose)
        except ProviderUnavailableError:
            raise
        except LLMError:
            _record_attempts(conn, layer, keys_of(entries))
            raise
    return guarded


def _log_retry_ceiling(layer, queue, stats):
    """Anything past the single-retry ceiling is left unsummarized and
    said so — the coverage accounting is what discloses it. Silence here
    would look like completeness."""
    over = len(queue) - config.MAX_SINGLE_RETRIES_PER_RUN
    if over > 0:
        logger.info(
            "%s: %d item(s) past the %d single-retry ceiling — left"
            " unsummarized and disclosed by coverage, not retried singly"
            " (~%dK input tokens each on the CLI backend)",
            layer, over, config.MAX_SINGLE_RETRIES_PER_RUN, 29)
        stats.setdefault("retry_ceiling_skipped", 0)
        stats["retry_ceiling_skipped"] += over


def _retry_in_groups(llm, stats, rows, call, harvest, purpose):
    """Retry missing items in small groups, returning those still missing.

    A missing item usually means the batch response was truncated, not that
    the item is unparseable — so a group retry recovers most of them at a
    fraction of the cost. Anything still missing afterwards gets the
    single-item isolation the caller falls back to."""
    still_missing = []
    for start in range(0, len(rows), config.MAX_RETRY_BATCH_ITEMS):
        group = rows[start:start + config.MAX_RETRY_BATCH_ITEMS]
        mapping, result = call(llm, stats, group, purpose)
        still_missing.extend(harvest(group, mapping, result))
    return still_missing


def _harvest_plain(conn, stats, entries, mapping, result):
    share_in = result["input_tokens"] // len(entries)
    share_out = result["output_tokens"] // len(entries)
    missing = []
    values = _match_replies("plain", stats, entries, mapping)
    for row, plain in zip(entries, values):
        if isinstance(plain, str) and plain.strip():
            _store_plain(
                conn, row, plain=" ".join(plain.split()), model=result["model"],
                input_tokens=share_in, output_tokens=share_out,
            )
            stats["plain_written"] += 1
        else:
            missing.append(row)
    if missing:
        logger.info("plain: response covered %d of %d requested items"
                    " (short response — likely truncation)",
                    len(entries) - len(missing), len(entries))
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
        "keys_normalized": 0,
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
            WHERE p.digest_day = ? AND s.prompt_version = ?
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
    # GUIDE §6 rule 14a: same guard as run()'s map loop -- an item
    # withdrawn after exhausting its plain-correction ceiling has no
    # summaries row for a 'map' withdrawal (so it's already absent from
    # this query via the JOIN), but a 'plain'-only withdrawal leaves the
    # map summary in place and would otherwise look pending again here.
    before_guard = len(pending)
    pending = [r for r in pending
               if not _lexicon_correction_exhausted(
                   conn, r["package_id"], r["granule_id"], "plain")]
    stats["skipped_lexicon_withdrawn"] = before_guard - len(pending)
    # GUIDE §6 rule 14: an item past its per-item ceiling is a disclosed
    # gap, not pending work (backlog D4 — the plain layer recorded
    # attempts but never read them).
    before_ceiling = len(pending)
    pending = [r for r in pending
               if not _attempts_exhausted(conn, r["package_id"], r["granule_id"], "plain")]
    stats["exhausted"] = before_ceiling - len(pending)
    stats["plain_pending"] = len(pending)

    plain_call = _recording(
        conn, "plain", lambda rows: [(r["package_id"], r["granule_id"]) for r in rows],
        _plain_call)
    retry_queue = []
    for start in range(0, len(pending), config.MAX_PLAIN_BATCH_ITEMS):
        batch = pending[start : start + config.MAX_PLAIN_BATCH_ITEMS]
        batch_no = start // config.MAX_PLAIN_BATCH_ITEMS + 1
        mapping, result = plain_call(llm, stats, batch, f"plain:batch{batch_no}")
        retry_queue.extend(_harvest_plain(conn, stats, batch, mapping, result))

    # Group retry first (cheap), then single-item isolation for the stubborn
    # remainder — the reliability the old one-call-per-item path provided,
    # without paying for it on every recovered item.
    retry_queue = _retry_in_groups(
        llm, stats, retry_queue, plain_call,
        lambda group, mapping, result: _harvest_plain(conn, stats, group, mapping, result),
        "plain:retry-group")
    for row in retry_queue[:config.MAX_SINGLE_RETRIES_PER_RUN]:
        mapping, result = plain_call(llm, stats, [row], "plain:retry-single")
        if _harvest_plain(conn, stats, [row], mapping, result):
            stats["failed_items"].append(
                {"package_id": row["package_id"], "granule_id": row["granule_id"]}
            )
    _log_retry_ceiling("plain", retry_queue, stats)
    _record_attempts(conn, "plain",
                     [(r["package_id"], r["granule_id"]) for r in retry_queue])
    return stats


def _lexicon_clean(text, *titles):
    """Whether `text` clears the lexicon gate on its own, exempting only
    occurrences of THIS item's own official title(s) (GUIDE §6 rule 14a
    "context aware" self-gate) -- narrower and more permissive than the
    whole-day exemption corpus `_validate_lexicon` uses, since a single
    item's correction has no business being exempted by a DIFFERENT
    item's title. A legitimate verbatim title/name quote passes; the
    model's own word choice does not."""
    officials = [t for t in titles if t]
    exempt = _official_spans(text, officials)
    for match in _BANNED_RE.finditer(text):
        if not any(a <= match.start() and match.end() <= b for a, b in exempt):
            return False
    return True


def _lexicon_correction_exhausted(conn, package_id, granule_id, layer):
    """Whether this item's correction ceiling (GUIDE §6 rule 14a,
    config.MAX_LEXICON_CORRECTION_ATTEMPTS) is already spent -- checked
    by both correct_lexicon_violation and the pending-selection loops in
    run()/run_plain(), so a withdrawn item never re-enters ordinary
    summarization with the uncorrected prompt at the same prompt
    version."""
    row = conn.execute(
        "SELECT attempts FROM summary_attempts WHERE package_id = ?"
        " AND granule_id = ? AND prompt_version = ? AND layer = ?",
        (package_id, granule_id, config.PROMPT_VERSION, f"{layer}-correction"),
    ).fetchone()
    return bool(row) and row[0] >= config.MAX_LEXICON_CORRECTION_ATTEMPTS


def _apply_lexicon_correction(conn, package_id, granule_id, layer, text, *,
                              model, input_tokens, output_tokens):
    now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    if layer == "map":
        conn.execute(
            "UPDATE summaries SET summary = ?, model = ?, input_tokens = ?,"
            " output_tokens = ?, created_at = ?"
            " WHERE package_id = ? AND granule_id = ? AND prompt_version = ?",
            (text, model, input_tokens, output_tokens, now,
             package_id, granule_id, config.PROMPT_VERSION),
        )
    else:
        conn.execute(
            "UPDATE plain_summaries SET plain = ?, model = ?, input_tokens = ?,"
            " output_tokens = ?, created_at = ?"
            " WHERE package_id = ? AND granule_id = ? AND plain_version = ?"
            " AND source_prompt_version = ?",
            (text, model, input_tokens, output_tokens, now,
             package_id, granule_id, config.PLAIN_PROMPT_VERSION, config.PROMPT_VERSION),
        )
    conn.commit()


def _withdraw_lexicon_violation(conn, package_id, granule_id, layer):
    """Past the correction ceiling: delete rather than leave a row that
    will keep failing validate() forever (GUIDE §6 rule 14a). A 'map'
    withdrawal also deletes the dependent plain row so nothing orphaned
    lingers; a 'plain' withdrawal leaves the (clean) map summary alone."""
    if layer == "map":
        conn.execute(
            "DELETE FROM summaries WHERE package_id = ? AND granule_id = ?"
            " AND prompt_version = ?",
            (package_id, granule_id, config.PROMPT_VERSION),
        )
        conn.execute(
            "DELETE FROM plain_summaries WHERE package_id = ? AND granule_id = ?"
            " AND source_prompt_version = ?",
            (package_id, granule_id, config.PROMPT_VERSION),
        )
    else:
        conn.execute(
            "DELETE FROM plain_summaries WHERE package_id = ? AND granule_id = ?"
            " AND plain_version = ? AND source_prompt_version = ?",
            (package_id, granule_id, config.PLAIN_PROMPT_VERSION, config.PROMPT_VERSION),
        )
    conn.commit()


def _log_lexicon_correction(conn, package_id, granule_id, layer, term, outcome):
    conn.execute(
        "INSERT INTO lexicon_corrections (package_id, granule_id, layer, term,"
        " outcome, corrected_at) VALUES (?, ?, ?, ?, ?, ?)",
        (package_id, granule_id, layer, term, outcome, utc_now_iso()),
    )
    conn.commit()


def correct_lexicon_violation(conn, llm, *, package_id, granule_id, layer, term):
    """One bounded, error-informed rewrite of a map summary or plain line
    that tripped the render-time lexicon gate (GUIDE §6 rule 14a).

    `layer` is the ORIGINAL failing layer ('map' or 'plain'); attempts
    are tracked durably under f'{layer}-correction' in summary_attempts
    (via the existing _record_attempts), so the ceiling
    (config.MAX_LEXICON_CORRECTION_ATTEMPTS) holds across every future
    run, not just the current one -- a rerun that finds the ceiling
    already spent withdraws immediately rather than spending another
    call. Exhausting it withdraws the row (DELETE) rather than leaving a
    stubborn word blocking the day forever -- editorial.md's "never
    fabricate" pattern, entered through a new trigger.

    Returns {"outcome": "corrected" | "withdrawn"}.
    """
    correction_layer = f"{layer}-correction"
    row = conn.execute(
        "SELECT attempts FROM summary_attempts WHERE package_id = ?"
        " AND granule_id = ? AND prompt_version = ? AND layer = ?",
        (package_id, granule_id, config.PROMPT_VERSION, correction_layer),
    ).fetchone()
    attempts_so_far = row[0] if row else 0

    item = conn.execute(
        "SELECT s.package_id, s.granule_id, s.summary, s.inclusion_rule,"
        " e.doc_type, e.title, e.collection, e.text,"
        " g.title AS granule_title, p.title AS package_title"
        " FROM summaries s"
        " LEFT JOIN extracted_texts e"
        "   ON e.package_id = s.package_id AND e.granule_id = s.granule_id"
        " LEFT JOIN granules g"
        "   ON g.package_id = s.package_id AND g.granule_id = s.granule_id"
        " LEFT JOIN packages p ON p.package_id = s.package_id"
        " WHERE s.package_id = ? AND s.granule_id = ? AND s.prompt_version = ?",
        (package_id, granule_id, config.PROMPT_VERSION),
    ).fetchone()
    if item is None:
        # Already gone -- nothing left to correct or withdraw.
        return {"outcome": "withdrawn"}
    item = dict(item)
    titles = (item.get("title"), item.get("granule_title"), item.get("package_title"))

    while attempts_so_far < config.MAX_LEXICON_CORRECTION_ATTEMPTS:
        if layer == "map":
            text = item["text"] or ""
            if len(text) > ITEM_TEXT_LIMIT:
                text = text[:ITEM_TEXT_LIMIT] + _TEXT_TRUNCATION_NOTE
            prompt = _CORRECTION_NOTICE.format(terms=term) + _build_prompt([(item, text)])
            purpose = "map:lexicon-correction"
        else:
            prompt = _CORRECTION_NOTICE.format(terms=term) + _build_plain_prompt([item])
            purpose = "plain:lexicon-correction"

        result = llm.complete(prompt, purpose=purpose,
                              package_id=package_id, granule_id=granule_id or None)
        mapping = _parse_reply(result["text"])
        candidate, _resp_key = _match_key(mapping, item)  # same key contract as the harvests
        attempts_so_far += 1
        _record_attempts(conn, correction_layer, [(package_id, granule_id)])

        if isinstance(candidate, str) and candidate.strip():
            candidate = (candidate.strip() if layer == "map"
                        else " ".join(candidate.split()))
            if _lexicon_clean(candidate, *titles):
                _apply_lexicon_correction(
                    conn, package_id, granule_id, layer, candidate,
                    model=result["model"], input_tokens=result["input_tokens"],
                    output_tokens=result["output_tokens"],
                )
                _log_lexicon_correction(conn, package_id, granule_id, layer, term,
                                        "corrected")
                return {"outcome": "corrected"}
            logger.warning("%s: correction attempt for %s/%s still fails the"
                           " lexicon gate — self-gated, not stored",
                           correction_layer, package_id, granule_id)
        else:
            logger.warning("%s: correction attempt for %s/%s returned no usable"
                           " text", correction_layer, package_id, granule_id)

    _withdraw_lexicon_violation(conn, package_id, granule_id, layer)
    _log_lexicon_correction(conn, package_id, granule_id, layer, term, "withdrawn")
    return {"outcome": "withdrawn"}


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
        "exhausted": 0,
        "keys_normalized": 0,
        "failed_items": [],
    }
    items = rules.select_items(conn, date)
    stats["selected"] = len(items)

    pending = []  # (item, text) still needing an LLM summary
    for item in items:
        if _summary_exists(conn, item):
            stats["skipped_existing"] += 1
            continue
        # GUIDE §6 rule 14a: an item withdrawn after exhausting its
        # lexicon-correction ceiling must never re-enter ordinary
        # summarization at the same prompt version -- its absent row
        # would otherwise look like fresh pending work and reproduce the
        # identical violation with the uncorrected prompt.
        if _lexicon_correction_exhausted(conn, item["package_id"], item["granule_id"], "map"):
            stats["skipped_lexicon_withdrawn"] = stats.get("skipped_lexicon_withdrawn", 0) + 1
            continue
        # GUIDE §6 rule 14: past the per-item ceiling the item is a
        # disclosed gap. collect.pending_items already skipped these for
        # the collector's trigger; the finalizer path did not, so every
        # exhausted item was re-bought at full batch cost each EOD.
        if _attempts_exhausted(conn, item["package_id"], item["granule_id"], "map"):
            stats["exhausted"] += 1
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

    call = _recording(
        conn, "map", lambda entries: [(i["package_id"], i["granule_id"]) for i, _t in entries],
        _call)
    retry_queue = []
    for start in range(0, len(pending), MAX_BATCH_ITEMS):
        batch = pending[start : start + MAX_BATCH_ITEMS]
        batch_no = start // MAX_BATCH_ITEMS + 1
        mapping, result = call(llm, stats, batch, f"map:batch{batch_no}")
        retry_queue.extend(_harvest(conn, stats, batch, mapping, result))

    # Group retry, then single-item isolation for whatever is still missing;
    # still-failing items are recorded and skipped — never fabricated. They
    # surface as known gaps in the Coverage Statement, not as silent
    # omissions (GUIDE §2).
    retry_queue = _retry_in_groups(
        llm, stats, retry_queue, call,
        lambda group, mapping, result: _harvest(conn, stats, group, mapping, result),
        "map:retry-group")
    for entry in retry_queue[:config.MAX_SINGLE_RETRIES_PER_RUN]:
        mapping, result = call(llm, stats, [entry], "map:retry-single")
        if _harvest(conn, stats, [entry], mapping, result):
            item = entry[0]
            stats["failed_items"].append(
                {
                    "package_id": item["package_id"],
                    "granule_id": item["granule_id"],
                    "rule_id": item["rule_id"],
                }
            )
    _log_retry_ceiling("map", retry_queue, stats)
    _record_attempts(conn, "map",
                     [(i["package_id"], i["granule_id"]) for i, _t in retry_queue])
    return stats

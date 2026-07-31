"""Daily developer-insight report (the ops feedback loop; extends OB-2).

After each EOD finalization the pipeline emits one Markdown report per
digest date under provenance/runs/: request and token accounting, retry
economics, error surfaces, coverage reconciliation, and collector
liveness — every number mechanical, straight from the databases the run
already keeps (fetch_log.db, llm_ledger.db, fapd.db). One optional
cheap-tier call turns those metrics into a short "suggested next steps"
list, labeled as model output per GUIDE §2 and versioned by
INSIGHT_PROMPT_VERSION (GUIDE §3a: developer-facing surface, never
editorial — its input is the metrics table itself, never document
content). The report rides the evidence commit because provenance/ is
already an evidence path (GUIDE §10).
"""

import json
import logging
import sqlite3

from . import config
from .sync import utc_now_iso

logger = logging.getLogger("fapd.insight")

_PROMPT = """You are reviewing one day's operational metrics for an
automated publication pipeline (fetch counts, LLM token spend, retry
economics, errors, coverage, collector liveness). Suggest the most
useful next steps for the developer.

Rules:
- Ground every suggestion in a specific number or line from the metrics.
- At most five suggestions, ordered by expected payoff; fewer is fine.
- One sentence each, concrete and checkable ("investigate X", "reduce
  Y", "confirm Z") — no generic advice, no praise, no filler.
- If the metrics look healthy, say so in one line instead of inventing
  work.

Output format: STRICT JSON, a single array of suggestion strings. No
markdown fences, no other keys.

=== METRICS ===
{metrics}
"""


def _ro(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def gather(conn, date, *, fetch_db=None, ledger_db=None):
    """Mechanical metrics for the report — zero tokens. `date` is the
    digest date just finalized; request/token accounting covers today
    (UTC), which is the operational day that produced the digest."""
    import time

    day = time.strftime("%Y-%m-%d", time.gmtime())
    m = {"digest_date": date, "run_day_utc": day}

    fdb = _ro(fetch_db or config.FETCH_LOG_DB)
    try:
        m["requests"] = [
            {"client": c, "requests": n, "errors": e or 0}
            for c, n, e in fdb.execute(
                "SELECT COALESCE(client,'govinfo'), COUNT(*),"
                " SUM(CASE WHEN status IS NULL OR status >= 400 THEN 1 ELSE 0 END)"
                " FROM fetch_log WHERE ts_utc >= ? GROUP BY 1 ORDER BY 2 DESC",
                (day,))
        ]
    finally:
        fdb.close()

    ldb = _ro(ledger_db or config.LLM_LEDGER_DB)
    try:
        m["llm"] = [
            {"purpose": p, "calls": n, "input_tokens": tin or 0,
             "output_tokens": tout or 0}
            for p, n, tin, tout in ldb.execute(
                "SELECT purpose, COUNT(*), SUM(input_tokens), SUM(output_tokens)"
                " FROM llm_calls WHERE ts_utc >= ? GROUP BY 1 ORDER BY 3 DESC",
                (day,))
        ]
        total_in = sum(r["input_tokens"] for r in m["llm"])
        retry_in = sum(r["input_tokens"] for r in m["llm"]
                       if ":retry" in r["purpose"])
        m["tokens"] = {
            "input_total": total_in,
            "output_total": sum(r["output_tokens"] for r in m["llm"]),
            "retry_input": retry_in,
            "retry_share_pct": round(100 * retry_in / total_in, 1)
            if total_in else 0.0,
        }
        m["llm_errors"] = [
            {"ts_utc": ts, "purpose": p, "error": (err or "")[:200]}
            for ts, p, err in ldb.execute(
                "SELECT ts_utc, purpose, error FROM llm_calls"
                " WHERE ts_utc >= ? AND error IS NOT NULL"
                " ORDER BY ts_utc DESC LIMIT 5", (day,))
        ]
    finally:
        ldb.close()

    # Model events are journaled without a digest_date, so counting them
    # per day has to go through the ingest row for the same item. The
    # earlier query grouped every event by digest_date directly and so
    # reported zero summarized on days that plainly had summaries — a
    # feedback loop that under-reported itself (found 2026-07-31).
    m["coverage"] = [
        {"date": d, "ingested": ing, "summarized": s or 0, "plain": pl or 0}
        for d, ing, s, pl in conn.execute(
            """
            SELECT i.digest_date,
                   COUNT(*),
                   SUM(EXISTS (SELECT 1 FROM item_journal e
                               WHERE e.package_id = i.package_id
                                 AND e.granule_id = i.granule_id
                                 AND e.event = 'summarized')),
                   SUM(EXISTS (SELECT 1 FROM item_journal e
                               WHERE e.package_id = i.package_id
                                 AND e.granule_id = i.granule_id
                                 AND e.event = 'plain'))
            FROM item_journal i
            WHERE i.event = 'ingested' AND i.digest_date >= date(?, '-3 days')
            GROUP BY 1 ORDER BY 1 DESC
            """, (date,))
    ]

    m["collectors"] = [
        {"worker": w, "last_ok_at": ok, "consecutive_errors": errs}
        for w, ok, errs in conn.execute(
            "SELECT worker, last_ok_at, consecutive_errors FROM collector_state"
            " ORDER BY consecutive_errors DESC, worker")
    ]
    return m


def render_report(metrics, suggestions=None):
    """Deterministic Markdown from the metrics dict. Suggestions, when
    present, render under an explicit model-output label (GUIDE §2)."""
    L = [f"# Operations report — digest {metrics['digest_date']}", "",
         f"Run day (UTC): {metrics['run_day_utc']}. Generated by the",
         "post-EOD feedback loop; all figures mechanical from fetch_log.db,",
         "llm_ledger.db, and the item journal.", ""]

    L += ["## HTTP requests (run day, by client)", "",
          "| client | requests | errors/blocked |", "|---|---|---|"]
    L += [f"| {r['client']} | {r['requests']} | {r['errors']} |"
          for r in metrics["requests"]] or ["| — | 0 | 0 |"]

    t = metrics["tokens"]
    L += ["", "## LLM spend (run day)", "",
          (f"Total {t['input_total']:,} in / {t['output_total']:,} out tokens; "
           f"retries consumed {t['retry_input']:,} input tokens "
           f"({t['retry_share_pct']}% of input)."), "",
          "| purpose | calls | in | out |", "|---|---|---|---|"]
    L += [f"| {r['purpose']} | {r['calls']} | {r['input_tokens']:,} |"
          f" {r['output_tokens']:,} |" for r in metrics["llm"]]

    L += ["", "## Errors"]
    if metrics["llm_errors"]:
        L += [""] + [f"- `{e['ts_utc']}` {e['purpose']}: {e['error']}"
                     for e in metrics["llm_errors"]]
    else:
        L += ["", "No LLM call errors recorded on the run day."]

    L += ["", "## Coverage (journal, last 4 digest days)", "",
          "| date | ingested | summarized | plain |", "|---|---|---|---|"]
    L += [f"| {c['date']} | {c['ingested']} | {c['summarized']} |"
          f" {c['plain']} |" for c in metrics["coverage"]]

    L += ["", "## Collector liveness", "",
          "| worker | last ok (UTC) | consecutive errors |", "|---|---|---|"]
    L += [f"| {c['worker']} | {c['last_ok_at'] or '—'} |"
          f" {c['consecutive_errors']} |" for c in metrics["collectors"]]

    if suggestions is not None:
        L += ["", "## Suggested next steps", "",
              ("*The list below is model output (insight prompt v"
               f"{config.INSIGHT_PROMPT_VERSION}), generated from the metrics"
               " above only. Developer judgment decides; nothing here"
               " executes automatically.*"), ""]
        L += [f"{i}. {s}" for i, s in enumerate(suggestions, 1)] or \
             ["(no suggestions returned)"]

    L += ["", f"*Generated {utc_now_iso()}.*", ""]
    return "\n".join(L)


def suggest(llm, metrics):
    """One cheap-tier call over the metrics. Returns a list of suggestion
    strings; a malformed reply degrades to an empty list — the report's
    mechanical sections never depend on this call succeeding."""
    result = llm.complete(
        _PROMPT.format(metrics=json.dumps(metrics, indent=1)),
        purpose="insight:suggestions", model=config.MAP_MODEL,
        package_id=f"OPS-{metrics['digest_date']}")
    text = result["text"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rstrip().removesuffix("```")
    try:
        parsed = json.loads(text)
    except ValueError:
        logger.warning("insight: unparseable suggestions reply — omitted")
        return []
    return [s.strip() for s in parsed if isinstance(s, str) and s.strip()][:5]


def run(conn, llm, date, *, out_dir=None, fetch_db=None, ledger_db=None):
    """Gather, optionally suggest (llm=None skips the call), write
    provenance/runs/insight-<date>.md. Returns the path."""
    metrics = gather(conn, date, fetch_db=fetch_db, ledger_db=ledger_db)
    suggestions = suggest(llm, metrics) if llm is not None else None
    out_dir = out_dir or (config.PROJECT_ROOT / "provenance" / "runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"insight-{date}.md"
    path.write_text(render_report(metrics, suggestions), encoding="utf-8")
    logger.info("insight report written: %s (%d suggestion(s))",
                path, len(suggestions or []))
    return path

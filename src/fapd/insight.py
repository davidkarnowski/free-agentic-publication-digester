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

import datetime as dt
import json
import logging
import sqlite3

from . import config
from .llm import LLMError
from .sync import utc_now_iso

logger = logging.getLogger("fapd.insight")

#: How long after a publication day ends the finalizer may still be
#: working. The EOD run starts at midnight Eastern and takes tens of
#: minutes; six hours is generous enough to contain it and tight enough
#: that a re-run of an old date still reports that date's own work.
_FINALIZE_GRACE = dt.timedelta(hours=6)

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


def _work_window(date, *, now=None):
    """The UTC span that actually produced the digest for `date`.

    The operational day straddles the UTC boundary: publication days are
    Eastern (GUIDE §3) and the finalizer runs just after midnight
    Eastern, which is 04:00 or 05:00 UTC. Windowing on "today (UTC)" —
    what this function replaced — therefore measured only the handful of
    hours between midnight UTC and the run, and reported it as the
    day's totals. Measured against production for digest 2026-08-04: the
    report that shipped saw 1,117 of 3,231 requests (35%) and 956,741 of
    2,443,574 input tokens (39%) — and 0 of the 15 zero-billed calls.

    Returns (start, end) as 19-character naive-UTC stamps
    ("YYYY-MM-DDTHH:MM:SS"). Deliberately without an offset suffix: the
    stored columns carry both `Z` and `+00:00` forms, and those sort
    against each other wrongly ('Z' > '+'). Truncating the bound to the
    shared prefix compares correctly against either, which is the same
    reasoning behind the substr() comparisons in compose_day.
    """
    now = now or dt.datetime.now(dt.UTC)
    midnight = dt.time(0, 0)
    day = dt.date.fromisoformat(date)
    start = dt.datetime.combine(day, midnight, config.PUBLICATION_TZ)
    end = dt.datetime.combine(
        day + dt.timedelta(days=1), midnight, config.PUBLICATION_TZ)
    # Extend past the day's end to contain the finalizer run itself, but
    # never past the grace bound — a re-run of an old date must report
    # that date's work, not everything since.
    end = min(now, end.astimezone(dt.UTC) + _FINALIZE_GRACE)
    fmt = "%Y-%m-%dT%H:%M:%S"
    return (start.astimezone(dt.UTC).strftime(fmt), end.strftime(fmt))


def gather(conn, date, *, fetch_db=None, ledger_db=None, now=None):
    """Mechanical metrics for the report — zero tokens. `date` is the
    digest date just finalized; request and token accounting cover the
    Eastern publication day that produced it, plus the finalizer run
    that closed it (see `_work_window`)."""
    start, end = _work_window(date, now=now)
    m = {"digest_date": date, "window_start_utc": start,
         "window_end_utc": end}

    fdb = _ro(fetch_db or config.FETCH_LOG_DB)
    try:
        m["requests"] = [
            {"client": c, "requests": n, "errors": e or 0}
            for c, n, e in fdb.execute(
                "SELECT COALESCE(client,'govinfo'), COUNT(*),"
                " SUM(CASE WHEN status IS NULL OR status >= 400 THEN 1 ELSE 0 END)"
                " FROM fetch_log WHERE ts_utc >= ? AND ts_utc < ?"
                " GROUP BY 1 ORDER BY 2 DESC",
                (start, end))
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
                " FROM llm_calls WHERE ts_utc >= ? AND ts_utc < ?"
                " GROUP BY 1 ORDER BY 3 DESC",
                (start, end))
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
                " WHERE ts_utc >= ? AND ts_utc < ? AND error IS NOT NULL"
                " ORDER BY ts_utc DESC LIMIT 5", (start, end))
        ]
        # A CLI call can fail having billed nothing: the ledger row lands
        # with zero tokens and, depending on how the backend classified
        # it, no error string. Counting only `error IS NOT NULL` made
        # that class invisible — on 2026-08-04 fifteen zero-billed
        # failures took nine source-desc batches, six source-assess
        # batches and this report's own suggestions call, and the report
        # still said "no LLM call errors". Zero-billed is reported on its
        # own terms, always, including when it is zero.
        m["zero_billed"] = [
            {"purpose": p, "calls": n}
            for p, n in ldb.execute(
                "SELECT purpose, COUNT(*) FROM llm_calls"
                " WHERE ts_utc >= ? AND ts_utc < ?"
                " AND COALESCE(input_tokens, 0) = 0"
                " AND COALESCE(output_tokens, 0) = 0"
                " GROUP BY 1 ORDER BY 2 DESC, 1", (start, end))
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


def render_report(metrics, suggestions=None, security=None):
    """Deterministic Markdown from the metrics dict. Suggestions, when
    present, render under an explicit model-output label (GUIDE §2)."""
    L = [f"# Operations report — digest {metrics['digest_date']}", "",
         (f"Work window (UTC): {metrics['window_start_utc']}"
          f" .. {metrics['window_end_utc']} —"),
         f"the {config.PUBLICATION_TZ_LABEL} publication day this digest covers, plus the",
         "finalizer run that closed it. Generated by the post-EOD feedback",
         "loop; all figures mechanical from fetch_log.db, llm_ledger.db,",
         "and the item journal.", ""]

    L += ["## HTTP requests (work window, by client)", "",
          "| client | requests | errors/blocked |", "|---|---|---|"]
    L += [f"| {r['client']} | {r['requests']} | {r['errors']} |"
          for r in metrics["requests"]] or ["| — | 0 | 0 |"]

    t = metrics["tokens"]
    L += ["", "## LLM spend (work window)", "",
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
        L += ["", "No LLM call errors recorded in the work window."]

    zb = metrics.get("zero_billed") or []
    total_zb = sum(r["calls"] for r in zb)
    L += ["", "### Zero-billed calls", ""]
    if total_zb:
        L += [f"{total_zb} call(s) returned with no tokens billed — work",
              "that was attempted and produced nothing. A zero-billed call",
              "may carry no error string, so it is counted here separately",
              "rather than inferred from the error list above.", "",
              "| purpose | calls |", "|---|---|"]
        L += [f"| {r['purpose']} | {r['calls']} |" for r in zb]
    else:
        L += ["None — every call in the window billed tokens."]

    L += ["", "## Coverage (journal, last 4 digest days)", "",
          "| date | ingested | summarized | plain |", "|---|---|---|---|"]
    L += [f"| {c['date']} | {c['ingested']} | {c['summarized']} |"
          f" {c['plain']} |" for c in metrics["coverage"]]

    L += ["", "## Collector liveness", "",
          "| worker | last ok (UTC) | consecutive errors |", "|---|---|---|"]
    L += [f"| {c['worker']} | {c['last_ok_at'] or '—'} |"
          f" {c['consecutive_errors']} |" for c in metrics["collectors"]]

    if security is not None:
        L += render_security(security.get("sweep"), security.get("problem"),
                             security.get("summary"))

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


_SECURITY_PROMPT = """Below is a machine-generated security sweep of a
static-site VPS. Every number in it was computed by a script and every
verdict was decided by a fixed threshold before you saw it.

Rules:
- Do NOT recount, re-classify, or re-rank anything. The verdicts are
  already decided.
- Do NOT speculate about causes you cannot see in this data.
- At most 150 words.
- Say whether anything changed that a human must act on today, name the
  single most important item, and say plainly if the answer is nothing.
- If "escalate" is true, lead with it.

Output: plain prose. No markdown headings, no bullet list, no JSON.

=== SWEEP ===
{sweep}
"""


def read_sweep(path=None, *, now=None):
    """Read the nightly security sweep. Returns (sweep_dict, problem).

    Exactly one of the two is None. `problem` is a human-readable reason
    the sweep is unusable, and it is rendered in the report verbatim —
    a missing or stale sweep must be *visible*, never silent.

    The staleness check is the point of this function. A sweep file that
    stopped being written would otherwise sit on disk reporting a clean
    bill of health forever, which is exactly the F-021 failure: a green
    report describing a run that never happened.
    """
    path = path or config.SECURITY_SWEEP_PATH
    try:
        with open(path) as fh:
            sweep = json.load(fh)
    except FileNotFoundError:
        return None, f"no sweep file at {path} — the host timer did not run"
    except (OSError, ValueError) as exc:
        return None, f"sweep file at {path} is unreadable: {exc}"

    stamp = sweep.get("generated_utc")
    if not stamp:
        return None, "sweep file carries no generated_utc — cannot trust its age"
    try:
        generated = dt.datetime.fromisoformat(stamp)
    except ValueError:
        return None, f"sweep file has an unparseable generated_utc: {stamp!r}"
    if generated.tzinfo is None:
        generated = generated.replace(tzinfo=dt.UTC)

    now = now or dt.datetime.now(dt.UTC)
    age = now - generated
    if age > dt.timedelta(hours=config.SECURITY_SWEEP_STALE_HOURS):
        hours = age.total_seconds() / 3600
        return None, (f"sweep is {hours:.0f}h old (generated {stamp}), past the "
                      f"{config.SECURITY_SWEEP_STALE_HOURS}h limit — treat as DID NOT RUN")
    return sweep, None


def render_security(sweep, problem=None, summary=None):
    """The security section. Entirely mechanical; `summary` is prose and
    the section is complete without it."""
    L = ["", "## Security sweep", ""]
    if problem:
        L += [f"**The sweep is unavailable: {problem}.**", "",
              "No security state is reported for this day. This line is",
              "deliberately loud: an absent sweep is a gap in the record,",
              "not a clean result.", ""]
        return L

    v = sweep.get("verdicts", [])
    if sweep.get("escalate"):
        crit = [x for x in v if x.get("severity") == "critical"]
        L += ["> **ESCALATE — " + str(len(crit)) + " critical finding(s).**",
              "> " + "; ".join(x["detail"] for x in crit), ""]

    probing = sweep.get("probing", {})
    L += [(f"Window: {sweep.get('window_hours', '?')}h to "
           f"{sweep.get('generated_utc', '?')}."), "",
          "| measure | value |", "|---|---|",
          f"| probe requests | {probing.get('events', 0)} |",
          f"| distinct probing addresses | {probing.get('distinct_ips', 0)} |",
          f"| correlated campaign findings | {len(probing.get('findings', []))} |",
          (f"| **probe paths served a 2xx** | "
           f"**{sweep.get('refusals', {}).get('probes_served_2xx', 0)}** |"),
          (f"| failed SSH attempts | {sweep.get('auth', {}).get('failed_ssh', 0)}"
           f" from {sweep.get('auth', {}).get('failed_ssh_distinct_ips', 0)} address(es) |"),
          (f"| host security packages pending | "
           f"{sweep.get('patch', {}).get('host_security_pending', 0)} |"),
          (f"| containers not healthy | "
           f"{sweep.get('integrity', {}).get('unhealthy', 0)} |")]

    fam = probing.get("by_family") or {}
    if fam:
        L += ["", "Probe families seen: "
              + ", ".join(f"{k} ({n})" for k, n in sorted(fam.items(), key=lambda x: -x[1]))
              + "."]

    if v:
        L += ["", "| severity | finding | detail |", "|---|---|---|"]
        L += [f"| {x['severity']} | `{x['key']}` | {x['detail']} |" for x in v]
    else:
        L += ["", "No verdict tripped a threshold."]

    tls = sweep.get("tls") or []
    if tls:
        L += ["", "Certificates: "
              + "; ".join(f"{c['cert']} {c['days']}d" for c in tls) + "."]

    if sweep.get("stage_errors"):
        L += ["", "*Sweep stages that errored (their figures are missing, not zero): "
              + "; ".join(sweep["stage_errors"]) + ".*"]

    thresholds = sweep.get("thresholds", {})
    if thresholds:
        L += ["", "*Verdicts were computed against: "
              + ", ".join(f"{k}={val}" for k, val in sorted(thresholds.items())) + ".*"]

    if summary:
        L += ["", (f"*Model summary (security prompt v"
                   f"{config.SECURITY_PROMPT_VERSION}), over the classified"
                   f" sweep above; it decides nothing.*"), "", summary]
    else:
        L += ["", "*(no inference available; the mechanical findings above are complete)*"]
    return L


def summarize_security(llm, sweep):
    """One cheap-tier call over the already-classified sweep. Returns a
    string, or None if the call fails — the section never depends on it.

    The payload is trimmed first: address lists and full path samples
    are evidence for a human reading the JSON, not context a summariser
    needs, and they are the only unbounded fields in the file."""
    trimmed = json.loads(json.dumps(sweep))
    for f in trimmed.get("probing", {}).get("findings", []):
        f.pop("sample_paths", None)
        if isinstance(f.get("ips"), list):
            f["ips"] = f["ips"][:5]
    trimmed.get("auth", {}).pop("accepted_from", None)
    result = llm.complete(
        _SECURITY_PROMPT.format(sweep=json.dumps(trimmed, indent=1)),
        purpose="security:summary", model=config.MAP_MODEL,
        package_id=f"SEC-{sweep.get('generated_utc', '')[:10]}")
    return (result["text"] or "").strip() or None


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


def run(conn, llm, date, *, out_dir=None, fetch_db=None, ledger_db=None,
        sweep_path=None):
    """Gather, optionally suggest (llm=None skips the call), write
    provenance/runs/insight-<date>.md. Returns the path."""
    metrics = gather(conn, date, fetch_db=fetch_db, ledger_db=ledger_db)
    suggestions = None
    if llm is not None:
        # The mechanical report is the product; the suggestions are a
        # garnish. `suggest` already degrades a malformed *reply* to an
        # empty list, but a failed *call* raised straight through here
        # and took the whole report with it: on 2026-08-04 a zero-billed
        # CLI failure on insight:suggestions meant insight-2026-08-03.md
        # was never written, and nothing noticed it was missing. Honor
        # the contract this module's docstrings already state.
        try:
            suggestions = suggest(llm, metrics)
        except LLMError as exc:
            logger.warning(
                "insight: suggestions call failed (%s) — writing the"
                " mechanical report without them", exc)
            suggestions = []
    # The security sweep is produced on the HOST by a systemd timer at
    # 03:40 UTC and read here through a read-only bind mount. It is
    # gathered after the suggestions call so that a provider outage
    # cannot cost us the security section too: read_sweep touches no
    # provider, and render_security is complete without prose.
    sweep, problem = read_sweep(sweep_path)
    security = {"sweep": sweep, "problem": problem, "summary": None}
    if sweep is not None and llm is not None:
        try:
            security["summary"] = summarize_security(llm, sweep)
        except LLMError as exc:
            logger.warning(
                "insight: security summary call failed (%s) — the mechanical"
                " findings are unaffected", exc)

    out_dir = out_dir or (config.PROJECT_ROOT / "provenance" / "runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"insight-{date}.md"
    path.write_text(render_report(metrics, suggestions, security), encoding="utf-8")
    logger.info("insight report written: %s (%d suggestion(s), security: %s)",
                path, len(suggestions or []),
                problem or f"{len(sweep.get('verdicts', []))} verdict(s)")
    return path

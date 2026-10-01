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

The host security sweep is the one exception: its findings are
operational security posture (certificates, host patch state,
authentication-failure counts, detection thresholds), which CLAUDE.md
§13 keeps out of the public repository (operator ruling 2026-09-29). It
is rendered into a separate
PRIVATE report under config.INSIGHT_SECURITY_DIR — gitignored and never
staged by the evidence commit — while the public report keeps only a
neutral pointer that leaks no posture. The loud "sweep did not run"
disclosure is preserved in full, in the private file.
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


#: A registered email source whose mailbox rows over this many days are
#: all subscription notices is flagged: it may be sending its bulletins
#: from an address the registry does not list (the EPA case, 2026-09-26).
_NOTICE_ONLY_DAYS = 14


def gather_email(conn, start, end, entries=None):
    """The Mailbox section's facts (plan-2026-09-26-mailbox-reporting T5).

    Counts and registry ids only — this report is committed publicly, so
    no sender address, subject, or body text appears. Unregistered
    government lists are counted; their addresses stay in the database
    (scripts/file_mailbox.py --report-unregistered)."""
    if entries is None:
        from .sources import load_registry
        entries = load_registry()
    email_ids = sorted(e["id"] for e in entries
                       if e["type"] == "email" and e["status"] in ("active", "planned"))
    out = {"available": True, "sources": [], "flags": [],
           "unregistered": {"messages": 0, "senders": 0, "new_senders": 0},
           "refused": 0}
    try:
        rows = conn.execute(
            "SELECT source_id, outcome, COUNT(*), SUM(items), SUM(no_url_items)"
            " FROM mailbox_messages WHERE source_id IS NOT NULL"
            " AND substr(observed_at, 1, 19) >= ? AND substr(observed_at, 1, 19) < ?"
            " GROUP BY 1, 2", (start, end)).fetchall()
    except sqlite3.OperationalError:
        return {"available": False}
    per = {}
    for sid, outcome, n, items, no_url in rows:
        rec = per.setdefault(sid, {"id": sid, "ingested": 0, "administrative": 0,
                                   "duplicate": 0, "empty": 0, "refused": 0,
                                   "error": 0, "items": 0, "no_url_items": 0})
        rec[outcome] = rec.get(outcome, 0) + n
        rec["items"] += items or 0
        rec["no_url_items"] += no_url or 0
    out["sources"] = [per[k] for k in sorted(per)]
    out["refused"] = sum(r["refused"] for r in out["sources"])

    for rec in out["sources"]:
        if rec["id"] not in email_ids:
            out["flags"].append(f"{rec['id']}: mail handled for a source that is "
                                "no longer active or planned in the registry")
        if rec["empty"]:
            out["flags"].append(f"{rec['id']}: {rec['empty']} bulletin(s) yielded "
                                "no item (parser extracted nothing; check)")
        if rec["no_url_items"]:
            out["flags"].append(f"{rec['id']}: {rec['no_url_items']} item(s) stored "
                                "without a URL (these can never be corroborated)")
        if rec["refused"]:
            out["flags"].append(f"{rec['id']}: {rec['refused']} junk-folder "
                                "message(s) refused on DKIM")
        if rec["error"]:
            out["flags"].append(f"{rec['id']}: {rec['error']} message(s) failed "
                                "processing")

    # Notice-only subscriptions over a longer span than the work window.
    lookback = conn.execute(
        "SELECT source_id, SUM(outcome = 'administrative'), COUNT(*)"
        " FROM mailbox_messages WHERE source_id IS NOT NULL"
        " AND substr(observed_at, 1, 10) >= date(?, ?) GROUP BY 1",
        (end[:10], f"-{_NOTICE_ONLY_DAYS} days")).fetchall()
    for sid, admin, total in lookback:
        if admin and admin == total:
            out["flags"].append(
                f"{sid}: only subscription notices in {_NOTICE_ONLY_DAYS} days — "
                "bulletins may be arriving from an unregistered address")

    # One document through two registered email sources: possible
    # misattribution, or two lists syndicating one release.
    from .report import _normalize_official_url
    by_url = {}
    for sid, url in conn.execute(
            "SELECT json_extract(e.metadata, '$.source_id'),"
            " json_extract(e.metadata, '$.url') FROM extracted_texts e"
            " JOIN packages p USING (package_id) WHERE e.collection = 'AGENCYPR'"
            " AND json_extract(e.metadata, '$.channel') = 'email'"
            " AND substr(p.first_seen_at, 1, 19) >= ?"
            " AND substr(p.first_seen_at, 1, 19) < ?", (start, end)):
        key = _normalize_official_url(url)
        if key:
            by_url.setdefault(key, set()).add(sid)
    pairs = {}
    for sids in by_url.values():
        if len(sids) > 1:
            pair = " + ".join(sorted(sids))
            pairs[pair] = pairs.get(pair, 0) + 1
    for pair, n in sorted(pairs.items()):
        out["flags"].append(f"{pair}: {n} document(s) arrived through both "
                            "email sources")

    msgs, senders = conn.execute(
        "SELECT COUNT(*), COUNT(DISTINCT sender) FROM mailbox_messages"
        " WHERE outcome = 'unregistered' AND substr(observed_at, 1, 19) >= ?"
        " AND substr(observed_at, 1, 19) < ?", (start, end)).fetchone()
    new = conn.execute(
        "SELECT COUNT(*) FROM (SELECT sender FROM mailbox_messages"
        " WHERE outcome = 'unregistered' GROUP BY sender"
        " HAVING substr(MIN(observed_at), 1, 19) >= ?"
        " AND substr(MIN(observed_at), 1, 19) < ?)", (start, end)).fetchone()[0]
    out["unregistered"] = {"messages": msgs, "senders": senders, "new_senders": new}
    if new:
        out["flags"].append(
            f"{new} government list sender(s) seen for the first time and not in "
            "the registry — review with scripts/file_mailbox.py "
            "--report-unregistered")
    return out


def _provider_metrics(ldb, start, end):
    """Per-backend availability and the fallback reserve's state (T4)."""
    out = {"fallback_reserve": None}
    out["providers"] = [
        {"backend": b, "calls": n, "billed": billed or 0,
         "refused": refused or 0, "short_circuit": sc or 0,
         "first_refusal": first, "last_refusal": last}
        for b, n, billed, refused, sc, first, last in ldb.execute(
            "SELECT backend, COUNT(*),"
            " SUM(COALESCE(input_tokens, 0) > 0),"
            " SUM(error IS NOT NULL AND COALESCE(input_tokens, 0) = 0"
            "     AND error NOT LIKE '%(short-circuit)%'),"
            " SUM(error LIKE '%(short-circuit)%'),"
            " MIN(CASE WHEN error IS NOT NULL AND COALESCE(input_tokens, 0) = 0"
            "     AND error NOT LIKE '%(short-circuit)%' THEN ts_utc END),"
            " MAX(CASE WHEN error IS NOT NULL AND COALESCE(input_tokens, 0) = 0"
            "     AND error NOT LIKE '%(short-circuit)%' THEN ts_utc END)"
            " FROM llm_calls WHERE ts_utc >= ? AND ts_utc < ?"
            " GROUP BY 1 ORDER BY 1", (start, end))
    ]
    fb = config.LLM_BACKEND_FALLBACK
    if fb:
        since = (dt.datetime.fromisoformat(end) - dt.timedelta(hours=24)
                 ).strftime("%Y-%m-%dT%H:%M:%S")
        used = ldb.execute(
            "SELECT COUNT(*) FROM llm_calls WHERE backend = ? AND ts_utc >= ?"
            " AND ts_utc < ? AND COALESCE(error, '') NOT LIKE"
            " '%(short-circuit)%'", (fb, since, end)).fetchone()[0]
        out["fallback_reserve"] = {
            "backend": fb, "daily_calls": config.LLM_FALLBACK_DAILY_CALLS,
            "collector_share": config.LLM_FALLBACK_COLLECTOR_SHARE,
            "collector_budget": config.collector_fallback_budget(),
            "used_24h": used}
    return out


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
        # Provider availability (plan-2026-09-27-inference-fallback T4). A
        # 36-hour CLI refusal (2026-09-24/26) read as five error lines in
        # this report; the span, per backend, is what the operator needs.
        # A refusal is a zero-billed error that reached the provider;
        # short-circuits are counted apart (they reached nothing).
        try:
            m.update(_provider_metrics(ldb, start, end))
        except sqlite3.OperationalError:
            # A ledger that predates the backend column (before 2026-07-30).
            m["providers"], m["fallback_reserve"] = [], None
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
    m["email"] = gather_email(conn, start, end)
    return m


def render_report(metrics, suggestions=None):
    """Deterministic Markdown from the metrics dict. Suggestions, when
    present, render under an explicit model-output label (GUIDE §2).

    The security sweep is not part of this public report — see the module
    docstring and render_security_report; only a neutral pointer remains."""
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

    L += render_providers(metrics.get("providers"), metrics.get("fallback_reserve"))

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

    L += render_email(metrics.get("email"))

    L += ["", "## Security sweep", "",
          "A host security sweep runs after finalization; its findings are",
          "recorded privately on the server and are not part of this public",
          "report (CLAUDE.md §13 — VPS security posture is not published to",
          "the repository)."]

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


def render_providers(providers, reserve):
    """Per-backend availability over the work window, and the fallback
    reserve's state (GUIDE §6 r7, amended 2026-09-27)."""
    L = ["", "## Provider availability (work window)", ""]
    if not providers:
        return L + ["No model calls in the window."]
    L += [("| backend | calls | billed | refused | short-circuit |"
           " refusals from .. to (UTC) |"), "|---|---|---|---|---|---|"]
    for p in providers:
        span = (f"{p['first_refusal'][:16]} .. {p['last_refusal'][:16]}"
                if p["refused"] else "—")
        L.append(f"| {p['backend']} | {p['calls']} | {p['billed']} |"
                 f" {p['refused']} | {p['short_circuit']} | {span} |")
    if reserve:
        L += ["", (f"Fallback `{reserve['backend']}`: {reserve['used_24h']} call(s)"
                   f" in the 24 h to the window's end, of a"
                   f" {reserve['daily_calls']}-call daily allowance; the"
                   f" continuous analyze layer may use {reserve['collector_budget']}"
                   f" ({reserve['collector_share']:.0%}), the rest is held for"
                   " the finalizer.")]
    return L


def render_email(email):
    """The Mailbox section. Counts and registry ids only (public report)."""
    L = ["", "## Mailbox (work window)", ""]
    if not email or not email.get("available"):
        return L + ["The mailbox log is not present in this database yet."]
    L += ["What the email poll did with each registered sender's mail,",
          "including messages that produced no item. A duplicate is a",
          "bulletin whose items had all arrived already — through another",
          "channel, or through another of the sender's own GovDelivery lists",
          "(topic-list overlap). 'No item' is reserved for a parse that",
          "yielded nothing.", ""]
    if email["sources"]:
        L += [("| source | ingested | notices | duplicate | no item | refused |"
               " errors | items | items without URL |"),
              "|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {r['id']} | {r['ingested']} | {r['administrative']} |"
              f" {r['duplicate']} | {r['empty']} | {r['refused']} | {r['error']} |"
              f" {r['items']} | {r['no_url_items']} |" for r in email["sources"]]
    else:
        L += ["No registered sender's mail was handled in the window."]
    u = email["unregistered"]
    L += ["", (f"Unregistered government lists: {u['messages']} message(s) from"
               f" {u['senders']} sender(s), {u['new_senders']} new. Addresses are"
               " not printed here; `scripts/file_mailbox.py --report-unregistered`"
               " lists them.")]
    L += ["", "### Classification flags", ""]
    clean = ("None — every handled message matched its registered source"
             " cleanly.")
    L += [f"- {f}" for f in email["flags"]] or [clean]
    return L


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


def _by_host(counts):
    """' (host: n, …)' for a per-host breakdown, or '' when there is none."""
    if not counts:
        return ""
    return " (" + ", ".join(f"{h}: {n}" for h, n in sorted(counts.items())) + ")"


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
           f"**{sweep.get('refusals', {}).get('probes_served_2xx', 0)}**"
           f"{_by_host(sweep.get('refusals', {}).get('probes_served_2xx_by_host'))} |"),
          # 2026-09-27: a single-page app answering every unknown path with
          # its own index page is not a probe being served. The sweep
          # classifies it separately; shown so the count stays visible.
          (f"| probe paths answered by an app's own index page |"
           f" {sweep.get('refusals', {}).get('probes_app_fallback', 0)} |"),
          (f"| failed SSH attempts (window) | "
           f"{sweep.get('auth', {}).get('failed_ssh', 0)}"
           f" from {sweep.get('auth', {}).get('failed_ssh_distinct_ips', 0)} address(es) |"),
          # All-time is context, not the window's number, and is labeled
          # so it can never be read as one. The first render conflated
          # them and reported a day with no failures as having 54.
          (f"| failed SSH attempts (retained) | "
           f"{sweep.get('auth', {}).get('failed_ssh_alltime', 0)}"
           f" from {sweep.get('auth', {}).get('failed_ssh_alltime_distinct_ips', 0)}"
           f" address(es) |"),
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


def render_security_report(date, sweep, problem=None, summary=None):
    """The standalone PRIVATE security report. Same section body the public
    report used to embed, written instead to config.INSIGHT_SECURITY_DIR
    (gitignored, host-durable, never staged by the evidence commit) —
    VPS security posture is not public-repository content (CLAUDE.md §13,
    operator ruling 2026-09-29). The loud 'sweep did not run' disclosure
    is preserved here in full."""
    L = [f"# Security sweep (private) — {date}", "",
         "Host security posture for the operator. NOT committed to the",
         "public repository (CLAUDE.md §13). Generated by the post-EOD",
         "feedback loop; the public insight report carries only a pointer."]
    L += render_security(sweep, problem, summary)
    L += ["", f"*Generated {utc_now_iso()}.*", ""]
    return "\n".join(L)


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
        sweep_path=None, security_dir=None):
    """Gather, optionally suggest (llm=None skips the call), write the
    public provenance/runs/insight-<date>.md and the private
    security-<date>.md. Returns the public report path."""
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
    path.write_text(render_report(metrics, suggestions), encoding="utf-8")

    # The security sweep is PRIVATE (CLAUDE.md §13, operator ruling
    # 2026-09-29): written to a gitignored, host-durable directory the
    # evidence commit never stages — never into the public report above.
    security_dir = security_dir or config.INSIGHT_SECURITY_DIR
    security_dir.mkdir(parents=True, exist_ok=True)
    sec_path = security_dir / f"security-{date}.md"
    sec_path.write_text(
        render_security_report(date, sweep, problem, security["summary"]),
        encoding="utf-8")

    logger.info("insight report written: %s (%d suggestion(s)); security"
                " (private): %s (%s)", path, len(suggestions or []), sec_path,
                problem or f"{len(sweep.get('verdicts', []))} verdict(s)")
    return path

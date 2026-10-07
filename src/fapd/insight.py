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

Since 2026-10-07 the private report opens with "Action today": each
verdict triaged against earlier nights (new, standing with nights open,
cleared) and routed to whoever acts. Each night leaves a small record
(security-<date>.record.json: verdict keys, hashed login addresses,
edge status counts) for the next night to compare against. The model
summary must pass ungrounded() or it is withheld.
"""

import datetime as dt
import hashlib
import json
import logging
import re
import sqlite3
import statistics

from . import config, fedcal
from .llm import LLMError
from .sync import utc_now_iso

logger = logging.getLogger("fapd.insight")

#: How long after a publication day ends the finalizer may still be
#: working. The EOD run starts at midnight Eastern and takes tens of
#: minutes; six hours is generous enough to contain it and tight enough
#: that a re-run of an old date still reports that date's own work.
_FINALIZE_GRACE = dt.timedelta(hours=6)

_PROMPT = """You are reviewing one day's operational metrics for an
automated pipeline that reads official US federal publications and
publishes a daily, cited digest. The metrics cover fetch counts and
answers, LLM token spend, coverage, packages filed for the day,
collector liveness and the email feed. Suggest the most useful next
steps for the developer.

What is normal here by design (do not suggest "fixing" these):
- govinfo often answers 503 with Retry-After while it builds a file.
  The download is set aside and tried again after the rest of the queue,
  never sooner than the server asked. Judge govinfo by the packages left
  unfetched for the day, not by its error count. Failed requests count
  against the request budget on purpose.
- Court-opinion packages marked "skipped" are revisions of old cases
  outside a seven-day window, skipped on purpose.
- A model layer recorded "idle" had nothing to work from (often a
  weekend or holiday, shown in the coverage table). It did not fail.
- The analysis layer works only on the current publication day and the
  day before; older unsummarized items are disclosed gaps, not backlog.
- An email "duplicate" is a bulletin whose items had already arrived,
  through another channel or another of the sender's own lists. Mail
  that fails sender verification is refused, never counted a duplicate.
- An email item "without URL" came from a bulletin that links to
  nothing for that item. It is stored, and it cannot be corroborated.
- There is no daily token cap: spend is measured first, on purpose.

Rules:
- Ground every suggestion in a figure from the metrics, quoted exactly
  as it appears there. Do not compute new ratios or invent baselines;
  compare only with a baseline the metrics give.
- Never suggest raising a request budget or ceiling, retrying sooner
  than a server asked, loosening a validation gate, re-rendering a
  frozen digest, or working around an access refusal. Those are the
  operator's decisions, not fixes.
- This report is public. Describe what a server answered; never
  characterize a publisher, agency or person. Do not mention hosting,
  servers' locations or security.
- At most five suggestions, ordered by expected payoff; fewer is fine.
  One sentence each, concrete and checkable. No generic advice, no
  praise, no filler.
- If the metrics look healthy, say so in one suggestion instead of
  inventing work.

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


def _request_counts(fdb, start, end):
    return fdb.execute(
        "SELECT COALESCE(client,'govinfo'), COUNT(*),"
        " SUM(CASE WHEN status IS NULL OR status >= 400 THEN 1 ELSE 0 END)"
        " FROM fetch_log WHERE ts_utc >= ? AND ts_utc < ?"
        " GROUP BY 1 ORDER BY 2 DESC", (start, end)).fetchall()


#: Earlier work windows the error baseline is computed over.
_BASELINE_WINDOWS = 7


def _error_baseline(fdb, date, *, now=None):
    """Each client's error rate over the previous work windows: median
    and range. Until 2026-10-07 the model compared the day with a
    baseline nobody had given it ("the established 18.1%", a figure from
    a July ruling); this one is measured every night from the same log."""
    rates = {}
    day = dt.date.fromisoformat(date)
    for k in range(1, _BASELINE_WINDOWS + 1):
        start, end = _work_window((day - dt.timedelta(days=k)).isoformat(), now=now)
        for c, n, e in _request_counts(fdb, start, end):
            if n:
                rates.setdefault(c, []).append(round(100 * (e or 0) / n, 1))
    return {c: {"windows": len(r), "median_pct": round(statistics.median(r), 1),
                "min_pct": min(r), "max_pct": max(r)}
            for c, r in sorted(rates.items())}


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
            {"client": c, "requests": n, "errors": e or 0,
             "error_pct": round(100 * (e or 0) / n, 1) if n else 0.0}
            for c, n, e in _request_counts(fdb, start, end)
        ]
        # What the errors were (2026-10-07). A bare count let the model
        # read govinfo's routine 503 set-asides as a failure to
        # investigate; the status split says what the servers answered.
        by_status = {}
        for c, st, n in fdb.execute(
                "SELECT COALESCE(client,'govinfo'), COALESCE(CAST(status AS TEXT), 'none'),"
                " COUNT(*) FROM fetch_log WHERE ts_utc >= ? AND ts_utc < ?"
                " AND (status IS NULL OR status >= 400) GROUP BY 1, 2 ORDER BY 3 DESC",
                (start, end)):
            by_status.setdefault(c, {})[st] = n
        for r in m["requests"]:
            r["errors_by_status"] = by_status.get(r["client"], {})
        m["error_baseline"] = _error_baseline(fdb, date, now=now)
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

    # The day's calendar and each model layer's outcome (2026-10-07): the
    # model read a quiet Sunday's idle layers as a failure to investigate.
    try:
        layers = {d: json.loads(lj) for d, lj in conn.execute(
            "SELECT date, layers FROM day_inference WHERE date >= date(?, '-3 days')",
            (date,))}
    except (sqlite3.OperationalError, ValueError):
        layers = {}
    for c in m["coverage"]:
        rp = fedcal.reduced_publishing(c["date"])
        c["calendar"] = f"{rp['kind']}: {rp['name']}" if rp else "business day"
        c["layers"] = layers.get(c["date"])

    # What happened to the day's packages: the outcome a govinfo error
    # count stands in for, badly.
    try:
        m["packages"] = [
            {"collection": c, "status": st, "count": n}
            for c, st, n in conn.execute(
                "SELECT collection, fetch_status, COUNT(*) FROM packages"
                " WHERE digest_day = ? GROUP BY 1, 2 ORDER BY 1, 2", (date,))]
    except sqlite3.OperationalError:
        m["packages"] = []

    # Packages given up on (OB-31's second gap, 2026-10-07). A package past
    # its fetch or extraction ceiling is a disclosed gap, never re-queued;
    # the 2026-09-29 Federal Register issue went that way and its digest
    # showed a zero, not a gap, while nothing reported the package. Listed
    # when the ceiling was reached inside this window, whatever its digest
    # day, so each one is reported exactly once, plus the standing totals.
    try:
        m["exhausted"] = [
            {"layer": layer, "collection": c, "package_id": pid, "digest_day": d,
             "attempts": n}
            for layer, c, pid, d, n in conn.execute(
                "SELECT 'fetch', collection, package_id, digest_day, fetch_attempts"
                " FROM packages WHERE fetch_status = 'exhausted'"
                " AND substr(last_attempt_at, 1, 19) >= ? AND substr(last_attempt_at, 1, 19) < ?"
                " UNION ALL"
                " SELECT 'extract', collection, package_id, digest_day, extract_attempts"
                " FROM packages WHERE extract_attempts >= ?"
                " AND substr(last_extract_attempt_at, 1, 19) >= ?"
                " AND substr(last_extract_attempt_at, 1, 19) < ?"
                " ORDER BY 1, 2, 3",
                (start, end, config.MAX_PACKAGE_EXTRACT_ATTEMPTS, start, end))]
        m["exhausted_totals"] = [
            {"collection": c, "packages": n}
            for c, n in conn.execute(
                "SELECT collection, COUNT(*) FROM packages"
                " WHERE fetch_status = 'exhausted' OR extract_attempts >= ?"
                " GROUP BY 1 ORDER BY 2 DESC, 1", (config.MAX_PACKAGE_EXTRACT_ATTEMPTS,))]
    except sqlite3.OperationalError:
        m["exhausted"], m["exhausted_totals"] = [], []

    m["collectors"] = [
        {"worker": w, "last_ok_at": ok, "consecutive_errors": errs}
        for w, ok, errs in conn.execute(
            "SELECT worker, last_ok_at, consecutive_errors FROM collector_state"
            " ORDER BY consecutive_errors DESC, worker")
    ]
    m["email"] = gather_email(conn, start, end)
    return m


def render_exhausted(rows, totals):
    """Packages that reached a retry ceiling in the work window. Always
    rendered, including when there are none: a gap must be visible."""
    if rows is None:
        return []
    L = ["", "## Packages given up on (work window)", "",
         "A package past its fetch or extraction retry ceiling is not tried",
         "again unless its content changes. Whatever it held is missing from",
         "its digest day and belongs in a correction.", ""]
    if rows:
        L += ["| layer | collection | package | digest day | attempts |",
              "|---|---|---|---|---|"]
        L += [f"| {r['layer']} | {r['collection']} | {r['package_id']} |"
              f" {r['digest_day'] or '—'} | {r['attempts']} |" for r in rows]
    else:
        L += ["None reached a ceiling in this window."]
    if totals:
        L += ["", "All packages given up on to date: "
              + ", ".join(f"{t['collection']} {t['packages']}" for t in totals) + "."]
    return L


def _status_list(counts):
    return ", ".join(f"{s}: {n}" for s, n in (counts or {}).items()) or "—"


def _layer_list(layers):
    """'all ran', or 'compose ran; map idle, plain idle, …'."""
    if not layers:
        return "—"
    states = set(layers.values())
    if len(states) == 1:
        return f"all {states.pop()}"
    groups = {}
    for name, st in sorted(layers.items()):
        groups.setdefault(st, []).append(name)
    order = {"ran": 0, "idle": 1, "skipped": 2, "failed": 3}
    return "; ".join(f"{', '.join(n)} {st}" for st, n in
                     sorted(groups.items(), key=lambda g: (order.get(g[0], 9), g[0])))


def render_report(metrics, suggestions=None, withheld=0):
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
          "| client | requests | errors/blocked | answers counted as errors |",
          "|---|---|---|---|"]
    L += [f"| {r['client']} | {r['requests']} | {r['errors']}"
          f"{' (' + str(r['error_pct']) + '%)' if 'error_pct' in r else ''} |"
          f" {_status_list(r.get('errors_by_status'))} |"
          for r in metrics["requests"]] or ["| — | 0 | 0 | — |"]
    base = metrics.get("error_baseline") or {}
    if base:
        L += ["", "Error rate in the previous work windows: " + "; ".join(
            f"{c} median {b['median_pct']}% (range {b['min_pct']}–{b['max_pct']}%,"
            f" {b['windows']} windows)" for c, b in base.items()) + "."]

    pk = metrics.get("packages") or []
    if pk:
        L += ["", "## Packages filed for this digest day", "",
              "| collection | status | packages |", "|---|---|---|"]
        L += [f"| {p['collection']} | {p['status']} | {p['count']} |" for p in pk]

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

    L += render_exhausted(metrics.get("exhausted"), metrics.get("exhausted_totals"))

    L += ["", "## Coverage (journal, last 4 digest days)", "",
          "| date | day | ingested | summarized | plain | model layers |",
          "|---|---|---|---|---|---|"]
    L += [f"| {c['date']} | {c.get('calendar', '—')} | {c['ingested']} |"
          f" {c['summarized']} | {c['plain']} | {_layer_list(c.get('layers'))} |"
          for c in metrics["coverage"]]

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
        if withheld:
            L += ["", (f"*{withheld} suggestion(s) withheld: each cited a figure that"
                       " does not appear in the metrics above.*")]

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


_SECURITY_PROMPT = """Below is tonight's machine-generated security sweep of
a VPS, and a mechanical triage of its verdicts against earlier nights:
"act" (new tonight, or critical), "standing" (open on earlier nights
too, with the number of nights), "watch" (new, lower severity),
"recorded" (low severity: nothing to do) and "cleared" (open last night,
gone tonight). Every number was computed by a script and every verdict
was decided by a fixed threshold before you saw it.

Rules:
- Use only facts present in the data below. Do not name any company,
  hosting provider, network, country, product or attacker the data does
  not name, and do not guess where traffic came from.
- Do NOT recount, re-classify or re-rank anything; quote numbers exactly
  as they appear.
- A verdict has already passed its threshold: never call it
  "approaching" or "near" one.
- Lead with what is in "act". If "act" is empty, say plainly that
  nothing new needs action, then give the standing items in one
  sentence with how many nights each has been open.
- If "escalate" is true, lead with it.
- At most 120 words.

Output: plain prose. No markdown headings, no bullet list, no JSON.

=== TRIAGE ===
{triage}

=== SWEEP ===
{sweep}
"""

#: Severity order, most urgent first. "low" (added to the sweep
#: 2026-10-07) means recorded, nothing to do.
_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

#: Who acts on a verdict, by key prefix (longest match wins). The sweep
#: decides THAT something is wrong; this only routes it, so the morning
#: reader knows whose list it belongs on.
_WHO_ACTS = {
    "intrusion.": "operator, now",
    "auth.": "operator, now",
    "integrity.auth_changed": "operator: confirm the change was yours",
    "integrity.schedule_changed": "operator: confirm (a staged script or a package?)",
    "integrity.image_changed": "confirm it was a deploy",
    "campaign.": "edge configuration",
    "jail.": "edge configuration",
    "edge.": "edge configuration",
    "tls.": "edge configuration (certificates)",
    "retention.": "edge configuration (log retention)",
    "sweep.": "the sweep's owner",
    "fault.upstream_5xx": "the failing site's project",
    "patch.host": "operator (host packages)",
    "patch.reboot": "operator (host reboot)",
    "patch.base_age": "image refresh (each image's owner)",
    "host.disk": "operator (disk)",
    "health.container": "the container's project",
}


def _who_acts(key):
    best = max((p for p in _WHO_ACTS if key.startswith(p)), key=len, default=None)
    return _WHO_ACTS[best] if best else "operator"


def _addr_tag(addr):
    """A short, stable tag for an address, so the history can say "new"
    without keeping the address itself on disk a second time."""
    return hashlib.sha256(addr.encode()).hexdigest()[:12]


def sweep_record(sweep):
    """The small per-night record kept beside the private report: the
    verdict keys and severities, tagged login addresses, and the edge
    refusal counts the next night compares against."""
    accepted = [a for a in (sweep.get("auth", {}).get("accepted_from") or "").split(",") if a]
    return {
        "generated_utc": sweep.get("generated_utc"),
        "verdicts": {v["key"]: v.get("severity") for v in sweep.get("verdicts", [])},
        "accepted_tags": sorted({_addr_tag(a) for a in accepted}),
        "by_status": sweep.get("refusals", {}).get("by_status") or {},
    }


def save_sweep_record(security_dir, date, sweep):
    path = security_dir / f"security-{date}.record.json"
    path.write_text(json.dumps(sweep_record(sweep), indent=1), encoding="utf-8")
    return path


def load_history(security_dir, date, nights=None):
    """Earlier nights' records, newest first, strictly before `date`. A
    missing or unreadable record ends nothing: it is skipped, and the
    'open N nights' count treats the gap as a break (see triage)."""
    nights = nights or config.SECURITY_HISTORY_NIGHTS
    out = []
    for path in sorted(security_dir.glob("security-*.record.json"), reverse=True):
        day = path.name[len("security-"):-len(".record.json")]
        if day >= date:
            continue
        try:
            out.append((day, json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, ValueError):
            continue
        if len(out) >= nights:
            break
    return out


#: Nights of records needed before a login address can read as new.
_LOGIN_NOVELTY_MIN_NIGHTS = 7


def _previous_day(date):
    return (dt.date.fromisoformat(date) - dt.timedelta(days=1)).isoformat()


def triage(date, sweep, history):
    """Sort tonight's verdicts by what a human must do with them.

    - act: critical, or high and new tonight;
    - standing: high or medium, open on consecutive earlier nights too;
    - watch: medium and new tonight;
    - recorded: low;
    - cleared: present in the previous night's record, absent tonight.

    The sweep's design asked for this from the start: "a number that has
    been true for three weeks reads differently from one that became true
    last night". Until 2026-10-07 every night listed the same high
    verdicts as if each were news. The verdicts themselves are the
    sweep's; nothing here changes a severity."""
    by_day = dict(history)
    out = {"act": [], "standing": [], "watch": [], "recorded": [], "cleared": [],
           "new_login_addresses": 0, "history_nights": len(history)}
    for v in sorted(sweep.get("verdicts", []),
                    key=lambda x: _SEVERITY_ORDER.get(x.get("severity"), 4)):
        nights, day = 1, _previous_day(date)
        while v["key"] in (by_day.get(day) or {}).get("verdicts", {}):
            nights += 1
            day = _previous_day(day)
        item = {"key": v["key"], "severity": v.get("severity"), "detail": v.get("detail", ""),
                "nights": nights, "who": _who_acts(v["key"])}
        sev = v.get("severity")
        if sev == "critical" or (sev == "high" and nights == 1):
            out["act"].append(item)
        elif sev == "low":
            out["recorded"].append(item)
        elif nights > 1:
            out["standing"].append(item)
        else:
            out["watch"].append(item)
    tonight = {v["key"] for v in sweep.get("verdicts", [])}
    prev = by_day.get(_previous_day(date))
    if prev:
        out["cleared"] = sorted(set(prev.get("verdicts", {})) - tonight)
    # An operator may log in from several addresses a day, so "new"
    # means something only against some weeks of records: below the
    # minimum it would fire every night.
    seen = {t for _, rec in history for t in rec.get("accepted_tags", [])}
    if len(history) >= _LOGIN_NOVELTY_MIN_NIGHTS:
        out["new_login_addresses"] = len(set(sweep_record(sweep)["accepted_tags"]) - seen)
    return out


def render_action_today(t, problem=None):
    """The block a morning reader reads first, and often only."""
    L = ["", "## Action today", ""]
    if problem:
        return L + [f"**Act: the security sweep did not run or cannot be trusted ({problem}).**",
                    "Nothing below describes last night.", ""]
    if t["act"]:
        L += ["**Act:**", "", "| severity | finding | who acts | detail |", "|---|---|---|---|"]
        L += [f"| {i['severity']} | `{i['key']}` | {i['who']} | {i['detail']} |" for i in t["act"]]
    else:
        L += ["**Nothing new needs action.**"]
    if t["new_login_addresses"]:
        L += ["", (f"**Watch:** SSH logins were accepted from {t['new_login_addresses']}"
                   f" address(es) not seen in the previous {t['history_nights']} night(s)"
                   " of records. Confirm they were yours.")]
    if t["watch"]:
        L += ["", "**Watch** (new tonight, lower severity):", ""]
        L += [f"- `{i['key']}` ({i['severity']}; {i['who']}): {i['detail']}" for i in t["watch"]]
    if t["standing"]:
        L += ["", "**Standing** (known; open on earlier nights too):", "",
              "| finding | severity | nights open | who acts | detail |", "|---|---|---|---|---|"]
        L += [f"| `{i['key']}` | {i['severity']} | {i['nights']} | {i['who']} | {i['detail']} |"
              for i in t["standing"]]
    if t["recorded"]:
        L += ["", "Recorded, nothing to do: "
              + "; ".join(f"`{i['key']}` ({i['detail']})" for i in t["recorded"]) + "."]
    if t["cleared"]:
        L += ["", "Cleared since the previous night: "
              + ", ".join(f"`{k}`" for k in t["cleared"]) + "."]
    if not t["history_nights"]:
        L += ["", "*No earlier records yet: every verdict reads as new tonight.*"]
    return L + [""]


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


def _finding_kinds(findings):
    """'2 (by-agent 1, by-target 1)'. One campaign is often seen twice,
    by its target paths and by its client; a bare total read as two
    campaigns beside a verdict that counted one (2026-10-06)."""
    if not findings:
        return "0"
    kinds = {}
    for f in findings:
        kinds[f.get("kind", "?")] = kinds.get(f.get("kind", "?"), 0) + 1
    return (f"{len(findings)} ("
            + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())) + ")")


#: Edge statuses worth a named line: refusals (400, 403, 404, 405, 444)
#: and the ones that show limits working (408 timeouts, 413 bodies too
#: large, 429 rate limits).
_NAMED_STATUSES = ("400", "403", "404", "405", "408", "413", "429", "444")


def _host_rows(sweep):
    """Rows for fields the sweep gained on 2026-10-07. A sweep from
    before that date has none of them and renders as it always did."""
    L = []
    host, edge, auth = sweep.get("host"), sweep.get("edge_errors"), sweep.get("auth", {})
    integ = sweep.get("integrity", {})
    if host:
        L += [f"| root filesystem used | {host.get('disk_pct', '?')}% |",
              ("| reboot required | "
               + (f"yes, {host.get('reboot_age_hours', 0)}h ({host.get('reboot_pkgs', '')})"
                  if host.get("reboot_required") else "no") + " |")]
    if "accepted_users" in auth:
        L += [f"| SSH accounts that logged in | {auth.get('accepted_users') or 'none'} |",
              f"| SSH password logins | {auth.get('password_logins', 0)} |"]
    if "fingerprints" in integ:
        changes = integ.get("fingerprint_changes") or []
        L += [(f"| watched files (accounts, keys, sudo, sshd, schedules) | "
               f"{len(integ['fingerprints'])}, "
               + ("baseline recorded" if integ.get("fingerprint_baseline")
                  else (f"{len(changes)} changed" if changes else "unchanged")) + " |")]
    if edge:
        levels = edge.get("by_level") or {}
        spill = edge.get("buffered_to_temp_file") or {}
        L += [("| edge error log, severe lines (crit/alert/emerg) | "
               f"{sum(levels.get(k, 0) for k in ('crit', 'alert', 'emerg'))} |"),
              ("| edge buffered to a temporary file (response / request body) | "
               f"{spill.get('upstream_response', 0)} / {spill.get('client_body', 0)} |")]
    by_status = sweep.get("refusals", {}).get("by_status") or {}
    named = [f"{c}: {by_status[c]}" for c in _NAMED_STATUSES if by_status.get(c)]
    if named:
        L += [f"| edge refusals by status | {', '.join(named)} |"]
    return L


def _jail_table(jails):
    """Each jail, and whether a firewall rule uses its chain. A jail with
    no bans may have no chain yet: most actions create it at the first
    ban. A jail WITH bans and a missing chain is the finding the sweep's
    jail.chainless verdict reports."""
    if not jails:
        return []
    L = ["", "| jail | banned now | banned since start | firewall chain |", "|---|---|---|---|"]
    for j in jails:
        if j.get("has_chain"):
            chain = j.get("chains") or "yes"
        elif not j.get("total_banned"):
            chain = "none yet (no bans)"
        else:
            chain = f"**missing: {j.get('missing_chains') or 'f2b-' + j.get('jail', '?')}**"
        L.append(f"| {j.get('jail')} | {j.get('currently_banned', 0)} |"
                 f" {j.get('total_banned', 0)} | {chain} |")
    return L


def render_security(sweep, problem=None, summary=None, withheld=None):
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
          f"| correlated campaign findings | {_finding_kinds(probing.get('findings', []))} |",
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

    L += _host_rows(sweep)

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

    L += _jail_table(sweep.get("jails") or [])

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
    elif withheld:
        L += ["", (f"*Model summary withheld: it named {withheld}, which the sweep does not"
                   " contain. The mechanical findings above are complete.*")]
    else:
        L += ["", "*(no inference available; the mechanical findings above are complete)*"]
    return L


def render_security_report(date, sweep, problem=None, summary=None, *,
                           triaged=None, withheld=None):
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
    if triaged is not None or problem:
        L += render_action_today(triaged or {}, problem)
    L += render_security(sweep, problem, summary, withheld)
    L += ["", f"*Generated {utc_now_iso()}.*", ""]
    return "\n".join(L)


def _trim_for_model(sweep):
    """Address lists, path samples and file hashes are evidence for a
    human reading the JSON, not context a summariser needs; they are
    also the only unbounded fields in the file."""
    trimmed = json.loads(json.dumps(sweep))
    for f in trimmed.get("probing", {}).get("findings", []):
        f.pop("sample_paths", None)
        if isinstance(f.get("ips"), list):
            f["ips"] = f["ips"][:5]
    trimmed.get("auth", {}).pop("accepted_from", None)
    for k in ("fingerprints", "images"):
        trimmed.get("integrity", {}).pop(k, None)
    return trimmed


def summarize_security(llm, sweep, triaged=None):
    """One cheap-tier call over the already-classified sweep. Returns a
    string, or None if the call fails — the section never depends on it.
    The caller passes the reply through ungrounded() before using it."""
    result = llm.complete(
        _SECURITY_PROMPT.format(triage=json.dumps(triaged or {}, indent=1),
                                sweep=json.dumps(_trim_for_model(sweep), indent=1)),
        purpose="security:summary", model=config.MAP_MODEL,
        package_id=f"SEC-{sweep.get('generated_utc', '')[:10]}")
    return (result["text"] or "").strip() or None


#: Words a summary may capitalize although the sweep never spells them:
#: protocol names, and the function words that open ordinary sentences.
#: Every other capitalized word, sentence-initial or not, must occur in
#: the data. (Skipping sentence-initial words let an invented provider
#: name through after a colon; the case is pinned in the tests.)
_GROUNDED_WORDS = {
    "ssh", "tls", "vps", "mcp", "http", "https", "ip", "utc", "dns", "api", "json",
    "fail2ban", "the", "a", "an", "no", "nothing", "none", "one", "two", "three", "four", "five",
    "it", "its", "this", "these", "that", "there", "all", "both", "every", "each",
    "and", "but", "or", "so", "if", "while", "since", "after", "before", "today",
    "tonight", "yesterday", "last", "new", "also", "only", "still", "otherwise",
    "however", "overall", "in", "on", "of", "for", "from", "with", "at", "by",
    "is", "are", "was", "were", "has", "have", "act", "action", "watch",
}


def _numbers(text):
    return re.findall(r"\d+(?:\.\d+)?", text)


def unsourced_numbers(text, *sources):
    """Numerals in `text` that appear nowhere in `sources` (as JSON)."""
    have = set(_numbers(" ".join(json.dumps(src) for src in sources)))
    out = []
    for n in _numbers(text):
        if n not in have and n not in out:
            out.append(n)
    return out


def ungrounded(summary, *sources):
    """What the summary names that its input does not: numerals and
    capitalized words absent from the JSON it was given, compared case-
    insensitively. Returns a comma-joined string, or '' when grounded.

    Written after v1 attributed a scan to a hosting provider it invented
    (2026-10-06): no provider appears anywhere in the sweep. A prompt rule
    asks the model not to; this check is the second, independent layer,
    in the same spirit as the lexicon gate behind the plain-speak prompt.
    A withheld summary costs nothing: the mechanical report is complete."""
    corpus = " ".join(json.dumps(src) for src in sources).lower()
    bad = unsourced_numbers(summary, *sources)
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9]*(?:[-'][A-Za-z0-9]+)*", summary):
        word = m.group(0)
        if not word[0].isupper() or word in bad:
            continue
        parts = [p for p in re.split(r"[-']", word.lower()) if p]
        if not all(p in _GROUNDED_WORDS or p in corpus for p in parts):
            bad.append(word)
    return ", ".join(bad)


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
    security_dir = security_dir or config.INSIGHT_SECURITY_DIR
    security_dir.mkdir(parents=True, exist_ok=True)
    triaged = (triage(date, sweep, load_history(security_dir, date))
               if sweep is not None else None)
    security = {"sweep": sweep, "problem": problem, "summary": None, "withheld": None}
    if sweep is not None and llm is not None:
        try:
            summary = summarize_security(llm, sweep, triaged)
        except LLMError as exc:
            summary = None
            logger.warning(
                "insight: security summary call failed (%s) — the mechanical"
                " findings are unaffected", exc)
        if summary:
            bad = ungrounded(summary, _trim_for_model(sweep), triaged)
            if bad:
                logger.warning("insight: security summary withheld; ungrounded: %s", bad)
                security["withheld"] = bad
            else:
                security["summary"] = summary

    out_dir = out_dir or (config.PROJECT_ROOT / "provenance" / "runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"insight-{date}.md"
    # A suggestion citing a figure the metrics do not hold is withheld,
    # not published: on 2026-10-06 one compared the day with "the
    # established 18.1% baseline", a number in no metric (it reached the
    # model through the CLI's project context, since removed).
    withheld = 0
    if suggestions:
        kept = [x for x in suggestions if not unsourced_numbers(x, metrics)]
        withheld = len(suggestions) - len(kept)
        if withheld:
            logger.warning("insight: %d suggestion(s) withheld for unsourced figures",
                           withheld)
        suggestions = kept
    path.write_text(render_report(metrics, suggestions, withheld), encoding="utf-8")

    # The security sweep is PRIVATE (CLAUDE.md §13, operator ruling
    # 2026-09-29): written to a gitignored, host-durable directory the
    # evidence commit never stages — never into the public report above.
    sec_path = security_dir / f"security-{date}.md"
    sec_path.write_text(
        render_security_report(date, sweep, problem, security["summary"],
                               triaged=triaged, withheld=security["withheld"]),
        encoding="utf-8")
    if sweep is not None:
        save_sweep_record(security_dir, date, sweep)

    logger.info("insight report written: %s (%d suggestion(s)); security"
                " (private): %s (%s)", path, len(suggestions or []), sec_path,
                problem or f"{len(sweep.get('verdicts', []))} verdict(s)")
    return path

"""Run the full daily pipeline with live narration and a detail report.

Usage: uv run python scripts/run_pipeline.py [--date YYYY-MM-DD]

Stages: sync -> agencies -> email -> extract -> analyze/plain/compose ->
render -> site. Each stage is a module-level function returning its stats
so the wiring is testable (tests/test_scripts.py) and a scheduler (the
VPS cron, docs/vps-runtime-plan.md) exercises exactly the code an
operator run does. Verbose logging is forced on so every HTTP request
and LLM call prints as it happens (the same narrative lands in
data/logs/access-*.log). After the site stage the developer-insight
report (fapd.insight) writes provenance/runs/insight-<date>.md — the
daily feedback loop; its failure never fails the run. Ends with a
detail report: requests by client, tokens by purpose, digest stats,
and validation outcome.
"""

import argparse
import sqlite3
import sys
import time

from digest import default_date  # scripts/ sibling; newest COMPLETE day

from fapd import (
    agencies,
    analyze,
    assess,
    compose,
    config,
    db,
    email_sources,
    extract,
    health,
    insight,
    llm,
    logging_setup,
    report,
    tags,
)
from fapd.client import BudgetExceededError, GovinfoClient
from fapd.publish import build_day, build_site
from fapd.sources import load_registry
from fapd.sync import sync_collection


def banner(title):
    print(f"\n{'=' * 68}\n== {title}\n{'=' * 68}", flush=True)


def stage(title):
    banner(title)
    return time.monotonic()


def done(t0):
    print(f"-- stage complete in {time.monotonic() - t0:.0f}s", flush=True)


def stage_sync(conn):
    """govinfo delta sync for every collection. Returns the request count.

    Runs reserve_exempt: this is the finalizer, and the reserve exists for
    exactly this call. A budget shortfall here is reported and the run
    continues — the day's items were collected hours ago, sync is a
    top-up, and refusing to publish a collected day because a top-up
    could not run is the wrong failure (2026-07-30: it cost a day)."""
    with GovinfoClient(reserve_exempt=True) as client:
        for collection in config.COLLECTIONS:
            try:
                stats = sync_collection(client, conn, collection, max_downloads=100)
            except BudgetExceededError as exc:
                print(f"   {collection:9} SKIPPED — {exc}", flush=True)
                continue
            print(f"   {collection:9} listed={stats['listed']:5} "
                  f"downloaded={stats['downloaded']:4} failed={stats['failed']:3} "
                  f"pending_remaining={stats['pending_remaining']:5}", flush=True)
        return client.requests_today()


def stage_agencies():
    """RSS poll of active agency newsrooms, per-host concurrent (GUIDE §4):
    every host still sees at most 1 req/s and its own crawl-delay, but no
    host waits behind another's pacing clock — gao.gov asks for 420s
    between requests, and serial polling made every other agency wait."""
    entries = [e for e in load_registry()
               if e["status"] == "active"
               and e["type"] in agencies.INGESTIBLE_TYPES]
    groups = agencies.host_groups(entries)
    print(f"   {len(entries)} source(s) across {len(groups)} host(s)", flush=True)
    results = agencies.run_concurrent(entries)
    stats = {"sources": len(entries), "hosts": len(groups),
             "new_items": sum(r["new_items"] for r in results),
             "wayback": sum(r["wayback_submitted"] for r in results)}
    print(f"   {stats['new_items']} new item(s), {stats['wayback']} wayback",
          flush=True)
    return stats


def stage_email(conn, *, entries=None, mailbox_factory=None, poll=None):
    """Poll the project mailbox for registered senders. Three contracts,
    all pinned by tests: an unconfigured mailbox is a reported skip; a
    poll returns aggregated counts; a mailbox outage is reported and the
    run continues — the gap is disclosed, never hidden."""
    if not (config.IMAP_HOST and config.IMAP_USER and config.IMAP_PASSWORD):
        print("   mailbox not configured (.env) — skipped", flush=True)
        return {"configured": False, "subscriptions": 0, "bulletins": 0,
                "items": 0, "administrative": 0, "error": None}
    if entries is None:
        entries = [e for e in load_registry()
                   if e["type"] == "email"
                   and e["status"] in ("active", "planned")
                   and e.get("sender")]
    mailbox_factory = mailbox_factory or email_sources.MailboxClient
    poll = poll or email_sources.poll_mailbox
    stats = {"configured": True, "subscriptions": len(entries), "bulletins": 0,
             "items": 0, "administrative": 0, "error": None}
    try:
        with mailbox_factory() as mbox:
            results = poll(mbox, conn, entries)
        stats["bulletins"] = sum(r["messages"] for r in results)
        stats["items"] = sum(r["items"] for r in results)
        stats["administrative"] = sum(r["administrative"] for r in results)
        print(f"   {stats['subscriptions']} subscription(s), "
              f"{stats['bulletins']} bulletin(s), {stats['items']} new item(s), "
              f"{stats['administrative']} administrivia skipped", flush=True)
    except Exception as exc:  # noqa: BLE001 — a mailbox outage must not
        # cost the rest of the run; the gap is reported, not hidden.
        stats["error"] = repr(exc)
        print(f"   mailbox poll failed: {exc!r} — continuing", flush=True)
    return stats


def stage_extract(conn):
    ex = extract.run(conn)
    print(f"   packages={ex['packages']} records={ex['records']} "
          f"chars={ex['chars']:,} failed={ex['failed']} "
          f"graphics={ex['assets_extracted']}", flush=True)
    return ex


def stage_analyze(conn, date):
    """Map + plain-speak + compose. Returns the layer stats plus the
    ledger's before/after token totals for the detail report."""
    with llm.LLMClient() as lclient:
        before = lclient.tokens_today()
        a = analyze.run(conn, lclient, date)
        print(f"   map: selected={a['selected']} official={a['official']} "
              f"llm={a['llm_summarized']} calls={a['llm_calls']} "
              f"failed={len(a['failed_items'])}", flush=True)
        p = analyze.run_plain(conn, lclient, date)
        print(f"   plain: {p['plain_written']}/{p['plain_pending']} written "
              f"({len(p['failed_items'])} failed)", flush=True)
        c = compose.compose_day(conn, lclient, date)
        s = compose.compose_sections(conn, lclient, date)
        t = tags.run(conn, lclient, date)
        print(f"   sections: {s['composed']} synopsis(es) "
              f"(skipped={s['skipped_existing']}); tags: {t['mechanical']} "
              f"mechanical + {t['llm']} discovery", flush=True)
        print(f"   compose: composed={c['composed']} "
              f"skipped_existing={c['skipped_existing']}", flush=True)
        after = lclient.tokens_today()
    return {"map": a, "plain": p, "compose": c, "sections": s,
            "before": before, "after": after}


def stage_render(conn, date):
    """Render + validate. Returns (out_path | None, validation string)."""
    try:
        out_path = report.render(conn, date)
        print(f"   digest written: {out_path}", flush=True)
        return out_path, "PASSED"
    except report.ValidationError as exc:
        print(f"   VALIDATION FAILED — nothing written: {exc}", flush=True)
        return None, f"FAILED: {exc}"


def stage_site():
    site = build_site()
    print(f"   {site['pages']} page(s) + index + sources, "
          f"{site['assets']} asset(s) -> {site['out_dir']}", flush=True)
    return site


def stage_day_view(conn, date):
    """Frozen day view (GUIDE §5 third artifact): the /today machinery
    rendered once more for the closed day, committed with the evidence.
    Failure never costs the finished digest — a missing day view is a
    visible gap at its URL, not a lost record."""
    try:
        day = build_day(conn, date)
        print(f"   day view: {day.get('items', 0)} item(s) -> "
              f"site/day/{date}.html + .json", flush=True)
    except Exception as exc:  # noqa: BLE001 — see docstring
        print(f"   day view failed: {exc!r} — continuing", flush=True)


def stage_source_text(conn, *, llm_client=None):
    """Source-page model text (GUIDE §3a source surfaces): descriptions
    for every registry entry (regenerated only when an entry changes),
    assessments for measured sources (initial / 30-day / health-change
    triggers). Runs BEFORE the site stage so this run's pages carry the
    fresh text. Failure never fails the run — a missing block is a
    visible gap on a source page, not a lost digest — and the throttle's
    budget-pause lands here too: the next EOD simply tries again."""
    try:
        entries = load_registry(config.PROJECT_ROOT / "sources" / "registry.yaml")
        payload = health.source_health(entries)
        stats = payload.get("sources") or {}
        labels = {sid: rec.get("health") for sid, rec in stats.items()}
        # The health-change trigger compares this run's labels against
        # the labels the layer saw at its LAST run — but the collector
        # refreshes source_health_state every 15 minutes, so "previous"
        # cannot be read from it at EOD. What IS durable: a transition
        # stamped after the newest stored assessment (state.since >
        # generated_at) is one the layer has not seen. Pass a sentinel
        # prev no real label equals, so the trigger fires exactly for
        # those; labels drive triggers only and never reach prose.
        prev = dict(labels)
        for sid, st in health.health_state(conn).items():
            newest = assess.latest_assessment(conn, sid)
            if newest and st.get("since") and st["since"] > newest["generated_at"]:
                prev[sid] = "(changed-since-last-assessment)"
        measured = [e for e in entries if stats.get(e["id"], {}).get("measured")]
        d = assess.refresh_descriptions(conn, llm_client, entries)
        a = assess.refresh_assessments(conn, llm_client, measured, stats,
                                       labels, prev)
        print(f"   descriptions: +{d['generated']} (skip {d['skipped']},"
              f" reject {d['rejected']}, fail {d['failed']}) · assessments:"
              f" +{a['generated']} (skip {a['skipped']}, reject"
              f" {a['rejected']}, fail {a['failed']})", flush=True)
    except Exception as exc:  # noqa: BLE001 — see docstring
        print(f"   source text failed: {exc!r} — continuing", flush=True)


def stage_insight(conn, date, *, llm_client=None):
    """Post-EOD developer-insight report (GUIDE §3a dev-facing surface).
    An insight failure never fails the run: the digest is already
    rendered and validated by this point, and the feedback loop is for
    the developer, not the reader."""
    try:
        path = insight.run(conn, llm_client, date)
        print(f"   insight report: {path}", flush=True)
        return path
    except Exception as exc:  # noqa: BLE001 — ops reporting must not
        # cost a finished run; the gap itself shows up in tomorrow's report.
        print(f"   insight report failed: {exc!r} — continuing", flush=True)
        return None


def detail_report(*, gov_requests, before, after, timings, validation,
                  out_path, site):
    banner("DETAIL REPORT")
    day = time.strftime("%Y-%m-%d", time.gmtime())
    fdb = sqlite3.connect(f"file:{config.FETCH_LOG_DB}?mode=ro", uri=True)
    print("HTTP requests today (UTC), by client:")
    for client_name, n, errs in fdb.execute(
        "SELECT COALESCE(client,'govinfo'), COUNT(*),"
        " SUM(CASE WHEN status IS NULL OR status >= 400 THEN 1 ELSE 0 END)"
        " FROM fetch_log WHERE ts_utc >= ? GROUP BY 1", (day,)
    ):
        print(f"   {client_name:9} {n:5} requests ({errs} error/blocked)")
    fdb.close()

    ldb = sqlite3.connect(f"file:{config.LLM_LEDGER_DB}?mode=ro", uri=True)
    print("LLM calls today (UTC), by purpose:")
    for purpose, n, tin, tout in ldb.execute(
        "SELECT substr(purpose, 1, instr(purpose||':', ':')-1), COUNT(*),"
        " SUM(input_tokens), SUM(output_tokens)"
        " FROM llm_calls WHERE ts_utc >= ? GROUP BY 1", (day,)
    ):
        print(f"   {purpose:10} {n:3} call(s)  {tin or 0:>9,} in / {tout or 0:>7,} out")
    ldb.close()
    run_in = after[0] - before[0]
    run_out = after[1] - before[1]
    print(f"This run: {run_in:,} in / {run_out:,} out tokens; "
          f"govinfo requests {gov_requests}")

    print("Stage timings: " + "  ".join(
        f"{k}={v:.0f}s" for k, v in timings.items()))
    print(f"Validation: {validation}")
    if out_path:
        print(f"\nDigest: {out_path}\nSite:   {site['out_dir']}/index.html")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="digest date (default: newest complete day)")
    args = ap.parse_args(argv)
    logging_setup.setup(verbose=True)
    timings = {}

    conn = db.connect()

    t0 = stage("STAGE 1/5 — SYNC (govinfo delta: CREC, BILLS, FR, USCOURTS)")
    gov_requests = stage_sync(conn)
    timings["sync"] = time.monotonic() - t0
    done(t0)

    t0 = stage("STAGE 1b/5 — AGENCY NEWSROOMS (RSS poll + capture + Wayback)")
    stage_agencies()
    timings["agencies"] = time.monotonic() - t0
    done(t0)

    t0 = stage("STAGE 1c/5 — EMAIL BULLETINS (project mailbox, registered senders)")
    stage_email(conn)
    timings["email"] = time.monotonic() - t0
    done(t0)

    t0 = stage("STAGE 2/5 — EXTRACT (raw archive -> normalized records)")
    stage_extract(conn)
    timings["extract"] = time.monotonic() - t0
    done(t0)

    date = args.date or default_date(conn)
    print(f"\n   digest date: {date}", flush=True)

    t0 = stage(f"STAGE 3/5 — ANALYZE (map + plain-speak + compose) for {date}")
    analysis = stage_analyze(conn, date)
    timings["analyze"] = time.monotonic() - t0
    done(t0)

    t0 = stage(f"STAGE 4/5 — RENDER + VALIDATE digest for {date}")
    out_path, validation = stage_render(conn, date)
    timings["render"] = time.monotonic() - t0
    done(t0)

    t0 = stage(f"STAGE 4b — FROZEN DAY VIEW for {date}")
    stage_day_view(conn, date)
    timings["day_view"] = time.monotonic() - t0
    done(t0)

    t0 = stage("STAGE 4c — SOURCE-PAGE TEXT (descriptions + assessments)")
    with llm.LLMClient() as lclient:
        stage_source_text(conn, llm_client=lclient)
    timings["source_text"] = time.monotonic() - t0
    done(t0)

    t0 = stage("STAGE 5/5 — SITE (canonical markdown -> styled HTML)")
    site = stage_site()
    timings["site"] = time.monotonic() - t0
    done(t0)

    t0 = stage(f"POST — OPERATIONS REPORT (developer feedback loop) for {date}")
    with llm.LLMClient() as lclient:
        stage_insight(conn, date, llm_client=lclient)
    timings["insight"] = time.monotonic() - t0
    done(t0)

    detail_report(gov_requests=gov_requests, before=analysis["before"],
                  after=analysis["after"], timings=timings,
                  validation=validation, out_path=out_path, site=site)
    conn.close()
    return 0 if out_path else 1


if __name__ == "__main__":
    sys.exit(main())

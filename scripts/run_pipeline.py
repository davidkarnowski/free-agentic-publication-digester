"""Run the full daily pipeline with live narration and a detail report.

Usage: uv run python scripts/run_pipeline.py [--date YYYY-MM-DD]

Stages: sync -> extract -> analyze/plain/compose -> render -> site.
Verbose logging is forced on so every HTTP request and LLM call prints as
it happens (the same narrative lands in data/logs/access-*.log). Ends
with a detail report: requests by client, tokens by purpose, digest
stats, and validation outcome.
"""

import argparse
import sqlite3
import sys
import time

from info_intel import analyze, compose, config, db, llm, logging_setup, report
from info_intel.client import GovinfoClient
from info_intel.publish import build_site
from info_intel.sync import sync_collection


def banner(title):
    print(f"\n{'=' * 68}\n== {title}\n{'=' * 68}", flush=True)


def stage(title):
    banner(title)
    return time.monotonic()


def done(t0):
    print(f"-- stage complete in {time.monotonic() - t0:.0f}s", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="digest date (default: newest complete day)")
    args = ap.parse_args()
    logging_setup.setup(verbose=True)
    timings = {}

    conn = db.connect()

    t0 = stage("STAGE 1/5 — SYNC (govinfo delta: CREC, BILLS, FR, USCOURTS)")
    with GovinfoClient() as client:
        for collection in config.COLLECTIONS:
            stats = sync_collection(client, conn, collection, max_downloads=100)
            print(f"   {collection:9} listed={stats['listed']:5} "
                  f"downloaded={stats['downloaded']:4} failed={stats['failed']:3} "
                  f"pending_remaining={stats['pending_remaining']:5}", flush=True)
        gov_requests = client.requests_today()
    timings["sync"] = time.monotonic() - t0
    done(t0)

    t0 = stage("STAGE 2/5 — EXTRACT (raw archive -> normalized records)")
    from info_intel import extract

    ex = extract.run(conn)
    print(f"   packages={ex['packages']} records={ex['records']} "
          f"chars={ex['chars']:,} failed={ex['failed']} "
          f"graphics={ex['assets_extracted']}", flush=True)
    timings["extract"] = time.monotonic() - t0
    done(t0)

    from digest import default_date  # scripts/ sibling; newest COMPLETE day

    date = args.date or default_date(conn)
    print(f"\n   digest date: {date}", flush=True)

    t0 = stage(f"STAGE 3/5 — ANALYZE (map + plain-speak + compose) for {date}")
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
        print(f"   sections: {s['composed']} synopsis(es) "
              f"(skipped={s['skipped_existing']})", flush=True)
        print(f"   compose: composed={c['composed']} "
              f"skipped_existing={c['skipped_existing']}", flush=True)
        after = lclient.tokens_today()
    timings["analyze"] = time.monotonic() - t0
    done(t0)

    t0 = stage(f"STAGE 4/5 — RENDER + VALIDATE digest for {date}")
    try:
        out_path = report.render(conn, date)
        print(f"   digest written: {out_path}", flush=True)
        validation = "PASSED"
    except report.ValidationError as exc:
        print(f"   VALIDATION FAILED — nothing written: {exc}", flush=True)
        validation = f"FAILED: {exc}"
        out_path = None
    timings["render"] = time.monotonic() - t0
    done(t0)

    t0 = stage("STAGE 5/5 — SITE (canonical markdown -> styled HTML)")
    site = build_site()
    print(f"   {site['pages']} page(s) + index + sources, "
          f"{site['assets']} asset(s) -> {site['out_dir']}", flush=True)
    timings["site"] = time.monotonic() - t0
    done(t0)

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
    conn.close()
    return 0 if out_path else 1


if __name__ == "__main__":
    sys.exit(main())

"""Poll active agency newsroom sources (S2 pilot): conditional feed GETs,
article captures with provenance + Wayback corroboration, items into the
AGENCYPR collection. Zero LLM calls.

Host groups are polled in parallel (GUIDE §4 concurrency-across-hosts
rule): each host still sees at most 1 request/second and its crawl-delay,
but no host waits behind another host's pacing clock.

Usage: uv run python scripts/ingest_agencies.py [--verbose] [--serial]
"""

import argparse
import datetime as dt
import sqlite3
import sys

from fapd import agencies, config, db, logging_setup
from fapd.client import AgencyClient


def _footprint_today():
    conn = sqlite3.connect(config.FETCH_LOG_DB)
    day = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT00:00:00")
    rows = conn.execute(
        "SELECT COALESCE(client, 'govinfo'), COUNT(*) FROM fetch_log"
        " WHERE ts_utc >= ? GROUP BY 1 ORDER BY 1",
        (day,),
    ).fetchall()
    conn.close()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--serial", action="store_true",
                    help="poll sources one at a time (old behavior)")
    ap.add_argument("--ids", help="comma-separated source ids (targeted re-poll)")
    args = ap.parse_args()
    logging_setup.setup(verbose=args.verbose)

    from fapd.sources import load_registry
    entries = [e for e in load_registry()
               if e["status"] == "active" and e["type"] in agencies.INGESTIBLE_TYPES]
    if args.ids:
        wanted = set(args.ids.split(","))
        entries = [e for e in entries if e["id"] in wanted]

    if args.serial:
        conn = db.connect()
        with AgencyClient() as client, agencies.WaybackClient() as wayback:
            results = agencies.run(client, wayback, conn, entries)
        conn.close()
    else:
        groups = agencies.host_groups(entries)
        print(f"polling {len(entries)} sources across {len(groups)} hosts"
              f" ({len(groups)} concurrent workers, per-host pacing)")
        results = agencies.run_concurrent(entries)

    total_new = sum(r["new_items"] for r in results)
    for r in sorted(results, key=lambda r: r["id"]):
        print(f"  {r['id']:22} {r['feed_status'] or '?':16} "
              f"new={r['new_items']:3} articles={r['articles_fetched']:3} "
              f"wayback={r['wayback_submitted']:3} errors={r['errors']}")
    print(f"total new items: {total_new}")
    for client_name, n in _footprint_today():
        print(f"  requests today ({client_name}): {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

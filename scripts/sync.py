"""Run a delta sync for the configured collections.

Usage:
  uv run python scripts/sync.py [--collections CREC,BILLS,FR]
                                [--list-only] [--max-downloads N]

--list-only updates the inventory and watermarks without downloading content
(useful to see what a download run would do). --max-downloads caps content
downloads per collection for this run; the remainder stays queued as
'pending' and is picked up next run (docs/schema.md step 5).
"""

import argparse
import sys

from fapd import config, db, logging_setup
from fapd.client import GovinfoClient
from fapd.sync import sync_collection


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collections", default=",".join(config.COLLECTIONS))
    ap.add_argument("--list-only", action="store_true")
    ap.add_argument("--max-downloads", type=int, default=100)
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="show DEBUG (pacing, per-attempt) on console; file log always has it")
    args = ap.parse_args()
    logging_setup.setup(verbose=args.verbose)

    conn = db.connect()
    with GovinfoClient() as client:
        for collection in args.collections.split(","):
            collection = collection.strip().upper()
            stats = sync_collection(
                client,
                conn,
                collection,
                list_only=args.list_only,
                max_downloads=args.max_downloads,
            )
            print(
                f"{collection:6} listed={stats['listed']:4}"
                f" downloaded={stats['downloaded']:4} failed={stats['failed']:3}"
                f" pending_remaining={stats['pending_remaining']:4}"
            )
        print(f"\nRequests today (UTC): {client.requests_today()}"
              f" / {config.MAX_REQUESTS_PER_DAY}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Run the extraction layer over fetched raw packages.

Usage:
  uv run python scripts/extract.py [--collections CREC,BILLS,FR] [--verbose]

Idempotent: only packages with missing/stale extractions are processed
(re-fetched raw or a bumped EXTRACTOR_VERSION triggers re-extraction).
No network access — extraction reads only the local archive.
"""

import argparse
import sys

from fapd import config, db, extract, logging_setup


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collections", default=",".join(config.COLLECTIONS))
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    logging_setup.setup(verbose=args.verbose)

    conn = db.connect()
    wanted = {c.strip().upper() for c in args.collections.split(",")}
    results = extract.run(conn, collections=wanted)
    print(
        f"packages={results['packages']} records={results['records']}"
        f" chars={results['chars']:,} failed={results['failed']}"
        f" assets_extracted={results['assets_extracted']}"
        f" assets_failed={results['assets_failed']}"
    )
    conn.close()
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())

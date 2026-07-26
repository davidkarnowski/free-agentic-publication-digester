"""Probe registry sources end-to-end (robots → fetch → capture → parse →
sample article → text extraction). GUIDE §3: viability is checked, never
presumed, and never forced — blocked sources are recorded, not fought.

Usage:
  uv run python scripts/check_sources.py [--status planned] [--ids a,b,c]
                                         [--verbose]
"""

import argparse
import sys

from info_intel import db, logging_setup
from info_intel.client import AgencyClient
from info_intel.probe import run
from info_intel.sources import load_registry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", default="planned")
    ap.add_argument("--ids", help="comma-separated source ids (overrides --status)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    logging_setup.setup(verbose=args.verbose)

    entries = load_registry()
    if args.ids:
        wanted = {s.strip() for s in args.ids.split(",")}
        entries = [e for e in entries if e["id"] in wanted]
    else:
        entries = [e for e in entries
                   if e["status"] == args.status
                   and e["type"] in ("rss", "html-index", "aggregator")]

    conn = db.connect()
    with AgencyClient() as client:
        out_dir, summary = run(client, conn, entries)
        print(f"probed {len(summary)} source(s) -> {out_dir}")
        for verdict in sorted({s['verdict'] for s in summary}):
            ids = [s["id"] for s in summary if s["verdict"] == verdict]
            print(f"  {verdict:16} {len(ids):3}  {', '.join(ids[:8])}"
                  f"{' …' if len(ids) > 8 else ''}")
        print(f"agency requests today: {client.requests_today()}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

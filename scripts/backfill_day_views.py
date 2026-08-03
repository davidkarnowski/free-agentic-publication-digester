"""One-shot backfill: frozen day views for past dates (GUIDE §5).

Renders site/day/<date>.html + .json for every past date the item
journal covers, via the same publish.build_day the end-of-day finalizer
uses — never a parallel implementation. Backfilled pages disclose their
provenance honestly: they are reconstructed from the stored observation
journal on the day this script runs, not frozen contemporaneously at
that day's end (the ``reconstructed_on`` disclosure variant). Dates
before the journal existed render nothing here and stay a disclosed gap.

Deliberate one-shot (the project's pattern for one-time operations —
never startup magic): idempotent, skips dates whose page already exists
unless --force. Run once per environment; the EOD finalizer owns every
day from then on. Zero LLM calls, zero requests.
"""

from __future__ import annotations

import argparse
import sys

from fapd import config, db
from fapd.publish import build_day
from fapd.sync import publication_date

# The official record starts here (operator decision, 2026-08-03: the
# 07-23/24 development-era digests were retired for the same reason).
# Also excludes stray journal rows filed under old publisher-claimed
# dates during early development — a day view for 2024 would manufacture
# exactly the confusion the record-start line exists to prevent.
RECORD_START = "2026-07-27"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="re-render dates whose day view already exists")
    parser.add_argument("--since", default=RECORD_START,
                        help=f"earliest date to render (default {RECORD_START},"
                             " the official record start)")
    args = parser.parse_args(argv)

    conn = db.connect()
    today = publication_date()
    dates = [row[0] for row in conn.execute(
        "SELECT DISTINCT digest_date FROM item_journal ORDER BY digest_date")]
    rendered = skipped = 0
    for date in dates:
        if date < args.since:
            continue  # before the official record; disclosed gap by design
        if date >= today:
            continue  # the live day belongs to /today; tonight's EOD freezes it
        out = config.SITE_DIR / "day" / f"{date}.html"
        if out.exists() and not args.force:
            skipped += 1
            continue
        result = build_day(conn, date, reconstructed_on=today)
        rendered += 1
        print(f"day/{date}: {result.get('items', 0)} item(s)"
              f" (reconstructed {today})", flush=True)
    conn.close()
    print(f"backfill complete: {rendered} rendered, {skipped} already present",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""One-shot cutover backfill for `packages.digest_day` (GUIDE §3,
amended 2026-08-06: observation-day filing).

The cutover is DIGEST 2026-08-06 — not the moment this code deployed.
Two classes of NULL rows exist and they need different answers:

- Rows first observed BEFORE the cutover day keep cover-date filing
  (`date_issued`). That is the cutover encoded in data: every frozen
  digest re-renders identically (§5 reproducibility).
- Rows first observed ON the cutover day (or later) were inserted by
  pre-deploy code into a digest day that has NOT frozen yet, so they
  get the LIVE policy — observation day for observation-filed
  collections, `date_issued` for cover-filed ones. Without this,
  CREC-2026-08-05 (87 granules, observed 2026-08-06T14:24Z, hours
  before this deploy) would backfill to its cover date, land in the
  FROZEN 08-05 digest, and become a third orphaned Record issue on the
  night the fix shipped.

Idempotent: only NULL rows are touched; a second run updates zero.

Usage: uv run python scripts/migrate_digest_day.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from fapd import config, db
from fapd.sync import publication_date_of

CUTOVER = "2026-08-06"  # the first digest under observation-day filing


def main():
    conn = db.connect()
    try:
        rows = conn.execute(
            "SELECT package_id, collection, date_issued, first_seen_at"
            " FROM packages WHERE digest_day IS NULL"
        ).fetchall()
        pre = post = 0
        for r in rows:
            observed_day = (publication_date_of(r["first_seen_at"])
                            or (r["first_seen_at"] or "")[:10])
            policy = config.FILING_POLICY.get(
                r["collection"], config.FILING_DEFAULT)
            if observed_day >= CUTOVER and policy != "cover":
                day = observed_day          # live policy: observation
                post += 1
            else:
                day = r["date_issued"] or observed_day  # pre-cutover / cover
                pre += 1
            conn.execute(
                "UPDATE packages SET digest_day = ? WHERE package_id = ?",
                (day, r["package_id"]))
        conn.commit()
        remaining = conn.execute(
            "SELECT COUNT(*) FROM packages WHERE digest_day IS NULL"
        ).fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
        print(f"backfilled: {pre} pre-cutover (cover-date), "
              f"{post} cutover-day (live policy); "
              f"NULL remaining: {remaining} of {total}")
        if remaining:
            print("FAILURE: rows without digest_day remain")
            return 1
        print("SUCCESS")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

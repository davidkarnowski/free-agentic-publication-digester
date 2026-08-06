"""One-shot cutover backfill for `packages.digest_day` (GUIDE §3,
amended 2026-08-06: observation-day filing).

Rows first seen BEFORE the cutover keep cover-date filing — that is the
cutover itself, encoded in data, so every frozen digest re-renders
identically (§5 reproducibility). Rows inserted after the code change
already carry digest_day from their INSERT and are untouched (the WHERE
clause makes this idempotent: a second run updates zero rows).

Deliberate one-shot per docs/schema.md's rule that destructive or
backfilling changes never live in startup DDL. Safe to re-run.

Usage: uv run python scripts/migrate_digest_day.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from fapd import db


def main():
    conn = db.connect()
    try:
        cur = conn.execute(
            "UPDATE packages SET digest_day ="
            "  COALESCE(date_issued, substr(first_seen_at, 1, 10))"
            " WHERE digest_day IS NULL"
        )
        conn.commit()
        remaining = conn.execute(
            "SELECT COUNT(*) FROM packages WHERE digest_day IS NULL"
        ).fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
        print(f"backfilled: {cur.rowcount} row(s); "
              f"NULL digest_day remaining: {remaining} of {total}")
        if remaining:
            print("FAILURE: rows without digest_day remain")
            return 1
        print("SUCCESS")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

"""One-shot rebuild of `packages` to add the fetch-retry-ceiling columns
and widen its `fetch_status` CHECK constraint (GUIDE §4, amended
2026-08-10).

This project's `_ensure_columns` micro-migration pattern (db.py) is
additive-only — `ALTER TABLE ... ADD COLUMN` cannot widen a CHECK
constraint on an existing table. Adding `fetch_status = 'exhausted'`
therefore needs a real table rebuild: create `packages_new` with the
target shape, copy every row across (new columns default to unattempted:
`fetch_attempts = 0`, `last_attempt_at = NULL` — no history is
reconstructed from fetch_log.db; see WORKLOG for why that's the accepted
trade), verify the row count is unchanged, then swap the table in.

Idempotent: skipped entirely if `packages` already has `fetch_attempts`
(a second run is a no-op, not an error).

Usage: uv run python scripts/migrate_widen_fetch_status.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from fapd import db

_TARGET_COLUMNS = (
    "package_id", "collection", "date_issued", "last_modified", "title",
    "package_link", "download_url", "download_format", "raw_path",
    "fetch_status", "first_seen_at", "digest_day", "fetched_at",
    "fetched_last_modified", "last_error",
)

_REBUILD_SQL = """
CREATE TABLE packages_new (
    package_id            TEXT PRIMARY KEY,
    collection            TEXT NOT NULL,
    date_issued           TEXT,
    last_modified         TEXT NOT NULL,
    title                 TEXT,

    package_link          TEXT,
    download_url          TEXT,
    download_format       TEXT,

    raw_path              TEXT,

    fetch_status          TEXT NOT NULL DEFAULT 'pending'
                          CHECK (fetch_status IN ('pending', 'fetched', 'failed',
                                                   'skipped', 'exhausted')),
    first_seen_at         TEXT NOT NULL,
    digest_day            TEXT,
    fetched_at            TEXT,
    fetched_last_modified TEXT,
    last_error            TEXT,
    fetch_attempts        INTEGER NOT NULL DEFAULT 0,
    last_attempt_at       TEXT
);

INSERT INTO packages_new ({cols}, fetch_attempts, last_attempt_at)
SELECT {cols}, 0, NULL FROM packages;

DROP TABLE packages;
ALTER TABLE packages_new RENAME TO packages;

CREATE INDEX idx_packages_collection_lastmod
    ON packages (collection, last_modified);
CREATE INDEX idx_packages_date_issued
    ON packages (date_issued);
CREATE INDEX idx_packages_unfetched
    ON packages (fetch_status)
    WHERE fetch_status IN ('pending', 'failed');
""".format(cols=", ".join(_TARGET_COLUMNS))


def main():
    conn = db.connect()
    try:
        have = {r["name"] for r in conn.execute("PRAGMA table_info(packages)")}
        if "fetch_attempts" in have:
            print("SUCCESS: already migrated (fetch_attempts present) — no-op")
            return 0

        before = conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]

        conn.execute("PRAGMA foreign_keys=OFF")
        try:
            conn.executescript(_REBUILD_SQL)
            after = conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
            if after != before:
                conn.rollback()
                print(f"FAILURE: row count changed during rebuild "
                      f"({before} before, {after} after) — rolled back")
                return 1
            conn.commit()
        finally:
            conn.execute("PRAGMA foreign_keys=ON")

        widened = {r["name"] for r in conn.execute("PRAGMA table_info(packages)")}
        if not {"fetch_attempts", "last_attempt_at"} <= widened:
            print("FAILURE: rebuilt table is missing the new columns")
            return 1

        print(f"SUCCESS: rebuilt packages ({before} rows preserved), "
              "fetch_status now accepts 'exhausted'")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

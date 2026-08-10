"""Tests for scripts/migrate_widen_fetch_status.py — the one-shot rebuild
that adds the fetch-retry-ceiling columns and widens fetch_status's CHECK
constraint (GUIDE §4, amended 2026-08-10). No prior migration-script test
existed in this repo (migrate_digest_day.py is a column backfill, not a
CHECK change); this establishes the pattern."""

import sqlite3

import migrate_widen_fetch_status as migrate
import pytest

from fapd import config


def _seed_old_shape_db(path):
    """A pre-migration packages table: the original 4-value CHECK, no
    fetch_attempts/last_attempt_at columns -- simulates an existing
    production database before this migration ever ran."""
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE packages (
            package_id TEXT PRIMARY KEY, collection TEXT NOT NULL,
            date_issued TEXT, last_modified TEXT NOT NULL, title TEXT,
            package_link TEXT, download_url TEXT, download_format TEXT,
            raw_path TEXT,
            fetch_status TEXT NOT NULL DEFAULT 'pending'
                CHECK (fetch_status IN ('pending','fetched','failed','skipped')),
            first_seen_at TEXT NOT NULL, digest_day TEXT, fetched_at TEXT,
            fetched_last_modified TEXT, last_error TEXT
        )
    """)
    for pid in ("PKG-A", "PKG-B", "PKG-C"):
        conn.execute(
            "INSERT INTO packages (package_id, collection, last_modified,"
            " fetch_status, first_seen_at) VALUES (?, 'BILLS', 'x', 'pending', 'x')",
            (pid,),
        )
    conn.commit()
    conn.close()


def test_migration_preserves_rows_and_widens_check(tmp_path, monkeypatch):
    db_path = tmp_path / "fapd.db"
    _seed_old_shape_db(db_path)
    monkeypatch.setattr(config, "PIPELINE_DB", db_path)

    assert migrate.main() == 0

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0] == 3
    cols = {r[1] for r in conn.execute("PRAGMA table_info(packages)")}
    assert {"fetch_attempts", "last_attempt_at"} <= cols

    # New value accepted...
    conn.execute("UPDATE packages SET fetch_status='exhausted' WHERE package_id='PKG-A'")
    conn.commit()
    row = conn.execute(
        "SELECT fetch_status FROM packages WHERE package_id='PKG-A'").fetchone()
    assert row[0] == "exhausted"

    # ...the CHECK still rejects garbage, and the indexes survived the rebuild.
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE packages SET fetch_status='bogus' WHERE package_id='PKG-B'")
    indexes = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='packages'")}
    assert {"idx_packages_collection_lastmod", "idx_packages_date_issued",
            "idx_packages_unfetched"} <= indexes
    conn.close()


def test_migration_is_idempotent(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "fapd.db"
    _seed_old_shape_db(db_path)
    monkeypatch.setattr(config, "PIPELINE_DB", db_path)

    assert migrate.main() == 0
    assert migrate.main() == 0  # second run: no-op, not an error
    assert "already migrated" in capsys.readouterr().out

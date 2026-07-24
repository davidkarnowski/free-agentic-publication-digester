"""Metadata store (data/info_intel.db). Schema per docs/schema.md — that
document is the design authority; keep the two in sync."""

import sqlite3

from . import config

_DDL = """
CREATE TABLE IF NOT EXISTS packages (
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
                          CHECK (fetch_status IN ('pending', 'fetched', 'failed', 'skipped')),
    first_seen_at         TEXT NOT NULL,
    fetched_at            TEXT,
    fetched_last_modified TEXT,
    last_error            TEXT
);

CREATE INDEX IF NOT EXISTS idx_packages_collection_lastmod
    ON packages (collection, last_modified);
CREATE INDEX IF NOT EXISTS idx_packages_date_issued
    ON packages (date_issued);
CREATE INDEX IF NOT EXISTS idx_packages_unfetched
    ON packages (fetch_status)
    WHERE fetch_status IN ('pending', 'failed');

CREATE TABLE IF NOT EXISTS granules (
    package_id    TEXT NOT NULL REFERENCES packages (package_id),
    granule_id    TEXT NOT NULL,
    granule_class TEXT,
    title         TEXT,
    first_seen_at TEXT NOT NULL,

    PRIMARY KEY (package_id, granule_id)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS idx_granules_class
    ON granules (granule_class);

CREATE TABLE IF NOT EXISTS sync_state (
    collection              TEXT PRIMARY KEY,
    last_modified_watermark TEXT NOT NULL,
    last_sync_started_at    TEXT,
    last_sync_completed_at  TEXT,
    last_sync_package_count INTEGER
);
"""


def connect(db_path=None):
    path = db_path or config.PIPELINE_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(_DDL)
    return conn

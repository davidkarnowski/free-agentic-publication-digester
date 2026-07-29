"""Metadata store (data/fapd.db). Schema per docs/schema.md — that
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

-- Phase 2: extraction layer (docs/schema.md, Extraction section) -----------

CREATE TABLE IF NOT EXISTS extracted_texts (
    package_id    TEXT NOT NULL REFERENCES packages (package_id),
    granule_id    TEXT NOT NULL DEFAULT '',   -- '' for whole-package docs (BILLS)
    collection    TEXT NOT NULL,
    doc_type      TEXT,                       -- FR: RULE/PRORULE/NOTICE/PRESDOCU;
                                              -- CREC: granule class; BILLS: version code
    title         TEXT,
    agency        TEXT,                       -- FR only
    metadata      TEXT NOT NULL DEFAULT '{}', -- JSON: collection-specific extras
    text          TEXT NOT NULL,
    char_count    INTEGER NOT NULL,
    graphics_substantive INTEGER NOT NULL DEFAULT 0,
    graphics_boilerplate INTEGER NOT NULL DEFAULT 0,
    extracted_at  TEXT NOT NULL,
    extractor_version INTEGER NOT NULL,

    PRIMARY KEY (package_id, granule_id)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS idx_extracted_collection_type
    ON extracted_texts (collection, doc_type);

CREATE TABLE IF NOT EXISTS graphic_assets (
    id            INTEGER PRIMARY KEY,
    package_id    TEXT NOT NULL REFERENCES packages (package_id),
    granule_id    TEXT NOT NULL DEFAULT '',
    gid           TEXT NOT NULL,              -- FR graphic filename, e.g. EN23JY26.004
    classification TEXT NOT NULL
                  CHECK (classification IN ('substantive', 'boilerplate')),
    page          TEXT,                       -- printed page (PRTPAGE) when known
    asset_path    TEXT,                       -- extracted image file, NULL until extracted
    status        TEXT NOT NULL DEFAULT 'inventoried'
                  CHECK (status IN ('inventoried', 'extracted', 'failed', 'skipped'))
);

CREATE INDEX IF NOT EXISTS idx_graphic_assets_package
    ON graphic_assets (package_id);

-- Sources expansion: mutable-source provenance (GUIDE §7, docs/schema.md) --

CREATE TABLE IF NOT EXISTS documents (
    id            INTEGER PRIMARY KEY,
    source_id     TEXT NOT NULL,              -- sources/registry.yaml id
    stable_id     TEXT NOT NULL,              -- feed GUID, else normalized URL
    url           TEXT NOT NULL,              -- as first discovered
    title         TEXT,
    claimed_published_at TEXT,                -- the source's own claim (T3/T4)
    first_seen_at TEXT NOT NULL,              -- our observation, never theirs
    state         TEXT NOT NULL DEFAULT 'present'
                  CHECK (state IN ('present', 'missing', 'removed', 'restored')),
    UNIQUE (source_id, stable_id)
);

CREATE TABLE IF NOT EXISTS captures (
    id            INTEGER PRIMARY KEY,
    document_id   INTEGER NOT NULL REFERENCES documents (id),
    ts_utc        TEXT NOT NULL,
    url           TEXT NOT NULL,
    final_url     TEXT,                       -- after redirects
    http_status   INTEGER,
    content_sha256 TEXT,                      -- decoded entity bytes (evidence)
    text_sha256   TEXT,                       -- normalized text (change signal)
    normalizer_version INTEGER,
    content_type  TEXT,
    bytes         INTEGER NOT NULL DEFAULT 0,
    response_headers TEXT,                    -- JSON subset (Date, Server, ETag...)
    change_kind   TEXT NOT NULL
                  CHECK (change_kind IN ('new', 'unchanged', 'unchanged_304',
                                         'bytes_changed', 'modified',
                                         'missing', 'removed', 'restored',
                                         'error', 'robots_refused')),
    prev_capture_id INTEGER REFERENCES captures (id),
    wayback_url   TEXT,
    wayback_status TEXT,
    note          TEXT
);

CREATE INDEX IF NOT EXISTS idx_captures_document ON captures (document_id, ts_utc);
CREATE INDEX IF NOT EXISTS idx_captures_ts ON captures (ts_utc);

CREATE TABLE IF NOT EXISTS mailbox_state (
    mailbox       TEXT PRIMARY KEY,           -- IMAP folder polled
    uid_validity  INTEGER,                    -- resets invalidate last_uid
    last_uid      INTEGER NOT NULL DEFAULT 0, -- highest processed UID
    last_polled_at TEXT
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS feed_state (
    source_id     TEXT PRIMARY KEY,
    etag          TEXT,
    last_modified TEXT,
    last_polled_at TEXT
);

-- Phase 3: analysis layer ---------------------------------------------------

CREATE TABLE IF NOT EXISTS summaries (
    package_id     TEXT NOT NULL,
    granule_id     TEXT NOT NULL DEFAULT '',
    prompt_version INTEGER NOT NULL,
    method         TEXT NOT NULL CHECK (method IN ('official', 'llm')),
    model          TEXT,                      -- model used when method='llm'
    inclusion_rule TEXT NOT NULL,             -- e.g. 'FR-SEL-01'
    summary        TEXT NOT NULL,
    input_tokens   INTEGER NOT NULL DEFAULT 0,
    output_tokens  INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL,

    PRIMARY KEY (package_id, granule_id, prompt_version)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS plain_summaries (
    package_id            TEXT NOT NULL,
    granule_id            TEXT NOT NULL DEFAULT '',
    plain_version         INTEGER NOT NULL,   -- config.PLAIN_PROMPT_VERSION
    source_prompt_version INTEGER NOT NULL,   -- summaries.prompt_version restated
    model                 TEXT,
    plain                 TEXT NOT NULL,
    input_tokens          INTEGER NOT NULL DEFAULT 0,
    output_tokens         INTEGER NOT NULL DEFAULT 0,
    created_at            TEXT NOT NULL,

    PRIMARY KEY (package_id, granule_id, plain_version, source_prompt_version)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS section_summaries (
    date           TEXT NOT NULL,
    section_key    TEXT NOT NULL,
    prompt_version INTEGER NOT NULL,
    model          TEXT NOT NULL,
    synopsis       TEXT NOT NULL,
    input_tokens   INTEGER NOT NULL DEFAULT 0,
    output_tokens  INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL,

    PRIMARY KEY (date, section_key, prompt_version)
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS day_summaries (
    date           TEXT NOT NULL,             -- digest date YYYY-MM-DD
    prompt_version INTEGER NOT NULL,
    model          TEXT NOT NULL,
    summary        TEXT NOT NULL,             -- the composed Day in Review
    input_tokens   INTEGER NOT NULL DEFAULT 0,
    output_tokens  INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL,

    PRIMARY KEY (date, prompt_version)
) WITHOUT ROWID;

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
    conn.execute("PRAGMA busy_timeout = 30000")  # before WAL switch: that PRAGMA
    conn.execute("PRAGMA foreign_keys = ON")     # needs an exclusive lock, and
    conn.execute("PRAGMA journal_mode = WAL")    # concurrent host workers (GUIDE §4) race on it
    conn.executescript(_DDL)
    return conn

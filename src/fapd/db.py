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
                          CHECK (fetch_status IN ('pending', 'fetched', 'failed',
                                                   'skipped', 'exhausted')),
    first_seen_at         TEXT NOT NULL,
    digest_day            TEXT,
    fetched_at            TEXT,
    fetched_last_modified TEXT,
    last_error            TEXT,
    fetch_attempts        INTEGER NOT NULL DEFAULT 0,
    last_attempt_at       TEXT,
    extract_attempts      INTEGER NOT NULL DEFAULT 0,
    extract_error         TEXT,
    last_extract_attempt_at TEXT
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

-- Per-day inference status (GUIDE §6 r15, 2026-08-24): which model
-- layers the finalizing run ran, and what produced the prose. The
-- digest renders one neutral line from it and never the cause
-- (docs/schema.md `day_inference`; fapd/inference.py is the only writer).
CREATE TABLE IF NOT EXISTS day_inference (
    date           TEXT PRIMARY KEY,          -- digest date YYYY-MM-DD
    available      INTEGER NOT NULL,          -- 1 when at least one layer ran
    backend        TEXT,                      -- llm backend name (cli/api/gemini/none)
    models         TEXT,                      -- comma-joined resolved models that produced prose
    layers         TEXT NOT NULL,             -- JSON {layer: ran|skipped|failed}
    recorded_at    TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS sync_state (
    collection              TEXT PRIMARY KEY,
    last_modified_watermark TEXT NOT NULL,
    last_sync_started_at    TEXT,
    last_sync_completed_at  TEXT,
    last_sync_package_count INTEGER
);

-- Continuous ingestion (GUIDE §5 two-artifact model; docs/continuous-ingestion.md).
-- Arrival journal: written by post-cycle reconciliation, never by the
-- collection functions themselves. observed_at is cycle-granularity by
-- design; dating rules key on claimed dates, not observation minutes.
CREATE TABLE IF NOT EXISTS item_journal (
    id            INTEGER PRIMARY KEY,
    observed_at   TEXT NOT NULL,
    source_class  TEXT NOT NULL CHECK (source_class IN ('govinfo', 'agency', 'email')),
    package_id    TEXT NOT NULL,
    granule_id    TEXT NOT NULL DEFAULT '',
    collection    TEXT,
    source_id     TEXT,                        -- registry id (agency/email classes)
    digest_date   TEXT,                        -- the day the item belongs to
    event         TEXT NOT NULL CHECK (event IN ('ingested', 'summarized', 'plain')),
    cycle_id      TEXT,

    UNIQUE (package_id, granule_id, event)
);
CREATE INDEX IF NOT EXISTS idx_item_journal_day
    ON item_journal (digest_date, observed_at);

-- Per-source model prose (GUIDE §3a source surfaces, 2026-08-03).
-- Assessment text is lexicon-scanned BEFORE insert; a failing scan
-- stores nothing (schema.md). Append-only; pages render the newest row.
CREATE TABLE IF NOT EXISTS source_assessments (
    source_id      TEXT NOT NULL,
    prompt_version INTEGER NOT NULL,
    generated_at   TEXT NOT NULL,
    model          TEXT NOT NULL,
    trigger_reason TEXT NOT NULL,   -- 'initial' | 'age-30d' | 'health-change'
    assessment     TEXT NOT NULL,
    PRIMARY KEY (source_id, prompt_version, generated_at)
);

-- What the source IS (summary + 250-500 word orientation). registry_hash
-- is the sha256 of the registry entry: an edited entry regenerates, an
-- untouched one never does — no timer (GUIDE §3a).
CREATE TABLE IF NOT EXISTS source_descriptions (
    source_id      TEXT NOT NULL,
    prompt_version INTEGER NOT NULL,
    registry_hash  TEXT NOT NULL,
    generated_at   TEXT NOT NULL,
    model          TEXT NOT NULL,
    summary        TEXT NOT NULL,
    description    TEXT NOT NULL,
    PRIMARY KEY (source_id, prompt_version, registry_hash)
);

-- Persisted health label per source, so a label TRANSITION is
-- detectable (the assessment layer's health-change trigger).
CREATE TABLE IF NOT EXISTS source_health_state (
    source_id    TEXT PRIMARY KEY,
    label        TEXT NOT NULL,
    since        TEXT NOT NULL,
    last_checked TEXT NOT NULL
);

-- Collector liveness, read by OPS-GUIDE / the fapd-health skill.
-- finalized_date is the EOD marker in its OWN column (review D5): every
-- last_result writer replaces that blob wholesale — the no-op path erased
-- the JSON marker on 2026-08-01 (35 duplicate pipeline runs) and the
-- error path had the identical hole. finalize_target/attempts are the
-- finalizer's per-day hard-stop ladder (schema.md).
CREATE TABLE IF NOT EXISTS collector_state (
    worker             TEXT PRIMARY KEY,       -- 'govinfo' | 'email' | 'analyze' | 'host:<netloc>'
    last_cycle_at      TEXT,
    last_ok_at         TEXT,
    last_result        TEXT,                   -- JSON stats of the last cycle (status line)
    consecutive_errors INTEGER NOT NULL DEFAULT 0,
    finalized_date     TEXT,                   -- 'eod' row only: newest finalized day
    finalize_target    TEXT,                   -- 'eod' row only: day the attempt ladder counts
    finalize_attempts  INTEGER NOT NULL DEFAULT 0,
    -- 'eod' row only: did the finalized day reach the REPOSITORY?
    -- Finalizing and publishing to git fail separately (F-021): on
    -- 2026-08-07 the digest served all day while the evidence commit sat
    -- rejected, and last_result was the only trace, so the row read a
    -- clean success. These are the durable measure.
    evidence_pushed_at     TEXT,
    evidence_push_error    TEXT,
    evidence_push_attempts INTEGER NOT NULL DEFAULT 0
);

-- Summarization attempts per item (GUIDE §6 rule 14). The retry ceiling
-- is per RUN, and the collector calls analyze.run every 15 minutes for
-- every pending date — so an item that cannot be summarized was retried
-- forever at ~29K input tokens a go (measured 2026-07-31: 1,345 single
-- retries, 39.7M tokens). Attempts are remembered so the ladder ends.
CREATE TABLE IF NOT EXISTS summary_attempts (
    package_id     TEXT NOT NULL,
    granule_id     TEXT NOT NULL DEFAULT '',
    prompt_version INTEGER NOT NULL,
    layer          TEXT NOT NULL DEFAULT 'map',
    attempts       INTEGER NOT NULL DEFAULT 0,
    last_at        TEXT,

    PRIMARY KEY (package_id, granule_id, prompt_version, layer)
);

-- Lexicon-correction attempts (GUIDE §6 r14a, incident 2026-08-08:
-- CREC-2026-07-13-pt1-PgH4403, "extreme"). One row per corrective call,
-- success or failure — an ops/audit trail, not a reader-facing surface.
-- The durable per-item ceiling itself lives in summary_attempts above,
-- under layer 'map-correction'/'plain-correction'; this table is what
-- lets scripts/audit.py and the insight report count and explain what
-- happened, the same way llm_calls explains ordinary spend.
CREATE TABLE IF NOT EXISTS lexicon_corrections (
    id           INTEGER PRIMARY KEY,
    package_id   TEXT NOT NULL,
    granule_id   TEXT NOT NULL DEFAULT '',
    layer        TEXT NOT NULL,   -- 'map' | 'plain'
    term         TEXT NOT NULL,
    outcome      TEXT NOT NULL CHECK (outcome IN ('corrected', 'withdrawn')),
    corrected_at TEXT NOT NULL
);

-- Section-level tags (GUIDE §6 r12a): mechanical branch/agency tags plus
-- model discovery keys, one row per (date, section, tag).
CREATE TABLE IF NOT EXISTS section_tags (
    date           TEXT NOT NULL,
    section_key    TEXT NOT NULL,
    tag            TEXT NOT NULL,
    method         TEXT NOT NULL CHECK (method IN ('mechanical', 'llm')),
    prompt_version INTEGER,                    -- NULL for mechanical
    model          TEXT,
    created_at     TEXT NOT NULL,

    PRIMARY KEY (date, section_key, tag)
) WITHOUT ROWID;

-- Section auto-tagging (schema-first; build is ops-backlog OB-9).
-- Tags attach to items — renderers aggregate to section level; LLM
-- discovery keys are a §3a-versioned model surface, labeled by method.
CREATE TABLE IF NOT EXISTS item_tags (
    package_id     TEXT NOT NULL,
    granule_id     TEXT NOT NULL DEFAULT '',
    tag_kind       TEXT NOT NULL CHECK (tag_kind IN ('branch', 'agency', 'discovery')),
    tag            TEXT NOT NULL,
    method         TEXT NOT NULL CHECK (method IN ('mechanical', 'llm')),
    prompt_version INTEGER,                    -- NULL for mechanical
    model          TEXT,
    created_at     TEXT NOT NULL,

    PRIMARY KEY (package_id, granule_id, tag_kind, tag)
) WITHOUT ROWID;
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
    _ensure_columns(conn, "collector_state", {
        "finalized_date": "TEXT",
        "finalize_target": "TEXT",
        "finalize_attempts": "INTEGER NOT NULL DEFAULT 0",
        "evidence_pushed_at": "TEXT",
        "evidence_push_error": "TEXT",
        "evidence_push_attempts": "INTEGER NOT NULL DEFAULT 0",
    })
    # Filing axis (GUIDE §3, amended 2026-08-06). Backfill of existing
    # rows is the deliberate one-shot scripts/migrate_digest_day.py,
    # never startup DDL.
    _ensure_columns(conn, "packages", {"digest_day": "TEXT"})
    # Extraction attempt ceiling (2026-08-24, docs/schema.md): additive,
    # so no rebuild — unlike fetch_attempts, which rode the CHECK-widening
    # migration of 2026-08-10 and therefore never needed this hook.
    _ensure_columns(conn, "packages", {
        "extract_attempts": "INTEGER NOT NULL DEFAULT 0",
        "extract_error": "TEXT",
        "last_extract_attempt_at": "TEXT",
    })
    return conn


def _ensure_columns(conn, table, columns):
    """Additive micro-migration (the LLMClient._ensure_backend_column
    pattern): _DDL's IF NOT EXISTS never alters an existing table, so a
    column added to the CREATE above must also be added here or every
    pre-existing database silently misses it. Destructive changes stay
    deliberate one-shot scripts, never startup DDL."""
    have = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
    for name, decl in columns.items():
        if name not in have:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")
    conn.commit()

# SQLite Schema — Pipeline Metadata Store

Status: living design document, per GUIDE.md §5. Covers Phase 1 (Fetch &
store: package inventory, granule inventory, delta-sync watermarks) and
Phase 2 (Extraction: normalized text records and graphic assets — see the
Extraction section at the end).

- **Database file:** `data/info_intel.db` (repo-relative, like all paths in
  this project — GUIDE §9).
- **Raw documents are not stored in the database.** They live on the
  filesystem under `data/raw/<collection>/<dateIssued>/` (GUIDE §5); the
  database stores the *path* and the fetch bookkeeping.
- **Request auditing is not in this database.** See
  [fetch_log.db](#the-separate-fetch_logdb) below.

## Conventions

- **Timestamps** are `TEXT`, ISO-8601, UTC, `Z`-suffixed:
  `2026-07-24T14:03:07Z`. This makes lexicographic comparison identical to
  chronological comparison, so `WHERE last_modified > ?` and `MAX(...)` work
  with plain string operators and indexes. Date-only fields (`date_issued`)
  are `YYYY-MM-DD`.
- **Column naming** is `snake_case`; the govinfo API's camelCase fields map
  1:1 (`packageId` → `package_id`, `lastModified` → `last_modified`,
  `dateIssued` → `date_issued`, `granuleClass` → `granule_class`).
- **Connections** run `PRAGMA foreign_keys = ON` (SQLite defaults it off) and
  `PRAGMA journal_mode = WAL` (set once; lets a digest read while a sync
  writes — the only concurrency this single-user pipeline needs).
- **Upserts** use `INSERT ... ON CONFLICT ... DO UPDATE`, keeping every sync
  idempotent — re-running a sync, or re-seeing a package at the watermark
  boundary, is always harmless.

---

## `packages`

One row per govinfo package ever seen by a sync. This is the inventory: what
exists, whether we hold a current local copy, and where that copy lives.

```sql
CREATE TABLE packages (
    package_id            TEXT PRIMARY KEY,              -- govinfo packageId, e.g. 'CREC-2026-07-23'
    collection            TEXT NOT NULL,                 -- collection code: 'CREC', 'BILLS', 'FR', ...
    date_issued           TEXT,                          -- official issue date, 'YYYY-MM-DD'
    last_modified         TEXT NOT NULL,                 -- server's lastModified, most recent value seen
    title                 TEXT,                          -- package title from the API

    package_link          TEXT,                          -- API summary URL (canonical citation link)
    download_url          TEXT,                          -- URL of the format we fetch (XML preferred)
    download_format       TEXT,                          -- 'xml' | 'pdf' | 'htm' | 'mods' | 'zip'

    raw_path              TEXT,                          -- repo-relative path of the stored raw file,
                                                         -- e.g. 'data/raw/CREC/2026-07-23/CREC-2026-07-23.xml'

    fetch_status          TEXT NOT NULL DEFAULT 'pending'
                          CHECK (fetch_status IN ('pending', 'fetched', 'failed', 'skipped')),
    first_seen_at         TEXT NOT NULL,                 -- when a sync first recorded this package
    fetched_at            TEXT,                          -- when the raw file was last downloaded
    fetched_last_modified TEXT,                          -- server lastModified at the time of that download
    last_error            TEXT                           -- most recent download error, NULL when healthy
);
```

### Column commentary

- **`package_id`** — the natural key. govinfo packageIds are globally unique
  and permanent, and every citation in a digest resolves through them
  (GUIDE §2 "cite everything"). No surrogate key needed.
- **`collection`** — denormalized from the packageId prefix on purpose: it is
  the left column of the delta-sync index and of most filters. A seven-row
  `collections` lookup table would add a join and buy nothing.
- **`date_issued`** — the official publication date; this is the axis the
  daily digest is built on ("what was published on day D"). Nullable because
  it comes from the API and we do not want a listing quirk to abort a sync.
- **`last_modified`** — the server's change signal, updated every time a sync
  sees the package. Together with `fetched_last_modified` it implements
  GUIDE §4's "never re-download unchanged content, keyed by package ID +
  lastModified": the local copy is current iff
  `fetched_last_modified = last_modified`.
- **`package_link` / `download_url` / `download_format`** — enough to
  (re)download without another summary call, and to render a citation link.
  We record the one format we chose (XML preferred, GUIDE §5), not the full
  format matrix — this is an inventory, not a mirror of the API.
- **`raw_path`** — repo-relative (GUIDE §9 bans absolute paths), NULL until
  the file is actually on disk.
- **`fetch_status`** — the download lifecycle, deliberately coarse:
  - `pending` — known to exist; no current local copy (new, or the server's
    `last_modified` moved past `fetched_last_modified`).
  - `fetched` — current raw file on disk at `raw_path`.
  - `failed` — download attempted, gave up after retries; `last_error` says
    why. Re-tried on a later run.
  - `skipped` — deliberately not downloaded (e.g., a package class we list
    for the coverage statement but chose not to archive). Distinct from
    `failed` so the GUIDE §2 completeness accounting can tell "couldn't"
    from "chose not to".
- **`first_seen_at` / `fetched_at`** — audit trail: when we learned of it
  vs. when we archived it. `fetched_at` NULL until first successful download.
- **`fetched_last_modified`** — the change-detection anchor (see
  `last_modified` above). When a sync observes a newer `last_modified`, it
  updates that column and flips `fetch_status` back to `'pending'`; the old
  `fetched_last_modified` stays until the re-download succeeds, so a crash
  between "noticed change" and "downloaded change" loses nothing.
- **`last_error`** — one column, most recent error only. The full per-request
  history (every attempt, status, timing) is already in `fetch_log.db`;
  duplicating it here would be warehouse thinking.

### Indexes

```sql
-- Delta sync: "packages in collection C, ordered by last_modified" — both
-- for upserting a sync page and for deriving/verifying the watermark
-- (MAX(last_modified) per collection resolves entirely in this index).
CREATE INDEX idx_packages_collection_lastmod
    ON packages (collection, last_modified);

-- Digest generation: "everything issued on day D" (optionally filtered by
-- collection afterwards — with ~a dozen packages per day, filtering the
-- handful of rows the index returns is free).
CREATE INDEX idx_packages_date_issued
    ON packages (date_issued);

-- Download queue: "what's unfetched". Partial index — it only contains
-- pending/failed rows, so it stays tiny (near-empty in steady state) no
-- matter how large the inventory grows, and the common query
--   SELECT ... FROM packages WHERE fetch_status IN ('pending','failed')
-- never scans the fetched majority.
CREATE INDEX idx_packages_unfetched
    ON packages (fetch_status)
    WHERE fetch_status IN ('pending', 'failed');
```

Not indexed: `title` (never searched in this store — discovery is the API's
job), `fetched_at` (audit column, read by humans).

---

## `granules`

Sub-documents of a package: individual Congressional Record sections for
CREC, individual rules/notices/presidential documents for FR. BILLS packages
are single documents and simply have no granule rows.

```sql
CREATE TABLE granules (
    package_id    TEXT NOT NULL REFERENCES packages (package_id),
    granule_id    TEXT NOT NULL,                         -- govinfo granuleId, e.g. 'CREC-2026-07-23-pt1-PgH4523'
    granule_class TEXT,                                  -- e.g. CREC: 'HOUSE','SENATE','EXTENSIONS','DAILYDIGEST';
                                                         --      FR: 'RULE','PRORULE','NOTICE','PRESDOCU'
    title         TEXT,                                  -- granule title (section heading / document subject)
    first_seen_at TEXT NOT NULL,

    PRIMARY KEY (package_id, granule_id)
) WITHOUT ROWID;
```

### Column commentary

- **`package_id` + `granule_id`** — composite natural primary key. govinfo
  granuleIds are unique within a package (and in practice globally, since
  they embed the packageId), but the composite key is what every real lookup
  uses: "granules of package P" is a prefix scan of the primary key, so the
  FK needs no extra index. `WITHOUT ROWID` because the table is pure TEXT
  keyed by that composite — it stores the rows in the primary-key B-tree
  directly instead of paying for a hidden rowid plus a separate PK index.
- **`granule_class`** — the API's `granuleClass`; the mechanical selection
  axis for digests ("all Daily Digest sections", "all economically
  significant rules start as class RULE"). Nullable: not every collection
  populates it.
- **`title`** — the section heading / document subject; this is what the
  digest quotes when listing what a package contains.
- **`first_seen_at`** — same audit role as on `packages`.
- **No link or path columns.** Granule content URLs are deterministic from
  `package_id` + `granule_id` + format, and Phase 1 archives whole packages
  (granule-level content lives inside the package XML). If a later phase
  fetches granules individually, it can add fetch bookkeeping then — not
  speculatively now.
- **Deletion/replacement:** if a package is re-fetched and its granule list
  changed, the sync deletes that package's granule rows and re-inserts —
  granules carry no local state worth preserving, so replace-on-refetch is
  simpler and always correct.

### Indexes

```sql
-- Digest selection by section type across a day's packages
-- ("give me every DAILYDIGEST granule", "list today's RULE granules").
CREATE INDEX idx_granules_class
    ON granules (granule_class);
```

The primary key already serves "granules of package P"; nothing else is
queried at Phase 1 scale (a CREC day is a few hundred granules).

---

## `sync_state`

One row per collection: the watermark that makes delta sync a delta.

```sql
CREATE TABLE sync_state (
    collection             TEXT PRIMARY KEY,             -- 'CREC', 'BILLS', 'FR', ...
    last_modified_watermark TEXT NOT NULL,               -- resume point: syncs ask the API for
                                                         -- lastModified >= this value
    last_sync_started_at   TEXT,                         -- most recent attempt (success or not)
    last_sync_completed_at TEXT,                         -- most recent *successful* completion
    last_sync_package_count INTEGER                      -- packages seen in that successful sync (audit)
);
```

### Column commentary

- **`collection`** — primary key; at most seven rows ever (GUIDE §3). No
  indexes needed beyond the PK, obviously.
- **`last_modified_watermark`** — the heart of GUIDE §4's "poll, don't
  hammer": the next sync's `lastModifiedStartDate`. It is a *server-side*
  `lastModified` value (taken from listing results), never a local clock
  reading — comparing our clock to GPO's invites missed packages.
- **`last_sync_started_at` vs `last_sync_completed_at`** — a started-but-not-
  completed pair is how a human (or the coverage statement) notices a sync
  died mid-run. The watermark is only advanced together with
  `last_sync_completed_at`, so a crashed sync re-covers the same window.
- **`last_sync_package_count`** — one number for the worklog and the digest's
  completeness accounting ("sync saw N changed packages"); cheap, useful,
  and not a substitute for `fetch_log.db`.

### Delta-sync algorithm (how this table is read and written)

Per collection, one scheduled run per day (GUIDE §4):

1. **Read** the collection's row.
   - Row exists → `start = last_modified_watermark`.
   - **No row (first sync or deliberate reset)** → per GUIDE §4, the sync is
     date-bounded, never open-ended:
     `start = now_utc - INITIAL_SYNC_LOOKBACK_DAYS` (currently 3 days,
     defined in `src/info_intel/config.py`). Older history is only ever
     acquired via a deliberate bulkdata backfill, never by widening this
     window.
2. **Write** `last_sync_started_at = now` (upserting the row if new).
3. **List** changed packages: `GET /collections/{collection}/{start}` with
   `offsetMark=*`, `pageSize` up to 1000, following `nextPage` until
   exhausted. While paging, track `max_seen = MAX(lastModified)` over all
   results.
4. **Upsert** each listed package into `packages`:
   - New `package_id` → insert with `fetch_status = 'pending'`.
   - Existing row with a newer `last_modified` → update `last_modified` and
     flip `fetch_status` to `'pending'` (content changed; re-download).
   - Existing row, unchanged `last_modified` (the inclusive watermark
     boundary re-appearing) → no-op. This is what makes step 6's inclusive
     resume safe.
5. **Download** everything `pending`/`failed` (via `idx_packages_unfetched`),
   under the rate budget; on success set `raw_path`, `fetched_at`,
   `fetched_last_modified = last_modified`, `fetch_status = 'fetched'`; on
   final failure set `'failed'` + `last_error`. Downloads that don't finish
   today are simply still pending tomorrow — the queue lives in `packages`,
   not in the watermark.
6. **Advance the watermark** — only after the listing in step 3 completed
   without error: set `last_modified_watermark = max_seen` (unchanged if the
   window was empty), `last_sync_completed_at = now`,
   `last_sync_package_count = count`. Crucially, the watermark depends on
   the *listing* succeeding, not on every *download* succeeding: undownloaded
   packages are safely parked as `pending` rows, so a partially-failed
   download pass never forces re-listing the whole window.

If the process dies between steps 2 and 6, the watermark never moved: the
next run re-lists the same window and the idempotent upserts absorb the
overlap. That is the entire crash-recovery story — no journaling table, no
run IDs.

---

## The separate `fetch_log.db`

Already exists; owned by the HTTP client (`config.FETCH_LOG_DB`, at
`data/fetch_log.db`). It records every outbound request — columns: `ts_utc`,
`url`, `params` (with `api_key` stripped), `status`, `bytes`, `elapsed_ms`,
`attempt`, `error` — satisfying GUIDE §4 "log every request."

It stays a **separate database file**, and this document does not redesign
it:

- Different owner and write cadence: the HTTP client appends a row per
  request, below the pipeline's transaction logic; the metadata store commits
  per sync step. Separate files mean the audit log can never be rolled back
  by a pipeline transaction, and a locked pipeline DB can never lose a log
  row.
- Different lifecycle: the request log is an append-only audit artifact that
  can be inspected, archived, or truncated independently of the inventory.
- The only "join" ever needed is human (correlating a `last_error` with its
  request rows by URL and timestamp), which needs no shared schema.

---

## Extraction layer (Phase 2)

Two tables written by the extraction orchestrator
(`src/info_intel/extract.py`); parsers themselves are pure functions
(`parsers/{fr,crec,bills}.py: parse(raw_path, package) -> iter[record]`)
that never touch the database.

### `extracted_texts`

One row per extracted document: an FR document, a CREC granule, or a whole
bill (`granule_id = ''`). Composite natural key `(package_id, granule_id)`,
`WITHOUT ROWID`, mirroring `granules`.

Columns beyond the obvious: `doc_type` (FR document class / CREC section /
bill version code) is the digest's mechanical-selection axis;
`metadata` is a sorted-key JSON bag for collection-specific extras (CFR
refs, sponsors, page ranges, official `<SUM>` summaries per GUIDE §6);
`graphics_substantive` / `graphics_boilerplate` carry the FR-GPH-01 split;
`extracted_at` + `extractor_version` drive staleness.

**Staleness rule** (query in `extract.pending_packages`): a fetched package
needs (re-)extraction iff it has no rows, `extracted_at < fetched_at`
(raw was re-fetched), or `extractor_version < EXTRACTOR_VERSION` (parser
logic changed). Re-extraction is replace-on-rerun per package
(delete + insert) — idempotent, partial failures re-run harmlessly, and one
bad package never blocks the rest (per-package isolation in `extract.run`).

Index: `(collection, doc_type)` for digest selection queries.

### `graphic_assets`

One row per `<GPH>` occurrence in an FR issue (rowid PK — GIDs repeat, e.g.
a signature graphic appearing in several documents). `classification` is
the FR-GPH-01 result; `page` is the printed page from `PRTPAGE`;
`asset_path` (repo-relative, under `data/assets/FR/<date>/<package>/`)
is set when the image was extracted from the companion PDF; `status`:
`inventoried` (known, not yet extracted), `extracted`, `failed`, `skipped`
(boilerplate is always skipped). Replace-on-rerun alongside the package's
text rows. Index on `package_id`.

### `plain_summaries` (plain-speak layer)

One row per plain-language restatement of a `summaries` row. Keyed by
`(package_id, granule_id, plain_version, source_prompt_version)` —
`plain_version` tracks `config.PLAIN_PROMPT_VERSION` (the restatement
prompt), `source_prompt_version` the summaries row it restates, so plain
rows self-invalidate if factual summaries regenerate, and phrasing
iterations never touch the summaries table. Rows are written by
`analyze.run_plain` (batched, cheap tier); a missing row simply renders the
item without its "In plain terms" line — presentation aid, never coverage.

---

## Provenance layer (sources expansion, GUIDE §7)

`documents` — stable identity for mutable-source items: keyed
(source_id, stable_id = feed GUID else normalized URL); stores the
source's `claimed_published_at` and our `first_seen_at` separately
(backdating detection depends on never conflating them); lifecycle
`state` present/missing/removed/restored with conservative promotion
(handled by the future re-check pass).

`captures` — one row per fetch **attempt** (including 304s, robots
refusals, errors — absence must be an assertion): two hashes
(content_sha256 = decoded entity bytes stored content-addressed under
data/captures/<sha[:2]>/; text_sha256 = normalized text, tagged
normalizer_version), response-header subset JSON, change_kind enum
(new/unchanged/unchanged_304/bytes_changed/modified/missing/removed/
restored/error/robots_refused), prev_capture_id chain, Wayback
corroboration columns. Daily attempt-level manifests are exported to
provenance/manifests/ (committed) with a previous-day hash chain.

`feed_state` — per-source conditional-GET validators (ETag/Last-Modified)
for the agency poller.

`fetch_log` (fetch_log.db) gained a `client` column via additive
migration: NULL rows are historical govinfo traffic; budgets are counted
per client bucket (govinfo vs agency vs wayback).

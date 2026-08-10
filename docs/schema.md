# SQLite Schema — Pipeline Metadata Store

Status: living design document, per GUIDE.md §5. Covers all five layers
of `data/fapd.db` (fetch & store; extraction; analysis; provenance;
continuous ingestion), plus the two companion databases the pipeline
keeps beside it (`fetch_log.db`, `llm_ledger.db`).

- **Database file:** `data/fapd.db` (repo-relative, like all paths in
  this project — GUIDE §9). `db.connect()` sets `busy_timeout = 30000`
  FIRST, then `foreign_keys`, then `journal_mode = WAL` — the WAL
  switch needs an exclusive lock and concurrent host workers race on
  it, so the timeout must already be armed (ordering is load-bearing).
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
                          CHECK (fetch_status IN ('pending', 'fetched', 'failed',
                                                   'skipped', 'exhausted')),
    first_seen_at         TEXT NOT NULL,                 -- when a sync first recorded this package
    digest_day            TEXT,                          -- the digest day this package files under (GUIDE §3, amended 2026-08-06)
    fetched_at            TEXT,                          -- when the raw file was last downloaded
    fetched_last_modified TEXT,                          -- server lastModified at the time of that download
    last_error            TEXT,                          -- most recent download error, NULL when healthy
    fetch_attempts        INTEGER NOT NULL DEFAULT 0,     -- consecutive cycle-level download failures (GUIDE §4, amended 2026-08-10)
    last_attempt_at       TEXT                           -- ISO-8601 UTC of the most recent attempt, NULL until first
);
```

### Column commentary

- **`package_id`** — the natural key. govinfo packageIds are globally unique
  and permanent, and every citation in a digest resolves through them
  (GUIDE §2 "cite everything"). No surrogate key needed.
- **`collection`** — denormalized from the packageId prefix on purpose: it is
  the left column of the delta-sync index and of most filters. A seven-row
  `collections` lookup table would add a join and buy nothing.
- **`date_issued`** — the document's own official date (proceedings day,
  opinion issue date, FR cover date). Nullable because it comes from the API
  and we do not want a listing quirk to abort a sync. *Until 2026-08-06 this
  was also the digest-filing axis; filing now keys on `digest_day` below,
  and `date_issued` remains the display date and the USCOURTS fetch-window
  key.*
- **`digest_day`** — the digest day this package files under (GUIDE §3,
  amended 2026-08-06: observation-day filing). **Write-once at first
  sight, never updated** — a revision re-fetch must not re-file a
  document. Per `config.FILING_POLICY`: observation-filed collections
  (CREC, BILLS, USCOURTS, PLAW) get the Eastern publication day of
  `first_seen_at`; cover-filed collections (FR, AGENCYPR) get
  `date_issued`. Pre-cutover rows are backfilled `= date_issued` by the
  one-shot `scripts/migrate_digest_day.py`, so every frozen digest
  re-renders identically. Nullable only for the instant between an old
  database attaching and the migration running.
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
    why. Re-tried on a later run, up to `config.MAX_PACKAGE_FETCH_ATTEMPTS`
    (GUIDE §4, amended 2026-08-10).
  - `skipped` — deliberately not downloaded (e.g., a package class we list
    for the coverage statement but chose not to archive). Distinct from
    `failed` so the GUIDE §2 completeness accounting can tell "couldn't"
    from "chose not to".
  - `exhausted` — retried `config.MAX_PACKAGE_FETCH_ATTEMPTS` (48, ~24h of
    cycles) times across collector cycles and never succeeded; a disclosed
    gap, distinct from `skipped` (this one genuinely *couldn't*, not
    *chose not to*) and from `sources.STATUSES`'s `unavailable` (a
    different, source-registry-level concept — a publisher refusing us
    entirely, not one package's download). Stops re-entering the download
    queue (`idx_packages_unfetched` only covers `pending`/`failed`). A
    later content revision (`last_modified` advancing) resets
    `fetch_attempts` to 0 and flips the row back to `pending` — a revision
    is a new problem, not a continuation of the old one. Added because
    `sync.py` had no cross-cycle retry ceiling at all before this: a
    permanently-failing package was re-attempted every ~30-minute cycle
    forever, inflating the 2026-07-31-accepted 18.1% govinfo error
    baseline to a measured 22-26% (2026-08-04 through 09). Adding this
    value required widening the `CHECK` constraint on an existing
    database, which `_ensure_columns`'s additive-only pattern cannot do
    (see `digest_day` above for that pattern's usual shape) — the
    one-shot `scripts/migrate_widen_fetch_status.py` rebuilds the table
    instead, this repo's first migration of that kind.
- **`fetch_attempts`** — consecutive cycle-level failures since the last
  success (GUIDE §4, amended 2026-08-10). Reset to 0 on a successful
  download (`_download_package`) and on a content revision
  (`_upsert_package`'s `last_modified`-advanced branch) — both are "start
  over," not "keep counting." This is a *cycle*-level counter, not a
  per-HTTP-attempt one: each cycle's own `client.py`-level retry (up to 5
  attempts with backoff) already happens before a cycle counts as one
  failure here — the two ceilings operate at different layers on purpose,
  the same relationship `MAX_ITEM_SUMMARY_ATTEMPTS` has to a single LLM
  call's own retry behavior.
- **`last_attempt_at`** — ISO-8601 UTC of the most recent attempt, NULL
  until the first one. Diagnostic only (surfaced by
  `scripts/audit.py`'s repeat-failures report); nothing keys off it.
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
     defined in `src/fapd/config.py`). Older history is only ever
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
`data/fetch_log.db`). Two tables:

`fetch_log` records every outbound request — columns: `id`, `ts_utc`,
`url` (logged pre-redacted: `api_key` is stripped from the query string
before the row is written; there is no separate params column),
`status`, `bytes`, `elapsed_ms`, `attempt`, `error`, and `client`
(added by in-place micro-migration; NULL rows are historical govinfo
traffic) — satisfying GUIDE §4 "log every request."

`robots_cache` (added 2026-07-31, finding F-007) — `host` PK, `body`
(NULL = known-absent robots.txt, an RFC 9309 allow), `fetched_at`.
Persists the 24-hour robots verdict across the collector's
client-per-cycle lifecycle; temporary 5xx disallows are deliberately
NOT persisted (a statement about a moment must not outlive the outage).
Pragmas: this DB sets `busy_timeout` only — it is not WAL (aligning it
is on the Corpus backlog).

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

## The separate `llm_ledger.db`

Owned by `LLMClient` (`config.LLM_LEDGER_DB`, at `data/llm_ledger.db`);
the accountability layer for model spend, paralleling the fetch log
(GUIDE §6 r7-r8). One table, `llm_calls`: `ts_utc`, `backend`
(`cli`/`api` — added by the `_ensure_backend_column` in-place ALTER,
the canonical micro-migration pattern), `model` (the resolved concrete
model, never the tier alias), `purpose` (`layer:detail`, e.g.
`map:batch2`), `package_id`/`granule_id`, `input_tokens` (currently the
SUM of regular + cache-read + cache-creation tokens — splitting the
three billed components is review R1), `output_tokens`, `duration_ms`,
`error`. Every call is recorded — failures included — before anyone
reads the response. No cap is enforced yet (§6 r8 measure-first; the
ceiling derived from this ledger is the Editorial section's top backlog
item). Pragmas: neither WAL nor busy_timeout today — aligning it is on
the Corpus backlog.

---

## Extraction layer (Phase 2)

Two tables written by the extraction orchestrator
(`src/fapd/extract.py`); parsers themselves are pure functions
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

## Analysis layer (Phase 3)

### `summaries` (map layer)

The most-queried analysis table: one row per summarized item, keyed by
`(package_id, granule_id, prompt_version)` — bumping
`config.PROMPT_VERSION` regenerates this layer only (GUIDE §6 r5).
`method ∈ official/llm` — official rows are verbatim agency/GPO text
(FR SUMMARY preambles) stored at zero token cost; `inclusion_rule`
names the mechanical rule that promoted the item (the digest's
"Included because" line reads it); `model` and the token columns are
the per-row share of the batched call that produced it. Reruns skip
existing rows: a summarized item never costs a second call.

### `section_summaries` / `day_summaries` (compose layer)

EOD-only synthesis, keyed by `(date, section_key, prompt_version)` and
`(date, prompt_version)` respectively; each versions independently
(§3a) so phrasing iterations never regenerate factual layers. A stored
day composition is invalidated when any item summary for the date is
newer than it (late-arriving Record issues must never leave the
synthesis stale — the `substr(...,1,19)` timestamp comparison in
`compose.py` carries the CLAUDE.md §10 confirm-gate).

### `summary_attempts` (GUIDE §6 r14 — the retry ceiling's memory)

`(package_id, granule_id, prompt_version, layer)` → `attempts`,
`last_at`. The per-run retry ceiling resets every collector cycle, and
analyze runs every 15 minutes per pending date — so before this table
existed an unsummarizable item was retried indefinitely (measured
2026-07-31: 1,345 single retries, 39.7M input tokens, 60% of the day).
`pending_map_items` excludes items at `MAX_ITEM_SUMMARY_ATTEMPTS`;
past the ceiling an item is a disclosed gap, not pending work. (Known
gap, review D4: the plain layer records attempts here but does not yet
consult them.)

**The `*-correction` layer convention (GUIDE §6 r14a, added 2026-08-09):**
`layer` values `'map-correction'`/`'plain-correction'` track a
*different* ceiling than ordinary `'map'`/`'plain'` retries — the bounded
number of error-informed rewrites attempted on a summary that already
exists but tripped the render-time lexicon gate, per
`config.MAX_LEXICON_CORRECTION_ATTEMPTS`. `analyze.run()`/`run_plain()`
consult this layer explicitly in their pending-selection loops (unlike
D4's gap above, this one is closed for the correction layer from the
start) — an item whose correction ceiling is exhausted must never
re-enter ordinary summarization with the uncorrected prompt, or the
withdrawn row would simply be regenerated with the same violation on the
next cycle.

### `lexicon_corrections` (GUIDE §6 r14a — the correction audit trail)

One row per corrective call attempt, success or failure. `package_id`,
`granule_id`, `layer` (`'map'` | `'plain'`), `term` (the violated word
that triggered the attempt), `outcome` (`'corrected'` | `'withdrawn'`),
`corrected_at`. This is an ops/audit surface — `scripts/audit.py` and
the insight report can count corrections and withdrawals the same way
`llm_calls` explains ordinary token spend — not a reader-facing table;
a withdrawn item's absence from the digest is disclosed through the
ordinary Coverage Statement "counted, not summarized" accounting, same
bucket as any other disclosed gap (editorial.md, "never fabricate").

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

### `mailbox_state` / `feed_state` (channel watermarks)

`mailbox_state` — one row per polled IMAP folder: `uid_validity`
(a server-side reset invalidates `last_uid`), `last_uid` (highest
processed message), `last_polled_at`. `feed_state` — per-source
conditional-GET validators (`etag`, `last_modified`) plus
`last_polled_at` for the web poller. Both are pure watermarks: losing
them costs re-examination, never data.

## Continuous-ingestion layer (2026-07-30; docs/continuous-ingestion.md)

`item_journal` — the intraday arrival journal, written by **post-cycle
reconciliation** (`WHERE NOT EXISTS` against the source tables), never
by the collection functions themselves. One row per (item, event) with
`event ∈ ingested/summarized/plain`; `observed_at` is
`COALESCE(extracted_texts.extracted_at, journaling time)` at cycle
granularity (one COALESCE, two arms — `documents.first_seen_at` is
deliberately not consulted) —
deliberately: dating rules key on claimed publication dates, and the
journal exists to timestamp the live `/today` view, not to assert
observation minutes. `digest_date` is the day the item belongs to under
GUIDE §3 dating rules. Indexed by `(digest_date, observed_at)`.

`collector_state` — one row per collector worker (`govinfo`, `email`,
`analyze`, `render`, `eod`, `host:<netloc>`): last cycle/ok timestamps,
`last_result` JSON, `consecutive_errors`, and six columns only the
EOD finalizer writes — `finalized_date`, `finalize_target`,
`finalize_attempts`, `evidence_pushed_at`, `evidence_push_error`,
`evidence_push_attempts`. The read surface for OPS-GUIDE.md and the
`/fapd-health` skill; a worker whose `consecutive_errors` grows or
whose `last_ok_at` goes stale is a finding.

**The finalized marker lives in `finalized_date`, its own column**
(2026-08-02, closing review D5 — the second half of the three-clock
incident). The first half was the no-op path: `run_cycle` stores
whatever `cycle()` returns, wholesale, as `last_result`, and a bare
`{"ran": false}` erased the JSON `finalized` key the reader depended
on — the full pipeline re-ran every ~20 minutes. The error path had
the identical hole (`record_state(ok=False)` also replaces the row),
so the marker moved to a column no `last_result` writer can touch.
`EODWorker.eod_due` reads the column first and falls back to the
JSON `finalized`/`date` keys only for rows written before the
migration. `last_result` remains a status line for humans; nothing
load-bearing reads it anymore.

`finalize_target` + `finalize_attempts` are the finalizer's hard-stop
ladder (same shape as `summary_attempts` / GUIDE §6 r14): failed
finalize attempts for one target day are counted, and at
`config.EOD_MAX_FINALIZE_ATTEMPTS` the day is loudly disclosed as
halted and not retried — a persistently failing day must not buy ~18
full pipeline runs per day forever. A new target day gets a fresh
ladder; a success clears it. `consecutive_errors` cannot serve as this
counter: the halt itself produces idle `ok=True` cycles, which reset
it.

`evidence_pushed_at` + `evidence_push_error` +
`evidence_push_attempts` are the same shape one step later: whether the
finalized day actually reached the repository. Finalizing and publishing
to git are separate gates and fail separately — on 2026-08-07 the digest
rendered, validated, and served all day while the evidence commit sat
rejected in the container (F-021). The failure was recorded only in
`last_result`, so the `eod` row read `finalize_attempts = 0`: a clean
success by every durable measure the system kept. These columns are the
durable measure. `evidence_pushed_at` stamps the last success;
`evidence_push_error` holds the failing exit reason and stays non-NULL
until a push succeeds; `evidence_push_attempts` bounds the retry at
`config.EVIDENCE_PUSH_MAX_ATTEMPTS`, after which the gap is loudly
disclosed rather than retried nightly against a fault that needs a
human. `finalized_date` is deliberately written even when the push
fails — the day IS finalized, and re-finalizing would re-render and
re-spend tokens for a day already paid for.

`source_assessments` — per-source model prose, layer one of the
2026-08-03 source-pages plan (GUIDE §3a source surfaces): append-only
history keyed `(source_id, prompt_version, generated_at)` with `model`,
`trigger_reason` (`initial` | `age-30d` | `health-change`), and the
`assessment` text — which was banned-lexicon-scanned BEFORE the insert;
a failing scan stores nothing. The page renders the newest row, labeled
model-derived with its date, model, version, and trigger.

`source_descriptions` — layer two: what the source IS. Keyed
`(source_id, prompt_version, registry_hash)` — `registry_hash` is the
sha256 of the source's registry entry, so an edited entry regenerates
its description and an untouched one never does (no timer). Carries
`summary` (1–2 sentences) and `description` (250–500 words), both
lexicon-scanned before insert, both rendered as a labeled model-written
orientation.

`source_health_state` — the persisted health label per source
(`source_id` PK, `label`, `since`, `last_checked`), maintained by the
health refresh. Exists so a label TRANSITION is detectable — the
assessment layer's `health-change` trigger — where the previous
render-time-only computation left no history.

`section_tags` — the LIVE tag table (2026-07-30, GUIDE §6 r12a): one
row per `(date, section_key, tag)` with `method ∈ mechanical/llm`;
mechanical branch/agency tags plus §3a-versioned model discovery keys
(`prompt_version`, `model` NULL for mechanical). Written by `tags.run`,
read by the digest's `Tags:` lines and /today's day-so-far chips.

`item_tags` — item-level auto-tagging, **schema-first** (the build is
ops-backlog OB-9's remainder): tags attach to items on the universal
`(package_id, granule_id)` key with `tag_kind ∈
branch/agency/discovery` and `method ∈ mechanical/llm`; the LLM
discovery keys carry `prompt_version` (a §3a-versioned surface) and
`model`, so model-derived tags are never mistakable for
source-provided data. Renderers join per item and aggregate to
section level.

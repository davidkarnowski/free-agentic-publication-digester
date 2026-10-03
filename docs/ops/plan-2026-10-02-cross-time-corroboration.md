# Plan — cross-time cross-source document corroboration (persisted)

*Follows docs/ops/plan-task-template.md. Amends GUIDE §3/§5, adds a
schema table (docs/schema.md is the authority), and adds a public note,
so it is a plan task.*
*Status: IMPLEMENTED 2026-10-02 (v3). Operator-approved; built on branch
`feature/cross-time-corroboration`, preflight green.*
*v2 change (operator): record the duplicate relationship in the DB —
link the entries to each other — rather than computing it only at render.*
*v3 (operator, 2026-10-02): metric chosen = word-shingle Jaccard (the
stored audit score) PLUS an overlap/containment guard — confirm iff
Jaccard ≥ 0.15 and overlap ≥ 0.45, thresholds set from the production
corpus (36 genuine FR↔PRESACT pairs: Jaccard 0.20–0.83, overlap
0.51–0.99; an unrelated collision scores Jaccard ≈ 0.10). The overlap
floor admits a truncated-but-contained duplicate that a symmetric metric
would miss; the implementation and its measured basis live in
`src/fapd/corroboration.py`.*

## Why

The same government document reaches us through more than one channel on
**different days** — e.g. an executive order appears in the White House
presidential-actions feed when signed, then in the Federal Register a few
days later. Today's `report.corroborate` de-duplicates only **same-day,
same-normalized-URL** observations, so these cross-day copies are
presented as two unrelated items. We want to **record** that the later
copy duplicates an earlier publication — as a stored fact, computed once,
programmatically, no inference — and reference it in the digest.

## Operator decisions — binding for this task

1. **Window: 30 days.** State publicly why a digest may reference a
   document first published on an earlier day (2026-10-02).
2. **Never suppress the entry.** The later copy is still listed — "what
   the government said today" is preserved — carrying a reference to the
   prior publication's **date** and **source**, rendered in the same
   style as today's same-day corroboration note (2026-10-02).
3. **Frozen days stay frozen.** The reference is recorded and shown on
   the day the later copy appears, on that day's entry, pointing back;
   the earlier, already-frozen day is never rewritten (2026-10-02).
4. **Secondary similarity confirmation.** A normalized-title match only
   makes a *candidate*; an extended, programmatic body-similarity check
   must confirm it before a link is recorded. It runs **only** as that
   second step, on candidates (2026-10-02).
5. **Record the relationship in the DB** (v2, 2026-10-02): duplicate
   publications from different sources are linked to each other as a
   stored fact, detected once; the render reads the stored link rather
   than re-deriving the match.
6. **Record the link in the daily manifest** (v2, 2026-10-02, operator):
   the corroboration link is part of the day's committed, hash-chained
   provenance — prior package/source/date and the similarity score — so
   the relationship is auditable in the evidence record, not only in the
   live DB.

## Data findings (prod DB, read-only, 2026-10-02)

- Presidential documents land in two channels: **PRESACT** (EO /
  PROCLAMATION, White House feeds) and **FR PRESDOCU** (Federal Register,
  govinfo). A normalized-title match links **46 of 90** PRESACT titles to
  an FR copy.
- Forward lag (FR after the web feed): **median 5 days**, bulk 3–6, thin
  tail to ~15, one 36-day outlier. 30 days covers it with margin.
- 10 "matches" had the FR date *earlier* (−8, −14): the 2026-08-06
  White House-feed activation welcome-batch. Detection must be
  **direction-aware** (link to an *earlier* publication) so backfill does
  not create spurious links.
- The America.gov and "Inaugurating the Era of Super Intelligence" EOs
  (2026-09-29 → FR 2026-10-02, gap 3) motivate this; the Fact Sheet / GSA
  release correctly do **not** title-match — no false positives in the
  sample.

## Scope

**Presidential documents first** (PRESACT EO/PROCLAMATION ↔ FR PRESDOCU):
the one class where the same document deterministically appears in both
channels with a stable official title; candidate set ~180 rows total.
Generalizes later (an indexed `title_key` makes the lookup an index seek).

## Architecture: detect once, store the link, read at render

1. **Detection runs once, in the mechanical pipeline** (zero-LLM), not at
   render. For each new presidential document of the day, look back 30
   days for a prior observation with the same `title_key` **from a
   different channel**, dated strictly earlier; confirm with the
   secondary body-similarity check; and **INSERT a corroboration link**
   (write-once). Cost: a title_key+date lookup over ~180 rows and a
   couple of body comparisons per presidential doc per day — negligible.
2. **The link is a stored fact** carrying the evidence (prior date,
   source, url, title_key, similarity score, detection time) — queryable,
   auditable, and stable across re-renders. **Every observation stays a
   distinct stored row** (GUIDE §3): nothing is merged or dropped; a
   relationship is *recorded between* them.
3. **Render reads the link.** `report.py` fetches the stored links for
   the day's entries and renders the "also published [date] by [source]"
   note — same display shape as the existing same-day corroboration
   (decision 2). The earlier frozen day is untouched (decision 3).

## Files

- `docs/schema.md` — define the new `corroborations` table (schema
  authority; precedes db.py).
- `src/fapd/db.py` — add that table to `_DDL` (`CREATE TABLE IF NOT
  EXISTS` — self-migrating, additive; CLAUDE.md §5).
- `src/fapd/corroboration.py` — **new module**: `_title_key`,
  `_same_document` (secondary check), `record_cross_source(conn, date,
  *, window_days=30)` (detect + write-once), `prior_links(conn,
  package_ids)` (read helper for render).
- `scripts/run_pipeline.py` / `src/fapd/finalize.py` — call
  `record_cross_source` in the mechanical stage, before render.
- `src/fapd/report.py` — read links via `prior_links`, attach
  `_prior_publication` to entries, render the note in the same-day style;
  `report.corroborate` (same-day URL) is unchanged.
- `src/fapd/provenance.py` (or the manifest builder) — include the day's
  corroboration links in the daily manifest (decision 6).
- `GUIDE.md` §3 (corroboration) and §5 (frozen days) — the amendment.
- `docs/site/methods.md` (or the coverage/about page `publish.py` renders)
  — the public "why we reference earlier days" note (decision 1).
- `tests/test_corroboration.py` (new) + `tests/test_report.py`,
  `tests/test_publish.py` — matcher, window edge, direction/backfill
  guard, secondary-check reject, write-once idempotence, frozen-day
  no-rewrite, render style across digest/live/day-view.

## Diff sketch

- **`corroborations` table** (docs/schema.md + db.py `_DDL`):
  ```
  CREATE TABLE IF NOT EXISTS corroborations (
    package_id        TEXT NOT NULL,            -- the later observation
    granule_id        TEXT NOT NULL DEFAULT '',
    prior_package_id  TEXT NOT NULL,            -- the earlier one it duplicates
    prior_granule_id  TEXT NOT NULL DEFAULT '',
    prior_collection  TEXT, prior_source TEXT,  -- for the display label
    prior_date        TEXT, prior_url TEXT,     -- for the reference
    title_key         TEXT NOT NULL,
    similarity        REAL,                     -- secondary-check score (audit)
    detected_at       TEXT NOT NULL,
    PRIMARY KEY (package_id, granule_id, prior_package_id, prior_granule_id)
  ) WITHOUT ROWID;
  CREATE INDEX IF NOT EXISTS idx_corroborations_pkg ON corroborations(package_id);
  ```
  Row direction is later→prior, so render fetches `WHERE package_id IN
  (the day's packages)` and never reads or writes the frozen earlier day.
- **`_title_key(title)`**: lowercase; strip a leading `Executive Order
  NNNNN[—:-]` prefix; drop non-alphanumerics; collapse whitespace. (Pure
  string; produced the 46 matches.)
- **`_same_document(a_text, b_text)`**: body similarity (candidate:
  word-shingle Jaccard, robust to formatting; or `difflib` ratio) ≥ a
  pinned threshold. Runs only on a title_key candidate.
- **`record_cross_source(conn, date, *, window_days=30)`**: for the day's
  presidential docs, find earlier same-`title_key` rows from another
  channel within the window, confirm with `_same_document`, `INSERT OR
  IGNORE` the link. Idempotent.
- **render**: `prior_links` → `entry["_prior_publication"]`; note shaped
  like `_corroborators` at report.py ~L788; entry kept, never suppressed.
- **GUIDE §3**: record cross-source duplicate publications as stored
  corroboration links (not a merge — observations stay distinct),
  detected once, mechanical, direction-aware 30-day window,
  secondary-confirmed. **§5**: the link is recorded/shown on the later
  day only; frozen days are not rewritten.
- **Public note**: one paragraph on the methods/coverage page (decision 1).

## Justification

- **Persisted link, detected once** (decision 5) — the relationship is a
  provenance fact (with its similarity evidence), computed a single time
  in the mechanical pipeline, cheap to read, stable across re-renders and
  across a matcher change. Querying cross-source duplication becomes
  possible (how often, which sources, what lag).
- **Still GUIDE §3-compatible** — "every observation stays stored" holds;
  we add a relationship between rows, we do not merge or drop them.
- **Two-stage matcher** — cheap title_key candidate + secondary body
  check removes the only key-only failure mode (same title, different
  doc), per decision 4.
- **Scoped to presidential docs** — deterministic; avoids false positives
  from title-matching high-volume classes.

## Alternatives considered

- **Presentation-layer only (v1)** — rejected by the operator (decision
  5): the relationship should be a recorded fact, not re-derived each
  render.
- **Persisted indexed `title_key` column on `extracted_texts`** — the
  generalization path (agency→FR); deferred, since the scoped set is tiny
  and `record_cross_source` can `_title_key` on the fly for now.
- **EO-number as the key** — deterministic but not always present at
  web-publication time; a possible high-confidence augment, not primary.
- **Suppressing the later copy** — rejected (decision 2).
- **LLM/embedding similarity** — rejected by constraint (no inference).

## Risk / blast radius

- Schema add is additive/self-migrating (`IF NOT EXISTS`); no destructive
  migration. The table starts empty; absent links change nothing.
- Coincidental `title_key` collision → the body check is the guard;
  threshold pinned by fixtures.
- Direction bug re-linking the activation backfill → "earlier only" rule
  + a backfill fixture.
- Detection-timing: must run after extraction, before render, in the
  mechanical (zero-LLM) stage; a re-finalize must not duplicate links
  (`INSERT OR IGNORE`, pinned).
- Render regression across the three surfaces → `test_report.py`,
  `test_publish.py`, `test_accessibility` (note markup).
- Provenance: the link is recorded in the daily manifest (decision 6),
  so a manifest-shape test must cover the new field and the hash chain
  must stay stable for a day with no links (back-compat).

## Verification

- `uv run pytest -q tests/test_corroboration.py tests/test_report.py tests/test_publish.py` green.
- Re-render 2026-10-02 (`scripts/digest.py --date 2026-10-02`): the
  America.gov / Super Intelligence FR entries carry a stored
  "also published 2026-09-29 (White House)" reference; the 2026-09-29
  digest is byte-unchanged; a `corroborations` row exists for each.
- `scripts/preflight.sh` green before merge.

## Rollback

Additive only: stop calling `record_cross_source` and revert the render
read; the `corroborations` table can be left in place (unused) or dropped
by a deliberate one-shot script. No data loss — every observation row is
untouched.

## Dependencies

None. Independent of the email adapter abstraction task.

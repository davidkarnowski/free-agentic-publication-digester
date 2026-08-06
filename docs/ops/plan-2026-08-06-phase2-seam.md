# P2 — switch the filing seam to `digest_day`

**Files:** `src/fapd/rules.py`, `src/fapd/report.py`,
`src/fapd/compose.py`, `src/fapd/collect.py`.

Every change is `p.date_issued = ?` → `p.digest_day = ?` (params
unchanged). Exact sites:

1. `rules._ROWS_SQL` (rules.py:171-178) — the WHERE clause. This
   redirects selection (`select_items`, `exclusion_counts`) and the
   collector's `pending_map_items` (collect.py:122) in one edit.
2. `report._load_items` (report.py:193-216) — `AND p.date_issued = ?`.
3. `report._crec_lines` issue-size count (report.py:932-938).
4. `report._crec_lines` unselected-by-doctype query (report.py:939-953).
5. `report._coverage` — every per-collection query that filters
   `p.date_issued = ?` (report.py:278-301 region and the sibling
   collection blocks; grep `date_issued` within `_coverage`).
6. `compose_day` staleness subquery (compose.py:61-84):
   `WHERE p.date_issued = ?` → `p.digest_day = ?`.
7. `compose_sections` staleness subquery (compose.py:216-237): same.
8. `collect.journal_new` (collect.py:45-70): journal `digest_date`
   currently `p.date_issued` (line 56) → `p.digest_day` — /today and
   day views then agree with the digest.

**Do NOT touch:** watermarks (`sync_state`), USCOURTS-FETCH-01 window
(`_apply_fetch_policy`, sync.py:172-189 — fetch policy keys on
`date_issued` correctly), AGENCYPR display paths (digest_day equals
date_issued there, so the seam is uniform).

**Also in this phase:** delete the duplicated constant
`report.CREC_FLOOR_THRESHOLD_CHARS` (report.py:73); import
`rules.CREC_FLOOR_CHAR_THRESHOLD` at its two use sites (F-015 note).

**Verify:** full suite — expect failures ONLY in tests that seed
packages without `digest_day`; fix in P4, not by weakening queries.
**Rollback:** revert the commit; P1's column stays, harmless.

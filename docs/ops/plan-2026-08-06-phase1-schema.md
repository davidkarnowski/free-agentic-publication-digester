# P1 — `packages.digest_day`: schema, insert policy, backfill

**Files:** `docs/schema.md`, `src/fapd/db.py`, `src/fapd/config.py`,
`src/fapd/sync.py`, `src/fapd/agencies.py` + `src/fapd/email_sources.py`
(locate their package inserts), `scripts/migrate_digest_day.py` (new).

**1. docs/schema.md** (design authority, edit FIRST): document
`packages.digest_day TEXT` — "the digest day this package files under;
write-once at first sight; observation-filed collections =
`publication_date_of(first_seen_at)`, cover-filed (FR, AGENCYPR) =
`date_issued`; pre-cutover rows backfilled = `date_issued`."

**2. db.py** — add to `_DDL`'s packages CREATE (after `first_seen_at`,
db.py:24): `digest_day TEXT,` AND to the `_ensure_columns` call at
db.py:342 add `"digest_day": "TEXT"` under a packages entry (create
one — currently only collector_state is ensured):
```python
_ensure_columns(conn, "packages", {"digest_day": "TEXT"})
```

**3. config.py** — near the collection constants:
```python
# GUIDE §3 (amended 2026-08-06): per-collection filing policy.
# "observation" files under the Eastern day of first observation;
# "cover" files under the document's own date_issued.
FILING_POLICY = {"FR": "cover", "AGENCYPR": "cover"}
FILING_DEFAULT = "observation"
```

**4. sync.py `_upsert_package`** (sync.py:146-169) — compute and insert
`digest_day`; the ON CONFLICT clause deliberately DOES NOT update it
(write-once for free):
```python
def _upsert_package(conn, collection, pkg):
    now = utc_now_iso()
    policy = config.FILING_POLICY.get(collection, config.FILING_DEFAULT)
    digest_day = (pkg.get("dateIssued") if policy == "cover"
                  else publication_date_of(now)) or publication_date_of(now)
    conn.execute(
        """
        INSERT INTO packages (package_id, collection, last_modified, title,
                              package_link, date_issued, first_seen_at,
                              digest_day)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(package_id) DO UPDATE SET
            ... (existing clauses unchanged — digest_day absent on purpose)
        """,
        (..., now, digest_day))
```
(`publication_date_of` is already in sync.py:66.)

**5. AGENCYPR inserts** — grep `INSERT INTO packages` in
`agencies.py`/`email_sources.py`; set `digest_day = date_issued`
(agency-stated day — semantics unchanged). If they build packages via a
shared helper, route through it once.

**6. scripts/migrate_digest_day.py** (one-shot, committed, idempotent):
```python
"""Cutover backfill (GUIDE §3 amended 2026-08-06): rows first seen
before the cutover keep cover-date filing so frozen digests reproduce."""
n = conn.execute(
    "UPDATE packages SET digest_day ="
    "  COALESCE(date_issued, substr(first_seen_at, 1, 10))"
    " WHERE digest_day IS NULL").rowcount
```
Print rowcount + a verification SELECT (count of NULL digest_day == 0).

**Verify:** `uv run pytest -q`; fresh-DB connect self-migrates; script
run twice → second run updates 0 rows. **Rollback:** column is
additive/inert until P2 lands; revert commits.

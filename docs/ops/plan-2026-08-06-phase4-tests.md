# P4 — tests

**Files:** `tests/conftest.py`, `tests/test_report.py`,
`tests/test_rules.py`, `tests/test_sync.py`, `tests/test_collect.py`,
`tests/test_compose.py` (wherever fixture packages are inserted —
grep `INSERT INTO packages` under tests/).

1. Fixture inserts gain `digest_day` = `date_issued` by default (one
   conftest helper if none exists), keeping the existing 607 green
   and meaningful.
2. New tests:
   - `test_sync.py`: a new CREC package observed on D gets
     `digest_day = D` while `date_issued = D-1`; an FR package gets
     `digest_day = date_issued`; a re-sync with newer `lastModified`
     does NOT move `digest_day` (write-once).
   - `test_rules.py`/`test_report.py`: a CREC package with
     `date_issued = D-1, digest_day = D` is selected, summarized-
     fixture rows render in D's §1 with "covering proceedings of D-1";
     D-1's render does NOT include it; §1 empty state renders the
     honest sentence, not "0 granule(s)".
   - `test_report.py`: mixed day (CREC observed + FR cover-dated)
     passes `_validate_coverage`.
   - `test_collect.py`: `journal_new` writes `digest_date =
     digest_day`.
   - migration script: run twice on a seeded temp DB → idempotent,
     zero NULLs.
3. `uv run pytest -q` + `uv run ruff check src/ scripts/ tests/`.

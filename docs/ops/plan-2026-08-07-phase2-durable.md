# P2 — a failed evidence push becomes durable, loud, and retried

**Files:** `docs/schema.md` (design authority, edit FIRST), `src/fapd/db.py`,
`src/fapd/config.py`, `src/fapd/collect.py`, `tests/test_collect.py`.

## Why

On 2026-08-07 the push failed and **nothing recorded it**. The observed `eod`
row read `finalized_date='2026-08-06'`, `finalize_target=NULL`,
`finalize_attempts=0` — a clean success by every durable measure. The only
trace was `pushed: false`, which `EODWorker.cycle` returns into
`collector_state.last_result`, and CLAUDE.md §9 says plainly: *`last_result`
is a status line; durable facts get their own column.* This is the same defect
shape as the EOD marker that caused 35 duplicate evidence commits on
2026-08-01 (review D5).

Worse, it never retries: `eod_due()` (`collect.py:536`) returns `None` once
`finalized_date` is set, so the next attempt is tomorrow's EOD — which fails
identically, forever, until a deploy.

## Diff sketch

**1. `docs/schema.md`** (the schema's design authority; `db.py` implements it,
not the reverse). Document three additions to `collector_state`, `'eod'` row
only, beside the existing finalize ladder:

- `evidence_pushed_at TEXT` — UTC stamp of the last successful evidence push
- `evidence_push_error TEXT` — last failure detail; `NULL` when clean
- `evidence_push_attempts INTEGER NOT NULL DEFAULT 0` — per-pending-commit
  retry ladder

**2. `db.py`** — extend the existing `_ensure_columns` call at `db.py:343`
(additions are self-migrating; destructive changes are one-shot scripts,
never startup DDL — CLAUDE.md §5). Add the same three names to the
`collector_state` CREATE inside `_DDL` (`db.py:275-284`) so a fresh database
and a migrated one agree, and extend that table's block comment:

```python
_ensure_columns(conn, "collector_state", {
    "finalized_date": "TEXT",
    "finalize_target": "TEXT",
    "finalize_attempts": "INTEGER NOT NULL DEFAULT 0",
    "evidence_pushed_at": "TEXT",
    "evidence_push_error": "TEXT",
    "evidence_push_attempts": "INTEGER NOT NULL DEFAULT 0",
})
```

**3. `config.py`** — beside `EOD_MAX_FINALIZE_ATTEMPTS` (`config.py:286`).
Constants are policy (GUIDE §4), so comment the reasoning, not the number:

```python
# Bounded retry for a failing evidence push (2026-08-07, F-021), same shape
# as EOD_MAX_FINALIZE_ATTEMPTS. A push failure is usually transient (GitHub
# unreachable) or structural (the box diverged from origin). Retrying every
# EOD cycle heals the first within minutes; the second needs a human, so the
# ladder ends and says so instead of hammering the remote nightly. The
# digest is already live either way — this ladder governs publication to the
# repository, never the record itself.
EVIDENCE_PUSH_MAX_ATTEMPTS = 3
```

**4. `collect.py` — `EODWorker`.** Three changes:

*(a) A durable recorder*, modelled on `_record_finalized` (`collect.py:579`)
and `_record_finalize_failure` — writing columns `record_state` never touches,
so an error or idle cycle replacing `last_result` cannot erase them:

```python
def _record_evidence_push(self, conn, ok, error=None):
    """Durable evidence-push state. Success clears the ladder; failure
    advances it and keeps the error visible until a push succeeds."""
    if ok:
        conn.execute(
            "UPDATE collector_state SET evidence_pushed_at = ?,"
            " evidence_push_error = NULL, evidence_push_attempts = 0"
            " WHERE worker = 'eod'", (utc_now_iso(),))
    else:
        conn.execute(
            "UPDATE collector_state SET evidence_push_error = ?,"
            " evidence_push_attempts = evidence_push_attempts + 1"
            " WHERE worker = 'eod'", (error,))
    conn.commit()
```

*(b) Record and shout on the existing push call* (`collect.py:635-637`).
`_record_finalized` stays **unconditional on push success** — the day *is*
finalized: the digest was rendered, validated and served. Re-finalizing would
re-render and re-spend tokens. Finalization and publication-to-repo are
separate concerns and must stay decoupled:

```python
if exit_code == 0 and config.EVIDENCE_PUSH:
    rc = self.sup.evidence_runner()
    pushed = rc == 0
    self._record_evidence_push(conn, pushed, None if pushed else f"exit {rc}")
    if not pushed:
        logger.error(
            "EVIDENCE PUSH FAILED for %s (exit %s) — the digest is LIVE on"
            " the site but the repository does not have it. The commit is in"
            " the container's writable layer; a rebuild DESTROYS it. Fix,"
            " then re-run deploy/vps/scripts/evidence-commit.sh.", target, rc)
```

*(c) Retry on later cycles.* `cycle()` currently returns
`{"ran": False, ...}` as soon as `eod_due()` yields `None`
(`collect.py:627-629`). Insert a branch before that return: when the day is
finalized but a push is still pending and the ladder has room, re-run the
evidence runner on this cycle. A transient outage then heals in one EOD
interval instead of a day:

```python
if not target:
    return self._retry_pending_push(conn, finalized)
```

`_retry_pending_push` reads `evidence_push_error` / `evidence_push_attempts`,
returns `{"ran": False, "finalized": finalized}` unchanged when there is
nothing pending or `config.EVIDENCE_PUSH` is off, and on ladder exhaustion
emits the loud disclosure the hard stop owes (GUIDE §2, no silent omission) —
mirroring the finalizer's "HALTED … will NOT be retried" language, logged once
at exhaustion rather than on every idle check.

**5. `tests/test_collect.py`** — the `EODWorker` seam and a fake
`sup.evidence_runner` already exist (see the block at `test_collect.py:284`):

- a failed push records `evidence_push_error` and does not clear it
- `finalized_date` is still written when the push fails
- a finalized day with a pending push retries on the next cycle
- retries stop at `EVIDENCE_PUSH_MAX_ATTEMPTS` and log the halt
- a successful push sets `evidence_pushed_at`, clears the error, zeroes attempts
- `FAPD_EVIDENCE_PUSH` unset still never invokes the runner — the existing
  guarantee at `test_collect.py:363` must not regress
- the retry branch never fires a *finalizer* run (it must push only)

## Justification

Three columns, not one JSON blob: CLAUDE.md §9 names `last_result` as the
anti-pattern by name, and the finalize ladder next door already demonstrates
the intended shape. `evidence_push_attempts` is separate from
`finalize_attempts` because they bound different things — one a full pipeline
run, the other a git push — and collapsing them would make a push failure
consume the finalizer's hard stop.

The retry lives in `EODWorker` rather than a new worker because the evidence
push is already its responsibility and the pause/serialization contract
(docs §7) is already established there.

## Alternatives considered

- **Re-run the whole finalizer on push failure** — rejected: re-renders and
  re-spends tokens for a day already paid for, and risks a second evidence
  commit for the same day (the 2026-08-01 failure mode).
- **Fail the EOD cycle on push failure** (raise, advancing `finalize_attempts`)
  — rejected: it would mark a *successfully finalized* day as failed and
  eventually halt finalization for a fault that is purely about publication.
- **Alert by email** — no alerting channel exists; adding one is a larger
  decision than this repair, and `docker logs` plus the durable column are
  what the OPS-GUIDE check in P5 reads.
- **One `evidence_push_state` JSON column** — the exact pattern §9 forbids.

## Risk / blast radius

Additive schema on a WAL database with concurrent readers — safe, and the
established path. The retry branch runs inside the EOD worker's normal cycle,
which already holds `pause_event`; it must not fire a finalizer run, hence
the explicit test. Worst plausible bug is a retry loop, bounded by
`EVIDENCE_PUSH_MAX_ATTEMPTS`.

## Verification

```sh
uv run pytest -q tests/test_collect.py tests/test_db.py
uv run ruff check src/ scripts/ tests/
# on the box after deploy
sudo docker exec fapd-backend python -c "
import sqlite3; c=sqlite3.connect('file:/app/data/fapd.db?mode=ro',uri=True)
print(dict(zip([d[0] for d in c.execute('SELECT * FROM collector_state WHERE worker=\"eod\"').description],
               c.execute('SELECT * FROM collector_state WHERE worker=\"eod\"').fetchone())))"
```

Expect `evidence_pushed_at` set and `evidence_push_error` NULL after the
2026-08-08 EOD.

## Rollback

Revert the code. The added columns are harmless if left in place — nothing
reads them once the code is gone, and dropping columns is a destructive
migration this project does not do at startup.

## Dependencies

Independent of P1 and P4, but P1 is what makes the recorded state *usually
green* — landing P2 alone would faithfully record a nightly failure.

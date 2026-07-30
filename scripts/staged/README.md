# Staged production scripts

The pattern for any production write (AGENT-VPS-SERVICING-GUIDE §2):
a self-contained bash script — **preconditions that abort before any
change** → backup/rollback artifacts → the change → self-verification →
explicit `SUCCESS:` / `FAILURE:` verdict, non-zero exit on failure.
`scp` to the box, run once, keep forever.

- Naming: `YYYY-MM-DD-<action>.sh`.
- Scripts here are **records** — never deleted, never edited after
  running (a follow-up is a new script).
- The value is the preconditions, rollback artifacts, and
  self-verification — not classifier avoidance or ceremony.

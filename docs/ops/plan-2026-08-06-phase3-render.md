# P3 — three-clock renderings + honest empty states

**Files:** `src/fapd/report.py`, `src/fapd/compose.py`,
`src/fapd/config.py`, `digests/TEMPLATE.md` if headers are mirrored
there.

1. **§1 source line** (report.py:965-968). The CREC issue(s) for the
   digest day are those with `digest_day = date`; their `date_issued`
   is the proceedings date. New form (one line per issue present):
   `Source: Congressional Record (CREC), issue observed {date},
   covering proceedings of {date_issued}. Published by govinfo
   {last_modified}. Total issue size: {total} granule(s).`
   Empty state (no CREC package with `digest_day = date`): `No
   Congressional Record issue was observed on this day. The Record for
   a day's proceedings is typically published by govinfo the following
   morning; it will appear in the digest for the day it is observed.`
   — never a bare zero. (Subsumes F-013's disclosure floor.)
2. **Item lines** (§1/§2/§5): where an item's `date_issued` differs
   from the digest day, append a mechanical clause: `(document dated
   {date_issued})`. Implement once in the shared item-line helper in
   report.py, not per-section.
3. **§5 USCOURTS disclosure** — reword: opinions appear in the digest
   of the day they are observed; each carries its issue date; the
   participation caveat stays.
4. **Coverage Statement** — "packages observed this day" wording; the
   `_validate_coverage` identity (report.py:1624-1659) already
   recomputes from the P2 queries, so the gate stays exact.
5. **Methodology section** — dated cutover note (operator-approved
   forward-only text from the plan index).
6. **Compose prompt** (compose.py `_PROMPT`): add the instruction that
   counts are of documents observed this digest day and documents may
   carry earlier dates — state them as observations, never as "N were
   issued today". Bump `COMPOSE_PROMPT_VERSION` in config.py (§3a
   step 2; day/section synthesis regenerates itself via the staleness
   checks — regeneration scope goes in the WORKLOG entry per step 3).

**Verify:** render 2026-08-04 from the local DB — must still produce
the frozen digest's numbers (cutover reproducibility); render a
fixture day with a late CREC → populated §1 with three clocks.
**Rollback:** revert; prompt-version bump is additive (old layer rows
remain keyed).

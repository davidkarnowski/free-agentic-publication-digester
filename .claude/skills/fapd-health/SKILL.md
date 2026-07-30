---
name: fapd-health
description: Read-only health check of the FAPD pipeline and site — digest freshness, request budgets, token spend, validation, collector liveness, VPS containers. Invoke when the user says /fapd-health or asks "is everything ok", "check the pipeline", "how fresh is the digest", or after any deploy.
---

# FAPD — health check (read-only)

The runbook is `docs/ops/OPS-GUIDE.md` — read it first; it is the
source of truth. This skill never writes or restarts anything.

## Preconditions
- Repo root; `data/fapd.db` exists for local checks.
- For VPS checks: key loaded (`ssh-add -l`), access facts from the
  operator's private dossier (pointer in `docs/ops/SERVER-GUIDE.md`).

## What to do when invoked
1. Run the OPS-GUIDE **local** block: digest freshness, `scripts/audit.py`
   budget posture, ledger spend by purpose/backend.
2. If collectors exist: read `collector_state` (any
   `consecutive_errors > 0` or stale `last_ok_at` is a finding).
3. If asked about the VPS or after a deploy: the OPS-GUIDE **VPS**
   block (curl 200s, container statuses, fapd-web networks ==
   `fapd_edge` only, cert expiry).
4. **Verify/report**: state each check's actual observed value against
   its expectation; flag anomalies — never summarize unchecked items as
   fine.

## Notes
- After a deploy, run again ~5 minutes later (cadence rule).
- Budget lines near caps are a finding even when nothing failed
  (backpressure/headroom, GUIDE §4).

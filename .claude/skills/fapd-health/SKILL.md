---
name: fapd-health
description: Read-only health check of the FAPD pipeline and site — digest freshness, request budgets, token spend, validation, collector liveness, evidence-push state, VPS containers. Invoke when the user says /fapd-health or asks "is everything ok", "check the pipeline", "how fresh is the digest", or after any deploy.
---

# FAPD — health check (read-only)

The runbook is `docs/ops/OPS-GUIDE.md` — read it first; it is the
source of truth. This skill never writes or restarts anything.

## Preconditions
- Repo root; `data/fapd.db` exists for local checks.
- For VPS checks: key loaded (`ssh-add -l`), and `deploy/vps/deploy.env`
  present (gitignored — copy `deploy.env.example`, `chmod 0600`). Every
  remote command runs through `deploy/vps/scripts/vps-ssh.sh '<cmd>'`,
  which resolves coordinates itself. **Never read connection facts from
  another project's tree.**

## What to do when invoked
1. Run the OPS-GUIDE **local** block: digest freshness, `scripts/audit.py`
   budget posture, ledger spend by purpose/backend. **Say plainly whether
   this machine runs the pipeline.** On a machine that does not, this
   block describes a development database and says nothing about
   production — on 2026-08-07 the operator's local DB was seven days
   stale while production ran normally.
2. If collectors exist: read `collector_state` (any
   `consecutive_errors > 0` or stale `last_ok_at` is a finding).
3. **Did the evidence reach the repository?** Run the OPS-GUIDE
   evidence-push check. `origin/main..HEAD` must be 0, and the `eod` row
   must show `evidence_push_error` NULL. **A digest that is live on the
   site but absent from `origin/main` is a finding, not a pass** — those
   are two separate gates and they fail separately (F-021).
4. If asked about the VPS or after a deploy: the OPS-GUIDE **VPS**
   block (curl 200s, container statuses, fapd-web networks ==
   `fapd_edge` only, cert expiry).
5. **Verify/report**: state each check's actual observed value against
   its expectation; flag anomalies — never summarize unchecked items as
   fine. If a check could not run, say so and why; an unrunnable check
   is not a passing one.

## Notes
- After a deploy, run again ~5 minutes later (cadence rule).
- Budget lines near caps are a finding even when nothing failed
  (backpressure/headroom, GUIDE §4).
- A freshly recreated container has an empty `known_hosts`; any command
  that talks to GitHub needs `StrictHostKeyChecking=accept-new` or it
  fails in a way that looks like a credential fault and is not.

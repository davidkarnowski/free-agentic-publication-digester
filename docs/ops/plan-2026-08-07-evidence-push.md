# Plan 2026-08-07 — repair the EOD evidence push and remove its blockers

*Plan-task shape per [plan-task-template.md](plan-task-template.md).
Touches production and a governing file (CLAUDE.md), so the operator
authorization gate in
[AGENT-VPS-SERVICING-GUIDE.md](AGENT-VPS-SERVICING-GUIDE.md) §0 applies to
every phase that reaches the box (P0, P5-deploy). Approved by the operator
2026-08-07.*

## Why

The 2026-08-07 overnight EOD cycle **succeeded** — digest 2026-08-06 is live
on fapd.info with all nine sections, a composed Day in Review, a frozen day
view, and an intact coverage statement; collectors are healthy and budgets sit
at 45% (govinfo) / 38% (agency). What failed is the last step: the evidence
commit never reached GitHub, and the failure is invisible, unretried, and one
`docker compose build` away from destroying a day of the public record.

## What was actually observed (read-only, 2026-08-07 ~17:00 UTC)

| Fact | Evidence |
|---|---|
| The commit exists | `36ae3b9 Daily pipeline evidence 2026-08-07 (automated)` — 168 files, incl. `digests/2026-08-06.md`, `provenance/manifests/2026-08-07.jsonl`, `provenance/runs/insight-2026-08-06.md`, `site/day/2026-08-06.{html,json}` |
| The push was rejected | `! [rejected] main -> main (fetch first)` in `docker logs fapd-backend` |
| Root cause | The box's `.git` is an rsynced snapshot of the laptop tree baked into the image (`Dockerfile.backend`: `COPY repo/ /app`). It **never fetches**. Box HEAD `50095fc`; origin advanced to `f9dd68c` after the deploy → non-fast-forward, permanently, until the next deploy |
| The key is fine | `git ls-remote origin main` over `/app/secrets/deploy_key` returns `f9dd68c` — fetch works; only the ordering was wrong |
| The rebase is clean | `f9dd68c` added **only** `scripts/staged/2026-08-07-repair-presact-journal-class.sh` — zero path overlap with the evidence commit |
| The evidence is ephemeral | `docker inspect` mounts are exactly `/app/data`, `/app/site`, `/app/secrets`. `/app/digests`, `/app/provenance` and `/app/.git` live in the container's writable layer (90.4 MB) |
| The failure is silent | `collect.py:636` puts the result in `pushed`, which lands in `collector_state.last_result` — which nothing load-bearing reads (CLAUDE.md §9). Observed row: `finalized_date='2026-08-06'`, `finalize_target=NULL`, `finalize_attempts=0` — the EOD ladder considers the night a clean success |
| It will not retry | `eod_due()` returns `None` once `finalized_date` is set, so the next attempt is tomorrow's EOD — which fails identically |

Everything else on the box verified healthy the same session: `fapd-backend`
and `fapd-web` up and healthy, `fapd-web` on exactly `fapd_edge`, disk 47%,
27 workers with zero consecutive errors.

## Intended outcome

The evidence commit lands every night; a failure is durable, loud, and
retried; the evidence survives a container rebuild; and any agent can run the
VPS half of `/fapd-health` from inside this project without reaching into a
sibling repository.

## Operator decisions taken 2026-08-07

1. Recover `36ae3b9` by rebasing and pushing **in-container** (preserves bot
   authorship and rehearses the permanent fix).
2. Add named volumes for `digests/` and `provenance/`.
3. Connection facts: **gitignored plaintext in-project**, plus a guard test.

## Phases

| Phase | File | Scope | Gate |
|---|---|---|---|
| P0 | [phase0-recover](plan-2026-08-07-phase0-recover.md) | Recover the 2026-08-06 evidence commit | **operator-gated (box write)** |
| P1 | [phase1-rebase](plan-2026-08-07-phase1-rebase.md) | `evidence-commit.sh` fetches and rebases before pushing | local code |
| P2 | [phase2-durable](plan-2026-08-07-phase2-durable.md) | Durable push state, loud failure, bounded retry | local code |
| P3 | [phase3-volumes](plan-2026-08-07-phase3-volumes.md) | `digests/` + `provenance/` as named volumes | local code, **needs P0 first** |
| P4 | [phase4-access](plan-2026-08-07-phase4-access.md) | In-project VPS coordinates + `vps-ssh.sh` + guard test | local code |
| P5 | [phase5-docs](plan-2026-08-07-phase5-docs.md) | Runbooks, findings, backlog, CLAUDE.md, WORKLOG, deploy | **operator-gated (deploy)** |

## Dependency order

**P0 must land before P3.** Docker seeds a new named volume from the **image**,
not from the running container's writable layer — creating the `digests`
volume while `36ae3b9` is still unpushed destroys 2026-08-06 permanently.

P1, P2 and P4 are independent of each other and may be worked in parallel
(all three are Operations-section work, `docs/agents/operations.md`). P5
depends on all of them. Section agents stage and report; only the
orchestrator commits (`docs/agents/orchestration.md`).

## Risk / blast radius, whole-plan

- P0 touches a live production container's git state. Bounded by a backup
  branch and a host-side file copy taken before any write; the push itself is
  additive (a new commit on `main`).
- P2 adds columns to `collector_state` via the existing self-migrating
  `_ensure_columns` path — additive, no destructive DDL (CLAUDE.md §5).
- P3 changes the container's storage shape and **extends the F-009
  stale-output class** to two more paths; disclosed, not silently accepted.
- P4 introduces a file holding server coordinates inside the working tree.
  The guard test is the control, and it must cover both rsync exclude lists,
  or the coordinates bake into a published container image.

## Verification, whole-plan

```sh
uv run ruff check src/ scripts/ tests/
uv run pytest -q
uv run pytest -q tests/test_dev_stack.py      # compose parity did not drift
git check-ignore -v deploy/vps/deploy.env
deploy/dev/scripts/dev-up.sh                  # prod image on a VPS seed (advisory)
```

End to end: the 2026-08-08 EOD run pushes unaided, and `collector_state`
shows `evidence_pushed_at` set with `evidence_push_error` NULL.

## Rollback, whole-plan

Every phase is independently revertable. P0's rollback is the backup branch;
P1–P4 are ordinary code reverts; P3 additionally requires
`docker volume rm fapd_fapd-digests fapd_fapd-provenance` **only after**
confirming the contents are pushed.

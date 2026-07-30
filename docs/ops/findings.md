# Findings register

*Stable-ID register of defects and risks found in reviews, sweeps, and
incidents. IDs are immutable and sequential (`F-001`, `F-002`, …);
severity is a column, not part of the ID. **Update `Status` in place —
never delete a row**; resolved findings keep their history. New
findings get the next ID.*

| ID | Sev | Area | Finding | Status |
|---|---|---|---|---|
| F-001 | low | repo hygiene | `.claude/` was wholly gitignored, so skills could not be tracked; split into `.claude/*` + `!.claude/skills/` (settings.local.json stays local — it's a permission allowlist). | resolved 2026-07-30 (standards push) |
| F-002 | info | deploy | `docker compose up -d` does not recreate a container whose only change is a single-file bind mount's content (new inode after rsync) — stage-B config silently not applied on first deploy. Convention: `--force-recreate <service>` for config-only deploys. | resolved 2026-07-30 (recorded in servicing guide §3 and the cohabitant bundle's README) |
| F-003 | low | corroboration | ~180 captures from 2026-07-28 lack a Wayback second witness; 31/37 Wayback submissions blocked on 2026-07-30 (their throttling). | open → tracked as OB-5 |
| F-004 | high | deploy | deploy.sh's bundle rsync ran `--delete` without excluding the box-only paths — it deleted the VPS `.env` on first real run (the deploy key survived only because root-owned `secrets/` was unreadable, which also aborted further deletions). Excludes added and marked load-bearing; `.env` re-provisioned. The sibling project's guide warned about exactly this. | resolved 2026-07-30 |

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
| F-005 | low | collect | First-boot race: parallel workers each attempt the fetch-log `client`-column ALTER on a fresh DB — losers get `duplicate column name` (contained, self-heals next cycle). Guard the ALTER with a caught exception. | open |
| F-006 | med | collect | The EOD pause stops *new* collector cycles but does not drain in-flight ones — the finalizer overlaps whatever was already running (safe under WAL/budgets, but the docs §7 serialization promise is only half-kept). Add a busy-flag drain wait. | open |
| F-007 | low | politeness | Each worker cycle constructs a fresh AgencyClient, so robots.txt is re-fetched per host per cycle (~half the agency-class request spend). Cache robots per worker or reuse the client across cycles. | open |
| F-008 | high | deploy | The baked repo's origin remote is HTTPS, so container evidence pushes cannot authenticate — accidentally safe for the experimental phase (no push can clobber canonical history), but OB-11 must flip it to SSH deliberately, together with state seeding, before pushes are enabled for real. | open → OB-11 |
| F-009 | low | deploy | Named-volume seeding is first-mount-only: rebuilding the backend image does not refresh the fapd-site volume, so presentation changes deployed mid-day stayed invisible until an in-container build_site ran. deploy.sh now rebuilds the site in-container post-up. | resolved 2026-07-30 |

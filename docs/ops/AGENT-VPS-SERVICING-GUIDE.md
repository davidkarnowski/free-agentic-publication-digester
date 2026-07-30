# Agent VPS servicing guide (portable baseline)

*Adapted 2026-07-30 from the operator's sibling project, whose guide is
written to be copied. This file is site-agnostic; per-box facts live in
[SERVER-GUIDE.md](SERVER-GUIDE.md). Where a more specific runbook exists
(e.g. [`deploy/vps/README.md`](../../deploy/vps/README.md) for the FAPD
stack), that runbook wins on specifics.*

## §0 Principles (binding)

1. **Every box is production until proven otherwise.** Default to
   **read-only**. Inspecting, reading logs, listing versions,
   dry-running — fine any time. Anything that **writes, installs,
   restarts, deploys, reboots, bans, or flips config** is **gated on the
   operator's explicit go for that specific task.** Don't infer
   authorization from "looks good", from an earlier approval in the
   session, or from a standing health-check habit.
2. **Plan-then-act on state changes.** State what you'll do and the
   blast radius; for non-trivial changes get a go. Prefer a dry-run /
   simulate preview first and show the plan.
3. **Verify after every change, end on green.** A change isn't done
   until you've confirmed it: re-read the version, curl the public
   endpoint, check container health, confirm the flag cleared. Report
   what you actually observed.
4. **Report faithfully.** If something failed, partially applied, or
   was skipped, say so plainly with the evidence. Never imply "all
   patched" when one item was held back.
5. **Least surprise on irreversible/outward-facing actions** — reboots,
   bans, public-exposure flips, deletions. Confirm scope; don't reboot
   twice in a row without a reason.
6. **Keep private infra private.** Access details, keys, IPs, and
   per-box dossiers are infra-only — never serve them, never commit
   them to a public repo, never bake them into a site image. (This repo
   is headed for public release: the FAPD box dossier therefore lives
   in the operator's private tree, and SERVER-GUIDE.md here carries
   only a pointer plus non-sensitive facts.)

## §1 Access conventions

- SSH with an explicit key path and port, `-o BatchMode=yes` (fail fast
  instead of hanging on a prompt), `-o StrictHostKeyChecking=accept-new`.
- **Never connect as root** — failed root publickey attempts trip
  fail2ban and ban your egress IP (symptom: connects that used to work
  now *time out*, not "refused").
- Keys may be passphrase-protected in the macOS keychain agent: check
  `ssh-add -l` first; if empty, hand the operator the
  `ssh-add --apple-use-keychain <key>` command — never attempt to read
  the key or supply a passphrase.
- Shell gotcha: **zsh does not word-split unquoted variables** — inline
  ssh flags or use an array (`OPTS=(-i key -p PORT)` +
  `"${OPTS[@]}"`); a scalar `$OPTS` silently falls back to port 22.
- Network egress may need the sandbox off; keep the command itself
  read-only unless the task is authorized to write.
- Docker on the box typically needs `sudo`. IPv4-only boxes are common:
  use `127.0.0.1`, not `localhost` (`::1`).

## §2 The staged-script pattern (for any production write)

Perform production changes as a **self-contained, self-verifying bash
script**: preconditions that **abort before any change** if the world
doesn't match the plan → backup/rollback artifacts → the change →
self-verification → an explicit `SUCCESS:` / `FAILURE:` verdict with a
non-zero exit on failure. `scp` it to the box and run it (or hand the
operator one command). The value is the preconditions, rollback
artifacts, and self-verification — not ceremony.

- Scripts live in [`scripts/staged/`](../../scripts/staged/) named
  `YYYY-MM-DD-<action>.sh`, and are **kept forever as records**.
- Never delete `*.bak` rollback artifacts, previous images/tags, or
  `/etc/letsencrypt` material without explicit operator approval.
- Skeleton: `set -u`; `fail()` accumulates; numbered `== sections ==`;
  end `SUCCESS`/`FAILURE: <list>; exit 1`.

## §3 Deploy model

- **Source of truth is a repo directory** (`deploy/vps/` here) that
  mirrors the box's bundle; author there, rsync to the box — never
  hand-edit on the box (the next deploy reverts it). Exclusions are
  load-bearing: runtime state (`.env`, data, certs, logs) is never
  synced in either direction.
- **Pin image tags to the stable branch** (not mainline, not `latest`);
  bump deliberately during CVE sweeps, in parity across containers.
- **Rehearse config changes in a throwaway container** (`docker run
  --rm ... nginx -t` style) before the live service sees them — attach
  the throwaway to the real networks when upstream resolution is part
  of the config.
- **Single-file bind mounts don't pick up rsync-replaced files** (new
  inode): deploy config-only changes with
  `docker compose up -d --force-recreate <service>`. (This bit us on
  day one — 2026-07-30.)
- `restart: unless-stopped` on every service so the stack survives
  reboots.
- After every deploy: run the health checks immediately **and again
  ~5 minutes later** (OPS-GUIDE cadence table).

## §4 Authorization gate (verbatim, repeated in every doc that can trigger a write)

> Only push to the VPS when the operator explicitly asks in the current
> session ("deploy", "push to the VPS", or by naming the script). Never
> infer authorization from a generic "looks good" or from a previous
> deploy in the session. Local edits and local git commits are not
> gated — only the VPS side is.

## §5 Session checklist

1. `ssh-add -l` (key loaded?) → read-only connect test.
2. State the task, classify read-only vs write; if write, confirm the
   explicit go exists for *this* task.
3. Do the work per the specific runbook; stage scripts for writes.
4. Verify, end on green, run the post-change health pass.
5. Record: same-commit doc updates (SERVER-GUIDE facts, CVE baseline,
   ops-backlog Done-notes), WORKLOG entry for status-changing events.

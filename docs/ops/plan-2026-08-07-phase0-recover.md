# P0 — recover the 2026-08-06 evidence commit

**Operator-gated: this writes to a live production container.** Do not run it
on a generic "looks good" or on the strength of this plan's approval
(AGENT-VPS-SERVICING-GUIDE §0.1). Confirm in the current session.

**Files:** `scripts/staged/2026-08-07-recover-evidence-push.sh` (new).

## Why

Commit `36ae3b9` — 168 files, including `digests/2026-08-06.md`,
`provenance/runs/insight-2026-08-06.md` and the frozen day view — exists
**only** in the `fapd-backend` container's writable layer. `/app` is not a
volume. Any `docker compose build` / container recreate destroys it, and P3
creates volumes that Docker seeds from the *image*, not from that layer. This
phase runs first or the day is lost.

Re-rendering is not an equivalent recovery: `provenance/runs/insight-2026-08-06.md`
is LLM-generated and would come out different, and re-running the finalizer
re-spends tokens for a day already paid for.

## Diff sketch

A staged script in the `scripts/staged/` pattern (kept forever as a record,
per AGENT-VPS-SERVICING-GUIDE §2). Structure: `set -u`, a `fail()`
accumulator, numbered `== section ==` headers, explicit `SUCCESS:` /
`FAILURE: <list>; exit 1` verdict. Follow
`scripts/staged/2026-08-07-repair-presact-journal-class.sh` for the shape,
including its `run_in()` style helper.

```sh
#!/usr/bin/env bash
# 2026-08-07 — recover the unpushed EOD evidence commit (36ae3b9).
#
# Why: [the narrative above — the writable layer, why P3 would destroy it,
# why re-render is not equivalent].
# Blast radius: git state of one container + one additive commit on origin/main.
set -u
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }

C=fapd-backend
KEY_ENV='GIT_SSH_COMMAND="ssh -i /app/secrets/deploy_key -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"'
g() { sudo docker exec -i "$C" sh -lc "cd /app && $KEY_ENV git $*"; }

echo "== 1. Preconditions (abort before any change) =="
sudo docker ps --format '{{.Names}}' | grep -qx "$C" || { echo "FAILURE: $C not running"; exit 1; }
HEAD_SHA="$(g rev-parse HEAD)"
g log -1 --format=%s | grep -q '^Daily pipeline evidence' \
  || fail "HEAD is not an evidence commit: $(g log -1 --format=%s)"
AHEAD="$(g rev-list --count origin/main..HEAD)"
[ "$AHEAD" = "1" ] || fail "expected exactly 1 unpushed commit, found $AHEAD"
g ls-remote origin main >/dev/null || fail "deploy key cannot reach origin"
g show --stat --format="" HEAD | grep -q 'digests/2026-08-06.md' \
  || fail "the commit does not carry digests/2026-08-06.md"
[ ${#FAILURES[@]} -eq 0 ] || { echo "FAILURE: ${FAILURES[*]}"; exit 1; }
echo "  ok — HEAD $HEAD_SHA, 1 commit ahead, remote reachable"

echo "== 2. Rollback artifacts =="
g branch -f evidence-backup-2026-08-07 HEAD
sudo mkdir -p /opt/fapd/backup/2026-08-07-evidence
sudo docker cp "$C:/app/digests"          /opt/fapd/backup/2026-08-07-evidence/
sudo docker cp "$C:/app/provenance"       /opt/fapd/backup/2026-08-07-evidence/
echo "  ok — branch evidence-backup-2026-08-07 + host copy under /opt/fapd/backup/"

echo "== 3. Fetch, rebase, push =="
g fetch origin main                     || { echo "FAILURE: fetch"; exit 1; }
if ! g rebase --autostash origin/main; then
  g rebase --abort || true
  echo "FAILURE: rebase conflict — backup branch intact, nothing pushed"; exit 1
fi
g push origin main                      || { echo "FAILURE: push"; exit 1; }

echo "== 4. Self-verification =="
g fetch origin main
[ "$(g rev-parse HEAD)" = "$(g rev-parse origin/main)" ] || fail "HEAD != origin/main after push"
g ls-remote origin main | grep -q "$(g rev-parse HEAD | cut -c1-8)" || fail "remote tip does not match"
[ ${#FAILURES[@]} -eq 0 ] && echo "SUCCESS: 2026-08-06 evidence is on origin/main" \
  || { echo "FAILURE: ${FAILURES[*]}"; exit 1; }
```

`--autostash` is required, not defensive: `RenderWorker._refresh_health`
rewrites `site/sources*.html` on a clock, so the working tree is reliably
dirty. The observed `git status` at diagnosis time showed
`M site/sources.html`, `M site/sources.json` and ~40 `site/sources/*.html`.

## Justification

- **In-container, not `docker cp` + commit from the laptop:** preserves the
  `fapd-pipeline` bot authorship and the commit's own metadata, and exercises
  the exact fetch→rebase→push sequence P1 makes permanent — P0 becomes the
  rehearsal for P1 rather than a one-off workaround.
- **`rebase`, not `merge`:** the evidence commit stays a single linear commit
  on top of `main`, matching every prior `Daily pipeline evidence` commit. A
  merge commit in the evidence stream would be a new shape for no gain.
- **Backup branch *and* host file copy:** the branch protects against a bad
  rebase; the file copy protects against losing the container entirely.

## Alternatives considered

- **`git push --force`** — rejected outright. It would discard `f9dd68c` from
  origin. Never appropriate here.
- **Copy files out, commit from the laptop** — works, but authors the commit
  as the operator, breaking the `fapd-pipeline` attribution that every other
  evidence commit carries, and proves nothing about the P1 fix.
- **Re-render 2026-08-06 locally from a fresh seed** — slowest, re-spends
  tokens, and cannot reproduce the insight report.

## Risk / blast radius

The rebase is verified clean in advance: `f9dd68c` added only
`scripts/staged/2026-08-07-repair-presact-journal-class.sh`, which the
evidence commit does not touch. Worst case is a conflict, which the script
aborts on, leaving the backup branch and nothing pushed. The push is additive.

Do **not** run this while an EOD finalize is in flight. Check
`collector_state.finalize_target IS NULL` first; at diagnosis time it was.

## Verification

```sh
# on the box
sudo docker exec fapd-backend git -C /app status -sb        # "## main...origin/main" (not ahead)
# on the operator machine
git pull && ls -la digests/2026-08-06.md provenance/runs/insight-2026-08-06.md
git log --oneline origin/main -2
```

The live site needs no change — 2026-08-06 has been served since 04:20 UTC.

## Rollback

```sh
sudo docker exec fapd-backend git -C /app reset --hard evidence-backup-2026-08-07
```

Valid only *before* step 3's push succeeds. After a successful push the
correct undo is a revert commit, not a reset — but there is nothing to undo:
the push only adds the evidence the repository was always meant to hold.

## Dependencies

None. **Blocks P3.**

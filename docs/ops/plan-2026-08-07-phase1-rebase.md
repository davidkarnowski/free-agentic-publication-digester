# P1 — `evidence-commit.sh` fetches and rebases before pushing

**Files:** `deploy/vps/scripts/evidence-commit.sh`.

## Why

The script pushes without ever fetching. The box's `origin/main` ref is a
frozen snapshot from deploy time (the whole `.git` is rsynced and baked by
`Dockerfile.backend`), so **any operator commit pushed after a deploy breaks
every subsequent night** with `! [rejected] main -> main (fetch first)` — as
it did on 2026-08-07. The condition never self-clears; only the next deploy
resets it.

## Diff sketch

Keep the existing guard-shell intact — the repo-root assertion (found
2026-07-30, pre-push), the staged-set allowlist, and the bot identity named
on the `commit` itself rather than trusting config (the first automated push
on 2026-07-31 was authored as the operator). All three are load-bearing and
each has a finding behind it.

**1. Export the SSH command once, at the top** — `fetch` needs the deploy key
too. Today `GIT_SSH_COMMAND` is inlined on the `push` line alone, which is
exactly why a fetch was never added:

```sh
export GIT_SSH_COMMAND="ssh -i /app/secrets/deploy_key -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
```

**2. Fetch before staging**, so `origin/main` is real for every later test:

```sh
git fetch origin main || { echo "GUARD ABORT — cannot reach origin"; exit 5; }
```

Unreachable remote aborts *before* anything is committed.

**3. Stage / guard / commit: unchanged.** Keep the `git add` set
(`digests/ provenance/ site/ SOURCES.md`), the `BAD` allowlist check with its
`git reset --mixed` on violation, and the commit message body.

**4. Replace the "nothing staged" early exit.** Today an empty stage exits 0.
That is now wrong: an empty stage with a *previously failed* push still has
work to do. New logic:

```sh
if [ -z "$STAGED" ]; then
  echo "evidence-commit: nothing staged"
else
  ...guard + commit as today...
fi

if [ "$(git rev-list --count origin/main..HEAD)" = "0" ]; then
  echo "evidence-commit: nothing to publish — HEAD is on origin/main"; exit 0
fi
```

**5. Rebase onto the fetched tip:**

```sh
if ! git rebase --autostash origin/main; then
  git rebase --abort || true
  echo "FAILURE — rebase conflict against origin/main; the evidence commit is"
  echo "  intact locally but UNPUSHED and lives in the container's writable"
  echo "  layer. Resolve before the next deploy or it is lost."
  exit 4
fi
```

`--autostash` is required, not cosmetic. `RenderWorker._refresh_health`
(`src/fapd/collect.py:462`) rebuilds `site/sources*.html` on a clock
(`config.SOURCE_HEALTH_REFRESH_MIN`), independent of the journal watermark, so
the tree is reliably dirty — `pause_event` stops workers at the top of their
loop but not mid-cycle. A bare `git rebase` would fail with "cannot rebase:
you have unstaged changes".

**6. Push, then verify before claiming success:**

```sh
git push origin main
git fetch origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || {
  echo "FAILURE — push reported success but HEAD != origin/main"; exit 6; }
echo "evidence-commit: SUCCESS (${DATE_TAG})"
```

A no-op push must never print `SUCCESS`; P2 keys its durable state off this
script's exit code, so the exit code has to mean what it says.

**7. Autostash-pop failure is a warning, not a failure.** If the rebase
succeeds but the autostash cannot reapply, the commit and push are still
correct and the stashed content is regenerable site output. Log it loudly
(`git stash list` will show the leftover) and continue.

## Justification

Fetch-then-rebase is the minimal change that makes the box's git state agree
with reality. The alternative — teaching `deploy.sh` to keep the box in sync —
only narrows the window; the box would still be a frozen snapshot between
deploys, and the operator commits *after* a deploy, which is precisely the
observed failure.

Exit codes are distinct on purpose (`2` non-evidence staged, `3` not repo
root, `4` rebase conflict, `5` remote unreachable, `6` push verification) so
P2's durable error string names the actual failure mode instead of "non-zero".

## Alternatives considered

- **`git pull --rebase`** — equivalent, but it hides the fetch, and the fetch
  needs its own failure branch that aborts before committing.
- **`git push --force-with-lease`** — would discard operator commits. Never.
- **Merge instead of rebase** — puts merge commits into the evidence stream
  for no benefit; every prior evidence commit is linear.
- **Have `deploy.sh` run `git fetch` in-container** — treats the symptom, and
  only until the operator's next commit.

## Risk / blast radius

The script runs only from `EODWorker` behind `FAPD_EVIDENCE_PUSH=1`. A bug
here cannot corrupt the digest, the database, or the live site — worst case is
another unpushed night, which P2 now makes loud. The rebase is bounded by the
allowlist: only `digests/`, `provenance/`, `site/`, `SOURCES.md` are ever
committed, so a conflict can only involve evidence paths.

`tests/test_dev_stack.py::test_dev_stack_cannot_push_evidence` must still
pass — the dev stack must not gain a push path from this change.

## Verification

Manufacture the exact failure instead of waiting for an EOD:

```sh
# 1. make origin deliberately ahead of the box (trivial commit from the laptop)
git commit --allow-empty -m "test: force box divergence" && git push

# 2. run the script in-container — today this exits non-zero
sudo docker exec fapd-backend bash deploy/vps/scripts/evidence-commit.sh; echo "exit=$?"

# 3. expect: fetch, rebase, push, exit 0, and
sudo docker exec fapd-backend git -C /app status -sb   # "## main...origin/main"
```

Also confirm the no-op path: run it twice; the second run must print
"nothing to publish" and exit 0 without creating an empty commit.

## Rollback

Revert the file. The previous version still commits correctly; it only fails
to push when diverged — the status quo ante.

## Dependencies

None. Independent of P2 and P4. P0 is a manual rehearsal of the same
sequence, not a prerequisite.

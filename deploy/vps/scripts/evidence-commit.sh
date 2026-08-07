#!/usr/bin/env bash
# Evidence commit for the EOD finalizer (GUIDE §10 evidence exemption,
# guard-shell pattern from docs/continuous-ingestion.md §9). Stages ONLY
# evidence paths, asserts the staged set matches, commits as the bot
# identity, rebases onto the real origin, pushes over the deploy key.
# Any mismatch aborts untouched.
#
# Exit codes are distinct because collect.EODWorker records them as the
# durable failure reason (F-021): 2 non-evidence paths staged, 3 not at
# repo root, 4 rebase conflict, 5 remote unreachable, 6 push verification.
set -euo pipefail
# Repo root is three levels up (scripts -> vps -> deploy -> root), the
# same walk deploy.sh does. One level up is deploy/vps — still inside
# the repo, where `git add digests/ ...` matches nothing and every
# evidence commit exits "nothing staged" (found 2026-07-30, pre-push).
cd "$(dirname "$0")/../../.."
test -f GUIDE.md || { echo "GUARD ABORT — not at repo root: $PWD"; exit 3; }

# Exported once, not inlined on the push: fetch needs the deploy key too,
# and it was inlined on push alone, which is precisely why no fetch was
# ever added. accept-new is load-bearing — a freshly recreated container
# has an empty known_hosts, and a bare fetch fails "Host key
# verification failed", which reads like a credential fault and is not.
export GIT_SSH_COMMAND="ssh -i /app/secrets/deploy_key -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"

DATE_TAG="$(date -u +%F)"

# Fetch BEFORE staging. The container's .git is an rsynced snapshot baked
# by Dockerfile.backend, so its origin/main ref is frozen at deploy time
# and every later operator commit made the push a non-fast-forward —
# silently, nightly, until the next deploy (F-021, 2026-08-07). An
# unreachable remote aborts here, before anything is committed.
git fetch origin main || { echo "GUARD ABORT — cannot reach origin"; exit 5; }

git add digests/ provenance/ site/ SOURCES.md 2>/dev/null || true

STAGED="$(git diff --cached --name-only | sort)"
if [ -z "$STAGED" ]; then
  echo "evidence-commit: nothing staged"
else
  BAD="$(echo "$STAGED" | grep -vE '^(digests/|provenance/|site/|SOURCES\.md)' || true)"
  if [ -n "$BAD" ]; then
    echo "GUARD ABORT — non-evidence paths staged:"; echo "$BAD"
    git reset --mixed >/dev/null; exit 2
  fi

  # The container image sets the bot identity globally, but the rsynced
  # repo carries the operator's .git/config, which wins — the first
  # automated push on 2026-07-31 was authored as the operator. Name the
  # identity on the commit itself so it cannot be overridden.
  git -c user.name="fapd-pipeline" \
      -c user.email="fapd-pipeline@users.noreply.github.com" \
      commit -m "Daily pipeline evidence ${DATE_TAG} (automated)

Digest, provenance manifest, and site as produced and validated by the
end-of-day finalizer run on the VPS backend container.

Co-Authored-By: fapd-pipeline <fapd-pipeline@users.noreply.github.com>"
fi

# Nothing staged is NOT the same as nothing to publish: a previously
# failed push leaves a good commit sitting unpushed, and before this
# check the empty-stage early exit stranded it for another day.
if [ "$(git rev-list --count origin/main..HEAD)" = "0" ]; then
  echo "evidence-commit: nothing to publish — HEAD is on origin/main"; exit 0
fi

# --autostash is required, not defensive: RenderWorker._refresh_health
# rebuilds site/sources*.html on a clock independent of the journal, so
# the tree is reliably dirty even with collectors paused (pause_event
# stops workers at the top of their loop, not mid-cycle). A bare rebase
# aborts on unstaged changes.
if ! git rebase --autostash origin/main; then
  git rebase --abort || true
  echo "FAILURE — rebase conflict against origin/main. The evidence commit"
  echo "  is intact locally but UNPUSHED, and /app/digests + /app/provenance"
  echo "  are volumes while .git is not: resolve before the next rebuild."
  exit 4
fi

git push origin main

# Verify rather than trust the exit code: EODWorker keys its durable
# state off this script's success, so success has to mean the evidence
# is actually on the remote.
git fetch origin main
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  echo "FAILURE — push reported success but HEAD != origin/main"; exit 6
fi

# A stash left behind is a warning, never a failure: the rebase and push
# already succeeded and the stashed content is regenerable site output.
if [ -n "$(git stash list)" ]; then
  echo "WARNING — autostash did not reapply cleanly; 'git stash list' is"
  echo "  non-empty. The commit and push are unaffected."
fi

echo "evidence-commit: SUCCESS (${DATE_TAG})"

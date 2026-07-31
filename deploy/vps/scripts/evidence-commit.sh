#!/usr/bin/env bash
# Evidence commit for the EOD finalizer (GUIDE §10 evidence exemption,
# guard-shell pattern from docs/continuous-ingestion.md §9). Stages ONLY
# evidence paths, asserts the staged set matches, commits as the bot
# identity, pushes over the deploy key. Any mismatch aborts untouched.
set -euo pipefail
# Repo root is three levels up (scripts -> vps -> deploy -> root), the
# same walk deploy.sh does. One level up is deploy/vps — still inside
# the repo, where `git add digests/ ...` matches nothing and every
# evidence commit exits "nothing staged" (found 2026-07-30, pre-push).
cd "$(dirname "$0")/../../.."
test -f GUIDE.md || { echo "GUARD ABORT — not at repo root: $PWD"; exit 3; }

DATE_TAG="$(date -u +%F)"
git add digests/ provenance/ site/ SOURCES.md 2>/dev/null || true

STAGED="$(git diff --cached --name-only | sort)"
if [ -z "$STAGED" ]; then
  echo "evidence-commit: nothing staged — no changes to publish"; exit 0
fi
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
GIT_SSH_COMMAND="ssh -i /app/secrets/deploy_key -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git push origin main
echo "evidence-commit: SUCCESS (${DATE_TAG})"

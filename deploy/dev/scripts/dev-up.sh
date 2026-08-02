#!/usr/bin/env bash
# Bring up the LOCAL dev stack: guard checks -> stage repo/ -> build ->
# up -> render -> report the URL. Runbook: deploy/dev/README.md.
# This script touches nothing outside the repo and the local Docker
# daemon — the VPS is never contacted here (seeding is dev-seed.sh, and
# that one is operator-gated).
set -euo pipefail
cd "$(dirname "$0")/../../.."   # repo root (scripts -> dev -> deploy -> root)
DEV=deploy/dev

# -- guards -----------------------------------------------------------------
# The dev stack must be PHYSICALLY unable to push evidence to the
# production repository. Refuse to start, don't warn.
if [ "${FAPD_EVIDENCE_PUSH:-}" = "1" ] || grep -qE '^FAPD_EVIDENCE_PUSH=1' "$DEV/.env" 2>/dev/null; then
  echo "GUARD ABORT — FAPD_EVIDENCE_PUSH=1 is set; the dev stack never pushes evidence." >&2
  exit 2
fi
if [ ! -f "$DEV/.env" ]; then
  echo "==> no $DEV/.env — creating from dev.env.example (render mode needs no edits)"
  cp "$DEV/dev.env.example" "$DEV/.env"
fi
# A prod-shaped env is the one copy-paste mistake this stack cannot absorb.
if grep -qE '^SITE_BASE_URL=https?://' "$DEV/.env"; then
  echo "GUARD ABORT — $DEV/.env sets an absolute SITE_BASE_URL; dev artifacts must not claim a real host." >&2
  exit 2
fi

echo "==> [1/4] stage build context ($DEV/repo/, shared exclude list)"
# Same excludes as deploy.sh's repo export — one list, two stagers, no drift.
rsync -a --delete --exclude-from deploy/common/repo-excludes.txt ./ "$DEV/repo/"

echo "==> [2/4] build"
docker compose -f "$DEV/docker-compose.yml" --project-directory "$DEV" build render

echo "==> [3/4] up + render"
docker compose -f "$DEV/docker-compose.yml" --project-directory "$DEV" up -d web
docker compose -f "$DEV/docker-compose.yml" --project-directory "$DEV" run --rm render

echo "==> [4/4] verify"
sleep 2
curl -fsSI http://localhost:8080/ | head -1
curl -fsS http://localhost:8080/today.html >/dev/null && echo "today.html: OK"
seeded=$(docker compose -f "$DEV/docker-compose.yml" --project-directory "$DEV" \
  run --rm --entrypoint cat render /app/data/SEEDED 2>/dev/null || true)
if [ -n "$seeded" ]; then
  echo "==> data vintage: seeded $seeded"
else
  echo "==> WARNING: no SEEDED stamp — run scripts/dev-seed.sh (operator-gated) for production-shaped data"
fi
echo "==> dev stack up: http://localhost:8080"

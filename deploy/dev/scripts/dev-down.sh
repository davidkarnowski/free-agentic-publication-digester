#!/usr/bin/env bash
# Stop the dev stack. --wipe also removes the volumes (seed + rendered
# site), so the next dev-up.sh proves the from-scratch bootstrap.
set -euo pipefail
cd "$(dirname "$0")/../../.."
DEV=deploy/dev

if [ "${1:-}" = "--wipe" ]; then
  docker compose -f "$DEV/docker-compose.yml" --project-directory "$DEV" down -v
  echo "==> dev stack down; volumes removed (re-seed before the next render)"
else
  docker compose -f "$DEV/docker-compose.yml" --project-directory "$DEV" down
  echo "==> dev stack down; volumes kept ($0 --wipe to remove)"
fi

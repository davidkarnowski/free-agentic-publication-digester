#!/usr/bin/env bash
# Deploy the FAPD stack to the VPS: test gate -> rsync bundle + repo
# export -> image build -> compose up. Authorization gate applies
# (deploy/vps/README.md): run only on the operator's explicit ask.
set -euo pipefail
cd "$(dirname "$0")/../.."     # repo root

SSH_KEY="${SSH_KEY:-$HOME/Projects/KnomeNet/hostinger_key}"
VPS="${VPS:-dkarnowski@31.220.60.2}"
PORT="${PORT:-2222}"
REMOTE_DIR="${REMOTE_DIR:-/opt/fapd}"
SSH_OPTS=(-i "$SSH_KEY" -p "$PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new)

echo "==> [1/4] test gate"
uv run ruff check src/ scripts/ tests/
uv run pytest -q

echo "==> [2/4] rsync bundle (deploy/vps/) and repo export (backend build context)"
rsync -az --delete --exclude '.DS_Store' -e "ssh ${SSH_OPTS[*]}" \
  deploy/vps/ "${VPS}:${REMOTE_DIR}/"
# The backend image bakes the tested working tree INCLUDING .git — the
# EOD finalizer commits evidence from inside the container and pushes to
# origin over the deploy key, which requires a real repo. Local state
# (.env, data/) never syncs.
rsync -az --delete \
  --exclude '.env' --exclude 'data/' --exclude '.venv/' \
  --exclude '__pycache__' --exclude '.pytest_cache' --exclude '.ruff_cache' \
  --exclude '.DS_Store' --exclude 'research/' --exclude '.claude/settings.local.json' \
  -e "ssh ${SSH_OPTS[*]}" \
  ./ "${VPS}:${REMOTE_DIR}/repo/"

echo "==> [3/4] build + up on the box"
ssh "${SSH_OPTS[@]}" "$VPS" \
  "cd '$REMOTE_DIR' && sudo docker compose --profile backend build backend \
   && sudo docker compose --profile backend up -d \
   && sudo docker compose ps --format '{{.Name}} {{.Status}}'"

echo "==> [4/4] verify"
sleep 10
curl -fsSI https://fapd.info | head -1
ssh "${SSH_OPTS[@]}" "$VPS" \
  "sudo docker ps --format '{{.Names}}\t{{.Status}}' | grep fapd"
echo "==> deploy complete — run the health check again in ~5 minutes"

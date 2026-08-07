#!/usr/bin/env bash
# Deploy the FAPD stack to the VPS: test gate -> rsync bundle + repo
# export -> image build -> compose up. Authorization gate applies
# (deploy/vps/README.md): run only on the operator's explicit ask.
set -euo pipefail
cd "$(dirname "$0")/../../.."  # repo root (scripts -> vps -> deploy -> root)

# Box coordinates: one resolver, shared with vps-ssh.sh so the two cannot
# drift (this file carried its own inline lookup until 2026-08-07). The
# public repo carries no server dossier facts (CLAUDE.md §13).
REPO_ROOT="$PWD"
# shellcheck source=/dev/null
. "$REPO_ROOT/deploy/vps/scripts/_env.sh"

echo "==> [1/4] test gate"
uv run ruff check src/ scripts/ tests/
uv run pytest -q

echo "==> [2/4] rsync bundle (deploy/vps/) and repo export (backend build context)"
# The excludes are load-bearing: .env, secrets/, and repo/ exist ONLY on
# the box; --delete without them destroys the deployment's own state
# (it did, once — findings F-004).
rsync -az --delete --exclude '.DS_Store' \
  --exclude '.env' --exclude 'secrets/' --exclude 'repo/' \
  --exclude 'deploy.env' \
  -e "ssh ${SSH_OPTS[*]}" \
  deploy/vps/ "${VPS}:${REMOTE_DIR}/"
# The backend image bakes the tested working tree INCLUDING .git — the
# EOD finalizer commits evidence from inside the container and pushes to
# origin over the deploy key, which requires a real repo. Local state
# (.env, data/) never syncs. The exclude list is shared with the dev
# stack's stager (deploy/common/repo-excludes.txt) so the two build
# contexts cannot drift; the bundle rsync above keeps its own inline
# list on purpose (F-004 — those excludes protect the box's state).
rsync -az --delete \
  --exclude-from 'deploy/common/repo-excludes.txt' \
  -e "ssh ${SSH_OPTS[*]}" \
  ./ "${VPS}:${REMOTE_DIR}/repo/"

echo "==> [3/4] build + up on the box"
ssh "${SSH_OPTS[@]}" "$VPS" \
  "cd '$REMOTE_DIR' && sudo docker compose --profile backend build backend \
   && sudo docker compose --profile backend up -d \
   && sudo docker compose ps --format '{{.Name}} {{.Status}}'"

# The fapd-site volume is seeded from the image only when EMPTY — an image
# rebuild does not refresh it (F-009). Rebuild the site in-container so
# presentation changes go live with the deploy instead of waiting for EOD.
ssh "${SSH_OPTS[@]}" "$VPS" \
  "sudo docker exec fapd-backend uv run python scripts/build_site.py || true"

# /today's RenderWorker skips on an unchanged journal watermark — it
# watches data, not code — so a deploy that changes the renderer must
# rebuild the live page itself or the new markup waits for the next
# journaled item.
ssh "${SSH_OPTS[@]}" "$VPS" \
  "sudo docker exec fapd-backend uv run python -c \
   'from fapd import db, publish; publish.build_today(db.connect())' || true"

# Belt-and-braces since 2026-08-07: Dockerfile.backend now bakes the SSH
# remote into the IMAGE, which is what makes it survive a container
# recreate (F-020 — this exec writes only to the running container's
# layer, so a recreate outside a deploy silently reverted it to the
# laptop tree's HTTPS remote, F-008). Kept because it costs one command
# and covers an image built before that change.
ssh "${SSH_OPTS[@]}" "$VPS" \
  "sudo docker exec fapd-backend git -C /app remote set-url origin \
   git@github.com:davidkarnowski/free-agentic-publication-digester.git"

echo "==> [4/4] verify"
sleep 10
curl -fsSI https://fapd.info | head -1
ssh "${SSH_OPTS[@]}" "$VPS" \
  "sudo docker ps --format '{{.Names}}\t{{.Status}}' | grep fapd"
echo "==> deploy complete — run the health check again in ~5 minutes"

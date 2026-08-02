#!/usr/bin/env bash
# Seed the dev stack from PRODUCTION: cold VACUUM INTO snapshots of the
# three databases, pulled over ssh, loaded into the fapd-dev data volume.
#
# AUTHORIZATION (deploy/vps/README.md gate): this reads production state
# and writes only a scratch dir on the box that it deletes — run it only
# on the operator's explicit ask, like every other VPS interaction.
#
# Copy COLD, never live (the 2026-07-30 cutover lesson: a live-WAL rsync
# arrives corrupt — "malformed database schema"). VACUUM INTO takes a
# read transaction and writes a checkpointed, WAL-free snapshot; the
# python:3.12-slim image has no sqlite3 CLI, so snapshots are made with
# the container's own Python. These are the canonical commands the ops
# docs describe in prose (OB-11, docs/agents/corpus.md).
set -euo pipefail
cd "$(dirname "$0")/../../.."   # repo root
DEV=deploy/dev

[ -f "$HOME/.fapd-deploy.env" ] && . "$HOME/.fapd-deploy.env"
: "${SSH_KEY:?set SSH_KEY - path to the box SSH key}"
: "${VPS:?set VPS - user@host}"
PORT="${PORT:-22}"
SSH_OPTS=(-i "$SSH_KEY" -p "$PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new)
# scp's port flag is -P (lowercase -p means preserve-times and silently
# eats the port number as a filename — found the hard way, first run).
SCP_OPTS=(-i "$SSH_KEY" -P "$PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new)

LOCAL_SEEDS="$(mktemp -d /tmp/fapd-seed.XXXXXX)"
trap 'rm -rf "$LOCAL_SEEDS"' EXIT

echo "==> [1/3] snapshot on the box (VACUUM INTO, inside the container)"
ssh "${SSH_OPTS[@]}" "$VPS" "
  set -e
  sudo docker exec fapd-backend sh -c 'rm -rf /app/data/snap && mkdir -p /app/data/snap'
  for db in fapd fetch_log llm_ledger; do
    sudo docker exec fapd-backend uv run python -c \
      \"import sqlite3; sqlite3.connect('data/\$db.db').execute(\\\"VACUUM INTO 'data/snap/\$db.db'\\\")\"
  done
  rm -rf /tmp/fapd-seed && mkdir -p /tmp/fapd-seed
  sudo docker cp fapd-backend:/app/data/snap/. /tmp/fapd-seed/
  sudo docker exec fapd-backend rm -rf /app/data/snap
"

echo "==> [2/3] pull snapshots"
scp -C "${SCP_OPTS[@]}" "${VPS}:/tmp/fapd-seed/*.db" "$LOCAL_SEEDS/"
ssh "${SSH_OPTS[@]}" "$VPS" "rm -rf /tmp/fapd-seed"
ls -lh "$LOCAL_SEEDS"

echo "==> [3/3] load into the fapd-dev data volume"
# A throwaway helper container is the supported way to write a named
# volume; the SEEDED stamp records the data's vintage for anyone
# debugging the stack later.
docker compose -f "$DEV/docker-compose.yml" --project-directory "$DEV" \
  create web >/dev/null 2>&1 || true   # ensures the volume exists
docker run --rm \
  -v fapd-dev_fapd-data:/data \
  -v "$LOCAL_SEEDS":/seeds:ro \
  alpine sh -c "cp /seeds/*.db /data/ && rm -f /data/*.db-wal /data/*.db-shm \
    && echo \"\$(date -u +%FT%TZ) from ${VPS%%@*}@$(echo "${VPS#*@}" | cut -c1-8)…\" > /data/SEEDED \
    && cat /data/SEEDED"
echo "==> seeded — run dev-up.sh to render against it"

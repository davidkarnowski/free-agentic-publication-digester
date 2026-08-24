#!/usr/bin/env bash
# 2026-08-24 — Restore LLM_BACKEND=cli on the VPS (operator-authorized this
# session: "let's attempt to get the anthropic CLI set back up. Proceed").
#
# Context: the claude CLI backend stopped authenticating 2026-08-14 23:08Z
# ("Your organization has disabled Claude subscription access for Claude
# Code"); production moved to Gemini free tier on 08-15 and the EOD
# finalizer then halted on 429 quota on eight of the next ten nights
# (docs/ops/plan-2026-08-24-eod-llm-resilience.md §0). Probed 2026-08-24
# 22:28Z: `claude -p` inside fapd-backend and the project's own
# CLIBackend path both succeed again on the stored CLAUDE_CODE_OAUTH_TOKEN.
#
# Changes (server side only; nothing in the repo changes):
# 1. Back up /opt/fapd/.env.
# 2. Set LLM_BACKEND=cli. GOOGLE_GEMINI_API_KEY is deliberately left in
#    place for the explicit-failover work (plan FEAT-4).
# 3. Recreate fapd-backend so the env applies (same image, no rebuild;
#    data/site/digests/provenance are volumes and survive).
#
# Verification: container env shows LLM_BACKEND=cli; container healthy;
# LLMClient resolves to cli; /fapd-health again at +5 min (cadence rule).
# Rollback: restore the backup and recreate again.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"

echo "== 1. Backup + edit /opt/fapd/.env on the VPS =="
"$VPS_SSH" "sudo bash -s" <<'REMOTE'
set -euo pipefail
ENV_FILE=/opt/fapd/.env
test -f "$ENV_FILE"
cp -p "$ENV_FILE" "$ENV_FILE.bak-$(date -u +%Y%m%d%H%M%S)"
grep -q '^CLAUDE_CODE_OAUTH_TOKEN=.\+' "$ENV_FILE" || { echo "no CLAUDE_CODE_OAUTH_TOKEN in .env" >&2; exit 1; }
sed -i 's/^LLM_BACKEND=.*/LLM_BACKEND=cli/' "$ENV_FILE"
grep -q '^LLM_BACKEND=cli$' "$ENV_FILE" || echo 'LLM_BACKEND=cli' >> "$ENV_FILE"
echo "LLM_BACKEND now: $(grep '^LLM_BACKEND=' "$ENV_FILE")"
ls -la "$ENV_FILE".bak-* | tail -1
REMOTE

echo "== 2. Recreate fapd-backend with the new env (no rebuild) =="
"$VPS_SSH" "cd /opt/fapd && sudo docker compose --profile backend up -d --no-build backend \
  && sudo docker compose ps --format '{{.Name}} {{.Status}}'"

echo "== 3. Verify =="
"$VPS_SSH" "sudo docker exec fapd-backend env | grep -E '^LLM_BACKEND='; \
  sudo docker exec -w /app fapd-backend uv run python -c \"from fapd import llm; c = llm.LLMClient(); print('resolved backend:', c._backend.name); c.close()\" 2>/dev/null \
  || sudo docker exec -w /app fapd-backend uv run python -c \"from fapd import llm, config; print('LLM_BACKEND=', config.LLM_BACKEND)\""
echo "done — run /fapd-health now and again in ~5 minutes"

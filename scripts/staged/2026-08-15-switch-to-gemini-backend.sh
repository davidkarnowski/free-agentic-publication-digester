#!/usr/bin/env bash
# 2026-08-15 — Safely transfer Google Gemini API key to VPS and switch LLM_BACKEND to gemini.
#
# Preconditions:
# 1. Local .env carries non-empty GOOGLE_GEMINI_API_KEY.
# 2. VPS SSH connection reachable via deploy/vps/scripts/vps-ssh.sh.
# 3. VPS /opt/fapd/.env exists.
#
# Changes:
# 1. Deploy local repo changes to VPS (/opt/fapd/repo).
# 2. Update /opt/fapd/.env on VPS with GOOGLE_GEMINI_API_KEY and LLM_BACKEND=gemini.
# 3. Rebuild and recreate fapd-backend container.
#
# Verification:
# 1. Check docker container health.
# 2. Verify LLMClient inside fapd-backend resolves to gemini backend.
# 3. Run a live test completion with Gemini backend inside container.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"

echo "== 1. Checking local preconditions =="
if [ ! -f "$REPO_ROOT/.env" ]; then
    echo "ERROR: Local .env file not found." >&2
    exit 1
fi

GEMINI_KEY=$(grep '^GOOGLE_GEMINI_API_KEY=' "$REPO_ROOT/.env" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [ -z "$GEMINI_KEY" ]; then
    echo "ERROR: GOOGLE_GEMINI_API_KEY is missing or empty in local .env" >&2
    exit 1
fi
echo "Local GOOGLE_GEMINI_API_KEY verified."

echo "== 2. Testing VPS connection =="
"$VPS_SSH" "echo 'VPS connection ok'"

echo "== 3. Syncing repo to VPS =="
"$REPO_ROOT/deploy/vps/scripts/deploy.sh"

echo "== 4. Updating /opt/fapd/.env on VPS =="
# Safely set or update GOOGLE_GEMINI_API_KEY and LLM_BACKEND in /opt/fapd/.env
"$VPS_SSH" "sudo bash -s" <<REMOTE_SCRIPT
set -euo pipefail
ENV_FILE="/opt/fapd/.env"

if [ ! -f "\$ENV_FILE" ]; then
    echo "ERROR: \$ENV_FILE does not exist on VPS" >&2
    exit 1
fi

# Backup current .env
cp "\$ENV_FILE" "\$ENV_FILE.bak-\$(date +%Y%m%d%H%M%S)"

# Remove any existing LLM_BACKEND or GOOGLE_GEMINI_API_KEY lines
grep -v '^LLM_BACKEND=' "\$ENV_FILE" | grep -v '^GOOGLE_GEMINI_API_KEY=' > "\$ENV_FILE.tmp"

# Append new values
cat <<EOF >> "\$ENV_FILE.tmp"
LLM_BACKEND=gemini
GOOGLE_GEMINI_API_KEY=$GEMINI_KEY
EOF

mv "\$ENV_FILE.tmp" "\$ENV_FILE"
chmod 0600 "\$ENV_FILE"
echo "Updated \$ENV_FILE with Gemini configuration."
REMOTE_SCRIPT

echo "== 5. Rebuilding and recreating backend container =="
"$VPS_SSH" "cd /opt/fapd && sudo docker compose --profile backend build backend && sudo docker compose --profile backend up -d --force-recreate backend"

echo "== 6. Verifying backend status and Gemini resolution =="
sleep 3
"$VPS_SSH" "sudo docker ps --filter name=fapd-backend"

VERIFY_OUT=$("$VPS_SSH" "sudo docker exec fapd-backend uv run python -c \"from fapd import config, llm; client = llm.LLMClient(); print('RESOLVED_BACKEND:', client._backend.name)\"")
echo "$VERIFY_OUT"

if [[ "$VERIFY_OUT" != *"RESOLVED_BACKEND: gemini"* ]]; then
    echo "FAILURE: Backend did not resolve to gemini." >&2
    exit 1
fi

echo "== 7. Testing live completion call via Gemini backend =="
LIVE_TEST_OUT=$("$VPS_SSH" "sudo docker exec fapd-backend uv run python -c \"from fapd import llm; client = llm.LLMClient(); res = client.complete('State in one word that Gemini API is connected.', purpose='probe:health'); print('LIVE_RESULT:', res['text'], '| TOKENS:', res['input_tokens'], 'in /', res['output_tokens'], 'out')\"")
echo "$LIVE_TEST_OUT"

if [[ "$LIVE_TEST_OUT" == *"LIVE_RESULT:"* ]]; then
    echo "SUCCESS: Gemini backend successfully deployed and verified on VPS."
else
    echo "FAILURE: Live Gemini completion test failed." >&2
    exit 1
fi

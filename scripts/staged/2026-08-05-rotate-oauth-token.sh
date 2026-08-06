#!/usr/bin/env bash
# 2026-08-05 — rotate CLAUDE_CODE_OAUTH_TOKEN in /opt/fapd/.env.
#
# Why: the operator's setup-token expires 2026-08-06. The CLI backend
# (LLM_BACKEND unset/cli) bills the operator's Claude subscription via
# this token; when it expires every model layer fails and the EOD
# finalizer produces a digest with no summaries.
#
# SECRET HANDLING — the point of this script's shape:
#   The token is read with `read -rs` from an interactive terminal. It is
#   never passed as an argument (visible in `ps` and shell history), never
#   echoed, never written to a log, and never printed on success or on
#   failure. Only its length and a 4-character prefix are ever shown, so
#   a typo is detectable without disclosing the value.
#
# RUN IT INTERACTIVELY — it prompts:
#   ssh -i <key> -p 2222 -t dkarnowski@<host> 'sudo bash /tmp/rotate-oauth.sh'
#
# Blast radius: one line of /opt/fapd/.env and one container recreate.
# .env is excluded from rsync in both directions (F-004), so editing it
# on the box is the designed path, not a workaround. Rollback is the
# timestamped .bak written before any change.

set -u

ENVF=/opt/fapd/.env
KEY=CLAUDE_CODE_OAUTH_TOKEN
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BAK="${ENVF}.bak.${STAMP}"
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }

echo "== 1. Preconditions (abort before any change) =="

if [[ ! -t 0 ]]; then
    echo "FAILURE: no terminal attached. Re-run with 'ssh -t' — this script"
    echo "         reads the token interactively so it never lands in a"
    echo "         command line, a log, or shell history."
    exit 1
fi

[[ -f "$ENVF" ]] || { echo "FAILURE: $ENVF not found."; exit 1; }
echo "  $ENVF present"

if ! grep -qE "^${KEY}=" "$ENVF"; then
    echo "FAILURE: $ENVF has no ${KEY} line to replace. Inspect before"
    echo "         adding one — the backend may be on a different backend."
    exit 1
fi
OLD_LEN=$(grep -E "^${KEY}=" "$ENVF" | head -1 | cut -d= -f2- | tr -d '\r\n' | wc -c | tr -d ' ')
echo "  ${KEY} present (current value length: ${OLD_LEN})"

HOUR=$(date -u +%H)
if [[ "$HOUR" =~ ^(03|04|05)$ ]]; then
    echo "FAILURE: ${HOUR}:xx UTC is inside the EOD finalizer window."
    echo "         Recreating the backend now could interrupt finalization."
    exit 1
fi
echo "  $(date -u +%H:%M) UTC — clear of the 03:00-06:00 EOD window"

sudo docker inspect fapd-backend >/dev/null 2>&1 \
    || { echo "FAILURE: fapd-backend container not found."; exit 1; }
echo "  fapd-backend present"

echo
echo "== 2. New token =="
echo "Generate one on your machine first if you have not:  claude setup-token"
echo "Paste it below. Input is hidden and is never echoed or logged."
printf "  new %s: " "$KEY"
read -rs NEW_TOKEN
echo

NEW_TOKEN="${NEW_TOKEN//[$'\r\n\t ']/}"   # strip stray whitespace from pasting
NEW_LEN=${#NEW_TOKEN}
if [[ "$NEW_LEN" -lt 20 ]]; then
    echo "FAILURE: token is ${NEW_LEN} characters — that is not a token."
    echo "         Nothing was changed."
    exit 1
fi
echo "  received: ${NEW_LEN} characters, prefix '${NEW_TOKEN:0:4}…'"
if [[ "$NEW_TOKEN" == *$'\n'* || "$NEW_TOKEN" == *"="* && "$NEW_TOKEN" == "${KEY}="* ]]; then
    echo "FAILURE: value looks like it includes the '${KEY}=' prefix."
    echo "         Paste only the token itself. Nothing was changed."
    exit 1
fi

echo "== 3. Backup =="
sudo cp -a "$ENVF" "$BAK" || { echo "FAILURE: backup failed"; exit 1; }
sudo chmod 600 "$BAK"
echo "  $BAK (mode 600)"
echo "  rollback:  sudo cp -a $BAK $ENVF && cd /opt/fapd && sudo docker compose up -d --force-recreate backend"

echo "== 4. Apply =="
# python rather than sed: the token may contain characters sed would treat
# as delimiters or backreferences, and this writes the value without ever
# interpolating it into a shell command line.
if ! NEW_TOKEN="$NEW_TOKEN" sudo -E python3 - "$ENVF" "$KEY" <<'PY'
import os, sys, re
path, key = sys.argv[1], sys.argv[2]
tok = os.environ["NEW_TOKEN"]
lines = open(path).read().splitlines()
out, done = [], False
for ln in lines:
    if re.match(rf"^{re.escape(key)}=", ln):
        out.append(f"{key}={tok}")
        done = True
    else:
        out.append(ln)
if not done:
    sys.exit("key vanished between check and write")
open(path, "w").write("\n".join(out) + "\n")
PY
then
    fail "rewrite failed — restore from $BAK"
    echo "FAILURE: ${FAILURES[*]}"; exit 1
fi
sudo chmod 600 "$ENVF"
WROTE_LEN=$(grep -E "^${KEY}=" "$ENVF" | head -1 | cut -d= -f2- | tr -d '\r\n' | wc -c | tr -d ' ')
echo "  written (new value length: ${WROTE_LEN}); .env mode 600"
unset NEW_TOKEN

echo "== 5. Recreate the backend =="
cd /opt/fapd || { fail "cannot cd /opt/fapd"; echo "FAILURE: ${FAILURES[*]}"; exit 1; }
sudo docker compose up -d --force-recreate backend 2>&1 | tail -4

echo "  waiting for health..."
for i in $(seq 1 30); do
    st=$(sudo docker inspect fapd-backend --format '{{.State.Health.Status}}' 2>/dev/null)
    [[ "$st" == "healthy" ]] && { echo "  healthy after ~$((i*3))s"; break; }
    sleep 3
done
[[ "$(sudo docker inspect fapd-backend --format '{{.State.Health.Status}}')" == "healthy" ]] \
    || fail "backend did not reach healthy"

echo "== 6. Self-verification: a real billed call =="
# The decisive check. A token that loads but cannot authenticate fails
# HERE, not at 04:00 when the finalizer needs it. The call is deliberately
# tiny and ledgers itself, so the rotation leaves an audit row.
VERIFY=$(sudo docker exec fapd-backend sh -lc "cd /app && uv run --no-sync python - <<'PY'
from fapd import llm
try:
    c = llm.LLMClient()
    r = c.complete('Reply with exactly: ok', purpose='ops:token-rotation-check')
    print('OK', r['input_tokens'], r['output_tokens'])
except Exception as e:
    print('ERR', type(e).__name__, str(e)[:160])
PY" 2>&1 | tail -1)

echo "  $VERIFY"
case "$VERIFY" in
    OK\ 0\ 0)  fail "call returned zero tokens — the zero-billed failure class" ;;
    OK\ *)     echo "  OK: token authenticates and bills normally" ;;
    *)         fail "verification call failed: $VERIFY" ;;
esac

echo "== Verdict =="
if [[ ${#FAILURES[@]} -eq 0 ]]; then
    echo "SUCCESS: ${KEY} rotated and verified with a real billed call."
    echo "Backup: $BAK   (keep it — never delete rollback artifacts)"
    echo "Next EOD run at 00:00 ET will use the new token."
    exit 0
fi
echo "FAILURE: ${FAILURES[*]}"
echo "Rollback: sudo cp -a $BAK $ENVF && cd /opt/fapd && sudo docker compose up -d --force-recreate backend"
exit 1

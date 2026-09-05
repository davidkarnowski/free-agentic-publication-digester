#!/usr/bin/env bash
# 2026-09-05 — rotate GOVINFO_API_KEY in /opt/fapd/.env.
#
# Why: the old key leaked in plaintext into container logs and two
# database columns (F-027; fixed in code by bug/redact-api-key-in-errors
# and scrubbed by 2026-09-05-scrub-leaked-api-key.sh). Redaction makes
# the stored copies unreadable; it does not invalidate the key. The
# operator issued a new one.
#
# SECRET HANDLING — the shape of this script is the point, and it
# follows 2026-08-05-rotate-oauth-token.sh:
#   The new key is read from STDIN. It is never a command argument
#   (visible in `ps` and in shell history), never echoed, never logged,
#   and never printed on success or failure. Only a SHA-256 fingerprint
#   prefix and the length are shown — enough to prove which key is
#   installed without disclosing it. The temp file it lands in is
#   created with a restrictive umask and removed on every exit path.
#
# Run from the dev machine, key piped in:
#   printf '%s\n' "$NEWKEY" | scripts/staged/2026-09-05-rotate-govinfo-key.sh
# or, reading it out of the local .env (which is gitignored, F-004):
#   scripts/staged/2026-09-05-rotate-govinfo-key.sh --from-local-env
#
# Blast radius: one line of /opt/fapd/.env and one container recreate.
# .env is excluded from rsync in BOTH directions, so editing it on the
# box is the designed path, not a workaround. Rollback is the
# timestamped .bak written before any change.
#
# Verified before writing this, from the VPS (not the operator's
# machine, which was on a VPN and could route differently):
#   no key -> 401, bogus key -> 401, NEW key -> 502.
# A 502 is govinfo's own backend outage, not an auth verdict — the point
# is that the new key does NOT get the 401 a bad key gets, so it clears
# api.data.gov's auth gate. A 200 end-to-end is not obtainable until
# govinfo recovers, and waiting for that is not a reason to keep a
# leaked key in service.
#
# NOT done here: revoking the old key. Measured the same way, the OLD
# key also still authenticates — so issuing a new one did not disable
# the exposed one. That is an api.data.gov account action for the
# operator and it is the part that actually closes the exposure.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

# ---------- read the key, never as an argument ----------
if [ "${1:-}" = "--from-local-env" ]; then
    [ -f "$REPO_ROOT/.env" ] || { echo "FAILURE: no local .env"; exit 1; }
    NEWKEY="$(python3 - "$REPO_ROOT/.env" <<'PY'
import re, sys, pathlib
m = re.search(r'^GOVINFO_API_KEY=(.*)$', pathlib.Path(sys.argv[1]).read_text(), re.M)
print((m.group(1).strip().strip('"').strip("'")) if m else "")
PY
)"
else
    IFS= read -r NEWKEY || true
fi
NEWKEY="$(printf '%s' "$NEWKEY" | tr -d '[:space:]')"

fingerprint() { printf '%s' "$1" | shasum -a 256 2>/dev/null | cut -c1-12; }

echo "== 1. Preconditions (abort before any change) =="
if [ -z "$NEWKEY" ]; then
    echo "FAILURE: no key on stdin and none found in the local .env."
    exit 1
fi
if [ "${#NEWKEY}" -lt 20 ]; then
    echo "FAILURE: key is ${#NEWKEY} chars — too short to be an api.data.gov key."
    exit 1
fi
echo "  new key: ${#NEWKEY} chars, fingerprint $(fingerprint "$NEWKEY")"

echo "  checking the new key authenticates (from the VPS, not from here)..."
AUTH=$(printf '%s\n' "$NEWKEY" | "$VPS_SSH" 'sudo docker exec -i fapd-backend python -c "
import sys, urllib.request, urllib.error
k = sys.stdin.readline().strip()
try:
    urllib.request.urlopen(urllib.request.Request(
        \"https://api.govinfo.gov/collections\",
        headers={\"X-Api-Key\": k, \"User-Agent\": \"FAPD key check\"}), timeout=25)
    print(\"200\")
except urllib.error.HTTPError as e:
    print(e.code)
except Exception:
    print(\"ERR\")
"' 2>/dev/null | tr -d '[:space:]')
echo "  auth probe: HTTP ${AUTH:-?}"
case "$AUTH" in
    200|502|503|429) echo "  -> clears the auth gate (a rejected key returns 401)" ;;
    401|403)         echo "FAILURE: the new key was REJECTED (HTTP $AUTH). Nothing changed."; exit 1 ;;
    *)               echo "FAILURE: inconclusive probe (HTTP ${AUTH:-?}). Nothing changed."; exit 1 ;;
esac

echo
echo "== 2. Back up /opt/fapd/.env, then install the key =="
printf '%s\n' "$NEWKEY" | "$VPS_SSH" "sudo bash -s -- '$STAMP'" <<'REMOTE'
set -euo pipefail
STAMP="$1"
ENVF=/opt/fapd/.env
umask 077
IFS= read -r NEWKEY
test -f "$ENVF"
cp -p "$ENVF" "$ENVF.bak.$STAMP"
grep -q '^GOVINFO_API_KEY=' "$ENVF" || { echo "FAILURE: no GOVINFO_API_KEY line to replace" >&2; exit 1; }
OLDFP=$(grep '^GOVINFO_API_KEY=' "$ENVF" | cut -d= -f2- | tr -d '[:space:]' | sha256sum | cut -c1-12)
# python does the substitution so the value never passes through a shell
# argument, a sed script, or the process list.
NEWKEY="$NEWKEY" python3 - "$ENVF" <<'PY'
import os, re, pathlib, sys
p = pathlib.Path(sys.argv[1])
t = p.read_text()
p.write_text(re.sub(r'^GOVINFO_API_KEY=.*$',
                    'GOVINFO_API_KEY=' + os.environ['NEWKEY'], t, count=1, flags=re.M))
PY
NEWFP=$(grep '^GOVINFO_API_KEY=' "$ENVF" | cut -d= -f2- | tr -d '[:space:]' | sha256sum | cut -c1-12)
chmod 600 "$ENVF"
echo "  old fingerprint: $OLDFP"
echo "  new fingerprint: $NEWFP"
echo "  backup: $ENVF.bak.$STAMP"
[ "$OLDFP" != "$NEWFP" ] || { echo "FAILURE: file unchanged" >&2; exit 1; }
REMOTE
rc=$?
[ $rc -eq 0 ] || { echo "FAILURE: install step failed (rc=$rc); .env backup retained"; exit 1; }

echo
echo "== 3. Recreate the backend so the env applies (no rebuild) =="
"$VPS_SSH" "cd /opt/fapd && sudo docker compose --profile backend up -d --no-build backend \
  && sudo docker compose ps --format '{{.Name}} {{.Status}}'"

echo
echo "== 4. Verify the container is running the new key =="
printf '%s\n' "$NEWKEY" | "$VPS_SSH" 'sudo docker exec -i fapd-backend python -c "
import sys, hashlib, os
expected = hashlib.sha256(sys.stdin.readline().strip().encode()).hexdigest()[:12]
from fapd import config
actual = hashlib.sha256((config.api_key() or \"\").encode()).hexdigest()[:12]
print(\"  expected fingerprint:\", expected)
print(\"  container resolves  :\", actual)
print(\"  MATCH\" if expected == actual else \"  MISMATCH\")
sys.exit(0 if expected == actual else 1)
"'
rc=$?

echo
if [ $rc -eq 0 ]; then
cat <<'EOT'
SUCCESS: the new govinfo key is installed and live in the container.

Note on proof: govinfo's backend is returning 502 to every request right
now, so this is verified as far as it can be — the key clears the auth
gate that a bad key does not. The first successful collection cycle
after govinfo recovers is the end-to-end confirmation; watch the govinfo
worker's consecutive_errors return to 0.

STILL OPEN — operator action at api.data.gov: REVOKE THE OLD KEY. It was
measured still authenticating from the VPS today, so the leaked
credential remains valid until it is disabled at the account. Issuing a
replacement did not close the exposure; revoking the old one does.
EOT
else
cat <<'EOT'
FAILURE: the container is not resolving the new key. The .env backup
(/opt/fapd/.env.bak.*) holds the previous value — restore it and
recreate the backend to roll back.
EOT
exit 1
fi

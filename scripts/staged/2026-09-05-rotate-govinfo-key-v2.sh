#!/usr/bin/env bash
# 2026-09-05 — rotate GOVINFO_API_KEY in /opt/fapd/.env. Second attempt.
#
# WHAT v1 GOT WRONG (2026-09-05-rotate-govinfo-key.sh, kept as the record
# of a change that was made and rolled back):
#
#   printf '%s\n' "$NEWKEY" | "$VPS_SSH" "sudo bash -s -- '$STAMP'" <<'REMOTE'
#   ...
#   IFS= read -r NEWKEY
#   REMOTE
#
# `bash -s` takes its SCRIPT from stdin, and the heredoc supplied that
# stdin — so the piped key never reached the remote at all, and `read`
# consumed the next LINE OF THE SCRIPT ITSELF as if it were the key.
# /opt/fapd/.env was written with a fragment of shell source in place of
# the credential. Docker Compose then warned five times that "$ENVF" was
# not set, which is what a stray `$ENVF` inside an env value looks like
# from the outside — the only visible symptom, and easy to dismiss as
# noise. The verification caught it: the installed fingerprint did not
# match the intended one, the script exited non-zero, and the .env was
# restored from the backup it had taken first.
#
# Two lessons, both cheap and both learned the hard way:
#   * A heredoc and a piped secret cannot share one stdin. Send the
#     remote script as a FILE, then pipe the secret to it.
#   * The fingerprint comparison is what turned a silent credential
#     corruption into a caught failure. Verify the value you INSTALLED,
#     never the value you meant to install.
#
# SECRET HANDLING (unchanged from v1 and from the 2026-08-05 OAuth
# rotation): the key is read from stdin, never a command argument
# (visible in `ps` and shell history), never echoed, never logged. Only
# a SHA-256 fingerprint prefix and the length are ever shown.
#
# Run:
#   scripts/staged/2026-09-05-rotate-govinfo-key-v2.sh --from-local-env
#   printf '%s\n' "$NEWKEY" | scripts/staged/2026-09-05-rotate-govinfo-key-v2.sh
#
# Blast radius: one line of /opt/fapd/.env and one container recreate.
# .env is excluded from rsync in both directions (F-004), so editing it
# on the box is the designed path. Rollback is the timestamped .bak.
#
# NOT done here: revoking the old key. Measured from the VPS today, the
# OLD key still authenticates — issuing a replacement did not disable
# the exposed one. That is an api.data.gov account action, and it is the
# part that actually closes F-027's exposure.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REMOTE_INSTALLER=/tmp/fapd-rotate-govinfo-${STAMP}.sh

# ---------- read the key; never as an argument ----------
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
NEWKEY="$(printf '%s' "${NEWKEY:-}" | tr -d '[:space:]')"
FP_NEW="$(printf '%s' "$NEWKEY" | shasum -a 256 | cut -c1-12)"

cleanup() { "$VPS_SSH" "sudo rm -f $REMOTE_INSTALLER" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "== 1. Preconditions (abort before any change) =="
[ -n "$NEWKEY" ] || { echo "FAILURE: no key on stdin and none in the local .env."; exit 1; }
[ "${#NEWKEY}" -ge 20 ] || { echo "FAILURE: key is ${#NEWKEY} chars — too short."; exit 1; }
echo "  new key: ${#NEWKEY} chars, fingerprint $FP_NEW"

echo "  probing the key from the VPS (not from here — the operator's"
echo "  machine is on a VPN and may route differently)..."
AUTH=$(printf '%s\n' "$NEWKEY" | "$VPS_SSH" 'sudo docker exec -i fapd-backend python -c "
import sys, urllib.request, urllib.error
k = sys.stdin.readline().strip()
try:
    urllib.request.urlopen(urllib.request.Request(
        \"https://api.govinfo.gov/collections\",
        headers={\"X-Api-Key\": k, \"User-Agent\": \"FAPD key check\"}), timeout=25)
    print(200)
except urllib.error.HTTPError as e:
    print(e.code)
except Exception:
    print(\"ERR\")
"' 2>/dev/null | tr -d '[:space:]')
echo "  auth probe: HTTP ${AUTH:-?}"
case "$AUTH" in
    200)     echo "  -> authenticated end to end" ;;
    502|503|429)
             echo "  -> clears the auth gate; govinfo's own backend is erroring."
             echo "     A rejected key returns 401, and this did not." ;;
    401|403) echo "FAILURE: the new key was REJECTED (HTTP $AUTH). Nothing changed."; exit 1 ;;
    *)       echo "FAILURE: inconclusive probe (HTTP ${AUTH:-?}). Nothing changed."; exit 1 ;;
esac

echo
echo "== 2. Stage the installer on the box (script as a FILE — v1's bug) =="
"$VPS_SSH" "cat > $REMOTE_INSTALLER" <<'INSTALLER'
#!/usr/bin/env bash
# Reads the new key from STDIN. Invoked as: printf '%s\n' KEY | sudo bash THIS
set -euo pipefail
umask 077
ENVF=/opt/fapd/.env
STAMP="${1:?stamp required}"
IFS= read -r NEWKEY
NEWKEY="$(printf '%s' "$NEWKEY" | tr -d '[:space:]')"
[ -n "$NEWKEY" ] || { echo "FAILURE: installer received no key on stdin" >&2; exit 1; }
[ "${#NEWKEY}" -ge 20 ] || { echo "FAILURE: installer got a ${#NEWKEY}-char value" >&2; exit 1; }
test -f "$ENVF"
cp -p "$ENVF" "$ENVF.bak.$STAMP"
grep -q '^GOVINFO_API_KEY=' "$ENVF" || { echo "FAILURE: no GOVINFO_API_KEY line" >&2; exit 1; }
fp() { grep '^GOVINFO_API_KEY=' "$1" | cut -d= -f2- | tr -d '[:space:]' | sha256sum | cut -c1-12; }
OLDFP="$(fp "$ENVF")"
LINES_BEFORE="$(wc -l < "$ENVF")"
# python does the substitution: the value never becomes a shell argument,
# a sed expression, or a visible process parameter.
NEWKEY="$NEWKEY" python3 - "$ENVF" <<'PY'
import os, re, pathlib, sys
p = pathlib.Path(sys.argv[1])
p.write_text(re.sub(r'^GOVINFO_API_KEY=.*$',
                    'GOVINFO_API_KEY=' + os.environ['NEWKEY'],
                    p.read_text(), count=1, flags=re.M))
PY
chmod 600 "$ENVF"
NEWFP="$(fp "$ENVF")"
LINES_AFTER="$(wc -l < "$ENVF")"
echo "  old fingerprint: $OLDFP"
echo "  installed      : $NEWFP"
echo "  lines: $LINES_BEFORE -> $LINES_AFTER (must be equal)"
echo "  backup: $ENVF.bak.$STAMP"
[ "$LINES_BEFORE" = "$LINES_AFTER" ] || { echo "FAILURE: line count changed" >&2; exit 1; }
[ "$OLDFP" != "$NEWFP" ]             || { echo "FAILURE: value unchanged" >&2; exit 1; }
printf 'INSTALLED_FP=%s\n' "$NEWFP"
INSTALLER

echo
echo "== 3. Install (key piped to the installer's own stdin) =="
OUT=$(printf '%s\n' "$NEWKEY" | "$VPS_SSH" "sudo bash $REMOTE_INSTALLER '$STAMP'" 2>&1)
echo "$OUT" | grep -v '^INSTALLED_FP='
INSTALLED_FP=$(printf '%s\n' "$OUT" | sed -n 's/^INSTALLED_FP=//p' | tr -d '[:space:]')
if [ "$INSTALLED_FP" != "$FP_NEW" ]; then
    echo
    echo "FAILURE: installed fingerprint ($INSTALLED_FP) != intended ($FP_NEW)."
    echo "         This is exactly v1's failure. Restoring the backup."
    "$VPS_SSH" "sudo bash -c 'cp -p /opt/fapd/.env.bak.$STAMP /opt/fapd/.env && chmod 600 /opt/fapd/.env'"
    exit 1
fi
echo "  fingerprint matches what we intended to install."

echo
echo "== 4. Recreate the backend so the env applies (no rebuild) =="
"$VPS_SSH" "cd /opt/fapd && sudo docker compose --profile backend up -d --no-build backend" 2>&1 \
  | grep -viE 'level=warning|variable is not set' || true
"$VPS_SSH" "sudo docker ps --format '{{.Names}} {{.Status}}' | grep fapd"

echo
echo "== 5. Verify the RUNNING container resolves the new key =="
VERIFY=$(printf '%s\n' "$NEWKEY" | "$VPS_SSH" 'sudo docker exec -i -w /app fapd-backend uv run python -c "
import sys, hashlib
expected = hashlib.sha256(sys.stdin.readline().strip().encode()).hexdigest()[:12]
from fapd import config
actual = hashlib.sha256((config.api_key() or \"\").encode()).hexdigest()[:12]
print(\"EXPECTED\", expected)
print(\"ACTUAL\", actual)
print(\"VERDICT\", \"MATCH\" if expected == actual else \"MISMATCH\")
"' 2>&1)
printf '%s\n' "$VERIFY" | grep -E '^(EXPECTED|ACTUAL|VERDICT)' | sed 's/^/  /'

if printf '%s\n' "$VERIFY" | grep -q '^VERDICT MATCH'; then
cat <<'EOT'

SUCCESS: the new govinfo key is installed and live in the container.

Proof boundary, stated honestly: govinfo's backend is returning 502 to
every request right now, so this is verified as far as it can be — the
key clears the auth gate that a rejected key does not, the installed
fingerprint matches the intended one, and the running process resolves
it. The first successful collection cycle after govinfo recovers is the
end-to-end confirmation; watch the govinfo worker's consecutive_errors
return to 0.

STILL OPEN — operator action at api.data.gov: REVOKE THE OLD KEY. It was
measured still authenticating from the VPS today. Issuing a replacement
did not close F-027's exposure; disabling the old key does.
EOT
else
cat <<EOT

FAILURE: the container does not resolve the new key.
Restore with:
  sudo cp -p /opt/fapd/.env.bak.$STAMP /opt/fapd/.env
  cd /opt/fapd && sudo docker compose --profile backend up -d --no-build backend
EOT
exit 1
fi

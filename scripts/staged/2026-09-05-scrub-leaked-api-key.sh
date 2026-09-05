#!/usr/bin/env bash
# 2026-09-05 — Remove the plaintext govinfo API key from the VPS's stored
# state and container logs (operator-authorized this session: "proceed
# with the fix for the log-leaking GovInfo API key ... ensure that key
# isn't plaintext in logs on the VPS").
#
# Context. The code fix (bug/redact-api-key-in-errors) stops NEW writes:
# requests builds the message of HTTPError and ConnectionError from the
# full request URL, and five callers stored that text verbatim. It cannot
# unwrite what is already there. This does that half.
#
# Measured before writing this, so the script knows what it is looking
# for rather than scrubbing blind:
#   collector_state.last_result   1 row
#   fetch_log.error               2 rows
#   fetch_log.url                 0   (the existing redaction always worked)
#   llm_ledger.llm_calls.error    0   (checked: Gemini's key was in a URL
#                                      query string until 2026-09-05)
#   committed evidence            0   (provenance/ digests/ site/ SOURCES.md)
#
# Method. Redact in place rather than delete: these rows are operational
# history — the 502 that exposed this is itself a finding — and GUIDE §4's
# "nothing bypasses logging" means an error row is accountability data.
# We remove the secret's VALUE, not the record that a request failed.
# The replacement matches the code's: `api_key=REDACTED`.
#
# Container logs. Docker's json-file log is root-owned on the host and
# cannot be edited in place safely while the container writes to it, so
# the log is TRUNCATED, not filtered — the alternative is rewriting a
# file the daemon holds an open handle to. Cost, stated plainly: the
# fapd-backend log since its 19:10Z recreate is lost. That is ~1 hour of
# INFO-level fetch lines, all of which are also in fetch_log.db, which is
# the durable record. The finalizer's own history lives in
# provenance/runs/, not here.
#
# NOT done here, and deliberately: rotating the key. That is an operator
# decision with a blast radius of its own (a new key must reach
# /opt/fapd/.env and the container recreated). This script makes the
# stored copies unreadable; it does not make the old key invalid.
#
# Verification: every counted surface returns 0 afterward, and the
# collector still works (its next cycle logs normally).
# Rollback: none needed — redaction is not destructive to any load-
# bearing value. DB backups are taken first regardless.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"
STAMP=$(date -u +%Y%m%d%H%M%S)

echo "== 1. Before: count the exposure (values never printed) =="
"$VPS_SSH" "sudo docker exec -i fapd-backend python - <<'PY'
import sqlite3
LIKE = '%api_key=%'
def count(path, table, col):
    try:
        c = sqlite3.connect(path)
        return c.execute(f'SELECT COUNT(*) FROM {table} WHERE {col} LIKE ?', (LIKE,)).fetchone()[0]
    except sqlite3.Error as exc:
        return f'ERR {exc}'
print('  collector_state.last_result :', count('/app/data/fapd.db', 'collector_state', 'last_result'))
print('  fetch_log.error             :', count('/app/data/fetch_log.db', 'fetch_log', 'error'))
print('  fetch_log.url               :', count('/app/data/fetch_log.db', 'fetch_log', 'url'))
print('  llm_calls.error             :', count('/app/data/llm_ledger.db', 'llm_calls', 'error'))
PY"

echo
echo "== 2. Back up the two databases that hold rows =="
"$VPS_SSH" "sudo bash -s" <<REMOTE
set -euo pipefail
cd /opt/fapd
for db in fapd fetch_log; do
  sudo docker exec fapd-backend python -c \
    "import sqlite3; sqlite3.connect('/app/data/\${db}.db').execute(\"VACUUM INTO '/app/data/\${db}.db.bak-${STAMP}'\")"
done
sudo docker exec fapd-backend sh -c 'ls -la /app/data/*.bak-* | tail -4'
REMOTE

echo
echo "== 3. Redact in place (value only; the error record survives) =="
"$VPS_SSH" "sudo docker exec -i fapd-backend python - <<'PY'
import re, sqlite3
SECRET = re.compile(r\"\\b(api_key|key)=[^&\\s\\\"'\\\`)>\\]]+\", re.IGNORECASE)
def scrub(path, table, col, pk):
    c = sqlite3.connect(path)
    c.execute('PRAGMA busy_timeout = 30000')
    rows = c.execute(f'SELECT {pk}, {col} FROM {table} WHERE {col} LIKE ?', ('%api_key=%',)).fetchall()
    n = 0
    for ident, text in rows:
        new = SECRET.sub(lambda m: m.group(1) + '=REDACTED', text or '')
        if new != text:
            c.execute(f'UPDATE {table} SET {col} = ? WHERE {pk} = ?', (new, ident))
            n += 1
    c.commit(); c.close()
    print(f'  {table}.{col}: {n} row(s) redacted')
scrub('/app/data/fapd.db', 'collector_state', 'last_result', 'worker')
scrub('/app/data/fetch_log.db', 'fetch_log', 'error', 'id')
scrub('/app/data/llm_ledger.db', 'llm_calls', 'error', 'id')
PY"

echo
echo "== 4. Truncate the container logs that carry the key =="
"$VPS_SSH" "sudo bash -s" <<'REMOTE'
set -euo pipefail
for c in fapd-backend fapd-web; do
  f=$(sudo docker inspect --format '{{.LogPath}}' "$c")
  if [ -n "$f" ] && sudo test -f "$f"; then
    before=$(sudo grep -ac 'api_key=' "$f" 2>/dev/null || echo 0)
    sudo truncate -s 0 "$f"
    echo "  $c: truncated (had $before line(s) containing api_key=)"
  else
    echo "  $c: no json log file found ($f)"
  fi
done
REMOTE

echo
echo "== 5. Verify: every surface must read 0 =="
"$VPS_SSH" "sudo docker exec -i fapd-backend python - <<'PY'
import sqlite3, sys
LIKE = '%api_key=%'
bad = 0
def count(path, table, col):
    global bad
    c = sqlite3.connect(path)
    n = c.execute(f'SELECT COUNT(*) FROM {table} WHERE {col} LIKE ?', (LIKE,)).fetchone()[0]
    print(f'  {table}.{col}: {n}')
    bad += n
    return n
count('/app/data/fapd.db', 'collector_state', 'last_result')
count('/app/data/fetch_log.db', 'fetch_log', 'error')
count('/app/data/fetch_log.db', 'fetch_log', 'url')
count('/app/data/llm_ledger.db', 'llm_calls', 'error')
sys.exit(1 if bad else 0)
PY"

"$VPS_SSH" "sudo bash -c 'n=0; for c in fapd-backend fapd-web; do f=\$(docker inspect --format \"{{.LogPath}}\" \$c); m=\$(grep -ac \"api_key=\" \"\$f\" 2>/dev/null || echo 0); echo \"  \$c log: \$m\"; n=\$((n+m)); done; exit \$([ \$n -eq 0 ] && echo 0 || echo 1)'"

echo
cat <<'EOT'
SUCCESS: no plaintext API key remains in the VPS databases or container logs.

Backups taken this run still contain the pre-redaction rows, by design
(*.bak-* under /app/data). Delete them once you are satisfied — the
servicing guide forbids removing them without your say-so.

STILL OPEN — operator decision: ROTATE THE GOVINFO KEY. This made the
stored copies unreadable; it did not invalidate the key itself, and the
key was in plaintext logs on a shared box. Rotation is a new key in
GOVINFO_API_KEY in /opt/fapd/.env plus a backend recreate.
EOT

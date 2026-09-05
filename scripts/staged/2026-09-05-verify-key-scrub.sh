#!/usr/bin/env bash
# 2026-09-05 — Correct verification for the key scrub. Follow-up to
# 2026-09-05-scrub-leaked-api-key.sh, which is kept as run (staged
# scripts are records; a mistake in one is fixed by a new script, never
# by editing the old one — scripts/staged/README.md).
#
# What went wrong in the predecessor's step 5. It counted rows matching
#   LIKE '%api_key=%'
# and demanded zero. But the redaction's own output is `api_key=REDACTED`,
# which matches that pattern — so the check could never pass, by
# construction, no matter how well the scrub worked. It reported
# "collector_state.last_result: 1, fetch_log.error: 2" and exited
# non-zero on a scrub that had in fact succeeded completely.
#
# The right predicate distinguishes the marker from a value:
#   api_key= NOT followed by REDACTED
#
# A second thing the predecessor's output made look wrong and was not:
# "collector_state.last_result: 0 row(s) redacted" while one row matched.
# That row was ALREADY redacted — by the deployed code fix, on the
# govinfo worker's first cycle after the deploy. The scrub found nothing
# to change because the fix had got there first. That is the system
# working, printed as if it were a miss.
#
# Lesson worth keeping: a verification that cannot fail is worthless, and
# so is one that cannot pass. Both are the same bug — the predicate does
# not describe the thing being verified. Check the check.
#
# Read-only. Safe to run any time.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"

echo "== Stored state: a leak is 'api_key=' NOT followed by REDACTED =="
"$VPS_SSH" "sudo docker exec -i fapd-backend python - <<'PY'
import re, sqlite3, sys
LEAK = re.compile(r\"\\b(?:api_key|key)=(?!REDACTED\\b)[^&\\s\\\"'\\\`)>\\]]+\", re.IGNORECASE)
bad = 0
def check(path, table, col):
    global bad
    c = sqlite3.connect(path)
    rows = c.execute(f'SELECT {col} FROM {table} WHERE {col} LIKE ?', ('%key=%',)).fetchall()
    leaks = [t for (t,) in rows if t and LEAK.search(t)]
    print(f'  {table}.{col}: {len(leaks)} leak / {len(rows) - len(leaks)} redacted marker(s)')
    bad += len(leaks)
check('/app/data/fapd.db', 'collector_state', 'last_result')
check('/app/data/fetch_log.db', 'fetch_log', 'error')
check('/app/data/fetch_log.db', 'fetch_log', 'url')
check('/app/data/llm_ledger.db', 'llm_calls', 'error')
print('  stored-state leaks:', bad)
sys.exit(1 if bad else 0)
PY"

echo
echo "== Container logs =="
"$VPS_SSH" 'sudo bash -s' <<'REMOTE'
total=0
for c in fapd-backend fapd-web; do
  f=$(docker inspect --format '{{.LogPath}}' "$c")
  n=$(grep -aoE '(api_key|key)=[^&", ]+' "$f" 2>/dev/null | grep -vc '=REDACTED' || true)
  size=$(stat -c %s "$f" 2>/dev/null || echo 0)
  echo "  $c: ${n:-0} leak(s); log ${size} bytes"
  total=$((total + ${n:-0}))
done
echo "  container-log leaks: $total"
[ "$total" -eq 0 ]
REMOTE

echo
echo "== The collector still works after the truncation =="
"$VPS_SSH" "sudo docker exec fapd-backend python -c \"
import sqlite3
c = sqlite3.connect('/app/data/fapd.db'); c.row_factory = sqlite3.Row
for r in c.execute('SELECT worker, last_ok_at, consecutive_errors FROM collector_state'
                   ' WHERE worker IN (\\\"govinfo\\\", \\\"analyze\\\", \\\"eod\\\")'):
    print('  ', r['worker'], 'last_ok', r['last_ok_at'], 'errors', r['consecutive_errors'])
\""

echo
cat <<'EOT'
SUCCESS: no plaintext key in stored state or container logs.

Backups from the scrub run still hold the pre-redaction rows by design
(/app/data/*.bak-2026*). Remove them when you are satisfied.

STILL OPEN — operator decision: ROTATE THE GOVINFO KEY. Nothing here
invalidates the key that was exposed.
EOT

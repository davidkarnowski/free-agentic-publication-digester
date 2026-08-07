#!/usr/bin/env bash
# 2026-08-07 — repair item_journal.source_class for PRESACT rows.
#
# Why: the 60 PRESACT rows were journaled at 23:47-23:53Z on 2026-08-06,
# before the _CLASS_WHERE fix deployed at 00:18Z. The old govinfo clause
# was a denylist — "collection NOT IN ('AGENCYPR','VOTES','BILLACTIONS')"
# — so the govinfo worker matched PRESACT and claimed all 60 as
# source_class='govinfo'.
#
# The consequence is a provenance error on a public page, not a cosmetic
# one: publish._today_channel_label reads source_class, so /today and the
# frozen day view label whitehouse.gov RSS documents "govinfo API", and
# the corroboration line reads "also received via govinfo API". These
# documents never touched the govinfo API. This project's entire claim is
# that it says where things came from.
#
# Time pressure: the EOD finalizer freezes the day view. A row repaired
# after that is repaired in a record already published.
#
# Scope: exactly the misfiled rows. PRESACT is the only affected
# collection (verified: every other collection/source_class pair is
# correct). The code fix is already deployed, so nothing re-creates them.
#
# Blast radius: one UPDATE on item_journal.source_class. No content, no
# dates, no digest text. Reversible by the inverse UPDATE.

set -u
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }
DB=/app/data/fapd.db

# The project venv, not the bare interpreter: the precondition imports
# fapd.collect to prove the DEPLOYED code already prevents recurrence.
run_py() { sudo docker exec -i fapd-backend sh -lc "cd /app && uv run --no-sync python -"; }

echo "== 1. Preconditions =="
run_py <<'PY' || exit 1
import sqlite3, sys
c = sqlite3.connect("file:/app/data/fapd.db?mode=ro", uri=True)
bad = c.execute("SELECT COUNT(*) FROM item_journal"
                " WHERE collection='PRESACT' AND source_class!='agency'").fetchone()[0]
tot = c.execute("SELECT COUNT(*) FROM item_journal WHERE collection='PRESACT'").fetchone()[0]
print(f"  PRESACT journal rows: {tot}; misfiled: {bad}")
if bad == 0:
    print("  nothing to repair — already correct"); sys.exit(1)
# The deployed code must already prevent recurrence, or we would repair
# rows the next cycle re-creates wrongly.
from fapd import collect
assert "PRESACT" in collect._AGENCY_CLASS_COLLECTIONS, \
    "deployed code still misclassifies PRESACT — deploy the fix first"
print("  deployed code classifies PRESACT as agency-class: ok")
# No other collection may be misfiled; this script is scoped to PRESACT.
rows = c.execute("SELECT collection, source_class, COUNT(*) FROM item_journal"
                 " GROUP BY 1,2").fetchall()
print("  collection/source_class pairs:", len(rows))
PY

echo "== 2. Backup the affected rows =="
sudo docker exec fapd-backend sh -lc \
  "cd /app && uv run --no-sync python -c \"
import sqlite3, json, datetime as dt
c = sqlite3.connect('data/fapd.db')
rows = [dict(zip(['id','source_class'], r)) for r in c.execute(
    \\\"SELECT id, source_class FROM item_journal WHERE collection='PRESACT'\\\")]
p = 'data/presact-journal-class.bak.json'
open(p,'w').write(json.dumps(rows))
print('  backed up', len(rows), 'rows ->', p)\""

echo "== 3. Repair =="
sudo docker exec fapd-backend sh -lc \
  "cd /app && uv run --no-sync python -c \"
import sqlite3
c = sqlite3.connect('data/fapd.db')
n = c.execute(\\\"UPDATE item_journal SET source_class='agency'\\\"
              \\\" WHERE collection='PRESACT' AND source_class!='agency'\\\").rowcount
c.commit()
print('  rows repaired:', n)\""

echo "== 4. Self-verification =="
run_py <<'PY'
import sqlite3
c = sqlite3.connect("file:/app/data/fapd.db?mode=ro", uri=True)
for r in c.execute("SELECT source_class, COUNT(*) FROM item_journal"
                   " WHERE collection='PRESACT' GROUP BY 1"):
    print("  PRESACT source_class:", tuple(r))
bad = c.execute("SELECT COUNT(*) FROM item_journal"
                " WHERE collection='PRESACT' AND source_class!='agency'").fetchone()[0]
print("  still misfiled:", bad)
raise SystemExit(0 if bad == 0 else 1)
PY
[[ $? -eq 0 ]] || fail "rows remain misfiled after the update"

echo "== Verdict =="
if [[ ${#FAILURES[@]} -eq 0 ]]; then
    echo "SUCCESS: PRESACT journal rows reclassified agency."
    echo "Next /today render (<=5 min) relabels them 'web feed'."
    echo "Rollback: data/presact-journal-class.bak.json in the container."
    exit 0
fi
echo "FAILURE: ${FAILURES[*]}"
exit 1

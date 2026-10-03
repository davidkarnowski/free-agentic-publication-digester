#!/usr/bin/env bash
# 2026-10-03 — put the Federal Register issue of 2026-09-29 back in the
# download queue.
#
# Why. FR-2026-09-29 is fetch_status='exhausted'. The publisher answered
# every one of 145 requests for it with a 200; each of 48 download
# attempts died in sync._refresh_granules on
#   UNIQUE constraint failed: granules.package_id, granules.granule_id
# because the publisher's granule listing repeated one granule id and the
# inventory was a plain INSERT. The package reached the retry ceiling on
# 2026-09-30 and stopped being tried. The issue has no raw file and no
# extracted text; the digest for 2026-09-29 reports zero Federal Register
# documents. Found in the review of 2026-10-03; nothing had reported it.
#
# The code fix (a repeated granule id is stored once; a failed download
# no longer commits a half-replaced inventory) must already be DEPLOYED.
# Precondition 3 checks the running container for it, because a reset
# against the old code only buys 48 more identical failures.
#
# What this does. One UPDATE on one row: fetch_status -> 'pending',
# fetch_attempts -> 0, last_error and last_attempt_at cleared. The
# collector's next govinfo cycle (at most 30 minutes away) downloads the
# issue through the normal path: the same requests, budgets and log as
# any other package.
#
# What this does NOT do. It does not re-render the 2026-09-29 digest or
# its frozen day page. Operator ruling, 2026-10-03: a frozen digest is
# never re-rendered; what it missed is published as a correction. The
# issue enters the corpus and the day's manifest records the fetch. The
# analyze layer works only on the current publication day and the one
# before it (GUIDE §6 r13), so this spends no inference.
#
# Blast radius: one row. Rollback: the backup written in step 2 holds the
# row as it was; restoring fetch_status='exhausted' and fetch_attempts=48
# puts it back.
#
# Run from the repository root on the operator's machine:
#   scripts/staged/2026-10-03-reset-fr-2026-09-29.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"
say() { printf '\n== %s ==\n' "$1"; }
in_container() { "$VPS_SSH" 'sudo docker exec -i fapd-backend sh -c "cd /app && /app/.venv/bin/python -"'; }

say "1-3. Preconditions (abort before any change)"
in_container <<'PY' || { echo "FAILURE: precondition not met — nothing was changed"; exit 1; }
import inspect
import sqlite3
import sys

PKG = "FR-2026-09-29"
c = sqlite3.connect("file:/app/data/fapd.db?mode=ro", uri=True)
c.row_factory = sqlite3.Row
row = c.execute(
    "SELECT fetch_status, fetch_attempts, last_error, raw_path, digest_day"
    " FROM packages WHERE package_id = ?", (PKG,)).fetchone()
if row is None:
    sys.exit(f"  ABORT: no package {PKG}")
print("  1. row:", dict(row))
if row["fetch_status"] != "exhausted":
    sys.exit("  ABORT: not 'exhausted' — nothing to reset (already done?)")
if "UNIQUE constraint failed: granules" not in (row["last_error"] or ""):
    sys.exit("  ABORT: a different failure than the one this script is for")
print("  2. the failure is the repeated-granule-id one: ok")

from fapd import sync
if "setdefault" not in inspect.getsource(sync._refresh_granules):
    sys.exit("  ABORT: the running code does not carry the fix — deploy it first")
print("  3. the running code stores a repeated granule id once: ok")
PY

say "4. Backup, change, verify"
in_container <<'PY' || { echo "FAILURE: see above"; exit 1; }
import json
import pathlib
import sys

from fapd import db

PKG = "FR-2026-09-29"
conn = db.connect()                 # WAL + busy timeout: the collector is running
row = conn.execute("SELECT * FROM packages WHERE package_id = ?", (PKG,)).fetchone()
granules = conn.execute(
    "SELECT granule_id, granule_class, title, first_seen_at FROM granules"
    " WHERE package_id = ? ORDER BY granule_id", (PKG,)).fetchall()
backup = pathlib.Path("/app/data/ops-repairs")
backup.mkdir(parents=True, exist_ok=True)
out = backup / "2026-10-03-FR-2026-09-29-before-reset.json"
out.write_text(json.dumps(
    {"package": dict(row), "granules": [dict(g) for g in granules]}, indent=1),
    encoding="utf-8")
print(f"  backup: {out} ({len(granules)} half-written granule row(s) recorded)")

cur = conn.execute(
    "UPDATE packages SET fetch_status = 'pending', fetch_attempts = 0,"
    " last_error = NULL, last_attempt_at = NULL"
    " WHERE package_id = ? AND fetch_status = 'exhausted'", (PKG,))
if cur.rowcount != 1:
    conn.rollback()
    sys.exit(f"  ABORT: expected to change 1 row, would change {cur.rowcount}")
conn.commit()

after = conn.execute(
    "SELECT fetch_status, fetch_attempts, last_error FROM packages"
    " WHERE package_id = ?", (PKG,)).fetchone()
print("  after:", dict(after))
if (after["fetch_status"], after["fetch_attempts"], after["last_error"]) != ("pending", 0, None):
    sys.exit("  verification failed")
PY

echo
echo "SUCCESS: FR-2026-09-29 is queued. The collector's next govinfo cycle"
echo "downloads it. Confirm with fetch_status='fetched', a granule count in"
echo "line with a normal issue, and extracted text for the package."

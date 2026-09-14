#!/usr/bin/env bash
# 2026-09-14 — install the fapd-mcp fail2ban jail (agent-discovery plan,
# Phase 4B files; checkpoint C-6, operator-run in Phase 5 after /mcp
# verifies). Rationale: docs/ops/plan-2026-09-13-security-review.md §4;
# runbook: docs/ops/OPS-GUIDE.md "MCP service".
#
# Host fail2ban config is shared with the cohabitant, so this script
# only ADDS three files — filter, jail, logrotate snippet — copied from
# /opt/fapd/fail2ban/ (the deploy bundle), and reloads. It never edits
# jail.local or any existing jail. Preconditions abort before any change;
# a config test runs BEFORE the reload; verification includes the
# packet-filter chain, because on 2026-09-13 three existing jails were
# running with no chain in DOCKER-USER and their bans reached nothing.
#
# Never run by an agent. Run once, keep forever (scripts/staged/README.md).

set -u
SRC=/opt/fapd/fail2ban
LOG=/opt/fapd/logs/mcp-access.log
FILTER_DST=/etc/fail2ban/filter.d/fapd-mcp.conf
JAIL_DST=/etc/fail2ban/jail.d/fapd-mcp.local
ROT_DST=/etc/logrotate.d/fapd-mcp
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP=/opt/fapd/fail2ban-backup-$STAMP
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }

echo "== 1. Preconditions =="
for f in "$SRC/filter.d/fapd-mcp.conf" "$SRC/jail.d/fapd-mcp.local" "$SRC/logrotate.d/fapd-mcp"; do
  [[ -f "$f" ]] || { echo "FAILURE: $f missing — deploy.sh has not synced the bundle."; exit 1; }
done
sudo systemctl is-active --quiet fail2ban || { echo "FAILURE: host fail2ban is not running."; exit 1; }
sudo test -f "$LOG" || { echo "FAILURE: $LOG does not exist — fapd-web must be up with the Phase 4B config and have served one /mcp request."; exit 1; }
if sudo test -f "$JAIL_DST" && ! sudo cmp -s "$SRC/jail.d/fapd-mcp.local" "$JAIL_DST"; then
  echo "FAILURE: $JAIL_DST exists and differs from the bundle copy — inspect before overwriting."; exit 1
fi
if sudo fail2ban-client status 2>/dev/null | grep -qw fapd-mcp; then
  echo "  note: jail fapd-mcp already reported by fail2ban-client (re-run is a reload)"
fi
echo "  ok: bundle files present, fail2ban running, log present"

echo "== 2. Backup any existing copies =="
sudo mkdir -p "$BACKUP"
for f in "$FILTER_DST" "$JAIL_DST" "$ROT_DST"; do
  if sudo test -f "$f"; then sudo cp -p "$f" "$BACKUP/"; echo "  backed up $f"; fi
done
echo "  backups (if any) in $BACKUP"

echo "== 3. Copy the three files (additive; nothing else in /etc/fail2ban is touched) =="
sudo install -m 644 "$SRC/filter.d/fapd-mcp.conf" "$FILTER_DST"
sudo install -m 644 "$SRC/jail.d/fapd-mcp.local"  "$JAIL_DST"
sudo install -m 644 "$SRC/logrotate.d/fapd-mcp"   "$ROT_DST"
echo "  written $FILTER_DST, $JAIL_DST, $ROT_DST"

echo "== 4. Config test BEFORE reload =="
if sudo fail2ban-client -t >/dev/null 2>&1; then
  echo "  ok: fail2ban-client -t"
else
  fail "fail2ban-client -t rejected the configuration"
  sudo rm -f "$FILTER_DST" "$JAIL_DST" "$ROT_DST"
  echo "FAILURE: ${FAILURES[*]} (the three files were removed; nothing reloaded)"; exit 1
fi
if sudo logrotate -d "$ROT_DST" >/dev/null 2>&1; then
  echo "  ok: logrotate -d parses the snippet"
else
  fail "logrotate -d rejected $ROT_DST"
fi

echo "== 5. Reload =="
sudo fail2ban-client reload >/dev/null || fail "fail2ban-client reload exited non-zero"
sleep 2

echo "== 6. Verify =="
if sudo fail2ban-client status fapd-mcp >/dev/null 2>&1; then
  echo "  ok: jail fapd-mcp is running"
  sudo fail2ban-client status fapd-mcp | sed 's/^/    /'
else
  fail "fail2ban-client status fapd-mcp: jail not reported"
fi
# Load-bearing: a running jail with no chain bans nothing (2026-09-13).
if sudo iptables -S DOCKER-USER 2>/dev/null | grep -q 'f2b-fapd-mcp'; then
  echo "  ok: f2b-fapd-mcp chain present in DOCKER-USER"
else
  fail "no f2b-fapd-mcp chain in iptables -S DOCKER-USER (check 'fail2ban-client get fapd-mcp actions' and the fail2ban log for actionstart errors)"
fi
MATCHES=$(sudo fail2ban-regex "$LOG" "$FILTER_DST" 2>/dev/null | grep -E '^Lines: ' || true)
echo "  fail2ban-regex: ${MATCHES:-(no summary line)}"
[[ -n "$MATCHES" ]] || fail "fail2ban-regex produced no summary over $LOG"

echo "== Verdict =="
if [[ ${#FAILURES[@]} -eq 0 ]]; then
  echo "SUCCESS: fapd-mcp jail installed, config-tested, reloaded; chain verified."
  echo "Manual unban (runbook): sudo fail2ban-client set fapd-mcp unbanip <addr>"
  exit 0
fi
echo "FAILURE: ${FAILURES[*]}"
echo "Rollback: sudo rm $FILTER_DST $JAIL_DST $ROT_DST && sudo fail2ban-client reload  (backups: $BACKUP)"
exit 1

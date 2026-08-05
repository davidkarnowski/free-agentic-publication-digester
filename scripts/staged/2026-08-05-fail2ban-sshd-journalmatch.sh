#!/usr/bin/env bash
# 2026-08-05 — repair the inert fail2ban sshd jail (OB-13 / F-017).
#
# Defect: /etc/fail2ban/filter.d/sshd.conf ships
#     journalmatch = _SYSTEMD_UNIT=sshd.service + _COMM=sshd
# but the unit on this Ubuntu box is `ssh.service`, not `sshd.service`.
# The match is an AND, so it never matched: 1,192 journal lines under
# ssh.service over 7 days versus 1 under sshd.service, and the jail
# reported Total failed: 0 / Total banned: 0 while user-enumeration
# sweeps ran against it.
#
# Fix: override journalmatch in jail.local's [sshd] section. The filter
# file itself is package-owned and would be reverted on upgrade, so the
# override belongs in jail.local — which is also where this box already
# overrides `port = 2222`.
#
# Scope: the jail's detection only. Not changed here: `mode = normal`
# (aggressive would also catch banner/kex probes but bans legitimate
# users on transient disconnects), bantime, maxretry, or any other jail.
# This box is shared with the cohabiting project; only [sshd] is touched.
#
# Blast radius: fail2ban reload. Worst case is a malformed jail.local,
# which the preconditions and the config test below are there to catch;
# rollback is the timestamped .bak beside the original.

set -u

JAIL=/etc/fail2ban/jail.local
FILTER=/etc/fail2ban/filter.d/sshd.conf
WANT='journalmatch = _SYSTEMD_UNIT=ssh.service + _COMM=sshd'
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BAK="${JAIL}.bak.${STAMP}"
FAILURES=()

fail() { FAILURES+=("$1"); echo "  !! $1"; }

echo "== 1. Preconditions (abort before any change) =="

if [[ ! -f "$JAIL" ]]; then
    echo "FAILURE: $JAIL not found; nothing to override safely."; exit 1
fi
echo "  jail.local present"

if ! sudo grep -qE '^\[sshd\]' "$JAIL"; then
    echo "FAILURE: no [sshd] section in $JAIL — refusing to guess placement."
    exit 1
fi
echo "  [sshd] section present"

if sudo grep -qE '^\s*journalmatch' "$JAIL"; then
    echo "FAILURE: $JAIL already sets journalmatch. Already applied, or"
    echo "         hand-edited since. Inspect before re-running."
    exit 1
fi
echo "  no existing journalmatch override (safe to add)"

if ! sudo grep -q '_SYSTEMD_UNIT=sshd\\\?.service' "$FILTER"; then
    echo "FAILURE: $FILTER no longer carries the expected journalmatch —"
    echo "         upstream may have fixed it. Re-read before overriding."
    exit 1
fi
echo "  package filter still carries the sshd.service match (defect present)"

UNIT_LINES=$(sudo journalctl _SYSTEMD_UNIT=ssh.service _COMM=sshd \
    --since "7 days ago" --no-pager 2>/dev/null | wc -l)
if [[ "$UNIT_LINES" -lt 1 ]]; then
    echo "FAILURE: the corrected journalmatch returns no journal lines."
    echo "         Do not apply a match that is also empty."
    exit 1
fi
echo "  corrected match returns $UNIT_LINES journal line(s) over 7 days"

if ! sudo systemctl is-active --quiet fail2ban; then
    echo "FAILURE: fail2ban is not running; fix that first."; exit 1
fi
echo "  fail2ban active"

echo "== 2. Backup =="
sudo cp -a "$JAIL" "$BAK" || { echo "FAILURE: backup failed"; exit 1; }
echo "  $BAK"
echo "  rollback:  sudo cp -a $BAK $JAIL && sudo systemctl reload fail2ban"

echo "== 3. Apply =="
# Insert immediately after the [sshd] header so the override sits with
# the port override this box already carries.
sudo sed -i "/^\[sshd\]/a ${WANT}" "$JAIL" || fail "sed insert failed"
echo "  [sshd] block now:"
sudo awk '/^\[sshd\]/{f=1} f&&/^\[/&&!/^\[sshd\]/{exit} f{print "    "$0}' "$JAIL"

echo "== 4. Reload =="
if sudo fail2ban-client reload sshd >/dev/null 2>&1; then
    echo "  sshd jail reloaded"
else
    fail "fail2ban-client reload sshd returned non-zero"
fi

echo "== 5. Self-verification =="

GOT=$(sudo fail2ban-client get sshd journalmatch 2>/dev/null)
echo "  effective journalmatch: ${GOT}"
if echo "$GOT" | grep -q 'ssh\.service'; then
    echo "  OK: jail is reading ssh.service"
else
    fail "jail journalmatch does not reference ssh.service"
fi

if sudo fail2ban-client status sshd >/dev/null 2>&1; then
    echo "  OK: sshd jail is up"
else
    fail "sshd jail is not reporting status"
fi

# The decisive check: does the filter now match real journal content?
# Counters start empty after a reload (findtime is 10m), so a zero
# "Currently failed" proves nothing either way — fail2ban-regex replays
# history through the same filter and does.
echo "  replaying 7 days of journal through the filter:"
MATCHED=$(sudo fail2ban-regex --journalmatch "_SYSTEMD_UNIT=ssh.service + _COMM=sshd" \
    systemd-journal sshd 2>/dev/null | grep -E '^Lines:' | head -1)
echo "    ${MATCHED:-<no summary line returned>}"
if echo "$MATCHED" | grep -qE '[1-9][0-9]* matched'; then
    echo "  OK: filter matches real journal lines (it matched none before)"
else
    fail "filter still matches nothing — the override did not take effect"
fi

echo "== Verdict =="
if [[ ${#FAILURES[@]} -eq 0 ]]; then
    echo "SUCCESS: sshd jail now reads ssh.service and matches real traffic."
    echo "Note: mode=normal matches auth failures (Invalid user, etc.), not"
    echo "protocol-level probing. Expect modest ban volume — the point is"
    echo "that the jail works at all, which it did not before."
    exit 0
fi
echo "FAILURE: ${FAILURES[*]}"
echo "Rollback: sudo cp -a $BAK $JAIL && sudo systemctl reload fail2ban"
exit 1

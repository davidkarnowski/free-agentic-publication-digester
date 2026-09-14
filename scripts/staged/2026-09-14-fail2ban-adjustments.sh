#!/usr/bin/env bash
# 2026-09-14 — host fail2ban adjustments after the agent-discovery deploy
# (operator direction the same day: "proceed with the fail2ban fixes").
# Companion to 2026-09-14-install-fapd-mcp-jail.sh (checkpoint C-6), which
# installs OUR jail; this script touches the shared, cohabitant-owned
# fail2ban setup, which is why it is staged for the operator rather than
# run by an agent. Everything here is additive or a one-word flip, with a
# backup and a config test before the reload. Run once, keep forever
# (scripts/staged/README.md).
#
# What it does, and why (WORKLOG 2026-09-14, "Deployed:" and the
# security-question entries):
#  1. /etc/fail2ban/jail.d/zz-operator-ignore.local — [DEFAULT] ignoreip
#     with loopback and the operator's own address, so the Phase 5
#     verification probes (which include a deliberate /.git/config) never
#     trip the nginx jails again. Box-local: the address is a per-box
#     fact and belongs in no repository. A per-jail ignoreip overrides
#     this (fapd-mcp sets its own; it does not need the exemption).
#  2. nginx-http-auth → enabled = false in the cohabitant's jail file
#     (both the live copy and /opt/spiralyst's), matching the edit in
#     ~/Projects/Spiralyst/spiralyst-site/host/fail2ban/jail.d/. Neither
#     site uses HTTP auth; the jail had banned nothing, ever.
#  3. fail2ban.service ordering drop-in: After/Requires docker.service.
#     Docker rebuilds the DOCKER-USER chain at boot and wipes the ban
#     rules fail2ban restored a few seconds earlier (observed on the box
#     2026-09-07: 27 bans in the database, 2 in the firewall). This is the
#     fix the Spiralyst tree's TODO §6.1 staged; it protects every jail in
#     DOCKER-USER, ours included.
#
# NOT done here, deliberately: no change to nginx-noscript's maxretry=1
# or to the Cloudflare-egress bans (operator ruling 2026-09-12: leave
# them banned). Reconsidering that is a separate decision.
#
# Usage: run on the box as the deploy user (needs sudo):
#   OPERATOR_IP=<your public address> bash /opt/fapd/repo/scripts/staged/2026-09-14-fail2ban-adjustments.sh

set -u
: "${OPERATOR_IP:?set OPERATOR_IP=<the operator's public IPv4 address>}"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
JAIL=/etc/fail2ban/jail.d/nginx-docker.local
TREE=/opt/spiralyst/fail2ban/jail.d/nginx-docker.local
IGN=/etc/fail2ban/jail.d/zz-operator-ignore.local
DROPIN=/etc/systemd/system/fail2ban.service.d/10-after-docker.conf
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }

echo "== 1. Preconditions =="
[[ "$OPERATOR_IP" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || { echo "FAILURE: OPERATOR_IP is not an IPv4 address"; exit 1; }
sudo systemctl is-active --quiet fail2ban || { echo "FAILURE: fail2ban is not running"; exit 1; }
sudo test -f "$JAIL" || { echo "FAILURE: $JAIL missing"; exit 1; }
echo "  ok"

echo "== 2. Backups =="
sudo cp "$JAIL" "/root/nginx-docker.local.bak-$STAMP" && echo "  $JAIL -> /root/nginx-docker.local.bak-$STAMP"

echo "== 3. Operator ignore list (box-local) =="
printf '# Box-local (2026-09-14): the operator'"'"'s own address, so verification\n# probes from it never trip the nginx jails. Not in any repository.\n# A per-jail ignoreip overrides this list (fapd-mcp has its own).\n[DEFAULT]\nignoreip = 127.0.0.1/8 ::1 %s\n' "$OPERATOR_IP" | sudo tee "$IGN" >/dev/null
echo "  wrote $IGN"

echo "== 4. Disable nginx-http-auth (live copy and /opt/spiralyst copy) =="
for f in "$JAIL" "$TREE"; do
  sudo test -f "$f" || { echo "  (skip: $f missing)"; continue; }
  sudo python3 - "$f" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
new, n = re.subn(r"(\[nginx-http-auth\]\n(?:#[^\n]*\n)*)enabled\s*=\s*true", r"\1enabled   = false", s, count=1)
if n == 0 and "[nginx-http-auth]" in s and re.search(r"\[nginx-http-auth\][^\[]*enabled\s*=\s*false", s):
    print(f"  {p}: already disabled")
elif n == 0:
    print(f"  {p}: pattern not found — inspect by hand"); sys.exit(2)
else:
    open(p, "w").write(new); print(f"  {p}: enabled = false")
PY
  [ $? -eq 0 ] || fail "could not edit $f"
done

echo "== 5. Config test, then reload =="
if sudo fail2ban-client -t >/dev/null 2>&1; then
  echo "  config test ok"
  sudo fail2ban-client reload >/dev/null && echo "  reloaded" || fail "reload failed"
  sleep 2
else
  fail "fail2ban-client -t failed — NOT reloading; restore from the backup in /root and inspect"
fi

echo "== 6. Verify =="
for j in nginx-noscript nginx-bad-request nginx-botsearch nginx-limit-req sshd; do
  ign=$(sudo fail2ban-client get "$j" ignoreip 2>/dev/null | tr '\n' ' ')
  echo "  $j ignoreip: $ign"
  [[ "$j" == sshd ]] || { echo "$ign" | grep -q "$OPERATOR_IP" || fail "$j does not ignore $OPERATOR_IP"; }
done
if sudo fail2ban-client status nginx-http-auth >/dev/null 2>&1; then fail "nginx-http-auth still reported"; else echo "  nginx-http-auth: gone"; fi
echo "  noscript: $(sudo fail2ban-client status nginx-noscript | grep 'Currently banned' | tr -s ' ')"
echo "  DOCKER-USER f2b chains: $(sudo iptables -S DOCKER-USER | grep -c f2b-)"

echo "== 7. fail2ban after docker (systemd drop-in) =="
sudo mkdir -p "$(dirname "$DROPIN")"
printf '[Unit]\nAfter=docker.service\nRequires=docker.service\n' | sudo tee "$DROPIN" >/dev/null
sudo systemctl daemon-reload
systemctl show fail2ban -p After | grep -q docker.service && echo "  After=docker.service: yes" || fail "drop-in not effective (After)"
systemctl show fail2ban -p Requires | grep -q docker.service && echo "  Requires=docker.service: yes" || fail "drop-in not effective (Requires)"
echo "  (verify after the next reboot: fail2ban-client banned count == iptables f2b rule count)"

echo
if [ ${#FAILURES[@]} -eq 0 ]; then echo "SUCCESS"; else echo "FAILURE: ${FAILURES[*]}"; exit 1; fi

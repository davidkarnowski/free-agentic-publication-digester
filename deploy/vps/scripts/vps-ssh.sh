#!/usr/bin/env bash
# Run a command on the FAPD box.
#
# READ-ONLY BY DEFAULT. This wrapper exists so a health check needs no
# server coordinates — not to make writes casual. Anything that writes,
# installs, restarts, deploys, reboots or bans is gated on the operator's
# explicit go for that specific task (AGENT-VPS-SERVICING-GUIDE §0.1),
# and that gate is unchanged by how convenient the connection became.
#
#   deploy/vps/scripts/vps-ssh.sh 'sudo docker ps'
#
# Network egress may need the tool sandbox disabled. Never connect as
# root: failed root publickey attempts trip fail2ban and ban the egress
# IP, whose symptom is connections that used to work now timing out.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
# shellcheck source=/dev/null
. "$REPO_ROOT/deploy/vps/scripts/_env.sh"

[ "$#" -gt 0 ] || { echo "usage: $(basename "$0") '<command>'" >&2; exit 2; }
exec ssh "${SSH_OPTS[@]}" "$VPS" "$@"

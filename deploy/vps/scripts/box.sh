#!/usr/bin/env bash
# Run one command on the FAPD box, through the external connector
# (deploy/vps/scripts/_env.sh). Replaces vps-ssh.sh (2026-11-10): the
# project no longer holds a key path, login or address.
#
# READ-ONLY BY DEFAULT. This wrapper exists so a health check needs no
# server coordinates, not to make writes casual. Anything that writes,
# installs, restarts, deploys, reboots or bans is gated on the operator's
# explicit go for that specific task, and that gate is unchanged by how
# convenient the connection became.
#
#   deploy/vps/scripts/box.sh 'sudo docker ps'
#
# Wrap long reads in `sudo timeout 20` so nothing outlives the session.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
# shellcheck source=/dev/null
. "$REPO_ROOT/deploy/vps/scripts/_env.sh"

[ "$#" -gt 0 ] || { echo "usage: $(basename "$0") '<command>'" >&2; exit 2; }
box "$@"

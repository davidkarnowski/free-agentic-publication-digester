#!/usr/bin/env bash
# 2026-08-05 — kernel 6.8.0-136 -> 6.8.0-137 (noble-security).
#
# Why: 6.8.0-137.137 carries 17 CVEs, the notable one being
# CVE-2026-53359 (KVM shadow-paging UAF, Ubuntu priority High). Practical
# exposure here is low — this box runs containers, not KVM guests, and is
# itself a guest — but it is the only real unpatched gap the 2026-08-05
# CVE sweep found, and it is a one-command fix plus a reboot.
#
# Scope: the six linux-* packages ONLY. Deliberately NOT upgraded:
#   cloud-init 24.1.3 -> 26.1  (major jump; touches boot-time network
#                               config on a VPS — not security-flagged,
#                               not worth bundling with a kernel reboot)
#   fwupd, docker-buildx-plugin (not security-flagged)
# Those stay for a separate, deliberate window.
#
# This script INSTALLS and VERIFIES ONLY. It does not reboot — the new
# kernel is not live until it does, and the reboot is issued separately
# so the install can be confirmed first.
#
# Blast radius: package install on a production host. The running kernel
# is untouched until reboot, and the previous kernel remains installed
# and bootable, which is the rollback.

set -u

WANT_ABI="6.8.0-137"
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }

echo "== 1. Preconditions (abort before any change) =="

RUNNING="$(uname -r)"
echo "  running kernel: $RUNNING"
if [[ "$RUNNING" == ${WANT_ABI}* ]]; then
    echo "FAILURE: already running $WANT_ABI — nothing to do."; exit 1
fi

HOUR=$(date -u +%H)
if [[ "$HOUR" =~ ^(03|04|05)$ ]]; then
    echo "FAILURE: ${HOUR}:xx UTC is inside the EOD finalizer window."
    echo "         A reboot now could interrupt digest finalization."
    exit 1
fi
echo "  $(date -u +%H:%M) UTC — clear of the 03:00-06:00 EOD window"

sudo apt-get -qq update >/dev/null 2>&1
PENDING=$(apt list --upgradable 2>/dev/null | grep -c "^linux-.*${WANT_ABI}")
if [[ "$PENDING" -lt 1 ]]; then
    echo "FAILURE: no pending linux-* upgrade to ${WANT_ABI} found."; exit 1
fi
echo "  $PENDING linux-* package(s) pending at ${WANT_ABI}"

for c in fapd-web fapd-backend spiralyst-proxy spiralyst-static; do
    pol=$(sudo docker inspect "$c" --format '{{.HostConfig.RestartPolicy.Name}}' 2>/dev/null)
    if [[ "$pol" != "unless-stopped" && "$pol" != "always" ]]; then
        fail "container $c has restart policy '$pol' — would NOT survive reboot"
    fi
done
if [[ ${#FAILURES[@]} -gt 0 ]]; then
    echo "FAILURE: ${FAILURES[*]}"; exit 1
fi
echo "  all four containers restart automatically"

if ! systemctl is-enabled --quiet docker; then
    echo "FAILURE: docker is not enabled at boot — stack would not return."
    exit 1
fi
echo "  docker enabled at boot"

FREE=$(df --output=avail -m /boot 2>/dev/null | tail -1 | tr -d ' ')
FREE=${FREE:-$(df --output=avail -m / | tail -1 | tr -d ' ')}
if [[ "$FREE" -lt 300 ]]; then
    echo "FAILURE: only ${FREE}MB free for /boot — kernel install needs room."
    exit 1
fi
echo "  ${FREE}MB free for the kernel install"

echo "== 2. Pre-change state snapshot (for post-reboot comparison) =="
echo "  kernel:     $RUNNING"
echo "  containers: $(sudo docker ps --format '{{.Names}}' | sort | tr '\n' ' ')"
echo "  newest digest day in DB:"
sudo docker exec -i fapd-backend python - <<'PY' 2>/dev/null || echo "    (unavailable)"
import sqlite3
c = sqlite3.connect("file:/app/data/fapd.db?mode=ro", uri=True)
print("   ", c.execute("SELECT MAX(date_issued) FROM packages").fetchone()[0])
PY

echo "== 3. Install (running kernel untouched until reboot) =="
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --only-upgrade \
    linux-image-virtual linux-headers-virtual linux-virtual \
    linux-headers-generic linux-libc-dev linux-tools-common \
    2>&1 | tail -15
STATUS=${PIPESTATUS[0]}
[[ "$STATUS" -eq 0 ]] || fail "apt-get install exited $STATUS"

echo "== 4. Self-verification (pre-reboot) =="

if ls /boot/vmlinuz-${WANT_ABI}* >/dev/null 2>&1; then
    echo "  OK: $(ls /boot/vmlinuz-${WANT_ABI}* | head -1) present"
else
    fail "no /boot/vmlinuz-${WANT_ABI}* — new kernel did not install"
fi

if [[ -f /var/run/reboot-required ]]; then
    echo "  OK: reboot-required flag set (expected)"
else
    fail "reboot-required flag absent — install may not have taken"
fi

STILL=$(apt list --upgradable 2>/dev/null | grep -c "^linux-.*${WANT_ABI}")
if [[ "$STILL" -eq 0 ]]; then
    echo "  OK: no linux-* packages left pending"
else
    fail "$STILL linux-* package(s) still pending after install"
fi

echo "  previous kernel retained for rollback:"
ls /boot/vmlinuz-* | sed 's/^/    /'

echo "== Verdict =="
if [[ ${#FAILURES[@]} -eq 0 ]]; then
    echo "SUCCESS: ${WANT_ABI} installed. Still running ${RUNNING}."
    echo "Reboot is a separate, deliberate step. Rollback if the new kernel"
    echo "misbehaves: pick the previous entry from the GRUB menu."
    exit 0
fi
echo "FAILURE: ${FAILURES[*]}"
echo "Rollback: no reboot has happened; the running kernel is unchanged."
exit 1

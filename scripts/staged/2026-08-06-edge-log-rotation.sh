#!/usr/bin/env bash
# 2026-08-06 — logrotate for the edge nginx logs (OB-15).
#
# /opt/spiralyst/logs/nginx/access.log has grown unrotated since
# 2026-05-23 (69.8MB, 96% healthcheck noise). Docker's own container
# json logs are already covered by /etc/logrotate.d/docker-containers;
# journald is capped 1G/7day; these two files are the only unrotated
# logs on the box. Shared-box note: the log path and the proxy belong
# to the cohabiting Spiralyst stack — this entry is additive and
# coordinated; the healthz access_log change is authored in that
# project's tree separately.
#
# Retention: daily, 14 rotations, compressed after one cycle. `nginx -s
# reopen` inside the container re-opens the bind-mounted files so the
# fresh file receives writes immediately (copytruncate would race and
# drop lines).
#
# `su dkarnowski dkarnowski`: the log DIRECTORY is group-writable and
# owned dkarnowski:dkarnowski, which logrotate refuses by default
# (first run failed exactly there, 2026-08-06). Rotation renames need
# only directory write permission, which dkarnowski has; nginx (root
# in the container) recreates the fresh file on reopen.

set -u
F=/etc/logrotate.d/spiralyst-nginx
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }

echo "== 1. Preconditions =="
[[ -f "$F" ]] && { echo "FAILURE: $F already exists — inspect before overwriting."; exit 1; }
sudo test -f /opt/spiralyst/logs/nginx/access.log || { echo "FAILURE: access.log not found."; exit 1; }
sudo docker inspect spiralyst-proxy --format '{{.State.Status}}' 2>/dev/null | grep -q running \
    || { echo "FAILURE: spiralyst-proxy not running (reopen signal needs it)."; exit 1; }
echo "  ok: entry absent, logs present, proxy running"
BEFORE=$(sudo stat -c %s /opt/spiralyst/logs/nginx/access.log)
echo "  access.log before: ${BEFORE} bytes"

echo "== 2. Write the logrotate entry =="
sudo tee "$F" >/dev/null <<'ROT'
/opt/spiralyst/logs/nginx/*.log {
    su dkarnowski dkarnowski
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    postrotate
        /usr/bin/docker exec spiralyst-proxy nginx -s reopen >/dev/null 2>&1 || true
    endscript
}
ROT
sudo chmod 644 "$F"
echo "  written $F"

echo "== 3. Dry-run =="
if sudo logrotate -d "$F" >/dev/null 2>&1; then
    echo "  ok: logrotate parses the entry"
else
    fail "logrotate -d rejected the entry"
    sudo rm -f "$F"
    echo "FAILURE: ${FAILURES[*]} (entry removed)"; exit 1
fi

echo "== 4. Force one rotation to prove the cycle =="
sudo logrotate -f "$F" || fail "forced rotation exited non-zero"
sleep 2
AFTER=$(sudo stat -c %s /opt/spiralyst/logs/nginx/access.log 2>/dev/null || echo missing)
ROTATED=$(sudo ls /opt/spiralyst/logs/nginx/access.log.1* 2>/dev/null | head -1)
echo "  access.log after: ${AFTER} bytes; rotated sibling: ${ROTATED:-NONE}"
[[ -n "${ROTATED:-}" ]] || fail "no rotated file appeared"
if [[ "$AFTER" != "missing" && "$AFTER" -lt "$BEFORE" ]]; then
    echo "  ok: fresh file is smaller than the original"
else
    fail "fresh access.log did not shrink (reopen may have failed)"
fi

echo "== 5. Prove the reopen took (a new request must land in the fresh file) =="
# NOT /healthz — its access_log is off as of the same change window,
# so it can never prove a reopen (the first run false-failed on this).
curl -s -o /dev/null -H "Host: fapd.info" http://127.0.0.1/robots.txt || true
sleep 2
LINES=$(sudo wc -l < /opt/spiralyst/logs/nginx/access.log)
if [[ "$LINES" -gt 0 ]]; then
    echo "  ok: ${LINES} line(s) in the fresh file — nginx is writing post-rotate"
else
    fail "fresh file has zero lines — nginx may still hold the old fd"
fi

echo "== Verdict =="
if [[ ${#FAILURES[@]} -eq 0 ]]; then
    echo "SUCCESS: rotation live — daily, keep 14, compressed; reopen verified."
    exit 0
fi
echo "FAILURE: ${FAILURES[*]}"
echo "Rollback: sudo rm $F  (rotated files are kept; harmless)"
exit 1

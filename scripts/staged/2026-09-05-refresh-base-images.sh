#!/usr/bin/env bash
# 2026-09-05 — Refresh the stack's base images onto patched OpenSSL, and
# turn on the finalizer's provider failover.
#
# Context. The 2026-09-05 health check found both base images stale: the
# backend image was built 6 days ago on a python:3.12-slim pulled 3 weeks
# ago, and nginx:1.30-alpine was pulled 7 weeks ago. Both are pinned by
# FLOATING TAG, so no repo edit is needed to move them — but deploy.sh
# passes neither --pull nor --no-cache, so every rebuild since has
# silently reused the cached stale base. That is the actual defect here:
# not the pin, the refresh that never happens.
#
# Exposure, resolved against the distro trackers rather than inferred
# from version strings (AGENT-CVE-GUIDE §1: "distro backports fix CVEs
# without changing the upstream version string", which is why the
# 2026-08-05 baseline scored 3.5.6 clean and was right to):
#
#   fapd-backend  Debian 13 trixie   openssl 3.5.6-1~deb13u2
#                 -> trixie-security 3.5.7-1~deb13u2          BEHIND
#   fapd-web      Alpine 3.24        libssl3/libcrypto3 3.5.7-r0
#                 -> v3.24 current   3.5.8-r0 (built 08-25)   BEHIND
#
# 3.5.8 is the August 2026 advisory's fix line for the 3.5.x branch.
# Both gaps are real. Six CVEs remain open in trixie at 3.5.7-1~deb13u2
# (CVE-2026-75803, -63076, -63074, -63072, -54874, CVE-2025-27587) —
# they are unfixed upstream of us, not something this script closes.
#
# NOT in this script: spiralyst-proxy. It runs the same Alpine 3.24 /
# libssl3 3.5.7-r0 and it is the container that actually terminates TLS
# for fapd.info, so it is the MORE exposed of the two — but it is the
# cohabitant's edge proxy, owned by the operator's spiralyst-site tree at
# /opt/spiralyst. The nginx pin in docker-compose.yml says "bump both
# together during CVE sweeps, never just one": this script does our half
# and the parity is not complete until the proxy's own deploy runs.
#
# Changes (server side):
#  1. Preconditions: no unpushed evidence commit, EOD not mid-run.
#  2. Rollback artifacts: retag the current backend image; record the
#     current nginx image id. There is no registry — the retagged image
#     IS the rollback, and the servicing guide forbids deleting it
#     without approval.
#  3. Pull both bases; rebuild the backend with --pull.
#  4. Recreate. `up -d` alone will NOT replace a running container whose
#     image tag is unchanged, even after a pull, so web is forced.
#  5. Re-run the site handoff (build_site + build_today): named volumes
#     seed from the image only when empty (F-009 / OB-19), so a rebuild
#     outside deploy.sh must do this or the site goes stale.
#  6. Verify: package versions, HTTPS, network isolation, health.
#
# Rollback: `docker tag fapd-backend:pre-20260905 fapd-backend:latest`
# then `docker compose --profile backend up -d --no-build backend`; for
# web, `docker tag <recorded id> nginx:1.30-alpine` and force-recreate.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"
STAMP=20260905

echo "== 0. Before: what we are moving from =="
"$VPS_SSH" "sudo bash -s" <<'REMOTE'
set -euo pipefail
echo "-- backend --"
sudo docker exec fapd-backend sh -c 'dpkg -l | awk "/ (openssl|libssl3t64) /{print \$2, \$3}"'
echo "-- web --"
sudo docker exec fapd-web sh -c 'apk info -v 2>/dev/null | grep -E "^(libssl3|libcrypto3)"'
echo "-- images --"
sudo docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedSince}}' \
  | grep -E 'python|nginx|fapd-backend'
REMOTE

echo
echo "== 1. Preconditions =="
"$VPS_SSH" "sudo bash -s" <<'REMOTE'
set -euo pipefail
# An unpushed evidence commit lives in the image writable layer (/app/.git
# is NOT a volume) and a rebuild destroys it. digests/ and provenance/ are
# volumes and survive, so the next run re-stages the files — but we do not
# rely on self-heal when a check is this cheap.
UNPUSHED=$(sudo docker exec fapd-backend git -C /app rev-list --count origin/main..HEAD 2>/dev/null || echo unknown)
echo "unpushed evidence commits: $UNPUSHED"
if [ "$UNPUSHED" != "0" ]; then
  echo "FAILURE: refusing to rebuild with unpushed evidence (or unreadable git state)" >&2
  exit 1
fi
# The EOD finalizer runs 04:00 UTC and takes ~35 min. Refuse that window.
H=$(date -u +%H)
if [ "$H" = "03" ] || [ "$H" = "04" ]; then
  echo "FAILURE: inside the EOD window (${H}:00 UTC) — come back later" >&2
  exit 1
fi
echo "preconditions OK"
REMOTE

echo
echo "== 2. Rollback artifacts =="
"$VPS_SSH" "sudo bash -s" <<REMOTE
set -euo pipefail
sudo docker tag fapd-backend:latest fapd-backend:pre-${STAMP}
sudo docker image inspect nginx:1.30-alpine --format 'nginx rollback image id: {{.Id}}' \
  | tee /opt/fapd/.rollback-nginx-${STAMP}.txt
sudo docker images --format '{{.Repository}}:{{.Tag}}' | grep "pre-${STAMP}"
REMOTE

echo
echo "== 3. Pull bases + rebuild backend =="
"$VPS_SSH" "cd /opt/fapd && sudo docker pull python:3.12-slim && sudo docker pull nginx:1.30-alpine"
"$VPS_SSH" "cd /opt/fapd && sudo docker compose --profile backend build --pull backend"

echo
echo "== 4. Recreate (web is forced: same tag, new image) =="
"$VPS_SSH" "cd /opt/fapd && sudo docker compose --profile backend up -d \
  && sudo docker compose up -d --force-recreate web \
  && sudo docker compose ps --format '{{.Name}} {{.Status}}'"

echo
echo "== 5. Site handoff (deploy.sh does this post-up; a bare rebuild must too) =="
# Same two calls deploy.sh makes post-up, in the same form (docker exec,
# container WORKDIR, `|| true`): a rebuild must not fail the run on a
# render that the RenderWorker will redo on its own clock anyway.
"$VPS_SSH" "sudo docker exec fapd-backend uv run python scripts/build_site.py || true"
"$VPS_SSH" "sudo docker exec fapd-backend uv run python -c \
   'from fapd import db, publish; publish.build_today(db.connect())' || true"

echo
echo "== 6. Verify =="
"$VPS_SSH" "sudo bash -s" <<'REMOTE'
set -euo pipefail
echo "-- backend openssl (want 3.5.7-1~deb13u2 or later) --"
sudo docker exec fapd-backend sh -c 'dpkg -l | awk "/ (openssl|libssl3t64) /{print \$2, \$3}"'
echo "-- web libssl (want 3.5.8-r0 or later) --"
sudo docker exec fapd-web sh -c 'apk info -v 2>/dev/null | grep -E "^(libssl3|libcrypto3)"'
echo "-- the finalizer's toolchain still works --"
sudo docker exec fapd-backend sh -c 'python -V; uv --version; node --version; claude --version'
echo "-- failover config visible to the container --"
sudo docker exec fapd-backend sh -c 'env | grep -E "^LLM_BACKEND(_FALLBACK)?=" | sed -E "s/=(.*)/=\1/"'
echo "-- network isolation: fapd_edge and nothing else --"
sudo docker inspect fapd-web --format '{{json .NetworkSettings.Networks}}'
echo "-- containers --"
sudo docker compose -f /opt/fapd/docker-compose.yml ps --format '{{.Name}} {{.Status}}' 2>/dev/null || sudo docker ps --format '{{.Names}} {{.Status}}'
REMOTE

echo
echo "-- site --"
curl -fsSI https://fapd.info | head -1
curl -fsS -o /dev/null -w 'day view: %{http_code}\n' https://fapd.info/day/2026-09-04.html

cat <<'EOT'

SUCCESS: base images refreshed and the stack recreated.

Still open, deliberately:
  * spiralyst-proxy is unchanged and still on libssl3 3.5.7-r0. It
    terminates TLS for fapd.info. Parity is NOT complete until its own
    repo deploys the same bump.
  * Six OpenSSL CVEs remain unfixed in Debian trixie at 3.5.7-1~deb13u2.

Now: /fapd-health immediately and again in ~5 minutes (OPS-GUIDE
cadence), then confirm tomorrow's 04:00 UTC finalizer pushed evidence.
EOT

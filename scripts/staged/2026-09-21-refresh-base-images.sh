#!/usr/bin/env bash
# 2026-09-21 — Refresh the stack's base images onto the current Debian
# and Alpine package sets, closing seven CVE rows found by the
# 2026-09-21 sweep.
#
# Context. Both bases are pinned by FLOATING TAG, so no repo edit moves
# them — but deploy.sh passes neither --pull nor --no-cache, so every
# rebuild reuses whatever base layer the box last cached. On the day of
# this sweep the cached images were built 2026-09-01 (python:3.12-slim)
# and 2026-09-02 (nginx:1.30-alpine); upstream had since pushed
# 2026-09-19 and 2026-09-18. A base refresh is therefore its own
# action, not a side effect of deploying. Third time this exact drift
# has produced findings (2026-08-05, 2026-09-05, today).
#
# WHAT THIS CLOSES — read the runtime after, never the tag:
#
#   fapd-backend (Debian 13 trixie)
#     libc6/libc-bin 2.41-12+deb13u3 -> u4   CVE-2026-5928, CVE-2026-5450
#     libpcre2-8-0   10.46-1~deb13u1 -> u2   CVE-2026-89156/89157/89158/
#                                            89160/89161(7.4 HIGH)/89162
#     libsqlite3-0   3.46.1-7+deb13u1 -> u2  CVE-2026-11822 (8.5 HIGH),
#                                            CVE-2026-11824 (7.8 HIGH)
#     gzip           1.13-1 -> 1.13-1+deb13u1 CVE-2026-41991, -41992
#     (bash, libcap2, libaudit, base-files, tzdata ride along: binNMUs
#      and data updates, no CVE content — verified in the changelogs.)
#
#   fapd-web + the two cohabitant nginx containers (Alpine 3.24)
#     libuuid   2.42.1-r0 -> 2.42.3-r1       CVE-2026-78408 + the
#                                            util-linux 2.42.3 set
#     xz-libs   5.8.3-r0  -> 5.8.4-r0        GHSA-5qpq-xqfv-j9pg (High,
#                                            NO CVE assigned — Alpine's
#                                            secfixes: block was never
#                                            updated for it, so secdb
#                                            alone calls this routine.
#                                            The aports commit says
#                                            "security upgrade".)
#     nginx     1.30.4 -> 1.30.5             CVE-2026-90439 (HTTP/3)
#
# EXPOSURE, stated honestly so the next reader does not over- or
# under-rate this run:
#   - sqlite:  NOT exposed. Both CVEs are FTS5; this codebase greps
#              clean for FTS5/FTS4/MATCH. Patched anyway — SQLite is the
#              pipeline's spine.
#   - pcre2:   transitive only (grep, git, glib). Python's `re` is its
#              own engine. Two of the six are 32-bit-only; we are amd64.
#   - nginx:   NOT exposed, two independent conditions unmet — no QUIC
#              listener anywhere (ss -ulpn shows only systemd-resolved)
#              and no quic/http3 directive in either config, and the
#              trigger needs OpenSSL <= 3.5.0 while Alpine ships 3.5.8.
#              The module IS compiled in (--with-http_v3_module), which
#              is why the version still matters.
#   - glibc/gzip/libuuid/xz: transitive, low, patched because they are
#              free to patch in the same action.
#
# WHAT THIS DOES **NOT** CLOSE — do not re-run it chasing these:
#   - expat. Trixie's 2.8.3-1~deb13u1 is vulnerable to CVE-2026-93990
#     (published 2026-09-19, affects even 2.8.4), plus CVE-2026-66046,
#     -76956, -76957. CPython has merged expat 2.8.4 to the 3.12 branch
#     but NO RELEASE CARRIES IT — verified: the newest tag is v3.12.14.
#     A refresh will fix this the day 3.12.15 ships and not one day
#     before. This is the sharpest open item for fapd-backend, which
#     runs ElementTree.fromstring over fetched government XML.
#   - CVE-2026-53266 (kernel, CISA KEV). Host-level, no fixed GA kernel
#     exists. Verified unreachable here: ebtables is empty in every
#     chain of both filter and nat tables and no ebtables module is
#     loaded at all.
#
# NOT IN THIS SCRIPT: spiralyst-proxy and spiralyst-static. They run the
# same Alpine base and carry the identical libuuid/xz/nginx rows, and
# the proxy TERMINATES TLS for fapd.info — the more exposed of the two.
# They are the cohabitant's, deployed from the operator's private tree.
# Our half is not the whole bump; the parity step is run separately the
# same day.
#
# Rollback: `docker tag fapd-backend:pre-20260921 fapd-backend:latest`
# then `docker compose --profile backend up -d --no-build backend`; for
# web, `docker tag <recorded id> nginx:1.30-alpine` and force-recreate.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VPS_SSH="$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh"
STAMP=20260921

say() { printf '\n== %s ==\n' "$1"; }

say "0. Preconditions"
# A backend rebuild destroys /app/.git (writable layer; digests/ and
# provenance/ are volumes). An unpushed evidence commit would go with it.
UNPUSHED=$("$VPS_SSH" 'sudo docker exec fapd-backend sh -lc "cd /app && \
  export GIT_SSH_COMMAND=\"ssh -i /app/secrets/deploy_key -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=accept-new\" && git fetch -q origin main && \
  git rev-list --count origin/main..HEAD"' | tr -d '[:space:]')
echo "unpushed evidence commits: $UNPUSHED"
if [ "$UNPUSHED" != "0" ]; then
  echo "ABORT: $UNPUSHED unpushed evidence commit(s). Push them first" >&2
  echo "       (deploy/vps/scripts/evidence-commit.sh in the container)." >&2
  exit 1
fi

# The EOD finalizer runs ~04:00 UTC. Rebuilding under it wastes a day's
# tokens and can strand a half-rendered day.
HOUR=$(date -u +%H)
if [ "$HOUR" = "03" ] || [ "$HOUR" = "04" ]; then
  echo "ABORT: ${HOUR}:xx UTC is the EOD finalizer window. Run outside it." >&2
  exit 1
fi

say "1. Before: what we are moving from"
"$VPS_SSH" 'echo "--- backend ---"; sudo docker exec fapd-backend sh -lc \
  "dpkg -l | grep -E \"^ii  (libc6|libc-bin|libpcre2-8-0|libsqlite3-0|gzip|libexpat1) \" | awk \"{print \\\$2, \\\$3}\""
echo "--- fapd-web ---"; sudo docker exec fapd-web sh -lc \
  "nginx -v 2>&1; apk info -v | grep -E \"^(libuuid|xz-libs|libssl3)-\" | sort"
echo "--- image ages ---"
sudo docker image inspect python:3.12-slim --format "python:3.12-slim created {{.Created}}"
sudo docker image inspect nginx:1.30-alpine --format "nginx:1.30-alpine created {{.Created}}"'

say "2. Rollback artifacts"
"$VPS_SSH" "sudo docker tag fapd-backend:latest fapd-backend:pre-$STAMP && \
  echo 'backend retagged: fapd-backend:pre-$STAMP'
  sudo docker image inspect nginx:1.30-alpine --format 'nginx rollback id: {{.Id}}' | tee /tmp/nginx-rollback-$STAMP.txt"

say "3. Pull both bases"
"$VPS_SSH" 'sudo docker pull python:3.12-slim && sudo docker pull nginx:1.30-alpine'

say "4. Rebuild backend AND mcp with --pull (parity rule: shared base)"
"$VPS_SSH" 'cd /opt/fapd && sudo docker compose --profile backend build --pull backend mcp'

say "5. Recreate"
# `up -d` will NOT replace a running container whose image tag is
# unchanged, even after a successful pull. web must be forced.
"$VPS_SSH" 'cd /opt/fapd && sudo docker compose --profile backend up -d backend mcp && \
  sudo docker compose up -d --force-recreate web'

say "6. Site handoff"
# Named volumes seed from the image only when empty (F-009 / OB-19), so
# a rebuild outside deploy.sh must re-run this or the site goes stale.
# build_today() takes an open connection — calling it bare raises
# TypeError, which this script did on its first run (2026-09-21).
"$VPS_SSH" 'sudo docker exec fapd-backend /app/.venv/bin/python /app/scripts/build_site.py && \
  sudo docker exec fapd-backend /app/.venv/bin/python -c \
  "from fapd import db, publish; publish.build_today(db.connect())"' || \
  echo "WARN: site handoff failed — run it by hand before trusting the site"

say "7. Verify by reading the runtime, not the tag"
"$VPS_SSH" 'echo "--- backend ---"; sudo docker exec fapd-backend sh -lc \
  "dpkg -l | grep -E \"^ii  (libc6|libc-bin|libpcre2-8-0|libsqlite3-0|gzip|libexpat1) \" | awk \"{print \\\$2, \\\$3}\""
sudo docker exec fapd-backend python -c "import pyexpat; print(\"bundled expat:\", pyexpat.EXPAT_VERSION)"
sudo docker exec fapd-backend python --version
echo "--- fapd-web ---"; sudo docker exec fapd-web sh -lc \
  "nginx -v 2>&1; apk info -v | grep -E \"^(libuuid|xz-libs|libssl3)-\" | sort"
echo "--- containers ---"; sudo docker ps --format "{{.Names}}\t{{.Status}}" | grep fapd
echo "--- mcp invariants ---"; sudo docker port fapd-mcp; echo "(empty above = no published port, correct)"
sudo docker inspect fapd-mcp --format "ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} CapDrop={{.HostConfig.CapDrop}} User={{.Config.User}}"'

say "8. Service checks"
curl -sI https://fapd.info | head -1
curl -sS -o /dev/null -w 'api-catalog: %{http_code}\n' https://fapd.info/.well-known/api-catalog
curl -sI https://fapd.info/mcp | head -1
echo
echo "Expected: HTTP/2 200 / 200 / HTTP/2 405."
echo "Then re-run the OPS-GUIDE VPS block, and again ~5 minutes later"
echo "(cadence rule). Remember the cohabitant parity step."

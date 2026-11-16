# fapd-web: the official nginx image, patched. Built by both stacks (prod
# compose and the dev stack), so the two keep one pin.
#
# Why a local build and not the plain official image (re-measured
# 2026-11-16): the official nginx:1.30.6-alpine build of 2026-11-05 now
# carries the brotli-libs and curl fixes this build was first written for
# (CVE sweep 2026-10-30; CVE-2026-111497 is on CISA's Known Exploited
# Vulnerabilities list), but it still lacks five Alpine fixes that the
# 3.24 repository already has (libxslt 1.1.43-r4, zlib 1.4-r0), and the
# image running before this rebuild lacked nine (expat 2.10.0-r0 as well).
# `apk upgrade` at build time installs whatever Alpine has fixed since the
# official image was built, so the running image never trails the
# distribution; the base stays pinned by hash so a rebuild is reproducible
# and a refresh is a visible one-line change. Re-pin at each sweep.
#
# nginx itself is untouched: the guard fails the build if it moved off the
# stable 1.30.6 (parity with the edge proxy), and the `need` lines fail it
# if a fixed library is missing, so a stale layer cache cannot pass. Raise
# a floor when a sweep finds a newer fix; never lower one.
FROM nginx:1.30.6-alpine@sha256:901e593c95dc85f5a729f5765516321366ef4ac401821431d408897e95287d0a
RUN set -eu; \
    apk upgrade --no-cache; \
    need() { v="$(apk info -v 2>/dev/null | grep -E "^$1-[0-9]" | head -n1)"; v="${v#"$1"-}"; \
             [ -n "$v" ] || { echo "$1 is not installed" >&2; exit 1; }; \
             if [ "$(apk version -t "$v" "$2")" = "<" ]; then echo "$1 $v is below $2" >&2; exit 1; fi; \
             echo "ok $1 $v (>= $2)"; }; \
    need brotli-libs 1.2.1-r0; need libcurl 8.23.0-r0; need curl 8.23.0-r0; \
    need libexpat 2.10.0-r0; need libxslt 1.1.43-r4; need zlib 1.4-r0; \
    nginx -v 2>&1 | grep -q 'nginx/1.30.6$' || { echo "nginx is no longer 1.30.6" >&2; exit 1; }

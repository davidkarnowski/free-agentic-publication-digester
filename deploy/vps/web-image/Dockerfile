# fapd-web: the official nginx image, patched. Built by both stacks (prod
# compose and the dev stack), so the two keep one pin.
#
# 2026-11-18: nginx 1.30.7, the stable security release of that day (eight
# CVEs; fapd-web sits behind the edge on plain HTTP/1.1 with no alias,
# subrequests, HTTP/2, HTTP/3, mail or stream, so few of them reach it, but
# the parity rule moves it with the edge proxy, which moved the same day).
# The official 1.30.7-alpine build of that day still lacks one Alpine fix
# (zlib 1.4-r0), so the local build stays.
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
# stable 1.30.7 (parity with the edge proxy), and the `need` lines fail it
# if a fixed library is missing, so a stale layer cache cannot pass. Raise
# a floor when a sweep finds a newer fix; never lower one.
#
# 2026-11-20 (1.30.7-p2): the same build, rebuilt for Alpine fixes that
# landed after p1. openssl 3.5.9-r1 (shipped 2026-11-18 23:31 UTC, after the
# p1 build) fixes CVE-2026-107496 (CMS), CVE-2026-88822 and CVE-2026-95691
# (QUIC) and CVE-2026-88823 and CVE-2026-95692 (AES-GCM-SIV); libxml2
# 2.13.9-r3 (shipped 2026-11-20) fixes CVE-2026-86144. None is reachable
# here: fapd-web has no QUIC listener and does no CMS encryption, and no
# nginx process loads libxml2. nginx links libssl3/libcrypto3, though, and
# the rule is to rebuild when fixes land, so the floors rise. Base digest and
# nginx unchanged.
FROM nginx:1.30.7-alpine@sha256:b24de00298eb7fb23839442d46c780991be7bc7ddb081b6c0876ac777012e352
RUN set -eu; \
    apk upgrade --no-cache; \
    need() { v="$(apk info -v 2>/dev/null | grep -E "^$1-[0-9]" | head -n1)"; v="${v#"$1"-}"; \
             [ -n "$v" ] || { echo "$1 is not installed" >&2; exit 1; }; \
             if [ "$(apk version -t "$v" "$2")" = "<" ]; then echo "$1 $v is below $2" >&2; exit 1; fi; \
             echo "ok $1 $v (>= $2)"; }; \
    need brotli-libs 1.2.1-r0; need libcurl 8.23.0-r0; need curl 8.23.0-r0; \
    need libexpat 2.10.0-r0; need libxslt 1.1.43-r4; need zlib 1.4-r0; \
    need libssl3 3.5.9-r1; need libcrypto3 3.5.9-r1; need libxml2 2.13.9-r3; \
    nginx -v 2>&1 | grep -q 'nginx/1.30.7$' || { echo "nginx is no longer 1.30.7" >&2; exit 1; }

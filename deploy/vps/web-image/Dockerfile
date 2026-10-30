# fapd-web: the official nginx image, patched. Built by both stacks (prod
# compose and the dev stack), so the two keep one pin.
#
# CVE sweep 2026-10-30: the official nginx:1.30.6-alpine image still ships
# brotli-libs 1.2.0-r1 (CVE-2026-111497, Google Brotli decoder memory
# corruption, on CISA's Known Exploited Vulnerabilities list since
# 2026-10-27) and curl 8.22.0-r0, while Alpine 3.24 already carries
# brotli-libs 1.2.1-r0 and curl 8.23.0-r0. nginx itself does not link
# Brotli (the library arrives through libcurl and freetype), so traffic
# does not reach it; this is defence in depth for a KEV-listed library.
# Measured on the production host: `apk upgrade` changes exactly those
# three packages and leaves nginx at 1.30.6.
#
# TEMPORARY (operator, 2026-10-30): return to the plain official digest
# pin, `image: nginx:<ver>-alpine@sha256:...` in both compose files, as
# soon as the official tag ships brotli-libs >= 1.2.1-r0 and
# curl >= 8.23.0-r0. The guard fails the build if the fixed packages are
# missing or nginx moved off 1.30.6, so a stale cache cannot pass.
FROM nginx:1.30.6-alpine@sha256:47928bf67eb62a1863cb08d9ecb52d3e704304ba614eaee17884204677702951
RUN set -eu; \
    apk upgrade --no-cache; \
    need() { v="$(apk info -v 2>/dev/null | grep -E "^$1-[0-9]" | head -n1)"; v="${v#"$1"-}"; \
             [ -n "$v" ] || { echo "$1 is not installed" >&2; exit 1; }; \
             if [ "$(apk version -t "$v" "$2")" = "<" ]; then echo "$1 $v is below $2" >&2; exit 1; fi; \
             echo "ok $1 $v (>= $2)"; }; \
    need brotli-libs 1.2.1-r0; need libcurl 8.23.0-r0; need curl 8.23.0-r0; \
    nginx -v 2>&1 | grep -q 'nginx/1.30.6$' || { echo "nginx is no longer 1.30.6" >&2; exit 1; }

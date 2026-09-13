#!/usr/bin/env bash
# deploy/vps/nginx/rehearse.sh — the LOCAL proof of the fapd-web config.
#
# Builds a fixture site with the real renderer, runs the pinned nginx
# image in a throwaway container with this directory mounted exactly as
# production mounts it, and drives the request matrix from
# docs/ops/plan-2026-09-13-phase3-web-config.md §3.5 against it. Every
# row records PASS / FAIL / SKIP; the script ends in SUCCESS or
# FAILURE: <rows> with a non-zero exit (AGENT-VPS-SERVICING-GUIDE §2).
#
# This script never contacts the VPS. It needs the local Docker daemon,
# uv, curl, and the repo root; nothing else. Run it before any deploy
# that touches deploy/vps/nginx/.
#
# Planting rule: routing is proven on its own. When a document another
# phase builds (the discovery files, the Markdown twins, the signpost
# body) is not in the fixture yet, a minimal stand-in is planted and a
# WARNING names it — so the same script is honest before and after
# Phases 1–2 merge. favicon.ico is never planted (row 18 is SKIP until
# Phase 1 builds it).
set -u
cd "$(dirname "$0")/../../.."   # repo root (nginx -> vps -> deploy -> root)

NAME=fapd-web-rehearsal
PORT=18080
BASE="http://127.0.0.1:${PORT}"
IMAGE=nginx:1.30-alpine          # the web service's pin; bump together

PASSES=0; FAILS=(); SKIPS=(); WARNINGS=0
ok()   { PASSES=$((PASSES + 1)); echo "  PASS  $1"; }
fail() { FAILS+=("$1"); echo "  FAIL  $1"; }
skip() { SKIPS+=("$1"); echo "  SKIP  $1"; }
warn() { WARNINGS=$((WARNINGS + 1)); echo "  WARNING: $1"; }
# verdict "<row>" <0|1>: 1 is pass. Keeps every row to one line of intent.
verdict() { if [ "$2" = 1 ]; then ok "$1"; else fail "$1"; fi; }

TMP=""
cleanup() {
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  [ -n "$TMP" ] && rm -rf "$TMP"
}
trap cleanup EXIT

echo "== 1. preconditions (local machine only) =="
missing=0
for tool in docker uv curl cmp; do
  command -v "$tool" >/dev/null 2>&1 || { echo "  missing tool: $tool"; missing=1; }
done
[ "$missing" = 0 ] || { echo "FAILURE: preconditions"; exit 1; }
docker info >/dev/null 2>&1 || { echo "  docker daemon not reachable"; echo "FAILURE: preconditions"; exit 1; }
[ -f pyproject.toml ] && [ -f deploy/vps/nginx/default.conf ] \
  || { echo "  not at the repo root"; echo "FAILURE: preconditions"; exit 1; }
if docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "  removing a stale $NAME from an earlier run"
  docker rm -f "$NAME" >/dev/null
fi
echo "  ok"

echo "== 2. fixture site (real renderer into a temp dir) =="
TMP=$(mktemp -d "${TMPDIR:-/tmp}/fapd-rehearsal.XXXXXX")
SITE="$TMP/site"
uv run python -c "from fapd import publish; publish.build_site(out_dir='$SITE')" >/dev/null \
  || { echo "  build_site failed"; echo "FAILURE: fixture"; exit 1; }
DATE=$(ls digests/????-??-??.md | tail -1 | xargs basename | sed 's/\.md$//')
echo "  built $(find "$SITE" -type f | wc -l | tr -d ' ') files; fixture digest date: $DATE"

# plant <relative path> <content>  — only if absent; one WARNING each.
plant() {
  if [ ! -e "$SITE/$1" ]; then
    mkdir -p "$(dirname "$SITE/$1")"
    printf '%s\n' "$2" > "$SITE/$1"
    warn "planted $1 (its phase has not merged; routing is proven on a stand-in)"
  fi
}
plant ".well-known/agent-skills/x/SKILL.md"  "# x"
plant "_signpost/not-offered.json"           '{"status": "not offered", "see": ["/agents.html", "/.well-known/api-catalog"]}'
plant "index.md"                             "# FAPD (stand-in twin)"
plant "auth.md"                              "# Authentication: none"
plant ".well-known/api-catalog"              '{"linkset": []}'
plant ".well-known/ai-catalog.json"          '{"stand-in": true}'
plant "today.html"                           "<!DOCTYPE html><title>today</title>"
if [ ! -e "$SITE/$DATE.md" ]; then
  cp "digests/$DATE.md" "$SITE/$DATE.md"
  warn "planted $DATE.md as a copy of digests/$DATE.md (Phase 2 not merged)"
fi
plant "robots.txt"   "User-agent: *"
plant "digests.json" "$(printf '{"stand_in": true, "pad": "%s"}' "$(head -c 1200 /dev/zero | tr '\0' x)")"
SKILL=$(cd "$SITE/.well-known/agent-skills" && ls -d */ | head -1 | tr -d /)

echo "== 3. throwaway container: $IMAGE, this directory as /etc/nginx/conf.d =="
docker run --rm -d --name "$NAME" -p "127.0.0.1:${PORT}:80" \
  -v "$PWD/deploy/vps/nginx:/etc/nginx/conf.d:ro" \
  -v "$SITE:/usr/share/nginx/html:ro" "$IMAGE" >/dev/null \
  || { echo "  docker run failed"; echo "FAILURE: container"; exit 1; }
TEST_OUT=$(docker exec "$NAME" nginx -t 2>&1)
echo "$TEST_OUT" | sed 's/^/  /'
verdict "0  nginx -t succeeds" "$(echo "$TEST_OUT" | grep -q 'test is successful' && echo 1 || echo 0)"
verdict "0b nginx -t emits no [warn]/[emerg]" "$(echo "$TEST_OUT" | grep -qE '\[(warn|emerg)\]' && echo 0 || echo 1)"
for _ in $(seq 1 50); do curl -fs -o /dev/null "$BASE/" && break; sleep 0.2; done

echo "== 4. the request matrix (phase file §3.5) =="
H="$TMP/hdr"; B="$TMP/body"; STATUS=""
# get <path> [curl args…]: STATUS + headers in $H + body in $B
get() { local p=$1; shift; STATUS=$(curl -sS -o "$B" -D "$H" -w '%{http_code}' "$@" "$BASE$p"); }
hdr() { grep -i "^$1:" "$H" | sed 's/^[^:]*: *//' | tr -d '\r' | paste -s -d ',' -; }
has() { case "$1" in *"$2"*) return 0;; *) return 1;; esac; }
LINK_RELS='rel="api-catalog" rel="service-desc" rel="service-doc" rel="describedby" rel="ai-catalog"'
all_rels() { local l; l=$(hdr link); for r in $LINK_RELS; do has "$l" "$r" || return 1; done; }

get /
verdict "1  GET / -> 200 text/html, all five Link rels, Vary: Accept" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/html && all_rels && has "$(hdr vary)" Accept && echo 1 || echo 0)"

get / -H 'Accept: text/markdown'
verdict "2  GET / (Accept: text/markdown) -> 200 text/markdown; charset=utf-8, body == index.md" \
  "$([ "$STATUS" = 200 ] && [ "$(hdr content-type)" = "text/markdown; charset=utf-8" ] && cmp -s "$B" "$SITE/index.md" && echo 1 || echo 0)"

get "/$DATE.html" -H 'Accept: text/markdown'
verdict "3  GET /$DATE.html (Accept: text/markdown) -> body byte-equals digests/$DATE.md" \
  "$([ "$STATUS" = 200 ] && cmp -s "$B" "digests/$DATE.md" && echo 1 || echo 0)"

get /today.html -H 'Accept: text/markdown'
verdict "4  GET /today.html (Accept: text/markdown) -> text/html, not negotiated, not 404" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/html && echo 1 || echo 0)"

get / -H 'Accept: text/html,application/xhtml+xml,*/*;q=0.8'
verdict "5  GET / (browser Accept) -> text/html" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/html && echo 1 || echo 0)"

get /.well-known/api-catalog
verdict "6  GET /.well-known/api-catalog -> 200 application/linkset+json, ACAO *" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" application/linkset+json && [ "$(hdr access-control-allow-origin)" = "*" ] && echo 1 || echo 0)"

get /.well-known/ai-catalog.json
verdict "7  GET /.well-known/ai-catalog.json -> 200 application/ai-catalog+json, ACAO *" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" application/ai-catalog+json && [ "$(hdr access-control-allow-origin)" = "*" ] && echo 1 || echo 0)"

get "/.well-known/agent-skills/$SKILL/SKILL.md"
verdict "8  GET /.well-known/agent-skills/$SKILL/SKILL.md -> 200 text/markdown" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/markdown && echo 1 || echo 0)"

get /.well-known/mcp/server-cards.json
verdict "9  GET /.well-known/mcp/server-cards.json -> 404 application/json, signpost body, ACAO *" \
  "$([ "$STATUS" = 404 ] && has "$(hdr content-type)" application/json && grep -q '"status": "not offered"' "$B" && [ "$(hdr access-control-allow-origin)" = "*" ] && echo 1 || echo 0)"

get /.well-known/oauth-authorization-server
verdict "10 GET /.well-known/oauth-authorization-server -> 404 + signpost" \
  "$([ "$STATUS" = 404 ] && grep -q '"status": "not offered"' "$B" && echo 1 || echo 0)"

get /_signpost/not-offered.json
verdict "11 GET /_signpost/not-offered.json directly -> 404 (internal), signpost NOT served" \
  "$([ "$STATUS" = 404 ] && ! grep -q 'not offered' "$B" && echo 1 || echo 0)"
B11="$TMP/body11"; cp "$B" "$B11"

get /.git/config; s_a=$STATUS
get /.env;        s_b=$STATUS
verdict "12 GET /.git/config, GET /.env -> 404, 404" "$([ "$s_a" = 404 ] && [ "$s_b" = 404 ] && echo 1 || echo 0)"
B12="$TMP/body12"; cp "$B" "$B12"

get /index.html -X POST
verdict "13 POST /index.html -> 405" "$([ "$STATUS" = 405 ] && echo 1 || echo 0)"

get /auth.md
verdict "14 GET /auth.md -> 200 text/markdown, ACAO *, Link present" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/markdown && [ "$(hdr access-control-allow-origin)" = "*" ] && all_rels && echo 1 || echo 0)"

get /digests.json -H 'Accept-Encoding: gzip'
verdict "15 GET /digests.json (Accept-Encoding: gzip) -> 200, ACAO *, Content-Encoding: gzip" \
  "$([ "$STATUS" = 200 ] && [ "$(hdr access-control-allow-origin)" = "*" ] && [ "$(hdr content-encoding)" = "gzip" ] && echo 1 || echo 0)"

get /robots.txt
verdict "16 GET /robots.txt -> 200 text/plain, ACAO *" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/plain && [ "$(hdr access-control-allow-origin)" = "*" ] && echo 1 || echo 0)"

verdict "17 404 bodies carry no nginx/1. version string; Server header is bare" \
  "$(! grep -q 'nginx/1\.' "$B11" "$B12" && [ "$(hdr server)" = "nginx" ] && echo 1 || echo 0)"

if [ -e "$SITE/favicon.ico" ]; then
  get /favicon.ico
  verdict "18 GET /favicon.ico -> 200" "$([ "$STATUS" = 200 ] && echo 1 || echo 0)"
else
  skip "18 GET /favicon.ico — not in the fixture (Phase 1 AD-8 builds it); not planted by rule"
fi

# Beyond the plan's table: the traps the phase file names, each proven.
get "/$DATE.html" -H 'Accept: text/markdown;q=0'
verdict "19 SR-1: Accept: text/markdown;q=0 is a refusal -> text/html" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/html && echo 1 || echo 0)"

get "/$DATE.html" -H 'Accept: text/html, text/markdown;q=0.8'
verdict "20 Accept: text/html, text/markdown;q=0.8 -> negotiated to Markdown" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/markdown && echo 1 || echo 0)"

get / -I
verdict "21 HEAD / -> 200" "$([ "$STATUS" = 200 ] && echo 1 || echo 0)"

get /
edge_dupes=0
for h in strict-transport-security x-frame-options x-content-type-options referrer-policy; do
  [ -z "$(hdr "$h")" ] || edge_dupes=1
done
verdict "22 no edge-owned security header is duplicated by fapd-web" "$([ "$edge_dupes" = 0 ] && echo 1 || echo 0)"

get "/$DATE.html"
verdict "23 GET /$DATE.html -> 200 text/html with Link (digest pages carry discovery too)" \
  "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/html && all_rels && echo 1 || echo 0)"

SRC=$(ls "$SITE/sources/"*.html 2>/dev/null | head -1 | xargs -r basename | sed 's/\.html$//')
if [ -n "$SRC" ] && [ -e "$SITE/sources/$SRC.md" ]; then
  get "/sources/$SRC.html" -H 'Accept: text/markdown'
  verdict "24 GET /sources/$SRC.html (Accept: text/markdown) -> 200 text/markdown" \
    "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" text/markdown && echo 1 || echo 0)"
else
  skip "24 /sources/<id>.html negotiation — no sources/<id>.md twin in the fixture (Phase 2 builds them)"
fi

echo "== 5. verdict =="
echo "  passes: $PASSES  fails: ${#FAILS[@]}  skips: ${#SKIPS[@]}  warnings: $WARNINGS"
if [ "${#FAILS[@]}" = 0 ]; then
  echo "SUCCESS"
  exit 0
fi
echo "FAILURE: $(printf '%s; ' "${FAILS[@]}")"
exit 1

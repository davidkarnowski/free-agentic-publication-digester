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
#
# Phase 4B (rows M1–M17): the fapd-mcp image is built from
# packages/static-mcp and run beside the web container the way
# production runs it — a second, --internal throwaway network shared by
# the two, no published port, read-only rootfs, uid 10001, all
# capabilities dropped, the dev manifest (deploy/dev/mcp) so 127.0.0.1
# passes the Host check — and the /mcp access log lands in a temp
# directory mounted at /var/log/fapd (nginx opens every access_log at
# config time, so the mount is what lets `nginx -t` pass at all).
set -u
cd "$(dirname "$0")/../../.."   # repo root (nginx -> vps -> deploy -> root)

NAME=fapd-web-rehearsal
MCP=fapd-mcp-rehearsal
NET_EDGE=fapd-rehearsal-edge     # web + the published test port
NET_MCP=fapd-rehearsal-mcp       # --internal: web + mcp, nothing else
PORT=18080
BASE="http://127.0.0.1:${PORT}"
IMAGE=nginx:1.30-alpine          # the web service's pin; bump together
MCP_IMAGE=fapd-mcp:rehearsal     # built here from packages/static-mcp

PASSES=0; FAILS=(); SKIPS=(); WARNINGS=0
ok()   { PASSES=$((PASSES + 1)); echo "  PASS  $1"; }
fail() { FAILS+=("$1"); echo "  FAIL  $1"; }
skip() { SKIPS+=("$1"); echo "  SKIP  $1"; }
warn() { WARNINGS=$((WARNINGS + 1)); echo "  WARNING: $1"; }
# verdict "<row>" <0|1>: 1 is pass. Keeps every row to one line of intent.
verdict() { if [ "$2" = 1 ]; then ok "$1"; else fail "$1"; fi; }

TMP=""
cleanup() {
  docker rm -f "$NAME" "$MCP" >/dev/null 2>&1 || true
  docker network rm "$NET_EDGE" "$NET_MCP" >/dev/null 2>&1 || true
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
for stale in "$NAME" "$MCP"; do
  if docker ps -a --format '{{.Names}}' | grep -qx "$stale"; then
    echo "  removing a stale $stale from an earlier run"
    docker rm -f "$stale" >/dev/null
  fi
done
docker network rm "$NET_EDGE" "$NET_MCP" >/dev/null 2>&1 || true
[ -f deploy/dev/mcp/fapd.manifest.json ] && [ -f packages/static-mcp/Dockerfile ] \
  || { echo "  missing the dev manifest or the static-mcp Dockerfile"; echo "FAILURE: preconditions"; exit 1; }
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
# Phase 4C builds the two MCP signposts; planted until it merges.
plant "_signpost/mcp-method.json"      '{"status": "method not allowed", "see": "/agents.html#mcp"}'
plant "_signpost/mcp-unavailable.json" '{"status": "mcp unavailable", "see": "/llms.txt"}'
SKILL=$(cd "$SITE/.well-known/agent-skills" && ls -d */ | head -1 | tr -d /)
mkdir -p "$TMP/logs"

echo "== 3. throwaway containers: $IMAGE + $MCP_IMAGE on two throwaway networks =="
docker network create "$NET_EDGE" >/dev/null || { echo "FAILURE: network"; exit 1; }
docker network create --internal "$NET_MCP" >/dev/null || { echo "FAILURE: network"; exit 1; }
docker build -q -t "$MCP_IMAGE" packages/static-mcp >/dev/null \
  || { echo "  docker build of the static-mcp image failed"; echo "FAILURE: mcp image"; exit 1; }
# The same hardening flags the compose service carries (pinned there by
# tests/test_dev_stack.py); M11 reads them back from docker inspect.
docker run -d --name "$MCP" --network "$NET_MCP" --network-alias fapd-mcp \
  --read-only --user 10001:10001 --cap-drop ALL --security-opt no-new-privileges:true \
  --pids-limit 64 \
  -v "$SITE:/srv/site:ro" -v "$PWD/deploy/dev/mcp:/etc/static-mcp:ro" \
  "$MCP_IMAGE" --manifest /etc/static-mcp/fapd.manifest.json >/dev/null \
  || { echo "  docker run (mcp) failed"; echo "FAILURE: mcp container"; exit 1; }
docker run --rm -d --name "$NAME" --network "$NET_EDGE" -p "127.0.0.1:${PORT}:80" \
  -v "$PWD/deploy/vps/nginx:/etc/nginx/conf.d:ro" \
  -v "$SITE:/usr/share/nginx/html:ro" \
  -v "$TMP/logs:/var/log/fapd" "$IMAGE" >/dev/null \
  || { echo "  docker run failed"; echo "FAILURE: container"; exit 1; }
docker network connect "$NET_MCP" "$NAME" || { echo "FAILURE: network connect"; exit 1; }
for _ in $(seq 1 50); do
  docker exec "$MCP" python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=1)" >/dev/null 2>&1 && break
  sleep 0.2
done
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

echo "== 4b. the MCP rows (phase 4 file §B.4, M1–M17) =="
# mcp_post <body> [curl args…]: a JSON POST to /mcp through the web container.
mcp_post() { local body=$1; shift; get /mcp -X POST -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' --data-binary "$body" "$@"; }
# pycheck '<python expression over b (the decoded body)>' -> 1 or 0
pycheck() { uv run python -c "import json,sys; b=json.load(open(sys.argv[1])); print(1 if ($1) else 0)" "$B" 2>/dev/null || echo 0; }
META='"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"rehearse","version":"1"},"io.modelcontextprotocol/clientCapabilities":{}}'
MODERN_H=(-H 'MCP-Protocol-Version: 2026-07-28')
MCP_REQ=0                        # every request that reaches /mcp (for M16)

mcp_post "{\"jsonrpc\":\"2.0\",\"id\":\"m1\",\"method\":\"server/discover\",\"params\":{$META}}" \
  "${MODERN_H[@]}" -H 'Mcp-Method: server/discover'; MCP_REQ=$((MCP_REQ + 1))
verdict "M1 modern server/discover -> 200, supportedVersions has 2026-07-28, serverInfo info.fapd/fapd" \
  "$([ "$STATUS" = 200 ] && [ "$(pycheck "'2026-07-28' in b['result']['supportedVersions'] and b['result']['_meta']['io.modelcontextprotocol/serverInfo']['name'] == 'info.fapd/fapd'")" = 1 ] && echo 1 || echo 0)"

mcp_post '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"rehearse","version":"1"}}}'; MCP_REQ=$((MCP_REQ + 1))
verdict "M2 legacy initialize 2025-06-18 -> 200, protocolVersion echoed, no Mcp-Session-Id" \
  "$([ "$STATUS" = 200 ] && [ "$(pycheck "b['result']['protocolVersion'] == '2025-06-18'")" = 1 ] && [ -z "$(hdr mcp-session-id)" ] && echo 1 || echo 0)"

mcp_post "{\"jsonrpc\":\"2.0\",\"id\":\"m3\",\"method\":\"tools/call\",\"params\":{\"name\":\"get_digest\",\"arguments\":{\"date\":\"$DATE\"},$META}}" \
  "${MODERN_H[@]}" -H 'Mcp-Method: tools/call' -H 'Mcp-Name: get_digest'; MCP_REQ=$((MCP_REQ + 1))
uv run python -c "import json,sys; b=json.load(open(sys.argv[1])); open(sys.argv[2],'w').write(b['result']['content'][1]['text'])" "$B" "$TMP/m3.md" 2>/dev/null || : > "$TMP/m3.md"
verdict "M3 modern tools/call get_digest $DATE -> 200, text after the preamble == digests/$DATE.md" \
  "$([ "$STATUS" = 200 ] && cmp -s "$TMP/m3.md" "digests/$DATE.md" && echo 1 || echo 0)"

get /mcp; MCP_REQ=$((MCP_REQ + 1))
verdict "M4 GET /mcp -> 405, JSON signpost body" \
  "$([ "$STATUS" = 405 ] && has "$(hdr content-type)" application/json && grep -q 'agents.html#mcp' "$B" && echo 1 || echo 0)"

head -c 102400 /dev/zero | tr '\0' x > "$TMP/big.json"
get /mcp -X POST -H 'Content-Type: application/json' --data-binary "@$TMP/big.json"; MCP_REQ=$((MCP_REQ + 1))
verdict "M5 POST /mcp with a 100 KB body -> 413" "$([ "$STATUS" = 413 ] && echo 1 || echo 0)"

mcp_post "{\"jsonrpc\":\"2.0\",\"id\":\"m6\",\"method\":\"server/discover\",\"params\":{$META}}" \
  "${MODERN_H[@]}" -H 'Mcp-Method: server/discover' -H 'Origin: https://evil.example'; MCP_REQ=$((MCP_REQ + 1))
verdict "M6 POST /mcp with Origin: https://evil.example -> 403" "$([ "$STATUS" = 403 ] && echo 1 || echo 0)"

n429=0
for _ in $(seq 1 60); do
  mcp_post '{"jsonrpc":"2.0","method":"notifications/initialized"}' -H 'X-Real-IP: 203.0.113.8'
  [ "$STATUS" = 429 ] && n429=$((n429 + 1))
done
MCP_REQ=$((MCP_REQ + 60))
verdict "M8 60 rapid POSTs from one X-Real-IP -> some 429s (got $n429)" "$([ "$n429" -gt 0 ] && echo 1 || echo 0)"

if [ -e "$SITE/mcp/server-card" ]; then
  get /mcp/server-card
  verdict "M9 GET /mcp/server-card -> 200 application/mcp-server-card+json" \
    "$([ "$STATUS" = 200 ] && has "$(hdr content-type)" application/mcp-server-card+json && echo 1 || echo 0)"
else
  skip "M9 GET /mcp/server-card — not in the fixture (Phase 4C builds it); not planted by rule"
fi

if docker exec "$MCP" python -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=3)" >/dev/null 2>&1; then
  verdict "M10 outbound request from inside fapd-mcp fails (no egress)" 0
else
  verdict "M10 outbound request from inside fapd-mcp fails (no egress)" 1
fi

# HostConfig.PortBindings, not NetworkSettings.Ports: the latter lists the
# Dockerfile's EXPOSE 8080 (unbound, null) and would count it as a port.
INSPECT=$(docker inspect "$MCP" --format '{{.HostConfig.ReadonlyRootfs}} {{.Config.User}} {{.HostConfig.CapDrop}} ports={{json .HostConfig.PortBindings}}')
verdict "M11 docker inspect fapd-mcp: ReadonlyRootfs true, user 10001, CapDrop ALL, no port bindings ($INSPECT)" \
  "$(echo "$INSPECT" | grep -qE '^true 10001:10001 \[ALL\] ports=(\{\}|null)$' && echo 1 || echo 0)"

get /mcp -X POST -H 'Content-Type: text/plain' --data-binary '{"jsonrpc":"2.0","id":1,"method":"ping"}'; MCP_REQ=$((MCP_REQ + 1))
verdict "M12 POST /mcp with Content-Type: text/plain -> 415 from nginx" "$([ "$STATUS" = 415 ] && echo 1 || echo 0)"

mcp_post "{\"jsonrpc\":\"2.0\",\"id\":\"m13\",\"method\":\"server/discover\",\"params\":{$META}}" \
  "${MODERN_H[@]}" -H 'Mcp-Method: server/discover' -H 'Host: evil.example'; MCP_REQ=$((MCP_REQ + 1))
verdict "M13 POST /mcp with Host: evil.example -> 403 from the service, JSON-RPC error without id" \
  "$([ "$STATUS" = 403 ] && [ "$(pycheck "'error' in b and 'id' not in b")" = 1 ] && echo 1 || echo 0)"

m14=1
DEEP="$(printf '[%.0s' $(seq 1 40))$(printf ']%.0s' $(seq 1 40))"
for body in "$DEEP" '{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":NaN}}' \
            '[{"jsonrpc":"2.0","id":1,"method":"ping"}]' \
            "{\"jsonrpc\":\"2.0\",\"id\":\"$(head -c 200 /dev/zero | tr '\0' i)\",\"method\":\"ping\"}"; do
  mcp_post "$body"; MCP_REQ=$((MCP_REQ + 1))
  { [ "$STATUS" = 400 ] && [ "$(pycheck "b.get('jsonrpc') == '2.0' and 'error' in b")" = 1 ]; } || m14=0
done
verdict "M14 40-deep nesting, NaN, batch array, 200-char id -> 400 each, well-formed JSON-RPC, no 5xx" "$m14"

# 12 connections held open in the location (headers complete, body pending)
# from one address, then one more: limit_conn 10 answers the extra with 429.
uv run python - "$PORT" "$TMP/m15.ready" "$TMP/m15.go" <<'PY' &
import socket, sys, time, os
port, ready, go = int(sys.argv[1]), sys.argv[2], sys.argv[3]
socks = []
for _ in range(12):
    s = socket.create_connection(("127.0.0.1", port), timeout=30)
    s.sendall(b"POST /mcp HTTP/1.1\r\nHost: 127.0.0.1\r\nX-Real-IP: 203.0.113.15\r\n"
              b"Content-Type: application/json\r\nContent-Length: 200\r\n\r\n{")
    socks.append(s)
open(ready, "w").close()
for _ in range(300):
    if os.path.exists(go):
        break
    time.sleep(0.1)
for s in socks:
    s.close()
PY
for _ in $(seq 1 100); do [ -e "$TMP/m15.ready" ] && break; sleep 0.1; done
sleep 0.5
mcp_post '{"jsonrpc":"2.0","method":"notifications/initialized"}' -H 'X-Real-IP: 203.0.113.15'
: > "$TMP/m15.go"; wait
# Only the connections nginx must answer count toward M16: the two the
# limit refused (429) and the extra one. The ten admitted uploads were
# aborted by the client mid-body; whether nginx writes a 400 line for an
# aborted upload is its choice and timing, not a property of our log.
MCP_REQ=$((MCP_REQ + 3))
verdict "M15 12 held-open connections from one address, then one more -> 429 (limit_conn)" \
  "$([ "$STATUS" = 429 ] && echo 1 || echo 0)"

LOGF="$TMP/logs/mcp-access.log"
docker stop "$MCP" >/dev/null
mcp_post "{\"jsonrpc\":\"2.0\",\"id\":\"m7\",\"method\":\"server/discover\",\"params\":{$META}}" \
  "${MODERN_H[@]}" -H 'Mcp-Method: server/discover'; s7=$STATUS; b7=$(grep -c 'llms.txt' "$B"); MCP_REQ=$((MCP_REQ + 1))
get /; s7b=$STATUS
verdict "M7 mcp container stopped: POST /mcp -> 503 with the mcp-unavailable signpost; GET / still 200" \
  "$([ "$s7" = 503 ] && [ "$b7" -gt 0 ] && [ "$s7b" = 200 ] && echo 1 || echo 0)"

sleep 1                          # let nginx finalize the last connections
LINES=$(wc -l < "$LOGF" | tr -d ' ')
BAD=$(grep -vcE '^[0-9a-fA-F.:]+ - \[[^]]+\] "[A-Z]+ /mcp HTTP/1\.[01]" [0-9]{3} ' "$LOGF" || true)
m16=$([ "$LINES" -ge "$MCP_REQ" ] && [ "$BAD" = 0 ] && ! grep -q 'jsonrpc' "$LOGF" && grep -q '^203\.0\.113\.8 ' "$LOGF" && echo 1 || echo 0)
[ "$m16" = 1 ] || { echo "  M16 status histogram:"; awk '{print $9}' "$LOGF" | sort | uniq -c | sed 's/^/    /'; echo "  M16 malformed lines: $BAD"; }
verdict "M16 /mcp access log: $LINES lines (>= $MCP_REQ requests), first field an address, no bodies, one line per request" "$m16"

# The jail filter lives in the operator's private host tree, not here
# (security configuration is applied to the box directly, 2026-09-14).
# Point FAPD_F2B_FILTER at that file to run M17; otherwise the row SKIPs.
if [ -n "${FAPD_F2B_FILTER:-}" ] && [ -f "$FAPD_F2B_FILTER" ]; then
M17=$(uv run python - "$LOGF" "$FAPD_F2B_FILTER" <<'PY'
import re, sys
log, conf = sys.argv[1], sys.argv[2]
pat = next(l.split("=", 1)[1].strip() for l in open(conf) if l.startswith("failregex"))
rx = re.compile(pat.replace("<HOST>", r"(?:::f{4,6}:)?(?P<host>[\w\-.:^_]*\w)"))
lines = open(log).read().splitlines()
hits = [l for l in lines if rx.search(l)]
want = [l for l in lines if re.search(r'" (400|403|405|413|415) ', l)]
never = [l for l in hits if re.search(r'" (200|202|404|429) ', l)]
print(1 if hits and hits == want and not never else 0, len(hits), len(lines))
PY
)
verdict "M17 fail2ban filter over the log matches exactly the 400/403/405/413/415 lines, none of the 200/202/404/429 ($M17)" \
  "$(echo "$M17" | grep -q '^1 ' && echo 1 || echo 0)"
else
skip "M17 fail2ban filter over the log — set FAPD_F2B_FILTER to the private host tree's filter.d/fapd-mcp.conf (the authoritative check is fail2ban-regex on the box)"
fi

echo "== 5. verdict =="
echo "  passes: $PASSES  fails: ${#FAILS[@]}  skips: ${#SKIPS[@]}  warnings: $WARNINGS"
if [ "${#FAILS[@]}" = 0 ]; then
  echo "SUCCESS"
  exit 0
fi
echo "FAILURE: $(printf '%s; ' "${FAILS[@]}")"
exit 1

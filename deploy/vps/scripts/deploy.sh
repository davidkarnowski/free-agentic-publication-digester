#!/usr/bin/env bash
# Deploy the FAPD stack to the VPS. The server pulls the pushed commit from
# GitHub and builds only what the change touched; nothing large leaves this
# machine. Authorization gate applies (deploy/vps/README.md): run only on
# the operator's explicit ask.
#
#   deploy/vps/scripts/deploy.sh          build backend, plus web or mcp when
#                                         the commit range touched them
#   deploy/vps/scripts/deploy.sh --all    build all three (base image refresh)
#
# Why the server pulls (operator, 2026-11-08: "There is nothing in this update
# that should require a large upload"). Until then this script rsynced the
# working tree INCLUDING .git to the box's staging copy. After a local repack
# the history went up again as one new pack, whatever the change: 139 MB for a
# three-file commit. The same commit is on GitHub already, and the repository
# is public, so the box fetches it anonymously. The rsync also never removed
# a path it excluded, so 266 MB of July agent worktrees (F-012) sat in the
# staging copy and was baked into every backend image; the checkout below is
# cleaned to exactly the commit's tracked files.
set -euo pipefail
cd "$(dirname "$0")/../../.."  # repo root (scripts -> vps -> deploy -> root)

# The connection: one resolver, shared with dev-seed.sh. Since 2026-11-10 it
# holds no coordinates at all; every call goes through an external
# connector that supplies the identity and the address (_env.sh). The public
# repo carries no server dossier facts (CLAUDE.md §13).
REPO_ROOT="$PWD"
# shellcheck source=/dev/null
. "$REPO_ROOT/deploy/vps/scripts/_env.sh"

ALL=0
case "${1:-}" in
  --all) ALL=1 ;;
  "") ;;
  *) echo "usage: deploy.sh [--all]" >&2; exit 2 ;;
esac
die() { echo "deploy: $*" >&2; exit 1; }
# One short ssh call per step: a long compound command loses its output when
# the connection drops, and then nobody knows how far it got (2026-11-08).
run() { box "$@"; }

echo "==> [0/4] preconditions"
# The box deploys what GitHub has, so main here must BE what GitHub has. A
# deploy from any other branch strands the evidence push (2026-10-25).
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || die "not on main"
git diff --quiet && git diff --cached --quiet || die "uncommitted changes to tracked files"
git fetch --quiet origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
  || die "main is not level with origin/main: push your commits, or pull the nightly evidence commit, first"
case "$(date -u +%H)" in
  03|04) die "03:00-05:00 UTC is the nightly build window" ;;
esac
TARGET="$(git rev-parse HEAD)"
# The floor: paths that must never reach an image even if an ignore rule is
# dropped by mistake. The box checks out only tracked files, so the floor
# holds as long as none of these is tracked.
while IFS= read -r p; do
  case "$p" in ''|'#'*) continue ;; esac
  p="${p%/}"
  if [ -n "$(git ls-files -- ":(glob)$p" ":(glob)$p/**" ":(glob)**/$p" ":(glob)**/$p/**")" ]; then
    die "a path on deploy/common/repo-excludes.txt is tracked: $p"
  fi
done < deploy/common/repo-excludes.txt

echo "==> [1/4] test gate"
uv run ruff check src/ scripts/ tests/ packages/
# An empty key stops the tests writing narration files into site/ (2026-10-08).
OPENAI_API_KEY= uv run pytest -q
git diff --quiet || die "the test run changed tracked files"

echo "==> [2/4] the box pulls ${TARGET:0:8} from GitHub"
# repo/ is only the backend's build context: no container reads it. Its
# origin is the public HTTPS URL, so the fetch needs no key; the image bakes
# the SSH remote for the evidence push afterwards (Dockerfile.backend).
run "test -d '$REMOTE_DIR/repo/.git'" \
  || die "no git checkout at $REMOTE_DIR/repo: first bring-up, see the private deploy README"
run "test \"\$(sudo find '$REMOTE_DIR/repo' -not -user \$(id -un) | wc -l)\" = 0" \
  || die "$REMOTE_DIR/repo holds files the deploy user does not own"
PREV="$(run "git -C '$REMOTE_DIR/repo' rev-parse HEAD" 2>/dev/null || true)"
run "git -C '$REMOTE_DIR/repo' fetch --quiet origin +refs/heads/main:refs/remotes/origin/main"
run "git -C '$REMOTE_DIR/repo' cat-file -e '$TARGET^{commit}'" \
  || die "the box did not receive $TARGET from GitHub"
run "git -C '$REMOTE_DIR/repo' symbolic-ref HEAD refs/heads/main \
  && git -C '$REMOTE_DIR/repo' reset --quiet --hard '$TARGET'"
# Exactly the commit's tracked files: -x takes ignored files too, -ff takes
# nested repositories such as agent worktrees.
run "git -C '$REMOTE_DIR/repo' clean -ffdxq"
run "git -C '$REMOTE_DIR/repo' fsck --connectivity-only --no-dangling"
[ -z "$(run "git -C '$REMOTE_DIR/repo' status --porcelain --ignored")" ] \
  || die "$REMOTE_DIR/repo is not a clean checkout after the reset"

# The bundle (compose file, image recipes, MCP manifest) comes from the same
# checkout instead of a second upload. The excludes are load-bearing: .env,
# secrets/ and repo/ exist ONLY on the box, and --delete without them
# destroys the deployment's own state (it did, once: findings F-004). logs/
# joined 2026-09-13 (security review SR-3): fapd-web bind-mounts
# /opt/fapd/logs/ for the /mcp access log, and --delete would erase it on
# every deploy. evidence/ joined 2026-09-26: incident material the operator
# keeps on the box, mirrored by nothing in deploy/vps/.
run "rsync -a --delete --exclude '.DS_Store' \
  --exclude '.env' --exclude 'secrets/' --exclude 'repo/' \
  --exclude 'deploy.env' --exclude 'logs/' --exclude 'evidence/' \
  '$REMOTE_DIR/repo/deploy/vps/' '$REMOTE_DIR/'"

echo "==> [3/4] build + up on the box"
# Only what the change touched. The backend image bakes the checkout, so it
# always builds; web and mcp build when their own sources changed, or with
# --all, or when the previous commit is unknown. Rebuilding an untouched
# image re-sent nothing new but cost every deploy three builds.
SERVICES="backend"
if [ "$ALL" = 1 ] || ! run "git -C '$REMOTE_DIR/repo' cat-file -e '${PREV:-none}^{commit}'" 2>/dev/null; then
  SERVICES="backend mcp web"
else
  CHANGED="$(run "git -C '$REMOTE_DIR/repo' diff --name-only '$PREV' '$TARGET'")"
  if grep -q '^packages/static-mcp/' <<<"$CHANGED"; then SERVICES="$SERVICES mcp"; fi
  if grep -q '^deploy/vps/web-image/' <<<"$CHANGED"; then SERVICES="$SERVICES web"; fi
fi
echo "building: $SERVICES"
# The MCP service (agent-discovery Phase 4B; docs/mcp-server.md) builds
# from repo/packages/static-mcp and runs as fapd-mcp with NO PUBLISHED
# PORT: Docker-published ports bypass ufw, and a port would also skip
# TLS, the edge rate limit and the security headers. It is reachable
# only from fapd-web over the internal fapd_mcp network; `docker port
# fapd-mcp` must print nothing (OPS-GUIDE). Never add `ports:` to it.
# logs/ is the /mcp access-log bind mount (compose); it is created
# here, not by Docker, so it is owned by the deploy user and the bundle
# sync's exclude (SR-3) keeps it across deploys.
# --pull re-resolves every base image on each build (CVE sweep 2026-10-30):
# without it a cached base outlived its security fixes for weeks. It
# downloads a base only when its digest changed.
run "cd '$REMOTE_DIR' && mkdir -p logs && chmod 755 logs"
run "cd '$REMOTE_DIR' && sudo docker compose --profile backend build --pull $SERVICES"
# up -d recreates only services whose image or definition changed.
run "cd '$REMOTE_DIR' && sudo docker compose --profile backend up -d"
run "cd '$REMOTE_DIR' && sudo docker compose ps --format '{{.Name}} {{.Status}}'"

# The fapd-web config reload also moved to the operator's private host tree (2026-09-21). Reloading
# it from here would apply a config this repo no longer has and never tested.
# If you changed fapd-web's config, you changed it in the operator's private host tree — deploy it
# from there.

# The fapd-site volume is seeded from the image only when EMPTY — an image
# rebuild does not refresh it (F-009). Rebuild the site in-container so
# presentation changes go live with the deploy instead of waiting for EOD.
run "sudo docker exec fapd-backend uv run --no-dev python scripts/build_site.py" || true

# /today's RenderWorker skips on an unchanged journal watermark — it
# watches data, not code — so a deploy that changes the renderer must
# rebuild the live page itself or the new markup waits for the next
# journaled item.
run "sudo docker exec fapd-backend uv run --no-dev python -c \
   'from fapd import db, publish; publish.build_today(db.connect())'" || true

# Belt-and-braces since 2026-08-07: Dockerfile.backend now bakes the SSH
# remote into the IMAGE, which is what makes it survive a container
# recreate (F-020 — this exec writes only to the running container's
# layer, so a recreate outside a deploy silently reverted it to the
# HTTPS remote, F-008). Kept because it costs one command and covers an
# image built before that change.
run "sudo docker exec fapd-backend git -C /app remote set-url origin \
   git@github.com:davidkarnowski/free-agentic-publication-digester.git"

echo "==> [4/4] verify"
sleep 10
# The container must run the commit that was deployed, on main, or the
# nightly evidence push halts (2026-10-25).
LIVE="$(run "sudo docker exec fapd-backend git -C /app rev-parse HEAD")"
[ "$LIVE" = "$TARGET" ] && echo "backend runs ${TARGET:0:8} (ok)" \
  || echo "backend runs ${LIVE:0:8}, expected ${TARGET:0:8} — investigate"
run "sudo docker exec fapd-backend git -C /app rev-parse --abbrev-ref HEAD"
curl -fsSI https://fapd.info | head -1
# The repo-managed config is live only if the discovery surfaces answer
# through the edge: the api-catalog with its linkset type, and the RFC
# 8288 Link header on the front page (agent-discovery plan §8.1/§8.3).
curl -fsS -o /dev/null -w '%{http_code} %{content_type}\n' https://fapd.info/.well-known/api-catalog
curl -fsSI https://fapd.info/ | grep -i '^link:'
# The MCP service answers through the edge: a modern server/discover
# POST (MCP 2026-07-28) must return 200 and serverInfo.name
# info.fapd/fapd (master plan §8.4). Prints "<status> <name>".
curl -sS -o /tmp/fapd-mcp-discover.json -w '%{http_code} ' -X POST https://fapd.info/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
  -d '{"jsonrpc":"2.0","id":"deploy","method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"deploy.sh","version":"1"},"io.modelcontextprotocol/clientCapabilities":{}}}}'
uv run python -c "import json; d = json.load(open('/tmp/fapd-mcp-discover.json')); print(d.get('result', {}).get('_meta', {}).get('io.modelcontextprotocol/serverInfo', {}).get('name', d.get('error')))"
rm -f /tmp/fapd-mcp-discover.json
run "sudo docker ps --format '{{.Names}}\t{{.Status}}' | grep fapd"
run "test -z \"\$(sudo docker port fapd-mcp)\" && echo 'fapd-mcp: no published port (ok)' || echo 'fapd-mcp: PUBLISHED PORT FOUND — investigate'"
echo "==> deploy complete — run the health check again in ~5 minutes"

# FAPD VPS stack — deploy runbook

> **2026-09-21 — `deploy/vps/nginx/` moved out of this repository.** Operator ruling:
> the fapd-web nginx config carries probe-refusal rules that state exactly what is and
> is not refused, and this repository is public. It now lives in the operator's private
> host tree and is mounted on the box from `/opt/edge/fapd-web`. References to
> `deploy/vps/nginx/` below are historical; git history retains the old config.

Source of truth for the containers running at `/opt/fapd` on the shared
VPS. Author changes **here**, never on the box (the next rsync would
revert them). The box dossier (access, host facts) lives in the
operator's private server guide — not in this public-bound repo.

> **Deploy authorization gate.** Only push to the VPS when the operator
> explicitly asks in the current session ("deploy", "push to the VPS",
> or by naming a command below). Never infer authorization from a
> generic "looks good" or from a previous deploy. Local edits and local
> git commits are not gated — only the VPS side is.
> `deploy/dev/scripts/dev-seed.sh` (a read-only snapshot pull that
> leaves only a scratch dir it deletes) follows the same rule: run it
> only on the operator's explicit ask.

## Architecture (strict segmentation)

- `fapd-web` — nginx serving the public site content. Sits ONLY on the
  external `fapd_edge` Docker network, which is created `--internal`:
  no default route, so the container has **zero egress**. The shared
  edge proxy (spiralyst-proxy) is the only other member; it terminates
  TLS for fapd.info and proxies here. FAPD and Spiralyst containers
  share no network — the proxy alone bridges the two edge networks.
  Since the agent-discovery plan (Phase 3, 2026-09-13; **pending
  deploy**) it runs the repo-managed configuration in
  [`nginx/`](nginx/README.md), mounted read-only as the whole of
  `/etc/nginx/conf.d/` — a directory, never a file, because rsync
  replaces files with new inodes that a single-file bind mount never
  sees. That config sets the discovery documents' content types, the
  RFC 8288 `Link` header, `Accept: text/markdown` negotiation, CORS on
  machine-readable files, signposted 404s under `/.well-known/`, and
  `server_tokens off`. The edge still owns HSTS, nosniff,
  frame-options and referrer-policy; `fapd-web` repeats none of them.
- `fapd-mcp` (agent-discovery Phase 4B, 2026-09-14; **pending
  deploy**) — the read-only, no-inference MCP service, GUIDE §2a rule
  4's one bounded exception (`docs/mcp-server.md`). The generic
  `packages/static-mcp` image with [`mcp/fapd.manifest.json`](mcp/README.md).
  Joins ONLY `fapd_mcp`, a second `internal` network whose other member
  is `fapd-web`, which proxies `POST /mcp` to it through a variable
  upstream (the site starts and serves without it, answering 503 with a
  signpost). **No published port, ever** — Docker-published ports bypass
  `ufw`, and a port would also skip TLS, the edge rate limit and the
  security headers. Reads the `fapd-site` volume read-only and nothing
  else; non-root, read-only rootfs, all capabilities dropped. Abuse
  controls: the edge's per-address limit → `fapd-web`'s `/mcp` zones
  (429) → the service's concurrency cap (503) → a host fail2ban jail on
  repeated rejections (jail files in the operator's private host tree (not in this repository — operator ruling 2026-09-14: security configuration is applied to the box directly, never published); installed 2026-09-14). `fapd-web` writes the `/mcp` access
  log to `./logs` (bind mount, excluded from the bundle rsync).
- `fapd-backend` (live since 2026-07-30, `profiles: ["backend"]`) — the collector
  supervisor + end-of-day finalizer. Own private egress-only network;
  NOT on `fapd_edge`; no published ports; unreachable from the proxy,
  the web container, or the public internet. Hands the built site to
  `fapd-web` through the `fapd-site` named volume, read-only on the web
  side — a volume, never a socket. Four volumes in all: `fapd-data`
  (`/app/data`), `fapd-site` (`/app/site`), and — added 2026-08-07 —
  `fapd-digests` (`/app/digests`) and `fapd-provenance`
  (`/app/provenance`). The last two exist because `/app` is the IMAGE:
  before they were mounted, a rendered digest and its manifest lived in
  the container's writable layer, and a rebuild after a failed evidence
  push would have destroyed a day of the record (F-021). Their cost is
  disclosed as OB-19 — a named volume seeds from the image only when
  empty, so a *retired* digest must be deleted from the volume by hand.

## The deploy path — `scripts/deploy.sh`, always

Every deploy runs `deploy/vps/scripts/deploy.sh`. Coordinates resolve
through `scripts/_env.sh` — `$FAPD_DEPLOY_ENV`, then the in-project
`deploy/vps/deploy.env` (gitignored, `chmod 0600`, excluded from BOTH
rsync lists so it cannot bake into an image, pinned by
`tests/test_deploy_secrets.py`), then `~/.fapd-deploy.env`. See
`deploy.env.example`. Read-only box checks go through
`scripts/vps-ssh.sh '<cmd>'`, which carries no host. Do not hand-roll the
rsync + `up -d` — a bare `docker compose up -d` silently skips the
backend (it sits behind `profiles: ["backend"]`), and the backend
image cannot even build without the staged `repo/` the script creates.
What the script does, in order:

1. **Test gate** — ruff + the full pytest suite; a red suite never
   deploys.
1b. **nginx syntax gate** (2026-09-13) — the candidate `nginx/` is
   rsynced to `/opt/fapd/.nginx-candidate/` and `nginx -t` runs against
   it in a throwaway container of the same pinned image, **before** the
   bundle rsync swaps it in. A bad config would crash-loop `fapd-web`,
   which is the edge proxy's static upstream: an edge restart in that
   window takes the cohabitant down too. The bundle rsync's `--delete`
   removes the candidate directory afterwards (intended). Since Phase
   4B the gate also mounts `/opt/fapd/logs` (created first): nginx
   opens the `/mcp` access log at config-test time, so without the
   mount a correct config fails the gate.
2. **Bundle rsync** (`deploy/vps/` → `/opt/fapd/`) with the
   load-bearing excludes `.env`, `secrets/`, `repo/` — those exist
   only on the box, and `--delete` without them destroys the
   deployment's own state (finding F-004) — and, since 2026-09-13,
   `logs/` (security review SR-3): Phase 4B bind-mounts
   `/opt/fapd/logs/` into `fapd-web` for the `/mcp` access log that
   fail2ban reads, and without the exclude every deploy would erase it.
3. **Repo export** (`./` → `/opt/fapd/repo/`, the backend build
   context, `.git` included for evidence commits) using the shared
   exclude list `deploy/common/repo-excludes.txt`.
4. **Build + up**: `mkdir -p logs`, then `docker compose --profile
   backend build backend mcp && --profile backend up -d`, then
   `nginx -t && nginx -s reload` inside `fapd-web` (2026-09-13): the
   config is a directory mount, and compose recreates a container only
   when its service definition changes, so a config-only change is
   invisible to `up -d` and takes effect on the reload. Verify then also
   curls `/.well-known/api-catalog` (expects `200 application/linkset+json`),
   greps the `Link` header on `/`, POSTs a modern `server/discover` to
   `/mcp` (expects `200 info.fapd/fapd`) and checks `docker port
   fapd-mcp` prints nothing.
5. **Three post-up steps**, each load-bearing: in-container
   `build_site.py` (F-009 — the site volume seeds from the image on
   first mount ONLY; a rebuild does not refresh it), in-container
   `publish.build_today` (the RenderWorker watches data, not code — a
   renderer change otherwise waits for the next journaled item), and
   the origin re-flip to the SSH remote. That last one is now
   belt-and-braces only: since 2026-08-07 `Dockerfile.backend` bakes the
   SSH remote into the IMAGE (F-020). The exec writes to the running
   container's layer, so a recreate outside a deploy silently reverted it
   to the laptop tree's HTTPS remote (F-008) and broke evidence pushes —
   invisibly, because the repo is public and anonymous HTTPS *fetch* keeps
   working, so only an actual push discovers it.

The EOD finalizer's automated pushes run
`deploy/vps/scripts/evidence-commit.sh` (guard-shell: repo-root check,
evidence-path allowlist, bot identity named on the commit itself).

**Pre-deploy check:** render your change against production-shaped
data first — `deploy/dev/` runs the same image recipe on a VPS data
snapshot at localhost:8080 (see its README). Advisory today, and
cheap. **A change under `nginx/` additionally runs
`deploy/vps/nginx/rehearse.sh` first** (local throwaway container, the
full request matrix, ~10 s) and must print `SUCCESS`.

### First-time bring-up (once per box)

`sudo docker network create --internal fapd_edge`, create `/opt/fapd`
with a server-side `.env` and root-owned `secrets/` (deploy key,
0600) — both exist ONLY on the box — then run `scripts/deploy.sh`.
Then add the fapd.info server blocks + `fapd_edge` membership to the
edge proxy's bundle (kept in the operator's spiralyst-site repo) and
deploy that. TLS: `sudo certbot certonly --webroot
-w /opt/spiralyst/certbot/www -d fapd.info -d www.fapd.info` (the edge
proxy serves the ACME webroot; its renewal deploy-hook reload covers
this cert too).

### The server-side `.env` (never synced, never in the repo)

`/opt/fapd/.env` is read by compose (`env_file`) and is the only place
provider choices live on the box. Keys, all documented in the repo's
`.env.example`: `GOVINFO_API_KEY`, `CONTACT_EMAIL`, `IMAP_*` (mailbox
ingest), `SITE_BASE_URL`, `FAPD_EVIDENCE_PUSH=1`, and the inference
block — `LLM_BACKEND` (`cli` / `api` / `gemini` / `none`), with
`CLAUDE_CODE_OAUTH_TOKEN` for `cli`, `ANTHROPIC_API_KEY` for `api`,
`GOOGLE_GEMINI_API_KEY` for `gemini`; `OPENAI_API_KEY` is deliberately
unset (narration is gated off, GUIDE §3a). A backend change is made by a
staged script under `scripts/staged/` that backs the file up and
recreates the container (`2026-08-15-switch-to-gemini-backend.sh`,
`2026-08-24-restore-cli-backend.sh`), and is recorded in GUIDE §6 r7's
provider record and CLAUDE.md §14 — the ledger's `backend` column alone
is not a record anyone reads in time.

### Static assets and the image bake

`Dockerfile.backend` copies `site/assets/*` from the repo export into
`/app/static_assets/` at build time (commit 14137fc), and `build_site`
copies `static_assets/` then `site/assets/` into the output tree on
every render (size-compare, not hash-compare). This is what keeps blog
and About-page media present when the site volume is rebuilt; it is
also one more class of output that nothing ever deletes (OB-12).

## Verify (after every deploy)

```sh
curl -sI https://fapd.info | head -1        # HTTP/2 200
curl -sI https://fapd.info/ | grep -i '^link:'                       # five rels (plan §8.3)
curl -sS -o /dev/null -w '%{http_code} %{content_type}\n' \
  https://fapd.info/.well-known/api-catalog                        # 200 application/linkset+json
curl -sI https://fapd.info/.well-known/oauth-authorization-server | head -1   # 404 (signposted)
curl -sI https://fapd.info/mcp | head -1                             # 405 (POST only; JSON signpost)
ssh <box> 'sudo docker ps --format "{{.Names}}\t{{.Status}}" | grep fapd'
ssh <box> 'sudo docker inspect fapd-web --format "{{json .NetworkSettings.Networks}}"'
#   ^ must list fapd_edge and fapd_mcp, nothing else
ssh <box> 'sudo docker inspect fapd-mcp --format "{{json .NetworkSettings.Networks}}"'
#   ^ must list fapd_mcp and nothing else
ssh <box> 'sudo docker port fapd-mcp'                                # prints NOTHING
```

The MCP `server/discover` probe and the fail2ban jail checks are in
`docs/ops/OPS-GUIDE.md` ("The MCP service").

Run the health check again ~5 minutes after any deploy (cadence rule,
docs/ops/OPS-GUIDE.md).

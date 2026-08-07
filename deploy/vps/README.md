# FAPD VPS stack — deploy runbook

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
2. **Bundle rsync** (`deploy/vps/` → `/opt/fapd/`) with the
   load-bearing excludes `.env`, `secrets/`, `repo/` — those exist
   only on the box, and `--delete` without them destroys the
   deployment's own state (finding F-004).
3. **Repo export** (`./` → `/opt/fapd/repo/`, the backend build
   context, `.git` included for evidence commits) using the shared
   exclude list `deploy/common/repo-excludes.txt`.
4. **Build + up**: `docker compose --profile backend build backend &&
   --profile backend up -d`.
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
cheap.

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

## Verify (after every deploy)

```sh
curl -sI https://fapd.info | head -1        # HTTP/2 200
ssh <box> 'sudo docker ps --format "{{.Names}}\t{{.Status}}" | grep fapd'
ssh <box> 'sudo docker inspect fapd-web --format "{{json .NetworkSettings.Networks}}"'
#   ^ must list fapd_edge and nothing else
```

Run the health check again ~5 minutes after any deploy (cadence rule,
docs/ops/OPS-GUIDE.md).

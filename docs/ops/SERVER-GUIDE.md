# FAPD server dossier (pointer + public-safe facts)

*Last reviewed: 2026-09-14 (agent-discovery Phase 4B: the `fapd-mcp`
container, the `fapd_mcp` network and the fail2ban jail added as
**pending deploy** rows; nothing on the box was touched or re-verified.
The 2026-08-07 verification rows stand as they were.)*

> **Connection facts live in the project, uncommitted (2026-08-07).**
> Copy `deploy/vps/deploy.env.example` to `deploy/vps/deploy.env`, fill
> it in, `chmod 0600`. It is gitignored, excluded from both rsync lists
> so it cannot bake into a container image, and pinned by
> `tests/test_deploy_secrets.py`. Every read-only check in
> [OPS-GUIDE.md](OPS-GUIDE.md) then runs through
> `deploy/vps/scripts/vps-ssh.sh '<cmd>'`, which carries no host — so an
> agent never handles coordinates and never needs to leave this
> repository. Before 2026-08-07 the only source was the operator's
> private guide in a sibling project tree, which meant the VPS half of
> `/fapd-health` could not run from here at all.
>
> **Box *quirks* remain private** — the cohabitation dossier, fail2ban
> specifics, and anything about the other project on the box stay in the
> operator's private tree. This file carries only what is safe to
> publish. Follow
> [AGENT-VPS-SERVICING-GUIDE.md](AGENT-VPS-SERVICING-GUIDE.md) §0–§1 for
> conduct: convenient access does not loosen the authorization gate.

## Public-safe facts

| Fact | Value |
|---|---|
| Hosting model | Shared VPS with the operator's Spiralyst project; strict Docker-network segmentation (the cohabitant's edge proxy is the only bridge) |
| FAPD stack path | `/opt/fapd` — source of truth [`deploy/vps/`](../../deploy/vps/) in this repo |
| Containers | `fapd-web` (nginx, inbound-only, zero egress — external `--internal` net `fapd_edge`; since Phase 4B also on `fapd_mcp`); `fapd-backend` **live 2026-07-30** (collector supervisor + EOD finalizer, egress-only on `fapd_fapd_backend`, no published ports, volume-coupled to web); `fapd-mcp` **pending deploy (2026-09-14)** — the read-only, no-inference MCP service (`packages/static-mcp` + `deploy/vps/mcp/`), on `fapd_mcp` only, no published port, non-root, read-only rootfs, reads the site volume read-only (`docs/mcp-server.md`) |
| Networks | `fapd_edge` (external, `--internal`: edge proxy ↔ `fapd-web`); `fapd_fapd_backend` (egress-only bridge, backend alone); `fapd_fapd_mcp` **pending deploy** (`internal: true`, compose-managed: `fapd-web` ↔ `fapd-mcp`, zero egress) |
| Host fail2ban | Cohabitant-owned config; FAPD adds exactly one jail, `fapd-mcp` (reads `/opt/fapd/logs/mcp-access.log`, bans in `DOCKER-USER`), installed by the operator at checkpoint C-6 — **pending** |
| TLS | Let's Encrypt for `fapd.info` + `www`, webroot method via the shared edge proxy, auto-renewing (deploy-hook reload covers it); issued 2026-07-30 |
| Public surface | `https://fapd.info` — the full digest site (served from the fapd-site volume since 2026-07-30) |
| Bot git identity (live 2026-07-30) | `fapd-pipeline` with a repo-scoped deploy key, for evidence commits |
| Backend scheduling (live 2026-07-30) | inside the supervisor container (EODWorker) — host needs only Docker |

## Held items / quirks

- **2026-08-05 — fail2ban's `sshd` jail is inert on this box.** Its
  journal match is `_SYSTEMD_UNIT=sshd.service`; the unit is
  `ssh.service`. Bounded by key-only auth. Tracked as OB-13 / F-017;
  the jail config is cohabitant-owned, so coordinate before changing it.
- **2026-08-05 — banned IPs in the `nginx-noscript` jail are Cloudflare
  edge ranges.** Both `fapd.info` and `spiralyst.com` resolve directly
  to the box, so these are someone else's CF-fronted domain still
  pointing here, not our own visitors. Harmless; noted so a future
  reader does not "fix" it by unbanning Cloudflare.

## Review-date table

| Item | Last verified |
|---|---|
| `fapd-web` runs the repo-managed config (`deploy/vps/nginx/`, directory mount): discovery content types, `Link` header, Markdown negotiation, CORS, signposted `/.well-known/` 404s, `server_tokens off` (agent-discovery Phase 3) | **pending deploy** (files landed 2026-09-13; rehearsed locally only — never verified on the box until Phase 5) |
| `deploy.sh` syntax-gates the nginx candidate on the box before the swap and reloads `fapd-web` after `up -d`; bundle rsync excludes `logs/` (SR-3) | **pending deploy** (2026-09-13; `bash -n` and static tests only) |
| `fapd-mcp` running: `fapd_mcp` network `internal`, no published port (`docker port fapd-mcp` empty), `ReadonlyRootfs`, user 10001, `CapDrop ALL`, no egress from inside; `fapd-web` on exactly `fapd_edge` + `fapd_mcp`; `POST /mcp` answers `server/discover` through the edge (agent-discovery Phase 4B) | **pending deploy** (files landed 2026-09-14; manifest and tools proven against a real render and a real client on the laptop; the container rehearsal rows are Phase 5's — never verified on the box until then) |
| `fapd-mcp` fail2ban jail installed, `f2b-fapd-mcp` chain present in `DOCKER-USER`, log's first field a client address | **pending** (checkpoint C-6, operator-run `scripts/staged/2026-09-14-install-fapd-mcp-jail.sh`) |
| **Evidence push repaired** — silently failing since the 2026-08-06 deploy; the stranded commit recovered and the cause fixed (F-021, plan P0–P3) | 2026-08-07 |
| Connection facts reachable from this repo (`deploy.env` + `vps-ssh.sh`) | 2026-08-07 |
| Containers healthy, `fapd-web` on exactly `fapd_edge`, site serving | 2026-08-07 |
| Backend deployed; segmentation re-verified; real site serving | 2026-08-05 |
| Evidence push **live over the SSH deploy key** (OB-11 landed; the earlier "inert by HTTPS remote" row described a state that ended 2026-07-30 — corrected 2026-08-05 after observing `1459dd6` reach origin) | 2026-08-05 |
| Full digest site serving over HTTPS, both hostnames | 2026-08-05 |
| `fapd.info` cert valid (expires 2026-10-28) | 2026-08-05 |
| Renewal dry-run green (both cohabiting certs) | 2026-07-30 |
| `fapd-web` networks == exactly `fapd_edge` | 2026-08-05 |
| `fapd-backend` egress-only, no published ports | 2026-08-05 |
| ufw open ports == exactly 2222 / 80 / 443 | 2026-08-05 |
| GitHub: sole collaborator is the owner; one write deploy key (`fapd-pipeline`); `main` ruleset active (CI check `test`, no force-push, no deletion; deploy-key bypass only); Actions default token read-only, fork-PR workflows need approval | 2026-08-27 |
| Secrets bind-mounted read-only, `0600` root-owned | 2026-08-05 |

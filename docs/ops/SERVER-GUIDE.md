# FAPD server dossier (pointer + public-safe facts)

*Last reviewed: 2026-08-07 (evidence-push incident F-021: the stranded
commit recovered, the cause fixed, connection facts brought into the
project. Containers, networks and the public surface re-verified the same
day; certs and firewall last checked 2026-08-05 — see the review table).*

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
| Containers | `fapd-web` (nginx, inbound-only, zero egress — external `--internal` net `fapd_edge`); `fapd-backend` **live 2026-07-30** (collector supervisor + EOD finalizer, egress-only on `fapd_fapd_backend`, no published ports, volume-coupled to web) |
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
| Secrets bind-mounted read-only, `0600` root-owned | 2026-08-05 |

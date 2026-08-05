# FAPD server dossier (pointer + public-safe facts)

*Last reviewed: 2026-08-05 (read-only health check: containers, networks,
certs, evidence push, firewall, and public surface all re-verified on the
box — see the review table).*

> **The full dossier is private.** This repository is headed for public
> release, so access details (host, port, user, key path, box quirks)
> live in the operator's **private** server guide in the Spiralyst tree
> — the FAPD stack cohabits that project's VPS. Agents: read that guide
> for connection facts; follow
> [AGENT-VPS-SERVICING-GUIDE.md](AGENT-VPS-SERVICING-GUIDE.md) §0–§1
> for conduct. Nothing in this file is sufficient to reach the box, by
> design.

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
| Backend deployed; segmentation re-verified; real site serving | 2026-08-05 |
| Evidence push **live over the SSH deploy key** (OB-11 landed; the earlier "inert by HTTPS remote" row described a state that ended 2026-07-30 — corrected 2026-08-05 after observing `1459dd6` reach origin) | 2026-08-05 |
| Full digest site serving over HTTPS, both hostnames | 2026-08-05 |
| `fapd.info` cert valid (expires 2026-10-28) | 2026-08-05 |
| Renewal dry-run green (both cohabiting certs) | 2026-07-30 |
| `fapd-web` networks == exactly `fapd_edge` | 2026-08-05 |
| `fapd-backend` egress-only, no published ports | 2026-08-05 |
| ufw open ports == exactly 2222 / 80 / 443 | 2026-08-05 |
| Secrets bind-mounted read-only, `0600` root-owned | 2026-08-05 |

# FAPD server dossier (pointer + public-safe facts)

*Last reviewed: 2026-08-02.*

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

(none recorded yet — add rows as they arise, dated)

## Review-date table

| Item | Last verified |
|---|---|
| Backend deployed; segmentation re-verified; real site serving | 2026-07-30 |
| Evidence push inert by HTTPS remote (deliberate, OB-11) | 2026-07-30 |
| Placeholder serving over HTTPS, both hostnames | 2026-07-30 |
| Renewal dry-run green (both cohabiting certs) | 2026-07-30 |
| `fapd-web` networks == exactly `fapd_edge` | 2026-07-30 |

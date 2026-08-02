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
- `fapd-backend` (next push, `profiles: ["backend"]`) — the collector
  supervisor + end-of-day finalizer. Own private egress-only network;
  NOT on `fapd_edge`; no published ports; unreachable from the proxy,
  the web container, or the public internet. Hands the built site to
  `fapd-web` through the `fapd-site` named volume, read-only on the web
  side — a volume, never a socket.

## First-time bring-up (once per box)

```sh
sudo docker network create --internal fapd_edge   # skip if it exists
rsync -az --exclude '.DS_Store' deploy/vps/ <box>:/opt/fapd/
ssh <box> 'cd /opt/fapd && sudo docker compose up -d'
```

Then add the fapd.info server blocks + `fapd_edge` membership to the
edge proxy's bundle (kept in the operator's spiralyst-site repo) and
deploy that. TLS: `sudo certbot certonly --webroot
-w /opt/spiralyst/certbot/www -d fapd.info -d www.fapd.info` (the edge
proxy serves the ACME webroot; its renewal deploy-hook reload covers
this cert too).

## Routine deploy

```sh
rsync -az --exclude '.DS_Store' deploy/vps/ <box>:/opt/fapd/
ssh <box> 'cd /opt/fapd && sudo docker compose up -d'
```

## Verify (after every deploy)

```sh
curl -sI https://fapd.info | head -1        # HTTP/2 200
ssh <box> 'sudo docker ps --format "{{.Names}}\t{{.Status}}" | grep fapd'
ssh <box> 'sudo docker inspect fapd-web --format "{{json .NetworkSettings.Networks}}"'
#   ^ must list fapd_edge and nothing else
```

Run the health check again ~5 minutes after any deploy (cadence rule,
docs/ops/OPS-GUIDE.md).

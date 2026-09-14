# fapd-web nginx configuration

The repo-managed server configuration for `fapd-web`, mounted read-only
as the whole of `/etc/nginx/conf.d/` by both `deploy/vps/docker-compose.yml`
(`./nginx`) and `deploy/dev/docker-compose.yml` (`../vps/nginx`). Landed
in Phase 3 of `docs/ops/plan-2026-09-13-agent-discovery.md`
(`plan-2026-09-13-phase3-web-config.md`, task AD-11). Before it, the
container ran the image's stock `default.conf`: version banner on,
gzip off, no content types for the discovery documents.

| File | Role |
|---|---|
| `default.conf` | The server. `map`s and limit zones sit in http context (the image's `nginx.conf` includes `conf.d/*.conf` inside `http {}`). Since Phase 4B it also carries `location = /mcp`, the stage-L0 transport gate in front of `fapd-mcp` (POST only, JSON only, 64 KiB, `limit_req` + `limit_conn`, variable upstream, 502/504 → 503 signpost) and the `fapd_mcp` access-log format whose first field is the true client address. That log goes to `/var/log/fapd/mcp-access.log`, a bind mount — and because nginx opens every `access_log` at config-test time, `nginx -t` needs the directory mounted (deploy.sh's gate and `rehearse.sh` both do). |
| `fapd-discovery-headers.inc` | The RFC 8288 `Link` header (master plan §8.3, verbatim) and `Vary: Accept`. Included by the `.html` and `.md` locations. |
| `fapd-cors.inc` | `Access-Control-Allow-Origin: *` (ruling D6) — machine-readable files only, never `/mcp`. |
| `fapd-static-methods.inc` | GET/HEAD only on static paths, 405 otherwise. Every location includes it itself: rewrite-module directives are not inherited by nested locations. |
| `rehearse.sh` | The local proof: fixture site from the real renderer, the pinned image in a throwaway container, the §3.5 request matrix, and (Phase 4B, rows M1–M17) the `fapd-mcp` image built from `packages/static-mcp` beside it on an `--internal` throwaway network; ends in `SUCCESS` or `FAILURE: <rows>`. Never touches the VPS. |

nginx loads only `*.conf` from this directory; the snippets are `*.inc`
so they are not loaded a second time at http level.

## What the config does

- **Content types** for the discovery documents (master plan §8.1):
  `application/linkset+json` for `/.well-known/api-catalog` (no
  extension), `application/ai-catalog+json` for the AI catalog,
  `application/mcp-server-card+json` for `/mcp/server-card`,
  `text/markdown; charset=utf-8` for every `.md` (not in nginx's
  `mime.types`).
- **Markdown negotiation** (§8.2): `Accept: text/markdown` on an
  eligible HTML path rewrites to its twin before location matching;
  `text/markdown;q=0` is a refusal, not a request (SR-1). `Vary: Accept`
  rides on every HTML and Markdown response.
- **Signposted refusals**: an unknown path under `/.well-known/` is a
  404 whose body is `/_signpost/not-offered.json` (internal; a direct
  request for it is a 404 too), with CORS so a browser-side agent can
  read it.
- **Hardening**: `server_tokens off`, `client_max_body_size 1k`, no
  dotfile served except `/.well-known/`, gzip for the types the edge
  proxy does not compress. The edge owns HSTS, nosniff, frame-options
  and referrer-policy — none is repeated here (pinned by
  `tests/test_web_conf.py`).
- **Phase 4B plumbing**: `$fapd_client` (X-Real-IP from the edge, or the
  peer address when the header is empty — SR-4) keys both the
  `fapd_mcp` request zone and the `fapd_conn` connection zone (SR-2).

## Change procedure

1. Edit here. Never on the box: the next deploy's rsync reverts it.
2. `deploy/vps/nginx/rehearse.sh` — must print `SUCCESS`. Rows it
   cannot run before another phase merges are `SKIP` with the reason;
   documents it plants as stand-ins print a `WARNING` each.
3. `uv run pytest -q tests/test_web_conf.py tests/test_dev_stack.py`.
4. Optionally `deploy/dev/scripts/dev-up.sh` and look at
   `http://localhost:8080` — the dev stack mounts this same directory.
5. Deploy (operator-gated). `deploy.sh` runs `nginx -t` against the
   candidate in a throwaway container on the box **before** the bundle
   rsync swaps it in, and `nginx -t && nginx -s reload` inside `fapd-web`
   after `up -d` — compose recreates the container only when the
   service definition changes, so a config-only change would otherwise
   never take effect.

Why the gate runs first: a crash-looping `fapd-web` takes fapd.info
down, and the edge proxy names `fapd-web` as a static upstream — an
edge restart during that window would take the cohabitant's site down
with it.

## Rehearsal findings worth knowing (2026-09-13)

- `charset_types` always includes `text/html`; listing it is a
  `duplicate MIME type` warning from `nginx -t`.
- The image's entrypoint script `10-listen-on-ipv6-by-default.sh` tries
  to add `listen [::]:80` by editing `default.conf` in place; under this
  read-only mount it logs a harmless "can not modify" line. The config
  carries both listens explicitly for that reason.

# The FAPD MCP service

> **Status: design of record, not yet built (2026-09-13).** This guide
> describes the service as planned in
> [docs/ops/plan-2026-09-13-agent-discovery.md](ops/plan-2026-09-13-agent-discovery.md)
> (Phase 4). Nothing here is live yet. Phase 4A/4B agents update this
> file to "built, pending deploy"; Phase 5 updates it to "live" with the
> verification date. **Until that banner changes, don't cite anything in
> this file as a description of production.**

*Owner: Operations (`docs/agents/operations.md`). Governing rule: GUIDE
§2a rule 4, the one bounded exception to "no endpoint of its own".
Last reviewed: 2026-09-13.*

---

## 1. What it is

`https://fapd.info/mcp` is a **Model Context Protocol** endpoint. MCP is
the protocol AI applications (Claude, ChatGPT connectors, IDE agents)
use to call **tools** and read **resources** on a server. The FAPD
service lets those applications fetch the digest the same way a person
reads the site: list the published days, read a day's digest, read the
live preliminary day, look up a source.

It's deliberately small:

- **It answers only from files the site already publishes.** Every
  response is a published file, or a slice of one, returned verbatim.
- **It performs no inference.** No model reads or writes anything on our
  side. That's the budget reason it exists at all.
- **It can't write, search, fetch, authenticate or remember.** It has no
  handler that does, no network route out, a read-only filesystem, and no
  session state.

Why have it, if every file is already on the web? Because many agents
only speak MCP. For them, "just fetch the JSON" means writing a file
reader first. This removes that step while keeping every disclosure the
files carry (GUIDE §1).

## 2. Where it sits

```
client ──HTTPS 443──▶ edge proxy (TLS, security headers, per-address rate limit)
                        │ internal network fapd_edge
                        ▼
                     fapd-web (nginx)
                        • static site, discovery documents
                        • location = /mcp: POST only, 64 KiB body cap, MCP rate limit,
                          15 s timeout → proxy to fapd-mcp
                        │ internal network fapd_mcp (NEW)
                        ▼
                     fapd-mcp (python, stdlib only)
                        • packages/static-mcp + deploy/vps/mcp/fapd.manifest.json
                        • reads the fapd-site volume READ-ONLY at /srv/site
```

- **No host port is published** for `fapd-mcp`. Docker-published ports
  bypass the host firewall (`ufw`), and publishing one would also skip
  TLS, the edge rate limit and the security headers. MCP rides the
  existing 443.
- `fapd-mcp` joins **only** `fapd_mcp`, an `internal` network. It has no
  egress, and the edge proxy can't reach it directly; only `fapd-web`
  can.
- `fapd-web` points at `fapd-mcp` through a **variable upstream**, so the
  site starts and serves normally even when the MCP container is absent.
  `/mcp` then answers 503 with a JSON pointer to the static files.

## 3. Protocol support

| Protocol revision | Supported | How |
|---|---|---|
| **2026-07-28** (modern, stateless) | yes | per-request `_meta` version and client info; `MCP-Protocol-Version` / `Mcp-Method` / `Mcp-Name` headers validated against the body; `server/discover` |
| **2025-11-25**, **2025-06-18** (legacy) | yes, **without sessions** | `initialize` negotiates the version; no `Mcp-Session-Id` is ever issued; follow-on requests are served statelessly |
| 2025-03-26 and older; the deprecated HTTP+SSE transport | no | — |
| SSE response streams, `subscriptions/listen`, sampling, elicitation, prompts, JSON-RPC batching | no | always plain `application/json` responses |

Transport: Streamable HTTP, `POST https://fapd.info/mcp`. `GET` or
`DELETE` → 405. A notification → 202.

## 4. Tools and resources (planned; regenerated from the manifest when built)

Every tool is read-only, idempotent and closed-world (annotations say so
and can't be changed by configuration).

| Tool | Returns | Parameters |
|---|---|---|
| `list_digests` | Published digest days, newest first: date, page URL, canonical Markdown path, teaser | `offset`, `limit` (≤60) |
| `get_digest` | The canonical Markdown digest for a date, verbatim, after a one-paragraph disclosure | `date` (YYYY-MM-DD) |
| `get_live_day` | Today's **preliminary** observed items with the day's disclosures and counts; excludes backfill by default | `offset`, `limit` (≤100), `include_backfill`, `collection` |
| `list_day_views` | Dates that have a frozen observed listing | `offset`, `limit` |
| `get_day_listing` | A finished day's frozen observed listing | `date`, `offset`, `limit`, `include_backfill`, `collection` |
| `list_sources` | The source directory with ingestion statistics (describes our ingestion, not any agency) | `offset`, `limit` |
| `get_source` | One source's record | `source_id` |
| `get_agent_guide` | `llms.txt` | — |

Resources: `https://fapd.info/llms.txt`, `/agents.md`, `/auth.md`,
`/digests.json`, `/sources.json`; templates `https://fapd.info/{date}.md`,
`/day/{date}.json`, `/sources/{source_id}.md`.

**The disclosures travel.** `get_digest` and `get_day_listing` start
with a statement that the text is the published file, that FAPD-AI lines
are model-written restatements, and that factual claims should cite each
item's official source. `get_live_day` starts with PRELIMINARY. Every
tool that reads `sources.json` states that its statistics describe our
ingestion. The server's `instructions` repeat the citation and
record-versus-preliminary rules.

## 5. Connecting a client

- **Claude Code:** `claude mcp add --transport http fapd https://fapd.info/mcp`
- **Any client taking JSON config:**
  `{"mcpServers": {"fapd": {"type": "http", "url": "https://fapd.info/mcp"}}}`
  (the exact key names vary by client).
- **Discovery without configuration:** the Server Card at
  `https://fapd.info/mcp/server-card` (also
  `/.well-known/mcp/server-card.json`), listed in
  `https://fapd.info/.well-known/ai-catalog.json`, and (after Phase 5) the
  official MCP Registry under `info.fapd/fapd`.

No account, key or token exists or is needed.

## 6. Security model

| Concern | Control |
|---|---|
| Writes, model calls, outbound requests | Impossible by construction: no handler kind does them; read-only volume; read-only root filesystem; `internal` network (no egress) |
| Path traversal | Parameters are validated against anchored patterns that can't match `/`, `\`, `..` or a leading `.` (enforced when the manifest loads); every resolved path must stay inside the site root, **after** symlink resolution |
| Oversized or slow requests | nginx: 64 KiB body cap, 2/10/15 s connect/send/read timeouts; server: body cap, socket timeout |
| Flooding | Edge per-address limit, plus a tighter `/mcp` zone in `fapd-web` (429), plus a server concurrency cap (503) |
| DNS rebinding / browser misuse | `Origin` validated: only `https://fapd.info` and `https://www.fapd.info` are accepted when present (403 otherwise). Requests without `Origin` (server-side clients) are allowed. No CORS on `/mcp`. |
| Privilege | Non-root user 10001, all capabilities dropped, `no-new-privileges`, PID and memory limits |
| Information leakage | No tracebacks or filesystem paths in responses; no session IDs; `Cache-Control: no-store` |
| Supply chain | Python standard library only; base image `python:3.12-slim`, swept with the backend under the CVE parity rule |
| Scope creep | GUIDE §2a rule 4: any new capability (search, writes, model calls, outbound requests, accounts) is a new constitutional ruling, not a manifest edit |

## 7. Privacy and logs

Requests pass through the normal web server access logs (see
`docs/site/privacy.md`). The MCP service itself writes one JSON line per
request to its container log: time, HTTP method, path, status, protocol
method, tool or resource name, protocol era and version, duration,
response size, and the client's self-reported User-Agent (truncated).
**It never logs the client IP, the request body, the arguments, or any
header beyond User-Agent.** Logs rotate at 5 MB × 3 files, like every
FAPD container.

```sh
deploy/vps/scripts/vps-ssh.sh 'sudo docker logs --tail 50 fapd-mcp'     # read-only
```

## 8. Operating it

| Task | How |
|---|---|
| Run the package's tests | `uv run pytest -q packages/static-mcp/tests` |
| Validate FAPD's manifest | `PYTHONPATH=packages/static-mcp/src python -m static_mcp check --manifest deploy/vps/mcp/fapd.manifest.json --root site` |
| Run locally without Docker | `PYTHONPATH=packages/static-mcp/src python -m static_mcp serve --manifest deploy/vps/mcp/fapd.manifest.json --root site` (binds 127.0.0.1:8080) |
| Rehearse web + MCP in throwaway containers | `deploy/vps/nginx/rehearse.sh` |
| Dev stack | `deploy/dev/scripts/dev-up.sh` → `http://localhost:8080/mcp` |
| Deploy | `deploy/vps/scripts/deploy.sh`, **only on the operator's "deploy"**, from `main` (see the Phase 5 plan for why) |
| Health (read-only) | `/fapd-health`; or a `server/discover` POST (below) |
| Take it offline, keep the site | `vps-ssh.sh 'cd /opt/fapd && sudo docker compose stop mcp'` (operator-gated write) |

A modern health probe:

```sh
curl -s -X POST https://fapd.info/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
  -d '{"jsonrpc":"2.0","id":"health","method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"fapd-health","version":"1"},"io.modelcontextprotocol/clientCapabilities":{}}}}'
```

## 9. Changing what it serves

1. Edit `deploy/vps/mcp/fapd.manifest.json`: add or change a tool using
   an existing handler kind (`static_text`, `text_file`, `json_file`,
   `file_listing`).
2. Bump `server.version` (semver: a new tool is a minor bump; a removed
   or renamed tool is a major bump).
3. `static-mcp check`; `uv run pytest -q tests/test_mcp_manifest.py
   tests/test_mcp_surfaces.py` (the Server Card, catalogs and agents.html
   section regenerate from the manifest, and the drift tests confirm it).
4. Branch → merge → deploy. The manifest directory is mounted, so a
   container restart picks it up (deploy recreates it on image change;
   for a manifest-only change restart `fapd-mcp`).
5. **A new handler kind** (anything the four kinds can't express) is a
   code change to `packages/static-mcp` with tests and a security review,
   and needs a GUIDE §2a check if it widens what the service can do.

## 10. Reusing this in another project

The server is the generic package `packages/static-mcp/`. It contains no
FAPD name, path or import (a test enforces this). FAPD is just one
manifest. To use it elsewhere:

1. Copy the package directory (or install it from a path or git URL). It
   has no dependencies.
2. Write a manifest for that project's static files (see the package
   README's reference and `examples/docs-site.manifest.json`).
3. `static-mcp check --manifest … --root …`.
4. Run the generic Dockerfile with the manifest mounted at
   `/etc/static-mcp/manifest.json` and the site mounted read-only at
   `/srv/site`.
5. Put a reverse proxy in front (POST-only location, body cap, rate
   limit, timeouts, variable upstream); the README has a minimal nginx
   block.
6. Publish a card with `static-mcp card` and list it with `static-mcp
   registry-json`.

Decisions each project must make: which files, which parameters and
patterns, allowed origins, limits, the instructions text, and whether its
own governance allows an endpoint at all.

## 11. Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `/mcp` returns 503 with the "temporarily unavailable" JSON | `fapd-mcp` stopped or unhealthy | `docker ps`, `docker logs fapd-mcp` |
| 400 with code `-32020` | the client's headers don't match its body (modern clients must mirror `Mcp-Method`/`Mcp-Name`) | client version; request headers |
| 400 with `-32022` and a `supported` list | the client asked for a protocol version we don't serve | the client should retry with a listed version |
| 403 | the request carried an `Origin` other than fapd.info (browser-based client) | by design in v1 |
| 404 with `-32601` | the method isn't implemented (e.g. `prompts/list`, `subscriptions/listen`) | §3 |
| 429 | rate limit | back off; conditional requests to the static files are cheaper |
| Legacy client fails after `initialize` | the client insists on a session ID | out of scope in v1 (stateless); record the client and version |
| A tool returns `isError` "no digest was published" | there's no digest for that date (weekends and holidays often have none) | `list_digests` |
| Result has `"truncated": true` | the page was too large for the result limit | lower `limit`, page with `offset` |

## 12. References (pinned 2026-09-13)

- MCP specification 2026-07-28 and 2025-11-25:
  `github.com/modelcontextprotocol/modelcontextprotocol`,
  `docs/specification/<revision>/`.
- Server Cards: SEP-2127 (Final) and
  `github.com/modelcontextprotocol/experimental-ext-server-card`.
- MCP Registry: `github.com/modelcontextprotocol/registry`
  (`docs/modelcontextprotocol-io/remote-servers.mdx`, `authentication.mdx`).
- Conformance tests: `github.com/modelcontextprotocol/conformance`.
- Plan and rulings: `docs/ops/plan-2026-09-13-agent-discovery.md`,
  `docs/ops/plan-2026-09-13-phase4-mcp-service.md`.

## 13. History

- 2026-09-13: designed. The operator ruled for a containerized,
  no-inference MCP service built to be reusable across projects, after a
  Cloudflare agent-readiness scan. GUIDE §2a rule 4 amended to name it as
  the single bounded endpoint.

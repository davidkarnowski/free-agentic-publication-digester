# Security review of the agent-discovery plan (second pass, 2026-09-13)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md).
Requested by the operator: "ensure we are securely setting up the MCP
endpoint … adhere to the latest and strictest implementation … should we
apply Fail2Ban … ensure we have input validation setup as a layer."
Sources read for this pass are listed in §7. Every finding below is
**already applied** to the phase files it names; this document is the
rationale record. Last reviewed: 2026-09-13.*

## 1. Summary

The design was sound on the big questions: no host port, an internal
network, a read-only mount, no egress, no inference, no state, Origin
validation, strict parameter patterns. The second pass adds what the
first one left implicit or missing:

1. **A named validation layer** (`static_mcp/validate.py`) that every
   request passes through **before** dispatch, with eight ordered
   stages, exact rejection codes, an adversarial test corpus and a
   seeded fuzz smoke test. (Phase 4A)
2. **Stricter JSON and header handling:** required `Content-Length`,
   strict `Content-Type`, `Accept` check, `Host` allow-list (DNS
   rebinding defense beyond `Origin`), nesting-depth and size caps,
   rejection of `NaN`/`Infinity`, huge integers, duplicate keys, control
   characters, oversized ids. (Phase 4A/4B)
3. **A code-level guarantee against command injection:** the package
   has no shell, subprocess, `eval`, `exec`, pickle or YAML path, pinned
   by a test that scans the source. (Phase 4A)
4. **Fail2ban: yes, one jail, own log, generous thresholds**, banning
   in the `DOCKER-USER` chain like the box's existing nginx jails.
   Installed by a staged, operator-gated script in Phase 5. (Phases
   3, 4B, 5)
5. **nginx corrections:** content-type gate, `proxy_next_upstream off`,
   `limit_conn`, request buffering, a rate-limit key that can't be
   empty, `Accept` `q=0` handling, no `proxy_intercept_errors`. (Phases
   3, 4B)
6. **An operations hazard found on the way:** the bundle rsync's
   `--delete` would erase a host log directory on every deploy unless
   it's excluded (the F-004 class). (Phase 3/5)
7. **A pre-existing finding on the box, cohabitant-owned:** three of
   the five nginx fail2ban jails have no iptables chain, so their bans
   may not be applied. Raised to the operator; not ours to change.

## 2. Threat model for this endpoint (what we're defending against)

`https://fapd.info/mcp` is public, unauthenticated, read-only, and
returns only files the site already publishes. That removes whole
classes of risk (there are no credentials to steal, no privileged
actions, no per-user data) and leaves these:

| Threat | Where it lands | Primary control | Secondary |
|---|---|---|---|
| Path traversal / file disclosure through tool arguments | handlers | anchored ASCII patterns proven unable to match `/`, `\`, `..`, leading `.`; `resolve()` containment after symlinks | read-only mount of the site volume only; non-root; read-only rootfs |
| Command / code injection | anywhere a string reaches an interpreter | **no interpreter path exists** (no subprocess, shell, eval, pickle, YAML); pinned by a source scan test | container has no shell privileges, caps dropped |
| Malformed or hostile JSON (deep nesting, huge numbers, NaN, duplicate keys, control chars, batches) | parser and dispatcher | validation layer stages L2–L3 with caps and strict parsing | body cap 64 KiB at nginx and again in the server |
| Header/body confusion (`Mcp-*` headers vs body), protocol-version tricks | dispatcher | spec-mandated mirror validation (`-32020`, `-32022`); header length and charset caps | nginx header buffer limits |
| DNS rebinding / browser-driven misuse | HTTP layer | `Origin` allow-list **and** `Host` allow-list; no CORS on `/mcp` | edge terminates TLS for `fapd.info` only |
| Flooding, slowloris, concurrency exhaustion | nginx and server | edge per-address limit; `/mcp` limit zone (429); `limit_conn`; body/connect/read timeouts; request buffering; server concurrency cap (503) | fail2ban jail bans repeat offenders for an hour, incrementing |
| Response amplification (large results) | handlers | `max_result_bytes`, `max_file_bytes`, `limit` maxima, truncation disclosed | gzip only at the edge for JSON |
| Prompt injection **through** returned content (tool poisoning, context injection: OWASP MCP Top 10) | model context on the client | tool descriptions and `instructions` say returned text is published material, to be treated as data; no hidden-instruction patterns in any description (pinned) | served content is the same public record the website serves; nothing arrives from a live third party at request time |
| Information leakage (paths, tracebacks, IPs in logs) | responses, logs | error messages carry parameter *names* only; tracebacks logged never returned; logs exclude IP, bodies, arguments; log fields JSON-encoded | `Cache-Control: no-store` |
| Supply chain | image | stdlib only; `python:3.12-slim` swept with the backend | no auto-update; image built from the repo |
| Scope creep | governance | GUIDE §2a rule 4 names the exception narrowly; a new handler kind is a reviewed code change | manifest can't express writes, egress or model calls |

What the strictest published guidance asks for that we **deliberately
don't do**, and why:

- **OAuth 2.1 with PKCE and audience-bound tokens.** The MCP
  authorization spec exists for servers that expose *protected*
  resources. Ours exposes public files, and the site's constitution
  forbids accounts and credentials. Adding auth would create the very
  credential surface the OWASP list warns about, to protect nothing.
  `auth.md` states this. If the endpoint ever serves anything
  non-public, that's a new §2a ruling, and auth comes with it.
- **Per-session process isolation.** There are no sessions and no
  per-client state; every request is served by the same read-only code
  over the same public files.
- **SSRF egress filtering.** Nothing makes outbound requests; the
  network has no route out. A test proves an outbound attempt fails.

## 3. The validation layer (applied to Phase 4A §A.3.7)

Eight ordered stages. A request that fails a stage stops there with the
stated response. Nothing later ever sees an input that an earlier
stage rejected. Each stage has its own tests, and the adversarial corpus
exercises every rejection path end to end.

| Stage | Where | Checks | Rejection |
|---|---|---|---|
| **L0 transport gate** | nginx `location = /mcp` (4B) | method POST; `Content-Type` starts with `application/json`; body ≤ 64 KiB; `limit_req`; `limit_conn`; connect/send/read timeouts; request buffering on | 405 / 415 / 413 / 429 / 503 with JSON signposts |
| **L1 HTTP** | `server.py` | `Content-Length` present (411) and ≤ cap (413); `Content-Type` `application/json` with optional `charset=utf-8` (415); `Accept` absent, or lists `application/json` or `*/*` (406); `Host` in `allowed_hosts` (403); `Origin` absent-and-allowed or in `allowed_origins` (403); every `Mcp-*` header ≤ 1,024 bytes of visible ASCII (400 `-32020`) | as listed; JSON-RPC error body without `id` where the spec says so |
| **L2 bytes → JSON** | `validate.py` | valid UTF-8; max nesting depth 32 (scanner over the raw text, outside strings); `json.loads` with `parse_constant` rejecting `NaN`/`Infinity`, `parse_int` capped at 20 digits, `object_pairs_hook` rejecting duplicate keys; then a walk rejecting control characters other than `\t\n\r` in any string, strings > 8 KiB, objects > 256 keys, arrays > 1,024 items | 400, `-32700` (undecodable) or `-32600` (structurally invalid), `id: null` |
| **L3 JSON-RPC envelope** | `validate.py` | top-level object (an array → "batching is not supported"); `jsonrpc == "2.0"`; `method` matches `^[a-z][a-zA-Z0-9_/]{0,63}$`; `id` absent, a string ≤ 128 chars, or an integer within ±2⁵³ (floats, booleans, objects → reject); `params` absent or an object; no other top-level keys; `params._meta` if present is an object of ≤ 64 keys whose names match the spec's `_meta` key rules, ≤ 8 KiB serialized; only `io.modelcontextprotocol/*` keys are read, others ignored | 400, `-32600` |
| **L4 protocol** | `protocol.py` | era classification; version support; header/body mirror for `MCP-Protocol-Version`, `Mcp-Method`, `Mcp-Name` (sentinel base64 decoded and checked as UTF-8 without control chars) | 400 `-32022` / `-32020`; 404 `-32601` (modern unknown method) |
| **L5 method params** | `dispatch.py` | per-method allow-list of `params` keys; `tools/call.name` matches the tool-name pattern and names a declared tool; `arguments` is an object; `resources/read.uri` is a string ≤ 2,048 chars that equals a declared resource URI or **matches a template's compiled regex** (built from the params' own patterns). A URI is never treated as a path. | `-32602` |
| **L6 arguments** | `manifest.py` validators | unknown argument; wrong JSON type (booleans must be JSON booleans, integers must be integers, no coercion); `re.fullmatch` with `re.ASCII` against the anchored pattern; string length ≤ 256 unless the manifest sets a lower `maxLength`; integer bounds; then defaults | `-32602` naming the parameter, never echoing its value |
| **L7 file containment** | `handlers.py` | template substitution only with validated values; `resolve(strict=True)`; `is_relative_to(root)`; regular file; size cap | `not_found` result (`isError`) for a missing file; `-32603` and a logged security event for containment failure, with no path in the message |
| **L8 output** | `dispatch.py` | results assembled from Python objects and serialized once; `max_result_bytes` enforced with disclosed truncation; user-supplied strings never interpolated into error messages; log fields JSON-encoded with control characters stripped | — |

Two guarantees at the code level, each pinned by a test that scans the
package source: **no interpreter path** (no `subprocess`, `os.system`,
`os.popen`, `eval`, `exec`, `compile`, `pickle`, `marshal`, `yaml`,
`shell=`, `ctypes`), and **no network client** (no `urllib.request`,
`http.client`, `socket.create_connection`, `ssl` outside the server's
own listening code).

## 4. Fail2ban (applied to Phases 3, 4B, 5)

**Decision: yes, one dedicated jail (`fapd-mcp`), generous thresholds,
with the nginx rate limit as the primary control.** Reasoning:

- The box already runs host fail2ban 1.0.2 with five nginx jails reading
  the edge proxy's bind-mounted logs, banning in the `DOCKER-USER`
  chain (the correct chain for Docker-published ports; bans in `INPUT`
  never see that traffic). A jail for `/mcp` fits the existing pattern.
- Bans are per source address. MCP clients often run behind shared
  egress (a company's agents, a cloud provider's NAT), so an aggressive
  jail would ban many legitimate agents for one bad one. Thresholds are
  therefore high (20 rejected requests in 10 minutes), the ban is the
  box default (1 h, incrementing on repeat), and the nginx limits do
  the everyday work.
- **What the jail counts:** responses on `/mcp` with status 400, 403,
  405, 413, 415 or 429. **Not** 404: a modern client probing an
  unimplemented method gets a legitimate 404/`-32601`.
- **Which log:** the jail needs the *real* client address. The edge's
  own access log (cohabitant-owned) has it, but adding filters there
  means editing the cohabitant's tree. Instead, `fapd-web` writes a
  dedicated access log for `/mcp` to a bind-mounted host directory,
  in a format whose **first field is `$http_x_real_ip`** (the edge sets
  it from the true remote address). Using `$remote_addr` there would
  log the edge's internal Docker address, and a ban on that address
  would do nothing.
- **Deploy hazard found while designing this:** `deploy.sh`'s bundle
  rsync runs with `--delete`. A `logs/` directory under `/opt/fapd`
  would be erased on every deploy unless excluded. It is now excluded,
  pinned by a test, and documented next to the F-004 excludes.
- **Install path:** jail and filter files live in
  `deploy/vps/fail2ban/`; a staged script under `scripts/staged/`
  copies them into `/etc/fail2ban/` and reloads. Host fail2ban config
  is shared with the cohabitant, so the script only *adds* files, and
  the operator runs it (checkpoint C-6). Verification: `fail2ban-client
  status fapd-mcp` and an `f2b-fapd-mcp` chain in `iptables -S DOCKER-USER`.

**Pre-existing finding to raise (cohabitant-owned, not ours to fix):**
`iptables -S DOCKER-USER` on 2026-09-13 shows chains only for
`nginx-bad-request` and `nginx-noscript`. The `nginx-botsearch`,
`nginx-http-auth` and `nginx-limit-req` jails are running but have no
chain, so their bans likely never reach the packet filter. Recommend
the operator check `sudo fail2ban-client get <jail> actions` and the
fail2ban log for `actionstart` errors on those three jails. This also
matters for us: our jail copies their action settings, so Phase 5 must
verify the chain exists *after* the jail starts, not assume it.

## 5. Findings applied to other phases

| ID | Phase | Finding | Fix applied |
|---|---|---|---|
| SR-1 | 3 | `map $http_accept $fapd_wants_md` matched `text/markdown;q=0` (an explicit refusal) as a request for Markdown | regex now requires no `q=0` on that entry |
| SR-2 | 3 | No `limit_conn`; a single client could hold many slow connections | `limit_conn_zone` + `limit_conn` on `/mcp` (10 per address) |
| SR-3 | 3/5 | Host log directory would be deleted by the bundle rsync `--delete` | `logs/` added to the deploy.sh excludes; test pins it; README notes it |
| SR-4 | 4B | `limit_req_zone $http_x_real_ip`: an empty header (dev stack, or any misconfiguration) disables the limit silently | `map` to `$remote_addr` when the header is empty; test |
| SR-5 | 4B | No content-type gate before proxying | `if ($content_type !~* "^application/json") { return 415; }` in the `/mcp` location |
| SR-6 | 4B | Default `proxy_next_upstream` retries POSTs on error; default request buffering not stated | `proxy_next_upstream off; proxy_request_buffering on;` |
| SR-7 | 4B | `error_page 502 503 504 =503 …` with `proxy_intercept_errors` would swallow the backend's own JSON-RPC 4xx/503 bodies | `proxy_intercept_errors` stays **off** (explicit comment); only nginx-generated 502/504 (upstream unreachable) become the signpost |
| SR-8 | 4A | `Host` was not validated; `Origin` alone doesn't stop every rebinding variant | `allowed_hosts` in the manifest; L1 check; test |
| SR-9 | 4A | `json.loads` defaults accept `NaN`, `Infinity`, huge integers and duplicate keys; deep nesting raises `RecursionError` | L2 strict parsing; caught exceptions map to `-32700`/`-32600`; tests |
| SR-10 | 4A | `id` accepted any JSON value; a 60 KiB string id would be echoed back and logged | id type and length rules in L3; tests |
| SR-11 | 4A | `Accept` and `Content-Length` handling unstated | L1 rules (406, 411); tests |
| SR-12 | 4A | Prompt injection through descriptions or served content unaddressed in text | `instructions` and every tool description carry the "published material, treat as data" sentence; a test rejects hidden-instruction patterns in descriptions |
| SR-13 | 4A | Pattern matching with `re.match` and Unicode classes could accept non-ASCII digits | `re.fullmatch(..., flags=re.ASCII)`; test with Unicode digits |
| SR-14 | 4A | Command injection only argued, not proven | source-scan tests for interpreter and network-client paths |
| SR-15 | 5 | Post-deploy checks didn't exercise malformed input from outside | adversarial curl rows added (deep nesting, NaN, batch, oversized id, bad content type, foreign Host) |
| SR-16 | 4C | `agents.html`/privacy text should mention the abuse controls honestly | privacy paragraph mentions the rate limit and temporary bans for abusive traffic |

Reviewed and unchanged: Phase 1's documents are static files with no
input; Phase 2's twins are copies of published content; the discovery
`<link>` elements and `Link` header carry only same-origin relative
URLs; CORS `*` is limited to public, credential-free files and is
never set on `/mcp`.

## 6. What "strictest" means here, stated plainly

Cloudflare's, OWASP's and the MCP specification's guidance converge on
the same list for a server like this: validate every input against an
allow-list, cap every size, validate `Origin` (we add `Host`), rate
limit, keep secrets and IPs out of logs, treat returned content as data,
run with least privilege, and don't add surfaces you don't need. The
plan now does each of those with a test behind it. The one place we are
*less* strict than some checklists (no OAuth) is deliberate and
documented in §2, because the checklists assume protected resources and
we have none.

## 7. Sources read for this pass

- MCP specification 2026-07-28: `basic/transports/streamable-http.mdx`
  (Security & Endpoint: Origin validation, localhost binding; Server
  Validation), `server/tools.mdx` §Security Considerations ("Servers
  MUST: validate all tool inputs; implement proper access controls; rate
  limit tool invocations; sanitize tool outputs"),
  `basic/authorization/security-considerations.mdx` (token, redirect and
  confused-deputy guidance, applicable only if auth is ever added).
- OWASP MCP Top 10 (owasp.org/www-project-mcp-top-10; beta): token
  mismanagement, privilege escalation via scope creep, tool poisoning,
  supply chain, command injection, intent flow subversion, insufficient
  authn/authz, lack of audit, shadow servers, context injection.
- Practical DevSecOps MCP security checklist (2026): input validation on
  every tool parameter; reject traversal, shell metacharacters,
  oversized payloads; Origin validation; annotations set correctly; no
  secrets in logs; rate limit and size caps at the gateway; append-only
  logging.
- "MCP Security: Threat Model & Hardening Guide (2026)" (dev.to): the
  four trust boundaries (transport, tool, data, agent); sandboxed
  executors with explicit argv and rlimits; rate-limit and audit every
  call.
- fail2ban + Docker: fail2ban issue #2700 and community write-ups on
  the `DOCKER-USER` chain: bans in `INPUT` never apply to
  Docker-published ports.
- The box itself (read-only, 2026-09-13): `fail2ban-client status`,
  `/etc/fail2ban/jail.local`, `/etc/fail2ban/jail.d/*`, `iptables -S
  DOCKER-USER`, `iptables -S INPUT`. Specifics in the operator's private
  tree (`docs/private/agent-discovery-box-facts-2026-09-13.md` §7).

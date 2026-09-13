# Phase 4 — the no-inference MCP service (agent discovery)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md)
(the master plan; read §3 rulings D2/D10/D12, §4 VPS findings, §5
architecture, §7 protocol and §8.4 identity contract first). Task AD-14,
split into three sub-phases with separate owners:*

| Sub-phase | Performed by | Depends on | Parallel with |
|---|---|---|---|
| **4A — generic `static-mcp` package** | `general-purpose` agent, ownership exactly `packages/static-mcp/**` | Phase 0 merged | Phases 1, 2, 3 |
| **4B — FAPD MCP service integration** | `fapd-operations` agent (continued from Phase 3) | Phases 3 and 4A merged | 4C |
| **4C — MCP publication surfaces** | `fapd-publication` agent (continued from Phase 2) | Phases 2 and 4A merged; reads 4B's manifest (see §C.0) | 4B |

*The companion guide [`docs/mcp-server.md`](../mcp-server.md) is the
design of record for the service. Sub-phases 4A and 4B turn it into the
as-built guide. Last reviewed: 2026-09-13.*

---

## Shared background (all three sub-phases)

### What MCP is, in two paragraphs

The Model Context Protocol lets an AI application ("client") call
**tools** and read **resources** offered by a "server", using JSON-RPC
2.0 messages. Over HTTP (the "Streamable HTTP" transport) the client
POSTs one JSON-RPC message per request to a single endpoint, here
`https://fapd.info/mcp`, and the server answers with JSON (or, optionally,
a Server-Sent Events stream; this server never streams).

The protocol changed shape on **2026-07-28**. Revisions up to
**2025-11-25** ("legacy") start with an `initialize` handshake and may use
sessions. **2026-07-28** ("modern") is stateless: no handshake, every
request carries its protocol version and client info in
`params._meta`, the HTTP request mirrors key fields in headers
(`MCP-Protocol-Version`, `Mcp-Method`, `Mcp-Name`), and servers must
implement `server/discover`. Clients in use in September 2026 are a mix
of both eras, so this server is **dual-era** and **stateless in both**.
It never mints a session ID; legacy revisions allow that.

### Pinned specification pages (read the ones for your sub-phase)

All in `https://github.com/modelcontextprotocol/modelcontextprotocol`, path
`docs/specification/<revision>/…`:

| Topic | Modern `2026-07-28` | Legacy |
|---|---|---|
| Changelog (what changed and why) | `changelog.mdx` | — |
| Transport | `basic/transports/streamable-http.mdx` (Security & Endpoint; Sending Messages; Request Metadata; Server Validation; Backward Compatibility) | `2025-11-25/basic/transports.mdx`, `2025-06-18/basic/transports.mdx` |
| Versioning / eras | `basic/versioning.mdx` (compatibility matrix; dual-era server rules) | `2025-11-25/basic/lifecycle.mdx` (initialize) |
| Discovery | `server/discover.mdx` | — |
| Base protocol, `_meta`, error codes | `basic/index.mdx` | `2025-11-25/basic/index.mdx` |
| Tools | `server/tools.mdx` | `2025-11-25/server/tools.mdx` |
| Resources | `server/resources.mdx` | `2025-11-25/server/resources.mdx` |
| Caching (`ttlMs`, `cacheScope`) | `server/utilities/caching.mdx` | — |
| Schema (source of truth for shapes) | `schema/2026-07-28/schema.ts` | `schema/2025-11-25/schema.ts` |

Plus: the Server Card extension
(`https://github.com/modelcontextprotocol/experimental-ext-server-card`,
`schema.ts` and `docs/discovery.md`); the MCP Registry
(`https://github.com/modelcontextprotocol/registry`,
`docs/modelcontextprotocol-io/remote-servers.mdx` and `authentication.mdx`);
and the conformance suite `https://github.com/modelcontextprotocol/conformance`
(active as of 2026-09-13).

**If the plan and the pinned spec disagree, the spec wins.** Record the
difference in your progress log with a `BLOG:` line, implement the spec,
and report the deviation.

### Facts established 2026-09-13 that the design relies on

- Modern: `server/discover` is required; results carry
  `resultType: "complete"`; list and read results carry `ttlMs` and
  `cacheScope`; unknown method → HTTP **404** with JSON-RPC `-32601`;
  header/body mismatch or missing required header → HTTP **400**, code
  **`-32020`** (HeaderMismatch); unsupported version → HTTP **400**, code
  **`-32022`** with `data.supported` and `data.requested`; resource not
  found → **`-32602`** (was `-32002`; clients should accept both); GET or
  DELETE on the endpoint → **405**; a notification POST → **202** with no
  body; `ping` and `logging/setLevel` were removed; `Mcp-Session-Id` and
  `Last-Event-ID` are ignored.
- Servers **MUST** validate `Origin` and answer an invalid one with
  **403**.
- A dual-era server serves a request carrying modern `_meta` statelessly
  under 2026-07-28, and serves an `initialize` request (and what follows
  it) under the negotiated legacy revision. It **MAY** do both on one
  endpoint.
- A Server Card describes **remote** connectivity only (SEP-2127, Final).
  Its schema is `https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json`
  with required `$schema`, `name` (reverse-DNS with exactly one `/`),
  `version`, `description` (≤100 chars), and optional `title`,
  `websiteUrl`, `repository {url, source, subfolder?, id?}`, `icons`,
  `remotes[] {type: "streamable-http"|"sse", url, headers?, variables?,
  supportedProtocolVersions?}`, `_meta`. Cards don't list tools. The
  recommended location is `<endpoint>/server-card`.
- MCP Registry: `server.json` with `$schema`
  `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`
  (verify the current date-stamped schema at publish time), `name`,
  `title`, `description`, `version`, `remotes[]`. The domain namespace
  `info.fapd/*` is proven by HTTP auth (`/.well-known/mcp-registry-auth`)
  or a DNS TXT record at the apex.

---

## A — the generic `static-mcp` package (AD-14a)

### A.0 Outcome

A stdlib-only Python package, `packages/static-mcp/`, that turns **a
directory of static files plus a declarative JSON manifest** into a
correct, dual-era, read-only MCP server over Streamable HTTP. It carries
no project-specific knowledge: the operator's other projects run the same
code with their own manifest. It ships with its own README (a reuse
guide), its own tests, a generic Dockerfile and a neutral example
manifest.

**Design stance (why a manifest and not code):** a declarative manifest
can only describe reads of files under one root, so the guarantees are
structural. No tool can write, call a model, or reach the network,
because no handler kind exists that does. Adding a capability means
adding a handler kind to the package, which is a reviewed code change.
It can't be configured into existence on the box.

### A.1 Ownership

**May edit / create:** everything under `packages/static-mcp/`, and only
that.
**Shared-file diffs for the exit report:** `pyproject.toml`
(`[tool.pytest.ini_options] testpaths` gains
`"packages/static-mcp/tests"`), `.github/workflows/ci.yml` (ruff paths
gain `packages/`), and `deploy/vps/scripts/deploy.sh` (ruff paths gain
`packages/`; Operations applies that one in 4B).
**Must not:** import anything from `fapd`, mention FAPD/fapd, or read
anything outside the package. A test enforces this (A.6 #12).

### A.2 Layout

```
packages/static-mcp/
  README.md                  what it is, security model, manifest reference, reuse guide, running, testing
  LICENSE                    Apache-2.0 (the repository's code licence), copied
  pyproject.toml             name "static-mcp", requires-python ">=3.12", dependencies = [], script static-mcp
  Dockerfile                 generic image (A.5)
  examples/
    docs-site.manifest.json  neutral example: a small documentation site
  src/static_mcp/
    __init__.py              __version__ = "0.1.0"
    __main__.py              python -m static_mcp → cli.main()
    errors.py                JSON-RPC and MCP error codes; exception types carrying (http_status, code, message, data)
    manifest.py              load + validate a manifest; compile params into validators and JSON Schemas
    handlers.py              the handler kinds (A.3.4); pure functions of (root, manifest item, validated args)
    protocol.py              era classification, version negotiation, header validation, result envelopes
    dispatch.py              method tables per era → handlers; builds tools/resources lists deterministically
    server.py                stdlib HTTP server: limits, Origin check, logging, /healthz
    card.py                  build_card(manifest) → MCP Server Card dict; build_registry_server_json(manifest)
    cli.py                   serve | check | card | registry-json | describe
  tests/
    conftest.py              sys.path insert of ../src; fixture site copied from tests/fixtures
    fixtures/site/…          neutral files: guide.txt, index.json, pages/2026-01-01.md, notes/*.md, big.json
    fixtures/manifest.json   exercises every handler kind
    test_manifest.py  test_handlers.py  test_protocol_modern.py  test_protocol_legacy.py
    test_http_server.py  test_security.py  test_card.py  test_cli.py  test_no_project_strings.py
```

### A.3 Behavior specification

#### A.3.1 Manifest (version 1)

JSON. Unknown top-level keys are an error, so typos don't silently
disable limits.

```json
{
  "manifest_version": 1,
  "server": {
    "name": "com.example/docs",
    "title": "Example Docs",
    "version": "1.0.0",
    "description": "Read-only access to the Example documentation. No inference.",
    "websiteUrl": "https://example.com/",
    "repository": {"url": "https://github.com/example/docs", "source": "github", "subfolder": "packages/static-mcp"},
    "instructions": "Plain-language guidance returned by server/discover and initialize."
  },
  "public_base_url": "https://example.com",
  "endpoint_path": "/mcp",
  "protocol_versions": {"modern": ["2026-07-28"], "legacy": ["2025-11-25", "2025-06-18"]},
  "http": {
    "allowed_origins": ["https://example.com"],
    "allow_missing_origin": true,
    "max_body_bytes": 65536,
    "max_concurrency": 16,
    "request_timeout_seconds": 10
  },
  "limits": {"max_file_bytes": 16777216, "max_result_bytes": 524288},
  "cache": {"ttl_ms": 300000, "scope": "public"},
  "params": {
    "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$", "description": "A date, YYYY-MM-DD."},
    "slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,62}$", "description": "A page slug."}
  },
  "resources": [
    {"uri": "https://example.com/guide.txt", "name": "guide", "title": "Guide", "description": "…", "mimeType": "text/plain", "file": "guide.txt"}
  ],
  "resource_templates": [
    {"uriTemplate": "https://example.com/pages/{date}.md", "name": "page", "title": "Page", "description": "…", "mimeType": "text/markdown", "file": "pages/{date}.md", "params": ["date"]}
  ],
  "tools": [
    {
      "name": "get_page",
      "title": "Get a page",
      "description": "…",
      "params": {"date": {"ref": "date", "required": true}},
      "preamble": "Optional text returned as the first content block.",
      "handler": {"kind": "text_file", "file": "pages/{date}.md", "mime_type": "text/markdown",
                  "not_found": "No page exists for {date}."}
    }
  ]
}
```

Validation rules (`manifest.py`, each with a test):
- `server.name` matches `^[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+$`;
  `description` ≤ 100 chars; `version` has no range operators.
- Every `pattern` starts with `^` and ends with `$`. **A string parameter
  used in a file template may not match `/`, `\`, `..`, or a leading `.`.**
  The validator proves it by testing the compiled regex against the
  strings `/`, `a/b`, `..`, `.x`, `a\\b`, and rejects the manifest if any
  match.
- Integer params require `minimum` and `maximum`. `limit`-type params
  require a `maximum`.
- Every `{name}` in a `file`/`uriTemplate` names a declared parameter.
- Tool and resource names are unique and match `^[a-z][a-z0-9_]{0,63}$`
  (tools) / `^[a-z][a-z0-9-]{0,63}$` (resources).
- Limits have ceilings that the package enforces even if the manifest
  asks for more: body ≤ 1 MiB, concurrency ≤ 64, result ≤ 4 MiB, file ≤
  64 MiB.
- `protocol_versions.modern` ⊆ the versions this package implements
  (`{"2026-07-28"}`); `legacy` ⊆ `{"2025-11-25", "2025-06-18"}`.
  Anything else is an error, not a silent downgrade.

#### A.3.2 Parameters → `inputSchema`

Each tool's `inputSchema` is generated: `{"type": "object", "properties":
{…}, "required": […], "additionalProperties": false}`, with `type`,
`pattern`, `minimum`/`maximum`, `default` and `description` copied from
the param definition. Arguments are validated by the package's own
validator, **not** by trusting the client: an unknown argument, a wrong
type, or a pattern failure → JSON-RPC **`-32602`** (Invalid params) with
a message naming the parameter. Defaults are applied after validation.

#### A.3.3 Result shapes

- **`tools/call`** success → `{"content": [...], "structuredContent": …?,
  "isError": false}`. A content block is `{"type": "text", "text": …}`.
  For `json_file` handlers, `structuredContent` holds the JSON value and a
  text block carries `json.dumps(value, indent=1, ensure_ascii=False)`
  (the spec's recommended fallback for clients that ignore structured
  content). A `preamble` becomes the first text block.
- **Tool-level "not found"** (a valid date with no file) → a result with
  `isError: true` and the manifest's `not_found` text. That's a tool
  execution result, not a protocol error, so the model can read it and
  recover.
- **`resources/read`** unknown URI → `-32602` (modern) or `-32002`
  (legacy).
- **Modern** results add `"resultType": "complete"` and
  `"_meta": {"io.modelcontextprotocol/serverInfo": {"name", "title", "version"}}`.
  `tools/list`, `resources/list`, `resources/templates/list` and
  `resources/read` also add `"ttlMs"` and `"cacheScope"` from the
  manifest's `cache`. **Legacy** results carry none of those fields.
- **Truncation is never silent.** If a result would exceed
  `max_result_bytes`, `json_file` pages shrink `limit` until the result
  fits and set `"truncated": true, "truncation_note": "…reduce limit or
  page with offset…"` in `structuredContent`. A `text_file` over the
  limit returns `isError: true` naming the file size and the limit.
- `tools/list` order = manifest order (deterministic, as the spec asks).
  Tool `annotations`: `{"readOnlyHint": true, "destructiveHint": false,
  "idempotentHint": true, "openWorldHint": false}` on every tool, always.
  The manifest can't change them.

#### A.3.4 Handler kinds (the complete list for v1)

| kind | Fields | Does |
|---|---|---|
| `static_text` | `text` | returns fixed text (e.g. a pointer to documentation) |
| `text_file` | `file` (template), `mime_type`, `not_found` | reads one UTF-8 file under root |
| `json_file` | `file` (template), `select` (dotted key path to a list or object; omitted = whole document), `envelope` (list of top-level keys copied alongside), `fields` (list of item keys kept; omitted = all), `filters` (see below), `find` (`{field, param}`: return the single item whose `field` equals the argument, or `not_found`), `page` (`{offset: <param>, limit: <param>}`), `order` (`"asc"`/`"desc"` by position), `not_found` | reads, selects, filters, projects, pages |
| `file_listing` | `glob` (relative, no `..`), `name_pattern` (anchored regex with one named group `key`), `order`, `page` | lists matching files, returning the `key` values (e.g. the dates of available pages) |

`filters`, applied in order before paging:
- `{"param": "<bool param>", "when": false, "exclude_where": {"field": "<f>", "equals": <json>}}`:
  when the argument equals `when`, drop items whose `field` equals the
  value.
- `{"param": "<string param>", "match_field": "<f>"}`: when the argument
  is present, keep only items whose `field` equals it.

That's the whole query language. **No free-text search, no regex from
clients, no sorting by client-chosen field.** If a project needs more, it
adds a handler kind in code, with tests and a security review.

**File access (`handlers.py`), the security core:**
1. Substitute validated arguments into the template.
2. `candidate = (root / rel).resolve(strict=True)`. A missing file is
   `not_found`.
3. Require `candidate.is_relative_to(root.resolve())`. Otherwise raise an
   internal error (logged as a security event) and return `-32603` with
   no path in the message.
4. Require a regular file, size ≤ `max_file_bytes`.
5. Read bytes, decode UTF-8 (JSON via `json.loads`). A failure is a tool
   error naming nothing but the tool.
6. Parsed JSON is cached by `(path, st_mtime_ns, st_size)` in a small LRU
   (16 entries), so a large file is parsed once per change.

#### A.3.5 HTTP behavior (`server.py`)

Built on `http.server.ThreadingHTTPServer` with
`protocol_version = "HTTP/1.1"` (every response sets `Content-Length`).
Stdlib's HTTP server isn't hardened for direct internet exposure. The
design assumes a reverse proxy in front of it (FAPD: nginx buffers the
request body and applies timeouts and rate limits). The README states
this plainly.

| Request | Response |
|---|---|
| `GET /healthz` | 200 `ok` (text/plain), for container health checks |
| `POST <endpoint_path>` with `Origin` present and not in `allowed_origins` | **403**, JSON-RPC error body without `id` |
| `POST` with no `Origin` and `allow_missing_origin: false` | 403 |
| `POST` with `Content-Length` > `max_body_bytes` (or absent) | **413** / 411 |
| `POST` with a body that isn't `application/json` | **415**, JSON-RPC error without `id` |
| `POST` with invalid JSON | **400**, `-32700` Parse error, `id: null` |
| `POST` with a JSON array (batch) | **400**, `-32600` "batching is not supported" |
| `POST` with a JSON-RPC notification (no `id`) | **202**, empty body |
| `POST` with a request, dispatched per A.3.6 | 200 / 400 / 404 as specified there |
| `GET` / `DELETE` / anything else on the endpoint | **405** with `Allow: POST` |
| any other path | 404 |
| `max_concurrency` requests already in flight | **503**, `Retry-After: 1` |

Every response: `Cache-Control: no-store`, `X-Content-Type-Options:
nosniff`, `Content-Type: application/json` (except `/healthz`). **Never
SSE.** An `Mcp-Session-Id` or `Last-Event-ID` request header is ignored,
and no session header is ever sent.

Socket timeout = `request_timeout_seconds`. Handler exceptions →
`-32603` Internal error, with the traceback logged and never returned.

**Logging (stdout, one JSON object per line):** `ts` (UTC ISO),
`http_method`, `path`, `status`, `rpc_method`, `mcp_name` (tool name or
resource name/URI as given in `Mcp-Name` or params), `era`,
`protocol_version`, `duration_ms`, `response_bytes`, `user_agent`
(truncated to 200 chars), `event` (e.g. `security.path_escape`).
**Never logged: client IP, request body, arguments, `Authorization` or
other headers.** The README's privacy section says exactly this.

#### A.3.6 Era classification and dispatch (`protocol.py`, `dispatch.py`)

For a single JSON-RPC request object `msg` and headers `h` (names are
case-insensitive):

1. If `msg.params._meta["io.modelcontextprotocol/protocolVersion"]` is
   present → **modern**:
   1. `v` = that value. If `v` ∉ `modern` → HTTP 400, `-32022`,
      `data: {"supported": modern + legacy, "requested": v}`.
   2. Require `h["MCP-Protocol-Version"] == v`, `h["Mcp-Method"] ==
      msg.method`, and, for `tools/call` (`params.name`) and
      `resources/read` (`params.uri`), `h["Mcp-Name"]` equal to that value
      after decoding the `=?base64?…?=` sentinel form. A missing or
      mismatched header → HTTP 400, `-32020`.
   3. Methods: `server/discover`, `tools/list`, `tools/call`,
      `resources/list`, `resources/read`, `resources/templates/list`.
      Anything else (including `initialize`, `ping`,
      `subscriptions/listen`) → HTTP **404**, `-32601`.
   4. `server/discover` result: `supportedVersions` = `modern` list;
      `capabilities`: `{"tools": {}, "resources": {}}` (no `listChanged`,
      no `subscribe`); `instructions`; `_meta.serverInfo`; `ttlMs`,
      `cacheScope`.
2. Else if `msg.method == "initialize"` → **legacy handshake** (no
   session): requested `params.protocolVersion`; negotiated = requested if
   in `legacy`, otherwise the newest `legacy` entry. Result:
   `{"protocolVersion": negotiated, "capabilities": {"tools":
   {"listChanged": false}, "resources": {"listChanged": false, "subscribe":
   false}}, "serverInfo": {"name", "title", "version"}, "instructions"}`.
3. Else → **legacy follow-on**: if `h["MCP-Protocol-Version"]` is present
   and is a modern version → HTTP 400, `-32020` ("modern version header
   without _meta"). If present and not in `legacy` → HTTP 400,
   JSON-RPC `-32600` naming the supported versions. If absent → treat as
   the newest `legacy` entry, which is lenient toward older clients (the
   spec lets a server assume a default). Methods: `ping` (→ `{}`),
   `tools/list`, `tools/call`, `resources/list`, `resources/read`,
   `resources/templates/list`. Unknown → HTTP **200** with `-32601`
   (legacy HTTP servers answered errors in-band).
4. The JSON-RPC `id` is echoed exactly (string or number), always.

### A.4 CLI (`cli.py`)

- `static-mcp serve --manifest PATH --root DIR [--host 127.0.0.1] [--port 8080]`
  validates the manifest, **refuses to start** if `--root` is missing or
  any non-template `file` in `resources` is missing (fail loud on missing
  config: code-standards §2 r9), then serves. The default host is
  `127.0.0.1`: binding all interfaces must be explicit (the container
  passes `0.0.0.0`).
- `static-mcp check --manifest PATH [--root DIR]` validates and prints a
  summary. Exits non-zero on any error.
- `static-mcp card --manifest PATH` prints the Server Card JSON
  (`card.build_card`): `$schema` v1 URL, `name`, `version`,
  `description`, `title`, `websiteUrl`, `repository`, and `remotes =
  [{"type": "streamable-http", "url": public_base_url + endpoint_path,
  "supportedProtocolVersions": modern + legacy}]`.
- `static-mcp registry-json --manifest PATH --schema-url URL` prints the
  MCP Registry `server.json` (name, title, description, version,
  `remotes`).
- `static-mcp describe --manifest PATH` prints a Markdown table of tools,
  parameters and resources. 4B uses it for `docs/mcp-server.md`, and 4C
  uses the same function for `agents.html`.

### A.5 Generic Dockerfile

```dockerfile
# static-mcp — a read-only MCP server over a directory of static files.
# Stdlib only; no dependencies to install.
FROM python:3.12-slim
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin staticmcp
COPY src/ /opt/static-mcp/src/
ENV PYTHONPATH=/opt/static-mcp/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 --start-period=5s \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).status == 200 else 1)"]
ENTRYPOINT ["python", "-m", "static_mcp", "serve", "--root", "/srv/site", "--host", "0.0.0.0", "--port", "8080"]
CMD ["--manifest", "/etc/static-mcp/manifest.json"]
```

`python:3.12-slim` matches the FAPD backend's base, so one CVE sweep
covers both (AGENT-CVE-GUIDE parity rule). A project that prefers another
base changes one line.

### A.6 Tests (all must fail without the code they cover)

1. **Manifest:** the example and the fixture manifest validate; each rule
   in A.3.1 has a rejecting case (unanchored pattern, slash-matching
   pattern, missing maximum, unknown key, bad server name, over-ceiling
   limit, unknown protocol version).
2. **Handlers:** every kind, every filter, `find`, paging (`offset`,
   `limit`, `next_offset`, `total`), projection, `not_found`, JSON cache
   invalidation on mtime change, truncation note.
3. **Modern protocol:** `server/discover` shape; `tools/list` (order,
   annotations, `inputSchema`, `ttlMs`/`cacheScope`, `resultType`,
   `_meta.serverInfo`); `tools/call` success and `isError`;
   `resources/list`, `resources/templates/list`, `resources/read`
   (found; unknown → `-32602`); unsupported version → 400/`-32022` with
   `supported`; each header-mismatch case → 400/`-32020` (missing
   `MCP-Protocol-Version`, mismatched `Mcp-Method`, missing `Mcp-Name` on
   `tools/call`, base64-sentinel `Mcp-Name` that decodes correctly is
   accepted); unknown method → 404/`-32601`; `initialize` sent with modern
   `_meta` → 404.
4. **Legacy protocol:** `initialize` negotiation (requested supported;
   requested unknown → newest legacy); no `Mcp-Session-Id` in response;
   `notifications/initialized` → 202; `ping`; tools and resources calls
   without `_meta`; resource not found → `-32002`; modern version header
   without `_meta` → 400/`-32020`.
5. **HTTP:** every row of A.3.5 against a server started on an ephemeral
   port in a thread; the `id` echo for string and numeric ids;
   `Content-Length` correct; `Cache-Control: no-store`.
6. **Security:** path escape attempts through a deliberately permissive
   test-only handler bypassing manifest validation (prove the resolve
   check alone stops `../`, absolute paths and a planted symlink
   pointing outside root); oversize body; slow client hits the timeout;
   concurrency cap yields 503; no traceback text in any response; log
   lines contain no body, no argument value, no IP (plant a unique token
   in arguments and assert it never appears in captured stdout).
7. **Card:** `build_card` output satisfies the v1 schema's required
   fields and patterns (write the checks; no dependency); description
   length; `remotes` URL = base + path.
8. **Registry JSON:** fields present; `$schema` taken from the argument.
9. **CLI:** `check` exit codes; `serve` refuses a missing root; the
   default host is `127.0.0.1`.
10. **Conformance smoke:** a scripted transcript per era (JSON files in
    `tests/fixtures/transcripts/`) replayed against the server with
    exact expected responses (ignoring `_meta` timing fields).
11. **Determinism:** two `tools/list` calls return byte-identical bodies.
12. **No project strings:** scan every file under `packages/static-mcp/`
    for `fapd`, `FAPD`, `federal`, `digest` (case-insensitive) and fail
    on any match. Keeps the package reusable.

Also run the **official conformance suite**
(`github.com/modelcontextprotocol/conformance`) locally against the
fixture server, if it supports a server target for 2026-07-28. Record
the command, version and results (pass, fail, not applicable) in the
progress log and exit report. If it needs Node, run it with `npx` in a
throwaway directory; it isn't added to the repo.

### A.7 README (`packages/static-mcp/README.md`) must cover

1. What it is (one paragraph), and what it will never do (write, infer,
   fetch, authenticate, stream).
2. Security model: read-only root, validated parameters, resolve
   containment, limits, no sessions, Origin check, logs without bodies or
   IPs, and the "put a reverse proxy in front" requirement, with a
   minimal nginx `location` example (POST only, body cap, rate limit,
   timeouts, variable upstream).
3. Manifest reference (every key in A.3.1 and A.3.4), with the neutral
   example.
4. **Reusing it in another project:** copy or vendor the package (or
   `pip install` from a path/git URL); write a manifest; `static-mcp
   check`; run locally; the container; put it behind the proxy; publish a
   card with `static-mcp card`; list it in the MCP Registry with
   `static-mcp registry-json`; a checklist of the decisions a project
   must make (which files, which params, allowed origins, limits).
5. Protocol support table (modern 2026-07-28; legacy 2025-11-25 and
   2025-06-18, without sessions; not supported: SSE, subscriptions,
   sampling, elicitation, prompts, batching, 2025-03-26 and earlier) and
   how to add a protocol revision.
6. Testing: `uv run pytest -q packages/static-mcp/tests`, plus the
   conformance suite.

### A.8 Acceptance criteria (4A)

1. Every A.6 test exists and passes. The package's tests run from the
   repo root once the `testpaths` diff is applied (report both ways).
2. The conformance suite result is recorded (or the reason it couldn't
   run).
3. No dependency added; `import static_mcp` works with only the stdlib.
4. The no-project-strings test passes.
5. `ruff check packages/` clean.
6. The README covers A.7 completely.

### A.9 Dispatch prompt (general-purpose agent)

```
You are building a reusable software package inside the FAPD repository.
You are NOT a FAPD section agent; your ownership is exactly
packages/static-mcp/** and nothing else. Before anything else read, in
order: docs/ops/plan-2026-09-13-agent-discovery.md (§7 working protocol
is binding), docs/ops/plan-2026-09-13-phase4-mcp-service.md "Shared
background" and all of section A, docs/code-standards.md, and
docs/mcp-server.md.

TASK: Build the generic, stdlib-only, dual-era, read-only MCP server
package `static-mcp` exactly as specified in section A of the phase file
(manifest v1, handler kinds, protocol behavior for MCP 2026-07-28 plus
legacy 2025-11-25/2025-06-18 without sessions, HTTP behavior and limits,
logging without bodies/IPs, CLI, generic Dockerfile, README reuse guide,
and every test in A.6), meeting every acceptance criterion in A.8. Read
the pinned specification pages listed in "Shared background" before
writing protocol code; where the spec and the plan disagree, implement
the spec and report the difference.

CONTEXT: Branch feature/agent-discovery. The package must contain no
FAPD-specific name, path, or import — the operator will reuse it in other
projects; FAPD's own manifest and container wiring are Phase 4B, done by
another agent. Phases 1–3 run at the same time in the same tree and touch
no file under packages/. Keep the progress log required by master plan
§7.2 at research/agent-logs/agent-discovery-phase4a-<YYYYMMDD>.md; write
its first entry before touching any file. Do not run anything against the
VPS. Local Docker and npx in a throwaway directory are fine for the
conformance suite.

CONTRACT (non-negotiable):
1. Edit only packages/static-mcp/**. Shared-file changes (pyproject.toml
   testpaths, .github/workflows/ci.yml, deploy/vps/scripts/deploy.sh ruff
   paths) go in your exit report as exact diffs.
2. Stage nothing, commit nothing. Leave the working tree modified.
3. Run `uv run ruff check .` and `uv run pytest -q packages/static-mcp/tests`
   and `uv run pytest -q` before reporting; report the actual numbers.
4. Follow docs/code-standards.md: stdlib-first, DI by optional
   parameters (clock, root, stdout writer), pure functions, fail loud on
   missing config.
5. New behavior gets a test that fails without the change.
6. If blocked, exit and report the blocker — do not improvise around it.

EXIT REPORT (required shape):
- Files created/modified (list)
- Shared-file diffs needed (exact diffs)
- Verification: ruff + pytest tails; conformance suite command and result
- Spec-vs-plan differences found, with the spec citation
- Deviations from the task, with rationale
- What a human should look at before this merges (especially security)
- Acceptance criteria A.8, each marked met / not met with evidence
- Progress log path, and all BLOG: lines copied out
```

---

## B — FAPD MCP service integration (AD-14b)

### B.0 Outcome

The generic package runs as `fapd-mcp` in the FAPD Docker stack (prod
and dev) with FAPD's manifest. `fapd-web` proxies `POST /mcp` to it over
a new internal network. The stack's invariants (master plan §5) are
pinned by tests. Runbooks and `docs/mcp-server.md` describe the service
as built. Nothing is deployed; that's Phase 5.

### B.1 Ownership

**May edit / create:** `deploy/vps/mcp/fapd.manifest.json`,
`deploy/vps/mcp/README.md`, `deploy/vps/docker-compose.yml`,
`deploy/dev/docker-compose.yml`, `deploy/dev/scripts/dev-up.sh` (only if
it needs to stage `packages/`; it already stages the repo),
`deploy/vps/nginx/default.conf` (the two insertion points only),
`deploy/vps/nginx/rehearse.sh` (MCP rows),
`deploy/vps/scripts/deploy.sh`, `docs/mcp-server.md`,
`docs/ops/OPS-GUIDE.md`, `docs/ops/SERVER-GUIDE.md` (rows marked
"pending deploy"), `docs/ops/AGENT-CVE-GUIDE.md` (the new container row),
`deploy/vps/README.md`, `tests/test_dev_stack.py`,
`tests/test_web_conf.py`, new `tests/test_mcp_manifest.py`,
`.claude/skills/fapd-health/` (add the MCP liveness check; read-only
commands only).
**Shared-file diffs:** `CLAUDE.md` (if anything beyond Phase 0's text is
needed), `.github/workflows/ci.yml`.

### B.2 The FAPD manifest (`deploy/vps/mcp/fapd.manifest.json`)

`server` block per master plan §8.4. `public_base_url`
`https://fapd.info`; `endpoint_path` `/mcp`; `allowed_origins`
`["https://fapd.info", "https://www.fapd.info"]` with
`allow_missing_origin: true` (server-side clients send no Origin);
`max_body_bytes` 65536; `max_concurrency` 16; `limits.max_file_bytes`
16 MiB (a heavy day's JSON has measured 3.7 MB); `max_result_bytes`
512 KiB; `cache` `{ttl_ms: 300000, scope: "public"}`.

`server.instructions` (plain, ≤ ~700 chars; no banned-lexicon terms):

> The Free Agentic Publication Digester publishes a validated daily
> digest of official United States federal publications. Congressional,
> executive and judicial items are selected by mechanical, party-blind
> rules, and every item cites its official source. This service returns
> published files verbatim; no model writes its responses. Dated digests
> are the record. The live day (get_live_day) is preliminary and changes
> until the end-of-day gates freeze it. Lines labeled FAPD-AI are the
> project's model-written restatements. For factual claims, cite the
> official source linked on each item, and credit FAPD for the
> aggregation (CC BY 4.0).

**Verify every field name below against the real files** (`publish.py`
`build_today` payload and `_sources_json`; a built `site/`) before
writing the manifest, and record what you checked in the progress log.
If a field doesn't exist, drop the filter or projection and note it.

| Tool | Params | Handler | Preamble |
|---|---|---|---|
| `list_digests` | `offset` (0…10000, default 0), `limit` (1…60, default 14) | `json_file` `digests.json`, `select: digests`, `fields: [date, html, canonical_markdown, teaser]`, `envelope: [title]`, page | — |
| `get_digest` | `date` (required) | `text_file` `{date}.md`, `text/markdown`, not_found "No digest was published for {date}. Call list_digests for published dates; weekends and federal holidays often have none." | "Canonical digest Markdown from fapd.info, returned verbatim (CC BY 4.0). Text labeled FAPD-AI is model-written restatement; cite each item's official source for claims." |
| `get_live_day` | `offset`, `limit` (1…100, default 50), `include_backfill` (bool, default false), `collection` (pattern `^[A-Z][A-Z0-9_]{1,15}$`, optional) | `json_file` `today.json`, `select: items`, `envelope: [date, disclosure, canonical_record, labels, counts, day_context, backfill_count, corroborated_count, pending_llm, last_observed_at]`, filters (backfill exclusion; `collection` match), page | "PRELIMINARY: observed so far today; items may change until the end-of-day digest freezes the record." |
| `list_day_views` | `offset`, `limit` (1…366, default 30) | `file_listing` `day/*.json`, `name_pattern ^(?P<key>[0-9]{4}-[0-9]{2}-[0-9]{2})\.json$`, `order: desc`, page | — |
| `get_day_listing` | `date` (required), `offset`, `limit`, `include_backfill`, `collection` | `json_file` `day/{date}.json`, same select/envelope/filters as live (plus `frozen`, `reconstructed_on`), not_found "No frozen day view exists for {date}; call list_day_views." | "Frozen observed listing for a finished day. The dated digest remains the record." |
| `list_sources` | `offset`, `limit` (1…200, default 50) | `json_file` `sources.json`, `select: sources`, `envelope: [title, scope, measurement, window]`, `fields: [id, name, description, method, page]` (plus the status/health keys verified present) | "Describes this project's ingestion of each source, not any agency's performance." |
| `get_source` | `source_id` (pattern `^[a-z0-9][a-z0-9-]{0,62}$`, required) | `json_file` `sources.json`, `select: sources`, `find: {field: id, param: source_id}`, `envelope: [scope, measurement]` | same as above |
| `get_agent_guide` | — | `text_file` `llms.txt` | — |

Resources: `https://fapd.info/llms.txt` (text/plain), `/agents.md`
(text/markdown, Phase 2), `/auth.md`, `/digests.json`, `/sources.json`.
Templates: `https://fapd.info/{date}.md`, `/day/{date}.json`,
`/sources/{source_id}.md`.

**`tests/test_mcp_manifest.py`:** load the manifest with
`static_mcp.manifest` (sys.path insert of `packages/static-mcp/src`)
and validate it. Build a fixture site with `publish.build_site` +
`build_today` + `build_day` (reuse `_seed_today`), then call every tool
through the package's dispatcher **in process** and assert: non-error
results; the preamble is present where specified; `get_live_day` with
default args excludes backfill items; `get_digest` for a fixture date
byte-matches `digests/<date>.md`; `get_digest` for a missing date returns
`isError`. Every template's `file` exists in the fixture build for a
fixture value.

### B.3 Compose (prod) — `deploy/vps/docker-compose.yml`

```yaml
  mcp:
    # Read-only, no-inference MCP service (GUIDE §2a rule 4's one bounded
    # exception, 2026-09-13; docs/mcp-server.md). The generic static-mcp
    # package (packages/static-mcp) with FAPD's manifest. Reachable ONLY
    # from fapd-web over the internal fapd_mcp network: no published
    # port (Docker-published ports bypass ufw), no egress, no write
    # access anywhere.
    build:
      context: ./repo/packages/static-mcp
    image: fapd-mcp:latest
    container_name: fapd-mcp
    restart: unless-stopped
    command: ["--manifest", "/etc/static-mcp/fapd.manifest.json"]
    networks: [fapd_mcp]
    volumes:
      - fapd-site:/srv/site:ro
      - ./mcp:/etc/static-mcp:ro     # directory mount (inode rule)
    read_only: true
    user: "10001:10001"
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    pids_limit: 64
    mem_limit: 128m
    cpus: 0.5
    logging:
      driver: json-file
      options: { max-size: "5m", max-file: "3" }
```

`web` gains `networks: [fapd_edge, fapd_mcp]`. It does **not** get
`depends_on: mcp`: the site must start without the MCP service.

```yaml
networks:
  fapd_mcp:
    driver: bridge
    internal: true            # no default route: zero egress for both members
```

Dev compose: the same `mcp` service. The build context is
`./repo/packages/static-mcp`, since `dev-up.sh` stages `repo/`. Confirm,
and add staging if not. The same network. Dev `web` already publishes
8080, so MCP is reachable at `http://localhost:8080/mcp`.

### B.4 nginx: the two insertion points in `deploy/vps/nginx/default.conf`

At `PHASE-4B-HTTP-INSERTION-POINT`:

```nginx
# /mcp rate limit, keyed on the client address the edge proxy sets. Only
# the edge can reach fapd-web, so X-Real-IP is trustworthy here; the
# edge's own per-address limit still applies first.
limit_req_zone $http_x_real_ip zone=fapd_mcp:10m rate=5r/s;
```

At `PHASE-4B-SERVER-INSERTION-POINT`:

```nginx
    # The one bounded endpoint (GUIDE §2a rule 4, 2026-09-13).
    location = /mcp {
        if ($request_method !~ ^POST$) { return 405; }
        error_page 405 /_signpost/mcp-method.json;          # status stays 405
        client_max_body_size 64k;
        limit_req zone=fapd_mcp burst=20 nodelay;
        limit_req_status 429;

        # Variable upstream + Docker DNS: fapd-web starts even when
        # fapd-mcp is absent, and then answers 503 with a signpost.
        resolver 127.0.0.11 valid=10s ipv6=off;
        set $fapd_mcp_upstream http://fapd-mcp:8080;
        proxy_pass $fapd_mcp_upstream;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 2s;
        proxy_send_timeout 10s;
        proxy_read_timeout 15s;
        error_page 502 503 504 =503 /_signpost/mcp-unavailable.json;
        add_header Cache-Control "no-store" always;
    }

    # The Server Card lives under the endpoint path (spec-recommended);
    # the exact-match block above does not capture it.
```

Rehearsal rows to add to `rehearse.sh` (run the `fapd-mcp` image too,
on a throwaway network with the throwaway web container):

| # | Request | Expect |
|---|---|---|
| M1 | `POST /mcp` modern `server/discover` (headers + `_meta`) | 200, `supportedVersions` contains `2026-07-28`, serverInfo name `info.fapd/fapd` |
| M2 | `POST /mcp` legacy `initialize` (`protocolVersion` `2025-06-18`) | 200, `protocolVersion` `2025-06-18`, no `Mcp-Session-Id` header |
| M3 | modern `tools/call` `get_digest` for a fixture date | 200, text equals the digest Markdown after the preamble |
| M4 | `GET /mcp` | 405, JSON signpost body |
| M5 | `POST /mcp` with a 100 KB body | 413 |
| M6 | `POST /mcp` with `Origin: https://evil.example` | 403 |
| M7 | stop the mcp container, `POST /mcp` | 503, `mcp-unavailable` signpost; `GET /` still 200 |
| M8 | 60 rapid POSTs from one `X-Real-IP` | some 429s |
| M9 | `GET /mcp/server-card` (Phase 4C built) | 200, `application/mcp-server-card+json` (SKIP if 4C not merged) |
| M10 | from inside `fapd-mcp`: `python -c "import urllib.request; urllib.request.urlopen('https://example.com', timeout=3)"` | fails (no egress) |
| M11 | `docker inspect fapd-mcp`: `ReadonlyRootfs` true, `User` 10001, `CapDrop` ALL, no `Ports` bindings | as stated |

### B.5 deploy.sh

- `[1/4]` ruff paths gain `packages/`.
- `[3/4]` build line: `sudo docker compose --profile backend build backend mcp`.
- `[4/4]` verify gains a modern `server/discover` POST to
  `https://fapd.info/mcp`, printing the HTTP status and `serverInfo.name`.
- A comment block states the no-port rule.

### B.6 Tests (`tests/test_dev_stack.py`, `tests/test_web_conf.py`)

- Prod compose: `mcp` has no `ports:`, `read_only: true`, `cap_drop:
  [ALL]`, `no-new-privileges`, `user` non-root, networks exactly
  `[fapd_mcp]`, site volume mounted `:ro`, no other volume except the
  `./mcp` config mount `:ro`, and no `env_file`. Network `fapd_mcp` is
  `internal: true`. `web` networks exactly `[fapd_edge, fapd_mcp]`. The
  `mem_limit:` and `healthcheck:` counts are updated (the healthcheck
  lives in the Dockerfile. Decide whether compose repeats it, and pin
  whichever you choose).
- Dev compose mirrors prod for the `mcp` service and network.
- `test_web_conf.py`: the `/mcp` location is POST-only, has a body cap,
  a limit zone, a variable `proxy_pass`, `resolver 127.0.0.11`, and error
  pages to the two signposts; both insertion markers were replaced
  (absent); no static `upstream` block exists anywhere in the config.

### B.7 Docs

- `docs/mcp-server.md`: flip the banner from "design, not yet built" to
  "built, pending deploy" and fill in the as-built details (tool table
  generated by `static-mcp describe`, exact limits, the rehearsal).
- `docs/ops/OPS-GUIDE.md`: add MCP health checks (container health,
  `server/discover` POST, logs command) and the "no port" invariant
  check (`docker port fapd-mcp` prints nothing).
- `docs/ops/SERVER-GUIDE.md`: containers row gains `fapd-mcp`; networks
  row; review rows "pending deploy".
- `docs/ops/AGENT-CVE-GUIDE.md`: `fapd-mcp` (`python:3.12-slim`, stdlib
  only) joins the container inventory under the parity rule.
- `.claude/skills/fapd-health`: add the read-only MCP checks.

### B.8 Acceptance criteria (4B)

1. `rehearse.sh` passes rows 1–18 and M1–M11 (SKIPs explained).
2. The dev stack serves `http://localhost:8080/mcp` to a real client:
   run `claude mcp add --transport http fapd-dev http://localhost:8080/mcp`
   in a scratch directory (or MCP Inspector) and call `list_digests` and
   `get_digest`. Record the transcript summary. **Remove the scratch MCP
   config afterwards.**
3. All B.6 tests pass; full ruff and pytest green.
4. `docs/mcp-server.md` and the runbooks describe the built system;
   nothing claims "deployed".

### B.9 Dispatch (SendMessage to the Phase 3 Operations agent)

```
Phases 3 and 4A are merged (commits <hash>, <hash>). Continue with Phase
4B of the agent-discovery plan: run the generic static-mcp package as the
fapd-mcp container with FAPD's manifest, proxied from fapd-web at /mcp
over a new internal network, exactly as specified in section B of
docs/ops/plan-2026-09-13-phase4-mcp-service.md, meeting every acceptance
criterion in B.8. Read "Shared background" and section B in full first,
and packages/static-mcp/README.md. Verify every data field the manifest
names against the real build output before writing it. Same contract
and exit-report shape as Phase 3; no VPS actions. Start
research/agent-logs/agent-discovery-phase4b-<YYYYMMDD>.md and write its
first entry before touching any file. Phase 4C (Publication) runs at the
same time and will read your manifest to generate the Server Card —
finish and report the manifest's server block first if you can, so 4C is
not blocked.
```

---

## C — MCP publication surfaces (AD-14c)

### C.0 Outcome and the manifest dependency

The public site tells agents about the MCP service, truthfully and from a
single source. The Server Card, the AI-catalog MCP entry, the
API-catalog MCP entry and the `agents.html` MCP section are all
**generated from `deploy/vps/mcp/fapd.manifest.json`**. If the manifest
is absent, none of them is built, and the documents that reference them
don't reference them. The public claims that say "no endpoint" are
corrected.

**Dependency:** 4C reads the manifest 4B writes. If 4B hasn't produced it
yet, start from a copy of the §8.4 values in a test fixture, build
everything against the fixture, and switch the build to the real file
when 4B's manifest lands (the orchestrator relays it).

### C.1 Ownership

**May edit:** `src/fapd/publish.py`; `tests/test_agent_discovery.py`,
`tests/test_publish.py`, new `tests/test_mcp_surfaces.py`;
`docs/site/privacy.md`; `docs/accessibility-doctrine.md` (the one claim);
`docs/site/agent-skills/*/SKILL.md` (add the MCP alternative where a
skill fetches files).
**Read-only:** `deploy/vps/mcp/fapd.manifest.json` (read at build time;
never edited by 4C), `packages/static-mcp/src/static_mcp/card.py`
(imported **only in tests**, for the drift check).

### C.2 Tasks

1. **Manifest reader:** `_mcp_manifest()` reads
   `config.PROJECT_ROOT / "deploy/vps/mcp/fapd.manifest.json"`, returning
   `None` if absent. It's read-only JSON; the backend image carries the
   repo, so the file exists in production builds. Add a seam parameter so
   tests can inject a path.
2. **Server Card:** write `out_dir/mcp/server-card` (no extension) and a
   byte-identical `out_dir/.well-known/mcp/server-card.json`, using the
   same field mapping as `static_mcp.card.build_card` (A.4), implemented
   in ~20 lines in `publish.py`. **Drift test:** the published card
   equals `build_card(manifest)` (import via `sys.path` insert in the
   test only).
3. **Catalogs:** remove the `PHASE4_PENDING` mechanism. The AI-catalog
   MCP entry and the API-catalog `/mcp` entry are emitted only when the
   manifest exists.
4. **Signposts:** `out_dir/_signpost/mcp-method.json` ("This endpoint
   accepts JSON-RPC POST requests from MCP clients; see
   {base}/agents.html#mcp") and `out_dir/_signpost/mcp-unavailable.json`
   ("The MCP service is temporarily unavailable. Every file it serves is
   also published statically; start at {base}/llms.txt"). Neither states
   a cause (the r15 disclosure habit: causes go to the logs).
5. **`agents.html` `## MCP service` section**, generated from the
   manifest: endpoint URL; "read-only, no inference, no account"; the
   supported protocol versions; how to connect (Claude Code:
   `claude mcp add --transport http fapd https://fapd.info/mcp`; generic
   JSON client configuration with `"type": "http"` / `"url"`); a tools
   table (name, what it returns, parameters) generated from the manifest,
   the same rendering `static-mcp describe` uses (reimplement in
   `publish.py`, pinned by a drift test against `describe`); what it
   doesn't do (no search, no writes, no sessions, no streaming); the rate
   limit; the privacy note; a link to the server card and to
   `docs/mcp-server.md` in the repository. Replace Phase 1's one-sentence
   placeholder.
6. **`llms.txt`:** after the MCP line, add one line per tool (`name` —
   short description), generated from the manifest.
7. **Privacy page (`docs/site/privacy.md`)**, new paragraph after the
   access-log paragraph:
   > **The MCP service.** Requests to `https://fapd.info/mcp` pass
   > through the same web server logs described above. The MCP service
   > itself logs, for each request, the time, the protocol method, the
   > tool or resource name, the response status and size, the
   > processing time, and the client's self-reported software name. It
   > does not log your IP address, the arguments you sent, or the
   > content of any request or response. Logs rotate on the same
   > schedule.
   Also adjust the sentence "Nothing on this site collects, transmits, or
   retains anything you type or click" so it stays true. It's about the
   HTML pages, so say "Nothing on these pages…".
8. **Accessibility doctrine (~line 286):** name the bounded exception and
   keep the argument intact:
   *"…no form that submits, no endpoint of our own except the read-only
   MCP service at `/mcp` (GUIDE §2a rule 4, 2026-09-13), which serves
   software rather than a page and changes nothing a person reads…"*.
   Leave the rest of that paragraph's reasoning as it is.
9. **Agent skills:** in `fapd-daily-digest` and `fapd-live-day`, add a
   short "If you speak MCP" step naming the tool equivalent. Digests
   recompute automatically.
10. **Accessibility:** the `agents.html` additions are prose, a table and
    code. Use `_accessible_tables` (as the doc pages do), give the table a
    caption, and describe code blocks by the text before them. It's an
    existing page class, so no findings entry is needed, but the table
    helper test must cover it.

### C.3 Acceptance criteria (4C)

1. Card drift test and describe drift test pass.
2. With the manifest removed (test), no card, no MCP catalog entries, no
   MCP section. With it present, all of them.
3. `git grep` from Phase 0 §2.7 finds no unexplained "no endpoint" claim
   in files 4C owns.
4. Privacy page and doctrine updated as specified.
5. Ruff clean, full pytest green.

### C.4 Dispatch (SendMessage to the Phase 2 Publication agent)

```
Phases 2 and 4A are merged (commits <hash>, <hash>). Continue with Phase
4C of the agent-discovery plan: the MCP publication surfaces (server card
at /mcp/server-card and /.well-known/mcp/server-card.json, the catalog
entries, the two MCP signposts, the generated agents.html MCP section
and llms.txt tool lines, the privacy paragraph, the accessibility
doctrine sentence, and the skill updates), all generated from
deploy/vps/mcp/fapd.manifest.json, exactly as specified in section C of
docs/ops/plan-2026-09-13-phase4-mcp-service.md, meeting every acceptance
criterion in C.3. Read "Shared background" and section C in full first.
If Phase 4B's manifest is not in the tree yet, build against a fixture of
the master plan §8.4 values and say so. Same contract and exit-report
shape as before; start
research/agent-logs/agent-discovery-phase4c-<YYYYMMDD>.md before touching
any file.
```

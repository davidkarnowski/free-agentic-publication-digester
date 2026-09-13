# Phase 0 — governance and scaffolding (agent discovery)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md)
(the master plan; read it first). Task AD-1. Performed by the
**orchestrator** (main session), not a section agent, because every file
here is orchestrator-owned (`docs/agents/orchestration.md` §2) or
governs all sections. Last reviewed: 2026-09-13.*

## 0. Outcome

Before any code: the constitution says what the new surfaces are and
why they're allowed, the ownership matrix names an owner for every new
path, every public "no endpoint" claim is listed for correction, and the
logs and notes exist. GUIDE §10: *changes to GUIDE precede
implementation.*

## 1. Start

1. `git rev-parse --abbrev-ref HEAD` → `feature/agent-discovery`.
2. Create or append the orchestrator log
   `research/agent-logs/agent-discovery-orchestrator-20260913.md` (it
   already exists with a START entry from plan creation).
3. Confirm `research/Cloudflare_Access/blog-notes-agent-readiness.md`
   exists.

## 2. Tasks

### 2.1 GUIDE.md §1 — new standing commitment (dual audience)

**Why:** §1's "Standing commitments for agentic access" names the agent
surfaces. The new discovery layer, Content Signals (a new policy
statement: D1), and the MCP service belong in that list.

**Where:** GUIDE.md §1, in the "Standing commitments for agentic access"
bullet list, after "Clean, stable, machine-first surfaces" (currently
~line 67).

**Draft text (the operator approves at C-2):**

```markdown
- **Discovery through the conventions agents actually poll (amended
  2026-09-13).** Besides `llms.txt` and the access page, the site
  publishes machine discovery documents at their registered or
  specified locations: Content Signals in robots.txt (search, AI input,
  and AI training are all welcome; CC BY 4.0 attribution still
  applies), RFC 8288 `Link` headers, an RFC 9727 API catalog with an
  OpenAPI description of the static files, an AI Catalog, an Agent
  Skills index, an `auth.md` stating that no authentication exists, and
  a Markdown twin of every page with a Markdown form, served by
  `Accept: text/markdown` content negotiation. **We publish no metadata
  for a capability we do not operate:** a probe for an unoffered
  protocol (OAuth, A2A, payments) receives an honest refusal naming
  where to go instead, never a document that implies the capability
  exists.
- **A read-only MCP service, with no inference (amended 2026-09-13).**
  `https://fapd.info/mcp` answers Model Context Protocol requests using
  only the files this site already publishes. It calls no model, makes
  no outbound connection, writes nothing, keeps no session, and knows
  nothing the static site does not already say. It exists so agents
  that speak MCP reach the same record, with the same disclosures, as
  agents that read files. Its design and security posture are
  documented in `docs/mcp-server.md`; its limits are §2a's.
```

### 2.2 GUIDE.md §2a — rules 4 and 5 (the bounded exception)

**Why:** Rule 4 says the site "exposes no endpoint of its own". The MCP
service is an endpoint that reads input. Rule 5 requires any such change
to be argued to the operator as both an access change and a security
change. The operator ruled for it on 2026-09-13, so the rule text has to
say so precisely, or the constitution overclaims.

**Current rule 4 (GUIDE.md ~line 248):**
> The published site accepts no input, exposes no endpoint of its own,
> and loads no third-party asset. No login, no server-side search, no
> submitting form, no comment field, no analytics, no hosted fonts, no
> content delivery network, no embedded third-party player.

**Draft replacement:**

```markdown
- **The published site accepts no input, exposes no endpoint of its own,
  and loads no third-party asset — with one bounded exception.** No
  login, no server-side search, no submitting form, no comment field, no
  analytics, no hosted fonts, no content delivery network, no embedded
  third-party player. Choosing among static files by a request's
  `Accept` header, and adding response headers to a GET, are neither
  input nor an endpoint. **The exception (operator ruling, 2026-09-13)
  is the MCP service at `/mcp`**: it reads a JSON-RPC request and answers
  only from the published static files, mounted read-only. It calls no
  model, makes no outbound connection, writes nothing, issues no
  credential, keeps no session, and runs with no privilege. Any widening
  of that exception (a write, a search index, a model call, an outbound
  request, an account) is a new ruling under rule 5, not an
  implementation detail.
```

**Rule 5 (~line 253): append one sentence:**

```markdown
  The MCP exception was argued this way on 2026-09-13 and is recorded
  in `docs/ops/plan-2026-09-13-agent-discovery.md`. Read as access, it
  lets agents that speak MCP reach the record without writing a file
  reader. Read as security, it is a new input surface, contained by a
  read-only mount, no egress, no state, strict parameter patterns, and
  rate limits.
```

### 2.3 CLAUDE.md

1. **§9 entry "The single script and the absent endpoints…"** (~line
   215): rename to "The single script and the one bounded endpoint".
   Replace "accepts no input, exposes no endpoint of its own" with
   "accepts no input and exposes no endpoint of its own except the
   read-only, no-inference MCP service at `/mcp` (GUIDE §2a rule 4,
   2026-09-13)". Add: "Do not widen `/mcp` (writes, search, model calls,
   outbound requests, accounts) without a new §2a ruling; do not publish
   a host port for `fapd-mcp` (Docker-published ports bypass ufw)."
2. **§3 stack table:** add a row `MCP | stdlib-only static-mcp package
   (packages/static-mcp/), FAPD manifest deploy/vps/mcp/, container
   fapd-mcp behind fapd-web; dual-era MCP 2026-07-28 + 2025-11-25/2025-06-18`.
3. **§4 layout:** add a row `packages/static-mcp/ | reusable no-inference
   MCP server (generic; FAPD is one manifest)`.
4. **§12 where to look:** add rows `Agent discovery documents |
   publish._build_agent_surfaces, docs/ops/plan-2026-09-13-agent-discovery.md`
   and `MCP service | docs/mcp-server.md, packages/static-mcp/,
   deploy/vps/mcp/`.
5. **§14 decision log, append:**

```markdown
- **2026-09-13** — **Agent discovery layer and a no-inference MCP
  service** (operator; GUIDE §1 and §2a rules 4–5 amended). A Cloudflare
  agent-readiness scan (2026-09-12) scored the site 19 / Level 1: the
  project's agent surfaces (llms.txt, agents.html) were real but
  invisible to the conventions graders and agents now poll. Ruled: Content
  Signals `search=yes, ai-input=yes, ai-train=yes`; `.well-known`
  discovery adopted (superseding agent-api-design §9); RFC 8288 Link
  headers, RFC 9727 API catalog + OpenAPI, AI Catalog, Agent Skills,
  auth.md, Markdown twins with content negotiation; honest refusals for
  OAuth, A2A, WebMCP and payment protocols; and one bounded exception to
  §2a's "no endpoint" rule: `/mcp`, a dual-era MCP service reading only
  the published files read-only, no model, no egress, no state, behind
  fapd-web on a new internal network, no host port. Built as a reusable
  stdlib package (`packages/static-mcp/`) so other projects can run it
  with their own manifest. Web Bot Auth for the crawler scheduled as its
  own plan. VPS inspection the same day found the edge passes
  `/.well-known/` and upstream headers through unchanged, and found
  agents.html's "no rate limiting" was an overclaim (the edge limits per
  address) — corrected in the build.
```

### 2.4 `docs/agents/orchestration.md` §2 — ownership for new paths

| Owner | Add |
|---|---|
| Operations | `packages/static-mcp/*` (the generic MCP package, its tests and its generic Dockerfile), `deploy/vps/mcp/*`, `deploy/vps/nginx/*`, `deploy/vps/fail2ban/*`, `deploy/dev/mcp/*`, `docs/mcp-server.md`, `.claude/skills/fapd-health/*` (read-only health commands) |
| Publication | `docs/site/agent-skills/*` (the SKILL.md sources) |

Shared-resources table: no change. `pyproject.toml` stays
orchestrator-owned. Phase 4A hands its `testpaths`/ruff changes over as
diffs.

**Note for Phase 4A:** a `general-purpose` agent builds the package. For
the duration of that task its ownership is exactly
`packages/static-mcp/**`; Operations owns the package afterwards.
Mention this in the Phase 4A dispatch.

`docs/agents/operations.md` and `docs/agents/publication.md`: add the
new paths to each file's "edit surface" sentence (so
`tests/test_agents_docs.py` drift checks stay green), and in
`publication.md` change the "One script, no endpoint, no input, no
third-party asset" bullet to name the `/mcp` exception and say that
Publication never edits it.

### 2.5 `docs/agent-api-design.md` — dated supersession note

At the top of §9 and at the `.well-known` bullet in §12, insert:

```markdown
> **Superseded in part, 2026-09-13** (operator; docs/ops/plan-2026-09-13-agent-discovery.md).
> `.well-known` discovery was rejected here as "a convention nobody
> polls". A Cloudflare agent-readiness scan on 2026-09-12 probed fourteen
> `.well-known` paths on fapd.info, and the MCP and AI Catalog
> specifications now name `/.well-known/ai-catalog.json` as the
> domain-level discovery point. The site now publishes an API catalog,
> an AI Catalog and an Agent Skills index there. The rest of this
> section (versioning, stability promises) stands.
```

At §12's first bullet ("Any server-side API"), insert a similar note:
the MCP service is a bounded exception (GUIDE §2a rule 4), read-only
over the same static files, and doesn't evaluate queries against the
database.

### 2.6 Backlog and checklist (one-file rule)

- `docs/pre-publication-todo.md`, "Agent-surface optimization package":
  append *"(c) JSON Schemas: absorbed by
  docs/ops/plan-2026-09-13-agent-discovery.md Phase 1 AD-3, 2026-09-13."*
  and, under "Rejected on constitutional grounds", note that server-side
  compute now has one bounded exception (`/mcp`), which still evaluates
  no queries against the database.
- `docs/ops/ops-backlog.md` **OB-3** (Web Bot Auth): append *"Scheduled
  2026-09-13 as Phase 7 of the agent-discovery plan; trigger met: FAPD
  is a site that sends requests (Cloudflare's own guidance)."*
- `docs/pre-publication-todo.md` launch item 3 (Web Bot Auth): same
  pointer.

### 2.7 Public claims that must change before Phase 5 deploys

Each one either changes in the phase named or is deliberately left as
dated history. **Phase 5 re-runs this grep and must find nothing
unexplained.**

```sh
git grep -n -i -E "no endpoint|accepts no input|exposes no endpoint|nothing to exploit|no rate limiting|nothing an agent needs to execute" -- ':!site/' ':!digests/' ':!WORKLOG.md' ':!deploy/dev/repo/' ':!docs/ops/plan-2026-09-13-*'
```

| File (as of 2026-09-13) | Claim | Changed in | Change |
|---|---|---|---|
| `GUIDE.md` §2a rules 4–5 | "exposes no endpoint of its own" | Phase 0 | §2.2 |
| `CLAUDE.md` §9 (~215) and §14 2026-09-05 entry (~585) | same | Phase 0 | §9 per §2.3. **The §14 entry is dated history: leave it.** |
| `docs/accessibility-doctrine.md` (~286) | "no endpoint of our own" | Phase 4C (Publication owns the file) | name the `/mcp` exception, keep the argument |
| `docs/agents/publication.md` (~70) | "One script, no endpoint…" | Phase 0 | §2.4 |
| `src/fapd/publish.py` `_AGENTS_MD` "Courtesy" (~4593) | "no auth, no rate limiting, and nothing an agent needs to execute" | Phase 1 AD-8 | "no authentication; a generous per-address rate limit protects the shared server; nothing an agent needs to execute" |
| `docs/site/privacy.md` | "Nothing on this site collects, transmits, or retains anything you type or click." / logs paragraph | Phase 4C | add what `/mcp` logs (method, tool name, status, timing; never request bodies or arguments) |
| `docs/devnotes/2026-09-05-built-to-be-reachable.md` | "The site accepts no input…" | **not changed** | a dated, published post; the new post (blog notes) explains the change |

## 3. Scaffolding the orchestrator creates now

- `research/agent-logs/` (gitignored). Agents create their own files in it.
- `research/Cloudflare_Access/blog-notes-agent-readiness.md` (gitignored)
  with one heading per phase.
- `docs/mcp-server.md`, the MCP guide (design of record, "not yet built"
  banner). Phases 4A–4C turn it into the as-built guide.

## 4. Verification

```sh
uv run ruff check .
uv run pytest -q tests/test_agents_docs.py   # ownership/router drift
uv run pytest -q                              # full suite still green
git diff --stat                               # only governance files touched
```

Read-through: every new sentence in GUIDE/CLAUDE.md describes what the
plan builds, no more. Nothing in them is true only after later phases
without saying so ("amended 2026-09-13" plus the plan pointer is
enough, because the whole branch merges together).

## 5. Commit and checkpoint

1. Show the operator the GUIDE and CLAUDE.md diff (**C-2**). Wait for
   approval.
2. Commit (orchestrator), subject: `docs: agents get discovery documents
   and one bounded MCP endpoint (GUIDE §1, §2a)`. Narrative body: the
   scan, the rulings, the VPS finding, the reuse goal. One
   `Co-Authored-By:` trailer, nothing else.
3. WORKLOG entry. Status table in the master plan → Phase 0 "done", with
   the commit hash, in the same commit or the immediately following
   bookkeeping commit.

## 6. Rollback

`git revert <commit>`. Nothing outside the repo has changed at this
point.

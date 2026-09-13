# Plan — agent discovery and a no-inference MCP service (2026-09-13)

*Master plan. Status: **approved in principle by the operator
2026-09-13; nothing built.** Branch: `feature/agent-discovery`. The
per-phase files listed in §6 carry the executable detail; this file
carries the why, the rulings, the contracts that let phases run in
parallel, the working protocol every agent follows, and the status table.
Shape follows [plan-task-template.md](plan-task-template.md). Last
reviewed: 2026-09-13.*

> **Any agent picking this up:** read this whole file, then your phase
> file, then your section file (`docs/agents/<section>.md`), then start
> your progress log (§7) **before touching any file**. If something
> here disagrees with GUIDE.md, GUIDE.md wins and this plan has a bug —
> stop and report it.

---

## 1. Why this exists (plain language)

On 2026-09-12 the operator scanned fapd.info with Cloudflare's URL
Scanner, which now grades "agent readiness". FAPD scored **19, Level 1
("Basic Web Presence")**: 3 of 16 scored checks passed. That is an odd
result for a project whose second readership is AI agents (GUIDE §1).
The reason is not that FAPD is hard for agents to use. It's that FAPD
advertises itself through `llms.txt` and `agents.html`, which the grader
doesn't score by default. Meanwhile it has none of the newer
machine-discovery conventions the grader does look for: RFC 8288 `Link`
headers, an RFC 9727 API catalog, an AI Catalog, an Agent Skills index,
Markdown content negotiation, Content Signals, and an MCP server.

This plan adds every one of those that FAPD can publish **truthfully**,
declines the ones it cannot (with the reasons published), and, by
operator ruling, adds a **hosted MCP (Model Context Protocol) service
that performs no inference**. It answers only from the static files the
site already publishes, so agents that speak MCP can use FAPD directly.
The MCP server is built as a **reusable, manifest-driven component**
(`packages/static-mcp/`), so the operator's other projects can run the
same build with a different manifest.

Source material (the scan itself lives in the operator's gitignored
research tree): Cloudflare Radar scan `29b9a1e9-2be1-430a-aad4-753385c42297`
(2026-09-12 14:40 UTC); Cloudflare's methodology post
<https://blog.cloudflare.com/agent-readiness/>; the scanner's per-check
instructions at `https://isitagentready.com/.well-known/agent-skills/<check>/SKILL.md`.

## 2. The scan, check by check, and what this plan does

| # | Check | Scan result | Disposition | Task ID |
|---|---|---|---|---|
| 1 | robots.txt | pass | keep; add pointers | AD-2 |
| 2 | sitemap | pass | keep | — |
| 3 | Link headers (RFC 8288) | fail | **build** | AD-7 (in-document), AD-11 (headers) |
| 4 | DNS-AID | fail | **build if the DNS panel supports it** | AD-13 |
| 5 | Markdown negotiation | fail | **build** | AD-9, AD-10, AD-11 |
| 6 | AI crawler rules | pass | keep (`*` covers all) | — |
| 7 | Content Signals | fail | **build** (`search=yes, ai-input=yes, ai-train=yes`) | AD-2 |
| — | Web Bot Auth | neutral | **build for our crawler, own plan** | AD-15 |
| 8 | API Catalog (RFC 9727) | fail | **build** | AD-3, AD-4 |
| 9 | OAuth/OIDC discovery | fail | **decline**: no auth server exists | AD-8 (recorded) |
| 10 | OAuth Protected Resource | fail | **decline**: nothing is protected | AD-8 (recorded) |
| 11 | auth.md | fail | **build** ("no authentication") | AD-5 |
| 12 | MCP Server Card | fail | **build**: real remote endpoint, operator ruling | AD-14 (4A/4B/4C) |
| 13 | A2A Agent Card | fail | **decline**: FAPD is not a task-taking agent | AD-8 (recorded) |
| 14 | Agent Skills index | fail | **build** | AD-6 |
| 15 | WebMCP | fail | **decline**: needs a second script (GUIDE §2a r3) | AD-8 (recorded) |
| 16 | ARD / AI Catalog | fail | **build** | AD-7 |
| — | x402, MPP, UCP, ACP, AP2 | neutral | not applicable (free site) | AD-8 (recorded) |

If every "build" lands and re-scans clean, 12 of 16 scored checks are
addressed; 4 stay declined by design. **No score is promised.** Cloudflare
doesn't publish its weights, so Phase 5 re-scans and records what
actually happened.

## 3. Rulings of record (operator, 2026-09-13)

| ID | Question | Ruling |
|---|---|---|
| D1 | Content Signals values | `search=yes, ai-input=yes, ai-train=yes` in the `User-agent: *` group. New policy statement: recorded in GUIDE §1 and `docs/site/privacy.md`. CC BY 4.0 attribution still applies. |
| D2 | MCP | **A containerized, no-inference MCP service in the Docker stack** (the original plan's option "b"), plus signposted refusals for every protocol we don't offer (option "d"). Built as a reusable component. |
| D3 | `.well-known` discovery | Adopt. Supersedes `docs/agent-api-design.md` §9 and the `.well-known` bullet in §12, via a dated note. |
| D4 | Web Bot Auth | Schedule after Phases 1–3, as its own plan (Phase 7 stub). |
| D5 | DNS | Turn on DNSSEC if the Hostinger panel supports it for `.info`. Publish DNS-AID only after reading the current draft and confirming SVCB support. Don't move DNS providers. |
| D6 | CORS | `Access-Control-Allow-Origin: *` on the public machine-readable files. Not on `/mcp` in v1. |
| D7 | WebMCP | Decline. |
| D8 | Schema validation in tests | A small stdlib validator in tests, no new dependency. |
| D9 | Branch | `feature/agent-discovery`. |
| D10 | Firewall | The operator's secondary edge firewall (Hostinger hPanel) is coordinated at checkpoint **C-1**. Finding (§4): **no new port is needed**, and the plan recommends not opening one. |
| D11 | Documentation | Every agent keeps a progress log and the orchestrator writes WORKLOG entries (§7). Blog notes kept throughout (§7.5). A repo MCP guide lives at `docs/mcp-server.md`. |
| D12 | Reuse | The MCP server is a generic package with a declarative manifest; FAPD is one manifest. No FAPD import, name, or path inside the package. |
| D13 | Input validation (operator, 2026-09-13 second pass) | A named, ordered **validation layer** in the package (`validate.py`, eight stages, adversarial corpus and fuzz tests) plus an nginx transport gate; normative text in [plan-2026-09-13-security-review.md §3](plan-2026-09-13-security-review.md). No interpreter or network-client path in the package, pinned by source-scan tests. |
| D14 | Fail2ban (operator, 2026-09-13 second pass) | Yes: one `fapd-mcp` jail reading fapd-web's own `/mcp` access log (true client address first), banning in `DOCKER-USER` like the box's existing nginx jails, generous thresholds (20 rejected requests / 10 min), nginx limits as the primary control. Files in Phase 4B, installed by a staged script at checkpoint C-6. Review §4. |

GUIDE amendments these rulings require are drafted in Phase 0. The
operator reads the exact amendment text before it is committed
(checkpoint C-2).

## 4. What was verified on the VPS (read-only, 2026-09-13)

Public-safe conclusions only. Box specifics are in the operator's
private tree (`docs/private/agent-discovery-box-facts-2026-09-13.md`).

| Question | Finding | Consequence |
|---|---|---|
| Does `https://fapd.info/.well-known/*` reach `fapd-web`? | Yes. The edge proxy passes every HTTPS path to `fapd-web`; the ACME webroot is only on port 80. | Discovery files published in `site/.well-known/` are reachable. No edge change needed. |
| Does the edge strip or replace upstream headers or 404 bodies? | No. No header hiding, no 404 interception for fapd.info. The edge adds HSTS, nosniff, frame-options and referrer-policy itself. | `Link`, `Vary`, CORS and content types set in `fapd-web` reach clients. Signposted 404 bodies survive. |
| Who serves the stock 404 page? | `fapd-web` (it shows its nginx version; the edge hides its own). | Phase 3 sets `server_tokens off` in `fapd-web`. |
| What config does `fapd-web` run? | The image's stock `default.conf`. Nothing repo-managed. | Phase 3 adds `deploy/vps/nginx/fapd-web.conf`. |
| Compression? | The edge gzips HTML, JSON, plain text, CSS, JS and SVG. It doesn't gzip Markdown, linkset, AI-catalog, Atom or XML types. | Phase 3 enables gzip for those types inside `fapd-web` (in-repo). |
| Rate limiting? | The edge applies a per-client-address request limit to all of fapd.info. | `/mcp` is already covered; Phase 4B adds a tighter MCP zone. **`agents.html` currently says "no rate limiting", which is an overclaim.** AD-8 fixes the sentence. |
| Open host ports | `ufw`: exactly 2222, 80, 443 (matches SERVER-GUIDE). | MCP rides existing 443 through the edge proxy. **No port opens.** |
| Could the MCP container be published on a port instead? | Technically, but Docker-published ports bypass `ufw` (Docker's iptables rules sit ahead of ufw's). It would also skip TLS, the edge rate limit and the security headers. | **Rejected.** `fapd-mcp` publishes no port and joins only a new internal network shared with `fapd-web`. |
| Edge startup dependency | The edge names `fapd-web` as a static upstream. If `fapd-web` is missing at edge start, the edge fails, including the cohabitant's site. | Never rename or remove `fapd-web`. `fapd-web` reaches `fapd-mcp` through a variable upstream, so a missing `fapd-mcp` can't stop `fapd-web` from starting. |

## 5. Architecture after this plan

```
Internet ──443──▶ spiralyst-proxy (edge; TLS, HSTS, per-IP limit)   [unchanged]
                     │  fapd_edge (internal network)                [unchanged]
                     ▼
                  fapd-web (nginx; static files from fapd-site:ro)  [new repo-managed config]
                     │   • /.well-known/*, /openapi.json, /auth.md, *.md twins   (Phases 1–2)
                     │   • Link / Vary / CORS / content types / signposts        (Phase 3)
                     │   • location = /mcp  ──proxy──┐                           (Phase 4B)
                     │  fapd_mcp (NEW internal network)
                     ▼                               │
                  fapd-mcp (python stdlib; static-mcp package + FAPD manifest)   (Phase 4A/4B)
                     • reads fapd-site volume READ-ONLY
                     • no inference, no egress, no writes, no sessions, no accounts
                     • non-root, read-only root filesystem, capabilities dropped

fapd-backend (unchanged) ── writes fapd-site volume (now also .well-known/, *.md, mcp/server-card)
```

Invariants this architecture must keep, each pinned by a test or a
Phase 5 check:

1. `fapd-web` and `fapd-mcp` have **zero egress**. Both networks they
   join are `internal`.
2. `fapd-mcp` is reachable **only** from `fapd-web`, not from the edge
   proxy, the backend, or the internet.
3. No container publishes a new port.
4. `fapd-mcp` mounts the site volume **read-only** and has no other
   volume.
5. The MCP service reads only files under the site root, with paths
   built from validated parameters. It never calls a model or any
   network service.
6. The site is still complete from a filesystem clone. Headers and
   `/mcp` add convenience; they are never the only way to reach content.
7. Every `/mcp` request passes the eight-stage validation layer before
   any handler runs (security review §3); the package contains no
   interpreter or network-client code path (pinned).
8. Abuse controls are layered: edge per-address limit → `fapd-web`
   `limit_req`/`limit_conn` → service concurrency cap → fail2ban jail on
   repeated rejections. None of them logs a request body.

## 6. Phases

| Phase | Plan file | Task IDs | Performed by | Depends on | Can run in parallel with |
|---|---|---|---|---|---|
| **0 — Governance and scaffolding** | [phase0-governance](plan-2026-09-13-phase0-governance.md) | AD-1 | Orchestrator (main session); operator approves text at C-2 | rulings §3 | — |
| **1 — Discovery documents** | [phase1-discovery-documents](plan-2026-09-13-phase1-discovery-documents.md) | AD-2 … AD-8 | `fapd-publication` agent | Phase 0 merged | Phase 3, Phase 4A |
| **2 — Markdown twins** | [phase2-markdown-twins](plan-2026-09-13-phase2-markdown-twins.md) | AD-9, AD-10 | `fapd-publication` agent (same agent, continued) | Phase 1 merged | Phase 3, Phase 4A |
| **3 — fapd-web configuration** | [phase3-web-config](plan-2026-09-13-phase3-web-config.md) | AD-11 | `fapd-operations` agent | Phase 0 merged; the §8 contracts | Phases 1, 2, 4A |
| **4A — Generic static-mcp package** | [phase4-mcp-service](plan-2026-09-13-phase4-mcp-service.md) §A | AD-14a | `general-purpose` agent, ownership limited to `packages/static-mcp/` | Phase 0 merged | Phases 1, 2, 3 |
| **4B — FAPD MCP service integration** | same file §B | AD-14b | `fapd-operations` agent (continued from Phase 3) | Phases 3 and 4A merged | Phase 4C |
| **4C — MCP publication surfaces** | same file §C | AD-14c | `fapd-publication` agent (continued) | Phases 2 and 4A merged | Phase 4B |
| **5 — Deploy, firewall coordination, verification, registry** | [phase5-deploy-verify](plan-2026-09-13-phase5-deploy-verify.md) | AD-12 | Orchestrator + **operator** (C-1, C-3, C-4) | Phases 1–4 merged to the branch, CI green | — |
| **6 — DNS** | [phase6-dns](plan-2026-09-13-phase6-dns.md) | AD-13 | **Operator** (Hostinger panel) + orchestrator verification | Phase 5 done | Phase 7 planning |
| **7 — Web Bot Auth for the crawler** | [phase7-web-bot-auth](plan-2026-09-13-phase7-web-bot-auth.md) (scope stub; becomes its own plan) | AD-15 | `fapd-acquisition` + `fapd-operations`, later | Phase 5 done; GUIDE §4 amendment | Phase 6 |

```
Phase 0 ─┬─▶ Phase 1 ──▶ Phase 2 ──┬──────────────▶ Phase 4C ─┐
         ├─▶ Phase 3 ──────────────┼─▶ Phase 4B ──────────────┼─▶ Phase 5 ─▶ Phase 6
         └─▶ Phase 4A ─────────────┴──────────────────────────┘        └─▶ Phase 7 (own plan)
```

**Why these boundaries.** Each phase's files belong to exactly one
section owner (`docs/agents/orchestration.md` §2), so phases that run at
the same time can't edit the same file. Phase 3 and Phase 4B both edit
`deploy/vps/nginx/fapd-web.conf` and the compose files, which is why 4B
waits for 3 and reuses the same Operations agent. Phases 1, 2 and 4C all
edit `publish.py`, which is why they're serial in one Publication agent.

## 7. Working protocol for every agent (binding)

### 7.1 Before touching any file

1. `git rev-parse --abbrev-ref HEAD` must print `feature/agent-discovery`.
   If it doesn't, stop and report. Never work on `main`.
2. Read, in order: this file → your phase file → `docs/agents/<section>.md`
   in full → `docs/code-standards.md` → for any HTML change,
   `docs/accessibility-doctrine.md`.
3. **Create your progress log** (§7.2) and write its first entry.
4. Do **not** launch with `isolation: "worktree"`. The progress logs live
   in the gitignored `research/agent-logs/`, which doesn't exist inside a
   worktree. Parallel agents are safe in the shared tree because their
   files don't overlap (§6).

### 7.2 Progress log (append-only, on disk, survives a cut-off session)

Path: `research/agent-logs/agent-discovery-<phase>-<YYYYMMDD>.md`
(e.g. `agent-discovery-phase1-20260914.md`). Timestamps in UTC,
`YYYY-MM-DD HH:MM`.

First entry, **before any code**:

```markdown
# Progress log — agent discovery, Phase <N> (<short name>)

## <timestamp> — START
**Brief:** <one self-contained paragraph: the outcome wanted, the plan
file, the branch, the constraints that bind this phase>
**Owned files (may edit):** <exact list from the phase file>
**Read-only / diff-in-exit-report only:** <shared files this phase needs changed>
**NEXT:** <the first concrete step>
```

Then one entry at **every milestone**: a decision and its reason, a file
finished, a test added, a test run (with numbers), a blocker. Each entry
ends with an updated `**NEXT:**` line. Keep the latest `NEXT:` accurate:
it's how a resuming agent knows where to start.

Things worth a blog paragraph go on their own line, prefixed
`**BLOG:**`: a surprise, a number, a design reason a new developer would
need explained (§7.5).

**Resuming after a cut-off:** read your log → `git diff --stat` →
`git status --short` → continue from the last `NEXT:`. Write a
`## <timestamp> — RESUMED` entry first.

### 7.3 Contract (from `docs/agents/orchestration.md` §3, restated)

1. Edit only the files your phase file lists as owned. Shared or foreign
   files: put the exact diff in your exit report.
2. **Stage nothing, commit nothing.** Only the orchestrator commits.
3. Before reporting, run `uv run ruff check .` and `uv run pytest -q`
   (plus the package's own tests in Phase 4A). Report the real numbers,
   failures included.
4. New behavior gets a test that fails without the change.
5. **No VPS actions of any kind.** Box facts you need are in §4 of this
   file. If you need more, ask the orchestrator.
6. If blocked, exit and report the blocker. Don't improvise around it.
7. Operator word rule: pytest's attribute-swapping fixture is named
   after a primate. That name may appear **only** where the code
   requires it as an identifier (the fixture parameter itself), never in
   prose, comments, docstrings, log entries or test data. Say "replace",
   "substitute" or "patch" instead.

### 7.4 Exit report (required shape)

- Files modified (list)
- Shared-file diffs needed (exact diffs, or "none")
- Verification: ruff + pytest tails, plus the manual checks the phase
  file lists
- Acceptance criteria: each one from the phase file, marked met or not
  met, with evidence
- Deviations from the phase file, with reasons
- What a human should look at before this merges
- Path of your progress log, and the `BLOG:` lines copied out

### 7.5 Orchestrator duties at each integration

1. Review the diff against the phase file's acceptance criteria.
2. Apply shared-file diffs yourself. Re-run `uv run ruff check .` and
   `uv run pytest -q`.
3. **Append a `WORKLOG.md` entry** (timestamped, append-only, never
   edited later): what landed, the evidence, deviations, the path of the
   agent's progress log.
4. Update the status table in §10 **in the same commit** as the work it
   describes (CLAUDE.md §8).
5. Copy the agent's `BLOG:` lines into
   `research/Cloudflare_Access/blog-notes-agent-readiness.md` under the
   matching phase heading, with a line of your own on what they mean.
6. Commit on `feature/agent-discovery` with a narrative body: the why,
   the tradeoffs, what was verified. Subject form `area: plain-English
   subject`. **Trailer: exactly one line,
   `Co-Authored-By: Claude <model> <noreply@anthropic.com>`. No session
   URL, run id, or conversation link.** Never mix evidence paths
   (`digests/`, `provenance/`, `site/`, `SOURCES.md`) with code. A local
   `site/` rebuild used for verification is **not** committed. Restore
   it with `git checkout -- site/` before committing, or leave it
   unstaged.
7. Send follow-up feedback to the **same** agent via SendMessage; don't
   spawn a fresh one.
8. Append to the orchestrator log
   `research/agent-logs/agent-discovery-orchestrator-20260913.md`.

### 7.6 Dispatch prompt

Every phase file ends with a filled-in copy of the
`docs/agents/orchestration.md` §3 template. Launch with that text
verbatim, adding this line to CONTEXT: *"Keep the progress log required
by docs/ops/plan-2026-09-13-agent-discovery.md §7.2; write its first
entry before touching any file."*

## 8. Interface contracts between phases (parallel phases build to these)

Changing a contract means changing this section first, in a commit of
its own, and telling every agent currently working.

### 8.1 Published paths and content types

| Path (site root = `site/`) | Built by | Content type served (Phase 3) | CORS `*` |
|---|---|---|---|
| `/robots.txt` | P1 AD-2 | `text/plain; charset=utf-8` | yes |
| `/openapi.json` | P1 AD-3 | `application/json` | yes |
| `/schema/digests.schema.json`, `today.schema.json`, `day.schema.json`, `sources.schema.json` | P1 AD-3 | `application/json` | yes |
| `/.well-known/api-catalog` (no extension) | P1 AD-4 | `application/linkset+json` | yes |
| `/auth.md` | P1 AD-5 | `text/markdown; charset=utf-8` | yes |
| `/.well-known/agent-skills/index.json` | P1 AD-6 | `application/json` | yes |
| `/.well-known/agent-skills/<name>/SKILL.md` | P1 AD-6 | `text/markdown; charset=utf-8` | yes |
| `/.well-known/ai-catalog.json` | P1 AD-7 | `application/ai-catalog+json` (fall back to `application/json` only if the Phase 5 re-scan rejects it) | yes |
| `/favicon.ico` | P1 AD-8 | `image/x-icon` | no |
| `/_signpost/not-offered.json` | P1 AD-8 | `application/json` (internal only; body of refusals) | yes |
| `/_signpost/mcp-method.json` | P4C | `application/json` (internal only; body of `GET /mcp` 405) | yes |
| `/_signpost/mcp-unavailable.json` | P4C | `application/json` (internal only; body of 502/503/504 on `/mcp`) | yes |
| `/<name>.md` for root pages, `/sources/<id>.md`, `/archive/<YYYY>.md` | P2 | `text/markdown; charset=utf-8` | yes |
| `/mcp` (POST) | P4B proxy → P4A server | `application/json` | no (D6) |
| `/mcp/server-card` (no extension, GET) | P4C | `application/mcp-server-card+json` | yes |
| `/.well-known/mcp/server-card.json` | P4C (byte-identical copy of `/mcp/server-card`) | `application/json` | yes |
| `/.well-known/mcp-registry-auth` | P5 (operator supplies the public key line) | `text/plain` | no |

### 8.2 Markdown negotiation eligibility (P2 builds; P3 routes)

A request is negotiated to Markdown when its `Accept` header contains
`text/markdown` **and** its path matches a row below. Phase 2 guarantees
**every** eligible path has a twin (pinned by a test), so a negotiated
request can never 404.

| Request path | Twin | Notes |
|---|---|---|
| `/` or `/index.html` | `/index.md` | |
| `/<name>.html` at the root, `<name>` matching `[A-Za-z0-9._-]+`, **except** `today`, `50x` | `/<name>.md` | digests (byte-identical to `digests/<date>.md`), doc pages, blog posts, `agents`, `sources`, `archive`, `readme`, `about`… |
| `/sources/<id>.html` | `/sources/<id>.md` | |
| `/archive/<YYYY>.html` | `/archive/<YYYY>.md` | |
| everything else (`/today.html`, `/day/*.html`, assets) | none | served as today; `Vary: Accept` still sent on HTML |

### 8.3 Discovery relations (P1 head links ≡ P3 `Link` header)

The `Link` header on every HTML response (Phase 3) and the `<link>`
elements in every page head (Phase 1) carry the same relations:

```
</.well-known/api-catalog>; rel="api-catalog"
</openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json"
</agents.html>; rel="service-doc"; type="text/html"
</llms.txt>; rel="describedby"; type="text/plain"
</.well-known/ai-catalog.json>; rel="ai-catalog"; type="application/ai-catalog+json"
```

Each page head additionally carries
`<link rel="alternate" type="text/markdown" href="<twin>">` when a twin
exists (Phase 2). In HTML the hrefs are relative (so a filesystem clone
works) and rebased for subdirectory pages by `_rebase_page`.

### 8.4 FAPD MCP identity (P4B manifest is the single source of truth)

`deploy/vps/mcp/fapd.manifest.json` → `server` block:

| Field | Value |
|---|---|
| `name` | `info.fapd/fapd` (reverse-DNS of fapd.info; MCP Registry domain namespace) |
| `title` | `Free Agentic Publication Digester` |
| `version` | semver of the FAPD MCP surface, starting `1.0.0` |
| `description` (≤100 chars) | `Cited daily digests of official US federal publications. Read-only; no inference.` |
| `websiteUrl` | `https://fapd.info/agents.html` |
| endpoint | `https://fapd.info/mcp`, transport `streamable-http` |
| supported protocol versions | modern `2026-07-28`; legacy `2025-11-25`, `2025-06-18` |

Phase 4C's server card and AI-catalog entry are **generated from this
file**. A drift test fails if they differ.

## 9. Coordination checkpoints (the operator acts; agents wait)

| ID | When | What the operator does | What the orchestrator does |
|---|---|---|---|
| **C-1 Firewall** | Before the Phase 5 deploy | In Hostinger hPanel → VPS → Firewall: confirm the rules allow inbound **443/tcp** (and 80/tcp for ACME) and **make no change**. Confirm no rule was ever added for the MCP port (there's no MCP port). If the operator wants `/mcp` restricted further, that is a new decision. | Before the deploy: record the operator's confirmation in WORKLOG. After the deploy: prove from outside that only 443 serves MCP (Phase 5 §5). |
| **C-2 GUIDE text** | End of Phase 0 | Reads the exact amendment diff (GUIDE §1, §2a rules 4–5, CLAUDE.md §9/§14) and says "approved" or edits it. | Doesn't commit GUIDE/CLAUDE.md changes before this. |
| **C-3 Deploy go** | Phase 5 | Says "deploy" in the session (the VPS authorization gate, AGENT-VPS-SERVICING-GUIDE §4). | Runs `deploy/vps/scripts/deploy.sh`, and nothing else on the box without it. |
| **C-4 MCP Registry publish** | Phase 5, after the live endpoint verifies | Generates the registry key pair locally (private key stays with the operator, logged in `docs/private/SECRETS-LOG.md`), gives the orchestrator the **public** proof line for `/.well-known/mcp-registry-auth`, then runs `mcp-publisher login http` / `publish`. | Builds and deploys the proof file; verifies the listing. |
| **C-5 DNS** | Phase 6 | Hostinger DNS panel: DNSSEC, DNS-AID records. | Verifies with `dig` / DoH. |
| **C-6 Fail2ban jail** | Phase 5, after `/mcp` verifies | Runs the staged install script for the `fapd-mcp` jail (host fail2ban config is shared with the cohabitant, so only the operator writes to it). Applies the AD-16 repair for the three pre-existing nginx jails in the spiralyst-site tree (Phase 5 §3.1; operator direction 2026-09-13). | Diagnoses AD-16 read-only first and hands over the exact diff; verifies both jails' chains exist after start; never trips a ban from the operator's own address. |

## 10. Status table (update in the same commit as the work)

| Phase | Status | Commit(s) | Agent log | WORKLOG entry |
|---|---|---|---|---|
| 0 | **done 2026-09-13** (C-2 approved) | 778e253 (plan), 4c888ab (security review), 07b6db4 (governance) | `research/agent-logs/agent-discovery-orchestrator-20260913.md` | 2026-09-13 |
| 1 | in progress (agent launched 2026-09-13) | — | `research/agent-logs/agent-discovery-phase1-20260913.md` | — |
| 2 | not started | — | — | — |
| 3 | in progress (agent launched 2026-09-13) | — | `research/agent-logs/agent-discovery-phase3-20260913.md` | — |
| 4A | in progress (agent launched 2026-09-13) | — | `research/agent-logs/agent-discovery-phase4a-20260913.md` | — |
| 4B | not started | — | — | — |
| 4C | not started | — | — | — |
| 5 | not started | — | — | — |
| 6 | not started | — | — | — |
| 7 | scoped only | — | — | — |

## 11. Definition of done (whole plan)

1. Every "build" row in §2 is live on `https://fapd.info` and passes the
   Phase 5 curl matrix. The Cloudflare re-scan JSON is stored and its
   per-check results are recorded in WORKLOG, including any that still
   fail and why.
2. `https://fapd.info/mcp` answers a modern `server/discover` and a
   legacy `initialize` correctly, and serves the tools in
   `docs/mcp-server.md` to at least two real clients (Claude Code plus
   one other), recorded with dates.
3. No new host port is open (external check recorded). Both new
   internal networks verified `internal: true`. `fapd-mcp` runs non-root
   with a read-only root filesystem and no egress.
4. GUIDE §1 and §2a amended. CLAUDE.md §9/§14, `docs/agents/orchestration.md`
   ownership, SERVER-GUIDE, OPS-GUIDE, AGENT-CVE-GUIDE, `docs/site/privacy.md`,
   `agents.html` and `llms.txt` all describe the system as built, with no
   leftover "no endpoint" claims.
5. `packages/static-mcp/` has its own README with a reuse guide, its own
   tests, and no FAPD-specific strings (pinned by a test).
6. Full `ruff` and `pytest` green; CI green on the branch; fast-forward
   merge to `main` per CLAUDE.md §8.
7. Blog notes file complete enough to draft the post. The draft goes to
   `docs/devnotes/` under the devnotes conventions.

## 12. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A bad `fapd-web` config takes fapd.info down; if `fapd-web` fails to start, the edge proxy's static upstream could also affect the cohabitant's site on the edge's next restart | medium | Rehearse `nginx -t` in the dev stack and in a throwaway container before deploy. Variable upstream for `/mcp`. Keep the rollback copy of the stock config. Phase 5 runs the health pass at deploy and again 5 minutes later. |
| MCP clients in the field speak a mix of protocol eras | high | The server is dual-era (modern stateless 2026-07-28 plus legacy 2025-11-25/2025-06-18 without sessions). Test with real clients. |
| The MCP endpoint becomes an abuse target | medium | Edge per-IP limit, plus a tighter `fapd-web` zone, 64 KiB body cap, concurrency cap, strict parameter patterns, no writes, no egress, read-only mount. Logs carry no request bodies. |
| Honesty drift: public docs still say "no endpoint" | medium | Phase 0 lists every such claim (§ phase0 table). A grep in the Phase 5 verification must find none left. |
| Spec churn (MCP, AI Catalog, Agent Skills, DNS-AID are young) | high | Pin spec revisions in the phase files. Re-scan after deploy. Every discovery document is regenerated by code, so a fix is one change. |
| Scanner rejects a truthful document (auth.md "no authentication"; AI-catalog media type) | medium | Keep the truthful document. Record the result. Change the media type only if the spec permits the alternative. |
| Fail2ban bans a shared-egress address and blocks many legitimate agents for one abuser | medium | High threshold (20/10 min), 1 h ban, nginx limits do the everyday work; runbook unban command; a reader's report is a defect report. |
| Host log directory erased by the bundle rsync `--delete` (F-004 class) | high without the fix | `logs/` excluded in `deploy.sh`, pinned by a test (SR-3). |
| Our fail2ban jail starts without a packet-filter chain, like three existing jails on the box | medium | Chain existence verified after start (Phase 5 §5.5), never assumed. |

## 13. Change log of this plan

- 2026-09-13 (second pass): security review added
  ([plan-2026-09-13-security-review.md](plan-2026-09-13-security-review.md))
  at the operator's request; rulings D13 (validation layer) and D14
  (fail2ban jail) recorded; findings SR-1…SR-16 applied to Phases 3, 4A,
  4B, 4C and 5; checkpoint C-6 added; a pre-existing cohabitant-owned
  fail2ban finding raised (Phase 5 §3.1).
- 2026-09-13: created from the research draft
  `research/Cloudflare_Access/agent-readiness-plan-2026-09-13.md`
  (operator-private) after the operator's rulings and a read-only VPS
  inspection.

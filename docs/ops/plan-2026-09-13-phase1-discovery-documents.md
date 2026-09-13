# Phase 1 — discovery documents (agent discovery)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md)
(the master plan; read it first, especially §7 working protocol and §8
contracts). Tasks AD-2 … AD-8. Performed by the **`fapd-publication`**
agent. Depends on Phase 0 merged. Runs in parallel with Phase 3 and
Phase 4A. Last reviewed: 2026-09-13.*

## 0. Outcome

A site build (`uv run python scripts/build_site.py`, or
`publish.build_site(...)` in tests) writes, deterministically and with
zero LLM calls, every discovery document in master plan §8.1 that is
marked "P1". Every HTML page's head carries the §8.3 relations.
`agents.html` and `llms.txt` describe the new layer and the protocols we
decline. The "no rate limiting" overclaim is corrected. All of it is
pinned by tests.

**These documents are static files.** They're correct and useful before
Phase 3 adds headers: a file-reading agent or a filesystem clone can
already use them. Phase 3 only adds content types, CORS and the `Link`
header.

## 1. Ownership for this phase

**May edit:**
- `src/fapd/publish.py`
- `tests/test_publish.py`, plus new test modules
  `tests/test_agent_discovery.py` and `tests/schema_subset.py` (a test
  helper, not a test module; name it without the `test_` prefix)
- `docs/site/agent-skills/<name>/SKILL.md` (new; four files)

**Read-only (diffs go in the exit report):** `src/fapd/config.py`,
`GUIDE.md`, `CLAUDE.md`, `tests/conftest.py`, `pyproject.toml`, anything
under `deploy/`.

**Must not touch:** committed `site/` output. Build into `tmp_path` in
tests. If you rebuild `site/` locally to look at it, restore it with
`git checkout -- site/` before reporting.

## 2. Background you need (read the code at these anchors)

- `src/fapd/publish.py`
  - `_PAGE` (~line 39): the one HTML shell. Its `<head>` already has
    `<link rel="alternate" type="text/plain" href="llms.txt">`.
  - `_render_page()` (~1473) and `_rebase_page()` (~1505): subdirectory
    pages (`sources/`, `day/`, `archive/`) are rendered like root pages,
    then every relative `href|src|action` gets `../`. A relative
    `.well-known/...` href is rebased correctly, because the regex skips
    only schemes, `//`, `/`, `#` and `../`.
  - `_AGENTS_MD` (~4530): Markdown source of `agents.html`.
  - `_build_agent_surfaces()` (~4679): builds `agents.html`, `llms.txt`,
    `digests.json`, `sources.json`, `feed.xml`, `robots.txt`,
    `sitemap.xml`. **All new documents are built from here or from
    helpers it calls.** It receives `base` (= `config.SITE_BASE_URL`, e.g.
    `https://fapd.info`, empty in most tests).
  - `build_today()` (~4083 → payload ~4457): the exact keys of
    `today.json` and `day/<date>.json` (`date, generated, disclosure,
    canonical_record, labels, counts, day_context, backfill_count,
    corroborated_count, backfill_note, facets, pending_llm,
    last_observed_at, items[]`, plus `frozen`, `reconstructed_on` on day
    files). Item rows come from `status["items"]` plus `opening_verbatim,
    official_url, channel_label, tags, claimed_day, is_backfill`, and
    `corroborated_by` / `duplicate_of` where present.
  - `_sources_json()` (~4615): keys of `sources.json`.
- `docs/site/*.md` are rendered as pages by `_doc_sources()` using a
  **non-recursive** `glob("*.md")`. SKILL.md files in
  `docs/site/agent-skills/<name>/` are therefore **not** rendered as doc
  pages (verified 2026-09-13). Keep it that way.
- Tests: `tests/test_publish.py` fixture `digests` (~57) writes two
  digests (`2026-07-01`, `2026-07-02`); `test_agent_surfaces_built`
  (~1065) and `test_agent_surfaces_are_bot_friendly` (~1292) are the
  existing pins. Extend them, and put new tests in
  `tests/test_agent_discovery.py`.
- The banned lexicon (`config.BANNED_TERMS`) binds the project's own
  prose (GUIDE §2). Every new sentence in these documents is our prose:
  add a test that scans the new documents' text for `BANNED_TERMS`
  (case-insensitive, word boundary).

**Determinism rule:** no timestamps (no `generated`, no `utc_now_iso()`)
in any new document, so two builds are byte-identical. Add one test that
builds twice into two directories and compares every new file's bytes.

**URL rule:** use absolute URLs `f"{base}/…"` when `base` is set; when
`base` is empty (local build, most tests), use root-relative `/…` paths
inside JSON documents and relative paths in HTML. Write one helper, e.g.
`_abs(base, path)`, and use it everywhere.

## 3. Tasks

### AD-2 — robots.txt: Content Signals, Agentmap, pointers

**Why:** Content Signals is scanner check 7 and the Level-2 gate; the
ruling is D1. `Agentmap:` is the AI Catalog's robots.txt discovery hook.

**Change** the robots block in `_build_agent_surfaces()` (~4831) so the
output is exactly (with `{base}` substituted):

```
# AI agents and crawlers are welcome here — indexing is
# encouraged. This is an AI-first digest of official US federal
# publications, built for machine ingestion as much as human
# reading.
#   Agent guide:  /agents.html
#   LLM guide:    /llms.txt
#   Machine index: /digests.json   Atom: /feed.xml
#   Source stats:  /sources.json  (our ingestion, not the record)
#   API catalog:  /.well-known/api-catalog   OpenAPI: /openapi.json
#   AI catalog:   /.well-known/ai-catalog.json
#   Agent skills: /.well-known/agent-skills/index.json
#   MCP:          /mcp  (read-only, no inference; see /agents.html)
#   Auth:         /auth.md  (there is none)
# /today.html is a PRELIMINARY live view; the dated digests are
# the record.
# Content signals (https://contentsignals.org/): search, AI input
# and AI training are all welcome. CC BY 4.0 attribution applies.
User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=yes
Allow: /

Sitemap: {base}/sitemap.xml
Agentmap: {base}/.well-known/ai-catalog.json
```

The `MCP:` comment line is correct once Phase 4 lands. The branch merges
as a whole, so it ships true. **If Phase 4 is ever dropped, delete that
line.**

**Tests:** extend `test_agent_surfaces_are_bot_friendly`. Assert the
`Content-Signal:` line appears exactly once, **inside** the
`User-agent: *` group (after that line, before the blank line). Assert
`Agentmap:` and `Sitemap:` lines exist. Parse the file with
`protego.Protego.parse` (already a dependency) and assert
`can_fetch("/", "GPTBot")`, `("…", "ClaudeBot")` and `("…", "*")` are
all true. The new lines must not break any crawler.

### AD-3 — `/openapi.json` and `/schema/*.schema.json`

**Why:** RFC 9727's `service-desc` relation needs a machine-readable API
description (scanner check 8). This also delivers backlog item "(c)
Published JSON Schemas". OpenAPI tooling can then generate typed readers
for what are, in fact, GET-only static files.

**Build:** new helpers `_json_schemas()` → dict filename→schema, and
`_openapi_doc(base)` → dict. Write with
`json.dumps(…, indent=1, sort_keys=True) + "\n"`.

**Schemas** (JSON Schema draft 2020-12; `$id` = `{base}/schema/<file>`).
Describe **what the code writes today**, not an ideal:
- `digests.schema.json`: object with `title`, `generated`,
  `agent_guide`, `digests[]` of `{date (pattern ^\d{4}-\d{2}-\d{2}$),
  html, canonical_markdown, teaser (string|null)}`.
- `today.schema.json`: the `build_today` payload keys (§2). `items[]`
  requires `package_id`, `observed_at`, `official_url`, `channel_label`,
  `tags`, `is_backfill`, `opening_verbatim`. **Copy each label string
  from the payload's `labels` object into the matching property's
  `description`**, so the honesty disclosures travel with the schema
  (GUIDE §1). Mark `additionalProperties: true` everywhere, because the
  file promises additive change.
- `day.schema.json`: `allOf` today plus `frozen: true`,
  optional `reconstructed_on`.
- `sources.schema.json`: `_sources_json` keys; `sources[]` items require
  `id`, `name`, `description`, `method`, `urls`, `added`, `card`,
  `page`. The `scope` description says "describes OUR ingestion, not any
  agency".

**OpenAPI 3.1 document** (`openapi: "3.1.0"`):
- `info`: `title` = "Free Agentic Publication Digester — static read
  API"; `version` = "1.0.0"; `description` explains, plainly: every path
  is a static file served by GET; no authentication; content is CC BY
  4.0 and quoted government text is public domain; the dated digests are
  the record and `today.json` is preliminary; cite official sources for
  claims. `license`: `{name: "CC BY 4.0", identifier: "CC-BY-4.0"}`.
- `servers`: `[{url: base or "/"}]`. `security: []`.
- `paths` (each `get` only, `operationId`, `summary`, `description`,
  `responses."200".content.<type>.schema.$ref` to `/schema/...` where
  applicable, and a `"404"` where the path is templated):
  - `/digests.json` → digests schema
  - `/today.json` → today schema (description says PRELIMINARY, and to
    filter `is_backfill=false` for the day's own news)
  - `/day/{date}.json` → day schema; `date` path parameter with pattern
  - `/sources.json` → sources schema
  - `/{date}.md` → `text/markdown` (canonical digest Markdown, the
    record). Note in the description that it's available once Phase 2
    lands; the branch ships whole.
  - `/feed.xml` → `application/atom+xml`
  - `/llms.txt` → `text/plain`
- `externalDocs`: `{url: base + "/agents.html"}`.

**Validator (D8):** `tests/schema_subset.py`, a minimal validator for the
subset of keywords the schemas use (`type` incl. lists, `properties`,
`required`, `items`, `pattern`, `enum`, `const`, `allOf`,
`additionalProperties: true`). Unknown keywords raise, so the subset
can't silently grow. About 80 lines, stdlib only.

**Tests:**
1. `build_site` into `tmp_path`, then validate the real `digests.json`
   and `sources.json` against the published schemas.
2. Seed a day with the existing `/today` test helper `_seed_today`
   (`tests/test_publish.py` ~1103). Run `build_today`, validate
   `today.json`. Run `build_day` for the same date, validate against
   `day.schema.json`.
3. Every `$ref` in `openapi.json` resolves to a built schema file.
4. OpenAPI paths only use `get`.

### AD-4 — `/.well-known/api-catalog` (RFC 9727)

**Build** a file literally named `api-catalog` (no extension) in
`out_dir/.well-known/`:

```json
{
 "linkset": [
  {
   "anchor": "{base}/",
   "service-desc": [
    {"href": "{base}/openapi.json", "type": "application/vnd.oai.openapi+json"}
   ],
   "service-doc": [
    {"href": "{base}/agents.html", "type": "text/html"},
    {"href": "{base}/llms.txt", "type": "text/plain"},
    {"href": "{base}/auth.md", "type": "text/markdown"}
   ],
   "describedby": [
    {"href": "{base}/.well-known/ai-catalog.json", "type": "application/ai-catalog+json"}
   ]
  },
  {
   "anchor": "{base}/mcp",
   "service-desc": [
    {"href": "{base}/mcp/server-card", "type": "application/mcp-server-card+json"}
   ],
   "service-doc": [
    {"href": "{base}/agents.html#mcp", "type": "text/html"}
   ]
  }
 ]
}
```

**No `status` relation:** FAPD runs no status endpoint. Pointing
`status` at `sources.json` would misdescribe that file. The second entry
(`/mcp`) references a card that Phase 4C builds.

**Tests:** valid JSON; every `href` without a fragment maps to a file in
the build (for `/mcp/server-card`, expect the path in the Phase 4C
contract instead: assert it's in a `PHASE4_PENDING` set that the Phase
4C agent removes); no `status` key anywhere.

### AD-5 — `/auth.md`

**Build** `out_dir/auth.md` from a module constant `_AUTH_MD`:

```markdown
# auth.md — Free Agentic Publication Digester

This file exists so automated clients can learn, without guessing, how
to authenticate to fapd.info. The answer is that you do not.

- **Audience:** any AI agent, crawler, or program.
- **Registration:** none. There are no accounts, API keys, OAuth
  clients, or registration endpoints, and none are planned.
- **Supported access:** anonymous HTTPS `GET` and `HEAD` for every
  published file, and anonymous JSON-RPC `POST` to the read-only MCP
  service at `/mcp`. Nothing else is accepted.
- **Credentials:** none are issued or read. Send none; an
  `Authorization` header is ignored.
- **What we ask in return:** identify yourself honestly in
  `User-Agent`, and use conditional requests (`If-None-Match`,
  `If-Modified-Since`). A per-address rate limit protects the shared
  server.
- **Start here:** `/llms.txt` · `/.well-known/api-catalog` ·
  `/agents.html`
```

**Tests:** the first line starts with `# auth.md`; the text contains no
URL ending in `register`, `token`, `authorize` or `oauth`.

### AD-6 — Agent Skills index and four SKILL.md files

**Spec (pinned):** Agent Skills Discovery RFC **v0.2.0**
(`https://github.com/cloudflare/agent-skills-discovery-rfc`, schema
`https://schemas.agentskills.io/discovery/0.2.0/schema.json`):
- Index at `/.well-known/agent-skills/index.json` =
  `{"$schema": "<that URL>", "skills": [ … ]}`.
- Each entry: `name` (1–64 chars, lowercase letters, digits and single
  hyphens, no leading or trailing hyphen), `type: "skill-md"`,
  `description`, `url`
  (`/.well-known/agent-skills/<name>/SKILL.md`), `digest`
  (`"sha256:" + 64 lowercase hex` of the **exact served bytes**).
- Each SKILL.md starts with YAML front matter containing `name` (equal to
  the index name) and `description`.

**Sources:** write the four files under `docs/site/agent-skills/<name>/SKILL.md`.
The build copies each byte-for-byte to
`out_dir/.well-known/agent-skills/<name>/SKILL.md` and computes the
digest from the copied bytes. Index order: alphabetical by name.

**The four skills.** Write them for an AI agent reader: numbered steps,
exact URLs (absolute `https://fapd.info/...`; these are public
instructions), what to check, what not to conclude. Under ~120 lines
each. No banned-lexicon terms. No claims about what the code doesn't do.

1. **`fapd-daily-digest`**, description: "Find and read the Free Agentic
   Publication Digester's validated daily digest of official US federal
   publications for a given date, and cite it correctly."
   Steps: fetch `/digests.json` (or `list_digests` via MCP) → pick the
   date → fetch `/<date>.md` (canonical Markdown; or `/<date>.html`) →
   read the header's Inference row and the Coverage Statement → tell
   verbatim official text apart from lines labeled as FAPD-AI
   restatements → for a factual claim, cite the official source linked
   on the item; cite FAPD for the aggregation → a missing date means no
   digest was published for it, not that nothing happened; check the
   weekend/holiday note.
2. **`fapd-live-day`**, description: "Read the in-progress federal
   publication day from today.json, or a finished day's frozen listing,
   without mistaking preliminary or backfilled items for the day's news."
   Steps: `/today.json` is PRELIMINARY; filter `is_backfill=false`; items
   with `duplicate_of` are second observations of the listed item;
   `corroborated_by` means another channel delivered the same URL, not a
   content judgment; `day_context` explains quiet weekends and holidays;
   `/day/<date>.json` is the frozen listing; the dated digest remains the
   record.
3. **`fapd-source-coverage`**, description: "Understand which federal
   sources the digest covers, which are planned or unavailable, and how
   to read its ingestion statistics."
   Steps: `/sources.json`; status active, planned or unavailable
   (unavailable is kept as a record of a refusal); the health labels and
   request statistics describe **our ingestion**, never an agency's
   performance; the thresholds are in the file, so labels can be
   recomputed; never cite this file as government publication.
4. **`fapd-verify-the-record`**, description: "Check a Free Agentic
   Publication Digester digest against its public repository history and
   provenance manifests."
   Steps: the canonical Markdown is `digests/<date>.md` in
   `https://github.com/davidkarnowski/free-agentic-publication-digester`;
   its git history shows when it was committed and whether it changed;
   `provenance/manifests/<date>.jsonl` records a SHA-256 for every fetch
   attempt of the day, and each manifest carries `prev_manifest_sha256`
   chaining it to the previous day. **Read `PROVENANCE.md` before writing
   this skill, and state only what it supports.** As of 2026-09-13,
   manifests hash *fetched source content*, not the digest file; don't
   write that a manifest verifies a digest.

**Tests:** index validates against the rules above (write the checks
directly: regex, digest recompute, front-matter parse with `yaml` or a
simple split); every `https://fapd.info/<path>` mentioned in a SKILL.md
maps to a file the fixture build produces, or to a templated path
documented in `openapi.json` (`/<date>.md`, `/day/<date>.json`) or in
the master plan §8.1 (`/mcp`); banned-lexicon scan.

### AD-7 — `/.well-known/ai-catalog.json` and site-wide head links

**Spec (pinned):** AI Catalog specification, `Agent-Card/ai-catalog`,
`specification/ai-catalog.md` as of 2026-09-13: media type
`application/ai-catalog+json`; required top-level `specVersion`
(`"1.0"`) and `entries`; `host.displayName` required when `host` is
present; each entry requires `identifier`, `type`, and exactly one of
`url` / `data`; recommended identifier `urn:air:{publisher}:{namespace}:{name}`.
**The scanner additionally requires** `host.identifier` and 2–5
`representativeQueries` per entry. Include both. Unknown members are
tolerated by the spec.

**Build** `out_dir/.well-known/ai-catalog.json`:

```json
{
 "specVersion": "1.0",
 "host": {
  "displayName": "Free Agentic Publication Digester",
  "identifier": "fapd.info",
  "documentationUrl": "{base}/agents.html"
 },
 "entries": [ … ]
}
```

`host.identifier` is the bare domain, **not `did:web:`**: a DID would
need a `/.well-known/did.json` we don't publish.

Entries, in this order. Each has `identifier`, `displayName`, `type`,
`url`, `description`, `tags` and `representativeQueries`. The queries
are **written by hand**, mechanical and party-neutral (they name
document types and dates, never parties, officials or issues):

| identifier | type | url | queries (2–5) |
|---|---|---|---|
| `urn:air:fapd.info:mcp:fapd` | `application/mcp-server-card+json` | `{base}/mcp/server-card` | "list the most recent federal publication digests"; "get the digest for 2026-09-04"; "what did the Federal Register publish yesterday" |
| `urn:air:fapd.info:api:static-read-api` | `application/linkset+json` | `{base}/.well-known/api-catalog` | "machine-readable index of daily federal digests"; "OpenAPI description of the FAPD files" |
| `urn:air:fapd.info:data:digest-index` | `application/json` | `{base}/digests.json` | "which dates have a published federal digest"; "teaser for each daily digest" |
| `urn:air:fapd.info:data:live-day` | `application/json` | `{base}/today.json` | "federal publications observed so far today"; "preliminary list of today's Congressional Record items" |
| `urn:air:fapd.info:data:source-directory` | `application/json` | `{base}/sources.json` | "which federal sources does the digest ingest"; "sources that are unavailable to automated clients" |
| `urn:air:fapd.info:feed:digests` | `application/atom+xml` | `{base}/feed.xml` | "subscribe to new daily federal digests" |
| `urn:air:fapd.info:guide:llms` | `text/plain` | `{base}/llms.txt` | "how should an AI agent use fapd.info" |
| `urn:air:fapd.info:skill:<name>` ×4 | `application/agent-skills+md` | `{base}/.well-known/agent-skills/<name>/SKILL.md` | two per skill, from its description |

The MCP entry points at a card Phase 4C builds. Use the same
`PHASE4_PENDING` test mechanism as AD-4.

**Head links:** add to `_PAGE`'s `<head>`, directly after the existing
`llms.txt` link:

```html
<link rel="api-catalog" href=".well-known/api-catalog">
<link rel="service-desc" type="application/vnd.oai.openapi+json" href="openapi.json">
<link rel="service-doc" type="text/html" href="agents.html">
<link rel="ai-catalog" type="application/ai-catalog+json" href=".well-known/ai-catalog.json">
<link rel="icon" href="favicon.ico" sizes="32x32">
```

(`rel="describedby"` for `llms.txt` is already covered by the existing
`alternate` link. Keep that one as it is; don't duplicate it.)

**Accessibility (doctrine §8):** `<link>` elements in `<head>` render
nothing and add nothing to the accessibility tree. No new page class,
so no findings entry. Say so in the exit report. **Do** run the existing
accessibility tests (they're part of the full suite).

**Tests:** every entry has exactly one of `url`/`data`; 2–5 queries;
identifiers unique and matching `^urn:air:fapd\.info:[a-z]+:[a-z0-9-]+$`;
every non-pending `url` maps to a built file; a root page, a
`sources/<id>.html` page and an `archive/<YYYY>.html` page each contain
the five links with correct relative prefixes (`../` on subdirectory
pages).

### AD-8 — `agents.html`, `llms.txt`, favicon, signpost body, the overclaim

**`_AGENTS_MD` changes:**
1. New section `## Discovery for agents` (after "What is here"): one
   bullet each for Content Signals, the API catalog + OpenAPI, the AI
   Catalog, the Agent Skills index, `auth.md`, Markdown twins ("append
   `.md` to a page URL, or send `Accept: text/markdown`"; Phase 2), and
   a pointer to the MCP section.
2. New section `## MCP service` with an explicit `{#mcp}` anchor. The
   `markdown` `toc` extension is on, so check how `_MD` renders heading
   ids and make sure `agents.html#mcp` resolves. **Phase 4C fills this
   section in.** In Phase 1 write only the heading and one sentence:
   "A read-only Model Context Protocol endpoint at `/mcp` is described
   in docs/mcp-server.md." Phase 4C replaces the sentence.
3. New section `## Protocols this site does not offer, and why`:
   - **OAuth / OpenID Connect discovery, OAuth protected-resource
     metadata:** nothing here is protected, so there's no authorization
     server to describe. See `/auth.md`.
   - **A2A agent card:** FAPD publishes a record; it isn't an agent that
     accepts tasks.
   - **WebMCP:** it would need a second script in every page. The site
     keeps exactly one (GUIDE §2a), and everything WebMCP would offer is
     already available as files, Markdown and MCP.
   - **Payment protocols (x402, MPP, UCP, ACP, AP2):** everything here
     is free.
   - "Requests to those protocols' well-known locations receive a 404
     whose body points here."
4. **Fix the overclaim** in `## Courtesy`: replace "Everything is static —
   no auth, no rate limiting, and nothing an agent needs to execute." with
   "Everything is static except the read-only MCP service — no
   authentication, nothing an agent needs to execute, and a generous
   per-address rate limit that protects the shared server."

**`llms.txt` changes** (`_build_agent_surfaces` lines list):
- In `## Core`, after the Atom feed line, add:
  `- [API catalog (RFC 9727)]({base}/.well-known/api-catalog) and [OpenAPI description]({base}/openapi.json)`
  `- [AI catalog]({base}/.well-known/ai-catalog.json)`
  `- [Agent skills]({base}/.well-known/agent-skills/index.json) — step-by-step instructions for reading and citing the digest`
  `- [MCP service]({base}/agents.html#mcp) — read-only, no inference: {base}/mcp`
  `- [auth.md]({base}/auth.md) — no authentication exists`
- In `## Notes`, add: `- Markdown: append .md to a digest URL
  (/<YYYY-MM-DD>.md is the canonical record), or send Accept: text/markdown.`
  and `- Declined protocols (OAuth, A2A, WebMCP, payments) and why: {base}/agents.html`.

**Favicon:** write `out_dir/favicon.ico` from a deterministic in-code
32×32 32-bit ICO. Build the BMP-in-ICO bytes with `struct` (stdlib) from
a small pixel map: a solid `#1f4e79` square with a white "F" glyph. Keep
the generator under ~40 lines. It's decorative, so no text alternative
is needed. Test: the file starts with `\x00\x00\x01\x00`, is identical
across two builds, and the head link exists.

**Signpost body** `out_dir/_signpost/not-offered.json` (Phase 3 serves it
as the body of refusals):

```json
{
 "status": "not offered",
 "explanation": "fapd.info does not operate this protocol. The site publishes official US federal publication digests as static files, a read-only MCP service at /mcp, and the discovery documents listed below. Nothing here requires authentication or payment.",
 "start_here": [
  "{base}/llms.txt",
  "{base}/.well-known/api-catalog",
  "{base}/.well-known/ai-catalog.json",
  "{base}/agents.html",
  "{base}/auth.md"
 ],
 "declined_protocols": "{base}/agents.html"
}
```

**Tests:** `test_agent_surfaces_built` gains assertions for every new
line and section; a test asserts the string `no rate limiting` appears
nowhere in the built site; the signpost JSON parses and every
`start_here` URL maps to a built file.

## 4. Acceptance criteria (report each as met / not met)

1. A fixture `build_site` produces every P1 path in master plan §8.1.
   A second build is byte-identical for all of them.
2. robots.txt parses with protego; all crawlers are still allowed; the
   Content-Signal line is inside the `*` group.
3. `openapi.json` is OpenAPI 3.1, GET-only, and every `$ref` resolves.
   Real `digests.json`, `sources.json`, `today.json` and `day/<date>.json`
   validate against the published schemas.
4. The API catalog and AI catalog meet their spec rules above, every
   non-pending link resolves, and there's no `status` relation.
5. Agent Skills: index digests equal sha256 of the served bytes; names
   and front matter match; every referenced URL is real or documented.
6. Every HTML page (root, `sources/`, `archive/`, `day/`, `today`)
   carries the §8.3 head links with correct relative prefixes.
7. `agents.html` has the Discovery, MCP (placeholder) and Declined
   sections and the corrected Courtesy sentence; `llms.txt` has the new
   lines; "no rate limiting" appears nowhere.
8. No banned-lexicon term in any new document.
9. `uv run ruff check .` clean; `uv run pytest -q` green (report
   counts).

## 5. Manual checks to run and paste into the exit report

```sh
uv run python - <<'PY'
import json, tempfile, pathlib
from fapd import publish
out = pathlib.Path(tempfile.mkdtemp()) / "site"
publish.build_site(out_dir=out)
for p in [".well-known/api-catalog", ".well-known/ai-catalog.json",
          ".well-known/agent-skills/index.json", "openapi.json", "auth.md",
          "robots.txt", "_signpost/not-offered.json", "favicon.ico"]:
    f = out / p
    print(p, f.exists(), f.stat().st_size if f.exists() else "-")
print(json.dumps(json.loads((out/".well-known/ai-catalog.json").read_text())["entries"][0], indent=1))
PY
```

(This builds from the real `digests/` into a temporary directory. It
doesn't touch `site/`.)

## 6. Rollback

Revert the phase commit. Built files left behind in a site volume are
harmless: nothing links to them without the code.

## 7. Dispatch prompt (orchestrator: launch with this text)

```
You are the FAPD PUBLICATION agent. Read docs/agents/publication.md IN FULL
before doing anything else — it is your instruction source of truth and
this prompt does not repeat it.

TASK: Implement Phase 1 of the agent-discovery plan: the static discovery
documents (robots Content Signals + Agentmap, openapi.json + JSON Schemas,
/.well-known/api-catalog, /auth.md, the Agent Skills index with four
SKILL.md files, /.well-known/ai-catalog.json, site-wide head links, the
agents.html and llms.txt updates including the declined-protocols section
and the "no rate limiting" correction, the favicon, and the signpost
body), exactly as specified in
docs/ops/plan-2026-09-13-phase1-discovery-documents.md, meeting every
acceptance criterion in its §4.

CONTEXT: Read docs/ops/plan-2026-09-13-agent-discovery.md first (rulings
§3, VPS findings §4, working protocol §7, interface contracts §8). Branch
feature/agent-discovery. Phase 3 (Operations, fapd-web nginx config) and
Phase 4A (the generic MCP package) run at the same time in the same tree
and edit none of your files; they build to the §8 contracts, so do not
change a contract without stopping and reporting. The MCP server card and
/mcp endpoint are built in Phase 4; reference them as the plan says and
use the PHASE4_PENDING test mechanism. Keep the progress log required by
docs/ops/plan-2026-09-13-agent-discovery.md §7.2; write its first entry
before touching any file. Do not run anything against the VPS. Do not
commit site/ output.

CONTRACT (non-negotiable):
1. Edit only files your section owns (your file §1 lists them). If the
   task seems to require editing a shared or foreign file, STOP work on
   that part and put the exact desired diff in your exit report instead.
2. Stage nothing, commit nothing. Leave the working tree modified.
3. Run `uv run ruff check .` and `uv run pytest -q` before reporting;
   report the actual numbers, including failures.
4. Follow docs/code-standards.md; match surrounding idiom.
5. New behavior gets a test that fails without the change.
6. If blocked, exit and report the blocker — do not improvise around it.

EXIT REPORT (required shape):
- Files modified (list)
- Shared-file diffs needed (exact diffs, or "none")
- Verification: ruff + pytest output tails, plus any manual checks run
- Deviations from the task, with rationale
- What a human should look at before this merges
- Acceptance criteria §4, each marked met / not met with evidence
- Progress log path, and all BLOG: lines copied out
```

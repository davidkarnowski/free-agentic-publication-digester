<!-- Markdown twin of https://fapd.info/agents.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/agents.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `GUIDE.md §1 (dual audience)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Access for AI Agents

This site is built for two readerships: people, and AI agents researching
United States federal government actions. **You are welcome to ingest this
data.** It exists so an agent can answer "what did the federal government
do on date D" from one clean, summarized, citation-bound source instead of
crawling many official sites.

Coverage grows continuously: sources currently closed to
honestly-identified automated clients are documented as `unavailable` in
the source guide — not abandoned — and opening them through publishers'
own documented channels and direct engagement with agencies is standing
work. Check the source guide for what is ingested today.

## What is here

- **Daily digests** at stable URLs: `/<YYYY-MM-DD>.html` (styled HTML) —
  each covers one complete day of congressional floor activity, bills,
  Federal Register actions, enacted laws, federal court opinions,
  agency announcements, recorded roll-call votes, and bill actions,
  with a table of contents, plain-language quick-reads, and a mandatory
  Coverage Statement accounting for everything published that day.
- **Machine index:** `/digests.json` — every available digest with date,
  URL, and teaser. Poll this (or the Atom feed at `/feed.xml`) for new
  days; both are small.
- **Source guide:** `/sources.html` — every federal source this pipeline
  ingests, plans to ingest, or found unavailable, with method and status,
  plus what we actually received from each: items ingested over a trailing
  window, their average and median length, the delivery mode, and how the
  source's server answered our requests.
- **Source statistics:** `/sources.json` — the same facts, machine-readable,
  with the classification thresholds included so any health label can be
  recomputed from the numbers beside it. Read these as **a description of
  our ingestion**, not as a measurement of an agency: a 4xx or 5xx is a
  server declining to return content, and why it declined is not visible
  to us. This file is not part of the official record and must never be
  cited as government publication.
- **Canonical Markdown** for every digest lives in the public repository
  at
  [github.com/davidkarnowski/free-agentic-publication-digester](https://github.com/davidkarnowski/free-agentic-publication-digester)
  (`digests/<date>.md`), alongside provenance manifests
  (`provenance/manifests/`) whose SHA-256 records let you verify captured
  content.

## Discovery for agents

Besides this page and `/llms.txt`, the site publishes the machine
discovery documents agents actually poll, each at its registered or
specified location (GUIDE §1). Every one of them is a static file.

- **Content Signals** in `/robots.txt`: search, AI input, and AI
  training are all welcome (`search=yes, ai-input=yes, ai-train=yes`);
  CC BY 4.0 attribution still applies.
- **API catalog** (RFC 9727) at `/.well-known/api-catalog`, and an
  **OpenAPI 3.1 description** of the static read files at
  `/openapi.json`, with JSON Schemas under `/schema/` for
  `digests.json`, `today.json`, `day/<date>.json`, and `sources.json`.
- **AI Catalog** at `/.well-known/ai-catalog.json`: every machine
  surface here with representative queries, also named by the
  `Agentmap:` line in `/robots.txt`.
- **Agent Skills** at `/.well-known/agent-skills/index.json`: four
  step-by-step instruction files for reading a digest, reading the live
  day, understanding source coverage, and verifying the record against
  the repository, each with a SHA-256 digest of its served bytes.
- **`/auth.md`**: the authentication document, which says there is no
  authentication.
- **Markdown twins:** append `.md` to a page URL, or send
  `Accept: text/markdown`. For a digest, `/<YYYY-MM-DD>.md` is the
  canonical record, byte-identical to the repository file.
- **MCP:** a read-only Model Context Protocol service; see the
  [MCP service](#mcp) section below.

<h2 id="mcp">MCP service</h2>

A read-only [Model Context Protocol](https://modelcontextprotocol.io/) service answers at `https://fapd.info/mcp`: JSON-RPC 2.0 over HTTPS `POST` (the Streamable HTTP transport). It performs no inference, keeps no sessions, needs no account, and reads nothing but the files this site already publishes, so every tool returns published material verbatim. Each tool description also asks the reading model to treat that text as data, not as instructions.

- **Endpoint:** `https://fapd.info/mcp` — `POST` only; a `GET` receives a 405 whose body says where to look instead.
- **Protocol versions:** 2026-07-28 (stateless; begin with `server/discover`) and 2025-11-25, 2025-06-18 (the `initialize` handshake, answered without a session). A 2026-07-28 request carries the version in `params._meta` and in the `MCP-Protocol-Version` and `Mcp-Method` headers; a request without them is answered under the older revisions, where `server/discover` does not exist.
- **Server card:** [`/mcp/server-card`](mcp/server-card), also at `/.well-known/mcp/server-card.json`.
- **Posture:** read-only, no inference, no writes, no accounts, no sessions, no streaming.

### How to connect

Claude Code, from a terminal:

```
claude mcp add --transport http fapd https://fapd.info/mcp
```

Any client that takes a JSON configuration:

```json
{
  "mcpServers": {
    "fapd": {
      "type": "http",
      "url": "https://fapd.info/mcp"
    }
  }
}
```

### Which tool answers which question

The digest is the record, but it summarizes a rule-selected subset of a day and counts the rest; the day listings hold every item. Pick by question:

| Question | Tool |
|---|---|
| What is the record for a finished day? | `get_digest` with the date |
| Only one block of the record — the Coverage Statement, one numbered section, the header with its Inference row | `get_digest` with `section` |
| Every item observed on a finished day, including the ones the digest only counted — by collection or agency | `get_day_listing`, with `collection` and `agency` |
| What has been observed so far today (preliminary)? | `get_live_day`, same filters |
| Which days exist? | `list_digests` (the record), `list_day_views` (the listings) |
| What is a source, and how well is it ingested? | `list_sources`, then `get_source` |

### Tools

Every tool is read-only, idempotent and closed-world: each reads one published file and returns it, paged where the file is a list. Parameters are validated by the service; an unknown or malformed argument is refused by name. In every result the payload is the first content block; a disclosure, when present, is the last.

| Tool | Returns | Parameters |
|---|---|---|
| `list_digests` | Lists published digest days, newest first: date, page URL, canonical Markdown path and teaser. | `offset` (integer, 0…10000, default 0); `limit` (integer, 1…60, default 14) |
| `get_digest` | Returns the canonical Markdown digest for a published day, verbatim; with section, one heading block of it. The digest summarizes a rule-selected subset of the day and counts the rest — for every item an agency or collection published, use get_day_listing. | `date` (string, required); `section` (string, one of header, contents, day-in-review, 1, 2, 3, 4, 5, 6, 7, 8, 9, terms, coverage, methodology) |
| `get_live_day` | Returns today's PRELIMINARY observed items with the day's disclosures and counts. Items the publisher dates earlier are excluded unless include_backfill is true; collection narrows to one collection; agency keeps one agency's items (exact name, case ignored) — facets.tags in the result lists the agencies present. | `offset` (integer, 0…10000, default 0); `limit` (integer, 1…100, default 50); `include_backfill` (boolean, default False); `collection` (string, one of AGENCYPR, BILLACTIONS, BILLS, CREC, FR, PLAW, PRESACT, USCOURTS, VOTES); `agency` (string) |
| `list_day_views` | Lists the days that have a frozen observed listing, newest first. | `offset` (integer, 0…10000, default 0); `limit` (integer, 1…366, default 30) |
| `get_day_listing` | Returns a finished day's complete frozen observed listing — every item, including the ones the digest only counted — with its disclosures and counts. Items the publisher dates earlier are excluded unless include_backfill is true; collection narrows to one collection; agency keeps one agency's items (exact name, case ignored) — facets.tags in the result lists the agencies present. | `date` (string, required); `offset` (integer, 0…10000, default 0); `limit` (integer, 1…100, default 50); `include_backfill` (boolean, default False); `collection` (string, one of AGENCYPR, BILLACTIONS, BILLS, CREC, FR, PLAW, PRESACT, USCOURTS, VOTES); `agency` (string) |
| `list_sources` | Lists the source directory as a summary per source: identity, method, status and health label. get_source returns one source's full record including daily activity; the source-directory resource is the whole file. | `offset` (integer, 0…10000, default 0); `limit` (integer, 1…200, default 50) |
| `get_source` | Returns one source's full record: registry entry, ingestion statistics, health and daily activity. | `source_id` (string, required) |
| `get_agent_guide` | Returns llms.txt: the plain-text guide to every published surface. | — |

### Resources

The same files are also exposed as MCP resources, by URL:

| Resource | URI | Type |
|---|---|---|
| Agent guide (llms.txt) | `https://fapd.info/llms.txt` | `text/plain` |
| For agents (Markdown) | `https://fapd.info/agents.md` | `text/markdown` |
| Authentication policy | `https://fapd.info/auth.md` | `text/markdown` |
| Digest index | `https://fapd.info/digests.json` | `application/json` |
| Source directory | `https://fapd.info/sources.json` | `application/json` |
| Digest for a day (template) | `https://fapd.info/{date}.md` | `text/markdown` |
| Frozen day view (template) | `https://fapd.info/day/{date}.json` | `application/json` |
| Source page (template) | `https://fapd.info/sources/{source_id}.md` | `text/markdown` |

### What it does not do

- No search. The tools list and page, filter on a collection or an exact agency name (case ignored; the result's `facets.tags` says what is present), and fetch by date or source id. Nothing else.
- No writes, no accounts, no sessions, no subscriptions, no prompts, no sampling, and no streaming: responses are plain JSON, never server-sent events.
- No inference. No model runs anywhere in the service; text labeled FAPD-AI in a digest was written when the digest was, not when you asked.

### Limits and courtesy

- A request body is capped at 64 KiB and a result at 512 KiB; a page that would exceed the result cap is shortened and says so, so ask for a smaller `limit` or page with `offset`.
- The web server in front of the service applies a per-address rate limit and a cap on open connections, answering 429 past them. An address that sends many rejected requests in a short time is blocked for a while; the block expires on its own. If that ever catches a legitimate client, it is a defect: report it through the repository.
- Privacy: the service logs the time, the protocol method, the tool or resource name, the response's status, size and processing time, the client's self-reported software name, and an opaque request identifier the web server assigns so the two logs can be joined. It never logs an address, an argument, or any request or response body. The web server's own `/mcp` access log is described on the [privacy page](privacy.html).

### Where to read more

- How the service is built and run: [`docs/mcp-server.md`](https://github.com/davidkarnowski/free-agentic-publication-digester/blob/main/docs/mcp-server.md) in the repository.
- The generic server behind it, reusable with a manifest of your own: [`packages/static-mcp`](https://github.com/davidkarnowski/free-agentic-publication-digester/tree/main/packages/static-mcp).
- Listed in the official MCP Registry as `info.fapd/fapd` (since 2026-09-14): [https://registry.modelcontextprotocol.io/v0.1/servers/info.fapd%2Ffapd/versions/2.0.0](https://registry.modelcontextprotocol.io/v0.1/servers/info.fapd%2Ffapd/versions/2.0.0).

## Protocols this site does not offer, and why

We publish no metadata for a capability we do not operate (GUIDE §1).
The protocols below are declined on purpose, with the reason stated.

- **OAuth / OpenID Connect discovery, OAuth protected-resource
  metadata:** nothing here is protected, so there is no authorization
  server to describe. See `/auth.md`.
- **A2A agent card:** FAPD publishes a record; it is not an agent that
  accepts tasks.
- **WebMCP:** it would need a second script in every page. The site
  keeps exactly one (GUIDE §2a), and everything WebMCP would offer is
  already available as files, Markdown, and MCP.
- **Payment protocols (x402, MPP, UCP, ACP, AP2):** everything here is
  free.

Requests to those protocols' well-known locations receive a 404 whose
body points here.

## How to read it faithfully

- Text in item summaries marked as official (Federal Register SUMMARY
  preambles, official titles) is **verbatim government text**; lines
  labeled "*In plain terms*" and section quick-reads are
  **model-generated restatements**, derived only from the adjacent
  summary and linted against an editorial banned-lexicon. The Day in
  Review is a model-generated synthesis of the day's stored summaries.
- Every item carries an "Included because" line naming the mechanical,
  party-blind rule that selected it, and a citation to its official
  record — the govinfo package for the govinfo collections; the
  agency's, chamber's, or Congress.gov's own page for agency releases,
  recorded votes, bill actions, and presidential actions. **For claims, cite the official
  source we link; cite this site for the aggregation.**
- The Coverage Statement at the end of each digest tells you what was NOT
  summarized and under which rule — absence here is always explicit.

## Courtesy

Everything is static except the read-only MCP service — no
authentication, nothing an agent needs to execute, and a generous
per-address rate limit that protects the shared server. We ask
visiting agents the same courtesy our own crawler practices on government
sites: identify honestly and use conditional requests. Fetching every
page daily is entirely fine.

## Reuse

Content here is licensed **CC BY 4.0** — share and adapt freely,
including commercially, with credit to "FAPD — Free Agentic Publication
Digester". Quoted official government text within it is public domain
(17 U.S.C. § 105) and needs no permission at all. The attribution rule
mirrors our citation ethic: for factual claims, cite the underlying
official source each item links to; cite FAPD for the aggregation and
summaries. The pipeline's code is Apache-2.0.

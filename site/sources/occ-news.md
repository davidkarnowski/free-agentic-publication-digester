<!-- Markdown twin of https://fapd.info/sources/occ-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/occ-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: occ-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# OCC News Releases

planned · Executive · Tier 2 · HTML index · Department of the Treasury

Official site: https://www.occ.gov/news-issuances/news-releases/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of the Comptroller of the Currency, a Treasury bureau, charters and supervises national banks and federal savings associations. Its news-release index carries supervision and enforcement announcements, including monthly enforcement-action lists, typically a few items per week.

**Model-written orientation**

The Office of the Comptroller of the Currency, a bureau of the Treasury Department, charters and supervises national banks; its press releases cover supervision, enforcement, and regulatory matters.

The Office of the Comptroller of the Currency is a bureau of the Department of the Treasury established in 1863. The OCC charters, regulates, and supervises national banks and federal savings associations. As the primary regulator of the national banking system, the OCC sets capital requirements, lending standards, and other operating parameters for the institutions it supervises.

OCC press releases announce supervisory and regulatory actions, including enforcement matters such as sanctions against banks or officers, examination findings or supervisory guidance, capital and liquidity determinations, and policy changes affecting supervised institutions. The agency publishes monthly lists of enforcement actions, making public the range of supervisory responses from warnings to formal enforcement orders.

The OCC also announces rulemaking activities, policy decisions, and major regulatory initiatives. Readers will encounter announcements of new supervisory guidance, changes to regulatory requirements, responses to economic developments, and updates on the agency's operations. The press releases include technical bulletins and advisories on compliance matters, updates to examination procedures, and guidance on regulatory interpretation.

As the federal regulator of national banks, the OCC's press releases constitute the official public disclosure of its regulatory and supervisory actions. They serve as the primary means through which the agency communicates its expectations for supervised institutions, announces policy changes, and makes public its enforcement determinations. These announcements typically appear before the actions are compiled in official regulatory or legal databases.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `occ-news` |
| Agency / parent organization | Department of the Treasury |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.occ.gov/news-issuances/news-releases/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — but research 2026-07-28 found OCC documents an RSS index at occ.gov/rss/index-rss.html with separate feeds for News Releases, Bulletins, Alerts, and Public Service Announcements (Bulletins/Alerts add supervisory-guidance coverage beyond press). Capture exact feed URLs from that page at probe; upgrade type to rss on confirmation. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 77 article link(s); 0 dated inside the 7-day lookback, 0 dated outside it, 77 skipped for no readable date — the served HTML states no per-entry publication date, so every entry is skipped rather than dated by observation. This is a script-rendered listing; opening it needs evidence of a dated channel, not a cadence decision. Probed 2026-08-06: https://www.occ.gov/rss/index-rss.html is an HTML index of RSS offerings, not a feed (verdict html-only). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would poll the documented RSS suite (occ.gov/rss/index-rss.html) for news releases, bulletins, and alerts. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.occ.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

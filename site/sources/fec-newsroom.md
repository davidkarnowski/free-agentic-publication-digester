<!-- Markdown twin of https://fapd.info/sources/fec-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fec-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fec-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FEC Press Releases

planned · Executive · Tier 1 · HTML index · Independent agency

Official site: https://www.fec.gov/updates/ · All sources: [sources.md](../sources.md)

## What this source is

The Federal Election Commission administers and enforces federal campaign-finance law. Its updates index carries press releases, commission meeting agendas, and closed enforcement matters, typically a few items per week.

**Model-written orientation**

The FEC publishes press releases about campaign-finance enforcement actions, regulatory guidance, and commission proceedings.

The Federal Election Commission is an independent agency established by Congress to administer and enforce federal campaign-finance law governing contributions and expenditures in federal elections. The FEC exercises regulatory and enforcement authority over candidates, political parties, political action committees (PACs), and other entities participating in federal elections.

The FEC's updates index carries press releases announcing enforcement actions, closed enforcement matters, commission meeting agendas and decisions, and regulatory guidance. Readers will see a few items per week describing enforcement proceedings, settled violations, policy decisions, and administrative announcements.

The releases announce civil enforcement actions and penalties assessed against candidates, committees, individuals, and organizations for campaign-finance law violations. Typical matters involve improper contributions exceeding legal limits, inadequate or inaccurate disclosure of contributions and expenditures, unauthorized use of committee funds, and non-compliance with FEC registration or reporting requirements. Each enforcement release describes the violation alleged or substantiated, the civil penalties assessed, and any remedial action or reporting requirements imposed. The FEC also announces rulemakings addressing campaign-finance regulation and publishes guidance on compliance with contribution limits, disclosure requirements, and coordination restrictions. The agency maintains a public database of campaign finance filings by candidates, committees, and donors, and the press releases often reference specific candidates or entities whose conduct was examined. The variety of releases reflects the FEC's role in overseeing financial activity in all federal elections and in maintaining public disclosure of money in federal campaigns.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fec-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.fec.gov/updates/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Research 2026-07-28: the OpenFEC API (api.open.fec.gov, api.data.gov key we hold, 1,000 calls/hr documented) covers filings/candidates/committees and legal-enforcement data — a rung-1 complement to the press index, not a replacement for it. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 54 article link(s); 2 dated inside the 7-day lookback, 21 dated outside it, 31 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the updates HTML index (filtered to press releases) daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.fec.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

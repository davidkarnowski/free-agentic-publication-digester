<!-- Markdown twin of https://fapd.info/sources/regulations-gov-api.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/regulations-gov-api.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: regulations-gov-api)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Regulations.gov API v4

planned · Executive · Tier 1 · API · General Services Administration (eRulemaking Program)

Official site: https://open.gsa.gov/api/regulationsgov/ · All sources: [sources.md](../sources.md)

## What this source is

The eRulemaking program's API exposes rulemaking dockets, documents, and public comments across roughly 180 agencies as structured JSON, searchable by agency and date — the comment-and-docket layer of rulemaking that neither the Federal Register nor govinfo carries.

**Model-written orientation**

The Regulations.gov API provides structured access to rulemaking documents, dockets, and public comments across federal agencies.

Regulations.gov is the federal government's official online portal for rulemaking. The site hosts rulemaking dockets and documents from roughly 180 federal agencies, along with public comments submitted on proposed rules and other rulemaking actions.

The regulations.gov API is maintained by the eRulemaking program, which is part of the General Services Administration. The API provides structured access to the rulemaking documents, dockets, and comments published on regulations.gov as JSON, searchable by date, agency, document type, and other fields.

When an agency publishes a proposed rule, it must publish it in the Federal Register and establish a rulemaking docket where the public can review and comment on the proposal. That docket, the proposed rule and related documents, and public comments submitted by the public and interest groups are all available through the regulations.gov portal. The portal centralizes these dockets, which would otherwise be scattered across agency websites.

The API allows programmatic access to these rulemaking documents and dockets. This includes the proposed rules themselves, supporting documents and analyses, agency responses to comments, and metadata about dockets and comment periods.

The API requires authentication via an API key and requires that uses link back to regulations.gov. Regulations.gov captures an important layer of the rulemaking process: the comment-and-docket stage, where the public participates and agencies respond. This stage is not captured by the Federal Register or by other sources. The API is particularly valuable for tracking rulemaking across all agencies simultaneously.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `regulations-gov-api` |
| Agency / parent organization | General Services Administration (eRulemaking Program) |
| Branch | executive |
| Type | API |
| Status | planned |
| Tier | 1 |
| URL (home) | https://open.gsa.gov/api/regulationsgov/ |
| URL (index) | https://api.regulations.gov/v4/documents |
| Registered | 2026-07-28 |
| Registry notes | Docs fetched 2026-07-28 (open.gsa.gov). Terms require linking back to regulations.gov. Rate limits 'variable, increases may be requested'. Per-agency filtering could power many registry views without per-site scraping. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Would query the v4 documents endpoint by posted date (api.data.gov key we already hold, X-Api-Key header). |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to api.regulations.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

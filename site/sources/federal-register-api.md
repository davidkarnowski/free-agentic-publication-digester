<!-- Markdown twin of https://fapd.info/sources/federal-register-api.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/federal-register-api.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: federal-register-api)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Register API (public inspection)

planned · Executive · Tier 1 · API · National Archives / Office of the Federal Register

Official site: https://www.federalregister.gov/developers/documentation/api/v1 · All sources: [sources.md](../sources.md)

## What this source is

The Office of the Federal Register's own REST API serves every FR document as structured JSON — and, uniquely, public-inspection documents: rules, notices, and presidential documents filed for public inspection before their publication day. The earliest official, structured channel for executive orders and major rules.

**Model-written orientation**

The Federal Register's official API provides structured access to all Federal Register documents and to public-inspection documents filed before their official publication.

The Federal Register is the official daily journal of the federal government. Every executive order, rule, notice, and other presidential or agency document subject to Federal Register publication is recorded there, along with meeting notices, proposed rules, and other administrative materials.

The Office of the Federal Register, which is part of the National Archives, manages the Federal Register and maintains its official application programming interface (API). This API provides structured, machine-readable access to every Federal Register document as JSON, searchable and browsable by date, agency, document type, and other fields.

One distinctive feature of the API is that it serves not just published documents but also public-inspection documents—materials that agencies file for publication before their official publication date. Federal law requires certain categories of documents to be filed with the Federal Register office and made publicly available for a period before they take official effect. These materials include executive orders, major rules, and presidential documents. The public-inspection system is designed to give the public notice and access to important executive actions and rules before they officially take effect.

The Federal Register API is the earliest official channel through which these public-inspection documents become available in structured, searchable form. Agencies also publish many of these same documents through other channels—their own websites, press releases, and other systems—but the Federal Register API provides the structured, official record.

The API is designed for automated access and is explicitly offered as the sanctioned channel for automated clients and bots. This source is valuable for readers and systems seeking structured access to executive branch documents and advance notice of major rules and executive actions.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `federal-register-api` |
| Agency / parent organization | National Archives / Office of the Federal Register |
| Branch | executive |
| Type | API |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.federalregister.gov/developers/documentation/api/v1 |
| URL (index) | https://www.federalregister.gov/api/v1/public-inspection-documents.json |
| Registered | 2026-07-28 |
| Registry notes | Keyless, officially documented. The site's own bot-gate page (unblock.federalregister.gov) explicitly directs automated visitors to the API — the sanctioned channel. Complements govinfo-fr (which sees documents only on publication day); does not duplicate it. Exact rate-limit terms unreadable to research fetchers; capture at probe. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Would delta-sync the public-inspection and documents endpoints (keyless JSON REST). |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.federalregister.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

<!-- Markdown twin of https://fapd.info/sources/loc-api.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/loc-api.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: loc-api)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Library of Congress JSON API

evaluated and excluded · Legislative · Tier 3 · API · Library of Congress

Official site: https://www.loc.gov/apis/ · All sources: [sources.md](../sources.md)

## What this source is

The loc.gov JSON/YAML API over the Library's collections, including Prints & Photographs — an archive of record with per-item rights variation, not a publication stream.

**Model-written orientation**

The Library of Congress JSON API provides programmatic access to the nation's library collections, including the Prints & Photographs Online Catalog, with item-level rights variation.

The Library of Congress is the research library of the United States Congress and serves as the de facto national library. Its collections span millions of items, including books, manuscripts, maps, photographs, prints, audio and video recordings, and digital materials documenting American culture and history.

The Library's JSON and YAML APIs enable programmatic search and retrieval across these collections. Unlike federal agency publications that are uniformly in the public domain, the Library's holdings include materials with varying rights statuses—some items are in the public domain, while others have copyright restrictions or donor-imposed conditions. Each item carries explicit rights documentation that must be observed.

As an archival collection rather than a source of current government action, the Library's materials reflect historical documentation and cultural artifacts rather than contemporaneous policy announcements or official decisions. Like the National Archives, the Library preserves and catalogs what has been, making it a resource for historical research and context rather than a source of tracking current government activities. The Library's collections grow through acquisition of manuscripts, donations, and transfers from other institutions, with preservation and cataloging following archival standards.

Congress and federal agencies rely on the Library's research capabilities and collections to support legislative work and government decision-making. Legislative data needs are separately met by dedicated congressional data sources such as the Congress.gov API. The API operates under enforced rate limits and requires no API key, with access designed for research and reference uses rather than for monitoring daily government actions and announcements.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `loc-api` |
| Agency / parent organization | Library of Congress |
| Branch | legislative |
| Type | API |
| Status | evaluated-excluded |
| Tier | 3 |
| URL (home) | https://www.loc.gov/apis/ |
| Registered | 2026-07-28 |
| Registry notes | Evaluated 2026-07-28: keyless documented API with enforced rate limits (429s under load), but archival; rights vary per item (LoC holdings are not uniformly public domain). Current legislative-data needs are met by api.congress.gov. Revisit for historical features only. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Not applicable to the daily flow — archive, not news-flow. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is evaluated-excluded.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is evaluated-excluded. Ingestion statistics are measured for active sources only.

### All time

No requests to www.loc.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

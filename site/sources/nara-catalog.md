<!-- Markdown twin of https://fapd.info/sources/nara-catalog.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nara-catalog.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nara-catalog)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# National Archives Catalog API

evaluated and excluded · Executive · Tier 3 · API · National Archives and Records Administration

Official site: https://catalog.archives.gov/api/v2/api-docs/ · All sources: [sources.md](../sources.md)

## What this source is

NARA's Catalog API v2 (catalog.archives.gov/api/v2) serves the nation's archival records, including DoD imagery transferred for preservation — an archive of record, not a publication stream.

**Model-written orientation**

The National Archives Catalog API provides access to the nation's archival records, including preserved Department of Defense imagery, through a documented API interface.

The National Archives and Records Administration maintains the official archives of the United States government, preserving records of historical significance and national importance. The Catalog API v2 provides programmatic access to holdings across this vast collection, including historical documents, photographs, and materials transferred for permanent preservation.

As an archival system, the Catalog serves as a record of what the government has done historically rather than a source of current government action or policy announcements. The materials in the National Archives reflect the documented history of federal operations, decisions, and activities across decades and centuries. Researchers, historians, and institutions use archival access to study government processes, decisions, and public administration.

The API operates under a documented key system with a monthly query allocation; access follows standard archival access policies and item-level rights documentation. Because archival materials are added to the collection as records are transferred for preservation—a process that reflects historical activity rather than contemporaneous government action—the Catalog does not function as a source of daily government news or current policy developments. It is consulted for historical context and background rather than for tracking the government's ongoing activities and announcements.

Archival records become available for research after agency disposition schedules allow transfer, and the National Archives applies standard preservation and access protocols to all materials. The Catalog represents the authoritative registry of what the government has chosen to preserve as its official record.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nara-catalog` |
| Agency / parent organization | National Archives and Records Administration |
| Branch | executive |
| Type | API |
| Status | evaluated-excluded |
| Tier | 3 |
| URL (home) | https://catalog.archives.gov/api/v2/api-docs/ |
| Registered | 2026-07-28 |
| Registry notes | Evaluated 2026-07-28 in the multi-modal survey: documented API (key by email to [address withheld], 10,000 queries/month default) but archival by nature — nothing it publishes constitutes a new government action on a given day. Revisit only for deliberate historical-context or backfill features. |

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

No requests to catalog.archives.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

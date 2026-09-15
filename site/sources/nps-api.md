<!-- Markdown twin of https://fapd.info/sources/nps-api.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nps-api.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nps-api)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# National Park Service API

planned · Executive · Tier 3 · API · Department of the Interior (NPS)

Official site: https://www.nps.gov/subjects/developer/api-documentation.htm · All sources: [sources.md](../sources.md)

## What this source is

The NPS developer API (developer.nps.gov) exposes news releases, alerts, events, and multimedia (galleries, videos, webcams) across the park system as structured JSON. News and alerts are the current-flow value; multimedia is largely evergreen reference.

**Model-written orientation**

The National Park Service developer API provides structured access to news, alerts, and multimedia across the national park system.

The National Park Service (NPS), a bureau of the Department of the Interior, manages America's national parks, national monuments, national seashores, and other protected lands and sites. The agency operates approximately 60 national parks and over 400 total sites encompassing diverse ecosystems, historical areas, and recreational resources. NPS responsibilities include resource preservation, visitor services, facility management, and coordination with state and local partners on conservation and recreation.

The NPS developer API provides structured, machine-readable access to operational data from parks and sites across the system. The API exposes news releases covering park management decisions, facility openings and closures, resource protection initiatives, and visitor-services announcements. Safety and operational alerts address immediate public-safety concerns such as hazardous conditions, temporary closures due to weather or maintenance, and visitor-access restrictions. The API also provides access to multimedia resources including photographs, videos, and webcam feeds from parks, which are largely evergreen reference material but reflect current facility and resource conditions.

News and alerts represent the current operational flow from parks nationwide, providing timely information about park conditions, management activities, and visitor safety. The structured JSON format enables researchers, application developers, and information systems to programmatically access NPS data. Readers of this digest will encounter updates about specific park operations, resource management actions, visitor-facility developments, and safety matters relevant to the park system. Content spans announcements from parks in all regions of the United States and covers both major parks and smaller historical and recreational sites. The API reflects the NPS's mission of preserving natural and historical resources while providing public access and managing visitor safety across the protected areas under its stewardship.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nps-api` |
| Agency / parent organization | Department of the Interior (NPS) |
| Branch | executive |
| Type | API |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.nps.gov/subjects/developer/api-documentation.htm |
| Registered | 2026-07-28 |
| Registry notes | Search-corroborated 2026-07-28 (docs page is JS-shelled to research fetchers; read via our client at probe). Text endpoints first; multimedia opportunistic. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Would query news/alerts endpoints with a registered key (documented 1,000 req/hour). |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.nps.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

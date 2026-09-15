<!-- Markdown twin of https://fapd.info/sources/gsa-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/gsa-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: gsa-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# GSA News Releases

planned · Executive · Tier 1 · HTML index · Independent agency

Official site: https://www.gsa.gov/about-us/newsroom/news-releases · All sources: [sources.md](../sources.md)

## What this source is

The General Services Administration manages federal procurement, real estate, and shared technology services. Its news-release index carries announcements on contracts, federal buildings, and government-wide programs, typically a few items per week.

**Model-written orientation**

The General Services Administration oversees federal procurement, real estate, and shared technology services. Its newsroom publishes announcements on contracts, federal property, and government-wide initiatives, typically several items per week.

The General Services Administration (GSA) is an independent agency responsible for managing critical federal infrastructure and services that support the entire U.S. government. GSA's portfolio spans federal real estate holdings, civilian procurement operations, supply and logistics management, and information technology services shared across agencies. The agency serves as the landlord for much of the federal government's office space and facilities, manages billions of dollars in annual procurement contracts, and provides technology platforms and telecommunications services used government-wide.

The GSA newsroom publishes announcements about the agency's operations and policy decisions. Readers will encounter news about federal procurement awards and contracts, including major acquisitions for goods and services used by federal agencies. The newsroom also carries updates on federal building projects, real estate transactions, facility management decisions, and announcements about federal properties. Additionally, the newsroom publishes policy announcements related to government-wide technology initiatives, shared services offerings, and GSA programs that affect how other agencies conduct their work. Content also includes updates on GSA-administered programs such as the General Services Schedule (a government-wide contract vehicle) and the Federal Acquisition Service.

Items are published with dates assigned by GSA and typically appear at a frequency of several per week. The newsroom serves as GSA's primary official channel for communicating its operational decisions, policy updates, and major contract and real estate actions to the public. Readers can expect straightforward, operational announcements related to federal administration and shared services.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `gsa-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.gsa.gov/about-us/newsroom/news-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 319 article link(s); 2 dated inside the 7-day lookback, 58 dated outside it, 259 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the news-release HTML index daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.gsa.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

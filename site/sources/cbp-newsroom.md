<!-- Markdown twin of https://fapd.info/sources/cbp-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cbp-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cbp-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CBP Media Releases

planned · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.cbp.gov/newsroom/media-releases · All sources: [sources.md](../sources.md)

## What this source is

U.S. Customs and Border Protection, within DHS, controls the borders and ports of entry. Its national media-release index carries announcements on border enforcement, trade actions, and travel operations, typically several items per week; field offices publish additional local releases.

**Model-written orientation**

U.S. Customs and Border Protection (CBP), within the Department of Homeland Security, manages the nation's borders and ports of entry. Its media releases announce border enforcement operations, trade-related actions, and travel procedures.

U.S. Customs and Border Protection is the Department of Homeland Security agency responsible for securing and managing the United States' borders, including all land borders, seaports, and airports. CBP's mandate encompasses immigration and customs enforcement, trade facilitation and tariff collection, and ports-of-entry operations. The agency employs officers and agents at the border and maintains oversight of international travel and commerce flowing through U.S. ports.

The CBP newsroom publishes official announcements about the agency's activities and policies. Publications typically include press releases on border-enforcement operations and interdiction activity; trade actions, tariff determinations, and trade compliance matters; ports-of-entry infrastructure and operations; travel requirements, documentation procedures, and entry policies; and new technologies or procedures deployed at border checkpoints.

In this digest, you will find CBP announcements about enforcement operations and agency activities (disclosed as part of operational transparency); changes to travel procedures, documentation requirements, or entry policies; new initiatives or technology installations at ports of entry; trade-related actions and tariff updates; and operational notices affecting international travelers and commerce entering the United States.

CBP's newsroom releases are factual announcements about agency operations and policy. Field offices also publish local releases; this digest covers the national media-release index. The releases serve as CBP's official channel for communicating about border and trade operations to the public. Publications emerge at a rate of several items per week, though rates vary seasonally and by operational developments.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cbp-newsroom` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.cbp.gov/newsroom/media-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. The page states one <time datetime> value, 2020-09-30T12:00:00+01:00, repeated on every entry — a template default, not a publication date. The lookback window is what kept those 11 entries out; do not activate this source until CBP publishes a real per-entry date. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | HTML index diff via AgencyClient (pending content evaluation) |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.cbp.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

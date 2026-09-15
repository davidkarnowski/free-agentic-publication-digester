<!-- Markdown twin of https://fapd.info/sources/energy-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/energy-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: energy-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Energy Press Releases

planned · Executive · Tier 1 · HTML index · Department of Energy

Official site: https://www.energy.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Department of Energy manages energy research, the national laboratories, and the nuclear weapons stockpile. Its newsroom index carries departmental press releases on funding awards, energy programs, and nuclear security, typically several items per week.

**Model-written orientation**

The Department of Energy operates the nation's system of federal laboratories and manages energy research and nuclear security; its newsroom publishes press releases on funding awards, research initiatives, and related developments.

The Department of Energy, established in 1977, is a cabinet-level agency responsible for advancing energy science and technology, managing the nation's nuclear weapons stockpile, and supporting energy-related research and development. The department operates or sponsors 17 national laboratories and conducts research across multiple scientific disciplines, from basic energy sciences to applied engineering and nuclear security.

The Energy newsroom publishes announcements of departmental activities and initiatives. These press releases typically cover funding awards to research institutions and companies, laboratory discoveries and technological advances, announcements of new programs or program expansions, and statements on energy policy matters within the department's purview. The newsroom also announces personnel appointments, facility updates, and participation in national or international energy-related initiatives.

DOE's research portfolio spans nuclear energy, renewable energy systems, energy efficiency, electric grid modernization, and basic energy science. The department manages the Strategic Petroleum Reserve, provides technical support to the power sector, and conducts research into emerging energy technologies. Readers of this source will encounter announcements reflecting this broad scope—awards for renewable energy research, advances in battery technology, nuclear security initiatives, and updates on major research projects at national laboratories.

The department's press releases are the primary means by which it communicates new initiatives, funding decisions, and policy developments to the public. They serve as the official record of departmental announcements and provide the first formal notice of many energy-related developments.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `energy-newsroom` |
| Agency / parent organization | Department of Energy |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.energy.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. The listing parses, but energy.gov's mega-menu puts topic, search and event links in the same date-bearing blocks as the releases, and three of them picked up a neighbouring release's date. An index_item_path of '/articles/' cuts it to 7 clean releases; that hint is registered nowhere yet because the source is not being activated. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the newsroom HTML index daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.energy.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

<!-- Markdown twin of https://fapd.info/sources/cdc-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cdc-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cdc-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CDC Newsroom

planned · Executive · Tier 2 · HTML index · Department of Health and Human Services

Official site: https://www.cdc.gov/media/index.html · All sources: [sources.md](../sources.md)

## What this source is

The Centers for Disease Control and Prevention is the national public-health agency within HHS. Its media index carries press releases, media statements, and telebriefing transcripts on outbreaks, advisories, and health guidance, typically several items per week.

**Model-written orientation**

The Centers for Disease Control and Prevention is the federal public-health agency within the Department of Health and Human Services, publishing health advisories and outbreak information.

The Centers for Disease Control and Prevention (CDC) is the primary federal agency responsible for protecting public health and safety in the United States. A division of the Department of Health and Human Services, CDC conducts disease surveillance, epidemiological investigation, research into disease prevention and control, and operates emergency-response systems for health threats. The agency's scope spans infectious disease, chronic disease, environmental health, workplace safety, injury prevention, and emergency preparedness.

CDC's work includes monitoring disease occurrence and trends through national surveillance systems, investigating outbreaks and unusual disease patterns, conducting research to understand disease causes and prevention strategies, and issuing health guidance and recommendations. The agency maintains laboratory and diagnostic capabilities, supports state and local health departments, and works internationally on disease control and health security. CDC is often a primary source of federal health information during outbreaks, health emergencies, and widespread public-health concerns.

In this digest, you will find CDC press releases and statements on disease outbreaks and their investigation, public-health advisories and warnings, updates on vaccine safety and efficacy, guidance on disease prevention and control, laboratory findings, and responses to emerging health threats. The releases may address foodborne illness, respiratory disease, vector-borne illness, and many other health domains. CDC's public releases inform healthcare providers, public-health officials, the media, and the general public of significant health developments and agency recommendations.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cdc-newsroom` |
| Agency / parent organization | Department of Health and Human Services |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.cdc.gov/media/index.html |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 19 article link(s); 1 dated inside the 7-day lookback, 6 dated outside it, 12 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: https://www.cdc.gov/rss is an HTML feed-directory page, not a feed (verdict html-only). Same shape as nsf-news. |

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

No requests to www.cdc.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

<!-- Markdown twin of https://fapd.info/sources/nrc-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nrc-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nrc-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NRC News Releases

planned · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.nrc.gov/reading-rm/doc-collections/news/ · All sources: [sources.md](../sources.md)

## What this source is

The Nuclear Regulatory Commission licenses and oversees civilian nuclear reactors and materials. Its news index carries releases on licensing actions, inspections, and enforcement, typically a few items per week.

**Model-written orientation**

The Nuclear Regulatory Commission licenses and oversees civilian nuclear reactors and nuclear materials in the United States, publishing releases on regulatory actions and enforcement.

The Nuclear Regulatory Commission (NRC) is an independent agency that regulates the civilian use of nuclear energy. Established by the Energy Reorganization Act of 1974, the NRC licenses and oversees nuclear reactors used for electricity generation and research, and regulates the possession, use, transport, and disposal of nuclear materials. The agency's core mission is to ensure public health and safety, protect the environment, and provide for the security of nuclear materials and facilities.

The NRC's regulatory work includes issuing operating licenses for nuclear power plants, conducting regular safety inspections, evaluating performance against regulatory standards, and taking enforcement actions when facilities or licensees do not meet requirements. The commission also regulates the nuclear fuel cycle—uranium enrichment, conversion, fabrication, and spent-fuel management—and oversees the use of radioactive materials in medical, industrial, and research applications.

In this digest, you will find NRC news releases announcing licensing decisions (including license issuances, renewals, or modifications), inspection findings, enforcement actions such as violations and civil penalties, security updates, and statements on significant regulatory matters. The releases reflect the agency's role as a technical regulator and the public-record basis for its licensing and oversight decisions. Readers will see a mix of routine regulatory items and announcements of particular significance to the nuclear industry, reactor operators, and the public.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nrc-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.nrc.gov/reading-rm/doc-collections/news/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. This index is not a release listing at all: it is a menu of year archives, and the only date on the page is 'Page Last Reviewed/Updated Tuesday, January 06, 2026' in the footer. The adapter returns nothing, which is correct — stamping the footer date onto 164 links would have been the worst available answer. Reaching NRC releases means following the per-year pages, a second request tier this adapter does not do. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: https://www.nrc.gov/public-involve/rss?feed=news returned an HTTP error. The site advertises RSS from its page body; the working URL was not found this pass. Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

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

No requests to www.nrc.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

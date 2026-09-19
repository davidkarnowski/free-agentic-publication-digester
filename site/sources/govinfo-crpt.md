<!-- Markdown twin of https://fapd.info/sources/govinfo-crpt.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-crpt.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-crpt)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Congressional Reports (CRPT)

planned · Legislative · Tier 1 · govinfo collection · U.S. Congress

Official site: https://www.govinfo.gov/app/collection/CRPT · All sources: [sources.md](../sources.md)

## What this source is

House, Senate, and conference committees report legislation with written analyses. This collection carries committee reports — a committee's explanation of a bill's purpose, provisions, and cost — published through the Government Publishing Office as bills advance.

**Model-written orientation**

Congressional Reports contains written analyses and recommendations from House, Senate, and conference committees, published by the Government Publishing Office as legislation advances through Congress.

Congressional Reports are the official explanations that accompany bills as they move through Congress. When a committee reports (votes to send forward) a bill, the committee typically produces a written report explaining the bill's purpose, summarizing its major provisions, discussing the committee's reasoning, and noting the estimated fiscal impact. These reports are published through the Government Publishing Office alongside the bills they explain and serve as part of the official legislative history.

Reports occupy an important place in legislative analysis and interpretation. When courts or agencies need to understand Congress's intent for a statute, they refer to committee reports as the authoritative guide to what Congress meant to accomplish. Reports often discuss specific provisions in detail, flag concerns the committee considered and rejected, and note compromises made during markup. For this reason, committee reports are studied alongside bill text to understand the full legislative record.

However, the collection faces a significant constraint: many reports in the Government Publishing Office collection date to earlier decades and represent retrospective digitization of older congressional records. The collection includes reports from ongoing legislation, but the bulk of what appears in the collection at any given time represents scanning and publication of historical congressional records—some dating back decades—rather than current committee work. When probed recently, the collection showed that most of what was changing were older reports being newly published through retrospective digitization, rather than new reports from current legislative activity. Reports actually dated within the current week appear rarely.

Within the congressional structure, reports are produced by committees in both chambers and by conference committees when a bill proceeds to conference. They are published through the Government Publishing Office as structured text, indexed by committee, bill number, and date of publication.

In this digest, readers would encounter congressional reports explaining current legislation under consideration or recently passed. However, because publication substantially lags committee action, and because much of the collection consists of retrospective digitization of older materials, the digest currently does not include this source. Reports on current legislation often reach official publication long after the legislative action they explain.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-crpt` |
| Agency / parent organization | U.S. Congress |
| Branch | legislative |
| Type | govinfo collection |
| Status | planned |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/CRPT |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-31 through the govinfo API: of 200 packages changed in the trailing 21 days, the newest dateIssued is 1971-01-02 — they are SERIALSET digitisation of 1970-71 committee reports, not current ones. Zero packages dated within 7 days. What changes daily in this collection is retrospective scanning, so under the §3 dating rule it would contribute nothing to a current digest. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | govinfo collection |
| Method | Would sync via the govinfo collections API delta mechanism once enabled (GUIDE §7 Phase 4). |
| Request budget | the govinfo class: at most 6,000 requests per day and 800 per hour, counted from the fetch log (failed requests count too); collectors stop at 85% so the end-of-day finalizer always has headroom |
| Politeness | keyed govinfo API access; every request is logged before it is made and identified as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com) |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 111,295 request(s) · 84,563 answered · 26,732 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-21 | 0 | 2575 | 641 |
| 2026-08-22 | 0 | 2230 | 527 |
| 2026-08-23 | 0 | 2174 | 685 |
| 2026-08-24 | 0 | 1196 | 610 |
| 2026-08-25 | 0 | 1486 | 466 |
| 2026-08-26 | 0 | 2746 | 598 |
| 2026-08-27 | 0 | 2316 | 546 |
| 2026-08-28 | 0 | 2828 | 708 |
| 2026-08-29 | 0 | 2370 | 457 |
| 2026-08-30 | 0 | 2332 | 708 |
| 2026-08-31 | 0 | 1152 | 622 |
| 2026-09-01 | 0 | 1519 | 615 |
| 2026-09-02 | 0 | 2874 | 563 |
| 2026-09-03 | 0 | 2621 | 684 |
| 2026-09-04 | 0 | 2327 | 640 |
| 2026-09-05 | 0 | 1838 | 485 |
| 2026-09-06 | 0 | 2034 | 676 |
| 2026-09-07 | 0 | 1120 | 598 |
| 2026-09-08 | 0 | 794 | 451 |
| 2026-09-09 | 0 | 1513 | 522 |
| 2026-09-10 | 0 | 1782 | 695 |
| 2026-09-11 | 0 | 2005 | 714 |
| 2026-09-12 | 0 | 2319 | 594 |
| 2026-09-13 | 0 | 1408 | 576 |
| 2026-09-14 | 0 | 780 | 843 |
| 2026-09-15 | 0 | 1504 | 812 |
| 2026-09-16 | 0 | 2266 | 580 |
| 2026-09-17 | 0 | 2387 | 608 |
| 2026-09-18 | 0 | 2655 | 746 |
| 2026-09-19 | 0 | 5 | 200 |

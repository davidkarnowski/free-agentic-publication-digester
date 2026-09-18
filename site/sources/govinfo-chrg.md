<!-- Markdown twin of https://fapd.info/sources/govinfo-chrg.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-chrg.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-chrg)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Congressional Hearings (CHRG)

planned · Legislative · Tier 1 · govinfo collection · U.S. Congress

Official site: https://www.govinfo.gov/app/collection/CHRG · All sources: [sources.md](../sources.md)

## What this source is

Congressional committees publish their hearing records through the Government Publishing Office. This collection carries printed hearing transcripts — witness testimony and member questioning — released weeks to months after the hearing date.

**Model-written orientation**

Congressional Hearings contains printed hearing transcripts from House and Senate committees, published by the Government Publishing Office weeks to months after hearings occur.

Congressional Hearings collects the official printed records of committee hearings in the House and Senate. When a committee holds a hearing—bringing witnesses before the committee for questioning—the committee produces a printed record containing the opening statements, witness testimony, and member questioning. These transcripts are published through the Government Publishing Office as part of the congressional record.

Hearings serve an important role in the legislative process. They provide a formal forum for committees to gather expert testimony, hear from affected stakeholders, and build a record justifying future legislative action. The hearing transcript becomes part of the legislative history—a permanent record of what was said, who testified, and what questions members posed. Courts and legal analysts refer to hearing transcripts to understand Congress's intent when interpreting ambiguous statutory language.

However, hearings reach publication through the Government Publishing Office with substantial delay. Committees must produce and edit transcripts, proofread testimony, and submit the final version to the Government Publishing Office for publishing. This process typically takes weeks to several months after the hearing occurs. Because of this publication lag, hearing transcripts dated within the current week are rarely available, and most of what appears in the collection at any given time are older hearings—sometimes dating back months or years—that are reaching publication only now.

Within the legislative process, hearings sit upstream of bills. A committee may hold hearings on a topic, then later introduce legislation based on what was heard. Hearings thus provide context for understanding why Congress decided to act and what problems it aimed to address. However, the delayed publication means hearings often reach official publication long after any resulting legislation has passed.

The collection is maintained by the Government Publishing Office and is updated as new hearing transcripts arrive from committees. Each hearing is published as structured text, indexed by committee, date of the hearing (as held, not as published), and topic.

In this digest, readers would encounter hearing transcripts only after substantial delay—a hearing held today might not appear in the digest for many weeks or months. For this reason, the digest currently does not include this source; hearings are noted as an available record but do not appear as current material.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-chrg` |
| Agency / parent organization | U.S. Congress |
| Branch | legislative |
| Type | govinfo collection |
| Status | planned |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/CHRG |
| Registered | 2026-07-26 |
| Registry notes | Publication lag means hearing transcripts are not day-shaped; date semantics need a rule before activation. Probed 2026-07-31 through the govinfo API: newest dateIssued 2026-06-30, a 31-day lag, and the packages actually changing day to day are dated 2024-2025. Zero dated within 7 days. Hearings are substantive but reach govinfo long after the hearing, so under the §3 dating rule they would not land on a current digest day. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | govinfo collection |
| Method | Would sync via the govinfo collections API delta mechanism once enabled (GUIDE §7 Phase 4). |
| Request budget | the govinfo class: at most 6,000 requests per day and 500 per hour, counted from the fetch log (failed requests count too); collectors stop at 85% so the end-of-day finalizer always has headroom |
| Politeness | keyed govinfo API access; every request is logged before it is made and identified as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com) |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 108,867 request(s) · 82,528 answered · 26,339 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-20 | 0 | 2954 | 594 |
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
| 2026-09-18 | 0 | 232 | 561 |

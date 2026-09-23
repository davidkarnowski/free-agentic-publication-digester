<!-- Markdown twin of https://fapd.info/sources/govinfo-bulkdata.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-bulkdata.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-bulkdata)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# govinfo Bulk Data

planned · Cross-branch · Tier 1 · govinfo collection · U.S. Government Publishing Office

Official site: https://www.govinfo.gov/bulkdata · All sources: [sources.md](../sources.md)

## What this source is

The Government Publishing Office operates a bulk-data repository alongside the govinfo API. It serves complete XML directory trees for BILLS, the Federal Register, the Congressional Record, CFR/eCFR, and bill status — the intended channel for multi-day historical backfills rather than item-by-item API calls.

**Model-written orientation**

The Government Publishing Office maintains a bulk-data repository containing XML archives for federal legislative records, regulatory documents, and congressional materials. This channel provides structured historical datasets rather than individual items.

The Government Publishing Office (GPO) is the federal government's official printing and publishing agency and operates govinfo as the official digital repository for federal government documents and information. GPO's mission includes ensuring public access to federal government information and publications. Alongside the item-by-item govinfo API, which is designed for accessing individual documents and recent updates, GPO operates a bulk-data service that provides a different access pattern.

The bulk-data repository contains complete XML directory trees representing comprehensive archives of major federal publications. These include legislative bills and enacted laws in their authoritative XML formats, Federal Register publications covering all regulatory notices and rules from federal agencies, Congressional Record proceedings containing the complete text of congressional debate and proceedings, the Code of Federal Regulations (CFR) and the electronic CFR (eCFR) representing all codified federal regulations, and bill status information tracking the legislative history and current status of bills in Congress.

The bulk-data channel is specifically designed for comprehensive historical backfills and research spanning multiple days, weeks, or longer periods. It is the preferred approach when accessing large volumes of federal legislative or regulatory data from a specified date range, in contrast to the item-by-item API which suits ongoing daily ingestion and updates of newly published items. The repository provides data in structured, machine-readable XML format that enables systematic analysis and research across federal legislative and regulatory materials.

Access to the bulk-data service typically requires off-peak timing to avoid affecting the GPO's live services and throttled request rates to respect service constraints. The repository serves researchers, analysts, and organizations conducting government information analysis, legislative tracking, and regulatory monitoring.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-bulkdata` |
| Agency / parent organization | U.S. Government Publishing Office |
| Branch | cross-branch |
| Type | govinfo collection |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.govinfo.gov/bulkdata |
| Registered | 2026-07-26 |
| Registry notes | Preferred over the API for any backfill of more than a few days (GUIDE §4); run off-peak, throttled. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | govinfo collection |
| Method | bulk XML for historical backfill |
| Request budget | the govinfo class: at most 6,000 requests per day and 800 per hour, counted from the fetch log (failed requests count too); collectors stop at 85% so the end-of-day finalizer always has headroom |
| Politeness | keyed govinfo API access; every request is logged before it is made and identified as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com) |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 117,897 request(s) · 89,445 answered · 28,452 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
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
| 2026-09-19 | 0 | 2032 | 655 |
| 2026-09-20 | 0 | 963 | 682 |
| 2026-09-21 | 0 | 981 | 482 |
| 2026-09-22 | 0 | 1687 | 630 |
| 2026-09-23 | 0 | 944 | 356 |

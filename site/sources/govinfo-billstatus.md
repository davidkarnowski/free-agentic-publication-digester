<!-- Markdown twin of https://fapd.info/sources/govinfo-billstatus.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-billstatus.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-billstatus)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# GPO Bulk Data — BILLSTATUS

planned · Legislative · Tier 1 · bulk data · Government Publishing Office

Official site: https://github.com/usgpo/bill-status · All sources: [sources.md](../sources.md)

## What this source is

GPO's bulk-data service publishes per-bill status XML — actions, committee referrals and activities, cosponsors, amendment actions, veto records — refreshed every 4 hours for the current Congress. Richer and timelier bill-action data than the BILLS text printings.

**Model-written orientation**

The Government Publishing Office publishes per-bill status XML files containing bill actions, committee activities, cosponsors, amendments, and veto records, updated every four hours for the current Congress.

The Government Publishing Office (GPO) is the official publisher of federal documents. The GPO maintains govinfo.gov, the official repository of federal legislative, executive, and judicial documents.

Beyond govinfo.gov's main portal, the GPO operates a bulk-data service that publishes document collections in machine-readable formats. One collection in the bulk-data service is BILLSTATUS, which contains per-bill status XML files for every bill and resolution in the current Congress.

Each BILLSTATUS file contains comprehensive information about one bill: its actions (introduction, committee referral, votes, passage, etc.), its committee referrals and committee activities, the list of cosponsors and how that list has changed over time, amendments and amendment actions, any veto records, and related procedural information. The files are structured XML that can be processed by automated systems.

The GPO updates the BILLSTATUS collection on a regular schedule: every four hours for bills in the current Congress, and daily for bills from prior Congresses. This makes BILLSTATUS both comprehensive and relatively current for recently-acted-upon bills.

The BILLSTATUS collection is richer than the bill-text collections govinfo publishes. It provides action histories and metadata that text collections do not include, and it updates more frequently than full text. The bulk-data service uses the same infrastructure and security model that the FAPD pipeline already uses for other govinfo sources.

This source is valuable for readers and systems tracking bill status and congressional activity. It provides timely, comprehensive, and structured access to bill actions and metadata across the current Congress, complementing other legislative sources by offering richer historical and amendment data.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-billstatus` |
| Agency / parent organization | Government Publishing Office |
| Branch | legislative |
| Type | bulk data |
| Status | planned |
| Tier | 1 |
| URL (feed) | https://www.govinfo.gov/rss/billstatus-batch.xml |
| URL (home) | https://github.com/usgpo/bill-status |
| URL (index) | https://www.govinfo.gov/bulkdata/BILLSTATUS |
| Registered | 2026-07-28 |
| Registry notes | User guide read on the official usgpo GitHub 2026-07-28: current-Congress job every 4 hours, prior Congresses daily. Same GPO infrastructure our govinfo client already trusts. Negative finding recorded: bulkdata carries NO CHRG or CRPT — committee hearings/reports remain govinfo API collections. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | bulk data |
| Method | Would watch the batch-completion RSS and sitemap index, then fetch changed status XML from the bulkdata directory (append /xml for machine-readable listings). |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.govinfo.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

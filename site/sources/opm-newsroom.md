<!-- Markdown twin of https://fapd.info/sources/opm-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/opm-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: opm-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# OPM News Releases

planned · Executive · Tier 1 · HTML index · Independent agency

Official site: https://www.opm.gov/news/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of Personnel Management sets federal civilian workforce policy and administers federal employee benefits. Its newsroom index carries releases on hiring policy, pay, and benefits programs, typically a few items per week.

**Model-written orientation**

The Office of Personnel Management sets policy for the federal civilian workforce and administers federal employee benefits. Its newsroom publishes releases on hiring policy, compensation, and benefits programs, typically several items per week.

The Office of Personnel Management (OPM) is an independent agency that serves as the chief human resources agency of the federal government. OPM establishes policy for federal civilian workforce management, administers the federal employee benefits programs, operates the civil service hiring system, and provides oversight of federal personnel management across the executive branch. The agency employs roughly 2,000 staff and serves as the steward of federal human resources policy affecting more than two million federal civilian employees.

OPM's primary responsibilities include administering federal employee health insurance programs, retirement and pension systems, life insurance and other benefits, and federal employee compensation policy. The agency also maintains the civil service rules that govern federal hiring, promotion, discipline, and other employment matters. OPM provides guidance to agencies on personnel policies, manages federal background investigation operations, and oversees federal employee training and development.

The OPM newsroom serves as the agency's official channel for announcing policy updates, program changes, and administrative decisions. Readers will encounter releases on federal hiring procedures and policy changes affecting how federal jobs are announced and filled; announcements related to federal employee compensation, including changes to pay scales, locality adjustments, and federal pay raises; news about federal employee benefits programs, including changes to health insurance plans, retirement program updates, and other benefits; and notices about federal employment policies, personnel regulations, and federal workforce management initiatives.

Content is typically released several items per week and focuses on OPM's regulatory and administrative responsibilities for the federal workforce. Readers can expect announcements that directly affect federal employees and federal hiring processes.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `opm-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.opm.gov/news/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 109 article link(s); 0 dated inside the 7-day lookback, 0 dated outside it, 109 skipped for no readable date — the served HTML states no per-entry publication date, so every entry is skipped rather than dated by observation. This is a script-rendered listing; opening it needs evidence of a dated channel, not a cadence decision. |

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

No requests to www.opm.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

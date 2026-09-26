<!-- Markdown twin of https://fapd.info/sources/uscourts-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/uscourts-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: uscourts-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# U.S. Courts News

active · ingestion health: quiet · Judicial · Tier 2 · RSS feed · Administrative Office of the U.S. Courts

Official site: https://www.uscourts.gov/data-news/judiciary-news · All sources: [sources.md](../sources.md)

## What this source is

The Administrative Office of the U.S. Courts supports the federal judiciary's administration. Its news index on uscourts.gov carries articles on judiciary operations, rulemaking, and Judicial Conference actions, typically a few items per week.

**Model-written orientation**

The Administrative Office of the U.S. Courts publishes news about federal judiciary operations, rulemaking, and governance decisions.

The United States federal judiciary operates through a complex administrative structure that supports the federal courts and judges across the country. The Administrative Office of the U.S. Courts (AO), a statutory agency created to provide administrative support to the federal judiciary, maintains a public news feed about the operations and governance of the federal court system.

The AO coordinates administrative services that enable the federal courts to function, including budget and financial management, personnel administration, procurement, and information systems support. As the administrative center of the judiciary, the AO publishes announcements and information about how the federal court system operates.

The news feed covers several categories of information. One category includes announcements from the Judicial Conference of the United States, the policy-making body of the federal judiciary. Another includes information about rulemaking—the process by which rules governing federal court procedures are developed and amended. The AO also publishes updates on administrative initiatives, personnel matters affecting the judiciary, statistics and reports about court operations, and other announcements related to how the federal court system functions.

The feed typically produces a few items per week. Items in this digest come from the AO's official news feed and reflect the AO's own publications about judiciary administration. The feed focuses on the machinery of the courts—how they operate and are governed—rather than individual cases or court decisions.

This source is valuable for readers interested in understanding how the federal court system is administered, how procedural rules are developed, and major governance decisions affecting the judiciary as an institution. The source covers an area of federal activity that the pipeline does not otherwise include.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `uscourts-news` |
| Agency / parent organization | Administrative Office of the U.S. Courts |
| Branch | judicial |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | http://news.uscourts.gov/feed |
| URL (home) | https://www.uscourts.gov/data-news/judiciary-news |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 404 — the site had moved, not blocked. Re-probed 2026-07-28 at the documented feed (news.uscourts.gov/feed, from uscourts.gov's official RSS page): verified end-to-end — 10 items, ~174-char descriptions, sample article extracted from the relocated index host. Covers AO announcements, Judicial Conference actions, and rulemaking — judiciary administration previously uncovered. Content evaluation: a few items/week; 10-item depth ample. Activated 2026-07-28. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the documented Judiciary News RSS feed via AgencyClient. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**quiet** — Most recent item 2026-09-17, 9 days ago (quiet past 7 days).

This label has held since 2026-09-25T04:26:06Z (UTC) and was last re-checked 2026-09-26T04:03:22Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-09-17 |
| Content length | 23,342 characters average, 23,342 median (shortest 23,342, longest 23,342) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to news.uscourts.gov | 346 request(s) · 346 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-26T04:07:58.970+00:00 UTC.

Most recent item 2026-09-17, 9 days ago (quiet past 7 days).

### All time

- **Our requests to news.uscourts.gov, all time (since 2026-07-30):** 1,675 request(s) · 1,674 answered · 1 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to news.uscourts.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-28 | 0 | 26 | 385 |
| 2026-08-29 | 0 | 27 | 376 |
| 2026-08-30 | 0 | 28 | 434 |
| 2026-08-31 | 0 | 26 | 357 |
| 2026-09-01 | 0 | 26 | 344 |
| 2026-09-02 | 0 | 26 | 547 |
| 2026-09-03 | 0 | 26 | 882 |
| 2026-09-04 | 0 | 26 | 429 |
| 2026-09-05 | 0 | 33 | 606 |
| 2026-09-06 | 0 | 26 | 369 |
| 2026-09-07 | 0 | 26 | 408 |
| 2026-09-08 | 0 | 26 | 743 |
| 2026-09-09 | 1 | 26 | 341 |
| 2026-09-10 | 0 | 26 | 314 |
| 2026-09-11 | 0 | 26 | 325 |
| 2026-09-12 | 0 | 29 | 541 |
| 2026-09-13 | 0 | 26 | 462 |
| 2026-09-14 | 0 | 30 | 606 |
| 2026-09-15 | 0 | 27 | 1062 |
| 2026-09-16 | 0 | 26 | 359 |
| 2026-09-17 | 1 | 26 | 390 |
| 2026-09-18 | 0 | 26 | 446 |
| 2026-09-19 | 0 | 26 | 355 |
| 2026-09-20 | 0 | 26 | 361 |
| 2026-09-21 | 0 | 29 | 483 |
| 2026-09-22 | 0 | 25 | 1011 |
| 2026-09-23 | 0 | 25 | 374 |
| 2026-09-24 | 0 | 26 | 350 |
| 2026-09-25 | 0 | 25 | 409 |
| 2026-09-26 | 0 | 3 | 219 |

## Our ingestion assessment

**Model-written ingestion assessment**

The U.S. Courts News source is ingested by polling its RSS feed and retrieving the full article text from each item's linked page. Over the past 14 days, we observed 1 new item, averaging 0.07 items per day. This rate represents a decrease from the 0.14 items per day reported in the previous assessment. The most recent item was delivered on 2026-09-17, resulting in 9 days without new content and a current "quiet" health status. The single observed item in this period measured 23,342 characters, consistent with the average of 20,842 characters previously reported for full-text articles. All 346 polling requests to news.uscourts.gov were answered successfully with a 0.0% error rate, an improvement from the 0.3% error rate noted in the prior period that included a transient error. No consecutive errors were recorded by the collector.

_Model-written assessment of our own ingestion, generated 2026-09-26 by gemini-2.5-flash, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/uscourts-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/uscourts-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: uscourts-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# U.S. Courts News

active · ingestion health: delivering · Judicial · Tier 2 · RSS feed · Administrative Office of the U.S. Courts

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

**delivering** — 2 item(s) in the last 14 days; most recent 2026-09-17; 1 of 354 request(s) to news.uscourts.gov returned no content.

This label has held since 2026-09-17T17:40:18Z (UTC) and was last re-checked 2026-09-18T03:55:01Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-09-17 |
| Content length | 20,842 characters average, 20,842 median (shortest 18,341, longest 23,342) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to news.uscourts.gov | 354 request(s) · 353 answered · 0 declined (4xx) · 0 server declined (5xx) · 1 no response — 0.3% returned no content |

last answered request 2026-09-18T04:20:15.828+00:00 UTC.

2 item(s) in the last 14 days; most recent 2026-09-17; 1 of 354 request(s) to news.uscourts.gov returned no content.

### All time

- **Our requests to news.uscourts.gov, all time (since 2026-07-30):** 1,465 request(s) · 1,464 answered · 1 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to news.uscourts.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-20 | 0 | 34 | 512 |
| 2026-08-21 | 0 | 29 | 349 |
| 2026-08-22 | 0 | 30 | 408 |
| 2026-08-23 | 0 | 29 | 399 |
| 2026-08-24 | 0 | 28 | 456 |
| 2026-08-25 | 0 | 26 | 397 |
| 2026-08-26 | 0 | 25 | 384 |
| 2026-08-27 | 1 | 26 | 449 |
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
| 2026-09-18 | 0 | 1 | 315 |

## Our ingestion assessment

**Model-written ingestion assessment**

The U.S. Courts News RSS feed continues delivering judiciary administration announcements via RSS. Over the 14-day measurement window, two items arrived on 2026-09-09 and 2026-09-17, bringing the average to 0.14 items per day—a doubling of the previous 0.07 items per day rate. Extracted full-text articles from news.uscourts.gov averaged 20,842 characters. Of 354 total requests to the feed, 353 succeeded; one request returned no content, yielding a 0.3% error rate—a minor departure from the zero-error rate recorded in the previous assessment. One hour (2026-09-12 16:00 UTC) recorded a transient error during otherwise consistent daily polling across the measurement period. The source's intermittent publication schedule persists, consistent with typical judiciary administration announcement patterns.

_Model-written assessment of our own ingestion, generated 2026-09-18 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

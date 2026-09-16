<!-- Markdown twin of https://fapd.info/sources/federal-reserve-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/federal-reserve-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: federal-reserve-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Reserve Press Releases

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Independent agency

Official site: https://www.federalreserve.gov/newsevents/pressreleases.htm · All sources: [sources.md](../sources.md)

## What this source is

The Board of Governors of the Federal Reserve System conducts monetary policy and regulates bank holding companies. This RSS feed carries all board press releases — FOMC statements, monetary-policy actions, banking regulation, and enforcement — as title-plus-teaser items (20 recent, ~110 characters of description; article pages extract at ~10,000 characters).

**Model-written orientation**

The Federal Reserve's Board of Governors conducts monetary policy and regulates bank holding companies; this feed carries press releases on FOMC statements, policy actions, and banking regulation.

The Federal Reserve System is the nation's central banking system, with the Board of Governors serving as its primary policymaking body based in Washington, D.C. The Board's main responsibilities are conducting monetary policy through the Federal Open Market Committee (FOMC) and supervising bank holding companies. The FOMC meets regularly to set interest-rate targets and determine strategies to influence the money supply and economic activity.

This feed publishes all press releases from the Board of Governors, making it the official channel for announcing monetary-policy decisions, supervisory actions, and regulatory guidance. FOMC statements—the most prominent releases—explain the Committee's interest-rate decisions, economic assessments, and future policy intentions. The feed also includes announcements on banking supervision, regulatory changes, enforcement actions against regulated institutions, and compliance guidance for banks.

Feed items consist of a title and brief description (typically about 110 characters), with full-text articles averaging around 10,000 characters. The feed displays the 20 most recent releases. Publication frequency varies with the FOMC schedule and regulatory developments, typically resulting in a few releases per week, though frequency can increase during policy shifts or financial-market conditions.

Readers will find FOMC policy statements, supervisory guidance and rule changes affecting regulated institutions, enforcement actions, statements on banking-system conditions, and other official Board communications. All releases represent official Board positions and carry institutional authority. The feed serves as the authoritative source for the Board's monetary-policy announcements and supervisory decisions.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `federal-reserve-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.federalreserve.gov/feeds/press_all.xml |
| URL (home) | https://www.federalreserve.gov/newsevents/pressreleases.htm |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 20 items, avg description 109 chars, sample article extracted (10066 chars text). Email sibling registered 2026-07-29: federal-reserve-email (GUIDE §3 email class; the web status here is unchanged). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | RSS poll via AgencyClient (pending content evaluation) |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 3 item(s) in the last 14 days; most recent 2026-09-11; 15 of 355 request(s) to www.federalreserve.gov returned no content.

This label has held since 2026-09-04T15:32:05Z (UTC) and was last re-checked 2026-09-16T04:00:04Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (24 answered, 1 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-09-11 |
| Content length | 10,317 characters average, 10,452 median (shortest 9,338, longest 11,161) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.federalreserve.gov | 355 request(s) · 340 answered · 15 declined (4xx) · 0 server declined (5xx) · 0 no response — 4.2% returned no content |

last answered request 2026-09-16T04:14:23.811+00:00 UTC.

3 item(s) in the last 14 days; most recent 2026-09-11; 15 of 355 request(s) to www.federalreserve.gov returned no content.

### All time

- **Our requests to www.federalreserve.gov, all time (since 2026-07-30):** 1,428 request(s) · 1,348 answered · 80 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.federalreserve.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-18 | 0 | 28 | 125 |
| 2026-08-19 | 1 | 25 | 103 |
| 2026-08-20 | 3 | 37 | 162 |
| 2026-08-21 | 0 | 29 | 104 |
| 2026-08-22 | 0 | 29 | 100 |
| 2026-08-23 | 0 | 30 | 109 |
| 2026-08-24 | 0 | 27 | 111 |
| 2026-08-25 | 1 | 27 | 87 |
| 2026-08-26 | 0 | 26 | 90 |
| 2026-08-27 | 1 | 27 | 113 |
| 2026-08-28 | 0 | 25 | 91 |
| 2026-08-29 | 0 | 27 | 98 |
| 2026-08-30 | 0 | 26 | 115 |
| 2026-08-31 | 0 | 25 | 107 |
| 2026-09-01 | 0 | 26 | 115 |
| 2026-09-02 | 0 | 26 | 74 |
| 2026-09-03 | 0 | 26 | 88 |
| 2026-09-04 | 1 | 27 | 110 |
| 2026-09-05 | 0 | 33 | 199 |
| 2026-09-06 | 0 | 26 | 107 |
| 2026-09-07 | 0 | 25 | 98 |
| 2026-09-08 | 0 | 26 | 92 |
| 2026-09-09 | 0 | 26 | 102 |
| 2026-09-10 | 1 | 27 | 125 |
| 2026-09-11 | 1 | 27 | 102 |
| 2026-09-12 | 0 | 29 | 151 |
| 2026-09-13 | 0 | 27 | 215 |
| 2026-09-14 | 0 | 29 | 245 |
| 2026-09-15 | 0 | 26 | 102 |
| 2026-09-16 | 0 | 1 | 142 |

## Our ingestion assessment

**Model-written ingestion assessment**

The RSS feed delivers board press releases with teaser descriptions and full article extraction. Over 14 days, 3 items arrived at 0.21 per day, a slight decline from the previous 0.29 per day. Extracted text averaged 9,220 characters. Our requests to www.federalreserve.gov returned a 3.8% error rate across 346 attempts, with 13 client errors; the previous period showed a 3.2% error rate. The most recent item was published on 2026-09-04. Publication rate remains infrequent, with individual items substantial in scope.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

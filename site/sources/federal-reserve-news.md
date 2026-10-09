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

**delivering** — 8 item(s) in the last 14 days; most recent 2026-10-08; 8 of 346 request(s) to www.federalreserve.gov returned no content.

This label has held since 2026-09-04T15:32:05Z (UTC) and was last re-checked 2026-10-09T03:52:22Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 8 in 14 days (0.57 per day) · most recent 2026-10-08 |
| Content length | 9,768 characters average, 9,386 median (shortest 8,959, longest 12,457) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.federalreserve.gov | 346 request(s) · 338 answered · 8 declined (4xx) · 0 server declined (5xx) · 0 no response — 2.3% returned no content |

last answered request 2026-10-09T04:00:10.520+00:00 UTC.

8 item(s) in the last 14 days; most recent 2026-10-08; 8 of 346 request(s) to www.federalreserve.gov returned no content.

### All time

- **Our requests to www.federalreserve.gov, all time (since 2026-07-30):** 1,957 request(s) · 1,941 answered · 16 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.federalreserve.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-10 | 1 | 26 | 122 |
| 2026-09-11 | 1 | 26 | 101 |
| 2026-09-12 | 0 | 28 | 147 |
| 2026-09-13 | 0 | 26 | 218 |
| 2026-09-14 | 0 | 28 | 228 |
| 2026-09-15 | 0 | 25 | 99 |
| 2026-09-16 | 2 | 28 | 115 |
| 2026-09-17 | 0 | 25 | 92 |
| 2026-09-18 | 2 | 27 | 130 |
| 2026-09-19 | 0 | 25 | 87 |
| 2026-09-20 | 0 | 26 | 77 |
| 2026-09-21 | 0 | 27 | 179 |
| 2026-09-22 | 1 | 27 | 104 |
| 2026-09-23 | 0 | 24 | 110 |
| 2026-09-24 | 2 | 27 | 114 |
| 2026-09-25 | 1 | 26 | 107 |
| 2026-09-26 | 0 | 26 | 146 |
| 2026-09-27 | 0 | 26 | 124 |
| 2026-09-28 | 0 | 27 | 150 |
| 2026-09-29 | 1 | 27 | 91 |
| 2026-09-30 | 1 | 26 | 96 |
| 2026-10-01 | 0 | 27 | 88 |
| 2026-10-02 | 3 | 29 | 88 |
| 2026-10-03 | 0 | 26 | 84 |
| 2026-10-04 | 0 | 25 | 98 |
| 2026-10-05 | 1 | 26 | 114 |
| 2026-10-06 | 0 | 27 | 88 |
| 2026-10-07 | 1 | 27 | 85 |
| 2026-10-08 | 1 | 26 | 83 |
| 2026-10-09 | 0 | 1 | 126 |

## Our ingestion assessment

**Model-written ingestion assessment**

Federal Reserve press releases arrive through an RSS feed with full article text extracted from linked pages. Over 14 days, 9 items accumulated at 0.64 per day, an increase from the previous 0.21 per day. Extracted text averaged 9,784 characters. Publication remains sparse; individual releases cover FOMC statements, monetary-policy actions, and banking regulation. Of 343 requests to www.federalreserve.gov, 336 succeeded; 7 returned no content for a 2.0% error rate. This represents a higher failure rate than the prior 3.8%, though item volume has improved. Most recent item published 2026-10-05.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

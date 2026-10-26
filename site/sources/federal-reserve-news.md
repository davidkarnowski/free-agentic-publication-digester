<!-- Markdown twin of https://fapd.info/sources/federal-reserve-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/federal-reserve-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: federal-reserve-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Reserve Press Releases

active · ingestion health: quiet · Executive · Tier 2 · RSS feed · Independent agency

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

**quiet** — Most recent item 2026-10-16, 10 days ago (quiet past 7 days).

This label has held since 2026-10-24T04:12:35Z (UTC) and was last re-checked 2026-10-26T12:04:27Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-10-16 |
| Content length | 9,316 characters average, 9,316 median (shortest 9,258, longest 9,373) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.federalreserve.gov | 339 request(s) · 337 answered · 2 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.6% returned no content |

last answered request 2026-10-26T11:45:14.431+00:00 UTC.

Most recent item 2026-10-16, 10 days ago (quiet past 7 days).

### All time

- **Our requests to www.federalreserve.gov, all time (since 2026-07-30):** 2,398 request(s) · 2,380 answered · 18 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.federalreserve.gov | Mean response time (ms) |
|---|---|---|---|
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
| 2026-10-09 | 1 | 26 | 90 |
| 2026-10-10 | 0 | 25 | 92 |
| 2026-10-11 | 0 | 27 | 90 |
| 2026-10-12 | 0 | 25 | 159 |
| 2026-10-13 | 1 | 26 | 83 |
| 2026-10-14 | 0 | 25 | 116 |
| 2026-10-15 | 0 | 26 | 97 |
| 2026-10-16 | 1 | 27 | 81 |
| 2026-10-17 | 0 | 25 | 75 |
| 2026-10-18 | 0 | 25 | 73 |
| 2026-10-19 | 0 | 25 | 82 |
| 2026-10-20 | 0 | 25 | 88 |
| 2026-10-21 | 0 | 25 | 58 |
| 2026-10-22 | 0 | 24 | 72 |
| 2026-10-23 | 0 | 26 | 85 |
| 2026-10-24 | 0 | 25 | 70 |
| 2026-10-25 | 0 | 26 | 83 |
| 2026-10-26 | 0 | 9 | 83 |

## Our ingestion assessment

**Model-written ingestion assessment**

Federal Reserve press releases arrive through an RSS feed with full article text fetched from linked pages, as feed summaries carry only brief teasers. Over the 14-day window, two items were ingested at 0.14 per day, a substantial decrease from the 0.64 per day recorded in the prior assessment. Extracted text averaged 9,316 characters. Of 330 requests to www.federalreserve.gov, 328 succeeded; two requests returned no content for a 0.6% error rate, improved from the 2.0% error rate previously reported. Most recent item published 2026-10-16, nine days ago.

_Model-written assessment of our own ingestion, generated 2026-10-25 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

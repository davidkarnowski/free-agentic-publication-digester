<!-- Markdown twin of https://fapd.info/sources/defense-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/defense-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: defense-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Defense News Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Department of Defense

Official site: https://www.defense.gov/News/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of Defense directs the armed forces and military policy. This RSS feed carries its news releases and stories — operations, contracts, and personnel announcements — as title-only items (10 most recent; no description text), with full text only on article pages that block automated clients.

**Model-written orientation**

The Department of Defense publishes news releases on military operations, personnel, defense contracts, and military policy through an RSS feed, serving as the official channel for defense announcements.

The Department of Defense directs the armed forces and formulates military policy for the United States. The Defense Department's news-release channel serves as an official source for the public and press on matters within its purview: military operations, deployment announcements, defense contracts and procurement, personnel actions, strategic policy guidance, military technology development, and readiness assessments.

The department's organizational structure includes the Office of the Secretary of Defense, the Joint Chiefs of Staff, and the combatant commands—geographic and functional commands responsible for military operations in their areas. The news channel carries announcements from across these components, including statements on military exercises, equipment deployments, personnel appointments, contract awards to defense contractors, and policy announcements addressing military readiness or strategic matters.

Readers will encounter announcements on military operations and exercises, statements on military personnel (retirements of senior officers, promotions), contract awards and defense procurement decisions, technology and weapons development milestones, international military cooperation and joint exercises, and responses to developments requiring military comment. Releases typically include attribution to the specific component issuing the statement.

The news feed carries approximately ten most recent releases, updated regularly as new announcements are published. Titles and publication metadata are available through the feed, with full article text available on the department's website. Releases are published on a rolling basis, with volume varying based on operational tempo and policy priorities. During periods of active military operations or strategic transitions, the department may issue multiple releases per business day.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `defense-newsroom` |
| Agency / parent organization | Department of Defense |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=945&max=10 |
| URL (home) | https://www.defense.gov/News/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified — 10 items with GUIDs and dates, avg description 0 chars (title-only); sample article fetch returned HTTP 403: feed accessible; article pages blocked to identified clients — feed-only ingestion candidate. Feed item links resolve to www.war.gov. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Would poll the news-release RSS feed daily for new items. |
| Adapter | rss-feed-only |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 25 item(s) in the last 14 days; most recent 2026-10-30; 0 of 328 request(s) to www.defense.gov returned no content.

This label has held since 2026-08-11T18:00:02Z (UTC) and was last re-checked 2026-10-31T03:45:15Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 25 in 14 days (1.79 per day) · most recent 2026-10-30 |
| Content length | 303 characters average, 301 median (shortest 229, longest 377) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.defense.gov | 328 request(s) · 328 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-31T04:00:12.919+00:00 UTC.

25 item(s) in the last 14 days; most recent 2026-10-30; 0 of 328 request(s) to www.defense.gov returned no content.

### All time

- **Our requests to www.defense.gov, all time (since 2026-07-30):** 2,482 request(s) · 2,472 answered · 10 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.defense.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-02 | 3 | 26 | 284 |
| 2026-10-03 | 1 | 26 | 312 |
| 2026-10-04 | 0 | 24 | 281 |
| 2026-10-05 | 1 | 26 | 302 |
| 2026-10-06 | 4 | 27 | 352 |
| 2026-10-07 | 3 | 26 | 306 |
| 2026-10-08 | 3 | 26 | 347 |
| 2026-10-09 | 2 | 25 | 282 |
| 2026-10-10 | 0 | 26 | 269 |
| 2026-10-11 | 0 | 25 | 297 |
| 2026-10-12 | 0 | 26 | 312 |
| 2026-10-13 | 2 | 25 | 280 |
| 2026-10-14 | 2 | 24 | 280 |
| 2026-10-15 | 4 | 25 | 351 |
| 2026-10-16 | 2 | 26 | 242 |
| 2026-10-17 | 1 | 26 | 291 |
| 2026-10-18 | 0 | 25 | 274 |
| 2026-10-19 | 2 | 25 | 256 |
| 2026-10-20 | 4 | 25 | 450 |
| 2026-10-21 | 1 | 26 | 283 |
| 2026-10-22 | 2 | 25 | 271 |
| 2026-10-23 | 2 | 25 | 296 |
| 2026-10-24 | 0 | 25 | 277 |
| 2026-10-25 | 0 | 25 | 211 |
| 2026-10-26 | 2 | 25 | 220 |
| 2026-10-27 | 4 | 25 | 296 |
| 2026-10-28 | 3 | 25 | 379 |
| 2026-10-29 | 4 | 25 | 264 |
| 2026-10-30 | 1 | 26 | 309 |
| 2026-10-31 | 0 | 1 | 410 |

## Our ingestion assessment

**Model-written ingestion assessment**

The Defense News Releases RSS feed continues to deliver title-only item summaries from the defense.gov domain. Over the 14-day measurement window (October 6–12), we collected 27 feed items averaging 1.93 per day and 287 characters per item. Publication showed clustering in the first four days (12 items October 6–9) with no items in the final three days. Feed-only ingestion mode remains in effect, as full article text is not accessible to automated clients. Our polling produced 336 requests to www.defense.gov with 335 successful responses; one client error on October 6 represents a 0.3% failure rate, substantially improved from the previous measurement period's 5.6% error rate. The most recent item dates to October 9.

_Model-written assessment of our own ingestion, generated 2026-10-12 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

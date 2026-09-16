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

**delivering** — 22 item(s) in the last 14 days; most recent 2026-09-15; 16 of 355 request(s) to www.defense.gov returned no content.

This label has held since 2026-08-11T18:00:02Z (UTC) and was last re-checked 2026-09-16T04:00:04Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (24 answered, 1 returned no content) · 3 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 22 in 14 days (1.57 per day) · most recent 2026-09-15 |
| Content length | 269 characters average, 278 median (shortest 154, longest 380) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.defense.gov | 355 request(s) · 339 answered · 13 declined (4xx) · 0 server declined (5xx) · 3 no response — 4.5% returned no content |

last answered request 2026-09-16T04:14:23.787+00:00 UTC.

22 item(s) in the last 14 days; most recent 2026-09-15; 16 of 355 request(s) to www.defense.gov returned no content.

### All time

- **Our requests to www.defense.gov, all time (since 2026-07-30):** 1,415 request(s) · 1,331 answered · 84 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.defense.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-18 | 5 | 27 | 394 |
| 2026-08-19 | 3 | 24 | 359 |
| 2026-08-20 | 2 | 34 | 519 |
| 2026-08-21 | 2 | 29 | 358 |
| 2026-08-22 | 0 | 30 | 551 |
| 2026-08-23 | 0 | 29 | 363 |
| 2026-08-24 | 2 | 28 | 439 |
| 2026-08-25 | 1 | 26 | 342 |
| 2026-08-26 | 6 | 26 | 345 |
| 2026-08-27 | 2 | 26 | 359 |
| 2026-08-28 | 3 | 25 | 382 |
| 2026-08-29 | 0 | 27 | 332 |
| 2026-08-30 | 0 | 26 | 462 |
| 2026-08-31 | 1 | 26 | 351 |
| 2026-09-01 | 2 | 26 | 345 |
| 2026-09-02 | 4 | 30 | 628 |
| 2026-09-03 | 3 | 29 | 1270 |
| 2026-09-04 | 3 | 26 | 466 |
| 2026-09-05 | 0 | 33 | 557 |
| 2026-09-06 | 0 | 27 | 383 |
| 2026-09-07 | 0 | 26 | 331 |
| 2026-09-08 | 4 | 26 | 340 |
| 2026-09-09 | 3 | 26 | 295 |
| 2026-09-10 | 1 | 26 | 335 |
| 2026-09-11 | 4 | 25 | 350 |
| 2026-09-12 | 0 | 29 | 542 |
| 2026-09-13 | 0 | 26 | 472 |
| 2026-09-14 | 1 | 29 | 792 |
| 2026-09-15 | 3 | 26 | 316 |
| 2026-09-16 | 0 | 1 | 259 |

## Our ingestion assessment

**Model-written ingestion assessment**

The feed continues to deliver title-only summaries at roughly 1.5 items per day, slightly lower than the prior measurement of 2 per day. Over 14 days we observed 21 items, averaging 278 characters per item. Article pages remain inaccessible to automated clients, so our ingestion is feed-only. Of 355 requests to www.defense.gov, 20 returned no content—a 5.6% error rate, improved from 9.8% in the prior period. Request failures occur sporadically throughout each day with no persistent pattern. The source remains consistently reachable, with the most recent item published on 2026-09-10.

_Model-written assessment of our own ingestion, generated 2026-09-11 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

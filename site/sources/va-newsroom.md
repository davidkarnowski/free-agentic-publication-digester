<!-- Markdown twin of https://fapd.info/sources/va-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/va-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: va-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# VA News Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Department of Veterans Affairs

Official site: https://news.va.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of Veterans Affairs provides health care, benefits, and memorial services to veterans. This WordPress feed carries VA news releases and feature stories with teaser-length descriptions (30 most recent items, ~140 characters each; article pages extract at ~6,000 characters).

**Model-written orientation**

The Department of Veterans Affairs publishes news releases and feature stories on veterans benefits, health care programs, and veteran services.

The Department of Veterans Affairs (VA) is the federal executive agency responsible for providing health care, disability compensation, education benefits, home loan assistance, life insurance, burial benefits, and other services to veterans and their eligible family members. The VA operates the largest integrated health care system in the United States, with medical centers and clinics nationwide, and administers a portfolio of benefit and service programs serving millions of veterans.

Through its news site, the VA publishes press releases, announcements, and feature stories on departmental programs, policy changes, and initiatives affecting veterans. Readers will find content covering topics such as new or expanded benefits programs, benefits program changes and eligibility updates, health care facility announcements and service expansions, new initiatives to serve specific veteran populations or address veteran needs, policy implementations affecting veteran services, departmental leadership announcements, ceremony and commemoration announcements, and stories about individual veterans and VA programs.

The VA news content serves multiple audiences: veterans seeking information about available benefits and services, veterans organizations and advocates, government employees administering veterans benefits, and the broader public with an interest in veterans affairs. The feed includes both official press releases announcing policy or program changes and longer feature stories providing context about veterans' experiences and VA services. The content emphasizes official program information, eligibility details, implementation timelines, and statements from departmental leadership. Content dates reflect the VA's publisher-supplied publication dates for each release or story. The news site serves as the primary official channel for departmental announcements, though specific VA medical centers and regional offices also communicate program-level updates and local services through their own channels.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `va-newsroom` |
| Agency / parent organization | Department of Veterans Affairs |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://news.va.gov/feed/ |
| URL (home) | https://news.va.gov/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 30 items, avg description 144 chars, sample article extracted (6366 chars text). Sampled item was a feature story, not a press release — the feed mixes both; a content evaluation should decide filtering. Email sibling registered 2026-07-29: va-email (GUIDE §3 email class; the web status here is unchanged). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Would poll the VA news site RSS feed daily for new items. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 40 item(s) in the last 14 days; most recent 2026-10-06; 1 of 379 request(s) to news.va.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 30 request(s) (30 answered, 0 returned no content) · 4 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 40 in 14 days (2.86 per day) · most recent 2026-10-06 |
| Content length | 7,581 characters average, 7,234 median (shortest 5,477, longest 11,480) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to news.va.gov | 379 request(s) · 378 answered · 0 declined (4xx) · 0 server declined (5xx) · 1 no response — 0.3% returned no content |

last answered request 2026-10-07T04:00:54.518+00:00 UTC.

40 item(s) in the last 14 days; most recent 2026-10-06; 1 of 379 request(s) to news.va.gov returned no content.

### All time

- **Our requests to news.va.gov, all time (since 2026-07-30):** 2,066 request(s) · 2,063 answered · 3 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to news.va.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-08 | 4 | 29 | 337 |
| 2026-09-09 | 5 | 31 | 271 |
| 2026-09-10 | 3 | 28 | 202 |
| 2026-09-11 | 4 | 28 | 297 |
| 2026-09-12 | 1 | 30 | 327 |
| 2026-09-13 | 1 | 25 | 236 |
| 2026-09-14 | 5 | 34 | 415 |
| 2026-09-15 | 4 | 29 | 229 |
| 2026-09-16 | 4 | 30 | 269 |
| 2026-09-17 | 1 | 26 | 255 |
| 2026-09-18 | 4 | 29 | 332 |
| 2026-09-19 | 2 | 27 | 228 |
| 2026-09-20 | 2 | 27 | 243 |
| 2026-09-21 | 4 | 31 | 286 |
| 2026-09-22 | 4 | 29 | 241 |
| 2026-09-23 | 3 | 27 | 239 |
| 2026-09-24 | 3 | 29 | 286 |
| 2026-09-25 | 4 | 29 | 287 |
| 2026-09-26 | 2 | 29 | 322 |
| 2026-09-27 | 2 | 27 | 265 |
| 2026-09-28 | 3 | 30 | 299 |
| 2026-09-29 | 3 | 30 | 270 |
| 2026-09-30 | 4 | 29 | 271 |
| 2026-10-01 | 4 | 30 | 322 |
| 2026-10-02 | 3 | 30 | 219 |
| 2026-10-03 | 2 | 28 | 247 |
| 2026-10-04 | 2 | 27 | 255 |
| 2026-10-05 | 4 | 30 | 251 |
| 2026-10-06 | 4 | 30 | 272 |
| 2026-10-07 | 0 | 1 | 294 |

## Our ingestion assessment

**Model-written ingestion assessment**

VA news releases arrive through an RSS feed with full article text extracted from linked pages. Over the past 14 days, 39 items accumulated at 2.79 per day, up from the previously measured 2.64 per day. Extracted text averaged 7,637 characters, slightly increased from 7,460. Items appear in clustered delivery windows, primarily 9–10 a.m., 1–2 p.m., and 3–5 p.m. Eastern. Of 376 requests to news.va.gov, 375 succeeded; one returned no content for a 0.3% error rate, compared to the prior period's 0% across 382 attempts. The source mixes feature stories with press releases. Most recent item published 2026-10-05.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

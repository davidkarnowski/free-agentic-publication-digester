<!-- Markdown twin of https://fapd.info/sources/nasa-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nasa-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nasa-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NASA News Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Independent agency

Official site: https://www.nasa.gov/news/ · All sources: [sources.md](../sources.md)

## What this source is

NASA conducts the civil space program and aeronautics research. This RSS feed carries the agency's breaking-news releases — missions, launches, crew activities, and research announcements — as teaser descriptions (10 most recent items, ~300 characters each; article pages extract at ~9,000 characters).

**Model-written orientation**

NASA releases breaking news about space missions, launches, crew activities, and aeronautics research through its official news-release feed.

The National Aeronautics and Space Administration (NASA) is an independent federal agency responsible for the civilian space program of the United States. Established in 1958, NASA conducts human spaceflight operations including the International Space Station; operates robotic missions throughout the solar system and beyond; pursues Earth observation and climate science research from space; conducts aeronautical research and development; and manages research centers and testing facilities across the country. The agency employs scientists, engineers, and support staff at ten major field centers and numerous smaller facilities.

NASA's breaking-news RSS feed serves as the agency's official channel for announcing significant developments to the public and media. The feed covers human spaceflight milestones such as crew launches and returns, activities aboard the International Space Station, and astronaut achievements in orbit. It includes announcements of robotic-mission accomplishments—planetary landings, orbital insertions, data transmissions from deep-space probes, and discoveries from ongoing missions throughout the solar system. Scientific announcements communicate findings from NASA's research programs in Earth science, heliophysics, planetary science, and astrophysics. The feed also carries administrative announcements affecting agency operations, workforce, or strategic direction.

Each feed item provides a brief summary with links to the full press release on NASA's website. Article pages provide detailed background, scientific context, high-resolution imagery, and often supplementary resources such as video or data links. The feed represents NASA's intended disclosure channel for significant news and is updated as events occur throughout the year. Readers of this digest will encounter a cross-section of NASA's activities spanning human spaceflight, robotic exploration, scientific research, and facility operations. Content reflects the agency's dual role as both an operational spaceflight organization and a scientific research institution conducting basic research in space and aeronautics.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nasa-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.nasa.gov/rss/dyn/breaking_news.rss |
| URL (home) | https://www.nasa.gov/news/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 10 items, avg description 313 chars, sample article extracted (9439 chars text). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Would poll the breaking-news RSS feed daily for new items. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 95 item(s) in the last 14 days; most recent 2026-10-05; 0 of 391 request(s) to www.nasa.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-06T03:59:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 30 request(s) (30 answered, 0 returned no content) · 9 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 95 in 14 days (6.79 per day) · most recent 2026-10-05 |
| Content length | 10,899 characters average, 10,608 median (shortest 7,125, longest 19,697) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.nasa.gov | 391 request(s) · 391 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-06T04:00:15.366+00:00 UTC.

95 item(s) in the last 14 days; most recent 2026-10-05; 0 of 391 request(s) to www.nasa.gov returned no content.

### All time

- **Our requests to www.nasa.gov, all time (since 2026-07-30):** 2,060 request(s) · 2,041 answered · 19 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nasa.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-07 | 2 | 25 | 128 |
| 2026-09-08 | 8 | 29 | 121 |
| 2026-09-09 | 7 | 29 | 123 |
| 2026-09-10 | 7 | 30 | 100 |
| 2026-09-11 | 7 | 27 | 113 |
| 2026-09-12 | 0 | 28 | 166 |
| 2026-09-13 | 1 | 25 | 150 |
| 2026-09-14 | 7 | 31 | 284 |
| 2026-09-15 | 7 | 31 | 93 |
| 2026-09-16 | 12 | 32 | 114 |
| 2026-09-17 | 5 | 29 | 101 |
| 2026-09-18 | 6 | 28 | 150 |
| 2026-09-19 | 1 | 25 | 97 |
| 2026-09-20 | 1 | 25 | 96 |
| 2026-09-21 | 10 | 33 | 195 |
| 2026-09-22 | 7 | 28 | 102 |
| 2026-09-23 | 12 | 31 | 98 |
| 2026-09-24 | 9 | 32 | 144 |
| 2026-09-25 | 9 | 32 | 104 |
| 2026-09-26 | 1 | 26 | 177 |
| 2026-09-27 | 1 | 26 | 145 |
| 2026-09-28 | 14 | 35 | 180 |
| 2026-09-29 | 11 | 37 | 104 |
| 2026-09-30 | 8 | 28 | 101 |
| 2026-10-01 | 8 | 29 | 103 |
| 2026-10-02 | 9 | 32 | 88 |
| 2026-10-03 | 1 | 26 | 107 |
| 2026-10-04 | 3 | 26 | 105 |
| 2026-10-05 | 9 | 30 | 107 |
| 2026-10-06 | 0 | 1 | 390 |

## Our ingestion assessment

**Model-written ingestion assessment**

NASA breaking-news releases arrive through an RSS feed with full article text extracted from linked pages. Over 14 days, 95 items accumulated at 6.79 per day, substantially up from the previously measured 4.86 per day, representing the highest collection volume among measured sources. Extracted text averaged 10,899 characters. Items distribute throughout most hours of each day, with concentrations in morning and midday windows. All 391 requests to www.nasa.gov succeeded without error or no-content responses, a significant improvement from the prior 4.8% error rate with 19 no-content responses. Most recent item published 2026-10-05.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

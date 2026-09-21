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

**delivering** — 69 item(s) in the last 14 days; most recent 2026-09-20; 0 of 383 request(s) to www.nasa.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-21T03:47:52Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 69 in 14 days (4.93 per day) · most recent 2026-09-20 |
| Content length | 10,723 characters average, 10,273 median (shortest 460, longest 18,480) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.nasa.gov | 383 request(s) · 383 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-21T04:01:54.247+00:00 UTC.

69 item(s) in the last 14 days; most recent 2026-09-20; 0 of 383 request(s) to www.nasa.gov returned no content.

### All time

- **Our requests to www.nasa.gov, all time (since 2026-07-30):** 1,691 request(s) · 1,672 answered · 19 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nasa.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-23 | 1 | 30 | 133 |
| 2026-08-24 | 8 | 29 | 160 |
| 2026-08-25 | 8 | 31 | 112 |
| 2026-08-26 | 7 | 31 | 104 |
| 2026-08-27 | 7 | 29 | 152 |
| 2026-08-28 | 7 | 31 | 98 |
| 2026-08-29 | 0 | 27 | 107 |
| 2026-08-30 | 4 | 27 | 158 |
| 2026-08-31 | 5 | 28 | 124 |
| 2026-09-01 | 5 | 27 | 109 |
| 2026-09-02 | 5 | 39 | 198 |
| 2026-09-03 | 6 | 32 | 268 |
| 2026-09-04 | 5 | 30 | 155 |
| 2026-09-05 | 1 | 33 | 241 |
| 2026-09-06 | 0 | 26 | 152 |
| 2026-09-07 | 2 | 26 | 128 |
| 2026-09-08 | 8 | 30 | 121 |
| 2026-09-09 | 7 | 30 | 121 |
| 2026-09-10 | 7 | 31 | 100 |
| 2026-09-11 | 7 | 28 | 113 |
| 2026-09-12 | 0 | 29 | 168 |
| 2026-09-13 | 1 | 26 | 147 |
| 2026-09-14 | 7 | 32 | 291 |
| 2026-09-15 | 7 | 32 | 93 |
| 2026-09-16 | 12 | 33 | 113 |
| 2026-09-17 | 5 | 30 | 100 |
| 2026-09-18 | 6 | 29 | 149 |
| 2026-09-19 | 1 | 26 | 97 |
| 2026-09-20 | 1 | 26 | 95 |
| 2026-09-21 | 0 | 1 | 100 |

## Our ingestion assessment

**Model-written ingestion assessment**

The RSS feed carries teaser descriptions with full article extraction from linked pages. Over 14 days, 68 items arrived at 4.86 per day, the highest rate among all sources measured, up from the previous 3.79 per day. Extracted text averaged 11,241 characters. Our requests to www.nasa.gov returned a 4.8% error rate across 392 attempts, with 19 no-content responses, a shift from the prior 100% success. The most recent item was published on 2026-09-04. Nine items arrived in the past 24 hours.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

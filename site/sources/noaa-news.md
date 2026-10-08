<!-- Markdown twin of https://fapd.info/sources/noaa-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/noaa-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: noaa-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NOAA News Releases

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Department of Commerce

Official site: https://www.noaa.gov/news-releases · All sources: [sources.md](../sources.md)

## What this source is

The National Oceanic and Atmospheric Administration, within Commerce, runs the National Weather Service and ocean, climate, and fisheries programs. Its news-release index carries announcements on weather, climate data, fisheries rules, and research, typically several items per week.

**Model-written orientation**

The National Oceanic and Atmospheric Administration, part of the Department of Commerce, operates the National Weather Service and ocean, climate, and fisheries programs and publishes a news-release index with announcements on weather, climate data, fisheries rules, and research.

The National Oceanic and Atmospheric Administration (NOAA) is a federal scientific agency within the Department of Commerce responsible for understanding and predicting changes in the Earth's atmosphere, oceans, and climate, and for managing marine resources. NOAA's primary components include the National Weather Service, which provides weather forecasts and warnings to the public and aviation system; the National Centers for Environmental Prediction; the National Marine Fisheries Service, which manages commercial and recreational fishing; and research divisions focused on oceanography, atmospheric science, and climate. NOAA operates a nationwide network of weather offices, operates ocean observation systems, conducts marine research, and maintains environmental monitoring networks.

NOAA's news-release index serves as the agency's central channel for announcements about its scientific work and operational activities. Releases typically appear several times per week and cover a broad range of topics reflecting NOAA's wide portfolio. Announcements address significant weather events and forecasts, newly available climate and ocean data, fisheries regulations and catch limits, research findings about ocean conditions or atmospheric phenomena, updates to weather forecasting systems or technology, marine conservation actions, updates about fishery closures or openings, coastal hazard warnings, El Niño or La Niña conditions, and information about NOAA's environmental monitoring programs. The agency communicates with fishermen, weather-dependent industries, coastal communities, scientists, and the general public.

In the digest, NOAA announcements represent official scientific documentation from the federal government's primary civilian agency for environmental information. Readers encounter news about weather and climate conditions, new scientific data about oceans and atmosphere, fisheries management decisions, and updates to forecasting and monitoring systems. The releases provide direct access to authoritative federal information about environmental and weather conditions affecting the nation, fishing industries, and coastal areas.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `noaa-news` |
| Agency / parent organization | Department of Commerce |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.noaa.gov/rss.xml |
| URL (home) | https://www.noaa.gov/news-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 403 (WAF) on the /news-releases index. Re-probed 2026-07-28: the documented main feed (noaa.gov/rss.xml, per NOAA's own RSS docs page — a path distinct from the blocked one) is open: HTTP 200, 10 items with rich ~6,700-char descriptions. Sample article page returned 403 — same WAF as the index — so this is feed-only ingestion (adapter rss-feed-only), honestly disclosed per item; the long descriptions carry the substance. Component feed libraries (oceanservice, climate.gov, nhc.noaa.gov) remain tier-3 candidates. Activated 2026-07-28. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the documented main RSS feed via AgencyClient, feed metadata only (article pages 403 identified clients). |
| Adapter | rss-feed-only |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 3 item(s) in the last 14 days; most recent 2026-10-07; 0 of 340 request(s) to www.noaa.gov returned no content.

This label has held since 2026-09-18T04:27:20Z (UTC) and was last re-checked 2026-10-08T03:55:12Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-07 |
| Content length | 2,846 characters average, 2,042 median (shortest 242, longest 6,254) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.noaa.gov | 340 request(s) · 340 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-08T04:00:13.642+00:00 UTC.

3 item(s) in the last 14 days; most recent 2026-10-07; 0 of 340 request(s) to www.noaa.gov returned no content.

### All time

- **Our requests to www.noaa.gov, all time (since 2026-07-30):** 1,987 request(s) · 1,878 answered · 109 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.noaa.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-09 | 1 | 29 | 1354 |
| 2026-09-10 | 1 | 24 | 400 |
| 2026-09-11 | 0 | 25 | 300 |
| 2026-09-12 | 0 | 28 | 240 |
| 2026-09-13 | 0 | 25 | 253 |
| 2026-09-14 | 0 | 29 | 413 |
| 2026-09-15 | 2 | 25 | 206 |
| 2026-09-16 | 0 | 25 | 319 |
| 2026-09-17 | 2 | 25 | 290 |
| 2026-09-18 | 0 | 25 | 925 |
| 2026-09-19 | 0 | 25 | 282 |
| 2026-09-20 | 0 | 25 | 266 |
| 2026-09-21 | 2 | 28 | 329 |
| 2026-09-22 | 1 | 25 | 236 |
| 2026-09-23 | 0 | 24 | 291 |
| 2026-09-24 | 1 | 25 | 295 |
| 2026-09-25 | 1 | 26 | 267 |
| 2026-09-26 | 0 | 26 | 350 |
| 2026-09-27 | 0 | 26 | 338 |
| 2026-09-28 | 0 | 28 | 464 |
| 2026-09-29 | 0 | 27 | 285 |
| 2026-09-30 | 1 | 25 | 268 |
| 2026-10-01 | 0 | 26 | 296 |
| 2026-10-02 | 0 | 26 | 278 |
| 2026-10-03 | 0 | 26 | 274 |
| 2026-10-04 | 0 | 25 | 311 |
| 2026-10-05 | 0 | 26 | 272 |
| 2026-10-06 | 0 | 26 | 247 |
| 2026-10-07 | 1 | 26 | 241 |
| 2026-10-08 | 0 | 1 | 266 |

## Our ingestion assessment

**Model-written ingestion assessment**

NOAA's news feed at noaa.gov/rss.xml remains feed-only ingestion; the news index and individual article pages return HTTP 403. Feed descriptions average 2,343 characters and supply the substance of items. Over the past 14 days we ingested 6 items at a rate of 0.43 per day, with the most recent on 2026-09-17. Request reliability has improved from the prior assessment: of 349 requests to www.noaa.gov in the current window, 18 returned no content (5.2% error rate) versus 15.3% no-response previously. A single failure occurred in the past 24 hours. Delivery cadence is intermittent—several inactive days followed by occasional pulses of multiple items within a single collection cycle.

_Model-written assessment of our own ingestion, generated 2026-09-19 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

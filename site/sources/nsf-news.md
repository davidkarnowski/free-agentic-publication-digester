<!-- Markdown twin of https://fapd.info/sources/nsf-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nsf-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nsf-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NSF News

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.nsf.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The National Science Foundation funds basic research across science and engineering. Its news index carries agency announcements on funding programs, research findings, and facilities, typically a few items per week.

**Model-written orientation**

The National Science Foundation funds basic research in science and engineering across the United States and publishes announcements on funding opportunities and research discoveries.

The National Science Foundation (NSF) is an independent agency that supports basic scientific research and science education across all fields of science and engineering except medicine. Established in 1950, NSF's mission is to promote the progress of science, advance national health and prosperity, and secure the national defense through research and education. The agency distributes billions of dollars annually in federal research funding to universities, research institutions, and individual investigators throughout the nation.

NSF operates through directorates covering distinct scientific domains: Biological Sciences, Computer and Information Science and Engineering, Engineering, Geosciences, Mathematical and Physical Sciences, and Social, Behavioral, and Economic Sciences. It also manages large research facilities—telescopes, supercomputers, research vessels, and observatories—that serve the broader scientific community. NSF funding supports fundamental research, graduate education, and undergraduate training, and the agency plays an important role in maintaining U.S. competitiveness in science and technology.

In this digest, you will see NSF announcements of new funding solicitations and programs, awards to major research institutions or research centers, significant research findings from NSF-supported projects, updates on facility operations or upgrades, and statements on agency initiatives. The releases span the full breadth of NSF's scientific portfolio, from biology and physics to computer science and social science. NSF's public releases serve researchers seeking funding opportunities, institutions managing research programs, and the general public interested in federally supported scientific advances.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nsf-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.nsf.gov/news |
| URL (index) | https://www.nsf.gov/news |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 71 article link(s); 4 dated inside the 7-day lookback, 7 dated outside it, 60 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the feed-shaped link in the captured page (https://nsf.gov/rss) is an HTML directory of feeds, not a feed — verdict html-only. A specific feed URL may exist behind it; not pursued further this pass. Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 1 entry dated inside the 7-day lookback (2026-09-21). The news listing carries podcasts and features as well as releases; that day's entry was a podcast episode. All are read. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only). |
| Adapter | html-index |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 13 request(s) to www.nsf.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 13 request(s) (13 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-09-28 |
| Content length | 262 characters average, 262 median (shortest 262, longest 262) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.nsf.gov | 13 request(s) · 13 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-29T04:10:14.026+00:00 UTC.

1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 13 request(s) to www.nsf.gov returned no content.

### All time

- **Our requests to www.nsf.gov, all time (since 2026-09-28):** 13 request(s) · 13 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nsf.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-31 | 0 | 0 | — |
| 2026-09-01 | 0 | 0 | — |
| 2026-09-02 | 0 | 0 | — |
| 2026-09-03 | 0 | 0 | — |
| 2026-09-04 | 0 | 0 | — |
| 2026-09-05 | 0 | 0 | — |
| 2026-09-06 | 0 | 0 | — |
| 2026-09-07 | 0 | 0 | — |
| 2026-09-08 | 0 | 0 | — |
| 2026-09-09 | 0 | 0 | — |
| 2026-09-10 | 0 | 0 | — |
| 2026-09-11 | 0 | 0 | — |
| 2026-09-12 | 0 | 0 | — |
| 2026-09-13 | 0 | 0 | — |
| 2026-09-14 | 0 | 0 | — |
| 2026-09-15 | 0 | 0 | — |
| 2026-09-16 | 0 | 0 | — |
| 2026-09-17 | 0 | 0 | — |
| 2026-09-18 | 0 | 0 | — |
| 2026-09-19 | 0 | 0 | — |
| 2026-09-20 | 0 | 0 | — |
| 2026-09-21 | 0 | 0 | — |
| 2026-09-22 | 0 | 0 | — |
| 2026-09-23 | 0 | 0 | — |
| 2026-09-24 | 0 | 0 | — |
| 2026-09-25 | 0 | 0 | — |
| 2026-09-26 | 0 | 0 | — |
| 2026-09-27 | 0 | 0 | — |
| 2026-09-28 | 1 | 11 | 199 |
| 2026-09-29 | 0 | 2 | 102 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September. The NSF news listing carries podcasts and features alongside press releases; all content types are read. We observed 1 item over 14 days. All 13 requests to www.nsf.gov succeeded with no failures. The listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. Entries lacking readable dates are dropped and never observation-dated. No machine-readable feeds are advertised on this source.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

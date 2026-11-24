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

The National Science Foundation funds basic research across science and engineering. Its news index carries agency announcements on funding programs, research findings, and facilities.

The National Science Foundation (NSF) is an independent agency that supports fundamental research and education in science and engineering across the United States. The NSF was established in 1950 and is distinct from other federal research agencies in that it emphasizes basic research—investigations designed to advance scientific understanding—rather than applied research directed toward specific technologies or products.

The NSF operates through several directorates that fund research across disciplines: Biological Sciences, Computer and Information Science and Engineering, Engineering, Geosciences, Mathematical and Physical Sciences, and Social, Behavioral and Economic Sciences. The agency also supports science and engineering education programs at all levels, from elementary school through graduate training and workforce development. The NSF distributes billions of dollars annually in competitive grants to universities, research institutions, and investigators across the country.

The NSF news index serves as the agency's primary channel for public announcements about its activities, policies, and funded research. The news section carries multiple types of content: agency announcements on new funding opportunities, changes to grant-making policies, or funding solicitations; highlights of selected research projects funded by NSF grants; announcements about NSF facilities and their activities; updates on education initiatives; and agency-wide policy or administrative announcements. The news index typically contains several items per week, though frequency varies with program announcements and research highlights.

Documents you will see from this source in the digest include announcements of new funding opportunities or changes to existing programs, summaries or highlights of research projects receiving NSF support, announcements related to NSF research facilities and infrastructure, updates on science education initiatives, notices of NSF meetings or workshops, and administrative or policy announcements from the agency. The news also includes podcasts and feature articles exploring NSF-funded research and agency initiatives. These items are dated by the NSF and sourced through the agency's news index.

The NSF is part of the Executive Branch and reports to the National Science and Technology Council. As an independent agency, the NSF does not duplicate other agencies' research missions and coordinates with other federal research funders including the National Institutes of Health, the Department of Energy, and the Department of Defense. The agency is funded through annual congressional appropriations and operates as a primary mechanism for federal support of academic research in the United States.

_Model-written orientation, generated 2026-09-30 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

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

**delivering** — 2 item(s) in the last 14 days; most recent 2026-11-23; 0 of 329 request(s) to www.nsf.gov returned no content.

This label has held since 2026-11-23T22:04:10Z (UTC) and was last re-checked 2026-11-24T04:53:50Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 24 request(s) (24 answered, 0 returned no content) · 2 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-11-23 |
| Content length | 252 characters average, 252 median (shortest 246, longest 257) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.nsf.gov | 329 request(s) · 329 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-11-24T05:00:16.076+00:00 UTC.

2 item(s) in the last 14 days; most recent 2026-11-23; 0 of 329 request(s) to www.nsf.gov returned no content.

### All time

- **Our requests to www.nsf.gov, all time (since 2026-09-28):** 1,432 request(s) · 1,432 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nsf.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-26 | 0 | 25 | 63 |
| 2026-10-27 | 2 | 24 | 80 |
| 2026-10-28 | 0 | 25 | 81 |
| 2026-10-29 | 0 | 25 | 48 |
| 2026-10-30 | 0 | 26 | 84 |
| 2026-10-31 | 0 | 25 | 84 |
| 2026-11-01 | 0 | 25 | 96 |
| 2026-11-02 | 1 | 25 | 75 |
| 2026-11-03 | 0 | 25 | 58 |
| 2026-11-04 | 0 | 25 | 58 |
| 2026-11-05 | 0 | 25 | 83 |
| 2026-11-06 | 0 | 26 | 111 |
| 2026-11-07 | 0 | 25 | 76 |
| 2026-11-08 | 0 | 26 | 75 |
| 2026-11-09 | 0 | 25 | 84 |
| 2026-11-10 | 0 | 26 | 80 |
| 2026-11-11 | 0 | 25 | 53 |
| 2026-11-12 | 0 | 28 | 90 |
| 2026-11-13 | 0 | 26 | 223 |
| 2026-11-14 | 0 | 25 | 81 |
| 2026-11-15 | 0 | 25 | 151 |
| 2026-11-16 | 0 | 26 | 177 |
| 2026-11-17 | 0 | 25 | 69 |
| 2026-11-18 | 0 | 24 | 99 |
| 2026-11-19 | 0 | 25 | 85 |
| 2026-11-20 | 0 | 25 | 79 |
| 2026-11-21 | 0 | 25 | 141 |
| 2026-11-22 | 0 | 25 | 80 |
| 2026-11-23 | 2 | 24 | 79 |
| 2026-11-24 | 0 | 1 | 93 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest NSF News through the HTML index adapter in feed-only mode, with one listing fetch per poll and no article pages, because no machine-readable feed is advertised. The listing carries releases, podcasts, and features, and all entries are read. The adapter reads the first page of the listing only, and entries it cannot date are dropped rather than dated by observation. Measured entries averaged 252 characters (median 252, range 246 to 257 across two items). The 14-day window holds two items, a rate of 0.14 per day, the most recent dated 2026-11-23. All 329 requests to www.nsf.gov were answered, none returning no content, and health reads delivering. Compared with the 2026-11-11 assessment, which recorded one item dated 2026-11-02 at 276 characters, the window count rose to two, the most recent date moved to 2026-11-23, and the average length fell from 276 to 252 characters. The source was activated 2026-09-28.

_Model-written assessment of our own ingestion, generated 2026-11-24 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

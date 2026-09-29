<!-- Markdown twin of https://fapd.info/sources/gsa-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/gsa-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: gsa-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# GSA News Releases

active · ingestion health: delivering · Executive · Tier 1 · HTML index · Independent agency

Official site: https://www.gsa.gov/about-us/newsroom/news-releases · All sources: [sources.md](../sources.md)

## What this source is

The General Services Administration manages federal procurement, real estate, and shared technology services. Its news-release index carries announcements on contracts, federal buildings, and government-wide programs, typically a few items per week.

**Model-written orientation**

General Services Administration announcements on federal procurement, real estate, technology services, and federal operations.

The General Services Administration is an independent agency that provides centralized services to the federal government across three major functions. First, it manages federal procurement, offering the GSA Schedule (a catalog of pre-negotiated contracts) and other buying vehicles that allow all federal agencies to purchase goods and services efficiently at negotiated rates. Second, it manages federal real property, owning and leasing office buildings, courthouses, federal office plazas, and other facilities for federal use. Third, it offers shared technology and administrative services to federal agencies, reducing duplication and costs across government. The GSA enables efficient federal operations by consolidating purchases and services.

The GSA's news-release index announces the agency's significant decisions, initiatives, and actions. Readers will find press releases on major contract awards and procurement programs, announcements of new products and services added to the GSA Schedule, updates on federal buildings and real property acquisitions or leases, information on government-wide shared services and new initiatives, proposed and final rulemaking affecting federal procurement or the agency's operations, personnel announcements, and other agency news. The GSA typically publishes a few items per week through this channel.

Materials in this feed serve federal procurement officers and agency administrators responsible for buying goods and services, vendors seeking federal contracting opportunities, federal employees and agencies using GSA services, real estate professionals, business associations in government contracting, and the public interested in federal procurement and operations.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `gsa-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.gsa.gov/about-us/newsroom/news-releases |
| URL (index) | https://www.gsa.gov/about-gsa/newsroom/news-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 319 article link(s); 2 dated inside the 7-day lookback, 58 dated outside it, 259 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: The listing now redirects from /about-us/ to /about-gsa/, registered as the index. 1 entry dated inside the 7-day lookback (2026-09-24); a low-rate source. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 13 request(s) to www.gsa.gov returned no content.

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
| Content length | 123 characters average, 123 median (shortest 123, longest 123) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.gsa.gov | 13 request(s) · 13 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-29T04:10:13.743+00:00 UTC.

1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 13 request(s) to www.gsa.gov returned no content.

### All time

- **Our requests to www.gsa.gov, all time (since 2026-09-28):** 13 request(s) · 13 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.gsa.gov | Mean response time (ms) |
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
| 2026-09-28 | 1 | 12 | 660 |
| 2026-09-29 | 0 | 1 | 227 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September. The listing at the GSA newsroom redirected from the /about-us/ path to /about-gsa/; we poll the target URL. We observed 1 item over 14 days. All 13 requests to www.gsa.gov succeeded with no failures. The listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. Entries lacking readable dates are dropped and never observation-dated. No machine-readable feeds are advertised on this source.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

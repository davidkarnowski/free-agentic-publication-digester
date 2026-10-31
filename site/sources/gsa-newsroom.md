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

**delivering** — 3 item(s) in the last 14 days; most recent 2026-10-27; 10 of 337 request(s) to www.gsa.gov returned no content.

This label has held since 2026-10-21T17:58:30Z (UTC) and was last re-checked 2026-10-31T03:45:15Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-27 |
| Content length | 319 characters average, 358 median (shortest 210, longest 388) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.gsa.gov | 337 request(s) · 327 answered · 0 declined (4xx) · 0 server declined (5xx) · 10 no response — 3.0% returned no content |

last answered request 2026-10-31T04:00:14.518+00:00 UTC.

3 item(s) in the last 14 days; most recent 2026-10-27; 10 of 337 request(s) to www.gsa.gov returned no content.

### All time

- **Our requests to www.gsa.gov, all time (since 2026-09-28):** 831 request(s) · 821 answered · 10 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.gsa.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-02 | 0 | 25 | 192 |
| 2026-10-03 | 0 | 25 | 213 |
| 2026-10-04 | 0 | 25 | 277 |
| 2026-10-05 | 0 | 26 | 195 |
| 2026-10-06 | 0 | 27 | 185 |
| 2026-10-07 | 0 | 26 | 206 |
| 2026-10-08 | 0 | 26 | 286 |
| 2026-10-09 | 0 | 26 | 158 |
| 2026-10-10 | 0 | 25 | 277 |
| 2026-10-11 | 0 | 24 | 213 |
| 2026-10-12 | 0 | 25 | 268 |
| 2026-10-13 | 0 | 25 | 261 |
| 2026-10-14 | 0 | 25 | 205 |
| 2026-10-15 | 0 | 25 | 265 |
| 2026-10-16 | 0 | 26 | 217 |
| 2026-10-17 | 0 | 25 | 261 |
| 2026-10-18 | 0 | 25 | 203 |
| 2026-10-19 | 0 | 24 | 210 |
| 2026-10-20 | 0 | 26 | 134 |
| 2026-10-21 | 2 | 26 | 212 |
| 2026-10-22 | 0 | 25 | 203 |
| 2026-10-23 | 0 | 25 | 184 |
| 2026-10-24 | 0 | 26 | 160 |
| 2026-10-25 | 0 | 25 | 130 |
| 2026-10-26 | 0 | 33 | 354 |
| 2026-10-27 | 1 | 25 | 200 |
| 2026-10-28 | 0 | 24 | 242 |
| 2026-10-29 | 0 | 25 | 153 |
| 2026-10-30 | 0 | 27 | 262 |
| 2026-10-31 | 0 | 1 | 1514 |

## Our ingestion assessment

**Model-written ingestion assessment**

Polling the GSA News Releases HTML index via daily diffing yields approximately 25 to 26 requests daily. All 328 requests to www.gsa.gov succeeded with zero failures over the measurement period. Two items were observed during the 14-day window, both dated 2026-10-21 and averaging 299 characters. The prior assessment (2026-10-10) recorded zero items with the most recent dating 2026-10-01; delivery resumed on 2026-10-21 after a nine-day gap. The index displays the first page only, creating the possibility of under-coverage if publication volume exceeds page capacity between polls. Entries without machine-readable dates are dropped and never observation-dated. A URL redirect from /about-us/ to /about-gsa/ has been registered as the active index.

_Model-written assessment of our own ingestion, generated 2026-10-22 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

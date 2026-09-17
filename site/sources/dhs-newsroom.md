<!-- Markdown twin of https://fapd.info/sources/dhs-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/dhs-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: dhs-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DHS News Releases

active · ingestion health: delivering · Executive · Tier 1 · HTML index · Department of Homeland Security

Official site: https://www.dhs.gov/news-releases · All sources: [sources.md](../sources.md)

## What this source is

The Department of Homeland Security oversees border security, immigration enforcement, cybersecurity, and disaster response. Its news-release index carries departmental press releases and secretarial statements, typically several items per week; component agencies publish separately.

**Model-written orientation**

The Department of Homeland Security publishes press releases and official statements on border security, immigration enforcement, cybersecurity, and disaster response operations.

The Department of Homeland Security (DHS) is the federal executive agency responsible for border security, immigration enforcement, customs operations, cybersecurity and infrastructure protection, and disaster response and management. DHS houses multiple operational components including U.S. Customs and Border Protection (CBP), U.S. Immigration and Customs Enforcement (ICE), the Cybersecurity and Infrastructure Security Agency (CISA), and the Federal Emergency Management Agency (FEMA). Together, these agencies implement federal law and policy affecting border operations, immigration, cybersecurity, and disaster management.

Through its news office, DHS publishes official press releases and announcements on departmental policies, operational updates, major initiatives, and enforcement priorities. Readers will find releases covering topics such as border security operations and enforcement statistics, immigration enforcement announcements, cybersecurity alerts and responses to threats, disaster response operations and recovery efforts, policy changes affecting border security or immigration operations, technology deployments and operational updates, leadership statements and appointments, and major departmental initiatives.

DHS releases serve as official notification to Congress, state and local government partners, industry, immigrant advocacy organizations, security professionals, and the public of federal actions and policies affecting border security, immigration, cybersecurity, and disaster management. The releases typically include operational data, geographic scope, policy details, and statements from departmental leadership. Individual component agencies within DHS—including CBP, ICE, CISA, and FEMA—maintain their own dedicated communication channels and publish frequent operational updates specific to their missions, but the departmental newsroom publishes releases addressing policies and actions at the secretary level affecting multiple components or the homeland security mission broadly. The feed includes releases published on the current page of the departmental news index; the full archive of releases extends back further and is available through the department's website.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `dhs-newsroom` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.dhs.gov/news-releases |
| URL (index) | https://www.dhs.gov/news-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered. Re-probed 2026-07-31: HTTP 200, robots allows, still no machine-readable feed. ACTIVATED 2026-07-31 with the html-index adapter. Gate 3: the index paginates at 10 entries per page and we read page 1 only; every entry carries a <time datetime> attribute, so all 10 are dated from DHS's own markup and none by observation, and the listing's own teaser (200-270 chars) is stored as the item's text — mode feed-only, one request per poll, no article fetches. The ~48 further links on the page are site navigation and are skipped for stating no date (an undated listing entry is dropped, never observation-dated). Under-coverage: component agencies (CBP, ICE, USCIS, TSA, FEMA) publish on their own indexes and are not in this one, and anything past page 1 — more than 10 releases between two polls — is not seen. |

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

**delivering** — 31 item(s) in the last 14 days; most recent 2026-09-16; 0 of 352 request(s) to www.dhs.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-17T03:58:34Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 4 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 31 in 14 days (2.21 per day) · most recent 2026-09-16 |
| Content length | 369 characters average, 357 median (shortest 260, longest 504) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.dhs.gov | 352 request(s) · 352 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-17T04:25:07.182+00:00 UTC.

31 item(s) in the last 14 days; most recent 2026-09-16; 0 of 352 request(s) to www.dhs.gov returned no content.

### All time

- **Our requests to www.dhs.gov, all time (since 2026-08-01):** 1,380 request(s) · 1,376 answered · 4 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.dhs.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-19 | 4 | 24 | 403 |
| 2026-08-20 | 3 | 34 | 495 |
| 2026-08-21 | 4 | 30 | 366 |
| 2026-08-22 | 0 | 30 | 371 |
| 2026-08-23 | 0 | 28 | 307 |
| 2026-08-24 | 3 | 28 | 372 |
| 2026-08-25 | 3 | 26 | 375 |
| 2026-08-26 | 2 | 25 | 381 |
| 2026-08-27 | 4 | 26 | 373 |
| 2026-08-28 | 3 | 26 | 746 |
| 2026-08-29 | 0 | 26 | 638 |
| 2026-08-30 | 0 | 26 | 382 |
| 2026-08-31 | 2 | 26 | 383 |
| 2026-09-01 | 3 | 26 | 432 |
| 2026-09-02 | 4 | 26 | 442 |
| 2026-09-03 | 2 | 28 | 622 |
| 2026-09-04 | 3 | 26 | 370 |
| 2026-09-05 | 1 | 34 | 467 |
| 2026-09-06 | 0 | 26 | 293 |
| 2026-09-07 | 0 | 26 | 421 |
| 2026-09-08 | 2 | 26 | 378 |
| 2026-09-09 | 4 | 26 | 304 |
| 2026-09-10 | 3 | 26 | 392 |
| 2026-09-11 | 6 | 26 | 421 |
| 2026-09-12 | 0 | 28 | 397 |
| 2026-09-13 | 0 | 26 | 479 |
| 2026-09-14 | 3 | 28 | 680 |
| 2026-09-15 | 5 | 26 | 403 |
| 2026-09-16 | 4 | 27 | 358 |
| 2026-09-17 | 0 | 1 | 380 |

## Our ingestion assessment

**Model-written ingestion assessment**

The index displays dated press releases with modest teaser text derived from the feed entry itself. Over 14 days, 29 items arrived at 2.07 per day, up from the previously measured 1.14 per day. Stored text averaged 390 characters per item from the publisher's own summaries. All indexed items carry dates provided by the agency, so none were dated by observation. Our requests to www.dhs.gov returned a 1.2% error rate across 344 attempts, with 4 no-content responses; an earlier measurement showed 100% success. Coverage remains limited to the first page of the index only; component agencies publish their releases on separate indexes.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

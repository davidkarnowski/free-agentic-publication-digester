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

**delivering** — 38 item(s) in the last 14 days; most recent 2026-11-06; 30 of 330 request(s) to www.dhs.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-07T04:57:24Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · 3 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 38 in 14 days (2.71 per day) · most recent 2026-11-06 |
| Content length | 412 characters average, 398 median (shortest 245, longest 618) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.dhs.gov | 330 request(s) · 300 answered · 30 declined (4xx) · 0 server declined (5xx) · 0 no response — 9.1% returned no content |

last answered request 2026-11-07T05:00:26.259+00:00 UTC.

38 item(s) in the last 14 days; most recent 2026-11-06; 30 of 330 request(s) to www.dhs.gov returned no content.

### All time

- **Our requests to www.dhs.gov, all time (since 2026-08-01):** 2,631 request(s) · 2,597 answered · 34 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.dhs.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-09 | 4 | 25 | 275 |
| 2026-10-10 | 0 | 25 | 309 |
| 2026-10-11 | 0 | 26 | 1044 |
| 2026-10-12 | 2 | 25 | 336 |
| 2026-10-13 | 3 | 25 | 352 |
| 2026-10-14 | 2 | 25 | 384 |
| 2026-10-15 | 4 | 26 | 359 |
| 2026-10-16 | 8 | 25 | 308 |
| 2026-10-17 | 0 | 25 | 319 |
| 2026-10-18 | 0 | 25 | 304 |
| 2026-10-19 | 4 | 25 | 275 |
| 2026-10-20 | 3 | 25 | 258 |
| 2026-10-21 | 3 | 26 | 488 |
| 2026-10-22 | 3 | 25 | 296 |
| 2026-10-23 | 4 | 25 | 282 |
| 2026-10-24 | 2 | 24 | 230 |
| 2026-10-25 | 0 | 26 | 230 |
| 2026-10-26 | 3 | 25 | 243 |
| 2026-10-27 | 4 | 25 | 284 |
| 2026-10-28 | 6 | 24 | 329 |
| 2026-10-29 | 5 | 25 | 294 |
| 2026-10-30 | 5 | 27 | 332 |
| 2026-10-31 | 0 | 25 | 302 |
| 2026-11-01 | 0 | 26 | 366 |
| 2026-11-02 | 5 | 25 | 381 |
| 2026-11-03 | 3 | 25 | 326 |
| 2026-11-04 | 0 | 25 | 206 |
| 2026-11-05 | 4 | 26 | 218 |
| 2026-11-06 | 3 | 25 | 303 |
| 2026-11-07 | 0 | 1 | 270 |

## Our ingestion assessment

**Model-written ingestion assessment**

We read the DHS News Releases index in feed-only mode, with one listing fetch per poll and no article fetches. Over the 14-day window we recorded 37 items at 2.64 per day, up from 29 items at 2.07 per day in the prior assessment. Each entry carries a datetime attribute in DHS's markup, so items are dated from the publisher's own markup. Item text averaged 413 characters (median 401, range 280 to 618), taken from the listing teaser. The most recent item is dated 2026-11-03. Of 328 requests to www.dhs.gov, 315 returned content and 13 returned no content, an error rate of 4.0 percent. The prior assessment recorded 338 requests with no failures. On 2026-11-04, 12 of 25 requests returned no content, and 1 more did so on 2026-11-05. We read page 1 only, which holds 10 entries, so more than 10 new releases between polls would not be seen. Component agency releases are not carried in this index.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

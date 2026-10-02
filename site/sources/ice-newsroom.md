<!-- Markdown twin of https://fapd.info/sources/ice-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ice-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ice-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# ICE Newsroom

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.ice.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

U.S. Immigration and Customs Enforcement, within DHS, enforces immigration and customs law in the interior. Its newsroom index carries news releases on enforcement and removal operations and Homeland Security Investigations cases, typically several items per week.

**Model-written orientation**

The ICE Newsroom publishes news releases on immigration enforcement operations, removals, and criminal investigations conducted within the United States.

U.S. Immigration and Customs Enforcement is a law enforcement bureau within the Department of Homeland Security. ICE's responsibilities include enforcing immigration law in the interior of the United States, managing detention facilities, and investigating immigration crimes. The agency also operates Homeland Security Investigations, a criminal investigative arm that handles international and domestic cases involving customs and immigration violations.

The ICE Newsroom serves as the agency's official channel for communicating with the news media, law enforcement, and the public about enforcement operations and investigations. The newsroom publishes news releases describing enforcement operations, removals, criminal investigations outcomes, and officer actions.

Readers will see from this source news releases describing immigration enforcement actions carried out by ICE and its investigative units. These may include announcements of significant enforcement operations, results of criminal investigations, removals of individuals, and statements on enforcement priorities. Some releases may highlight transnational criminal organizations or customs violations. Others may address operational statistics or agency initiatives.

ICE news releases are written primarily for law enforcement officials, the media, and the general public. The agency publishes several releases per week, though volume varies depending on operational activity. The dates on releases represent ICE's own publication dates.

The Newsroom operates as an HTML index on the ICE website. The digest polls this index regularly, without fetching full articles, to identify new releases. Articles listed without a readable date are not included. The digest's coverage is limited to items appearing on the first page of the index at the time of polling; items published between polls that exceed one page of listings may not be captured.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ice-newsroom` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.ice.gov/newsroom |
| URL (index) | https://www.ice.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 95 article link(s); 6 dated inside the 7-day lookback, 19 dated outside it, 70 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 7 entries dated inside the 7-day lookback (2026-09-21..28), all news releases with ICE's own dates. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 9 item(s) in the last 14 days; most recent 2026-10-01; 0 of 95 request(s) to www.ice.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-02T03:48:29Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 9 in 14 days (0.64 per day) · most recent 2026-10-01 |
| Content length | 364 characters average, 362 median (shortest 215, longest 543) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.ice.gov | 95 request(s) · 95 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-02T04:18:05.942+00:00 UTC.

9 item(s) in the last 14 days; most recent 2026-10-01; 0 of 95 request(s) to www.ice.gov returned no content.

### All time

- **Our requests to www.ice.gov, all time (since 2026-09-28):** 95 request(s) · 95 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.ice.gov | Mean response time (ms) |
|---|---|---|---|
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
| 2026-09-28 | 7 | 12 | 225 |
| 2026-09-29 | 0 | 29 | 152 |
| 2026-09-30 | 1 | 26 | 171 |
| 2026-10-01 | 1 | 27 | 167 |
| 2026-10-02 | 0 | 1 | 172 |

## Our ingestion assessment

**Model-written ingestion assessment**

The ICE Newsroom is ingested via HTML index diffing with one listing poll per cycle. Activation on 2026-09-28 set the measurement baseline. In the 6 days since activation, seven items were ingested with dates ranging from 2026-09-21 to 2026-09-28, averaging 360 characters each. The source operates feed-only with no article fetches; index text serves as the full digest content. All 13 polling requests to www.ice.gov completed successfully with no errors. Coverage is limited to dateable entries on the listing's first page; undatable entries are dropped and never observation-dated.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/cdc-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cdc-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cdc-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CDC Newsroom

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Department of Health and Human Services

Official site: https://www.cdc.gov/media/index.html · All sources: [sources.md](../sources.md)

## What this source is

The Centers for Disease Control and Prevention is the national public-health agency within HHS. Its media index carries press releases, media statements, and telebriefing transcripts on outbreaks, advisories, and health guidance, typically several items per week.

**Model-written orientation**

The CDC Newsroom publishes press releases, media statements, and briefing transcripts on disease outbreaks, health advisories, and guidance affecting U.S. populations.

The Centers for Disease Control and Prevention is the federal government's principal public health agency, located within the Department of Health and Human Services. The CDC works to detect and respond to emerging health threats, conduct disease surveillance across the United States, and provide scientific guidance to the public and healthcare professionals.

The CDC Newsroom serves as the agency's official communication channel with the news media and the public about current and developing public health matters. It publishes press releases announcing disease surveillance findings, statements on health threats, and transcripts from media telebriefings at which CDC officials discuss health topics of public interest.

Readers will see in the digest a range of CDC announcements: disease outbreak notifications with information about transmission and public health response; health alerts and recommendations related to seasonal and emerging illnesses; guidance on prevention measures affecting the general public or specific populations; and updates on vaccination programs and disease monitoring efforts. Some releases address food safety, occupational health, or environmental health concerns. Others may announce research findings or changes to disease surveillance protocols.

CDC press releases are typically written for a general audience, though they often include epidemiological data and technical language reflecting the agency's scientific basis. Releases are published at varying intervals depending on public health events and the agency's communication schedule, typically several per week. The dates on releases represent the CDC's own publication dates.

The Newsroom operates as an HTML index on the CDC's website. The digest polls this index regularly, without fetching the full articles, to identify new releases as they are published. Articles listed without a readable date are not included in the digest. As a result, the digest contains releases the CDC has published on its Newsroom and dated, but does not backfill older items or entries for which dating information is unavailable in the listing itself.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cdc-newsroom` |
| Agency / parent organization | Department of Health and Human Services |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.cdc.gov/media/index.html |
| URL (index) | https://www.cdc.gov/media/index.html |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 19 article link(s); 1 dated inside the 7-day lookback, 6 dated outside it, 12 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: https://www.cdc.gov/rss is an HTML feed-directory page, not a feed (verdict html-only). Same shape as nsf-news. Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 1 entry dated inside the 7-day lookback (2026-09-22), a CDC media release; a low-rate source. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 143 request(s) to www.cdc.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-09-28 |
| Content length | 206 characters average, 206 median (shortest 206, longest 206) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.cdc.gov | 143 request(s) · 143 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-04T04:00:11.688+00:00 UTC.

1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 143 request(s) to www.cdc.gov returned no content.

### All time

- **Our requests to www.cdc.gov, all time (since 2026-09-28):** 143 request(s) · 143 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.cdc.gov | Mean response time (ms) |
|---|---|---|---|
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
| 2026-09-28 | 1 | 11 | 259 |
| 2026-09-29 | 0 | 26 | 253 |
| 2026-09-30 | 0 | 25 | 219 |
| 2026-10-01 | 0 | 28 | 190 |
| 2026-10-02 | 0 | 26 | 309 |
| 2026-10-03 | 0 | 26 | 170 |
| 2026-10-04 | 0 | 1 | 235 |

## Our ingestion assessment

**Model-written ingestion assessment**

The CDC Newsroom is ingested via HTML index diffing with one listing poll per cycle. Activation on 2026-09-28 set the measurement baseline. In the 6 days since activation, one item was ingested dated 2026-09-22 with 206 characters. The source operates feed-only; no article fetches are performed and index text serves as the full digest content. All 12 polling requests to www.cdc.gov completed successfully with no errors. Coverage is limited to dateable entries on the listing's first page; undatable entries are dropped and never observation-dated.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/irs-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/irs-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: irs-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# IRS Newsroom

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Department of the Treasury

Official site: https://www.irs.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Internal Revenue Service, a Treasury bureau, administers federal tax law. Its newsroom index carries news releases on filing seasons, tax guidance, and enforcement programs, typically one or more items per business day.

**Model-written orientation**

The IRS Newsroom publishes news releases on tax filing guidance, deadlines, enforcement actions, and updates to tax programs and procedures.

The Internal Revenue Service is the federal bureau within the Department of the Treasury that administers and enforces federal income tax law. The IRS processes millions of tax returns and payments annually, administers tax credits and deductions, and conducts examination and enforcement of tax law.

The IRS Newsroom serves as the agency's official channel for communicating with the public and tax professionals about tax policy, deadlines, and enforcement initiatives. The newsroom publishes news releases addressing the tax filing process, changes to tax procedures or deadlines, announcements of tax compliance programs, criminal investigations and enforcement actions, and guidance on tax benefits and credits.

Readers will encounter from this source a variety of IRS announcements: notices of filing season dates and deadline extensions; guidance on tax credits or deductions; announcements of enforcement initiatives targeting specific compliance issues; and notices of changes to IRS procedures or systems. Some releases provide guidance to specific taxpayer categories, such as businesses, nonprofits, or self-employed individuals. Others address identity theft, fraud alerts, or scams targeting taxpayers.

IRS news releases are written primarily for tax professionals and the general public. They are published regularly throughout the year, with increased frequency during filing seasons, typically January through April. The dates on releases represent the IRS's own publication dates.

The Newsroom operates as an HTML index on the IRS website. The digest polls this index regularly, without fetching the full articles, to identify new releases. Articles listed without a readable date are not included. The email sibling, irs-email, may carry the same releases through a separate GovDelivery subscription channel; a release reaching the digest through both channels is noted as corroborated. The digest's coverage is limited to items appearing on the first page of the index at the time of polling; items published between polls that exceed one page of listings may not be captured.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `irs-newsroom` |
| Agency / parent organization | Department of the Treasury |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.irs.gov/newsroom |
| URL (index) | https://www.irs.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Email sibling registered 2026-07-29: irs-email (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 102 article link(s); 1 dated inside the 7-day lookback, 3 dated outside it, 98 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 3 entries dated inside the 7-day lookback (2026-09-21..28), news releases with the IRS's own dates. irs-email stays active beside it; a release reaching both channels at the same URL merges as corroboration (GUIDE §3). Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 6 item(s) in the last 14 days; most recent 2026-10-02; 0 of 147 request(s) to www.irs.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 6 in 14 days (0.43 per day) · most recent 2026-10-02 |
| Content length | 349 characters average, 360 median (shortest 258, longest 412) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.irs.gov | 147 request(s) · 147 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-04T04:00:11.734+00:00 UTC.

6 item(s) in the last 14 days; most recent 2026-10-02; 0 of 147 request(s) to www.irs.gov returned no content.

### All time

- **Our requests to www.irs.gov, all time (since 2026-09-28):** 147 request(s) · 147 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.irs.gov | Mean response time (ms) |
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
| 2026-09-28 | 3 | 12 | 288 |
| 2026-09-29 | 0 | 28 | 223 |
| 2026-09-30 | 0 | 26 | 656 |
| 2026-10-01 | 2 | 27 | 271 |
| 2026-10-02 | 1 | 27 | 219 |
| 2026-10-03 | 0 | 26 | 200 |
| 2026-10-04 | 0 | 1 | 205 |

## Our ingestion assessment

**Model-written ingestion assessment**

The IRS Newsroom is ingested via HTML index diffing with one listing poll per cycle. Activation on 2026-09-28 set the measurement baseline. In the 6 days since activation, three items were ingested with dates ranging from 2026-09-21 to 2026-09-28, averaging 358 characters each. The source operates feed-only with no article fetches; index text serves as the full digest content. All 13 polling requests to www.irs.gov completed successfully with no errors. A correlated email channel (irs-email) carries the same releases; releases reaching both channels merge as corroboration. Coverage is limited to dateable entries on the listing's first page; undatable entries are dropped and never observation-dated.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/fdic-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fdic-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fdic-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FDIC Press Releases

active · ingestion health: quiet · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.fdic.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Federal Deposit Insurance Corporation insures bank deposits and supervises state-chartered banks. Its press-release index carries announcements on bank supervision, failures and resolutions, and rulemaking, typically a few items per week.

**Model-written orientation**

The Federal Deposit Insurance Corporation insures bank deposits and supervises state-chartered banks. Its press-release index carries announcements on bank supervision, failures and resolutions, and rulemaking.

The Federal Deposit Insurance Corporation (FDIC) is an independent agency that insures deposits in U.S. banks and supervises state-chartered banks that are not members of the Federal Reserve System. The FDIC was created in 1933 in response to bank failures during the Great Depression and operates as part of the federal banking regulatory framework.

The FDIC's core missions are deposit insurance and bank supervision. Deposit insurance protects depositors' accounts up to $250,000 per depositor per bank, maintaining public confidence in the banking system. The agency supervises and examines state-chartered banks to assess their safety and soundness, evaluate their management, and ensure compliance with banking laws.

The FDIC press-release index is the agency's primary channel for public announcements. These releases typically cover several categories of news: notifications of bank failures or conservatorships and their resolutions, including information about how deposits and other matters are being handled; announcements of new or revised regulations and supervisory guidance; reports on the agency's examination activities and focus areas; updates on the Deposit Insurance Fund; and information about the agency's programs and initiatives. The index typically contains a few items per week, though the frequency varies with regulatory activity and banking conditions.

Documents you will see from this source in the digest include press releases on specific banking events (such as the resolution of a failed bank), regulatory announcements (new rules, guidance documents, or supervisory letters), reports on examination findings, updates on the state of the banking system, and notices about the agency's public meetings or comment periods for proposed rules. These releases are dated by the FDIC and sourced through the agency's own press-release index.

The FDIC is part of the Executive Branch and operates independently, though it coordinates with other banking regulators including the Federal Reserve and the Office of the Comptroller of the Currency. The agency does not charge taxpayers; it is funded through assessments on insured banks.

_Model-written orientation, generated 2026-09-30 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fdic-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.fdic.gov/news/press-releases |
| URL (index) | https://www.fdic.gov/news/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Research 2026-07-28: conflicting evidence on a GovDelivery-hosted press RSS (public.govdelivery.com/topics/USFDIC_26/feed.rss cited by an integration vendor, but the modern GovDelivery platform generally exposes no public per-topic RSS) — one probe of that URL settles both this source and the GovDelivery-pattern question for every agency marked 'GovDelivery to evaluate'. Separately, BankFind Suite API at api.fdic.gov/banks/docs offers structured bank data (not press). Email sibling registered 2026-07-29: fdic-email (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 61 article link(s); 3 dated inside the 7-day lookback, 21 dated outside it, 34 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the FDIC page links a GovDelivery feed (https://public.govdelivery.com/topics/USFDIC_26/feed.rss); that host's robots.txt REFUSES us. Recorded and not retried — a refusal is accountability data (GUIDE §4). The FDIC's own email channel is already active as fdic-email, which covers this source's releases through a channel we are welcome on. Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 2 entries dated inside the 7-day lookback (2026-09-25), press releases with the FDIC's own dates. fdic-email stays active beside it; same-URL copies merge as corroboration (GUIDE §3). Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**quiet** — Most recent item 2026-10-05, 11 days ago (quiet past 7 days).

This label has held since 2026-10-13T04:07:47Z (UTC) and was last re-checked 2026-10-16T03:47:50Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-05 |
| Content length | 88 characters average, 88 median (shortest 88, longest 88) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.fdic.gov | 330 request(s) · 330 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-16T04:01:12.300+00:00 UTC.

Most recent item 2026-10-05, 11 days ago (quiet past 7 days).

### All time

- **Our requests to www.fdic.gov, all time (since 2026-09-28):** 445 request(s) · 445 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.fdic.gov | Mean response time (ms) |
|---|---|---|---|
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
| 2026-09-28 | 2 | 10 | 231 |
| 2026-09-29 | 1 | 27 | 257 |
| 2026-09-30 | 1 | 25 | 261 |
| 2026-10-01 | 0 | 27 | 325 |
| 2026-10-02 | 0 | 26 | 275 |
| 2026-10-03 | 0 | 26 | 284 |
| 2026-10-04 | 0 | 24 | 376 |
| 2026-10-05 | 1 | 25 | 369 |
| 2026-10-06 | 0 | 27 | 315 |
| 2026-10-07 | 0 | 26 | 288 |
| 2026-10-08 | 0 | 26 | 297 |
| 2026-10-09 | 0 | 24 | 342 |
| 2026-10-10 | 0 | 25 | 324 |
| 2026-10-11 | 0 | 26 | 287 |
| 2026-10-12 | 0 | 25 | 305 |
| 2026-10-13 | 0 | 25 | 203 |
| 2026-10-14 | 0 | 25 | 344 |
| 2026-10-15 | 0 | 25 | 303 |
| 2026-10-16 | 0 | 1 | 149 |

## Our ingestion assessment

**Model-written ingestion assessment**

The FDIC Press Releases source utilizes an HTML-index adapter to ingest listings in a feed-only mode, as a GovDelivery feed link previously discovered was inaccessible due to robots.txt restrictions. We observed 1 item over the past 14 days, delivered on 2026-10-05, resulting in an average of 0.07 items per day. This represents a decrease in activity compared to the 2 items observed in the previous assessment. All 333 requests to www.fdic.gov succeeded with a 0.0% error rate, maintaining the 100% success rate reported previously. Extracted items averaged 88 characters. A known limitation is that only the first page of the listing is processed, and entries lacking readable dates are not ingested. The source is currently quiet, with no items detected in the last 7 days.

_Model-written assessment of our own ingestion, generated 2026-10-14 by gemini-2.5-flash, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

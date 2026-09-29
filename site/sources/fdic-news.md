<!-- Markdown twin of https://fapd.info/sources/fdic-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fdic-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fdic-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FDIC Press Releases

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.fdic.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Federal Deposit Insurance Corporation insures bank deposits and supervises state-chartered banks. Its press-release index carries announcements on bank supervision, failures and resolutions, and rulemaking, typically a few items per week.

**Model-written orientation**

The Federal Deposit Insurance Corporation insures bank deposits and supervises state-chartered banks; its press releases cover bank supervision, resolutions, and regulatory matters.

The Federal Deposit Insurance Corporation is an independent agency established in 1933 to maintain stability and public confidence in the banking system. The FDIC insures deposits at member banks up to applicable limits and supervises state-chartered banks that are not members of the Federal Reserve System.

FDIC press releases announce actions taken in pursuit of these missions. These include announcements of bank supervision activities, supervisory findings, enforcement actions, and capital adequacy determinations for supervised banks. The FDIC also announces bank failures and resolutions, through which the agency either arranges for a failed bank's assets and liabilities to be transferred to another institution or manages the liquidation process. Readers will encounter announcements of assistance programs for failing institutions, updates on bank supervision policy, responses to changing economic conditions, and regulatory guidance issued to supervised institutions.

The agency also announces rulemaking activities, including proposed and final rules governing deposit insurance, capital requirements, lending practices, and other regulatory matters affecting banks under its supervision. Personnel announcements and updates on FDIC operations, including examination results summaries and regional office activities, appear in the press releases.

As an insurance and supervisory agency, the FDIC's press releases constitute the official record of its actions affecting member institutions and the banking system. They serve as the primary mechanism through which the FDIC communicates supervisory expectations, policy changes, and significant actions to affected banks, the financial industry, and the public. These announcements are typically the first public disclosure of FDIC supervisory or policy actions before they appear in regulatory databases or the Federal Register.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

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

**delivering** — 2 item(s) in the last 14 days; most recent 2026-09-28; 0 of 12 request(s) to www.fdic.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 12 request(s) (12 answered, 0 returned no content) · 2 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-09-28 |
| Content length | 95 characters average, 95 median (shortest 78, longest 112) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.fdic.gov | 12 request(s) · 12 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-29T04:10:13.866+00:00 UTC.

2 item(s) in the last 14 days; most recent 2026-09-28; 0 of 12 request(s) to www.fdic.gov returned no content.

### All time

- **Our requests to www.fdic.gov, all time (since 2026-09-28):** 12 request(s) · 12 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.fdic.gov | Mean response time (ms) |
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
| 2026-09-28 | 2 | 11 | 258 |
| 2026-09-29 | 0 | 1 | 236 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September. The FDIC press-release listing yields items carrying the publisher's own dates. The companion fdic-email channel delivers the same releases via email; identical URLs are merged as corroboration under the multi-channel policy. A GovDelivery feed link was found but the hosting domain refused our requests via robots.txt; such refusals are recorded and not retried, as they constitute accountability data. We observed 2 items over 14 days. All 12 requests to www.fdic.gov succeeded with no failures. The listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. Entries lacking readable dates are dropped and never observation-dated.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

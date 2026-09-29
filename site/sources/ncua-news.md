<!-- Markdown twin of https://fapd.info/sources/ncua-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ncua-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ncua-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NCUA Press Releases

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Independent agency

Official site: https://ncua.gov/newsroom/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The National Credit Union Administration charters and supervises federal credit unions and insures share deposits. Its press-release index carries announcements on supervision, conservatorships, and board actions, typically a few items per week.

**Model-written orientation**

The National Credit Union Administration charters and supervises federal credit unions and insures member deposits; its press releases cover supervision, conservatorships, and board actions.

The National Credit Union Administration is an independent agency established in 1970 to regulate federal credit unions and administer the National Credit Union Share Insurance Fund, which protects member deposits at federally insured credit unions. The NCUA charters federal credit unions, supervises their operations, and exercises regulatory authority over credit union capital, lending, and member protections.

NCUA press releases announce supervisory and regulatory actions taken by the agency, including enforcement actions, examinations, and supervisory guidance issued to credit unions. The agency also announces actions related to credit union failures or conservatorships, through which the NCUA either facilitates merger of a failing credit union or manages its liquidation. Readers will encounter announcements of supervision policy changes, guidance on regulatory compliance, and actions taken against credit unions in response to safety and soundness concerns.

The NCUA Board makes policy decisions affecting the credit union system through formal board actions, which are announced in press releases. These include decisions on capital requirements, insurance fund assessments, regulatory rule changes, and system-wide policy initiatives. Personnel announcements, updates on NCUA operations, and notices of rulemaking activity also appear in the agency's press releases.

As the federal regulator and insurer for the credit union system, the NCUA's press releases serve as the official record of agency actions and policy decisions. They constitute the primary mechanism through which the NCUA communicates supervisory expectations, policy changes, and significant regulatory actions to credit unions and the public. These announcements typically appear before compilation in official databases or regulatory registers.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ncua-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://ncua.gov/newsroom/press-releases |
| URL (index) | https://ncua.gov/news/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 128 article link(s); 1 dated inside the 7-day lookback, 59 dated outside it, 68 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: The listing now redirects from /newsroom/press-releases to /news/press-releases, registered as the index. 1 entry dated inside the 7-day lookback (2026-09-23); a low-rate source. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 14 request(s) to ncua.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 14 request(s) (14 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-09-28 |
| Content length | 78 characters average, 78 median (shortest 78, longest 78) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to ncua.gov | 14 request(s) · 14 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-29T04:10:14.084+00:00 UTC.

1 item(s) in the last 14 days; most recent 2026-09-28; 0 of 14 request(s) to ncua.gov returned no content.

### All time

- **Our requests to ncua.gov, all time (since 2026-09-28):** 14 request(s) · 14 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to ncua.gov | Mean response time (ms) |
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
| 2026-09-28 | 1 | 12 | 404 |
| 2026-09-29 | 0 | 2 | 321 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September. The listing at NCUA's newsroom redirected from /newsroom/press-releases to /news/press-releases; we poll the target URL. We observed 1 item over 14 days. All 14 requests to ncua.gov succeeded with no failures. The listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. Entries lacking readable dates are dropped and never observation-dated. No machine-readable feeds are advertised on this source.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/eeoc-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/eeoc-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: eeoc-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# EEOC Newsroom

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.eeoc.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Equal Employment Opportunity Commission enforces federal workplace anti-discrimination law. Its newsroom index carries press releases on lawsuits, settlements, and enforcement guidance, typically a few items per week.

**Model-written orientation**

The Equal Employment Opportunity Commission enforces federal workplace anti-discrimination laws and investigates employment discrimination complaints.

The Equal Employment Opportunity Commission (EEOC) is an independent federal agency charged with enforcing federal statutes prohibiting employment discrimination. The agency's mandate covers discrimination based on race, color, religion, sex, national origin, age, disability, genetic information, and other protected characteristics defined by law. The EEOC operates through a network of field offices and investigates complaints filed by individuals alleging employment discrimination. The Commission has authority to pursue its own litigation on behalf of complainants or groups of workers, to issue Right-to-Sue letters enabling private litigation, and to conduct strategic enforcement initiatives targeting patterns or practices of discrimination in particular industries or occupations. The agency also publishes guidance documents, conducts public outreach, and works with employers on compliance with employment law. The EEOC's newsroom publishes announcements documenting the public record of the agency's enforcement work. Readers of EEOC press releases in this digest will encounter announcements of significant lawsuits filed or settled by the Commission, information about enforcement settlements with employers, guidance documents clarifying legal requirements and compliance obligations, and notices of investigative initiatives the agency has undertaken. Press releases typically identify the parties involved, describe the allegations or violations that were addressed, outline any settlement terms or court actions taken, and provide context about the laws and rights involved. The newsroom reflects the agency's enforcement priorities and the breadth of employment law it administers, with releases covering discrimination cases in various industries and involving different protected characteristics. The agency typically publishes a few items per week, showing ongoing investigative and litigation activity. EEOC materials document federal employment discrimination enforcement and provide a window into workplace disputes and legal developments in this area of law.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `eeoc-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.eeoc.gov/newsroom |
| URL (index) | https://www.eeoc.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered. Re-probed 2026-07-31: HTTP 200, robots allows, still no feed. ACTIVATED 2026-07-31 with the html-index adapter, and chosen deliberately as the prose-dated case: the newsroom states no <time> element anywhere, only 'July 30, 2026' as text, which the adapter converts to ISO before storing — an unconverted prose date is unreadable to report._claimed_day and would silently be replaced by the observation day. Gate 3: 21 dated entries are visible on the page (about three weeks of output at EEOC's few-per-week rate); the ~81 further links are navigation and are skipped for stating no date. The listing carries a long lede (the stored text runs 560-660 chars per item), so mode feed-only loses less here than the mode name suggests. Under-coverage: the page shows only its first screen of releases, and litigation filings and guidance documents live elsewhere on eeoc.gov. |

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

**delivering** — 8 item(s) in the last 14 days; most recent 2026-09-17; 0 of 343 request(s) to www.eeoc.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-21T03:47:52Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 8 in 14 days (0.57 per day) · most recent 2026-09-17 |
| Content length | 621 characters average, 616 median (shortest 573, longest 712) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.eeoc.gov | 343 request(s) · 343 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-21T04:01:54.719+00:00 UTC.

8 item(s) in the last 14 days; most recent 2026-09-17; 0 of 343 request(s) to www.eeoc.gov returned no content.

### All time

- **Our requests to www.eeoc.gov, all time (since 2026-08-01):** 1,480 request(s) · 1,475 answered · 5 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.eeoc.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-23 | 0 | 29 | 288 |
| 2026-08-24 | 0 | 28 | 340 |
| 2026-08-25 | 0 | 26 | 316 |
| 2026-08-26 | 4 | 26 | 292 |
| 2026-08-27 | 3 | 26 | 327 |
| 2026-08-28 | 2 | 25 | 291 |
| 2026-08-29 | 0 | 27 | 267 |
| 2026-08-30 | 0 | 26 | 318 |
| 2026-08-31 | 0 | 26 | 281 |
| 2026-09-01 | 1 | 26 | 271 |
| 2026-09-02 | 1 | 26 | 282 |
| 2026-09-03 | 0 | 25 | 325 |
| 2026-09-04 | 0 | 27 | 309 |
| 2026-09-05 | 0 | 33 | 412 |
| 2026-09-06 | 0 | 26 | 286 |
| 2026-09-07 | 0 | 26 | 274 |
| 2026-09-08 | 2 | 26 | 298 |
| 2026-09-09 | 0 | 25 | 286 |
| 2026-09-10 | 1 | 27 | 262 |
| 2026-09-11 | 0 | 26 | 299 |
| 2026-09-12 | 0 | 28 | 343 |
| 2026-09-13 | 0 | 26 | 315 |
| 2026-09-14 | 1 | 28 | 422 |
| 2026-09-15 | 1 | 27 | 260 |
| 2026-09-16 | 2 | 26 | 322 |
| 2026-09-17 | 1 | 26 | 274 |
| 2026-09-18 | 0 | 26 | 319 |
| 2026-09-19 | 0 | 26 | 259 |
| 2026-09-20 | 0 | 25 | 253 |
| 2026-09-21 | 0 | 1 | 289 |

## Our ingestion assessment

**Model-written ingestion assessment**

The newsroom listing displays prose-dated text entries without machine-readable timestamps; dated items are extracted from the visible index. Over 14 days, 11 items arrived at 0.79 per day, an increase from the previous 0.43 per day. Each item carries a 560- to 725-character summary paragraph (median 617 characters). All 344 polling requests succeeded. The most recent item was published on 2026-09-02. The listing shows only its first screen of roughly 21 releases; litigation filings and guidance documents are published through separate channels.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

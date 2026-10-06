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

**delivering** — 37 item(s) in the last 14 days; most recent 2026-10-05; 0 of 338 request(s) to www.eeoc.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-06T03:59:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 37 in 14 days (2.64 per day) · most recent 2026-10-05 |
| Content length | 613 characters average, 615 median (shortest 538, longest 691) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.eeoc.gov | 338 request(s) · 338 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-06T04:00:16.646+00:00 UTC.

37 item(s) in the last 14 days; most recent 2026-10-05; 0 of 338 request(s) to www.eeoc.gov returned no content.

### All time

- **Our requests to www.eeoc.gov, all time (since 2026-08-01):** 1,817 request(s) · 1,812 answered · 5 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.eeoc.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-07 | 0 | 25 | 275 |
| 2026-09-08 | 2 | 25 | 298 |
| 2026-09-09 | 0 | 24 | 281 |
| 2026-09-10 | 1 | 26 | 262 |
| 2026-09-11 | 0 | 25 | 300 |
| 2026-09-12 | 0 | 27 | 340 |
| 2026-09-13 | 0 | 25 | 316 |
| 2026-09-14 | 1 | 27 | 410 |
| 2026-09-15 | 1 | 26 | 259 |
| 2026-09-16 | 2 | 25 | 324 |
| 2026-09-17 | 1 | 25 | 274 |
| 2026-09-18 | 0 | 25 | 316 |
| 2026-09-19 | 0 | 25 | 258 |
| 2026-09-20 | 0 | 24 | 253 |
| 2026-09-21 | 1 | 27 | 325 |
| 2026-09-22 | 2 | 25 | 264 |
| 2026-09-23 | 3 | 24 | 298 |
| 2026-09-24 | 3 | 26 | 292 |
| 2026-09-25 | 6 | 25 | 288 |
| 2026-09-26 | 0 | 27 | 333 |
| 2026-09-27 | 0 | 26 | 299 |
| 2026-09-28 | 5 | 28 | 356 |
| 2026-09-29 | 4 | 28 | 388 |
| 2026-09-30 | 12 | 25 | 274 |
| 2026-10-01 | 3 | 27 | 319 |
| 2026-10-02 | 0 | 25 | 271 |
| 2026-10-03 | 0 | 26 | 312 |
| 2026-10-04 | 0 | 24 | 297 |
| 2026-10-05 | 1 | 26 | 286 |
| 2026-10-06 | 0 | 1 | 497 |

## Our ingestion assessment

**Model-written ingestion assessment**

The newsroom listing delivered items at 2.64 per day over 14 days, a substantial increase from the prior 0.79 per day. Thirty-seven items were ingested with an average of 613 characters drawn from prose-dated entries on the listing page. All 338 polling requests succeeded. The visible index shows only its first screen of approximately 21 releases; litigation filings and guidance documents are published through separate channels.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

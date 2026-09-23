<!-- Markdown twin of https://fapd.info/sources/congress-gov-api.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/congress-gov-api.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: congress-gov-api)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Congress.gov API

active · ingestion health: delivering · Legislative · Tier 1 · API · Library of Congress

Official site: https://github.com/LibraryOfCongress/api.congress.gov · All sources: [sources.md](../sources.md)

## What this source is

The Library of Congress's official API for structured legislative data: committee meetings with witnesses and documents, nominations, treaties, bill actions and cosponsors, House roll-call votes (beta), daily Congressional Record metadata, and CRS reports. Fills the committee-activity and nominations coverage the pipeline currently lacks entirely.

**Model-written orientation**

The Library of Congress's official API provides structured access to legislative data including bill actions, committee meetings, nominations, and Congressional Record metadata.

Congress.gov is the official website of the United States Congress and the legislative branch. It provides the public with access to information about bills, resolutions, members of Congress, committee activities, nominations, treaties, and the Congressional Record.

The Library of Congress maintains Congress.gov and publishes an official API that provides structured access to legislative data. The API exposes several categories of information: bill and resolution records with metadata and action histories, committee meeting schedules and witness lists, committee documents, nominations sent to the Senate for confirmation, treaties submitted to the Senate, congressional research reports, and metadata about Congressional Record publications.

This digest currently ingests bill actions through the Congress.gov API. Bill actions are recorded every time a bill or resolution is acted upon—when it is introduced, referred to committee, debated, voted on, passed or rejected, sent to the President, or signed into law. The API exposes the most recent action for each bill and allows querying by date to find bills acted upon recently. The API does not expose the full history of all actions on a bill, but rather the latest action and related metadata.

The API requires an API key, which the FAPD pipeline holds. Rate limits are set well above current usage levels.

The Congress.gov API fills important coverage gaps in the federal publication record. It provides the earliest official access to committee activity, nominations, and bill actions—information that is not published through the Federal Register or govinfo. This digest publishes bill actions from this API, representing legislative activity that would otherwise not appear in the federal record as captured by this system. This source is valuable for readers interested in tracking legislative activity, monitoring bills of interest, following nominations, or understanding the actions and proceedings of Congress.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `congress-gov-api` |
| Agency / parent organization | Library of Congress |
| Branch | legislative |
| Type | API |
| Status | active |
| Tier | 1 |
| URL (home) | https://github.com/LibraryOfCongress/api.congress.gov |
| URL (index) | https://api.congress.gov/v3/bill |
| Registered | 2026-07-28 |
| Registry notes | Documented rate limit 5,000 req/hour — far above our §4 posture. Endpoint docs read from the official LoC GitHub repo 2026-07-28 (incl. CommitteeMeetingEndpoint.md, CRSReportEndpoint.md). The crsreport endpoint is registered separately as crs-reports. Senate votes are NOT here (House only) — see senate-xml. Gate 3 (2026-07-31, live through the identified client, ONE endpoint only): the api.data.gov key we already hold authenticates here (200 with data), and /v3/bill answers JSON. What the source publishes in total vs what we see: the endpoint enumerates 429,331 bill records across all Congresses and exposes, per record, ONLY the measure's identity and its LATEST action — not the full action history, not cosponsors, not text; the committee-meeting, nomination, treaty and beta House-roll-call endpoints this entry also describes are NOT ingested and stay future work. Volume measured: 749 records were updated across 2026-07-30 and 350 by 19:20 ET on 07-31, against a page of 250 per poll and an hourly collector — roughly 8x headroom on the observed ~31/hour update rate, with the loop's dedupe accumulating a day across polls; a burst of >250 updates inside one poll interval is the one loss case and is not currently detected. Three limits disclosed rather than papered over: (a) actionDate (when it happened) is not updateDate (when the record changed) — 250 records all updated 07-31 carried actions from 1997 to 07-30, so items are dated and bounded by actionDate; (b) the record is published the morning AFTER the action (0 actions dated 07-31 anywhere on the page; 97 dated 07-30; the bulk of a day's actions entered between 08:00 and 12:00 UTC the next day), so BILLACTIONS is dated by the publisher like govinfo collections and the lag is a standing digest disclosure; (c) two actions on one bill on one day collapse to a single item, because only the latest is exposed. The cited link is the www.congress.gov bill page, which answers 403 to our identified client (verified on three bill URLs) — hence wants_article() is False: we ingest what the API offers and never force what the website refuses. Sending sort as a pre-encoded 'updateDate%2Bdesc' made the service return ASCENDING order (records from 1995), so the parameter is passed with a literal space and the order is verified by reading dates, never assumed. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Conditional GET of one page of the bill endpoint per poll (limit=250, sort=updateDate+desc, api.data.gov key in request PARAMETERS so the fetch log redacts it). The congress-bill-actions adapter emits one item per bill whose latestAction.actionDate falls inside config.INDEX_LOOKBACK_DAYS and never fetches an article page. Stored under the BILLACTIONS collection (GUIDE §3 bill actions), dated by the publisher's actionDate, never AGENCYPR. |
| Adapter | congress-bill-actions |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 789 item(s) in the last 14 days; most recent 2026-09-21; 13 of 347 request(s) to api.congress.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-23T03:59:19Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 24 request(s) (23 answered, 1 returned no content) · 49 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 789 in 14 days (56.36 per day) · most recent 2026-09-21 |
| Content length | 429 characters average, 400 median (shortest 247, longest 1,618) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to api.congress.gov | 347 request(s) · 334 answered · 13 declined (4xx) · 0 server declined (5xx) · 0 no response — 3.7% returned no content |

last answered request 2026-09-23T05:17:43.095+00:00 UTC.

789 item(s) in the last 14 days; most recent 2026-09-21; 13 of 347 request(s) to api.congress.gov returned no content.

### All time

- **Our requests to api.congress.gov, all time (since 2026-08-01):** 1,540 request(s) · 1,479 answered · 61 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.congress.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-25 | 0 | 26 | 303 |
| 2026-08-26 | 8 | 26 | 313 |
| 2026-08-27 | 63 | 26 | 333 |
| 2026-08-28 | 0 | 26 | 301 |
| 2026-08-29 | 0 | 26 | 306 |
| 2026-08-30 | 0 | 26 | 331 |
| 2026-08-31 | 43 | 26 | 314 |
| 2026-09-01 | 51 | 26 | 946 |
| 2026-09-02 | 37 | 26 | 499 |
| 2026-09-03 | 69 | 26 | 539 |
| 2026-09-04 | 8 | 26 | 361 |
| 2026-09-05 | 0 | 33 | 418 |
| 2026-09-06 | 0 | 27 | 306 |
| 2026-09-07 | 0 | 26 | 296 |
| 2026-09-08 | 41 | 26 | 310 |
| 2026-09-09 | 0 | 26 | 318 |
| 2026-09-10 | 62 | 25 | 336 |
| 2026-09-11 | 4 | 26 | 315 |
| 2026-09-12 | 0 | 29 | 436 |
| 2026-09-13 | 0 | 26 | 294 |
| 2026-09-14 | 174 | 30 | 464 |
| 2026-09-15 | 131 | 26 | 317 |
| 2026-09-16 | 252 | 26 | 342 |
| 2026-09-17 | 137 | 26 | 447 |
| 2026-09-18 | 2 | 26 | 465 |
| 2026-09-19 | 0 | 26 | 295 |
| 2026-09-20 | 0 | 26 | 318 |
| 2026-09-21 | 27 | 28 | 368 |
| 2026-09-22 | 0 | 26 | 296 |
| 2026-09-23 | 0 | 1 | 297 |

## Our ingestion assessment

**Model-written ingestion assessment**

The Congress.gov bill-actions endpoint delivered 287 items over 14 days at 20.5 per day, up from 14.36 per day in the prior assessment. The most recent item is dated 2026-09-03. Each item represents a bill whose latest action falls within our lookback window; the endpoint exposes only the latest action per bill, not the full action history. Request success was 331 of 345 answered (4.1% no-response), consistent with the 96.2% success rate reported previously. Daily item counts showed substantial variation: 70 items 2026-09-04, 49 items 2026-09-03, 39 items 2026-09-02, 43 items 2026-09-01. The API's documented 5,000-request-per-hour limit far exceeds our observed throughput. Committee meetings, nominations, treaties, and House roll-call votes are documented endpoints not yet covered; CRS reports are registered separately.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

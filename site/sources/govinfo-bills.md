<!-- Markdown twin of https://fapd.info/sources/govinfo-bills.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-bills.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-bills)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Congressional Bills (BILLS)

active · ingestion health: degraded · Legislative · Tier 1 · govinfo collection · U.S. Congress

Official site: https://www.govinfo.gov/app/collection/BILLS · All sources: [sources.md](../sources.md)

## What this source is

Congress publishes bill and resolution text through the Government Publishing Office at each printed stage (introduced, engrossed, enrolled, and others). This collection carries the full text as XML, with roughly 60-70 new or revised bill printings on a typical publication day (~28 KB of text each).

**Model-written orientation**

Congressional Bills contains the complete official text of U.S. House and Senate bills and resolutions at each stage of publication by the Government Publishing Office, from initial introduction through enactment.

Congressional Bills is the authoritative collection of legislation text. When a bill is introduced in the House or Senate, the Government Publishing Office publishes it in a standardized format. As the bill advances through the legislative process—amended in committee, passed by one chamber, amended by the other chamber, or sent to the President—new versions are published. Each published version is included in this collection.

Congress publishes bills at specific stages. An introduced bill shows the original text. When a committee reports out a bill with amendments, a new version (engrossed) is published. When a chamber passes a bill, that version is published. If the other chamber amends it, another version appears. When both chambers pass identical text and the bill moves to the President, a final enrolled version is published. This collection contains text from all these stages, allowing readers to trace how language changed as a bill progressed.

The collection sits at the center of the legislative record. It works alongside the Congressional Record (which documents floor debate) and committee reports (which explain legislative intent). Together, these sources provide a complete picture of what Congress did and why. Congressional Bills provides the actual statutory language, updated at each major procedural checkpoint.

The data is published as structured text by the Government Publishing Office. Each bill is typically 20-40 kilobytes of XML text, depending on the bill's length. The collection is complete—every bill introduced receives a bill number, is published in text form, and appears in this source.

In this digest, readers encounter Congressional Bills when new legislation is introduced or when bills reach a significant procedural milestone (passage by a chamber, committee markup, or presidential action). The digest extracts from bills to show what they propose, what provisions they contain, or what they would change in existing law. Readers see the official legislative language, as published by the Government Publishing Office, grounding reports about legislative activity in the statutory text itself.

Note: bills that fail to be introduced formally, or that exist only as draft proposals before introduction, do not appear here. This collection contains only formally introduced measures given bill numbers by Congress.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-bills` |
| Agency / parent organization | U.S. Congress |
| Branch | legislative |
| Type | govinfo collection |
| Status | active |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/BILLS |
| Registered | 2026-07-26 |
| Registry notes | Coverage (gate 3, backfilled 2026-07-30): the complete official bill-text record — every printed stage of every bill GPO publishes is listed by delta sync and extracted; nothing is sampled or filtered. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | govinfo collection |
| Method | govinfo collections API delta sync |
| Poll cadence | about every 30 minutes while the collector runs |
| Request budget | the govinfo class: at most 6,000 requests per day and 800 per hour, counted from the fetch log (failed requests count too); collectors stop at 85% so the end-of-day finalizer always has headroom |
| Politeness | keyed govinfo API access; every request is logged before it is made and identified as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com) |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**degraded** — 5204 of 27284 request(s) to api.govinfo.gov returned no content (19.1%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-30T03:49:13Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,145 request(s) (1,813 answered, 332 returned no content) · 6 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 117 in 14 days (8.36 per day) · most recent 2026-10-29 |
| Content length | 9,623 characters average, 4,152 median (shortest 799, longest 153,910) |
| Our requests to api.govinfo.gov | 27,284 request(s) · 22,080 answered · 0 declined (4xx) · 5,182 server declined (5xx) · 22 no response — 19.1% returned no content |

last answered request 2026-10-30T04:00:09.560+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

5204 of 27284 request(s) to api.govinfo.gov returned no content (19.1%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 198,214 request(s) · 151,307 answered · 46,907 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-10-01 | 12 | 2548 | 622 |
| 2026-10-02 | 101 | 2843 | 431 |
| 2026-10-03 | 14 | 5013 | 468 |
| 2026-10-04 | 0 | 582 | 887 |
| 2026-10-05 | 0 | 1461 | 486 |
| 2026-10-06 | 91 | 2451 | 615 |
| 2026-10-07 | 109 | 2464 | 533 |
| 2026-10-08 | 57 | 2343 | 489 |
| 2026-10-09 | 0 | 1898 | 591 |
| 2026-10-10 | 46 | 2079 | 550 |
| 2026-10-11 | 0 | 475 | 354 |
| 2026-10-12 | 0 | 448 | 344 |
| 2026-10-13 | 0 | 447 | 296 |
| 2026-10-14 | 38 | 2868 | 451 |
| 2026-10-15 | 15 | 3501 | 472 |
| 2026-10-16 | 21 | 2469 | 626 |
| 2026-10-17 | 0 | 2140 | 573 |
| 2026-10-18 | 0 | 2138 | 434 |
| 2026-10-19 | 13 | 504 | 398 |
| 2026-10-20 | 11 | 2440 | 384 |
| 2026-10-21 | 10 | 2357 | 477 |
| 2026-10-22 | 1 | 4062 | 594 |
| 2026-10-23 | 30 | 3041 | 562 |
| 2026-10-24 | 2 | 2255 | 541 |
| 2026-10-25 | 0 | 606 | 387 |
| 2026-10-26 | 0 | 514 | 335 |
| 2026-10-27 | 35 | 2542 | 666 |
| 2026-10-28 | 9 | 2535 | 526 |
| 2026-10-29 | 6 | 2145 | 515 |
| 2026-10-30 | 0 | 5 | 199 |

## Our ingestion assessment

**Model-written ingestion assessment**

Congressional bill text continues to arrive through govinfo collections API delta sync, capturing all printed editions across publication stages. The current 14-day window shows 534 items at roughly 38 per day, averaging 16,796 characters (range 553 to ~2 million), most recent on October 3. The shared api.govinfo.gov host exhibits 26.3% request failure. Compared to the assessment of September 5 (243 items at roughly 17 per day), collection volume in this window has approximately doubled, reflecting increased legislative activity in this measurement period.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

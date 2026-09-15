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
| Request budget | the govinfo class: at most 6,000 requests per day and 500 per hour, counted from the fetch log (failed requests count too); collectors stop at 85% so the end-of-day finalizer always has headroom |
| Politeness | keyed govinfo API access; every request is logged before it is made and identified as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com) |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**degraded** — 4750 of 23420 request(s) to api.govinfo.gov returned no content (20.3%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-15T03:50:21Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 785 request(s) (648 answered, 137 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 211 in 14 days (15.07 per day) · most recent 2026-09-12 |
| Content length | 18,675 characters average, 3,947 median (shortest 570, longest 1,992,086) |
| Our requests to api.govinfo.gov | 23,420 request(s) · 18,670 answered · 1 declined (4xx) · 4,749 server declined (5xx) · 0 no response — 20.3% returned no content |

last answered request 2026-09-15T04:00:51.614+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

4750 of 23420 request(s) to api.govinfo.gov returned no content (20.3%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 102,483 request(s) · 77,257 answered · 25,226 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-17 | 0 | 255 | 194 |
| 2026-08-18 | 9 | 1598 | 660 |
| 2026-08-19 | 24 | 3986 | 680 |
| 2026-08-20 | 0 | 2954 | 594 |
| 2026-08-21 | 10 | 2575 | 641 |
| 2026-08-22 | 12 | 2230 | 527 |
| 2026-08-23 | 0 | 2174 | 685 |
| 2026-08-24 | 0 | 1196 | 610 |
| 2026-08-25 | 23 | 1486 | 466 |
| 2026-08-26 | 1 | 2746 | 598 |
| 2026-08-27 | 7 | 2316 | 546 |
| 2026-08-28 | 37 | 2828 | 708 |
| 2026-08-29 | 0 | 2370 | 457 |
| 2026-08-30 | 0 | 2332 | 708 |
| 2026-08-31 | 0 | 1152 | 622 |
| 2026-09-01 | 51 | 1519 | 615 |
| 2026-09-02 | 43 | 2874 | 563 |
| 2026-09-03 | 20 | 2621 | 684 |
| 2026-09-04 | 61 | 2327 | 640 |
| 2026-09-05 | 3 | 1838 | 485 |
| 2026-09-06 | 0 | 2034 | 676 |
| 2026-09-07 | 0 | 1120 | 598 |
| 2026-09-08 | 0 | 794 | 451 |
| 2026-09-09 | 36 | 1513 | 522 |
| 2026-09-10 | 0 | 1782 | 695 |
| 2026-09-11 | 47 | 2005 | 714 |
| 2026-09-12 | 1 | 2319 | 594 |
| 2026-09-13 | 0 | 1408 | 576 |
| 2026-09-14 | 0 | 780 | 843 |
| 2026-09-15 | 0 | 5 | 209 |

## Our ingestion assessment

**Model-written ingestion assessment**

Bill text arrives as structured XML through govinfo delta sync, capturing all printed editions across publication stages. Over 14 days we collected 243 items averaging 20,938 characters (range 505 to 2.8 million) at roughly 17 per day, most recent on September 4. The shared api.govinfo.gov host exhibits 25.6% request failure across all collections. Compared to the previous measurement (307 items at ~22/day), both collection volume and daily rate have declined. The substantial average item size reflects the mix of complete bill texts across different publication stages.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

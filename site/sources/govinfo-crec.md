<!-- Markdown twin of https://fapd.info/sources/govinfo-crec.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-crec.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-crec)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Congressional Record (CREC)

active · ingestion health: degraded · Legislative · Tier 1 · govinfo collection · U.S. Congress

Official site: https://www.govinfo.gov/app/collection/CREC · All sources: [sources.md](../sources.md)

## What this source is

The Congressional Record is the official verbatim record of congressional proceedings, published by the Government Publishing Office each day a chamber is in session. This collection carries the daily edition — House and Senate floor debate, Extensions of Remarks, and the Daily Digest — as structured XML (~2 MB of text on a typical session day) with PDF page images.

**Model-written orientation**

The Congressional Record is the official verbatim account of U.S. House and Senate floor proceedings, published daily by the Government Publishing Office when the chambers are in session.

The Congressional Record serves as the federal government's permanent account of legislative floor activity. Published by the Government Publishing Office, the Record is produced on each day the House or Senate meets and captures floor speeches, procedural motions, votes, committee announcements, and statements entered into the record. It is the official source document for understanding what transpired during a day's legislative session.

The Record comprises four main sections. The Senate section contains floor debate and remarks, arranged by bill or topic. The House section similarly captures floor activity. Both chambers' sections include statements members submit for the record without having been delivered orally (called Extensions of Remarks in the House). The Daily Digest provides a summary of the day's actions—bills introduced, votes taken, unanimous-consent agreements, committee meetings scheduled, and similar procedural events. This index allows readers to track specific actions or subjects.

The Record occupies a specific place in the legislative process. It is not committee work (captured in committee reports), not bill text (published separately), and not floor voting records alone—it is the complete operational transcript of the chambers' public proceedings. Congress publishes it as a matter of constitutional and statutory obligation to maintain a public record of legislative actions.

Data from the Congressional Record reaches this digest as structured text, with each granule of content (speeches, diary entries, bills listed) marked by speaker, chamber, date, and topic. The Government Publishing Office publishes the Record with page images included, allowing readers to see the original formatting and any graphics originally published alongside the text.

In this digest, readers encounter Congressional Record items when floor debate occurs, bills are introduced, or other chamber proceedings are documented. A reader will see floor speeches or remarks on substantive topics, procedural actions, or announcements about committee meetings and legislative schedules. The digested items reflect what the chambers actually did on a given day, sourced from the official floor record.

One note: the Record reflects only public proceedings of the chambers. Closed hearings, private meetings, or side conversations among members are not included; they are recorded, if at all, in other sources like committee hearing transcripts.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-crec` |
| Agency / parent organization | U.S. Congress |
| Branch | legislative |
| Type | govinfo collection |
| Status | active |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/CREC |
| Registered | 2026-07-26 |
| Registry notes | Coverage (gate 3, backfilled 2026-07-30): the collection is itself the complete official record of the daily edition; delta sync lists every package and extraction reads every granule, so ingestion sees 100% of what GPO publishes here. |

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

**degraded** — 3999 of 22570 request(s) to api.govinfo.gov returned no content (17.7%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-20T03:51:20Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,032 request(s) (1,626 answered, 406 returned no content) · 11 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1,027 in 14 days (73.36 per day) · most recent 2026-09-19 |
| Content length | 7,239 characters average, 1,376 median (shortest 53, longest 1,055,258) |
| Our requests to api.govinfo.gov | 22,570 request(s) · 18,571 answered · 0 declined (4xx) · 3,994 server declined (5xx) · 5 no response — 17.7% returned no content |

last answered request 2026-09-20T04:04:34.763+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

3999 of 22570 request(s) to api.govinfo.gov returned no content (17.7%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 113,327 request(s) · 86,189 answered · 27,138 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-22 | 0 | 2230 | 527 |
| 2026-08-23 | 0 | 2174 | 685 |
| 2026-08-24 | 0 | 1196 | 610 |
| 2026-08-25 | 42 | 1486 | 466 |
| 2026-08-26 | 0 | 2746 | 598 |
| 2026-08-27 | 0 | 2316 | 546 |
| 2026-08-28 | 79 | 2828 | 708 |
| 2026-08-29 | 0 | 2370 | 457 |
| 2026-08-30 | 0 | 2332 | 708 |
| 2026-08-31 | 0 | 1152 | 622 |
| 2026-09-01 | 150 | 1519 | 615 |
| 2026-09-02 | 134 | 2874 | 563 |
| 2026-09-03 | 161 | 2621 | 684 |
| 2026-09-04 | 155 | 2327 | 640 |
| 2026-09-05 | 60 | 1838 | 485 |
| 2026-09-06 | 0 | 2034 | 676 |
| 2026-09-07 | 0 | 1120 | 598 |
| 2026-09-08 | 0 | 794 | 451 |
| 2026-09-09 | 89 | 1513 | 522 |
| 2026-09-10 | 182 | 1782 | 695 |
| 2026-09-11 | 93 | 2005 | 714 |
| 2026-09-12 | 0 | 2319 | 594 |
| 2026-09-13 | 0 | 1408 | 576 |
| 2026-09-14 | 0 | 780 | 843 |
| 2026-09-15 | 236 | 1504 | 812 |
| 2026-09-16 | 277 | 2266 | 580 |
| 2026-09-17 | 0 | 2387 | 608 |
| 2026-09-18 | 139 | 2655 | 746 |
| 2026-09-19 | 11 | 2032 | 655 |
| 2026-09-20 | 0 | 5 | 210 |

## Our ingestion assessment

**Model-written ingestion assessment**

Congressional Record daily editions arrive through govinfo collections API delta sync, delivering all editions (House, Senate, Extensions of Remarks, Daily Digest) as structured XML. Over the measured 14-day window we collected 566 items averaging 4,664 characters per item at roughly 40 per day, most recent on September 3. The underlying api.govinfo.gov host exhibits 25.6% request failure rate, affecting all delta-synced govinfo collections equally. Compared to the previous 14-day measurement (708 items at ~50/day), ingestion volume has declined while the error rate remains elevated but slightly improved. Despite host-level degradation, collection cadence continues consistently.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

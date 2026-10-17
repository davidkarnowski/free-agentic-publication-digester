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

**degraded** — 5666 of 23491 request(s) to api.govinfo.gov returned no content (24.1%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-17T03:56:12Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,457 request(s) (1,843 answered, 614 returned no content) · 93 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 572 in 14 days (40.86 per day) · most recent 2026-10-16 |
| Content length | 1,803 characters average, 1,417 median (shortest 53, longest 16,659) |
| Our requests to api.govinfo.gov | 23,491 request(s) · 17,825 answered · 0 declined (4xx) · 5,664 server declined (5xx) · 2 no response — 24.1% returned no content |

last answered request 2026-10-17T04:00:10.510+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

5666 of 23491 request(s) to api.govinfo.gov returned no content (24.1%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 170,935 request(s) · 129,232 answered · 41,703 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-09-18 | 139 | 2655 | 746 |
| 2026-09-19 | 11 | 2032 | 655 |
| 2026-09-20 | 0 | 963 | 682 |
| 2026-09-21 | 0 | 981 | 482 |
| 2026-09-22 | 195 | 1687 | 630 |
| 2026-09-23 | 1477 | 3975 | 588 |
| 2026-09-24 | 98 | 3610 | 542 |
| 2026-09-25 | 274 | 2283 | 578 |
| 2026-09-26 | 0 | 2284 | 670 |
| 2026-09-27 | 0 | 1185 | 802 |
| 2026-09-28 | 0 | 1179 | 585 |
| 2026-09-29 | 120 | 2810 | 689 |
| 2026-09-30 | 88 | 2761 | 684 |
| 2026-10-01 | 140 | 2548 | 622 |
| 2026-10-02 | 163 | 2843 | 431 |
| 2026-10-03 | 0 | 5013 | 468 |
| 2026-10-04 | 0 | 582 | 887 |
| 2026-10-05 | 0 | 1461 | 486 |
| 2026-10-06 | 190 | 2451 | 615 |
| 2026-10-07 | 80 | 2464 | 533 |
| 2026-10-08 | 0 | 2343 | 489 |
| 2026-10-09 | 0 | 1898 | 591 |
| 2026-10-10 | 130 | 2079 | 550 |
| 2026-10-11 | 0 | 475 | 354 |
| 2026-10-12 | 0 | 448 | 344 |
| 2026-10-13 | 0 | 447 | 296 |
| 2026-10-14 | 79 | 2868 | 451 |
| 2026-10-15 | 0 | 3501 | 472 |
| 2026-10-16 | 93 | 2469 | 626 |
| 2026-10-17 | 0 | 5 | 236 |

## Our ingestion assessment

**Model-written ingestion assessment**

The Congressional Record continues to arrive through govinfo collections API delta sync at full coverage per the registry. The current 14-day measurement shows 2,360 items at roughly 169 per day, averaging 5,699 characters (range 90 to ~1.4 million), most recent on October 2. The underlying api.govinfo.gov host exhibits a 26.3% request failure rate, affecting this and all collections sharing that endpoint. Compared to the assessment of September 5 (566 items at roughly 40 per day), collection volume in this window has increased substantially. The daily activity from September 30 through October 2 shows concentrated ingestion with heavy request errors from midday forward each day; October 3 through 6 shows no items collected to date.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

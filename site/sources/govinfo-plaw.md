<!-- Markdown twin of https://fapd.info/sources/govinfo-plaw.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-plaw.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-plaw)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Public and Private Laws (PLAW)

active · ingestion health: degraded · Legislative · Tier 1 · govinfo collection · U.S. Congress

Official site: https://www.govinfo.gov/app/collection/PLAW · All sources: [sources.md](../sources.md)

## What this source is

After a bill becomes law by presidential signature or veto override, the Government Publishing Office publishes the enacted text as a slip law. This collection carries public and private law text, typically appearing weeks after enactment; same-day text is available through the BILLS enrolled stage.

**Model-written orientation**

Public and Private Laws contains the official text of enacted federal legislation, published as slip laws by the Government Publishing Office after bills receive presidential signature or veto override.

Public and Private Laws represent the final, enacted form of legislation. After Congress passes a bill and the President signs it (or Congress overrides a veto), the Government Publishing Office publishes the enacted law in a standardized format called a slip law. This collection contains that official published text for all public laws (legislation affecting the general public or the government) and private laws (legislation affecting specific individuals or entities).

Slip laws serve as the intermediate step between bill passage and codification into the United States Code. When a law is enacted, the slip law is the first official publication of the complete text in its final form. Slip laws include the statutory language and a front matter section showing the bill number, the date of enactment, the President who signed it (if applicable), and procedural details. The Government Publishing Office publishes slip laws as they are enacted, which typically occurs weeks after a bill passes Congress—the time lag accounts for the process of enrolling the bill (producing the final, ceremonial copy Congress and the President sign).

Within the legislative record, slip laws serve as the authoritative source for understanding what Congress actually enacted. They sit between the Congressional Record and Bills (which show the legislative process) and the U.S. Code (which integrates laws into the standing legal framework). A reader tracing a law from proposal to enactment would encounter the bill text in the Bills collection, debate in the Congressional Record, and final enacted language here.

The collection is complete for the modern era: every public and private law enacted and published receives a law number and appears here. The Government Publishing Office publishes slip laws as structured text, making them machine-readable and consistent across publications.

In this digest, readers encounter enacted laws when legislation passes both chambers and is signed into law. The digest reports on new public laws affecting policy areas of national interest—legislation on budgets, regulations, benefits, or other matters Congress has enacted. Readers see the official Government Publishing Office publication, providing the authoritative text of what the law actually says.

Note: the collection captures only laws that have reached enactment. Bills that fail, vetoes that are not overridden, or other legislation that does not become law do not appear here.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-plaw` |
| Agency / parent organization | U.S. Congress |
| Branch | legislative |
| Type | govinfo collection |
| Status | active |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/PLAW |
| Registered | 2026-07-26 |
| Registry notes | Coverage (gate 3, backfilled 2026-07-30): the complete enacted-laws record, delta-only from 2026-07-25 (deeper history via bulkdata if ever needed). No packages listed in the window yet — govinfo has published no slip law since activation, so the digest's Enacted Laws section correctly renders its empty state. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | govinfo collection |
| Method | Syncs via the govinfo collections API delta mechanism (activated 2026-07-28, delta-only). |
| Poll cadence | about every 30 minutes while the collector runs |
| Request budget | the govinfo class: at most 6,000 requests per day and 500 per hour, counted from the fetch log (failed requests count too); collectors stop at 85% so the end-of-day finalizer always has headroom |
| Politeness | keyed govinfo API access; every request is logged before it is made and identified as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com) |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**degraded** — 3946 of 21982 request(s) to api.govinfo.gov returned no content (18.0%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-18T03:55:01Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,395 request(s) (1,896 answered, 499 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — most recent 2026-09-02 |
| Our requests to api.govinfo.gov | 21,982 request(s) · 18,036 answered · 1 declined (4xx) · 3,945 server declined (5xx) · 0 no response — 18.0% returned no content |

last answered request 2026-09-18T04:20:14.521+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

3946 of 21982 request(s) to api.govinfo.gov returned no content (18.0%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 108,867 request(s) · 82,528 answered · 26,339 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-20 | 4 | 2954 | 594 |
| 2026-08-21 | 0 | 2575 | 641 |
| 2026-08-22 | 0 | 2230 | 527 |
| 2026-08-23 | 0 | 2174 | 685 |
| 2026-08-24 | 0 | 1196 | 610 |
| 2026-08-25 | 2 | 1486 | 466 |
| 2026-08-26 | 0 | 2746 | 598 |
| 2026-08-27 | 0 | 2316 | 546 |
| 2026-08-28 | 0 | 2828 | 708 |
| 2026-08-29 | 0 | 2370 | 457 |
| 2026-08-30 | 0 | 2332 | 708 |
| 2026-08-31 | 0 | 1152 | 622 |
| 2026-09-01 | 0 | 1519 | 615 |
| 2026-09-02 | 1 | 2874 | 563 |
| 2026-09-03 | 0 | 2621 | 684 |
| 2026-09-04 | 0 | 2327 | 640 |
| 2026-09-05 | 0 | 1838 | 485 |
| 2026-09-06 | 0 | 2034 | 676 |
| 2026-09-07 | 0 | 1120 | 598 |
| 2026-09-08 | 0 | 794 | 451 |
| 2026-09-09 | 0 | 1513 | 522 |
| 2026-09-10 | 0 | 1782 | 695 |
| 2026-09-11 | 0 | 2005 | 714 |
| 2026-09-12 | 0 | 2319 | 594 |
| 2026-09-13 | 0 | 1408 | 576 |
| 2026-09-14 | 0 | 780 | 843 |
| 2026-09-15 | 0 | 1504 | 812 |
| 2026-09-16 | 0 | 2266 | 580 |
| 2026-09-17 | 0 | 2387 | 608 |
| 2026-09-18 | 0 | 232 | 561 |

## Our ingestion assessment

**Model-written ingestion assessment**

Public and Private Laws collection syncs via govinfo delta mechanism from July 25 baseline. Over the measured 14-day window we collected 3 items averaging 4,270 characters at 0.21 per day, most recent on September 2. This reflects minimal publishing activity noted in the registry: no slip laws have been published within our observation window. The collection is positioned to capture enacted laws as they are published by the Government Publishing Office. Compared to the prior assessment (no items as of August 5), we now have minimal data as publication begins.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/govinfo-uscourts.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-uscourts.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-uscourts)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# U.S. Courts Opinions (USCOURTS)

active · ingestion health: degraded · Judicial · Tier 1 · govinfo collection · Federal judiciary

Official site: https://www.govinfo.gov/app/collection/USCOURTS · All sources: [sources.md](../sources.md)

## What this source is

The federal judiciary provides opinions to the Government Publishing Office through a partnership with the Administrative Office of the U.S. Courts. This collection carries opinions from ~140 participating appellate, district, bankruptcy, and national courts as case-shaped packages, posted with a lag after filing; it is participation-based, not the complete federal judicial record.

**Model-written orientation**

U.S. Courts Opinions collects decisions and opinions from approximately 140 federal appellate, district, bankruptcy, and specialized courts, published through the Government Publishing Office.

U.S. Courts Opinions represents the judicial branch's participation in the official publication ecosystem. Through a partnership with the Administrative Office of the U.S. Courts, federal judges' opinions are compiled and published by the Government Publishing Office. The collection includes decisions from appellate courts (circuit courts and the Supreme Court, where participated), district courts, bankruptcy courts, and specialized federal courts such as the Court of International Trade and the Court of Federal Claims.

The collection is participation-based, meaning it includes opinions from courts that actively submit them. Approximately 140 courts participate, covering most federal judicial activity. However, participation is not universal—some courts do not submit opinions to this system, and some opinions may not be published immediately or at all. This collection therefore represents a substantial but incomplete picture of federal judicial activity.

Within the judicial system, this collection serves as one of several opinion-publication channels. The Supreme Court publishes its opinions independently through multiple official and commercial channels. Federal appellate courts publish through this system and through other services. The Government Publishing Office collection standardizes publication and makes opinions available in a consistent format.

Opinions are published with a lag after filing—courts may take weeks to submit opinions to the Government Publishing Office, and the office requires time to process and publish them. As a result, an opinion listed today may have been filed and decided some days or weeks ago. The collection includes metadata on each opinion: the court, the parties, the date decided, the docket number, and a judge-authored summary.

In this digest, readers encounter federal court opinions when appellate decisions are issued on questions of national interest, district-court rulings on important cases, or specialized-court opinions on their respective domains (patents, international trade, federal employment claims, etc.). Each opinion is sourced from the official publication, meaning readers see the court's own account of the decision and its reasoning.

Readers should understand that this collection, while substantial, does not capture every federal court opinion issued. Some courts do not participate, and the lag between decision and publication means recent decisions may not yet appear. The digest carries a standing note acknowledging this—the opinions shown represent only those available through this source.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-uscourts` |
| Agency / parent organization | Federal judiciary |
| Branch | judicial |
| Type | govinfo collection |
| Status | active |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/USCOURTS |
| Registered | 2026-07-26 |
| Registry notes | Rule USCOURTS-FETCH-01: courts post opinions with delay, so each sync re-checks a trailing 7-day archive window rather than a single date. Participation-based (~140 courts), not the complete federal judicial record — every digest's judicial section carries the standing completeness disclosure (GUIDE §3). |

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

Last 24 hours: 2,032 request(s) (1,626 answered, 406 returned no content) · 968 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 11,519 in 14 days (822.79 per day) · most recent 2026-09-19 |
| Content length | 12,931 characters average, 4,535 median (shortest 55, longest 1,213,913) |
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
| 2026-08-22 | 1204 | 2230 | 527 |
| 2026-08-23 | 468 | 2174 | 685 |
| 2026-08-24 | 505 | 1196 | 610 |
| 2026-08-25 | 1100 | 1486 | 466 |
| 2026-08-26 | 1094 | 2746 | 598 |
| 2026-08-27 | 1463 | 2316 | 546 |
| 2026-08-28 | 1873 | 2828 | 708 |
| 2026-08-29 | 1257 | 2370 | 457 |
| 2026-08-30 | 395 | 2332 | 708 |
| 2026-08-31 | 146 | 1152 | 622 |
| 2026-09-01 | 1707 | 1519 | 615 |
| 2026-09-02 | 1113 | 2874 | 563 |
| 2026-09-03 | 1124 | 2621 | 684 |
| 2026-09-04 | 974 | 2327 | 640 |
| 2026-09-05 | 966 | 1838 | 485 |
| 2026-09-06 | 251 | 2034 | 676 |
| 2026-09-07 | 570 | 1120 | 598 |
| 2026-09-08 | 180 | 794 | 451 |
| 2026-09-09 | 1022 | 1513 | 522 |
| 2026-09-10 | 980 | 1782 | 695 |
| 2026-09-11 | 1329 | 2005 | 714 |
| 2026-09-12 | 1374 | 2319 | 594 |
| 2026-09-13 | 192 | 1408 | 576 |
| 2026-09-14 | 410 | 780 | 843 |
| 2026-09-15 | 1415 | 1504 | 812 |
| 2026-09-16 | 1096 | 2266 | 580 |
| 2026-09-17 | 1096 | 2387 | 608 |
| 2026-09-18 | 887 | 2655 | 746 |
| 2026-09-19 | 968 | 2032 | 655 |
| 2026-09-20 | 0 | 5 | 210 |

## Our ingestion assessment

**Model-written ingestion assessment**

Court opinions arrive through govinfo delta sync using a trailing 7-day re-check window to accommodate delayed publication across approximately 140 participating courts. Over 14 days we collected 12,613 items averaging 13,381 characters (median 4,941) at roughly 901 per day, most recent on September 4. The shared govinfo host exhibits 25.6% request failure. Compared to the prior measurement (15,171 items at ~1,084/day, median 4,067 chars), both volume and daily rate have declined while median document size increased. Coverage remains participation-based across approximately 140 courts.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

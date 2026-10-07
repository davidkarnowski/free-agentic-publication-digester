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

**degraded** — 7856 of 31059 request(s) to api.govinfo.gov returned no content (25.3%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,495 request(s) (1,890 answered, 605 returned no content) · 965 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 11,843 in 14 days (845.93 per day) · most recent 2026-10-06 |
| Content length | 16,570 characters average, 6,077 median (shortest 0, longest 3,077,461) |
| Our requests to api.govinfo.gov | 31,059 request(s) · 23,203 answered · 0 declined (4xx) · 7,852 server declined (5xx) · 4 no response — 25.3% returned no content |

last answered request 2026-10-07T04:00:53.807+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

7856 of 31059 request(s) to api.govinfo.gov returned no content (25.3%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 151,987 request(s) · 114,687 answered · 37,300 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-09-08 | 190 | 794 | 451 |
| 2026-09-09 | 1044 | 1513 | 522 |
| 2026-09-10 | 993 | 1782 | 695 |
| 2026-09-11 | 1344 | 2005 | 714 |
| 2026-09-12 | 1414 | 2319 | 594 |
| 2026-09-13 | 201 | 1408 | 576 |
| 2026-09-14 | 419 | 780 | 843 |
| 2026-09-15 | 1447 | 1504 | 812 |
| 2026-09-16 | 1133 | 2266 | 580 |
| 2026-09-17 | 1118 | 2387 | 608 |
| 2026-09-18 | 913 | 2655 | 746 |
| 2026-09-19 | 1005 | 2032 | 655 |
| 2026-09-20 | 363 | 963 | 682 |
| 2026-09-21 | 268 | 981 | 482 |
| 2026-09-22 | 1141 | 1687 | 630 |
| 2026-09-23 | 1295 | 3975 | 588 |
| 2026-09-24 | 817 | 3610 | 542 |
| 2026-09-25 | 1161 | 2283 | 578 |
| 2026-09-26 | 1276 | 2284 | 670 |
| 2026-09-27 | 233 | 1185 | 802 |
| 2026-09-28 | 170 | 1179 | 585 |
| 2026-09-29 | 1532 | 2810 | 689 |
| 2026-09-30 | 1569 | 2761 | 684 |
| 2026-10-01 | 1519 | 2548 | 622 |
| 2026-10-02 | 921 | 2843 | 431 |
| 2026-10-03 | 928 | 5013 | 468 |
| 2026-10-04 | 225 | 582 | 887 |
| 2026-10-05 | 527 | 1461 | 486 |
| 2026-10-06 | 965 | 2451 | 615 |
| 2026-10-07 | 0 | 49 | 186 |

## Our ingestion assessment

**Model-written ingestion assessment**

Federal court opinions continue to arrive through govinfo collections API delta sync using a 7-day re-check window to accommodate publication delays across approximately 140 participating courts. The current 14-day window shows 12,152 items at roughly 868 per day, averaging 17,047 characters (median 6,016), most recent on October 5. The shared api.govinfo.gov host exhibits 26.3% request failure. Compared to the assessment of September 5 (12,613 items at roughly 901 per day, median 4,067 chars), both collection volume and daily rate have declined modestly while median document size has increased. Coverage remains participation-based across approximately 140 courts.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

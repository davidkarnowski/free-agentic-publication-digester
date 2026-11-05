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

**degraded** — 4141 of 24240 request(s) to api.govinfo.gov returned no content (17.1%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-05T04:59:44Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,552 request(s) (2,078 answered, 474 returned no content) · 1,067 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 9,056 in 14 days (646.86 per day) · most recent 2026-11-04 |
| Content length | 11,689 characters average, 4,662 median (shortest 59, longest 947,976) |
| Our requests to api.govinfo.gov | 24,240 request(s) · 20,099 answered · 0 declined (4xx) · 4,119 server declined (5xx) · 22 no response — 17.1% returned no content |

last answered request 2026-11-05T05:00:16.330+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

4141 of 24240 request(s) to api.govinfo.gov returned no content (17.1%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 208,811 request(s) · 160,231 answered · 48,580 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-10-07 | 937 | 2464 | 533 |
| 2026-10-08 | 907 | 2343 | 489 |
| 2026-10-09 | 1303 | 1898 | 591 |
| 2026-10-10 | 870 | 2079 | 550 |
| 2026-10-11 | 75 | 475 | 354 |
| 2026-10-12 | 16 | 448 | 344 |
| 2026-10-13 | 37 | 447 | 296 |
| 2026-10-14 | 933 | 2868 | 451 |
| 2026-10-15 | 1420 | 3501 | 472 |
| 2026-10-16 | 959 | 2469 | 626 |
| 2026-10-17 | 800 | 2140 | 573 |
| 2026-10-18 | 898 | 2138 | 434 |
| 2026-10-19 | 33 | 504 | 398 |
| 2026-10-20 | 700 | 2440 | 384 |
| 2026-10-21 | 820 | 2357 | 477 |
| 2026-10-22 | 1872 | 4062 | 594 |
| 2026-10-23 | 923 | 3041 | 562 |
| 2026-10-24 | 1036 | 2255 | 541 |
| 2026-10-25 | 90 | 606 | 387 |
| 2026-10-26 | 18 | 514 | 335 |
| 2026-10-27 | 815 | 2542 | 666 |
| 2026-10-28 | 1054 | 2535 | 526 |
| 2026-10-29 | 920 | 2145 | 515 |
| 2026-10-30 | 894 | 2168 | 523 |
| 2026-10-31 | 1360 | 2621 | 555 |
| 2026-11-01 | 38 | 486 | 326 |
| 2026-11-02 | 16 | 442 | 352 |
| 2026-11-03 | 825 | 2328 | 565 |
| 2026-11-04 | 1067 | 2550 | 584 |
| 2026-11-05 | 0 | 7 | 211 |

## Our ingestion assessment

**Model-written ingestion assessment**

Over the 14-day window we recorded 9,056 opinion items, about 647 per day, with a mean of 11,689 characters (median 4,662, range 59 to 947,976). Daily activity shows large counts on 2026-10-30 (894), 2026-10-31 (1,360), 2026-11-03 (825), and 2026-11-04 (1,067), with 38 on 2026-11-01, 16 on 2026-11-02, and none on 2026-11-05. The most recent item is dated 2026-11-04. The shared api.govinfo.gov host returned no content for 17.1 percent of attempts, and the collection is marked degraded on that basis. The registry notes describe a participation-based collection of about 140 courts with a trailing 7-day re-check window, and this measurement covers only those participating courts. Compared with the 2026-10-06 assessment, which recorded 12,152 items at about 868 per day, a mean of 17,047 characters, a median of 6,016, and a last item of 2026-10-05, the daily rate, mean size, and median size are all lower, and the last item date has advanced.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

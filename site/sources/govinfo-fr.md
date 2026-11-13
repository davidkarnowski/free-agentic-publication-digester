<!-- Markdown twin of https://fapd.info/sources/govinfo-fr.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-fr.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-fr)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Register (FR)

active · ingestion health: degraded · Executive · Tier 1 · govinfo collection · National Archives and Records Administration

Official site: https://www.govinfo.gov/app/collection/FR · All sources: [sources.md](../sources.md)

## What this source is

The Federal Register is the executive branch's daily journal, compiled by the Office of the Federal Register and published each business day. This collection carries final rules, proposed rules, notices, and presidential documents as structured XML (~2.6 MB of text per issue), with an agency-written abstract per document.

**Model-written orientation**

The Federal Register is the executive branch's daily journal, published each business day by the Office of the Federal Register, containing executive actions, agency rules, and notices.

The Federal Register is the official gazette of the executive branch and independent agencies. Published each business day, it serves as the primary channel through which federal agencies announce actions, publish new rules, solicit public comment, or inform the public of administrative decisions. The Office of the Federal Register, part of the National Archives and Records Administration, compiles and publishes the Register.

The Register contains several classes of documents. Final rules are agency regulations that have been through a public-comment period and are now in effect. Proposed rules are agencies' announcements of potential new regulations, opened for public comment. Notices cover agency announcements, committee meetings, policy positions, and other agency actions that don't fit other categories. Presidential documents—including executive orders, proclamations, memoranda, and determinations—are published here as well. Each document is typically accompanied by an abstract written by the publishing agency, explaining the action in plain language.

Within the federal structure, the Federal Register occupies a unique position: it is the official publication channel for almost all executive-branch regulatory activity. When an agency decides to change a rule, it must publish in the Register. When a committee meets, the notice goes to the Register. The Register thus serves as both a transparency tool (making government action public) and a legal requirement (regulations don't take effect until published there). It is the government's central bulletin board for executive-branch activity.

The data is published as structured text by the Office of the Federal Register. Each issue typically contains 50-100 documents, varying by the time of year and the number of agencies' announcements. The Register is published in full-text form, with each document indexed by agency, subject matter, effective date, and comment deadline (if applicable).

In this digest, readers encounter Federal Register items when agencies announce new rules, solicit public input, or make policy decisions. A reader might see a proposed rule from an environmental agency, a final regulation from a financial regulator, a notice of a committee meeting, or a presidential executive order. Each item comes with the government's own explanation of what the action means and when it takes effect, sourced from the official Register text.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-fr` |
| Agency / parent organization | National Archives and Records Administration |
| Branch | executive |
| Type | govinfo collection |
| Status | active |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/FR |
| Registered | 2026-07-26 |
| Registry notes | Coverage (gate 3, backfilled 2026-07-30): the complete daily issue — every document in each day's Federal Register is listed, extracted, and carries its official agency abstract; companion graphics PDFs are fetched for flagged documents under rule FR-GPH-01. |

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

**degraded** — 3219 of 21184 request(s) to api.govinfo.gov returned no content (15.2%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-13T04:50:48Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 470 request(s) (414 answered, 56 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 796 in 14 days (56.86 per day) · most recent 2026-11-12 |
| Content length | 30,284 characters average, 6,341 median (shortest 344, longest 4,444,364) |
| Our requests to api.govinfo.gov | 21,184 request(s) · 17,965 answered · 0 declined (4xx) · 3,219 server declined (5xx) · 0 no response — 15.2% returned no content |

last answered request 2026-11-13T05:00:08.783+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

3219 of 21184 request(s) to api.govinfo.gov returned no content (15.2%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 221,561 request(s) · 171,082 answered · 50,479 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-10-15 | 78 | 3501 | 472 |
| 2026-10-16 | 129 | 2469 | 626 |
| 2026-10-17 | 0 | 2140 | 573 |
| 2026-10-18 | 0 | 2138 | 434 |
| 2026-10-19 | 146 | 504 | 398 |
| 2026-10-20 | 82 | 2440 | 384 |
| 2026-10-21 | 63 | 2357 | 477 |
| 2026-10-22 | 96 | 4062 | 594 |
| 2026-10-23 | 82 | 3041 | 562 |
| 2026-10-24 | 0 | 2255 | 541 |
| 2026-10-25 | 0 | 606 | 387 |
| 2026-10-26 | 99 | 514 | 335 |
| 2026-10-27 | 81 | 2542 | 666 |
| 2026-10-28 | 104 | 2535 | 526 |
| 2026-10-29 | 102 | 2145 | 515 |
| 2026-10-30 | 119 | 2168 | 523 |
| 2026-10-31 | 0 | 2621 | 555 |
| 2026-11-01 | 0 | 486 | 326 |
| 2026-11-02 | 102 | 442 | 352 |
| 2026-11-03 | 81 | 2328 | 565 |
| 2026-11-04 | 92 | 2550 | 584 |
| 2026-11-05 | 111 | 2037 | 574 |
| 2026-11-06 | 80 | 2631 | 820 |
| 2026-11-07 | 0 | 2323 | 563 |
| 2026-11-08 | 0 | 440 | 716 |
| 2026-11-09 | 98 | 424 | 944 |
| 2026-11-10 | 108 | 2183 | 597 |
| 2026-11-11 | 0 | 2238 | 639 |
| 2026-11-12 | 124 | 476 | 379 |
| 2026-11-13 | 0 | 5 | 240 |

## Our ingestion assessment

**Model-written ingestion assessment**

Over the 14-day window we recorded 862 Federal Register items, about 62 per day, with a mean of 20,866 characters (median 6,097, range 564 to 1,433,883). Daily activity shows items on 2026-10-30 (119), 2026-10-31 (102), 2026-11-03 (81), and 2026-11-04 (193), with none on 2026-11-01, 2026-11-02, or 2026-11-05. The most recent item is dated 2026-11-04. The shared api.govinfo.gov host returned no content for 17.1 percent of attempts, and the collection is marked degraded on that basis. This measurement does not break out companion graphics PDFs, which the registry notes describe as fetched for flagged documents. Compared with the 2026-10-06 assessment, which recorded 965 items at about 69 per day, a mean of 20,426 characters, and a last item of 2026-10-05, the daily rate is lower, the mean size is similar, and the last item date has advanced. The registry notes record a coverage backfill on 2026-07-30 and no other incidents.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

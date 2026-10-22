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

**degraded** — 5375 of 23769 request(s) to api.govinfo.gov returned no content (22.6%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-22T03:45:30Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,357 request(s) (1,805 answered, 552 returned no content) · 171 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 816 in 14 days (58.29 per day) · most recent 2026-10-21 |
| Content length | 15,933 characters average, 6,374 median (shortest 566, longest 536,639) |
| Our requests to api.govinfo.gov | 23,769 request(s) · 18,394 answered · 0 declined (4xx) · 5,375 server declined (5xx) · 0 no response — 22.6% returned no content |

last answered request 2026-10-22T04:00:12.295+00:00 UTC; this host serves 5 registered sources, so these figures are host-wide.

5375 of 23769 request(s) to api.govinfo.gov returned no content (22.6%, at or above the 10% mark).

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 180,514 request(s) · 136,624 answered · 43,890 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-09-23 | 98 | 3975 | 588 |
| 2026-09-24 | 106 | 3610 | 542 |
| 2026-09-25 | 104 | 2283 | 578 |
| 2026-09-26 | 0 | 2284 | 670 |
| 2026-09-27 | 0 | 1185 | 802 |
| 2026-09-28 | 101 | 1179 | 585 |
| 2026-09-29 | 116 | 2810 | 689 |
| 2026-09-30 | 128 | 2761 | 684 |
| 2026-10-01 | 112 | 2548 | 622 |
| 2026-10-02 | 94 | 2843 | 431 |
| 2026-10-03 | 0 | 5013 | 468 |
| 2026-10-04 | 0 | 582 | 887 |
| 2026-10-05 | 106 | 1461 | 486 |
| 2026-10-06 | 94 | 2451 | 615 |
| 2026-10-07 | 73 | 2464 | 533 |
| 2026-10-08 | 133 | 2343 | 489 |
| 2026-10-09 | 89 | 1898 | 591 |
| 2026-10-10 | 0 | 2079 | 550 |
| 2026-10-11 | 0 | 475 | 354 |
| 2026-10-12 | 0 | 448 | 344 |
| 2026-10-13 | 103 | 447 | 296 |
| 2026-10-14 | 126 | 2868 | 451 |
| 2026-10-15 | 78 | 3501 | 472 |
| 2026-10-16 | 129 | 2469 | 626 |
| 2026-10-17 | 0 | 2140 | 573 |
| 2026-10-18 | 0 | 2138 | 434 |
| 2026-10-19 | 146 | 504 | 398 |
| 2026-10-20 | 82 | 2440 | 384 |
| 2026-10-21 | 63 | 2357 | 477 |
| 2026-10-22 | 0 | 5 | 270 |

## Our ingestion assessment

**Model-written ingestion assessment**

Federal Register daily issues continue to arrive as structured XML via govinfo collections API delta sync, including agency abstracts and graphics per standard processing. The current 14-day window shows 965 items at roughly 69 per day, averaging 20,426 characters (median 6,290, range 393 to ~1.5 million), most recent on October 5. The shared api.govinfo.gov host exhibits 26.3% request failure across all collections. Compared to the assessment of September 5 (989 items at roughly 71 per day, averaging 15,121 characters), collection volume has declined slightly while daily rate has remained essentially stable.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

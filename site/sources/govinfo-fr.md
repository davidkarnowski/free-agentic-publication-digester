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

**degraded** — 3999 of 22570 request(s) to api.govinfo.gov returned no content (17.7%, at or above the 10% mark).

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-20T03:51:20Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2,032 request(s) (1,626 answered, 406 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 997 in 14 days (71.21 per day) · most recent 2026-09-18 |
| Content length | 16,770 characters average, 6,160 median (shortest 594, longest 732,996) |
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
| 2026-08-24 | 84 | 1196 | 610 |
| 2026-08-25 | 90 | 1486 | 466 |
| 2026-08-26 | 92 | 2746 | 598 |
| 2026-08-27 | 99 | 2316 | 546 |
| 2026-08-28 | 111 | 2828 | 708 |
| 2026-08-29 | 0 | 2370 | 457 |
| 2026-08-30 | 0 | 2332 | 708 |
| 2026-08-31 | 121 | 1152 | 622 |
| 2026-09-01 | 116 | 1519 | 615 |
| 2026-09-02 | 85 | 2874 | 563 |
| 2026-09-03 | 108 | 2621 | 684 |
| 2026-09-04 | 83 | 2327 | 640 |
| 2026-09-05 | 0 | 1838 | 485 |
| 2026-09-06 | 0 | 2034 | 676 |
| 2026-09-07 | 0 | 1120 | 598 |
| 2026-09-08 | 69 | 794 | 451 |
| 2026-09-09 | 127 | 1513 | 522 |
| 2026-09-10 | 119 | 1782 | 695 |
| 2026-09-11 | 115 | 2005 | 714 |
| 2026-09-12 | 0 | 2319 | 594 |
| 2026-09-13 | 0 | 1408 | 576 |
| 2026-09-14 | 156 | 780 | 843 |
| 2026-09-15 | 121 | 1504 | 812 |
| 2026-09-16 | 104 | 2266 | 580 |
| 2026-09-17 | 72 | 2387 | 608 |
| 2026-09-18 | 114 | 2655 | 746 |
| 2026-09-19 | 0 | 2032 | 655 |
| 2026-09-20 | 0 | 5 | 210 |

## Our ingestion assessment

**Model-written ingestion assessment**

Federal Register daily issues arrive as structured XML via govinfo delta sync, including agency abstracts and graphics per standard processing. Over 14 days we collected 989 items averaging 15,121 characters (median 6,402) at roughly 71 per day, most recent on September 4. The shared govinfo host shows 25.6% request failure across all collections. Compared to the previous 14-day window (958 items at ~68/day, averaging 24,891 characters), collection volume and rate have remained stable while average document size has decreased, with median size essentially unchanged.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

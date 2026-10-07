<!-- Markdown twin of https://fapd.info/sources/crs-reports.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/crs-reports.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: crs-reports)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CRS Reports

planned · Legislative · Tier 1 · API · Congressional Research Service

Official site: https://crsreports.congress.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Congressional Research Service provides nonpartisan policy and legal analysis to members and committees of Congress. New and updated CRS reports, released under 2018 appropriations law, typically several items per business day.

**Model-written orientation**

The Congressional Research Service provides nonpartisan policy and legal research to members and committees of Congress, publishing analysis on a wide range of legislative and policy topics. New and updated reports typically appear several times per business day.

The Congressional Research Service (CRS) is the public policy research arm of the United States Congress, providing nonpartisan analysis, research, and legal interpretation to members of Congress and congressional committees. CRS is part of the Library of Congress and operates without partisan affiliation, serving members of both parties equally. The service employs subject-matter specialists, lawyers, analysts, and researchers with expertise spanning domestic policy, foreign affairs, economics, law, and other fields relevant to congressional work.

CRS conducts research and analysis on a comprehensive range of topics including federal legislation and enacted laws, constitutional questions and legal interpretation, federal agency policies and programs, international affairs and diplomatic developments, domestic policy questions across all areas of federal responsibility, and economic and fiscal policy. Each report provides background, analysis of relevant facts and issues, legal context where applicable, and information relevant to congressional consideration. CRS reports are released publicly under the 2018 appropriations law, which requires CRS to make its research available to the public.

CRS reports vary considerably in length and depth, ranging from brief issue summaries and fact sheets addressing specific current questions to comprehensive research products providing extensive background and analysis. Reports are updated regularly as circumstances change and new information becomes available. The service conducts research on request from congressional members and committees, and research priorities reflect current congressional interests and legislative activity.

Readers will encounter authoritative nonpartisan analysis on topics ranging from pending legislation under congressional consideration to ongoing policy questions, constitutional issues, and international developments. New and updated reports are published frequently throughout the year, typically resulting in several new or revised items per business day. Readers can expect in-depth, balanced analysis designed to inform congressional decision-making and oversight.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `crs-reports` |
| Agency / parent organization | Congressional Research Service |
| Branch | legislative |
| Type | API |
| Status | planned |
| Tier | 1 |
| URL (home) | https://crsreports.congress.gov/ |
| URL (index) | https://api.congress.gov/v3/crsreport |
| Registered | 2026-07-26 |
| Registry notes | crsreports.congress.gov itself: HTTP 403 to honestly-identified automated client (WAF, probed 2026-07-26) and publishes no machine-access documentation — that path stays closed. Research 2026-07-28: the officially documented channel is the Congress.gov API crsreport endpoint (LoC GitHub docs, CRSReportEndpoint.md read): product IDs, pub/update dates, titles, authors, topics, summaries, and format-URL containers. Metadata + summaries alone are digest-worthy; whether the congress.gov-hosted full-text URLs fetch cleanly for our client needs probe. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Would delta-sync the api.congress.gov crsreport endpoint (same api.data.gov key the pipeline already holds). |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

- **Our requests to api.congress.gov, all time (since 2026-08-01):** 1,845 request(s) · 1,839 answered · 6 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.congress.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-08 | 0 | 25 | 310 |
| 2026-09-09 | 0 | 25 | 319 |
| 2026-09-10 | 0 | 24 | 339 |
| 2026-09-11 | 0 | 25 | 317 |
| 2026-09-12 | 0 | 28 | 443 |
| 2026-09-13 | 0 | 25 | 296 |
| 2026-09-14 | 0 | 29 | 472 |
| 2026-09-15 | 0 | 25 | 320 |
| 2026-09-16 | 0 | 25 | 346 |
| 2026-09-17 | 0 | 25 | 455 |
| 2026-09-18 | 0 | 25 | 472 |
| 2026-09-19 | 0 | 25 | 295 |
| 2026-09-20 | 0 | 25 | 321 |
| 2026-09-21 | 0 | 27 | 371 |
| 2026-09-22 | 0 | 25 | 298 |
| 2026-09-23 | 0 | 24 | 309 |
| 2026-09-24 | 0 | 24 | 320 |
| 2026-09-25 | 0 | 25 | 356 |
| 2026-09-26 | 0 | 26 | 717 |
| 2026-09-27 | 0 | 26 | 355 |
| 2026-09-28 | 0 | 28 | 1015 |
| 2026-09-29 | 0 | 26 | 314 |
| 2026-09-30 | 0 | 25 | 543 |
| 2026-10-01 | 0 | 27 | 315 |
| 2026-10-02 | 0 | 27 | 325 |
| 2026-10-03 | 0 | 25 | 408 |
| 2026-10-04 | 0 | 25 | 391 |
| 2026-10-05 | 0 | 25 | 559 |
| 2026-10-06 | 0 | 27 | 327 |
| 2026-10-07 | 0 | 1 | 257 |

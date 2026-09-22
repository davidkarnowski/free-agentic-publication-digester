<!-- Markdown twin of https://fapd.info/sources/govinfo-dcpd.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/govinfo-dcpd.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: govinfo-dcpd)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Daily Compilation of Presidential Documents (DCPD)

planned · Executive · Tier 1 · govinfo collection · Executive Office of the President

Official site: https://www.govinfo.gov/app/collection/DCPD · All sources: [sources.md](../sources.md)

## What this source is

The Office of the Federal Register compiles presidential materials released by the White House press secretary. This collection carries that compilation — statements, remarks, executive orders, proclamations, and nominations — published on a lag behind the events themselves.

**Model-written orientation**

The Daily Compilation of Presidential Documents contains statements, remarks, executive orders, proclamations, and other materials released by the White House, published by the Office of the Federal Register.

The Daily Compilation of Presidential Documents (formally, the Compilation of Presidential Documents) is the executive branch's official collection of presidential materials. It includes statements issued by the President, remarks delivered at various events, executive orders, proclamations, memoranda, determinations, and related materials released by the White House. The Office of the Federal Register compiles these materials and publishes them through the Government Publishing Office.

Presidential documents serve multiple purposes in the federal system. Executive orders carry the force of law and direct executive-branch agencies to take specific actions. Proclamations typically address matters of national ceremony or observance. Statements and remarks provide the President's stated position on matters of public interest. Determinations address technical or administrative decisions under existing authorities. Together, these materials create an official record of presidential actions and communications.

However, the collection faces a substantial publication lag. Materials released by the White House press office reach the Government Publishing Office for compilation and publication after a delay of several weeks. When probed recently, the collection showed that materials being published—dated in late June—had been released by the White House in early July, representing a lag of approximately five weeks between White House release and official publication through the Government Publishing Office.

Within the executive structure, presidential documents are published through multiple channels simultaneously. The White House press office releases them immediately. The Federal Register also publishes certain classes (executive orders, proclamations) in the same issue as other executive-branch documents. The Government Publishing Office collection consolidates them into a single compilation. However, readers seeking the same-day record of presidential actions can find them through the Federal Register (where they appear under the PRESDOCU category), while the dedicated compilation appears later.

In this digest, readers would encounter presidential documents only after substantial delay—a presidential statement issued today might not appear in the official published compilation for several weeks. Because of this lag, and because presidential actions are already captured through the Federal Register's same-day publication channel, this source currently does not feed the digest.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `govinfo-dcpd` |
| Agency / parent organization | Executive Office of the President |
| Branch | executive |
| Type | govinfo collection |
| Status | planned |
| Tier | 1 |
| URL (collection) | https://www.govinfo.gov/app/collection/DCPD |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-31 through the govinfo API. TWO findings. (1) `DCPD` is not a govinfo collection code — the collections endpoint does not list it, and every query returns zero. The real code is `CPD` (Compilation of Presidential Documents, 18,441 packages); package IDs are prefixed DCPD-, which is the likely source of this entry's error. (2) CPD is live (62 packages in 14 days) but publishes with roughly a five-week lag — newest dateIssued 2026-06-23 when probed on 07-31 — so under the §3 dating rule its documents belong to digest days already published and never re-rendered. Presidential documents are already carried same-day through FR PRESDOCU (FR-SEL-03). One document per package, no granules, no xmlLink (txt/pdf/zip only). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | govinfo collection |
| Method | Would sync via the govinfo collections API delta mechanism once enabled (GUIDE §7 Phase 4). |
| Request budget | the govinfo class: at most 6,000 requests per day and 800 per hour, counted from the fetch log (failed requests count too); collectors stop at 85% so the end-of-day finalizer always has headroom |
| Politeness | keyed govinfo API access; every request is logged before it is made and identified as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com) |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

- **Our requests to api.govinfo.gov, all time (since 2026-07-30):** 115,271 request(s) · 87,697 answered · 27,574 returned no content

This host serves 5 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to api.govinfo.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-24 | 0 | 1196 | 610 |
| 2026-08-25 | 0 | 1486 | 466 |
| 2026-08-26 | 0 | 2746 | 598 |
| 2026-08-27 | 0 | 2316 | 546 |
| 2026-08-28 | 0 | 2828 | 708 |
| 2026-08-29 | 0 | 2370 | 457 |
| 2026-08-30 | 0 | 2332 | 708 |
| 2026-08-31 | 0 | 1152 | 622 |
| 2026-09-01 | 0 | 1519 | 615 |
| 2026-09-02 | 0 | 2874 | 563 |
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
| 2026-09-18 | 0 | 2655 | 746 |
| 2026-09-19 | 0 | 2032 | 655 |
| 2026-09-20 | 0 | 963 | 682 |
| 2026-09-21 | 0 | 981 | 482 |
| 2026-09-22 | 0 | 5 | 189 |

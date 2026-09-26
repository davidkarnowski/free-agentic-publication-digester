<!-- Markdown twin of https://fapd.info/sources/whitehouse-executive-orders.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/whitehouse-executive-orders.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: whitehouse-executive-orders)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# White House Executive Orders

active · ingestion health: quiet · Executive · Tier 1 · RSS feed · Executive Office of the President

Official site: https://www.whitehouse.gov/presidential-actions/executive-orders/ · All sources: [sources.md](../sources.md)

## What this source is

The executive-orders category of whitehouse.gov's presidential actions. A narrower feed than the parent, and a deeper one: because each feed is capped at 30 items, proclamations crowd executive orders out of the combined feed, so this one reaches substantially further back in time.

**Model-written orientation**

A specialized White House feed publishing executive orders, providing more comprehensive historical coverage than the broader presidential actions feed.

Executive orders are a category of presidential instruments through which the President directs executive-branch agencies and establishes policy within the scope of executive authority. Each executive order has the force of law and typically directs federal agencies to take specific actions, establish procedures, or implement policy changes.

This feed collects executive orders specifically, narrowing the broader presidential actions feed—which includes proclamations, memoranda, and nominations—to focus on orders alone. Because the White House maintains a chronological feed capped at 30 recent items, and because proclamations and memoranda are issued frequently, executive orders can fall out of the main presidential actions feed relatively quickly. This dedicated feed preserves a longer historical window, allowing readers to access a more complete record of recent executive orders without them being displaced by other forms of presidential action.

The orders published here cover the full scope of executive authority: foreign policy and trade, appointments and personnel, regulatory matters, agency organization and operations, national security, emergency declarations, and other matters within presidential purview. Each order is published with its full text, the date signed, and any accompanying explanatory materials.

Executive orders are official government publications with legal force. They serve as the formal record of executive directives and are cited in legal proceedings, agency operations, and policy analysis. This feed represents the real-time publication of executive orders as they are signed, before they are compiled in official registers or legal databases.

Readers accessing this source receive the complete, chronologically ordered record of recent executive orders with minimal lag from the moment of signing.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `whitehouse-executive-orders` |
| Agency / parent organization | Executive Office of the President |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.whitehouse.gov/presidential-actions/executive-orders/feed/ |
| URL (home) | https://www.whitehouse.gov/presidential-actions/executive-orders/ |
| Registered | 2026-08-06 |
| Registry notes | Registered 2026-08-06 alongside whitehouse-presidential-actions (operator decision: two entries). NOT a subset of the parent feed, which is why both are registered: each caps at 30 items, and the parent's slots are consumed by proclamations and memoranda, so executive orders fall out of its window far sooner. Measured 2026-08-06 — parent feed spans 2026-06-25 to 08-06 (~6 weeks); this one spans 2026-03-06 to 08-06 (~5 months), and 24 of its 30 orders are absent from the parent. Probed 2026-08-06: HTTP 200, application/rss+xml, 668,654 bytes, verdict feed-ok, 30 items, 30/30 with pubDate and guid. Gate-3 content evaluation: identical shape to the parent feed — <description> is a teaser, so full mode is required; the sample article extracted at 8,940 characters. Duplication is real and intended: where the two feeds carry the same order the link URL is identical (verified 6/6 on the overlap), so report.corroborate merges them into one listing marked corroborated, and no new dedup code was needed. Editorial register: attributed, per GUIDE §2 (operator, 2026-08-06). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the executive-orders RSS feed via AgencyClient, then fetches each new item's page for the full order text (mode full); overlaps whitehouse-presidential-actions by design — shared items carry identical link URLs and merge through the standing corroboration rule. |
| Adapter | presidential-actions |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**quiet** — Most recent item 2026-09-18, 8 days ago (quiet past 7 days).

This label has held since 2026-09-26T04:03:22Z (UTC) and was last re-checked 2026-09-26T04:03:22Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 54 request(s) (54 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 4 in 14 days (0.29 per day) · most recent 2026-09-18 |
| Content length | 13,471 characters average, 12,170 median (shortest 10,707, longest 18,838) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.whitehouse.gov | 694 request(s) · 694 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-26T04:07:59.272+00:00 UTC; this host serves 2 registered sources, so these figures are host-wide.

Most recent item 2026-09-18, 8 days ago (quiet past 7 days).

### All time

- **Our requests to www.whitehouse.gov, all time (since 2026-08-06):** 2,818 request(s) · 2,811 answered · 7 returned no content

This host serves 2 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.whitehouse.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-28 | 0 | 52 | 43 |
| 2026-08-29 | 0 | 51 | 43 |
| 2026-08-30 | 0 | 53 | 54 |
| 2026-08-31 | 0 | 51 | 54 |
| 2026-09-01 | 0 | 51 | 44 |
| 2026-09-02 | 0 | 56 | 113 |
| 2026-09-03 | 0 | 53 | 214 |
| 2026-09-04 | 2 | 55 | 72 |
| 2026-09-05 | 0 | 63 | 101 |
| 2026-09-06 | 0 | 51 | 52 |
| 2026-09-07 | 0 | 52 | 50 |
| 2026-09-08 | 2 | 58 | 67 |
| 2026-09-09 | 0 | 52 | 49 |
| 2026-09-10 | 0 | 51 | 77 |
| 2026-09-11 | 0 | 51 | 64 |
| 2026-09-12 | 0 | 55 | 63 |
| 2026-09-13 | 0 | 51 | 44 |
| 2026-09-14 | 0 | 58 | 140 |
| 2026-09-15 | 0 | 53 | 46 |
| 2026-09-16 | 1 | 56 | 49 |
| 2026-09-17 | 2 | 56 | 69 |
| 2026-09-18 | 1 | 54 | 81 |
| 2026-09-19 | 0 | 51 | 42 |
| 2026-09-20 | 0 | 53 | 40 |
| 2026-09-21 | 0 | 57 | 72 |
| 2026-09-22 | 0 | 49 | 59 |
| 2026-09-23 | 0 | 49 | 52 |
| 2026-09-24 | 0 | 51 | 54 |
| 2026-09-25 | 0 | 54 | 61 |
| 2026-09-26 | 0 | 2 | 52 |

## Our ingestion assessment

**Model-written ingestion assessment**

The White House Executive Orders source is ingested by polling its RSS feed and then fetching the full text from each item's linked page. Over the past 14 days, we observed 4 new items at a rate of 0.29 per day. This represents a decrease from the 0.36 items per day reported in the previous assessment. The most recent item was delivered on 2026-09-18, resulting in 8 days without new content and a current "quiet" health status. All 694 polling requests to www.whitehouse.gov were answered successfully with a 0.0% error rate, consistent with previous observations. Extracted content averaged 13,471 characters, with a range of 10,707 to 18,838 characters, an increase from the previous average of 9,980 characters. The feed retains its characteristic of being capped at 30 items but covering a longer historical period than the broader presidential actions feed.

_Model-written assessment of our own ingestion, generated 2026-09-26 by gemini-2.5-flash, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

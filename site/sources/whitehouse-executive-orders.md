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

**quiet** — Most recent item 2026-10-22, 9 days ago (quiet past 7 days).

This label has held since 2026-10-30T04:11:38Z (UTC) and was last re-checked 2026-10-31T03:45:15Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 104 request(s) (104 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-22 |
| Content length | 14,490 characters average, 13,917 median (shortest 12,211, longest 17,341) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.whitehouse.gov | 1,327 request(s) · 1,326 answered · 0 declined (4xx) · 0 server declined (5xx) · 1 no response — 0.1% returned no content |

last answered request 2026-10-31T04:00:16.210+00:00 UTC; this host serves 4 registered sources, so these figures are host-wide.

Most recent item 2026-10-22, 9 days ago (quiet past 7 days).

### All time

- **Our requests to www.whitehouse.gov, all time (since 2026-08-06):** 6,024 request(s) · 6,008 answered · 16 returned no content

This host serves 4 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.whitehouse.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-10-02 | 0 | 79 | 65 |
| 2026-10-03 | 0 | 75 | 39 |
| 2026-10-04 | 0 | 75 | 40 |
| 2026-10-05 | 1 | 83 | 55 |
| 2026-10-06 | 0 | 95 | 77 |
| 2026-10-07 | 0 | 106 | 81 |
| 2026-10-08 | 0 | 104 | 69 |
| 2026-10-09 | 0 | 101 | 80 |
| 2026-10-10 | 0 | 100 | 76 |
| 2026-10-11 | 0 | 100 | 73 |
| 2026-10-12 | 0 | 104 | 78 |
| 2026-10-13 | 0 | 100 | 76 |
| 2026-10-14 | 0 | 100 | 72 |
| 2026-10-15 | 0 | 100 | 75 |
| 2026-10-16 | 1 | 102 | 76 |
| 2026-10-17 | 0 | 100 | 77 |
| 2026-10-18 | 0 | 100 | 71 |
| 2026-10-19 | 1 | 102 | 76 |
| 2026-10-20 | 0 | 100 | 84 |
| 2026-10-21 | 0 | 101 | 84 |
| 2026-10-22 | 2 | 106 | 94 |
| 2026-10-23 | 0 | 105 | 67 |
| 2026-10-24 | 0 | 100 | 77 |
| 2026-10-25 | 0 | 104 | 76 |
| 2026-10-26 | 0 | 100 | 75 |
| 2026-10-27 | 0 | 100 | 77 |
| 2026-10-28 | 0 | 101 | 84 |
| 2026-10-29 | 0 | 100 | 77 |
| 2026-10-30 | 0 | 104 | 71 |
| 2026-10-31 | 0 | 4 | 48 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest the executive-orders RSS feed of whitehouse.gov's presidential actions. It was registered 2026-08-06 as a separate entry from whitehouse-presidential-actions because each feed holds 30 items and this one reaches back further. Feed descriptions are teasers, so we fetch each item's page for full order text (delivery mode full). Measured lengths in the current window were 12,211, 13,917, and 17,341 characters, averaging 14,490; the previous assessment averaged 12,509. Over the past 14 days we measured three items at 0.21 per day, the most recent dated 2026-10-22, nine days before this assessment, and the health reading is quiet. The previous assessment recorded two items, the most recent dated 2026-10-16. Orders that also appear in the parent feed carry identical link URLs and merge through corroboration. Of 1,327 requests to www.whitehouse.gov, 1,326 returned content and one returned no content, the same single no-content count as the previous assessment. From outside, we cannot tell whether that was load, maintenance, or a limit set by the publisher.

_Model-written assessment of our own ingestion, generated 2026-10-31 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

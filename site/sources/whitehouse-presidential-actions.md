<!-- Markdown twin of https://fapd.info/sources/whitehouse-presidential-actions.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/whitehouse-presidential-actions.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: whitehouse-presidential-actions)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# White House Presidential Actions

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Executive Office of the President

Official site: https://www.whitehouse.gov/presidential-actions/ · All sources: [sources.md](../sources.md)

## What this source is

The Executive Office of the President publishes the President's instruments — executive orders, proclamations, presidential memoranda, and nominations — on whitehouse.gov as they are signed. This RSS feed carries them with full document text, days ahead of their compilation in the Federal Register.

**Model-written orientation**

The White House publishes presidential instruments—executive orders, proclamations, memoranda, and nominations—through whitehouse.gov as they are signed.

Presidential actions are the formal instruments through which the President exercises executive authority. These include executive orders, which direct executive-branch agencies and have the force of law; proclamations, which announce policy positions or actions open to the public (such as national emergencies, holidays, or trade actions); presidential memoranda, which direct action within the executive branch on specific matters; and notifications of nominations for Senate-confirmed positions.

The White House publishes these instruments on whitehouse.gov as they are signed, making them publicly available in real time. This represents the first formal public disclosure of most presidential instruments—the instruments typically appear on whitehouse.gov before they are printed in the Federal Register, which compiles them in order and provides the permanent official record.

Each presidential action carries the signature of the President, the date signed, and the full text of the instrument. Executive orders and proclamations are typically accompanied by background information or explanatory notes. The instruments cover the full range of executive authority—foreign policy, national security, personnel appointments, regulatory matters, and responses to emergencies or events.

Presidential actions form one category of official government publications. They are legally binding (in the case of executive orders), serve as formal policy announcements (proclamations), or direct executive action (memoranda). Readers of this source encounter the complete record of presidential instruments as they are issued, making it possible to follow executive action in real time as it occurs.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `whitehouse-presidential-actions` |
| Agency / parent organization | Executive Office of the President |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.whitehouse.gov/presidential-actions/feed/ |
| URL (home) | https://www.whitehouse.gov/presidential-actions/ |
| Registered | 2026-08-06 |
| Registry notes | Registered 2026-08-06 after the operator asked why the 'Ending Birth Tourism' executive order was not in the day's digest. It was not, and could not be: presidential actions reach us only through the Federal Register compilation, measured on our own record at a five-day lag (the quartz proclamation was published by the White House 2026-07-31 and appeared in the 2026-08-05 digest); the other compilation path, govinfo CPD, probed at a ~5-week lag and cannot reach a digest day at all under the §3 dating rule. Access: robots.txt is 'User-agent: * / Disallow:' — everything permitted, no crawl-delay declared — and it advertises a sitemap, so this is rung-1 directed programmatic access, not scraping. Probed 2026-08-06: HTTP 200, application/rss+xml, 619,343 bytes, verdict feed-ok, 30 items, 30/30 with pubDate, 30/30 with guid. Gate-3 content evaluation: the feed's <description> is a 400-700 character TEASER ending in an ellipsis (avg 691 chars), so the substance is NOT in the feed — full mode is required and the sample article page extracted cleanly at 8,940 characters, which is more than the feed's own <content:encoded> yields normalized (5,252 for the same document). Coverage: the feed holds 30 items spanning 2026-06-25 to 08-06 (~6 weeks) against a publication rate of roughly 2-4 presidential actions per week, so nothing published while we are polling can fall out of the window unseen. Cost: one poll plus one fetch per new item, no crawl-delay to pay. Items are tagged with the publisher's own taxonomy (Presidential Actions plus one of Executive Orders, Proclamations, Presidential Memoranda, Nominations &amp; Appointments), which drives the digest's section-9 subsections mechanically. Overlaps whitehouse-executive-orders by design; shared items carry identical link URLs and merge under the standing corroboration rule. Editorial register: GUIDE §2's attributed-speech rule applies here in full (operator, 2026-08-06) — presidential actions render attributed, exactly as agency releases do. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the presidential-actions RSS feed via AgencyClient, then fetches each new item's page for the full instrument text (mode full). |
| Adapter | presidential-actions |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 17 item(s) in the last 14 days; most recent 2026-09-17; 0 of 709 request(s) to www.whitehouse.gov returned no content.

This label has held since 2026-08-06T23:57:19Z (UTC) and was last re-checked 2026-09-18T03:55:01Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 58 request(s) (58 answered, 0 returned no content) · 3 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 17 in 14 days (1.21 per day) · most recent 2026-09-17 |
| Content length | 11,391 characters average, 10,707 median (shortest 5,045, longest 18,838) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.whitehouse.gov | 709 request(s) · 709 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-18T04:20:16.108+00:00 UTC; this host serves 2 registered sources, so these figures are host-wide.

17 item(s) in the last 14 days; most recent 2026-09-17; 0 of 709 request(s) to www.whitehouse.gov returned no content.

### All time

- **Our requests to www.whitehouse.gov, all time (since 2026-08-06):** 2,400 request(s) · 2,393 answered · 7 returned no content

This host serves 2 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.whitehouse.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-20 | 1 | 68 | 72 |
| 2026-08-21 | 0 | 57 | 48 |
| 2026-08-22 | 0 | 59 | 42 |
| 2026-08-23 | 0 | 57 | 46 |
| 2026-08-24 | 0 | 55 | 64 |
| 2026-08-25 | 1 | 52 | 40 |
| 2026-08-26 | 3 | 55 | 57 |
| 2026-08-27 | 2 | 55 | 52 |
| 2026-08-28 | 1 | 52 | 43 |
| 2026-08-29 | 0 | 51 | 43 |
| 2026-08-30 | 0 | 53 | 54 |
| 2026-08-31 | 0 | 51 | 54 |
| 2026-09-01 | 0 | 51 | 44 |
| 2026-09-02 | 0 | 56 | 113 |
| 2026-09-03 | 0 | 53 | 214 |
| 2026-09-04 | 2 | 55 | 72 |
| 2026-09-05 | 0 | 63 | 101 |
| 2026-09-06 | 0 | 51 | 52 |
| 2026-09-07 | 1 | 52 | 50 |
| 2026-09-08 | 7 | 58 | 67 |
| 2026-09-09 | 1 | 52 | 49 |
| 2026-09-10 | 0 | 51 | 77 |
| 2026-09-11 | 0 | 51 | 64 |
| 2026-09-12 | 0 | 55 | 63 |
| 2026-09-13 | 0 | 51 | 44 |
| 2026-09-14 | 1 | 58 | 140 |
| 2026-09-15 | 0 | 53 | 46 |
| 2026-09-16 | 4 | 56 | 49 |
| 2026-09-17 | 3 | 56 | 69 |
| 2026-09-18 | 0 | 2 | 64 |

## Our ingestion assessment

**Model-written ingestion assessment**

The feed continues to deliver via its established pattern: RSS descriptions average 691 characters as teasers, with full instrument text fetched from each item's page. Over the 14-day measurement window, 9 items arrived at an observed rate of 0.64 items per day, a decline from the prior 2.14 items per day documented on 2026-08-07. Document size has also decreased slightly, averaging 11,234 characters per item versus 13,141 previously. The feed retains 30 items spanning approximately six weeks of history. In the most recent 24 hours, 53 requests succeeded with no failures. However, the source experienced isolated request failures on 2026-09-02 and 2026-09-03 (7 failures out of 700 total attempts over the tracking period), and no new items have arrived since 2026-09-04. Feed entries carry publisher-supplied timestamps and globally unique identifiers, enabling deduplication. The content size variation ranges from 5,219 to 20,226 characters. The historical pattern measured on 2026-08-07 showed this feed typically delivered presidential actions approximately five days ahead of their Federal Register compilation.

_Model-written assessment of our own ingestion, generated 2026-09-07 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

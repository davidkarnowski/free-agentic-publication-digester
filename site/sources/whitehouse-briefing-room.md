<!-- Markdown twin of https://fapd.info/sources/whitehouse-briefing-room.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/whitehouse-briefing-room.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: whitehouse-briefing-room)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# White House Briefing Room

active · ingestion health: delivering · Executive · Tier 1 · HTML index · Executive Office of the President

Official site: https://www.whitehouse.gov/briefing-room/ · All sources: [sources.md](../sources.md)

## What this source is

The White House briefing room is the Executive Office of the President's direct publication channel. It carries statements, releases, remarks, and presidential actions — executive orders and proclamations as first announced, ahead of their official compilation in DCPD — typically several items per day.

**Model-written orientation**

White House statements, remarks, press releases, and presidential actions released ahead of formal publication.

The White House Briefing Room is the direct publication channel of the Executive Office of the President, serving as the administration's primary means of communicating official actions, policy, and statements to the public and media. The Briefing Room publishes statements and remarks by the President and other administration officials, press releases on administration initiatives and policy announcements, remarks delivered at events and ceremonies, and presidential actions in the form of executive orders and proclamations.

The Briefing Room publishes these materials as they are announced, typically several items per day, making it a rapid channel for official White House communications. Executive orders and proclamations appear first in the Briefing Room and are later published in the Federal Register and in the official compilations maintained by the Government Publishing Office (the Daily Compilation of Presidential Documents and the Code of Federal Regulations). Presidential statements may address pending legislation, foreign policy, domestic policy initiatives, or ceremonial matters. Press releases cover administration announcements on policy, personnel, and initiatives. Remarks include speeches, statements on current events, and remarks at ceremonies.

Readers will find official statements on administration policy priorities and decisions, the full text of executive orders and proclamations upon signing, press releases on administration actions and announcements, and remarks by the President and senior officials. The Briefing Room serves the media, policymakers, legal researchers tracking presidential actions, government employees implementing presidential directives, and the public seeking to understand White House decisions and policy.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `whitehouse-briefing-room` |
| Agency / parent organization | Executive Office of the President |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.whitehouse.gov/briefing-room/ |
| URL (index) | https://www.whitehouse.gov/news/ |
| Registered | 2026-07-26 |
| Registry notes | Fast channel: the official compilation of the same material arrives later via the planned govinfo DCPD collection. Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Research 2026-07-28: site confirmed WordPress (~2-3 items/day); the platform's /feed/ convention may be live or disabled (the first Trump-era site disabled WP RSS) — one feed-URL check at probe settles it. For presidential documents specifically, the Federal Register API's public-inspection endpoint (see federal-register-api) is the structured, official near-same-day channel and may obviate scraping this site. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 87 article link(s); 10 dated inside the 7-day lookback, 0 dated outside it, 77 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: /briefing-room/ now redirects to /news/, which is registered as the index. 10 entries dated inside the 7-day lookback (2026-09-24..27), each from the page's own <time datetime>, across releases, briefings-statements and fact-sheets. One was a proclamation under /presidential-actions/, already ingested into PRESACT by the presidential-action feeds, so index_exclude_path skips that prefix (9 remain) and no document lists in both section 6 and section 9. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only). |
| Adapter | html-index |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 28 item(s) in the last 14 days; most recent 2026-10-04; 7 of 851 request(s) to www.whitehouse.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-05T03:47:32Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 76 request(s) (76 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 28 in 14 days (2.0 per day) · most recent 2026-10-04 |
| Content length | 114 characters average, 105 median (shortest 55, longest 207) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.whitehouse.gov | 851 request(s) · 844 answered · 7 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.8% returned no content |

last answered request 2026-10-05T04:00:11.898+00:00 UTC; this host serves 3 registered sources, so these figures are host-wide.

28 item(s) in the last 14 days; most recent 2026-10-04; 7 of 851 request(s) to www.whitehouse.gov returned no content.

### All time

- **Our requests to www.whitehouse.gov, all time (since 2026-08-06):** 3,464 request(s) · 3,450 answered · 14 returned no content

This host serves 3 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.whitehouse.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-09-06 | 0 | 51 | 52 |
| 2026-09-07 | 0 | 52 | 50 |
| 2026-09-08 | 0 | 58 | 67 |
| 2026-09-09 | 0 | 52 | 49 |
| 2026-09-10 | 0 | 51 | 77 |
| 2026-09-11 | 0 | 51 | 64 |
| 2026-09-12 | 0 | 55 | 63 |
| 2026-09-13 | 0 | 51 | 44 |
| 2026-09-14 | 0 | 58 | 140 |
| 2026-09-15 | 0 | 53 | 46 |
| 2026-09-16 | 0 | 56 | 49 |
| 2026-09-17 | 0 | 56 | 69 |
| 2026-09-18 | 0 | 54 | 81 |
| 2026-09-19 | 0 | 51 | 42 |
| 2026-09-20 | 0 | 53 | 40 |
| 2026-09-21 | 0 | 57 | 72 |
| 2026-09-22 | 0 | 49 | 59 |
| 2026-09-23 | 0 | 49 | 52 |
| 2026-09-24 | 0 | 51 | 54 |
| 2026-09-25 | 0 | 54 | 61 |
| 2026-09-26 | 0 | 53 | 85 |
| 2026-09-27 | 0 | 53 | 69 |
| 2026-09-28 | 11 | 67 | 69 |
| 2026-09-29 | 4 | 85 | 53 |
| 2026-09-30 | 3 | 76 | 42 |
| 2026-10-01 | 4 | 79 | 42 |
| 2026-10-02 | 4 | 80 | 65 |
| 2026-10-03 | 1 | 76 | 39 |
| 2026-10-04 | 1 | 76 | 41 |
| 2026-10-05 | 0 | 3 | 84 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September, reading from the /news/ listing which carries releases, statements, and fact sheets. We exclude items under /presidential-actions/ to avoid duplication with proclamation feeds already ingested into the presidential actions section. We observed 11 items over 14 days. Of 709 total requests to www.whitehouse.gov, 7 returned no content, yielding a 1% failure rate; failed requests count against the request budget per policy. The listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. Entries lacking readable dates are dropped and never observation-dated.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

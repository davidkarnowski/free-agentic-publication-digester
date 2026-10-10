<!-- Markdown twin of https://fapd.info/sources/energy-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/energy-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: energy-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Energy Press Releases

active · ingestion health: delivering · Executive · Tier 1 · HTML index · Department of Energy

Official site: https://www.energy.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Department of Energy manages energy research, the national laboratories, and the nuclear weapons stockpile. Its newsroom index carries departmental press releases on funding awards, energy programs, and nuclear security, typically several items per week.

**Model-written orientation**

Department of Energy newsroom with releases on energy research, funding awards, and nuclear security.

The Department of Energy, established in 1977, manages the nation's energy policy, funds scientific research, and stewards the nuclear weapons stockpile and related security programs. The Department operates a network of national laboratories across the United States that conduct research in physics, materials science, energy efficiency, renewable energy, computational science, and related fields. It also manages the strategic petroleum reserves and coordinates the nation's response to energy emergencies.

The Department's newsroom serves as the primary public information channel for the agency's significant decisions and initiatives. Readers will find press releases announcing new funding opportunities and awards for energy research and development, announcements of research findings from Department-supported projects, updates on national laboratory achievements and initiatives, notices on nuclear security and weapons-stockpile stewardship activities, information on energy policy decisions and regulatory actions, and announcements of departmental operations, programs, and personnel changes. The newsroom typically publishes several items per week, covering the breadth of the Department's scientific and policy missions.

The Department's work spans multiple domains: scientific research fundamental to the nation's technological advancement, energy security and supplies, nuclear weapons stewardship, environmental remediation of legacy nuclear-weapons production sites, and energy efficiency and renewable-energy development. The newsroom serves researchers and institutions seeking federal funding opportunities, the energy sector and utilities, policymakers and government officials, the scientific community, media covering science and energy policy, and the public interested in federal energy and research initiatives.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `energy-newsroom` |
| Agency / parent organization | Department of Energy |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.energy.gov/newsroom |
| URL (index) | https://www.energy.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. The listing parses, but energy.gov's mega-menu puts topic, search and event links in the same date-bearing blocks as the releases, and three of them picked up a neighbouring release's date. An index_item_path of '/articles/' cuts it to 7 clean releases; that hint is registered nowhere yet because the source is not being activated. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: Without a hint the listing yields 14 dated entries, several of them mega-menu topic links carrying a neighbouring release's date. index_item_path /articles/ (recorded 2026-07-31) keeps 5 real releases (2026-09-21..25). Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 12 item(s) in the last 14 days; most recent 2026-10-08; 0 of 297 request(s) to www.energy.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-10T03:58:47Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 12 in 14 days (0.86 per day) · most recent 2026-10-08 |
| Content length | 297 characters average, 197 median (shortest 117, longest 904) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.energy.gov | 297 request(s) · 297 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-10T04:00:08.845+00:00 UTC.

12 item(s) in the last 14 days; most recent 2026-10-08; 0 of 297 request(s) to www.energy.gov returned no content.

### All time

- **Our requests to www.energy.gov, all time (since 2026-09-28):** 297 request(s) · 297 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.energy.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-11 | 0 | 0 | — |
| 2026-09-12 | 0 | 0 | — |
| 2026-09-13 | 0 | 0 | — |
| 2026-09-14 | 0 | 0 | — |
| 2026-09-15 | 0 | 0 | — |
| 2026-09-16 | 0 | 0 | — |
| 2026-09-17 | 0 | 0 | — |
| 2026-09-18 | 0 | 0 | — |
| 2026-09-19 | 0 | 0 | — |
| 2026-09-20 | 0 | 0 | — |
| 2026-09-21 | 0 | 0 | — |
| 2026-09-22 | 0 | 0 | — |
| 2026-09-23 | 0 | 0 | — |
| 2026-09-24 | 0 | 0 | — |
| 2026-09-25 | 0 | 0 | — |
| 2026-09-26 | 0 | 0 | — |
| 2026-09-27 | 0 | 0 | — |
| 2026-09-28 | 5 | 11 | 148 |
| 2026-09-29 | 1 | 27 | 84 |
| 2026-09-30 | 0 | 25 | 79 |
| 2026-10-01 | 1 | 27 | 92 |
| 2026-10-02 | 0 | 26 | 92 |
| 2026-10-03 | 0 | 25 | 87 |
| 2026-10-04 | 0 | 25 | 113 |
| 2026-10-05 | 2 | 26 | 108 |
| 2026-10-06 | 0 | 27 | 99 |
| 2026-10-07 | 0 | 26 | 101 |
| 2026-10-08 | 3 | 26 | 85 |
| 2026-10-09 | 0 | 25 | 88 |
| 2026-10-10 | 0 | 1 | 190 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September. The energy.gov newsroom index listing yields press releases carrying the publisher's own dates. We registered an index_item_path hint of /articles/ to filter out mega-menu topic and search links that were picking up neighboring release dates in the parser; the filtered listing read cleanly. We observed 5 items over 14 days from this source; the listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. All 13 requests to www.energy.gov succeeded with no failures. Entries lacking readable dates are dropped and never observation-dated. No machine-readable feeds are advertised on this source.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

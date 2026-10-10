<!-- Markdown twin of https://fapd.info/sources/ustr-press.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ustr-press.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ustr-press)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USTR Press Releases

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Executive Office of the President

Official site: https://ustr.gov/about-us/policy-offices/press-office/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Office of the United States Trade Representative, in the Executive Office of the President, negotiates trade agreements and leads trade enforcement. Its press-release index carries announcements on negotiations, tariff actions, and dispute proceedings, typically a few items per week.

**Model-written orientation**

U.S. Trade Representative press releases on trade agreements, negotiations, enforcement, and tariff actions.

The Office of the United States Trade Representative, located within the Executive Office of the President, is responsible for developing and implementing U.S. trade policy. The USTR leads negotiations on bilateral and multilateral trade agreements, represents the United States in trade dispute proceedings, manages tariff policy and trade remedies, enforces U.S. trade rights under existing agreements, and advises the President on trade matters. The USTR is one of the primary policy bodies shaping U.S. international economic relations.

The USTR's press-release index is the official channel for announcing trade policy decisions, negotiations, and enforcement actions. Readers will find press releases on the initiation, progress, and conclusion of trade negotiations with other countries, announcements of new trade agreements or modifications to existing arrangements, statements on tariff actions and trade remedies, notices of trade dispute proceedings and resolutions, enforcement actions against perceived trade violations by other countries, personnel announcements, and policy statements on trade-related matters. The USTR typically publishes a few items per week through this channel.

Materials in this feed serve businesses engaged in international trade and export, trading partners and foreign governments, trade-law and customs professionals, industry associations, media covering trade policy, and the public interested in U.S. foreign economic policy and international commerce.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ustr-press` |
| Agency / parent organization | Executive Office of the President |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://ustr.gov/about-us/policy-offices/press-office/press-releases |
| URL (index) | https://ustr.gov/about-us/policy-offices/press-office/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 459 article link(s); 1 dated inside the 7-day lookback, 366 dated outside it, 91 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 5 entries dated inside the 7-day lookback (2026-09-21..27), all press releases with USTR's own dates. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 17 item(s) in the last 14 days; most recent 2026-10-09; 0 of 295 request(s) to ustr.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-10T03:58:47Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 17 in 14 days (1.21 per day) · most recent 2026-10-09 |
| Content length | 115 characters average, 118 median (shortest 59, longest 173) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to ustr.gov | 295 request(s) · 295 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-10T04:00:11.478+00:00 UTC.

17 item(s) in the last 14 days; most recent 2026-10-09; 0 of 295 request(s) to ustr.gov returned no content.

### All time

- **Our requests to ustr.gov, all time (since 2026-09-28):** 295 request(s) · 295 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to ustr.gov | Mean response time (ms) |
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
| 2026-09-28 | 6 | 10 | 114 |
| 2026-09-29 | 0 | 27 | 65 |
| 2026-09-30 | 2 | 25 | 79 |
| 2026-10-01 | 0 | 26 | 68 |
| 2026-10-02 | 5 | 26 | 69 |
| 2026-10-03 | 0 | 26 | 65 |
| 2026-10-04 | 0 | 25 | 73 |
| 2026-10-05 | 1 | 25 | 84 |
| 2026-10-06 | 0 | 27 | 68 |
| 2026-10-07 | 1 | 26 | 69 |
| 2026-10-08 | 1 | 25 | 78 |
| 2026-10-09 | 1 | 26 | 134 |
| 2026-10-10 | 0 | 1 | 151 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September. The USTR press-release listing yields items carrying the publisher's own dates. We observed 6 items over 14 days. All 13 requests to ustr.gov succeeded with no failures. The listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. Entries lacking readable dates are dropped and never observation-dated. No machine-readable feeds are advertised on this source.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

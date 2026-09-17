<!-- Markdown twin of https://fapd.info/sources/cftc-press.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cftc-press.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cftc-press)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CFTC Press Releases

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.cftc.gov/PressRoom/PressReleases · All sources: [sources.md](../sources.md)

## What this source is

The Commodity Futures Trading Commission regulates U.S. derivatives markets. Its press-release index carries enforcement actions, rulemaking announcements, and commissioner statements, typically a few items per week.

**Model-written orientation**

The Commodity Futures Trading Commission regulates U.S. derivatives markets; its press-release index announces enforcement actions, rulemaking, and commissioner statements.

The Commodity Futures Trading Commission (CFTC) is an independent agency with authority to regulate U.S. futures, options, and derivatives markets. The CFTC oversees exchanges and clearinghouses, enforces trading rules, prevents fraud and manipulation, and sets capital and conduct requirements for firms handling customer funds. The agency plays a central role in ensuring the integrity and efficiency of derivatives markets, which serve both financial institutions and businesses managing price risks.

The CFTC's press-release index is the official publication channel for announcing enforcement actions, proposed and final rules, commissioner statements, market-surveillance findings, and policy initiatives. The index is formatted as an HTML table containing releases with dates stated by the CFTC. Releases typically appear a few times per week. The index maintains approximately five months of output at any given time, reflecting the agency's typical publication pace.

Items in the index cover enforcement actions against firms or individuals for market violations, proposed and final rulemakings affecting trading participants, statements from CFTC commissioners on policy matters or market conditions, announcements of trading halts or market actions, updates on agency initiatives or priorities, and findings from CFTC market surveillance or research. Readers will encounter official CFTC announcements of enforcement decisions, regulatory guidance and rule changes, commissioner statements on derivatives-market policy and conditions, and statements on market-related matters.

All releases represent official CFTC communications and carry institutional authority. The press-release index serves as the authoritative source for CFTC enforcement decisions, regulatory rulemakings, policy announcements, and market-related statements affecting U.S. derivatives markets.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cftc-press` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.cftc.gov/PressRoom/PressReleases |
| URL (index) | https://www.cftc.gov/PressRoom/PressReleases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered. Re-probed 2026-07-31: HTTP 200, robots allows, still no feed. ACTIVATED 2026-07-31 with the html-index adapter. Gate 3: the press-release index is an HTML table of 37 releases — roughly five months of output at CFTC's few-per-week rate — and every row states its date twice, as a <time datetime> and as visible 07/31/2026 text, so the whole table is agency-dated and nothing is dated by observation. The stored text is the row itself (headline plus release number, ~20 chars); the release body is on the linked page and is deliberately not fetched (mode feed-only, one request per poll), because section 6 renders the attributed title and citation and nothing more. Depth is generous enough that pagination is not a risk here. |

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

**delivering** — 6 item(s) in the last 14 days; most recent 2026-09-15; 0 of 352 request(s) to www.cftc.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-17T03:58:34Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 6 in 14 days (0.43 per day) · most recent 2026-09-15 |
| Content length | 129 characters average, 132 median (shortest 79, longest 203) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.cftc.gov | 352 request(s) · 352 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-17T04:25:07.130+00:00 UTC.

6 item(s) in the last 14 days; most recent 2026-09-15; 0 of 352 request(s) to www.cftc.gov returned no content.

### All time

- **Our requests to www.cftc.gov, all time (since 2026-08-01):** 1,377 request(s) · 1,377 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.cftc.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-19 | 2 | 24 | 71 |
| 2026-08-20 | 1 | 34 | 150 |
| 2026-08-21 | 1 | 30 | 70 |
| 2026-08-22 | 0 | 29 | 57 |
| 2026-08-23 | 0 | 29 | 74 |
| 2026-08-24 | 0 | 28 | 97 |
| 2026-08-25 | 0 | 26 | 72 |
| 2026-08-26 | 0 | 25 | 86 |
| 2026-08-27 | 0 | 26 | 89 |
| 2026-08-28 | 1 | 25 | 61 |
| 2026-08-29 | 0 | 27 | 52 |
| 2026-08-30 | 0 | 27 | 90 |
| 2026-08-31 | 1 | 26 | 75 |
| 2026-09-01 | 1 | 26 | 59 |
| 2026-09-02 | 2 | 26 | 77 |
| 2026-09-03 | 0 | 26 | 63 |
| 2026-09-04 | 0 | 26 | 70 |
| 2026-09-05 | 0 | 32 | 213 |
| 2026-09-06 | 0 | 26 | 67 |
| 2026-09-07 | 0 | 26 | 66 |
| 2026-09-08 | 0 | 26 | 63 |
| 2026-09-09 | 1 | 26 | 76 |
| 2026-09-10 | 1 | 26 | 75 |
| 2026-09-11 | 2 | 26 | 72 |
| 2026-09-12 | 0 | 30 | 114 |
| 2026-09-13 | 0 | 26 | 90 |
| 2026-09-14 | 1 | 28 | 225 |
| 2026-09-15 | 1 | 27 | 59 |
| 2026-09-16 | 0 | 26 | 83 |
| 2026-09-17 | 0 | 1 | 70 |

## Our ingestion assessment

**Model-written ingestion assessment**

The press-release index is an HTML table with agency-dated entries across roughly five months of output at the publisher's few-per-week cadence. We poll in feed-only mode. Over 14 days, 5 items arrived at 0.36 per day, a slight decline from the previous 0.43 per day. Stored text consists of headline and release number (average 110 characters); linked release bodies are not fetched. All 344 polling requests succeeded. The most recent item was published on 2026-09-02.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

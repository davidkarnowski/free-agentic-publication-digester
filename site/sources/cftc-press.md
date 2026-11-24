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

**delivering** — 7 item(s) in the last 14 days; most recent 2026-11-23; 0 of 333 request(s) to www.cftc.gov returned no content.

This label has held since 2026-10-19T19:18:28Z (UTC) and was last re-checked 2026-11-24T04:53:50Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 24 request(s) (24 answered, 0 returned no content) · 3 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 7 in 14 days (0.5 per day) · most recent 2026-11-23 |
| Content length | 103 characters average, 104 median (shortest 68, longest 129) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.cftc.gov | 333 request(s) · 333 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-11-24T05:00:16.040+00:00 UTC.

7 item(s) in the last 14 days; most recent 2026-11-23; 0 of 333 request(s) to www.cftc.gov returned no content.

### All time

- **Our requests to www.cftc.gov, all time (since 2026-08-01):** 3,061 request(s) · 3,061 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.cftc.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-26 | 1 | 25 | 81 |
| 2026-10-27 | 3 | 25 | 88 |
| 2026-10-28 | 1 | 24 | 76 |
| 2026-10-29 | 0 | 25 | 58 |
| 2026-10-30 | 0 | 26 | 68 |
| 2026-10-31 | 0 | 25 | 54 |
| 2026-11-01 | 0 | 26 | 54 |
| 2026-11-02 | 0 | 26 | 74 |
| 2026-11-03 | 2 | 25 | 68 |
| 2026-11-04 | 1 | 25 | 75 |
| 2026-11-05 | 2 | 26 | 80 |
| 2026-11-06 | 0 | 25 | 84 |
| 2026-11-07 | 0 | 25 | 81 |
| 2026-11-08 | 0 | 26 | 70 |
| 2026-11-09 | 1 | 26 | 76 |
| 2026-11-10 | 0 | 25 | 81 |
| 2026-11-11 | 0 | 25 | 81 |
| 2026-11-12 | 0 | 30 | 80 |
| 2026-11-13 | 2 | 26 | 85 |
| 2026-11-14 | 0 | 25 | 62 |
| 2026-11-15 | 0 | 25 | 56 |
| 2026-11-16 | 0 | 26 | 76 |
| 2026-11-17 | 1 | 25 | 67 |
| 2026-11-18 | 0 | 25 | 82 |
| 2026-11-19 | 0 | 25 | 66 |
| 2026-11-20 | 1 | 25 | 61 |
| 2026-11-21 | 0 | 26 | 59 |
| 2026-11-22 | 0 | 25 | 49 |
| 2026-11-23 | 3 | 24 | 60 |
| 2026-11-24 | 0 | 1 | 100 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest the CFTC Press Releases index through the html-index adapter in feed-only mode, reading one HTML listing fetch per poll and no article pages. The source was activated on 2026-07-31. Each row of the press-release table states its date twice, as a machine-readable datetime attribute and as visible text, so every entry is dated by the publisher and none by observation. The stored text is the row itself, a headline with its release number, and the linked release body is not fetched. Over the 14-day window we recorded 4 items at 0.29 per day, the most recent dated 2026-11-17, with item text averaging 109 characters (range 84 to 132). The previous assessment recorded 3 items at 0.21 per day, the most recent dated 2026-10-19, and a 148-character average. All 335 requests to www.cftc.gov returned content, an error rate of 0.0 percent, compared with 329 successful requests and no errors in the previous window. The registry notes record the probes, the activation, and a table of about 37 releases, with no incidents. Health reads delivering, with the most recent item 2 days old.

_Model-written assessment of our own ingestion, generated 2026-11-19 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

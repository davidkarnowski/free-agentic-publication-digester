<!-- Markdown twin of https://fapd.info/sources/fhfa-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fhfa-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fhfa-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FHFA News Releases

planned · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.fhfa.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Federal Housing Finance Agency regulates Fannie Mae, Freddie Mac, and the Federal Home Loan Bank System, and acts as conservator of the enterprises. Its news index carries releases on housing-finance policy, house-price data, and enterprise oversight, typically a few items per week.

**Model-written orientation**

The Federal Housing Finance Agency regulates Fannie Mae, Freddie Mac, and the Federal Home Loan Bank System, and publishes policy announcements and data releases on housing finance.

The Federal Housing Finance Agency (FHFA) is an independent agency that plays a central role in the nation's housing-finance system. Created by the Housing and Economic Recovery Act of 2008, FHFA has statutory responsibility to regulate and oversee Fannie Mae, Freddie Mac, and the Federal Home Loan Bank System—collectively, the government-sponsored enterprises and banks that provide liquidity and stability to the mortgage market. Following the 2008 financial crisis, FHFA also serves as conservator of Fannie Mae and Freddie Mac, managing their operations to ensure they continue to support the mortgage market while protecting taxpayers.

FHFA's mission spans housing-finance policy, market operations, and institutional supervision. The agency publishes releases on capital standards, mortgage-purchase rules, lending requirements, and other regulatory actions affecting the enterprises and the Home Loan Banks. It also releases data products such as house-price indexes, which track residential real-estate values across the country and are widely used by investors, researchers, and policymakers to understand housing-market conditions.

In this digest, you will see releases announcing new regulations or amendments to existing rules, data releases (particularly house-price indexes and mortgage-market statistics), and statements on enterprise capital levels, dividends, or conservatorship milestones. The releases are grounded in FHFA's statutory mandates and public-interest functions. FHFA's work operates at the intersection of banking regulation, housing policy, and financial stability, and its public notices inform participants in the mortgage market and the broader public of significant changes in housing finance.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fhfa-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.fhfa.gov/news |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 103 article link(s); 0 dated inside the 7-day lookback, 0 dated outside it, 103 skipped for no readable date — the served HTML states no per-entry publication date, so every entry is skipped rather than dated by observation. This is a script-rendered listing; opening it needs evidence of a dated channel, not a cadence decision. Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | HTML index diff via AgencyClient (pending content evaluation) |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.fhfa.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

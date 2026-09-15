<!-- Markdown twin of https://fapd.info/sources/bls-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/bls-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: bls-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# BLS News Releases

planned · Executive · Tier 2 · RSS feed · Department of Labor (Bureau of Labor Statistics)

Official site: https://www.bls.gov/newsroom/ · All sources: [sources.md](../sources.md)

## What this source is

The Bureau of Labor Statistics publishes the government's most market-sensitive statistical releases — the Employment Situation, CPI, and workplace-injury reports — with documented news-release RSS feeds and a developer API. Statistical releases do not flow through the DOL newsroom feed we already ingest.

**Model-written orientation**

The Bureau of Labor Statistics publishes official statistical releases covering employment, prices, and workplace conditions, with news releases distributed via RSS feeds.

The Bureau of Labor Statistics, a division of the Department of Labor, produces the federal government's official statistics on labor markets, prices, and workplace safety. These statistics carry particular weight in the economy and policy because they form the baseline measurement for economic conditions and are closely monitored by investors, employers, policymakers, and the public.

BLS publishes several major statistical releases on regular schedules. The Employment Situation report, released monthly, contains current unemployment rates and job creation figures. The Consumer Price Index (CPI) measures price changes across categories of goods and services, serving as the primary inflation metric. Workplace injury and illness reports track safety outcomes across industries. These statistical releases are distinct from general agency news and are published through dedicated feeds organized by program.

Each statistical release goes through a formal process: data collection, analysis, review, and coordinated public release at a specific time. The release includes both the headline figures and detailed breakdowns by industry, region, demographic group, and other dimensions. News releases accompanying the data highlight key findings and provide context for interpretation.

Unlike political or discretionary announcements, BLS releases follow a mechanical publication calendar established well in advance. The statistical content itself is produced according to documented methodologies that remain consistent over time, making the data comparable across years and suitable for trend analysis.

For the digest, BLS releases represent the government's authoritative measurement of labor-market conditions and economic price levels—foundational data points for understanding federal economic policy and conditions.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `bls-news` |
| Agency / parent organization | Department of Labor (Bureau of Labor Statistics) |
| Branch | executive |
| Type | RSS feed |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.bls.gov/newsroom/ |
| URL (index) | https://www.bls.gov/feed/ |
| Registered | 2026-07-28 |
| Registry notes | Feeds page documented at bls.gov/feed (2026-07-28). Probe 2026-07-28: the guessed URL bls.gov/feed/news_release.rss returned 404 — the convention guess was wrong; robots and host are open (robots.txt HTTP 200, no block). Next step: fetch the bls.gov/feed documentation page itself through AgencyClient to read the exact feed URLs, then re-probe. Resolved 2026-07-31 (operator machine, off the server budget) by doing exactly that: bls.gov/feed/ answers HTTP 200 to our identified client and documents about 55 feeds, and NONE of them is an agency-wide news-release stream. The list is two families: ~42 per-program release feeds (empsit.rss, cpi.rss, ppi.rss, jolts.rss, ...) and ~13 *_latest.rss 'Latest Numbers' data feeds. Sampled evidence: empsit.rss is Atom, 12 items, every one with a guid and a date, ~259-character descriptions, linking to the real news-release pages — genuinely ingestible; bls_latest.rss is a single-item dashboard rollup with no guid, not a news stream. bls.gov/newsroom/ advertises no feed and autodiscovers none. So the correct registered address is the feed directory, not a feed: one registry entry cannot represent this source honestly. Left planned. The right shape is a fan-out — one entry per program feed, starting with the market-sensitive ones (empsit, cpi, ppi, jolts, eci, realer) — or a multi-feed adapter; either is a new-source decision, not a URL correction. Note for whoever picks it up: bls.gov returns 403 to unidentified fetchers but 200 to ours, so read its documentation through AgencyClient. Re-probe through scripts/check_sources.py, 2026-07-31: verdict html-only against the feed directory — HTTP 200, 66 KB, 7,591 characters — which is the accurate verdict, because the registered address is a catalogue of feeds and not a feed. Probed 2026-07-31: registered URL returned 404 (https://www.bls.gov/feed/news_release.rss) — the publisher moved or retired it; not a refusal. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Would poll the documented news-release feeds daily; the v2 API (api.bls.gov, registered key, 500 queries/day) is a later data extension. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.bls.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

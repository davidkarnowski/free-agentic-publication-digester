<!-- Markdown twin of https://fapd.info/sources/usps-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usps-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usps-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USPS Newsroom

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Independent establishment

Official site: https://about.usps.com/newsroom/national-releases/ · All sources: [sources.md](../sources.md)

## What this source is

The United States Postal Service is an independent establishment providing mail and package delivery. This autodiscovered RSS feed carries national news releases — stamp issuances, rates, service changes, and operations — as lede-paragraph descriptions with unusually deep history (668 items, ~270 characters each, no GUIDs); feed links route through a JavaScript redirect interstitial that carries no article text.

**Model-written orientation**

The United States Postal Service, an independent establishment, operates the national mail and package delivery network serving every address in the United States.

The United States Postal Service (USPS) is an independent establishment of the federal government that operates the nation's universal mail and package delivery system. The USPS is constitutionally mandated to provide mail service and operates a network of post offices and delivery facilities reaching every address in the United States, regardless of geography or profitability. The agency employs hundreds of thousands of postal workers and maintains one of the world's largest logistics networks. USPS provides several categories of mail service: First-Class Mail for letters and small packages, Priority Mail for faster delivery of packages, Priority Mail Express for overnight or two-day delivery, Media Mail for educational materials, and other specialized services. The agency also handles the distribution and sale of postage stamps and provides services such as money orders and notary services at post offices. The USPS newsroom publishes announcements through an RSS feed covering national news releases. The feed carries several hundred recent releases with brief descriptions of announcement topics. Readers of USPS newsroom materials in this digest will see announcements about postage rate changes or adjustments to mail service, new stamp designs and commemorative stamp series, changes to mail delivery schedules or service standards, announcements about facility consolidations, closures, or relocations, operational updates affecting mail or package delivery, customer service initiatives, and other agency announcements. The feed maintains a substantial archive reflecting the ongoing nature of postal operations and the agency's regular communications with customers and the public about service matters. USPS materials document the agency's public announcements regarding its role in providing mail and package delivery services and reflect the operational decisions and initiatives of the nation's postal service.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usps-newsroom` |
| Agency / parent organization | Independent establishment |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://about.usps.com/news/latestnews.rss |
| URL (home) | https://about.usps.com/newsroom/national-releases/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26; captured bytes re-examined 2026-07-28: feed verified — 668 items, ~270-char lede-paragraph descriptions with datelines, no GUIDs. Every feed link routes through /newsroom/rssrequest.htm?nr=<article-path>, and the captured sample-article bytes are that 1.8 KB JavaScript redirect interstitial, not an article: it embeds NO content (no JSON-LD, no framework state blob; its entire visible text is 'RSS Feed Request' — the probe's 16-char extraction). The real article pages at /newsroom/<nr> were never fetched, so their extractability is unknown, not proven bad. The usps adapter therefore: (1) derives document identity by statically resolving nr= to the canonical article URL, normalized (lowercase host, query/fragment/trailing slash stripped) — dedupes URL variants despite the missing GUIDs; (2) ingests feed-metadata only (title + lede description, mode feed-only), never spending a request per item on the known-contentless interstitial. Can extract: titles, ~270-char ledes, claimed dates, canonical article URLs. Cannot extract: full article text — would require a deliberate re-probe of a resolved direct article URL (e.g. /newsroom/national-releases/2026/...htm) before any change to this posture. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | RSS poll via AgencyClient, feed-metadata only (usps adapter; pending content evaluation) |
| Adapter | usps |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 7 item(s) in the last 14 days; most recent 2026-09-23; 0 of 347 request(s) to about.usps.com returned no content.

This label has held since 2026-09-08T15:31:58Z (UTC) and was last re-checked 2026-09-24T03:57:29Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 7 in 14 days (0.5 per day) · most recent 2026-09-23 |
| Content length | 270 characters average, 278 median (shortest 193, longest 354) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to about.usps.com | 347 request(s) · 347 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-24T04:46:20.234+00:00 UTC.

7 item(s) in the last 14 days; most recent 2026-09-23; 0 of 347 request(s) to about.usps.com returned no content.

### All time

- **Our requests to about.usps.com, all time (since 2026-08-01):** 1,565 request(s) · 1,564 answered · 1 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to about.usps.com | Mean response time (ms) |
|---|---|---|---|
| 2026-08-26 | 0 | 26 | 255 |
| 2026-08-27 | 0 | 26 | 225 |
| 2026-08-28 | 1 | 26 | 357 |
| 2026-08-29 | 0 | 27 | 167 |
| 2026-08-30 | 0 | 26 | 217 |
| 2026-08-31 | 0 | 26 | 196 |
| 2026-09-01 | 0 | 26 | 175 |
| 2026-09-02 | 0 | 26 | 260 |
| 2026-09-03 | 0 | 27 | 402 |
| 2026-09-04 | 0 | 26 | 263 |
| 2026-09-05 | 0 | 33 | 304 |
| 2026-09-06 | 0 | 27 | 204 |
| 2026-09-07 | 0 | 26 | 198 |
| 2026-09-08 | 2 | 26 | 203 |
| 2026-09-09 | 0 | 26 | 191 |
| 2026-09-10 | 0 | 25 | 491 |
| 2026-09-11 | 0 | 26 | 184 |
| 2026-09-12 | 1 | 29 | 288 |
| 2026-09-13 | 0 | 26 | 227 |
| 2026-09-14 | 1 | 29 | 578 |
| 2026-09-15 | 0 | 26 | 223 |
| 2026-09-16 | 0 | 26 | 176 |
| 2026-09-17 | 1 | 26 | 232 |
| 2026-09-18 | 1 | 26 | 219 |
| 2026-09-19 | 1 | 26 | 216 |
| 2026-09-20 | 0 | 26 | 155 |
| 2026-09-21 | 0 | 28 | 315 |
| 2026-09-22 | 1 | 27 | 199 |
| 2026-09-23 | 1 | 25 | 374 |
| 2026-09-24 | 0 | 1 | 1091 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest from the USPS Newsroom RSS feed in feed-only mode, extracting titles and lede-paragraph descriptions averaging 319 characters. The feed delivers links through JavaScript redirects containing no article text; we resolve canonical article URLs for deduplication without using feed GUIDs. Requests to about.usps.com have maintained a 0.3% error rate (1 of 349 requests unanswered). Over the past 14 days, 3 items have arrived, with the most recent on 2026-09-08. The observed delivery rate is 0.21 items per day. Compared to the previous assessment on 2026-09-06, which recorded 4 items (most recent 2026-08-28) at an average of 335 characters, the current 14-day window shows 3 items averaging 319 characters.

_Model-written assessment of our own ingestion, generated 2026-09-09 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

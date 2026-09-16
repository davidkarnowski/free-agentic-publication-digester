<!-- Markdown twin of https://fapd.info/sources/sec-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/sec-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: sec-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# SEC Press Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Independent agency

Official site: https://www.sec.gov/newsroom/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Securities and Exchange Commission regulates securities markets and public-company disclosure. This RSS feed carries its press releases — enforcement actions, rulemakings, and commission announcements — as teaser descriptions (25 recent items, ~250 characters each; article pages extract at ~5,000 characters).

**Model-written orientation**

The SEC publishes press releases announcing enforcement actions, settlements, and rulemakings related to securities markets and public-company disclosure.

The Securities and Exchange Commission is an independent agency created by Congress in 1934 to administer federal securities law and protect investors. The SEC exercises regulatory authority over securities markets, broker-dealers, investment advisers and companies, and publicly traded corporations. The Commission's Division of Enforcement investigates alleged violations of securities law and brings civil enforcement actions; the Department of Justice may pursue parallel criminal prosecutions.

The SEC's press-release channel carries announcements of significant Commission actions: enforcement proceedings and settlements against market participants, proposed and finalized regulations affecting securities markets and disclosure requirements, examination results and targeted investigations by the agency's inspection division, and policy guidance on securities law matters.

Pressure releases typically summarize charges against individuals or firms, agreed settlement terms and remedies, descriptions of alleged violations, and the factual bases underlying enforcement actions. Readers will encounter enforcement matters involving insider trading, disclosure violations by public companies or securities professionals, investment advisory fraud and fiduciary breaches, market manipulation, and fraudulent schemes. The releases also announce rulemakings addressing topics such as public-company proxy voting procedures, executive compensation disclosure, beneficial ownership reporting, cybersecurity requirements, and investment fund operations. Each press release provides an accessible summary of a Commission decision, with references to full legal documents—complaints, settlement orders, and rule text—available through the SEC's official websites and the Federal Register.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `sec-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.sec.gov/news/pressreleases.rss |
| URL (home) | https://www.sec.gov/newsroom/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 25 items, avg description 251 chars, sample article extracted (5315 chars text). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Would poll the press-release RSS feed daily for new items. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 8 item(s) in the last 14 days; most recent 2026-09-14; 2 of 362 request(s) to www.sec.gov returned no content.

This label has held since 2026-08-27T22:46:31Z (UTC) and was last re-checked 2026-09-16T04:00:04Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 8 in 14 days (0.57 per day) · most recent 2026-09-14 |
| Content length | 5,703 characters average, 5,590 median (shortest 4,079, longest 8,779) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.sec.gov | 362 request(s) · 360 answered · 0 declined (4xx) · 0 server declined (5xx) · 2 no response — 0.6% returned no content |

last answered request 2026-09-16T04:14:23.640+00:00 UTC.

8 item(s) in the last 14 days; most recent 2026-09-14; 2 of 362 request(s) to www.sec.gov returned no content.

### All time

- **Our requests to www.sec.gov, all time (since 2026-07-30):** 1,434 request(s) · 1,431 answered · 3 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.sec.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-18 | 2 | 29 | 164 |
| 2026-08-19 | 0 | 24 | 170 |
| 2026-08-20 | 0 | 34 | 216 |
| 2026-08-21 | 0 | 30 | 156 |
| 2026-08-22 | 0 | 30 | 154 |
| 2026-08-23 | 0 | 29 | 172 |
| 2026-08-24 | 0 | 28 | 180 |
| 2026-08-25 | 0 | 25 | 148 |
| 2026-08-26 | 0 | 25 | 161 |
| 2026-08-27 | 1 | 27 | 151 |
| 2026-08-28 | 1 | 26 | 143 |
| 2026-08-29 | 0 | 27 | 148 |
| 2026-08-30 | 0 | 27 | 169 |
| 2026-08-31 | 1 | 27 | 199 |
| 2026-09-01 | 3 | 29 | 155 |
| 2026-09-02 | 0 | 26 | 833 |
| 2026-09-03 | 2 | 29 | 1848 |
| 2026-09-04 | 0 | 27 | 211 |
| 2026-09-05 | 0 | 33 | 256 |
| 2026-09-06 | 0 | 26 | 178 |
| 2026-09-07 | 0 | 26 | 165 |
| 2026-09-08 | 0 | 26 | 155 |
| 2026-09-09 | 0 | 26 | 169 |
| 2026-09-10 | 4 | 29 | 137 |
| 2026-09-11 | 1 | 27 | 142 |
| 2026-09-12 | 0 | 30 | 176 |
| 2026-09-13 | 0 | 26 | 185 |
| 2026-09-14 | 1 | 30 | 301 |
| 2026-09-15 | 0 | 26 | 131 |
| 2026-09-16 | 0 | 1 | 114 |

## Our ingestion assessment

**Model-written ingestion assessment**

The SEC Press Releases RSS feed carries enforcement actions, rulemakings, and commission announcements as teaser descriptions paired with full-text extraction from article pages. Over the 14-day measurement window we received 3 items averaging 6,861 characters per extracted article. Of 386 polling requests to www.sec.gov, 385 succeeded; one returned no content (0.3% error rate). The most recent item arrived on August 27. Compared to our previous assessment two days ago, which found one item in that window, delivery has resumed. Extracted article length has continued to increase from the previous average of 6,334 characters.

_Model-written assessment of our own ingestion, generated 2026-08-28 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

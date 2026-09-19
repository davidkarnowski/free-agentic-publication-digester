<!-- Markdown twin of https://fapd.info/sources/fda-press.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fda-press.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fda-press)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FDA Press Announcements

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Department of Health and Human Services

Official site: https://www.fda.gov/news-events/fda-newsroom/press-announcements · All sources: [sources.md](../sources.md)

## What this source is

The Food and Drug Administration regulates drugs, medical devices, food safety, and tobacco. This RSS feed carries its press announcements — approvals, recalls, enforcement actions, and public-health advisories — as teaser descriptions (20 recent items, ~230 characters each; article pages extract cleanly at ~7,000 characters).

**Model-written orientation**

The Food and Drug Administration regulates the safety and efficacy of drugs, medical devices, food, dietary supplements, and tobacco products.

The Food and Drug Administration (FDA) is a federal agency within the Department of Health and Human Services responsible for regulating the safety, efficacy, and labeling of drugs, biological products, and medical devices; ensuring the safety of the nation's food supply and dietary supplements; regulating the manufacture, marketing, and sale of tobacco products; and overseeing other products under its jurisdiction. The FDA reviews and approves new drugs and medical devices before they can be marketed, based on evidence of safety and efficacy submitted by manufacturers. The agency monitors the safety of products already on the market through adverse event reporting systems, inspection programs, and post-market surveillance, and investigates reports of product defects or safety concerns. When products are found to pose risks to public health, the FDA may request or require recalls, issue warnings, or take enforcement actions. The agency also establishes and enforces standards for food production, manufacturing, labeling, and safety, inspects food facilities, and works with state and local authorities on food safety. The FDA's press office announces new drug approvals and medical device clearances, product recalls and safety warnings, enforcement actions taken against manufacturers or distributors, public health advisories, guidance documents, and policy announcements. Readers of FDA press releases in this digest will see announcements of FDA approval of new medications or medical devices, notices of product recalls due to safety defects or contamination risks, enforcement actions taken against companies for regulatory violations, public health warnings or advisories issued by the agency regarding risks associated with specific products or practices, recalls of food products due to contamination or safety concerns, and information about FDA policies and regulatory initiatives. The press feed carries descriptions of recent announcements, with full article texts providing additional detail and context. FDA materials document the agency's regulatory activities and public health actions and provide information about the government's oversight of drugs, medical devices, food, dietary supplements, and tobacco products.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fda-press` |
| Agency / parent organization | Department of Health and Human Services |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml |
| URL (home) | https://www.fda.gov/news-events/fda-newsroom/press-announcements |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 20 items, avg description 233 chars, sample article extracted (7227 chars text). Email sibling registered 2026-07-29: fda-email (GUIDE §3 email class; the web status here is unchanged). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | RSS poll via AgencyClient (pending content evaluation) |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 2 item(s) in the last 14 days; most recent 2026-09-17; 0 of 346 request(s) to www.fda.gov returned no content.

This label has held since 2026-09-15T14:20:47Z (UTC) and was last re-checked 2026-09-19T03:52:51Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 28 request(s) (28 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-09-17 |
| Content length | 7,473 characters average, 7,473 median (shortest 7,041, longest 7,905) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.fda.gov | 346 request(s) · 346 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-19T04:05:46.742+00:00 UTC.

2 item(s) in the last 14 days; most recent 2026-09-17; 0 of 346 request(s) to www.fda.gov returned no content.

### All time

- **Our requests to www.fda.gov, all time (since 2026-07-30):** 1,511 request(s) · 1,510 answered · 1 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.fda.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-21 | 0 | 30 | 210 |
| 2026-08-22 | 0 | 30 | 207 |
| 2026-08-23 | 0 | 28 | 218 |
| 2026-08-24 | 0 | 28 | 240 |
| 2026-08-25 | 1 | 27 | 209 |
| 2026-08-26 | 1 | 27 | 190 |
| 2026-08-27 | 2 | 28 | 220 |
| 2026-08-28 | 1 | 27 | 191 |
| 2026-08-29 | 0 | 26 | 196 |
| 2026-08-30 | 0 | 26 | 224 |
| 2026-08-31 | 0 | 26 | 203 |
| 2026-09-01 | 0 | 27 | 204 |
| 2026-09-02 | 0 | 27 | 317 |
| 2026-09-03 | 3 | 29 | 714 |
| 2026-09-04 | 2 | 28 | 259 |
| 2026-09-05 | 0 | 33 | 311 |
| 2026-09-06 | 0 | 26 | 222 |
| 2026-09-07 | 0 | 26 | 208 |
| 2026-09-08 | 0 | 26 | 215 |
| 2026-09-09 | 0 | 25 | 239 |
| 2026-09-10 | 0 | 26 | 161 |
| 2026-09-11 | 0 | 26 | 156 |
| 2026-09-12 | 0 | 28 | 266 |
| 2026-09-13 | 0 | 25 | 285 |
| 2026-09-14 | 0 | 30 | 310 |
| 2026-09-15 | 1 | 27 | 175 |
| 2026-09-16 | 0 | 27 | 177 |
| 2026-09-17 | 1 | 26 | 187 |
| 2026-09-18 | 0 | 27 | 209 |
| 2026-09-19 | 0 | 1 | 174 |

## Our ingestion assessment

**Model-written ingestion assessment**

We poll the FDA press announcements RSS feed and retrieve full article text from each item's linked page. The feed delivers teasers of approximately 230 characters; extracted text from articles ranges from 5,196 to 7,905 characters, with a median of 6,380 characters. Over the past 14 days, we observed 6 items at a rate of 0.43 per day, an increase from the previous measurement's 0.36 per day. The most recent item dates to September 15, representing a resumption of deliveries after an 8-day quiet period noted in the prior assessment. Our polling requests achieved a 100% success rate, with all 356 requests to www.fda.gov returning content, improving from the prior period when one request returned no content. Polling maintains a consistent hourly cadence throughout the measurement window. An associated email-based FDA source continues to operate in parallel.

_Model-written assessment of our own ingestion, generated 2026-09-16 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

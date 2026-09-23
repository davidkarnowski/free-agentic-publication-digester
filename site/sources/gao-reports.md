<!-- Markdown twin of https://fapd.info/sources/gao-reports.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/gao-reports.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: gao-reports)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# GAO Reports & Testimonies

active · ingestion health: delivering · Legislative · Tier 1 · RSS feed · Government Accountability Office

Official site: https://www.gao.gov/reports-testimonies · All sources: [sources.md](../sources.md)

## What this source is

The Government Accountability Office is Congress's audit and oversight arm. This RSS feed carries its reports and testimonies — program audits, evaluations, and legal decisions — with long report-summary descriptions (25 recent items, ~4,000 characters each; report pages extract at ~9,000 characters).

**Model-written orientation**

The Government Accountability Office serves as Congress's independent audit and investigative arm, publishing reports and testimonies on federal programs and operations. The digest draws from the GAO's RSS feed of reports and testimonies.

The Government Accountability Office (GAO) is an independent, nonpartisan agency of the federal government that serves Congress. GAO is often referred to as the investigative arm of Congress and the supreme audit institution of the federal government. The agency conducts comprehensive evaluations and audits of federal programs, policies, and operations; examines federal agency performance and effectiveness; provides legal opinions and decisions on government operations and authority; and conducts investigations into federal spending and program implementation.

GAO reports and testimonies cover a wide range of federal operations and concerns. Program audits examine the efficiency, effectiveness, and proper use of federal resources in specific government programs and initiatives. Performance evaluations assess how well federal agencies are implementing their mandates and serving their missions. Legal decisions and opinions address questions of federal authority, government operations, and compliance with federal law. GAO reports typically include detailed analyses, findings based on GAO's investigations and reviews, supporting evidence, and recommendations for agency action. Reports are written at varying levels of technical complexity and depth depending on their subject matter.

The digest draws from the GAO's official RSS feed, which publishes notices of new and updated reports and testimonies as they are released. Each RSS feed entry includes a summary of the report's content written by GAO, along with metadata identifying the subject matter, affected agencies, and the date of publication or most recent update. These summaries provide the essential content and context readers need to understand each report's significance and scope. GAO publishes reports as its work is completed and released, typically resulting in new items most business days throughout the year. Readers can expect to encounter rigorous, evidence-based analysis of federal agency performance and government operations.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `gao-reports` |
| Agency / parent organization | Government Accountability Office |
| Branch | legislative |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.gao.gov/rss/reports.xml |
| URL (home) | https://www.gao.gov/reports-testimonies |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 25 items, avg description 4083 chars, sample article extracted (8987 chars text). robots.txt sets Crawl-delay: 420 in its User-agent: * block — the server's stated limit for all crawlers, honored without exception; that prices each article fetch at 7 minutes of wall clock. Posture decision 2026-07-28: feed-only (adapter rss-feed-only) — the ~4,000-char descriptions are GAO's own report summaries and carry the digest-relevant substance; the article page (~9,000 chars) adds mostly site furniture. Fewer requests, not faster ones. 16 bootstrap items ingested as full before the switch; later items are feed-only — both modes disclosed per item. Revisit if a report's summary proves insufficient (targeted single fetches remain possible within the delay). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | RSS poll via AgencyClient, feed metadata only (crawl-delay economics; see notes). |
| Adapter | rss-feed-only |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 35 item(s) in the last 14 days; most recent 2026-09-22; 0 of 346 request(s) to www.gao.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-23T03:59:19Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · 3 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 35 in 14 days (2.5 per day) · most recent 2026-09-22 |
| Content length | 3,929 characters average, 3,772 median (shortest 1,092, longest 7,366) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.gao.gov | 346 request(s) · 346 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-23T05:17:42.016+00:00 UTC.

35 item(s) in the last 14 days; most recent 2026-09-22; 0 of 346 request(s) to www.gao.gov returned no content.

### All time

- **Our requests to www.gao.gov, all time (since 2026-07-30):** 1,580 request(s) · 1,580 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.gao.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-25 | 0 | 26 | 167 |
| 2026-08-26 | 2 | 26 | 176 |
| 2026-08-27 | 2 | 26 | 216 |
| 2026-08-28 | 1 | 25 | 187 |
| 2026-08-29 | 0 | 26 | 175 |
| 2026-08-30 | 0 | 26 | 197 |
| 2026-08-31 | 2 | 26 | 165 |
| 2026-09-01 | 1 | 26 | 159 |
| 2026-09-02 | 1 | 26 | 460 |
| 2026-09-03 | 6 | 26 | 446 |
| 2026-09-04 | 1 | 26 | 254 |
| 2026-09-05 | 0 | 33 | 276 |
| 2026-09-06 | 0 | 26 | 184 |
| 2026-09-07 | 0 | 25 | 226 |
| 2026-09-08 | 3 | 26 | 178 |
| 2026-09-09 | 0 | 26 | 160 |
| 2026-09-10 | 3 | 26 | 168 |
| 2026-09-11 | 1 | 25 | 166 |
| 2026-09-12 | 0 | 29 | 185 |
| 2026-09-13 | 0 | 26 | 177 |
| 2026-09-14 | 6 | 28 | 354 |
| 2026-09-15 | 5 | 26 | 196 |
| 2026-09-16 | 3 | 26 | 183 |
| 2026-09-17 | 8 | 26 | 223 |
| 2026-09-18 | 2 | 26 | 208 |
| 2026-09-19 | 0 | 26 | 172 |
| 2026-09-20 | 0 | 26 | 173 |
| 2026-09-21 | 4 | 28 | 231 |
| 2026-09-22 | 3 | 26 | 162 |
| 2026-09-23 | 0 | 2 | 142 |

## Our ingestion assessment

**Model-written ingestion assessment**

The RSS feed was adapted to feed-only mode on 2026-07-28 to respect the publisher's stated crawl-delay limit. The feed's own report summaries (averaging 3,824 characters) carry the digest-relevant substance; full-page extraction was discontinued from that date forward, though 16 bootstrap items ingested earlier include full-text content. Over 14 days, 17 items arrived at 1.21 per day, declining from the previous 2.93 per day. All 342 polling requests succeeded. The most recent item was published on 2026-09-04.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

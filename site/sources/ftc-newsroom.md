<!-- Markdown twin of https://fapd.info/sources/ftc-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ftc-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ftc-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FTC Press Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Independent agency

Official site: https://www.ftc.gov/news-events/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Federal Trade Commission enforces antitrust and consumer-protection law. This RSS feed carries its press releases — complaints, settlements, rule actions, and consumer-refund programs — with paragraph-length descriptions (10 most recent items, ~500 characters each; article pages extract at ~9,000 characters).

**Model-written orientation**

The FTC publishes press releases announcing enforcement actions, settlements, and initiatives related to antitrust law and consumer protection.

The Federal Trade Commission is an independent agency responsible for enforcing federal antitrust statutes and consumer-protection laws. The FTC's authority extends to unfair methods of competition affecting commerce and unfair or deceptive acts or practices affecting consumers. The Commission's Bureau of Competition enforces the Sherman Act and the Clayton Act; the Bureau of Consumer Protection enforces statutes governing consumer transactions, privacy, data security, and unfair business practices.

The FTC's press-release channel announces enforcement actions and policy initiatives: civil complaints and settlements against firms accused of antitrust violations or unfair competition, consumer-protection enforcement against deceptive or unfair business practices, negotiated consent orders establishing remedies and behavioral requirements, civil penalties and monetary awards, and consumer redress or refund programs established through settlements.

Pressure releases summarize allegations against defendants, factual bases for enforcement actions, agreed remedies and behavioral requirements, monetary penalties imposed, and any consumer compensation programs or data-security enhancements mandated. Readers will encounter a range of enforcement matters including merger investigations and challenges, monopoly and exclusive-dealing enforcement, price-fixing and bid-rigging cases, privacy violations and data-security breaches, identity theft and fraud schemes, and violations of specific consumer-protection statutes. Each release provides an accessible overview of an enforcement action, with references to detailed complaint documents, consent orders, and factual records filed with the Commission and available through its website.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ftc-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.ftc.gov/feeds/press-release.xml |
| URL (home) | https://www.ftc.gov/news-events/news/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 10 items, avg description 520 chars, sample article extracted (9347 chars text). |

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

**delivering** — 8 item(s) in the last 14 days; most recent 2026-10-06; 0 of 345 request(s) to www.ftc.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 8 in 14 days (0.57 per day) · most recent 2026-10-06 |
| Content length | 12,368 characters average, 12,920 median (shortest 9,193, longest 13,797) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.ftc.gov | 345 request(s) · 345 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-07T04:00:54.626+00:00 UTC.

8 item(s) in the last 14 days; most recent 2026-10-06; 0 of 345 request(s) to www.ftc.gov returned no content.

### All time

- **Our requests to www.ftc.gov, all time (since 2026-07-30):** 1,910 request(s) · 1,905 answered · 5 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.ftc.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-08 | 1 | 25 | 264 |
| 2026-09-09 | 1 | 27 | 254 |
| 2026-09-10 | 1 | 25 | 249 |
| 2026-09-11 | 0 | 25 | 230 |
| 2026-09-12 | 0 | 29 | 297 |
| 2026-09-13 | 0 | 25 | 290 |
| 2026-09-14 | 0 | 27 | 425 |
| 2026-09-15 | 1 | 26 | 304 |
| 2026-09-16 | 1 | 27 | 234 |
| 2026-09-17 | 3 | 28 | 265 |
| 2026-09-18 | 0 | 25 | 279 |
| 2026-09-19 | 0 | 25 | 232 |
| 2026-09-20 | 0 | 24 | 216 |
| 2026-09-21 | 0 | 27 | 281 |
| 2026-09-22 | 1 | 26 | 240 |
| 2026-09-23 | 0 | 24 | 252 |
| 2026-09-24 | 2 | 27 | 315 |
| 2026-09-25 | 0 | 25 | 264 |
| 2026-09-26 | 0 | 28 | 299 |
| 2026-09-27 | 0 | 26 | 269 |
| 2026-09-28 | 1 | 27 | 274 |
| 2026-09-29 | 0 | 27 | 291 |
| 2026-09-30 | 0 | 25 | 253 |
| 2026-10-01 | 0 | 27 | 232 |
| 2026-10-02 | 2 | 27 | 256 |
| 2026-10-03 | 0 | 26 | 255 |
| 2026-10-04 | 0 | 24 | 245 |
| 2026-10-05 | 2 | 28 | 295 |
| 2026-10-06 | 1 | 27 | 238 |
| 2026-10-07 | 0 | 1 | 269 |

## Our ingestion assessment

**Model-written ingestion assessment**

The FTC press-release RSS feed provides teaser descriptions with full article text extracted from linked pages. Over 14 days, 7 items arrived at 0.5 per day, a slight decline from the previous 0.57 per day. Extracted text averaged 12,598 characters per release. Publication remains sparse; individual items carry substantial scope covering complaints, settlements, and enforcement actions. All 342 requests to www.ftc.gov succeeded without error or no-content responses, compared to the prior 1.4% error rate with 5 no-content responses. Most recent item published 2026-10-05.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

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

**delivering** — 7 item(s) in the last 14 days; most recent 2026-11-12; 0 of 342 request(s) to www.ftc.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-13T04:50:48Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 31 request(s) (31 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 7 in 14 days (0.5 per day) · most recent 2026-11-12 |
| Content length | 12,811 characters average, 12,313 median (shortest 10,753, longest 15,392) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.ftc.gov | 342 request(s) · 342 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-11-13T05:00:13.385+00:00 UTC.

7 item(s) in the last 14 days; most recent 2026-11-12; 0 of 342 request(s) to www.ftc.gov returned no content.

### All time

- **Our requests to www.ftc.gov, all time (since 2026-07-30):** 2,885 request(s) · 2,870 answered · 15 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.ftc.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-15 | 2 | 27 | 268 |
| 2026-10-16 | 0 | 26 | 212 |
| 2026-10-17 | 0 | 25 | 224 |
| 2026-10-18 | 0 | 26 | 241 |
| 2026-10-19 | 3 | 28 | 240 |
| 2026-10-20 | 0 | 24 | 191 |
| 2026-10-21 | 0 | 34 | 367 |
| 2026-10-22 | 2 | 26 | 236 |
| 2026-10-23 | 0 | 25 | 229 |
| 2026-10-24 | 0 | 25 | 244 |
| 2026-10-25 | 0 | 26 | 195 |
| 2026-10-26 | 1 | 26 | 226 |
| 2026-10-27 | 1 | 26 | 215 |
| 2026-10-28 | 1 | 26 | 396 |
| 2026-10-29 | 3 | 28 | 252 |
| 2026-10-30 | 0 | 26 | 222 |
| 2026-10-31 | 0 | 25 | 228 |
| 2026-11-01 | 0 | 26 | 240 |
| 2026-11-02 | 1 | 25 | 226 |
| 2026-11-03 | 0 | 26 | 194 |
| 2026-11-04 | 0 | 24 | 206 |
| 2026-11-05 | 1 | 28 | 254 |
| 2026-11-06 | 1 | 26 | 301 |
| 2026-11-07 | 0 | 25 | 214 |
| 2026-11-08 | 0 | 26 | 228 |
| 2026-11-09 | 2 | 28 | 267 |
| 2026-11-10 | 1 | 26 | 210 |
| 2026-11-11 | 0 | 25 | 186 |
| 2026-11-12 | 1 | 31 | 269 |
| 2026-11-13 | 0 | 1 | 556 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest the FTC Press Releases RSS feed in full mode, fetching each new item's page for article text. Over the 14-day window we recorded 7 items at 0.5 per day, the same count and daily rate as the prior assessment. Extracted article text averaged 12,896 characters (median 11,648, range 10,585 to 16,730), up from the 12,598 characters in the prior assessment. The most recent item moved from 2026-10-05 in the prior assessment to 2026-11-02. Of 335 requests to www.ftc.gov, all returned content, an error rate of 0 percent. The prior assessment recorded 342 requests with no errors. The feed's descriptions averaged about 520 characters at the 2026-07-26 probe, and the full text comes from the article pages.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

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

**delivering** — 6 item(s) in the last 14 days; most recent 2026-10-30; 0 of 333 request(s) to www.sec.gov returned no content.

This label has held since 2026-08-27T22:46:31Z (UTC) and was last re-checked 2026-10-31T03:45:15Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 6 in 14 days (0.43 per day) · most recent 2026-10-30 |
| Content length | 5,710 characters average, 5,495 median (shortest 4,443, longest 7,375) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.sec.gov | 333 request(s) · 333 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-31T04:00:12.792+00:00 UTC.

6 item(s) in the last 14 days; most recent 2026-10-30; 0 of 333 request(s) to www.sec.gov returned no content.

### All time

- **Our requests to www.sec.gov, all time (since 2026-07-30):** 2,524 request(s) · 2,521 answered · 3 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.sec.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-02 | 0 | 26 | 129 |
| 2026-10-03 | 0 | 26 | 126 |
| 2026-10-04 | 0 | 24 | 128 |
| 2026-10-05 | 1 | 27 | 147 |
| 2026-10-06 | 2 | 28 | 148 |
| 2026-10-07 | 0 | 27 | 130 |
| 2026-10-08 | 0 | 26 | 148 |
| 2026-10-09 | 1 | 26 | 138 |
| 2026-10-10 | 0 | 26 | 128 |
| 2026-10-11 | 0 | 25 | 143 |
| 2026-10-12 | 0 | 25 | 140 |
| 2026-10-13 | 0 | 24 | 166 |
| 2026-10-14 | 1 | 26 | 125 |
| 2026-10-15 | 0 | 26 | 129 |
| 2026-10-16 | 0 | 25 | 112 |
| 2026-10-17 | 0 | 24 | 138 |
| 2026-10-18 | 0 | 25 | 121 |
| 2026-10-19 | 1 | 26 | 138 |
| 2026-10-20 | 2 | 26 | 111 |
| 2026-10-21 | 0 | 25 | 129 |
| 2026-10-22 | 0 | 25 | 111 |
| 2026-10-23 | 1 | 27 | 106 |
| 2026-10-24 | 0 | 25 | 105 |
| 2026-10-25 | 0 | 25 | 121 |
| 2026-10-26 | 0 | 24 | 120 |
| 2026-10-27 | 0 | 25 | 132 |
| 2026-10-28 | 0 | 26 | 148 |
| 2026-10-29 | 1 | 26 | 135 |
| 2026-10-30 | 1 | 27 | 142 |
| 2026-10-31 | 0 | 1 | 249 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest the SEC Press Releases RSS feed (registered 2026-07-26, status active). The feed carries teaser descriptions averaging about 251 characters, and we fetch full article text from each item's own page. In the 14-day window we recorded 4 items, a rate of 0.29 per day, with the most recent dated 2026-10-23, six days before this assessment. Extracted article text averaged 5,441 characters (median 4,974; range 4,443 to 7,375). All 329 requests to www.sec.gov returned content, an error rate of 0.0%, and the collector shows no consecutive errors. The registry notes record only the 2026-07-26 probe, which verified the feed end to end, and no incidents are recorded. Compared with the previous assessment dated 2026-09-28, the 14-day item count fell from 5 to 4, average extracted length fell from about 6,038 to 5,441 characters, and the error rate remained at zero. Health is recorded as delivering.

_Model-written assessment of our own ingestion, generated 2026-10-29 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

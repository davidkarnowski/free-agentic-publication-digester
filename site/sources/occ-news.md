<!-- Markdown twin of https://fapd.info/sources/occ-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/occ-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: occ-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# OCC News Releases

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Department of the Treasury

Official site: https://www.occ.gov/news-issuances/news-releases/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of the Comptroller of the Currency, a Treasury bureau, charters and supervises national banks and federal savings associations. Its news-release index carries supervision and enforcement announcements, including monthly enforcement-action lists, typically a few items per week.

**Model-written orientation**

The Office of the Comptroller of the Currency, a Treasury bureau, charters and supervises national banks and federal savings associations, publishing news releases on supervision and enforcement.

The Office of the Comptroller of the Currency (OCC) is a bureau of the Department of the Treasury that charters, regulates, and supervises national banks and federal savings associations. The OCC operates the federal banking system's chartering authority and sets supervisory standards for the approximately 1,000 national banks and federal savings associations under its jurisdiction. These institutions provide banking services to millions of Americans and businesses. The OCC addresses a wide range of supervisory matters including capital and liquidity requirements, consumer protection, anti-money-laundering compliance, and community reinvestment. The agency's news releases announce significant enforcement actions against banks for violations of law or regulation, monthly lists of enforcement actions taken, policy guidance, and other supervisory developments, typically publishing a few items per week. Enforcement actions may include civil money penalties, consent orders requiring specific remedial actions, or other formal enforcement measures. Policy guidance covers topics such as capital planning, cybersecurity, third-party risk management, and new regulatory requirements. In this digest you will see OCC press releases describing recently completed enforcement actions, policy announcements, and supervisory initiatives. Each release provides context for the action or policy, the specific regulatory concerns involved, and the bank or banks affected. Readers interested in banking regulation, bank supervision, or financial regulatory enforcement will find the OCC's releases a direct source for its actions and policy positions.

_Model-written orientation, generated 2026-10-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `occ-news` |
| Agency / parent organization | Department of the Treasury |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.occ.gov/rss/occ_news.xml |
| URL (home) | https://www.occ.gov/news-issuances/news-releases/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — but research 2026-07-28 found OCC documents an RSS index at occ.gov/rss/index-rss.html with separate feeds for News Releases, Bulletins, Alerts, and Public Service Announcements (Bulletins/Alerts add supervisory-guidance coverage beyond press). Capture exact feed URLs from that page at probe; upgrade type to rss on confirmation. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 77 article link(s); 0 dated inside the 7-day lookback, 0 dated outside it, 77 skipped for no readable date — the served HTML states no per-entry publication date, so every entry is skipped rather than dated by observation. This is a script-rendered listing; opening it needs evidence of a dated channel, not a cadence decision. Probed 2026-08-06: https://www.occ.gov/rss/index-rss.html is an HTML index of RSS offerings, not a feed (verdict html-only). ACTIVATED 2026-10-05 (operator) on the feed OCC documents on its RSS index page, https://www.occ.gov/rss/occ_news.xml. Probed 2026-10-04 through FAPD's identified probe client. Re-verified 2026-10-05 from the operator machine as a brief test, outside the server's budget, through FAPD's identified probe client (robots allows, no crawl-delay, no Retry-After, HTTP 200): 10 items, 10/10 dated in RFC 822 form without a weekday ('5 Oct 2026 16:30:00 -0400'), which report._claimed_day reads; no GUIDs, so identity is the release link, which carries the year and release number. The newest item was dated the day of the check and its own page states the same date; the sample release extracted at 6,503 characters. Coverage (gate 3): 10 items spanned 2026-09-10 to 10-05, so the feed's depth comfortably exceeds what an hourly poll can miss; descriptions are ~250-character teasers, so full mode. The listing page still states no per-entry date (0 entries read 2026-10-05), which is why the feed and not the listing is the channel. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls OCC's News Releases RSS feed via AgencyClient, then fetches each new release for full text (mode full). The feed carries no GUIDs, so identity is the release link. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 13 item(s) in the last 14 days; most recent 2026-10-08; 0 of 193 request(s) to www.occ.gov returned no content.

This label has held since 2026-10-05T23:57:58Z (UTC) and was last re-checked 2026-10-09T03:52:22Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 54 request(s) (54 answered, 0 returned no content) · 2 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 13 in 14 days (0.93 per day) · most recent 2026-10-08 |
| Content length | 5,829 characters average, 5,733 median (shortest 4,514, longest 8,360) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.occ.gov | 193 request(s) · 193 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-09T04:00:11.573+00:00 UTC; this host serves 2 registered sources, so these figures are host-wide.

13 item(s) in the last 14 days; most recent 2026-10-08; 0 of 193 request(s) to www.occ.gov returned no content.

### All time

- **Our requests to www.occ.gov, all time (since 2026-10-05):** 193 request(s) · 193 answered · 0 returned no content

This host serves 2 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.occ.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-09-10 | 0 | 0 | — |
| 2026-09-11 | 0 | 0 | — |
| 2026-09-12 | 0 | 0 | — |
| 2026-09-13 | 0 | 0 | — |
| 2026-09-14 | 0 | 0 | — |
| 2026-09-15 | 0 | 0 | — |
| 2026-09-16 | 0 | 0 | — |
| 2026-09-17 | 0 | 0 | — |
| 2026-09-18 | 0 | 0 | — |
| 2026-09-19 | 0 | 0 | — |
| 2026-09-20 | 0 | 0 | — |
| 2026-09-21 | 0 | 0 | — |
| 2026-09-22 | 0 | 0 | — |
| 2026-09-23 | 0 | 0 | — |
| 2026-09-24 | 0 | 0 | — |
| 2026-09-25 | 0 | 0 | — |
| 2026-09-26 | 0 | 0 | — |
| 2026-09-27 | 0 | 0 | — |
| 2026-09-28 | 0 | 0 | — |
| 2026-09-29 | 0 | 0 | — |
| 2026-09-30 | 0 | 0 | — |
| 2026-10-01 | 0 | 0 | — |
| 2026-10-02 | 0 | 0 | — |
| 2026-10-03 | 0 | 0 | — |
| 2026-10-04 | 0 | 0 | — |
| 2026-10-05 | 10 | 32 | 121 |
| 2026-10-06 | 0 | 52 | 215 |
| 2026-10-07 | 1 | 53 | 203 |
| 2026-10-08 | 2 | 54 | 202 |
| 2026-10-09 | 0 | 2 | 208 |

## Our ingestion assessment

**Model-written ingestion assessment**

OCC news releases arrive through an RSS feed with full article text extracted from linked pages. The source was activated on 2026-10-05. In the single day of collection measured, 10 items were ingested spanning September and early October publication dates. Extracted text averaged 5,868 characters; feed descriptions provide approximately 250-character teasers. The feed carries no GUIDs; item identity depends on the release link. All 34 requests to www.occ.gov succeeded without error or no-content responses. Items arrived in a concentrated poll window on 2026-10-05 evening.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

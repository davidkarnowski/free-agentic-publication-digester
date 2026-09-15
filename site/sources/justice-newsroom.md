<!-- Markdown twin of https://fapd.info/sources/justice-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/justice-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: justice-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Justice Press Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Department of Justice

Official site: https://www.justice.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Department of Justice enforces federal law and represents the United States in court. Its Office of Public Affairs channel carries national press releases — indictments, plea agreements, settlements, and policy announcements — typically many items per business day across litigating divisions.

**Model-written orientation**

The Department of Justice publishes press releases on federal law enforcement, litigation outcomes, and legal policy through its Office of Public Affairs, covering criminal prosecutions, civil litigation, and policy announcements.

The Department of Justice enforces federal law and represents the United States in litigation. Its Office of Public Affairs channel serves as the official press release mechanism for departmental announcements to the press and public. The Justice Department publishes many releases per business day during typical operational periods, reflecting the scope and complexity of federal law enforcement.

The department's litigating divisions and components conduct distinct enforcement activities: the Criminal Division handles federal crimes; the Civil Division represents the United States in civil litigation; the Antitrust Division addresses anticompetitive business conduct; the Tax Division pursues federal tax enforcement and litigation; the Civil Rights Division enforces federal civil rights laws; and U.S. Attorneys' Offices, located in judicial districts across the country, prosecute federal crimes in their districts. The news channel carries announcements from all these components.

Readers will encounter releases on federal criminal prosecutions (indictments, plea agreements, convictions, sentencing), civil litigation outcomes, antitrust investigations or enforcement actions, tax prosecutions, civil rights enforcement, and policy statements on legal matters within the department's authority. Each release is attributed to the specific division or U.S. Attorney's Office that handled the matter, providing readers information about which part of the federal government took action.

The news feed carries the most recent releases with full descriptions and links to department pages with additional detail. Volume of releases varies based on enforcement activity; heavy prosecution periods or major legal actions may generate many releases per day, while quieter periods may have fewer. The Justice Department also publishes separate channels for specific divisions and regional U.S. Attorneys' Offices.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `justice-newsroom` |
| Agency / parent organization | Department of Justice |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.justice.gov/feeds/justice-news.xml?type=All&component%5B436%5D=436&organization=All |
| URL (home) | https://www.justice.gov/news |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 404 at the old /feeds/opa/justice-news.xml path — a stale path, not a block. Re-probed 2026-07-28 at the corrected URL: feed verified — 25 items, ~250-char descriptions; the probe's single sample article extracted (3,117 chars). First full ingest 2026-07-28 revealed the catch: sustained article fetching (25 pages at the host's own 10s crawl-delay) is answered with Akamai bm-verify challenge interstitials (~2.5 KB, no content) — captured as evidence. Following the challenge URL would be bot-check circumvention, which we never do, so the posture is feed-only (adapter rss-feed-only): titles + descriptions, honestly disclosed per item. Content evaluation: DOJ publishes many items per business day; 25-item feed depth can under-cover heavy days — disclosed; division/USAO sibling feeds are the expansion path. A working DOJ feed also partially covers DEA and ATF (their enforcement news is republished here, DOJ-attributed). Activated 2026-07-28 (feed-only). Email sibling registered 2026-07-29: justice-email and usattorneys-email (GUIDE §3 email class; the web status here is unchanged). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the Drupal views news feed (component parameter filters to Office of Public Affairs) via AgencyClient, feed metadata only. |
| Adapter | rss-feed-only |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 590 item(s) in the last 14 days; most recent 2026-09-14; 6 of 356 request(s) to www.justice.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-15T03:50:21Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 30 request(s) (30 answered, 0 returned no content) · 64 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 590 in 14 days (42.14 per day) · most recent 2026-09-14 |
| Content length | 315 characters average, 288 median (shortest 42, longest 1,126) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.justice.gov | 356 request(s) · 350 answered · 1 declined (4xx) · 0 server declined (5xx) · 5 no response — 1.7% returned no content |

last answered request 2026-09-15T04:00:52.187+00:00 UTC.

590 item(s) in the last 14 days; most recent 2026-09-14; 6 of 356 request(s) to www.justice.gov returned no content.

### All time

- **Our requests to www.justice.gov, all time (since 2026-07-30):** 1,394 request(s) · 1,378 answered · 16 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.justice.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-17 | 41 | 27 | 281 |
| 2026-08-18 | 84 | 27 | 242 |
| 2026-08-19 | 65 | 24 | 328 |
| 2026-08-20 | 83 | 34 | 400 |
| 2026-08-21 | 48 | 29 | 275 |
| 2026-08-22 | 0 | 30 | 219 |
| 2026-08-23 | 0 | 29 | 217 |
| 2026-08-24 | 66 | 28 | 389 |
| 2026-08-25 | 90 | 26 | 455 |
| 2026-08-26 | 88 | 25 | 511 |
| 2026-08-27 | 87 | 27 | 368 |
| 2026-08-28 | 80 | 25 | 359 |
| 2026-08-29 | 0 | 27 | 216 |
| 2026-08-30 | 0 | 26 | 284 |
| 2026-08-31 | 60 | 26 | 295 |
| 2026-09-01 | 87 | 26 | 335 |
| 2026-09-02 | 65 | 26 | 379 |
| 2026-09-03 | 80 | 31 | 487 |
| 2026-09-04 | 74 | 26 | 336 |
| 2026-09-05 | 0 | 33 | 304 |
| 2026-09-06 | 0 | 26 | 184 |
| 2026-09-07 | 8 | 26 | 177 |
| 2026-09-08 | 66 | 26 | 255 |
| 2026-09-09 | 91 | 26 | 253 |
| 2026-09-10 | 81 | 26 | 400 |
| 2026-09-11 | 61 | 26 | 395 |
| 2026-09-12 | 0 | 28 | 214 |
| 2026-09-13 | 0 | 26 | 204 |
| 2026-09-14 | 64 | 29 | 406 |
| 2026-09-15 | 0 | 1 | 219 |

## Our ingestion assessment

**Model-written ingestion assessment**

Justice press releases arrive through RSS feed (Office of Public Affairs channel, approximately 25-item feed depth). Over 14 days we collected 777 items averaging 297 characters at roughly 56 per day, most recent on September 4. Delivery is feed-only (titles and descriptions) because sustained article page fetches trigger Akamai bot-check interstitials, documented as evidence. The www.justice.gov host shows 1.7% request failure. Compared to the prior 14-day window (230 items at ~16/day, 1.2% failure), collection volume has increased more than threefold while host stability and article fetch limitations remain unchanged.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

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

**delivering** — 579 item(s) in the last 14 days; most recent 2026-11-12; 14 of 352 request(s) to www.justice.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-12T19:56:10Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 30 request(s) (30 answered, 0 returned no content) · 33 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 579 in 14 days (41.36 per day) · most recent 2026-11-12 |
| Content length | 317 characters average, 303 median (shortest 38, longest 2,374) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.justice.gov | 352 request(s) · 338 answered · 14 declined (4xx) · 0 server declined (5xx) · 0 no response — 4.0% returned no content |

last answered request 2026-11-12T20:01:16.734+00:00 UTC.

579 item(s) in the last 14 days; most recent 2026-11-12; 14 of 352 request(s) to www.justice.gov returned no content.

### All time

- **Our requests to www.justice.gov, all time (since 2026-07-30):** 2,818 request(s) · 2,776 answered · 42 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.justice.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-14 | 67 | 25 | 357 |
| 2026-10-15 | 69 | 26 | 328 |
| 2026-10-16 | 36 | 25 | 215 |
| 2026-10-17 | 0 | 25 | 246 |
| 2026-10-18 | 11 | 25 | 323 |
| 2026-10-19 | 53 | 25 | 351 |
| 2026-10-20 | 67 | 25 | 538 |
| 2026-10-21 | 67 | 25 | 544 |
| 2026-10-22 | 85 | 25 | 519 |
| 2026-10-23 | 69 | 25 | 265 |
| 2026-10-24 | 10 | 25 | 186 |
| 2026-10-25 | 0 | 26 | 183 |
| 2026-10-26 | 51 | 25 | 296 |
| 2026-10-27 | 61 | 24 | 504 |
| 2026-10-28 | 69 | 25 | 382 |
| 2026-10-29 | 82 | 29 | 221 |
| 2026-10-30 | 95 | 25 | 515 |
| 2026-10-31 | 0 | 25 | 219 |
| 2026-11-01 | 0 | 26 | 234 |
| 2026-11-02 | 47 | 25 | 245 |
| 2026-11-03 | 59 | 27 | 282 |
| 2026-11-04 | 44 | 24 | 194 |
| 2026-11-05 | 64 | 27 | 441 |
| 2026-11-06 | 80 | 25 | 328 |
| 2026-11-07 | 0 | 25 | 177 |
| 2026-11-08 | 0 | 25 | 214 |
| 2026-11-09 | 71 | 27 | 300 |
| 2026-11-10 | 74 | 25 | 379 |
| 2026-11-11 | 12 | 25 | 233 |
| 2026-11-12 | 33 | 21 | 293 |

## Our ingestion assessment

**Model-written ingestion assessment**

This source is measured in feed-only delivery mode, which the registry describes as the feed summary, since the source publishes no more than that through this channel. Over the 14-day window we recorded 587 items, about 42 per day, with a mean of 323 characters (median 306, range 38 to 2,374). Daily activity shows items on 2026-10-30 (95), 2026-11-02 (47), 2026-11-03 (59), and 2026-11-04 (44), with none on the other measured days. The most recent item is dated 2026-11-04. The www.justice.gov host returned no content for 6.0 percent of attempts (20 of 332). Registry notes record a 404 on a stale feed path on 2026-07-26, and challenge interstitials returned in place of article content during sustained article fetching on 2026-07-28; article fetching was not continued after that. The 25-item feed depth is recorded as a limit on heavy publication days. Compared with the 2026-10-06 assessment, which recorded 635 items at about 45 per day with a 0 percent host failure rate and a last item of 2026-10-05, the item count and daily rate are lower, the mean size is similar, and the host failure rate is higher.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

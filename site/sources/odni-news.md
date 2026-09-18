<!-- Markdown twin of https://fapd.info/sources/odni-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/odni-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: odni-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# ODNI Newsroom

active · ingestion health: quiet · Executive · Tier 2 · RSS feed · Office of the Director of National Intelligence

Official site: https://www.odni.gov/newsroom/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of the Director of National Intelligence coordinates the intelligence community. Its newsroom carries press releases, statements, and declassification announcements at a low but steady rate — roughly two to four a month — and is the pipeline's only intelligence-community coverage.

**Model-written orientation**

The Office of the Director of National Intelligence publishes press releases and statements on intelligence policy and declassification matters.

The Office of the Director of National Intelligence (ODNI) serves as the coordinator of the U.S. intelligence community, working across the Central Intelligence Agency, Defense Intelligence Agency, National Security Agency, and dozens of other intelligence and security organizations. ODNI's newsroom publishes official communications about intelligence policy, organizational governance, and declassification decisions.

Press releases from ODNI address matters of intelligence policy and governance: organizational announcements, policy statements on intelligence-related issues, and formal positions on matters affecting intelligence community operations. The agency also publishes declassification announcements as classified documents are released to the public following established legal timelines. These declassification actions become part of the permanent historical record, making previously restricted information available for research and public understanding.

Intelligence policy announcements represent decisions on how intelligence authorities are exercised, how agencies coordinate, and how intelligence activities interface with other federal functions. These are distinct from the operational or tactical announcements individual intelligence agencies might make.

ODNI's publications are infrequent compared to other federal agencies—typically two to four releases per month—reflecting the confidential nature of much intelligence community work. The announcements come at irregular intervals rather than on a fixed schedule, appearing in response to policy decisions and declassification milestones rather than routine operational cycles.

For readers tracking federal government activity, ODNI represents the intelligence community's official public voice on matters of organizational policy, intelligence governance, and historical declassification.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `odni-news` |
| Agency / parent organization | Office of the Director of National Intelligence |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.odni.gov/newsroom/press-releases/feed/ |
| URL (home) | https://www.odni.gov/newsroom/ |
| Registered | 2026-07-28 |
| Registry notes | RSS section documented at dni.gov/index.php/rss (2026-07-28, surfaced in search results). Probe 2026-07-28: the candidate feed path /index.php/rss/311-odni-news-feed returned 404 (10-byte response); host is open and its robots.txt sets a 10s crawl-delay (honored). Next step: fetch the /index.php/rss section page through AgencyClient to read the real feed URL, then re-probe. Resolved 2026-07-31 (operator machine, off the server budget), and the answer was bigger than a bad path: ODNI has left Joomla AND left the domain. Every /index.php/* address now 301s to archive.dni.gov, where it 404s, and www.dni.gov/newsroom/ redirects to www.odni.gov/newsroom/ — a WordPress site. The 404 was a whole-publisher migration our registry read as a broken link. Do not use the site-wide WordPress feed (odni.gov/feed/): it carries 532 items of which 371 are media-library /download/ attachments and several are bare offsite links to YouTube with empty descriptions. The category feed is the right door. Gate-3 coverage evaluation (2026-07-31, from the probe): https://www.odni.gov/newsroom/press-releases/feed/ answers HTTP 200 with well-formed RSS carrying 54 items — the entire press-release category since the site migration, 2025-02-12 through 2026-06-19 (43 in 2025, 11 in 2026), every one with a guid (the WordPress post id, /?p=NNNNN, so identity does not depend on URL shape) and an RFC 822 date, every link on odni.gov, none with an empty description. Descriptions average 344 characters — teaser length — but the sample article page extracted 8,082 characters, so this ingests at mode full rather than feed-only. What we will NOT see: the newsroom's sibling categories /newsroom/remarks/ and /newsroom/reports/, each presumably its own WordPress feed; those are separate registry entries if wanted, and their absence is the disclosed under-coverage here. Publication is sparse — the newest item at activation was six weeks old — so empty days are the source's normal state, not a fault. One-time activation cost to budget: the feed hands us all 54 items at once and the default adapter fetches each article page, so first ingest spends about 54 requests at this host's 10-second crawl-delay (~9 minutes of wall clock); the dating rule then excludes almost all of them as backfill under AGENCYPR-EX-01. Steady state is one conditional request a day. If the agency class is near its daily ceiling the budget will simply cut the backfill short and the next run resumes it — but prefer to activate on a day with headroom. Probed 2026-07-31: registered URL returned 404 (https://www.dni.gov/index.php/rss/311-odni-news-feed) — the publisher moved or retired it; not a refusal. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the ODNI press-release RSS feed daily; article pages are fetched and extracted, honoring the host's 10-second crawl-delay. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**quiet** — Most recent item 2026-08-03, 46 days ago (quiet past 7 days).

This label has held since 2026-08-11T04:22:38Z (UTC) and was last re-checked 2026-09-18T03:55:01Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — most recent 2026-08-03 |
| Our requests to www.odni.gov | 354 request(s) · 354 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-18T04:20:15.746+00:00 UTC.

Most recent item 2026-08-03, 46 days ago (quiet past 7 days).

### All time

- **Our requests to www.odni.gov, all time (since 2026-08-01):** 1,462 request(s) · 1,462 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.odni.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-20 | 0 | 34 | 271 |
| 2026-08-21 | 0 | 30 | 179 |
| 2026-08-22 | 0 | 30 | 199 |
| 2026-08-23 | 0 | 29 | 165 |
| 2026-08-24 | 0 | 27 | 210 |
| 2026-08-25 | 0 | 26 | 230 |
| 2026-08-26 | 0 | 26 | 184 |
| 2026-08-27 | 0 | 26 | 157 |
| 2026-08-28 | 0 | 25 | 223 |
| 2026-08-29 | 0 | 27 | 154 |
| 2026-08-30 | 0 | 27 | 177 |
| 2026-08-31 | 0 | 26 | 176 |
| 2026-09-01 | 0 | 26 | 177 |
| 2026-09-02 | 0 | 26 | 476 |
| 2026-09-03 | 0 | 25 | 370 |
| 2026-09-04 | 0 | 26 | 197 |
| 2026-09-05 | 0 | 33 | 236 |
| 2026-09-06 | 0 | 27 | 164 |
| 2026-09-07 | 0 | 26 | 207 |
| 2026-09-08 | 0 | 26 | 169 |
| 2026-09-09 | 0 | 26 | 231 |
| 2026-09-10 | 0 | 25 | 204 |
| 2026-09-11 | 0 | 27 | 135 |
| 2026-09-12 | 0 | 29 | 259 |
| 2026-09-13 | 0 | 26 | 254 |
| 2026-09-14 | 0 | 29 | 449 |
| 2026-09-15 | 0 | 26 | 133 |
| 2026-09-16 | 0 | 27 | 177 |
| 2026-09-17 | 0 | 26 | 293 |
| 2026-09-18 | 0 | 1 | 110 |

## Our ingestion assessment

**Model-written ingestion assessment**

The ODNI Newsroom RSS feed has entered a prolonged quiet period. No items have been ingested over the past 14 days; the most recent item was published on 2026-08-03, 39 days ago. Our polling requests to www.odni.gov continue to succeed at 100%—all 348 attempts answered with no content failures—but the feed itself is returning no new items. In the previous 14-day window (ending 2026-08-12), the source delivered 55 items at an average rate of 3.93 per day. The shift from regular publication to silence marks a significant change in delivery pattern. The registry notes that article extraction was working when the source last published, and that the feed respects a 10-second crawl-delay.

_Model-written assessment of our own ingestion, generated 2026-09-11 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

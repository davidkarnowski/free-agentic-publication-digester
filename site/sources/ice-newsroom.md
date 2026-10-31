<!-- Markdown twin of https://fapd.info/sources/ice-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ice-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ice-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# ICE Newsroom

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.ice.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

U.S. Immigration and Customs Enforcement, within DHS, enforces immigration and customs law in the interior. Its newsroom index carries news releases on enforcement and removal operations and Homeland Security Investigations cases, typically several items per week.

**Model-written orientation**

The ICE Newsroom publishes news releases on immigration enforcement operations, removals, and criminal investigations conducted within the United States.

U.S. Immigration and Customs Enforcement is a law enforcement bureau within the Department of Homeland Security. ICE's responsibilities include enforcing immigration law in the interior of the United States, managing detention facilities, and investigating immigration crimes. The agency also operates Homeland Security Investigations, a criminal investigative arm that handles international and domestic cases involving customs and immigration violations.

The ICE Newsroom serves as the agency's official channel for communicating with the news media, law enforcement, and the public about enforcement operations and investigations. The newsroom publishes news releases describing enforcement operations, removals, criminal investigations outcomes, and officer actions.

Readers will see from this source news releases describing immigration enforcement actions carried out by ICE and its investigative units. These may include announcements of significant enforcement operations, results of criminal investigations, removals of individuals, and statements on enforcement priorities. Some releases may highlight transnational criminal organizations or customs violations. Others may address operational statistics or agency initiatives.

ICE news releases are written primarily for law enforcement officials, the media, and the general public. The agency publishes several releases per week, though volume varies depending on operational activity. The dates on releases represent ICE's own publication dates.

The Newsroom operates as an HTML index on the ICE website. The digest polls this index regularly, without fetching full articles, to identify new releases. Articles listed without a readable date are not included. The digest's coverage is limited to items appearing on the first page of the index at the time of polling; items published between polls that exceed one page of listings may not be captured.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ice-newsroom` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.ice.gov/newsroom |
| URL (index) | https://www.ice.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 95 article link(s); 6 dated inside the 7-day lookback, 19 dated outside it, 70 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 7 entries dated inside the 7-day lookback (2026-09-21..28), all news releases with ICE's own dates. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only). |
| Adapter | html-index |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 31 item(s) in the last 14 days; most recent 2026-10-30; 0 of 329 request(s) to www.ice.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-31T03:45:15Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · 4 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 31 in 14 days (2.21 per day) · most recent 2026-10-30 |
| Content length | 324 characters average, 312 median (shortest 199, longest 542) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.ice.gov | 329 request(s) · 329 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-31T04:00:14.121+00:00 UTC.

31 item(s) in the last 14 days; most recent 2026-10-30; 0 of 329 request(s) to www.ice.gov returned no content.

### All time

- **Our requests to www.ice.gov, all time (since 2026-09-28):** 827 request(s) · 827 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.ice.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-02 | 0 | 26 | 168 |
| 2026-10-03 | 0 | 25 | 170 |
| 2026-10-04 | 0 | 26 | 159 |
| 2026-10-05 | 2 | 26 | 149 |
| 2026-10-06 | 1 | 26 | 188 |
| 2026-10-07 | 1 | 26 | 213 |
| 2026-10-08 | 0 | 26 | 193 |
| 2026-10-09 | 0 | 25 | 159 |
| 2026-10-10 | 0 | 25 | 175 |
| 2026-10-11 | 0 | 25 | 161 |
| 2026-10-12 | 0 | 26 | 235 |
| 2026-10-13 | 1 | 25 | 188 |
| 2026-10-14 | 1 | 25 | 189 |
| 2026-10-15 | 2 | 26 | 154 |
| 2026-10-16 | 0 | 25 | 173 |
| 2026-10-17 | 0 | 25 | 156 |
| 2026-10-18 | 0 | 25 | 161 |
| 2026-10-19 | 0 | 25 | 161 |
| 2026-10-20 | 6 | 25 | 161 |
| 2026-10-21 | 2 | 25 | 149 |
| 2026-10-22 | 2 | 25 | 144 |
| 2026-10-23 | 0 | 25 | 175 |
| 2026-10-24 | 1 | 25 | 131 |
| 2026-10-25 | 1 | 26 | 140 |
| 2026-10-26 | 6 | 25 | 141 |
| 2026-10-27 | 3 | 25 | 155 |
| 2026-10-28 | 3 | 25 | 180 |
| 2026-10-29 | 3 | 25 | 148 |
| 2026-10-30 | 4 | 27 | 164 |
| 2026-10-31 | 0 | 1 | 114 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest the ICE newsroom through an HTML index, with one listing fetch per poll and no article pages fetched (feed-only mode). The items we recorded are news releases carrying ICE's own dates, covering the enforcement and removal operations and Homeland Security Investigations cases that the registry describes for this source. Over the 14-day window we recorded 27 items, most recently dated 2026-10-29, with a median of 308 characters and an average of 310. Daily item counts in the most recent seven days ranged from zero to six. The listing shows its first page only, and entries we cannot date are dropped rather than dated by observation. All 327 requests to www.ice.gov were answered, with none failing, and the registry notes record no delivery incidents. The previous assessment covered the six days since activation, when we recorded 7 items averaging 360 characters from 13 successful polling requests. Since then the item count has risen to 27 and the average length has moved to 310 characters.

_Model-written assessment of our own ingestion, generated 2026-10-30 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/uscis-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/uscis-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: uscis-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USCIS Newsroom

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.uscis.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

U.S. Citizenship and Immigration Services, within DHS, adjudicates immigration benefits. Its newsroom index carries news releases and alerts on benefits processing, fees, and policy updates, typically a few items per week.

**Model-written orientation**

The USCIS Newsroom publishes news releases and alerts on immigration benefits processing, fees, deadlines, and policy changes.

U.S. Citizenship and Immigration Services is a bureau within the Department of Homeland Security that adjudicates immigration benefits. USCIS processes applications for asylum, permanent residence, citizenship, work permits, travel documents, and other immigration benefits. The agency operates service centers, field offices, and interviews applicants across the United States.

The USCIS Newsroom serves as the agency's official communication channel with applicants, immigration attorneys, employers, and the public regarding immigration benefits processing. The newsroom publishes news releases announcing changes to application procedures, fee schedules, processing times, filing deadlines, and new programs or benefits.

Readers will see from this source news releases on a range of topics: announcements of changes to application procedures or requirements; alerts about processing time estimates; notices of fee increases or new fee schedules; announcements of disaster relief programs or temporary protected status designations; alerts during government closures; and statements on immigration benefits policy. Some releases address specific applicant categories, such as spouses of U.S. citizens or individuals with work authorizations.

USCIS news releases are written primarily for individuals applying for benefits, immigration attorneys and representatives, employers sponsoring workers, and the general public. The agency publishes several releases per week, though volume varies seasonally and by operational activity. The dates on releases represent USCIS's own publication dates.

The Newsroom operates as an HTML index on the USCIS website, with access limited to the news-releases section to exclude sidebar and navigation links. The digest polls this index regularly, without fetching full articles, to identify new releases. Articles listed without a readable date are not included. USCIS's website observes a 10-second crawl-delay policy in its robots.txt file, which the digest respects. The email sibling, uscis-email, carries some of the same releases through a separate GovDelivery channel; a release reaching the digest through both channels is noted as corroborated. The digest's coverage is limited to items appearing on the first page of the index at the time of polling.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `uscis-newsroom` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.uscis.gov/newsroom |
| URL (index) | https://www.uscis.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Email sibling registered 2026-07-29: uscis-email (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 85 article link(s); 2 dated inside the 7-day lookback, 0 dated outside it, 83 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: robots.txt sets a 10-second crawl-delay, honored. Without a hint the listing yields 6 entries dated 2026-09-25, four of them sidebar links (All USCIS News; Data and Statistics; Electronic Reading Room; Upcoming Events). index_item_path /newsroom/news-releases/ keeps the 2 real releases. uscis-email stays active beside it. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

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

**delivering** — 6 item(s) in the last 14 days; most recent 2026-10-02; 0 of 176 request(s) to www.uscis.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-05T03:47:32Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 6 in 14 days (0.43 per day) · most recent 2026-10-02 |
| Content length | 274 characters average, 274 median (shortest 207, longest 368) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.uscis.gov | 176 request(s) · 176 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-05T04:00:11.338+00:00 UTC.

6 item(s) in the last 14 days; most recent 2026-10-02; 0 of 176 request(s) to www.uscis.gov returned no content.

### All time

- **Our requests to www.uscis.gov, all time (since 2026-09-28):** 176 request(s) · 176 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.uscis.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-06 | 0 | 0 | — |
| 2026-09-07 | 0 | 0 | — |
| 2026-09-08 | 0 | 0 | — |
| 2026-09-09 | 0 | 0 | — |
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
| 2026-09-28 | 3 | 12 | 218 |
| 2026-09-29 | 1 | 29 | 156 |
| 2026-09-30 | 0 | 26 | 196 |
| 2026-10-01 | 0 | 28 | 159 |
| 2026-10-02 | 2 | 27 | 155 |
| 2026-10-03 | 0 | 27 | 153 |
| 2026-10-04 | 0 | 26 | 236 |
| 2026-10-05 | 0 | 1 | 213 |

## Our ingestion assessment

**Model-written ingestion assessment**

The USCIS Newsroom is ingested via HTML index diffing with path filtering to /newsroom/news-releases/ and one listing poll per cycle. Activation on 2026-09-28 set the measurement baseline. In the 6 days since activation, three items were ingested with the most recent dated 2026-09-28, averaging 297 characters each. The host publishes a 10-second crawl-delay which is honored. The source operates feed-only with no article fetches; filtered index text serves as the full digest content. All 14 polling requests to www.uscis.gov completed successfully with no errors. A correlated email channel (uscis-email) carries the same releases. Coverage is limited to dateable entries on the filtered page; undatable entries are dropped and never observation-dated.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

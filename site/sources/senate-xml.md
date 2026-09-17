<!-- Markdown twin of https://fapd.info/sources/senate-xml.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/senate-xml.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: senate-xml)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Senate.gov XML services

active · ingestion health: delivering · Legislative · Tier 1 · XML index · Secretary of the Senate (LIS)

Official site: https://www.senate.gov/general/common/generic/XML_Availability.htm · All sources: [sources.md](../sources.md)

## What this source is

The Senate's officially documented directory of XML files: roll-call vote menus and individual votes, the committee hearings/meetings schedule, the floor schedule, and nine nomination-status files (pending, confirmed, withdrawn, failed — civilian and non-civilian). The only machine source for Senate votes.

**Model-written orientation**

The Senate publishes XML files for roll-call votes, committee schedules, floor schedules, and nomination statuses through its official XML services.

The United States Senate maintains an official set of XML data files published through the Senate's LIS (Legislative Information System). These files provide structured access to several key categories of Senate activity.

The roll-call votes files list every roll-call vote taken in the Senate, with each vote's date, subject matter, tally, and member-by-member voting record. These votes are published the same day they are taken. The files include votes spanning prior Congresses, providing a historical record of recorded Senate votes.

The Senate also publishes XML files for other information: committee hearings and meetings schedules, the Senate floor schedule showing upcoming business, and nomination status files tracking nominations awaiting Senate action.

This digest currently ingests Senate roll-call votes through these XML files. Each vote is published as a separate XML file, and the system retrieves votes that fall within the publication lookback window.

The XML files are officially documented and maintained by the Secretary of the Senate. They are offered as a machine-readable alternative to browsing the Senate website and represent the official Senate record of votes and schedule information. One important point about the Senate vote data: the tally is stored in the per-vote XML file, not in the vote menu.

The Senate XML files complement other sources in the federal record. The Congress.gov API provides House votes, while these XML services provide the authoritative Senate vote record. Together with other legislative sources, they provide comprehensive access to recorded votes in both chambers of Congress. This source is valuable for readers interested in tracking Senate votes, monitoring how Senators vote on specific issues, or analyzing voting patterns in the Senate.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `senate-xml` |
| Agency / parent organization | Secretary of the Senate (LIS) |
| Branch | legislative |
| Type | XML index |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.senate.gov/general/common/generic/XML_Availability.htm |
| URL (index) | https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_119_2.xml |
| Registered | 2026-07-28 |
| Registry notes | Gate 3 (2026-07-31, live through the identified client): the menu answers 200 text/xml, 123,670 bytes, and lists the WHOLE session — 217 <vote> elements from 05-Jan to 30-Jul, so ingestion sees 100% of the Senate's recorded votes but must bound itself (8 fell inside the 7-day lookback that day: 1 index fetch + 8 records = 9 requests). Two coverage limits, both disclosed rather than papered over: (a) vote_date carries NO YEAR ('30-Jul') and vote_tally is present but EMPTY on all 217, so the tally exists only in the per-vote record, which is why wants_article() is True; (b) 2 of 217 rows are en-bloc confirmations carrying no issue/question/result — their title alone identifies them. Per-vote URL pattern vote{congress}{session}/vote_{c}_{s}_{NNNNN}.xml verified by fetching vote_119_2_00217.xml (200, 28,745 bytes, all 100 member positions). The index URL names the current congress/session and must be advanced when session 3 opens. Complements congress-gov-api, whose roll-call endpoint is House-only. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | XML index |
| Method | Conditional GET of the current session's roll-call vote menu; the senate-votes adapter bounds enumeration to config.INDEX_LOOKBACK_DAYS and fetches one per-vote XML record per in-window vote. Stored under the VOTES collection (GUIDE §3 recorded votes), never AGENCYPR. |
| Adapter | senate-votes |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 4 item(s) in the last 14 days; most recent 2026-09-15; 0 of 355 request(s) to www.senate.gov returned no content.

This label has held since 2026-09-15T00:13:06Z (UTC) and was last re-checked 2026-09-17T03:58:34Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 4 in 14 days (0.29 per day) · most recent 2026-09-15 |
| Content length | 2,155 characters average, 2,104 median (shortest 2,041, longest 2,373) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.senate.gov | 355 request(s) · 355 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-17T04:25:07.580+00:00 UTC.

4 item(s) in the last 14 days; most recent 2026-09-15; 0 of 355 request(s) to www.senate.gov returned no content.

### All time

- **Our requests to www.senate.gov, all time (since 2026-08-01):** 1,401 request(s) · 1,401 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.senate.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-19 | 0 | 24 | 281 |
| 2026-08-20 | 0 | 34 | 333 |
| 2026-08-21 | 0 | 30 | 269 |
| 2026-08-22 | 0 | 30 | 214 |
| 2026-08-23 | 0 | 28 | 204 |
| 2026-08-24 | 0 | 28 | 227 |
| 2026-08-25 | 0 | 26 | 192 |
| 2026-08-26 | 0 | 26 | 236 |
| 2026-08-27 | 0 | 26 | 233 |
| 2026-08-28 | 0 | 26 | 259 |
| 2026-08-29 | 0 | 27 | 201 |
| 2026-08-30 | 0 | 26 | 323 |
| 2026-08-31 | 0 | 26 | 241 |
| 2026-09-01 | 0 | 26 | 297 |
| 2026-09-02 | 0 | 26 | 277 |
| 2026-09-03 | 0 | 25 | 354 |
| 2026-09-04 | 0 | 26 | 287 |
| 2026-09-05 | 0 | 33 | 313 |
| 2026-09-06 | 0 | 27 | 221 |
| 2026-09-07 | 0 | 26 | 190 |
| 2026-09-08 | 0 | 26 | 188 |
| 2026-09-09 | 0 | 26 | 219 |
| 2026-09-10 | 0 | 25 | 199 |
| 2026-09-11 | 0 | 26 | 212 |
| 2026-09-12 | 0 | 28 | 212 |
| 2026-09-13 | 0 | 26 | 241 |
| 2026-09-14 | 1 | 29 | 656 |
| 2026-09-15 | 3 | 29 | 183 |
| 2026-09-16 | 0 | 27 | 175 |
| 2026-09-17 | 0 | 1 | 144 |

## Our ingestion assessment

**Model-written ingestion assessment**

Our ingestion of Senate.gov's XML vote records maintains a consistent daily polling pattern, typically 25–29 requests per day, with zero request failures across 350 attempts. The source delivers roll-call vote menus and individual per-vote XML records containing complete member position data. Over the 14-day window, one item was observed on 2026-09-14. The ingestion bounds enumeration to a 7-day lookback to control request volume despite the published index listing the full Senate session. The underlying structure carries two known coverage limits: vote dates in the index lack year information and vote tallies are empty, requiring per-vote record retrieval; and en-bloc confirmations contain minimal structured metadata beyond title. The per-vote URL pattern has been verified and remains stable. Compared to the previous assessment from 2026-08-16, item delivery remains sparse, continuing a pattern in which the source answers all requests but new vote records appear infrequently.

_Model-written assessment of our own ingestion, generated 2026-09-15 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

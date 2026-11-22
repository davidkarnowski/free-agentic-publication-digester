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

Senate.gov's officially documented set of XML files, covering roll-call votes, committee hearing and meeting schedules, the floor schedule, and nomination status. It is the only machine-readable source in this digest for Senate votes.

Senate.gov XML services is the Senate's publicly documented collection of machine-readable files, published on the Senate website. The files are maintained under the Secretary of the Senate, which operates the Senate's Legislative Information System (LIS). The Senate is one of the two chambers of the United States Congress, the legislative branch of the federal government. The Secretary of the Senate is an officer of the Senate itself and is responsible for the chamber's legislative records. The files listed here are produced from those records.

The directory contains several kinds of XML files. The roll-call vote menu lists the recorded votes taken during a session of Congress. Each vote also has its own individual XML record that shows the question voted on, the result, and the position each senator took. Other files cover the committee hearings and meetings schedule, the Senate floor schedule, and nine nomination-status files. The nomination files sort nominations by status (pending, confirmed, withdrawn, or failed) and by whether the nomination is civilian or non-civilian.

Congress is numbered in two-year periods called Congresses, and each Congress has two annual sessions. The index files name a specific Congress and session, so the vote menu covers one session at a time.

In this digest, this source is the reference for Senate recorded votes. Entries drawn from it give the vote date, the question voted on, and the result. Because the source is structured data rather than narrative text, digest entries summarize fields in the files and do not quote prose from them. Schedule and nomination entries reflect what the files listed when they were retrieved. The files record only the fields described above and do not explain the reasons for any vote, scheduling decision, or nomination. Readers who want context on a particular action should consult the Senate's own pages.

Not every field is filled in every case. In the vote menu, the vote date may appear without a year, and the tally may appear only in the individual vote record. Some en-bloc confirmations are identified by their title alone, because the menu lists no question or result for them.

_Model-written orientation, generated 2026-11-14 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

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
| Status change | 2026-11-13: returned to active. A fresh probe through the identified client on 2026-11-13 at 15:50 UTC answered normally: HTTP 200, 168,372 bytes, the whole session's 262 votes. The refusal that began on 2026-10-23 has ended; its cause is not known, and the record of it is kept in the notes. Polling resumes. Votes taken while this source was unavailable are not listed in section 7 of the digests for those days; the Congressional Record granules in which they were printed appear in section 1.3. |
| Registry notes | Status history, the card's change note from 2026-11-08 to 2026-11-13: 2026-11-08: moved from active to unavailable. The Senate's roll-call vote menu answered normally through 2026-10-23 10:18 UTC, then refused our honestly-identified client with HTTP 403 on every poll from 2026-10-23 11:16 UTC (408 consecutive refusals by 2026-11-08), while robots.txt on the same host kept answering 200. The cause is not known. The refusal is recorded as observed and never evaded, and polling stops with this change. This is the only active source for the digest's recorded-votes section, so that section lists no votes while this source is unavailable. Votes captured before the change stay on the record. This source is to be re-probed in the future for a possible service update, and it returns to active only on a fresh probe through the identified client. Gate 3 (2026-07-31, live through the identified client): the menu answers 200 text/xml, 123,670 bytes, and lists the WHOLE session — 217 <vote> elements from 05-Jan to 30-Jul, so ingestion sees 100% of the Senate's recorded votes but must bound itself (8 fell inside the 7-day lookback that day: 1 index fetch + 8 records = 9 requests). Two coverage limits, both disclosed rather than papered over: (a) vote_date carries NO YEAR ('30-Jul') and vote_tally is present but EMPTY on all 217, so the tally exists only in the per-vote record, which is why wants_article() is True; (b) 2 of 217 rows are en-bloc confirmations carrying no issue/question/result — their title alone identifies them. Per-vote URL pattern vote{congress}{session}/vote_{c}_{s}_{NNNNN}.xml verified by fetching vote_119_2_00217.xml (200, 28,745 bytes, all 100 member positions). The index URL names the current congress/session and must be advanced when session 3 opens. Complements congress-gov-api, whose roll-call endpoint is House-only. |

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

**delivering** — 23 item(s) in the last 14 days; most recent 2026-11-20; 1 of 239 request(s) to www.senate.gov returned no content.

This label has held since 2026-11-21T05:10:23Z (UTC) and was last re-checked 2026-11-22T04:56:32Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 23 in 14 days (1.64 per day) · most recent 2026-11-20 |
| Content length | 1,798 characters average, 2,052 median (shortest 136, longest 2,141) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.senate.gov | 239 request(s) · 238 answered · 1 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.4% returned no content |

last answered request 2026-11-22T05:00:17.585+00:00 UTC.

23 item(s) in the last 14 days; most recent 2026-11-20; 1 of 239 request(s) to www.senate.gov returned no content.

### All time

- **Our requests to www.senate.gov, all time (since 2026-08-01):** 2,946 request(s) · 2,537 answered · 409 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.senate.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-24 | 0 | 25 | 207 |
| 2026-10-25 | 0 | 25 | 186 |
| 2026-10-26 | 0 | 25 | 180 |
| 2026-10-27 | 0 | 25 | 200 |
| 2026-10-28 | 0 | 25 | 217 |
| 2026-10-29 | 0 | 25 | 199 |
| 2026-10-30 | 0 | 27 | 191 |
| 2026-10-31 | 0 | 25 | 187 |
| 2026-11-01 | 0 | 26 | 200 |
| 2026-11-02 | 0 | 25 | 180 |
| 2026-11-03 | 0 | 26 | 168 |
| 2026-11-04 | 0 | 25 | 176 |
| 2026-11-05 | 0 | 25 | 198 |
| 2026-11-06 | 0 | 25 | 220 |
| 2026-11-07 | 0 | 25 | 227 |
| 2026-11-08 | 0 | 12 | 163 |
| 2026-11-09 | 0 | 0 | — |
| 2026-11-10 | 0 | 0 | — |
| 2026-11-11 | 0 | 0 | — |
| 2026-11-12 | 0 | 0 | — |
| 2026-11-13 | 6 | 20 | 308 |
| 2026-11-14 | 0 | 26 | 239 |
| 2026-11-15 | 0 | 24 | 229 |
| 2026-11-16 | 2 | 28 | 272 |
| 2026-11-17 | 1 | 26 | 195 |
| 2026-11-18 | 3 | 27 | 332 |
| 2026-11-19 | 3 | 28 | 297 |
| 2026-11-20 | 8 | 33 | 252 |
| 2026-11-21 | 0 | 26 | 201 |
| 2026-11-22 | 0 | 1 | 443 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest the Senate.gov XML services through the senate-votes adapter, which reads the current session's roll-call vote menu and fetches one per-vote XML record for each vote inside the seven-day lookback. We have ingested the vote menu and per-vote records, delivered in full, and item text averages 1,798 characters across the window. The 14-day window holds 23 items, a rate of 1.64 per day, with the most recent dated 2026-11-20, and health reads delivering. Of 239 requests to www.senate.gov, 238 returned content and one returned no content. From 2026-10-23 the vote menu answered HTTP 403 on every poll, reaching 408 consecutive HTTP 403 responses by 2026-11-08, when the source was set to unavailable; the cause is not known to us. A fresh probe through the identified client answered HTTP 200 on 2026-11-13, and the source returned to active. Votes taken during the unavailable period are not listed in digest section 7 for those days; their Congressional Record granules appear in section 1.3. Compared with the 2026-11-14 assessment, which recorded six items at 0.43 per day, with 189 of 210 requests returning no content and health reading degraded, the window now holds 23 items, the most recent date has moved from 2026-11-13 to 2026-11-20, and health reads delivering.

_Model-written assessment of our own ingestion, generated 2026-11-22 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/senate-xml.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/senate-xml.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: senate-xml)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Senate.gov XML services

unavailable · Legislative · Tier 1 · XML index · Secretary of the Senate (LIS)

Official site: https://www.senate.gov/general/common/generic/XML_Availability.htm · All sources: [sources.md](../sources.md)

## What this source is

The Senate's officially documented directory of XML files: roll-call vote menus and individual votes, the committee hearings/meetings schedule, the floor schedule, and nine nomination-status files (pending, confirmed, withdrawn, failed — civilian and non-civilian). The only machine source for Senate votes.

**Model-written orientation**

The Senate.gov XML services are officially documented machine-readable files published by the Secretary of the Senate, covering roll-call votes, committee and floor schedules, and nomination status. In this digest, the source is the only machine source for Senate recorded votes and is currently marked unavailable.

The Senate.gov XML services are a set of machine-readable files published on the official website of the United States Senate. They are listed on the Senate's XML availability page and are maintained under the Office of the Secretary of the Senate, the chamber officer responsible for its official records.

The Senate is the upper chamber of Congress, the legislative branch established by Article I of the Constitution. It shares lawmaking power with the House of Representatives, and each state is represented by two senators. The files in this source present parts of that work in structured form. They include roll-call vote menus, which list the votes taken in a session, and individual vote records that show how each senator voted on a given question. Other files cover the committee hearings and meetings schedule and the floor schedule, which show when the chamber and its committees are scheduled to meet. Nine nomination-status files track presidential nominations by status (pending, confirmed, withdrawn, or failed), separated into civilian and non-civilian nominations.

In this digest, the source feeds the recorded-votes section. A vote menu for a session is updated as votes occur. Each recorded vote generally has its own record, which can include the question voted on, the result, and the tally. Some entries are en bloc confirmations, which group several nominations into a single vote and may not carry a standard question or result line, so the vote title alone identifies them. Vote dates in the menu appear without a year, so the year comes from the session the file belongs to.

The source is currently marked unavailable in this digest. The last successful capture was on 2026-10-23. Votes captured before that point remain on the record, and no votes appear in the recorded-votes section while the source is unavailable. Readers who need Senate roll-call votes outside this digest can consult the Senate's roll-call vote pages on senate.gov.

_Model-written orientation, generated 2026-11-09 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `senate-xml` |
| Agency / parent organization | Secretary of the Senate (LIS) |
| Branch | legislative |
| Type | XML index |
| Status | unavailable |
| Tier | 1 |
| URL (home) | https://www.senate.gov/general/common/generic/XML_Availability.htm |
| URL (index) | https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_119_2.xml |
| Registered | 2026-07-28 |
| Status change | 2026-11-08: moved from active to unavailable. The Senate's roll-call vote menu answered normally through 2026-10-23 10:18 UTC, then refused our honestly-identified client with HTTP 403 on every poll from 2026-10-23 11:16 UTC (408 consecutive refusals by 2026-11-08), while robots.txt on the same host kept answering 200. The cause is not known. The refusal is recorded as observed and never evaded, and polling stops with this change. This is the only active source for the digest's recorded-votes section, so that section lists no votes while this source is unavailable. Votes captured before the change stay on the record. This source is to be re-probed in the future for a possible service update, and it returns to active only on a fresh probe through the identified client. |
| Registry notes | Gate 3 (2026-07-31, live through the identified client): the menu answers 200 text/xml, 123,670 bytes, and lists the WHOLE session — 217 <vote> elements from 05-Jan to 30-Jul, so ingestion sees 100% of the Senate's recorded votes but must bound itself (8 fell inside the 7-day lookback that day: 1 index fetch + 8 records = 9 requests). Two coverage limits, both disclosed rather than papered over: (a) vote_date carries NO YEAR ('30-Jul') and vote_tally is present but EMPTY on all 217, so the tally exists only in the per-vote record, which is why wants_article() is True; (b) 2 of 217 rows are en-bloc confirmations carrying no issue/question/result — their title alone identifies them. Per-vote URL pattern vote{congress}{session}/vote_{c}_{s}_{NNNNN}.xml verified by fetching vote_119_2_00217.xml (200, 28,745 bytes, all 100 member positions). The index URL names the current congress/session and must be advanced when session 3 opens. Complements congress-gov-api, whose roll-call endpoint is House-only. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | XML index |
| Method | Conditional GET of the current session's roll-call vote menu; the senate-votes adapter bounds enumeration to config.INDEX_LOOKBACK_DAYS and fetches one per-vote XML record per in-window vote. Stored under the VOTES collection (GUIDE §3 recorded votes), never AGENCYPR. |
| Adapter | senate-votes |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is unavailable.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is unavailable. Ingestion statistics are measured for active sources only.

### All time

- **Our requests to www.senate.gov, all time (since 2026-08-01):** 2,707 request(s) · 2,299 answered · 408 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.senate.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-11 | 0 | 26 | 203 |
| 2026-10-12 | 0 | 25 | 229 |
| 2026-10-13 | 0 | 25 | 209 |
| 2026-10-14 | 0 | 25 | 166 |
| 2026-10-15 | 0 | 26 | 153 |
| 2026-10-16 | 0 | 25 | 171 |
| 2026-10-17 | 0 | 25 | 155 |
| 2026-10-18 | 0 | 25 | 158 |
| 2026-10-19 | 0 | 25 | 160 |
| 2026-10-20 | 0 | 25 | 142 |
| 2026-10-21 | 0 | 25 | 181 |
| 2026-10-22 | 0 | 25 | 204 |
| 2026-10-23 | 0 | 25 | 189 |
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

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest the Senate XML vote menu for the current session and fetch one per-vote record for each vote inside our seven-day lookback. At registration on 2026-07-31, the index listed 217 votes for the session, although its vote dates carry no year. In the 14-day window we ingested no items. The most recent item is dated 2026-10-01, 37 days before this measurement. Of 330 requests to www.senate.gov, none returned content, and the fetch summary classifies all 330 as client errors. The daily breakdown for 2026-11-01 through 2026-11-07 records 153 failed requests. Our most recent successful request was on 2026-10-23 at 10:18 UTC, and health reads no-response. The 2026-10-25 assessment recorded 43 of 327 requests (13.1 percent) that returned no content, with errors beginning 2026-10-23, and reported that this crossed our 10 percent degradation threshold. The share of requests without content is now 100 percent. From outside, we cannot tell whether these requests returned no content because of load, maintenance, or a limit the publisher sets.

_Model-written assessment of our own ingestion, generated 2026-11-07 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/state-travel-advisories.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/state-travel-advisories.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: state-travel-advisories)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# State Travel Advisories

active · ingestion health: quiet · Executive · Tier 2 · RSS feed · Department of State

Official site: https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html · All sources: [sources.md](../sources.md)

## What this source is

The State Department's Bureau of Consular Affairs keeps a travel advisory for each country, rating it from Level 1 (exercise normal precautions) to Level 4 (do not travel) and giving the reasons. An advisory is re-issued when its level or content changes or after periodic review; across all countries that happens several times a week.

**Model-written orientation**

The State Department's Bureau of Consular Affairs issues travel advisories for countries worldwide, using a four-level scale to rate conditions that may affect travel safety.

The Bureau of Consular Affairs, part of the U.S. Department of State, maintains travel advisories for every country and territory to help Americans understand conditions that may affect their safety abroad. Each advisory receives one of four levels: Level 1 (exercise normal precautions), Level 2 (exercise increased caution), Level 3 (reconsider travel), or Level 4 (do not travel). A country's level reflects conditions including crime, civil unrest, natural disasters, disease, and terrorism risk. The bureau updates advisories when circumstances change or on a periodic review cycle; across all countries, reissues occur several times per week. The bureau maintains the advisories as an ongoing resource, with each advisory accessible from the bureau's website and updated when new information warrants. An update to an advisory means the bureau has reissued it, which happens when material conditions have shifted or when a standing periodic review is complete. In this digest you will see advisories that were newly reissued within the displayed time period. Each entry shows the country, its current advisory level, and the text of the advisory itself. Because the advisory pages do not respond to automated requests, the digest draws the advisory text from the RSS feed that publishes the advisories, rather than from the advisory page itself. The digest includes advisories across the full range of levels—from countries with Level 1 status to those with Level 4—and readers can see countries where advisory status changed during the period. The advisories reflect conditions as assessed by the State Department based on information from embassy staff and other sources, and they help both individuals and organizations make decisions about international travel and understand circumstances in regions of interest.

_Model-written orientation, generated 2026-10-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `state-travel-advisories` |
| Agency / parent organization | Department of State |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://travel.state.gov/_res/rss/TAsTWs.xml |
| URL (home) | https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html |
| Registered | 2026-10-05 |
| Registry notes | Registered 2026-10-05 from the 2026-10-04 source research. Probed 2026-10-04 through FAPD's identified probe client: the feed answered HTTP 200 (956 KB, 216 items); the sample advisory page answered 403, recorded and not retried. Re-verified 2026-10-05 from the operator machine as a brief test, outside the server's budget, through FAPD's identified probe client (robots allows, no crawl-delay, no Retry-After, HTTP 200) for the feed (614 KB, 223 items, 223/223 dated, date-only RFC 822 'Tue, 15 Sep 2026'); its robots.txt answered 403, which the client reads as allow (RFC 9309), and no advisory page was requested. Three findings shaped a dedicated adapter (operator-approved 2026-10-05): the feed is a snapshot of every advisory in force (back to 2023-06), not a list of recent posts, so it is bounded to the lookback window; every item's GUID is the country's permanent page, which a re-issue keeps, so identity is the GUID plus the advisory's date, or each re-issue would be deduped away (disclosed limit: an edit made without a new date is not seen); and the advisory pages refuse FAPD, so it is feed-only, with the advisory text taken from the item description (~2,000 characters on average). Gate 2 through the adapter, 2026-10-05: 223 items read, 0 inside the 7-day window (the newest advisory was dated 2026-09-15), none undated; the channel's own pubDate is the moment of the request, so the feed is generated live, not a stale file. The feed sends no ETag or Last-Modified, so every hourly poll is a full fetch (about 614 KB, compressed in transit); the home URL is the one the feed's channel names. Coverage (gate 3): every re-issue dated inside the window. Of the advisories in force on 2026-10-05, 48 carried an August 2026 date and 17 a September date; a country re-issued twice shows only its latest, so these count countries, not re-issues. To measure after activation: whether an advisory is posted on the date it carries (one posted a day late is counted as backfill, not listed). ACTIVATED 2026-10-05 (operator). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the travel-advisory RSS feed via AgencyClient, feed metadata only (travel-advisories adapter), keeping advisories dated within the lookback window; each item's description carries the advisory text. |
| Adapter | travel-advisories |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**quiet** — No item recorded from this source in the last 180 days.

This label has held since 2026-10-05T23:57:58Z (UTC) and was last re-checked 2026-10-08T03:55:12Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — none recorded in the lookback period |
| Our requests to travel.state.gov | 60 request(s) · 60 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-08T04:00:10.275+00:00 UTC.

No item recorded from this source in the last 180 days.

### All time

- **Our requests to travel.state.gov, all time (since 2026-10-05):** 60 request(s) · 60 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to travel.state.gov | Mean response time (ms) |
|---|---|---|---|
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
| 2026-09-28 | 0 | 0 | — |
| 2026-09-29 | 0 | 0 | — |
| 2026-09-30 | 0 | 0 | — |
| 2026-10-01 | 0 | 0 | — |
| 2026-10-02 | 0 | 0 | — |
| 2026-10-03 | 0 | 0 | — |
| 2026-10-04 | 0 | 0 | — |
| 2026-10-05 | 0 | 6 | 322 |
| 2026-10-06 | 0 | 26 | 306 |
| 2026-10-07 | 0 | 27 | 303 |
| 2026-10-08 | 0 | 1 | 559 |

## Our ingestion assessment

**Model-written ingestion assessment**

State Department travel advisories activated October 5 via a dedicated feed-only adapter reading an RSS feed of all advisories in force, with advisory text extracted from item descriptions (~2,000 characters per advisory on average). The feed carries advisories dating back to 2023-06, generated live on each poll (223 items across all advisory levels on October 5 verification). The current 14-day window shows 0 items collected because the most recent advisory in the feed carries a September 15 date, falling outside the 7-day lookback window. Advisory detail pages return HTTP 403, confirming feed-only posture. The feed sends no ETag or Last-Modified, so each hourly poll fetches the full feed (~614 KB compressed). Coverage will be measured by whether advisories are filed on the date they carry.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

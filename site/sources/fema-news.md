<!-- Markdown twin of https://fapd.info/sources/fema-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fema-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fema-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FEMA Press Releases

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.fema.gov/about/news-multimedia/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Federal Emergency Management Agency, within DHS, coordinates federal disaster response and recovery. Its national press-release index carries disaster declarations, response updates, and assistance-program announcements; volume rises sharply during active disasters.

**Model-written orientation**

The Federal Emergency Management Agency coordinates federal disaster response and recovery and publishes announcements of disaster declarations, recovery operations, and assistance programs.

The Federal Emergency Management Agency (FEMA) is an agency within the Department of Homeland Security responsible for coordinating the federal government's response to and recovery from disasters—including natural disasters such as hurricanes, earthquakes, wildfires, and flooding; human-caused disasters such as industrial accidents and hazardous materials releases; and terrorism-related events. FEMA works with state and local emergency management agencies, the American Red Cross, and other organizations to provide emergency response coordination and financial assistance.

FEMA operates the Disaster Assistance Program, which provides grants and loans to individuals, businesses, and state and local governments affected by declared disasters. The agency also maintains the National Response Framework, which coordinates response resources across federal agencies, and operates the National Incident Management System, the standardized incident management framework used by emergency responders nationwide. FEMA also manages risk reduction programs including flood insurance through the National Flood Insurance Program and hazard mitigation initiatives.

FEMA's press releases cover disaster declarations (which trigger federal assistance eligibility), major disasters as they occur, updates on ongoing disaster response operations, recovery milestones, assistance program announcements, grant and funding opportunities, preparedness initiatives, and administrative notices. During active disasters, release volume increases substantially as the agency issues daily updates on response activities and recovery progress.

In this digest, readers will encounter disaster declarations, response updates and operational announcements, recovery milestones, assistance program notices, preparedness announcements, and administrative updates. Volume and frequency of releases vary significantly based on active disasters; periods without major active disasters produce fewer releases, while major disaster events generate multiple daily updates. For comprehensive information on ongoing disaster response, readers should consult FEMA's dedicated disaster pages and other emergency management resources.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fema-news` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.fema.gov/about/news-multimedia/press-releases |
| URL (index) | https://www.fema.gov/about/news-multimedia/press-releases |
| Registered | 2026-07-26 |
| Registry notes | FEMA also posts per-disaster releases; the national index is a subset. Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered. Re-probed 2026-07-31: HTTP 200, robots allows (crawl-delay 15s, honored), still no feed. ACTIVATED 2026-07-31 with the html-index adapter. Gate 3: the index paginates at 10 entries per page and we read page 1 only; each entry carries a <time datetime> with a full timestamp and a 150-300-char body paragraph, both read from FEMA's own markup — so every listed item is agency-dated, none observation-dated, and the stored text is the agency's own summary (mode feed-only, one request per poll, no article fetches). Under-coverage, and it is real here: FEMA's volume rises sharply during an active disaster, and at 10 entries per page an hourly poll would miss releases published faster than that; the per-disaster release pages are a separate channel this entry does not cover. |

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

**delivering** — 55 item(s) in the last 14 days; most recent 2026-10-08; 0 of 340 request(s) to www.fema.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-09T03:52:22Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 9 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 55 in 14 days (3.93 per day) · most recent 2026-10-08 |
| Content length | 432 characters average, 355 median (shortest 155, longest 943) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.fema.gov | 340 request(s) · 340 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-09T04:00:11.776+00:00 UTC.

55 item(s) in the last 14 days; most recent 2026-10-08; 0 of 340 request(s) to www.fema.gov returned no content.

### All time

- **Our requests to www.fema.gov, all time (since 2026-08-01):** 1,906 request(s) · 1,891 answered · 15 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.fema.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-10 | 1 | 24 | 1414 |
| 2026-09-11 | 1 | 26 | 518 |
| 2026-09-12 | 0 | 27 | 927 |
| 2026-09-13 | 0 | 25 | 240 |
| 2026-09-14 | 7 | 27 | 342 |
| 2026-09-15 | 4 | 25 | 525 |
| 2026-09-16 | 1 | 26 | 470 |
| 2026-09-17 | 4 | 25 | 146 |
| 2026-09-18 | 2 | 29 | 214 |
| 2026-09-19 | 0 | 25 | 188 |
| 2026-09-20 | 0 | 25 | 188 |
| 2026-09-21 | 6 | 28 | 237 |
| 2026-09-22 | 5 | 25 | 1836 |
| 2026-09-23 | 10 | 24 | 184 |
| 2026-09-24 | 7 | 25 | 752 |
| 2026-09-25 | 7 | 26 | 1653 |
| 2026-09-26 | 2 | 26 | 200 |
| 2026-09-27 | 0 | 26 | 192 |
| 2026-09-28 | 7 | 27 | 274 |
| 2026-09-29 | 6 | 27 | 158 |
| 2026-09-30 | 9 | 25 | 488 |
| 2026-10-01 | 9 | 27 | 159 |
| 2026-10-02 | 4 | 26 | 554 |
| 2026-10-03 | 0 | 26 | 155 |
| 2026-10-04 | 0 | 25 | 159 |
| 2026-10-05 | 5 | 26 | 189 |
| 2026-10-06 | 3 | 26 | 339 |
| 2026-10-07 | 1 | 26 | 356 |
| 2026-10-08 | 9 | 26 | 152 |
| 2026-10-09 | 0 | 1 | 131 |

## Our ingestion assessment

**Model-written ingestion assessment**

The national press-release index delivered 66 items over 14 days at 4.71 per day, substantially above the prior 2.57 per day. Each item averages 452 characters extracted from FEMA's markup. All 337 polling requests succeeded, an improvement from the prior 2.8% no-response rate. The index paginates at 10 entries per page and we read page 1 only; each entry carries a full timestamp and a 150–300-character summary. FEMA volume rises sharply during active disasters; the single-page read means releases published faster than the hourly poll interval may be missed.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

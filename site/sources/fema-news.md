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

**delivering** — 3 item(s) in the last 14 days; most recent 2026-11-11; 31 of 336 request(s) to www.fema.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-13T04:50:48Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 31 request(s) (31 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-11-11 |
| Content length | 233 characters average, 247 median (shortest 167, longest 285) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.fema.gov | 336 request(s) · 305 answered · 31 declined (4xx) · 0 server declined (5xx) · 0 no response — 9.2% returned no content |

last answered request 2026-11-13T05:00:14.910+00:00 UTC.

3 item(s) in the last 14 days; most recent 2026-11-11; 31 of 336 request(s) to www.fema.gov returned no content.

### All time

- **Our requests to www.fema.gov, all time (since 2026-08-01):** 2,795 request(s) · 2,749 answered · 46 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.fema.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-15 | 2 | 26 | 149 |
| 2026-10-16 | 2 | 25 | 166 |
| 2026-10-17 | 1 | 25 | 162 |
| 2026-10-18 | 1 | 25 | 149 |
| 2026-10-19 | 3 | 24 | 148 |
| 2026-10-20 | 12 | 25 | 123 |
| 2026-10-21 | 3 | 25 | 211 |
| 2026-10-22 | 12 | 25 | 137 |
| 2026-10-23 | 1 | 25 | 132 |
| 2026-10-24 | 0 | 25 | 138 |
| 2026-10-25 | 1 | 26 | 180 |
| 2026-10-26 | 2 | 24 | 128 |
| 2026-10-27 | 5 | 25 | 133 |
| 2026-10-28 | 5 | 25 | 162 |
| 2026-10-29 | 4 | 25 | 124 |
| 2026-10-30 | 0 | 27 | 140 |
| 2026-10-31 | 0 | 25 | 160 |
| 2026-11-01 | 0 | 25 | 176 |
| 2026-11-02 | 1 | 25 | 141 |
| 2026-11-03 | 0 | 25 | 152 |
| 2026-11-04 | 0 | 25 | 132 |
| 2026-11-05 | 0 | 26 | 171 |
| 2026-11-06 | 1 | 25 | 146 |
| 2026-11-07 | 0 | 25 | 113 |
| 2026-11-08 | 0 | 26 | 140 |
| 2026-11-09 | 0 | 26 | 276 |
| 2026-11-10 | 0 | 26 | 149 |
| 2026-11-11 | 1 | 25 | 117 |
| 2026-11-12 | 0 | 31 | 160 |
| 2026-11-13 | 0 | 1 | 188 |

## Our ingestion assessment

**Model-written ingestion assessment**

We read the FEMA Press Releases national index in feed-only mode through the html-index adapter, with one listing fetch per poll and no article fetches. Each entry carries FEMA's own full timestamp and a body paragraph, which we store as the item text, so items are dated from the publisher's markup. Over the 14-day window we recorded 19 items at 1.36 per day, down from 66 items at 4.71 per day in the prior assessment. Item text averaged 488 characters (median 437, range 167 to 869). The most recent item is dated 2026-11-02. Of 328 requests to www.fema.gov, 315 returned content and 13 returned no content, an error rate of 4.0 percent. The prior assessment recorded 337 requests with all succeeding. On 2026-11-04, 12 of 25 requests returned no content, and 1 more did so on 2026-11-05. We read page 1 only, which holds 10 entries, so releases published between polls beyond that page would not be seen. The per-disaster release pages are a separate channel that this entry does not cover.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

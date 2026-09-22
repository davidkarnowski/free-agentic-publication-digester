<!-- Markdown twin of https://fapd.info/sources/labor-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/labor-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: labor-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Labor News Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Department of Labor

Official site: https://www.dol.gov/newsroom/releases · All sources: [sources.md](../sources.md)

## What this source is

The Department of Labor administers wage, workplace-safety, and benefits law and publishes major employment statistics. This RSS feed carries its national news releases — enforcement actions, rulemakings, and program announcements — with near-full-text descriptions (10 most recent items, ~1,800 characters each; article pages extract at ~6,000 characters).

**Model-written orientation**

The Department of Labor publishes national news releases on employment enforcement, workplace safety initiatives, and federal labor programs.

The Department of Labor is the federal executive agency responsible for administering and enforcing federal wage and hour law, workplace safety regulations, employment benefits programs, and labor statistics. It houses the Occupational Safety and Health Administration (OSHA), the Wage and Hour Division, the Employee Benefits Security Administration, and the Bureau of Labor Statistics, among other components. Through its newsroom RSS feed, the department publishes press releases and announcements on major departmental actions, policy changes, and enforcement initiatives affecting workers and employers across the United States.

Readers will find press releases covering a broad range of labor-related topics. These include announcements of workplace safety enforcement actions, such as citations and penalties for violations of occupational safety standards; final rules and regulations affecting wage and hour protections, benefits, or working conditions; announcements of grant programs or funding for workforce development and training; major litigation outcomes or settlements; statistics on employment and labor market conditions; and departmental initiatives addressing worker rights, workplace safety, or employment programs. Releases often include enforcement data, statements from departmental officials, details about how rules will be implemented, and information about affected populations or industries.

The press releases reflect the department's role in day-to-day enforcement of federal labor law and administration of employment programs. They serve as official notification to employers, workers, advocacy organizations, and the public of federal labor policy decisions and enforcement priorities. The newsroom publishes both immediate announcements of specific enforcement or policy actions and longer-term program announcements. Content dates are supplied by the publisher and reflect the official release date of each announcement.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `labor-newsroom` |
| Agency / parent organization | Department of Labor |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.dol.gov/rss/releases.xml |
| URL (home) | https://www.dol.gov/newsroom/releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: RSS verified end-to-end — 10 items, avg description 1765 chars, sample article extracted (6033 chars text). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Would poll the news-release RSS feed daily for new items. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 4 item(s) in the last 14 days; most recent 2026-09-17; 4 of 352 request(s) to www.dol.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-22T03:47:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 28 request(s) (28 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 4 in 14 days (0.29 per day) · most recent 2026-09-17 |
| Content length | 1,189 characters average, 1,193 median (shortest 337, longest 2,033) |
| Delivery mode | feed-fallback — the feed's summary, used because the article page could not be read |
| Our requests to www.dol.gov | 352 request(s) · 348 answered · 4 declined (4xx) · 0 server declined (5xx) · 0 no response — 1.1% returned no content |

last answered request 2026-09-22T04:01:28.409+00:00 UTC.

4 item(s) in the last 14 days; most recent 2026-09-17; 4 of 352 request(s) to www.dol.gov returned no content.

### All time

- **Our requests to www.dol.gov, all time (since 2026-07-30):** 1,596 request(s) · 1,578 answered · 18 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.dol.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-24 | 3 | 31 | 204 |
| 2026-08-25 | 0 | 26 | 184 |
| 2026-08-26 | 2 | 28 | 168 |
| 2026-08-27 | 1 | 27 | 201 |
| 2026-08-28 | 0 | 26 | 174 |
| 2026-08-29 | 0 | 27 | 177 |
| 2026-08-30 | 0 | 26 | 231 |
| 2026-08-31 | 0 | 26 | 176 |
| 2026-09-01 | 0 | 25 | 191 |
| 2026-09-02 | 0 | 26 | 348 |
| 2026-09-03 | 2 | 28 | 353 |
| 2026-09-04 | 1 | 27 | 260 |
| 2026-09-05 | 0 | 33 | 288 |
| 2026-09-06 | 0 | 26 | 192 |
| 2026-09-07 | 1 | 27 | 288 |
| 2026-09-08 | 1 | 27 | 162 |
| 2026-09-09 | 0 | 27 | 167 |
| 2026-09-10 | 1 | 27 | 135 |
| 2026-09-11 | 0 | 25 | 150 |
| 2026-09-12 | 0 | 29 | 227 |
| 2026-09-13 | 0 | 26 | 235 |
| 2026-09-14 | 1 | 30 | 298 |
| 2026-09-15 | 1 | 27 | 131 |
| 2026-09-16 | 0 | 27 | 206 |
| 2026-09-17 | 1 | 27 | 139 |
| 2026-09-18 | 0 | 26 | 214 |
| 2026-09-19 | 0 | 26 | 166 |
| 2026-09-20 | 0 | 26 | 161 |
| 2026-09-21 | 0 | 28 | 228 |
| 2026-09-22 | 0 | 1 | 153 |

## Our ingestion assessment

**Model-written ingestion assessment**

Labor news releases arrive through RSS feed. Over 14 days we collected 9 items averaging 1,799 characters at 0.64 per day, most recent on September 4. Delivery mode is feed-fallback, indicating article page fetches are not retrieving content, so feed summaries serve as the delivery text. The www.dol.gov host shows 2.6% request failure (9 of 352 requests). Compared to the prior assessment (15 items at ~1/day with full article extraction), collection volume has declined and delivery has shifted from full article text extraction to feed summaries only.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

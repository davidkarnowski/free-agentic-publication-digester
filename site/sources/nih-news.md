<!-- Markdown twin of https://fapd.info/sources/nih-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nih-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nih-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NIH News Releases

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Department of Health and Human Services

Official site: https://www.nih.gov/news-events/news-releases · All sources: [sources.md](../sources.md)

## What this source is

The National Institutes of Health is the federal biomedical research agency within HHS. Its news-release index carries announcements of research findings, grant programs, and institute actions, typically one or more items per business day.

**Model-written orientation**

The National Institutes of Health, the federal biomedical research agency within the Department of Health and Human Services, publishes announcements of research discoveries and grant programs.

The National Institutes of Health (NIH) is the federal government's primary research agency supporting biomedical and behavioral science. Part of the Department of Health and Human Services, NIH conducts intramural research in its own laboratories on the NIH campus in Maryland and supports extramural research through grants to universities, medical schools, research hospitals, and independent research institutions across the nation and internationally. With an annual budget of tens of billions of dollars, NIH is among the world's largest funding sources for medical research.

NIH is organized into twenty-seven institutes and centers (ICs), each focused on particular diseases or research areas: the National Cancer Institute, National Heart, Lung, and Blood Institute, National Institute of Diabetes and Digestive and Kidney Diseases, and many others. Each IC manages research programs, training initiatives, and intramural labs within its domain. NIH research spans basic science (molecular biology, genetics, neuroscience) to clinical investigation and translational research aimed at developing new treatments and therapies. The agency also funds science education and training for the next generation of biomedical researchers.

In this digest, you will see NIH announcements of research discoveries from NIH-supported scientists, major grant awards and program announcements, updates on research initiatives and collaborative consortia, and statements from NIH leadership. The news releases highlight significant research findings, new funding opportunities, and scientific advances with potential bearing on human health. NIH news typically includes links to peer-reviewed publications, detailed research descriptions, and information on grant programs, serving researchers, healthcare professionals, patients, and the science-interested public.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nih-news` |
| Agency / parent organization | Department of Health and Human Services |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.nih.gov/news-releases/feed.xml |
| URL (home) | https://www.nih.gov/news-events/news-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 56 article link(s); 3 dated inside the 7-day lookback, 7 dated outside it, 46 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Feed FOUND 2026-08-06 by mining the 2026-07-31 captured page for feed-shaped links (autodiscovery had missed it — NIH links its feed from the page body, not <link rel=alternate> in <head>): https://www.nih.gov/news-releases/feed.xml probes feed-ok, 10 items, 10/10 with guid and date, sample article extracts at 9,549 chars, newest item current. NOT activated: the feed states dates as 'Wed, 08/05/2026 - 08:00', a Drupal format report._claimed_day cannot read (verified — it returns None). An unreadable claimed date falls to LISTED, not backfill, so activating as-is would publish the feed's whole window as today's news — the 721-item failure of 2026-07-31 through a new door. Activation needs a date-parsing extension for the Drupal 'm/d/Y - H:i' form, then a re-probe. ACTIVATED 2026-08-06. Feed found by mining the 2026-07-31 captured page for feed-shaped links — autodiscovery had missed it because NIH links its feed from the page body, not <link rel=alternate> in <head>. Probed feed-ok twice: 10 items, 10/10 with guid and date, sample release extracts at 9,549 chars; the feed's description is a ~123-character teaser, so full mode is required. Activation was blocked until the same day by the date format: NIH's Drupal site emits 'Wed, 08/05/2026 - 08:00' in <pubDate>, which neither the RFC 822 nor the ISO reader could parse, and an unreadable claimed date falls to LISTED rather than backfill — activating unparsed would have published the feed's seven-week window as today's news. The third dating tier (GUIDE §3, 2026-08-06) reads it; verified against the live feed, all ten items now sort to backfill because none was published today. Expect zero listed items from this source on days NIH does not publish, which is most days. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the news-releases RSS feed via AgencyClient, then fetches each new release for full text (mode full). |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 3 item(s) in the last 14 days; most recent 2026-10-08; 0 of 337 request(s) to www.nih.gov returned no content.

This label has held since 2026-10-07T13:44:05Z (UTC) and was last re-checked 2026-10-09T03:52:22Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-08 |
| Content length | 8,156 characters average, 7,856 median (shortest 6,834, longest 9,778) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.nih.gov | 337 request(s) · 337 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-09T04:00:11.597+00:00 UTC.

3 item(s) in the last 14 days; most recent 2026-10-08; 0 of 337 request(s) to www.nih.gov returned no content.

### All time

- **Our requests to www.nih.gov, all time (since 2026-08-06):** 1,691 request(s) · 1,691 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nih.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-10 | 0 | 25 | 259 |
| 2026-09-11 | 1 | 26 | 327 |
| 2026-09-12 | 0 | 27 | 321 |
| 2026-09-13 | 0 | 25 | 358 |
| 2026-09-14 | 2 | 31 | 448 |
| 2026-09-15 | 0 | 25 | 287 |
| 2026-09-16 | 0 | 26 | 329 |
| 2026-09-17 | 0 | 25 | 308 |
| 2026-09-18 | 1 | 26 | 350 |
| 2026-09-19 | 0 | 25 | 300 |
| 2026-09-20 | 0 | 25 | 252 |
| 2026-09-21 | 1 | 28 | 334 |
| 2026-09-22 | 0 | 26 | 289 |
| 2026-09-23 | 2 | 26 | 379 |
| 2026-09-24 | 1 | 26 | 268 |
| 2026-09-25 | 0 | 26 | 336 |
| 2026-09-26 | 0 | 26 | 332 |
| 2026-09-27 | 0 | 25 | 270 |
| 2026-09-28 | 0 | 27 | 360 |
| 2026-09-29 | 0 | 25 | 312 |
| 2026-09-30 | 0 | 25 | 301 |
| 2026-10-01 | 0 | 26 | 279 |
| 2026-10-02 | 0 | 26 | 257 |
| 2026-10-03 | 0 | 24 | 223 |
| 2026-10-04 | 0 | 25 | 232 |
| 2026-10-05 | 0 | 26 | 265 |
| 2026-10-06 | 0 | 26 | 263 |
| 2026-10-07 | 2 | 29 | 223 |
| 2026-10-08 | 1 | 26 | 230 |
| 2026-10-09 | 0 | 1 | 308 |

## Our ingestion assessment

**Model-written ingestion assessment**

The source delivers full-text articles via RSS feed at www.nih.gov/news-releases/feed.xml. The feed was discovered and activated 2026-08-06 after date-format parsing support was added to handle the publisher's Drupal format. Over 14 days, 2 items arrived at 0.14 items per day, with the most recent on 2026-10-07. Extracted articles average 7,345 characters, ranging from 6,834 to 7,856 characters. All 337 polling requests succeeded with no failures (0% error rate). The feed carries a 123-character teaser in each item, requiring full-text extraction from article pages. The source publishes inconsistently; most days carry no releases. Compared to the assessment of 2026-10-03, the 14-day window now contains 2 items versus 4 measured then, reflecting the natural aging of earlier items out of the measurement window.

_Model-written assessment of our own ingestion, generated 2026-10-08 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

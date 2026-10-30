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

**delivering** — 2 item(s) in the last 14 days; most recent 2026-10-23; 0 of 330 request(s) to www.nih.gov returned no content.

This label has held since 2026-10-23T17:22:46Z (UTC) and was last re-checked 2026-10-30T03:49:13Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-10-23 |
| Content length | 8,735 characters average, 8,735 median (shortest 7,557, longest 9,913) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.nih.gov | 330 request(s) · 330 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-30T04:00:14.093+00:00 UTC.

2 item(s) in the last 14 days; most recent 2026-10-23; 0 of 330 request(s) to www.nih.gov returned no content.

### All time

- **Our requests to www.nih.gov, all time (since 2026-08-06):** 2,225 request(s) · 2,225 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nih.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-01 | 0 | 26 | 279 |
| 2026-10-02 | 0 | 26 | 257 |
| 2026-10-03 | 0 | 24 | 223 |
| 2026-10-04 | 0 | 25 | 232 |
| 2026-10-05 | 0 | 26 | 265 |
| 2026-10-06 | 0 | 26 | 263 |
| 2026-10-07 | 2 | 29 | 223 |
| 2026-10-08 | 1 | 26 | 230 |
| 2026-10-09 | 1 | 26 | 240 |
| 2026-10-10 | 0 | 25 | 218 |
| 2026-10-11 | 0 | 26 | 211 |
| 2026-10-12 | 0 | 25 | 231 |
| 2026-10-13 | 1 | 26 | 253 |
| 2026-10-14 | 1 | 26 | 268 |
| 2026-10-15 | 0 | 26 | 275 |
| 2026-10-16 | 0 | 25 | 248 |
| 2026-10-17 | 0 | 25 | 236 |
| 2026-10-18 | 0 | 25 | 234 |
| 2026-10-19 | 0 | 25 | 222 |
| 2026-10-20 | 0 | 25 | 232 |
| 2026-10-21 | 0 | 25 | 231 |
| 2026-10-22 | 0 | 25 | 219 |
| 2026-10-23 | 2 | 28 | 251 |
| 2026-10-24 | 0 | 26 | 245 |
| 2026-10-25 | 0 | 25 | 197 |
| 2026-10-26 | 0 | 25 | 224 |
| 2026-10-27 | 0 | 25 | 217 |
| 2026-10-28 | 0 | 25 | 234 |
| 2026-10-29 | 0 | 25 | 216 |
| 2026-10-30 | 0 | 1 | 248 |

## Our ingestion assessment

**Model-written ingestion assessment**

The NIH News Releases source ingests via an RSS feed available at https://www.nih.gov/news-releases/feed.xml, delivering full article text. Feed descriptions are approximately 123 characters; the feed carries publication dates in Drupal format ('Wed, 08/05/2026 - 08:00'), which required date-parsing support added prior to activation on 2026-08-06 to prevent publishing the entire feed window as current content. Over the 14-day measurement window, four items were delivered at an average of 0.29 per day, with extracted content ranging from 7,557 to 9,913 characters (average 8,676, median 8,616). All 333 polling requests to www.nih.gov succeeded with a zero error rate. The publication pattern is irregular; the source publishes infrequently and most days contain no releases. The prior assessment from 2026-10-23 measured two items, and the current measurement shows this count has doubled, with the most recent item now dated 2026-10-23 compared to the prior most-recent date of 2026-10-14.

_Model-written assessment of our own ingestion, generated 2026-10-24 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/nist-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nist-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nist-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NIST News

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Department of Commerce

Official site: https://www.nist.gov/news-events/news · All sources: [sources.md](../sources.md)

## What this source is

The National Institute of Standards and Technology, within Commerce, develops measurement science and technical standards. Its news index carries announcements on standards publications, research results, and technology programs, typically several items per week.

**Model-written orientation**

The National Institute of Standards and Technology (NIST), within the Commerce Department, publishes news on standards development, measurement science research, and technology programs.

The National Institute of Standards and Technology (NIST) is a non-regulatory agency of the U.S. Department of Commerce. Founded in 1901 as the National Bureau of Standards, NIST conducts research and develops standards and technical guidelines across a wide range of scientific, technological, and industrial applications. The institute maintains laboratories, develops measurement science, and collaborates with industry, academia, and other government agencies.

NIST's news channel covers announcements related to the institute's research programs, published standards, technology initiatives, and partnerships. Content typically includes notices of new or updated standards publications, results from laboratory research programs, announcements of research collaborations, information about NIST conferences and technical working groups, organizational changes, and program updates. The news feed provides both broad announcements and specialized topic-specific updates.

Items appearing in this digest from NIST will reflect news the agency has chosen to publish. These may include published or revised standards in various technical fields, research project completions or breakthroughs, partnerships with private companies or academic institutions, grant opportunities, cybersecurity standards or guidelines, manufacturing technology development, or organizational announcements. NIST's publications serve industry, government, and the public by establishing technical baselines and advancing measurement science.

NIST's role as a standards-development agency means its publications carry significant weight across multiple sectors. The institute produces standards and guidelines used in manufacturing, cybersecurity, healthcare, energy, and many other fields. The news channel provides a direct window into what standards and research initiatives NIST is prioritizing and completing.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nist-news` |
| Agency / parent organization | Department of Commerce |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.nist.gov/news-events/news/rss.xml |
| URL (home) | https://www.nist.gov/news-events/news |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: no feed autodiscovered in the index HTML — but NIST's own feed documentation page (nist.gov/pao/nist-rss-feeds) lists news-events/news/rss.xml plus ~24 topic feeds and 4 blogs; autodiscovery alone under-finds. Re-probed 2026-07-28 at the documented URL: verified end-to-end — 40 items, short teaser descriptions (~134 chars), sample article page extracted cleanly. Content evaluation: article fetch is the substance (descriptions are teasers); ~24 topic feeds remain unregistered depth. Activated 2026-07-28. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the documented news RSS feed via AgencyClient. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 3 item(s) in the last 14 days; most recent 2026-09-18; 0 of 348 request(s) to www.nist.gov returned no content.

This label has held since 2026-09-10T14:45:25Z (UTC) and was last re-checked 2026-09-24T03:57:29Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-09-18 |
| Content length | 7,481 characters average, 7,085 median (shortest 6,872, longest 8,486) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.nist.gov | 348 request(s) · 348 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-09-24T04:46:19.552+00:00 UTC.

3 item(s) in the last 14 days; most recent 2026-09-18; 0 of 348 request(s) to www.nist.gov returned no content.

### All time

- **Our requests to www.nist.gov, all time (since 2026-07-30):** 1,630 request(s) · 1,624 answered · 6 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nist.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-08-26 | 0 | 26 | 135 |
| 2026-08-27 | 0 | 25 | 178 |
| 2026-08-28 | 0 | 26 | 132 |
| 2026-08-29 | 0 | 27 | 115 |
| 2026-08-30 | 0 | 27 | 132 |
| 2026-08-31 | 0 | 26 | 115 |
| 2026-09-01 | 0 | 26 | 117 |
| 2026-09-02 | 0 | 26 | 135 |
| 2026-09-03 | 0 | 25 | 122 |
| 2026-09-04 | 0 | 26 | 136 |
| 2026-09-05 | 0 | 32 | 229 |
| 2026-09-06 | 0 | 26 | 123 |
| 2026-09-07 | 0 | 26 | 129 |
| 2026-09-08 | 0 | 26 | 125 |
| 2026-09-09 | 0 | 26 | 134 |
| 2026-09-10 | 1 | 27 | 146 |
| 2026-09-11 | 0 | 26 | 144 |
| 2026-09-12 | 0 | 28 | 163 |
| 2026-09-13 | 0 | 26 | 145 |
| 2026-09-14 | 0 | 28 | 327 |
| 2026-09-15 | 2 | 28 | 124 |
| 2026-09-16 | 0 | 27 | 165 |
| 2026-09-17 | 0 | 26 | 146 |
| 2026-09-18 | 1 | 27 | 191 |
| 2026-09-19 | 0 | 27 | 136 |
| 2026-09-20 | 0 | 26 | 137 |
| 2026-09-21 | 0 | 27 | 174 |
| 2026-09-22 | 0 | 26 | 131 |
| 2026-09-23 | 0 | 25 | 133 |
| 2026-09-24 | 0 | 1 | 187 |

## Our ingestion assessment

**Model-written ingestion assessment**

The NIST News RSS feed has delivered only 1 item over the 14-day measurement window, representing a publication rate of 0.07 per day. The feed itself responds reliably—of 347 requests to www.nist.gov, only 1 returned no content (0.3% error rate). Our ingestion is currently in feed-fallback mode, meaning article pages from www.nist.gov are not being extracted; we are capturing the feed's teaser summaries instead. The single observed item in this period contained 188 characters. Publication from this source has been sparse, with no items observed for 10 days prior to the most recent item on 2026-09-10. The registry documents approximately 24 topical feeds and 4 blogs published by NIST beyond this general news feed.

_Model-written assessment of our own ingestion, generated 2026-09-11 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

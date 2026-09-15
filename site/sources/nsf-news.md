<!-- Markdown twin of https://fapd.info/sources/nsf-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nsf-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nsf-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NSF News

planned · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.nsf.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The National Science Foundation funds basic research across science and engineering. Its news index carries agency announcements on funding programs, research findings, and facilities, typically a few items per week.

**Model-written orientation**

The National Science Foundation funds basic research in science and engineering across the United States and publishes announcements on funding opportunities and research discoveries.

The National Science Foundation (NSF) is an independent agency that supports basic scientific research and science education across all fields of science and engineering except medicine. Established in 1950, NSF's mission is to promote the progress of science, advance national health and prosperity, and secure the national defense through research and education. The agency distributes billions of dollars annually in federal research funding to universities, research institutions, and individual investigators throughout the nation.

NSF operates through directorates covering distinct scientific domains: Biological Sciences, Computer and Information Science and Engineering, Engineering, Geosciences, Mathematical and Physical Sciences, and Social, Behavioral, and Economic Sciences. It also manages large research facilities—telescopes, supercomputers, research vessels, and observatories—that serve the broader scientific community. NSF funding supports fundamental research, graduate education, and undergraduate training, and the agency plays an important role in maintaining U.S. competitiveness in science and technology.

In this digest, you will see NSF announcements of new funding solicitations and programs, awards to major research institutions or research centers, significant research findings from NSF-supported projects, updates on facility operations or upgrades, and statements on agency initiatives. The releases span the full breadth of NSF's scientific portfolio, from biology and physics to computer science and social science. NSF's public releases serve researchers seeking funding opportunities, institutions managing research programs, and the general public interested in federally supported scientific advances.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nsf-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.nsf.gov/news |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 71 article link(s); 4 dated inside the 7-day lookback, 7 dated outside it, 60 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the feed-shaped link in the captured page (https://nsf.gov/rss) is an HTML directory of feeds, not a feed — verdict html-only. A specific feed URL may exist behind it; not pursued further this pass. Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | HTML index diff via AgencyClient (pending content evaluation) |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.nsf.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

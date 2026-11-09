<!-- Markdown twin of https://fapd.info/sources/cisa-advisories.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cisa-advisories.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cisa-advisories)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CISA Cybersecurity Advisories

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Department of Homeland Security (CISA)

Official site: https://www.cisa.gov/news-events/cybersecurity-advisories · All sources: [sources.md](../sources.md)

## What this source is

The Cybersecurity and Infrastructure Security Agency publishes cybersecurity advisories, alerts, and the Known Exploited Vulnerabilities (KEV) catalog — federal directives and warnings that constitute an action category the pipeline does not cover at all.

**Model-written orientation**

The Cybersecurity and Infrastructure Security Agency publishes cybersecurity advisories, alerts, and known exploited vulnerabilities that inform federal and public security practices.

The Cybersecurity and Infrastructure Security Agency (CISA), part of the Department of Homeland Security, is the federal government's civilian cybersecurity authority. CISA publishes official advisories and alerts on cybersecurity threats and vulnerabilities, serving as actionable guidance for federal agencies, critical infrastructure operators, and the broader public.

CISA advisories address specific cybersecurity vulnerabilities and threats: detailed technical information on security flaws in software and systems, recommendations for remediation, and guidance on defensive practices. Advisories may accompany warnings about active exploitation of particular vulnerabilities or newly discovered threats.

The Known Exploited Vulnerabilities (KEV) catalog is CISA's authoritative list of security flaws that have been observed in active use by malicious actors. This catalog serves as a reference for organizations prioritizing remediation efforts—CISA has issued guidance that federal agencies address vulnerabilities on this list by specified deadlines.

These publications represent a category of federal action not covered by other sources in the digest: direct security guidance and threat notification. Unlike analysis or commentary, CISA advisories are technical directives intended to inform security decisions across the government and critical infrastructure.

For readers concerned with cybersecurity policy, federal security posture, and threat awareness, CISA advisories represent the government's official guidance on current and emerging security challenges.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cisa-advisories` |
| Agency / parent organization | Department of Homeland Security (CISA) |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.cisa.gov/cybersecurity-advisories/all.xml |
| URL (home) | https://www.cisa.gov/news-events/cybersecurity-advisories |
| URL (index) | https://www.cisa.gov/known-exploited-vulnerabilities-catalog |
| Registered | 2026-07-28 |
| Registry notes | Research flagged the 2025-05 RSS retirement announcement, but the probe (2026-07-28) found all.xml alive and rich: HTTP 200, 2.0 MB feed, 30 recent advisories whose descriptions embed the full advisory text (~55,000 chars each); sample advisory page also extracts (9,317 chars). Content evaluation: descriptions carry the substance — article fetches add layout, not content — but pages fetch cleanly, so full mode is kept for capture/provenance value. First ingest brings ~30 substantial items. Activated 2026-07-28. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the advisories RSS feed via AgencyClient; KEV JSON is a later extension. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 15 item(s) in the last 14 days; most recent 2026-11-06; 30 of 346 request(s) to www.cisa.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-09T04:48:02Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 15 in 14 days (1.07 per day) · most recent 2026-11-06 |
| Content length | 30,436 characters average, 4,752 median (shortest 4,403, longest 352,794) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.cisa.gov | 346 request(s) · 316 answered · 30 declined (4xx) · 0 server declined (5xx) · 0 no response — 8.7% returned no content |

last answered request 2026-11-09T05:00:17.816+00:00 UTC.

15 item(s) in the last 14 days; most recent 2026-11-06; 30 of 346 request(s) to www.cisa.gov returned no content.

### All time

- **Our requests to www.cisa.gov, all time (since 2026-07-30):** 2,941 request(s) · 2,907 answered · 34 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.cisa.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-10-11 | 0 | 26 | 130 |
| 2026-10-12 | 0 | 25 | 140 |
| 2026-10-13 | 4 | 29 | 112 |
| 2026-10-14 | 1 | 26 | 139 |
| 2026-10-15 | 6 | 31 | 124 |
| 2026-10-16 | 4 | 30 | 115 |
| 2026-10-17 | 0 | 25 | 128 |
| 2026-10-18 | 0 | 25 | 148 |
| 2026-10-19 | 0 | 25 | 109 |
| 2026-10-20 | 7 | 31 | 82 |
| 2026-10-21 | 1 | 27 | 129 |
| 2026-10-22 | 20 | 45 | 86 |
| 2026-10-23 | 2 | 27 | 110 |
| 2026-10-24 | 0 | 25 | 118 |
| 2026-10-25 | 0 | 25 | 137 |
| 2026-10-26 | 1 | 26 | 121 |
| 2026-10-27 | 3 | 29 | 138 |
| 2026-10-28 | 1 | 26 | 204 |
| 2026-10-29 | 4 | 28 | 119 |
| 2026-10-30 | 1 | 28 | 152 |
| 2026-10-31 | 0 | 25 | 189 |
| 2026-11-01 | 0 | 25 | 150 |
| 2026-11-02 | 0 | 25 | 156 |
| 2026-11-03 | 2 | 28 | 130 |
| 2026-11-04 | 0 | 26 | 124 |
| 2026-11-05 | 3 | 29 | 139 |
| 2026-11-06 | 1 | 26 | 123 |
| 2026-11-07 | 0 | 25 | 150 |
| 2026-11-08 | 0 | 25 | 165 |
| 2026-11-09 | 0 | 1 | 552 |

## Our ingestion assessment

**Model-written ingestion assessment**

Our ingestion of CISA cybersecurity advisories runs through the all.xml RSS feed, with full article text fetched from each item's own page (delivery mode full). The registry notes record that a 2026-07-28 probe found the feed live and that its descriptions carry the advisory text. Over 14 days we recorded 14 items, or 1.0 per day, with the most recent on 2026-11-03; daily detail shows one item on 2026-10-30 and two on 2026-11-03. Item text has a median of 4,538 characters, a minimum of 4,399 and a maximum of 352,794. Of 344 requests, 13 returned no content (3.8 percent). Twelve of these fell on 2026-11-04, from 13:00 UTC onward, out of 26 requests that day, and one fell at 00:00 on 2026-11-05. Compared with the previous assessment, which recorded 27 items at 1.93 per day and 361 requests with a 1.0 percent no-response rate, the item rate is lower and the request failure rate is higher in this window.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

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

**delivering** — 32 item(s) in the last 14 days; most recent 2026-10-06; 0 of 368 request(s) to www.cisa.gov returned no content.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 32 request(s) (32 answered, 0 returned no content) · 6 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 32 in 14 days (2.29 per day) · most recent 2026-10-06 |
| Content length | 9,771 characters average, 8,990 median (shortest 4,389, longest 23,805) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.cisa.gov | 368 request(s) · 368 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-07T04:00:55.888+00:00 UTC.

32 item(s) in the last 14 days; most recent 2026-10-06; 0 of 368 request(s) to www.cisa.gov returned no content.

### All time

- **Our requests to www.cisa.gov, all time (since 2026-07-30):** 2,041 request(s) · 2,037 answered · 4 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.cisa.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-08 | 3 | 28 | 150 |
| 2026-09-09 | 1 | 26 | 142 |
| 2026-09-10 | 5 | 31 | 113 |
| 2026-09-11 | 2 | 26 | 126 |
| 2026-09-12 | 0 | 28 | 230 |
| 2026-09-13 | 0 | 25 | 182 |
| 2026-09-14 | 1 | 29 | 338 |
| 2026-09-15 | 9 | 35 | 107 |
| 2026-09-16 | 3 | 28 | 135 |
| 2026-09-17 | 7 | 32 | 105 |
| 2026-09-18 | 2 | 27 | 199 |
| 2026-09-19 | 0 | 25 | 162 |
| 2026-09-20 | 0 | 25 | 152 |
| 2026-09-21 | 1 | 29 | 224 |
| 2026-09-22 | 10 | 35 | 105 |
| 2026-09-23 | 1 | 25 | 128 |
| 2026-09-24 | 3 | 28 | 193 |
| 2026-09-25 | 2 | 28 | 166 |
| 2026-09-26 | 0 | 26 | 237 |
| 2026-09-27 | 2 | 28 | 172 |
| 2026-09-28 | 0 | 25 | 220 |
| 2026-09-29 | 8 | 34 | 105 |
| 2026-09-30 | 1 | 25 | 185 |
| 2026-10-01 | 8 | 35 | 107 |
| 2026-10-02 | 1 | 27 | 134 |
| 2026-10-03 | 0 | 26 | 128 |
| 2026-10-04 | 1 | 26 | 122 |
| 2026-10-05 | 0 | 27 | 139 |
| 2026-10-06 | 6 | 32 | 110 |
| 2026-10-07 | 0 | 1 | 108 |

## Our ingestion assessment

**Model-written ingestion assessment**

The cybersecurity-advisories feed delivered 27 items over 14 days at 1.93 per day, a decline from the prior 2.86 per day. Each item averages 9,480 characters of extracted text, with descriptions ranging up to 23,805 characters. All 361 requests succeeded, an improvement from the prior 1.0% no-response rate. Article page fetches are performed to capture layout and formatting; the feed's embedded full-text descriptions already carry the substance of each advisory.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/uscis-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/uscis-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: uscis-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USCIS Newsroom

planned · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.uscis.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

U.S. Citizenship and Immigration Services, within DHS, adjudicates immigration benefits. Its newsroom index carries news releases and alerts on benefits processing, fees, and policy updates, typically a few items per week.

**Model-written orientation**

U.S. Citizenship and Immigration Services (USCIS), within the Department of Homeland Security, adjudicates immigration benefit applications. Its newsroom publishes releases and alerts about immigration processing, fees, and policy.

U.S. Citizenship and Immigration Services is the Department of Homeland Security agency that reviews and makes decisions on immigration benefit petitions and applications. USCIS processes applications for lawful permanent residency, citizenship naturalization, employment authorization, work visas, refugee and asylee status designations, special immigrant categories, and other immigration benefits. The agency maintains immigration records, issues immigration documents and identification, and manages benefit applicant services.

The USCIS newsroom publishes official announcements about agency operations, policy changes, procedural updates, and service notices. Typical releases address application processing procedures and timelines; fee adjustments and payment policy; employment authorization and employment-based visa processing; citizenship and naturalization procedures; refugee and asylee processing and resettlement; visa categories and eligibility; new forms, online systems, or application procedures; and operational notices or service alerts.

In this digest, you will find USCIS announcements about application fee changes; updates to processing times or procedures; new forms or online systems for filing applications; changes to employment authorization or work-visa policy; refugee and asylee program updates; changes to visa categories or eligibility requirements; and alerts about office operations or service changes affecting benefit applicants.

USCIS newsroom releases are factual statements about the agency's immigration benefit operations. The announcements explain how the benefit system works and communicate procedural changes directly to applicants. Publications emerge at a rate of a few items per week. The newsroom serves as USCIS's primary channel for communicating with immigration benefit applicants and the public about how to navigate the immigration benefit system.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `uscis-newsroom` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.uscis.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Email sibling registered 2026-07-29: uscis-email (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 85 article link(s); 2 dated inside the 7-day lookback, 0 dated outside it, 83 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

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

No requests to www.uscis.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

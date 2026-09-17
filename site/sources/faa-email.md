<!-- Markdown twin of https://fapd.info/sources/faa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/faa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: faa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FAA Updates (email)

planned · Executive · Tier 2 · email bulletin · Department of Transportation (FAA)

Official site: https://www.faa.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Federal Aviation Administration regulates civil aviation and operates the national airspace system. Its bulletins carry press releases, airworthiness and regulatory notices, and safety announcements affecting operators, manufacturers, and travelers.

**Model-written orientation**

The Federal Aviation Administration regulates civil aviation and operates the national airspace system. Its subscription bulletins carry press releases, airworthiness directives, and safety announcements affecting aircraft operators and manufacturers.

The Federal Aviation Administration (FAA) is a bureau of the Department of Transportation responsible for regulating civil aviation and managing the national airspace system. The FAA has regulatory authority over aircraft design and manufacture, aircraft operators (airlines and private pilots), and airports. The agency also operates the air traffic control system and sets standards for aviation safety and security.

In its regulatory capacity, the FAA issues airworthiness directives (mandatory actions for aircraft and aircraft components to address safety defects), certifies aircraft designs before they may be manufactured, and certifies pilots, mechanics, and air-traffic controllers. It investigates aviation accidents and incidents and issues safety recommendations to manufacturers and operators based on those investigations. The agency also conducts safety oversight of the space-launch industry.

In its operational capacity, the FAA runs the air traffic control system, staffing air-traffic control facilities nationwide and setting procedures for aircraft separation and movement in U.S. airspace. The agency also coordinates with international aviation authorities and sets policies affecting U.S. aviation internationally.

The FAA distributes a subscription bulletin service to which this project subscribes. The bulletins report on regulatory actions (airworthiness directives, new certifications, enforcement actions), accident investigation findings and safety recommendations, policy announcements, and notices to airmen (NOTAMs) of particular importance. The content serves operators, manufacturers, pilots, and the aviation industry generally.

Readers will see a mix of regulatory notices, safety alerts, investigation findings, and operational announcements, reflecting the FAA's role in both regulating and operating aviation infrastructure.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `faa-email` |
| Agency / parent organization | Department of Transportation (FAA) |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.faa.gov/newsroom |
| URL (signup) | https://public.govdelivery.com/accounts/USAFAA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of faa-newsroom, which returns HTTP 403 to our identified client — the first working input for this agency. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-19 | 0 |
| 2026-08-20 | 6 |
| 2026-08-21 | 1 |
| 2026-08-22 | 0 |
| 2026-08-23 | 5 |
| 2026-08-24 | 0 |
| 2026-08-25 | 0 |
| 2026-08-26 | 0 |
| 2026-08-27 | 1 |
| 2026-08-28 | 2 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 5 |
| 2026-09-01 | 4 |
| 2026-09-02 | 0 |
| 2026-09-03 | 3 |
| 2026-09-04 | 3 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 1 |
| 2026-09-09 | 2 |
| 2026-09-10 | 0 |
| 2026-09-11 | 1 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 2 |
| 2026-09-15 | 3 |
| 2026-09-16 | 1 |
| 2026-09-17 | 0 |

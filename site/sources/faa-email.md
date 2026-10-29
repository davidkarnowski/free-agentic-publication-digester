<!-- Markdown twin of https://fapd.info/sources/faa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/faa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: faa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FAA Updates (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Transportation (FAA)

Official site: https://www.faa.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Federal Aviation Administration regulates civil aviation and operates the national airspace system. Its bulletins carry press releases, airworthiness and regulatory notices, and safety announcements affecting operators, manufacturers, and travelers.

**Model-written orientation**

The FAA's bulletin service delivers press releases, airworthiness and safety notices, and regulatory announcements to aviation stakeholders via email.

The Federal Aviation Administration is the federal agency within the Department of Transportation that regulates civil aviation, issues airworthiness certificates, certifies pilots and mechanics, and operates the National Airspace System. The FAA's mission is to ensure safe and efficient aviation operations in the United States.

The FAA publishes a subscription bulletin service via GovDelivery that delivers regulatory and safety announcements to subscribers. The FAA's email subscribers include airlines, aircraft manufacturers, airport operators, pilots, maintenance facilities, and other aviation professionals who need timely notification of regulatory changes and safety guidance.

Readers will see from this source email bulletins containing FAA press releases, notices of new or amended regulations, airworthiness directives (mandatory maintenance or modifications to aircraft), advisory circulars providing guidance to the aviation industry, safety alerts, event announcements, and notifications of changes to procedures or systems. The bulletins are typically official notices with direct operational impact on aviation operations, maintenance, or certification.

The FAA publishes these bulletins at regular intervals to reach subscribers with time-critical information. Volume varies depending on regulatory activity and safety priorities. Bulletins are dated at the time the FAA sends them.

The digest receives this source through an email subscription to the FAA's GovDelivery service. Bulletins are captured as full email text and authenticated via DKIM signature verification to ensure they originate from the FAA's authorized email sender. Bulletins are ingested starting from the date of subscription; earlier bulletins in the mailbox are not backfilled. The specific topics and notice types included in the bulletin stream depend on subscription settings selected at signup. A web copy of a bulletin, where available, may be cited alongside the archived email.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `faa-email` |
| Agency / parent organization | Department of Transportation (FAA) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.faa.gov/newsroom |
| URL (signup) | https://public.govdelivery.com/accounts/USAFAA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of faa-newsroom, which returns HTTP 403 to our identified client — the first working input for this agency. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. Gate-3 coverage evaluation (2026-09-28, from live delivery): 81 items from 2026-08-05 to 2026-09-28, every one DKIM-verified with the key archived and signed by info.dot.gov, which aligns with the sender's domain. The stream is mostly FAA Orders and Notices and Advisory Circulars update notifications, plus event notices; 11 of the 81 items link to a web copy, the rest cite the archived message. The topic selection made at signup was not recorded, so no coverage relationship to the FAA's full output is claimed: the bulletin stream is the measure. The only working channel for the FAA while faa-newsroom refuses our identified client. ACTIVATED 2026-09-28. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Poll cadence | the project mailbox is read about every 15 minutes |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 17 item(s) in the last 14 days; most recent 2026-10-27, delivered by email.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-10-29T03:48:33Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 17 in 14 days (1.21 per day) · most recent 2026-10-27 |
| Content length | 345 characters average, 171 median (shortest 67, longest 2,046) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 22 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-28 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

17 item(s) in the last 14 days; most recent 2026-10-27, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-30 | 4 |
| 2026-10-01 | 4 |
| 2026-10-02 | 3 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 11 |
| 2026-10-06 | 0 |
| 2026-10-07 | 3 |
| 2026-10-08 | 3 |
| 2026-10-09 | 3 |
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 2 |
| 2026-10-14 | 2 |
| 2026-10-15 | 3 |
| 2026-10-16 | 1 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 1 |
| 2026-10-20 | 0 |
| 2026-10-21 | 3 |
| 2026-10-22 | 1 |
| 2026-10-23 | 6 |
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 2 |
| 2026-10-27 | 3 |
| 2026-10-28 | 0 |
| 2026-10-29 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

We receive FAA Updates through the email adapter from the sender usafaa@info.dot.gov, with the subscription confirmed 2026-07-29 and the entry activated 2026-09-28. Bulletins carry full item text in the message, and each message is DKIM-verified and archived. The registry notes a coverage review of live delivery from 2026-08-05 to 2026-09-28 that found 81 items, all DKIM-verified; 11 linked to a web copy and the rest cite the archived message. The topic selection made at signup was not recorded, so we make no claim about coverage of the agency's full output. Over the past 14 days we measured 20 items at 1.43 per day, the most recent dated 2026-10-27. Item text ranges from 67 to 2,046 characters, with a median of 140. The mailbox recorded 24 bulletins, no errors, and no refusals. The previous assessment, dated 2026-09-27, measured 13 bulletins at about 0.93 per day, the most recent dated 2026-09-24, with lengths from 121 to 664 characters and a median of 175.

_Model-written assessment of our own ingestion, generated 2026-10-28 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

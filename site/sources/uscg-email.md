<!-- Markdown twin of https://fapd.info/sources/uscg-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/uscg-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: uscg-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Coast Guard News (email)

planned · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Homeland Security (U.S. Coast Guard)

Official site: https://www.news.uscg.mil/ · All sources: [sources.md](../sources.md)

## What this source is

The United States Coast Guard conducts maritime search and rescue, law enforcement, and marine safety and environmental response. Its bulletins carry operational announcements, safety alerts, and marine-casualty and enforcement news.

**Model-written orientation**

The United States Coast Guard distributes operational announcements, safety alerts, and maritime-casualty news by email subscription.

The United States Coast Guard, a component of the Department of Homeland Security, operates as the nation's maritime law-enforcement and safety agency. The Coast Guard conducts search and rescue operations at sea; enforces federal maritime laws and international maritime treaties; maintains aids to navigation; inspects commercial vessels and facilities; responds to marine pollution incidents; and conducts coastal and offshore security operations. The service operates a fleet of cutters, boats, and aircraft deployed at stations, sectors, and districts throughout U.S. coastal waters and the Great Lakes.

The Coast Guard's email bulletins carry operational announcements about significant Coast Guard activities, enforcement actions, and personnel developments. Safety alerts communicate maritime hazards to commercial mariners, recreational boaters, and the public—including weather hazards, navigation obstructions, facility closures, and safety procedures or requirements. The bulletins also report significant marine casualties such as vessel accidents, injuries, or environmental incidents; enforcement operations including boardings, arrests, or regulatory actions; and search and rescue activities. These communications inform stakeholders including maritime industry operators, state and local authorities, recreational boating organizations, and the general public about conditions affecting maritime operations and public safety.

The bulletins reflect the Coast Guard's operational tempo and mission across multiple areas of responsibility. Readers of this digest will encounter safety information relevant to maritime commerce and recreation, reports of enforcement and rescue activities, and operational updates from Coast Guard units and facilities throughout the United States. Content spans activities from coastal regions to offshore waters and includes announcements from all Coast Guard districts and field commanders. The email list serves as the service's official channel for communicating safety-critical information and operational developments to mariners and the public.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `uscg-email` |
| Agency / parent organization | Department of Homeland Security (U.S. Coast Guard) |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.news.uscg.mil/ |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of uscg-news, whose robots.txt disallows our client. A second consent-based path alongside the planned DVIDS API integration; content evaluation will determine which carries the fuller record. Signup URL not recorded: the address inferred from the sender was checked and did not resolve, so only the confirmed sender is asserted here. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-30, delivered by email.

This label has held since 2026-10-30T15:31:59Z (UTC) and was last re-checked 2026-10-31T03:45:15Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-30 |
| Content length | 8,597 characters average, 8,597 median (shortest 8,597, longest 8,597) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-30 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-30, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |
| 2026-10-08 | 0 |
| 2026-10-09 | 0 |
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 0 |
| 2026-10-14 | 0 |
| 2026-10-15 | 0 |
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 0 |
| 2026-10-20 | 0 |
| 2026-10-21 | 0 |
| 2026-10-22 | 0 |
| 2026-10-23 | 0 |
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 0 |
| 2026-10-27 | 0 |
| 2026-10-28 | 0 |
| 2026-10-29 | 0 |
| 2026-10-30 | 1 |
| 2026-10-31 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest Coast Guard News from GovDelivery bulletins that arrive by email from uscoastguard@service.govdelivery.com, with bulletins carrying the full item text. One bulletin is recorded in the current window, dated 2026-10-30 and measuring 8,597 characters, a rate of 0.07 per day, with health reading delivering. The mailbox shows one message and one bulletin, with no errors and no refused messages. The previous assessment recorded no messages and no items from this sender, so this bulletin is the first recorded in the measurements to date. The registry does not record a signup URL, because the address inferred from the sender did not resolve when checked. The registry status remains planned, and the subscription was confirmed 2026-07-29.

_Model-written assessment of our own ingestion, generated 2026-10-31 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

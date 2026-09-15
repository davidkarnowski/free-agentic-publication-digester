<!-- Markdown twin of https://fapd.info/sources/uscg-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/uscg-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: uscg-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Coast Guard News (email)

planned · Executive · Tier 2 · email bulletin · Department of Homeland Security (U.S. Coast Guard)

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

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

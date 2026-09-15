<!-- Markdown twin of https://fapd.info/sources/epa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/epa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: epa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# EPA News Releases (email)

planned · Executive · Tier 1 · email bulletin · Environmental Protection Agency

Official site: https://www.epa.gov/newsreleases · All sources: [sources.md](../sources.md)

## What this source is

The Environmental Protection Agency administers federal environmental law. Its bulletins carry news releases on enforcement settlements, permit and rule announcements, grant awards, and regional actions affecting specific communities.

**Model-written orientation**

The Environmental Protection Agency administers federal environmental law. Its subscription bulletins carry news releases on enforcement settlements, permit and rule announcements, grant awards, and regional actions.

The Environmental Protection Agency (EPA) is an independent federal agency responsible for implementing and enforcing federal environmental law. The EPA regulates air quality, water quality, hazardous waste, pesticides, toxic substances, and other environmental matters. The agency has both a headquarters office and ten regional offices covering different geographic areas of the country.

The EPA's regulatory functions include setting air and water quality standards, issuing permits for industrial facilities and water discharge, regulating waste disposal, and licensing pesticides and other chemical products. The agency also enforces environmental law through civil and criminal prosecution of violations, negotiating settlements for contamination and other environmental injuries, and requiring remediation of contaminated sites.

The EPA distributes a subscription bulletin service to which this project subscribes. The bulletins report on enforcement settlements (usually involving monetary penalties and required remediation), permit and rule announcements, grant awards to states for environmental programs, and actions by EPA regional offices. The content includes national announcements from EPA headquarters and regional announcements of local significance.

A typical bulletin may report that a manufacturing facility settled a Clean Air Act violation, that the EPA issued a final rule governing emissions from a particular industry, that the agency made a Superfund remediation decision at a contaminated site, or that a community was awarded a grant for a specific environmental project.

Readers will see a mix of regulatory actions and enforcement decisions, reflecting the EPA's role in environmental protection and compliance oversight.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `epa-email` |
| Agency / parent organization | Environmental Protection Agency |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.epa.gov/newsreleases |
| URL (signup) | https://www.epa.gov/newsroom/email-subscriptions-epa-headquarters-new-releases |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of epa-newsroom, whose web path robots.txt disallows — the first working input for this agency. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

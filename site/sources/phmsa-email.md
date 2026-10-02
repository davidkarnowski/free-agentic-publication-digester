<!-- Markdown twin of https://fapd.info/sources/phmsa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/phmsa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: phmsa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# PHMSA (email)

active · ingestion health: no data · Executive · Tier 2 · email bulletin · Department of Transportation (PHMSA)

Official site: https://www.phmsa.dot.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Pipeline and Hazardous Materials Safety Administration regulates the safe transport of hazardous materials and the nation's pipelines. Its bulletins carry safety advisories, rulemaking notices, and program announcements.

**Model-written orientation**

The Pipeline and Hazardous Materials Safety Administration publishes safety advisories and rulemaking notices for the transport of hazardous materials and pipeline operations.

The Pipeline and Hazardous Materials Safety Administration (PHMSA), part of the Department of Transportation, is the federal agency responsible for regulating the safe transportation of hazardous materials by all modes—highway, rail, air, and water—and for overseeing the nation's pipeline infrastructure for natural gas and hazardous liquids. PHMSA develops and enforces safety standards, conducts inspections and audits, investigates incidents, and administers training and certification programs for hazmat handlers. The agency's work spans regulating shippers and carriers of dangerous goods, pipeline operators, and manufacturers of hazmat containers and equipment. PHMSA's bulletins include safety advisories warning of hazards or unsafe conditions that have been identified, notices of proposed and final regulations affecting hazardous materials transport or pipeline operations, announcements of safety programs and compliance initiatives, and updates on incident investigations and lessons learned. Readers will see technical safety information and regulatory notices aimed at hazmat transporters and handlers, pipeline operators and maintenance professionals, safety managers at transportation and industrial companies, manufacturers and shippers, and regulatory compliance specialists. The announcements reflect PHMSA's dual responsibility for both the safe movement of substances that can cause injury or environmental damage and the safe operation of the nation's critical pipeline infrastructure. Safety failures in either area can have serious consequences for public safety, property, and the environment.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `phmsa-email` |
| Agency / parent organization | Department of Transportation (PHMSA) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.phmsa.dot.gov/news |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). The project mailbox received PHMSA bulletins over the changeover window (e.g. the 'Hazardous Matters' newsletter). Subscribed through DOT's own flow (sender [address withheld]); exact topic selection is in the operator's subscription records, not transcribed here. Sibling to the departmental transportation-email, whose web newsroom refuses our client; DKIM recorded per message at ingest. |

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-10-01T21:38:40Z (UTC) and was last re-checked 2026-10-02T03:48:29Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — none recorded in the lookback period |
| Mailbox | no message from this sender in the last 14 days |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

No bulletin recorded from this source in the last 180 days.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

## Our ingestion assessment

**Model-written ingestion assessment**

Subscription bulletins to the project mailbox, ingested by the email adapter with DKIM verification and alignment. Activated 2026-10-01 on observed delivery. The project mailbox received PHMSA bulletins during the changeover window (e.g., 'Hazardous Matters' newsletter) carrying safety advisories and program announcements. However, no items have yet been recorded as of 2026-10-02. The source is subscribed through DOT's GovDelivery flow (sender phmsa.subscriptions@info.dot.gov) in the active tier. It is a sibling to the departmental transportation-email source.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

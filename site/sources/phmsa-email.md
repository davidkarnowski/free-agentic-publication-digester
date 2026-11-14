<!-- Markdown twin of https://fapd.info/sources/phmsa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/phmsa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: phmsa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# PHMSA (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Transportation (PHMSA)

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-11-09, delivered by email.

This label has held since 2026-11-09T19:44:29Z (UTC) and was last re-checked 2026-11-14T04:53:49Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-11-09 |
| Content length | 1,306 characters average, 1,306 median (shortest 1,306, longest 1,306) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-11-09 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-11-09, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-10-30 | 0 |
| 2026-10-31 | 0 |
| 2026-11-01 | 0 |
| 2026-11-02 | 0 |
| 2026-11-03 | 0 |
| 2026-11-04 | 0 |
| 2026-11-05 | 0 |
| 2026-11-06 | 0 |
| 2026-11-07 | 0 |
| 2026-11-08 | 0 |
| 2026-11-09 | 1 |
| 2026-11-10 | 0 |
| 2026-11-11 | 0 |
| 2026-11-12 | 0 |
| 2026-11-13 | 0 |
| 2026-11-14 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

This source delivers full-text subscription bulletins from phmsa.subscriptions@info.dot.gov to the project mailbox, which are then ingested by the email adapter with DKIM verification and raw message capture. The source was activated on 2026-10-01. The previous assessment, dated 2026-10-16, noted two bulletins received since activation, with the most recent on 2026-10-07, and an average content length of 2,005 characters for those items. The current measurement shows one item received on 2026-11-09, with a content length of 1306 characters, making it the most recent item delivered. The mailbox has recorded one bulletin with zero errors or refusals, and the source's health status is "delivering." A sibling departmental web newsroom continues to refuse our client.

_Model-written assessment of our own ingestion, generated 2026-11-10 by gemini-2.5-flash, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

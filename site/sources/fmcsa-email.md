<!-- Markdown twin of https://fapd.info/sources/fmcsa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fmcsa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fmcsa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FMCSA (email)

active · ingestion health: no data · Executive · Tier 2 · email bulletin · Department of Transportation (FMCSA)

Official site: https://www.fmcsa.dot.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Federal Motor Carrier Safety Administration regulates commercial motor-vehicle safety. Its bulletins carry safety programs, rulemaking and enforcement announcements, and awareness campaigns.

**Model-written orientation**

The Federal Motor Carrier Safety Administration publishes safety programs, rulemaking notices, and compliance guidance for commercial motor-vehicle operations.

The Federal Motor Carrier Safety Administration (FMCSA), part of the Department of Transportation, is the federal agency responsible for regulating safety in the commercial motor-carrier industry. FMCSA sets and enforces safety standards for carriers operating commercial trucks and buses, establishes qualifications for drivers, sets rules for vehicle maintenance and inspection, and administers programs designed to reduce crashes and injuries. The agency oversees compliance through audits and safety reviews of carriers, licenses motor-carrier companies, administers the Commercial Driver License (CDL) program, and conducts safety research and analysis. FMCSA's bulletins include announcements of safety programs and enforcement initiatives, notices of proposed and final rulemaking that affect motor-carrier operations, guidance on compliance with federal safety regulations, and awareness campaigns on safety topics affecting the trucking and bus industries. Readers will encounter safety and regulatory information aimed at trucking and bus companies and their safety departments, professional drivers and driver-training programs, motor-carrier insurance and compliance specialists, and transportation industry associations. The announcements may cover topics such as hours of service rules that limit driver fatigue, vehicle inspection and maintenance requirements, driver qualification standards and medical certification, safety technology and vehicle equipment standards, or safety campaigns promoting practices such as commercial vehicle pre-trip inspections or drug and alcohol prevention in transportation. For the motor-carrier industry, these announcements represent regulatory requirements and best practices governing fleet operations.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fmcsa-email` |
| Agency / parent organization | Department of Transportation (FMCSA) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.fmcsa.dot.gov/newsroom |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). The project mailbox received an FMCSA bulletin during the changeover window (e.g. 'Celebrate the Pros During National Truck Driver Appreciation Week'); low volume observed so far, mixed program and awareness content. Subscribed through DOT's own flow (sender [address withheld]); exact topic selection is in the operator's subscription records, not transcribed here. DKIM recorded per message at ingest. |

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

This label has held since 2026-10-01T21:38:40Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter with DKIM verification and alignment. Activated 2026-10-01 on observed delivery. The project mailbox received an FMCSA bulletin during the changeover window (e.g., 'Celebrate the Pros During National Truck Driver Appreciation Week') carrying mixed program and awareness content. However, no items have yet been recorded as of 2026-10-02. The source is subscribed through DOT's GovDelivery flow (sender usdotfmcsa@info.dot.gov) in the active tier. Low volume has been observed in the early sample period.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

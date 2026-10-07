<!-- Markdown twin of https://fapd.info/sources/medicare-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/medicare-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: medicare-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Medicare (email)

active · ingestion health: no data · Executive · Tier 2 · email bulletin · Department of Health and Human Services (CMS)

Official site: https://www.cms.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Centers for Medicare & Medicaid Services administers Medicare. Its subscriber bulletins carry beneficiary-facing announcements — plan previews, enrollment periods, coverage changes, and program news — as CMS distributes them.

**Model-written orientation**

The Centers for Medicare & Medicaid Services publishes beneficiary-facing announcements about Medicare plans, enrollment periods, and coverage changes.

The Centers for Medicare & Medicaid Services (CMS), part of the Department of Health and Human Services, administers the Medicare program that provides health coverage to Americans age 65 and older and some younger people with disabilities or end-stage renal disease. Medicare is a major federal health insurance program serving tens of millions of beneficiaries through several program components: Original Medicare (Parts A and B), Medicare Advantage (Part C), and prescription drug coverage (Part D). CMS distributes subscriber bulletins with announcements and information relevant to Medicare beneficiaries and those considering Medicare enrollment. These bulletins include notifications about the annual enrollment period each fall when beneficiaries can change health plans and prescription drug coverage, previews of plan options for the coming year with details on premiums, deductibles, and covered services, notices of coverage changes or benefit updates that may affect current beneficiaries, and updates on Medicare programs and services. Readers will encounter straightforward, beneficiary-focused information about when enrollment periods occur, how to compare and select plans, what coverage options are available, and any changes to existing benefits or program rules. The content is designed for current Medicare beneficiaries seeking to stay informed about their options and any changes affecting their coverage, as well as those approaching eligibility for Medicare who are learning about the program. The announcements help beneficiaries make informed decisions about their health coverage and understand changes to the programs that provide their health insurance.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `medicare-email` |
| Agency / parent organization | Department of Health and Human Services (CMS) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.cms.gov/newsroom |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). The project mailbox received Medicare bulletins over the changeover window (e.g. 'Attention, preview 2027 plans now'). Subscribed through the publisher's own flow (sender [address withheld]); exact topic selection is in the operator's subscription records, not transcribed here. Content is beneficiary-facing program news; DKIM recorded per message at ingest. |

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

This label has held since 2026-10-01T21:38:40Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter with DKIM verification and alignment. Activated 2026-10-01 on observed delivery. The project mailbox received a Medicare bulletin during the changeover window (e.g., 'Attention, preview 2027 plans now') carrying beneficiary-facing program news. However, no items have yet been recorded in the system as of 2026-10-02. The source is subscribed through Medicare's GovDelivery flow (sender medicare@subscriptions.medicare.gov) in the active tier. Collector cycling shows no delivery events since activation.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

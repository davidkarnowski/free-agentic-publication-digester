<!-- Markdown twin of https://fapd.info/sources/fsis-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fsis-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fsis-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FSIS Recalls and Public Health Alerts (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Agriculture (FSIS)

Official site: https://www.fsis.usda.gov/recalls · All sources: [sources.md](../sources.md)

## What this source is

The Food Safety and Inspection Service inspects meat, poultry, and egg products. Its bulletins carry recall notices and public-health alerts naming specific products and establishments, a document class distinct from departmental press releases.

**Model-written orientation**

The Food Safety and Inspection Service distributes recall notices and public-health alerts for meat, poultry, and egg products by email subscription.

The Food Safety and Inspection Service (FSIS), located within the Department of Agriculture, holds statutory responsibility for the safety and labeling of meat, poultry, and egg products sold in the United States. The agency conducts continuous inspection at processing plants nationwide, establishes and enforces food-safety standards based on federal statute and regulations, investigates foodborne-illness outbreaks, and coordinates public-health responses with state and local authorities when safety concerns arise. FSIS maintains inspection offices in all states and operates a national network of laboratories for testing and analysis.

FSIS maintains a dedicated email subscription list for recall notices and public-health alerts—documents distinct from general departmental press releases. These bulletins identify specific products and establishments affected by food-safety issues and provide guidance for consumers, retailers, and food-service operators on appropriate response actions. Recalls may address contamination such as bacteria or foreign materials, mishandling or mislabeling, or other safety issues. Public-health alerts communicate investigation findings, testing results, and interim guidance when a potential hazard is identified. The bulletins provide product descriptions, establishment names and locations, distribution channels, and specific guidance on product identification and consumer actions such as disposal or return.

These bulletins represent urgent, product-specific safety communications issued when FSIS identifies a potential hazard or receives consumer complaints indicating a safety concern. They may affect products ranging from fresh meat and poultry to processed convenience foods and prepared meals sold across retail and food-service channels nationwide. Readers of this digest will see notifications about product recalls, epidemiological investigation findings, and public-health guidance issued by FSIS as safety matters arise, enabling consumers, retailers, and food-service operators to respond immediately to potential health risks. The bulletins provide the specific product information and establishment details necessary for targeted response.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fsis-email` |
| Agency / parent organization | Department of Agriculture (FSIS) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.fsis.usda.gov/recalls |
| URL (signup) | https://public.govdelivery.com/accounts/USFSIS/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Registered separately from agriculture-email because recalls are a distinct, time-critical document class rather than press material. Gate-3 coverage evaluation (2026-07-30, from the 2026-07-29 bulletins): 1 bulletin carried 1 recall/alert, full text, DKIM-verified, with its canonical fsis.usda.gov URL. The subscription is FSIS's own recall-and-alert distribution list — the channel the agency operates for exactly this document class; the public recalls page remains the visible cross-check. |

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

**delivering** — 10 item(s) in the last 14 days; most recent 2026-10-06, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 10 in 14 days (0.71 per day) · most recent 2026-10-06 |
| Content length | 1,736 characters average, 546 median (shortest 69, longest 8,931) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 6 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-06 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

10 item(s) in the last 14 days; most recent 2026-10-06, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-08 | 2 |
| 2026-09-09 | 6 |
| 2026-09-10 | 1 |
| 2026-09-11 | 3 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 3 |
| 2026-09-15 | 3 |
| 2026-09-16 | 2 |
| 2026-09-17 | 3 |
| 2026-09-18 | 3 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 3 |
| 2026-09-22 | 3 |
| 2026-09-23 | 1 |
| 2026-09-24 | 0 |
| 2026-09-25 | 4 |
| 2026-09-26 | 0 |
| 2026-09-27 | 0 |
| 2026-09-28 | 1 |
| 2026-09-29 | 2 |
| 2026-09-30 | 0 |
| 2026-10-01 | 0 |
| 2026-10-02 | 2 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 1 |
| 2026-10-07 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Food Safety and Inspection Service recall notices and public-health alerts arrive via email at 0.71 items per day over 14 days, a decrease from the 1.36 items per day observed in the prior assessment. We received 10 items with the most recent arriving 2026-10-02. The subscription represents the agency's own time-critical recall-and-alert distribution channel, a document class distinct from departmental press releases. Text ranged from 69 to 8,931 characters with a median of 493. The source has delivered consistently without consecutive failures, providing product identification and safety information.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

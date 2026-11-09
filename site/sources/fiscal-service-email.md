<!-- Markdown twin of https://fapd.info/sources/fiscal-service-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fiscal-service-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fiscal-service-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Bureau of the Fiscal Service (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of the Treasury, Bureau of the Fiscal Service

Official site: https://www.fiscal.treasury.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Bureau of the Fiscal Service manages federal payments, collections, borrowing, and government-wide accounting. Its media-relations mail carries the bureau's press releases.

**Model-written orientation**

The Bureau of the Fiscal Service manages federal payments, collections, borrowing, and government-wide accounting. Its press releases cover bureau operations and policy developments.

The Bureau of the Fiscal Service is a bureau within the Department of the Treasury responsible for managing the financial operations of the federal government. The bureau performs several distinct functions: it processes and distributes federal payments (wages, benefits, refunds, grants), collects federal revenue and manages accounts receivable, manages the federal government's borrowing and debt, maintains the government's accounting records, and operates the systems that support these functions.

As the government's payment processor, Fiscal Service processes hundreds of billions of dollars in payments annually through its primary payment systems. It manages the deposit account system that receives revenue, oversees financial agent banks that handle transactions, and operates the payment platform through which federal agencies submit payments. The bureau also manages the Treasury's investments of federal trust funds and maintains financial systems that support all federal agencies' accounting needs.

Fiscal Service manages the federal government's borrowing program, including the issuance of Treasury securities (bills, notes, and bonds) that fund federal operations and finance the national debt. The bureau maintains records of all outstanding Treasury securities and manages the auction process through which they are sold. It also oversees the government's cash management, including forecasting federal cash flows and managing the Treasury's account balances.

The bureau operates as a financial services provider to federal agencies, offering accounting services, payment processing, collections support, and financial reporting. It maintains compliance with federal financial management requirements and provides data to support government-wide financial reporting and budget processes.

When Fiscal Service appears in the digest, you will see press releases on treasury operations, announcements of treasury security auctions and results, updates on payment systems, financial management policy developments, accounting and reporting guidance, and notices affecting government financial operations. Announcements may be relevant to federal agencies, state and local governments receiving federal funds, financial institutions, and Treasury securities holders.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fiscal-service-email` |
| Agency / parent organization | Department of the Treasury, Bureau of the Fiscal Service |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.fiscal.treasury.gov/ |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: treasury-email, treasury-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 1 item(s) in the last 14 days; most recent 2026-11-02, delivered by email.

This label has held since 2026-11-02T16:44:39Z (UTC) and was last re-checked 2026-11-09T04:48:02Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-11-02 |
| Content length | 4,853 characters average, 4,853 median (shortest 4,853, longest 4,853) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-11-02 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-11-02, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-10-30 | 0 |
| 2026-10-31 | 0 |
| 2026-11-01 | 0 |
| 2026-11-02 | 1 |
| 2026-11-03 | 0 |
| 2026-11-04 | 0 |
| 2026-11-05 | 0 |
| 2026-11-06 | 0 |
| 2026-11-07 | 0 |
| 2026-11-08 | 0 |
| 2026-11-09 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest Bureau of the Fiscal Service media-relations bulletins through the email adapter. The sender is media-relations@fiscal.treasury.gov, and we keep raw RFC-5322 captures and verify DKIM. The subscription was confirmed through the publisher's signup flow and registered on 2026-09-26. The registry status is planned. Bulletins observed before registration were not backfilled. In the 14-day window measured on 2026-11-03, we recorded one bulletin, delivered 2026-11-02 at 16:43:48 UTC, carrying full item text at 4,853 characters. The mailbox recorded one message, with zero administrative messages, zero errors, and zero refused. No HTTP requests apply to this source, so health reads delivering from delivery recency alone. The gate-3 coverage evaluation is pending the first ingested bulletins. The registry lists treasury-email and treasury-newsroom as related entries that may publish the same news. A copy at the same URL merges as corroboration, and the same event at a different URL is listed separately. Since the previous assessment (2026-10-28), which recorded zero items and a no-data health reading with no bulletin in the last 180 days, the first bulletin has been ingested.

_Model-written assessment of our own ingestion, generated 2026-11-03 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

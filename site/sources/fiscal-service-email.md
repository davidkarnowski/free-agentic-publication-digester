<!-- Markdown twin of https://fapd.info/sources/fiscal-service-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fiscal-service-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fiscal-service-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Bureau of the Fiscal Service (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of the Treasury, Bureau of the Fiscal Service

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-10-01T03:53:55Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter. Registered 2026-09-26 with sender media-relations@fiscal.treasury.gov. The registry notes mail was observed in the project mailbox prior to registration but earlier bulletins are not backfilled. As of 2026-09-27, no bulletins from this source have been parsed and stored; the collector shows zero items. Status is planned, with gate-3 coverage evaluation pending the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

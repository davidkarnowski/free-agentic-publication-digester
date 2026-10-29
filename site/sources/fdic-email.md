<!-- Markdown twin of https://fapd.info/sources/fdic-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fdic-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fdic-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FDIC Press Releases (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Federal Deposit Insurance Corporation

Official site: https://www.fdic.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Federal Deposit Insurance Corporation insures bank deposits and supervises state-chartered banks. Its subscription bulletins carry press releases, financial institution letters, enforcement decisions, and failure and resolution announcements.

**Model-written orientation**

The Federal Deposit Insurance Corporation sends email bulletins on press releases, enforcement decisions, and announcements of bank failures and resolutions.

The Federal Deposit Insurance Corporation is an independent agency created in 1933 to maintain stability in the nation's banking system. The FDIC insures deposits at member banks—if an insured bank fails, depositors are protected up to the insurance limit per account—and supervises state-chartered banks that are not members of the Federal Reserve. The FDIC also manages the orderly resolution of failed banks, working to minimize disruption to customers and the financial system.

The FDIC email subscription delivers the agency's official bulletins and press releases. Readers receive announcements of significant supervisory actions: enforcement orders against institutions for safety-and-soundness violations or consumer-protection failures, guidance to banks on emerging regulatory issues or risk management, policy statements on examination standards or banking practices, and notifications of changes to insurance coverage rules. Most prominently, subscribers are notified immediately when a bank fails and the FDIC assumes its assets and liabilities, manages the orderly resolution, and protects insured depositors. Press releases cover actions the FDIC takes against institutions for unsafe practices, announcements of interagency guidance on financial risks or lending standards, and data releases on banking-system health. The stream also includes statements on consumer protections, identity theft, fraud prevention, and other matters affecting depositors and the public. The recipient base includes financial institutions, policymakers, the media, and members of the public interested in banking stability. Bank-failure announcements carry operational details: which FDIC-insured bank is closing, which institution will assume its operations (if any), and key dates for customer transition. Each bulletin reflects the FDIC's dual role as both supervisor of institutions and protector of depositor confidence in the banking system.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fdic-email` |
| Agency / parent organization | Federal Deposit Insurance Corporation |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.fdic.gov/news/press-releases |
| URL (signup) | https://www.fdic.gov/about/subscriptions/ |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of the planned fdic-news web entry, and it settles the open GovDelivery-topic-RSS question in favor of the email channel for this agency. Gate-3 coverage evaluation (2026-07-30, from live delivery): 1 bulletin -> 1 item on 2026-07-30 (agency release list). DKIM-verified with the key archived; the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Poll cadence | the project mailbox is read about every 15 minutes |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-26, delivered by email.

This label has held since 2026-10-26T16:09:20Z (UTC) and was last re-checked 2026-10-29T03:48:33Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-26 |
| Content length | 3,360 characters average, 3,360 median (shortest 3,360, longest 3,360) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-26 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-26, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-30 | 1 |
| 2026-10-01 | 0 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 2 |
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
| 2026-10-26 | 1 |
| 2026-10-27 | 0 |
| 2026-10-28 | 0 |
| 2026-10-29 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The fdic-email subscription, sender subscriptions@subscriptions.fdic.gov, has been confirmed since 2026-07-29 and is ingested by the email adapter as full-text bulletins, each DKIM-verified with the key archived. In the current 14-day window we recorded one item at 3,360 characters, most recently delivered 2026-10-26, a rate of 0.07 items per day. The mailbox shows one bulletin and one message, with zero errors and zero refused deliveries. The previous assessment, dated 2026-10-15, recorded two items at 0.14 per day, with content ranging from 1,128 to 1,622 characters, an average of 1,375, and a most recent delivery on 2026-10-05. Relative to that assessment, the item count in the window fell from two to one, the most recent delivery date moved to 2026-10-26, and the average extracted size rose from 1,375 to 3,360 characters. The collector reports no consecutive errors, with a last cycle at 2026-10-27T03:48:33Z. Registry notes record that same-URL copies from this channel and from fdic-news merge as corroboration.

_Model-written assessment of our own ingestion, generated 2026-10-27 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

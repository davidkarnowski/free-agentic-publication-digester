<!-- Markdown twin of https://fapd.info/sources/tigta-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/tigta-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: tigta-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Treasury Inspector General for Tax Administration (email)

active · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of the Treasury, Treasury Inspector General for Tax Administration

Official site: https://www.tigta.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Treasury Inspector General for Tax Administration audits and investigates the Internal Revenue Service. Its bulletins announce audit and inspection reports on IRS programs, payments, and enforcement.

**Model-written orientation**

The Treasury Inspector General for Tax Administration announces audit and inspection reports on IRS operations, programs, and effectiveness via email bulletin.

The Treasury Inspector General for Tax Administration is an independent office within the Department of the Treasury that audits and investigates the Internal Revenue Service. TIGTA's mission is to promote integrity, efficiency, and economy in IRS operations through audits and investigations. The office reports to Congress on IRS oversight matters and publishes reports on its findings.

TIGTA publishes a subscription bulletin service via GovDelivery that delivers announcements of recently completed audits and inspections to subscribers. The office's reports address IRS programs, tax enforcement, taxpayer services, information security, financial management, and operational efficiency. Subscribers include Congress, tax professionals, policy organizations, and others interested in IRS oversight.

Readers will see from this source email announcements of newly released TIGTA audit and inspection reports. Announcements typically include the title of the report, its subject matter, key findings, and recommendations. Audits may address specific IRS programs such as filing assistance, identity theft protection, or enforcement; operational systems; or government-wide tax compliance issues. The announcements direct readers to the full report, usually available through TIGTA's website or the Treasury Inspector General's Office of Inspector General portal.

TIGTA publishes audit announcements at regular intervals as reports are completed. The timing and volume depend on TIGTA's audit schedule and priorities. Bulletins are dated at the time the announcement is sent.

The digest receives this source through an email subscription to TIGTA's GovDelivery service. Bulletins are captured as full email text and authenticated via DKIM signature verification. The email is sent through GovDelivery's delivery platform, and DKIM signatures are archived by the digest. Bulletins are ingested starting from the date of subscription; earlier bulletins are not backfilled. Topic selections made at signup determine which audit announcements are delivered; the bulletin stream reflects the coverage of the particular subscription. A web copy of a report, where available, is cited within the bulletin.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `tigta-email` |
| Agency / parent organization | Department of the Treasury, Treasury Inspector General for Tax Administration |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.tigta.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USTREASTIGTA/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation (2026-09-28, from live delivery): 1 bulletin -> 1 item on 2026-09-28 (an announcement of two new audit reports). The bulletin carries no link to a web copy, so the item cites the archived message itself. DKIM-verified with the key archived; signed by service.govdelivery.com, the delivery platform's domain, not the agency's. The inbox rule labels and ingests such mail; the same message delivered to the junk folder would be refused (GUIDE §3, 2026-09-26). One bulletin is a thin sample, and the topic selection made at signup was not recorded, so this evaluation claims no coverage relationship to the agency's full output: the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector and shown on the source page. Related entries that can publish the same news: oversight-gov, treasury-email, treasury-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-20, delivered by email.

This label has held since 2026-10-20T14:18:15Z (UTC) and was last re-checked 2026-10-21T03:52:40Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-20 |
| Content length | 2,912 characters average, 2,912 median (shortest 2,912, longest 2,912) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-20 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-20, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-22 | 0 |
| 2026-09-23 | 0 |
| 2026-09-24 | 0 |
| 2026-09-25 | 0 |
| 2026-09-26 | 0 |
| 2026-09-27 | 0 |
| 2026-09-28 | 1 |
| 2026-09-29 | 0 |
| 2026-09-30 | 0 |
| 2026-10-01 | 0 |
| 2026-10-02 | 1 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
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
| 2026-10-20 | 1 |
| 2026-10-21 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The TIGTA email subscription via GovDelivery delivers bulletins with full text to the project mailbox, announcing audit and inspection reports. Over the past 14 days, 1 item arrived at a rate of 0.07 per day, containing 2,912 characters. The message, delivered 2026-10-20 at 14:16 UTC, was DKIM-verified with zero errors and zero rejected items. Bulletins cite archived messages without carrying external web links. Compared to the previous assessment from 2026-10-11, the ingestion pattern has changed: that measurement showed 2 items at 0.14 per day, averaging 5,513 characters (ranging 3,930 to 7,096), with the most recent from 2026-10-02. The current 14-day window beginning 2026-10-07 captures only 1 of those items; a new bulletin arrived on 2026-10-20. Email collection maintains stable operational status with zero errors.

_Model-written assessment of our own ingestion, generated 2026-10-21 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/tigta-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/tigta-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: tigta-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Treasury Inspector General for Tax Administration (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of the Treasury, Treasury Inspector General for Tax Administration

Official site: https://www.tigta.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Treasury Inspector General for Tax Administration audits and investigates the Internal Revenue Service. Its bulletins announce audit and inspection reports on IRS programs, payments, and enforcement.

**Model-written orientation**

The Treasury Inspector General for Tax Administration publishes bulletins announcing audit reports and investigations of Internal Revenue Service programs and operations.

The Treasury Inspector General for Tax Administration (TIGTA) is an independent audit and investigative office within the Department of the Treasury. TIGTA was established to provide oversight of the Internal Revenue Service and related tax administration functions. Unlike the IRS itself, which administers and collects taxes, TIGTA examines whether the IRS's operations, programs, and spending align with law and meet standards of efficiency and integrity.

TIGTA's email bulletins announce the release of audit reports, audit projects initiated, and investigative findings. Audit reports examine IRS programs related to tax collection, taxpayer service, enforcement, or internal operations—for example, reports on how the IRS manages a particular tax or compliance program, how it deploys its enforcement resources, or how it manages its IT systems. Investigative reports cover potential wrongdoing by IRS employees or third parties engaged in tax-related fraud or misconduct. TIGTA may also announce the start of new audit projects, signaling topics the office plans to examine.

The Treasury Inspector General's office is one of many independent inspectors general across the federal government, each assigned to provide oversight of their respective departments or agencies. This office's unique focus is tax administration and the IRS. Readers of this digest will see announcements of TIGTA's findings and work, providing visibility into independent oversight of the nation's tax administration.

It is important to understand that TIGTA reports on its findings and projects, while the IRS makes policy and operational decisions independently. A TIGTA audit report does not necessarily result in immediate changes; its value lies in examining and disclosing the IRS's operations to Congress, the public, and other stakeholders. Items appear in the digest as TIGTA releases them and do not include earlier TIGTA work or findings not yet published through the email channel.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `tigta-email` |
| Agency / parent organization | Department of the Treasury, Treasury Inspector General for Tax Administration |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.tigta.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USTREASTIGTA/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: oversight-gov, treasury-email, treasury-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-28T03:57:50Z (UTC).

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

Treasury Inspector General for Tax Administration audit announcements are delivered via email subscription confirmed 2026-09-26. No bulletins have been recorded in our ingestion logs as of the measurement period start; the subscription remains in planned status pending first ingestion cycle following registration.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

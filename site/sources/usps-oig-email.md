<!-- Markdown twin of https://fapd.info/sources/usps-oig-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usps-oig-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usps-oig-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USPS Inspector General (email)

active · ingestion health: delivering · Executive · Tier 3 · email bulletin · U.S. Postal Service Office of Inspector General

Official site: https://www.uspsoig.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Postal Service Office of Inspector General audits and investigates postal operations. Its bulletins carry audit reports, investigative findings, and white papers on postal finances, delivery performance, and program integrity.

**Model-written orientation**

The United States Postal Service Office of Inspector General publishes audit reports, investigative findings, and policy research through email bulletins. This digest includes items from the OIG's subscription release list.

The United States Postal Service Office of Inspector General is an independent office within the Postal Service created by statute to conduct audits and investigations of postal operations. The OIG operates independently from Postal Service management to provide oversight of the agency's finances, programs, and operations.

The OIG publishes audit reports examining postal programs and functions. These audits review how the Postal Service manages its delivery network, processes mail, manages personnel and labor relations, procures goods and services, manages information systems, and operates its financial controls. Audits may focus on operations at the national level, regional operations, or specific facilities and programs. Each report presents findings about program performance and compliance, identifies issues, and recommends corrective actions.

The OIG also publishes investigative reports on fraud and misconduct. These investigations examine allegations including employee misconduct, contractor fraud, mail theft, and other violations of law or policy within postal operations. Published investigation reports describe scope and findings.

The OIG publishes white papers and research reports analyzing postal finances, delivery performance, and program integrity issues. These materials provide evidence-based analysis of operational data and policy questions.

The email bulletins in this digest represent the OIG's official release list—a curated stream of completed audits, investigative findings, and research publications. The Postal Service is unique among federal agencies as the only independent agency with a statutory obligation to provide mail delivery service to every address in the United States. The OIG's audits and investigations provide insight into the operational and financial challenges of maintaining universal mail service. Readers interested in federal government audits, postal operations, or oversight of federal agencies will find substantive material here.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usps-oig-email` |
| Agency / parent organization | U.S. Postal Service Office of Inspector General |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.uspsoig.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USPSOIG/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]); a real audit-release bulletin arrived the same day. Overlaps the planned oversight.gov aggregator, which collects IG reports government-wide; the aggregator rule applies if both are activated. Gate-3 coverage evaluation (2026-07-30, from the 2026-07-29 bulletins): 1 bulletin carried 1 audit release, full text, DKIM-verified, with its canonical uspsoig.gov URL. The subscription is the OIG's own release list; its published output (audits, white papers) is low-volume and the bulletin stream matches the classes the site publishes. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Poll cadence | the project mailbox is read about every 15 minutes |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 23 item(s) in the last 14 days; most recent 2026-09-22, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-23T03:59:19Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 3 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 23 in 14 days (1.64 per day) · most recent 2026-09-22 |
| Content length | 1,205 characters average, 950 median (shortest 536, longest 3,052) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

23 item(s) in the last 14 days; most recent 2026-09-22, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-25 | 0 |
| 2026-08-26 | 7 |
| 2026-08-27 | 2 |
| 2026-08-28 | 2 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 0 |
| 2026-09-01 | 0 |
| 2026-09-02 | 0 |
| 2026-09-03 | 0 |
| 2026-09-04 | 1 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 1 |
| 2026-09-09 | 2 |
| 2026-09-10 | 6 |
| 2026-09-11 | 3 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 0 |
| 2026-09-15 | 0 |
| 2026-09-16 | 2 |
| 2026-09-17 | 3 |
| 2026-09-18 | 4 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 2 |
| 2026-09-22 | 3 |
| 2026-09-23 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The USPS OIG subscription (uspsoig@public.govdelivery.com) has delivered 12 items over 14 days, averaging 0.86 items per day. Bulletins arrive as full-text email to the project mailbox, ranging from 495 to 1,228 characters (average 807). Delivery has accelerated substantially since the previous assessment on 2026-08-05, which recorded 3 items at 0.21 per day. The source now delivers on a faster cadence, with the most recent item on 2026-09-04 and 1 item in the last 24 hours. The email adapter confirms DKIM verification and archival of all subscribed bulletins. No request metrics apply. The collector reports no consecutive errors and full operational status as of 2026-09-05.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

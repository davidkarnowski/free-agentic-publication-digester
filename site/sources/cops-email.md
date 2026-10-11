<!-- Markdown twin of https://fapd.info/sources/cops-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cops-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cops-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DOJ COPS Office (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Justice, Office of Community Oriented Policing Services

Official site: https://cops.usdoj.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of Community Oriented Policing Services funds and supports community policing. Its bulletins carry grant announcements, solicitations, and published standards and resources.

**Model-written orientation**

The DOJ COPS Office provides funding and support for community-oriented policing initiatives across the United States. Its emails carry grant announcements, solicitations, and published resources.

The Office of Community Oriented Policing Services (COPS) is a bureau within the Department of Justice dedicated to advancing community policing practices and providing federal funding to support police departments and tribal law enforcement agencies. Community policing emphasizes collaboration between law enforcement and communities to identify and solve public safety problems together. COPS operates as both a funding source and a knowledge center, distributing grants while also publishing research, best practices, training resources, and technical assistance materials.

COPS administers multiple grant programs designed to support police hiring, training, technology, and community engagement initiatives. These grants help departments hire new officers, implement community policing strategies, develop problem-solving approaches, acquire technology and equipment, and create community advisory boards and engagement programs. The office also funds research on policing practices and operates training academies and regional training centers.

Beyond grants, COPS publishes practical guidance documents, case studies, and evidence-based resources that police departments use to implement community policing strategies. The office maintains a library of training materials, toolkits, and published standards on topics ranging from procedural justice to community engagement to problem-solving frameworks. COPS also convenes law enforcement professionals through conferences, working groups, and collaborative networks.

When COPS appears in the digest, you will see grant solicitations with application deadlines, grant awards announcements, published standards and best-practice documents, training opportunity notices, research findings on policing practices, and updates on COPS initiatives and programs. Documents are relevant to law enforcement agencies, police chiefs, training institutions, and communities interested in police practices.

As a federal funding source, COPS announcements often have specific deadlines and eligibility requirements that vary by grant program, making them time-sensitive for agencies considering applications.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cops-email` |
| Agency / parent organization | Department of Justice, Office of Community Oriented Policing Services |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://cops.usdoj.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDOJCOPS/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: justice-email, justice-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-10, delivered by email.

This label has held since 2026-10-10T14:47:50Z (UTC) and was last re-checked 2026-10-11T03:57:56Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-10 |
| Content length | 417 characters average, 417 median (shortest 417, longest 417) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 2 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-10 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-10, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 0 |
| 2026-09-15 | 0 |
| 2026-09-16 | 0 |
| 2026-09-17 | 0 |
| 2026-09-18 | 0 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 0 |
| 2026-09-22 | 0 |
| 2026-09-23 | 0 |
| 2026-09-24 | 0 |
| 2026-09-25 | 0 |
| 2026-09-26 | 0 |
| 2026-09-27 | 0 |
| 2026-09-28 | 0 |
| 2026-09-29 | 0 |
| 2026-09-30 | 0 |
| 2026-10-01 | 0 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |
| 2026-10-08 | 0 |
| 2026-10-09 | 0 |
| 2026-10-10 | 1 |
| 2026-10-11 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Subscription bulletins via GovDelivery deliver grant announcements and resources to the project mailbox with full text. Status is 'planned.' Over 14 days, 1 item was ingested on 2026-10-10 at 417 characters. The mailbox received 2 messages total, with 1 parsed as a bulletin. Messages arrive from two sender addresses: copsdonotreply@service.govdelivery.com and copsusdoj@service.govdelivery.com. All messages are verified and error-free. The previous assessment noted zero bulletins after registration on 2026-09-26; this measurement shows the first ingested item. Gate-3 coverage evaluation is pending.

_Model-written assessment of our own ingestion, generated 2026-10-11 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

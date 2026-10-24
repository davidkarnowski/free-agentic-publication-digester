<!-- Markdown twin of https://fapd.info/sources/hhs-owh-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/hhs-owh-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: hhs-owh-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# HHS Office on Women's Health (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Health and Human Services, Office on Women's Health

Official site: https://womenshealth.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Office on Women's Health coordinates women's health policy within the Department of Health and Human Services. Its bulletins carry press releases and program announcements.

**Model-written orientation**

The HHS Office on Women's Health coordinates women's health policy and research across the Department of Health and Human Services. Its emails carry press releases and program announcements.

The Office on Women's Health (OWH) is a sub-agency within the Office of the Secretary of the Department of Health and Human Services. It coordinates federal efforts on women's health and reproductive health policy across the department and its agencies, bringing together research, program development, and public health initiatives. The office's work spans the full range of women's health topics, from maternal and infant health through menopause and aging, including reproductive health, chronic disease prevention, mental health, and health equity.

As a policy coordination office rather than a grant-making or regulatory agency, OWH functions as a central point for women's health issues within HHS. It convenes working groups across HHS agencies, supports research initiatives, develops evidence-based resources and toolkits for health professionals and the public, and tracks national health trends affecting women. The office also works to ensure that federal health programs and policies address women's health needs.

When OWH appears in the digest, you will see press releases announcing new research findings, program launches, resource releases, and federal health initiatives related to women's health. Documents may also include announcements of working group findings, federal policy positions on health topics, or the release of educational materials for clinicians and patients.

Because OWH operates as a coordinating office, its publications typically reflect policy developments, evidence syntheses, or program announcements from across HHS rather than new data collection or direct service provision. Readers seeking detailed scientific research on women's health may also find relevant material from the National Institutes of Health and the Centers for Disease Control and Prevention, which are separate agencies within HHS.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `hhs-owh-email` |
| Agency / parent organization | Department of Health and Human Services, Office on Women's Health |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://womenshealth.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USOPHSOWH/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-18, delivered by email.

This label has held since 2026-10-18T14:36:04Z (UTC) and was last re-checked 2026-10-24T03:42:48Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-18 |
| Content length | 153 characters average, 153 median (shortest 153, longest 153) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-18 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-18, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 0 |
| 2026-10-14 | 0 |
| 2026-10-15 | 0 |
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 1 |
| 2026-10-19 | 0 |
| 2026-10-20 | 0 |
| 2026-10-21 | 0 |
| 2026-10-22 | 0 |
| 2026-10-23 | 0 |
| 2026-10-24 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

GovDelivery subscription bulletins carrying press releases and program announcements have begun delivery to the project mailbox with full text. Subscription was confirmed 2026-09-26. One message arrived 2026-10-18 at 153 characters, DKIM-verified with zero errors or refusals. This represents the first observable ingestion from this source; the previous assessment dated 2026-09-27 reported zero bulletins since registration and deployment. Current health status indicates active delivery. The email collector operates without consecutive errors and last accessed the mailbox 2026-10-19.

_Model-written assessment of our own ingestion, generated 2026-10-19 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

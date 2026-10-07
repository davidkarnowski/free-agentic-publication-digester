<!-- Markdown twin of https://fapd.info/sources/nih-orwh-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nih-orwh-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nih-orwh-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NIH Office of Research on Women's Health (email)

active · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Health and Human Services (NIH / ORWH)

Official site: https://orwh.od.nih.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The NIH Office of Research on Women's Health coordinates women's-health research across the National Institutes of Health. Its bulletins carry research announcements, funding and data-standard news, and event invitations.

**Model-written orientation**

The National Institutes of Health Office of Research on Women's Health coordinates women's health research across NIH institutes and centers. Its email bulletins carry research announcements, funding opportunities, and event notifications.

The Office of Research on Women's Health (ORWH) operates within the National Institutes of Health, a component of the Department of Health and Human Services. ORWH coordinates research on women's health topics across the many institutes and centers that comprise NIH.

The National Institutes of Health is the primary federal research agency, supporting medical and health research across the United States. It comprises numerous institutes and centers, each focused on different disease areas, research domains, or research functions. ORWH serves as a coordinating body within this structure, working to advance women's health research across NIH's portfolio.

ORWH's email bulletins are distributed to researchers, healthcare professionals, and others interested in women's health research. These bulletins share research announcements and discoveries in women's health, funding opportunities and grant announcements, updates on data standards and research initiatives, and notifications about events, discussions, and webinars.

The range of content reflects ORWH's coordination role. Readers will see announcements about research advances in areas such as reproductive health, cardiovascular disease, cancer, mental health, and other areas relevant to women's health; notices of funding opportunities from various NIH institutes; and invitations to research discussions and professional meetings.

Note that ORWH's bulletins include a mix of content—alongside research and funding announcements, readers will encounter event and webinar invitations alongside substantive research and funding news.

In this digest, readers will encounter ORWH's official communications drawn from announcements that ORWH distributes to its email subscription audience, primarily research announcements, funding opportunities, and program information.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nih-orwh-email` |
| Agency / parent organization | Department of Health and Human Services (NIH / ORWH) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://orwh.od.nih.gov/ |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). Coverage caveat: a meaningful share of ORWH mail is event and webinar invitations (e.g. 'Developing Research Common Data Elements' discussion) alongside research and funding news — mixed signal, tier 3. Subscribed through NIH's own flow (sender [address withheld]); DKIM recorded per message at ingest. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-05, delivered by email.

This label has held since 2026-10-05T18:11:01Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-05 |
| Content length | 1,250 characters average, 1,250 median (shortest 1,250, longest 1,250) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-05 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-05, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-08 | 0 |
| 2026-09-09 | 0 |
| 2026-09-10 | 0 |
| 2026-09-11 | 0 |
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
| 2026-10-05 | 1 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

NIH's Office of Research on Women's Health subscription was activated on 2026-10-01 following observed delivery. It carries research announcements, funding news, and event invitations via email. One item has been recorded since activation, delivered on 2026-10-05 at 1,250 characters. The email adapter confirms DKIM verification and archival of messages received. No request-level statistics apply as this source delivers via email. The collector shows normal status with no consecutive errors.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

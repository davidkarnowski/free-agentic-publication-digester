<!-- Markdown twin of https://fapd.info/sources/irs-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/irs-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: irs-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# IRS Newswire (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of the Treasury (IRS)

Official site: https://www.irs.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Internal Revenue Service administers federal tax law. Its newswire bulletins carry filing-season guidance, revenue procedures and rulings as announced, tax-scam alerts, and enforcement announcements — the agency's primary channel for reaching taxpayers and practitioners quickly.

**Model-written orientation**

The IRS Newswire delivers agency guidance, revenue procedures and rulings, tax-scam alerts, and enforcement announcements via email bulletins to taxpayers and tax professionals.

The Internal Revenue Service, operating within the Department of the Treasury, administers the federal tax laws and enforces the Internal Revenue Code. The IRS collects federal income taxes from individuals and businesses, processes millions of tax returns annually, manages tax-exempt organizations, and conducts examinations and enforcement actions against taxpayers who violate the tax code. The IRS communicates with taxpayers, tax professionals, and the general public through multiple channels to provide guidance on tax obligations, explain policy changes and legal interpretations, warn about emerging scams, and announce enforcement actions.

The IRS Newswire subscription delivers the agency's announcements via email bulletins to tax professionals and subscribers. These bulletins carry filing-season guidance issued at the start of each tax year with updates on forms, deadlines, and procedures; revenue procedures and rulings that formally interpret the tax code for specific situations and provide guidance to taxpayers and practitioners; alerts about tax scams and fraudulent schemes targeting taxpayers and professionals; and announcements of enforcement actions and penalties. The newswire reaches tax professionals, accountants, enrolled agents, financial advisors, and taxpayers who rely on timely IRS communication to stay current with changing regulations, emerging threats, and administrative procedures.

Revenue procedures and rulings are formal policy interpretations issued by the IRS Chief Counsel's office and posted to the Federal Register; the newswire subscription provides an immediate notification channel that reaches subscribers on the day the agency issues guidance. This dual-channel approach ensures that both the formal regulatory process and rapid practitioner communication are served.

The subscription is confirmed and actively receiving bulletins. Each bulletin is captured and verified using standard email protocols, providing a direct record of the IRS's own announcements as they are distributed to subscribers.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `irs-email` |
| Agency / parent organization | Department of the Treasury (IRS) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.irs.gov/newsroom |
| URL (signup) | https://www.irs.gov/newsroom/e-news-subscriptions |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of the planned irs-newsroom web entry. Gate-3 coverage evaluation (2026-07-30, from live delivery): 1 bulletin -> 1 item on 2026-07-30 (the agency's own release list; first working input for IRS releases). DKIM-verified with the key archived; the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector. |

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

**delivering** — 13 item(s) in the last 14 days; most recent 2026-09-24, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-25T03:53:38Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 13 in 14 days (0.93 per day) · most recent 2026-09-24 |
| Content length | 608 characters average, 190 median (shortest 135, longest 2,839) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

13 item(s) in the last 14 days; most recent 2026-09-24, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-27 | 1 |
| 2026-08-28 | 2 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 0 |
| 2026-09-01 | 0 |
| 2026-09-02 | 1 |
| 2026-09-03 | 2 |
| 2026-09-04 | 3 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 2 |
| 2026-09-09 | 1 |
| 2026-09-10 | 2 |
| 2026-09-11 | 0 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 1 |
| 2026-09-15 | 2 |
| 2026-09-16 | 0 |
| 2026-09-17 | 2 |
| 2026-09-18 | 2 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 2 |
| 2026-09-22 | 2 |
| 2026-09-23 | 0 |
| 2026-09-24 | 2 |
| 2026-09-25 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The IRS newswire delivers bulletins to the project mailbox via GovDelivery subscription at 1.0 item per day over 14 days, a five-fold increase from the 0.21 items per day reported in the prior assessment. We received 14 items with the most recent arriving 2026-09-04. The bulletin stream carries full-text releases bearing irs.gov URLs; DKIM signature verification has been applied. This email subscription represents the first working input for IRS releases and is the department's primary distribution channel for announcements reaching practitioners and taxpayers. Bulletin content includes the agency's own parsed item list, providing a direct measure of delivery from this channel.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

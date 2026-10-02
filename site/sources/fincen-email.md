<!-- Markdown twin of https://fapd.info/sources/fincen-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fincen-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fincen-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FinCEN Updates (email)

planned · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of the Treasury (FinCEN)

Official site: https://www.fincen.gov/news-room · All sources: [sources.md](../sources.md)

## What this source is

The Financial Crimes Enforcement Network administers the Bank Secrecy Act and issues advisories, alerts, and enforcement actions on money laundering, sanctions evasion, and illicit finance. Its bulletins carry those advisories and enforcement announcements directly, a document class that reaches the Federal Register only in part.

**Model-written orientation**

The Financial Crimes Enforcement Network delivers advisories, alerts, and enforcement announcements via email bulletins, covering money laundering, sanctions evasion, and illicit finance enforcement.

The Financial Crimes Enforcement Network (FinCEN) is a bureau of the Department of the Treasury dedicated to combating financial crimes. FinCEN administers the Bank Secrecy Act, which requires financial institutions to report suspicious transactions and maintain records of certain customer transactions. The agency works with federal, state, and local law enforcement; foreign financial intelligence units; and the international financial system to detect, deter, and disrupt money laundering, sanctions evasion, terrorist financing, and other forms of illicit financial activity.

FinCEN issues multiple classes of guidance to the financial sector: advisories to financial institutions about emerging threats and suspicious patterns, alerts warning about specific schemes or suspicious activities, enforcement actions announcing civil penalties and administrative orders against violators, and policy guidance interpreting the Bank Secrecy Act and related regulations. Financial institutions, bank regulators, law enforcement agencies, and compliance professionals rely on FinCEN guidance and alerts to understand emerging financial crime threats and adjust their monitoring and reporting practices accordingly.

FinCEN distributes certain advisories and alerts through email subscription bulletins, a document class that reaches the Federal Register only in part. The subscription provides subscribers with direct notification of new guidance and enforcement announcements as they are issued, making the bulletin stream an important channel for tracking the agency's actions and policy guidance. The subscription was confirmed in 2026, and monitoring is active for the first published bulletins.

Once bulletins begin arriving, they will be captured and verified for authenticity using standard email protocols, with DKIM verification and archival of the original message format.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fincen-email` |
| Agency / parent organization | Department of the Treasury (FinCEN) |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.fincen.gov/news-room |
| URL (signup) | https://public.govdelivery.com/accounts/USFINCEN/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-10-01T17:51:05Z (UTC) and was last re-checked 2026-10-02T03:48:29Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-01 |
| Content length | 1,128 characters average, 1,128 median (shortest 1,128, longest 1,128) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-01 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-03 | 1 |
| 2026-09-04 | 1 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 2 |
| 2026-09-09 | 1 |
| 2026-09-10 | 1 |
| 2026-09-11 | 0 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 0 |
| 2026-09-15 | 0 |
| 2026-09-16 | 1 |
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
| 2026-10-01 | 1 |
| 2026-10-02 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The FinCEN Updates source delivers bulletins through email subscription. One bulletin was observed in the 14-day window, delivered on 2026-10-01, measuring 1,128 characters and carrying the full text of a financial crime advisory. The email adapter is functioning without errors. The source shows sparse activity with approximately 0.07 items per day. DKIM verification is applied on ingestion and the raw message capture is archived.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

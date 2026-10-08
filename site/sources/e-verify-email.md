<!-- Markdown twin of https://fapd.info/sources/e-verify-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/e-verify-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: e-verify-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# E-Verify (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Homeland Security, U.S. Citizenship and Immigration Services

Official site: https://www.e-verify.gov/ · All sources: [sources.md](../sources.md)

## What this source is

E-Verify is the USCIS program employers use to confirm employment eligibility. Its bulletins carry program updates, including changes to work-authorization documents such as Temporary Protected Status terminations.

**Model-written orientation**

E-Verify is a U.S. Citizenship and Immigration Services program that allows employers to confirm the employment eligibility of their employees. This email source carries bulletins about program updates and changes to work authorization requirements.

E-Verify is a program operated jointly by the U.S. Citizenship and Immigration Services (USCIS) and the Social Security Administration (SSA) that provides employers with an electronic means to confirm that employees are legally authorized to work in the United States. Employers use the system to verify information from Form I-9, the employment eligibility verification form, against federal databases maintained by SSA and USCIS.

The program operates through a web-based interface that allows employers to check employee eligibility information in real time or near-real time. While use is voluntary for most private-sector employers, federal contractors and federal agencies are required to use E-Verify. The program supports employers' compliance with employment eligibility verification requirements and provides the government with a tool for immigration enforcement by allowing verification of work authorization status.

Email bulletins from E-Verify notify subscribers about program updates, changes to the types of work authorization documents accepted for verification, changes to employment eligibility or immigration statuses, technical updates to the E-Verify system, procedural guidance for employers, and announcements of agency actions. Readers may see notifications about changes to temporary protected status designations or terminations, updates to the documents accepted for employment verification, notices of E-Verify system maintenance or enhancements, guidance documents for employers on compliance procedures, and announcements about document changes or eligibility category updates. The bulletins reflect the program's role in providing employers with accurate employment eligibility information and regulatory compliance tools.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `e-verify-email` |
| Agency / parent organization | Department of Homeland Security, U.S. Citizenship and Immigration Services |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.e-verify.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDHSCISEVERIFY/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: uscis-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 3 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-10-01T14:21:57Z (UTC) and was last re-checked 2026-10-08T03:55:12Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-01 |
| Content length | 1,415 characters average, 1,510 median (shortest 1,194, longest 1,541) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 3 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-01 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

3 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-10-01 | 3 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |
| 2026-10-08 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The E-Verify subscription was registered on 2026-09-26 via GovDelivery. Three bulletins were observed in the 14-day measurement window, all delivered on 2026-10-01 across three separate hours, ranging from 1,194 to 1,541 characters. The email adapter is functioning without errors. This represents the first ingested bulletins from this source since registration. Multiple program updates were announced in succession on that date. Earlier bulletins present in the mailbox before registration were not backfilled.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

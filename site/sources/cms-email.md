<!-- Markdown twin of https://fapd.info/sources/cms-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cms-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cms-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CMS Newsroom (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Health and Human Services (CMS)

Official site: https://www.cms.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Centers for Medicare and Medicaid Services administer Medicare, Medicaid, and the health-insurance marketplaces. Its bulletins carry payment-rule announcements, coverage decisions, program guidance to states and providers, and enrollment data.

**Model-written orientation**

CMS distributes payment-rule announcements, coverage decisions, guidance, and enrollment data affecting Medicare, Medicaid, and health-insurance marketplaces.

The Centers for Medicare and Medicaid Services (CMS), part of the Department of Health and Human Services, administers Medicare—the federal health-insurance program for seniors aged 65 and older and certain disabled individuals; Medicaid—the joint federal-state program providing health coverage to low-income individuals and families; and the health-insurance marketplaces established under federal law. CMS operates nationwide with regional offices and maintains substantial data systems for enrollment, claims processing, and program analytics. The agency also oversees quality reporting and performance measurement for providers participating in its programs.

CMS email bulletins communicate changes to Medicare and Medicaid payment rates and rules that determine reimbursement to hospitals, physicians, and other healthcare providers for medical services. Coverage decisions establish which treatments, procedures, and technologies are paid for under Medicare and Medicaid, directly affecting what care beneficiaries can access and what providers can deliver. Payment announcements communicate annual updates to physician fee schedules, hospital payment rates, and skilled-nursing facility rates—changes affecting provider revenue and operational planning. Medicaid guidance addresses eligibility rules, enrollment procedures, and program requirements to state Medicaid agencies, enabling states to administer their programs consistently with federal law. Enrollment data releases communicate the number of beneficiaries in each program, demographic breakdowns, and trends in program participation.

These bulletins affect multiple audiences with different interests: healthcare providers care about payment rates and coverage decisions affecting their operations; state Medicaid agencies need guidance on program administration; health plans need to understand coverage policies; and beneficiaries and advocates monitor enrollment numbers and policy changes affecting access to care. Readers of this digest will encounter announcements about changes to Medicare and Medicaid payment rates, new or modified coverage policies, quarterly enrollment updates, and guidance affecting how providers, states, and beneficiaries interact with the nation's largest health-insurance programs. Content reflects CMS's role in program administration, payment policy, and healthcare financing.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cms-email` |
| Agency / parent organization | Department of Health and Human Services (CMS) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.cms.gov/newsroom |
| URL (signup) | https://public.govdelivery.com/accounts/USCMS/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of the planned cms-newsroom web entry. The HHS departmental subscription is awaiting email confirmation; NIH Office of Research on Women's Health, the Office on Women's Health, and ODPHP lists are also confirmed and may be registered after evaluation. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

**delivering** — 2 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-20T03:51:20Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-09-17 |
| Content length | 1,476 characters average, 1,476 median (shortest 1,407, longest 1,544) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

2 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-22 | 0 |
| 2026-08-23 | 0 |
| 2026-08-24 | 0 |
| 2026-08-25 | 0 |
| 2026-08-26 | 0 |
| 2026-08-27 | 1 |
| 2026-08-28 | 0 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 0 |
| 2026-09-01 | 0 |
| 2026-09-02 | 0 |
| 2026-09-03 | 1 |
| 2026-09-04 | 0 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 0 |
| 2026-09-09 | 0 |
| 2026-09-10 | 1 |
| 2026-09-11 | 0 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 0 |
| 2026-09-15 | 0 |
| 2026-09-16 | 0 |
| 2026-09-17 | 1 |
| 2026-09-18 | 0 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

CMS Newsroom bulletins arrive via email with full text, carrying payment-rule announcements, coverage decisions, program guidance, and enrollment data. The source delivered 2 items over 14 days through 2026-09-03, maintaining the 0.14 items per day rate observed through 2026-08-03. Absolute volume is minimal with both items arriving on 2026-09-03 and no deliveries since. Text length is consistent at 1,453 and 1,492 characters. Delivery remains reliable with no consecutive failures. At subscription confirmation on 2026-07-29, no bulletins had arrived in the initial monitoring window. Additional CMS-related subscriptions remain awaiting confirmation.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

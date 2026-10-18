<!-- Markdown twin of https://fapd.info/sources/uscis-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/uscis-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: uscis-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USCIS Updates (email)

active · ingestion health: quiet · Executive · Tier 2 · email bulletin · Department of Homeland Security (USCIS)

Official site: https://www.uscis.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

United States Citizenship and Immigration Services adjudicates immigration and naturalization benefits. Its bulletins carry policy-manual updates, form revisions, filing-fee and processing changes, and program announcements that determine how applications are handled.

**Model-written orientation**

USCIS distributes policy updates, form revisions, and program announcements affecting immigration and naturalization adjudication.

United States Citizenship and Immigration Services (USCIS), a component of the Department of Homeland Security, adjudicates applications and petitions for immigration and naturalization benefits under federal immigration law. The agency processes visa petitions from employers, family members, and individuals; determines employment authorization; adjudicates asylum and refugee claims; processes applications for permanent residence (green cards); conducts naturalization proceedings and citizenship ceremonies; and administers humanitarian programs. USCIS maintains field offices in every state and maintains processing centers for applications and supporting documentation.

USCIS email bulletins communicate updates to immigration policy and procedures that directly affect how applicants are served and cases are adjudicated. Bulletins announce revisions to application forms—such as new versions of visa petition forms or naturalization application forms—and explain the changes and their effective dates. Announcements address filing fees and processing times, communicating fee increases or reductions and revised estimates for case processing. Policy updates cover manual procedures, eligibility criteria, interview requirements, and documentary requirements that immigration attorneys, employers, nonprofit organizations, and individuals need to understand. Program announcements address new initiatives, temporary programs, or pilot projects affecting specific visa categories or immigration benefits.

These bulletins ensure that stakeholders—including immigration attorneys, employers sponsoring workers, nonprofit organizations assisting immigrants, state agencies, and individuals pursuing immigration benefits—understand current procedures, applicable fees and forms, and policy changes. Implementation dates and transition information allow applicants and service providers to plan accordingly. Readers of this digest will see official guidance on how immigration procedures work, what forms and fees apply to different benefit types, and how policies and procedures evolve as the agency administers the immigration system. Content reflects USCIS's role in both routine benefit adjudication and policy-level decisions affecting immigration law implementation.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `uscis-email` |
| Agency / parent organization | Department of Homeland Security (USCIS) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.uscis.gov/newsroom |
| URL (signup) | https://public.govdelivery.com/accounts/USDHSCIS/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of the planned uscis-newsroom web entry. Department-level DHS and ICE subscriptions are awaiting email confirmation. Gate-3 coverage evaluation (2026-07-30, from the 2026-07-29 bulletins): 1 bulletin carried 1 update, full text, DKIM-verified, with its canonical uscis.gov URL. The subscription is the agency's own update list covering policy-manual, form, and processing changes — document classes the newsroom page also lists; per-topic subscription scope means the newsroom comparison stays part of coverage accounting as volume accrues. |

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

**quiet** — Most recent item 2026-10-10, 8 days ago (quiet past 7 days).

This label has held since 2026-10-10T20:42:26Z (UTC) and was last re-checked 2026-10-18T03:58:25Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-10 |
| Content length | 351 characters average, 351 median (shortest 351, longest 351) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 3 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-16 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-10-10, 8 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-09-29 | 1 |
| 2026-09-30 | 1 |
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
| 2026-10-12 | 0 |
| 2026-10-13 | 0 |
| 2026-10-14 | 0 |
| 2026-10-15 | 0 |
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Subscription bulletins via GovDelivery deliver policy and procedural updates to the project mailbox with full text. Over 14 days, 3 items arrived at 0.21 per day (ranging 351 to 1,543 characters, median 1,471), with the most recent on 2026-10-10. All mailbox entries are DKIM-verified bulletins with zero errors or refusals. The previous assessment recorded 2 items in the window; this measurement shows 3, with the latest delivery occurring after the prior assessment date. The email collector operates stably with zero consecutive errors.

_Model-written assessment of our own ingestion, generated 2026-10-11 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

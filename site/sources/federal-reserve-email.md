<!-- Markdown twin of https://fapd.info/sources/federal-reserve-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/federal-reserve-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: federal-reserve-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Reserve Board Announcements (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Federal Reserve Board

Official site: https://www.federalreserve.gov/newsevents.htm · All sources: [sources.md](../sources.md)

## What this source is

The Board of Governors of the Federal Reserve System conducts monetary policy and supervises banks. Its announcement notifications carry press releases, enforcement actions, policy statements, and speeches as the Board posts them.

**Model-written orientation**

The Federal Reserve Board sends email announcements of policy statements, press releases, enforcement actions, and speeches on monetary policy and financial supervision.

The Board of Governors of the Federal Reserve System is the central governing body of the Federal Reserve, the nation's central bank. The Federal Reserve operates with a dual mandate from Congress: to promote maximum employment and to maintain stable prices. It also supervises banks and the broader financial system to ensure financial stability and consumer protection.

The Federal Reserve Board's email notification system delivers official announcements as the Board issues them. These announcements cover the full scope of Fed operations: monetary-policy decisions and statements by the Federal Open Market Committee (which meets approximately every six weeks to set short-term interest-rate targets and discuss the economic outlook), speeches and testimonies by the Board Chair and other governors on economic conditions and policy, press releases announcing enforcement actions against banks for regulatory violations, policy statements on consumer protection and fair lending, announcements of new banking regulations or guidance to financial institutions, and notices of changes to discount-window lending procedures or reserve requirements. Readers encounter the Board's formal monetary-policy communications, statements about evolving economic conditions, announcements affecting banking practices and capital requirements, and consumer-protection guidance. The feed captures the Fed's actions in real time: interest-rate changes, guidance to markets about future policy, supervisory directives to banks, and public communications about economic outlook and policy reasoning. The subscriber base includes financial-market participants, banks, economists, policymakers, and the general public seeking to track the central bank's activities. The stream represents the authoritative voice of the Federal Reserve on monetary policy, financial supervision, and economic assessment.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `federal-reserve-email` |
| Agency / parent organization | Federal Reserve Board |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.federalreserve.gov/newsevents.htm |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). The Board runs its own notification system rather than GovDelivery, so the adapter must not assume a single platform. Corroborating sibling of the active federal-reserve-news feed. Federal Reserve Bank of New York alerts are also confirmed. Signup URL not recorded: the address inferred from the sender was checked and did not resolve, so only the confirmed sender is asserted here. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription notifications to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Poll cadence | the project mailbox is read about every 15 minutes |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 13 item(s) in the last 14 days; most recent 2026-10-02, delivered by email.

This label has held since 2026-09-28T18:01:41Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 13 in 14 days (0.93 per day) · most recent 2026-10-02 |
| Content length | 492 characters average, 498 median (shortest 423, longest 641) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 13 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-02 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

13 item(s) in the last 14 days; most recent 2026-10-02, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
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
| 2026-09-28 | 1 |
| 2026-09-29 | 4 |
| 2026-09-30 | 2 |
| 2026-10-01 | 3 |
| 2026-10-02 | 3 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Federal Reserve Board announcements are delivered via email subscription confirmed 2026-07-29, providing email-full delivery to the project mailbox with complete message text; no external links are fetched. One bulletin was ingested over the 14-day measurement window, dated 2026-09-28 with 477 characters, DKIM-verified and archived. A Federal Reserve Bank of New York alerts subscription is also active. Compared to the previous assessment dated 2026-09-09, which noted one bulletin on 2026-07-31 followed by 40 quiet days, a second bulletin arrived on 2026-09-28 after an additional 20-day interval. Total subscription activity: two bulletins across 62 days.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/federal-reserve-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/federal-reserve-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: federal-reserve-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Reserve Board Announcements (email)

active · ingestion health: quiet · Executive · Tier 2 · email bulletin · Federal Reserve Board

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
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**quiet** — Most recent item 2026-07-31, 53 days ago (quiet past 7 days).

This label has held since 2026-08-08T04:17:58Z (UTC) and was last re-checked 2026-09-22T03:47:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — most recent 2026-07-31 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-07-31, 53 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

## Our ingestion assessment

**Model-written ingestion assessment**

Subscription confirmed 2026-07-29 via the Federal Reserve Board's proprietary notification system (sender: frb-webannouncements@announcements.federalreserve.gov). One bulletin was delivered on 2026-07-31 (757 characters); no additional items have arrived in the 40 days since. The subscription is designed to carry press releases, enforcement actions, policy statements, and speeches. A Federal Reserve Bank of New York alerts subscription is also confirmed and active. No mailbox delivery or processing failures have been recorded. Compared to the previous assessment on 2026-08-09, which noted 9 days without items, the source has remained quiet through the subsequent 31 days.

_Model-written assessment of our own ingestion, generated 2026-09-09 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

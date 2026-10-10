<!-- Markdown twin of https://fapd.info/sources/cdfi-fund-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cdfi-fund-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cdfi-fund-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CDFI Fund (email)

planned · ingestion health: quiet · Executive · Tier 3 · email bulletin · Department of the Treasury, Community Development Financial Institutions Fund

Official site: https://www.cdfifund.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Community Development Financial Institutions Fund certifies and funds community lenders and administers the New Markets Tax Credit. Its bulletins carry policy updates, award announcements, and program data releases.

**Model-written orientation**

The Community Development Financial Institutions Fund certifies and funds community lenders serving underserved areas and administers tax credit programs for investing in low-income communities. This email source carries bulletins about policy updates, award announcements, and data releases.

The Community Development Financial Institutions (CDFI) Fund is an office within the Department of the Treasury that oversees and supports community development financial institutions—lenders, venture capital funds, and financial service providers that serve low-income and underserved communities. The fund certifies institutions as CDFIs based on their demonstrated commitment to community development, provides grants and loans to build their capacity, and offers technical assistance.

The CDFI Fund administers the New Markets Tax Credit, a federal tax credit that attracts private investment to low-income communities by providing incentives to investors who fund or finance eligible projects and businesses located in economically distressed areas. The fund manages programs supporting access to financial services, capital formation in underserved regions, and economic opportunity in communities with limited access to traditional lending and financial services.

Email bulletins from the CDFI Fund announce policy decisions, funding opportunities for community development financial institutions, awards of grants and tax credits to specific entities or projects, releases of program data or performance reports, and guidance documents. Readers may see announcements of new certification rounds for CDFIs, available funding for community development financial institutions to build lending capacity or services, awards of New Markets Tax Credits to specific projects and investors, reports on the reach and impact of CDFI programs, data releases about community lending trends, and notices of policy changes affecting community development finance or economic development programs. The bulletins reflect the fund's mission to expand access to financial services, credit, and capital in underserved communities.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cdfi-fund-email` |
| Agency / parent organization | Department of the Treasury, Community Development Financial Institutions Fund |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.cdfifund.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USTREASCDFI/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: treasury-email, treasury-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**quiet** — Most recent item 2026-09-30, 10 days ago (quiet past 7 days).

This label has held since 2026-10-08T04:14:09Z (UTC) and was last re-checked 2026-10-10T03:58:47Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-09-30 |
| Content length | 3,210 characters average, 3,464 median (shortest 2,321, longest 3,845) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 3 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-09-30 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-09-30, 10 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-09-30 | 3 |
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

## Our ingestion assessment

**Model-written ingestion assessment**

The CDFI Fund email source, registered 2026-09-26, delivers bulletins from cdfifund@service.govdelivery.com via GovDelivery subscription. Three bulletins have been ingested since activation, all delivered on 2026-09-30 in full-text format, ranging from 2,321 to 3,845 characters with median 3,464 characters. No subsequent deliveries have arrived; the source has been quiet for 9 days. The mailbox maintains stable access with no delivery errors or refused messages. Delivery cadence cannot yet be established from a single event day. Gate-3 coverage evaluation is proceeding with these initial ingestions. Related sources that may publish overlapping content include treasury-email and treasury-newsroom; items at the same URL merge as corroboration, while the same event at different URLs are tracked separately.

_Model-written assessment of our own ingestion, generated 2026-10-09 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

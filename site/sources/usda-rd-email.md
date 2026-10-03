<!-- Markdown twin of https://fapd.info/sources/usda-rd-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usda-rd-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usda-rd-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USDA Rural Development (email)

planned · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Agriculture, Rural Development

Official site: https://www.rd.usda.gov/ · All sources: [sources.md](../sources.md)

## What this source is

USDA Rural Development finances housing, utilities, and business development in rural areas. Its bulletins carry news releases on program funding, rules, and leadership.

**Model-written orientation**

USDA Rural Development publishes bulletins on program funding, policy changes, rules, and announcements affecting rural housing, utilities, and business development.

USDA Rural Development, a division of the Department of Agriculture, finances housing, utilities, and business development in rural areas and small towns. The agency uses federal loan and grant programs to support rural residents and communities in areas where private financing may be limited or unavailable.

Rural Development email bulletins carry news releases on grant awards and funding opportunities, policy changes affecting programs, new rules or guidance, and announcements. Readers of the digest will see announcements of available funding for purposes such as rural housing development or renovation, rural utility infrastructure, rural business expansion and creation, water and waste disposal systems, and community facilities. The agency may also announce changes to program eligibility, application processes, or rules affecting applicants and communities.

Rural Development operates in rural regions of all states. Its work encompasses individual housing loans and grants, cooperative and business lending, utility and water system infrastructure financing, and community facility support. The agency works with local partners, nonprofit organizations, and private lenders to deliver its programs.

The agency's email channel carries announcements from headquarters and may include program updates, policy guidance, or funding opportunities affecting rural development nationwide. A reader of this digest will see the ongoing deployment of federal rural development resources and policy changes affecting rural communities. The agency also publishes notices and rules in the Federal Register; items there appear under separate registry entries.

Unlike regulatory agencies, Rural Development's primary role is financing and support rather than enforcement or standard-setting. Items appear in the digest as the agency publishes them through the email channel and do not include announcements or releases published before the email subscription was activated or through other agency channels.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usda-rd-email` |
| Agency / parent organization | Department of Agriculture, Rural Development |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.rd.usda.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDARD/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: agriculture-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 4 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-09-28T17:26:00Z (UTC) and was last re-checked 2026-10-03T03:48:44Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 4 in 14 days (0.29 per day) · most recent 2026-10-01 |
| Content length | 2,646 characters average, 2,070 median (shortest 1,768, longest 4,677) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 4 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-01 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

4 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-04 | 0 |
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
| 2026-09-29 | 0 |
| 2026-09-30 | 1 |
| 2026-10-01 | 2 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Registered 2026-09-26 with three configured sender addresses; began delivering 2026-09-28. One bulletin ingested in full text (~4,677 characters) generating one item, with no errors or refusals. The collector maintains stable contact with the email system. A single bulletin is an insufficient sample to characterize completeness; the observed stream is the subscription's own coverage measure.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

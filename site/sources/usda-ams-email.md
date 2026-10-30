<!-- Markdown twin of https://fapd.info/sources/usda-ams-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usda-ams-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usda-ams-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Agricultural Marketing Service (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Agriculture, Agricultural Marketing Service

Official site: https://www.ams.usda.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Agricultural Marketing Service administers marketing programs, grading standards, and the National Organic Program. Its bulletins carry program announcements and notices.

**Model-written orientation**

The Agricultural Marketing Service administers marketing programs and grading standards for agricultural commodities, as well as the National Organic Program. This email source carries bulletins about program announcements and regulatory updates.

The Agricultural Marketing Service (AMS) is an agency within the U.S. Department of Agriculture that develops and administers marketing programs and standards for agricultural products. AMS works to ensure fair and orderly marketing conditions for commodities and to promote the quality and value of American agricultural products in domestic and international markets.

AMS's responsibilities include setting and enforcing grading standards for fruits, vegetables, dairy, and other products; operating programs that support farmers and marketing organizations; and administering the National Organic Program, which sets standards for organic production and labeling. The agency also oversees programs like the Farmers Market Promotion Program and other direct-market initiatives that support local food systems and agricultural commerce.

Email bulletins from AMS carry announcements about program changes, new funding opportunities, updates to regulatory requirements, and notices related to commodity marketing and certification. Readers may see announcements about organic certification changes, commodity grading updates, new grant programs for farmers' markets and local food systems, notices of rulemaking or policy changes affecting agricultural marketing, and updates to standards or labeling requirements. The bulletins reflect the agency's role in supporting agricultural commerce, maintaining quality standards that affect farmers, processors, retailers, and consumers, and promoting domestic and international trade in American agricultural products.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usda-ams-email` |
| Agency / parent organization | Department of Agriculture, Agricultural Marketing Service |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.ams.usda.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDAAMS/subscriber/new |
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

**delivering** — 2 item(s) in the last 14 days; most recent 2026-10-27, delivered by email.

This label has held since 2026-10-27T18:16:17Z (UTC) and was last re-checked 2026-10-30T03:49:13Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-10-27 |
| Content length | 1,572 characters average, 1,572 median (shortest 917, longest 2,226) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 2 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-27 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

2 item(s) in the last 14 days; most recent 2026-10-27, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-10-01 | 0 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 2 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |
| 2026-10-08 | 0 |
| 2026-10-09 | 0 |
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 0 |
| 2026-10-14 | 0 |
| 2026-10-15 | 0 |
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 1 |
| 2026-10-20 | 0 |
| 2026-10-21 | 0 |
| 2026-10-22 | 0 |
| 2026-10-23 | 0 |
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 0 |
| 2026-10-27 | 1 |
| 2026-10-28 | 0 |
| 2026-10-29 | 0 |
| 2026-10-30 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Bulletins from the Agricultural Marketing Service arrive in the project mailbox from usdaams@public.govdelivery.com and are ingested by the email adapter with DKIM verification. The registry lists the delivery mode as email-full, meaning the bulletin carried the full item text. Across the 14-day window we measured two items, with a median and average of 1572 characters, a minimum of 917 characters, and a maximum of 2226 characters. One item was recorded in the hour-13 bucket on 2026-10-27, and the mailbox's last message is timestamped 2026-10-27T17:59:50Z. The mailbox shows two bulletins with zero errors and zero refused messages, and health reads delivering at 0.14 items per day. Since the previous assessment on 2026-10-20, which recorded one item dated 2026-10-19 at 0.07 items per day, one additional bulletin dated 2026-10-27 has been ingested. Earlier bulletins were not backfilled, and the status remains planned pending gate-3 coverage evaluation.

_Model-written assessment of our own ingestion, generated 2026-10-28 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

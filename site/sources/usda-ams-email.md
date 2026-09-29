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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-09-28, delivered by email.

This label has held since 2026-09-28T20:11:15Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-09-28 |
| Content length | 954 characters average, 954 median (shortest 954, longest 954) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-09-28 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-09-28, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-31 | 0 |
| 2026-09-01 | 0 |
| 2026-09-02 | 0 |
| 2026-09-03 | 0 |
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

## Our ingestion assessment

**Model-written ingestion assessment**

Registered 2026-09-26; began delivering 2026-09-28. One bulletin ingested in full text (~954 characters) generating one item, with no errors or refusals. The collector maintains stable contact with the email system. A single bulletin cannot characterize source coverage; the stream observed is the subscription's own editorial selection.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

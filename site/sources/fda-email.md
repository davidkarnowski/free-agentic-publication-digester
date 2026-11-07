<!-- Markdown twin of https://fapd.info/sources/fda-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fda-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fda-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FDA Email Updates (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Health and Human Services (FDA)

Official site: https://www.fda.gov/news-events/fda-newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Food and Drug Administration regulates food, drugs, medical devices, and tobacco. Its bulletins carry approvals, safety communications, recalls, and warning letters as the agency issues them.

**Model-written orientation**

The FDA distributes drug approvals, safety communications, recalls, and enforcement actions by email subscription.

The Food and Drug Administration (FDA), part of the Department of Health and Human Services, regulates the safety and efficacy of pharmaceuticals, biological products, medical devices, food safety, dietary supplements, and tobacco products in the United States. The agency reviews applications for new drugs and devices before market entry; inspects manufacturing and distribution facilities; monitors product safety and adverse events after products reach the market; and takes enforcement action when products or manufacturers fail to meet legal standards. FDA maintains laboratories, field offices, and review divisions nationwide and employs scientists, physicians, engineers, and compliance specialists.

FDA email bulletins communicate drug and device approvals—including new molecular entities, new indications for existing drugs, and novel medical devices cleared or approved for marketing. Safety communications address identified safety concerns affecting marketed products, providing healthcare professionals and the public with updated guidance about risks, appropriate use, or monitoring. The bulletins also communicate product recalls when safety defects, contamination, or other issues are identified, specifying affected product batches and distribution channels. Warning letters to manufacturers or distributors communicate regulatory violations and enforcement expectations. Fast-track designations, breakthrough-therapy designations, and accelerated-approval pathways are also announced.

These bulletins reach healthcare professionals—including physicians, nurses, and pharmacists—as well as manufacturers, industry, and the general public with urgent or significant safety and regulatory information. They communicate FDA's regulatory decisions and findings from post-market surveillance activities. Readers of this digest will encounter notifications about new approved treatments becoming available; safety warnings about existing products requiring action by healthcare providers or consumers; product recalls; and enforcement actions against manufacturers or distributors of drugs, devices, or food products. Content reflects FDA's role in both pre-market approval and post-market safety monitoring across the products it regulates.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fda-email` |
| Agency / parent organization | Department of Health and Human Services (FDA) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.fda.gov/news-events/fda-newsroom |
| URL (signup) | https://public.govdelivery.com/accounts/USFDA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Corroborating sibling of the active fda-press feed; content evaluation will establish whether the bulletins carry material the feed omits. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

**delivering** — 21 item(s) in the last 14 days; most recent 2026-11-06, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-11-07T04:57:24Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 21 in 14 days (1.5 per day) · most recent 2026-11-06 |
| Content length | 2,189 characters average, 2,051 median (shortest 510, longest 5,023) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 22 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-11-07 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

21 item(s) in the last 14 days; most recent 2026-11-06, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-10-09 | 1 |
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 1 |
| 2026-10-14 | 12 |
| 2026-10-15 | 0 |
| 2026-10-16 | 2 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 4 |
| 2026-10-20 | 4 |
| 2026-10-21 | 1 |
| 2026-10-22 | 0 |
| 2026-10-23 | 3 |
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 2 |
| 2026-10-27 | 0 |
| 2026-10-28 | 3 |
| 2026-10-29 | 2 |
| 2026-10-30 | 4 |
| 2026-10-31 | 1 |
| 2026-11-01 | 0 |
| 2026-11-02 | 2 |
| 2026-11-03 | 3 |
| 2026-11-04 | 2 |
| 2026-11-05 | 1 |
| 2026-11-06 | 1 |
| 2026-11-07 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

FDA email bulletins are ingested by email with full text carried in each message, DKIM-verified and archived. Over the 14-day window we ingested 22 items at 1.57 per day, with the most recent dated 2026-11-04. The mailbox recorded 23 bulletin messages with no administrative messages, errors, or refused deliveries, and we have not reconciled the difference between 23 messages and 22 items. Item length ranged from 510 to 3,492 characters, averaging 1,979 with a median of 1,942. Daily counts in the seven records shown were 4 on 2026-10-30, 1 on 2026-10-31, 2 on 2026-11-02, 3 on 2026-11-03, and 2 on 2026-11-04, with none on the other two days. The collector reports no consecutive errors and health reads delivering. Since the previous assessment on 2026-10-06, the 14-day count fell from 27 items at 1.93 per day, the most recent item moved from 2026-10-05 to 2026-11-04, the maximum length fell from 6,571 to 3,492 characters, and the median rose from 1,768 to 1,942. The registry records this source as a corroborating sibling of the fda-press feed.

_Model-written assessment of our own ingestion, generated 2026-11-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

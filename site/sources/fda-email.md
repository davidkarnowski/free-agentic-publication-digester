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
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 24 item(s) in the last 14 days; most recent 2026-09-16, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-17T03:58:34Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 5 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 24 in 14 days (1.71 per day) · most recent 2026-09-16 |
| Content length | 1,653 characters average, 1,522 median (shortest 272, longest 5,689) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

24 item(s) in the last 14 days; most recent 2026-09-16, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-19 | 6 |
| 2026-08-20 | 6 |
| 2026-08-21 | 1 |
| 2026-08-22 | 0 |
| 2026-08-23 | 0 |
| 2026-08-24 | 4 |
| 2026-08-25 | 3 |
| 2026-08-26 | 10 |
| 2026-08-27 | 3 |
| 2026-08-28 | 4 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 6 |
| 2026-09-01 | 2 |
| 2026-09-02 | 1 |
| 2026-09-03 | 5 |
| 2026-09-04 | 5 |
| 2026-09-05 | 0 |
| 2026-09-06 | 1 |
| 2026-09-07 | 0 |
| 2026-09-08 | 6 |
| 2026-09-09 | 1 |
| 2026-09-10 | 0 |
| 2026-09-11 | 2 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 3 |
| 2026-09-15 | 1 |
| 2026-09-16 | 5 |
| 2026-09-17 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

FDA updates arrive via email with full text, carrying approvals, safety communications, recalls, and warning letters. The source delivered 43 items over 14 days through 2026-09-04, averaging 3.07 per day, more than tripling the 1.0 items per day observed in the initial seven days. The email channel operates as a corroborating input alongside the active fda-press RSS feed; whether the bulletins carry material the feed omits remains under evaluation. Text averaged 1,918 characters, ranging from 296 to 4,652. Delivery has been consistent with no consecutive failures. At subscription confirmation on 2026-07-29, no bulletins had arrived in the initial monitoring window.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

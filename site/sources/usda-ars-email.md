<!-- Markdown twin of https://fapd.info/sources/usda-ars-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usda-ars-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usda-ars-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Agricultural Research Service (email)

active · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Agriculture, Agricultural Research Service

Official site: https://www.ars.usda.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Agricultural Research Service is USDA's in-house research agency. Its news service bulletins report research findings.

**Model-written orientation**

The Agricultural Research Service is the scientific research agency of the U.S. Department of Agriculture, conducting studies to improve agricultural methods and food systems. This digest includes findings and announcements from the service's email bulletins.

The Agricultural Research Service (ARS) is the scientific research agency within the U.S. Department of Agriculture. As USDA's in-house research body, ARS conducts investigations into agricultural production, food safety, environmental stewardship, and related topics to support American farming and food systems. With research facilities distributed across the country, the service works on challenges ranging from crop science and livestock production to agricultural engineering, food quality assessment, and natural resource management.

The service shares its work through multiple channels, including email bulletins distributed to subscribers. These bulletins highlight research projects, discoveries, and developments of broader interest. Topics typically cover advances in agricultural methods, findings from long-term studies, developments in farm technology, food safety research, and environmental or conservation research related to agriculture. The bulletins serve as a window into ongoing work at ARS facilities and stations.

In this digest, items from ARS appear when the service distributes news about research findings or agricultural developments through its email service. Readers will encounter announcements of studies, reports on research outcomes, and information about agricultural science developments. The bulletins are archived and available through the digest, with each item citing the original message. Because email-delivered news represents one channel among multiple ways the service communicates its work, coverage reflects both the topics selected at signup and the service's publishing priorities. The digest shows what the service published on any given day.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usda-ars-email` |
| Agency / parent organization | Department of Agriculture, Agricultural Research Service |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.ars.usda.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDAARS/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation (2026-09-28, from live delivery): 1 bulletin -> 1 item on 2026-09-28 (a research feature on precision agriculture infrastructure). The bulletin carries no link to a web copy, so the item cites the archived message itself. DKIM-verified with the key archived; signed by subscribers.usda.gov, which aligns with the sender's domain. One bulletin is a thin sample, and the topic selection made at signup was not recorded, so this evaluation claims no coverage relationship to the agency's full output: the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector and shown on the source page. Related entries that can publish the same news: agriculture-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-09-28, delivered by email.

This label has held since 2026-09-28T15:46:43Z (UTC) and was last re-checked 2026-09-30T03:54:28Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-09-28 |
| Content length | 1,507 characters average, 1,507 median (shortest 1,507, longest 1,507) |
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
| 2026-09-30 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Registered 2026-09-26, began delivering 2026-09-28. One bulletin ingested in full text (~1,507 characters) generating one item, with no errors or refusals. DKIM signature verified and archived; signed by subscribers.usda.gov. The bulletin carried no external link; the item cites the archived message. The collector maintains stable contact. A single bulletin is too thin a sample to establish coverage scope; the stream is the subscription's own measure.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

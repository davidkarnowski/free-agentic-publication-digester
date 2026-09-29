<!-- Markdown twin of https://fapd.info/sources/cpsc-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cpsc-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cpsc-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CPSC Recalls and News (email)

planned · ingestion health: no data · Executive · Tier 2 · email bulletin · Consumer Product Safety Commission

Official site: https://www.cpsc.gov/Newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Consumer Product Safety Commission regulates consumer product safety and orders recalls. Its bulletins carry recall announcements naming specific products and hazards, safety warnings, and civil-penalty settlements.

**Model-written orientation**

The Consumer Product Safety Commission sends email notifications of product recalls, safety hazards, and enforcement actions affecting consumer products.

The Consumer Product Safety Commission is an independent federal regulatory agency established to protect the public against unsafe consumer products. The CPSC has the authority to set safety standards for thousands of consumer products—from toys and children's products to household appliances, electronics, and furniture—and to order recalls when products pose hazards. The commission also enforces compliance with safety standards and imposes civil penalties on manufacturers and distributors who violate regulations.

The CPSC email subscription notifies readers of recalls and safety actions. Each announcement identifies the specific product being recalled (brand, model, or product line), describes the hazard that prompted the recall (structural failure, choking risk, fire or burn danger, chemical exposure, electrical hazard), and provides instructions for consumers—whether to stop using the product, return it for a refund or replacement, or await a repair kit. Readers also receive notices of import refusals (products the CPSC blocked from entering U.S. commerce because they failed safety testing), safety warnings about product defects or misuse risks, and announcements of civil-penalty settlements against manufacturers for safety violations. The feed covers the full range of the CPSC's regulatory authority: children's products (toys, cribs, car seats, clothing), household products (appliances, furniture, tools), electronics (chargers, batteries, cordless devices), and leisure products (bicycles, sporting goods, recreational equipment). A single day may bring recalls of toys, furniture, and appliances as manufacturers discover defects through field reports or testing. The stream serves consumers seeking recall alerts, media outlets reporting on product safety, retail and e-commerce businesses managing inventory compliance, and manufacturers monitoring the regulatory environment. Each bulletin reflects the CPSC's core mission: identifying unsafe products and removing them from commerce or requiring remediation.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cpsc-email` |
| Agency / parent organization | Consumer Product Safety Commission |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.cpsc.gov/Newsroom |
| URL (signup) | https://www.cpsc.gov/Newsroom/Subscribe |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). New coverage: the commission had no registered source before this subscription. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — none recorded in the lookback period |
| Mailbox | no message from this sender in the last 14 days |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

No bulletin recorded from this source in the last 180 days.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

## Our ingestion assessment

**Model-written ingestion assessment**

Consumer Product Safety Commission recall announcements are delivered via email subscription confirmed 2026-07-29. No bulletins have been recorded in our ingestion logs; the subscription remains in planned status despite active confirmation with the sender.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

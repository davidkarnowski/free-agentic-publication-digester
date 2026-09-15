<!-- Markdown twin of https://fapd.info/sources/cpsc-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cpsc-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cpsc-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CPSC Recalls and News (email)

planned · Executive · Tier 2 · email bulletin · Consumer Product Safety Commission

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
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

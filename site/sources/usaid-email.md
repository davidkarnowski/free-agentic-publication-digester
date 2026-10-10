<!-- Markdown twin of https://fapd.info/sources/usaid-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usaid-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usaid-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USAID Industry Liaison (email)

active · ingestion health: no data · Executive · Tier 2 · email bulletin · U.S. Agency for International Development

Official site: https://www.usaid.gov/news-information · All sources: [sources.md](../sources.md)

## What this source is

The U.S. Agency for International Development administers civilian foreign aid and development assistance. Its Industry Liaison bulletins carry procurement, partnership, and policy-guidance announcements for implementing partners.

**Model-written orientation**

The U.S. Agency for International Development publishes procurement opportunities and policy guidance for development-assistance partners and implementing organizations.

The U.S. Agency for International Development (USAID) is the federal agency responsible for administering civilian foreign aid and international development assistance programs. USAID works globally to support development priorities including economic growth, global health, humanitarian assistance, education, and climate resilience, implementing these programs through partnerships with a diverse network of organizations. USAID's implementing partners include nonprofit organizations and NGOs, educational institutions, for-profit contractors, consulting firms, research organizations, and local organizations in partner countries. These partners design and carry out development programs on the ground while USAID provides funding, oversight, and strategic direction. Effective coordination with the implementing-partner network is essential to USAID's ability to deliver development assistance. USAID's Industry Liaison office serves as a key communication channel with the partner and contractor community. The office's bulletins include procurement announcements and bidding opportunities for development projects and programs, notices of available partnership and funding opportunities, policy guidance and procedural updates for organizations implementing USAID programs, and other announcements relevant to prospective and active USAID partners. Readers involved in international development work—including nonprofit organizations and NGOs seeking USAID funding partnerships, contractors bidding on development projects, universities and research institutions engaged in development work, and consultants and specialists providing services to USAID programs—will see information about how to work with USAID, bidding processes and deadlines for development projects, available funding opportunities, and updates to USAID policies and procedures affecting partners and implementers.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usaid-email` |
| Agency / parent organization | U.S. Agency for International Development |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.usaid.gov/news-information |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). The project mailbox received a USAID bulletin during the changeover window (e.g. 'USAID Termination Settlement Negotiation and Voucher Guidance') carrying substantive policy guidance. Subscribed through USAID's own flow (sender [address withheld]); exact topic selection is in the operator's subscription records, not transcribed here. DKIM recorded per message at ingest. |

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-10-01T21:38:40Z (UTC) and was last re-checked 2026-10-10T03:58:47Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter with DKIM verification and alignment. Activated 2026-10-01 on observed delivery. The project mailbox received a USAID bulletin during the changeover window (e.g., 'USAID Termination Settlement Negotiation and Voucher Guidance') carrying substantive policy guidance for implementing partners. However, no items have yet been recorded as of 2026-10-02. The source is subscribed through USAID's GovDelivery flow (sender usaid-industry-liaison@subscribe.usaid.gov) in the active tier.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

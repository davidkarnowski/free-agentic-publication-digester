<!-- Markdown twin of https://fapd.info/sources/dot-intergov-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/dot-intergov-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: dot-intergov-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DOT Intergovernmental Affairs (email)

active · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Transportation

Official site: https://www.transportation.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of Transportation's Office of Intergovernmental Affairs coordinates with state, local, and tribal governments. Its bulletins carry meeting notices and coordination announcements.

**Model-written orientation**

The Department of Transportation's Office of Intergovernmental Affairs coordinates federal-state-local transportation policy, funding, and program implementation.

The Department of Transportation's Office of Intergovernmental Affairs serves as the liaison and primary coordination channel between the federal Department of Transportation and state, local, and tribal governments. The office facilitates communication and collaboration on transportation policy, funding programs, and implementation matters that involve federal and sub-federal levels of government. Transportation in the United States is inherently a multi-level undertaking—the federal government provides funding, sets national standards and policies, and oversees certain national interests, while states and local governments own and operate most of the nation's roads, transit systems, and transportation infrastructure. Effective coordination and information-sharing among these levels is essential for implementing federal transportation programs and addressing transportation challenges. The office's bulletins include notices of meetings, forums, and coordination sessions where federal and state transportation leaders convene to discuss policy and programs, announcements of federal transportation funding opportunities and grant programs available to states and localities, updates on federal policies and programs affecting state and local transportation, and other coordination announcements relevant to multi-level transportation governance. Readers, particularly state transportation officials, local transportation agencies, regional planning organizations, and tribal transportation authorities, will see information about opportunities to participate in federal-state coordination, available federal funding for transportation projects, and updates on federal transportation programs and policies affecting their operations and planning.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `dot-intergov-email` |
| Agency / parent organization | Department of Transportation |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.transportation.gov/ |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). Coverage caveat: this is an HQ-office coordination channel (e.g. 'Monthly Meeting with USDOT Intergovernmental Affairs Office'), mostly meeting notices — low digest signal, tier 3. Registered because the operator approved the DOT set; may be declined if meeting notices are not wanted. Subscribed through DOT's own flow (sender [address withheld]); DKIM recorded per message at ingest. |

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

This label has held since 2026-10-01T21:38:40Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter with DKIM verification and alignment. Activated 2026-10-01 on observed delivery. No items have been recorded as of 2026-10-02. This is an HQ-office coordination channel (e.g., 'Monthly Meeting with USDOT Intergovernmental Affairs Office') carrying mostly meeting notices and coordination announcements with lower digest signal. The source is subscribed through DOT's GovDelivery flow (sender intergov@info.dot.gov) in tier 3. The source was registered as part of the DOT set; operator approval is required for continuation.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/childrens-bureau-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/childrens-bureau-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: childrens-bureau-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Children's Bureau — News From CB (email)

active · ingestion health: no data · Executive · Tier 2 · email bulletin · Department of Health and Human Services (ACF / Children's Bureau)

Official site: https://www.acf.hhs.gov/cb · All sources: [sources.md](../sources.md)

## What this source is

The Children's Bureau, within the Administration for Children and Families, oversees federal child-welfare programs including foster care, adoption, and child-abuse prevention. Its 'News From CB' bulletins carry policy news to the public — Child Welfare Policy Manual amendments, program announcements, and guidance.

**Model-written orientation**

The Children's Bureau oversees federal child welfare programs including foster care, adoption support, and child abuse prevention. Its 'News From CB' email bulletins deliver policy updates, program announcements, and guidance.

The Children's Bureau operates within the Administration for Children and Families (ACF), a division of the Department of Health and Human Services. The Children's Bureau administers federal child welfare programs and sets policy for the nation's child welfare system.

Child welfare in the United States is a shared responsibility among federal, state, and local governments. The federal role centers on funding, oversight, and policy guidance. The Children's Bureau carries out the federal responsibility—it funds state and local child welfare agencies, establishes policies and standards, and provides technical assistance to states and communities working in child welfare.

The Children's Bureau's portfolio includes major federal programs: foster care and adoption services, support for families at risk of child abuse and neglect, child abuse prevention and investigation, and permanency services that help children remain with families or achieve stable, permanent placements. The bureau also maintains the legal and regulatory framework that guides how states and counties operate their child welfare systems.

Through its 'News From CB' email bulletins, the Children's Bureau communicates with a public audience including child welfare professionals, policymakers, advocates, and others interested in federal child welfare policy. These bulletins carry announcements of changes to the Child Welfare Policy Manual, program announcements and funding opportunities, guidance and technical updates for states and localities, and news on federal child welfare initiatives.

The communications inform the child welfare community of federal policy direction, updates to federal requirements and guidance, opportunities for funding and training, and changes to federal programs and regulations.

In this digest, readers will see the Children's Bureau's official communications from its public bulletin series—primarily policy updates, policy manual amendments, and program announcements that the bureau distributes to keep the child welfare community informed.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `childrens-bureau-email` |
| Agency / parent organization | Department of Health and Human Services (ACF / Children's Bureau) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.acf.hhs.gov/cb |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 (operator approval) on observed delivery over the late-September changeover: the project mailbox received 'News From CB' bulletins (e.g. 'Amendments to the Child Welfare Policy Manual') carrying Children's Bureau policy news to the public. Distinct from the Child Welfare Information Gateway's 'My Child Welfare Librarian' resource digest ([address withheld]), reviewed the same day and left unregistered as specific-use reference content rather than press or news. Subscribed through the publisher's own flow; DKIM recorded per message at ingest. |

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

This label has held since 2026-10-01T22:11:29Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

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

Children's Bureau "News From CB" bulletin series was activated on 2026-10-01 following observed delivery of policy announcements during the late-September changeover. The registry distinguishes this from the separate Child Welfare Information Gateway resource digest, reviewed and left unregistered as specific-use reference content. No messages have been recorded in the mailbox since activation. Messages are ingested through the email adapter via DKIM verification.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

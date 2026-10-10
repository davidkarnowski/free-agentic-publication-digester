<!-- Markdown twin of https://fapd.info/sources/nrcs-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nrcs-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nrcs-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USDA NRCS (email)

active · ingestion health: quiet · Executive · Tier 2 · email bulletin · Department of Agriculture (NRCS)

Official site: https://www.nrcs.usda.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Natural Resources Conservation Service helps farmers, ranchers, and landowners conserve soil, water, and wildlife habitat. Its bulletins carry conservation-program announcements, funding and investment decisions, and enrollment deadlines as the agency distributes them.

**Model-written orientation**

The Natural Resources Conservation Service delivers conservation-program announcements and funding deadlines for farmers, ranchers, and landowners.

The Natural Resources Conservation Service (NRCS), part of the Department of Agriculture, is the federal agency that works with private landowners and agricultural operations to conserve and enhance natural resources. NRCS administers a portfolio of conservation programs that provide technical assistance and financial incentives for soil and water conservation, wildlife habitat enhancement, forest management, and other environmental stewardship activities on privately held land. The agency partners with farmers, ranchers, and other land managers to design and implement conservation practices tailored to local conditions and landowner goals. NRCS's bulletins include announcements of new or expanded conservation programs, notifications of available funding and cost-share opportunities with eligibility criteria and application deadlines, updates on enrollment periods for existing initiatives, and information about changes to program requirements or technical guidance. Readers will see practical information about grant and cost-share programs, funding amounts and deadlines, eligibility requirements, and how to apply. The content reflects NRCS's mission of distributing federal conservation resources and coordinating with landowners on land and natural-resource management. These announcements are relevant to agricultural producers seeking technical or financial assistance, conservation professionals working with landowners, land trusts and conservation organizations, and anyone managing private land who may benefit from NRCS conservation programs or cost-share support.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nrcs-email` |
| Agency / parent organization | Department of Agriculture (NRCS) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.nrcs.usda.gov/news |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). The project mailbox received NRCS bulletins over the late-September changeover window (e.g. 'USDA Invests $52 Million in 19 Projects to Expand Wildlife Conservation') carrying conservation-program and investment announcements. Subscribed through the publisher's own GovDelivery flow (sender [address withheld]); exact topic selection is in the operator's subscription records, not transcribed here. DKIM posture is recorded per message at ingest. |

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

**quiet** — Most recent item 2026-10-02, 8 days ago (quiet past 7 days).

This label has held since 2026-10-02T13:48:30Z (UTC) and was last re-checked 2026-10-10T03:58:47Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-02 |
| Content length | 1,170 characters average, 1,170 median (shortest 1,170, longest 1,170) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-02 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-10-02, 8 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-09-28 | 0 |
| 2026-09-29 | 0 |
| 2026-09-30 | 0 |
| 2026-10-01 | 0 |
| 2026-10-02 | 1 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |
| 2026-10-08 | 0 |
| 2026-10-09 | 0 |
| 2026-10-10 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The Natural Resources Conservation Service delivers conservation announcements to the project mailbox via GovDelivery (sender usdafarmers@public.govdelivery.com). Activated 2026-10-01 on observed delivery, with one bulletin recorded 2026-10-02 at 1,170 characters carrying conservation-program and funding announcements. All messages pass DKIM verification and alignment. The source is registered at tier 2 with active status; delivery cadence and format patterns are not yet established from a single item.

_Model-written assessment of our own ingestion, generated 2026-10-03 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

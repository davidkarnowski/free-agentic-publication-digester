<!-- Markdown twin of https://fapd.info/sources/nhtsa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nhtsa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nhtsa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NHTSA Press Releases (email)

planned · Executive · Tier 2 · email bulletin · Department of Transportation (NHTSA)

Official site: https://www.nhtsa.gov/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The National Highway Traffic Safety Administration regulates vehicle safety and investigates defects. Its bulletins carry press releases, recall announcements, defect investigations, and crash-data releases — safety actions with direct consequences for vehicle owners.

**Model-written orientation**

The National Highway Traffic Safety Administration regulates motor vehicle safety and investigates safety defects. Its subscription bulletins announce recalls, defect investigations, and crash-safety research findings.

The National Highway Traffic Safety Administration (NHTSA) is a bureau of the Department of Transportation with two main functions: setting and enforcing federal motor-vehicle safety standards, and investigating vehicle safety defects.

In its standard-setting role, NHTSA issues federal motor-vehicle safety standards (FMVSS) specifying safety requirements for vehicle design, equipment, and performance. These standards address crashworthiness, handling, visibility, and other aspects of vehicle safety. NHTSA also oversees fuel-economy standards and vehicle emissions standards under authority delegated to it.

In its investigation role, NHTSA receives consumer complaints about vehicles, investigates those complaints to determine if a safety defect exists, and orders manufacturers to recall vehicles and correct defects. The agency has authority to impose civil penalties on manufacturers that fail to report known defects or that comply late with recall requirements. NHTSA also conducts crash-testing and publishes safety ratings to inform consumers.

NHTSA operates its own subscription bulletin service, separate from the DOT departmental service. The bulletins report on recalls (including the specific vehicles and model years affected, the defect description, and the remedy offered by the manufacturer), defect investigations underway or completed, new or amended safety standards, grant awards, and crash-research findings.

Readers will see safety notices affecting vehicle owners directly: recalls that may require them to bring a vehicle to a dealership, information about safety features and ratings, and notices of defect investigations that may lead to future recalls. The publication cadence reflects the rate of safety investigations, recall decisions, and standards development.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nhtsa-email` |
| Agency / parent organization | Department of Transportation (NHTSA) |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.nhtsa.gov/press-releases |
| URL (signup) | https://public.govdelivery.com/accounts/USDOTNHTSA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of nhtsa-press, which returns HTTP 403 to our identified client. NHTSA operates its own bulletin account rather than sharing the departmental one, giving finer topic control than expected. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
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

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-28 | 0 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
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
| 2026-09-16 | 1 |
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

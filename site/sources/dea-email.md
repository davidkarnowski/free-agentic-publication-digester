<!-- Markdown twin of https://fapd.info/sources/dea-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/dea-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: dea-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DEA Updates (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Justice (DEA)

Official site: https://www.dea.gov/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Drug Enforcement Administration enforces controlled-substance law. Its bulletins carry enforcement announcements, scheduling actions, and public-safety alerts on emerging drug threats.

**Model-written orientation**

The Drug Enforcement Administration enforces federal controlled-substance law and coordinates drug-policy operations. Its subscription bulletins report enforcement actions, drug-scheduling decisions, and public-safety advisories on emerging drug threats.

The Drug Enforcement Administration (DEA) is a bureau of the Department of Justice charged with enforcing federal drug laws. The DEA investigates drug trafficking, clandestine drug laboratories, and diversion of controlled substances from the legal supply chain to the illicit market. It also administers the controlled-substances registration program, which licenses practitioners, researchers, manufacturers, and distributors to handle regulated drugs.

The DEA operates through a network of field offices and overseas posts covering the United States and major drug-trafficking regions. The agency coordinates with state and local law enforcement, the Postal Inspection Service, and international law-enforcement partners on drug cases.

The DEA distributes a subscription bulletin service to which this project subscribes. The bulletins report on enforcement operations, including major drug seizures, arrest announcements, and dismantled drug-production sites. They announce regulatory actions such as temporary or permanent scheduling of new substances under the Controlled Substances Act, changes to diversion-control requirements for practitioners and manufacturers, and regulatory guidance.

The bulletins may also alert the public to emerging drug threats identified through enforcement activity or surveillance: new synthetic drugs entering communities, novel distribution methods, or public-health concerns related to specific substances. These advisories are informational, aimed at law enforcement, medical practitioners, public-health officials, and community leaders.

The content of the bulletins reflects the DEA's investigative priorities and the pace of regulatory decisions, resulting in variable bulletin frequency. Readers will see a mix of major enforcement announcements, new scheduling actions, regulatory guidance, and emerging-threat advisories, with a geographic and substance-type variety reflecting the national and international scope of the DEA's jurisdiction.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `dea-email` |
| Agency / parent organization | Department of Justice (DEA) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.dea.gov/press-releases |
| URL (signup) | https://public.govdelivery.com/accounts/USDOJDEA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of dea-press, which returns HTTP 403 to our identified client — the first working input for this agency. The Diversion Control Division list is subscribed but awaiting email confirmation. Gate-3 coverage evaluation (2026-07-30, from live delivery): 1 bulletin -> 1 item on 2026-07-30 (main DEA account; the Diversion Control list remains unconfirmed separately). DKIM-verified with the key archived; the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector. |

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

**delivering** — 8 item(s) in the last 14 days; most recent 2026-09-21, delivered by email.

This label has held since 2026-09-09T20:07:29Z (UTC) and was last re-checked 2026-09-22T03:47:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 8 in 14 days (0.57 per day) · most recent 2026-09-21 |
| Content length | 1,845 characters average, 1,048 median (shortest 64, longest 5,579) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

8 item(s) in the last 14 days; most recent 2026-09-21, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-24 | 0 |
| 2026-08-25 | 0 |
| 2026-08-26 | 0 |
| 2026-08-27 | 1 |
| 2026-08-28 | 0 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 1 |
| 2026-09-01 | 0 |
| 2026-09-02 | 0 |
| 2026-09-03 | 0 |
| 2026-09-04 | 0 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 0 |
| 2026-09-09 | 1 |
| 2026-09-10 | 0 |
| 2026-09-11 | 2 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 1 |
| 2026-09-15 | 1 |
| 2026-09-16 | 0 |
| 2026-09-17 | 1 |
| 2026-09-18 | 0 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 2 |
| 2026-09-22 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The DEA Updates source delivers bulletins by email subscription with DKIM verification, serving as the primary ingestion channel for this agency. Email bulletins arrive in teaser format (short summaries), not full article text. Over the 14-day measurement window, 2 items were delivered, averaging 0.14 items per day. The most recent bulletin arrived on 2026-09-09. Extracted bulletin text ranges from 82 to 5,579 characters, with a median of 2,830 characters. The source exhibited a delivery gap prior to the recent arrival; the previous assessment recorded the prior delivery on August 31. The sibling dea-press HTTP endpoint returns an access error to our client, making email subscription the only working channel. The Diversion Control Division mailing list, subscribed during setup, remains unconfirmed and has not yet delivered content.

_Model-written assessment of our own ingestion, generated 2026-09-10 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

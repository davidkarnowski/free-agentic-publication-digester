<!-- Markdown twin of https://fapd.info/sources/doe-cmei-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/doe-cmei-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: doe-cmei-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DOE Critical Minerals and Energy Innovation (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Energy, Office of Critical Minerals and Energy Innovation

Official site: https://www.energy.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of Energy's Office of Critical Minerals and Energy Innovation funds critical-minerals and energy technology programs. Its bulletins carry program launches, funding opportunities, and office updates.

**Model-written orientation**

The Department of Energy's Office of Critical Minerals and Energy Innovation supports research and deployment of energy technologies and oversees critical minerals programs. This email source carries bulletins about funding opportunities, program launches, and office updates.

The Office of Critical Minerals and Energy Innovation is a division within the Department of Energy that focuses on advancing energy technology development and securing reliable supplies of critical minerals essential to energy systems and modern technologies. The office manages research programs, funding initiatives, and partnerships with industry, universities, laboratories, and other organizations.

The office's work spans multiple energy technology areas, including renewable energy, energy storage, grid modernization, and industrial applications. It also works to develop domestic supplies and refine the use of critical minerals—elements and compounds needed for technologies like batteries, solar panels, wind turbines, permanent magnets, and electric vehicle components—reducing dependence on foreign sources and supporting national economic resilience and energy independence.

Email bulletins from this office announce new funding opportunities for research and development projects, report on awarded grants and successful projects, provide updates on policy initiatives or program changes, publicize research findings or technology achievements, and offer guidance on application processes. Readers may see announcements of grant application deadlines for energy technology research or development, awards to projects developing new energy technologies or mineral processing and refining techniques, updates on critical minerals policy or initiatives, notices of public meetings or webinars, and summaries of published research. The bulletins reflect the office's role in directing federal energy innovation investments and advancing national energy security and technological competitiveness.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `doe-cmei-email` |
| Agency / parent organization | Department of Energy, Office of Critical Minerals and Energy Innovation |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.energy.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USEERE/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: energy-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 2 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-09-28T17:09:04Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-10-01 |
| Content length | 4,194 characters average, 4,194 median (shortest 2,009, longest 6,378) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 2 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-01 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

2 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-10-01 | 1 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Registered 2026-09-26 with three configured sender addresses; began delivering 2026-09-28. One bulletin ingested in full text (~2,009 characters) generating one item, with no errors or refusals. The collector maintains stable contact with the email system. A single bulletin is an insufficient sample to characterize completeness; the observed stream is the subscription's own coverage measure.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/nih-fogarty-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nih-fogarty-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nih-fogarty-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Fogarty International Center (email)

active · ingestion health: quiet · Executive · Tier 3 · email bulletin · Department of Health and Human Services (NIH / FIC)

Official site: https://www.fic.nih.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Fogarty International Center at NIH supports global-health research and researcher training. Its bulletins carry funding opportunities, research news, and program announcements in global health.

**Model-written orientation**

The Fogarty International Center at the National Institutes of Health supports research in global health and provides training for health researchers worldwide. Its email bulletins share funding opportunities, research news, and program announcements.

The Fogarty International Center (FIC) is a component of the National Institutes of Health within the Department of Health and Human Services. Fogarty supports the NIH's mission in global health research and international research training.

The National Institutes of Health is the primary federal research agency for medical and health research. Within NIH's structure, Fogarty serves a specific function: it promotes global health research and supports the international research enterprise. Fogarty funds research on infectious disease, non-communicable diseases, and other health priorities in low- and middle-income countries, and it supports programs that train health researchers from around the world.

Fogarty's email bulletins communicate with researchers, institutions, and others engaged in or interested in global health research. These bulletins carry announcements of funding opportunities for global health research, news about research projects and research findings in global health, program announcements and fellowship opportunities, and information about collaborative research initiatives.

Through its communications, Fogarty shares information about grant competitions and funding mechanisms for researchers working on global health challenges, updates on research supported by Fogarty and its partner organizations, opportunities for researcher training and exchange, and news on international research collaborations and capacity-building efforts.

Fogarty's public communications reach researchers, research institutions, universities, government agencies, and nonprofit organizations involved in or supporting global health research worldwide.

In this digest, readers will encounter Fogarty's official announcements drawn from its email bulletins—primarily funding opportunities, research news, and program information that Fogarty distributes to its audience of researchers and research organizations interested in global health.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nih-fogarty-email` |
| Agency / parent organization | Department of Health and Human Services (NIH / FIC) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.fic.nih.gov/ |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). The project mailbox received Fogarty bulletins over the changeover window (e.g. 'Funding news for global health researchers') carrying grant and research news. Subscribed through NIH's own flow (sender [address withheld]); exact topic selection is in the operator's subscription records, not transcribed here. DKIM recorded per message at ingest. |

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

**quiet** — Most recent item 2026-10-08, 11 days ago (quiet past 7 days).

This label has held since 2026-10-16T04:16:49Z (UTC) and was last re-checked 2026-10-19T03:57:17Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-10-08 |
| Content length | 892 characters average, 892 median (shortest 680, longest 1,105) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 2 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-08 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-10-08, 11 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 1 |
| 2026-10-07 | 0 |
| 2026-10-08 | 1 |
| 2026-10-09 | 0 |
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 0 |
| 2026-10-14 | 0 |
| 2026-10-15 | 0 |
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Fogarty International Center bulletins have been delivered to the project mailbox via ficinfo@subscriptions.nih.gov subscription since activation on 2026-10-01. Two bulletins were received: one on 2026-10-06 carrying 1105 characters and one on 2026-10-08 carrying 680 characters, averaging 892 characters per message. Both arrived in full-text email format with DKIM verification recorded at ingest. No delivery errors, refusals, or administrative complications have been recorded. Delivery cadence was sparse: two days between the first and second bulletins, followed by nine days of quiet through the current measurement window ending 2026-10-17. Since the previous assessment on 2026-10-07, the second bulletin arrived on 2026-10-08; the source has produced no further activity since then. Ingestion relies entirely on direct mailbox delivery with no HTTP requests to external services, and health is measured from email arrival recency alone. Measured delivery behavior remains consistent with initial activation observations.

_Model-written assessment of our own ingestion, generated 2026-10-17 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

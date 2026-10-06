<!-- Markdown twin of https://fapd.info/sources/nih-fogarty-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nih-fogarty-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nih-fogarty-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Fogarty International Center (email)

active · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Health and Human Services (NIH / FIC)

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-10-01T21:38:40Z (UTC) and was last re-checked 2026-10-06T03:59:42Z (UTC).

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

The Fogarty International Center at NIH was activated on 2026-10-01 based on observed bulletins during the late-September changeover carrying funding announcements and global-health research news. No messages have been recorded in the mailbox since activation. Messages are ingested through the email adapter via DKIM verification.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

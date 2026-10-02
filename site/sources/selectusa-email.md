<!-- Markdown twin of https://fapd.info/sources/selectusa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/selectusa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: selectusa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# SelectUSA (email)

active · ingestion health: no data · Executive · Tier 2 · email bulletin · Department of Commerce (International Trade Administration)

Official site: https://www.trade.gov/selectusa · All sources: [sources.md](../sources.md)

## What this source is

SelectUSA, within the International Trade Administration, promotes business investment into the United States. Its bulletins carry investment news, program updates, and event announcements.

**Model-written orientation**

SelectUSA is part of the International Trade Administration and works to attract foreign direct investment to the United States. Its email bulletins deliver news on investment opportunities, programs, and events.

SelectUSA operates within the International Trade Administration, a bureau of the Department of Commerce. SelectUSA promotes foreign direct investment in the United States.

The International Trade Administration sits within the Department of Commerce and works on U.S. international trade and investment matters. SelectUSA specifically focuses on foreign direct investment into the United States, serving as a coordinating entity that brings together federal, state, and local government resources with information and services for foreign investors.

SelectUSA distributes email bulletins to businesses, investors, and organizations interested in U.S. investment opportunities. These bulletins carry announcements about investment opportunities and sectors, updates on SelectUSA programs and initiatives, event announcements and networking opportunities, and information on U.S. business resources.

The communications share information about investment possibilities across different U.S. states and sectors, program updates affecting investment processes and the resources available to investors, and invitations to events, conferences, and webinars where foreign investors can connect with U.S. business and government officials.

SelectUSA's public communications reach investors, business organizations, state economic development agencies, and others interested in U.S. investment opportunities. The bulletins provide information about sectors and locations and connections between foreign investors and U.S. business opportunities.

In this digest, readers will see SelectUSA's official announcements drawn from its email bulletins—primarily investment news, program updates, and event notices that the organization publishes to its subscription audience.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `selectusa-email` |
| Agency / parent organization | Department of Commerce (International Trade Administration) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.trade.gov/selectusa |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). SelectUSA mail arrived from two sender addresses over the changeover window ([address withheld] and [address withheld]), both carrying 'SelectUSA News & Updates'-style investment news; both are listed on this one ITA entry. Subscribed through ITA's own flow; exact topic selection is in the operator's subscription records, not transcribed here. DKIM recorded per message at ingest. |

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

This label has held since 2026-10-01T21:38:40Z (UTC) and was last re-checked 2026-10-02T03:48:29Z (UTC).

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

SelectUSA from the International Trade Administration was activated on 2026-10-01 based on observed bulletins arriving during the late-September changeover from two sender addresses carrying investment news. No messages have been recorded in the mailbox since activation. Messages are ingested through the email adapter via DKIM verification.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

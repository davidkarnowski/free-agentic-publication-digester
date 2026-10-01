<!-- Markdown twin of https://fapd.info/sources/nifa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nifa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nifa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# National Institute of Food and Agriculture (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Agriculture, National Institute of Food and Agriculture

Official site: https://www.nifa.usda.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The National Institute of Food and Agriculture funds agricultural research, education, and extension. Its weekly update carries grant programs, funding opportunities, and agency news.

**Model-written orientation**

The National Institute of Food and Agriculture funds agricultural research, education, and extension programs across the country. This email source carries weekly bulletins about grant programs, funding opportunities, and agency news.

The National Institute of Food and Agriculture (NIFA) is an agency within the U.S. Department of Agriculture that funds and supports agricultural research, education, and extension programs. NIFA distributes competitive grants to universities, research institutions, and agricultural extension services, supporting work on agricultural productivity, environmental sustainability, food security, rural development, and related topics.

NIFA's funding supports a broad spectrum of agricultural and food-related research and education: crop and livestock production, soil and water management, pest and disease management, food safety and nutrition, agricultural economics and business, and rural community development. The agency works with the Cooperative Extension System and land-grant universities to translate research findings into practical knowledge and training for farmers, ranchers, agricultural professionals, and rural communities.

Email bulletins from NIFA announce grant funding opportunities and application deadlines, report on awarded grants and descriptions of funded projects, publicize significant research findings, announce new initiatives or programs, and provide updates on agency priorities and activities. Readers may see announcements of competitive grant deadlines in areas such as crop and livestock research, sustainable agriculture and natural resources, food safety and security, agricultural innovation and technology, and rural development; notices of grant awards and descriptions of funded research projects; invitations to webinars, workshops, or training events; and updates on NIFA programs, priorities, or policy developments. The bulletins reflect the agency's role in directing federal agricultural research and education investments and supporting the agricultural science enterprise.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nifa-email` |
| Agency / parent organization | Department of Agriculture, National Institute of Food and Agriculture |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.nifa.usda.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDANIFA/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: agriculture-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-09-30, delivered by email.

This label has held since 2026-09-30T21:44:29Z (UTC) and was last re-checked 2026-10-01T03:53:55Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-09-30 |
| Content length | 10,041 characters average, 10,041 median (shortest 10,041, longest 10,041) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-09-30 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-09-30, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-09-30 | 1 |
| 2026-10-01 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

This source delivers bulletins through GovDelivery email subscription. The previous assessment from 2026-09-27 recorded zero bulletins after the 2026-09-26 registration date. As of 2026-10-01, the source has delivered one bulletin on 2026-09-30 during UTC hour 17. The bulletin contained 10,041 characters in full-text format. The collector has maintained stable mailbox access throughout with no delivery errors. No delivery pattern beyond the single observation is yet apparent. Gate-3 coverage evaluation proceeds with the first ingested bulletin. Related sources that may publish the same news include agriculture-email; items duplicated at the same URL merge as corroboration, while the same event at different URLs are listed separately.

_Model-written assessment of our own ingestion, generated 2026-10-01 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

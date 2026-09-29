<!-- Markdown twin of https://fapd.info/sources/nifa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nifa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nifa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# National Institute of Food and Agriculture (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Agriculture, National Institute of Food and Agriculture

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

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

This source delivers bulletins through the project mailbox using the GovDelivery platform. Subscription was confirmed through the publisher's signup flow in September 2026, and the source was registered for automated ingestion on 2026-09-26. Bulletins matching this sender were already present in the mailbox before registration; ingestion begins with the first poll following deployment. No bulletins have been recorded from this source since registration. The collector has accessed the mailbox without errors, observing zero messages associated with this source across the past week. No delivery pattern, cadence, or format characteristics are yet observable. Gate-3 coverage evaluation awaits the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

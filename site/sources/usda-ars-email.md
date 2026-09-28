<!-- Markdown twin of https://fapd.info/sources/usda-ars-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usda-ars-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usda-ars-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Agricultural Research Service (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Agriculture, Agricultural Research Service

Official site: https://www.ars.usda.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Agricultural Research Service is USDA's in-house research agency. Its news service bulletins report research findings.

**Model-written orientation**

The Agricultural Research Service is the U.S. Department of Agriculture's in-house science agency, conducting research on crops, animals, soils, and agricultural systems. This email source carries bulletins reporting research findings and scientific discoveries.

The Agricultural Research Service (ARS) is USDA's chief research agency, employing scientists who conduct basic and applied research to address challenges in agriculture and food production. ARS operates laboratories and research facilities across the United States, working on topics ranging from crop diseases and livestock health to soil conservation and sustainable farming practices.

ARS's research portfolio spans plant breeding and genetics, animal health and nutrition, pest and weed management, soil and water conservation, food safety, and agricultural economics. The agency develops and tests new crop varieties, management practices, and technologies intended to improve agricultural productivity and sustainability. ARS publishes findings through scientific journals, technical reports, and public announcements, making its work accessible to farmers, industry professionals, researchers, policymakers, and the general public.

Email bulletins from ARS publicize major research findings, new technologies or tools developed at ARS laboratories, announcements of scientific meetings or training opportunities, and updates on ongoing research initiatives. Readers may see announcements of new crop varieties or animal breeds developed through ARS research, advances in livestock health management or production practices, findings about soil health and conservation techniques, food safety research results, and notices of public events, data releases, or collaboration opportunities. The bulletins reflect the agency's mission to conduct research that strengthens American agriculture and addresses production, sustainability, and food system challenges.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usda-ars-email` |
| Agency / parent organization | Department of Agriculture, Agricultural Research Service |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.ars.usda.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDAARS/subscriber/new |
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

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-28T03:57:50Z (UTC).

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

This source was registered on 2026-09-26 via the GovDelivery email subscription service. No bulletins have been recorded since registration. The collector has maintained stable contact with the email system throughout the measurement period (2026-09-21 through 2026-09-27) with no errors reported. The mailbox log shows zero messages, zero administrative entries, and zero refused messages. Gate-3 coverage evaluation is pending first ingested bulletins. Related sources that can publish the same news include agriculture-email; duplicate items at the same URL will merge as corroboration, while the same event published at different URLs will be listed separately.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

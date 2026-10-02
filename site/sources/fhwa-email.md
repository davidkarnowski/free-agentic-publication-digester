<!-- Markdown twin of https://fapd.info/sources/fhwa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fhwa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fhwa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Highway Administration (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Transportation, Federal Highway Administration

Official site: https://highways.dot.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Federal Highway Administration funds and oversees the national highway system. Its bulletins carry program notices and announcements.

**Model-written orientation**

The Federal Highway Administration funds and oversees the national highway system and related transportation infrastructure. Its emails carry program notices and announcements.

The Federal Highway Administration (FHWA) is a bureau within the Department of Transportation responsible for the federal-aid highway program and the management of the National Highway System. FHWA provides federal funding for highway construction, maintenance, and improvements; establishes highway safety standards; oversees federal-aid project approvals; and conducts research on highway technology and practices. The National Highway System encompasses Interstate highways, major arterial routes, and strategic connections comprising roughly 4 percent of the nation's road network but carrying over 40 percent of traffic.

FHWA administers federal transportation funds distributed to states through various programs. The primary mechanism is the federal-aid highway program, through which states receive apportionments based on formulas considering population, area, and road miles. States use these funds for construction and maintenance of eligible roads, typically with local matching funds. FHWA also administers discretionary grant programs for specific purposes such as bridge replacement, safety improvements, and transportation innovation. The agency must approve major projects and certifies that states are complying with federal requirements before releasing funds.

Beyond funding, FHWA establishes technical standards for highway design, construction, and maintenance; establishes safety standards for traffic control devices and work zones; oversees the Manual on Uniform Traffic Control Devices; and conducts safety oversight including reviewing safety performance data. The agency also administers the Federal Highway Beautification Program, which addresses outdoor advertising along highways, and supports various environmental and sustainability initiatives in highway planning and design.

When FHWA appears in the digest, you will see announcements of grant solicitations and deadlines, notices of funding availability, program guidance and policy updates, safety standards and technical directives, research announcements, and updates on FHWA initiatives. You may also see notices of rule changes affecting highway projects, environmental guidance, or special programs addressing specific transportation needs.

FHWA announcements are relevant to state departments of transportation, local transportation agencies, consulting engineers and construction companies, advocacy organizations focused on transportation, environmental groups, and communities affected by highway projects.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fhwa-email` |
| Agency / parent organization | Department of Transportation, Federal Highway Administration |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://highways.dot.gov/ |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]); no bulletin observed as of registration (2026-09-26). Registered so the first bulletin is attributed on arrival; activate on first parsed bulletin. Related entries that can publish the same news: transportation-email, transportation-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-10-02T03:48:29Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter. Registered 2026-09-26 with sender usdotfhwa@info.dot.gov. The registry notes no bulletin was observed at the time of registration; the source was registered to attribute the first bulletin on arrival. As of 2026-09-27, no bulletins have been received or parsed; the collector shows zero items. Status is planned and will activate on the first parsed bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

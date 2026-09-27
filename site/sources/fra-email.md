<!-- Markdown twin of https://fapd.info/sources/fra-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fra-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fra-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Railroad Administration (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Transportation, Federal Railroad Administration

Official site: https://railroads.dot.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Federal Railroad Administration regulates railroad safety and funds rail programs. Its bulletins carry safety and program announcements.

**Model-written orientation**

The Federal Railroad Administration regulates railroad safety and distributes federal rail funding, publishing safety directives and program announcements.

The Federal Railroad Administration (FRA) is an agency of the Department of Transportation responsible for regulating passenger and freight railroad operations across the United States. The FRA sets and enforces safety standards for all U.S. railroads, reviews railroad safety plans, investigates accidents, and administers federal funding for rail infrastructure and development.

The FRA's safety mission encompasses a broad range of railroad operations, including track integrity, signal systems, locomotive equipment, crew qualifications, hazardous materials transport, and grade crossing safety. The agency develops and issues safety directives, technical guidance, and research findings to the railroad industry and the public. Beyond regulation, the FRA administers several federal funding programs supporting rail development, including grants for passenger rail service, capital improvements to rail corridors, and rail research initiatives. The agency also coordinates with state transportation departments on matters affecting their rail systems.

The bulletins from the FRA that appear in this digest cover administrative announcements, safety advisories, funding opportunity notices, and program updates. You may encounter notices about new safety standards, grant applications opening or closing, meeting announcements, regulatory guidance, or updates to existing programs. The FRA publishes these bulletins to keep railroads, rail employees, state agencies, and the public informed of regulatory changes, funding availability, and safety requirements.

The FRA is distinct from Amtrak, the national passenger rail operator, and from state rail authorities, though the FRA maintains a coordinating role with both. The FRA's sister agencies within the Department of Transportation include the Federal Highway Administration, Federal Aviation Administration, and Federal Transit Administration.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fra-email` |
| Agency / parent organization | Department of Transportation, Federal Railroad Administration |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://railroads.dot.gov/ |
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

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-27T03:49:31Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter. Registered 2026-09-26 with sender usdotfra@info.dot.gov. The registry notes no bulletin was observed at the time of registration; the source was registered to attribute the first bulletin on arrival. As of 2026-09-27, no bulletins have been received or parsed; the collector shows zero items. Status is planned and will activate on the first parsed bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

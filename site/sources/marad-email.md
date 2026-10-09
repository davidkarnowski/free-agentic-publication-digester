<!-- Markdown twin of https://fapd.info/sources/marad-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/marad-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: marad-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Maritime Administration (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Transportation, Maritime Administration

Official site: https://www.maritime.dot.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Maritime Administration supports the U.S. merchant marine, ports, and shipbuilding. Its bulletins carry program and funding announcements.

**Model-written orientation**

The Maritime Administration supports U.S. merchant shipping, ports, and shipbuilding, publishing program and funding announcements.

The Maritime Administration (MARAD) is an agency of the Department of Transportation that supports the U.S. merchant marine—the commercial shipping industry—along with port development and domestic shipbuilding. MARAD administers federal maritime funding programs, manages the National Defense Reserve Fleet, and works to maintain America's maritime capability for both commercial and national security purposes.

MARAD's responsibilities include administering loans and grants for ship construction and modernization, supporting domestic shipping through operating-differential subsidies, managing cargo preference policies that reserve certain government cargo for U.S. vessels, and supporting port infrastructure development. The agency also administers maritime training programs and workforce development initiatives to support the maritime workforce.

The bulletins from MARAD that appear in this digest cover funding opportunities, grant announcements, program updates, meeting notices, and administrative decisions. You may see notices about loan applications opening or closing, grants available for port or ship projects, maritime workforce program updates, policy guidance, or announcements related to shipping regulations and maritime commerce.

MARAD operates within the Department of Transportation alongside the Federal Railroad Administration, Federal Highway Administration, and other transportation agencies. The agency coordinates with the U.S. Coast Guard, which handles maritime safety, vessel inspections, and law enforcement on the water, though the organizations maintain distinct missions and responsibilities.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `marad-email` |
| Agency / parent organization | Department of Transportation, Maritime Administration |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.maritime.dot.gov/ |
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

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-10-09T03:52:22Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter. Registered 2026-09-26 with sender marad@info.dot.gov. The registry notes no bulletin was observed at the time of registration; the source was registered to attribute the first bulletin on arrival. As of 2026-09-27, no bulletins have been received or parsed; the collector shows zero items. Status is planned and will activate on the first parsed bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

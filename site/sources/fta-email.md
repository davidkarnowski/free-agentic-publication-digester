<!-- Markdown twin of https://fapd.info/sources/fta-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fta-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fta-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Federal Transit Administration (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Transportation, Federal Transit Administration

Official site: https://www.transit.dot.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Federal Transit Administration funds and oversees public transportation. Its bulletins carry safety advisories, program notices, and funding announcements.

**Model-written orientation**

The Federal Transit Administration funds and oversees public transportation systems nationwide. Its emails carry safety advisories, program notices, and funding announcements.

The Federal Transit Administration (FTA) is a bureau within the Department of Transportation responsible for administering federal funding programs and oversight of public transportation systems. FTA provides grants and financing to states and local transit agencies for capital projects (buses, rail vehicles, stations), operations support, research, and planning. The agency also establishes and enforces safety standards for transit systems and oversees compliance with federal transit requirements.

FTA's grant programs support the full spectrum of public transportation modes: fixed-route buses, light rail, commuter rail, heavy rail, ferries, and demand-responsive systems. Funding is available for vehicle acquisition, station construction and rehabilitation, technology systems, accessibility improvements, workforce training, and transit-oriented development. The agency also provides financing tools including loans and credit assistance programs to supplement traditional grants.

Beyond capital funding, FTA establishes federal safety standards for transit systems, oversees safety certification programs, and investigates safety incidents. The agency also coordinates with the National Transportation Safety Board on major transit accidents. FTA maintains data on transit system performance and ridership trends, publishes guidance and technical assistance materials for transit agencies, and supports research on transit technology and practice.

When FTA appears in the digest, you will see grant solicitation announcements with deadlines, grant awards, safety directives and advisories, technical assistance notices, program updates, research reports, and policy guidance documents. You may also see notices of rule changes or new requirements affecting transit agencies, or announcements of special initiatives such as those addressing climate goals or equity.

FTA announcements are relevant to transit agencies and authorities, city and county governments supporting transit, transit worker organizations, organizations serving people with disabilities and transportation-dependent populations, and private companies in the transit industry. Safety advisories can affect transit operations immediately, while grant solicitations have specific application deadlines.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fta-email` |
| Agency / parent organization | Department of Transportation, Federal Transit Administration |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.transit.dot.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDOTFTA/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: transportation-email, transportation-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

Subscription bulletins to the project mailbox, ingested by the email adapter. Registered 2026-09-26 with sender usdotfta@info.dot.gov. The registry notes mail was observed in the project mailbox prior to registration but earlier bulletins are not backfilled. As of 2026-09-27, no bulletins from this source have been parsed and stored; the collector shows zero items. Status is planned, with gate-3 coverage evaluation pending the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

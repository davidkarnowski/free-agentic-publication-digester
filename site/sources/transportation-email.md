<!-- Markdown twin of https://fapd.info/sources/transportation-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/transportation-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: transportation-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Transportation Press Releases (email)

planned · Executive · Tier 1 · email bulletin · Department of Transportation

Official site: https://www.transportation.gov/briefing-room · All sources: [sources.md](../sources.md)

## What this source is

The Department of Transportation sets national transportation policy and oversees the modal administrations governing aviation, highways, rail, transit, pipelines, and maritime commerce. Its departmental bulletins carry press releases, grant awards, and safety announcements.

**Model-written orientation**

The Department of Transportation sets national transportation policy and oversees aviation, highways, rail, transit, pipeline, and maritime transportation. Its subscription bulletins carry press releases on policy initiatives, grant awards, and safety announcements.

The Department of Transportation (DOT) is a cabinet-level agency responsible for federal transportation policy and regulation. The department is organized around seven modal administrations, each overseeing a specific transportation sector: the Federal Aviation Administration (aviation), Federal Highway Administration (roads and highways), Federal Railroad Administration (rail), Federal Transit Administration (public transit), Pipeline and Hazardous Materials Safety Administration (pipelines and hazmat), Maritime Administration (maritime commerce), and the Motor Carrier Safety Administration (commercial trucks and buses). The DOT also houses other offices including the National Highway Traffic Safety Administration, which regulates vehicle safety.

The DOT sets policies affecting the planning and operation of transportation systems, oversees funding mechanisms (including the Highway Trust Fund), and coordinates transportation policy with states and localities. The Secretary of Transportation chairs the department and advises the President on transportation matters.

The DOT departmental office distributes a subscription bulletin service to which this project subscribes. The bulletins report on departmental policy announcements, grant awards to states and localities for transportation infrastructure and operations, safety initiatives, and regulatory actions. The content reflects the department's broad jurisdiction across transportation modes and its coordination role among the modal administrations, states, and the private sector.

Additionally, the modal administrations themselves operate their own bulletin services, which this project may subscribe to separately if content evaluation indicates distinct action streams warranting separate coverage. Those services would report on mode-specific policy, rule changes, and safety initiatives.

Readers will see announcements spanning multiple transportation sectors—aviation safety, highway funding, rail policy, transit grants, pipeline safety—reflecting the department's role as the federal coordinating point for all major transportation modes.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `transportation-email` |
| Agency / parent organization | Department of Transportation |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.transportation.gov/briefing-room |
| URL (signup) | https://public.govdelivery.com/accounts/USDOT/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of transportation-newsroom, which returns HTTP 403 to our identified client. Modal-administration lists also subscribed and confirmed under the same platform, to be split into their own entries if content evaluation shows distinct action streams: FRA, FHWA, FTA, FMCSA, PHMSA, MARAD, and the DOT Inspector General. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-26 | 1 |
| 2026-08-27 | 0 |
| 2026-08-28 | 0 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 0 |
| 2026-09-01 | 0 |
| 2026-09-02 | 0 |
| 2026-09-03 | 0 |
| 2026-09-04 | 0 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 0 |
| 2026-09-09 | 0 |
| 2026-09-10 | 1 |
| 2026-09-11 | 0 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 0 |
| 2026-09-15 | 0 |
| 2026-09-16 | 0 |
| 2026-09-17 | 0 |
| 2026-09-18 | 1 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 0 |
| 2026-09-22 | 0 |
| 2026-09-23 | 0 |
| 2026-09-24 | 0 |

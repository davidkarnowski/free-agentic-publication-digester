<!-- Markdown twin of https://fapd.info/sources/ofac-recent-actions.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ofac-recent-actions.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ofac-recent-actions)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# OFAC Recent Actions

planned · Executive · Tier 2 · HTML index · Department of the Treasury (OFAC)

Official site: https://ofac.treasury.gov/recent-actions · All sources: [sources.md](../sources.md)

## What this source is

The Office of Foreign Assets Control publishes sanctions designations, delistings, and general licenses on its recent-actions index — high-consequence official actions currently invisible to the pipeline except as delayed Federal Register notices.

**Model-written orientation**

The Office of Foreign Assets Control publishes official sanctions designations, delistings, and policy directives on its recent actions index.

The Office of Foreign Assets Control (OFAC), a division of the Department of the Treasury, administers and enforces economic sanctions policies authorized by Congress and the President. These sanctions restrict financial transactions with designated countries, entities, and individuals under various federal statutes and executive authorities, serving as a tool of foreign policy and national security.

OFAC's recent actions index publishes official designations—formal determinations adding entities or individuals to sanctions lists subject to transaction restrictions—and delistings, when sanctions are lifted and transaction restrictions are removed. The agency also issues general licenses, which are policy directives specifying exceptions, modifications, or clarifications to how sanctions restrictions apply in particular contexts.

Sanctions designations and delistings are high-consequence official actions: they directly restrict or enable financial transactions with specific persons or organizations and carry legal and commercial implications for banks, businesses, and other entities conducting international transactions. A designation typically prevents U.S. financial institutions and persons from engaging in transactions with the designated entity. General licenses represent policy decisions about how sanctions authorities will be applied—for example, permitting humanitarian transactions with a sanctioned country or clarifying the scope of a restriction.

OFAC publishes these actions as official notices through multiple channels and maintains a consolidated index on its website. Each action is dated and described in official legal language, forming a continuous record of sanctions policy decisions.

For readers tracking federal government action in foreign policy and economic governance, OFAC publications represent the official record of sanctions designations, delistings, and related policy decisions—actions carrying direct legal effect and significant international implications.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ofac-recent-actions` |
| Agency / parent organization | Department of the Treasury (OFAC) |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://ofac.treasury.gov/recent-actions |
| URL (index) | https://ofac.treasury.gov/recent-actions |
| Registered | 2026-07-28 |
| Registry notes | OFAC retired its RSS 2025-01-31 (own notice) in favor of GovDelivery email; the recent-actions HTML index remains. Probed 2026-07-31 17:44Z: HTTP 200, robots allowed, index captured. Re-probed 2026-07-31 23:57Z for activation and the host would not serve robots.txt at all — five attempts, every one closed without a response — so the client fell closed and fetched nothing, which is the correct posture (GUIDE §4) and not something to retry into submission. The adapter itself is ready: against the 17:44Z capture it reads 11 dated actions (prose 'July 30, 2026'), correctly dropping the per-entry 'Sanctions List Updates' category link that repeats in every block. Stays planned pending a robots.txt that answers; recheck before any activation. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 43 article link(s); 4 dated inside the 7-day lookback, 7 dated outside it, 32 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | html-index adapter via AgencyClient — parses cleanly against captured bytes, but the host would not serve robots.txt on 2026-07-31, so nothing is fetched. |
| Adapter | html-index |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to ofac.treasury.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

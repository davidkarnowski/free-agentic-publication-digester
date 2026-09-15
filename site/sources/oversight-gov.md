<!-- Markdown twin of https://fapd.info/sources/oversight-gov.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/oversight-gov.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: oversight-gov)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Oversight.gov IG Reports

planned · Executive · Tier 1 · aggregator · Council of the Inspectors General on Integrity and Efficiency

Official site: https://www.oversight.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Council of the Inspectors General on Integrity and Efficiency operates oversight.gov as a central aggregator. It republishes audit, inspection, and investigative reports from roughly 70 federal Offices of Inspector General, with new reports posted most business days; every item originates on an individual IG's own site.

**Model-written orientation**

Oversight.gov is a central aggregator published by the Council of Inspectors General on Integrity and Efficiency, republishing audit, inspection, and investigative reports from federal Inspectors General.

Inspectors General are independent statutory offices within federal agencies and departments, established by law to conduct audits, inspections, and investigations of agency activities. Each Inspector General is appointed by the President (with Senate confirmation for most agencies) and reports to both the agency head and Congress. The Inspector General Act of 1978 established the IG system and gave these offices broad authority to investigate fraud, waste, and abuse in their respective agencies.

Oversight.gov serves as a centralized clearinghouse for Inspectors General reports, published by the Council of the Inspectors General on Integrity and Efficiency (CIGIE), a statutory council that coordinates IG activities across roughly 70 federal Inspectors General. The site republishes reports from individual IGs shortly after they are released by those offices, making them accessible through a single consolidated index rather than requiring readers to visit dozens of separate agency IG sites.

Inspector General reports typically include audits of agency programs and financial controls, investigations into alleged misconduct or improper agency actions, evaluations of agency effectiveness, and reviews of major initiatives. Reports cover topics ranging from program performance to financial stewardship to management practices. The reports are factual and technical in nature, presenting findings and recommendations for corrective action.

Oversight.gov provides readers with immediate notice of Inspector General investigations and audits across the federal government. It serves as the primary disclosure mechanism for IG findings that may affect public understanding of how agencies operate. Because each report originates from an independent Inspector General office, the aggregate collection provides a cross-government perspective on agency performance, control systems, and areas flagged for improvement.

Readers of this source encounter the full range of government operations as examined by independent oversight offices—financial controls, program effectiveness, personnel matters, and agency compliance with law and regulation.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `oversight-gov` |
| Agency / parent organization | Council of the Inspectors General on Integrity and Efficiency |
| Branch | executive |
| Type | aggregator |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.oversight.gov/ |
| Registered | 2026-07-26 |
| Registry notes | Aggregator source class: content is republished, so digest citations must point to the originating IG. Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | aggregator |
| Method | HTML index diff via AgencyClient (pending content evaluation); aggregator rule: every ingested item must cite the originating Inspector General as its origin, never oversight.gov itself. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.oversight.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

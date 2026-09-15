<!-- Markdown twin of https://fapd.info/sources/docs-house-gov.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/docs-house-gov.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: docs-house-gov)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# House Document Repository (floor + committee)

planned · Legislative · Tier 1 · XML index · U.S. House of Representatives

Official site: https://docs.house.gov/floor/ · All sources: [sources.md](../sources.md)

## What this source is

docs.house.gov publishes 'Bills This Week' — legislation expected on the House floor — as weekly XML files, plus the Committee Repository of scheduled committee meetings with documents (PDF+XML). The pipeline's first forward-looking source: everything currently ingested is retrospective.

**Model-written orientation**

The House of Representatives publishes weekly schedules of legislation expected on the House floor and a repository of scheduled committee meetings with associated documents.

The U.S. House of Representatives is one of two chambers of Congress responsible for introducing and voting on federal legislation. It comprises 435 members representing the states apportioned by population. The House Document Repository provides advance notice and documentation of legislative activity through two primary channels, offering a window into the chamber's forthcoming work.

"Bills This Week" is a weekly publication indicating which bills the House floor plans to consider in the coming week—a preview of the legislative calendar sometimes weeks in advance. This allows the public, advocacy groups, and other stakeholders to anticipate which measures are under active consideration by the chamber and prepare responses or advocacy as appropriate.

The Committee Repository documents the schedule of House committee meetings across all committees and subcommittees. Committees are where much of the detailed legislative work happens: members examine bills in depth, hear testimony from witnesses and experts, and draft amendments before measures proceed to the full House floor for a vote. The repository includes not only meeting schedules but the associated documents—hearing materials, draft committee reports, and procedural records—that inform committee deliberations.

Both components are published as structured data files, making them suitable for systematic monitoring of the House's legislative agenda. The House publishes this material as a forward-looking resource—what will happen, rather than what has already happened—complementing the retrospective record of enacted laws and floor votes published elsewhere in the federal record.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `docs-house-gov` |
| Agency / parent organization | U.S. House of Representatives |
| Branch | legislative |
| Type | XML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://docs.house.gov/floor/ |
| URL (index) | https://docs.house.gov/committee/ |
| Registered | 2026-07-28 |
| Registry notes | Help documentation describes well-formed self-describing XML (search-corroborated 2026-07-28; direct fetch 403'd the research tool — our identified client may differ; probe decides). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | XML index |
| Method | Would poll the weekly floor XML and committee-repository listings and diff. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to docs.house.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

<!-- Markdown twin of https://fapd.info/sources/nasa-image-library.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nasa-image-library.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nasa-image-library)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NASA Image and Video Library

planned · Executive · Tier 2 · API · Independent agency

Official site: https://images.nasa.gov · All sources: [sources.md](../sources.md)

## What this source is

NASA's consolidated media library and API (images-api.nasa.gov): current mission imagery, video, and audio with titles, descriptions, keywords, and per-asset manifests offering original/medium/small renditions plus caption files for video. A continuous news-flow of new visual assets alongside the historical archive.

**Model-written orientation**

NASA's consolidated image and video library provides mission photographs, video, and audio content with comprehensive metadata and multiple resolution options.

The National Aeronautics and Space Administration maintains a consolidated digital library of imagery and video from space missions, Earth observation, and scientific research. The library serves as both a current news source for mission imagery and a deep archive of historical content.

NASA's ongoing missions continuously generate new visual content: photographs and video from human spaceflight missions, robotic planetary and lunar exploration, Earth-observing satellites, telescope observations, and scientific research. This content is published with titles, descriptions, keywords, and technical metadata describing the subject, mission, and origin of each asset.

The image library provides multiple resolution versions of images and comprehensive metadata for video content, including captions. This structured approach makes content suitable for various uses—from news publication to educational application to scientific reference.

Content flows from multiple NASA centers and missions: human spaceflight operations, planetary science missions, Earth science observations, astrophysics missions, and aeronautics research. Each asset carries information about its origin and context within a particular mission or research program.

The library represents a continuous stream of new visual documentation of space exploration and Earth observation alongside decades of accumulated mission imagery. Content is generally not subject to copyright restrictions and is intended for public use.

For readers following federal government activity, NASA's image library represents the government's visual documentation of space exploration and Earth science—current mission imagery alongside the ongoing record of American space activity.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nasa-image-library` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | API |
| Status | planned |
| Tier | 2 |
| URL (home) | https://images.nasa.gov |
| URL (index) | https://images-api.nasa.gov/search |
| Registered | 2026-07-28 |
| Registry notes | API spec PDF (v1.22.0) fetched 2026-07-28: /search, /asset/{nasa_id}, /metadata, /captions endpoints; keyless; Collection+JSON. Second multi-modal source after DVIDS proves the schema path — weaker on every axis (no since-filter, no structured credit/branch apparatus, slower news cadence) but documented and open. NASA media guidelines: generally not copyrighted, no-endorsement rule. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Would search date-windowed (no changed-since filter documented; client-side dedupe), fetching asset manifests for selected items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to images-api.nasa.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

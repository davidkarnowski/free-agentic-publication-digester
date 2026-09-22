<!-- Markdown twin of https://fapd.info/sources/whitehouse-briefing-room.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/whitehouse-briefing-room.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: whitehouse-briefing-room)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# White House Briefing Room

planned · Executive · Tier 1 · HTML index · Executive Office of the President

Official site: https://www.whitehouse.gov/briefing-room/ · All sources: [sources.md](../sources.md)

## What this source is

The White House briefing room is the Executive Office of the President's direct publication channel. It carries statements, releases, remarks, and presidential actions — executive orders and proclamations as first announced, ahead of their official compilation in DCPD — typically several items per day.

**Model-written orientation**

The White House Briefing Room is the Executive Office of the President's primary publication channel, carrying presidential statements, remarks, press releases, and official presidential actions. Content typically includes several items per day.

The White House Briefing Room serves as the Executive Office of the President's official publication channel for presidential communications and official actions. The briefing room publishes the President's official statements, remarks, press releases, and notices of executive actions. This channel carries the President's direct communications to the public and official records of presidential decisions and actions.

Readers will encounter presidential statements and remarks on policy, legislation, national events, and matters of presidential concern; press releases announcing presidential decisions, policy initiatives, and administrative actions; official notices regarding executive orders and proclamations issued by the President; and announcements on administration initiatives, priorities, and policy direction. The briefing room also carries remarks and speeches delivered by the President at public events, state dinners, campaign events, and other official occasions, as well as announcements of presidential appointments, honors, and official recognitions.

Presidential actions such as executive orders and proclamations are often released through the White House Briefing Room before appearing in their official compilation in the Daily Compilation of Presidential Documents (DCPD), which is the authoritative permanent record maintained by the Government Publishing Office. The briefing room thus represents the first-published form of these official actions. Content appears regularly, typically with several items published per day reflecting the President's schedule and official activities.

Each item is dated with the date and time of publication assigned by the White House. Readers encounter the President's official communications and actions in their initial published form through this channel. The briefing room serves as a central repository of presidential statements and official actions, providing the public with direct access to the President's official communications and decisions.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `whitehouse-briefing-room` |
| Agency / parent organization | Executive Office of the President |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.whitehouse.gov/briefing-room/ |
| Registered | 2026-07-26 |
| Registry notes | Fast channel: the official compilation of the same material arrives later via the planned govinfo DCPD collection. Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Research 2026-07-28: site confirmed WordPress (~2-3 items/day); the platform's /feed/ convention may be live or disabled (the first Trump-era site disabled WP RSS) — one feed-URL check at probe settles it. For presidential documents specifically, the Federal Register API's public-inspection endpoint (see federal-register-api) is the structured, official near-same-day channel and may obviate scraping this site. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 87 article link(s); 10 dated inside the 7-day lookback, 0 dated outside it, 77 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | HTML index diff via AgencyClient (pending content evaluation) |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

- **Our requests to www.whitehouse.gov, all time (since 2026-08-06):** 2,615 request(s) · 2,608 answered · 7 returned no content

This host serves 2 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.whitehouse.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-08-24 | 0 | 55 | 64 |
| 2026-08-25 | 0 | 52 | 40 |
| 2026-08-26 | 0 | 55 | 57 |
| 2026-08-27 | 0 | 55 | 52 |
| 2026-08-28 | 0 | 52 | 43 |
| 2026-08-29 | 0 | 51 | 43 |
| 2026-08-30 | 0 | 53 | 54 |
| 2026-08-31 | 0 | 51 | 54 |
| 2026-09-01 | 0 | 51 | 44 |
| 2026-09-02 | 0 | 56 | 113 |
| 2026-09-03 | 0 | 53 | 214 |
| 2026-09-04 | 0 | 55 | 72 |
| 2026-09-05 | 0 | 63 | 101 |
| 2026-09-06 | 0 | 51 | 52 |
| 2026-09-07 | 0 | 52 | 50 |
| 2026-09-08 | 0 | 58 | 67 |
| 2026-09-09 | 0 | 52 | 49 |
| 2026-09-10 | 0 | 51 | 77 |
| 2026-09-11 | 0 | 51 | 64 |
| 2026-09-12 | 0 | 55 | 63 |
| 2026-09-13 | 0 | 51 | 44 |
| 2026-09-14 | 0 | 58 | 140 |
| 2026-09-15 | 0 | 53 | 46 |
| 2026-09-16 | 0 | 56 | 49 |
| 2026-09-17 | 0 | 56 | 69 |
| 2026-09-18 | 0 | 54 | 81 |
| 2026-09-19 | 0 | 51 | 42 |
| 2026-09-20 | 0 | 53 | 40 |
| 2026-09-21 | 0 | 57 | 72 |
| 2026-09-22 | 0 | 2 | 40 |

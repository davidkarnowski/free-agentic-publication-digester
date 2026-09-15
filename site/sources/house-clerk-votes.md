<!-- Markdown twin of https://fapd.info/sources/house-clerk-votes.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/house-clerk-votes.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: house-clerk-votes)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# House Clerk roll-call votes

planned · Legislative · Tier 1 · XML index · Clerk of the House of Representatives

Official site: https://clerk.house.gov/Votes · All sources: [sources.md](../sources.md)

## What this source is

Every House roll-call vote as XML at clerk.house.gov/evs/{year}/roll{NNN}.xml with a yearly index — published same-day, examples back to 2001. Pairs with the Congress.gov API's beta house-vote endpoint as a cross-check.

**Model-written orientation**

The House Clerk publishes XML files containing complete voting records for every House roll-call vote, updated daily and with historical records available back to 2001.

The House of Representatives maintains an official record of all roll-call votes taken on the House floor. The Clerk of the House, the chief administrative officer of the House, publishes these votes through the House's official web services in machine-readable XML format.

Each House roll-call vote is published as a separate XML file containing the complete voting record for that vote. The XML file includes the date and description of what was voted on, the voting tally (how many voted yes and no), and a member-by-member record showing how each of the 435 representatives voted. These files follow a consistent and documented XML schema that makes them suitable for programmatic access and analysis.

The House Clerk publishes new vote files the same day votes are taken, ensuring the record is current. Historical vote files are available dating back to 2001, spanning multiple Congresses and providing a long-term record of House voting activity.

The vote files are organized by year and follow a documented naming convention that allows automated systems to predict file locations and construct queries. The House Clerk maintains an index of votes within each year.

The House Clerk vote files represent the official record of roll-call votes as maintained by the House of Representatives itself. They serve as the authoritative source for House voting records and offer an alternative access method to other House vote data. This source complements the Senate XML services, which provide the equivalent voting records for the Senate. Together, the House Clerk votes and Senate XML services provide access to recorded votes in both chambers of Congress from the official sources maintained by the legislative chambers themselves.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `house-clerk-votes` |
| Agency / parent organization | Clerk of the House of Representatives |
| Branch | legislative |
| Type | XML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://clerk.house.gov/Votes |
| URL (index) | https://clerk.house.gov/evs/2026/index.asp |
| Registered | 2026-07-28 |
| Registry notes | Vote XML files verifiably exist and are indexed (2026-07-28). The formal schema documentation lives on xml.house.gov, which 403'd research fetchers — read it via our identified client at probe. 2026-07-31, live: the per-vote XML is confirmed (evs/2026/roll283.xml → 200 text/xml, 82,500 bytes, full metadata + member positions) and clerk.house.gov publishes NO robots.txt (404, nothing disallowed), but the YEAR INDEX IS HTML, NOT XML — evs/2026/index.asp is a 7 KB <TABLE> of ~15 recent votes linking to cgi-bin/vote.asp, evs/2026/index.xml is 404, and clerk.house.gov/Votes is a 249 KB JavaScript application. So this entry needs the html-index adapter (plan Phase 5), not the xml-index one that activated senate-xml; it stays planned rather than ship half-understood. Type stays xml-index because the per-vote records are XML; revisit the type when the index adapter lands. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | XML index |
| Method | Would walk the numeric roll-call sequence from a watermark, fetching new vote XML files. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to clerk.house.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

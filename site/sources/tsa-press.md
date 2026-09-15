<!-- Markdown twin of https://fapd.info/sources/tsa-press.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/tsa-press.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: tsa-press)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# TSA Press Releases

planned · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.tsa.gov/news/press/releases · All sources: [sources.md](../sources.md)

## What this source is

The Transportation Security Administration, within DHS, secures transportation systems, chiefly through aviation screening. Its press-release index carries announcements on screening policy, checkpoint technology, and enforcement, typically a few items per week.

**Model-written orientation**

The Transportation Security Administration (TSA), within the Department of Homeland Security, secures the nation's transportation systems. Its press releases cover aviation security policies, screening technology, and operational procedures.

The Transportation Security Administration is the Department of Homeland Security agency responsible for securing transportation systems across the United States, with primary focus on aviation security. TSA manages security screening at airports nationwide, establishes security procedures and policies for passengers and baggage, operates trusted-traveler programs including PreCheck, oversees transportation worker identification programs, and conducts security research and technology evaluation.

The TSA press office publishes announcements about the agency's programs, policies, and operations. These releases typically address aviation security procedures and policy changes; security screening technology, equipment, and deployments; trusted-traveler programs and enrollment procedures; transportation worker identification and credentials; checkpoint operations and procedures; and public guidance on travel security requirements.

In this digest, you will see TSA press releases announcing changes to security procedures affecting air travel; new screening technology or equipment being deployed at airports; updates to PreCheck or other trusted-traveler programs; public notices about screening procedures or documentation requirements; alerts or advisories related to screening operations; and reports on TSA activities and screening statistics.

TSA's releases focus on the mechanics and public-facing aspects of aviation security. The announcements explain how screening procedures work and what travelers should expect. Publications emerge at a rate of a few items per week. The press releases serve as TSA's official communication channel to the traveling public about security requirements and operational updates.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `tsa-press` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.tsa.gov/news/press/releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. 25 entries parse cleanly from <time datetime> attributes, but the newest was 2026-07-17 — TSA had published nothing inside the 7-day window. Nothing is wrong here; the source is simply low-rate. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Feed FOUND 2026-08-06 from the captured page (same body-link method as nih-news): https://www.tsa.gov/news/press/releases/feed.xml probes feed-ok, 10 items, 10/10 with guid and date, sample article extracts at 6,597 chars. NOT activated, two blockers: the newest item's title is EMPTY, and dates read 'July 17, 2026' which report._claimed_day cannot parse (returns None, which falls to listed rather than backfill). Also stale — newest item was three weeks old at probe. Needs both a date-format extension and a title fallback before it is worth re-probing. Re-probed 2026-08-06 after the dating fix removed its date blocker: the feed is live and well-formed (10 items, 10/10 guid and date) and 'July 17, 2026' now parses. STILL NOT ACTIVATED, for a structural reason the date fix does not touch: ALL TEN items carry an EMPTY <title>. Section 6 renders attributed release titles, so a titleless item is unrenderable. Activation needs a title fallback (the link slug carries the headline) and a re-probe. Also stale — newest item three weeks old at probe. |

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

No requests to www.tsa.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

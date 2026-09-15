<!-- Markdown twin of https://fapd.info/sources/dvids.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/dvids.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: dvids)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DVIDS (Digital Visual Information Distribution System)

planned · Executive · Tier 2 · API · Department of Defense (Defense Media Activity / DWIA)

Official site: https://api.dvidshub.net/ · All sources: [sources.md](../sources.md)

## What this source is

DoD's own distribution platform and public API for military media — 1.8M+ assets: unit/service news, still imagery with official captions and credit lines, video with official closed-caption transcripts, and unit publications. The Search API filters by branch, unit, type, and three date axes; the Asset API returns direct full-resolution download URLs, VIRIN identifiers, and structured credit. The pipeline's designated first multi-modal source.

**Model-written orientation**

DVIDS is the Department of Defense's official digital platform for military media, distributing news, photography, video, and unit publications from across the armed services.

The Department of Defense maintains DVIDS (Digital Visual Information Distribution System) as the consolidated repository and distribution point for official military media. The armed services—Army, Navy, Air Force, Marines, Space Force, and Coast Guard—use DVIDS to publish their own news releases, unit announcements, and multimedia content.

The content on DVIDS spans multiple media types. News releases cover military operations, personnel announcements, technology development, training exercises, and organizational changes. Photography includes official imagery from service members and units with standardized captions and attribution. Video content carries official closed-caption transcripts, making multimedia content accessible alongside traditional text announcements. Unit and service publications represent internal communications made public.

The platform hosts more than 1.8 million assets accumulated over its operational history, reflecting the continuous news flow from the defense establishment. Search capabilities allow filtering by military branch, unit, media type, and date, making it possible to follow developments within particular services or regions.

From a publication standpoint, DVIDS serves as the authoritative source for military institutions' own communications about their activities and decisions. Content is attributed directly to originating units or services, maintaining a clear chain of authorship. The platform operates under a public-use model with official media guidelines governing reproduction and attribution.

For readers following federal government activity, DVIDS represents the defense establishment's direct public voice—distinct from reporting about military matters found in news media or Department of Defense public affairs statements at the agency level.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `dvids` |
| Agency / parent organization | Department of Defense (Defense Media Activity / DWIA) |
| Branch | executive |
| Type | API |
| Status | planned |
| Tier | 2 |
| URL (home) | https://api.dvidshub.net/ |
| URL (index) | https://api.dvidshub.net/docs/search_api |
| Registered | 2026-07-28 |
| Registry notes | Deep dive 2026-07-28 (docs/dvids-multimodal-research-2026-07-28.md): API docs, TOS ('free for commercial use'; discretionary quotas; cache-refresh duty), copyright policy (public domain unless indicated; no-endorsement rule; journalist credit requested; some assets contractor-licensed — per-asset status check required) all read. stable_id design: dvids:{type}:{id} (API's own permanent key); VIRIN stored as official cross-system identifier. Video posture: metadata+thumbnail+captions only, no A/V downloads. Supersedes six unavailable service entries. Before probing: API-key registration, plus adoption of the proposed policy amendments (media byte budget, video posture, caption/credit rules, asset_posture adapter decision). Probe questions: news body text, rate-limit headers, full-res without login, CDN URL stability, per-branch volume census. Naming: DMA now presents as DWIA (Department of War Information Activity) — rename in progress; API host stable. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | API |
| Method | Would delta-sync the Search API per branch (types news+image first; date-windowed under the depth-1000 pagination cap; a timestamp pass honors the TOS cache-refresh duty), then the Asset API for selected items, with a free registered key; items attributed to the originating unit/service per the aggregator rule. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to api.dvidshub.net are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

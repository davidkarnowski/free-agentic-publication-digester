<!-- Markdown twin of https://fapd.info/sources/state-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/state-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: state-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# State Press Releases

planned · Executive · Tier 1 · HTML index · Department of State

Official site: https://www.state.gov/press-releases/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of State conducts U.S. foreign policy and diplomacy. Its press-release index carries departmental press statements, media notes, and the Secretary's remarks and travel announcements, typically several items per business day.

**Model-written orientation**

The Department of State publishes press releases on U.S. foreign policy, diplomacy, and international affairs, including statements from the Secretary and official positions on global developments.

The Department of State conducts United States foreign policy and diplomatic relations with other nations. The State Department's press-release index serves as the official channel for departmental announcements to the public and press, typically containing multiple items per business day during periods of active diplomatic engagement. Announcements include press statements on international developments, media notes addressing press inquiries, remarks delivered by the Secretary of State or senior officials, and travel announcements related to departmental delegations.

State Department communications address matters within its portfolio: bilateral relations with other countries, participation in international organizations, sanctions and travel restrictions, visa and passport policy changes, humanitarian assistance coordination, and responses to international crises and developments. Press releases document the department's positions on ongoing international matters and policy decisions affecting U.S. foreign relations.

The department's organizational structure includes regional bureaus covering geographic areas of the world and functional bureaus addressing specific policy domains such as economic affairs, human rights, or international organizations. Readers will encounter statements from any of these components, though the most visible communications typically originate from the Office of the Spokesperson, the Secretary's office, or senior geographic bureaus.

Releases are published on a rolling basis during business hours as diplomatic developments warrant. The index can be searched by date and keyword, and the department maintains a calendar of the Secretary's travel and engagements.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `state-newsroom` |
| Agency / parent organization | Department of State |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.state.gov/press-releases/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Research 2026-07-28: State documents feeds at state.gov/rss-feeds; an indexed live feed exists at state.gov/rss-feed/department-press-briefings/feed/ (implying .../press-releases/feed/). Site soft-blocks some non-browser clients but served our identified client HTTP 200 in July — re-probe the /rss-feed/<category>/feed/ URLs. Email sibling registered 2026-07-29: state-week-email (partial: weekly newsletter, not the press-statement stream) (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture (644 KB) it finds no article links at all, let alone dated ones: the listing is assembled client-side. This is a script-rendered listing; opening it needs evidence of a dated channel, not a cadence decision. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the press-release HTML index daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.state.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

<!-- Markdown twin of https://fapd.info/sources/interior-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/interior-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: interior-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Interior Press Releases

planned · Executive · Tier 1 · HTML index · Department of the Interior

Official site: https://www.doi.gov/news/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Department of the Interior manages public lands, national parks, and wildlife programs, and administers tribal trust responsibilities. Its press-release index carries departmental announcements on land management, species decisions, and grants, typically a few items per business day.

**Model-written orientation**

The Department of the Interior publishes announcements on public land management, wildlife conservation, national parks, and tribal trust responsibilities, reflecting the department's stewardship of federal natural resources.

The Department of the Interior manages federal public lands and natural resources, administers national parks and wildlife programs, and holds in trust legal and financial assets belonging to federally recognized Native American tribes and individual tribal members. The Interior Department's press-release index publishes multiple announcements per business day on its areas of responsibility.

The department's bureaus and offices conduct different aspects of this mission: the National Park Service manages the national park system; the Bureau of Land Management administers public lands in the West; the Fish and Wildlife Service manages wildlife refuges and enforces wildlife protection laws; the U.S. Geological Survey conducts research on natural resources and natural hazards; the Bureau of Indian Affairs administers programs affecting Native American tribes; and regional field offices implement policies specific to their geographic areas.

Readers will encounter announcements on land-management decisions (permits, conservation designations, wilderness area designations), species protection actions (endangered species listings or delisting decisions, habitat protections), grant programs and funding opportunities for state and tribal governments, disaster declarations or emergency responses, public-land access policies, and decisions on resource extraction on federal land. Releases reflect the department's dual responsibilities: stewardship of public natural resources and facilitation of resource development on federal land.

Interior publishes releases on a rolling basis during business hours. The department's large geographic footprint and multiple bureaus result in a steady stream of announcements reflecting on-the-ground management decisions, scientific findings, and policy implementation. Many releases originate from regional offices addressing matters specific to their areas, though significant policy announcements come from the Secretary's office. The index is searchable by date and topic.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `interior-newsroom` |
| Agency / parent organization | Department of the Interior |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.doi.gov/news/newsroom |
| URL (index) | https://www.doi.gov/news |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 404 at registered URL — path likely wrong or moved; correct URL and re-probe before concluding availability. URL recovered 2026-07-31 (operator machine, off the server budget): the department retired /pressreleases; its own newsroom page (doi.gov/news/newsroom) points at doi.gov/news, which answers HTTP 200 with the dated press-release index (newest 2026-07-31). The only feed the site advertises is https://www.doi.gov/feeds/content/36980/rss.xml — well-formed RSS, rebuilt today, and carrying ZERO items, so it is deliberately not registered as urls.feed: registering it would point the poller at a door that yields nothing while the index has the material. Left planned; ingestion waits on the html-index adapter, not on the publisher. Re-check the empty feed when that adapter lands — a working feed would be cheaper than parsing the index. Re-probe through scripts/check_sources.py, 2026-07-31: verdict html-only — HTTP 200, 67 KB, 6,508 characters of extracted index text, robots permitting. Probed 2026-07-31: registered URL returned 404 (https://www.doi.gov/pressreleases) — the publisher moved or retired it; not a refusal. |

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

No requests to www.doi.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

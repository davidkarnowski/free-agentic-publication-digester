<!-- Markdown twin of https://fapd.info/sources/commerce-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/commerce-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: commerce-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Commerce Press Releases

unavailable · Executive · Tier 1 · HTML index · Department of Commerce

Official site: https://www.commerce.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Department of Commerce promotes trade and economic growth and houses the federal statistical and standards agencies. Its press-release index carries departmental announcements, including trade-enforcement actions and program launches, typically a few items per week.

**Model-written orientation**

The Department of Commerce publishes announcements on trade, economic development, business statistics, and standards, reflecting the department's role in promoting U.S. economic interests.

The Department of Commerce promotes U.S. trade and economic growth and houses several federal statistical and standards agencies. The Commerce Department's press-release index publishes announcements related to its diverse portfolio of responsibilities.

The department's bureaus serve distinct functions: the International Trade Administration enforces trade laws and helps U.S. exporters access foreign markets; the Bureau of Industry and Security regulates the export of sensitive goods; the National Oceanic and Atmospheric Administration manages fisheries and marine resources and operates the National Weather Service; the National Institute of Standards and Technology develops standards and conducts research; the U.S. Patent and Trademark Office examines patent and trademark applications; the Census Bureau conducts the decennial census and produces economic statistics; and the Bureau of Economic Analysis produces national accounts data.

Readers will encounter announcements on trade enforcement actions and investigations (tariff actions, enforcement against dumping or intellectual property violations), export promotion initiatives and trade missions, patent and trademark policy or significant patent decisions, standards development, economic data releases (GDP, employment statistics, trade figures), and fisheries management decisions. Releases reflect the department's role as both an economic advocate for U.S. business and as a steward of federal statistical agencies and natural-resource programs.

The department publishes releases on a rolling basis, with volume varying based on trade policy cycles, statistical releases, and economic developments. Releases may come from any of Commerce's bureaus, and readers may see a single day's announcements covering trade enforcement, economic data, patent policy, and fisheries management.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `commerce-newsroom` |
| Agency / parent organization | Department of Commerce |
| Branch | executive |
| Type | HTML index |
| Status | unavailable |
| Tier | 1 |
| URL (home) | https://www.commerce.gov/news/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 403 to honestly-identified automated client (WAF) on the web index. Research 2026-07-28: Commerce publishes a content API at api.commerce.gov/api with a /news endpoint, documented at commerce.gov/data-and-reports/developer-resources/commercegov-api and in the official CommerceGov GitHub repo — a rung-1 door around the WAF. Staleness risk: repo changelog last touched Oct 2019. Re-probe the API with our api.data.gov key; status returns to unavailable if the API is dead. Email sibling registered 2026-07-29: commercial-service-email (partial: trade promotion only, not the press office) (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31: https://www.commerce.gov/news/press-releases answered 403 to our honestly-identified client. Recorded as a refusal. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would query the Commerce.gov content API /news endpoint (api.data.gov key family) for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is unavailable.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is unavailable. Ingestion statistics are measured for active sources only.

### All time

No requests to www.commerce.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

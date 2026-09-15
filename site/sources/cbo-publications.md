<!-- Markdown twin of https://fapd.info/sources/cbo-publications.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cbo-publications.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cbo-publications)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CBO Publications

unavailable · Legislative · Tier 1 · HTML index · Congressional Budget Office

Official site: https://www.cbo.gov/publications · All sources: [sources.md](../sources.md)

## What this source is

The Congressional Budget Office produces nonpartisan budget and economic analysis for Congress. Its publications index carries cost estimates for pending legislation, baseline and outlook reports, and analytic studies, typically several items per week.

**Model-written orientation**

The Congressional Budget Office produces nonpartisan fiscal and economic analysis for Congress, publishing cost estimates for pending legislation and broader fiscal and economic outlook reports. Publications typically number several items per week.

The Congressional Budget Office (CBO) is an independent agency of the legislative branch that provides nonpartisan fiscal and economic analysis to Congress. CBO serves as Congress's principal source of nonpartisan budgetary and economic analysis, and its staff includes economists, budget analysts, and policy researchers with expertise across federal finances and economic policy. The agency operates without partisan affiliation or political agenda and provides analysis intended to inform congressional deliberations across both parties.

CBO's primary publications include cost estimates for pending federal legislation, which provide detailed fiscal projections for bills and proposed programs including effects on federal revenues, spending, and the deficit; baseline projections and economic outlook reports presenting long-term fiscal and economic forecasts for the federal budget, including projections of revenues, spending, deficits, and economic conditions; studies and analyses on fiscal policy questions, taxation policy, employment and labor economics, healthcare economics, and other economic topics relevant to federal policy; and reports on federal programs and spending patterns examining specific areas of federal activity.

These publications represent CBO's assessments and analyses and are released as analytical work is completed and finalized. CBO publications are written for congressional audiences and typically include detailed quantitative analysis, data tables, and explanations of methodology. Readers will encounter rigorous numerical analyses, fiscal projections, economic forecasting, and policy evaluations grounded in economic research and data. The analyses are designed to inform congressional decision-making on federal spending, taxation, and economic policy.

CBO publishes several items per week on a rolling basis. Publication dates and update dates indicate when analyses were released or revised. Readers can expect authoritative nonpartisan fiscal and economic analysis on topics ranging from specific pending legislation to broader fiscal and economic policy questions affecting the federal budget.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cbo-publications` |
| Agency / parent organization | Congressional Budget Office |
| Branch | legislative |
| Type | HTML index |
| Status | unavailable |
| Tier | 1 |
| URL (home) | https://www.cbo.gov/publications |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 403 to honestly-identified automated client (WAF). Recorded, not evaded. Research 2026-07-28: two partial rung-1 alternatives — (1) CBO's official GitHub org US-CBO publishes 15 budget/economic datasets as versioned CSVs with a DCAT catalog.json (github.com/US-CBO/cbo-data), which is data, not the publication stream; (2) CBO cost estimates for bills surface in api.congress.gov bill data (cboCostEstimates container: title/URL/date per estimate). Whether those two channels cover enough of CBO's output is a pending project decision; the newsroom itself stays unavailable. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | HTML index diff via AgencyClient (pending viability check) |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is unavailable.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is unavailable. Ingestion statistics are measured for active sources only.

### All time

No requests to www.cbo.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

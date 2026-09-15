<!-- Markdown twin of https://fapd.info/sources/irs-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/irs-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: irs-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# IRS Newsroom

planned · Executive · Tier 2 · HTML index · Department of the Treasury

Official site: https://www.irs.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Internal Revenue Service, a Treasury bureau, administers federal tax law. Its newsroom index carries news releases on filing seasons, tax guidance, and enforcement programs, typically one or more items per business day.

**Model-written orientation**

The Internal Revenue Service administers federal tax law and publishes guidance on tax filing, refund processing, and enforcement activities.

The Internal Revenue Service (IRS) is a bureau of the Department of the Treasury and is the federal agency responsible for administering and enforcing federal income tax law, employment tax law, excise tax law, and other taxes under the Internal Revenue Code. The IRS operates through a nationwide system of ten regional offices, service centers, and specialized units handling different categories of taxpayers and tax issues.

The IRS's core functions include processing tax returns filed by individuals and businesses, issuing refunds, auditing tax returns and investigating non-compliance, enforcing payment of owed taxes, and providing taxpayer assistance and educational outreach. Beyond these core functions, the agency administers tax incentives and credits designed to accomplish policy objectives in areas such as clean energy, education, and retirement savings. The IRS also coordinates with state tax authorities and foreign governments on tax compliance matters.

IRS news releases cover annual filing season announcements, updates on tax law changes enacted by Congress, guidance on new tax credits or incentives, refund information and processing updates, electronic filing information, enforcement actions, changes to IRS procedures or forms, staffing and resource updates, and alerts on common scams. The releases often include practical guidance for individual and business taxpayers.

In this digest, readers will encounter filing season announcements, guidance on tax law changes, information about tax credits and deductions, refund processing updates, notices of new forms or procedures, enforcement announcements, alerts on tax scams and fraudulent schemes, and agency administrative updates. These releases serve individual taxpayers, business owners, tax professionals, payroll professionals, and accountants seeking timely updates on tax law changes and procedural information.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `irs-newsroom` |
| Agency / parent organization | Department of the Treasury |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.irs.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Email sibling registered 2026-07-29: irs-email (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 102 article link(s); 1 dated inside the 7-day lookback, 3 dated outside it, 98 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). |

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

No requests to www.irs.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

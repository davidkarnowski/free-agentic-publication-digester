<!-- Markdown twin of https://fapd.info/sources/ssa-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ssa-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ssa-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# SSA Press Releases

unavailable · Executive · Tier 1 · HTML index · Independent agency

Official site: https://www.ssa.gov/news/en/press/releases/index.html · All sources: [sources.md](../sources.md)

## What this source is

The Social Security Administration administers retirement, disability, and survivor benefits. Its newsroom carries press releases on benefit amounts, policy changes, and program administration, typically a few items per month.

**Model-written orientation**

The Social Security Administration publishes press releases about benefit changes, policy modifications, and program administration.

The Social Security Administration is an independent agency that administers federal retirement, disability, and survivor insurance benefits through the Old-Age, Survivors, and Disability Insurance (OASDI) program and Supplemental Security Income (SSI) assistance. SSA serves tens of millions of beneficiaries and maintains field offices and processing centers nationwide.

SSA's news-release channel carries announcements of changes affecting beneficiaries and the public: annual adjustments to benefit payment amounts, regulatory changes affecting eligibility or benefit computation, policy modifications affecting work incentives or other program rules, administrative process changes, outreach initiatives, and agency operational announcements.

Readers will typically see a few items per month covering topics such as annual cost-of-living adjustments announced each fall, changes to earnings limits affecting beneficiaries who work, modifications to medical evidence requirements for disability determinations, updates to beneficiary representative-payee rules, cybersecurity and fraud prevention initiatives, and notices about application procedures or benefit verification requirements. The releases are directed toward current beneficiaries, individuals considering applying for benefits, representative payees managing benefits for others, and the general public. Many releases address questions frequently raised by SSA's constituencies about how policy changes will affect their benefits or obligations. SSA also maintains an Office of Inspector General that conducts oversight of agency programs and publishes its own investigative and audit reports.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ssa-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | unavailable |
| Tier | 1 |
| URL (home) | https://www.ssa.gov/news/en/press/releases/index.html |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: HTTP 403 to honestly-identified automated client (WAF). Recorded, not evaded. Research 2026-07-28: press index moved to /news/en/press/releases/ (recorded for any future re-probe); no feed or API alternative found — GovDelivery email (USSSA) is the documented channel. SSA OIG has RSS at oig.ssa.gov/rss/ and is also covered by the planned oversight.gov aggregator. Email sibling registered 2026-07-29: ssa-email (GUIDE §3 email class; the web status here is unchanged). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the newsroom HTML index daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is unavailable.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is unavailable. Ingestion statistics are measured for active sources only.

### All time

No requests to www.ssa.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

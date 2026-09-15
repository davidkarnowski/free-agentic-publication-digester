<!-- Markdown twin of https://fapd.info/sources/cms-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cms-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cms-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CMS Newsroom

planned · Executive · Tier 2 · HTML index · Department of Health and Human Services

Official site: https://www.cms.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Centers for Medicare & Medicaid Services administers Medicare, Medicaid, and the health-insurance marketplaces within HHS. Its newsroom index carries press releases and fact sheets on payment rules, coverage policy, and program data, typically several items per week.

**Model-written orientation**

The Centers for Medicare & Medicaid Services, within the Department of Health and Human Services, administers Medicare and Medicaid and publishes releases on program policy and payment rules.

The Centers for Medicare & Medicaid Services (CMS) is the federal agency within the Department of Health and Human Services that administers Medicare, Medicaid, and the health-insurance marketplaces. Medicare is the federal health-insurance program for people aged sixty-five and older, certain younger people with disabilities, and people with end-stage renal disease. Medicaid is a joint federal-state program providing health coverage to low-income individuals and families. The health-insurance marketplaces established under the Affordable Care Act are also administered by CMS.

CMS manages programs affecting hundreds of millions of Americans and controls a major share of federal healthcare spending. The agency sets payment rates and coverage policies for Medicare services, works with states on Medicaid administration and policy, and operates the federal marketplace where individuals can purchase health insurance. CMS also collects and publishes healthcare data, manages fraud and abuse prevention, and coordinates with providers, insurers, and state agencies on program implementation and compliance.

In this digest, you will see CMS releases announcing changes to payment rates (for hospitals, physicians, and other providers), coverage determinations and policy changes, program rule amendments, enrollment and participation data, and statements on agency initiatives and program administration. The releases address Medicare policy, Medicaid guidance (often relevant to state programs), marketplace operations, and data releases. CMS announcements are closely watched by healthcare providers, insurers, states, and beneficiaries because they directly affect program eligibility, benefits, and reimbursement.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cms-newsroom` |
| Agency / parent organization | Department of Health and Human Services |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.cms.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Email sibling registered 2026-07-29: cms-email (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 16 article link(s); 6 dated inside the 7-day lookback, 2 dated outside it, 8 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

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

No requests to www.cms.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

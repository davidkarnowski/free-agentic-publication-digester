<!-- Markdown twin of https://fapd.info/sources/treasury-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/treasury-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: treasury-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Treasury Press Releases

unavailable · Executive · Tier 1 · HTML index · Department of the Treasury

Official site: https://home.treasury.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Department of the Treasury manages federal finances, collects revenue, and administers economic sanctions. Its press-release index carries sanctions designations, debt-management statements, and economic-policy announcements, typically multiple items per business day.

**Model-written orientation**

The Department of the Treasury publishes announcements on federal finances, tax policy, economic sanctions, and financial regulation, reflecting the department's broad stewardship of U.S. economic policy.

The Department of the Treasury manages federal finances, collects federal revenue, and administers economic sanctions on behalf of the U.S. government. The department oversees a broad portfolio spanning federal borrowing and debt management, tax policy, financial intelligence and enforcement against money laundering and terrorist financing, trade sanctions (administered through the Office of Foreign Assets Control), currency and mint operations, and oversight of federally chartered banks.

The Treasury Department publishes multiple types of announcements reflecting its operations: statements on debt auctions and borrowing schedules, designations of individuals and entities subject to economic sanctions, announcements of financial regulations or guidance documents issued by its component bureaus, notices of enforcement actions or settlements with regulated institutions, and policy statements on economic matters within Treasury's jurisdiction.

Treasury's bureaus and offices maintain separate channels: the Internal Revenue Service issues tax policy announcements and enforcement notices; the Financial Crimes Enforcement Network provides guidance related to financial crimes; the Bureau of Alcohol, Tobacco, Firearms and Explosives addresses firearms and explosives; the Bureau of Engraving and Printing manages currency production; and the Office of the Comptroller of the Currency oversees national banks. Readers will see content reflecting the work of these offices as well as department-wide policy statements.

The department publishes multiple items per business day during active periods, particularly around debt-management milestones, sanctions actions, or regulatory changes. Releases reflect the interconnected nature of federal economic policy and financial oversight.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `treasury-newsroom` |
| Agency / parent organization | Department of the Treasury |
| Branch | executive |
| Type | HTML index |
| Status | unavailable |
| Tier | 1 |
| URL (home) | https://home.treasury.gov/news/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: robots.txt disallows our identified client for this path. Not fetched, per GUIDE §3 (no evasion). Research 2026-07-28: no web feed alternative found — GovDelivery email (code USTREAS) is the documented channel, and modern GovDelivery exposes no public per-topic RSS (bulletins archive is login-walled), so the fallback means an email-ingestion adapter. OFAC sanctions actions live on a separate host (see ofac-recent-actions); OFAC formally retired its RSS 2025-01-31 in favor of GovDelivery email. Email sibling registered 2026-07-29: treasury-email (departmental bulletins; FinCEN, IRS, TTB, BEP, CDFI, TIGTA and OFR lists also subscribed) (GUIDE §3 email class; the web status here is unchanged). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the press-release HTML index daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is unavailable.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is unavailable. Ingestion statistics are measured for active sources only.

### All time

No requests to home.treasury.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

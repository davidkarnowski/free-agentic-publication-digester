<!-- Markdown twin of https://fapd.info/sources/fdic-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fdic-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fdic-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FDIC Press Releases

planned · Executive · Tier 2 · HTML index · Independent agency

Official site: https://www.fdic.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Federal Deposit Insurance Corporation insures bank deposits and supervises state-chartered banks. Its press-release index carries announcements on bank supervision, failures and resolutions, and rulemaking, typically a few items per week.

**Model-written orientation**

The Federal Deposit Insurance Corporation insures bank deposits and supervises state-chartered banks; its press releases cover bank supervision, resolutions, and regulatory matters.

The Federal Deposit Insurance Corporation is an independent agency established in 1933 to maintain stability and public confidence in the banking system. The FDIC insures deposits at member banks up to applicable limits and supervises state-chartered banks that are not members of the Federal Reserve System.

FDIC press releases announce actions taken in pursuit of these missions. These include announcements of bank supervision activities, supervisory findings, enforcement actions, and capital adequacy determinations for supervised banks. The FDIC also announces bank failures and resolutions, through which the agency either arranges for a failed bank's assets and liabilities to be transferred to another institution or manages the liquidation process. Readers will encounter announcements of assistance programs for failing institutions, updates on bank supervision policy, responses to changing economic conditions, and regulatory guidance issued to supervised institutions.

The agency also announces rulemaking activities, including proposed and final rules governing deposit insurance, capital requirements, lending practices, and other regulatory matters affecting banks under its supervision. Personnel announcements and updates on FDIC operations, including examination results summaries and regional office activities, appear in the press releases.

As an insurance and supervisory agency, the FDIC's press releases constitute the official record of its actions affecting member institutions and the banking system. They serve as the primary mechanism through which the FDIC communicates supervisory expectations, policy changes, and significant actions to affected banks, the financial industry, and the public. These announcements are typically the first public disclosure of FDIC supervisory or policy actions before they appear in regulatory databases or the Federal Register.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fdic-news` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.fdic.gov/news/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Research 2026-07-28: conflicting evidence on a GovDelivery-hosted press RSS (public.govdelivery.com/topics/USFDIC_26/feed.rss cited by an integration vendor, but the modern GovDelivery platform generally exposes no public per-topic RSS) — one probe of that URL settles both this source and the GovDelivery-pattern question for every agency marked 'GovDelivery to evaluate'. Separately, BankFind Suite API at api.fdic.gov/banks/docs offers structured bank data (not press). Email sibling registered 2026-07-29: fdic-email (GUIDE §3 email class; the web status here is unchanged). Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 61 article link(s); 3 dated inside the 7-day lookback, 21 dated outside it, 34 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the FDIC page links a GovDelivery feed (https://public.govdelivery.com/topics/USFDIC_26/feed.rss); that host's robots.txt REFUSES us. Recorded and not retried — a refusal is accountability data (GUIDE §4). The FDIC's own email channel is already active as fdic-email, which covers this source's releases through a channel we are welcome on. Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

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

No requests to www.fdic.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

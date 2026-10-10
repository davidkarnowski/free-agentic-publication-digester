<!-- Markdown twin of https://fapd.info/sources/cfpb-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/cfpb-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: cfpb-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# CFPB Newsroom

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Independent agency

Official site: https://www.consumerfinance.gov/about-us/newsroom/ · All sources: [sources.md](../sources.md)

## What this source is

The Consumer Financial Protection Bureau regulates consumer financial products and services. Its newsroom carries press releases and statements on rules, supervision, and enforcement actions; in 2026 it has posted about one item a month.

**Model-written orientation**

The Consumer Financial Protection Bureau regulates consumer financial products and services, publishing press releases and statements on rules, enforcement actions, and supervision.

The Consumer Financial Protection Bureau (CFPB) is an independent federal agency created by the Dodd-Frank Act to regulate consumer financial products and services. The bureau writes rules, supervises financial institutions, and enforces federal consumer financial law to protect consumers from unfair, deceptive, or abusive practices. Its authority covers a broad range of financial services including mortgages, credit cards, bank accounts, payday loans, debt collection, credit reporting, and other consumer credit and payment products. The CFPB has supervisory authority over large banks and nonbanks that offer consumer financial products or services, and it works with federal and state regulators to oversee the financial institutions under its jurisdiction. The bureau's newsroom publishes press releases and statements on the agency's enforcement actions, proposed and final rules, supervision activities, and other significant agency developments, typically at a low frequency of about one item per month. Enforcement actions may include settlements requiring institutions to refund consumers, cease certain practices, pay civil money penalties, or implement compliance improvements. Rules issued by the bureau set requirements for how financial institutions may treat consumers and what disclosures or protections are required. Supervision activities focus on examining institutions for compliance with consumer protection law. In this digest you will see CFPB press releases and statements describing recently announced enforcement actions, proposed or finalized rules, supervisory findings, and other agency actions or initiatives. Each release provides context for the action or rule, the legal basis for the agency's authority, and the specific practices or issues addressed. Readers interested in consumer finance, financial regulation, or consumer protection will find the CFPB's releases a direct source for the agency's actions and policy positions.

_Model-written orientation, generated 2026-10-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `cfpb-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.consumerfinance.gov/about-us/newsroom/feed/ |
| URL (home) | https://www.consumerfinance.gov/about-us/newsroom/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 81 article link(s); 1 dated inside the 7-day lookback, 19 dated outside it, 61 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). ACTIVATED 2026-10-05 (operator) on https://www.consumerfinance.gov/about-us/newsroom/feed/. CFPB's published site source (the cfgov feeds module) serves a feed at <page>/feed/ for every filterable list page, with a GUID built from the page's internal id, so identity survives a URL change. Probed 2026-10-04 through FAPD's identified probe client. Re-verified 2026-10-05 from the operator machine as a brief test, outside the server's budget, through FAPD's identified probe client (robots allows, no crawl-delay, no Retry-After, HTTP 200): 22 items, 22/22 with GUID and date; newest 2026-10-02, the same five newest dates the listing page shows, so the feed is current. Sample release extracted at 5,804 characters; descriptions are ~180-character teasers, so full mode. Coverage (gate 3): the feed reaches back to 2025-02 and holds about one release a month in 2026, so expect most days to list nothing. The first poll fetches the 21 older releases once, and they sort to backfill. Not activated with it: the enforcement-actions feed (/enforcement/actions/feed/), which held nothing newer than 2025-09-22 on 2026-10-05, is not in date order, and states dates whose meaning (filing or last update) is unconfirmed. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the newsroom RSS feed via AgencyClient, then fetches each new release for full text (mode full). |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 22 item(s) in the last 14 days; most recent 2026-10-05; 0 of 132 request(s) to www.consumerfinance.gov returned no content.

This label has held since 2026-10-05T23:57:58Z (UTC) and was last re-checked 2026-10-10T03:58:47Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 25 request(s) (25 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 22 in 14 days (1.57 per day) · most recent 2026-10-05 |
| Content length | 5,096 characters average, 4,120 median (shortest 2,681, longest 12,025) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.consumerfinance.gov | 132 request(s) · 132 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-10T04:00:10.884+00:00 UTC.

22 item(s) in the last 14 days; most recent 2026-10-05; 0 of 132 request(s) to www.consumerfinance.gov returned no content.

### All time

- **Our requests to www.consumerfinance.gov, all time (since 2026-10-05):** 132 request(s) · 132 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.consumerfinance.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-11 | 0 | 0 | — |
| 2026-09-12 | 0 | 0 | — |
| 2026-09-13 | 0 | 0 | — |
| 2026-09-14 | 0 | 0 | — |
| 2026-09-15 | 0 | 0 | — |
| 2026-09-16 | 0 | 0 | — |
| 2026-09-17 | 0 | 0 | — |
| 2026-09-18 | 0 | 0 | — |
| 2026-09-19 | 0 | 0 | — |
| 2026-09-20 | 0 | 0 | — |
| 2026-09-21 | 0 | 0 | — |
| 2026-09-22 | 0 | 0 | — |
| 2026-09-23 | 0 | 0 | — |
| 2026-09-24 | 0 | 0 | — |
| 2026-09-25 | 0 | 0 | — |
| 2026-09-26 | 0 | 0 | — |
| 2026-09-27 | 0 | 0 | — |
| 2026-09-28 | 0 | 0 | — |
| 2026-09-29 | 0 | 0 | — |
| 2026-09-30 | 0 | 0 | — |
| 2026-10-01 | 0 | 0 | — |
| 2026-10-02 | 0 | 0 | — |
| 2026-10-03 | 0 | 0 | — |
| 2026-10-04 | 0 | 0 | — |
| 2026-10-05 | 22 | 27 | 74 |
| 2026-10-06 | 0 | 26 | 122 |
| 2026-10-07 | 0 | 27 | 139 |
| 2026-10-08 | 0 | 26 | 122 |
| 2026-10-09 | 0 | 25 | 127 |
| 2026-10-10 | 0 | 1 | 251 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated 2026-10-05, the newsroom feed is delivering releases at 1.57 per day. Twenty-two items were ingested, each averaging 5,096 characters. All 28 requests to www.consumerfinance.gov succeeded. The feed carries GUID identifiers and published dates; feed descriptions are approximately 180-character teasers, and full text is fetched from the release page.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

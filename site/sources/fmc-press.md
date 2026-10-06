<!-- Markdown twin of https://fapd.info/sources/fmc-press.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fmc-press.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fmc-press)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FMC Press Releases

active · ingestion health: delivering · Executive · Tier 3 · RSS feed · Independent agency

Official site: https://www.fmc.gov/category/news-articles/press-releases/ · All sources: [sources.md](../sources.md)

## What this source is

The Federal Maritime Commission regulates ocean shipping in U.S. foreign trade: carriers, marine terminals, and ocean transportation intermediaries. Its press releases announce enforcement actions, rulemakings, and commission decisions; volume is low, ten releases from January to July 2026.

**Model-written orientation**

The Federal Maritime Commission regulates ocean shipping in U.S. foreign trade, publishing press releases on enforcement actions, rulemakings, and commission decisions.

The Federal Maritime Commission (FMC) is an independent federal agency that regulates ocean shipping in U.S. foreign trade. The commission has authority over ocean shipping rates, service contracts, and practices; marine terminals; and ocean transportation intermediaries (freight forwarders and non-vessel-operating common carriers). The FMC's jurisdiction covers foreign and domestic ocean shipping affecting U.S. trade, including shipping to and from U.S. ports. The commission enforces the Shipping Act and related maritime law, oversees the licensing of ocean transportation intermediaries, and addresses disputes between shipping companies and shippers. The FMC has five commissioners and maintains area offices in major ports. The commission's press releases announce enforcement actions taken against ocean transportation companies for violations of law or regulation, notices of rulemakings and adopted rules, significant commission decisions in formal proceedings, and other agency activities. The volume of press releases is lower than at many federal agencies, with ten releases issued from January through July 2026. Enforcement actions may address practices such as service failures, rate violations, or discriminatory treatment of shippers. Rulemakings may cover topics such as tariff requirements, service contract terms, or marine terminal practices. In this digest you will see FMC press releases describing recently announced enforcement actions, adopted rules or rulemakings, significant commission decisions, and other significant agency actions. Each release provides context for the action or decision and the shipping or maritime practices at issue. Readers interested in maritime commerce, ocean shipping regulation, or international trade will find the FMC's releases a source for agency actions and policy decisions affecting the ocean shipping industry.

_Model-written orientation, generated 2026-10-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fmc-press` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 3 |
| URL (feed) | https://www.fmc.gov/category/news-articles/press-releases/feed/ |
| URL (home) | https://www.fmc.gov/category/news-articles/press-releases/ |
| Registered | 2026-10-05 |
| Registry notes | Registered and ACTIVATED 2026-10-05 (operator), from the 2026-10-04 source research. Probed 2026-10-04 through FAPD's identified probe client. Re-verified 2026-10-05 from the operator machine as a brief test, outside the server's budget, through FAPD's identified probe client (robots allows, no crawl-delay, no Retry-After, HTTP 200): 10 items, 10/10 with GUID (the site's post id) and date; newest 2026-07-08, the same newest dates the press-release listing shows, so the feed is current and the Commission is quiet. Sample release extracted at 4,429 characters and its page states the feed's date; descriptions are ~680-character excerpts, so full mode. Coverage (gate 3): 10 items spanned 2026-01-26 to 07-08; expect most weeks to list nothing. The first poll fetches the ten releases once and they sort to backfill. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the press-release category RSS feed via AgencyClient, then fetches each new release for full text (mode full). |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 10 item(s) in the last 14 days; most recent 2026-10-05; 0 of 16 request(s) to www.fmc.gov returned no content.

This label has held since 2026-10-05T23:57:58Z (UTC) and was last re-checked 2026-10-06T03:59:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 16 request(s) (16 answered, 0 returned no content) · 10 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 10 in 14 days (0.71 per day) · most recent 2026-10-05 |
| Content length | 5,472 characters average, 3,729 median (shortest 2,455, longest 22,756) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.fmc.gov | 16 request(s) · 16 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-06T04:00:16.751+00:00 UTC.

10 item(s) in the last 14 days; most recent 2026-10-05; 0 of 16 request(s) to www.fmc.gov returned no content.

### All time

- **Our requests to www.fmc.gov, all time (since 2026-10-05):** 16 request(s) · 16 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.fmc.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-07 | 0 | 0 | — |
| 2026-09-08 | 0 | 0 | — |
| 2026-09-09 | 0 | 0 | — |
| 2026-09-10 | 0 | 0 | — |
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
| 2026-10-05 | 10 | 15 | 114 |
| 2026-10-06 | 0 | 1 | 180 |

## Our ingestion assessment

**Model-written ingestion assessment**

Newly ingested starting 2026-10-05, the press-release feed is delivering items at a measured rate of 0.71 per day. Ten releases were observed spanning January through July, each averaging 5,472 characters of extracted text. All 16 requests to www.fmc.gov succeeded. The feed carries GUID identifiers and published dates; feed descriptions are approximately 680-character excerpts, warranting full-text fetches.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

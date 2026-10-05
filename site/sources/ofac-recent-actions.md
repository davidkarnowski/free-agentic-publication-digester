<!-- Markdown twin of https://fapd.info/sources/ofac-recent-actions.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ofac-recent-actions.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ofac-recent-actions)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# OFAC Recent Actions

active · ingestion health: delivering · Executive · Tier 2 · HTML index · Department of the Treasury (OFAC)

Official site: https://ofac.treasury.gov/recent-actions · All sources: [sources.md](../sources.md)

## What this source is

The Office of Foreign Assets Control publishes sanctions designations, delistings, and general licenses on its recent-actions index — high-consequence official actions currently invisible to the pipeline except as delayed Federal Register notices.

**Model-written orientation**

The OFAC Recent Actions index lists sanctions designations, delistings, and general licenses issued under U.S. economic sanctions authorities.

The Office of Foreign Assets Control is a bureau within the Department of the Treasury that administers and enforces U.S. economic sanctions programs. OFAC sanctions certain countries, entities, and individuals in accordance with Presidential executive orders and Congressional legislation. Sanctions are imposed for reasons including national security, foreign policy, and counterterrorism objectives.

OFAC publishes a record of recent actions taken under its sanctions authority. These official actions include the designation of entities or individuals as sanctions targets, the removal of designations (delistings), the issuance of general licenses that authorize specified activities that would otherwise violate sanctions, and amendments to sanctions programs. These actions have immediate legal and commercial effect for persons and entities subject to U.S. jurisdiction.

Readers will see from this source official notices of OFAC sanctions designations, delistings, general licenses, and related program guidance. Each notice includes the date of action, the entities or individuals affected (where applicable), and references to the applicable sanctions program. Designations and delistings are binding legal actions that businesses and individuals must observe to comply with sanctions law.

OFAC publishes these actions on a regular basis as they are taken. The timing and volume vary depending on foreign policy and the agency's enforcement priorities. The dates on recent actions represent the dates the actions were taken or effective.

The Recent Actions index operates as an HTML listing on the OFAC website. The digest polls this index regularly, without fetching full documents, to identify recent actions. Actions listed without a readable date are not included. Prior to 2026, OFAC offered an RSS feed for this content, which has since been retired in favor of email delivery through GovDelivery; the HTML index remains as the current public disclosure mechanism. The digest's coverage is limited to items appearing on the first page of the index at the time of polling; actions published between polls that exceed one page of listings may not be captured.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ofac-recent-actions` |
| Agency / parent organization | Department of the Treasury (OFAC) |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 2 |
| URL (home) | https://ofac.treasury.gov/recent-actions |
| URL (index) | https://ofac.treasury.gov/recent-actions |
| Registered | 2026-07-28 |
| Registry notes | OFAC retired its RSS 2025-01-31 (own notice) in favor of GovDelivery email; the recent-actions HTML index remains. Probed 2026-07-31 17:44Z: HTTP 200, robots allowed, index captured. Re-probed 2026-07-31 23:57Z for activation and the host would not serve robots.txt at all — five attempts, every one closed without a response — so the client fell closed and fetched nothing, which is the correct posture (GUIDE §4) and not something to retry into submission. The adapter itself is ready: against the 17:44Z capture it reads 11 dated actions (prose 'July 30, 2026'), correctly dropping the per-entry 'Sanctions List Updates' category link that repeats in every block. Stays planned pending a robots.txt that answers; recheck before any activation. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 43 article link(s); 4 dated inside the 7-day lookback, 7 dated outside it, 32 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: The host served robots.txt this time (it would not on 2026-07-31). Without a hint the listing yields 5 dated entries, two of them category links (General Licenses; Regulations and Guidance) carrying an action's date. index_item_path /recent-actions/20 keeps the 3 dated action pages (2026-09-23..28). Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only). |
| Adapter | html-index |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 8 item(s) in the last 14 days; most recent 2026-10-02; 0 of 172 request(s) to ofac.treasury.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-05T03:47:32Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 8 in 14 days (0.57 per day) · most recent 2026-10-02 |
| Content length | 160 characters average, 155 median (shortest 74, longest 250) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to ofac.treasury.gov | 172 request(s) · 172 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-05T04:00:20.201+00:00 UTC.

8 item(s) in the last 14 days; most recent 2026-10-02; 0 of 172 request(s) to ofac.treasury.gov returned no content.

### All time

- **Our requests to ofac.treasury.gov, all time (since 2026-09-28):** 172 request(s) · 172 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to ofac.treasury.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-06 | 0 | 0 | — |
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
| 2026-09-28 | 3 | 12 | 9383 |
| 2026-09-29 | 2 | 28 | 9266 |
| 2026-09-30 | 1 | 25 | 9125 |
| 2026-10-01 | 1 | 28 | 9286 |
| 2026-10-02 | 1 | 26 | 9161 |
| 2026-10-03 | 0 | 26 | 9017 |
| 2026-10-04 | 0 | 26 | 8905 |
| 2026-10-05 | 0 | 1 | 8217 |

## Our ingestion assessment

**Model-written ingestion assessment**

OFAC Recent Actions is ingested via HTML index diffing with path filtering to /recent-actions/20 and one listing poll per cycle. Activation on 2026-09-28 set the measurement baseline. In the 6 days since activation, three items were ingested with dates ranging from 2026-09-23 to 2026-09-28, averaging 137 characters each. The source operates feed-only with no article fetches; filtered index text serves as the full digest content. All 13 polling requests to ofac.treasury.gov completed successfully with no errors. The host refused robots.txt requests on 2026-07-31 but answered normally on 2026-09-28; no polling was attempted during the outage window. Coverage is limited to dateable entries on the filtered page; undatable entries are dropped and never observation-dated.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

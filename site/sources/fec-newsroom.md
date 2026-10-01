<!-- Markdown twin of https://fapd.info/sources/fec-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fec-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fec-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FEC Press Releases

active · ingestion health: delivering · Executive · Tier 1 · HTML index · Independent agency

Official site: https://www.fec.gov/updates/ · All sources: [sources.md](../sources.md)

## What this source is

The Federal Election Commission administers and enforces federal campaign-finance law. Its updates index carries press releases, commission meeting agendas, and closed enforcement matters, typically a few items per week.

**Model-written orientation**

Federal Election Commission updates on campaign finance enforcement, regulatory actions, and meeting notices.

The Federal Election Commission is an independent agency created by the Federal Election Campaign Act of 1971 to administer and enforce the federal campaign-finance laws that regulate money in elections. The Commission has six voting members appointed by the President and confirmed by the Senate. Its mandate includes interpreting the campaign-finance statutes, writing regulations and providing guidance, reviewing and disclosing campaign-finance reports, investigating potential violations of the law, and pursuing civil enforcement action against violators of federal election law.

The Commission's updates channel publishes an index of all official materials issued by the agency. Readers will find press releases announcing enforcement actions and closed investigation decisions, agendas and notices for Commission meetings where rules and policy are set, final and proposed regulations and official interpretive guidance for candidates and political committees, advisory opinions on specific campaign-finance questions, significant filings and disclosures, notices of proposed rulemaking, and other official Commission publications. The updates listing is comprehensive, reflecting all of the Commission's official outputs. The FDIC typically publishes a few items per week through this channel.

Materials in this feed serve candidates and political committees seeking to understand their legal obligations, election-law attorneys and compliance professionals, political consultants, media outlets covering elections, political-watchdog organizations, and the public interested in campaign finance regulation, enforcement, and transparency.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fec-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.fec.gov/updates/ |
| URL (index) | https://www.fec.gov/updates/ |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Research 2026-07-28: the OpenFEC API (api.open.fec.gov, api.data.gov key we hold, 1,000 calls/hr documented) covers filings/candidates/committees and legal-enforcement data — a rung-1 complement to the press index, not a replacement for it. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 54 article link(s); 2 dated inside the 7-day lookback, 21 dated outside it, 31 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed live 2026-09-28 from the operator machine as a brief test, outside the server's budget (identified client, robots allows). ACTIVATED 2026-09-28 with the html-index adapter. Gate 3: 4 entries dated inside the 7-day lookback (2026-09-21..28). The updates listing is broader than press releases: that day it carried compliance tips, a weekly digest and filing reminders, all the Commission's own publications, and all are read. A press-release-only view was the earlier plan and was not probed. Under-coverage: the listing's first page only, so more new entries between two hourly polls than the page holds would not be seen; entries the parser cannot date are dropped, never observation-dated. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only). Reads the whole updates listing, not press releases alone. |
| Adapter | html-index |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 4 item(s) in the last 14 days; most recent 2026-09-28; 0 of 68 request(s) to www.fec.gov returned no content.

This label has held since 2026-09-28T18:49:43Z (UTC) and was last re-checked 2026-10-01T03:53:55Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 4 in 14 days (0.29 per day) · most recent 2026-09-28 |
| Content length | 264 characters average, 314 median (shortest 85, longest 346) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.fec.gov | 68 request(s) · 68 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-01T04:00:11.037+00:00 UTC.

4 item(s) in the last 14 days; most recent 2026-09-28; 0 of 68 request(s) to www.fec.gov returned no content.

### All time

- **Our requests to www.fec.gov, all time (since 2026-09-28):** 68 request(s) · 68 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.fec.gov | Mean response time (ms) |
|---|---|---|---|
| 2026-09-02 | 0 | 0 | — |
| 2026-09-03 | 0 | 0 | — |
| 2026-09-04 | 0 | 0 | — |
| 2026-09-05 | 0 | 0 | — |
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
| 2026-09-28 | 4 | 12 | 1742 |
| 2026-09-29 | 0 | 29 | 776 |
| 2026-09-30 | 0 | 26 | 1498 |
| 2026-10-01 | 0 | 1 | 2627 |

## Our ingestion assessment

**Model-written ingestion assessment**

Activated with the html-index adapter in late September. The FEC's updates listing is broader in scope than press releases alone and includes compliance tips, weekly digests, filing reminders, and enforcement notices—all of which are read and ingested as published. We observed 4 items over 14 days from this source carrying the Commission's own dates. All 14 requests to www.fec.gov succeeded with no failures. The listing displays the first page only, so any entries published between two polls that exceed the page size would not be seen. Entries lacking readable dates are dropped and never observation-dated. No machine-readable feeds are advertised on this source.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/occ-bulletins.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/occ-bulletins.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: occ-bulletins)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# OCC Bulletins

active · ingestion health: delivering · Executive · Tier 2 · RSS feed · Department of the Treasury

Official site: https://www.occ.gov/rss/index-rss.html · All sources: [sources.md](../sources.md)

## What this source is

The Office of the Comptroller of the Currency's bulletins are its numbered supervisory issuances to national banks and federal savings associations: guidance, handbook revisions, rescissions, and notices of rulemaking. They are a separate series from its news releases, typically several a month.

**Model-written orientation**

The Office of the Comptroller of the Currency issues numbered bulletins as supervisory guidance to national banks and federal savings associations, covering regulatory requirements and policy changes.

The Office of the Comptroller of the Currency's bulletins are its formal supervisory issuances to the national banks and federal savings associations it regulates. Bulletins differ from press releases in that they communicate requirements, guidance, and policy directly to institutions under the OCC's jurisdiction rather than announcing actions already taken. The bulletins are numbered sequentially and cover a wide range of supervisory topics including updates to regulations, interpretations of law, new guidance on emerging risks, handbook revisions that reflect current policy, notices regarding rulemakings, and rescissions of prior guidance that are no longer in effect. The OCC issues bulletins as a primary method of communicating expectations and requirements to the banking institutions it supervises, and they are typically several per month. Bulletins may address topics such as capital requirements, asset quality expectations, management of specific types of risk, cybersecurity standards, anti-money-laundering compliance, consumer compliance, and fair lending. Some bulletins implement new federal regulations; others reflect the agency's own supervisory judgment about prudent banking practices. In this digest you will see OCC bulletins that were issued within the displayed time period. Each bulletin carries its title, number, date, and the full text of the bulletin itself. Readers interested in banking regulation, supervisory expectations for national banks, or changes in OCC policy will find the bulletins a direct source for regulatory guidance as issued by the regulator. The bulletins are sometimes referenced or summarized in the financial press, but the full official text appears in this digest.

_Model-written orientation, generated 2026-10-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `occ-bulletins` |
| Agency / parent organization | Department of the Treasury |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 2 |
| URL (feed) | https://www.occ.gov/rss/occ_bulletins.xml |
| URL (home) | https://www.occ.gov/rss/index-rss.html |
| Registered | 2026-10-05 |
| Registry notes | Registered and ACTIVATED 2026-10-05 (operator), from the 2026-10-04 source research: OCC's RSS index page lists a Bulletins feed beside News Releases. Probed 2026-10-04 through FAPD's identified probe client. Re-verified 2026-10-05 from the operator machine as a brief test, outside the server's budget, through FAPD's identified probe client (robots allows, no crawl-delay, no Retry-After, HTTP 200): 10 items, 10/10 dated in RFC 822 form without a weekday, no GUIDs (identity is the bulletin link, which carries the year and bulletin number). Newest item 2026-09-30; its own page states the same date; the sample bulletin extracted at 6,333 characters. Coverage (gate 3): 10 items spanned 2026-08-27 to 09-30 (seven in September), well inside the feed's depth at an hourly poll; descriptions are ~390-character summaries, so full mode. Overlap: an OCC rulemaking also appears in the Federal Register, which govinfo-fr already collects; the two are separate documents (the bulletin is OCC's notice to banks), not merged. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls OCC's Bulletins RSS feed via AgencyClient, then fetches each new bulletin for full text (mode full). The feed carries no GUIDs, so identity is the bulletin link. |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 10 item(s) in the last 14 days; most recent 2026-10-05; 0 of 139 request(s) to www.occ.gov returned no content.

This label has held since 2026-10-05T23:57:58Z (UTC) and was last re-checked 2026-10-08T03:55:12Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 53 request(s) (53 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 10 in 14 days (0.71 per day) · most recent 2026-10-05 |
| Content length | 7,408 characters average, 6,226 median (shortest 5,316, longest 12,791) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.occ.gov | 139 request(s) · 139 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-08T04:00:12.445+00:00 UTC; this host serves 2 registered sources, so these figures are host-wide.

10 item(s) in the last 14 days; most recent 2026-10-05; 0 of 139 request(s) to www.occ.gov returned no content.

### All time

- **Our requests to www.occ.gov, all time (since 2026-10-05):** 139 request(s) · 139 answered · 0 returned no content

This host serves 2 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.occ.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
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
| 2026-10-05 | 10 | 32 | 121 |
| 2026-10-06 | 0 | 52 | 215 |
| 2026-10-07 | 0 | 53 | 203 |
| 2026-10-08 | 0 | 2 | 296 |

## Our ingestion assessment

**Model-written ingestion assessment**

Newly ingested starting 2026-10-05, the feed delivers OCC bulletins at a measured rate of 0.71 per day. Ten items were observed spanning late September through early October, each averaging 7,408 characters of extracted text. All 34 requests to www.occ.gov succeeded. The feed carries RFC 822–formatted dates without weekday information and no GUIDs; item identity is established by the bulletin link.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

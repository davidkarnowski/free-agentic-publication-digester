<!-- Markdown twin of https://fapd.info/sources/nlrb-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nlrb-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nlrb-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NLRB News Releases

active · ingestion health: delivering · Executive · Tier 1 · RSS feed · Independent agency

Official site: https://www.nlrb.gov/news-publications/news/news-releases · All sources: [sources.md](../sources.md)

## What this source is

The National Labor Relations Board adjudicates private-sector labor-relations cases and conducts union elections. Its news-release index carries announcements of board decisions, election results, and enforcement actions, typically a few items per week.

**Model-written orientation**

The National Labor Relations Board adjudicates labor-relations disputes in the private sector and oversees union elections, publishing news releases on board decisions and enforcement actions.

The National Labor Relations Board (NLRB) is an independent federal agency that administers labor law in the private sector. The board hears cases involving alleged violations of the National Labor Relations Act, which governs the rights of private-sector employees to organize, engage in collective bargaining, and take part in union activities, and it also protects employer rights to certain management functions. The board also oversees union elections and decertifications. The agency has five board members, a general counsel, and regional offices across the country. Its news-release index announces significant board decisions, election results and related developments, and enforcement actions, typically publishing a few items per week. The types of cases the board handles include disputes over unfair labor practices, questions about whether employees want union representation, and appeals of regional office decisions. In this digest you will see the board's press releases describing recently decided cases, election outcomes, enforcement actions, and other agency developments. Each release carries details of the matter involved, the board's decision or action, and relevant facts. A single release may cover one case or multiple related cases. Readers interested in labor-relations policy, union representation, or the enforcement of labor law will find the board's releases a direct source for its decisions. Because the board is an adjudicatory body rather than a rulemaking one, its press releases reflect the outcomes of cases brought before it and actions taken by its general counsel and regional offices, not proposed rules or policy positions.

_Model-written orientation, generated 2026-10-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nlrb-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | RSS feed |
| Status | active |
| Tier | 1 |
| URL (feed) | https://www.nlrb.gov/rss/rssPressReleases.xml |
| URL (home) | https://www.nlrb.gov/news-publications/news/news-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 229 article link(s); 1 dated inside the 7-day lookback, 26 dated outside it, 202 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). ACTIVATED 2026-10-05 (operator) on https://www.nlrb.gov/rss/rssPressReleases.xml, listed on NLRB's own RSS page (nlrb.gov/resources/rss-feeds), which is how it was found after the convention guesses failed. Probed 2026-10-04 through FAPD's identified probe client. Re-verified 2026-10-05 from the operator machine as a brief test, outside the server's budget, through FAPD's identified probe client (robots allows, no crawl-delay, no Retry-After, HTTP 200): 10 items, 10/10 with GUID and date; newest 2026-09-11, the same five newest dates the listing page shows (NLRB had posted nothing newer). The feed's descriptions carry the release text (~2,800 characters on average); the article is fetched anyway for the page of record (sample extracted at 10,520 characters). Coverage (gate 3): 10 items spanned 2026-08-17 to 09-11, about three a week, inside the feed's depth at an hourly poll. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | RSS feed |
| Method | Polls the press-release RSS feed via AgencyClient, then fetches each new release for full text (mode full). |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 10 item(s) in the last 14 days; most recent 2026-10-05; 0 of 16 request(s) to www.nlrb.gov returned no content.

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
| Content length | 11,187 characters average, 10,592 median (shortest 10,123, longest 13,081) |
| Delivery mode | full — full article text, fetched from the item's own page |
| Our requests to www.nlrb.gov | 16 request(s) · 16 answered · 0 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.0% returned no content |

last answered request 2026-10-06T04:00:15.660+00:00 UTC.

10 item(s) in the last 14 days; most recent 2026-10-05; 0 of 16 request(s) to www.nlrb.gov returned no content.

### All time

- **Our requests to www.nlrb.gov, all time (since 2026-10-05):** 16 request(s) · 16 answered · 0 returned no content

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.nlrb.gov | Mean response time (ms) |
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
| 2026-10-05 | 10 | 15 | 202 |
| 2026-10-06 | 0 | 1 | 576 |

## Our ingestion assessment

**Model-written ingestion assessment**

NLRB press releases arrive through an RSS feed with full article text extracted from linked pages. The source was activated on 2026-10-05. In the single day of collection measured, 10 items were ingested spanning August through early October publication dates. Extracted text averaged 11,187 characters; feed descriptions provide approximately 2,800 characters. The feed carries no GUIDs, so item identity depends on the release link. All 16 requests to www.nlrb.gov succeeded without error or no-content responses. Items arrived in a concentrated poll window.

_Model-written assessment of our own ingestion, generated 2026-10-06 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/nlrb-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nlrb-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nlrb-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NLRB News Releases

planned · Executive · Tier 1 · HTML index · Independent agency

Official site: https://www.nlrb.gov/news-publications/news/news-releases · All sources: [sources.md](../sources.md)

## What this source is

The National Labor Relations Board adjudicates private-sector labor-relations cases and conducts union elections. Its news-release index carries announcements of board decisions, election results, and enforcement actions, typically a few items per week.

**Model-written orientation**

The National Labor Relations Board, an independent agency, adjudicates disputes over union representation and unfair labor practices in the private sector; its newsroom publishes announcements of decisions, election results, and enforcement actions.

The National Labor Relations Board is an independent agency established under the National Labor Relations Act to administer federal labor law in the private sector. The NLRB has two principal functions: conducting elections to determine whether workers wish to be represented by a union, and adjudicating disputes over whether employers or unions have violated federal labor law.

The NLRB operates through its General Counsel's office, which investigates and prosecutes unfair-labor-practice charges, and its administrative law judges and board members, who conduct elections and render decisions. The agency is structured to insulate its decision-making from political direction, though the President appoints board members with Senate confirmation.

NLRB press releases announce outcomes of major board decisions in labor disputes, results of representation elections, enforcement actions taken by the General Counsel, and updates on board operations. A reader will see announcements of decisions in cases involving union recognition disputes, claims of unfair labor practices, strikes, and related labor matters. The agency also announces procedural updates and changes to its operations. These releases become the official public record of board actions and provide the initial notice of decisions before they appear in legal databases or official reporter systems.

The NLRB's press releases reflect the full scope of federal private-sector labor law and the disputes that arise under it. They serve as the agency's primary means of communicating its enforcement and adjudicatory work to the public and interested parties.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nlrb-newsroom` |
| Agency / parent organization | Independent agency |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.nlrb.gov/news-publications/news/news-releases |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 229 article link(s); 1 dated inside the 7-day lookback, 26 dated outside it, 202 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the news-release HTML index daily for new items. |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.nlrb.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

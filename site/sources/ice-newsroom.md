<!-- Markdown twin of https://fapd.info/sources/ice-newsroom.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ice-newsroom.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ice-newsroom)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# ICE Newsroom

planned · Executive · Tier 2 · HTML index · Department of Homeland Security

Official site: https://www.ice.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

U.S. Immigration and Customs Enforcement, within DHS, enforces immigration and customs law in the interior. Its newsroom index carries news releases on enforcement and removal operations and Homeland Security Investigations cases, typically several items per week.

**Model-written orientation**

U.S. Immigration and Customs Enforcement, a division of the Department of Homeland Security, enforces immigration and customs law and publishes releases on enforcement operations.

U.S. Immigration and Customs Enforcement (ICE) is a federal law-enforcement agency within the Department of Homeland Security. ICE has two primary divisions: Enforcement and Removal Operations (ERO), which enforces immigration law in the interior of the United States; and Homeland Security Investigations (HSI), which investigates transnational crime and immigration-related criminal matters. ICE's mandate includes enforcing immigration statutes, investigating immigration crimes, securing borders and ports of entry, and managing the detention and removal of aliens subject to deportation.

Enforcement and Removal Operations identifies individuals in the United States who are deportable, pursues removal proceedings, and manages detention facilities. Homeland Security Investigations investigates human smuggling, human trafficking, document fraud, employment violations, and other crimes at the nexus of immigration and national security. ICE also administers programs such as Secure Communities and the Criminal Alien Program, which identify removable aliens in the criminal-justice system.

In this digest, you will see ICE press releases and announcements of law-enforcement operations, individual and group removals, arrests related to criminal activity, investigations and prosecutions, workplace enforcement operations, and statements on agency enforcement priorities. The releases document enforcement actions taken under immigration and customs law. Because ICE's work is enforcement-focused, its news contains details of operations, arrests, and apprehensions carried out by the agency and its partners.

_Model-written orientation, generated 2026-08-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ice-newsroom` |
| Agency / parent organization | Department of Homeland Security |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.ice.gov/newsroom |
| Registered | 2026-07-26 |
| Registry notes | Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 95 article link(s); 6 dated inside the 7-day lookback, 19 dated outside it, 70 skipped for no readable date, and the entries it lists carry the publisher's own dates. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). Probed 2026-08-06: the Drupal Views convention <index-path>/feed.xml — confirmed working on nih-news and tsa-press — returns 404 here. Recorded as a negative so the next reader does not repeat the guess: on this registry, mining a source's own captured page for feed links finds feeds, and guessing platform conventions does not (14 of 14 candidates 404'd). |

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

No requests to www.ice.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

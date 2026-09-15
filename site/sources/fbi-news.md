<!-- Markdown twin of https://fapd.info/sources/fbi-news.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fbi-news.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fbi-news)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# FBI Press Releases

planned · Executive · Tier 2 · HTML index · Department of Justice

Official site: https://www.fbi.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Federal Bureau of Investigation is the Justice Department's principal investigative agency. Its national press-release index carries announcements on investigations, arrests, and public alerts; most case-level news appears instead on field-office pages and in DOJ releases.

**Model-written orientation**

The Federal Bureau of Investigation is the Justice Department's principal investigative agency and publishes a national press-release index covering major investigations and public alerts.

The Federal Bureau of Investigation (FBI) is a bureau of the Department of Justice and serves as the primary federal law enforcement and intelligence agency for domestic matters. The FBI maintains a domestic intelligence division, investigates federal crimes, and operates specialized units focused on terrorism prevention, cybercrime, public corruption, civil rights violations, organized crime, and major thefts.

The FBI operates through 56 field offices in major cities across the United States, international legal attaché offices in U.S. embassies worldwide, and numerous smaller resident agencies. Each field office maintains its own public information office and issues press releases covering investigations, arrests, and agency activities specific to that region. The FBI also coordinates with state and local law enforcement agencies and other federal agencies on joint investigations and task forces.

The national FBI press-release index contains announcements of major national-significance investigations, arrests of note, public safety alerts, and major headquarters announcements. Many FBI cases originate at field offices or emerge through partnership with other federal agencies including the Department of Justice, which separately publishes press releases on federal prosecutions, other federal investigative agencies, and local police departments. As a result, the national FBI index represents a portion—though not the entirety—of FBI investigative activity appearing in public records.

In this digest, readers will encounter announcements of significant federal criminal investigations, arrests, public safety warnings, national security alerts, and major operational updates from FBI headquarters. The releases cover the full breadth of the FBI's investigative mandate, including terrorism prevention, cybercrime, public corruption, civil rights violations, organized crime, bank robbery, kidnapping, and other federal crimes. For comprehensive coverage of federal law enforcement activity, readers should also consult Department of Justice press releases and individual FBI field office announcements.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fbi-news` |
| Agency / parent organization | Department of Justice |
| Branch | executive |
| Type | HTML index |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.fbi.gov/news/press-releases |
| Registered | 2026-07-26 |
| Registry notes | Most FBI case news is published by field offices and by DOJ; the national index is a subset. Probed 2026-07-26: index reachable (HTTP 200); an autodiscovered feed (https://www.fbi.gov/news/press-releases/RSS) was fetched but the advertised feed did not parse as RSS/Atom; investigate. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. Against the 2026-07-31 capture it reads listing has 79 article link(s); 0 dated inside the 7-day lookback, 0 dated outside it, 79 skipped for no readable date — the served HTML states no per-entry publication date, so every entry is skipped rather than dated by observation. This is a script-rendered listing; opening it needs evidence of a dated channel, not a cadence decision. |

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

No requests to www.fbi.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

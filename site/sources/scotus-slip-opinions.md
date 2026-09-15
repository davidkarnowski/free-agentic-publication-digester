<!-- Markdown twin of https://fapd.info/sources/scotus-slip-opinions.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/scotus-slip-opinions.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: scotus-slip-opinions)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Supreme Court Slip Opinions

planned · Judicial · Tier 1 · HTML index · Supreme Court of the United States

Official site: https://www.supremecourt.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Supreme Court of the United States is the highest federal court; it does not publish through govinfo's USCOURTS collection. Its site posts slip opinions and order lists as PDFs on per-term HTML index pages, with opinions concentrated in the October-June term and each opinion led by an official syllabus.

**Model-written orientation**

The Supreme Court of the United States publishes slip opinions and order lists as PDFs on its official website, serving as the first authoritative release of the Court's decisions during its October-June term.

The Supreme Court of the United States is the nation's highest court. Unlike the federal circuit and district courts, which publish opinions through the govinfo platform, the Supreme Court maintains its own publication system. The Court's website publishes slip opinions—the authoritative first release of decisions—typically during its October-June term, along with order lists showing actions on pending cases. Each opinion is accompanied by a syllabus, a summary prepared by the Court that outlines facts, legal questions, and the Court's ruling.

The Court's term typically runs from October through June, with decisions concentrated in the latter months. During summer recess (roughly July through September), the Court publishes fewer opinions, though emergency matters may receive expedited treatment. Slip opinions are the definitive text of decisions and are later incorporated into the bound United States Reports.

Readers will encounter Supreme Court opinions on cases addressing constitutional questions, federal law interpretation, and disputes where lower courts reached conflicting decisions or important legal principles are at issue. Opinions include the majority reasoning, concurring opinions, and dissents, providing a complete record of the Court's deliberations on cases it decides to hear. The Court hears only a small fraction of petitions filed, typically around 70–80 cases per term from thousands of petitions, making each published opinion significant for understanding how the Court interprets the Constitution and federal law.

_Model-written orientation, generated 2026-08-04 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `scotus-slip-opinions` |
| Agency / parent organization | Supreme Court of the United States |
| Branch | judicial |
| Type | HTML index |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.supremecourt.gov/ |
| URL (index) | https://www.supremecourt.gov/opinions/slipopinions.aspx |
| Registered | 2026-07-26 |
| Registry notes | First planned non-govinfo primary source, admitted deliberately per GUIDE §3. Slip-opinion index is per-term; the stable .aspx alias should resolve to the current term (verify at activation). Probed 2026-07-26: index reachable (HTTP 200), no RSS/Atom feed found or autodiscovered — HTML index diffing required. Probed 2026-07-31 (from the operator machine, outside the server's daily budget): reachable, HTTP 200, robots allows, but no machine-readable feed is advertised — ingestion waits on an html-index adapter, not on the publisher. Phase 5, 2026-07-31: the html-index adapter now exists and was run against this source's captured index bytes. 67 opinions parse cleanly from the slip-opinion table, none inside the 7-day window (the Court was in summer recess). Note this is judicial record, not an agency announcement: activating it under the AGENCYPR collection would subject opinions to the agency dating rule and executive-branch tagging, so it needs its own adapter COLLECTION first, the way roll-call votes got VOTES. Activation awaits the operator's polling-cadence decision (the agency class holds 500 requests a day). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Would parse the current term's slip-opinion HTML index and fetch opinion PDFs, drafting syllabus-first (GUIDE §3 phase J2). |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

No requests to www.supremecourt.gov are recorded in the request log.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

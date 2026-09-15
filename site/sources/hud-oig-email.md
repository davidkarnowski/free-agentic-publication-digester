<!-- Markdown twin of https://fapd.info/sources/hud-oig-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/hud-oig-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: hud-oig-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# HUD Inspector General (email)

planned · Executive · Tier 3 · email bulletin · Department of Housing and Urban Development, Office of Inspector General

Official site: https://www.hudoig.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The HUD Office of Inspector General audits and investigates housing programs. Its bulletins carry audit reports, investigative results, and fraud alerts concerning public housing, mortgage insurance, and disaster-recovery funds.

**Model-written orientation**

The Department of Housing and Urban Development Office of Inspector General publishes audit reports, investigative findings, and fraud alerts concerning housing programs and disaster relief.

The Department of Housing and Urban Development administers federal housing programs serving millions of Americans, including public housing operated by local housing authorities, rental assistance for low-income families, mortgage insurance for home buyers who do not meet conventional lending requirements, and disaster recovery housing assistance following major disasters. The HUD Office of Inspector General is an independent office within the department that conducts audits and investigations of these programs.

Through this email subscription, readers receive the Office of Inspector General's audit reports examining the management and effectiveness of public housing authorities and the residents they serve, rental assistance programs operated by local housing agencies, mortgage insurance programs, and disaster recovery housing initiatives. Investigative reports address fraud, waste, and misuse of program funds by recipients, contractors, housing authorities, or others. Fraud alerts notify housing authorities, program administrators, and the public of schemes detected or suspected in housing programs and disaster recovery assistance, helping prevent future losses. The Office of Inspector General publishes these materials as audits and investigations are completed. The subscription serves HUD program administrators and officials managing federal housing programs, public housing authorities operating public housing, Congress, state and local disaster recovery officials, and those monitoring the administration and integrity of federal housing assistance.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `hud-oig-email` |
| Agency / parent organization | Department of Housing and Urban Development, Office of Inspector General |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.hudoig.gov/newsroom |
| URL (signup) | https://www.hudoig.gov/subscribe |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). The signup page returns HTTP 403 to our identified client; recorded as observed, not evaded. Partial coverage for the department: hud-newsroom returns HTTP 403 to our identified client and the HUD-NEWS-L press listserv signup did not complete — the IG stream is oversight material, not the department's own announcements. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. Gate-3 coverage evaluation (2026-07-31, from live delivery): 1 bulletin -> 1 item on 2026-07-30, mode email-full (avg 852 chars). DKIM verified with the key archived; the bulletin stream is the subscription's own measure of coverage. Gate-3 coverage evaluation (2026-07-31, from live delivery): 4 bulletins -> 4 items on 2026-07-30, mode email-full (avg 1,602 chars). DKIM verified with the key archived; the bulletin stream is the subscription's own measure of coverage. Gate-3 coverage evaluation (2026-07-31, from live delivery): 1 bulletin -> 1 item on 2026-07-31, mode email-full (avg 757 chars); the web channel is separately active but degraded. DKIM verified with the key archived; the bulletin stream is the subscription's own measure of coverage. Gate-3 coverage evaluation (2026-07-31, from live delivery): 4 bulletins -> 4 items across 2026-07-30/31, mode email-full (avg 2,234 chars); SSA's web newsroom refuses our client, so this is the agency's only working path. DKIM verified with the key archived; the bulletin stream is the subscription's own measure of coverage. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

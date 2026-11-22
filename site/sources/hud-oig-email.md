<!-- Markdown twin of https://fapd.info/sources/hud-oig-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/hud-oig-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: hud-oig-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# HUD Inspector General (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Housing and Urban Development, Office of Inspector General

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
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 2 item(s) in the last 14 days; most recent 2026-11-19, delivered by email.

This label has held since 2026-11-17T18:51:42Z (UTC) and was last re-checked 2026-11-22T04:56:32Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-11-19 |
| Content length | 1,858 characters average, 1,858 median (shortest 1,836, longest 1,881) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 2 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-11-19 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

2 item(s) in the last 14 days; most recent 2026-11-19, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 0 |
| 2026-10-27 | 0 |
| 2026-10-28 | 0 |
| 2026-10-29 | 0 |
| 2026-10-30 | 0 |
| 2026-10-31 | 0 |
| 2026-11-01 | 0 |
| 2026-11-02 | 0 |
| 2026-11-03 | 0 |
| 2026-11-04 | 0 |
| 2026-11-05 | 0 |
| 2026-11-06 | 0 |
| 2026-11-07 | 0 |
| 2026-11-08 | 0 |
| 2026-11-09 | 0 |
| 2026-11-10 | 0 |
| 2026-11-11 | 0 |
| 2026-11-12 | 0 |
| 2026-11-13 | 0 |
| 2026-11-14 | 0 |
| 2026-11-15 | 0 |
| 2026-11-16 | 0 |
| 2026-11-17 | 1 |
| 2026-11-18 | 0 |
| 2026-11-19 | 1 |
| 2026-11-20 | 0 |
| 2026-11-21 | 0 |
| 2026-11-22 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

We ingest HUD Office of Inspector General bulletins from hudoig@info.hudoig.gov through the email adapter. Messages are full-text, captured raw and DKIM-verified before parsing, so no article fetch is made. The 14-day window holds one item, dated 2026-11-17, measuring 1,836 characters. The mailbox counter records one bulletin, with no errors and no refused messages, last received 2026-11-17T18:42:05Z. Health reads delivering. The registry status is planned, and the subscription was confirmed 2026-07-29. The registry notes record that the signup page returned HTTP 403 to our identified client. That response was recorded as observed and was not worked around. The department's newsroom also returned HTTP 403 to our client, and a HUD-NEWS-L signup did not complete. The registry describes this stream as Inspector General oversight material, not the department's own announcements. The 2026-07-31 coverage evaluations recorded bulletin-to-item matches. Compared with the previous assessment, which recorded one item dated 2026-10-13 at 4,202 characters, the current window holds a different item, dated 2026-11-17, at 1,836 characters.

_Model-written assessment of our own ingestion, generated 2026-11-18 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

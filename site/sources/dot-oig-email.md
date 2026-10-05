<!-- Markdown twin of https://fapd.info/sources/dot-oig-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/dot-oig-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: dot-oig-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DOT Inspector General (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Transportation, Office of Inspector General

Official site: https://www.oig.dot.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of Transportation's Office of Inspector General audits and investigates the department's programs. Its bulletins announce audit reports, audits initiated, and investigative results.

**Model-written orientation**

The Department of Transportation's Office of Inspector General publishes bulletins announcing audit reports and investigative findings related to DOT programs and operations.

The Department of Transportation's Office of Inspector General (OIG) is an independent audit and investigative office within the DOT. Like other inspectors general across the federal government, the DOT OIG provides oversight of the department's operations, programs, and spending to ensure compliance with law and efficient use of federal funds.

The DOT OIG's email bulletins announce completed audit reports, audits initiated, and investigative findings. Audit reports examine DOT programs and operations across the department's various agencies and modes of transportation oversight—including aviation, highways, rail, maritime, and public transit. Reports may examine specific programs, safety initiatives, grant management, or internal operations. Investigative findings address potential fraud, waste, or misconduct by DOT employees, contractors, or others involved in DOT-funded activities.

The department is a large federal agency with significant responsibilities across the transportation sector. Readers of this digest will see announcements of independent oversight examining DOT's work. These announcements provide insight into the department's operations as reviewed by an independent office within it—findings and recommendations that may shape future departmental policy or operations.

As with other inspector general offices, the release of an audit report is distinct from implementation of its recommendations. An audit report discloses findings to Congress, the DOT, and the public; the department then decides what actions to take in response. Items appear in the digest as the OIG releases them and do not include earlier reports or findings not yet published through the email channel.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `dot-oig-email` |
| Agency / parent organization | Department of Transportation, Office of Inspector General |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.oig.dot.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDOTOIG/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: oversight-gov, transportation-email, transportation-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 3 item(s) in the last 14 days; most recent 2026-10-02, delivered by email.

This label has held since 2026-09-30T13:28:48Z (UTC) and was last re-checked 2026-10-05T03:47:32Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-02 |
| Content length | 3,391 characters average, 3,407 median (shortest 3,301, longest 3,464) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 3 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-02 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

3 item(s) in the last 14 days; most recent 2026-10-02, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 0 |
| 2026-09-09 | 0 |
| 2026-09-10 | 0 |
| 2026-09-11 | 0 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 0 |
| 2026-09-15 | 0 |
| 2026-09-16 | 0 |
| 2026-09-17 | 0 |
| 2026-09-18 | 0 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 0 |
| 2026-09-22 | 0 |
| 2026-09-23 | 0 |
| 2026-09-24 | 0 |
| 2026-09-25 | 0 |
| 2026-09-26 | 0 |
| 2026-09-27 | 0 |
| 2026-09-28 | 0 |
| 2026-09-29 | 0 |
| 2026-09-30 | 1 |
| 2026-10-01 | 1 |
| 2026-10-02 | 1 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

This source delivers bulletins through GovDelivery email subscription. The previous assessment from 2026-09-27 recorded zero bulletins after the 2026-09-26 registration date. As of 2026-10-01, the source has delivered one bulletin on 2026-09-30 during UTC hour 9. The bulletin contained 3,464 characters in full-text format. The collector has maintained stable mailbox access throughout with no delivery errors. No delivery pattern beyond the single observation is yet apparent. Gate-3 coverage evaluation proceeds with the first ingested bulletin. Related sources that may publish the same news include oversight-gov, transportation-email, and transportation-newsroom; items duplicated at the same URL merge as corroboration, while the same event at different URLs are listed separately.

_Model-written assessment of our own ingestion, generated 2026-10-01 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

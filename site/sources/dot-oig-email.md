<!-- Markdown twin of https://fapd.info/sources/dot-oig-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/dot-oig-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: dot-oig-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DOT Inspector General (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Transportation, Office of Inspector General

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-28T03:57:50Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — none recorded in the lookback period |
| Mailbox | no message from this sender in the last 14 days |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

No bulletin recorded from this source in the last 180 days.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

## Our ingestion assessment

**Model-written ingestion assessment**

This source was registered on 2026-09-26 via the GovDelivery email subscription service. No bulletins have been recorded since registration. The collector has maintained stable contact with the email system through the measurement period (2026-09-21 through 2026-09-27), with no delivery errors reported. The mailbox statistics show zero messages received, zero administrative entries, and zero refused messages. Gate-3 coverage evaluation is pending first ingested bulletins. Related sources that may publish overlapping news include oversight-gov, transportation-email, and transportation-newsroom; any items that duplicate at the same URL will merge as corroboration, while the same event at different URLs will be listed separately.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

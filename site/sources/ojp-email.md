<!-- Markdown twin of https://fapd.info/sources/ojp-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ojp-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ojp-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Office of Justice Programs (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Justice, Office of Justice Programs

Official site: https://www.ojp.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of Justice Programs administers the Justice Department's grant programs, including the Office for Victims of Crime. Its bulletins carry funding opportunities and grant program notices.

**Model-written orientation**

The Office of Justice Programs administers the Department of Justice's grant programs and research initiatives, including funding for law enforcement, courts, and victim services. Its emails carry grant announcements, funding opportunities, and program notices.

The Office of Justice Programs (OJP) is the principal research and grant-making arm of the Department of Justice. It operates multiple offices and programs that distribute federal funding to states, localities, and nonprofits for criminal justice initiatives, supporting law enforcement, courts, corrections, victim services, research, and technology innovation. OJP's component offices include the National Institute of Justice (research), the Bureau of Justice Statistics (data and analysis), the Office for Victims of Crime, and the Office of Juvenile Justice and Delinquency Prevention, among others.

OJP administers billions of dollars annually in grants and cooperative agreements, making it a major source of federal funding for criminal justice work at the state and local level. Grant programs support a wide range of activities: law enforcement training and equipment, court technology and management improvements, corrections and reentry programs, victim assistance services, research on criminal justice topics, and data collection initiatives. Funding is typically distributed through competitive solicitations with specific eligibility requirements and reporting obligations.

When OJP appears in the digest, you will see announcements of new grant solicitations, funding opportunity notices with application deadlines, grant awards, program updates, research findings, and administrative notices about existing programs. Documents may include changes to funding eligibility or application requirements, technical assistance announcements, and updates on OJP initiatives.

The Office of Justice Programs coordinates with other Justice Department components and works with federal, state, and local partners. Its announcements often affect criminal justice professionals, government agencies, research institutions, and nonprofits working in victim services and criminal justice reform. The scope of OJP's work means you may see funding announcements relevant to police departments, courts, prosecutors, public defenders, corrections agencies, and community organizations.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ojp-email` |
| Agency / parent organization | Department of Justice, Office of Justice Programs |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.ojp.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDOJOJP_COMMS/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: justice-email, justice-newsroom, bjs-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-27T03:49:31Z (UTC).

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

This source delivers bulletins through the project mailbox using the GovDelivery platform across multiple registered sender addresses. Subscription was confirmed through the publisher's signup flow in September 2026, and the source was registered for automated ingestion on 2026-09-26. Bulletins matching these senders were already present in the mailbox before registration; ingestion begins with the first poll following deployment. No bulletins have been recorded from this source since registration. The collector has accessed the mailbox without errors, observing zero messages associated with these senders across the past week. No delivery pattern, cadence, or format characteristics are yet observable. Gate-3 coverage evaluation awaits the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

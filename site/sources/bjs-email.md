<!-- Markdown twin of https://fapd.info/sources/bjs-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/bjs-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: bjs-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Bureau of Justice Statistics (email)

planned · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Justice, Office of Justice Programs, Bureau of Justice Statistics

Official site: https://bjs.ojp.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Bureau of Justice Statistics is the Justice Department's statistical agency. Its bulletins announce statistical reports, data releases, and funding opportunities.

**Model-written orientation**

The Bureau of Justice Statistics publishes statistical reports, data releases, and funding announcements related to criminal justice and law enforcement.

The Bureau of Justice Statistics (BJS), a division of the Department of Justice, is the federal government's principal source of statistics on crime, criminal justice, and law enforcement. The bureau conducts or coordinates major data collection programs on crime victimization, criminal offending, the court system, correctional facilities and populations, law enforcement agencies, and other aspects of the justice system.

The BJS email bulletins announce the release of statistical reports, new datasets, research findings, and funding opportunities. Readers of the digest will see notices of newly available statistics on topics such as crime and victimization trends, characteristics of the incarcerated population, sentencing patterns, law enforcement agency operations, and the performance and conditions of correctional facilities. The bureau also announces grants, fellowships, or other funding for research and capacity-building in the justice statistics field.

BJS data is used by researchers, policy analysts, criminal justice practitioners, and others seeking to understand the nation's justice system through reliable statistics. The bureau publishes both raw data files and analytical reports that synthesize findings for broader audiences. Data releases are often accompanied by summary reports highlighting key findings.

Like other statistical agencies within the federal government, BJS focuses on measurement and analysis rather than policy-making or enforcement. Its role is to provide factual, comprehensive data that illuminate how the nation's criminal justice system operates and changes over time. Items appear in the digest as BJS releases them through the email channel and do not include earlier releases or reports published before the email subscription was activated.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `bjs-email` |
| Agency / parent organization | Department of Justice, Office of Justice Programs, Bureau of Justice Statistics |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://bjs.ojp.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDOJOJP_COMMS/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: justice-email, justice-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-10-01T14:38:17Z (UTC) and was last re-checked 2026-10-07T03:45:41Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-01 |
| Content length | 1,379 characters average, 1,379 median (shortest 1,379, longest 1,379) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-01 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-09-30 | 0 |
| 2026-10-01 | 1 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The Bureau of Justice Statistics subscription was registered on 2026-09-26 via GovDelivery. One bulletin was observed in the 14-day measurement window, delivered on 2026-10-01, measuring 1,379 characters. The email adapter is functioning without errors. This is the first ingested bulletin from this source since registration. The bulletin carries the full text of a statistical report announcement or data release. Earlier bulletins present in the mailbox before registration were not backfilled.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

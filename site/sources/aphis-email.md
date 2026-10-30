<!-- Markdown twin of https://fapd.info/sources/aphis-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/aphis-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: aphis-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Animal and Plant Health Inspection Service (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Agriculture, Animal and Plant Health Inspection Service

Official site: https://www.aphis.usda.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Animal and Plant Health Inspection Service protects U.S. agriculture from animal and plant pests and diseases. Its stakeholder bulletins carry regulatory actions, emergency notifications, and program announcements.

**Model-written orientation**

APHIS's bulletin service delivers regulatory notices, emergency notifications, and program announcements to agriculture industry stakeholders via email.

The Animal and Plant Health Inspection Service is a federal agency within the Department of Agriculture that protects U.S. agriculture and natural resources from animal and plant pests and diseases. APHIS conducts disease surveillance, quarantines, inspections, and enforcement to prevent the introduction and spread of regulated pests and diseases in the United States.

APHIS publishes a subscription bulletin service via GovDelivery that delivers regulatory and operational announcements to agriculture industry stakeholders. Subscribers include farmers, ranchers, agricultural organizations, veterinarians, manufacturers, importers, and other industry participants who need notification of regulatory actions, disease outbreaks, and program changes.

Readers will see from this source email announcements containing APHIS regulatory actions, emergency notifications of disease detections or outbreaks, new or amended regulations affecting agricultural imports or operations, quarantine notices, program announcements and deadlines, event notifications, and updates to APHIS procedures or systems. The bulletins typically address matters with direct operational impact on agricultural businesses and producers, such as new import requirements, disease-control measures, or program enrollment deadlines.

APHIS publishes these bulletins at regular intervals as regulatory actions and events occur. Volume varies depending on disease activity, trade matters, and regulatory priorities. Bulletins are dated at the time APHIS sends them.

The digest receives this source through an email subscription to APHIS's GovDelivery service. Bulletins are captured as full email text and authenticated via DKIM signature verification to ensure they originate from APHIS's authorized sender. Bulletins are ingested starting from the date of subscription; earlier bulletins in the mailbox are not backfilled. The specific topics included in the bulletin stream depend on subscription settings selected at signup. A web copy of a bulletin, where available, is cited alongside the archived email. The same announcement published at the same URL through a different channel is noted as corroborated; the same announcement at a different URL is listed separately.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `aphis-email` |
| Agency / parent organization | Department of Agriculture, Animal and Plant Health Inspection Service |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.aphis.usda.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDAAPHIS/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation (2026-09-28, from live delivery): 1 bulletin -> 1 item on 2026-09-28 (a stakeholder event notice, "Reminder: Bird Biosecurity Webinar Sep 29"). The bulletin carries no link to a web copy, so the item cites the archived message itself. DKIM-verified with the key archived; signed by subscribers.usda.gov, which aligns with the sender's domain. One bulletin is a thin sample, and the topic selection made at signup was not recorded, so this evaluation claims no coverage relationship to the agency's full output: the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector and shown on the source page. Related entries that can publish the same news: agriculture-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Poll cadence | the project mailbox is read about every 15 minutes |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 3 item(s) in the last 14 days; most recent 2026-10-29, delivered by email.

This label has held since 2026-09-28T14:07:50Z (UTC) and was last re-checked 2026-10-30T03:49:13Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-29 |
| Content length | 3,238 characters average, 2,446 median (shortest 1,852, longest 5,416) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 4 bulletin(s), 0 subscription notice(s), 3 junk-folder message(s) refused on a failed or unaligned DKIM signature in the last 14 days; most recent message 2026-10-29 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

3 item(s) in the last 14 days; most recent 2026-10-29, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-10-01 | 1 |
| 2026-10-02 | 1 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 3 |
| 2026-10-06 | 2 |
| 2026-10-07 | 3 |
| 2026-10-08 | 1 |
| 2026-10-09 | 1 |
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 1 |
| 2026-10-14 | 0 |
| 2026-10-15 | 1 |
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 0 |
| 2026-10-20 | 1 |
| 2026-10-21 | 0 |
| 2026-10-22 | 0 |
| 2026-10-23 | 1 |
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 0 |
| 2026-10-27 | 0 |
| 2026-10-28 | 0 |
| 2026-10-29 | 1 |
| 2026-10-30 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

APHIS bulletins are ingested by email from the project mailbox. The bulletins carry full text, the item cites the archived message because the bulletin contains no web link, and DKIM verification passes with the signing domain aligned to the sender. The average item is 3,238 characters (median 2,446, range 1,852 to 5,416). In the last 14 days we ingested 3 items, the most recent dated 2026-10-29. The mailbox recorded 7 messages in total: 4 bulletins were ingested and 3 were refused, with no collector errors. The measured data does not record the reason for the refusals. The registry notes that the subscription's topic selection at signup was not recorded, and that the coverage evaluation rests on a single bulletin and claims no relationship to the agency's full output. Since the previous assessment on 2026-09-29, which described one bulletin of about 1,051 characters with no refusals, the stream now shows 3 items, 4 bulletins, and 3 refused messages.

_Model-written assessment of our own ingestion, generated 2026-10-30 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

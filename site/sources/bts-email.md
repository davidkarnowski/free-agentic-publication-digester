<!-- Markdown twin of https://fapd.info/sources/bts-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/bts-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: bts-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Bureau of Transportation Statistics (email)

planned · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Transportation, Bureau of Transportation Statistics

Official site: https://www.bts.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Bureau of Transportation Statistics is the Department of Transportation's statistical agency. Its bulletins announce data releases on freight, fuel prices, travel, and transportation economics.

**Model-written orientation**

The Bureau of Transportation Statistics publishes data releases and announcements on freight movements, transportation costs, travel patterns, and transportation economics.

The Bureau of Transportation Statistics (BTS), a division of the Department of Transportation, is the federal government's principal source of statistics on transportation systems and their use. The bureau conducts data collection and analysis across all modes of transportation—air, rail, highway, transit, and maritime—and produces statistics on freight movements, passenger travel, transportation safety, and the economic performance of transportation sectors.

The BTS email bulletins announce the release of statistical reports, datasets, and research findings. Readers of the digest will see notices of newly available data on topics such as freight volume and movements across the nation's transportation networks, fuel prices and energy consumption in transportation, passenger travel trends and mode shares, airport operations and traffic, and economic measures like transportation industry employment or transportation spending. The bureau also announces its data release schedules, giving users and researchers notice of when new data will become available.

BTS data is widely used by researchers, transportation planners, businesses, and policymakers to understand trends and inform decisions. The bureau publishes both raw datasets and analytic reports that summarize findings. Announcements in this digest signal when new data and reports become available for public access.

Unlike regulatory or enforcement agencies, BTS focuses on measurement and analysis rather than rule-making or oversight. Its role is to gather and publish transportation data so that the public, researchers, and decision-makers have factual information about how the nation's transportation systems operate and their use over time. Items appear in the digest as BTS releases them through the email channel and do not include earlier releases not published through this subscription.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `bts-email` |
| Agency / parent organization | Department of Transportation, Bureau of Transportation Statistics |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.bts.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USDOT/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: transportation-email, transportation-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 2 item(s) in the last 14 days; most recent 2026-09-30, delivered by email.

This label has held since 2026-09-30T15:21:24Z (UTC) and was last re-checked 2026-10-02T03:48:29Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 2 in 14 days (0.14 per day) · most recent 2026-09-30 |
| Content length | 3,364 characters average, 3,364 median (shortest 2,251, longest 4,477) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 2 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-09-30 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

2 item(s) in the last 14 days; most recent 2026-09-30, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-03 | 0 |
| 2026-09-04 | 0 |
| 2026-09-05 | 0 |
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
| 2026-09-30 | 2 |
| 2026-10-01 | 0 |
| 2026-10-02 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

This source delivers bulletins through GovDelivery email subscription. The previous assessment from 2026-09-27 recorded zero bulletins after the 2026-09-26 registration date. As of 2026-10-01, the source has delivered two bulletins on 2026-09-30, ingested during UTC hours 11 and 13. The bulletins ranged from 2,251 to 4,477 characters with a median of 3,364 characters, both in full-text format. The collector has maintained stable mailbox access throughout with no delivery errors. Cadence cannot yet be established from a single delivery day. Gate-3 coverage evaluation proceeds with the first ingested bulletins. Related sources that may publish the same news include transportation-email and transportation-newsroom; items duplicated at the same URL merge as corroboration, while the same event at different URLs are listed separately.

_Model-written assessment of our own ingestion, generated 2026-10-01 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

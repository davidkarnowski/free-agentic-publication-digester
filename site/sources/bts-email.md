<!-- Markdown twin of https://fapd.info/sources/bts-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/bts-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: bts-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Bureau of Transportation Statistics (email)

planned · ingestion health: no data · Executive · Tier 2 · email bulletin · Department of Transportation, Bureau of Transportation Statistics

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-30T03:54:28Z (UTC).

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

This source was registered on 2026-09-26 via the GovDelivery email subscription service. No bulletins have been recorded since registration. The collector has maintained stable contact with the email system throughout the measurement period (2026-09-21 through 2026-09-27), with no errors reported. The mailbox log shows zero messages, zero administrative entries, and zero refused messages. Gate-3 coverage evaluation is pending first ingested bulletins. Related sources that can publish the same announcements include transportation-email and transportation-newsroom; duplicate items at the same URL will merge as corroboration, while the same event at a different URL will be listed separately.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

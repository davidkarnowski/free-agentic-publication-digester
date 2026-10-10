<!-- Markdown twin of https://fapd.info/sources/epa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/epa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: epa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# EPA News Releases (email)

planned · ingestion health: delivering · Executive · Tier 1 · email bulletin · Environmental Protection Agency

Official site: https://www.epa.gov/newsreleases · All sources: [sources.md](../sources.md)

## What this source is

The Environmental Protection Agency administers federal environmental law. Its bulletins carry news releases on enforcement settlements, permit and rule announcements, grant awards, and regional actions affecting specific communities.

**Model-written orientation**

The Environmental Protection Agency publishes bulletins announcing enforcement actions, permit decisions, rule changes, grants, and regional programs affecting environmental protection.

The Environmental Protection Agency (EPA) is an executive-branch agency established to develop and enforce regulations protecting human health and the natural environment. The agency administers federal environmental law covering air quality, water protection, waste management, and chemical safety, among other areas.

The EPA's email bulletins carry official announcements from the agency's headquarters and ten regional offices. Items typically include enforcement settlements—agreements reached when the agency determines a party has violated environmental law; permit decisions affecting industrial operations or other regulated activities; and notices of new or revised regulations and rules under EPA authority. The bulletins also announce grant awards and funding opportunities for environmental projects, research, or capacity-building work. Regional offices use the channel to alert communities and regulated parties to programs and actions affecting their areas.

A reader of this digest will see the range of the EPA's regulatory and enforcement work. An enforcement action might involve a settlement with a company regarding water discharge; a permit announcement might affect a facility's operations; a rule change could shift requirements across an industry. Because the EPA has both operational reach and regulatory authority, readers see both compliance-focused announcements and policy changes that set future requirements.

It is important to note that the email subscription captures bulletins on an ongoing basis starting from the point of activation and does not retrieve earlier messages. Readers should understand that the digest reports on the bulletins sent through this particular channel; other EPA announcements and the same events may be reported through the agency's Federal Register publications or web-based newsroom, entries that appear separately in the digest. The same event may be listed multiple times if published through different channels; these are merged in presentation when they reference the same underlying document.

The EPA's enforcement, permitting, and regulatory actions are public records, and this bulletin channel provides one avenue for the agency to disseminate them to interested parties.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `epa-email` |
| Agency / parent organization | Environmental Protection Agency |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 1 |
| URL (home) | https://www.epa.gov/newsreleases |
| URL (signup) | https://www.epa.gov/newsroom/email-subscriptions-epa-headquarters-new-releases |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of epa-newsroom, whose web path robots.txt disallows — the first working input for this agency. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. Correction 2026-09-26: the subscription's bulletins arrive from [address withheld], not the confirming address, so none had been ingested; the sender was added and ingestion starts with the first poll after deploy. Earlier bulletins are not backfilled. EPA's Federal Register documents arrive separately through the FR collection; a press release about a rule and the rule itself are distinct documents and are both listed. |

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

**delivering** — 14 item(s) in the last 14 days; most recent 2026-10-09, delivered by email.

This label has held since 2026-09-29T15:58:13Z (UTC) and was last re-checked 2026-10-10T03:58:47Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 14 in 14 days (1.0 per day) · most recent 2026-10-09 |
| Content length | 3,647 characters average, 3,778 median (shortest 881, longest 9,963) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 14 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-09 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

14 item(s) in the last 14 days; most recent 2026-10-09, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-09-29 | 2 |
| 2026-09-30 | 2 |
| 2026-10-01 | 1 |
| 2026-10-02 | 5 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 1 |
| 2026-10-07 | 1 |
| 2026-10-08 | 0 |
| 2026-10-09 | 2 |
| 2026-10-10 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The EPA News Releases source delivers bulletins via email subscription (GovDelivery) to the project mailbox. Following a configuration correction in late September that identified the actual bulletin-sending address (epapress@govdelivery.epa.gov), distinct from the administrative confirmation address, ingestion began with the first poll after the correction. Over the measured period, 2 new items were delivered on 2026-09-29, averaging 3,170 characters per item (range 2,882–3,459). Both bulletins arrived within the same day, carrying full text and archive-eligible content. No backfill of earlier bulletins occurs. The email adapter operates without errors, and health status is read from delivery recency alone, as email sources generate no polling requests to track.

_Model-written assessment of our own ingestion, generated 2026-09-30 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

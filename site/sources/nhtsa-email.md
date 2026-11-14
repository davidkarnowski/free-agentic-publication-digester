<!-- Markdown twin of https://fapd.info/sources/nhtsa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nhtsa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nhtsa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# NHTSA (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Transportation (NHTSA)

Official site: https://www.nhtsa.gov/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The National Highway Traffic Safety Administration regulates vehicle safety and investigates defects. Its bulletins carry press releases, recall announcements, defect investigations, and crash-data releases — safety actions with direct consequences for vehicle owners.

**Model-written orientation**

The National Highway Traffic Safety Administration publishes vehicle safety recalls, defect investigations, and crash-data reports that directly affect vehicle owners.

The National Highway Traffic Safety Administration (NHTSA), a division of the Department of Transportation, is the federal agency responsible for regulating vehicle safety and investigating defects in automobiles and related equipment. NHTSA sets safety standards for vehicles and components, oversees recalls when safety defects are identified, conducts investigations into potential safety problems, and publishes crash data and safety trend analysis. The agency's announcements include recall notices with specific information about affected vehicles, makes, models, and years, along with remedies available to owners; notices of defect investigations and their findings; press releases about safety campaigns and initiatives; and reports on crash data and safety research. Readers will encounter time-sensitive safety information: recall announcements may apply to specific vehicle populations and require action from owners, investigation notices track NHTSA's ongoing examination of potential safety defects, and data releases inform public understanding of vehicle safety trends. The bulletins in this digest reach consumers who own or are shopping for vehicles, manufacturers and dealers who must comply with recalls and regulations, safety professionals monitoring the vehicle market, and anyone with interest in vehicle safety. Through this digest, readers stay informed about vehicle safety actions and investigations that may have direct practical consequences—a recall may require service visits, an investigation notice may indicate that a defect is being examined, and safety data provides context about vehicle reliability and risk across the fleet.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nhtsa-email` |
| Agency / parent organization | Department of Transportation (NHTSA) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.nhtsa.gov/press-releases |
| URL (signup) | https://public.govdelivery.com/accounts/USDOTNHTSA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of nhtsa-press, which returns HTTP 403 to our identified client. Activated 2026-10-01 (operator approval) on observed delivery: NHTSA's Traffic Safety Marketing list ([address withheld]) delivered to the project mailbox over the late-September changeover (e.g. 'Happening Now \| Labor Day Impaired Driving Prevention Campaigns'), so both NHTSA sender lists are carried on this one entry. Coverage caveat: the press-release list ([address withheld]) had not delivered a bulletin as of activation, and the Traffic Safety Marketing stream is campaign/awareness content, lighter signal than press releases. DKIM is recorded per message at ingest. |

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

**delivering** — 3 item(s) in the last 14 days; most recent 2026-11-13, delivered by email.

This label has held since 2026-11-06T13:06:13Z (UTC) and was last re-checked 2026-11-14T04:53:49Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 1 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-11-13 |
| Content length | 652 characters average, 702 median (shortest 199, longest 1,055) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 3 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-11-13 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

3 item(s) in the last 14 days; most recent 2026-11-13, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 2 |
| 2026-10-20 | 0 |
| 2026-10-21 | 0 |
| 2026-10-22 | 0 |
| 2026-10-23 | 0 |
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 0 |
| 2026-10-27 | 1 |
| 2026-10-28 | 1 |
| 2026-10-29 | 0 |
| 2026-10-30 | 0 |
| 2026-10-31 | 0 |
| 2026-11-01 | 0 |
| 2026-11-02 | 0 |
| 2026-11-03 | 0 |
| 2026-11-04 | 0 |
| 2026-11-05 | 0 |
| 2026-11-06 | 1 |
| 2026-11-07 | 0 |
| 2026-11-08 | 0 |
| 2026-11-09 | 1 |
| 2026-11-10 | 0 |
| 2026-11-11 | 0 |
| 2026-11-12 | 0 |
| 2026-11-13 | 1 |
| 2026-11-14 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

NHTSA bulletins reach the project mailbox from two GovDelivery sender lists, nhtsa@service.govdelivery.com and traffic_safety_marketing@service.govdelivery.com. Each message carries the full item text and is DKIM-verified and archived at ingest. Over the 14-day window we hold three bulletins at 0.21 per day, with lengths from 646 to 1,055 characters (median 683, average 795). The most recent is dated 2026-11-06. Our measurements are not broken down by sender. The mailbox recorded no administrative messages, errors, or refused messages. Compared with the 2026-11-06 assessment, which counted two bulletins at 0.14 per day, with the most recent dated 2026-10-28 and lengths from 646 to 683 characters, the window now holds one more bulletin, the most recent date has moved to 2026-11-06, and the upper length bound has risen to 1,055 characters. The registry notes that no press-release bulletin had been delivered as of activation on 2026-10-01. The sibling entry nhtsa-press has returned HTTP 403 to our identified client.

_Model-written assessment of our own ingestion, generated 2026-11-07 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

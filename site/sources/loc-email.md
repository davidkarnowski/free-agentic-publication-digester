<!-- Markdown twin of https://fapd.info/sources/loc-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/loc-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: loc-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Library of Congress (email)

active · ingestion health: delivering · Legislative · Tier 3 · email bulletin · Library of Congress

Official site: https://www.loc.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Library of Congress is the research library of Congress and the home of the U.S. Copyright Office. Its bulletins carry announcements, acquisitions, programs, and events.

**Model-written orientation**

The Library of Congress is the research library serving the U.S. Congress and the nation, and houses the U.S. Copyright Office. This digest includes announcements about the Library's collections, programs, and services distributed through its email service.

The Library of Congress is a legislative branch institution serving as the official research library of the U.S. Congress. Beyond its constitutional role supporting Congress, the Library functions as the nation's library, holding millions of items in diverse formats and serving researchers, historians, students, and members of the public. The Library of Congress also houses the U.S. Copyright Office, the federal agency responsible for copyright registration, deposit, and administration.

The Library publishes news, announcements, and information about its collections, programs, exhibitions, and services. These communications reach audiences through multiple channels, including an email service that notifies subscribers about acquisitions, new collections, public programs, legislative research services, educational resources, exhibitions, and institutional developments. The bulletins cover the Library's work in preserving American cultural and historical materials, supporting legislative research, expanding public access to collections, and serving information needs across the country.

In this digest, items from the Library of Congress appear when the institution distributes announcements and news through its email service. Readers will encounter information about new collections, public programs, exhibitions, research services, acquisitions, and other institutional developments. Each item links to the original announcement where available, providing context for the Library's work. Because this source reaches readers through email subscriptions, coverage reflects the Library's own selection of announcements deemed suitable for email distribution. The digest presents what the Library published on any given day through this channel.

_Model-written orientation, generated 2026-09-29 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `loc-email` |
| Agency / parent organization | Library of Congress |
| Branch | legislative |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.loc.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USLOC/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation (2026-09-28, from live delivery): 1 bulletin -> 1 item on 2026-09-28 (a post on the Library's blog, blogs.loc.gov, linked from the bulletin). DKIM-verified with the key archived; signed by service.govdelivery.com, the delivery platform's domain, not the agency's. The inbox rule labels and ingests such mail; the same message delivered to the junk folder would be refused (GUIDE §3, 2026-09-26). One bulletin is a thin sample, and the topic selection made at signup was not recorded, so this evaluation claims no coverage relationship to the agency's full output: the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector and shown on the source page. |

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

**delivering** — 4 item(s) in the last 14 days; most recent 2026-09-30, delivered by email.

This label has held since 2026-09-28T13:19:06Z (UTC) and was last re-checked 2026-10-01T03:53:55Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 2 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 4 in 14 days (0.29 per day) · most recent 2026-09-30 |
| Content length | 2,395 characters average, 1,132 median (shortest 733, longest 6,583) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 4 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-09-30 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

4 item(s) in the last 14 days; most recent 2026-09-30, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-02 | 0 |
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
| 2026-09-28 | 1 |
| 2026-09-29 | 1 |
| 2026-09-30 | 2 |
| 2026-10-01 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Registered 2026-09-26, began delivering 2026-09-28. One bulletin ingested in full text (~733 characters) generating one item, with no errors or refusals. DKIM signature verified and archived; signed by service.govdelivery.com, the delivery platform. Inbox rules accept such mail; the same message delivered to the junk folder would be refused. The collector maintains stable contact. A single bulletin is too thin a sample to characterize coverage; the stream is the subscription's own selection.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

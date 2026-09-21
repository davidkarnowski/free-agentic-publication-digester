<!-- Markdown twin of https://fapd.info/sources/va-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/va-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: va-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# VA Updates (email)

active · ingestion health: delivering · Executive · Tier 1 · email bulletin · Department of Veterans Affairs

Official site: https://news.va.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of Veterans Affairs administers veterans' health care, benefits, and memorial services. Its bulletins carry benefit-policy announcements, claims and eligibility changes, and health-system news reaching veterans directly.

**Model-written orientation**

The Department of Veterans Affairs sends email bulletins with benefit-policy announcements, claims and eligibility updates, and health-system news for veterans.

The Department of Veterans Affairs administers comprehensive programs serving military veterans and their families. It operates the Veterans Health Administration, the nation's largest integrated health-care system; the Veterans Benefits Administration, which processes disability compensation and pension claims; and the National Cemetery Administration. The VA sits within the executive branch as a cabinet-level department responsible for a constituency of millions of living veterans and their survivors.

The VA email subscription delivers the department's official announcements through automated bulletins. Readers receive updates when benefit-eligibility rules change, when the VA opens or modifies enrollment periods for health care or compensation programs, and when significant changes to claims-processing procedures take effect. Health-system announcements cover facility openings, closure of services, and major programmatic shifts. These bulletins represent the VA's direct-to-veteran communication channel, complementing the department's main press office. A bulletin on this feed signals information the VA considers immediately actionable for the veteran population—policy changes that affect enrollment deadlines, benefit rates, or access to care. The stream reflects the full scope of the department's operations: health services, disability and survivor benefits, home-loan programs, education benefits, and cemetery services. Readers will encounter both routine administrative notices (rate adjustments, deadline extensions) and significant policy announcements (benefits expansion, facility renovations, or program restructuring).

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `va-email` |
| Agency / parent organization | Department of Veterans Affairs |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 1 |
| URL (home) | https://news.va.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USVA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (senders [address withheld] and [address withheld]). Corroborating sibling of the active va-newsroom feed. Gate-3 coverage evaluation (2026-07-30, from live delivery): 1 bulletin -> 1 item on 2026-07-30 (department press list; corroborates the active va-newsroom feed). DKIM-verified with the key archived; the bulletin stream is the subscription's own measure of coverage, observed continuously by the collector. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Poll cadence | the project mailbox is read about every 15 minutes |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 9 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-21T03:47:52Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 9 in 14 days (0.64 per day) · most recent 2026-09-17 |
| Content length | 1,618 characters average, 593 median (shortest 156, longest 4,682) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

9 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-23 | 0 |
| 2026-08-24 | 0 |
| 2026-08-25 | 0 |
| 2026-08-26 | 1 |
| 2026-08-27 | 0 |
| 2026-08-28 | 0 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 0 |
| 2026-09-01 | 0 |
| 2026-09-02 | 1 |
| 2026-09-03 | 1 |
| 2026-09-04 | 0 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 1 |
| 2026-09-09 | 2 |
| 2026-09-10 | 0 |
| 2026-09-11 | 0 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 0 |
| 2026-09-15 | 0 |
| 2026-09-16 | 1 |
| 2026-09-17 | 5 |
| 2026-09-18 | 0 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The VA subscriptions (veteransaffairs@messages.va.gov and veteransbenefits@messages.va.gov) have delivered 3 items over the 14-day measurement window, averaging 0.21 items per day. Items arrive as full-text email bulletins to the project mailbox, with lengths ranging from 1,152 to 5,235 characters (average 3,643). Delivery has accelerated since the previous assessment on 2026-08-05, which recorded 1 item and 0.07 per day; the source now sustains more regular bulletin frequency. Most recent delivery arrived 2026-09-03. No request-level statistics apply; the email adapter confirms DKIM verification and archival of all bulletins. The collector reports no consecutive errors and full operational status as of 2026-09-05.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

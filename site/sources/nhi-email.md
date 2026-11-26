<!-- Markdown twin of https://fapd.info/sources/nhi-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/nhi-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: nhi-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# National Highway Institute (email)

active · ingestion health: quiet · Executive · Tier 3 · email bulletin · Department of Transportation (FHWA / NHI)

Official site: https://www.nhi.fhwa.dot.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The National Highway Institute is the training arm of the Federal Highway Administration. Its bulletins carry course offerings and training-program announcements for the transportation workforce.

**Model-written orientation**

The National Highway Institute (NHI) is the training division of the Federal Highway Administration, part of the Department of Transportation. It publishes bulletins announcing course offerings and professional development programs for the transportation workforce.

The National Highway Institute (NHI) is the training and professional development arm of the Federal Highway Administration (FHWA), which operates within the Department of Transportation. The FHWA oversees the nation's interstate highway system and provides technical assistance to state transportation agencies, and NHI serves as its primary vehicle for workforce development and continuing education.

NHI publishes course announcements and training-program bulletins covering a broad range of topics relevant to transportation professionals, including highway design, construction, maintenance, safety, and management. These publications are directed at practitioners—engineers, planners, administrators, and technicians—working in state departments of transportation, local governments, and the transportation consulting industry.

The documents you will see in this digest from NHI are course catalogs, training schedules, and announcements of new or updated programs. These are typically formatted as bulletins describing course content, dates, registration information, and intended audience. The content reflects NHI's role as an educational institution: most items focus on technical skills, professional certification, and updating the workforce on evolving practices and standards.

NHI operates training delivery in multiple formats, from in-person seminars to online instruction, and its publications reflect this mix. Announcements may cover new training initiatives, upcoming sessions, changes to existing programs, or resources made available to practitioners nationwide.

In the context of this digest, NHI's bulletins represent training and professional-development activities within the federal transportation system. Unlike agency press releases or policy announcements, these documents are primarily informational—they tell the transportation workforce what educational opportunities are available. The digest includes them because they represent official government activity and are part of the public record of federal agency communications.

Readers interested in transportation policy, infrastructure, or workforce development may find value in tracking these announcements. For professionals in the transportation field, NHI bulletins are a direct source of continuing education and professional advancement opportunities.

_Model-written orientation, generated 2026-10-03 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `nhi-email` |
| Agency / parent organization | Department of Transportation (FHWA / NHI) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.nhi.fhwa.dot.gov/ |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 on observed delivery (operator approval). Coverage caveat: this is a training-catalog channel (e.g. 'NHI's Lanes of Learning: Summer Edition 2026'), not a press-release stream — low digest signal, tier 3. Registered because the operator approved the DOT sub-agency set; the operator may decline it if the training content is not wanted. Subscribed through DOT's own flow (sender [address withheld]); DKIM recorded per message at ingest. |

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

**quiet** — Most recent item 2026-11-16, 10 days ago (quiet past 7 days).

This label has held since 2026-11-24T05:12:04Z (UTC) and was last re-checked 2026-11-26T04:49:09Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-11-16 |
| Content length | 1,019 characters average, 1,019 median (shortest 1,019, longest 1,019) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-11-16 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-11-16, 10 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-10-28 | 0 |
| 2026-10-29 | 0 |
| 2026-10-30 | 0 |
| 2026-10-31 | 0 |
| 2026-11-01 | 0 |
| 2026-11-02 | 0 |
| 2026-11-03 | 0 |
| 2026-11-04 | 0 |
| 2026-11-05 | 0 |
| 2026-11-06 | 0 |
| 2026-11-07 | 0 |
| 2026-11-08 | 0 |
| 2026-11-09 | 0 |
| 2026-11-10 | 0 |
| 2026-11-11 | 0 |
| 2026-11-12 | 0 |
| 2026-11-13 | 0 |
| 2026-11-14 | 0 |
| 2026-11-15 | 0 |
| 2026-11-16 | 1 |
| 2026-11-17 | 0 |
| 2026-11-18 | 0 |
| 2026-11-19 | 0 |
| 2026-11-20 | 0 |
| 2026-11-21 | 0 |
| 2026-11-22 | 0 |
| 2026-11-23 | 0 |
| 2026-11-24 | 0 |
| 2026-11-25 | 0 |
| 2026-11-26 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

National Highway Institute bulletins are ingested by the email adapter into the project mailbox from nhi@info.dot.gov, delivering full item text with DKIM recorded per message at ingest. The subscription was activated on 2026-10-01 upon observed delivery. The registry notes this is a training-catalog channel. In the 14-day window, one item was recorded, with the most recent on 2026-11-16, at a rate of 0.07 items per day and a length of 1,019 characters. The mailbox shows one bulletin and one message, last received on 2026-11-16. No delivery incidents, errors, administrative messages, or refused deliveries have been reported. Compared to the 2026-11-17 assessment, which also recorded one item on 2026-11-16 and a delivering health status, the current health status is quiet as the most recent item is now nine days old.

_Model-written assessment of our own ingestion, generated 2026-11-25 by gemini-2.5-flash, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

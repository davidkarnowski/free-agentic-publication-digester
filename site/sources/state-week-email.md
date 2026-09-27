<!-- Markdown twin of https://fapd.info/sources/state-week-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/state-week-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: state-week-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# The Week at State (email)

planned · ingestion health: quiet · Executive · Tier 2 · email bulletin · Department of State

Official site: https://www.state.gov/week-at-state/ · All sources: [sources.md](../sources.md)

## What this source is

The Department of State conducts U.S. foreign policy and diplomacy. The Week at State is the department's weekly public newsletter, summarizing diplomatic engagements, program announcements, and Secretary travel — a digest of the week rather than the press-statement stream itself.

**Model-written orientation**

The Department of State distributes a weekly email newsletter summarizing diplomatic engagements, program announcements, and State Department activities.

The Department of State conducts United States foreign policy, manages diplomatic relations with other nations, and administers consular services to Americans abroad. The Secretary of State leads the department and serves as the President's chief foreign-policy advisor. The State Department maintains embassies in nearly every country and operates a worldwide Foreign Service.

The Week at State is the department's curated weekly newsletter, distinct from its daily press-statement stream or real-time announcements. Each bulletin summarizes significant diplomatic activities and policy announcements from the preceding week, providing readers with a consolidated overview rather than individual releases. The newsletter covers the Secretary's travel and meetings with foreign leaders, major diplomatic initiatives and consultations, international conference participation, announcements of new programs or aid initiatives, personnel changes and ambassador appointments, and policy statements on regional or global issues. Readers encounter summaries of bilateral and multilateral engagement, announcements of diplomatic appointments, descriptions of new foreign-aid programs or humanitarian initiatives, and broad statements on U.S. foreign-policy priorities. The format makes it accessible to readers who want a digest of State Department activity without tracking daily press releases. The topics span all regions of the world and all functional areas of diplomacy—political relations, economic and commercial matters, development and humanitarian programs, educational and cultural exchanges, and consular affairs. The newsletter reflects the State Department's public-facing role as the institution managing U.S. relationships with the international community.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `state-week-email` |
| Agency / parent organization | Department of State |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.state.gov/week-at-state/ |
| URL (signup) | https://public.govdelivery.com/accounts/USSTATEBPA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Only partial coverage for state-newsroom: weekly and summarized, not the daily press statements or briefing transcripts. The documented state.gov press-release and briefing feeds remain the target for full coverage. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

**quiet** — Most recent item 2026-08-03, 55 days ago (quiet past 7 days).

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-27T03:49:31Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — most recent 2026-08-03 |
| Mailbox | no message from this sender in the last 14 days |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-08-03, 55 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

## Our ingestion assessment

**Model-written ingestion assessment**

The Department of State's weekly digest arrived via confirmed email subscription; one item was ingested on 2026-08-03. The source has been quiet for 55 consecutive days with no items in the 14-day measurement window, reflecting the weekly publication schedule of this summarized digest format.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

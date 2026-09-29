<!-- Markdown twin of https://fapd.info/sources/ussc-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ussc-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ussc-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Sentencing Commission News (email)

planned · ingestion health: quiet · Judicial · Tier 2 · email bulletin · U.S. Sentencing Commission

Official site: https://www.ussc.gov/topic/news · All sources: [sources.md](../sources.md)

## What this source is

The United States Sentencing Commission sets federal sentencing guidelines. Its bulletins carry guideline amendments, public hearing notices, and research reports on federal sentencing practice.

**Model-written orientation**

The United States Sentencing Commission publishes guideline amendments, public hearing notices, and sentencing research through email bulletins. This digest includes items from the Commission's subscription announcements.

The United States Sentencing Commission is an independent agency within the federal judiciary established by Congress to develop and maintain sentencing guidelines for federal crimes. The Commission comprises judges, prosecutors, defense attorneys, and public members who work together to research sentencing practice and develop uniform guidelines that inform judges in federal criminal cases.

The Commission publishes guideline amendments that clarify or modify the sentencing ranges for different offense categories and types of defendants. These amendments follow a formal process: the Commission drafts proposed amendments, solicits written and oral public comment, holds public hearings where judges, prosecutors, defense attorneys, and other stakeholders testify about the impact of proposed changes, and then issues final amendments with detailed explanations of the rationale behind each change.

The Commission also publishes research reports on federal sentencing patterns and practice. These reports analyze data on how federal judges apply the guidelines across different crime types, geographic regions, and defendant characteristics. Such reports track trends in sentencing outcomes and inform ongoing guideline revisions.

Public hearing notices announce upcoming Commission sessions where stakeholders can comment on proposed amendments. These notices include hearing dates, locations, agendas, and instructions for submitting comments.

This digest draws from the Commission's email bulletins, which announce new guideline amendments, research releases, and upcoming public hearings. Readers with interest in federal criminal sentencing, legal practice in federal courts, or policy research on sentencing outcomes will find substantive material here.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ussc-email` |
| Agency / parent organization | U.S. Sentencing Commission |
| Branch | judicial |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.ussc.gov/topic/news |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of ussc-news, whose documented RSS feed was reachable but empty at probe — the bulletin channel may prove the more reliable input for this judicial-branch agency. Signup URL not recorded: the address inferred from the sender was checked and did not resolve, so only the confirmed sender is asserted here. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

**quiet** — Most recent item 2026-08-27, 33 days ago (quiet past 7 days).

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | none in the last 14 days — most recent 2026-08-27 |
| Mailbox | no message from this sender in the last 14 days |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

Most recent item 2026-08-27, 33 days ago (quiet past 7 days).

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

## Our ingestion assessment

**Model-written ingestion assessment**

U.S. Sentencing Commission news bulletins are delivered via confirmed email subscription. One item was ingested on 2026-08-27; the source has been quiet for 31 consecutive days with no items in the 14-day measurement window.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

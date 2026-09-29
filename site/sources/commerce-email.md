<!-- Markdown twin of https://fapd.info/sources/commerce-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/commerce-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: commerce-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Department of Commerce (email)

planned · ingestion health: no data · Executive · Tier 2 · email bulletin · Department of Commerce

Official site: https://www.commerce.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Department of Commerce promotes trade, economic development, and technology, and houses the Census Bureau, NOAA, and NIST. Its communications bulletins carry departmental announcements.

**Model-written orientation**

The Department of Commerce promotes trade, economic development, and innovation, overseeing major agencies like NOAA and NIST, and publishing departmental announcements.

The Department of Commerce is a cabinet-level department with broad responsibility for promoting U.S. trade, economic development, innovation, and competitiveness. Within Commerce sit several major agencies with distinct missions: the National Oceanic and Atmospheric Administration (NOAA), which manages marine resources, ocean policy, and weather forecasting; the National Institute of Standards and Technology (NIST), which conducts scientific research and develops technical standards; and the Census Bureau, which conducts the decennial census and produces ongoing economic statistics.

The Department oversees international trade policy, export controls, and trade dispute resolution. It supports American businesses through trade promotion programs and works to attract foreign investment. Commerce also houses the Patent and Trademark Office, which administers intellectual property registration for patents and trademarks.

The bulletins from the Department of Commerce that appear in this digest originate from the departmental communications office and cover announcements from across the department's bureaus and offices. These may include trade policy updates, international commerce announcements, initiatives related to economic development or innovation, grant and funding opportunity announcements, personnel announcements, and notices of departmental events or meetings.

Because the Department of Commerce oversees multiple major agencies with diverse missions, its communications often touch on varied topics including weather and climate (NOAA), scientific standards and research (NIST), economic statistics (Census Bureau), patents and trademarks, and international trade. The departmental bulletins provide a broad view of Commerce activity and frequently direct readers to more detailed information at specific bureau websites.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `commerce-email` |
| Agency / parent organization | Department of Commerce |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.commerce.gov/news |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]); no bulletin observed as of registration (2026-09-26). Registered so the first bulletin is attributed on arrival; activate on first parsed bulletin. Related entries that can publish the same news: commerce-newsroom, census-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. commerce-newsroom's web refusal stands. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

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

The Department of Commerce email subscription was registered on 2026-09-26 through the publisher's own signup flow, with subscription confirmed at sender communications@updates.doc.gov. As of 2026-09-27, no bulletins have been received from this source. The source remains in planned status, awaiting its first bulletin to activate; subsequent bulletins will be logged upon delivery and attributed to this source.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/loc-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/loc-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: loc-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Library of Congress (email)

planned · ingestion health: no data · Legislative · Tier 3 · email bulletin · Library of Congress

Official site: https://www.loc.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Library of Congress is the research library of Congress and the home of the U.S. Copyright Office. Its bulletins carry announcements, acquisitions, programs, and events.

**Model-written orientation**

The Library of Congress is the research library of the U.S. Congress and home of the U.S. Copyright Office. This email source carries bulletins about acquisitions, programs, events, and agency announcements.

The Library of Congress is the research library of the legislative branch, serving Congress, federal agencies, researchers, and the public. It is the oldest federal cultural institution in the United States and maintains vast collections of books, manuscripts, recordings, prints, photographs, maps, digital materials, and other resources documenting American history, culture, government, and creativity. The Library also houses the U.S. Copyright Office, which registers copyrights, administers federal copyright law, and serves as the authoritative source for copyright registration and administration.

The Library's collections and services support the legislative process, historical research, and public access to American cultural and governmental heritage. It maintains extensive digital collections and provides specialized research and reference services. The Library's role extends beyond Congress to include stewardship of significant cultural materials, development of standards and best practices for libraries and information systems, and administration of federal copyright law.

Email bulletins from the Library of Congress announce new programs, exhibitions, and major acquisitions; publicize digitization projects and new digital collections; communicate copyright-related policy updates or guidance; and provide notice of events, training opportunities, and public services. Readers may see announcements of newly available digital collections, exhibitions or special events at the Library, updates to copyright registration procedures or policy, acquisitions of significant historical or cultural materials, availability of Congressional research services, notices of public programs and educational offerings, and updates to Library collections or services. The bulletins reflect the Library's multifaceted role as steward of American documentary and cultural heritage, administrator of federal copyright law, and support to Congress and the broader public.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `loc-email` |
| Agency / parent organization | Library of Congress |
| Branch | legislative |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.loc.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USLOC/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. |

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

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-27T03:49:31Z (UTC).

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

This source delivers bulletins through the project mailbox using the GovDelivery platform. Subscription was confirmed through the publisher's signup flow in September 2026, and the source was registered for automated ingestion on 2026-09-26. Bulletins matching this sender were already present in the mailbox before registration; ingestion begins with the first poll following deployment. No bulletins have been recorded from this source since registration. The collector has accessed the mailbox without errors, observing zero messages associated with this source across the past week. No delivery pattern, cadence, or format characteristics are yet observable. Gate-3 coverage evaluation awaits the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

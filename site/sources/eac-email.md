<!-- Markdown twin of https://fapd.info/sources/eac-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/eac-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: eac-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Election Assistance Commission (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · U.S. Election Assistance Commission

Official site: https://www.eac.gov/newsroom · All sources: [sources.md](../sources.md)

## What this source is

The Election Assistance Commission supports state and local election administration, certifies voting systems, and distributes election-security funding. Its bulletins carry certification decisions, guidance to election officials, grant announcements, and survey data releases.

**Model-written orientation**

The Election Assistance Commission sends email notifications on voting-system certifications, election-administration guidance, and grant and funding announcements.

The Election Assistance Commission is an independent, bipartisan agency established to support state and local election administrators in conducting elections. The EAC certifies voting systems and equipment to federal standards, distributes federal election-security grants to states, conducts research on election administration, and provides technical assistance and guidance to election officials. The commission works with state election directors and local election officials who manage voter registration, polling places, and ballot counting.

The EAC email subscription notifies subscribers of agency actions and guidance. Readers receive announcements when the EAC certifies new voting machines or updates to existing systems—detailing which systems have been approved for use in elections and meeting federal standards for security and accuracy. The subscription carries notices of election-administration guidance: recommendations for conducting recounts or audits, best practices for cybersecurity and poll-worker training, guidance on voter-assistance technology and accessibility, and advisories on emerging threats to election infrastructure. Grant announcements inform states of new federal funding opportunities for election security improvements, voting-system upgrades, or poll-worker recruitment and training. The EAC also publishes survey data releases on election administration—compiling information from state elections officials about practices, costs, and challenges—and announcements of research findings on election technology and administration. Recipients include state and county election officials, voting-system vendors, election-administration nonprofits, researchers, and members of the public interested in election security and voting access. Certification announcements specify the voting systems approved and may detail technical specifications or validation testing results. Guidance and advisory bulletins help election officials implement new procedures or address emerging operational challenges. The stream reflects the EAC's mission: supporting states and localities in administering accessible, secure elections.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `eac-email` |
| Agency / parent organization | U.S. Election Assistance Commission |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.eac.gov/newsroom |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). New coverage: no registered source before this subscription. Signup URL not recorded: the address inferred from the sender was checked and did not resolve, so only the confirmed sender is asserted here. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-10-01T18:22:50Z (UTC) and was last re-checked 2026-10-08T03:55:12Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-01 |
| Content length | 9,909 characters average, 9,909 median (shortest 9,909, longest 9,909) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-01 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
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
| 2026-09-28 | 0 |
| 2026-09-29 | 0 |
| 2026-09-30 | 0 |
| 2026-10-01 | 1 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |
| 2026-10-08 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The Election Assistance Commission subscription delivers bulletins to the project mailbox. One bulletin was observed in the 14-day window, delivered on 2026-10-01, measuring 9,909 characters and carrying substantive content on election administration guidance. The email adapter is functioning without errors. A previous assessment noted an extended quiet period; activity has resumed with this recent delivery. The larger message size indicates full article text inclusion.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

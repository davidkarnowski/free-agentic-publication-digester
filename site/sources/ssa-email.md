<!-- Markdown twin of https://fapd.info/sources/ssa-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ssa-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ssa-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# SSA Press Releases (email)

active · ingestion health: delivering · Executive · Tier 1 · email bulletin · Social Security Administration

Official site: https://www.ssa.gov/news/en/press/releases/index.html · All sources: [sources.md](../sources.md)

## What this source is

The Social Security Administration administers retirement, disability, and survivor benefits. Its bulletins carry press releases on benefit amounts, cost-of-living adjustments, policy changes, and program administration.

**Model-written orientation**

The Social Security Administration's press releases are delivered via email bulletins, covering benefit announcements, cost-of-living adjustments, policy changes, and program administration.

The Social Security Administration administers the Social Security program, which provides retirement, disability, and survivor insurance benefits to millions of Americans. Social Security is the foundation of retirement income security for older Americans and provides essential income support to workers who become disabled and to the families of deceased workers. The SSA manages the Old-Age and Survivors Insurance program, the Disability Insurance program, and Supplemental Security Income, collectively serving over 70 million beneficiaries.

The SSA communicates policy changes, benefit-related announcements, and program administration decisions through press releases distributed to the public, beneficiaries, advocates, and media. These announcements include the annual cost-of-living adjustment (COLA) to benefit amounts, announced each year to account for inflation; changes to program rules, eligibility criteria, or application procedures; major policy initiatives and legislative proposals; data releases on the beneficiary population and program finances; and administrative updates affecting how people interact with the program.

The agency distributes these press releases through subscription bulletins delivered via email. This channel reaches beneficiaries and prospective beneficiaries, advocacy organizations representing seniors and people with disabilities, media outlets covering aging and disability policy, financial advisors and financial planners, employers and human resources professionals, and others who track Social Security policy and administration. The subscription provides notification as announcements are issued, enabling stakeholders to stay current with SSA policy, benefit information, and administrative procedures.

The subscription has been confirmed with the SSA's distribution system and is currently open to receive bulletins. The email channel represents the agency's confirmed distribution mechanism for press releases and serves as the source for tracking SSA announcements in the digest.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ssa-email` |
| Agency / parent organization | Social Security Administration |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.ssa.gov/news/en/press/releases/index.html |
| URL (signup) | https://public.govdelivery.com/accounts/USSSA/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of ssa-newsroom, which returns HTTP 403 to our identified client — the first working input for this agency. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

**delivering** — 75 item(s) in the last 14 days; most recent 2026-09-24, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-25T03:53:38Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 9 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 75 in 14 days (5.36 per day) · most recent 2026-09-24 |
| Content length | 3,816 characters average, 4,255 median (shortest 607, longest 4,918) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

75 item(s) in the last 14 days; most recent 2026-09-24, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-27 | 4 |
| 2026-08-28 | 4 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 8 |
| 2026-09-01 | 4 |
| 2026-09-02 | 9 |
| 2026-09-03 | 9 |
| 2026-09-04 | 7 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 14 |
| 2026-09-09 | 13 |
| 2026-09-10 | 6 |
| 2026-09-11 | 12 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 12 |
| 2026-09-15 | 8 |
| 2026-09-16 | 9 |
| 2026-09-17 | 10 |
| 2026-09-18 | 4 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |
| 2026-09-21 | 7 |
| 2026-09-22 | 8 |
| 2026-09-23 | 8 |
| 2026-09-24 | 9 |
| 2026-09-25 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Social Security Administration press releases arrive via email subscription with full text, DKIM-verified. Over the past 14 days through 2026-09-04, the source delivered 93 items at an average of 6.64 per day, a substantial increase from the earlier 0.71 items per day observed through 2026-08-04. The subscription was confirmed 2026-07-29 and represents the only working input for this agency; the web newsroom returns HTTP 403 to our identified client. Delivery has been consistent with no consecutive failures. Text averaged 3,918 characters with a median of 4,252. The volume increase since activation reflects the agency's own distribution cadence for its benefits programs.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

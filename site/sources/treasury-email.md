<!-- Markdown twin of https://fapd.info/sources/treasury-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/treasury-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: treasury-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Treasury Press Releases (email)

active · ingestion health: delivering · Executive · Tier 1 · email bulletin · Department of the Treasury

Official site: https://home.treasury.gov/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Department of the Treasury manages federal finances, collects revenue, and administers economic sanctions. Its subscription bulletins carry press releases as the department distributes them directly to the public — sanctions designations, debt-management statements, and economic-policy announcements — reaching subscribers on the same day they are issued.

**Model-written orientation**

The Treasury Department's press releases are delivered directly to subscribers via email bulletins, covering sanctions designations, debt-management statements, and economic-policy announcements as they are issued.

The Department of the Treasury manages the nation's finances, oversees federal revenue collection, administers economic sanctions against foreign entities and individuals, and develops federal economic policy. The Treasury manages federal borrowing and debt, operates the U.S. Mint, collects federal taxes through the Internal Revenue Service, and enforces laws against money laundering and financial crimes. The department's press releases communicate official policy positions, economic data, administrative decisions, and enforcement actions to the public, financial institutions, regulated entities, and markets.

Treasury distributes its press releases through subscription bulletins delivered directly to subscribers via email. These releases cover the full scope of the department's work: sanctions designations and foreign asset control updates issued by the Office of Foreign Assets Control, Treasury securities offerings and debt-management statements, economic analyses and forecasts affecting markets and policy, tax policy announcements, departmental administrative decisions, and enforcement actions. The bulletin subscription reaches subscribers on the same day releases are issued, making it the department's direct communication channel to the public and financial sector.

The email bulletins are captured using standard email protocols, with cryptographic verification of sender authenticity (DKIM) and archival of the original message format. This subscription is the confirmed distribution list the Treasury Department uses for its own press releases, making it the working source for tracking the department's official announcements. The subscription began in 2026 and has been verified to align with the publicly announced release volume.

Release text in the bulletins includes the canonical home.treasury.gov URL where the announcement is published, providing readers direct access to the full official source and any supporting documents or data the Treasury has attached.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `treasury-email` |
| Agency / parent organization | Department of the Treasury |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 1 |
| URL (home) | https://home.treasury.gov/news/press-releases |
| URL (signup) | https://service.govdelivery.com/service/multi_subscribe.html?code=USTREAS |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of treasury-newsroom, whose web path robots.txt disallows — that refusal stands unchanged. Treasury component subscriptions also confirmed and registered separately or noted here: FinCEN (fincen-email), TTB, BEP, CDFI Fund, TIGTA, Office of Financial Research (ofr-email), and the Federal Reserve Bank of New York alerts. Gate-3 coverage evaluation (2026-07-30, from the 2026-07-29 bulletins): 5 bulletins carried 5 press releases, full text, DKIM-verified, each with its canonical home.treasury.gov URL. The subscription is the department's own press-release distribution list; because the web channel refuses our client, this is the department's first working input and the bulletin stream is the measure of its own coverage — item counts are consistent with the newsroom's public daily volume, and any gap the web page would reveal cannot be checked without crawling a site that refused us (we do not). |

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

**delivering** — 67 item(s) in the last 14 days; most recent 2026-09-14, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-15T03:50:21Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 8 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 67 in 14 days (4.79 per day) · most recent 2026-09-14 |
| Content length | 1,604 characters average, 221 median (shortest 81, longest 19,796) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

67 item(s) in the last 14 days; most recent 2026-09-14, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-17 | 10 |
| 2026-08-18 | 7 |
| 2026-08-19 | 10 |
| 2026-08-20 | 9 |
| 2026-08-21 | 8 |
| 2026-08-22 | 0 |
| 2026-08-23 | 0 |
| 2026-08-24 | 13 |
| 2026-08-25 | 5 |
| 2026-08-26 | 8 |
| 2026-08-27 | 6 |
| 2026-08-28 | 8 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 7 |
| 2026-09-01 | 9 |
| 2026-09-02 | 6 |
| 2026-09-03 | 10 |
| 2026-09-04 | 8 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 9 |
| 2026-09-09 | 8 |
| 2026-09-10 | 11 |
| 2026-09-11 | 7 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 8 |
| 2026-09-15 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Treasury press releases arrive via GovDelivery email subscription at 5.71 items per day over 14 days, representing a doubling from the 2.43 per day observed in the prior assessment. We received 80 items with the most recent arriving 2026-09-04. The bulletin stream carries full-text releases bearing home.treasury.gov URLs. This email subscription is the department's own press-release distribution list; the web newsroom path blocks our automated client, making the bulletin stream the first available input for this channel. DKIM signature verification has been applied to each bulletin. Item delivery frequency aligns with the department's release volume as observed through the email channel itself.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

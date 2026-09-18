<!-- Markdown twin of https://fapd.info/sources/justice-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/justice-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: justice-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Justice Department News (email)

active · ingestion health: delivering · Executive · Tier 1 · email bulletin · Department of Justice

Official site: https://www.justice.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Department of Justice enforces federal law. Its departmental bulletins carry Office of Public Affairs releases — indictments, plea agreements, settlements, and policy announcements — as the department distributes them, providing a second independent channel alongside the department's news feed.

**Model-written orientation**

The Justice Department's Office of Public Affairs delivers news releases via email bulletins, covering indictments, plea agreements, settlements, and policy announcements as they are issued.

The Department of Justice is the federal executive agency responsible for enforcing the law and defending the interests of the United States according to law. The department supervises 93 U.S. Attorneys' offices nationwide responsible for criminal prosecution in federal courts, litigates civil cases on behalf of the United States, enforces antitrust laws, represents the nation in Supreme Court proceedings, administers federal prisons through the Bureau of Prisons, and oversees law enforcement agencies including the Federal Bureau of Investigation, Drug Enforcement Administration, Bureau of Alcohol, Tobacco, Firearms and Explosives, and U.S. Marshals Service.

The department's Office of Public Affairs issues press releases announcing significant law enforcement actions, policy decisions, and departmental activities. These releases describe major criminal indictments and prosecutions, civil settlements and enforcement actions, policy announcements affecting the federal justice system and law enforcement, organizational decisions, and other significant departmental news. Press releases are the primary means by which the public and media learn of major federal prosecutions, departmental positions, and Justice Department policy initiatives.

The Department distributes press releases through multiple channels: an RSS news feed from the main Justice website and email subscription bulletins. The email bulletins deliver the same announcements to subscribers on the day they are released, providing an independent notification channel. Because some days generate many releases—particularly during active prosecution periods or during policy announcements—the email subscription provides an additional coverage mechanism to capture announcements that might exceed the depth available through other feeds. The email subscription was confirmed in 2026 as a corroborating channel to the existing RSS feed.

The email subscription is confirmed and actively receiving bulletins. Release text includes links to official DOJ sources, enabling readers to access the full official statement and supporting documents.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `justice-email` |
| Agency / parent organization | Department of Justice |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.justice.gov/news |
| URL (signup) | https://public.govdelivery.com/accounts/USDOJ/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Corroborating sibling of the active justice-newsroom feed, whose 25-item depth can under-cover heavy days; the bulletin stream is expected to close part of that gap. Gate-3 coverage evaluation (2026-07-30, from the 2026-07-29 bulletins): 7 bulletins yielded 3 ingested items after cross-channel dedup — most releases had already arrived via the justice-newsroom RSS feed and dedup is first-recorded-wins, which is the intended behavior for a corroborating channel. Coverage adds depth beyond the feed's 25-item window rather than new document classes; both channels are counted in coverage accounting. |

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

**delivering** — 107 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-18T03:55:01Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 12 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 107 in 14 days (7.64 per day) · most recent 2026-09-17 |
| Content length | 955 characters average, 872 median (shortest 14, longest 4,796) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

107 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-20 | 7 |
| 2026-08-21 | 10 |
| 2026-08-22 | 0 |
| 2026-08-23 | 0 |
| 2026-08-24 | 9 |
| 2026-08-25 | 14 |
| 2026-08-26 | 11 |
| 2026-08-27 | 22 |
| 2026-08-28 | 14 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 1 |
| 2026-09-01 | 22 |
| 2026-09-02 | 11 |
| 2026-09-03 | 7 |
| 2026-09-04 | 23 |
| 2026-09-05 | 0 |
| 2026-09-06 | 1 |
| 2026-09-07 | 0 |
| 2026-09-08 | 7 |
| 2026-09-09 | 13 |
| 2026-09-10 | 10 |
| 2026-09-11 | 9 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 24 |
| 2026-09-15 | 15 |
| 2026-09-16 | 16 |
| 2026-09-17 | 12 |
| 2026-09-18 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Justice Department news arrives via email carrying full-text bulletins from the Office of Public Affairs. The source delivered 134 items over 14 days through 2026-09-04, averaging 9.57 per day, roughly double the 5.07 items per day observed through 2026-08-04. The email channel operates as a corroborating input alongside the active justice-newsroom RSS feed, which maintains a 25-item depth limit. Early testing showed the email channel provides additional depth beyond the feed's sliding window while maintaining cross-channel dedup. Text ranged from 27 to 5,164 characters with a median of 773. Delivery remains consistent with no failures recorded.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

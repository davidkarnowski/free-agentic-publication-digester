<!-- Markdown twin of https://fapd.info/sources/census-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/census-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: census-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Census Bureau (email)

planned · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Commerce, U.S. Census Bureau

Official site: https://www.census.gov/newsroom.html · All sources: [sources.md](../sources.md)

## What this source is

The Census Bureau conducts the decennial census and the government's principal demographic and economic surveys. Its bulletins announce data releases, release schedules, and survey operations.

**Model-written orientation**

The U.S. Census Bureau publishes announcements of data releases from decennial census operations and ongoing demographic and economic surveys.

The U.S. Census Bureau, a division of the Department of Commerce, is the federal government's principal statistical agency for demographic and economic data. The bureau is best known for the decennial census, a constitutionally mandated count of the U.S. population every ten years, but it also operates numerous ongoing surveys that collect information on the nation's population, households, businesses, and economy throughout each year.

The Census Bureau email bulletins announce data releases, release schedules, and survey operations updates. Readers of the digest will see notices when new census data becomes available—whether decennial census data rolled out in phases following a census year, or data from the ongoing American Community Survey, the Current Population Survey, the Survey of Income and Program Participation, the Economic Census, or other surveys the bureau administers. Announcements may also include notices of survey operations, such as changes to survey methodology, release timing, or access methods.

Census data is used extensively by researchers, demographers, economists, urban planners, federal and state agencies, and businesses to understand population characteristics, economic conditions, and social trends. The bureau publishes data in multiple formats and often accompanies releases with analytical reports and visualizations. Data products range from detailed cross-tabulations to high-level summary statistics.

The Census Bureau's role is to collect and publish statistical data while maintaining privacy protections for respondents. The bureau does not make policy; rather, it provides factual information that others use for research, planning, and decision-making. Items appear in the digest as the Census Bureau publishes them through the email channel. The digest does not backfill earlier announcements or releases published before the email subscription was activated.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `census-email` |
| Agency / parent organization | Department of Commerce, U.S. Census Bureau |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.census.gov/newsroom.html |
| URL (signup) | https://public.govdelivery.com/accounts/USCENSUS/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: census-newsroom, commerce-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 9 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-09-28T16:01:47Z (UTC) and was last re-checked 2026-10-03T03:48:44Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 9 in 14 days (0.64 per day) · most recent 2026-10-01 |
| Content length | 1,694 characters average, 1,797 median (shortest 537, longest 2,854) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 9 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-01 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

9 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-04 | 0 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 0 |
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
| 2026-09-28 | 4 |
| 2026-09-29 | 3 |
| 2026-09-30 | 1 |
| 2026-10-01 | 1 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The source was registered on 2026-09-26 and began delivering bulletins on 2026-09-28. Four bulletins have been ingested to date, each generating one item, with no delivery errors or refusals. Bulletins arrive in full text form, averaging 1,890 characters (range 695–2,854). The collector maintains stable contact with the email system with no recorded errors. A four-bulletin sample over a single day is insufficient to characterize source coverage or completeness; the observed stream is the subscription's own editorial selection.

_Model-written assessment of our own ingestion, generated 2026-09-29 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

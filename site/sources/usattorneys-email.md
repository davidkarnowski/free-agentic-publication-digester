<!-- Markdown twin of https://fapd.info/sources/usattorneys-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/usattorneys-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: usattorneys-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# U.S. Attorneys News (email)

active · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Justice (Executive Office for U.S. Attorneys)

Official site: https://www.justice.gov/usao/pressreleases · All sources: [sources.md](../sources.md)

## What this source is

The 93 United States Attorneys prosecute federal criminal cases and represent the United States in civil litigation across every district. Their combined news bulletins carry district-level charging announcements, convictions, and sentencings. Volume is high relative to departmental releases; the content evaluation will measure it rather than estimate it. Bulletins are multi-item digests: one message carries many district releases.

**Model-written orientation**

The 93 U.S. Attorneys prosecute federal criminal cases and represent the federal government in civil litigation nationwide. Their subscription bulletins carry district-level announcements of charges filed, convictions, and sentencings.

The United States Attorneys are federal prosecutors stationed in 93 districts covering the entire country, one per district. Each U.S. Attorney reports to the Attorney General and prosecutes federal criminal cases in their jurisdiction, including offenses related to federal law: fraud, drug trafficking, terrorism, civil rights violations, and other federal crimes. The office also represents the United States in civil litigation in federal court.

The U.S. Attorneys collectively distribute a consolidated email bulletin to which this project subscribes. The bulletins report on prosecution activity across all 93 districts: charges filed against individuals and organizations, guilty pleas, jury verdicts, sentencings, and civil settlements. A single bulletin often contains announcements from multiple districts. Each item typically includes the name of the defendant or defendant organization, a description of the conduct alleged or proven, the applicable federal statute, the judicial proceeding (which court and which judge), and the sentence or settlement terms where applicable. The bulletin also includes the name and contact information for the prosecuting Assistant U.S. Attorney.

The Office of the Executive U.S. Attorneys coordinates the consolidated bulletin and is the source point for this subscription. While the same releases appear on the individual U.S. Attorneys' web newsrooms and on justice.gov/usao/pressreleases, those channels cannot currently be accessed by our client, making the bulletin the primary input channel for this content.

Readers will see announcements of federal prosecutions of all types, with geographic breadth: one bulletin may include a terrorism prosecution in one district, a drugs case in another, and a white-collar case in a third. The publication cadence and specificity are set by the rate of prosecutorial activity and the districts' own communications practices.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `usattorneys-email` |
| Agency / parent organization | Department of Justice (Executive Office for U.S. Attorneys) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 2 |
| URL (home) | https://www.justice.gov/usao/pressreleases |
| URL (signup) | https://public.govdelivery.com/accounts/USDOJUSAO/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]); a real news bulletin arrived the same day. Signup URL recovered from the bulletin List-Unsubscribe header and verified (account USDOJUSAO); an earlier address inferred from the sender had not resolved. [Note corrected 2026-07-30: this entry and ofr-email carried each other's signup-URL provenance sentences; see WORKLOG.] Gate-3 coverage evaluation (2026-07-30, from the 2026-07-29 bulletins): the subscription is EOUSA's consolidated all-districts distribution — 3 bulletins carried 25 district releases (20 with full text, 5 teaser-mode), DKIM-verified, one bulletin alone carrying sixteen. The open question is resolved: the digest lists district releases individually, as the adapter already parses them; per-district volume is whatever EOUSA distributes, and the coverage statement counts every item. Fraction of the visible newsroom stream: the same releases appear on justice.gov/usao/pressreleases, which sustained article fetching cannot use (recorded DOJ challenge behavior) — the bulletin channel is the fuller input, and under-coverage relative to it has not been observed in the window. |

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

**delivering** — 388 item(s) in the last 14 days; most recent 2026-09-14, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-15T03:50:21Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 56 item(s) ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 388 in 14 days (27.71 per day) · most recent 2026-09-14 |
| Content length | 342 characters average, 300 median (shortest 44, longest 1,128) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

388 item(s) in the last 14 days; most recent 2026-09-14, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-17 | 25 |
| 2026-08-18 | 40 |
| 2026-08-19 | 26 |
| 2026-08-20 | 59 |
| 2026-08-21 | 44 |
| 2026-08-22 | 1 |
| 2026-08-23 | 0 |
| 2026-08-24 | 46 |
| 2026-08-25 | 65 |
| 2026-08-26 | 16 |
| 2026-08-27 | 63 |
| 2026-08-28 | 32 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 44 |
| 2026-09-01 | 55 |
| 2026-09-02 | 59 |
| 2026-09-03 | 79 |
| 2026-09-04 | 24 |
| 2026-09-05 | 1 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 34 |
| 2026-09-09 | 45 |
| 2026-09-10 | 53 |
| 2026-09-11 | 36 |
| 2026-09-12 | 0 |
| 2026-09-13 | 1 |
| 2026-09-14 | 56 |
| 2026-09-15 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

U.S. Attorneys' news arrives via consolidated email from the Executive Office for U.S. Attorneys, delivering releases from all 93 districts with full text. The source provided 483 items over 14 days through 2026-09-04, averaging 34.5 per day—nearly double the 18.29 items per day observed through 2026-08-04. Individual bulletins carry multiple district releases in varying text completeness. The subscription represents EOUSA's all-districts distribution and provides fuller coverage than the web press page, which the system cannot retrieve through article fetching. Text averaged 307 characters with a median of 293. No consecutive delivery failures have occurred.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

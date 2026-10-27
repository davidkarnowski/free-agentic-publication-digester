<!-- Markdown twin of https://fapd.info/sources/atf-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/atf-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: atf-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# ATF News (email)

planned · ingestion health: delivering · Executive · Tier 2 · email bulletin · Department of Justice (ATF)

Official site: https://www.atf.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Bureau of Alcohol, Tobacco, Firearms and Explosives regulates the firearms and explosives industries and investigates related crime. Its bulletins carry enforcement announcements, industry rulings and open letters to licensees, and regulatory guidance.

**Model-written orientation**

The Bureau of Alcohol, Tobacco, Firearms and Explosives regulates firearms and explosives and investigates related federal crimes. Its subscription bulletins carry enforcement announcements, industry rulings, and regulatory guidance.

The Bureau of Alcohol, Tobacco, Firearms and Explosives (ATF) is a federal law-enforcement agency within the Department of Justice. The ATF has two main functions: regulating the firearms and explosives industries, and investigating federal crimes involving firearms, explosives, arson, and alcohol-tax violations.

In its regulatory capacity, the ATF issues licenses to firearms dealers, manufacturers, importers, and explosive handlers. It sets standards for the manufacture, sale, and possession of firearms and explosives and enforces those standards through inspections and enforcement actions. The agency maintains a tracing system for firearms recovered in crimes, which provides data on trafficking patterns and source channels. The agency also issues guidance to licensees through open letters, rulings on specific factual scenarios, and formal regulatory notices addressing compliance questions.

In its law-enforcement capacity, the ATF investigates crimes such as firearms trafficking, illegal weapons manufacture, explosives offenses, and arson. The agency also participates in joint task forces with state and local law enforcement and provides technical investigative assistance, forensic support, and explosives expertise.

The ATF distributes a subscription bulletin service to which this project subscribes. The bulletins report on enforcement operations (arrests, prosecutions, significant seizures and forfeitures), industry rulings and guidance documents, and regulatory actions affecting licensees. A bulletin may include an open letter to all firearms dealers on a compliance matter, an announcement of a major investigation, or a notice of a change in regulatory requirements.

Readers will see a mix of guidance documents and enforcement announcements, reflecting the ATF's dual role as regulator and law-enforcement agency.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `atf-email` |
| Agency / parent organization | Department of Justice (ATF) |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 2 |
| URL (home) | https://www.atf.gov/news |
| URL (signup) | https://public.govdelivery.com/accounts/USATF/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of atf-news, which returns HTTP 403 to our identified client — the first working input for this agency. Corrects the 2026-07-29 access research, which concluded no ATF-specific bulletin account existed; the account exists under a different code than the one guessed. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-22, delivered by email.

This label has held since 2026-10-22T17:54:48Z (UTC) and was last re-checked 2026-10-27T03:54:11Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-22 |
| Content length | 1,113 characters average, 1,113 median (shortest 1,113, longest 1,113) |
| Delivery mode | email-full — the bulletin carried the full item text |
| Mailbox | 1 bulletin(s), 0 subscription notice(s) in the last 14 days; most recent message 2026-10-22 |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

1 item(s) in the last 14 days; most recent 2026-10-22, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-09-28 | 0 |
| 2026-09-29 | 0 |
| 2026-09-30 | 0 |
| 2026-10-01 | 0 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |
| 2026-10-04 | 0 |
| 2026-10-05 | 0 |
| 2026-10-06 | 0 |
| 2026-10-07 | 0 |
| 2026-10-08 | 0 |
| 2026-10-09 | 0 |
| 2026-10-10 | 0 |
| 2026-10-11 | 0 |
| 2026-10-12 | 0 |
| 2026-10-13 | 0 |
| 2026-10-14 | 0 |
| 2026-10-15 | 0 |
| 2026-10-16 | 0 |
| 2026-10-17 | 0 |
| 2026-10-18 | 0 |
| 2026-10-19 | 0 |
| 2026-10-20 | 0 |
| 2026-10-21 | 0 |
| 2026-10-22 | 1 |
| 2026-10-23 | 0 |
| 2026-10-24 | 0 |
| 2026-10-25 | 0 |
| 2026-10-26 | 0 |
| 2026-10-27 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

The ATF News source delivers bulletins via email subscription (atf@service.govdelivery.com) to the project mailbox, ingested through DKIM verification and RFC-5322 archiving. Over 14 days, one bulletin arrived dated 2026-10-22, measuring 1,113 characters in full-text delivery mode. The mailbox collector recorded zero consecutive errors and zero refused messages. The source has demonstrated sporadic delivery: the prior assessment (2026-09-27) reported a single bulletin from August 14, after which no further deliveries occurred for over two months. The recent bulletin on 2026-10-22 represents resumed delivery. Email sources generate no polling requests; health is assessed from mailbox activity alone.

_Model-written assessment of our own ingestion, generated 2026-10-23 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/atf-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/atf-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: atf-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# ATF News (email)

planned · Executive · Tier 2 · email bulletin · Department of Justice (ATF)

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
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; a failing signature is labeled, never silently dropped |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

Not ingested: the registry status of this source is planned.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

Not ingested: the registry status of this source is planned. Ingestion statistics are measured for active sources only.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

No requests and no items were recorded in the last 30 days, so there is nothing to chart.

<!-- Markdown twin of https://fapd.info/sources/otip-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/otip-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: otip-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Office on Trafficking in Persons (email)

active · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Health and Human Services (ACF / OTIP)

Official site: https://www.acf.hhs.gov/otip · All sources: [sources.md](../sources.md)

## What this source is

The Office on Trafficking in Persons, within the Administration for Children and Families, leads federal anti-human-trafficking policy and victim-assistance programs. Its bulletins carry public announcements, grant and program news, reports, and prevention-awareness communications.

**Model-written orientation**

The Office on Trafficking in Persons leads federal anti-human-trafficking policy and victim-assistance programs. Its email bulletins share grant announcements, program news, policy reports, and awareness information.

The Office on Trafficking in Persons (OTIP) operates within the Administration for Children and Families (ACF), a division of the Department of Health and Human Services. OTIP leads the federal government's policy response to human trafficking and oversees programs that support trafficking survivors.

Human trafficking—the exploitation of people through force, fraud, or coercion for labor or commercial sex—is both a federal law-enforcement priority and a public health and social-services challenge. The federal response spans multiple agencies, but OTIP serves as the lead for policy coordination and victim services. OTIP administers federal grant programs that support organizations providing services to trafficking survivors and coordinates federal policy on anti-trafficking efforts.

OTIP's email bulletins communicate with a broad audience: nonprofit organizations that provide services to trafficking survivors, law enforcement agencies, policymakers, public health officials, victim advocates, and the general public interested in anti-trafficking efforts. These bulletins carry announcements of grant opportunities for organizations providing victim services, news on programs and policy initiatives in anti-trafficking work, reports and findings from federal anti-trafficking efforts, and public awareness information about trafficking.

The content reflects OTIP's work across both victim services and public awareness. Alongside grant announcements and program news that inform service providers and agencies, readers will see public awareness communications that OTIP develops and distributes to the public.

OTIP's public communications reach service providers, government agencies, advocacy organizations, researchers, and the general public with information about federal anti-trafficking programs, victim services, and prevention awareness.

In this digest, readers will encounter OTIP's official communications drawn from its email bulletins—including grant announcements, program updates, policy reports, and public information that OTIP distributes to keep stakeholders and the public informed about federal anti-trafficking policy and victim assistance resources.

_Model-written orientation, generated 2026-10-02 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `otip-email` |
| Agency / parent organization | Department of Health and Human Services (ACF / OTIP) |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 3 |
| URL (home) | https://www.acf.hhs.gov/otip |
| Registered | 2026-10-01 |
| Registry notes | Activated 2026-10-01 (operator approval) on observed delivery over the late-September changeover. Coverage caveat: OTIP bulletins mix public news (grants, reports, policy) with prevention-awareness campaigns — the observed message was a NOPE awareness bulletin — so content is public-facing but not purely press-release, tier 3. Subscribed through the publisher's own GovDelivery flow (sender [address withheld]); DKIM recorded per message at ingest. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
| Adapter | govdelivery |
| Poll cadence | the project mailbox is read about every 15 minutes |
| Requests | none — bulletins are delivered to the project mailbox by the agency's own subscription service |
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-10-01T22:11:29Z (UTC) and was last re-checked 2026-10-04T03:57:33Z (UTC).

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

The Office on Trafficking in Persons was activated on 2026-10-01 based on observed delivery during the late-September changeover. Messages carry public announcements and grant news mixed with prevention-awareness campaigns (tier 3). No messages have been recorded in the mailbox since activation. Messages are ingested through the email adapter via DKIM verification.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/fns-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fns-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fns-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Food and Nutrition Service (email)

planned · ingestion health: delivering · Executive · Tier 3 · email bulletin · Department of Agriculture, Food and Nutrition Service

Official site: https://www.fns.usda.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Food and Nutrition Service administers SNAP, school meals, and WIC. Its bulletins carry program announcements and initiatives.

**Model-written orientation**

The Food and Nutrition Service administers federal nutrition assistance programs including SNAP, school meals, and WIC. Its emails carry program announcements and initiatives.

The Food and Nutrition Service (FNS) is a bureau within the Department of Agriculture responsible for administering federal nutrition assistance programs that serve millions of Americans. FNS manages the Supplemental Nutrition Assistance Program (SNAP, formerly food stamps), the National School Lunch Program and School Breakfast Program, the Women, Infants, and Children (WIC) program, the Child and Adult Care Food Program, and the Summer Food Service Program, among others. These programs work together to provide nutrition assistance across the lifespan, from infancy through adulthood.

Each FNS program has distinct eligibility requirements and serves different populations. SNAP provides monthly benefits to low-income households to purchase food; school meal programs ensure that schoolchildren have access to nutritious meals during the school day; WIC serves pregnant women, new mothers, and young children with tailored nutrition assistance and nutrition education; and other programs serve specific settings like child care facilities and senior centers. FNS also administers nutrition education initiatives and supports efforts to connect benefits recipients with local food sources.

As the administrator of these programs, FNS issues regulations and guidance to states and localities implementing the programs, manages federal funding, collects data on program participation and outcomes, and works on policy initiatives to improve program effectiveness and efficiency. The agency coordinates with other federal agencies, state health departments, and community organizations on nutrition-related work.

When FNS appears in the digest, you will see program policy updates, guidance to states on program implementation, announcements of nutrition education initiatives, updates on benefit amounts or eligibility, special program opportunities, research findings on nutrition and food security, and administrative notices affecting program operations. Documents may also include updates on FNS efforts to address food security, childhood nutrition, and health equity.

FNS announcements are relevant to state and local nutrition program administrators, school districts, child care providers, WIC clinics, nonprofits serving low-income populations, public health agencies, and advocates for food security and nutrition.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `fns-email` |
| Agency / parent organization | Department of Agriculture, Food and Nutrition Service |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.fns.usda.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USFNS/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: agriculture-email. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

**delivering** — 1 item(s) in the last 14 days; most recent 2026-10-01, delivered by email.

This label has held since 2026-10-01T14:38:17Z (UTC) and was last re-checked 2026-10-03T03:48:44Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 1 in 14 days (0.07 per day) · most recent 2026-10-01 |
| Content length | 1,240 characters average, 1,240 median (shortest 1,240, longest 1,240) |
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
| 2026-09-28 | 0 |
| 2026-09-29 | 0 |
| 2026-09-30 | 0 |
| 2026-10-01 | 1 |
| 2026-10-02 | 0 |
| 2026-10-03 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

Subscription bulletins to the project mailbox, ingested by the email adapter with DKIM verification. Registered 2026-09-26; the previous assessment noted no bulletins had been parsed. As of 2026-10-02, one bulletin has been delivered and recorded, arriving 2026-10-01 at 14:22 UTC via GovDelivery (sender usda.fna@service.govdelivery.com), approximately 1,240 characters. The collector shows healthy cycling with no consecutive errors. This single data point marks a transition from the planned state to active delivery; observations remain limited pending further bulletins to establish cadence and volume patterns. Gate-3 coverage evaluation can now proceed with the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-10-02 by haiku, prompt version 1, trigger: health-change. It restates our measured figures and is not official-record content._

<!-- Markdown twin of https://fapd.info/sources/fns-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/fns-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: fns-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Food and Nutrition Service (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Agriculture, Food and Nutrition Service

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

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-09-29T04:08:42Z (UTC).

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

Subscription bulletins to the project mailbox, ingested by the email adapter. Registered 2026-09-26 with sender usda.fna@service.govdelivery.com. The registry notes mail was observed in the project mailbox prior to registration but earlier bulletins are not backfilled. As of 2026-09-27, no bulletins from this source have been parsed and stored; the collector shows zero items. Status is planned, with gate-3 coverage evaluation pending the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

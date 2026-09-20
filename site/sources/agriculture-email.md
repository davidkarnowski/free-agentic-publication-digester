<!-- Markdown twin of https://fapd.info/sources/agriculture-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/agriculture-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: agriculture-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# USDA News (email)

active · ingestion health: delivering · Executive · Tier 1 · email bulletin · Department of Agriculture

Official site: https://www.usda.gov/about-usda/news/press-releases · All sources: [sources.md](../sources.md)

## What this source is

The Department of Agriculture administers farm programs, food-safety inspection, nutrition assistance, and rural development. Its departmental bulletins carry press releases on program funding, disaster designations, trade actions, and regulatory decisions.

**Model-written orientation**

The Department of Agriculture administers federal farm support, food-safety inspection, nutrition assistance, and rural development. Its subscription bulletins carry press releases on program funding, disaster relief, trade actions, and regulatory decisions.

The Department of Agriculture (USDA) is a cabinet-level agency with responsibility for a broad range of domestic and international agricultural and food-related matters. The USDA administers farm-commodity support programs, regulates food safety through inspection, runs the nutrition-assistance programs (including SNAP, formerly food stamps), oversees rural development and lending, and represents U.S. agricultural interests in international trade.

The USDA is organized into multiple agencies and offices, each managing a specific function or commodity: the Food and Nutrition Service administers benefit programs; the Food Safety and Inspection Service conducts meat and poultry inspections; the Foreign Agricultural Service handles agricultural trade and exports; the Natural Resources Conservation Service manages conservation programs; the Farm Service Agency administers commodity programs and disaster assistance; and the Rural Development agency provides loans and grants for rural infrastructure and businesses. The Secretary of Agriculture chairs the department and has authority over agricultural policy, trade negotiations, and resource allocation.

The USDA departmental office distributes a subscription bulletin service to which this project subscribes. The bulletins report on departmental announcements, including press releases on farm-program funding, disaster designations and relief, agricultural trade actions and agreements, rule changes, grant awards, and policy initiatives. The content reflects the department's responsibility for agricultural production, food safety, food assistance, rural economic development, and natural-resource conservation.

Additionally, component agencies may operate their own bulletin services. This project may subscribe to those separately if content evaluation indicates distinct action streams warranting separate coverage.

Readers will see announcements spanning multiple agricultural sectors and programs—commodity-program payments, food-safety recalls or regulatory changes, disaster relief, rural-development funding, and trade actions—reflecting the department's broad jurisdiction over food, agriculture, and rural America.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `agriculture-email` |
| Agency / parent organization | Department of Agriculture |
| Branch | executive |
| Type | email bulletin |
| Status | active |
| Tier | 1 |
| URL (home) | https://www.usda.gov/about-usda/news/press-releases |
| URL (signup) | https://public.govdelivery.com/accounts/USDAOC/subscriber/new |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Sibling of agriculture-newsroom, whose web path robots.txt disallows — the first working input for this department. Component lists also subscribed and confirmed, to be split into their own entries if content evaluation shows distinct action streams: Foreign Agricultural Service, Food and Nutrition Service, Agricultural Marketing Service, APHIS, NIFA, Agricultural Research Service, Rural Development, and Farmers.gov. Gate-3 coverage evaluation (2026-07-30, from the 2026-07-29 bulletins): 2 bulletins carried 2 departmental releases, full text, DKIM-verified, with canonical usda.gov URLs. The subscription is the departmental press list; with the web channel refusing our client it is this department's only input, so the bulletin stream is the measure of its own coverage; component-list volume is observed under this entry until the split decision. |

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

**delivering** — 20 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.

This label has held since 2026-08-03T18:46:01Z (UTC) and was last re-checked 2026-09-20T03:51:20Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 20 in 14 days (1.43 per day) · most recent 2026-09-18 |
| Content length | 527 characters average, 556 median (shortest 124, longest 1,179) |
| Delivery mode | email-full — the bulletin carried the full item text |

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

20 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.

### All time

Bulletins from this source are delivered to the project mailbox, so there are no requests to report. Its health is read from delivery recency alone.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-22 | 0 |
| 2026-08-23 | 0 |
| 2026-08-24 | 2 |
| 2026-08-25 | 2 |
| 2026-08-26 | 1 |
| 2026-08-27 | 1 |
| 2026-08-28 | 1 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 2 |
| 2026-09-01 | 3 |
| 2026-09-02 | 1 |
| 2026-09-03 | 1 |
| 2026-09-04 | 2 |
| 2026-09-05 | 0 |
| 2026-09-06 | 0 |
| 2026-09-07 | 0 |
| 2026-09-08 | 2 |
| 2026-09-09 | 0 |
| 2026-09-10 | 2 |
| 2026-09-11 | 2 |
| 2026-09-12 | 0 |
| 2026-09-13 | 0 |
| 2026-09-14 | 1 |
| 2026-09-15 | 3 |
| 2026-09-16 | 3 |
| 2026-09-17 | 2 |
| 2026-09-18 | 5 |
| 2026-09-19 | 0 |
| 2026-09-20 | 0 |

## Our ingestion assessment

**Model-written ingestion assessment**

USDA press releases arrive via email subscription with full text, DKIM-verified. The source delivered 16 items over 14 days through 2026-09-04, averaging 1.14 per day, a modest increase from the 0.71 items per day observed in the initial seven days. The departmental web channel returns access refusals via robots.txt, making this email subscription the sole working input for departmental press material. Additional component-list subscriptions (Foreign Agricultural Service, Food and Nutrition Service, Agricultural Marketing Service, APHIS, NIFA, Agricultural Research Service, Rural Development, and Farmers.gov) are confirmed and measured under this entry pending a future separation decision. Text ranged from 123 to 7,830 characters with a median of 676.

_Model-written assessment of our own ingestion, generated 2026-09-05 by haiku, prompt version 1, trigger: age-30d. It restates our measured figures and is not official-record content._

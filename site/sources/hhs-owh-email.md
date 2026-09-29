<!-- Markdown twin of https://fapd.info/sources/hhs-owh-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/hhs-owh-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: hhs-owh-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# HHS Office on Women's Health (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Health and Human Services, Office on Women's Health

Official site: https://womenshealth.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Office on Women's Health coordinates women's health policy within the Department of Health and Human Services. Its bulletins carry press releases and program announcements.

**Model-written orientation**

The HHS Office on Women's Health coordinates women's health policy and research across the Department of Health and Human Services. Its emails carry press releases and program announcements.

The Office on Women's Health (OWH) is a sub-agency within the Office of the Secretary of the Department of Health and Human Services. It coordinates federal efforts on women's health and reproductive health policy across the department and its agencies, bringing together research, program development, and public health initiatives. The office's work spans the full range of women's health topics, from maternal and infant health through menopause and aging, including reproductive health, chronic disease prevention, mental health, and health equity.

As a policy coordination office rather than a grant-making or regulatory agency, OWH functions as a central point for women's health issues within HHS. It convenes working groups across HHS agencies, supports research initiatives, develops evidence-based resources and toolkits for health professionals and the public, and tracks national health trends affecting women. The office also works to ensure that federal health programs and policies address women's health needs.

When OWH appears in the digest, you will see press releases announcing new research findings, program launches, resource releases, and federal health initiatives related to women's health. Documents may also include announcements of working group findings, federal policy positions on health topics, or the release of educational materials for clinicians and patients.

Because OWH operates as a coordinating office, its publications typically reflect policy developments, evidence syntheses, or program announcements from across HHS rather than new data collection or direct service provision. Readers seeking detailed scientific research on women's health may also find relevant material from the National Institutes of Health and the Centers for Disease Control and Prevention, which are separate agencies within HHS.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `hhs-owh-email` |
| Agency / parent organization | Department of Health and Human Services, Office on Women's Health |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://womenshealth.gov/ |
| URL (signup) | https://public.govdelivery.com/accounts/USOPHSOWH/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. |

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

This source delivers bulletins through the project mailbox using the GovDelivery platform. Subscription was confirmed through the publisher's signup flow in September 2026, and the source was registered for automated ingestion on 2026-09-26. Bulletins matching this sender were already present in the mailbox before registration; ingestion begins with the first poll following deployment. No bulletins have been recorded from this source since registration. The collector has accessed the mailbox without errors, observing zero messages associated with this source across the past week. No delivery pattern, cadence, or format characteristics are yet observable. Gate-3 coverage evaluation awaits the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

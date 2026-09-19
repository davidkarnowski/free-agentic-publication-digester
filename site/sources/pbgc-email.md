<!-- Markdown twin of https://fapd.info/sources/pbgc-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/pbgc-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: pbgc-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# PBGC Updates (email)

planned · Executive · Tier 3 · email bulletin · Pension Benefit Guaranty Corporation

Official site: https://www.pbgc.gov/news · All sources: [sources.md](../sources.md)

## What this source is

The Pension Benefit Guaranty Corporation insures private-sector defined-benefit pension plans and takes over failed plans. Its bulletins carry trusteeship announcements, premium and interest-rate notices, and policy guidance affecting plan sponsors and retirees.

**Model-written orientation**

The Pension Benefit Guaranty Corporation sends email updates on pension plan trusteeship, premium rates, and guidance for plan sponsors and retirees.

The Pension Benefit Guaranty Corporation is a self-financing federal agency that protects the retirement income of American workers covered by private-sector defined-benefit pension plans. When a pension plan has insufficient assets to pay promised benefits and the plan sponsor cannot meet its obligations, the PBGC steps in as trustee, assumes the plan's assets and liabilities, and pays benefits to participants and retirees up to federally insured limits. The PBGC also collects insurance premiums from plan sponsors to fund this guarantee.

The PBGC email subscription delivers official announcements to plan sponsors—employers and unions that sponsor pension plans—and the professional advisors who serve them. Subscribers receive notices when the PBGC takes trusteeship of a failed plan, specifying the plan name, the plan sponsor, and the effective date of the PBGC's assumption. Announcements cover premium-rate adjustments for the coming year (the insurance premiums employers must pay per participant), interest-rate announcements used in calculating pension liabilities and funding requirements, policy guidance on plan administration and compliance with federal law, and notices of changes to benefit-guarantee levels (the maximum benefit the PBGC will pay if a plan fails). Readers also receive statistical releases about the pension insurance program—the number of plans, participants covered, and funding levels—and notices of significant regulatory or legislative changes affecting pension obligations. The feed targets plan sponsors, pension administrators, actuaries, attorneys, and financial advisors managing or advising on defined-benefit plans. Announcements of new trusteeship actions carry operational details for affected plan participants and beneficiaries. Premium-rate notices and funding guidance are essential to plan sponsors' financial planning and compliance obligations. The stream reflects the PBGC's dual role: guaranteeing retirement income for workers and collecting data and premiums to sustain the insurance program.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `pbgc-email` |
| Agency / parent organization | Pension Benefit Guaranty Corporation |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.pbgc.gov/news |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). New coverage: no registered source before this subscription. Signup URL not recorded: the address inferred from the sender was checked and did not resolve, so only the confirmed sender is asserted here. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

## How we ingest it

| Term | Description |
|---|---|
| Channel | email bulletin |
| Method | Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive). |
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

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested |
|---|---|
| 2026-08-21 | 0 |
| 2026-08-22 | 0 |
| 2026-08-23 | 0 |
| 2026-08-24 | 1 |
| 2026-08-25 | 0 |
| 2026-08-26 | 0 |
| 2026-08-27 | 0 |
| 2026-08-28 | 0 |
| 2026-08-29 | 0 |
| 2026-08-30 | 0 |
| 2026-08-31 | 0 |
| 2026-09-01 | 0 |
| 2026-09-02 | 0 |
| 2026-09-03 | 0 |
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

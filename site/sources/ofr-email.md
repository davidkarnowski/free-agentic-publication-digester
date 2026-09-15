<!-- Markdown twin of https://fapd.info/sources/ofr-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/ofr-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: ofr-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Office of Financial Research (email)

planned · Executive · Tier 3 · email bulletin · Department of the Treasury (OFR)

Official site: https://www.financialresearch.gov/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of Financial Research supports the Financial Stability Oversight Council with data and analysis on risks to the financial system. Its bulletins carry working papers, financial-stability monitors, and data releases.

**Model-written orientation**

The Office of Financial Research distributes working papers, financial-stability monitors, and data releases via email bulletins to track emerging risks to the nation's financial system.

The Office of Financial Research (OFR) is an agency within the Department of the Treasury established to support the Financial Stability Oversight Council. The Council coordinates across federal banking regulators, the Securities and Exchange Commission, the Commodity Futures Trading Commission, and other financial agencies to monitor risks to the stability of the U.S. financial system and recommend policy responses. The OFR provides the analytical and data foundation for this monitoring work.

The Office publishes research on financial risks and market dynamics written for regulators, policymakers, financial institutions, and researchers working to understand systemic financial vulnerabilities. Publications include working papers that analyze specific threats to financial stability—such as risks in asset management, derivatives markets, or emerging market exposures—quarterly financial-stability monitors that track key indicators and emerging vulnerabilities, and data releases on topics ranging from asset management to corporate debt to financial interconnections. The OFR's research and data inform policy decisions at the federal level and contribute to the international financial regulatory community's understanding of financial-system risks.

The OFR distributes announcements of new publications and data releases through email subscription bulletins, providing subscribers with timely notification when new research and data products become available. This channel supports those who follow the Office's work and the broader financial-stability monitoring community in staying informed of the latest analysis and data on systemic risks.

The subscription was confirmed in 2026 and is currently monitoring for the first published bulletins. Once bulletins begin arriving, they will be processed and verified using standard email protocols with sender authentication.

_Model-written orientation, generated 2026-08-05 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `ofr-email` |
| Agency / parent organization | Department of the Treasury (OFR) |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.financialresearch.gov/ |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Signup URL not recorded: the address inferred from the sender was checked and did not resolve, so only the confirmed sender is asserted here. [Note corrected 2026-07-30: this entry and usattorneys-email carried each other's signup-URL provenance sentences; see WORKLOG.] No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

<!-- Markdown twin of https://fapd.info/sources/commercial-service-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/commercial-service-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: commercial-service-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# U.S. Commercial Service (email)

planned · Executive · Tier 3 · email bulletin · Department of Commerce (International Trade Administration)

Official site: https://www.trade.gov/commercial-service · All sources: [sources.md](../sources.md)

## What this source is

The U.S. Commercial Service is the trade-promotion arm of the International Trade Administration. Its bulletins carry export-assistance announcements, trade-mission notices, and market guidance for U.S. exporters.

**Model-written orientation**

The U.S. Commercial Service provides email notifications on export-assistance programs, trade missions, and market guidance for American exporters and businesses.

The U.S. Commercial Service is the trade-promotion arm of the International Trade Administration, a bureau within the Department of Commerce. The Commerce Department develops and implements U.S. trade policy and promotes American economic interests globally. The Commercial Service specifically focuses on helping U.S. businesses export their products and services—particularly small and medium-sized enterprises—by providing market research, introductions to foreign buyers, and guidance on export regulations.

The Commercial Service maintains a worldwide network of trade specialists in U.S. embassies and consulates, as well as domestic export assistance centers. The email subscription notifies recipients of specific, actionable opportunities: scheduled trade missions to targeted countries or industries, trade shows and international business conferences, market-entry guidance for particular sectors or regions, and changes to export regulations and tariffs affecting specific goods. Readers receive advance notice of export financing programs, trade agreement details that open new markets, and sector-specific market reports. Unlike the Commerce Department's broader press office, this channel targets the business community directly, delivering information about programs, opportunities, and regulatory changes that affect export decisions. A bulletin typically carries details of upcoming trade promotion events, updates to country-specific business practices or import requirements, industry assessments, or announcements of new export-financing mechanisms. The stream reflects the Commercial Service's core mission: helping American exporters navigate foreign markets and connect with international buyers.

_Model-written orientation, generated 2026-08-06 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `commercial-service-email` |
| Agency / parent organization | Department of Commerce (International Trade Administration) |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.trade.gov/commercial-service |
| Registered | 2026-07-29 |
| Registry notes | Subscribed and confirmed 2026-07-29 (sender [address withheld]). Partial coverage only for commerce-newsroom, which returns HTTP 403 to our identified client: this is a trade-promotion channel, not the department's press office. A departmental Commerce subscription remains to be found. Signup URL not recorded: the address inferred from the sender was checked and did not resolve, so only the confirmed sender is asserted here. No bulletin observed as of the 2026-07-29 evening poll (~45-minute window); subscription confirmed, window open — activate on first parsed bulletin. |

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

<!-- Markdown twin of https://fapd.info/sources/commercial-service-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/commercial-service-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: commercial-service-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# U.S. Commercial Service (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Commerce (International Trade Administration)

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
| Authenticity | every message's DKIM signature is checked on arrival and the result is disclosed on each item; in the inbox a failing signature is labeled, never silently dropped; in the junk folder, which is read too, only a message whose signature verifies and matches the sender's domain is accepted, and the rest are refused and counted |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**no data** — No bulletin recorded from this source in the last 180 days.

This label has held since 2026-09-27T00:51:29Z (UTC) and was last re-checked 2026-10-02T03:48:29Z (UTC).

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

This source delivers export-assistance announcements from the U.S. Commercial Service via email subscription confirmed 2026-07-29. No bulletins have been recorded in our ingestion logs; the subscription remains in planned status with no items or delivery attempts measured across the observation period.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

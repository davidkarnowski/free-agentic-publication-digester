<!-- Markdown twin of https://fapd.info/sources/doe-indian-energy-email.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/doe-indian-energy-email.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: doe-indian-energy-email)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# DOE Office of Indian Energy (email)

planned · ingestion health: no data · Executive · Tier 3 · email bulletin · Department of Energy, Office of Indian Energy Policy and Programs

Official site: https://www.energy.gov/indianenergy · All sources: [sources.md](../sources.md)

## What this source is

The Department of Energy's Office of Indian Energy funds and supports tribal energy development. Its bulletins carry funding opportunities, grant results, and program updates.

**Model-written orientation**

The DOE Office of Indian Energy funds and supports tribal energy development and sovereignty initiatives. Its emails carry funding announcements, grant results, and program updates.

The Office of Indian Energy Policy and Programs (IEPP) is part of the Department of Energy and works specifically with Native American tribes and Alaska Native villages to advance energy development aligned with tribal priorities and sovereignty. The office recognizes tribal nations as governments and partners with them on energy policy, project development, financing, and capacity building. Its mission centers on supporting tribes in achieving energy independence, building local economic opportunity, and managing energy resources according to tribal values and needs.

The office administers grant programs, technical assistance initiatives, and financing programs that support tribal energy projects. Funded activities include renewable energy development (solar, wind, geothermal), energy efficiency in tribal facilities and homes, grid modernization and resilience projects, feasibility studies and planning, workforce development and training, and institutional capacity building within tribal governments and entities. IEPP also works on broadband deployment in Indian Country, recognizing the connection between energy and digital infrastructure.

Beyond grants, the office provides technical assistance, workforce development resources, and connections to financing mechanisms including loan guarantees and private capital sources. It maintains a knowledge center with resources on renewable energy, energy efficiency, project development, and financing for tribal communities. The office coordinates with other federal agencies and private sector partners to increase support for tribal energy initiatives.

When IEPP appears in the digest, you will see grant solicitations with application deadlines, grant awards and project selections, technical assistance announcements, workforce training opportunity notices, research findings on tribal energy topics, and updates on IEPP initiatives. Documents may also include announcements of partnerships, financing opportunities, or policy developments affecting tribal energy work.

The office's announcements are relevant to tribal governments and their energy entities, tribal nonprofits and enterprises, and organizations supporting tribal energy development.

_Model-written orientation, generated 2026-09-27 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `doe-indian-energy-email` |
| Agency / parent organization | Department of Energy, Office of Indian Energy Policy and Programs |
| Branch | executive |
| Type | email bulletin |
| Status | planned |
| Tier | 3 |
| URL (home) | https://www.energy.gov/indianenergy |
| URL (signup) | https://public.govdelivery.com/accounts/USDOEIE/subscriber/new |
| Registered | 2026-09-26 |
| Registry notes | Subscription confirmed through the publisher's own signup flow (sender [address withheld]). Bulletins were observed in the project mailbox before registration; registered 2026-09-26 and ingested from the first poll after deploy — earlier bulletins are not backfilled. Gate-3 coverage evaluation pending first ingested bulletins. Related entries that can publish the same news: energy-newsroom. A copy at the same URL merges as corroboration (GUIDE §3); the same event published at a different URL is listed separately, by rule. |

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

Subscription bulletins to the project mailbox, ingested by the email adapter. Registered 2026-09-26 with sender indianenergy@public.govdelivery.com. The registry notes mail was observed in the project mailbox prior to registration but earlier bulletins are not backfilled. As of 2026-09-27, no bulletins from this source have been parsed and stored; the collector shows zero items. Status is planned, with gate-3 coverage evaluation pending the first ingested bulletin.

_Model-written assessment of our own ingestion, generated 2026-09-27 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

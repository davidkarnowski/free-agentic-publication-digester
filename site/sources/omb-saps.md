<!-- Markdown twin of https://fapd.info/sources/omb-saps.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources/omb-saps.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml (id: omb-saps)` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# OMB Statements of Administration Policy

active · ingestion health: delivering · Executive · Tier 1 · HTML index · Executive Office of the President

Official site: https://www.whitehouse.gov/omb/statements-of-administration-policy/ · All sources: [sources.md](../sources.md)

## What this source is

The Office of Management and Budget issues a Statement of Administration Policy before the House or Senate takes up a bill on the floor: the Administration's formal written position on that measure, often including whether the President's advisers would recommend a veto. Volume follows the floor schedule, from none to a few on a session day.

**Model-written orientation**

The White House Office of Management and Budget issues Statements of Administration Policy (SAPs) to communicate the Administration's formal position on bills before the House or Senate takes floor action.

The Office of Management and Budget (OMB) is part of the Executive Office of the President and serves as the President's principal budget and management agency. Among its functions is issuing Statements of Administration Policy—formal written positions on pending legislation.

A Statement of Administration Policy is released shortly before the House or Senate considers a bill on the floor. It communicates the Administration's official stance on that measure, including whether the President's advisers would recommend approval or veto. SAPs serve as the executive branch's primary mechanism for signaling its position to Congress during the legislative process, distinct from other forms of executive communication like press statements or messaging.

Because SAPs address measures under active floor consideration, their volume directly follows the congressional schedule. On days when neither chamber has floor action scheduled, no SAPs are issued; on days with floor action, a few may appear, depending on the number and significance of measures under consideration.

Each SAP you will see in this digest carries its official title as published, the date of issuance, and a link to the PDF on the OMB website where the full statement can be read. The digest does not extract or summarize SAP content—each statement's actual position lives solely in its PDF, and reading it is a matter for readers themselves. The digest's role is to notify you that a position has been issued and to point you to the official text.

SAPs are not reprinted in the Federal Register or included in the White House's main news feed; they appear only in this dedicated OMB listing, which is why they are collected from that source alone. They are filed in this digest as agency releases and attributed to the Office of Management and Budget. When a SAP is withdrawn by the Administration after having been published, the digest retains the record of its original issuance, as it does for all captured documents.

_Model-written orientation, generated 2026-10-07 by haiku, prompt version 1. It may draw on general knowledge of public institutions and is not official-record content._

## Identity and registry record

| Field | Value |
|---|---|
| Registry id | `omb-saps` |
| Agency / parent organization | Executive Office of the President |
| Branch | executive |
| Type | HTML index |
| Status | active |
| Tier | 1 |
| URL (index) | https://www.whitehouse.gov/omb/statements-of-administration-policy/ |
| Registered | 2026-10-06 |
| Registry notes | Registered 2026-10-06 from the 2026-10-04 source research. Operator ruling 2026-10-06: SAPs are attributed official statements under GUIDE §2, filed as agency releases (AGENCYPR) with document type SAP; titled verbatim and attributed, never characterized. No feed exists; the listing is a WordPress page linking each SAP's PDF under /wp-content/uploads/, which the index_item_path hint selects. Not carried elsewhere: SAPs are not printed in the Federal Register, and the White House news listing and presidential-action feeds do not list them. Probed 2026-10-04 through FAPD's identified probe client: HTTP 200, 3 entries dated inside the 7-day window. Re-verified 2026-10-05 from the operator machine as a brief test, outside the server's budget: 3 of 3 entries dated (2026-09-29, 09-29, 09-30), no Retry-After, no crawl-delay. The position a SAP states lives only in its PDF; reading it is a later, separate decision. A SAP withdrawn after FAPD stored it stays stored, as every capture does. Gate 2 through the new adapter, 2026-10-06 (operator machine, brief test, one request): feed-ok, 3 of 3 window entries dated, each naming its measure (H.R. 9340, S.Res. 852, S.J.Res. 197, the spaced forms included); the listing holds 194 SAP links back to the start of the Administration, bounded to the 7-day window. Coverage (gate 3): every SAP the listing dates inside the window; title, date and PDF link only. The three in the window when activated are a week old and file as backfill. ACTIVATED 2026-10-06 (operator). |

## How we ingest it

| Term | Description |
|---|---|
| Channel | HTML index |
| Method | Parses the dated SAP listing via AgencyClient (statements-of-administration-policy adapter, a listing subclass); stores each SAP's title, date and PDF link, and the bill numbers its title names, without fetching the PDF (mode feed-only). |
| Adapter | statements-of-administration-policy |
| Poll cadence | about every 60 minutes while the collector runs |
| Request budget | the agency class: at most 3,000 requests per day shared across every agency web source, counted from the fetch log (failed requests count too) |
| Politeness | robots.txt is honored as observed — including each host's crawl-delay, exactly — and every request identifies itself as fapd/0.1 (Free Agentic Publication Digester; +https://fapd.info/bot.html; contact: hustleyourcity@gmail.com); a refusal is recorded, never evaded |
| Capture and hash | captured raw content is hashed (SHA-256) into the day's committed provenance manifest, hash-chained day to day (PROVENANCE.md) |

## Ingestion health

**delivering** — 3 item(s) in the last 14 days; most recent 2026-10-06; 7 of 1028 request(s) to www.whitehouse.gov returned no content.

This label has held since 2026-10-06T12:25:01Z (UTC) and was last re-checked 2026-10-09T03:52:22Z (UTC).

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

## Ingestion statistics

These figures describe this project's ingestion of this source — items we recorded and requests we made — and nothing else. They are not a measurement of the publisher.

### Last 24 hours

Last 24 hours: 104 request(s) (104 answered, 0 returned no content) · no items ingested

### Last 14 days

| Measure | Value |
|---|---|
| Items ingested | 3 in 14 days (0.21 per day) · most recent 2026-10-06 |
| Content length | 176 characters average, 93 median (shortest 57, longest 378) |
| Delivery mode | feed-only — the feed's own summary — the source publishes no more than this through this channel |
| Our requests to www.whitehouse.gov | 1,028 request(s) · 1,021 answered · 7 declined (4xx) · 0 server declined (5xx) · 0 no response — 0.7% returned no content |

last answered request 2026-10-09T04:00:13.552+00:00 UTC; this host serves 4 registered sources, so these figures are host-wide.

3 item(s) in the last 14 days; most recent 2026-10-06; 7 of 1028 request(s) to www.whitehouse.gov returned no content.

### All time

- **Our requests to www.whitehouse.gov, all time (since 2026-08-06):** 3,794 request(s) · 3,780 answered · 14 returned no content

This host serves 4 registered sources, so these figures are host-wide.

Request counts begin 2026-07-30, the day this service went into production; earlier development-machine traffic is excluded. Counts before 2026-08-03 include unmarked source-probe traffic; probes are labeled and excluded thereafter. Robots.txt checks, about one a day per host, are left out of these figures and of every health label: they fetch no publication, so a source's health rests on the requests that fetch its publications. They are still logged and counted against our request budget.

### Last 30 days, day by day

Each day runs midnight to midnight on Eastern time (Washington, D.C.), the publication day the digests use; the stored request stamps remain UTC.

| Day | Items ingested | Requests to www.whitehouse.gov (host-wide) | Mean response time (ms) |
|---|---|---|---|
| 2026-09-10 | 0 | 50 | 76 |
| 2026-09-11 | 0 | 50 | 64 |
| 2026-09-12 | 0 | 54 | 62 |
| 2026-09-13 | 0 | 50 | 44 |
| 2026-09-14 | 0 | 57 | 142 |
| 2026-09-15 | 0 | 52 | 46 |
| 2026-09-16 | 0 | 55 | 49 |
| 2026-09-17 | 0 | 55 | 69 |
| 2026-09-18 | 0 | 53 | 81 |
| 2026-09-19 | 0 | 50 | 41 |
| 2026-09-20 | 0 | 52 | 39 |
| 2026-09-21 | 0 | 56 | 72 |
| 2026-09-22 | 0 | 48 | 59 |
| 2026-09-23 | 0 | 48 | 52 |
| 2026-09-24 | 0 | 50 | 54 |
| 2026-09-25 | 0 | 53 | 60 |
| 2026-09-26 | 0 | 52 | 85 |
| 2026-09-27 | 0 | 52 | 70 |
| 2026-09-28 | 0 | 66 | 69 |
| 2026-09-29 | 0 | 84 | 52 |
| 2026-09-30 | 0 | 75 | 41 |
| 2026-10-01 | 0 | 78 | 42 |
| 2026-10-02 | 0 | 79 | 65 |
| 2026-10-03 | 0 | 75 | 39 |
| 2026-10-04 | 0 | 75 | 40 |
| 2026-10-05 | 0 | 83 | 55 |
| 2026-10-06 | 3 | 95 | 77 |
| 2026-10-07 | 0 | 106 | 81 |
| 2026-10-08 | 0 | 104 | 69 |
| 2026-10-09 | 0 | 4 | 120 |

## Our ingestion assessment

**Model-written ingestion assessment**

This source was activated on 2026-10-06 with HTML index polling via the statements-of-administration-policy adapter in feed-only mode. Over six measurement days from October 1-7, three items were ingested, all dated before activation and filed as backfill; each entry lists its measure number and date on the index listing, with the adapter reading title, date, and PDF link without downloading PDF content. All 921 requests to www.whitehouse.gov completed with only 7 failures (0.8% error rate). Activity concentrated on the activation day when 95 requests returned the three items; content averaged 176 characters, ranging from 57 to 378. The index holds 194 SAP links spanning the administration, bounded by the adapter's 7-day lookback window during polling. No new items have arrived in the collection window since activation.

_Model-written assessment of our own ingestion, generated 2026-10-07 by haiku, prompt version 1, trigger: initial. It restates our measured figures and is not official-record content._

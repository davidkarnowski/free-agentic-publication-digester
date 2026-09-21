<!-- Markdown twin of https://fapd.info/sources.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/sources.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `sources/registry.yaml` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Sources

> These figures describe this project's ingestion of each source, and nothing else. They are counts of items we recorded and of requests we made, taken mechanically from the pipeline's own databases at build time. They are not a measurement of any agency, department, or publisher, and no label below is a judgement about one.

129 sources registered — 45 active, 62 planned, 20 unavailable, 2 evaluated and excluded.

38 of 45 active sources delivered items in the 14 days ending 2026-09-21 — 16,426 item(s) in all, about 1173.3 per day across the directory. 14 source(s) recorded requests that returned no content, across 10 host(s), out of 31,220 request(s) we made.

Counts are of our own requests, retries included. A 4xx or 5xx is the server declining to return content — that may be load, maintenance, on-demand generation, or a limit the publisher sets, and we cannot tell which from outside. Nothing here is a measurement of the publisher.

Status key:

- **active** — ingested by the pipeline today; each active entry carries a dated coverage evaluation in its registry notes.
- **planned** — registered so the coverage gap is visible; activation waits on the source's probe and content evaluation.
- **unavailable** — the publisher's site refuses the project's honestly-identified automated client; the refusal is recorded as observed, never evaded, and re-checked as sites change.
- **evaluated and excluded** — examined and found outside the project's scope of newly published federal government actions; kept on the record.

## Official govinfo collections

### Active (5)

- **Congressional Record (CREC)** (`govinfo-crec`) — active; govinfo collections API delta sync; [page](sources/govinfo-crec.md) — ingestion health: degraded; last 24 hours: 973 request(s) (792 answered, 181 returned no content) · no items ingested. 3927 of 22418 request(s) to api.govinfo.gov returned no content (17.5%, at or above the 10% mark).
- **Congressional Bills (BILLS)** (`govinfo-bills`) — active; govinfo collections API delta sync; [page](sources/govinfo-bills.md) — ingestion health: degraded; last 24 hours: 973 request(s) (792 answered, 181 returned no content) · no items ingested. 3927 of 22418 request(s) to api.govinfo.gov returned no content (17.5%, at or above the 10% mark).
- **Federal Register (FR)** (`govinfo-fr`) — active; govinfo collections API delta sync; [page](sources/govinfo-fr.md) — ingestion health: degraded; last 24 hours: 973 request(s) (792 answered, 181 returned no content) · 76 item(s) ingested. 3927 of 22418 request(s) to api.govinfo.gov returned no content (17.5%, at or above the 10% mark).
- **U.S. Courts Opinions (USCOURTS)** (`govinfo-uscourts`) — active; govinfo collections API delta sync; [page](sources/govinfo-uscourts.md) — ingestion health: degraded; last 24 hours: 973 request(s) (792 answered, 181 returned no content) · 348 item(s) ingested. 3927 of 22418 request(s) to api.govinfo.gov returned no content (17.5%, at or above the 10% mark).
- **Public and Private Laws (PLAW)** (`govinfo-plaw`) — active; Syncs via the govinfo collections API delta mechanism (activated 2026-07-28, delta-only).; [page](sources/govinfo-plaw.md) — ingestion health: degraded; last 24 hours: 973 request(s) (792 answered, 181 returned no content) · no items ingested. 3927 of 22418 request(s) to api.govinfo.gov returned no content (17.5%, at or above the 10% mark).

### Planned (4)

- **Congressional Hearings (CHRG)** (`govinfo-chrg`) — planned; Would sync via the govinfo collections API delta mechanism once enabled (GUIDE §7 Phase 4).; [page](sources/govinfo-chrg.md)
- **Congressional Reports (CRPT)** (`govinfo-crpt`) — planned; Would sync via the govinfo collections API delta mechanism once enabled (GUIDE §7 Phase 4).; [page](sources/govinfo-crpt.md)
- **Daily Compilation of Presidential Documents (DCPD)** (`govinfo-dcpd`) — planned; Would sync via the govinfo collections API delta mechanism once enabled (GUIDE §7 Phase 4).; [page](sources/govinfo-dcpd.md)
- **govinfo Bulk Data** (`govinfo-bulkdata`) — planned; bulk XML for historical backfill; [page](sources/govinfo-bulkdata.md)

## Agency newsrooms and web channels

### Active (25)

- **Defense News Releases** (`defense-newsroom`) — active; Would poll the news-release RSS feed daily for new items.; [page](sources/defense-newsroom.md) — ingestion health: delivering; last 24 hours: 27 request(s) (26 answered, 1 returned no content) · no items ingested. 25 item(s) in the last 14 days; most recent 2026-09-19; 15 of 345 request(s) to www.defense.gov returned no content.
- **Justice Press Releases** (`justice-newsroom`) — active; Polls the Drupal views news feed (component parameter filters to Office of Public Affairs) via AgencyClient, feed metadata only.; [page](sources/justice-newsroom.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 714 item(s) in the last 14 days; most recent 2026-09-18; 0 of 346 request(s) to www.justice.gov returned no content.
- **Labor News Releases** (`labor-newsroom`) — active; Would poll the news-release RSS feed daily for new items.; [page](sources/labor-newsroom.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 5 item(s) in the last 14 days; most recent 2026-09-17; 5 of 351 request(s) to www.dol.gov returned no content.
- **VA News Releases** (`va-newsroom`) — active; Would poll the VA news site RSS feed daily for new items.; [page](sources/va-newsroom.md) — ingestion health: delivering; last 24 hours: 29 request(s) (29 answered, 0 returned no content) · 2 item(s) ingested. 40 item(s) in the last 14 days; most recent 2026-09-20; 1 of 387 request(s) to news.va.gov returned no content.
- **DHS News Releases** (`dhs-newsroom`) — active; html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only).; [page](sources/dhs-newsroom.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 33 item(s) in the last 14 days; most recent 2026-09-18; 0 of 344 request(s) to www.dhs.gov returned no content.
- **SEC Press Releases** (`sec-newsroom`) — active; Would poll the press-release RSS feed daily for new items.; [page](sources/sec-newsroom.md) — ingestion health: delivering; last 24 hours: 28 request(s) (28 answered, 0 returned no content) · no items ingested. 8 item(s) in the last 14 days; most recent 2026-09-17; 0 of 355 request(s) to www.sec.gov returned no content.
- **FTC Press Releases** (`ftc-newsroom`) — active; Would poll the press-release RSS feed daily for new items.; [page](sources/ftc-newsroom.md) — ingestion health: delivering; last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested. 8 item(s) in the last 14 days; most recent 2026-09-17; 0 of 352 request(s) to www.ftc.gov returned no content.
- **NASA News Releases** (`nasa-newsroom`) — active; Would poll the breaking-news RSS feed daily for new items.; [page](sources/nasa-newsroom.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · 1 item(s) ingested. 69 item(s) in the last 14 days; most recent 2026-09-20; 0 of 383 request(s) to www.nasa.gov returned no content.
- **GAO Reports & Testimonies** (`gao-reports`) — active; RSS poll via AgencyClient, feed metadata only (crawl-delay economics; see notes).; [page](sources/gao-reports.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 31 item(s) in the last 14 days; most recent 2026-09-18; 0 of 343 request(s) to www.gao.gov returned no content.
- **White House Presidential Actions** (`whitehouse-presidential-actions`) — active; Polls the presidential-actions RSS feed via AgencyClient, then fetches each new item's page for the full instrument text (mode full).; [page](sources/whitehouse-presidential-actions.md) — ingestion health: delivering; last 24 hours: 55 request(s) (55 answered, 0 returned no content) · no items ingested. 18 item(s) in the last 14 days; most recent 2026-09-18; 0 of 701 request(s) to www.whitehouse.gov returned no content.
- **White House Executive Orders** (`whitehouse-executive-orders`) — active; Polls the executive-orders RSS feed via AgencyClient, then fetches each new item's page for the full order text (mode full); overlaps whitehouse-presidential-actions by design — shared items carry identical link URLs and merge through the standing corroboration rule.; [page](sources/whitehouse-executive-orders.md) — ingestion health: delivering; last 24 hours: 55 request(s) (55 answered, 0 returned no content) · no items ingested. 6 item(s) in the last 14 days; most recent 2026-09-18; 0 of 701 request(s) to www.whitehouse.gov returned no content.
- **Federal Reserve Press Releases** (`federal-reserve-news`) — active; RSS poll via AgencyClient (pending content evaluation); [page](sources/federal-reserve-news.md) — ingestion health: delivering; last 24 hours: 27 request(s) (25 answered, 2 returned no content) · no items ingested. 6 item(s) in the last 14 days; most recent 2026-09-18; 18 of 354 request(s) to www.federalreserve.gov returned no content.
- **CFTC Press Releases** (`cftc-press`) — active; html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only).; [page](sources/cftc-press.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 7 item(s) in the last 14 days; most recent 2026-09-17; 0 of 346 request(s) to www.cftc.gov returned no content.
- **EEOC Newsroom** (`eeoc-newsroom`) — active; html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only).; [page](sources/eeoc-newsroom.md) — ingestion health: delivering; last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested. 8 item(s) in the last 14 days; most recent 2026-09-17; 0 of 343 request(s) to www.eeoc.gov returned no content.
- **USPS Newsroom** (`usps-newsroom`) — active; RSS poll via AgencyClient, feed-metadata only (usps adapter; pending content evaluation); [page](sources/usps-newsroom.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 7 item(s) in the last 14 days; most recent 2026-09-19; 0 of 344 request(s) to about.usps.com returned no content.
- **FDA Press Announcements** (`fda-press`) — active; RSS poll via AgencyClient (pending content evaluation); [page](sources/fda-press.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 2 item(s) in the last 14 days; most recent 2026-09-17; 0 of 346 request(s) to www.fda.gov returned no content.
- **NIH News Releases** (`nih-news`) — active; Polls the news-releases RSS feed via AgencyClient, then fetches each new release for full text (mode full).; [page](sources/nih-news.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 4 item(s) in the last 14 days; most recent 2026-09-18; 0 of 350 request(s) to www.nih.gov returned no content.
- **FEMA Press Releases** (`fema-news`) — active; html-index adapter via AgencyClient — one listing fetch per poll, no article fetches (mode feed-only).; [page](sources/fema-news.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 30 item(s) in the last 14 days; most recent 2026-09-18; 5 of 348 request(s) to www.fema.gov returned no content.
- **NOAA News Releases** (`noaa-news`) — active; Polls the documented main RSS feed via AgencyClient, feed metadata only (article pages 403 identified clients).; [page](sources/noaa-news.md) — ingestion health: delivering; last 24 hours: 27 request(s) (26 answered, 1 returned no content) · no items ingested. 6 item(s) in the last 14 days; most recent 2026-09-17; 18 of 349 request(s) to www.noaa.gov returned no content.
- **NIST News** (`nist-news`) — active; Polls the documented news RSS feed via AgencyClient.; [page](sources/nist-news.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 4 item(s) in the last 14 days; most recent 2026-09-18; 1 of 349 request(s) to www.nist.gov returned no content.
- **U.S. Courts News** (`uscourts-news`) — active; Polls the documented Judiciary News RSS feed via AgencyClient.; [page](sources/uscourts-news.md) — ingestion health: delivering; last 24 hours: 26 request(s) (26 answered, 0 returned no content) · no items ingested. 2 item(s) in the last 14 days; most recent 2026-09-17; 1 of 347 request(s) to news.uscourts.gov returned no content.
- **Congress.gov API** (`congress-gov-api`) — active; Conditional GET of one page of the bill endpoint per poll (limit=250, sort=updateDate+desc, api.data.gov key in request PARAMETERS so the fetch log redacts it). The congress-bill-actions adapter emits one item per bill whose latestAction.actionDate falls inside config.INDEX_LOOKBACK_DAYS and never fetches an article page. Stored under the BILLACTIONS collection (GUIDE §3 bill actions), dated by the publisher's actionDate, never AGENCYPR.; [page](sources/congress-gov-api.md) — ingestion health: delivering; last 24 hours: 27 request(s) (26 answered, 1 returned no content) · no items ingested. 780 item(s) in the last 14 days; most recent 2026-09-18; 13 of 345 request(s) to api.congress.gov returned no content.
- **Senate.gov XML services** (`senate-xml`) — active; Conditional GET of the current session's roll-call vote menu; the senate-votes adapter bounds enumeration to config.INDEX_LOOKBACK_DAYS and fetches one per-vote XML record per in-window vote. Stored under the VOTES collection (GUIDE §3 recorded votes), never AGENCYPR.; [page](sources/senate-xml.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 7 item(s) in the last 14 days; most recent 2026-09-17; 0 of 350 request(s) to www.senate.gov returned no content.
- **ODNI Newsroom** (`odni-news`) — active; Polls the ODNI press-release RSS feed daily; article pages are fetched and extracted, honoring the host's 10-second crawl-delay.; [page](sources/odni-news.md) — ingestion health: quiet; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. Most recent item 2026-08-03, 49 days ago (quiet past 7 days).
- **CISA Cybersecurity Advisories** (`cisa-advisories`) — active; Polls the advisories RSS feed via AgencyClient; KEV JSON is a later extension.; [page](sources/cisa-advisories.md) — ingestion health: delivering; last 24 hours: 27 request(s) (27 answered, 0 returned no content) · no items ingested. 33 item(s) in the last 14 days; most recent 2026-09-18; 0 of 379 request(s) to www.cisa.gov returned no content.

### Planned (43)

- **Supreme Court Slip Opinions** (`scotus-slip-opinions`) — planned; Would parse the current term's slip-opinion HTML index and fetch opinion PDFs, drafting syllabus-first (GUIDE §3 phase J2).; [page](sources/scotus-slip-opinions.md)
- **State Press Releases** (`state-newsroom`) — planned; Would parse the press-release HTML index daily for new items.; [page](sources/state-newsroom.md)
- **Interior Press Releases** (`interior-newsroom`) — planned; Would parse the press-release HTML index daily for new items.; [page](sources/interior-newsroom.md)
- **Energy Press Releases** (`energy-newsroom`) — planned; Would parse the newsroom HTML index daily for new items.; [page](sources/energy-newsroom.md)
- **Education Press Releases** (`education-newsroom`) — planned; Would parse the press-release HTML index daily for new items.; [page](sources/education-newsroom.md)
- **FCC Headlines** (`fcc-newsroom`) — planned; Would poll the EDOCS RSS API (api2.fcc.gov, separate host from the www WAF) for new items.; [page](sources/fcc-newsroom.md)
- **NLRB News Releases** (`nlrb-newsroom`) — planned; Would parse the news-release HTML index daily for new items.; [page](sources/nlrb-newsroom.md)
- **FEC Press Releases** (`fec-newsroom`) — planned; Would parse the updates HTML index (filtered to press releases) daily for new items.; [page](sources/fec-newsroom.md)
- **GSA News Releases** (`gsa-newsroom`) — planned; Would parse the news-release HTML index daily for new items.; [page](sources/gsa-newsroom.md)
- **OPM News Releases** (`opm-newsroom`) — planned; Would parse the newsroom HTML index daily for new items.; [page](sources/opm-newsroom.md)
- **CRS Reports** (`crs-reports`) — planned; Would delta-sync the api.congress.gov crsreport endpoint (same api.data.gov key the pipeline already holds).; [page](sources/crs-reports.md)
- **White House Briefing Room** (`whitehouse-briefing-room`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/whitehouse-briefing-room.md)
- **Oversight.gov IG Reports** (`oversight-gov`) — planned; HTML index diff via AgencyClient (pending content evaluation); aggregator rule: every ingested item must cite the originating Inspector General as its origin, never oversight.gov itself.; [page](sources/oversight-gov.md)
- **FDIC Press Releases** (`fdic-news`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/fdic-news.md)
- **OCC News Releases** (`occ-news`) — planned; Would poll the documented RSS suite (occ.gov/rss/index-rss.html) for news releases, bulletins, and alerts.; [page](sources/occ-news.md)
- **CFPB Newsroom** (`cfpb-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/cfpb-newsroom.md)
- **NCUA Press Releases** (`ncua-news`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/ncua-news.md)
- **FHFA News Releases** (`fhfa-news`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/fhfa-news.md)
- **NRC News Releases** (`nrc-news`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/nrc-news.md)
- **SBA Newsroom** (`sba-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/sba-newsroom.md)
- **NSF News** (`nsf-news`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/nsf-news.md)
- **USTR Press Releases** (`ustr-press`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/ustr-press.md)
- **CDC Newsroom** (`cdc-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/cdc-newsroom.md)
- **CMS Newsroom** (`cms-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/cms-newsroom.md)
- **IRS Newsroom** (`irs-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/irs-newsroom.md)
- **FBI Press Releases** (`fbi-news`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/fbi-news.md)
- **ICE Newsroom** (`ice-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/ice-newsroom.md)
- **CBP Media Releases** (`cbp-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/cbp-newsroom.md)
- **TSA Press Releases** (`tsa-press`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/tsa-press.md)
- **USCIS Newsroom** (`uscis-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/uscis-newsroom.md)
- **Census Bureau Press Releases** (`census-newsroom`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/census-newsroom.md)
- **USPTO News Updates** (`uspto-press`) — planned; HTML index diff via AgencyClient (pending content evaluation); [page](sources/uspto-press.md)
- **Sentencing Commission News** (`ussc-news`) — planned; Would poll the documented press-release RSS feed daily for new items.; [page](sources/ussc-news.md)
- **Federal Register API (public inspection)** (`federal-register-api`) — planned; Would delta-sync the public-inspection and documents endpoints (keyless JSON REST).; [page](sources/federal-register-api.md)
- **Regulations.gov API v4** (`regulations-gov-api`) — planned; Would query the v4 documents endpoint by posted date (api.data.gov key we already hold, X-Api-Key header).; [page](sources/regulations-gov-api.md)
- **GPO Bulk Data — BILLSTATUS** (`govinfo-billstatus`) — planned; Would watch the batch-completion RSS and sitemap index, then fetch changed status XML from the bulkdata directory (append /xml for machine-readable listings).; [page](sources/govinfo-billstatus.md)
- **House Clerk roll-call votes** (`house-clerk-votes`) — planned; Would walk the numeric roll-call sequence from a watermark, fetching new vote XML files.; [page](sources/house-clerk-votes.md)
- **House Document Repository (floor + committee)** (`docs-house-gov`) — planned; Would poll the weekly floor XML and committee-repository listings and diff.; [page](sources/docs-house-gov.md)
- **DVIDS (Digital Visual Information Distribution System)** (`dvids`) — planned; Would delta-sync the Search API per branch (types news+image first; date-windowed under the depth-1000 pagination cap; a timestamp pass honors the TOS cache-refresh duty), then the Asset API for selected items, with a free registered key; items attributed to the originating unit/service per the aggregator rule.; [page](sources/dvids.md)
- **BLS News Releases** (`bls-news`) — planned; Would poll the documented news-release feeds daily; the v2 API (api.bls.gov, registered key, 500 queries/day) is a later data extension.; [page](sources/bls-news.md)
- **OFAC Recent Actions** (`ofac-recent-actions`) — planned; html-index adapter via AgencyClient — parses cleanly against captured bytes, but the host would not serve robots.txt on 2026-07-31, so nothing is fetched.; [page](sources/ofac-recent-actions.md)
- **NASA Image and Video Library** (`nasa-image-library`) — planned; Would search date-windowed (no changed-since filter documented; client-side dedupe), fetching asset manifests for selected items.; [page](sources/nasa-image-library.md)
- **National Park Service API** (`nps-api`) — planned; Would query news/alerts endpoints with a registered key (documented 1,000 req/hour).; [page](sources/nps-api.md)

## Agency email bulletins

### Active (15)

- **Treasury Press Releases (email)** (`treasury-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/treasury-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 115 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **IRS Newswire (email)** (`irs-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/irs-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 12 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **SSA Press Releases (email)** (`ssa-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/ssa-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 88 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **Justice Department News (email)** (`justice-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/justice-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 116 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **U.S. Attorneys News (email)** (`usattorneys-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/usattorneys-email.md) — ingestion health: delivering; last 24 hours: 1 item(s) ingested. 358 item(s) in the last 14 days; most recent 2026-09-20, delivered by email.
- **DEA Updates (email)** (`dea-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/dea-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 6 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.
- **USDA News (email)** (`agriculture-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/agriculture-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 20 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **FSIS Recalls and Public Health Alerts (email)** (`fsis-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/fsis-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 26 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **USCIS Updates (email)** (`uscis-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/uscis-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 4 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **FDA Email Updates (email)** (`fda-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/fda-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 22 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.
- **CMS Newsroom (email)** (`cms-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/cms-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 2 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.
- **VA Updates (email)** (`va-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/va-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 9 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.
- **Federal Reserve Board Announcements (email)** (`federal-reserve-email`) — active; Subscription notifications to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/federal-reserve-email.md) — ingestion health: quiet; last 24 hours: no items ingested. Most recent item 2026-07-31, 52 days ago (quiet past 7 days).
- **FDIC Press Releases (email)** (`fdic-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/fdic-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 6 item(s) in the last 14 days; most recent 2026-09-17, delivered by email.
- **USPS Inspector General (email)** (`usps-oig-email`) — active; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/usps-oig-email.md) — ingestion health: delivering; last 24 hours: no items ingested. 21 item(s) in the last 14 days; most recent 2026-09-18, delivered by email.

### Planned (15)

- **FinCEN Updates (email)** (`fincen-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/fincen-email.md)
- **Office of Financial Research (email)** (`ofr-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/ofr-email.md)
- **ATF News (email)** (`atf-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/atf-email.md)
- **Transportation Press Releases (email)** (`transportation-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/transportation-email.md)
- **FAA Updates (email)** (`faa-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/faa-email.md)
- **NHTSA Press Releases (email)** (`nhtsa-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/nhtsa-email.md)
- **EPA News Releases (email)** (`epa-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/epa-email.md)
- **Coast Guard News (email)** (`uscg-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/uscg-email.md)
- **U.S. Commercial Service (email)** (`commercial-service-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/commercial-service-email.md)
- **The Week at State (email)** (`state-week-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/state-week-email.md)
- **CPSC Recalls and News (email)** (`cpsc-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/cpsc-email.md)
- **PBGC Updates (email)** (`pbgc-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/pbgc-email.md)
- **Election Assistance Commission (email)** (`eac-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/eac-email.md)
- **Sentencing Commission News (email)** (`ussc-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/ussc-email.md)
- **HUD Inspector General (email)** (`hud-oig-email`) — planned; Subscription bulletins to the project mailbox, ingested by the email adapter (src/fapd/email_sources.py; raw RFC-5322 capture, DKIM verify-and-archive).; [page](sources/hud-oig-email.md)

## Unavailable sources (20)

- **Treasury Press Releases** (`treasury-newsroom`) — unavailable; Would parse the press-release HTML index daily for new items.; [page](sources/treasury-newsroom.md)
- **USDA Press Releases** (`agriculture-newsroom`) — unavailable; Would parse the press-release HTML index daily for new items.; [page](sources/agriculture-newsroom.md)
- **Commerce Press Releases** (`commerce-newsroom`) — unavailable; Would query the Commerce.gov content API /news endpoint (api.data.gov key family) for new items.; [page](sources/commerce-newsroom.md)
- **HHS Press Releases** (`hhs-newsroom`) — unavailable; Would parse the newsroom HTML index daily for new items.; [page](sources/hhs-newsroom.md)
- **HUD Press Releases** (`hud-newsroom`) — unavailable; Would parse the press-release HTML index daily for new items.; [page](sources/hud-newsroom.md)
- **DOT Press Releases** (`transportation-newsroom`) — unavailable; Would parse the newsroom HTML index daily for new items.; [page](sources/transportation-newsroom.md)
- **EPA News Releases** (`epa-newsroom`) — unavailable; Would poll the news-release RSS feed daily for new items.; [page](sources/epa-newsroom.md)
- **SSA Press Releases** (`ssa-newsroom`) — unavailable; Would parse the newsroom HTML index daily for new items.; [page](sources/ssa-newsroom.md)
- **CBO Publications** (`cbo-publications`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/cbo-publications.md)
- **FERC News Releases** (`ferc-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/ferc-news.md)
- **DEA Press Releases** (`dea-press`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/dea-press.md)
- **ATF Press Releases** (`atf-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/atf-news.md)
- **Coast Guard News Releases** (`uscg-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/uscg-news.md)
- **FAA Newsroom** (`faa-newsroom`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/faa-newsroom.md)
- **NHTSA Press Releases** (`nhtsa-press`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/nhtsa-press.md)
- **Army News Releases** (`army-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/army-news.md)
- **Navy Press Releases** (`navy-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/navy-news.md)
- **Air Force News** (`air-force-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/air-force-news.md)
- **Marine Corps News** (`marines-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/marines-news.md)
- **Space Force News** (`space-force-news`) — unavailable; HTML index diff via AgencyClient (pending viability check); [page](sources/space-force-news.md)

## Evaluated and excluded (2)

- **National Archives Catalog API** (`nara-catalog`) — evaluated and excluded; Not applicable to the daily flow — archive, not news-flow.; [page](sources/nara-catalog.md)
- **Library of Congress JSON API** (`loc-api`) — evaluated and excluded; Not applicable to the daily flow — archive, not news-flow.; [page](sources/loc-api.md)

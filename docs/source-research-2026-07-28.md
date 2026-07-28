# Source-expansion research — 2026-07-28

Three parallel research passes (blocked-source re-evaluation; executive-branch
expansion; legislative + judicial deepening), all under one rule: **read the
publisher's own access documentation first** — developer pages, API docs,
official RSS directories — via ordinary web research. No endpoints probed, no
project scripts run, nothing through the pipeline's budgeted clients. Probes
remain a separate, operator-visible step (GUIDE §3 gate 2).

Registry effect: 81 → **93 sources** — 12 new `planned` entries added and 17
existing entries corrected or annotated. Per-source detail lives in
`sources/registry.yaml` notes; this document is the narrative and the ranking.

## Cross-cutting findings

1. **A WAF on the newsroom is not a closed agency.** Of the 23 sources
   recorded `unavailable`, research found documented alternative machine
   channels for roughly half — usually an API or feed on a *different host or
   path* than the one that blocked us (FCC's api2.fcc.gov EDOCS API,
   Commerce's api.commerce.gov, NOAA's rss.xml, OFAC's own subdomain, DVIDS
   for all six military services). Robots and WAF verdicts are per-path and
   per-host; the registry now records which door to knock on next.

2. **Several "404 unavailable" entries were just moved pages.** uscourts.gov
   news, USSC news, and the DOJ feed all relocated; the corrected URLs (with
   documented RSS feeds for all three) are in the registry. A 404 recorded at
   probe time deserves a documentation search before it hardens into
   "unavailable."

3. **The api.data.gov key we already hold is a master key.** Congress.gov API
   (committee meetings, nominations, House votes, CRS reports — 5,000
   req/hour documented), Regulations.gov v4, OpenFEC, and the Commerce
   content API all ride it. Highest coverage-per-integration-effort in the
   sprint.

4. **Autodiscovery under-finds feeds.** NIST documents ~24 RSS feeds on its
   own feeds page; none are advertised in the index HTML our probe read. The
   probe's `<link rel=alternate>` scan is necessary but not sufficient — a
   documentation search belongs in the onboarding evaluation (gate 3).

5. **GovDelivery is (probably) email-only — one probe settles it.** The
   platform's bulletins archive is login-walled and OFAC's RSS-retirement
   notice points users to email, but one vendor-documented topic feed
   (FDIC `USFDIC_26/feed.rss`) contradicts the pattern. A single probe of
   that URL resolves the question for every agency marked "GovDelivery to
   evaluate." If it is email-only, the fallback for Treasury/USDA/HHS/SSA-class
   agencies is an **email-ingestion adapter** (subscribe a project address,
   parse bulletins) — a new adapter class needing its own GUIDE treatment.

6. **The research fetcher's blocks are not our client's blocks.** Several
   .gov hosts 403'd the research tooling but served our identified client
   HTTP 200 in July probes (state.gov, supremecourt.gov), and vice versa (EPA
   robots-blocks us but tolerated the research fetcher). Only
   `scripts/check_sources.py` verdicts are recorded as availability facts.

## Ranked recommendations

### Tier A — probe next (documented, high coverage value, low effort)

1. **Federal Register API — public-inspection documents** (`federal-register-api`):
   keyless; documents visible *before* publication day; the site's own
   bot-gate page directs automation to the API. The single biggest freshness
   upgrade available; also the structured alternative to scraping
   whitehouse.gov for presidential actions.
2. **Congress.gov API** (`congress-gov-api` + `crs-reports`): committee
   meetings with witnesses, nominations, House votes, CRS reports — four
   coverage gaps, one key, one client.
3. **DVIDS API** (`dvids`): re-opens six blocked military-service sources
   through DoD's own distribution API in one integration.
4. **DOJ corrected feed** (`justice-newsroom`): the 404 was a stale path
   (probe got 404, not 403); the documented feed pattern plus division/USAO
   feeds fills the highest-value newsroom gap and partially covers DEA/ATF.
5. **Judicial pair** (`uscourts-news`, `ussc-news`): both had merely moved;
   both now have documented RSS feeds registered. Trivial re-probes.

### Tier B — probe soon (documented, one uncertainty each)

6. **GPO BILLSTATUS bulk data** (`govinfo-billstatus`): 4-hour bill-action
   cadence with batch RSS for change detection, on GPO infrastructure we
   already trust.
7. **Senate XML + House Clerk votes** (`senate-xml`, `house-clerk-votes`):
   the only machine sources for same-day floor votes in each chamber.
8. **FCC EDOCS API** (`fcc-newsroom`): purpose-built feed API on a non-WAF
   host; 2020-vintage documentation needs a liveness check.
9. **NIST + OCC + NOAA feed upgrades**: documented feed URLs recorded;
   near-zero effort if the probes pass.
10. **Regulations.gov API v4** (`regulations-gov-api`): opens the
    rulemaking-docket layer for ~180 agencies at once; decide volume policy
    at content evaluation.

### Tier C — registered, needs operator decisions or has real uncertainty

- **CISA advisories** (`cisa-advisories`): RSS formally retired 2025-05;
  KEV JSON + html-index path works regardless. New action category.
- **BLS / ODNI / OFAC / docs.house.gov / FDIC-GovDelivery**: registered with
  documented starting points; each needs one confirming probe.
- **Commerce content API**: real but possibly stale (2019 changelog).

### Flagged for operator decision (not recommended without a policy change)

- **PACER CM/ECF RSS**: documented, free at the feed layer, but document
  links bill per PACER's fee schedule, and GUIDE §3 defers docket-level
  coverage to J3. Parked.
- **SEC EDGAR**: welcoming documented policy for identified clients (10
  req/s, declared UA) but thousands of company filings/day — company speech,
  not agency speech; would need its own source class and filtering policy.
- **Email-ingestion adapter class**: the only route to several WAF'd cabinet
  newsrooms (Treasury, HHS, SSA, HUD press). New adapter class + GUIDE
  amendment if pursued.

### Noted, not registered (next tier)

SAM.gov opportunities API, Grants.gov search2 API, CDC Content Services API,
NIH news RSS (feed URL unconfirmed), FDIC BankFind, NHTSA recalls API,
FERC eCollection filings RSS, eCFR API, epa.mediaroom.com (official EPA
press-alert platform on a third-party host; content looked stale), circuit
courts' self-hosted RSS (ca4/ca5/ca9 — probe selectively if USCOURTS lag
hurts), FJC data exports (reference data, not a publication stream),
govinfo.gov/feeds (cheaper change detection over collections we already
sync). Each is one registry entry away if wanted.

## Negative findings worth keeping

- GPO bulkdata carries **no CHRG or CRPT** — committee hearings/reports stay
  govinfo API collections.
- **HUD verifiably has no press RSS** (its /rss page lists only the HUD USER
  research feed); press distribution is a listserv.
- **supremecourt.gov offers no feed at all** — the planned html-index
  approach for `scotus-slip-opinions` stands, now with officially documented
  timeliness (opinions posted within minutes; argument transcripts same day).
- **CourtListener/RECAP remain ineligible** (third-party, however good):
  official sources only.
- open.cdc.gov is DNS-dead; CDC's live machine channel is the Content
  Services API at tools.cdc.gov/api.

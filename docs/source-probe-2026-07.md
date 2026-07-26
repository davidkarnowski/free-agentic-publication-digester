# Source Probe Analysis — 2026-07-26

First end-to-end viability sweep of the Tier 1–2 source universe.
Methodology: for each of 72 non-govinfo registered sources, through our
honestly-identified `AgencyClient` (paced ≤1 req/s, robots.txt enforced
via RFC 9309 parser, crawl-delays honored, every request logged, every
response captured into the provenance layer): robots verdict → fetch of
the registered feed/index URL → format detection with RSS/Atom
autodiscovery → item enumeration → one sample article fetched and
text-extracted. 193 requests total (~39% of the agency daily budget).
Raw findings: `data/probe/2026-07-26/*.json`; capture hashes in
`provenance/manifests/2026-07-26.jsonl`.

## Headline numbers

| Verdict | Count | Meaning |
|---|---|---|
| feed-ok | 10 | RSS verified end-to-end incl. sample-article text extraction |
| html-only | 34 | Index reachable; no feed found — HTML diffing required |
| HTTP 403 | 13 | Blocked by WAF despite honest identification |
| HTTP 404 | 6 | Registered URL wrong/moved — correct and re-probe |
| robots refused | 9 | robots.txt disallows our client — honored, not fetched |

**14% of the federal Tier 1–2 source universe is ingestible today via the
politest possible channel (verified RSS).** Roughly half is reachable but
feed-less; roughly a third is closed to honestly-identified automated
access at the probed paths.

## The ten verified feeds — ingestion-ready cohort

| Source | Items | Feed body | Sample article text | Assessment |
|---|---|---|---|---|
| GAO reports | 25 | ~4,100 chars (near-full-text) | 9.0K chars | Best-in-class; feed alone nearly sufficient |
| Labor | 10 | ~1,800 chars | 6.0K | Strong |
| FTC | 10 | ~520 | 9.3K | Strong |
| SEC | 25 | ~250 | 5.3K | Strong |
| NASA | 10 | ~310 | 9.4K | Strong |
| FDA | 20 | ~230 | 7.2K | Strong |
| Federal Reserve | 20 | ~110 | 10.1K | Teaser feed, rich articles |
| VA | 30 | ~140 | 6.4K | Strong |
| Defense | 10 | 0 | **article 403** | Feed-only candidate: articles WAF-blocked |
| USPS | **668** | ~270 | **16 chars** | Feed metadata usable; articles script-rendered — extraction fails |

Two failure modes worth naming because they'll recur: **Defense's split
posture** (feed open, article pages blocked) means feed-description-only
ingestion with disclosed depth limits; **USPS's script-rendered articles**
defeat plain-HTML extraction — item metadata is ingestible, full text is
not, and we disclose rather than run a browser.

## Accountability findings (worth publishing in their own right)

1. **All four-plus-one military service newsrooms (Army, Navy, Air Force,
   Marines, Space Force) and the Coast Guard disallow our client via
   robots.txt**, as do Treasury, USDA, and — notably for an environmental
   *disclosure* agency — EPA. We honored every refusal (zero fetches).
2. **CBO and CRS — the legislative support agencies whose entire purpose
   is public analysis — returned HTTP 403 to an honestly-identified
   client.** So did HHS, HUD, FCC, FAA, NOAA, SSA, DOT, Commerce, FERC,
   NHTSA, DEA, and ATF. The pattern is WAF defaults, not policy decisions,
   but the effect is identical: official public information that cannot be
   programmatically read without pretending to be a browser, which we will
   not do (GUIDE §3).
3. Combined: **22 of 72 sources (31%) are closed to identified automated
   access at their primary newsroom paths.** This number is now tracked in
   SOURCES.md and is itself a finding about public-information access.
4. The 404 cohort (Justice, Interior, Education, USCourts, USSC) is
   probably our URL guesses aging against redesigns — correct and re-probe
   before drawing conclusions.

## Implications for S2 (ingestion pilot)

- **Pilot cohort = the 8 clean feeds** (GAO, Labor, FTC, SEC, NASA, FDA,
  Fed, VA) + Defense feed-only. Estimated volume from observed feed
  depths: ~40–80 items/day combined — well within the agency budget with
  conditional GETs.
- GAO's near-full-text feed makes it the ideal first **report-publisher**
  ingest (GUIDE §3 class) — high value, zero article fetches needed.
- The html-only 34 (incl. State, CDC, IRS, White House, oversight.gov)
  need per-source index parsing — S3 work, prioritized by tier and by
  whether GovDelivery/email fallbacks exist for the blocked cohort.
- Re-probe cadence: monthly for `unavailable` (WAF configs change), plus
  immediately after any registry URL correction.

## Provenance note

Every probe response is captured content-addressed with both hashes and
appears in the 2026-07-26 committed manifest — the archive's first real
mutable-source observations, including the refusals and errors, per the
absence-is-an-assertion rule (GUIDE §7).

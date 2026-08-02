# Pre-publication TODO

The launch checklist. (Historical framing: written while the repo was
private; the repo went public and the site went live 2026-07-30 — items
below that gate remain are post-launch quality gates.) Items marked **[decision]** need the
operator; the rest are build work. Companion analysis:
`docs/publication-readiness-2026-07-29.md`. Maintain this file as items
close (check them off with dates).

## Decisions (operator)

- [x] 2026-07-29 **[decision] Code license: Apache-2.0** (operator).
  `LICENSE` (canonical text) + `NOTICE` committed; pyproject
  `license`/`license-files` set.
- [x] 2026-07-29 **[decision] Content license: CC BY 4.0** (operator).
  `LICENSE-CONTENT.md` committed; stated in site footer, llms.txt Reuse
  note, agents-page Reuse section, README Licensing section, and each
  digest's methodology footer (all digests re-rendered).
- [x] 2026-07-30 **[decision] Domain: `fapd.info`** (operator).
  `SITE_BASE_URL=https://fapd.info` set in `.env`/`.env.example` and all
  machine surfaces regenerated with absolute URLs. Hosting resolved the
  same day: **served from the shared VPS** (Docker stack, `deploy/vps/`;
  placeholder live over HTTPS with auto-renewing TLS since 2026-07-30).
  Real site content replaces the placeholder when the backend container
  deploys (ops-backlog OB-1).
- [x] 2026-07-30 **[decision] Repo visibility flip** (operator, this
  evening: "since we are live anyway I think it's time"). Pre-flip
  hygiene done same evening: full-history credential sweep clean; VPS
  coordinates scrubbed from deploy.sh (env-file pattern; one historical
  commit retains them — operator-accepted, SSH is key-only);
  SECURITY/CONTRIBUTING/CITATION/CODE_OF_CONDUCT added; repo URL wired
  into site footer, llms.txt, agents page. Deferred knowingly: the
  editorial spot-audit (queued for the first fully-VPS digest,
  2026-07-30's EOD).

## Build work

### Publishing infrastructure
- [ ] ~~GH Pages deploy workflow~~ **Dead track (2026-07-30):** the VPS
  runtime won (docs/vps-runtime-plan.md); the site is served by the
  fapd stack's nginx and GH Pages is not planned. Kept for the record:
  actions/deploy-pages from the `site/` directory (branch-based Pages
  cannot serve `site/`; a workflow is required). Include `SITE_BASE_URL`
  env so machine surfaces emit absolute URLs.
- [x] 2026-07-30 **CI workflow** (`.github/workflows/ci.yml`): `uv sync`
  + `ruff check` + `pytest` on push/PR — promoted from the `gh-native`
  branch.
- [x] 2026-07-30 **LLM backend swap** (`src/fapd/llm.py`): Anthropic-API
  backend behind `LLM_BACKEND=api|cli` with a per-tier model mapping
  (CLI stays the local default). Unblocks hosted scheduling and
  decouples the VPS from `claude` CLI tooling.
- [x] **Daily scheduling — active track: VPS runtime.** *Complete: the
  named remainders both landed 2026-07-30 — /today renderer (OB-8 Done)
  and canonical VPS evidence pushes (OB-11 Done). History:* *2026-07-30:
  the collector core landed (src/fapd/collect.py — supervisor,
  per-source-class workers, journal, triggers; GUIDE §4/§5/§6 r12
  amendments) and the backend container deployed the same day (real
  site live on fapd.info, collector running on the box); remaining
  scope is the /today renderer (ops-backlog OB-8) and making VPS
  evidence pushes canonical (OB-11), designed in
  docs/continuous-ingestion.md.* Original item:
  (docs/vps-runtime-plan.md, adopted 2026-07-30, superseding the
  GH-native track before its T2–T5 evaluation ran): the pipeline runs
  on a VPS under cron/systemd, pushes evidence commits (digests,
  manifests, SOURCES.md, site) with a bot identity, and GitHub remains
  the public repo, CI, and integrity witness (GUIDE §7). Stable IPv4 +
  rDNS become the crawler-identity anchor; Web Bot Auth signing is a
  strengthening layer, not a prerequisite. Remaining work is the
  deployment outline in the plan doc (provision, first-run smoke, bot
  identity, scheduler, rDNS, run-summary emitter). Open since Phase 1.

### Community files
- [x] 2026-07-30 `SECURITY.md` — contact route (hustleyourcity address), what's in
  scope (the pipeline; not .gov sites — include a pointer explaining we
  are not an authority for government-site issues).
- [x] 2026-07-30 `CONTRIBUTING.md` — GUIDE-first rule (changes to GUIDE.md precede
  implementation), test expectations, register/lexicon rules for prose,
  how to propose a new source (five gates, adding-sources.md).
- [x] 2026-07-30 `CITATION.cff` — cite the aggregation; reinforce citing official
  sources for claims.
- [x] 2026-07-30 `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1 by
  reference, plus the non-partisan-space rule.

### Flip-time edits (do these the same day the repo goes public)
- [x] 2026-07-30 agents page + about page say "public repository" — true at flip
  while private; verify true, or reword, at flip time.
- [ ] README "How this project is built" link check; site readme.html
  regeneration.
- [x] 2026-07-30 Repo URL in every page footer, llms.txt, and the agents page.
- [ ] Announce-facing check of SOURCES.md rendering (it is the public
  accountability artifact).

### Token economics (baseline now measured)
- [x] 2026-07-29 **Batch the retries.** Both LLM layers now escalate:
  group retry (5 items) first, single-item isolation only for what is
  still missing. On the measured day this collapses ~25 calls to ~5,
  about 500K input tokens. Shortfall logging added to establish whether
  truncation drives the misses before tuning batch size.
- [ ] ~~Set the GUIDE §6 rule-8 daily cap~~ **tracked in exactly one
  place: ops-backlog OB-4** (and prioritized as review R1 in the
  Editorial agent's backlog). Struck here per the one-file rule.

### Accuracy & freshness
- [x] 2026-07-30 **Dated STATUS snapshot** (README "Status (2026-07-30)"
  section): registry counts, active sources by channel, test count,
  latest digest date, live-site URL — the single authoritative numbers
  block, so external AI readers stop averaging stale worklog figures
  (lesson from the NotebookLM briefing fact-check). Refresh the date
  with each update; anything elsewhere that disagrees defers to it.
  *Regressed and re-fixed 2026-08-02 (doc audit): the block sat at
  2026-07-30 values while every number moved. A block that calls
  itself authoritative decays fastest — refresh it with each
  substantive merge, or demote it to pointers at derived surfaces.*
- [ ] Editorial spot-audit of a full digest against sources (GUIDE §2
  compliance read-through by the operator).
- [ ] ~~Wayback top-up pass~~ **tracked in exactly one place:
  ops-backlog OB-5** (F-003 points there too). Struck here per the
  one-file rule.

### Source work that continues regardless (the standing pillar)
- [ ] Probe shortlist Tier A: federal-register-api (public inspection),
  congress-gov-api, DVIDS (needs key signup + media-policy GUIDE
  amendments: byte budget, video posture, caption/credit rules,
  asset_posture), FCC api2 re-probe (504 was possibly transient),
  BLS/ODNI feed-URL reads, USSC activation when its feed populates,
  GovDelivery-pattern probe (FDIC topic feed).
- [ ] **Official-video transcripts** (research complete 2026-07-29:
  docs/youtube-transcripts-research-2026-07-29.md — YouTube captions
  are not legitimately reachable by non-owners and the scraper path
  fails the consent test, finally; the transcripts' authoritative homes
  are .gov pages): adopt the four GUIDE amendments (commercial-platform
  mirrors rule, Digital Registry verification, signal-class sources,
  ASR ≠ official text), then probe/register the GovTranscript pages
  (state.gov briefings feed, whitehouse.gov, war.gov transcripts).
  Digital-Registry verifier CORRECTED 2026-07-29 after hands-on check:
  the Touchpoints API requires a federal-affiliated account
  (source-verified) — no public read path exists. Replaced by (a) an
  engagement letter to feedback-analytics@gsa.gov requesting public
  read/export of the registry, and (b) the interim standard: official
  social accounts verified against the agency's own .gov social
  directory page, evidenced per registration.
- [ ] **Blocked-source access program** (ranked plan in
  docs/access-alternatives-research-2026-07-29.md):
  1. Email-ingestion adapter over GovDelivery — ~~GUIDE amendment~~
     **done 2026-07-29** (§3 "Email-distributed sources" + §7 DKIM
     corroboration). Remaining: project mailbox under the public
     identity (operator: create + put credentials in .env), then the
     adapter build (type: email registry entries, IMAP poll, raw-message
     captures, DKIM verify-and-archive, email-full/email-teaser modes),
     then subscribe USTREAS/USSSA/USDOJDEA/USAFAA/HHS first.
  2. M-23-22 template letters to the 11 WAF-blocked agencies (quote the
     "shall permit web scraping … unimpeded" language; offer
     Friendly-Bots/Web-Bot-Auth verification; cc GSA/TTS Digital.gov);
     record all outcomes, including silence, in registry notes.
  3. Web Bot Auth request signing (Ed25519 + /.well-known JWKS on the
     site) + Cloudflare Verified/Friendly Bots submission; reference in
     every letter. IETF WG specs due April/August 2026.
  Interim: Wayback CDX read-path for WAF-403 sources, pre-existing
  captures only (bright line: never Save-Page-Now-as-proxy), labeled
  archive-sourced. GUIDE amendments precede each implementation.

## Feature backlog (post-launch, operator-requested)

- [x] ~~Section auto-tagging~~ **tracked in exactly one place: ops-backlog OB-9** (section layer done; item-level remainder lives there). Struck here per the one-file rule. Original item: **Section auto-tagging** (requested 2026-07-30). *2026-07-30: the
  section layer shipped — GUIDE §6 r12a, `src/fapd/tags.py`, `Tags:`
  lines in the digest and tag chips on the site; item-level tags and
  digests.json/meta emission remain (ops-backlog OB-9).* Original item:
  digest sections
  and items carry machine-readable tags on the site and agent surfaces —
  (a) branch (`legislative`/`executive`/`judicial`), mechanical from the
  collection and registry, zero tokens; (b) department/agency names,
  mechanical from registry `parent_org` and FR agency metadata; (c)
  LLM-generated one-to-three-word key values representing each section's
  natural-language content, for SEO and LLM-based discovery. Layer (c)
  is a new model layer: independently prompt-versioned, ledgered,
  banned-lexicon-gated, and labeled model-derived like every other
  generated field — never laundered into fields that read as
  source-provided. Rendering: HTML meta/keywords + visible tag chips on
  section headers, tags in digests.json entries, and a tags block on
  each digest's agent surface. GUIDE amendment precedes implementation
  (new §2/§6 language for the tag layer).

- [ ] **Per-item official-text marker in the canonical digest**
  (follow-up to the 2026-07-30 readability layer): the site now styles
  plain-speak and mechanical notations, but cannot distinguish
  verbatim-official item summaries from model-written ones — that fact
  lives only in the DB (`summaries.method`). Amend the digest format
  (report.py + TEMPLATE) to mark it per item (e.g. a trailing
  "— official summary" token), then style the two registers apart in
  publish. Canonical-format change: GUIDE §2 note precedes.
- ~~**PDF render and serve**~~ — **dropped 2026-07-30** (operator, the
  same day it was requested). Struck rather than deleted: the design
  notes stay in git history if the idea returns. Human archival and
  citation needs are already served by the canonical Markdown and the
  styled HTML, and agents were never the audience for a fixed-layout
  format.

## Done (for the record)
- [x] 2026-07-29 — Sensitive-content audit of full history: PASS.
- [x] 2026-07-29 — `research/` + `.claude/` structurally gitignored.
- [x] 2026-07-29 — Internal vocabulary removed from public pages.
- [x] 2026-07-29 — `SITE_BASE_URL` machinery for absolute machine-surface
  URLs (sitemap/feed/robots/llms.txt/digests.json), tested.
- [x] 2026-07-29 — AI-development transparency page + GUIDE §9 policy.
- [x] 2026-07-29 — Access-advocacy pillar in GUIDE §1/§3 and all public
  surfaces.
- [x] 2026-07-29 — pyproject urls/readme/keywords metadata.
- [x] 2026-07-28 — Rebrand to FAPD incl. wire identity (UA, feed IDs) in
  the pre-publication window.
- [x] 2026-07-28 — Agency dating rule (no backfill passed off as news).

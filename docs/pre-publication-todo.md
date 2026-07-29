# Pre-publication TODO

The launch checklist: everything standing between the private repo and a
public repo + published site. Items marked **[decision]** need the
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
- [ ] **[decision] Domain.** Choose and register the public domain (or
  decide user-site `davidkarnowski.github.io`). Then: `CNAME` in site/,
  set `SITE_BASE_URL` in the build environment (machinery landed
  2026-07-29), regenerate.
- [ ] **[decision] Repo visibility flip date** — after the items below
  it gates are done.

## Build work

### Publishing infrastructure
- [ ] **GH Pages deploy workflow** (`.github/workflows/pages.yml`):
  actions/deploy-pages from the `site/` directory (branch-based Pages
  cannot serve `site/`; a workflow is required). Include `SITE_BASE_URL`
  env so machine surfaces emit absolute URLs.
- [ ] **CI workflow** (`.github/workflows/ci.yml`): `uv sync` + `ruff
  check` + `pytest` on push/PR. 227 tests currently run only on the
  operator's machine.
- [ ] **LLM backend swap** (`src/fapd/llm.py`): add an Anthropic-API
  backend behind the existing interface (the `claude` CLI binds runs to
  the local machine/subscription and cannot run hosted). Blocks any
  hosted scheduling; local scheduling does not need it.
- [ ] **Daily scheduling** with overlap guard (launchd/cron locally
  first; hosted later once the backend swap lands). Open since Phase 1.

### Community files
- [ ] `SECURITY.md` — contact route (hustleyourcity address), what's in
  scope (the pipeline; not .gov sites — include a pointer explaining we
  are not an authority for government-site issues).
- [ ] `CONTRIBUTING.md` — GUIDE-first rule (changes to GUIDE.md precede
  implementation), test expectations, register/lexicon rules for prose,
  how to propose a new source (five gates, adding-sources.md).
- [ ] `CITATION.cff` — cite the aggregation; reinforce citing official
  sources for claims.
- [ ] Decide on `CODE_OF_CONDUCT.md` (Contributor Covenant default).

### Flip-time edits (do these the same day the repo goes public)
- [ ] agents page + about page say "public repository" — currently false
  while private; verify true, or reword, at flip time.
- [ ] README "How this project is built" link check; site readme.html
  regeneration.
- [ ] Add repo URL to site footers / about page once public.
- [ ] Announce-facing check of SOURCES.md rendering (it is the public
  accountability artifact).

### Accuracy & freshness
- [ ] **Dated STATUS snapshot** (README section or STATUS.md,
  regenerated with the site): registry counts, active sources, test
  count, latest digest date — the single authoritative numbers block, so
  external AI readers stop averaging stale worklog figures (lesson from
  the NotebookLM briefing fact-check).
- [ ] Editorial spot-audit of a full digest against sources (GUIDE §2
  compliance read-through by the operator).
- [ ] Wayback top-up pass for the ~180 uncorroborated 07-28 captures
  (spread over later days' 100/day budgets; S3 re-check pass design).

### Source work that continues regardless (the standing pillar)
- [ ] Probe shortlist Tier A: federal-register-api (public inspection),
  congress-gov-api, DVIDS (needs key signup + media-policy GUIDE
  amendments: byte budget, video posture, caption/credit rules,
  asset_posture), FCC api2 re-probe (504 was possibly transient),
  BLS/ODNI feed-URL reads, USSC activation when its feed populates,
  GovDelivery-pattern probe (FDIC topic feed).
- [ ] **Blocked-source access program** (ranked plan in
  docs/access-alternatives-research-2026-07-29.md):
  1. Email-ingestion adapter over GovDelivery — GUIDE amendment (mailbox
     identity, DKIM verify-and-archive, teaser posture), project mailbox
     under the public identity, subscribe USTREAS/USSSA/USDOJDEA/USAFAA/
     HHS first. Broadest coverage per unit effort; DKIM signatures
     upgrade §7 provenance.
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

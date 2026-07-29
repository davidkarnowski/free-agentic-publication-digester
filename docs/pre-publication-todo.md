# Pre-publication TODO

The launch checklist: everything standing between the private repo and a
public repo + published site. Items marked **[decision]** need the
operator; the rest are build work. Companion analysis:
`docs/publication-readiness-2026-07-29.md`. Maintain this file as items
close (check them off with dates).

## Decisions (operator)

- [ ] **[decision] Code license.** MIT (maximally simple) vs Apache-2.0
  (adds an explicit patent grant and NOTICE conventions).
  Recommendation: **Apache-2.0** — the fork-this-for-your-government
  mission benefits from the patent grant and contribution clarity.
  Then: `LICENSE` file, `license` field + classifier in pyproject.
- [ ] **[decision] Content license for digests/site text.** CC0 (public
  domain dedication, zero friction) vs CC-BY 4.0 (requires attribution).
  Recommendation: **CC-BY 4.0** — attribution aligns exactly with the
  onward-citation ask we already make of agents. Then: site footer
  statement, llms.txt reuse note, README section, digest methodology
  footer line.
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
- [ ] First agency-engagement outreach: pick 2–3 `unavailable` cabinet
  newsrooms (Treasury, USDA, HHS) and write to their published web/API
  contacts describing the project and requesting a machine-readable
  channel; record outcomes in registry notes (GUIDE §3 continued-
  engagement rule).

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

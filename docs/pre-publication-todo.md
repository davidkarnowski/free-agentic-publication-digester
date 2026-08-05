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
  congress-gov-api, DVIDS (needs key signup + ~~media-policy GUIDE
  amendments: byte budget, video posture, caption/credit rules,
  asset_posture~~ **amendments landed 2026-08-05**: GUIDE §3
  "Multi-media publications" states the byte posture, the
  embed-don't-rehost rule, asset hashing, and the mechanical-selection
  requirement that DVIDS volume specifically motivated), FCC api2
  re-probe (504 was possibly transient),
  BLS/ODNI feed-URL reads, USSC activation when its feed populates,
  GovDelivery-pattern probe (FDIC topic feed).
- [ ] **Official-video transcripts** (research complete 2026-07-29:
  docs/youtube-transcripts-research-2026-07-29.md — YouTube captions
  are not legitimately reachable by non-owners and the scraper path
  fails the consent test, finally; the transcripts' authoritative homes
  are .gov pages): adopt the four GUIDE amendments (commercial-platform
  mirrors rule, Digital Registry verification, signal-class sources,
  ~~ASR ≠ official text~~ **landed 2026-08-05** — §2's derived-media
  bullet and §3's "Media transformation specifically" say it in the
  general form this item asked for: an official transcript always beats
  speech-to-text, and STT output is derived text that is marked, never
  quoted as the record; three amendments remain), then probe/register
  the GovTranscript pages
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
     **done 2026-07-29**; ~~mailbox + adapter build + first
     subscriptions~~ **done and in production 2026-07-30** (stale
     "Remaining:" line corrected 2026-08-02 — it described work that
     had already shipped): the project mailbox is live, `email_sources
     .py` implements the full contract (registry-driven allowlist,
     raw-RFC-5322 captures, DKIM verify-and-archive, multi-item
     GovDelivery parsing), and the collector's EmailWorker polls every
     15 minutes. Registry today: 30 `type: email` sources, **15
     active** (Treasury, IRS, SSA, DOJ/US Attorneys/DEA, USDA/FSIS,
     USCIS, FDA, CMS, VA, Federal Reserve, FDIC, USPS OIG), 15 planned.
     True remaining work: flip the 15 planned entries as subscription
     evidence arrives (gate-3 notes, docs/email-sources.md), and
     OB-10's IMAP IDLE if poll latency ever matters.
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

- [ ] **Agent-surface optimization package** (filed 2026-08-04 from an
  external-agent review + our own agentic test of 2026-08-03; set aside
  by the operator pending prioritization). Accepted, in build order:
  (a) **`primary_agency_id`** — a deterministic department/branch slug
  on every item in today.json/day.json (registry `parent_org` for
  agency/email classes, an FR agency-name→slug map, collection defaults
  `congress`/`judiciary`; unmapped = null, never guessed; mapping table
  published). (b) **JSON Feed** at `/feed.json` (jsonfeed.org 1.1, 20
  newest digests, record-surface rules apply). (c) **Published JSON
  Schemas** under `/schema/` for day/today/sources/digests JSON, with a
  drift test validating real rendered output against the published
  schema. (d) **`Cache-Control: immutable`** on `/day/*` (nginx block,
  deploy bundle) + llms.txt documenting that frozen day files never
  change — the honest answer to "trailing window" requests. (e) Revive
  **docs/agent-api-design.md** (`/api/v1/` sharded indexes +
  latest.json) as the umbrella for per-agency rollups and year-scale
  listing — now evidenced twice (3.7 MB day file measured 2026-08-03).
  Rejected on constitutional grounds, recorded so it stays decided:
  query-parameter filtering and any server-side compute (static flat
  files only; filesystem-clone complete), and a rolling multi-day item
  blob (re-ships unchanged history daily; immutable per-day files +
  caching strictly dominate).

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
- [ ] **Deep Digester — a second reading depth** (filed 2026-08-05,
  operator; **major site component**, not a feature). Extended,
  context-aware analysis of individual publications, with its own
  pipeline, its own site documentation page, and its own economics —
  announced publicly in the 2026-08-05 blog post, which commits us to
  the guardrail that reader funding changes analysis **depth only,
  never selection and never conclusions**, and that the end goal is
  covering every observed publication rather than only funded ones.
  Test documents chosen by the operator: GAO `gao-26-108403` and the
  USPS OIG white paper on postal applications of artificial
  intelligence — two different document classes on sources already in
  the registry. Deliverables: the pipeline; a worked demonstration on
  both documents publishing real token and wall-clock cost; a blog post
  carrying the demonstration; and a method page on the site carrying it
  too, so the documentation does not depend on the announcement.
  **Research first — this is not yet a plan.** The working document is
  in the operator's gitignored `research/` tree
  (`deep-digester-research-task.md`) and graduates to a plan-task doc
  per [docs/ops/plan-task-template.md](ops/plan-task-template.md) once
  the constitutional question is answered. That question, stated plainly
  because it gates everything else: GUIDE §2 bans motive attribution and
  predictions of political outcomes in generated prose, and "a reading
  of likely implications" is close to both. Three resolutions are
  drafted for the operator (implications confined to the document's own
  stated effects; permitted inside a labeled separate block; or a new
  register that is explicitly not the digest's voice). Also unresolved:
  GUIDE §6 rule 1 forbids whole PDFs reaching a model, which is in
  direct tension with "spares no token expense"; and the *mechanical*
  selection rule for unfunded deep runs, since "as many as the budget
  allows" is not yet party-blind or stateable. One practical constraint
  is already settled — gao.gov's 420-second crawl-delay prices each
  document fetch at seven minutes of wall clock, and the registry's
  2026-07-28 posture note already sanctions exactly this case
  ("targeted single fetches remain possible within the delay"), so no
  posture change is needed. GUIDE amendments precede implementation.
- [ ] **Redundant, provider-segmented inference** (filed 2026-08-05,
  operator). Stand up additional LLM providers beside Anthropic (Google
  and Cerebras named) so no single vendor's outage, rate limit, or
  refusal can stop a digest. GUIDE §6 rule 7's 2026-08-05 amendment
  governs: `backend` stays the provenance of who produced each output,
  failover is explicit and logged, and the §2 gates are provider-blind.
  The seam already exists and is cheap to extend — `LLMClient.__init__`
  takes a duck-typed `backend=` object (`.name` + `.complete`), tier
  resolution keys `config.LLM_MODELS` by backend name, and the ledger
  already writes `backend` on every row; a third provider needs a class,
  a `LLM_MODELS` sub-dict, and a branch. Two defects to fix while there,
  both of which get worse with three providers: the backend contract is
  informal (no Protocol/ABC, so a new implementation has nothing to
  check itself against), and the backend selection's `else` is a
  fallthrough, so an unrecognized `LLM_BACKEND` silently gets the CLI.
  Open policy question for the operator, not a code question: when
  failover fires, whether the digest discloses which provider answered,
  and how per-provider spend is bounded.
- [ ] **Blog post: "From the Human Side of the Dev Team"** (filed
  2026-08-05, operator — **hand-written by the operator, not
  model-generated**; the AI-development transparency policy in GUIDE §9
  makes the authorship of this particular post load-bearing). The blog
  surface already exists (`publish._build_blog`, `blog.html`), so this
  is content, not build. Four beats as specified: (a) the project as
  live AI-partnered development, with the GitHub repo as the visible
  evidence — the work log, the branches, the mistakes kept in place;
  (b) a personal message on public access to government publications —
  we watch; (c) the democratizing effect of open source: a forkable
  digester any citizenry can point at its own government's official
  record; (d) what "official" means here — these publications are the
  record the government chose to publish, nothing more and nothing
  other, and the project's whole discipline follows from taking that
  literally.
- [ ] **Research push: federal publications we do not yet ingest**
  (filed 2026-08-05, operator). A systematic sweep for official
  publication series outside the current registry, distinct from the
  Tier A probe shortlist above, which is a list of *known* candidates.
  Method is the established one: `docs/adding-sources.md` +
  `scripts/check_sources.py`, evidence before activation, gate-3
  content evaluation answering what fraction of a source we would
  actually see. Under-coverage is disclosed, not discovered later.
- [ ] **Research push: multi-media publications** (filed 2026-08-05,
  operator; GUIDE §3 "Multi-media publications" and the §2 derived-media
  bullet landed the same day and govern all three children). The class
  is admitted; this item is the build. Related work lives above and is
  not duplicated here: DVIDS sits in the Tier A probe shortlist, and
  official-transcript sourcing is the "Official-video transcripts" item.
  (a) **Audio bulletins** (USDA's radio service and peers). First
  question per source is whether an official transcript exists; where it
  does, this is ordinary text ingestion. Where it does not, STT is the
  fallback rung and its output is derived text under §2 — marked, never
  quoted as the agency's words, rendered with the transcription model
  and version. The operator's offline audio podcast downloader is the
  candidate STT path; evaluate it as a component rather than assuming
  it. (b) **Image feeds** (NASA image of the day the worked example).
  Ingest published caption and alt text first — that text is the record;
  generated captioning is a separate, labeled model surface for
  extended summarization. Display is by direct link or embed at the
  publisher's URL, never scrape-and-serve. Assets are hashed like
  extracted document text so a silently replaced image is detectable
  (§7). (c) **Video.** Capture any published transcript or caption file;
  model summarization runs over that transcript and, where justified,
  sampled frames — never a full media scrape. Embedding is
  source-dependent and gets decided per source, not globally. DVIDS is
  the major source and needs mechanical filtering *before* any model
  sees a transcript (§6 rule 4), or it is a token drain; GUIDE §3 states
  the bar: a media source that can only be filtered by asking a model
  what matters is not ready to ingest.
  Each child needs a plan-task document per `docs/ops/plan-task-template
  .md` before implementation — the work crosses Acquisition (adapter,
  registry, probe), Corpus (asset capture, hashing, schema), and
  Editorial (any ASR or vision surface).

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

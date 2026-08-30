# CLAUDE.md — agent working guide for FAPD

Project guide for Claude (or any AI agent) working in this repository.
Scope: enough context to navigate confidently and make safe changes.
Living document — update when architecture or conventions shift.

## 1. What this project is

The **Free Agentic Publication Digester (FAPD)** reads the official
publications of the US federal government — congressional proceedings,
bills, the Federal Register, enacted laws, court opinions, agency
releases (web and email) — and produces a daily, cited, opinion-agnostic
digest for people and AI agents. Selection is mechanical and party-blind;
every item cites the official record; a digest that fails validation is
not published, with no override. Full mission and editorial rules:
GUIDE.md §1–§2.

## 2. Governing documents & precedence

- **GUIDE.md** is the editorial constitution — mission, editorial gates,
  respectful-access policy, token economics, provenance. **Changes to it
  precede implementation** (§10). If this file and GUIDE.md ever appear
  to disagree, GUIDE.md wins and this file has a bug — fix this file.
- **WORKLOG.md** — timestamped session log, append-only, **never
  retroactively edited** (entries before 2026-07-28 use the old project
  name; that's deliberate).
- **docs/schema.md** — the design authority for the SQLite schema;
  `db.py` implements it, not the other way around.
- **docs/code-standards.md** — engineering rules (see §6).
- **docs/ops/** — operational runbooks and their authorization gates.
- **docs/pre-publication-todo.md** = launch checklist;
  **docs/ops/ops-backlog.md** = operational gaps. An item lives in
  exactly one.

## 3. Stack at a glance

| Thing | Choice |
|---|---|
| Language | Python ≥3.12, `uv`-managed, hatchling build |
| Deps | deliberately few: requests, python-dotenv, pyyaml, pypdf, pillow, markdown, protego, dkimpy, anthropic |
| Storage | SQLite ×3: `data/fapd.db` (pipeline), `data/fetch_log.db` (every HTTP attempt), `data/llm_ledger.db` (every LLM call) |
| Site | static HTML, no framework — `publish.py` renders it; exactly one script (the live page's local-time snippet, code-standards §2 r10) |
| Lint/tests | ruff (line 100), pytest (740+ tests; bare `pytest` collects `tests/` only via pyproject `testpaths` — the dev stack's staged repo copy would otherwise double-collect), CI on push/PR |
| LLM | pluggable backends: `claude` CLI (default; production again since 2026-08-24) / Anthropic API (`LLM_BACKEND=api`) / Google Gemini (`LLM_BACKEND=gemini`, `GOOGLE_GEMINI_API_KEY`; production 2026-08-15..24) / none (`LLM_BACKEND=none`, GUIDE §6 r15); tier aliases resolved per backend via `config.LLM_MODELS`; an unknown value is an error, not the CLI |

## 4. Repository layout

| Path | Role |
|---|---|
| `src/fapd/` | the library — fetch → extract → analyze → report → publish |
| `scripts/` | CLI entry points (plain modules; tests import them via conftest's sys.path insert) |
| `sources/registry.yaml` | the source universe; renders deterministically to SOURCES.md (drift-tested) |
| `digests/` | canonical daily digests (committed) |
| `site/` | derived static site (committed, regenerable) |
| `provenance/manifests/` | committed daily manifests, hash-chained day to day |
| `deploy/vps/` | the Docker stack running on the VPS (source of truth) |
| `docs/` | schema, research memos, ops runbooks, devnotes |
| `data/` | gitignored local state (DBs, raw archive, captures) |

## 5. Database model — read before editing SQL

- `data/fapd.db` is **WAL mode with 30s busy_timeout** — multi-process
  access is a design feature (collector + finalizer coexist). Honest
  current state: `fetch_log.db` sets busy_timeout but not WAL, and
  `llm_ledger.db` sets neither — aligning the two audit DBs is on the
  Corpus backlog; do not describe all three as WAL until it lands.
- `db.connect()` runs the full `_DDL` (`IF NOT EXISTS`) on every
  connect: schema additions are self-migrating; destructive changes are
  deliberate one-shot scripts, never startup DDL.
- **Request budgets are counted from the fetch log by the client
  itself** — nothing can bypass logging, and enforcement works across
  processes. Same pattern for the LLM ledger.
- Summary tables are keyed by `(package_id, granule_id, prompt_version)`
  — bumping a prompt version regenerates that layer only (GUIDE §6 r5).

## 6. Conventions

See **docs/code-standards.md** — the rules are descriptive of this
codebase first (seams inventory, DI-by-optional-parameter, deterministic
render, zero-LLM-where-SQL-works). Read it before any non-trivial code
change.

## 7. Common commands

```sh
uv run pytest -q                              # full suite
uv run ruff check src/ scripts/ tests/        # lint
uv run python scripts/run_pipeline.py         # full daily run (EOD finalizer)
uv run python scripts/run_pipeline.py --no-llm # same, mechanical only (GUIDE §6 r15)
uv run python scripts/digest.py --date D      # (re)render one digest (--no-llm: stored rows only)
uv run python scripts/collect.py --once       # one collector cycle (after B-workstream)
uv run python scripts/collect.py --finalize D # finalize day D now: marker + evidence push
                                              # (a bare run_pipeline.py records and pushes nothing)
uv run python scripts/audit.py                # our server footprint
uv run python scripts/sources_doc.py          # regenerate SOURCES.md after registry edits
deploy/dev/scripts/dev-seed.sh                # (operator-gated) pull VPS snapshots
deploy/dev/scripts/dev-up.sh                  # local prod-image render at localhost:8080
```

## 8. Branching & commits

- **main is sacred — for code** (GUIDE §10, verbatim): work on
  `feature/…`, `bug/…`, `arch/…`; CI green before fast-forward merge.
  **Enforced by a GitHub ruleset since 2026-08-27** (`main: CI green,
  no force-push, no deletion`, id 21668661): a push to `main` must carry
  a passing `test` check on its tip commit, force-pushes and deletion
  are refused for everyone including the owner, and the **only bypass
  is the `fapd-pipeline` deploy key** — the nightly evidence commit has
  no CI run before it pushes. Removing that bypass silently breaks the
  evidence push (the F-019/F-021 class); an emergency push without CI
  means editing the ruleset in Settings, not working around it.
  About to edit code on `main`? **STOP and confirm a branch name with
  the operator.** Check `git rev-parse --abbrev-ref HEAD` at task start.
- **Evidence exemption:** `digests/`, `provenance/`, `site/`,
  `SOURCES.md` from pipeline runs commit direct to main. Never mix
  evidence and code paths in one commit.
- Commits: `area: plain-English subject`, **narrative bodies** — the
  why, tradeoffs, what was verified. Future agents read the log to learn
  boundaries; a thin message wastes that signal. **Never amend, squash,
  or force-push to "tidy" recent work** — the messiness is the
  documentation. Trailer: `Co-Authored-By:` per GUIDE §9.
- Status tables and checklists update **in the same commit** as the work
  they describe. "Last reviewed" dates are load-bearing — date-only
  bumps without content review are forbidden.

## 9. Things that are intentional (don't "fix" without asking)

- **gao.gov's 420-second crawl-delay is honored exactly** — the answer
  to slowness is fewer requests (feed-only mode), never faster ones.
- **No daily LLM token cap is enforced yet** — GUIDE §6 rule 8 is
  measure-first; the ledger exists precisely to set the cap from data.
- **The analyze layer only ever works on the current publication day and
  the one before it** (GUIDE §6 r13). Older pending items are deliberate
  disclosure, not a backlog to drain — draining it is what starved the
  digest day on 2026-07-30.
- **Failed requests count against the request budget on purpose** — a 503
  cost the server a request. Do not "fix" the budget by excluding them.
- **Collectors see a smaller budget than the finalizer** (85%, GUIDE §4
  reserve). A client constructed `reserve_exempt=True` is the finalizer;
  nothing else should be.
- **The retry ceiling is per ITEM as well as per run** (GUIDE §6 r14,
  `MAX_ITEM_SUMMARY_ATTEMPTS`). The per-run ceiling alone resets every
  cycle and the collector runs analyze every 15 minutes per pending date,
  so an unsummarizable item was retried indefinitely — 1,345 single
  retries and 39.7M input tokens on 2026-07-31, 60% of the day. An item
  past the ceiling is a disclosed gap, not pending work.
- **Single-item LLM retries are the expensive path by design** — group
  retries first (`MAX_RETRY_BATCH_ITEMS`); the 2026-07-29 ledger showed
  25 single retries costing 645K input tokens (42% of the day).
- **`stage_email` swallows mailbox outages** — the disclosed-gap
  contract ("reported, not hidden"), pinned by tests.
- **USCOURTS syncs only a 7-day date_issued window** (USCOURTS-FETCH-01)
  — old-case lastModified churn is listed, skipped, and disclosed.
- **Publication days are on the publication clock, observation stamps
  are UTC** (GUIDE §3, amended 2026-07-30 and 2026-08-26). The clock is
  `config.PUBLICATION_TZ` (`FAPD_PUBLICATION_TZ`, Eastern in
  production) and `sync.publication_date()` is the single source of the
  day boundary — used by agency/email ingest, the `/today` renderer, the
  EOD target, and (since 2026-08-02) `scripts/digest.py::default_date()`,
  a call site the amendment missed: its UTC "today" made the in-progress
  day look complete for four hours every evening and published an Aug 1
  digest at 22:39 ET on Aug 1. Never date a document with
  `now[:10]`/UTC again, and never convert a stored observation stamp to
  the publication clock *for storage or for dating*: what is on the
  publication clock is the day a document belongs to. The one licensed
  conversion (2026-08-26) is **presentation bucketing** — a reader-facing
  graph or health window places stored UTC stamps into publication-clock
  days and hours, in Python via `sync.publication_day_hour()`, and says
  which clock it shows; a table or graph never mixes the two. Rendered
  prose never hard-codes "Eastern"/"ET"/"Washington" — the labels come
  from config (`PUBLICATION_TZ_LABEL`/`_ABBREV`/`_PLACE`), pinned by an
  audit test. When auditing this rule, enumerate ALL call sites —
  `report._claimed_day()` was the last known-wrong one, fixed
  2026-08-02 (review D1).
- **`collector_state.last_result` is a status line; durable facts get
  their own column** — `run_cycle` and its error path replace the JSON
  blob wholesale. When the EOD finalized marker lived there, a bare
  `{"ran": False}` erased it and the full pipeline re-ran every ~20
  minutes on 2026-08-01 (35 duplicate evidence commits); since
  2026-08-02 (review D5) the marker is the `finalized_date` column, the
  failing-finalizer hard stop is the `finalize_target`/`finalize_attempts`
  ladder, and nothing load-bearing reads `last_result`. Never route a
  new durable fact through it.
- **`evidence-commit.sh` fetches and rebases before it pushes, on
  purpose** — the backend's `.git` is an rsynced snapshot baked by
  `Dockerfile.backend`, so its `origin/main` ref freezes at deploy time
  and never moves. Every operator commit made *after* a deploy turns the
  nightly push into a non-fast-forward: F-019 recorded this on
  2026-08-05, was hand-fixed and left open, and it duly ate the
  2026-08-06 evidence commit. `--autostash` is equally load-bearing —
  `RenderWorker._refresh_health` rewrites `site/sources*.html` (and,
  since fc7ab66, `site/style.css`) on a clock, so the tree is reliably
  dirty. Do not "simplify" either away.
- **A failed evidence push is durable, loud, and retried on a bounded
  ladder** (`evidence_pushed_at` / `evidence_push_error` /
  `evidence_push_attempts`). **The digest being live is NOT evidence
  that it was published to the repository** — two gates, failing
  separately. `_record_finalized` is deliberately unconditional on push
  success: the day IS finalized, and re-finalizing would re-render and
  re-spend tokens for a day already paid for.
- **`/app/digests` and `/app/provenance` are volumes; `/app/.git` is
  not** — the asymmetry is the design. Once the files are durable a lost
  `.git` is survivable: the next evidence commit re-stages the
  survivors. Disclosed cost (OB-19): a volume seeds from the image only
  when empty, so a *retired* digest must be deleted from the volume
  explicitly — the F-009 class.
- **`scripts/digest.py` imports the analysis layer lazily** — report-only
  runs must work even if analysis modules break.
- **`LLMClient._ensure_backend_column`** does an in-place ALTER — the
  deliberate micro-migration pattern for additive ledger changes.
- **An undated index entry is DROPPED, never observation-dated** — the
  inverse of the feed rule, deliberately. GUIDE §3 lets a feed item with
  no parseable date fall back to the observed date because a feed carries
  what was just published; a listing page carries months of entries, so
  the same fallback would file dozens of old releases as today's news and
  `AGENCYPR-EX-01` could not catch them (their claimed day would equal the
  digest day). `HtmlIndexAdapter` logs the drop count on every poll; a
  source that mostly drops is a source that should not be active.
- **`HtmlIndexAdapter.wants_article()` is False on budget grounds, not
  access grounds** — a listing carries everything section 6 renders
  (title, URL, agency-stated date), so an article fetch would multiply the
  agency class's request count by the item count for text nothing reads.
  Four sources cost four requests per poll.
- **Index adapters bound their own lookback** (`config.INDEX_LOOKBACK_DAYS`).
  `SourceAdapter.items()` is the enumeration seam; a feed is bounded by its
  publisher but an index is not — the Senate vote menu lists every vote of
  the Congress. An unbounded `items()` is a request-budget bomb on first
  activation, not a completeness win: the §3 dating rule excludes the tail
  as backfill anyway.
- **Bill actions are dated by the publisher, agency releases are not**
  (`SourceAdapter.DATED_BY_PUBLISHER`, GUIDE §3). Congress.gov publishes
  a day's bill actions the *following* morning — measured 2026-07-31: 97
  actions dated 07-30 on the page, zero dated 07-31 — so `BILLACTIONS`
  rows are filed under their `actionDate` like every govinfo collection,
  which is why a re-render of an earlier day gains items. Dating them by
  observation, the way the §3 agency dating rule dates newsroom
  releases, makes section 8 permanently empty. Do not "unify" the two.
  *(2026-08-06: BILLS-the-collection now files by observation day — the
  §3 amendment; BILLACTIONS section 8, fed by the Congress.gov API's
  own actionDate record, is unchanged.)*
- **Digest filing for govinfo collections is by observation day**
  (`packages.digest_day`, GUIDE §3 amended 2026-08-06): CREC, BILLS,
  USCOURTS, PLAW file under the Eastern day our collector first
  observed them; FR and AGENCYPR file by their own date
  (`config.FILING_POLICY`). `date_issued` remains the document's own
  date for display and the USCOURTS fetch window — do not "simplify"
  filing queries back onto it, and never update `digest_day` after
  first sight (write-once; a revision re-fetch must not re-file).
- **The registry keeps `unavailable` entries forever** — a refusal is
  accountability data; a success elsewhere never erases it.
- **Empty-state digest sections render on purpose** (e.g. PLAW's "No
  laws were published") — disclosure, not a bug.
- **A day finalizes without any inference provider** (GUIDE §6 r15,
  2026-08-24). `LLM_BACKEND=none` is a configuration, not an error; a
  provider that is disabled, unauthenticated, or out of quota trips the
  client's per-run breaker and every model layer records `skipped`/
  `failed` in `day_inference`; the render proceeds on stored rows and
  the gates decide. The digest's **Inference** row says only that no
  inference was available and that content is source-derived or
  mechanically constructed — **never the cause** (operator ruling):
  causes go to the manifest, the insight report, and the logs. Do not
  "improve" the disclosure with error text, and do not make an
  `LLMError` fatal to the finalizer again — that is what left ten days
  unpushed in August 2026.

## 10. Things that look intentional but are bugs

Add entries here **instead of fixing silently**; each carries a
confirm-gate.

- `compose_day`/`compose_sections` staleness checks compare timestamps
  via `substr(...,1,19)` prefix — correct across current writers' formats
  (`Z` vs `+00:00` suffixes), but a new writer using a different format
  would silently break invalidation. **Confirm with the operator before
  changing any stored-timestamp format.**

## 11. Section agents

The system is segmented into five sections with explicit boundaries so
work can be split across focused agents; `docs/agents/README.md` is the
router and `docs/agents/orchestration.md` governs dispatch (verbatim
prompt template, file-ownership matrix, shared-resource rules, and the
one structural rule: **section agents stage and report; only the
orchestrator commits**).

| Section | Instructions | Launch for |
|---|---|---|
| Acquisition | `docs/agents/acquisition.md` | Sources, adapters, clients, sync, email, registry |
| Corpus & Provenance | `docs/agents/corpus.md` | Schema, extraction, parsers, captures, manifests |
| Editorial | `docs/agents/editorial.md` | Rules, model layers, prompts, token economics |
| Publication | `docs/agents/publication.md` | Digest render, validation gates, the site, /today |
| Operations | `docs/agents/operations.md` | Supervisor/workers, health, pipeline, VPS stack |

Before section work — delegated or done in the main session — load the
section file; it carries the area's philosophy, its CLAUDE.md §9 subset,
its review backlog, and its grep-able audits. Thin launcher definitions
live in `.claude/agents/fapd-*.md` (tracked).

## 12. Where to look first

| Task | Files |
|---|---|
| Politeness, pacing, budgets | `src/fapd/client.py`, `config.py` (constants are policy — GUIDE §4) |
| Add/probe a source | `docs/adding-sources.md`, `sources/registry.yaml`, `scripts/check_sources.py` |
| Selection/exclusion rules | `src/fapd/rules.py` (registry order = precedence) |
| Prompts / model layers | `analyze.py`, `compose.py`, `tags.py`, `insight.py` — GUIDE §3a governs changes |
| Daily ops feedback loop | `src/fapd/insight.py` → `provenance/runs/insight-<date>.md` (OB-2) |
| Digest layout & validation gates | `src/fapd/report.py` |
| Site & agent surfaces | `src/fapd/publish.py` (+ `fedcal.py` for the weekend/holiday banner) |
| Provenance / hashes | `src/fapd/provenance.py`, `PROVENANCE.md` |
| No-inference floor / layer outcomes | `src/fapd/finalize.py`, `inference.py` (`day_inference`), the digest's Inference row in `report.py` |
| Narration (TTS, gated off) | `src/fapd/tts.py`; called from `compose.py` only with `OPENAI_API_KEY`; players rendered by `publish.py` — GUIDE §3a narration note |
| Email ingestion | `src/fapd/email_sources.py`, `docs/email-sources.md` |
| Continuous ingestion | `src/fapd/collect.py`, `docs/continuous-ingestion.md` |
| VPS / deploy | `deploy/vps/README.md`, `docs/ops/` |
| Local pre-deploy testing | `deploy/dev/README.md` (prod image + VPS data seed) |
| VPS access (read-only checks) | `deploy/vps/scripts/vps-ssh.sh` + gitignored `deploy/vps/deploy.env` |
| Section-agent instructions | `docs/agents/` (§11) |
| Forking: the publication clock and the working calendar | `docs/forking.md` → `config.py` (`FAPD_PUBLICATION_TZ` + labels), `fedcal.py` |

## 13. Posture

- **Repo is PUBLIC (since 2026-07-30)** and the site is live; write
  accordingly (GUIDE §9) — no personal paths, no secrets, dossier facts
  about the shared VPS live in the operator's private tree, not here.
  A repository this public documents itself: prose that overclaims what
  the code does is a defect (see the 2026-08-02 doc audit).
- **Never propose raising request budgets, loosening validation gates,
  or evading an access refusal to fix a symptom** — these are GUIDE
  changes, made by the operator, or they don't happen.
- **VPS authorization gate:** only deploy to or act on the VPS when the
  operator explicitly asks in the current session ("deploy", "push to
  the VPS", or by naming the script). Never inferred from a generic
  "looks good" or a previous deploy. Local edits and local commits are
  not gated — only the VPS side is.
- Plans that touch production or governing docs follow
  `docs/ops/plan-task-template.md`.

## 14. Decision log (append-only, dated)

- **2026-07-30** — Domain `fapd.info`; full-name branding rule (always
  expand "Free Agentic Publication Digester").
- **2026-07-30** — VPS runtime over GH-native (superseded before its
  evaluation ran; branch preserved as evidence). Same day: hosting
  resolved onto the shared VPS as a segmented Docker stack; placeholder
  live over HTTPS.
- **2026-07-30** — Anthropic-API LLM backend built beside the CLI;
  tier→model mapping env-overridable.
- **2026-07-30** — Email sources activate on evidence only: 7 flipped
  with gate-3 notes; 23 stay planned with dated open-window notes.
- **2026-07-30** — main-is-sacred branching + evidence exemption;
  agent-ops standards adopted from the operator's sibling projects.
- **2026-07-31** — `api` adapter shipped against Congress.gov's `bill`
  endpoint (not the Federal Register: the operator ruled
  public-inspection documents out of scope, and govinfo already supplies
  published FR). New `BILLACTIONS` collection, digest §8, publisher
  dating, one request per poll, key redacted in `HttpClient`.
- **2026-07-30** — Continuous ingestion: single supervisor daemon,
  fully-continuous mechanical layers, batched model layers, EOD-only
  compose; `/today` derived-only, canonical digest frozen at EOD.
- **2026-08-02** — EOD three-clock fix (Eastern default_date, durable
  finalized marker, explicit --date) deployed; premature 08-01 digest
  superseded itself. Same day: /today overhaul + `fedcal.py`
  weekend/holiday banner; local dev stack (`deploy/dev/`) seeding from
  VPS `VACUUM INTO` snapshots.
- **2026-08-02** — GUIDE amendments ratifying measured behavior
  (operator-authorized, from the doc audit): §3 index-drop carve-out,
  §4 backpressure scope, §5 live-page mechanical-editorial license
  (fedcal governed), §6 r8 baseline-arrived note, r14 per-item ceiling,
  §7 chain honest scope, §3 collections status note.
- **2026-08-02** — System segmented into five sections with tracked
  agent instruction files (`docs/agents/`, launchers in
  `.claude/agents/`), per the Spiralyst pattern: explicit edit
  surfaces, orchestrator-owned shared files, agents stage but never
  commit. Drift-tested against the repo.
- **2026-08-02** — **No daily LLM token cap** (operator, superseding
  the OB-4/R1 cap-value question): build throttle-on-demand instead —
  the cap mechanism behind an env knob, unset by default; engaging it
  is an ops action, not policy. GUIDE §6 r8's "the value stays the
  operator's" includes the value "none".
- **2026-08-02** — **Lexicon official-name exemption, option (a)**
  (operator): the banned lexicon binds only the digest's own prose;
  official text is never gated, altered, or suppressed ("we aren't
  censoring, we are trying not to be biased in what we publish and
  summarize"), and generated prose may carry a banned term only inside
  an exact occurrence of an official title/name stored for that day.
  GUIDE §2 amended; gate enforcement made positional.
- **2026-08-03** — **Source-pages plan shipped and deployed** (GUIDE
  §3a source surfaces + §5 frozen-day-view amendments): per-source
  pages for every registry entry with two new model layers
  (descriptions/assessments, storage-time lexicon gate), probe-labeled
  fetch statistics at 24h/14d/all-time windows, inline-SVG charts;
  frozen day views `/day/<date>` built at EOD (pipeline stage 4b) and
  backfilled once from the journal with disclosed reconstruction;
  digest headers carry the fedcal calendar note and the day-view link.
  Operator feedback same day: sources.html titles link OUR per-source
  pages (official site demoted to a small link), health precedes
  statistics on source pages.
- **2026-08-03** — **The official record begins 2026-07-27** (operator):
  the 2026-07-23/24 development-era digests retired from the tree —
  history keeps them, manifests untouched. The day-view backfill floors
  at the record start. Ops lesson the same evening: `build_site` never
  deletes stale outputs, so a retirement must also clean the VPS site
  volume or the next evidence commit's `git add site/` resurrects the
  pages (happened, caught, cleaned; runbook item on the ops backlog).
- **2026-08-03** — **Published request statistics begin 2026-07-30**
  (operator; `publish.ALL_TIME_STATS_SINCE`): the production cutover.
  Earlier fetch-log rows are the development machine's migrated
  traffic, excluded from all-time figures and the per-source request
  charts, with the floor disclosed beside the numbers. Item counts are
  the corpus record and are not floored.
- **2026-08-05/06** — GUIDE amendments: §5 frozen-day supersession
  (operator; superseded for the CREC case one day later, retained for
  genuine corrections), §2/§3 derived-media-is-never-the-record + the
  multi-media class, §6 r7 provider redundancy (backend column is
  provenance, failover explicit, gates provider-blind).
- **2026-08-06** — **Observation-day filing** (operator): govinfo
  collections file under the Eastern day of FIRST OBSERVATION
  (`packages.digest_day`, write-once) — the three clocks doctrine
  (Action / Publication / Observation; observation is the only
  timestamp we define precisely and is the filing source of truth; a
  source outage cannot drop a document under it). FR keeps cover-date
  (posts early — measured); AGENCYPR keeps the agency dating rule.
  Forward-only cutover with digest 2026-08-06; the two pre-cutover
  Record issues stay out of the canonical digests, disclosed. Root
  cause this resolves, data-verified: every auto-frozen digest had an
  empty §1 while fully-paid-for CREC summaries sat unpublished
  (F-013).
- **2026-08-07** — **The evidence push is a gate of its own** (F-019
  recurrence + F-021). A digest that renders, validates and serves is not
  thereby published: the 2026-08-06 commit was rejected as a
  non-fast-forward and the only trace was `last_result`, so the `eod` row
  read a clean success while the repository sat a day behind the live
  site — thirteen hours, unnoticed. Fixed in four parts: fetch-and-rebase
  in `evidence-commit.sh`, durable state with a bounded retry, `digests/`
  + `provenance/` as volumes (the writable layer was one
  `docker compose build` away from destroying the day), and the check
  written into OPS-GUIDE and `/fapd-health`. Standing lesson: **a
  known-open high finding with a hand-fix and no durable alarm is a
  scheduled recurrence.** Same day: box coordinates moved into the
  project as a gitignored `deploy/vps/deploy.env` behind
  `tests/test_deploy_secrets.py`, so the VPS half of the health check
  runs from this repo instead of a sibling tree; `/today`'s model
  summaries are signed **FAPD-AI** (operator), with both labels explained
  in the page's own prose so the label stays a disclosure and not just
  branding; and CREC listings got their titles back (F-022).
- **2026-08-09** — **Lexicon-gate failures get a corrective rewrite, not
  a blind rerun** (GUIDE §6 rule 5 amended, new rule 14a; operator).
  Incident: the 2026-08-08 EOD finalizer halted after three identical
  failures — a CREC summary's "extreme cold weather" tripped
  `_validate_lexicon`, and because rule 5 makes a stored summary
  permanent, every rerun hit the same cached row and failed the same
  way every time; the ladder could never have succeeded on its own. Fix:
  an attributable per-item lexicon failure now gets up to
  `MAX_LEXICON_CORRECTION_ATTEMPTS` (2) error-informed, self-gated
  corrective regenerations before falling back to today's behavior; past
  the ceiling the row is withdrawn (never left blocking the day), same
  disclosed-gap bucket editorial.md's "never fabricate" rule already
  uses. Scoped to CREC/BILLS/FR/PLAW/USCOURTS/PRESACT map+plain layers
  only — compose-level prose (Day in Review, section synopses) has no
  item identity to correct against and is unaffected. Same change:
  PRESACT's section 9 now renders the stored summary and plain-language
  line (previously title-only despite paying full LLM cost to generate
  them — a pre-existing waste bug, fixed alongside since it's what
  brought PRESACT into the correction surface in the first place).
- **2026-08-10** — **`sync.py` gets the retry ceiling the LLM and
  finalizer layers already had** (GUIDE §4 amended; operator). Six
  consecutive daily insight reports (2026-08-04 through 2026-08-09)
  flagged a chronic 22-26% govinfo error rate — well above the 18.1%
  baseline the 2026-07-31 amendment already accepted and ruled on — and
  none of them got acted on. Root cause, found by reading `sync.py`
  directly rather than the reports: `_download_pending()` had no
  cross-cycle retry ceiling at all. A failed package re-entered the same
  `pending`/`failed` query every ~30-minute cycle forever, and the
  `date_issued DESC` sort put a permanently-stuck recent package at the
  front of the queue every time — the identical bug shape already fixed
  twice elsewhere (`MAX_ITEM_SUMMARY_ATTEMPTS`, the EOD finalizer
  ladder), never generalized to sync. Fix:
  `config.MAX_PACKAGE_FETCH_ATTEMPTS` (48, ~24h of cycles) before a package is
  marked `fetch_status='exhausted'` — a new terminal status, distinct
  from `'skipped'` (deliberate non-fetch) and `'unavailable'` (a
  different, source-registry-level concept) — and stops re-entering the
  queue; a later content revision resets the ceiling. Required this
  project's first CHECK-constraint-widening migration
  (`scripts/migrate_widen_fetch_status.py`) since `_ensure_columns` is
  additive-only. Does not touch the daily cap, hourly ceiling, per-call
  attempt count, or backoff — reduces total request volume over time,
  same direction as the standing "fewer requests, never faster retries"
  rule. `scripts/audit.py` gained a repeat-failure report so the fix's
  effect is actually measurable, which is what the tooling was missing
  the whole six days this sat unactioned.
- **2026-08-15** — *(recorded 2026-08-24)* Production LLM backend moved
  from the `claude` CLI to **Google Gemini** (`LLM_BACKEND=gemini`, free
  tier) after the vendor disabled subscription access for the CLI on
  2026-08-14 23:08 UTC. The switch was made by staged script with no
  GUIDE/CLAUDE.md trace; the free tier's ~20-request daily quota then
  starved the 04:00 UTC finalizer on eight of ten nights.
- **2026-08-24** — **The mechanical digest is the floor** (operator;
  GUIDE §6 r15): every day finalizes with or without inference; the
  published digest states only that no inference was available and
  that content is source-derived or mechanically constructed — no
  causes; no prose backfill into frozen days; the continuous analyze
  layer stops touching a finalized day. Same day: production returned
  to the CLI backend at 22:28 UTC after the block lifted
  (`scripts/staged/2026-08-24-restore-cli-backend.sh`); the Gemini key
  stays configured for a future explicit failover (parked).
- **2026-08-26** — **The publication clock is one knob, and it is the
  clock of presentation** (operator). Eastern is the project's main
  clock for every timing question because it is the federal publishers'
  schedule; a fork for a state or another country must change it in one
  place. Ruled: `config.PUBLICATION_TZ` (`FAPD_PUBLICATION_TZ`) plus its
  labels own the clock, no rendered string hard-codes it, and
  `fedcal.py` is the second, documented swap point (docs/forking.md).
  Same ruling: the source cards' activity graphs bucketed request
  stamps by UTC day and hour (and item stamps by publication day but
  UTC hour) — unlabeled, and lining up with no digest day. GUIDE §3/§5
  amended first: storage and dating unchanged (UTC stamps,
  publication-day filing); *presentation* of activity over time buckets
  on the publication clock in Python and labels the clock; DST nights
  are disclosed by the day's hour count, never normalized.
- **2026-08-30** — **The lexicon exemption is phrase-scoped, not
  whole-string-scoped** (GUIDE §2 amended, operator). Two bills renaming
  "National Historic..." sites were withdrawn 2026-08-28/29 because the
  prior rule required a byte-identical copy of an entire official title/
  summary/sentence to exempt a banned word inside it; the model quoting
  the same name in different wording earned nothing. Now the exemption
  is: the exact phrase the render uses at that hit — term plus at least
  one adjacent content word, never a bare stopword alone, capped at a
  sentence boundary — occurs verbatim somewhere in that day's published
  corpus, which now includes `extracted_texts.text` (the document body,
  not just titles). Model output — ours, on any item — stays excluded
  from the corpus; only text the digest did not write can license a
  banned word in text it did write. `find_lexicon_violation` builds the
  corpus once per call, not once per item, after a synthetic stress test
  measured the naive per-item shape at over a second per call.

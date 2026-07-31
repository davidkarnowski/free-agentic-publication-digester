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
| Site | static HTML, no JS, no framework — `publish.py` renders it |
| Lint/tests | ruff (line 100), pytest (295+ tests), CI on push/PR |
| LLM | pluggable backends: `claude` CLI (local default) / Anthropic API (`LLM_BACKEND=api`); tier aliases resolved per backend via `config.LLM_MODELS` |

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

- All three DBs are **WAL mode with 30s busy_timeout** — multi-process
  access is a design feature (collector + finalizer coexist).
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
uv run python scripts/digest.py --date D      # (re)render one digest
uv run python scripts/collect.py --once       # one collector cycle (after B-workstream)
uv run python scripts/audit.py                # our server footprint
uv run python scripts/sources_doc.py          # regenerate SOURCES.md after registry edits
```

## 8. Branching & commits

- **main is sacred — for code** (GUIDE §10, verbatim): work on
  `feature/…`, `bug/…`, `arch/…`; CI green before fast-forward merge.
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
- **Single-item LLM retries are the expensive path by design** — group
  retries first (`MAX_RETRY_BATCH_ITEMS`); the 2026-07-29 ledger showed
  25 single retries costing 645K input tokens (42% of the day).
- **`stage_email` swallows mailbox outages** — the disclosed-gap
  contract ("reported, not hidden"), pinned by tests.
- **USCOURTS syncs only a 7-day date_issued window** (USCOURTS-FETCH-01)
  — old-case lastModified churn is listed, skipped, and disclosed.
- **Publication days are Eastern, observation stamps are UTC** (GUIDE
  §3, amended 2026-07-30). `sync.publication_date()` is the single
  source of that boundary — used by agency/email ingest, the `/today`
  renderer, and the EOD target. Never date a document with
  `now[:10]`/UTC again, and never convert a stored observation stamp to
  Eastern: what is Eastern is the day a document belongs to.
- **`scripts/digest.py` imports the analysis layer lazily** — report-only
  runs must work even if analysis modules break.
- **`LLMClient._ensure_backend_column`** does an in-place ALTER — the
  deliberate micro-migration pattern for additive ledger changes.
- **The registry keeps `unavailable` entries forever** — a refusal is
  accountability data; a success elsewhere never erases it.
- **Empty-state digest sections render on purpose** (e.g. PLAW's "No
  laws were published") — disclosure, not a bug.

## 10. Things that look intentional but are bugs

Add entries here **instead of fixing silently**; each carries a
confirm-gate.

- `compose_day`/`compose_sections` staleness checks compare timestamps
  via `substr(...,1,19)` prefix — correct across current writers' formats
  (`Z` vs `+00:00` suffixes), but a new writer using a different format
  would silently break invalidation. **Confirm with the operator before
  changing any stored-timestamp format.**

## 11. Where to look first

| Task | Files |
|---|---|
| Politeness, pacing, budgets | `src/fapd/client.py`, `config.py` (constants are policy — GUIDE §4) |
| Add/probe a source | `docs/adding-sources.md`, `sources/registry.yaml`, `scripts/check_sources.py` |
| Selection/exclusion rules | `src/fapd/rules.py` (registry order = precedence) |
| Prompts / model layers | `analyze.py`, `compose.py`, `tags.py`, `insight.py` — GUIDE §3a governs changes |
| Daily ops feedback loop | `src/fapd/insight.py` → `provenance/runs/insight-<date>.md` (OB-2) |
| Digest layout & validation gates | `src/fapd/report.py` |
| Site & agent surfaces | `src/fapd/publish.py` |
| Provenance / hashes | `src/fapd/provenance.py`, `PROVENANCE.md` |
| Email ingestion | `src/fapd/email_sources.py`, `docs/email-sources.md` |
| Continuous ingestion | `src/fapd/collect.py`, `docs/continuous-ingestion.md` |
| VPS / deploy | `deploy/vps/README.md`, `docs/ops/` |

## 12. Posture

- **Repo is private until the launch checklist gates clear**
  (docs/pre-publication-todo.md); everything is written as if already
  public (GUIDE §9) — no personal paths, no secrets, dossier facts about
  the shared VPS live in the operator's private tree, not here.
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

## 13. Decision log (append-only, dated)

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
- **2026-07-30** — Continuous ingestion: single supervisor daemon,
  fully-continuous mechanical layers, batched model layers, EOD-only
  compose; `/today` derived-only, canonical digest frozen at EOD.

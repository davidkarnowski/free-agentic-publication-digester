# Continuous ingestion — design and operating spec

*Adopted 2026-07-30 (GUIDE §3/§4/§5/§6 amendments of the same date).
This document is the authority for the collector architecture; the
next-push designs (§8–§10) are complete here so those builds need no
re-design. Last reviewed: 2026-08-02 (doc audit; §3/§5/§8/§9 corrected to code truth).*

## §1 Why

Sources publish at varied times; a single daily run both delays
ingestion and concentrates load. Slow sources are the clearest case:
gao.gov's 420-second crawl-delay serialized a daily stage until
per-host concurrency fixed it — the same logic extended in time says
that host should collect in the background on its own clock all day.
Email bulletins arrive when agencies send them. The site should present
the in-progress day honestly (preliminary, timestamped) and freeze a
canonical digest at end of day.

## §2 Architecture: one supervisor, not many units

**`fapd-collect`** — one supervising process (`scripts/collect.py`
driving `src/fapd/collect.py`) with per-source-class worker threads:

- It is the existing `run_concurrent` shape extended in time: per-host
  workers, each with its own pacing clock; budgets global via the fetch
  log (read-before-request, cross-process safe).
- One process = one coordinated manifest writer, one health surface
  (`collector_state`), one container later.
- The "one polite, identified crawler" identity (GUIDE §1) argues for
  one process shape too.

**Considered and rejected:** one scheduler unit per source class. It
buys isolation the per-worker crash containment already provides, at
the price of N schedulers, cross-process manifest export races, and N
things to health-check.

## §3 Reuse — collectors call existing functions only

| Worker | Calls | Why it's already incremental |
|---|---|---|
| GovinfoWorker | `sync.sync_collection(client, conn, c, max_downloads=50)` then `extract.run(conn)` | watermark delta; extract staleness-keyed |
| AgencyHostWorker (one per `host_groups()` key) | `agencies._poll_isolated(...)` per entry (the crash-isolating wrapper around `poll_source`) | `feed_state` conditional GETs → 304s |
| EmailWorker | `email_sources.poll_mailbox(mbox, conn, entries)` (registry filtered to configured email senders; short-circuits when IMAP is unconfigured) | `mailbox_state` UID watermark |
| AnalyzeWorker | `analyze.run` / `analyze.run_plain` on trigger — dates bounded to `ANALYZE_MAX_AGE_DAYS` (§6 r13) and items past `MAX_ITEM_SUMMARY_ATTEMPTS` excluded (r14) | keyed by `(package, granule, prompt_version)` |
| RenderWorker (§8) | `publish.build_today` on journal-watermark movement (5-min clock); `publish.refresh_sources` on its own 15-min clock | zero tokens, zero requests |
| EODWorker (§9; only with `--eod`) | `run_pipeline.py --date <target>` as a subprocess, then the evidence commit when enabled | once per closed publication day, durable `finalized` marker |

**Journaling is reconciliation, not instrumentation:** after each
cycle the worker inserts `item_journal` rows for items present in the
source tables but absent from the journal (`WHERE NOT EXISTS`), with
`observed_at` = best available per class (`extracted_at`,
`documents.first_seen_at`, else journaling time). Zero changes to the
collection functions; the EOD finalizer's late items get journaled the
same way. Fidelity is cycle-granularity and disclosed; dating rules
(GUIDE §3) key on claimed/issued dates, not observation minutes.

## §4 The token trade — "fully continuous" by layer (GUIDE §6 r12)

- **Mechanical layers: truly continuous.** Item listing, official
  summaries, counts, and (at OB-8) the `/today` render update on every
  arrival — `report.render` is deterministic and zero-LLM, so this
  costs CPU only.
- **Map/plain layers: batched triggers.** Map fires for a date when
  `pending_selected ≥ MAX_BATCH_ITEMS (6)` **or** oldest pending age ≥
  `ANALYZE_MAX_LATENCY_MIN (60)`, spaced ≥ `ANALYZE_MIN_INTERVAL_MIN
  (15)`; plain runs in the same cycle after map (threshold 25 or the
  same age bound). Rationale is measured: single-item calls re-pay a
  fixed prompt overhead (the 2026-07-29 ledger's 42%-of-day lesson).
- **Compose: EOD-only, enforced structurally** — `collect.py` contains
  no compose call. Its staleness rule would recompose on nearly every
  batch, and the Day in Review describes a completed day.
- `--no-llm` runs the collector mechanical-only (items land with
  official data; the finalizer pays all model costs) — the degraded but
  valid mode, and the test mode.

## §5 Budget-aware pacing (GUIDE §4 amended, invariants unchanged)

Same clients, same per-request politeness, same logging. Cadences:
govinfo ~30 min (`GOVINFO_POLL_INTERVAL_MIN`), agency hosts ~60 min
(`AGENCY_POLL_INTERVAL_MIN`), mailbox ~15 min
(`EMAIL_POLL_INTERVAL_MIN`), /today render check ~5 min
(`TODAY_RENDER_INTERVAL_MIN`), source health ~15 min
(`SOURCE_HEALTH_REFRESH_MIN`), EOD check every 10 min (hard-coded
default in `_build_workers`), all jittered. **Backpressure:** past 70%
of the AGENCY class's daily budget its host workers double their
interval for the rest of the UTC day — the other classes reserve EOD
headroom via the 15% finalizer reserve instead; extending backpressure
beyond the agency class is an open GUIDE §4 alignment item. Manifest:
the current day's `export_manifest` re-runs after any agency cycle
that produced NEW items (a cycle of only 304s/unchanged captures
reaches the committed manifest at the next new-item cycle or EOD).
Known limit, review D11: the export is truncate-then-write and host
workers run concurrently — single-owner/atomic export is queued.

## §6 State (schema authority: docs/schema.md)

- **`item_journal`** — arrival journal: `observed_at`, `source_class`
  (govinfo|agency|email), package/granule, `digest_date`, `event`
  (ingested|summarized|plain), `cycle_id`;
  `UNIQUE(package_id, granule_id, event)`.
- **`collector_state`** — per-worker liveness: `last_cycle_at`,
  `last_ok_at`, `last_result` (JSON), `consecutive_errors`.
- **`item_tags`** — tagging lands schema-first (build is OB-9): tags
  attach to **items** (same key as everything), `tag_kind`
  (branch|agency|discovery), `method` (mechanical|llm),
  `prompt_version` for the LLM kind. Renderers join per item and
  aggregate to section level; the journal's `observed_at` timestamps
  section updates, so tags need no time dimension.

Migration = `db.connect()`'s `IF NOT EXISTS` DDL on first post-merge
connect (additive; the busy_timeout covers the brief lock).

## §7 EOD handoff

`run_pipeline.py` stays the finalizer, unchanged in role: final delta
sweep, remaining summaries (mostly no-ops — collectors already paid),
compose (the day's one substantial EOD token cost), render through the
validation gates, site build, final manifest, evidence commit (bot
identity, direct to main per the exemption). Coexistence with the
collector is *safe* (WAL + shared budget counting) but serialized
anyway: the supervisor pauses collector workers during finalization
(§9) to avoid duplicate sweeps in the same hour.

---

## §8 `/today` renderer (OB-8 — built 2026-07-30)

`publish.build_today(conn)` consuming exactly
`collect.today_status(conn, date)` → `site/today.html` + `today.json`:

- Data contract: mechanical counts + per-item rows (title, source,
  citation, official/model summary if present, `observed_at`), one
  chronological stream with ET hour headings (2026-08-02) — not digest
  sections; `pending_llm` shown as "N items awaiting model summary."
- The §3 dating rule applied live: items the publisher dates on another
  day split out as backfill (shared helper with report.py), counted and
  disclosed, never listed as today's news (2026-07-31 incident).
- A weekend/federal-holiday notice (`fedcal.reduced_publishing`,
  2026-08-02) on the page and as `day_context` in today.json; openings
  gated by a mechanical prose check so scraped nav chrome never renders.
- Mandatory disclosure header (GUIDE §5 wording) + "Last updated" in
  ET with the reader's local time appended by the site's one script.
- No Day-in-Review, no section synopses — labeled "composed at end of
  day."
- The RenderWorker is an independent worker on a ~5-minute clock: it
  rebuilds when the journal watermark moved (or today.html is missing)
  and separately refreshes source health on a 15-minute clock —
  clock-driven on purpose, because a failing source journals nothing.
  Never committed; excluded from the Atom feed; `llms.txt`/`robots.txt`
  carry a `/today` pointer labeled preliminary. Section tags render as
  day-so-far chips.

## §9 Backend container (OB-1 — LIVE since 2026-07-30)

- `deploy/vps/Dockerfile.backend`: `python:3.12-slim` + uv + git; repo
  at `/app`; entrypoint `scripts/collect.py` (run_forever).
- Compose service `backend` under `profiles: ["backend"]`:
  `restart: unless-stopped`; networks `[fapd_backend]` (private bridge,
  egress-only — NOT `fapd_edge`; no published ports; unreachable from
  proxy/web/public); volumes `fapd-data:/app/data`,
  `fapd-site:/app/site`; `env_file: .env` (server-side, never synced);
  a mounted read-only deploy key for evidence pushes.
- **EODWorker inside the supervisor** replaces host scheduling. Once
  the publication day has closed on Washington's clock (EOD_ET_HOUR =
  0; the target is always the PREVIOUS Eastern day, so "due at any
  hour" is the intended meaning) and the durable `finalized` marker in
  `collector_state.last_result` does not already cover the target, it:
  sets a pause event all collector workers respect (checked at cycle
  start — in-flight cycles are NOT drained, finding F-006/R16), runs
  `scripts/run_pipeline.py --date <target>` **as a subprocess** (its
  own process, its own connections; the explicit --date is half of the
  2026-08-02 three-clock fix — run_pipeline otherwise picks its own
  day), records `finalized` through EVERY return path (the other half:
  a bare status once erased the marker and re-fired the pipeline every
  ~20 minutes), then — only on exit 0 and only when
  `FAPD_EVIDENCE_PUSH=1` — runs the evidence commit
  (`deploy/vps/scripts/evidence-commit.sh`: repo-root guard, stage the
  evidence paths, ABORT unless the staged set is a SUBSET of the
  allowlist, commit with the `fapd-pipeline` identity named on the
  commit itself, push over the deploy key), and clears the pause in a
  `finally`. Host needs only Docker.
- `fapd-web` serves `fapd-site:...:ro`. `deploy.sh` carries the test
  gate, the two rsyncs (bundle + repo export via
  `deploy/common/repo-excludes.txt`), the image build, and three
  post-up steps (in-container site rebuild per F-009, /today rebuild,
  origin re-flip per F-008). No `/fapd-deploy` skill exists; deploy.sh
  is the runbook's script.

## §10 Tagging build (OB-9 — section layer LIVE 2026-07-30; item-level tags remain)

Mechanical taggers (zero tokens): branch from collection
(CREC/BILLS/PLAW→legislative, FR/AGENCYPR→executive,
USCOURTS→judicial), agency from registry `parent_org` + FR agency
metadata. Discovery keys: a new §3a model surface —
`TAG_PROMPT_VERSION`, cheap tier, batched like plain-speak,
banned-lexicon-gated, stored `method='llm'`, labeled model-derived,
never in fields that read as source-provided. Rendering: section chips
(/today + digest HTML), `digests.json` tags arrays, HTML meta
keywords, agent-surface tag blocks. GUIDE §2/§6 amendment precedes the
build (per the backlog item).

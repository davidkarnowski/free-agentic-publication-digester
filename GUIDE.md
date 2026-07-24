# Information Intelligence — Project Guide

> The governing document for this project. All design, code, and editorial
> decisions should be checkable against this guide. When we change direction,
> we change this document first and record why in `WORKLOG.md`.

---

## 1. Mission

Build an automated pipeline that monitors official United States government
publications — congressional transcripts, bills, the Federal Register, and
related primary sources — and produces a **daily digest** that a single person
can ingest with reasonable effort, while preserving a path back to the full,
unadulterated source record for every claim made.

Two goals in tension, both mandatory:

1. **Digestible** — summarized and aggregated so the day's most significant
   official activity fits in one sitting.
2. **Faithful** — nothing summarized without a citation to the primary source;
   nothing significant silently dropped; no editorial spin introduced.

## 2. Editorial Principles (non-negotiable)

These exist because summarization is where bias creeps in. Every analysis or
reporting component must comply.

- **Primary sources only.** We ingest official government publications, not
  news coverage, not commentary. The source record *is* the product's ground
  truth.
- **Opinion-agnostic output.** Summaries describe what was published, said, or
  enacted — never whether it was good or bad. Banned in generated prose:
  loaded adjectives ("controversial", "landmark", "extreme"), motive
  attribution ("in an attempt to..."), and predictions of political outcomes.
- **Coverage symmetry.** Selection criteria for "what matters today" must be
  mechanical and party-blind: e.g., floor time consumed, number of cosponsors,
  regulatory economic-significance designation, stage of legislative process —
  never subject-matter preference.
- **Cite everything.** Every summarized item links to its govinfo package ID /
  permanent URL. A reader must always be able to check our summary against the
  original in one click.
- **Completeness accounting.** Each digest ends with a coverage statement:
  what was published that day, what we summarized, and what we deliberately
  did not (with counts). Silent omission is the failure mode we most guard
  against.
- **Separate the layers.** Raw data → extracted facts → summaries are stored
  as distinct artifacts. The summary layer can be regenerated or audited
  without re-fetching anything.
- **Method transparency.** Prompts, selection rules, and ranking heuristics
  live in this repo, versioned. If someone asks "why did this item make the
  digest?", the answer must be reproducible.

## 3. Data Sources

### Primary: govinfo (GPO)

- **govinfo API** — `https://api.govinfo.gov` — content and metadata for
  publications from all three branches, in self-describing "packages."
  - Requires a free API key from **api.data.gov** (stored in `.env`, never
    committed).
  - Default rate limits: 36,000 req/hour, 1,200 req/minute, 40 req/second.
    (We will operate far below these — see §4.)
  - Key services:
    - `collections` — list packages by collection code **and last-modified
      date**. This is our change-detection mechanism: poll "what changed since
      timestamp X" instead of re-scanning.
    - `published` — packages by official issue date.
    - `packages` / `granules` — package summaries and sub-documents (e.g.,
      individual Congressional Record sections), with formats: XML, PDF, HTML
      (htm), MODS, PREMIS, ZIP.
    - `search` — POST search service (use sparingly; discovery via
      `collections` is cheaper and deterministic).
  - Pagination: `offsetMark` (start with `*`) + `pageSize` (max 1,000).
  - Quirk: ZIP/MODS may return **503 + Retry-After** while generated
    on-demand; honor the header exactly.
- **govinfo Bulk Data** — `https://www.govinfo.gov/bulkdata` — direct XML for
  BILLS (113th Congress forward), Federal Register, CFR/eCFR, Congressional
  Record, and bill status. Append `/xml` or `/json` to a bulkdata URL for a
  machine-readable directory listing; set proper `Accept` headers or expect
  406. Prefer bulk data over the API for large backfills.
  Docs: `github.com/usgpo/api`, `github.com/usgpo/bulk-data`.

### Collections of interest (initial scope)

| Code | Collection | Why |
|------|-----------|-----|
| `CREC` | Congressional Record (daily) | Floor proceedings & debate — the core transcript source |
| `BILLS` | Congressional Bills | Text of introduced/engrossed/enrolled legislation |
| `FR` | Federal Register | Rules, proposed rules, notices, presidential documents |
| `PLAW` | Public and Private Laws | What actually became law |
| `CHRG` | Congressional Hearings | Committee transcripts (published with lag) |
| `CRPT` | Congressional Reports | Committee analysis accompanying bills |
| `DCPD` | Daily Compilation of Presidential Documents | Executive statements, orders, remarks |

Start with `CREC`, `BILLS`, `FR`; add the rest once the pipeline is stable.

### Secondary (later phases)

- **Congress.gov API** (`api.congress.gov`, same api.data.gov key) — bill
  status, actions, cosponsors, votes metadata.
- **FederalRegister.gov API** — richer FR metadata (agencies, significance
  flags), no key required.

## 4. Respectful Access Policy

We are guests on public infrastructure. Rules, enforced in code, not by
discipline:

- **Self-imposed budget:** max **1 request/second sustained** and a daily cap
  (start: 2,000 requests/day) — roughly 1% of what GPO permits. The client
  refuses to exceed it.
- **Poll, don't hammer:** one scheduled sync per day (a second late-day pass
  is acceptable later). Use the `collections` service's last-modified
  filtering so each sync asks only "what changed since my last watermark."
- **Date-bound every sync.** A sync with no stored watermark (first run, or a
  reset) must not walk open-ended history: it starts at now minus a small
  fixed lookback window (`INITIAL_SYNC_LOOKBACK_DAYS`, currently 3 days) and
  sets the watermark from there. Older history is only ever acquired as a
  deliberate bulkdata backfill, never as an accidental API crawl.
- **Never re-download unchanged content.** Cache everything fetched, keyed by
  package ID + lastModified. Honor HTTP caching (ETag/If-Modified-Since)
  where offered.
- **Honor server signals:** back off exponentially on 5xx, respect
  `Retry-After` exactly, watch `X-RateLimit-Remaining` and stop early if it
  drops unexpectedly.
- **Bulk data for bulk needs.** Any backfill of more than a few days of
  history uses the bulkdata endpoints (built for this), run off-peak
  (overnight US Eastern), throttled.
- **Identify ourselves:** descriptive `User-Agent` with contact email.
- **Log every request, twice.** Accountability has two layers, both with the
  API key redacted:
  1. `data/fetch_log.db` — the canonical, queryable record of every outbound
     request (URL, UTC timestamp, status, bytes, elapsed ms, attempt, error),
     written by the HTTP client itself so nothing can bypass it.
  2. `data/logs/access-YYYY-MM-DD.log` — a human-readable narrative at DEBUG
     level (every request, pacing sleeps, retries and why, watermark moves,
     per-package outcomes), regardless of console verbosity.
  `scripts/audit.py` reports our footprint from layer 1 at any time:
  requests/day vs. budget, status mix, bytes, retries, recent errors.

## 5. Architecture Concept

Four stages, each writing durable artifacts so any stage can be re-run
without touching upstream:

```
[1 FETCH]  scheduled sync → govinfo collections delta → download new/changed
           packages → store raw (XML preferred; PDF where graphics require)
           + metadata + fetch log
                │
[2 EXTRACT] parse raw XML → normalized records (speaker, chamber, bill ids,
           agency, doc type, dates, full text) → local store (SQLite to
           start). Graphics flagged in the source (FR <GPH>) are inventoried
           per document and extracted as individual image assets.
                │
[3 ANALYZE] mechanical aggregation first (counts, stages, cross-references);
           LLM summarization second, constrained by §2 rules, always with
           citations back to package/granule IDs. Selected items' graphics
           get a vision pass (see §6) so visual content informs the summary.
                │
[4 REPORT]  daily digest (Markdown): headline activity, per-chamber summary,
           new rules/laws, tracked-item updates, coverage statement.
           Digests embed relevant source graphics (stored under
           digests/assets/, cited like text) rather than only linking out.
```

- **Storage:** filesystem for raw documents (`data/raw/<collection>/<date>/`),
  SQLite for metadata and extracted records. No cloud dependency to start.
- **Language:** Python (mature XML tooling, easy scheduling). Decide at first
  implementation step; record in worklog.
- **Digest output:** `digests/YYYY-MM-DD.md` — accumulates as a browsable
  archive.

## 6. Token Economics (LLM Budget Discipline)

The analysis layer (§5 stage 3) uses LLM calls, which are the pipeline's only
meaningfully metered resource. Same philosophy as §4: budgets are properties
of the code, not of operator discipline.

### Measured reality (2026-07-24, from our own archive)

- Raw archive size wildly overstates LLM-relevant volume: a ~49 MB CREC day
  is ~46.6 MB PDF page images and only ~2 MB XML text.
- Actual text per publication day: CREC ~2 MB, FR ~2.6 MB, BILLS ~2 MB
  (~28 KB/bill × 60–70). Verbatim-everything ceiling ≈ **1.5–2M input
  tokens/day**. A full day therefore exceeds every single-call context
  window — per-item map-reduce is structurally required.
- With mechanical selection and official-summary-first drafting, realistic
  daily load is **~300–800K input / ~10–20K output tokens**.

### Rules (enforced in code when the analysis layer is built)

1. **Whole PDFs never reach a model.** Text always comes from XML — a PDF
   page is ~an order of magnitude more tokens than its text. Graphics are
   the exception, handled as *individual extracted images*, not PDF pages:
   documents that flag graphics (FR `<GPH>`; measured 0–54/issue) get their
   images extracted at the EXTRACT stage, and a **vision pass runs only on
   graphics belonging to items already promoted by a selection rule** —
   rule 4 applies to images exactly as to text. Image tokens count against
   the daily cap and are logged in the ledger like any other call.
   - **Rule FR-GPH-01 (boilerplate graphics).** FR content graphics carry
     section-coded GIDs (e.g. `EN23JY26.004` — equations, forms, maps,
     annex pages; measured 103 of 111 in our first window). Non-conforming
     GIDs (e.g. `Trump.EPS` — signatures, seals) are boilerplate: they
     never trigger a PDF fetch, never get a vision pass, and are never
     embedded. Excluded counts are disclosed in the Coverage Statement —
     the classification is mechanical (a filename pattern), party-blind,
     and costs zero tokens.
2. **Mechanical work costs zero tokens.** Counts, stages, vote tallies,
   groupings, and the entire Coverage Statement are computed in code. An LLM
   call that could have been a SQL query is a bug.
3. **Official summaries before our summaries.** FR agency abstracts, the
   CREC Daily Digest section, and official bill titles/stage codes are the
   first drafting inputs. We summarize verbatim primary text only for items
   a selection rule promoted — this is cheaper *and* editorially safer.
4. **Selection before summarization, always.** No model ever sees an item
   that hasn't passed a §2 mechanical selection rule. The rules bound the
   token spend; loosening a rule is a GUIDE change, not a tweak.
5. **Summarize once, store forever.** Summaries are durable artifacts keyed
   by package/granule ID + content version. Regeneration happens only when
   the source's lastModified changes or the prompt version bumps —
   never as a side effect of re-running the digest.
6. **Tier the models.** Cheap/fast models for per-item map work
   (classification, per-item compression); the strongest model only for the
   final digest composition pass, which sees already-compressed input.
7. **Token ledger, like the fetch log.** Every LLM call is logged (UTC
   timestamp, model, purpose, input/output tokens, package IDs touched) to a
   local ledger. A self-audit report (like `scripts/audit.py`) answers "what
   did analysis cost this week?" at any time.
8. **Measure first, then cap.** The token ledger (rule 7) runs from the
   analysis layer's very first call, but **no hard cap is enforced until
   real test runs establish a measured baseline** — capping against
   estimates risks tuning the digest around a guess (decided 2026-07-24).
   Once a few days of ledger data exist, a daily input-token cap is set
   from observed load (working figure: ~1M/day) and enforced with a hard
   stop: overflow items stay queued for the next day and are named in the
   Coverage Statement's known gaps — a budget stop must never become a
   silent omission (§2).
9. **Graphics in digests are cited evidence, not decoration.** A digest
   embeds a source graphic only when it belongs to a summarized item, and
   it carries the same citation discipline as text (package/granule ID +
   permanent URL). Selected graphics are copied to `digests/assets/<date>/`
   so the published digest is self-contained; items whose remaining
   graphics were *not* rendered still disclose the count with a link to the
   source PDF — the §2 no-silent-omission rule applies to images too.
10. **Batch-friendly by design.** The daily job is not latency-sensitive:
   structure analysis as batchable per-item calls so it can run on
   discounted/off-peak capacity, and so a partial day's work is resumable —
   mirroring the fetch layer's pending-queue semantics.

## 7. Roadmap

- **Phase 0 — Foundation (now):** this guide, worklog, repo scaffolding,
  obtain API key, verify access with a handful of hand-run requests.
- **Phase 1 — Fetch & store:** rate-limited govinfo client, daily delta sync
  for CREC/BILLS/FR, raw archive + fetch log.
- **Phase 2 — Extract:** XML parsers per collection, normalized SQLite
  schema; graphic inventory (`<GPH>` counts per document) and image-asset
  extraction for flagged documents.
- **Phase 3 — Analyze & report:** mechanical aggregation, citation-bound
  summarization, vision pass on selected items' graphics, first real daily
  digest with embedded source graphics; iterate on digest format.
- **Phase 4 — Broaden & harden:** add PLAW/CHRG/CRPT/DCPD, Congress.gov
  metadata, backfill via bulk data, bias/faithfulness spot-audits
  (periodically diff a digest item against its full source).

## 8. Open-Source Readiness

This repo may be published on GitHub at any time. Everything committed is
written as if it were already public:

- **No personal details in tracked files.** Real email addresses, names,
  account identifiers, and machine hostnames live only in `.env` (git-ignored)
  and are read via `config.py`. Committed examples use blank or placeholder
  values.
- **No private/absolute paths.** Code and docs use repo-relative paths only
  (`config.py` derives everything from its own location — keep it that way).
- **Secrets are structurally impossible to commit:** they exist solely in
  `.env`, which is git-ignored; code fails loudly if they're missing rather
  than falling back to embedded defaults.
- **Worklog is public-ready.** Write `WORKLOG.md` entries with publication in
  mind — describe work and decisions, not personal circumstances.
- **Pre-commit habit:** skim the diff for emails, keys, tokens, home paths
  (`/Users/...`), and IPs before every commit.
- **Author attribution convention:** wherever the author's name appears in
  content we control (git identity, package metadata, license, docs), use
  **"David D. Karnowski"** — the middle initial disambiguates from other
  David Karnowskis in tech. Contact email in public-facing metadata is the
  dedicated project address (repo-local `git config user.email`), never a
  personal or GitHub-credential address.

## 9. Working Agreements

- `WORKLOG.md` gets a timestamped, verbose entry for every work session:
  what was done, why, decisions made, dead ends included.
- Decisions that change scope, sources, or editorial rules are made in this
  file first, then implemented.
- Secrets (API keys) live in `.env`, git-ignored, never in code or logs.

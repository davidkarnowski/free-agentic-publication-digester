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

### Dual audience: humans and AI agents (amended 2026-07-28)

This project is a publishing house for **two readerships**: people, and AI
agents researching federal government actions. An agent that needs "what
did the government do on date D" should be able to ingest our digest —
summarized, cited, coverage-accounted — instead of crawling a dozen
official sites itself. That substitution is a feature we actively
advertise, and it is respectful infrastructure twice over: agents get
clean structured access, and government servers get one polite,
disciplined crawler (ours) instead of many.

Standing commitments for agentic access:

- **Explicit invitation.** Public-facing documentation states plainly that
  this data is built for agent ingestion; the site's robots.txt allows
  automated access, and an `llms.txt` guide plus a dedicated access page
  tell agents what exists, where, and how to use it.
- **Clean, stable, machine-first surfaces:** canonical Markdown in the
  repository; static no-JS/no-auth HTML with stable URL patterns
  (`/<YYYY-MM-DD>.html`); a machine-readable digest index
  (`digests.json`); an Atom feed for change discovery; the source guide
  and provenance manifests published alongside.
- **Honesty travels with the data.** Every surface an agent ingests
  carries the same disclosures humans get: citations to the official
  record, inclusion rules, coverage statements, which text is verbatim
  official vs. model-generated, and the §7 provenance trail for
  verification.
- **Guided onward citation.** We ask agents to cite the underlying
  official sources (the govinfo IDs we carry) for claims, and us for the
  aggregation — the digest is a route to the record, never a replacement
  for it.
- **Reciprocity.** We ask of visiting agents exactly the courtesy our own
  crawler practices (§4): honest identification and conditional requests.
  The site is static and cheap to serve precisely so heavy agent traffic
  is harmless.

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
- **Agency statements are attributed speech, never established fact.**
  Press releases and newsroom content are primary sources for what an
  agency *said* — official advocacy, not neutral record. All digest prose
  derived from them must attribute ("the Department stated…", "according
  to the release…") and must never repackage an agency's claims as
  facts the digest itself asserts. Titles quoted verbatim are quoted, not
  endorsed.
- **Plain-language renderings are labeled interpretation.** A digest may
  carry a model-generated "In plain terms" line per item to make official
  register parseable. Constraints: it is derived ONLY from the item's
  stored summary (never from raw text or outside knowledge, so the reader
  can check it against the adjacent official text in place); it adds no
  facts and no significance judgments; it is always visually distinct and
  labeled as our rendering; it is linted un-masked by the banned-lexicon
  gate; an item whose plain rendering fails simply renders without one —
  plain language is a presentation aid, never a substitute for the cited
  summary.

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
| `USCOURTS` | United States Courts Opinions | Judicial branch: opinions from participating federal courts |

Start with `CREC`, `BILLS`, `FR`; add the rest once the pipeline is stable.

### Judicial branch coverage (amended 2026-07-25)

The digest covers all three branches. Judicial coverage is phased:

- **J1 (active):** the govinfo `USCOURTS` collection — opinions from ~140
  participating appellate, district, bankruptcy, and national courts.
  **Structural completeness disclosure (mandatory, standing):** unlike CREC
  and FR, which are the complete official record of their branches,
  USCOURTS is participation-based and is *not* the complete federal
  judicial record. Every digest's judicial section and Coverage Statement
  must carry this disclosure. Mechanical selection leans on the courts' own
  published/precedential designations and court type (appellate summarized;
  district/bankruptcy counted).
- **J2 (planned):** Supreme Court slip opinions and order lists directly
  from supremecourt.gov — our first non-govinfo primary source, admitted
  deliberately because SCOTUS does not publish via USCOURTS; the official
  syllabus serves as the zero-token drafting input (§6 rule 3).
- **J3 (deferred):** docket/filing activity (PACER/RECAP/CourtListener) —
  partial by nature and outside the official-publication model; revisit
  only with a deliberate GUIDE change.
- **Date semantics:** court packages are case-shaped, not day-shaped; a
  digest's judicial items are opinions *filed* on the digest date, and
  publication lag (courts post with delay) is disclosed under Known gaps.

### Agency newsrooms (amended 2026-07-26)

A second non-GPO source class: official agency press releases, statements,
and announcements published on agency websites (RSS feeds preferred;
direct HTML index pages where no feed exists). Governing rules:

- **The registry is the scope authority.** `sources/registry.yaml` (and
  its generated `SOURCES.md`) records every source ingested, planned,
  evaluated-excluded, or unavailable — coverage of the federal source
  universe is measured there, never assumed.
- **Viability is checked, not presumed, and never forced.** A source
  becomes `active` only after a passing robots.txt + feed check through
  our identified client. **No WAF evasion ever** — no browser user-agent
  spoofing, no header games. A site that blocks honestly-identified
  automated access is recorded `unavailable` with the observed behavior:
  that fact is itself accountability data.
- **Mutable-source disclosure.** Unlike the GPO record, agency web content
  can be edited or removed without notice. Digest sections built on this
  class carry a standing disclosure, and §7 (Provenance) governs how
  captures are preserved and how changes are detected and disclosed.
- Ingestion obeys §4 unchanged: paced, budgeted (its own daily bucket),
  fully logged, conditional requests wherever the server supports them,
  robots.txt honored via an RFC 9309 parser with crawl-delay respected.
- **Tiers (amended 2026-07-26).** The registry classifies sources by tier
  so comprehensiveness is measurable against a defined universe rather
  than the famously uncountable full agency list: **Tier 1** — cabinet
  departments, top independents, legislative support agencies (GAO, CBO,
  CRS), the White House briefing room, and core govinfo collections;
  **Tier 2** — major sub-agency newsrooms (CDC, FDA, IRS, FBI, FEMA,
  FAA, service branches, …) and regulator clusters (Federal Reserve,
  FDIC, CFPB, NRC, …) whose output does not flow through their parent
  department's newsroom; **Tier 3** — the long tail, added
  opportunistically. Coverage claims are always stated per tier.
- **Report publishers.** GAO, CBO, and CRS publish *reports*, not press
  releases — closer in character to the GPO record than to newsrooms.
  They are ingested through the same registry/capture machinery, and
  their documents are treated editorially like official analyses:
  attributed to their institution, with its nonpartisan mandate noted.
- **Aggregator sources.** An aggregator (e.g. oversight.gov, which
  collects reports from ~70 Inspectors General) is transport, not origin:
  digest citations must point to the originating agency's document, and
  the aggregator's role is disclosed.

### Source onboarding lifecycle (amended 2026-07-26)

Adding a source is an evaluation, not a URL paste. Every source moves
through these gates, each recorded in the registry entry:

1. **Registered** (`planned`): identity, description, best-known URLs,
   tier — added to the registry so the gap is visible.
2. **Probed:** `scripts/check_sources.py` exercises the *whole* ingestion
   chain through our identified client — robots verdict, fetch (captured
   into provenance), format detection with feed autodiscovery, item
   enumeration with field inventory (GUIDs? dates? full text or
   teasers?), and one sample article fetched and text-extracted. Findings
   are stored as structured JSON; failures record exactly what was
   observed (never retried into submission, never evaded).
3. **Content-evaluated:** before activation, someone (human or model)
   reviews the probe findings and answers, in the registry entry's notes:
   *what does this source publish in total, and what fraction will our
   ingestion see?* (e.g. a feed carrying only the latest 10 items of a
   40/day newsroom under-covers it; an index page may expose categories
   the feed omits). Under-coverage is disclosed, not discovered later.
4. **Active:** ingestion wired, appearing in digests, coverage-statement
   accounting includes it.
5. **Re-evaluated:** any persistent fetch failure or site redesign drops
   the source to `unavailable`/re-probe; status changes are worklog
   events.

## 3a. Prompt Governance (amended 2026-07-26)

All LLM prompts are code, versioned, and change through procedure:

- **Inventory.** Three prompt surfaces exist: the map/summarization
  preamble (`analyze._PREAMBLE`, versioned by `PROMPT_VERSION`), the
  plain-speak restatement preamble (`analyze._PLAIN_PREAMBLE`,
  `PLAIN_PROMPT_VERSION`), and the Day-in-Review compose prompt
  (`compose._PROMPT`, `COMPOSE_PROMPT_VERSION`). Each layer versions
  independently — a deliberate design so iterating on one never
  regenerates the artifacts of another.
- **The plain-speak contract specifically** (the most iterated surface):
  input is ONLY the stored summary (never raw text, never outside
  knowledge); output is one sentence ≤ ~35 words; jargon is expanded into
  ordinary words; dates/deadlines preserved; the §2 banned list restated
  inside the prompt AND enforced un-masked by the render-time lexicon
  gate — two independent layers, prompt-side and validator-side.
- **Iteration procedure:** (1) edit the prompt text in code; (2) bump
  that surface's version constant; (3) state the regeneration scope in
  the worklog entry (what re-runs, what it costs — the version keying
  makes this precise); (4) the validation gates are never loosened to
  accommodate a prompt change — if new prose trips the lexicon, the
  prompt is wrong, not the gate; (5) spot-audit a sample of regenerated
  output against §2 before the next digest publishes.
- **Measured-cost discipline:** prompt iterations are cheap by design
  (plain-layer rephrase ≈ 85K tokens/day of data; compose ≈ 30K) —
  this cheapness exists because of the version decoupling and must be
  preserved by it.

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
           A static HTML site (site/, built by scripts/build_site.py) is a
           derived, zero-LLM presentation layer over the canonical
           Markdown — regenerable at any time, suitable for local viewing
           and GitHub Pages.
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
9. **Plain-speak is a decoupled, batched restatement pass.** The per-item
   plain-language layer (§2) is generated by its own batched pass over
   *stored summaries only* (~170 tokens/item, ~25 items/call), versioned
   independently (`PLAIN_PROMPT_VERSION`) so phrasing iterations never
   regenerate factual summaries. Cheap tier, ledgered like everything else.
10. **Graphics in digests are cited evidence, not decoration.** A digest
   embeds a source graphic only when it belongs to a summarized item, and
   it carries the same citation discipline as text (package/granule ID +
   permanent URL). Selected graphics are copied to `digests/assets/<date>/`
   so the published digest is self-contained; items whose remaining
   graphics were *not* rendered still disclose the count with a link to the
   source PDF — the §2 no-silent-omission rule applies to images too.
11. **Batch-friendly by design.** The daily job is not latency-sensitive:
   structure analysis as batchable per-item calls so it can run on
   discounted/off-peak capacity, and so a partial day's work is resumable —
   mirroring the fetch layer's pending-queue semantics.

## 7. Provenance & Tamper-Evidence

For mutable sources (§3 agency newsrooms), the archive must support the
claim: *this content was served at this URL at this time, and here is
exactly what it said.* Anticipated interference and mitigations:

| Threat | Mitigation |
|---|---|
| Stealth edit after publication | two-hash captures + re-check pass → `modified` events with both versions retained |
| Silent removal | conservative `missing`→`removed` promotion (≥3 failures over ≥48h), captures retained; `restored` tracked |
| Backdating / retro-insertion | `claimed_published_at` vs our `first_seen_at`, always stored separately; claimed dates inside a demonstrably covered window are a flagged anomaly |
| URL churn | document identity keyed by stable id (feed GUID / normalized URL); url + final_url recorded |
| Content served differently to us | Wayback Machine snapshot per new capture — an independent second witness |
| "You fabricated the archive" | attempt-level daily manifests (committed) with a previous-day hash chain; git/GitHub history ordering; Wayback corroboration |

Mechanics:
- **Two hashes per capture:** `content_sha256` (exact decoded entity
  bytes — the evidentiary hash; bytes stored content-addressed under
  `data/captures/`) and `text_sha256` (normalized extracted text,
  versioned by `normalizer_version` — drives change detection, because
  raw agency HTML churns with tokens and asset URLs). Both recorded, so
  both "the bytes changed" and "the words changed" are supportable and
  distinguishable.
- **Attempt-level manifests:** `provenance/manifests/YYYY-MM-DD.jsonl`
  (committed) records every *attempt* — captures, 304s, robots refusals,
  errors — because absence must be an assertion (§2): a gap in monitoring
  is on the record as a gap, never ambiguous. Each manifest's header
  carries the previous manifest's sha256 (deletion or reordering of days
  is detectable from the files alone).
- **Honest limits (stated wherever provenance is claimed):** hashes prove
  what was served **to our identified client** — not what every visitor
  saw; our timestamps are backed by git/GitHub history and Wayback
  corroboration, not third-party notarization (external anchoring, e.g.
  OpenTimestamps, was considered and declined 2026-07-26; revisitable).
  Full statement in `PROVENANCE.md`.

## 8. Roadmap

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
- **Phase J1 — Judicial via govinfo (active):** USCOURTS collection through
  the existing pipeline; opinion extraction from case packages; selection by
  court type + published designation; digest section 5 with the standing
  completeness disclosure.
- **Phase J2 — Supreme Court direct:** supremecourt.gov slip opinions and
  orders, syllabus-first drafting.
- **Phase 4 — Broaden & harden:** add PLAW/CHRG/CRPT/DCPD, Congress.gov
  metadata, backfill via bulk data, bias/faithfulness spot-audits
  (periodically diff a digest item against its full source).

## 9. Open-Source Readiness

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

## 10. Working Agreements

- `WORKLOG.md` gets a timestamped, verbose entry for every work session:
  what was done, why, decisions made, dead ends included.
- Decisions that change scope, sources, or editorial rules are made in this
  file first, then implemented.
- Secrets (API keys) live in `.env`, git-ignored, never in code or logs.

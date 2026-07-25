# Work Production Log — Information Intelligence

> Reverse-chronological log of all work on this project. Every session gets an
> entry: timestamped, verbose, explanatory. Decisions include the *why*, and
> dead ends are recorded alongside successes — the log should let a future
> reader reconstruct not just what we built, but how we got there.

Entry format:

```
## YYYY-MM-DD HH:MM TZ — <short title>
**Context:** what prompted this session
**Work performed:** narrative of what was done
**Decisions:** choices made and rationale
**Open questions / next steps:**
```

---

## 2026-07-25 10:20 PDT — Plain-speak layer: per-item plain-language renderings + readability mechanics

**Context:** User assessment of the first digest: accurate but hard to
parse as a human (verbatim official FR summaries are acronym-dense;
ALL-CAPS Record headings; unexplained procedural jargon). Planned in plan
mode with a design-review sub-agent; user chose per-item plain lines
covering all summarized items.

**Work performed:**

1. **Design deviation (improvement) from the approved plan, adopted from
   the design-review agent:** instead of extending the map-call contract +
   a summaries column + a PROMPT_VERSION bump, the plain layer is a
   **decoupled restatement pass**: new `plain_summaries` table keyed by
   (package, granule, PLAIN_PROMPT_VERSION, source_prompt_version), fed
   only by *stored summaries*. Wins: no migration (table auto-creates);
   phrasing iterations never regenerate factual summaries (~85K vs ~180K+
   tokens per iteration); editorially stronger — every plain line is
   checkable against the adjacent summary it restates; the 07-23 re-run
   cost only the plain pass. PROMPT_VERSION stays 1.
2. **GUIDE first** (§2 + §6 rule 9): plain renderings are labeled
   interpretation — derived only from the stored summary, no new facts, no
   significance judgments, visually distinct, linted un-masked, and an
   item whose restatement fails renders without one (presentation aid,
   never fabricated, never blocks the digest).
3. **`analyze.run_plain`**: batched (25 items/call — inputs are ~170-token
   summaries), cheap tier, strict-JSON, one-retry-then-honest-failure,
   idempotent; ledger purposes `plain:batchN`/`plain:retry`.
4. **Renderer**: `*In plain terms:*` line under every item (CREC, BILLS,
   FR); smart display-casing for ALL-CAPS headings (acronym/digit/dotted
   tokens preserved; disclosed in Methodology); static 15-term procedural
   glossary → "Terms Used Today" section listing only terms present
   (zero tokens); Methodology now states both version numbers and the
   plain-layer provenance. Banned list extended with plain-register
   evaluative framing (red tape, crackdown, slams, loophole).
5. **Validator caught my own bug during development:** glossary entries
   formatted `- **term**` matched the item-block pattern and were rejected
   for lacking inclusion-rule lines — exactly the class of error the gate
   exists for. Fixed by italic term formatting.
6. **Verification run:** only the plain pass executed (map + compose
   idempotent) — 3 Haiku calls, 86,311 in / 10,959 out tokens, **51/51
   plain lines, 0 failures**, validation passed. Spot-check: the
   suppressors interim final rule now reads "The Commerce Department is
   revising export controls to transfer firearm silencers ... to less
   restrictive Commerce controls..." — factual, jargon-free, neutral.
7. **Tests: 131 passing** (+4 run_plain, +5 report incl. un-masked-lint
   proof: a banned term in a plain line fails validation; a banned term in
   an official summary does not).

**Measured:** full-day bill with plain layer ≈ 235K in / 18K out
(149K map+compose + 86K plain) — ~24% of the 1M working figure; still
overhead-dominated (25K/call × ~7 calls).

**Open questions / next steps:** unchanged (cap after more ledger days;
scheduling; vision pass; periodic §2 editorial spot-audit — now including
plain lines).

---

## 2026-07-24 13:20 PDT — Phase 3 built; first digest generated (uncapped test run)

**Context:** Phase 3 (Analyze & report) built and test-run in one session:
LLM client + token ledger (main thread), analysis and rendering layers
(two concurrent sub-agents), compose stage added mid-build on user
direction (a full-day synthesis pass over the final outputs). Per GUIDE §6
rule 8 (amended today): uncapped, measure-first.

**Work performed:**

1. **`llm.py`** — LLM client backed by the `claude` CLI in headless mode
   (usage bills to the operator's Claude subscription; no API key), with a
   persistent token ledger (`data/llm_ledger.db`) mirroring the fetch log:
   every call recorded (model, purpose, package ids, tokens, duration,
   errors). Smoke test surfaced the decisive measurement: **~25K input
   tokens fixed overhead per headless call** — which dictated batching the
   map stage (≤6 items/call) before any real run happened.
2. **`rules.py` / `analyze.py`** (sub-agent): named mechanical rule
   registry (CREC-SEL-01 floor-time ≥15K chars; CREC-SEL-02 recorded votes
   always listed — regex calibrated on real Record text incl. a pinned
   false-positive guard for demanded-but-not-taken votes; BILLS-SEL-01
   reached-stage; FR-SEL-01/02/03 all rules/proposed/presidential) plus
   named exclusions for coverage. Map stage: official-summary-first (FR
   SUMMARY preambles stored verbatim at zero tokens), batched strict-JSON
   Haiku calls for the rest, one-retry-then-honest-failure, idempotent by
   (package, granule, prompt_version).
3. **`compose.py`** (main thread, user-directed scope addition): one
   strong-model "Day in Review" pass whose inputs are the stored item
   summaries + mechanical counts only — never the raw corpus. Stored in
   `day_summaries`; idempotent; rendered at the top of the digest; linted
   UN-masked by the banned-lexicon validator.
4. **`report.py` / `scripts/digest.py`** (sub-agent): fully deterministic
   zero-LLM render of TEMPLATE.md — header with git version + watermarks,
   CREC per chamber + votes, BILLS stage table, FR by agency with embedded
   graphics (TIFF→PNG via Pillow, ≤2/item + disclosure), SQL-computed
   Coverage Statement, methodology footer. Validation gate before any file
   is written: citation resolution against the DB, coverage arithmetic
   reconciliation (recomputed independently), banned-lexicon scan (official
   summaries masked; LLM prose not), inclusion-rule line on every item.
5. **Test run (uncapped), digest for 2026-07-23:** 51 items selected
   (33 official / 18 LLM), 4 LLM calls total — 3 Haiku map batches + 1 Opus
   compose — **148,571 input / 6,890 output tokens**, ~75 seconds of model
   time. Validation passed; digests/2026-07-23.md written (366 lines,
   51 inclusion-rule lines, 7 graphics embedded as PNG with the remainder
   disclosed). Day in Review reads factual and party-blind on inspection
   (recorded-vote tallies, proclamations, rule actions — no editorializing).
6. **Test suite: 125 passing** (llm 4, compose 3, analyze 14, report 11 +
   all prior), ruff clean.

**Measured baseline (the point of running uncapped):**
- ~150K input tokens/day for a full busy-day digest — **~15% of the 1M/day
  working figure**; two-thirds of it is CLI fixed overhead (4 × ~25K), so
  the marginal content cost is ~50K/day.
- Implication for the future cap: 500K/day would already carry ~3× margin;
  decision deferred until a few scheduled days accumulate in the ledger.

**Decisions:**
- Compose stage restored to the design (user direction; matches GUIDE §6
  rule 6's original tiering) — synthesis over stored outputs, never over
  raw corpus; strictest lint applied to it.
- Backend choice (claude CLI vs API SDK) recorded as revisitable: the CLI
  binds usage to the Max plan; if per-call overhead ever matters, an SDK
  backend on `llm.py`'s interface is a drop-in change.

**Open questions / next steps:**
- [ ] Accumulate a few days of ledger data, then set the cap (§6 rule 8).
- [ ] Schedule the daily pipeline: sync → extract → digest (launchd/cron,
      overlap guard).
- [ ] Vision pass on selected items' graphics (currently disclosed as "not
      yet implemented" in the Coverage Statement).
- [ ] Review the generated digest's editorial quality against §2 with fresh
      eyes after a few days of output.

---

## 2026-07-24 12:50 PDT — Phase 2 complete: extraction layer built and run over the full archive

**Context:** Phase 2 (Extract) built in one session: three collection
parsers and the graphics asset extractor developed concurrently by four
sub-agents against the real archive, with schema + orchestrator built in
the main thread, then integrated and run end-to-end.

**Work performed:**

1. **Schema** (db.py + docs/schema.md "Extraction layer" section):
   `extracted_texts` — one row per FR document / CREC granule / whole bill,
   composite key (package_id, granule_id), doc_type as the selection axis,
   JSON metadata (incl. official FR `SUMMARY:` abstracts per GUIDE §6),
   FR-GPH-01 graphic counts, extracted_at + extractor_version for
   staleness; `graphic_assets` — per-`<GPH>` inventory with classification,
   printed page, repo-relative asset path, status.
2. **Orchestrator** (`extract.py` + `scripts/extract.py`): staleness query
   (missing / raw re-fetched / version bump), per-package replace-on-rerun,
   per-package failure isolation, FR graphics inventory + image extraction
   to `data/assets/FR/<date>/<pid>/`. 6 orchestrator tests via fake parsers.
3. **Parsers** (sub-agents; pure functions, no DB; stdlib only):
   - `parsers/fr.py` — walks the full tree (sections are NOT reliably
     top-level: `NEWPART` nesting, `PRESDOC` wrappers); FRDOC regex
     extraction (PRESDOCU splits the wrapper across siblings); DATES vs
     EFFDATE variants; official SUMMARY captured to metadata. 743 documents
     across 7 issues, doc count == FRDOC count in every file.
   - `parsers/crec.py` — granule htm from the daily ZIP (files live under
     `html/` despite docs saying `htm/`; matched by filename pattern);
     verbatim text with line structure and page markers preserved, GPO
     header boilerplate dropped; issue-order sorting. 838 granules over 4
     days, 100% section-typed, zero empty texts. Granule `<title>` tags are
     issue-level boilerplate → titles come from our granules table instead.
   - `parsers/bills.py` — longest-type-first package-id decomposition
     (hconres before hr), stage attribute from either root form, sponsors
     (absent on 50/209 — post-introduction versions drop the block).
     209/209 parse; 9 stage values; two 118th-Congress bills present
     (lastModified revision tracking, same effect as the old FR issues).
4. **Graphics** (`graphics.py`, sub-agent): 103/103 substantive graphics
   extracted from the six companion PDFs (~10.5 MB; 100 TIFF, 3 PNG), all
   verified pixel-decodable; 8 boilerplate correctly skipped without
   opening a PDF. Notable engineering: pypdf's CCITT `get_data()` writes a
   corrupt TIFF header (missing next-IFD terminator) — module builds its
   own minimal TIFF around the raw Group-4 stream; FR PDFs carry no
   /PageLabels, so printed pages are recovered by scanning page-header text
   (a constant offset is provably wrong: unnumbered part-divider pages
   interleave mid-issue).
5. **Full run:** 220/220 packages extracted, **1,790 records, 22.7M chars,
   0 failures**; DB totals reconcile exactly with each agent's
   independently-reported per-file counts. FR doc-type distribution:
   566 NOTICE / 102 RULE / 67 PRORULE / 8 PRESDOCU.
6. **Test suite: 90 passing** (client 10, sync 14, extract 6, parsers 48,
   graphics 12), ruff clean.

**Decisions:**
- Parsers are pure `parse(raw_path, package) -> iter[record]` functions;
  the orchestrator owns all DB writes. Kept parsers standalone (FR-GPH-01
  regex duplicated locally rather than importing sync).
- Graphic assets stored as extracted (TIFF/PNG); conversion to
  web-embeddable format is a Phase 3 (REPORT) concern, at embed time.

**Open questions / next steps:**
- [ ] Phase 3: selection rules → mechanical aggregation → token ledger +
      1M/day cap → tiered summarization → digest generation per
      TEMPLATE.md (convert embedded graphics TIFF→PNG at embed time).
- [ ] Schedule the daily pipeline (sync → extract) via launchd/cron with
      the run-overlap guard.

---

## 2026-07-24 11:45 PDT — Graphics classification: rule FR-GPH-01 (boilerplate vs content)

**Context:** User inspected the fetched FR PDFs and observed graphics that
looked like boilerplate — the official seal, the President's signature —
questioning whether the PDF fetch is warranted. Investigated empirically.

**Work performed:**

1. **Ground truth from the XML.** FR `<GPH>` elements carry a `<GID>`
   filename that encodes what the graphic is. Content graphics use a
   section-coded pattern (`EN23JY26.004` etc. — EN/ER/EP/ED + date + seq):
   in our window these are *rate formulas rendered as images* (small,
   DEEP=15–30), agency forms, and full-page executive-order annexes
   (DEEP≈640). Signature graphics use non-conforming names — every
   boilerplate instance found was `Trump.EPS` (DEEP=80, right-aligned,
   following "IN WITNESS WHEREOF..." text). Key negative finding: image
   *size* is NOT a usable signal (equations are tiny but substantive);
   the GID naming convention is.
2. **Classification across the archive:** 111 flagged graphics = 103
   substantive + 8 signature boilerplate (all 8 in FR-2026-07-23's
   presidential documents). So the user-observed signatures are real but
   the minority; the companion PDFs remain justified — every one of the 6
   archived PDFs has ≥1 substantive graphic, so no pruning or re-sync was
   needed.
3. **Rule FR-GPH-01 implemented** (`classify_graphics()` in sync.py): PDF
   fetch now triggers only on ≥1 *substantive* graphic. Signature-only
   documents never cost a request, never get vision, never get embedded;
   boilerplate exclusions are logged and will be disclosed in the Coverage
   Statement. Codified in GUIDE §6 rule 1; TEMPLATE.md coverage line now
   splits observed graphics into content vs boilerplate-excluded.
4. **Tests:** fixtures updated to real GID structures; new signature-only
   test proves no PDF request is made; classifier unit test. 24 passing.

**Decisions:**
- Classification is by GID filename pattern — mechanical, party-blind, zero
  tokens — not by image size (provably misleading) and not by an LLM.
- The rule is named (FR-GPH-01) so digest exclusion disclosures can cite it,
  per the §2 pattern of named mechanical rules.

**Open questions / next steps:** unchanged (Phase 2 extraction; its graphic
inventory now records the substantive/boilerplate split per document).

---

## 2026-07-24 11:22 PDT — Graphics fetch implemented; FR re-synced with companion PDFs

**Context:** Implementing the fetch-layer half of the graphics scope change,
then re-syncing FR to backfill graphic content for already-held packages.

**Work performed:**

1. **`sync.py`: conditional companion-PDF fetch.** After an FR package's XML
   is archived, the bytes are scanned for `<GPH>`; if flagged, the package's
   PDF is also downloaded to a sibling path
   (`data/raw/FR/<date>/<pid>.pdf`). XML remains the primary artifact
   (`download_format` unchanged); no-graphics packages make no extra
   request; an already-present PDF is not re-fetched (idempotent). CREC
   needs no equivalent — its ZIPs already contain the PDFs.
2. **2 new tests** (22 total, all passing): flagged FR package archives both
   XML and PDF; unflagged package skips the PDF *and provably makes no PDF
   request*.
3. **FR re-sync** using the designed re-download path (flip `fetch_status`
   to `pending`, run `--collections FR`): 7/7 re-fetched, 0 failures,
   28 requests (day total 488/2000, ~24% of budget). Result: 6 of 7 issues
   carry graphics — companion PDFs archived for all 6 (111 flagged graphics
   total; FR-2026-07-23 alone has 54). FR-2026-07-24 (0 graphics) correctly
   skipped its PDF — the conditional verified live, both directions.

**Decisions:**
- Companion PDF presence is derivable (sibling path exists) rather than a
  new `packages` column — Phase 2's extractor checks the filesystem; if
  extraction later needs richer bookkeeping (per-graphic rows), that
  belongs in the Phase 2 schema addition, not a stopgap column now.

**Open questions / next steps:** unchanged — Phase 2 extraction (parsers,
graphic inventory + image-asset extraction from the now-present PDFs).

---

## 2026-07-24 10:55 PDT — Scope change: graphics become first-class (multimodal analysis + embedded in digests)

**Context:** Investigated whether XML-only extraction misses visual content.
Empirical answer from our archive: CREC and BILLS are pure text (BILLS
"graphic" grep hits were words like "geographic"); FR tables come through as
structured `<GPOTABLE>` XML (better than PDF for analysis); but FR carries
real graphics — 0–54 `<GPH>` elements per issue (maps, form facsimiles,
labeling examples, diagrams) whose content exists only outside the XML.
User direction: graphics are in scope — multimodal analysis, and final
digests should include relevant source graphics.

**Work performed (GUIDE first, per working agreement):**

1. **GUIDE §5 architecture** updated across all four stages: FETCH may pull
   PDF where graphics require it; EXTRACT inventories `<GPH>` per document
   and extracts individual image assets; ANALYZE runs a vision pass on
   selected items' graphics; REPORT embeds relevant graphics in digests
   (self-contained under `digests/assets/<date>/`).
2. **GUIDE §6 rule 1 amended** — was "PDFs never reach a model," now "whole
   PDFs never reach a model": text still comes from XML only, but
   individually-extracted graphics may go to vision, gated by the same
   selection rules as text, with image tokens counted against the daily cap
   and logged in the ledger.
3. **GUIDE §6 new rule 9** — graphics in digests are cited evidence, not
   decoration: embedded only for summarized items, carrying full citations;
   unrendered graphics are disclosed with a count and source-PDF link (§2
   no-silent-omission applies to images).
4. **Roadmap** Phase 2/3 items updated (graphic inventory + asset
   extraction; vision pass + embedding).
5. **digests/TEMPLATE.md** — FR item slots gain embedded-graphic blocks with
   captions, per-graphic citations, and a required disclosure line for
   unrendered graphics; Coverage Statement gains a source-graphics
   accounting line (observed / vision-analyzed / embedded).

**Decisions:**
- Graphics equal citizens editorially: same selection gating, citation
  discipline, and omission accounting as text. Factual captions only
  (§2 opinion-agnostic prose applies).
- Digest self-containment: selected graphics are copied into
  `digests/assets/` (committed) rather than hotlinked, so the published
  archive stands alone; volume is naturally small (only summarized items'
  graphics).

**Open questions / next steps:**
- [ ] Fetch-layer implication: FR currently downloads XML only. Phase 2 must
      add "fetch the PDF (or graphic files) when a package's XML flags
      `<GPH>`" — a second, conditional download per flagged package, well
      within request budget (graphics-bearing FR issues are a handful/week).
- [ ] Choose image-extraction approach from FR PDFs at Phase 2 build time
      (e.g., pypdf/pdfplumber image extraction vs page-region rendering).

---

## 2026-07-24 10:40 PDT — Token economics: measured the corpus, codified LLM budget rules

**Context:** User raised the right pre-Phase-3 question: can a daily archive
that measures 215 MB be summarized within a monthly Claude Code Max plan?
Answered empirically, then codified the answer as guidance.

**Work performed:**

1. **Measured the real text volume** (from our own archive, not estimates):
   a ~49 MB CREC day decomposes into ~46.6 MB of PDF page images and only
   ~2 MB of XML text. Per publication day: CREC ~2 MB, FR ~2.6 MB, BILLS
   ~2 MB text. Verbatim-everything ceiling ≈ 1.5–2M input tokens/day;
   with mechanical selection + official-summary-first drafting, realistic
   load is ~300–800K input / 10–20K output tokens/day. Conclusion: easily
   within a Max plan's daily headless run (limits are shared with
   interactive use and not token-denominated, so contention — not
   feasibility — is the consideration); even API pay-per-token would be
   ~$1–2/day, halved via batch processing.
2. **New GUIDE.md §6 "Token Economics (LLM Budget Discipline)"** — mirrors
   §4's philosophy (budgets as code): PDFs never reach a model; mechanical
   work costs zero tokens (an LLM call that could be SQL is a bug);
   official summaries (FR abstracts, CREC Daily Digest, bill titles) before
   our own; selection always precedes summarization; summarize-once-store-
   forever keyed by content version; model tiering (cheap map, strong final
   compose); a token ledger paralleling the fetch log with its own audit
   report; a hard daily input-token cap (initial 1M/day) whose overflow
   queues to tomorrow and is named in the Coverage Statement (a budget stop
   must never be a silent omission); batch-friendly, resumable analysis.
3. **Renumbering:** Roadmap → §7, Open-Source Readiness → §8, Working
   Agreements → §9. Cross-references updated in docs/schema.md; earlier
   worklog entries citing "§7" refer to the numbering current at their
   timestamps and are left as written.

**Decisions:**
- Daily LLM input cap set at 1M tokens (~half the verbatim ceiling, ~2×
  expected load) — enforced by the analysis runner when built, same
  hard-stop pattern as the HTTP client's request budget.
- Token spend gets the same two-layer accountability as server access:
  structured ledger + audit script.

**Open questions / next steps:**
- [ ] Phase 2 extraction unchanged; Phase 3 must implement the §6 rules as
      code (ledger, cap, tiering) alongside the first digest generation.

---

## 2026-07-24 10:15 PDT — First full sync complete: 220/220 fetched, zero errors

**Context:** The background download run launched at 09:48 PDT finished
(exit 0). This entry records the verified results of the project's first
complete data acquisition.

**Work performed / results:**

1. **Final state:** all 220 packages in the 3-day window fetched — BILLS 209,
   FR 7, CREC 4. Zero failures, zero packages left pending.
2. **Footprint (from scripts/audit.py, i.e., our own canonical record):**
   460 requests on 2026-07-24 UTC = 23.0% of the self-imposed daily budget
   (and ~1.3% of one *hour* of GPO's actual allowance). 460/460 responses
   were 2xx; zero errors, zero retries needed; 215 MB transferred; average
   response 987 ms.
3. **Raw archive:** 215 MB on disk — CREC 191 MB (whole daily Congressional
   Record issues as ZIP), FR 18 MB, BILLS 6 MB.
4. **Granule inventory:** 838 CREC granules classified (430 HOUSE,
   258 SENATE, 125 EXTENSIONS, 25 DAILYDIGEST).
5. **Watermarks:** all three collections now hold server-side lastModified
   watermarks (BILLS 2026-07-24T16:07:05Z, FR 2026-07-24T16:11:21Z, CREC
   2026-07-24T11:53:38Z); the next sync is a true delta.
6. **Algorithm observations from the live run:**
   - The download run's own listing (after the earlier list-only pass had
     advanced watermarks) re-listed exactly 1 boundary package per
     collection — the inclusive-watermark overlap being absorbed by
     idempotent upserts, as designed.
   - The lastModified delta also surfaced three *old* FR issues
     (FR-2024-06-18, FR-2025-04-11, FR-2026-04-02) that GPO recently
     reprocessed — revision tracking working, not a bug.

**Decisions:** none new; this entry is verification of the design under real
conditions.

**Open questions / next steps:**
- [ ] Schedule the daily sync run (launchd/cron); include a run-level
      wall-clock guard so a pathologically slow run can't overlap the next
      day's (noted 2026-07-24; guard protects our scheduling, not the server).
- [ ] Phase 2: XML parsers — CREC granules (from the package ZIPs), BILLS
      bill text, FR documents — feeding the extraction schema.
- [ ] CHRG lag note for Phase 4: committee hearing transcripts publish weeks
      to months after the hearing (witness/member review, committee
      clearance, GPO typesetting). They will be digested as "newly
      published" with the original hearing date shown — never presented as
      same-day coverage. Floor transcripts (CREC) are next-morning.

---

## 2026-07-24 09:55 PDT — Delta sync implemented + first real sync; accountability logging

**Context:** Continuing Phase 1: the metadata store and delta-sync engine,
the first real data pull, and (user directive) deeper verbosity/logging so
every API interaction is accountable.

**Work performed:**

1. **`src/info_intel/db.py`** — metadata store, DDL exactly per docs/schema.md
   (packages / granules / sync_state, WAL mode, foreign keys on, partial
   unfetched index).
2. **`src/info_intel/sync.py`** — the delta-sync algorithm as designed:
   watermark (or date-bounded start on first run) → paged listing → idempotent
   upserts (newer lastModified flips a fetched row back to pending; equal is
   a no-op) → watermark advanced only after listing success → downloads from
   the pending queue (XML preferred, ZIP fallback for CREC, PDF last resort),
   granule inventory refresh for CREC/FR, per-package failure isolation,
   budget/rate-floor aborts preserve the queue. `scripts/sync.py` CLI with
   `--list-only`, `--max-downloads`, `--verbose`.
3. **10 new tests** (20 total, all passing, still zero network): date-bounded
   first start, watermark resume/advance, listing-failure leaves watermark,
   pending-flip semantics, download bookkeeping incl. repo-relative raw_path,
   failure isolation, budget abort, download cap, CREC granule inventory.
4. **First real sync.** `--list-only` first: 3-day window held 220 changed
   packages (CREC 4, BILLS 209, FR 7) — the date bound working as intended
   (an unbounded BILLS listing would have been ~289k). Then a full download
   run (~460 requests projected, ~23% of daily budget) launched in the
   background at the enforced 1 req/s.
5. **Accountability logging** (user directive). Two layers, documented in
   GUIDE.md §4:
   - `data/fetch_log.db` remains the canonical per-request record (client-
     written, key-redacted).
   - New `info_intel/logging_setup.py`: console (INFO, or DEBUG with
     `--verbose`) + daily file `data/logs/access-YYYY-MM-DD.log` that always
     captures DEBUG — every request with running budget count ("[today:
     N/2000]"), pacing sleeps, retries with cause (Retry-After vs backoff),
     budget refusals, rate-floor halts, watermark moves, per-package archive
     outcomes with byte and granule counts.
   - New `scripts/audit.py`: self-audit report from the fetch log — per-UTC-day
     requests vs. budget, status mix, MB transferred, avg latency, retry
     count, recent errors, busiest endpoints. First real run: 23 requests,
     1.1% of budget, zero errors/retries; CREC ZIPs dominate bytes (whole
     daily Congressional Record issues, ~190 MB total — expected).
   - Verified offline (fake session): redaction holds in both log layers.

**Decisions:**
- File log always records DEBUG regardless of console verbosity — the
  narrative must be complete on disk even when the console is quiet.
- Audit script opens the fetch log read-only (`mode=ro`) — the auditor cannot
  modify the record it audits.
- Deferred: log rotation/retention (daily files are small; revisit if bulk).

**Open questions / next steps:**
- [ ] Confirm background sync completion; check final audit + pending queue.
- [ ] Phase 2: XML parsers (CREC granules, BILLS text, FR docs) feeding the
      extraction schema.

---

## 2026-07-24 09:10 PDT — Phase 1: rate-limited client (+ schema design, digest template)

**Context:** Start of Phase 1 (Fetch & store). Core deliverable: the
rate-limited govinfo HTTP client. Per user direction, independent
work items were parallelized to sub-agents: the SQLite schema design and the
daily digest template, both of which depend only on GUIDE.md, not on client
code.

**Work performed:**

1. **`src/info_intel/client.py` — `GovinfoClient`.** GUIDE.md §4 enforced in
   code:
   - Paces requests to `MAX_REQUESTS_PER_SECOND` (1/sec) via monotonic-clock
     interval enforcement.
   - Daily budget (`MAX_REQUESTS_PER_DAY` = 2000) counted from the
     *persistent* fetch log in `data/fetch_log.db` — a process restart cannot
     reset the budget. Exceeding it raises `BudgetExceededError`.
   - Every attempt (not just every logical request) is logged with UTC
     timestamp, URL + params, status, bytes, elapsed ms, attempt number, and
     error — with the API key stripped before logging.
   - 429/5xx handling: honors `Retry-After` exactly when present; otherwise
     exponential backoff (2/4/8/16 s); gives up after `MAX_ATTEMPTS` = 5.
   - Safety halt: if the server ever reports `X-RateLimit-Remaining` below
     `MIN_SERVER_REMAINING` (1000), the client refuses further requests
     (`RateLimitFloorError`) — at ~1% budgeted usage we should never be near
     the server's limit, so proximity means a bug on our side.
   - `paginate()` follows `nextPage` links, always re-injecting our own key
     and discarding any echoed `api_key` parameter.
   - Session, sleep, and clock are constructor-injectable for testing.
2. **`tests/test_client.py`** — 10 tests, no network (fake session +
   deterministic clock, tmp-path DB): pacing, budget enforcement across a
   simulated restart, Retry-After honored, backoff sequence, give-up after
   max attempts, key redaction in logs, per-attempt logging, rate-floor halt,
   pagination key-stripping, User-Agent presence. All pass; ruff clean.
3. **Live dogfood:** `scripts/verify_key.py` rewritten to use the client.
   One real request: HTTP 200, fetch-log row written correctly
   (~4.8 KB, ~2.8 s elapsed), budget accounting 1/2000.
4. **`docs/schema.md`** (sub-agent) — SQLite schema design for the metadata
   store (`data/info_intel.db`): `packages` (natural key `package_id`,
   change detection via `fetched_last_modified` vs `last_modified`, coarse
   4-state `fetch_status`, partial index for the unfetched queue),
   `granules` (composite-key `WITHOUT ROWID`), `sync_state` (per-collection
   server-side `lastModified` watermark, advanced only after a listing
   completes — crash recovery by harmless re-listing + idempotent upserts,
   no journal). DDL was machine-validated against a real SQLite instance by
   the designing agent. First-sync date bound (3 days) incorporated.
5. **`digests/TEMPLATE.md`** (sub-agent) — the digest output contract:
   mechanical section names, required "Included because: {rule}" line and
   govinfo permanent-URL citation on every item slot, explicit "If none"
   renderings so absence is never silent, mandatory Coverage Statement
   reconciling all observed packages (summarized / counted-only / excluded
   by named rule), methodology footer. Worked fictional EXAMPLE blocks per
   section, clearly fenced.

**Decisions:**
- Fetch log stays a **separate DB file** from the pipeline metadata store
  (different owner, append-only audit lifecycle; can't be rolled back by
  pipeline transactions). Rationale in docs/schema.md.
- Client halts (rather than warns) on low server-reported remaining quota:
  proximity to the server limit at our budget level can only mean a client
  bug, and the safe response to a suspected bug is stopping.
- Watermark semantics: advance only on successful *listing*, not successful
  *download* — failed downloads park as `pending` rows and never force
  re-listing a window.

**Open questions / next steps:**
- [ ] Implement `db.py` (apply docs/schema.md DDL) and the delta-sync module
      per the algorithm in docs/schema.md.
- [ ] First real sync run (date-bounded, CREC/BILLS/FR).
- [ ] Then Phase 2: XML parsers feeding the extraction layer that
      TEMPLATE.md's slots require.

---

## 2026-07-24 08:47 PDT — Repo scaffolding, API key verified, first-sync bound

**Context:** Phase 0 continuation: turn the empty directory into a working
repo and get govinfo API access confirmed.

**Work performed:**

1. **Repo scaffolding.** `git init` (branch `main`); directory layout per
   GUIDE.md §5: `src/info_intel/` (pipeline code), `scripts/` (operational
   one-offs), `data/` (git-ignored raw archive + future SQLite), `digests/`
   (committed output), `tests/`. Added `.gitignore` (secrets, data, Python
   artifacts), `README.md` (setup + layout), `pyproject.toml`.
2. **Python project.** Managed with **uv** (Python 3.14 available; project
   requires ≥3.12). Runtime deps kept minimal: `requests`, `python-dotenv`.
   Dev deps: `pytest`, `ruff`. `uv sync` created `.venv` and lockfile.
3. **Config module** (`src/info_intel/config.py`): loads `.env`, defines
   paths, API base URLs, and — as code, not documentation — the GUIDE.md §4
   access-policy constants (`MAX_REQUESTS_PER_SECOND = 1.0`,
   `MAX_REQUESTS_PER_DAY = 2000`) plus a descriptive `User-Agent` with
   contact email.
4. **API key.** `.env.example` created; user obtained an api.data.gov key and
   populated `.env` themselves. Wrote `scripts/verify_key.py` — a single GET
   to the `collections` service. Result: **HTTP 200**, rate limit confirmed
   at 36,000/hr, and all seven target collections visible with package
   counts: BILLS ~289k, CRPT ~158k, CHRG ~47k, FR ~23k, PLAW ~6k, CREC ~6k.
5. **First-sync date bound** (user directive mid-session): a sync with no
   stored watermark must not walk open-ended history. Added
   `INITIAL_SYNC_LOOKBACK_DAYS = 3` to config and a corresponding rule to
   GUIDE.md §4. The package counts above make the risk concrete — an
   unbounded first "delta" against BILLS would try to enumerate ~289k
   packages.

6. **Open-source readiness** (user directive mid-session): the repo may be
   published on GitHub, so committed content must contain no private paths,
   personal details, or other revealing information. Added GUIDE.md §7
   ("Open-Source Readiness") codifying this: personal details only in
   git-ignored `.env`, repo-relative paths only, public-ready worklog style,
   pre-commit diff scan for emails/keys/home paths. Immediate fix required:
   `.env.example` had the author's real contact email baked in — scrubbed to
   a blank placeholder before first commit. Verified the rest of the tree
   with a grep for emails and `/Users/` paths: clean.

7. **Identity separation.** Configured a dedicated project email
   (repo-local `git config user.email`) distinct from the author's personal
   and GitHub-credential addresses; re-authored the initial commit with it.
   The same dedicated address is used for `CONTACT_EMAIL` in `.env`, so the
   User-Agent presented to GPO carries project contact info rather than a
   personal account.

8. **Attribution convention.** The repo will be published under the author's
   normal GitHub account, so the goal is scrubbing incidental private details,
   not anonymity. Convention adopted (GUIDE.md §7): author name is written
   "David D. Karnowski" everywhere we control it (git identity, pyproject
   authors metadata, future license/docs) to disambiguate from other people
   with the same name in tech. Applied via repo-local git config and a
   re-authored root commit.

**Decisions:**
- **Python + uv confirmed** as implementation stack (previously deferred).
  Rationale: mature XML tooling, uv gives reproducible env with lockfile.
- **First-run watermark = now − 3 days.** Small enough to be a trivial number
  of requests, large enough to cover a weekend gap. Backfills beyond that are
  bulkdata-only, per existing policy.
- `data/` is git-ignored (regenerable, potentially large); `digests/` is
  committed (it's the product and its archive).

**Open questions / next steps:**
- [ ] Phase 1: rate-limited client (token bucket + daily counter + request
      log), then the collections delta sync for CREC/BILLS/FR.
- [ ] Sketch SQLite schema (packages, granules, fetch_log, sync watermarks).
- [ ] Draft digest template.

---

## 2026-07-24 08:33 PDT — Project inception: concept, guide, and worklog

**Context:** New empty project directory (`Information_Intelligence`). Goal
defined in conversation: programmatic access to US government official
publications (congressional transcripts, bills, Federal Register, etc.),
producing an automated daily analysis/digest that is non-political, unbiased,
and opinion-agnostic, while preserving a full, unadulterated picture of the
source record. Explicit constraint from the outset: be respectful of
government servers — no abusive API usage.

**Work performed:**

1. **Source research.** Confirmed govinfo.gov (run by the U.S. Government
   Publishing Office) as the primary data source. Reviewed GPO's official
   developer documentation (github.com/usgpo/api and github.com/usgpo/bulk-data;
   the api.govinfo.gov/docs site itself is a JavaScript app that doesn't yield
   to simple fetching). Key findings:
   - API requires a free key from **api.data.gov**; default limits are
     36,000 requests/hour, 1,200/minute, 40/second — far more than we will
     ever need, and we will self-impose much lower budgets anyway.
   - The **collections service** supports listing packages by last-modified
     timestamp. This is the architecturally important find: it enables a
     clean "what changed since my last sync" delta poll — one cheap daily
     query pattern instead of any re-scanning.
   - Packages come in multiple formats (XML, PDF, HTML, MODS, PREMIS, ZIP);
     XML is the preferred format for parsing. ZIP/MODS can return
     503 + Retry-After while generated on demand.
   - A separate **bulk data** repository (govinfo.gov/bulkdata) serves XML
     for BILLS, FR, CFR/eCFR, and Congressional Record — the right channel
     for any historical backfill, keeping the API for daily deltas.
   - Noted secondary sources for later: Congress.gov API (bill status, votes,
     cosponsors — same api.data.gov key) and the FederalRegister.gov API
     (richer FR metadata, no key needed).

2. **Wrote `GUIDE.md`**, the project's governing document, covering:
   - Mission: the digestible-vs-faithful tension named explicitly as the core
     design problem.
   - Editorial principles: primary sources only; opinion-agnostic prose with
     specific banned patterns (loaded adjectives, motive attribution);
     mechanical, party-blind selection criteria; universal citations; a
     per-digest "coverage statement" so omissions are never silent; layered
     artifacts (raw → extracted → summary); versioned, reproducible methods.
   - Initial collection scope: CREC (Congressional Record), BILLS, FR
     (Federal Register) first; PLAW, CHRG, CRPT, DCPD once stable.
   - Respectful access policy, enforced in code: ≤1 req/sec sustained,
     ~2,000 req/day cap (~1% of permitted), single daily delta sync, cache
     everything, honor Retry-After and rate-limit headers, descriptive
     User-Agent with contact info, full request logging for self-audit.
   - Four-stage architecture (FETCH → EXTRACT → ANALYZE → REPORT) with
     durable artifacts between stages; filesystem + SQLite storage; digest
     output as dated Markdown files.
   - Roadmap phases 0–4.

3. **Created this `WORKLOG.md`** with the entry format above.

**Decisions:**
- **govinfo as primary source; API for daily deltas, bulk data for
  backfills.** Rationale: single authoritative origin (GPO) covering all
  three branches; delta polling via the collections service is both the
  cheapest and the most respectful access pattern.
- **Start scope = CREC + BILLS + FR.** These cover the three highest-value
  daily streams (floor transcripts, legislation text, executive/regulatory
  actions) without overcommitting the parser work.
- **Editorial rules written before any code.** Bias enters at the
  summarization layer, so the constraints on that layer are defined first
  and treated as non-negotiable in GUIDE.md §2.
- **Self-imposed rate budget ~1% of GPO's allowance.** Daily-digest use case
  simply doesn't need more, and it makes "respectful access" a property of
  the client, not of operator discipline.
- Deferred: implementation language (Python is the leading candidate — mature
  XML tooling — but this gets decided and logged when Phase 1 starts).

**Open questions / next steps:**
- [ ] Obtain api.data.gov API key; store in `.env` (git-ignored).
- [ ] Hand-run a few sample requests against `collections/CREC` and a single
      package summary to verify assumptions about response shapes (small,
      one-off, well within budget).
- [ ] Decide repo scaffolding: git init, `.gitignore`, `data/` layout,
      Python project skeleton.
- [ ] Sketch the SQLite schema for package metadata + fetch log.
- [ ] Draft the daily digest template (sections, coverage statement format)
      before building the analysis layer, so reporting drives extraction
      requirements rather than the reverse.

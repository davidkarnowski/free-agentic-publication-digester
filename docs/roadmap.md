# Roadmap — where the Free Agentic Publication Digester is going

*Living document, tracked. Replaces GUIDE §8's original phase list
(2026-07), which described a project that had not yet shipped; this
describes the one that has. Reviewed 2026-08-31 after a project-wide
read of the code, the research memos, the published digests, and five
weeks of production evidence. GUIDE.md governs; this document plans.
Items are grouped by kind so the branch discipline in CLAUDE.md §8
applies cleanly. Each item names its gate — a GUIDE amendment, an
operator ruling, or plain CI.*

## 0. Where we are

Thirty-four daily digests since 2026-07-27, produced by a supervisor
that has run unattended on a shared VPS since 07-30 and finalized every
publication day since the mechanical floor landed on 08-24 (GUIDE §6
r15). Nine collections, 129 registered sources (45 active), a corpus
of ~54,000 packages, ~99,500 logged requests at 20% error (nearly all
govinfo's on-demand ZIP 503s, disclosed as baseline), and ~120M input
tokens of inference — of which roughly two-thirds were the CLI's own
fixed per-call context, not our documents (see §3).

What the review found is a project whose stated standards are mostly
true of it — deterministic zero-LLM render, parameterized SQL, seams,
bounded retries everywhere, empty-state disclosure — and whose weakest
surface is not the machinery but the **editorial signal**: only 5–9%
of a business day's units get a summary, court volume swamps
everything, and the Congressional Record section can be empty on a
real session day because selection is by character count.

## 1. Editorial signal (highest leverage; GUIDE §2/§3 rulings first)

- **CREC selection by granule kind, not length.** Two real session
  days (08-21, 08-25) rendered "no floor items met the selection
  thresholds" while 78 and 42 granules sat counted. Select debate on a
  named measure and recorded votes by type; keep the length rule as a
  secondary signal. *Gate: GUIDE §3 CREC-SEL amendment.*
- **USCOURTS: dedup by docket, flag stale opinions, filter clerk
  notices.** One case listed six times on 08-29; 35 of 843 listed
  opinions in 14 days were filed before August (back to 2024-07) and
  summarized as current; 6–20 Eighth Circuit rehearing-deadline notices
  a day render as opinions. *Gate: §3 judicial amendment + a test on
  the 08-29 fixture.*
- **Presidential actions: summarize at EOD or say why not.** 08-25/26
  summarized 0 of 5 (a national-emergency order rendered bare).
  *Gate: investigate first; likely the key-contract fix of 08-27
  already resolved it — verify against the next PRESACT day.*
- **Sections 7/8 collapse to one line when empty** (13 of 14 days);
  fix or retire `senate-xml` (quiet since 08-08). *Gate: CI.*
- **Agency announcements carry the feed's own teaser, attributed**, not
  titles only — ~140 items/day is the digest's longest and least
  informative section, and sensational official headlines run
  unmediated. *Gate: GUIDE §2 attribution paragraph already permits it;
  render change + lexicon gate on the teaser text.*
- **Glossary from real terms** (remand, vacate, en banc, ad valorem…)
  and a "how to read a citation" paragraph on the FAQ (granule ids,
  `(rh)`, CFR parts). *Gate: CI.*
- **Plain-language lines that add facts** ("prices", "torturing") —
  tighten the plain prompt's self-check; two cases found in twelve
  sampled. *Gate: `PLAIN_PROMPT_VERSION` bump.*

## 2. Machine surfaces

- `site/day/*.json` and `today.json` carry **no model attribution**:
  add `inference` (backend, models, per-layer status from
  `day_inference`), `prompt_version`, per-item `date_issued` and
  `section`, and `inclusion_rule` for every listed item. *Gate: CI;
  schema is additive.*
- `llms.txt`/agents page promise votes and bill actions as content;
  they are empty most days — say so, or fix §1 first.
- Decide the five open questions in `docs/agent-api-design.md`
  (versioned `/api/v1/`, archive feed, write-if-unchanged builds), or
  mark it parked. At minimum stop stamping the build wall-clock into
  digest HTML. *Gate: operator.*

## 3. Inference: cost, provider, and the floor

- **Lean CLI context.** `claude -p` bills ~26,500 tokens per call for
  Claude Code's own system prompt and tool definitions; with
  `--system-prompt`, `--tools ""`, `--exclude-dynamic-system-prompt-
  sections`, `--setting-sources ""` the same call bills ~250. Projected
  −67% input tokens/day and an end to the 5-hour session-limit trips.
  *Gate: GUIDE §3a — ratify as a transport change after a dev-stack
  golden comparison, or bump `PROMPT_VERSION`.*
- **Provider contract.** A Protocol/ABC for backends; an explicit,
  logged failover (`LLM_BACKEND_FALLBACK`) now that the r7 attribution
  and the per-run breaker exist; HTTP `Retry-After` capped like the LLM
  one (D22). *Gate: CI + GUIDE §6 r7 note.*
- **The mechanical floor stays the floor.** r15 is deployed and has
  carried six clean nights; the phrase-scoped lexicon exemption (08-30)
  removes the last class of false gate trips seen in production. No
  further gate loosening without a GUIDE amendment.

## 4. Operations

- **Backups.** Nightly `VACUUM INTO` of the three databases plus an
  rsync of the raw archive to a second location; a restore rehearsal
  written into OPS-GUIDE. Today the repo holds the digests and the
  manifests; the box alone holds the corpus they hash.
- **Retention.** `data/` is 22 GB after five weeks (19 GB USCOURTS
  ZIPs), growing ~4 GB/week, with no policy. Decide what the hash chain
  must still prove after raw is pruned; then a keep-N-days rule.
  *Gate: GUIDE §7 amendment.*
- **Latent secret-handling bug:** the Gemini backend passes its key in
  the URL query string; a connection-level error would write that URL
  into the ledger. Verified not exploited on production (0 rows). Move
  to the `x-goog-api-key` header with a test. *Gate: CI.*
- **One pacing clock per host across processes.** The collector and the
  nightly finalizer each keep per-host pacing in memory; on nights when
  both poll the same host, gao.gov's 420-second `crawl-delay` was
  undercut six times in seven days (gaps of 58–355 s, all on a feed
  that answered 304). The fetch log is already the shared record —
  read the host's last request from it before pacing. *Gate: CI; GUIDE
  §4 already states the rule the code should meet.*
- Content-Security-Policy (OB-18, now achievable: one script, no inline
  handlers), `scripts/check.sh` (OB-7), the weekly CVE sweep script
  (OB-17), stale-output deletion in `build_site` (OB-12/OB-19 merged).

## 5. Code health

- Split `publish.py` (4,484 lines) at its own section markers into
  site core, sources pages, per-source pages, blog, today/day view, and
  agent surfaces; split `_build_day_page` (376 lines, eleven `if live:`
  branches) into a shared body plus two wrappers.
- Extract the harvest/call shape in `analyze.py` — three callers now
  (map, plain, lexicon correction).
- `tts.py`: an injectable transport, a seams-table row, and the audio
  write moved out of `compose_day` (a model layer should not write to
  the site tree). Then narration is either governed (version, ledger,
  gate, label — GUIDE §3a) or removed; the 15 MB of orphan MP3s go
  either way.
- Lint that means something: enable ruff `B`, `BLE`, `SIM`; fix the six
  unchecked `zip()`s (two in `analyze.py`'s harvest would drop items on
  a length mismatch); `db.connect_ro()` for the four hand-rolled
  read-only openers; drop `BULKDATA_BASE`/`SOURCES_REGISTRY`.
- Tests: `db.py` is the schema authority at a 0.28 test ratio — direct
  tests for `_ensure_columns`, WAL and busy-timeout contracts; inject
  `sleep=` in the three 2-second LLM retry tests.

## 6. Sources and access

- **Send the first letter.** The access-alternatives memo (07-29) drafted
  the M-23-22 and GSA-registry approaches; none has been sent, and the
  README currently says "we engage agency web and API teams directly."
  Either send one or soften the sentence. 20 sources are `unavailable`
  because their newsrooms refuse bots — we back off, by design.
- **Re-probe cadence.** The July probe said "monthly"; no re-probe has
  run. Decide a cadence and script it.
- **Judicial completion:** a SCOTUS COLLECTION decision (`scotus`
  planned since July) and the html-index polling-cadence ruling that
  unblocks ~21 planned sources.
- **Multi-media:** DVIDS key + adapter, or park the class explicitly.

## 7. Documentation

- Nine research memos, seven never revisited: add `docs/decisions.md`
  (recommendation → decision → date) so PACER, EDGAR, YouTube, DVIDS,
  the re-probe cadence, `/api/v1`, and the live brief stop being
  open-by-omission.
- `docs/architecture.md`: fetch → extract → analyze → render → freeze →
  push in five minutes, with the three clocks and a data-model diagram.
- README status block regenerated (it is 27 days old on a public page);
  a "what we don't do" list.
- Hygiene: a dozen items resolved in code but still open (F-017, F-023/
  F-024 "deploy pending", D15, D20b, D20f, D24); OB-19 merged into
  OB-12; both 08-24 and 08-30 plans stamped shipped; `code-standards`
  and `accessibility` last-reviewed dates made real.

## 8. Retired from the old GUIDE §8

Phases 0–3, J1 and R are done (R's "cron/systemd timer" became the
in-container supervisor). CHRG/CRPT/DCPD were cancelled by the 07-31
probe; PRESACT shipped instead. "Backfill via bulk data" and the
"vision pass on selected graphics" were never built and are not
planned. J2 (Supreme Court direct) is the open item above.

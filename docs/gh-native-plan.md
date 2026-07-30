# GH-Native Runtime Plan — running FAPD entirely on GitHub

> **STATUS: SUPERSEDED (2026-07-30).** The operator chose a VPS-hosted
> runtime before the T2–T5 evaluation ran: the pipeline will execute on
> a VPS while GitHub remains the public repository, CI, and the
> committed digest/manifest integrity record. The active plan is
> [`vps-runtime-plan.md`](vps-runtime-plan.md). The `gh-native` branch
> is preserved unmerged as the evaluation record, per this plan's own
> rule ("if evaluation fails, the branch is evidence, not debt");
> `ci.yml` was the one artifact promoted to `main`. The text below is
> unchanged from adoption on 2026-07-29.

*Adopted as the active scheduling track 2026-07-29. Built and evaluated
on the `gh-native` branch; promoted to `main` only by reviewed PR after
the test plan below passes. The VPS/self-hosted-runner alternative is
documented at the end — considered, not settled, and revisitable on
evidence.*

## Goal

The whole project — code, evidence, *and execution* — lives on GitHub:
scheduled Actions workflows run the daily pipeline on hosted runners,
commit the evidence, refresh the state, and deploy the site. The
pipeline remains a plain Python program throughout; GitHub is a
scheduler around it, never a dependency inside it, and a local run
stays possible forever.

## Design principle: git history for evidence, Releases for state

Measured state (2026-07-29): `fapd.db` 80 MB, captures 73 MB, raw
archives 800 MB, fetch log 512 KB. The committed evidence (digests
9.6 MB, manifests 184 KB, site 8.7 MB) is text and small. Binary state
that changes daily does not belong in git history.

1. **State store: a rolling GitHub Release** (tag `pipeline-state`).
   Each run downloads the prior assets (`fapd.db.zst`,
   `fetch_log.db.zst`, `llm_ledger.db.zst`), executes, and uploads
   replacements. No repo bloat; assets may be up to 2 GB. The state is
   public — radical transparency, and safe by construction: the fetch
   log has been key-redacted since day one. `actions/cache` may
   accelerate restores but is never the source of truth.
   `data/raw` and `data/captures` roll into monthly `*.tar.zst` Release
   bundles (the long-planned S4 storage design, accelerated); raw is
   re-fetchable from govinfo if a bundle is ever lost.
2. **Evidence is committed by the run itself**: digests, provenance
   manifests, SOURCES.md, site/ — plus a new committed daily
   **run summary** (`provenance/runs/YYYY-MM-DD.md`: per-client request
   counts vs budgets, items ingested, digest validation verdict, stage
   timings). This is the answer to "don't Actions logs provide access
   accountability?" — they don't (90-day retention, admin-deletable,
   private-repo-scoped); our own committed, hash-chain-adjacent record
   does, permanently and publicly.
3. **Automated commits use a bot identity** (`fapd-pipeline
   <noreply@github.com>`) so pipeline authorship and human authorship
   stay distinguishable in history.

## The LLM stage

`src/fapd/llm.py` gains an **AnthropicBackend** (official `anthropic`
SDK) selected by `LLM_BACKEND=api|cli` — default stays `cli` locally so
nothing changes for operator runs. Model mapping: map/plain layers
haiku→`claude-haiku-4-5`; compose opus→`claude-opus-4-8`. The token
ledger and prompt versioning are backend-independent and unchanged.
Honest cost note: ~$1–2/day at measured loads, billed to an API key
held in Actions secrets.

## Workflows (all born on the `gh-native` branch)

- **`ci.yml`** — hosted, on push/PR: `uv sync`, `ruff check`, `pytest`.
  No secrets; safe on any branch and, later, on the public repo.
- **`pipeline.yml`** — `workflow_dispatch` during evaluation, daily
  `schedule:` cron (off-peak US Eastern, per GUIDE §4) once promoted:
  restore state from the Release → `run_pipeline` (sync → agencies →
  extract → analyze[api] → digest) → commit evidence → upload state →
  build the site artifact. `concurrency:` group is the overlap guard;
  `timeout-minutes` generous but far inside the 6-hour job cap (the
  crawl-delay-heavy source is feed-only now).
- **`pages.yml`** — `actions/deploy-pages` from the site artifact
  (site/ was never a servable branch directory; the artifact path
  solves it), with `SITE_BASE_URL` set so the machine surfaces emit the
  absolute URLs they formally require.
- **Secrets**: `GOVINFO_API_KEY`, `ANTHROPIC_API_KEY`, `CONTACT_EMAIL`,
  and IMAP credentials when the email adapter lands. Scheduled
  workflows never expose secrets to fork PRs.

## The honest trade: what the VPS bought that GitHub does not

Hosted runner IPs are shared and changing. The identified-client
posture loses IP stability and reverse-DNS, and agency WAFs may 403
more often than they do from a stable address. Mitigations, in order:
the User-Agent + contact identification is unchanged; the effect is
**measured, not assumed** (test T4 below records a per-source 403 delta
against local baselines); **Web Bot Auth request signing** becomes the
priority identity mechanism — a cryptographic identity travels with the
request regardless of IP (keys in secrets; see
`docs/access-alternatives-research-2026-07-29.md`); and govinfo, our
heaviest source by far, is a key-authenticated API that does not care
about caller IP.

**Decision rule:** if the measured 403 delta materially shrinks agency
coverage and signing doesn't recover it, revisit the VPS/hybrid shape —
with the branch's evidence in hand rather than speculation.

## Evaluation plan (on `gh-native`, from GitHub itself)

- **T1** — `ci.yml` green on the branch: the suite runs on GitHub
  infrastructure.
- **T2** — one-time state seeding: upload current local state to the
  `pipeline-state` Release (documented `gh release` commands).
- **T3** — dispatch `pipeline.yml` in list-only/dry mode: proves state
  restore, budget enforcement, and logging on a hosted runner without
  downloads.
- **T4** — dispatch a full run on a real day; **diff the digest against
  a local run of the same day** (prose must be identical; only
  footprint metadata may differ) and record the per-source agency 403
  delta in the run summary — the IP-reputation measurement.
- **T5** — several consecutive scheduled days, branch committing its
  evidence to itself; editorial review; then a reviewed PR promotes the
  runtime to main and local runs become the fallback.

**Branch isolation is a hard rule:** main receives only documentation
until T1–T5 pass. If evaluation fails, the branch is evidence, not
debt.

## Build backlog for the branch (in order)

1. AnthropicBackend in llm.py (+ tests with a fake SDK client).
2. Run-summary emitter (`provenance/runs/`, from audit/ledger data).
3. State restore/upload steps in pipeline.yml (gh release download/
   upload, zstd).
4. Evidence-commit step with the bot identity.
5. T2–T4 execution; per-source 403 comparison.
6. Cron enablement + pages.yml cutover; PR to main.

## The documented alternative: VPS self-hosted runner (not settled)

A Dockerized self-hosted runner (or plain cron) on a VPS offers a
consistent public IPv4 with reverse-DNS — identity infrastructure that
verified-bot programs and M-23-22 engagement letters can point at — plus
local state and the CLI LLM backend unchanged. Its costs: a second
platform to harden and pay for, the self-hosted-runner security rule
(never attach to a public repo; a private ops repo would be required),
and the project no longer "living completely on GitHub." It remains the
fallback if the decision rule above triggers.

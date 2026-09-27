# Plan 2026-09-27 — Gemini fallback for every inference caller

*Approved 2026-09-27 and implemented (T1–T4; T5 waits for a paid tier).
Follows docs/ops/plan-task-template.md.
Touches GUIDE §6 r7 and CLAUDE.md §9 ("provider failover is
finalizer-only"), so T1 is a GUIDE amendment and precedes the code.*

## Why now

From 2026-09-24 23:22 UTC to 2026-09-26 11:00 UTC the `claude` CLI refused
every call with "Your organization has disabled Claude subscription
access for Claude Code": 156 refused calls in about 36 hours, the same
message as the 2026-08-14 outage. The finalizer failed over to Gemini as
designed. The 09-24 and 09-25 digests finalized on Gemini, although the
map layer failed for 09-24. The continuous AnalyzeWorker has no fallback,
by the 2026-09-05 ruling, so it paused for the whole outage. On 09-26
only 34 of 1,345 journaled items were summarized.

The ruling that kept the collector off Gemini rested on the free tier:
about 20 requests a day, against an all-day load of 30–60 map and plain
calls and a finalizer hour of 4–11. The ledger bears that out. The last
Gemini quota error was on 2026-08-23. During the 09-25 and 09-26
failovers, Gemini served 13 calls (7 errors, none of them quota) and 18
calls (no errors). **Whether that ceiling still holds decides the size of
this plan** (see *Open question*).

The operator's direction (2026-09-27): any inference the pipeline needs
falls back to Gemini when the Claude CLI is not available.

## Answered: the outage was a paused subscription

Operator, 2026-09-27: the Anthropic subscription behind the CLI was
paused while a payment was pending. That accounts for the 36-hour
refusal ("organization has disabled Claude subscription access"). It was
not an API credit balance, and no Anthropic API key is configured. Gemini
is still the **free tier**, so T2's reserve is load-bearing: without it,
a daytime outage spends the fallback's roughly 20 daily calls before the
04:00 finalizer, which is the August 2026 failure. T5 (a stronger Gemini
model for composing) waits for a paid tier.

## T1 — GUIDE §6 r7: failover for every inference caller

- **Why:** r7 and CLAUDE.md §9 limit failover to the finalizer on
  purpose. Widening it is a GUIDE change.
- **Files:** `GUIDE.md` §6 r7 (dated amendment), `CLAUDE.md` §9 (the
  entry is rewritten, not deleted: its reasoning becomes the reserve's
  justification), §14 decision log.
- **Diff sketch:** failover applies to every caller that makes model
  calls: the finalizer, the AnalyzeWorker, source descriptions and
  assessments, and the insight report. It stays one hop, never a chain,
  and fires only on a refusal that will not change within the run. Two
  rules are new:
  - **Finalizer reserve:** callers other than the finalizer may spend
    at most `LLM_FALLBACK_COLLECTOR_SHARE` of the fallback's daily call
    budget. It is counted from the ledger, the same way request budgets
    are counted from the fetch log.
  - **Return to primary:** the next cycle tries the primary first.
- **Alternatives considered:**
  - Switching production to Gemini outright. Rejected: August showed
    what the free tier does to the finalizer.
  - A per-caller allowlist. Rejected: every caller should get the same
    rule, with the reserve as the only asymmetry.
- **Risk:** without the reserve, a daytime outage spends the fallback
  before the 04:00 finalizer. That is the exact August failure.
- **Verification:** read the amended rule and `git diff GUIDE.md`.
- **Rollback:** revert the amendment and unset
  `LLM_FALLBACK_COLLECTOR_SHARE`, which restores finalizer-only failover.
- **Dependencies:** none (the question is answered above).

## T2 — The collector gets a fallback, behind a ledger-counted reserve

- **Why:** this is the operator's direction, and the collector is where
  the 36-hour outage did its damage.
- **Files:** `src/fapd/config.py`, `src/fapd/collect.py`
  (`Supervisor._default_llm`), `src/fapd/llm.py` (the hop checks the
  reserve), tests.
- **Diff sketch:**
  - `_default_llm()` returns `LLMClient(fallback=config.LLM_BACKEND_FALLBACK,
    fallback_budget=collector_budget)`.
  - `collector_budget` is the fallback's daily call cap
    (`LLM_FALLBACK_DAILY_CALLS`) times `LLM_FALLBACK_COLLECTOR_SHARE`.
  - Before hopping, and before each call on the fallback, the client
    counts today's ledger rows for the fallback backend. At or past the
    budget it declines to hop, trips the breaker exactly as today, and
    logs that the reserve is held for the finalizer.
  - The finalizer's client passes no budget and may use the whole cap.
  - Defaults: cap 20 and collector share 0.5 for the free tier. With a
    paid tier the operator raises the cap in `.env`.
- **Justification:** the ledger is already the source of truth for model
  spend (GUIDE §6 r8), and counting from it works across processes and
  restarts, exactly like the request budgets. AnalyzeWorker already builds
  a fresh client every cycle (`with self.sup.llm_factory()`), so the
  return to the primary needs no new code: each cycle tries the CLI
  first. The CLI answers a disabled-access refusal instantly (`api_ms=0`),
  so that retry costs almost nothing.
- **Alternatives considered:** a cross-cycle "primary is down, skip it
  for N minutes" memory. Deferred: the instant refusal makes it
  unnecessary, and it is one more state to get wrong.
- **Risk:** Gemini prose in continuous summaries. Attribution already
  handles it: the ledger records the backend per call, and
  `day_inference.backend` is plural. The lexicon gate and every validation
  gate are provider-blind (GUIDE §6 r7).
- **Verification:**
  - Tests: a primary refusal hops to the fallback under the budget and
    declines at the budget.
  - Tests: the finalizer client is never capped by the collector share.
  - Tests: the next cycle's client tries the primary first.
  - Tests: ledger rows carry the serving backend.
- **Rollback:** set `LLM_FALLBACK_COLLECTOR_SHARE=0`.
- **Dependencies:** T1.

## T3 — Source descriptions and assessments follow the same client

- **Why:** they run inside `run_pipeline.py` on the finalizer's client,
  which already has the fallback. Confirm this with a test rather than
  assume it.
- **Files:** tests only, unless the test shows a gap.
- **Dependencies:** T2.

## T4 — The insight report says when the primary was down

- **Why:** the 36-hour outage showed up as five error lines.
- **Files:** `src/fapd/insight.py`, tests.
- **Diff sketch:** a "Provider availability" block per backend in the
  work window:
  - the first and last refusal, and the refusal count;
  - how many calls the fallback served;
  - how much of the collector reserve was used.

  This is mechanical and costs no tokens.
- **Dependencies:** none; it can ship first.

## T5 — The compose tier on Gemini (only if the tier is paid)

- **Why:** both tiers resolve to `gemini-2.5-flash` today. Composing the
  Day in Review on the smallest model is a quality cost that was accepted
  only because the free tier left no choice.
- **Files:** `.env` on the box (`FAPD_COMPOSE_MODEL_GEMINI`); no code.
- **Dependencies:** the open question.

## Not in this plan

- **Access logging.** Operator ruling 2026-09-27: fapd.info keeps minimal
  logs, used for security only, and no usage reporting is built from them.
  Edge log depth for security attribution is planned in the operator's
  private edge tree.

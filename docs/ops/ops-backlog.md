# Ops backlog — tracked, not scheduled

*Operational gaps we know about and have consciously chosen not to
schedule yet. **Each item lists the trigger that promotes it into
active work.** Review this file whenever a trigger event approaches.
Completed work gets a dated `**Done YYYY-MM-DD:**` paragraph appended
in place — what changed, what was verified, where rollback artifacts
live, what was deferred. Scope rule:
[docs/pre-publication-todo.md](../pre-publication-todo.md) is the
*launch* checklist; this file is *operations*; an item lives in exactly
one.*

---

**OB-1 — Backend container deployment (`fapd-backend`)**
- **Gap:** the VPS serves only the placeholder; the pipeline still runs
  on the operator machine.
- **Trigger:** operator says go, after the continuous-ingestion
  workstream merges.
- **Sketch:** `deploy/vps/Dockerfile.backend` (python:3.12-slim + uv +
  git); compose service under `profiles: ["backend"]`, egress-only
  private network, `fapd-data` + `fapd-site` volumes, `.env` via
  env_file, mounted deploy key; EOD scheduling inside the supervisor
  (EODWorker: pause collectors → finalize → guard-shell evidence commit
  as `fapd-pipeline` → resume); web container swaps placeholder mount
  for the `fapd-site` volume; `deploy.sh` with test gate + load-bearing
  excludes; `/fapd-deploy` skill lands with the runbook. Full design:
  [docs/continuous-ingestion.md](../continuous-ingestion.md).

**OB-11 — Make VPS evidence pushes real: state seeding + SSH remote**
- **Gap:** the backend renders from its own fresh-start database (its
  2026-07-29 digest is thinner than the canonical one) and its HTTPS
  origin cannot push (F-008) — currently a deliberate safety.
- **Trigger:** operator decision that VPS output should become the
  canonical record (requires API credits first; see OB-1 Done-note).
- **Sketch:** stop backend → seed the fapd-data volume with the
  operator machine's fapd.db (+ fetch_log/ledger) so the VPS continues
  the record instead of re-deriving it → `git remote set-url origin
  git@github.com:...` in the deploy flow → controlled first push
  verified against a local render of the same day (the old T4 parity
  check) → only then leave FAPD_EVIDENCE_PUSH=1.
- **Done 2026-07-30 (evening):** executed as designed. Backend stopped;
  first-day volume backed up on the box; the operator machine's full
  data/ (raw archives, captures, assets) rsynced in, with the three
  SQLite databases re-copied as checkpointed `VACUUM INTO` snapshots
  after the first rsync produced a WAL-torn `fapd.db` (malformed schema
  on open — copy databases cold, never live-file rsync). collector_state
  seeded with the 07-29 finalization so the EOD didn't refire on start.
  Parity: in-container re-render of 2026-07-29 differed from the
  committed digest ONLY in the generated-at timestamp and pipeline
  version hash — content byte-identical. deploy.sh now re-flips the
  baked origin to SSH every deploy (F-008); deploy-key `ls-remote`
  verified against main. FAPD_EVIDENCE_PUSH=1 stands; first automated
  push expected at the next EOD. The laptop is fallback only.

**OB-2 — Committed daily run summary (`provenance/runs/YYYY-MM-DD.md`)**
- **Gap:** run facts (budgets, counts, verdicts, timings) live only in
  local logs; the public record has no per-run execution transparency.
- **Trigger:** OB-1 (evidence commits become automated).
- **Sketch:** emitter reading fetch-log/ledger/validation state, called
  by the EOD finalizer; committed with the evidence.
- **Done 2026-07-30:** built as `fapd.insight` — `provenance/runs/
  insight-<date>.md` from the run_pipeline post-stage: requests by
  client, token spend with retry share, LLM errors, journal coverage,
  collector liveness, plus a labeled cheap-tier suggested-next-steps
  list (INSIGHT_PROMPT_VERSION, GUIDE §3a dev-facing surface). Rides
  the evidence commit (provenance/ is already staged). Failure never
  fails the run.

**OB-3 — Web Bot Auth request signing**
- **Gap:** crawler identity is UA + contact + (now) stable IP; no
  cryptographic identity.
- **Trigger:** IETF WG specs finalize, or a WAF-blocked agency offers
  verified-bot onboarding.
- **Sketch:** Ed25519 keys in `.env`/secrets; JWKS at
  `/.well-known/` on the site; sign per request; reference in M-23-22
  letters.

**OB-4 — GUIDE §6 rule-8 daily token cap**
- **Gap:** no hard cap enforced; measure-first period is over — real
  baselines exist (ordinary ~90K, judicial-heavy 1.53M, post-fix ~200K
  input/day).
- **Trigger:** operator reviews the baselines and picks the number.
- **Sketch:** cap constant + hard stop in `LLMClient`; overflow items
  queue to the next day and are named in the Coverage Statement's known
  gaps (a budget stop must never be a silent omission).

**OB-5 — Wayback corroboration top-up**
- **Gap:** ~180 captures from 2026-07-28 lack a Wayback second witness
  (budget exhaustion + 31/37 blocked submissions on 2026-07-30).
- **Trigger:** any audit/verification pass over that window, or three
  consecutive under-budget days.
- **Sketch:** re-submission pass spread over daily 100-request budgets,
  oldest first.

**OB-6 — `data/` backup policy**
- **Gap:** `fapd.db`, `fetch_log.db`, `llm_ledger.db`, and captures are
  not re-fetchable; no backup exists. (Raw govinfo archive IS
  re-fetchable — lower priority.)
- **Trigger:** OB-1 (the data moves to the VPS), or any near-miss.
- **Sketch:** nightly sqlite `.backup` + captures rsync to a second
  location; restore drill documented.

**OB-7 — One-command verification protocol**
- **Gap:** code-standards §7 steps 1–3 are run by hand.
- **Trigger:** the third time anyone forgets one.
- **Sketch:** `scripts/check.sh`: ruff → pytest → smoke flags.

**OB-8 — `/today` renderer**
- **Gap:** intraday state (item_journal) has no public surface.
- **Trigger:** operator go, after the collector core proves stable
  locally.
- **Sketch:** designed in full in
  [docs/continuous-ingestion.md](../continuous-ingestion.md) —
  `build_today()` over `collect.today_status()`, site/today.html +
  today.json, preliminary-disclosure header, RenderWorker rebuild after
  any journaling cycle, never committed.

- **Done 2026-07-30 (operator go):** `publish.build_today` renders
  site/today.html + today.json from `collect.today_status` — disclosure
  block (GUIDE §5 wording), last-updated stamp, per-section newest-item
  times, pending-model-summary count, official/model summary labels in
  place. A RenderWorker (5-min check, rebuild only when the journal
  watermark moved or the artifact is missing) keeps it fresh at zero
  tokens. Both files gitignored — derived-only, never committed;
  llms.txt/robots.txt/nav gained pointers labeled preliminary.

**OB-9 — Section auto-tagging build**
- **Gap:** `item_tags` schema exists (B2); no taggers, no rendering.
- **Trigger:** operator go (was requested 2026-07-30; schema-first by
- **Done 2026-07-30 (section layer):** GUIDE §6 r12a; tags.py
  (mechanical branch/agency + batched discovery keys,
  TAG_PROMPT_VERSION, lexicon-gated via the digest); canonical
  Tags: lines with model keys labeled in place; site renders
  chips. Remaining: digests.json/meta emission + item-level
  tags (item_tags stays schema-ready).
  design).
- **Sketch:** mechanical branch/agency taggers (zero tokens); LLM 1–3
  word discovery keys as a new §3a surface (`TAG_PROMPT_VERSION`, cheap
  tier, lexicon-gated, labeled model-derived); chips on section
  headers, tags in digests.json + HTML meta + agent surfaces; GUIDE
  §2/§6 amendment precedes.

**OB-10 — IMAP IDLE for email**
- **Gap:** email collects on a 15-minute poll, not push.
- **Trigger:** a real bulletin-latency need the poll cadence can't
  meet.
- **Sketch:** IDLE loop with reconnect/backoff inside EmailWorker;
  keep the poll as fallback.

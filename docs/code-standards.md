# FAPD code standards

*Adopted 2026-07-30, adapted from the operator's sibling projects. Read
before any non-trivial code change. Last reviewed: 2026-07-30.*

## §0 Why this exists — and what kind of document it is

These standards are **descriptive first**: the codebase already follows
them, and this file makes drift visible. FAPD's editorial machinery
(GUIDE §2, §6) only works if the code is testable and deterministic —
validation gates that can be unit-tested, renders that are pure
functions of stored state, LLM layers that are idempotent and
independently versioned. The standards below are the engineering
posture that makes those guarantees checkable.

## §1 Seams inventory (the injection points that exist — extend this table)

Every external dependency is injectable through an optional constructor
or keyword parameter with a config/global default. **No DI containers —
optional parameters are the whole pattern.**

| Seam | Where |
|---|---|
| `LLMClient(db_path=, runner=, backend=)` | `src/fapd/llm.py` — runner fakes the CLI; backend fakes the API |
| `CLIBackend(runner=)` / `AnthropicBackend(client=)` | `src/fapd/llm.py` |
| `HttpClient(...)` pacing/log seams | `src/fapd/client.py` |
| `MailboxClient(...)` + `poll_mailbox(dkim_verifier=)` | `src/fapd/email_sources.py` |
| `run_concurrent(client_factory=, wayback_factory=, conn_factory=)` | `src/fapd/agencies.py` |
| `Supervisor(sources_builder=)` | `src/fapd/collect.py` — the source-health refresh, injectable so a test drives the cadence without rendering |
| `SourceAdapter.items(body, content_type)` | `src/fapd/agencies.py` — the enumeration seam: a source's shape (feed, XML index, JSON API) is the adapter's business, the poll loop's invariants are not |
| `SourceAdapter.request_params()` | `src/fapd/agencies.py` — the request seam: page size, sort order and any credential for the index fetch. Credentials go here and never into a URL string, because `HttpClient._redacted_params` is what keeps them out of the fetch log |
| `SourceAdapter(entry)` | `src/fapd/agencies.py` — the registry entry the adapter is polling, injected by `adapter_for`; optional, so construction without one stays valid. It carries the index URL (a listing page's hrefs are relative and `items()` is handed bytes, not a URL) and the entry's per-source hints |
| `stage_email(conn, entries=, mailbox_factory=, poll=)` | `scripts/run_pipeline.py` |
| `db.connect(db_path=)` | `src/fapd/db.py` — tests use `tmp_path` DBs |
| `Supervisor(...factories...)` | `src/fapd/collect.py` (continuous ingestion) |
| `source_health(entries, pipeline_db=, fetch_db=, today=, window_days=)` | `src/fapd/health.py` — reads both DBs read-only; the date seam makes a trailing window testable |
| `build_site(digest_dir, out_dir, pipeline_db=, fetch_db=)` | `src/fapd/publish.py` — carries the health seam through to the site build |

New code that talks to the network, a subprocess, a clock, or an LLM
**must** expose the same shape of seam and add a row here (same commit).

## §2 Rules for new code

Deviations need an explicit comment explaining why.

1. **Module docstrings cite the GUIDE section they implement** —
   `client.py`, `db.py`, `llm.py` all do; the docstring is the contract
   pointer, not decoration.
2. **Stdlib-first.** A new dependency is an operator discussion, not an
   import. (The dep list is nine packages; keep it boring.)
3. **DI via optional parameters with config defaults.** See §1. No
   containers, no registries-of-factories, no frameworks.
4. **Pure functions over mutable state; side effects at the edges.**
   Selection (`rules.py`), rendering (`report.py`), doc generation
   (`sources.render_doc`) are pure functions of stored state; writes
   live in narrow `_store`/`_log` functions.
5. **Deterministic render, zero LLM at render time.** GUIDE §6 rule 2
   verbatim: an LLM call that could have been a SQL query is a bug.
   Re-rendering a digest or the site must always cost zero tokens.
6. **Idempotence is the default contract.** Sync is watermarked; extract
   is staleness-keyed; summaries are keyed by
   `(package, granule, prompt_version)`; a rerun that changes nothing
   must cost nothing. New pipeline stages follow suit.
7. **Three similar lines beat a premature factory.** Build the one; copy
   for the second; extract on the third.
8. **Every state-changing surface gets a programmatic seam** so an agent
   or test can drive it without a human — that is how this project's
   features get verified (see §5).
9. **Fail loud on missing config; degrade disclosed on runtime
   failures.** A missing API key raises; a mailbox outage is reported
   and the run continues (`stage_email` contract). Never silently skip.

9. **Outbound links open in a new tab, sitewide** (operator rule,
   2026-07-30). Any link whose href leaves fapd.info gets
   `target="_blank" rel="noopener noreferrer"` — so a reader following a
   citation to the official record never loses the digest they were
   reading. This is enforced in ONE place, `publish._externalize_links`,
   applied to whole rendered pages inside `_render_page`; do not add
   `target` by hand at call sites, and do not add a second rendering
   path that bypasses `_render_page`. Same-site links, fragments, and
   non-HTTP schemes (`mailto:`) keep default behavior.

10. **The site ships no script except one** (operator request,
   2026-07-30). Presentation is server-rendered and complete without
   JavaScript; the single exception is `publish._LOCAL_TIME_JS`, which
   appends the reader's local time beside already-rendered UTC stamps on
   `/today.html`. Any new script must clear the same bar: inline (no
   external resource), no network call, no storage or cookies, purely
   additive to content that is already correct without it — and the
   public privacy claims must be updated in the same commit. Interactive
   presentation should reach for CSS first; the keyword filter's
   `:target` pattern is the worked example.

## §3 Worked example — `stage_email`

The three contracts, each pinned by a test through injected seams
(`tests/test_scripts.py`):

1. Unconfigured mailbox → **reported skip** (`configured: False`,
   mailbox never touched).
2. Working poll → **aggregated counts** returned and printed.
3. Poll raises → **error captured, run continues** — "the gap is
   reported, not hidden."

This is the template: contracts stated in the docstring, seams in the
signature, one test per contract.

## §4 What "modular" does NOT mean

- No plugin registries where a dict suffices (`ADAPTERS` is a dict; the
  registry drift-test keeps it honest).
- No abstract base classes with one implementation. `SourceAdapter`
  earns its base-class status with four concrete variants and a frozen
  four-method contract.
- No config knobs for things that never vary. Access-policy constants
  are code on purpose (GUIDE §4) — making them configurable would make
  politeness an operator mood.
- No refactoring sweeps that ship no behavior. Extract shape when the
  third copy appears, not before.

## §5 Test layering

- **Stub-injection, never network.** No test touches the internet, the
  real mailbox, the `claude` CLI, or the Anthropic API — fakes go in
  through §1 seams. No monkeypatching internals when a seam exists.
- **Shared corpus in `tests/conftest.py`** spans every selection rule;
  rule changes update the corpus and `EXPECTED_RULES` together.
- **Real SQLite at `tmp_path`** — never mock the DB; the SQL is part of
  the behavior under test.
- **Scripts are tested as imported modules** (conftest puts `scripts/`
  on sys.path); `main()` orchestration gets a wiring smoke with stages
  stubbed.
- Pin *contracts*, including degraded modes (validation refusals,
  outage continuations, empty states).

## §6 Logging

- Two-layer rule per GUIDE §4: machine log (the DBs — nothing can
  bypass them) + human narrative (`data/logs/`).
- **No interpolation in the message string** — variable values ride as
  printf-style arguments (`logger.info("%s: %d items", src, n)`), never
  f-strings into the message. Agents and greps parse logs; one grammar.
- Every LLM call and every HTTP attempt is ledgered *before* the
  response is examined — failures included.

## §7 Verification protocol (run before calling work done)

1. `uv run ruff check src/ scripts/ tests/`
2. `uv run pytest -q`
3. Affected-script smoke: `run_pipeline.py` stages via tests,
   `collect.py --once --no-llm`, `digest.py --date` as applicable.
4. Prompt changes additionally follow GUIDE §3a (version bump, ledger
   purpose, regeneration scope stated in the WORKLOG entry).
5. Registry edits: `scripts/sources_doc.py` + drift test in the same
   commit.

(Automating 1–3 as one script is ops-backlog OB-7.)

## §8 How this document changes

Rule changes land **in the same commit** as the code that motivates
them, with a dated line below. Date-only bumps without content review
are forbidden.

- 2026-07-30 — created (adoption push).
- 2026-07-31 — §1 gains the `SourceAdapter.request_params()` row, added
  with the `api` adapter (Congress.gov bill actions): the first source
  whose index fetch carries a credential, and the reason `api_key`
  redaction moved down to `HttpClient` where no subclass can forget it.

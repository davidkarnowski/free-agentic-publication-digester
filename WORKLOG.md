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

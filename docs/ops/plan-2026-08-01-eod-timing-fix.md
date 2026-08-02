# Stop the EOD re-fire loop and fix the publication-day boundary

## Context

Right now, at **22:58 ET on 2026-08-01**, `digests/2026-08-01.md` is published on
the public repository and the live site — a digest for a day that has not ended.
Worse, the pipeline is not finished with it: **35 automated evidence commits** have
landed, firing every ~20–25 minutes since 16:01 UTC and continuing (newest 02:16
UTC, ~40 minutes ago). Each one is a full `run_pipeline.py`: sync, analyze, compose,
tags, render, insight — a complete LLM chain, roughly hourly, all day.

Three independent defects combine to produce this. All three are already fixed in
the working tree on branch `bug/eod-timing`; the suite is green at 489 tests. What
remains is one lint error, a rebase, the documentation, the merge, and the deploy.

### The three defects

1. **`scripts/digest.py::default_date()` used the UTC day as "today."** It picks the
   newest date strictly before today, on the theory that a day is only complete once
   it has ended. GUIDE §3 was amended on 2026-07-30 to make the publication day
   Eastern; this function was written before that and the amendment missed it. Between
   20:00 ET and midnight ET — four hours every single day — UTC has already rolled
   over, so the day still in progress looks complete. That is the direct cause of an
   Aug 1 digest existing at 22:39 ET on Aug 1.

2. **The EOD done-marker was erased by its own idle cycles.** `run_cycle` stores
   whatever `cycle()` returns as `last_result`, and `eod_due` reads `last_result["date"]`
   to decide whether the day is already finalized. A cycle with nothing due returned
   a bare `{"ran": False}` — which overwrote the row and erased the proof. The next
   cycle therefore saw no completed date, considered the day due again, and ran the
   entire pipeline. That is the ~20-minute re-fire loop, and the 35 commits.

3. **`_run_finalizer()` did not pass its target date.** `EODWorker` computes the
   publication day that just closed (`publication_date(now - 1 day)` = 2026-07-31
   right now) and then invoked `run_pipeline.py` with no `--date`, so the subprocess
   fell through to `default_date()` and chose its own — Aug 1, per defect #1. The
   supervisor and the finalizer disagreed about which day was being published.

### One correction to what I reported earlier

I previously told you the EOD **hour gate** (`hour < config.EOD_ET_HOUR`, with
`EOD_ET_HOUR = 0`) was a fourth defect — "dead code." That was an overstatement.
Because the target is computed as the day *before* now, the targeted day has always
ended, so "due at any hour" is exactly the intended meaning of `EOD_ET_HOUR = 0`.
The gate is inert, not wrong. Three real defects, not four.

## Changes already made (working tree, `bug/eod-timing`)

| File | Change |
|---|---|
| `scripts/digest.py` | `default_date()` calls `sync.publication_date()` instead of `dt.datetime.now(dt.UTC)`. Docstring records why, since the old comment actively asserted UTC. |
| `src/fapd/collect.py` | New `EODWorker._last_finalized()`; `cycle()` carries a `finalized` key through **every** return path. `eod_due` reads `finalized` first and falls back to `date` so rows written before this change still count. |
| `src/fapd/collect.py` | `_run_finalizer(date=None)` appends `--date <target>`. `run_pipeline.py` already accepts it (line 235). |
| `tests/test_collect.py` | Both `finalizer_runner` stubs record the date they receive; two new regression tests — the marker survives a no-op cycle and is persisted to `collector_state`, and the day does not re-fire after idling. |
| `tests/test_scripts.py` | New test freezing the clock at 02:39 UTC / 22:39 ET and asserting `default_date()` returns `2026-07-31`, not `2026-08-01`. |

## Steps to finish

1. **Fix the remaining lint error.** `ruff` I001 on the function-local import block in
   the new `tests/test_scripts.py` test — `import digest` and `from fapd import db`
   need a blank line between them. `uv run ruff check . --fix` resolves it.
2. **Green the gates:** `uv run ruff check .` and `uv run pytest -q` (expect 489 passed).
3. **Rebase onto `origin/main`.** The branch is 28 commits behind; every one is an
   automated evidence commit and none touch `scripts/`, `src/` or `tests/`, so the
   rebase is clean. Confirm with
   `git log --oneline bug/eod-timing..origin/main | grep -v "Daily pipeline evidence"`
   returning nothing before rebasing.
4. **Documentation, in the same commit as the code** (CLAUDE.md §8):
   - `WORKLOG.md` — append a dated entry: the three defects, the 35-commit evidence
     trail as the measurement, and the correction about the hour gate.
   - `CLAUDE.md` §9 — add: *a worker's `cycle()` return value is durable state, not a
     status line; every return path must carry the keys `eod_due` reads.* This is the
     generalizable lesson and the one most likely to be reintroduced.
   - `CLAUDE.md` §9 already carries the Eastern-boundary rule; extend that bullet to
     name `scripts/digest.py::default_date()` as a call site the 07-30 amendment missed,
     so the next person auditing that rule has the full list.
5. **Commit** on `bug/eod-timing` with a narrative body, `Co-Authored-By` per GUIDE §9.
   Fast-forward merge to `main`, push.
6. **Deploy to the VPS** — `deploy/vps/scripts/deploy.sh`, then restart the backend
   container so the supervisor picks up the new `collect.py`. **Approving this plan is
   the explicit VPS authorization required by CLAUDE.md §12.** Until this deploy lands,
   the loop keeps firing a full pipeline roughly every 20 minutes.
7. **Verify on the VPS:** tail the supervisor log across at least two EOD cycles and
   confirm exactly one `EOD finalizer firing` line, that `collector_state`'s `eod` row
   retains `finalized` through idle cycles, and that no new evidence commit appears
   until after 00:00 ET on Aug 2.

## What happens to the premature Aug 1 digest — nothing manual

No cleanup commit is needed, and none should be made. After the fix, at 00:05 ET on
Aug 2 the EOD target becomes `2026-08-01`; the stored marker reads `2026-07-31`, which
is less than the target, so the day is due. The finalizer then runs
`run_pipeline.py --date 2026-08-01` and re-renders the digest over the complete day.
The premature version is superseded in place, and the 35 commits stay in history where
they belong — they are the evidence that produced this diagnosis, and CLAUDE.md §8
forbids tidying them away.

Worth checking after that run: `digests/2026-07-31.md` exists on `origin/main` and was
produced under the same broken code path, so confirm it covers the full Eastern day
rather than a truncated one. If it is short, a single re-render with `--date 2026-07-31`
fixes it, committed under the evidence exemption.

## Verification

- `uv run ruff check .` clean; `uv run pytest -q` at 489 passed.
- The two new `tests/test_collect.py` tests fail against the pre-fix `cycle()` and pass
  after — that is the specific proof the re-fire is closed.
- The new `tests/test_scripts.py` test fails against the pre-fix `default_date()` — the
  frozen 22:39 ET clock is the exact condition under which this shipped.
- Post-deploy, the observable success criterion is negative and time-bound: **no evidence
  commit between the deploy and 00:00 ET on 2026-08-02**, then exactly one.

---

## Appendix — deferred: local dev Docker stack

Preserved from the earlier planning round. You rejected it with a question that
identified a real hole: *"How does our local dev stack access source content if the VPS
is the holder of the db?"* Local `data/fapd.db` holds 5,383 extracted rows against the
VPS's 11,744, and has **zero** rows for usps, odni, senate or congress — so a stack
seeded from local data cannot reproduce the backfill bug it exists to catch. **The
revision needed before this is worth re-proposing:** `dev-seed.sh` must pull cold
`VACUUM INTO` snapshots from the VPS over scp, read-only, rather than copying local DBs.
Everything below still stands apart from the seeding source.

### Shape

```
deploy/dev/          NEW — project name `fapd-dev`, own volumes, own containers
  docker-compose.yml
  .dockerignore              (must equal deploy/vps/.dockerignore — pinned by test)
  dev.env.example            → copied to deploy/dev/.env (gitignored)
  README.md                  runbook + the fidelity notes below
  scripts/dev-up.sh          stage → build → seed → up → render → report URL
  scripts/dev-seed.sh        cold VACUUM INTO snapshots (source: VPS, per above)
  scripts/dev-down.sh        down, with a --wipe flag for the volumes
  repo/                      staged tree (gitignored) — the build context
deploy/common/
  repo-excludes.txt    NEW — one exclude list, used by BOTH deploy.sh and dev-up.sh
```

### The build must reuse the production Dockerfile

`deploy/vps/Dockerfile.backend` ends with `COPY repo/ /app`, and `repo/` is created only
by `deploy.sh`'s second rsync — **so `docker compose build` cannot run on a laptop
today.** That is the one hard blocker. Fix without touching the Dockerfile: `dev-up.sh`
stages `deploy/dev/repo/` locally with the *same* rsync excludes, and the dev compose
builds with `context: .` and `dockerfile: ../vps/Dockerfile.backend`. Extract the
exclude list to `deploy/common/repo-excludes.txt` so the two staging steps cannot drift;
this is the only edit to a production file and must be verified as a no-op by comparing
rsync dry-runs before and after.

### Two modes

**Default — render (offline, zero tokens, zero requests):** a `render` service running
exactly the two commands `deploy.sh` runs post-up (`build_site.py`, then
`publish.build_today`), `restart: "no"`, with `web` serving at **http://localhost:8080**.
This is the loop that would have caught the backfill bug.

**Opt-in — live collection** (`--profile live`): `scripts/collect.py --once --no-llm
--no-wayback`. Never `--eod`. `--no-wayback` does not exist yet and is the one
application change required; `Supervisor` already takes `wayback_factory`, so the flag
passes a stub whose `save()` returns `None`. Without it a dev run writes real
Save-Page-Now submissions to a public archive.

### Guardrails — must be impossible, not merely discouraged

| Hazard | Why it matters | Guard |
|---|---|---|
| `--eod` on a fresh volume | `EOD_ET_HOUR=0` and a fresh `collector_state` has no `eod` row — the full pipeline runs within seconds of boot, LLM chain included | `--eod` appears nowhere in dev compose; pinned by test |
| `--no-llm` does not stop EOD spend | It only gates `AnalyzeWorker`; `run_pipeline.py` has no such flag and builds `LLMClient` unconditionally | default mode never runs the supervisor at all |
| Evidence push | `FAPD_EVIDENCE_PUSH=1` + a mounted key would `git push origin main` on the production repo | no `./secrets` mount; var absent from `dev.env.example`; `dev-up.sh` refuses to start if it is set |
| Shared govinfo quota | Budgets count rows in the **local** fetch log, so dev and production each believe they are under budget while sharing one api.data.gov quota | live mode requires a **separate dev key** |
| Production identity | `CONTACT_EMAIL` feeds the User-Agent sent to ~22 real `.gov` hosts | dev env sets a dev contact string |
| `SITE_BASE_URL` | `.env.example` ships `https://fapd.info` pre-filled, so a copied env makes dev artifacts claim to be production | `dev.env.example` sets it empty |
| Repo pollution | `provenance.export_manifest` and `sources_doc.py` write into the git tree, not `data/` | the staged `deploy/dev/repo/` is a copy, gitignored |

### Fidelity — deliberate divergences and their cost

Matches production exactly: the backend image recipe and every layer, the
`nginx:1.30-alpine` pin, the stock nginx config, the site handoff via a named volume
(`:ro` for web, rw for backend), the `data/` layout and DDL-on-connect, the two post-up
render commands, and the Eastern publication-day boundary.

Differs deliberately: no edge proxy (so the branded 404, security headers, HSTS and
`limit_req` cannot be validated locally — a blind spot to state in the README rather
than discover); no TLS (mitigated by `SITE_BASE_URL` being empty, so links are
root-relative); `web` is not on an `--internal` network, so dev cannot prove the
zero-egress property; no secrets, no evidence push, no EOD; separate project name and
volumes so it cannot collide with anything.

### Open question carried forward

Should `dev-up.sh` be a **mandatory** pre-flight for `deploy.sh` (deploy refuses unless
a dev render succeeded), or stay advisory? Mandatory is stronger but couples a laptop
Docker daemon to every deploy.

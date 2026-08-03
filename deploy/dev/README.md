# FAPD local dev stack

Run the production rendering path on your machine, against a cold
snapshot of the **production** databases, before anything deploys. This
is the integration test the 2026-07-31 `/today` backfill bug proved was
missing: the unit suite was green while the live page listed 2021 press
releases as today's news, because no test rendered a page from a
database containing a real feed's archive.

## Quick start

```sh
deploy/dev/scripts/dev-seed.sh   # operator-gated: pulls VPS snapshots (see below)
deploy/dev/scripts/dev-up.sh     # stage -> build -> up -> render
open http://localhost:8080       # index, digests, /today — production-shaped data
deploy/dev/scripts/dev-down.sh   # stop (--wipe to also drop the volumes)
```

`dev-up.sh` creates `deploy/dev/.env` from `dev.env.example` on first
run; render mode needs no edits and no secrets. Re-run `dev-up.sh` after
any code change — it restages and re-renders in one step.

## What it is

The **same backend image recipe as production** (`../vps/Dockerfile.backend`,
byte-for-byte: same base, uv/Node/claude layers, `uv sync --frozen
--no-dev`), built from a locally staged `repo/` using the same exclude
list deploy.sh uses (`deploy/common/repo-excludes.txt` — one list, two
stagers, drift-tested). The same `nginx:1.30-alpine` pin, the same
site-volume handoff, and the same two post-up render commands deploy.sh
runs on the box (F-009: the site volume seeds from the image only on
first mount, so rendering is always explicit).

## Seeding (why the data comes from the VPS)

The laptop's own `data/` cannot reproduce production — at the time this
stack was designed it held roughly half the extracted rows and none of
the sources whose archives caused the backfill bug. `dev-seed.sh` pulls
cold `VACUUM INTO` snapshots of the three databases from the box
(checkpointed, WAL-free — a live-file copy arrives corrupt; 2026-07-30
cutover lesson) and loads them into the dev volume with a `SEEDED`
vintage stamp. Only the three DBs move: `extracted_texts` carries the
document text, so rendering needs neither `data/raw/` nor captures.

**Authorization:** the seed pull reads production state (and writes only
a scratch dir it deletes). Per the gate in `deploy/vps/README.md`, run
it only on the operator's explicit ask.

## Two modes

| Mode | Command | Network | Tokens | Secrets |
|---|---|---|---|---|
| **Render** (default) | `dev-up.sh` | none | zero | none |
| **Live collection** (opt-in) | `docker compose --profile live ... run --rm collector` | real `.gov` requests | zero (`--no-llm`) | separate dev `GOVINFO_API_KEY` |

Live mode is one serial cycle (`--once`) — never the supervisor daemon —
with `--no-wayback` so a test run never writes to a public archive, and
a **separate dev api.data.gov key** because budgets are counted from
each machine's own fetch log: dev and prod sharing a key would each
believe they are under the publisher's limit while jointly exceeding it.

## Guardrails (enforced, not advised — pinned by tests/test_dev_stack.py)

- The end-of-day flag appears nowhere in `deploy/dev/`: on a fresh
  volume the finalizer would fire within a cycle of boot (no
  `collector_state` row), running the full pipeline, LLM chain included.
- No `secrets/` mount and no `FAPD_EVIDENCE_PUSH`; `dev-up.sh` refuses
  to start if the variable is set to `1` anywhere. This stack must be
  physically unable to push to the production repository.
- `dev-up.sh` refuses an absolute `SITE_BASE_URL` — dev artifacts never
  claim a real host.
- `deploy/dev/.dockerignore` is byte-equal to `deploy/vps/.dockerignore`.
- The origin re-flip deploy.sh performs on the box (F-008) is VPS-only
  and deliberately absent here.

## Fidelity — what dev deliberately does NOT prove

- **No edge proxy** (web publishes `8080:80` directly): the branded 404,
  security headers, HSTS, and rate limiting live in the shared proxy and
  cannot be validated locally. Known blind spot — stated, not
  discovered.
- **No TLS**; mitigated by `SITE_BASE_URL` staying empty (root-relative
  links).
- **`web` has egress here** — dev cannot prove production's zero-egress
  property (`fapd_edge` is `--internal` on the box).
- ~~Resource limits and log rotation exist here and not yet in prod~~ —
  the divergence closed 2026-08-02: the production compose copied this
  stack's tested block (review D19/R4), plus a backend DB-heartbeat
  healthcheck prod alone carries. The dev stack ran the block first by
  design.
- Data is as fresh as the last `dev-seed.sh`; the `SEEDED` stamp in the
  data volume records the vintage, and `dev-up.sh` prints it.

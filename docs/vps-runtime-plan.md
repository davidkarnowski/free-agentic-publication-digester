# VPS Runtime Plan — the pipeline runs on a VPS; GitHub holds the record

> **STATUS: DONE / SUPERSEDED (2026-07-30).** Everything this plan
> deferred landed the same day it was written: provisioning, deploy,
> TLS, the backend container, the bot identity, and evidence pushes
> (ops-backlog OB-1/OB-11). One decision changed in execution:
> scheduling is NOT cron/systemd — the in-container `EODWorker` owns
> it (docs/continuous-ingestion.md §9 is the design authority now).
> Remaining threads live in ops-backlog: rDNS, Web Bot Auth (OB-3),
> backup policy (OB-6). The body below is preserved as the decision
> record; do not build from it.

*Adopted 2026-07-30, superseding [`gh-native-plan.md`](gh-native-plan.md)
before its T2–T5 evaluation ran. This push records the decision and
builds the one piece of it that is code (the API LLM backend); VPS
selection and provisioning are a later push.*

## The decision

The daily pipeline executes on a VPS under a scheduler (cron or a
systemd timer). GitHub keeps everything it is actually good at for this
project:

- **The public repository** — code, governing documents, registry.
- **CI** — the test suite and lint run on every push and PR
  (`.github/workflows/ci.yml`).
- **The integrity record** — digests, provenance manifests (hash-chained
  day to day), SOURCES.md, and the site are committed by the pipeline
  run and pushed with a bot identity, so GitHub history remains the
  independent ordering witness GUIDE §7 already names. Accountability
  lives in our own committed artifacts, never in platform logs — that
  conclusion from the GH-native deliberation stands unchanged.

## Update 2026-07-30 (evening): hosting resolved — shared VPS, Docker stack

Same-day development: `fapd.info` now points at the VPS the operator
already runs for another project, and the **placeholder site is live
over HTTPS** (Let's Encrypt, webroot method, auto-renewing). Decisions
this resolves and reshapes:

- **The stack is fully containerized** (operator direction). The
  bare-host "Python + uv + cron" shape below is superseded by a Docker
  compose stack at `/opt/fapd`, source of truth in this repo's
  [`deploy/vps/`](../deploy/vps/): `fapd-web` (nginx, inbound-only — it
  sits solely on an external `--internal` Docker network with zero
  egress) and, next push, `fapd-backend` (collector supervisor + EOD
  finalizer; egress-only on its own private network, no published
  ports, unreachable from anything public). Backend hands the built
  site to web through a read-only named volume — never a socket.
- **Traffic sorting** happens in the cohabiting project's edge proxy,
  which terminates TLS for both hostnames and is the only container
  bridging the two projects' networks. The proxy bundle and the box
  dossier live in the operator's private tree, not this repo.
- **EOD scheduling moves inside the backend supervisor** (no host
  cron/systemd dependency; the host needs only Docker) — see
  `docs/continuous-ingestion.md`.
- **LLM billing (operator decision, 2026-07-30 evening): the VPS runs
  `LLM_BACKEND=cli`**, billing the operator's Claude subscription via a
  `claude setup-token` credential — the claude.ai usage-credit balance
  covers it, whereas API keys draw on a separate (unfunded) Console
  balance. The API backend remains built, tested, and one `.env` edit
  away (`LLM_BACKEND=api` + a funded `ANTHROPIC_API_KEY`) if the
  subscription coupling ever becomes a constraint. Never set both the
  OAuth token and an API key: the key shadows the token and silently
  switches billing.
- The stable-IPv4/rDNS identity argument below is unchanged and now
  concrete: the box exists and its identity can anchor M-23-22 letters
  and verified-bot registrations.

## Why a VPS over hosted runners

The identified-client posture is the project's access ethic, and a VPS
is the shape that strengthens it rather than trading it away:

- **Stable IPv4 + reverse DNS** — identity infrastructure that
  verified-bot programs and M-23-22 engagement letters can point at.
  Hosted runners offered shared, changing IPs and would have made Web
  Bot Auth signing a *prerequisite* for identity; on a VPS it becomes a
  strengthening layer instead.
- **State stays local.** `data/` (SQLite databases, raw archive,
  captures) lives on the VPS disk. The GH-native plan's rolling-Release
  state store — its most intricate machinery — is simply unnecessary.
- **No 6-hour job cap, no shared-runner variability**; crawl-delay-heavy
  sources cost wall-clock only.

What is consciously given up: the project no longer "lives completely on
GitHub," and the VPS is a second platform to harden, pay for, and keep
patched. The self-hosted-*runner* variant (GitHub Actions dispatching to
our machine) is rejected: it inherits the security rule against
attaching self-hosted runners to public repos, which would force a
private ops repo — plain scheduling on the VPS with results pushed back
is simpler and equally accountable.

## Kept from the GH-native work

- **`ci.yml`** — promoted to `main` (branch filter reduced to `main`).
- **The AnthropicBackend** (`LLM_BACKEND=api`) — built in this push, on
  `main`, with a per-tier model mapping so hosted runs are not bound to
  the operator's `claude` CLI subscription. The CLI remains the local
  default. Note the VPS could run either backend; the API backend keeps
  the server decoupled from CLI tooling and its update cycle.
- **The committed daily run-summary** (`provenance/runs/YYYY-MM-DD.md`)
  remains a good idea and moves to this plan's backlog: per-client
  request counts vs budgets, items ingested, validation verdict, stage
  timings — public execution transparency that outlives any platform.

Dropped: the rolling `pipeline-state` Release, `pipeline.yml`, and the
monthly Release state bundles (the S4 storage design returns to its own
schedule, unforced by runner statelessness).

## Deployment outline (later push)

1. Provision: small VPS, Python 3.12+ + `uv`, repo clone, `.env` from
   the operator (govinfo key, contact, IMAP, `ANTHROPIC_API_KEY`,
   `LLM_BACKEND=api`, `SITE_BASE_URL=https://fapd.info`).
2. **First-run smoke, in order:** `scripts/verify_key.py`;
   `scripts/verify_mailbox.py`; a single manual `LLMClient` call on the
   API backend (one cheap-tier request, verified in the ledger with
   `backend=api` and the resolved model id) — before any full run.
3. Bot git identity (`fapd-pipeline`) with a deploy key limited to this
   repository; evidence commits distinguishable from human commits.
4. Scheduler: one daily `run_pipeline` off-peak US Eastern (GUIDE §4),
   with `concurrency` guaranteed by the scheduler (no overlapping runs).
5. rDNS set to a name under the project domain; User-Agent unchanged.
6. Backlog: run-summary emitter; Web Bot Auth request signing (Ed25519,
   JWKS under the site's `/.well-known/`) as the portable identity
   layer; backup policy for `data/` (raw is re-fetchable from govinfo;
   the SQLite databases and captures are not).

## Reversal criteria

This is infrastructure, not doctrine. If VPS operation proves
unsustainable (cost, maintenance burden, reliability), the GH-native
plan remains fully documented with a tested CI base and a written
evaluation path — the way back is a branch away.

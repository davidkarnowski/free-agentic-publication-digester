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
- **Done 2026-07-30:** the backend container runs the pipeline on the
  VPS (supervisor + EODWorker, egress-only network, `fapd-data`/
  `fapd-site` volumes, server-side `.env`, mounted deploy key); the
  real site serves on fapd.info. deploy.sh carries the test gate,
  load-bearing excludes (F-004), and the post-up steps (F-008/F-009).
  No `/fapd-deploy` skill was built — deploy.sh is the runbook's
  script. Original sketch kept below for the record.
- **Gap (historical):** the VPS served only the placeholder; the
  pipeline ran on the operator machine.
- **Trigger (historical):** operator says go, after the
  continuous-ingestion workstream merges.
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
- **Done 2026-08-02 (as redirected):** the operator ruled NO standing
  cap ("don't token cap at this time, just allow us to throttle when
  needed"). Built as an on-demand throttle instead:
  `FAPD_DAILY_TOKEN_THROTTLE` (unset by default), ledger-counted in
  `LLMClient.complete`, pause-type error the workers already treat as
  our-own-budget backpressure. Engage by setting the variable in the
  box's `.env` and restarting the backend; clear it the same way. The
  per-call prompt-size guard (`LLM_MAX_PROMPT_CHARS`) landed as
  standing policy. GUIDE §6 r8 amended in the same change. The
  runaway-day defense-in-depth remains r14's per-item ceiling + this
  throttle when engaged.

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
  design).
- **Done 2026-07-30 (section layer):** GUIDE §6 r12a; tags.py
  (mechanical branch/agency + batched discovery keys,
  TAG_PROMPT_VERSION, lexicon-gated via the digest); canonical
  Tags: lines with model keys labeled in place; site renders
  chips. Remaining: digests.json/meta emission + item-level
  tags (item_tags stays schema-ready).
- **Sketch:** mechanical branch/agency taggers (zero tokens); LLM 1–3
  word discovery keys as a new §3a surface (`TAG_PROMPT_VERSION`, cheap
  tier, lexicon-gated, labeled model-derived); chips on section
  headers, tags in digests.json + HTML meta + agent surfaces; GUIDE
  §2/§6 amendment precedes.

**OB-12 — Stale-output cleanup in the site render**
- **Gap:** `build_site` (and `refresh_sources`/`build_day`) write outputs
  but never remove pages they no longer produce. Found live 2026-08-03:
  the retired 2026-07-23/24 digest pages were still sitting in the VPS
  site volume — and still being *served* — after the retirement removed
  them from the repo, and the next `git add site/` (the backfill's
  evidence commit) resurrected them into the record until a follow-up
  guarded commit deleted them and the missed `site/assets/2026-07-23/`.
- **Trigger:** the next content retirement, or any renderer change that
  renames an output path.
- **Sketch:** either a manifest-of-expected-outputs sweep at the end of
  `build_site` (delete files under managed directories that this render
  did not produce, with a printed list — loud, never silent), or a
  documented retirement runbook step: remove from repo AND volume in the
  same operation. The evidence-commit guard already caught the symptom;
  the fix belongs at the source.
**OB-10 — Email IMAP IDLE (push instead of poll)**
*(Header restored 2026-08-05: this entry had lost its `**OB-10 — …**`
line and was dangling after OB-12's Sketch, making it read as part of
that item. It is referenced by ID from
[docs/pre-publication-todo.md](../pre-publication-todo.md); the ID is
not reusable.)*
- **Gap:** email collects on a 15-minute poll, not push.
- **Trigger:** a real bulletin-latency need the poll cadence can't
  meet.
- **Sketch:** IDLE loop with reconnect/backoff inside EmailWorker;
  keep the poll as fallback.

**OB-13 — fail2ban `sshd` jail is inert**
- **Gap:** the jail's journal match is `_SYSTEMD_UNIT=sshd.service`, but
  the unit on this box is `ssh.service` — 1,145 journal entries under
  `ssh.service` over 7 days versus 1 under `sshd.service`. The jail
  reports `Total failed: 0` / `Total banned: 0`. Found 2026-08-05.
  Severity is bounded by key-only auth (`PasswordAuthentication no`,
  `PermitRootLogin no`, `MaxAuthTries 3`): lost defense-in-depth and
  lost visibility, not an open door.
  **Traffic correction (same day):** the first pass of this entry cited
  "183 attempts from a single IP" as evidence of ongoing scanning. That
  was a bad grep — it pulled `from <ip>` out of every sshd line,
  including successful ones. `98.97.136.86` is 183 *accepted publickey*
  and 0 invalid-user; `185.230.126.195` is 90 accepted and 0 invalid.
  Both are the operator's own sessions. The only genuine attack traffic
  in 14 days is one 84-second burst from `161.35.210.58` (DigitalOcean)
  on 2026-07-30 trying `sol`, `alertmanager`, `alertuser`, `apache`,
  `app` — a crypto-scanner wordlist. The box is quiet; the jail was
  still broken, which is why this stayed a finding.
- **Trigger:** ~~immediate on the next authorized VPS write window~~
  **Done 2026-08-05.**
- **Done 2026-08-05:** `journalmatch = _SYSTEMD_UNIT=ssh.service +
  _COMM=sshd` added to jail.local's `[sshd]` block (the filter file is
  package-owned and would revert on upgrade; jail.local already
  overrides `port` there). Applied by
  `scripts/staged/2026-08-05-fail2ban-sshd-journalmatch.sh`; rollback
  artifact `/etc/fail2ban/jail.local.bak.20260805T144738Z` on the box.
  Verified by replaying the journal through the filter with
  `fail2ban-regex`: **1,445 lines, 5 matched** where it matched 0
  before — counters alone prove nothing right after a reload, since
  `findtime` is 10m. Those 5 are exactly the 07-30 burst, which at
  `maxretry=5`/`findtime=10m` would now earn a ban.
- **Deliberately not changed:** `mode = normal`. Aggressive mode would
  also catch banner/kex probing, but it matches `Connection closed by
  ... [preauth]`, which the operator's own multiplexed SSH generates
  constantly — it would ban us. Revisit only with an `ignoreip` for
  operator egress, and note those addresses are dynamic.

**OB-14 — Container hardening (`fapd-web`, `fapd-backend`)**
- **Gap:** both containers run as **root** with no `cap_drop`, no
  `read_only` root filesystem, and no `no-new-privileges`. The one that
  matters is `fapd-backend`, which parses untrusted fetched content
  (XML, HTML, PDF, RFC-5322 email) as root — the CVE guide itself calls
  that the largest exposure in the system. Measured 2026-08-05.
- **Trigger:** the next `deploy/vps/` change that already requires a
  container recreate, so the hardening rides along instead of buying its
  own outage window.
- **Sketch:** `security_opt: [no-new-privileges:true]` on both;
  `cap_drop: [ALL]` with the minimum re-added (nginx needs
  `NET_BIND_SERVICE`, `CHOWN`, `SETUID`, `SETGID`); `read_only: true`
  plus explicit `tmpfs` where the volume layout allows. Author in
  `deploy/vps/`, never on the box. Needs a plan-task document — a
  wrong `cap_drop` takes the site down, and the backend writes to
  volumes the read-only flag would otherwise block.

**OB-15 — Edge nginx access log is unrotated and mostly healthcheck**
- **Gap:** `/opt/spiralyst/logs/nginx/access.log` is 68 MB and has no
  logrotate entry — unrotated since 2026-05-23. Separately, 631,522 of
  its 655,769 lines (96%) are the `GET /healthz` probe, which makes real
  traffic hard to read during an incident. Disk is at 39%, so this is
  hygiene, not urgency. *(Correction 2026-08-06: the original entry
  also flagged the spiralyst containers' uncapped docker json logs —
  `/etc/logrotate.d/docker-containers` already rotates ALL container
  logs at host level, daily/50M/keep-3; that half of the gap never
  existed.)*
- **Trigger:** ~~disk above ~70%~~ **Done 2026-08-06** (operator
  approved "both" the same morning).
- **Done 2026-08-06:** both halves live. (1) `/etc/logrotate.d/
  spiralyst-nginx` — daily, keep 14, compressed, `nginx -s reopen`
  postrotate — applied by `scripts/staged/2026-08-06-edge-log-
  rotation.sh`; first forced rotation archived the 69.9MB file and the
  fresh file took the very next request (reopen proven). Two lessons
  are in the script as comments: the log directory is group-writable
  dkarnowski-owned, which logrotate refuses without an explicit
  `su dkarnowski dkarnowski`; and the self-check must NOT probe
  /healthz, because (2) `access_log off` now covers the healthz
  location — authored in the Spiralyst tree (all four mode confs),
  applied to the live `full.conf` with an inode-preserving in-place
  write (F-002: a bind-mounted single file must keep its inode),
  `nginx -t` + reload, verified by the healthz line-count freezing
  across two healthcheck cycles while both public sites stayed 200.
  Rollback artifacts: `access.log.1`/`error.log.1` on the box; the
  logrotate entry is one `rm` to revert.

**OB-16 — govinfo USCOURTS `/zip` 503 retry cost**
- **Gap:** 4,745 `503`s since 2026-08-01, every one of them a
  `USCOURTS-*/zip` request, ~370/day and ~17% of the daily request
  budget. They are transient by design on govinfo's side — the zip is
  built on demand — and they do resolve: of 400 distinct 503 URLs
  sampled, **400** later returned 200. So the work completes and the
  cost is real. This is the mechanism behind the 2026-08-01 budget
  breach (119.6% of cap).
- **Trigger:** daily budget use back above ~80%, or any day the cap is
  breached again.
- **Sketch:** honor `Retry-After` by deferring the package to a later
  cycle instead of retrying inside the current one, so a 503 costs one
  request per cycle rather than a burst. Per GUIDE §4 the answer is
  fewer requests, never faster ones, and failed requests keep counting
  against the budget — that is deliberate and stays.

**OB-17 — CVE sweep refactor to deterministic sources**
- **Gap:** `AGENT-CVE-GUIDE.md` §2 prescribes open-ended web research,
  which is slow, approval-heavy, and less accurate than machine-readable
  sources. Demonstrated 2026-08-05 (first real sweep): one OSV batch
  call cleared all 19 Python dependencies, and two throwaway-container
  commands gave distro ground truth for the images.
- **Trigger:** the next weekly sweep.
- **Sketch:** deterministic layers — OSV batch API from `uv.lock` (with
  a known-vulnerable control row so a silent API failure cannot read as
  "clean"), `apt list --upgradable` / `apk version -l '<'` in
  **throwaway** containers, CISA KEV JSON for exploitation status —
  plus a *narrow* researched layer for the runtime/toolchain only
  (CPython, nginx, Node, OpenSSL, Docker, the CLI). Keep that layer:
  OSV does not index CPython, and the scanner-only path would have
  scored two real things clean — CVE-2026-15308, and the fact that
  `fapd-backend` uses a bundled expat 2.7.4 while the patched system
  `libexpat1` 2.8.2 sits unused beside it. Candidate implementation:
  `scripts/cve_scan.py`, zero-LLM and deterministic.

**OB-18 — No Content-Security-Policy or Permissions-Policy**
- **Gap:** the site sends HSTS, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: SAMEORIGIN`, and `Referrer-Policy:
  strict-origin-when-cross-origin`, but no CSP and no Permissions-Policy
  (verified 2026-08-05). Low exposure — the site is static with no
  user input and no third-party assets — so this is defense-in-depth.
- **Trigger:** any change that introduces a second script, an embed, or
  externally-hosted assets. The multi-media workstream's embed posture
  is exactly such a change and should not land before this does.
- **Sketch:** the site has exactly one inline script (the live page's
  local-time snippet, code-standards §2 r10), so a hash-based CSP is
  achievable without a nonce pipeline: `default-src 'self'`,
  `script-src 'sha256-…'`, `frame-ancestors 'self'`. Set in the nginx
  config in `deploy/vps/`, and add a render-time test asserting the
  inline script's hash matches the header so the two cannot drift.

**OB-19 — Retiring an evidence file now needs a volume cleanup step**
- **Gap:** `digests/` and `provenance/` became named volumes on
  2026-08-07 (P3, F-021) so an unpushed evidence commit can survive a
  container rebuild. Docker seeds a named volume from the image only
  when the volume is **empty**, so a rebuild never refreshes a populated
  one. Deleting a digest, manifest or day view from the repository
  therefore does **not** remove it from the box: the file persists in
  the volume, and the next `git add digests/ provenance/` re-commits it.
  This is the F-009 class, now covering three paths instead of one.
- **Precedent:** exactly this happened on 2026-08-03 with the site
  volume. The two development-era digests were retired from the tree,
  `build_site` never deleted stale outputs, and the next evidence commit
  resurrected the pages — caught and cleaned by hand the same evening.
- **Trigger:** the next retirement of a digest, manifest or day view —
  or any deliberate deletion under `digests/` or `provenance/`.
- **Sketch:** a short staged script in the servicing-guide §2 shape that
  deletes the named paths from `fapd-digests` / `fapd-provenance` inside
  the container and re-runs `build_site`, with the retired paths as
  preconditions (abort if they are absent — nothing to do) and a
  self-verification that they are gone from the volume, the site volume,
  and the next `git status`. Alternatively fold the cleanup into the
  retirement runbook so the deletion and the volume are one action; the
  hazard is that they are currently two, and only one of them is
  obvious.

# Work Production Log — Free Agentic Publication Digester (FAPD)

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

## 2026-07-30 08:40 PDT — Agent-ops standards adopted from the sibling projects (branch arch/agent-ops-standards)

**Context:** The operator directed FAPD to adopt the operational
standards of their two other projects, both surveyed in depth this
session: agent-ops runbooks, a CLAUDE.md working guide, a code-standards
document, thin-dispatcher skills, a CVE sweep process, branch
discipline, and trigger-driven operational bookkeeping. FAPD had strong
editorial governance and none of this engineering governance.

**Decisions (operator, via Q&A):** main-is-sacred branching with the
evidence-commit exemption (data with an integrity role, scoped by
path); this workstream is itself the rule's first exercise — built on
`arch/agent-ops-standards`, merged only with CI green.

**Work performed (this workstream, committed in sequence):** GUIDE §10
amendments (branch rule, engineering-governance pointers, ops
authorization gates); CLAUDE.md (13 sections — including the
intentional-vs-bug split and the task→file table); docs/code-standards.md
(descriptive-first: the seams and rules the codebase already follows,
made explicit); docs/ops/ suite (portable VPS servicing guide with the
six principles, per-box dossier pointer, read-only health runbook,
plan-task template, staged-scripts convention); ops-backlog
(Gap/Trigger/Sketch) + stable-ID findings register; CVE sweep guide
adapted to FAPD's surface (parsers over fetched government content)
with three skills as thin dispatchers and the .gitignore change that
lets skills be tracked while settings stay local.

**Open questions / next steps:** continuous-ingestion workstream
follows on its own branch; /fapd-deploy skill waits for the backend
deploy runbook (ops-backlog OB-1).

## 2026-07-30 08:25 PDT — fapd.info live: placeholder over HTTPS on the shared VPS, strict Docker segmentation

**Context:** The operator pointed fapd.info's DNS at the VPS already
running another of their projects and directed: reuse the same SSH
management method, sort traffic in the edge proxy, stand up a
dark-theme placeholder container, issue the Let's Encrypt cert by the
same webroot method, and architect everything as a Docker stack with
strict network segmentation between the two projects and between
FAPD's own public-facing and backend containers.

**Work performed:**
- **New `deploy/vps/` in this repo** — the FAPD stack's source of
  truth: compose file (project `fapd`), dark placeholder page carrying
  the full project name, and a deploy runbook with the
  authorization-gate wording. `fapd-web` (nginx, pinned to the same
  stable tag as the edge proxy) sits ONLY on a new external
  `--internal` Docker network `fapd_edge` — no default route, zero
  egress, inbound only via the proxy. Named volumes `fapd-site` /
  `fapd-data` declared ahead of the backend container (next push),
  which will be egress-only on its own network and hand the site to
  the web container through a read-only volume, never a socket.
- **Edge routing** (authored in the cohabiting project's private
  bundle, deployed with its tooling): the proxy joins both edge
  networks — the only bridge between the projects — with fapd.info
  server blocks staged in two deploys: (A) HTTP + ACME webroot first;
  cert issuance (`certbot certonly --webroot`, same account, ECDSA,
  fapd.info + www, expires 2026-10-28, covered by the existing renewal
  reload hook); then (B) the `:443` block. The stage-B config was
  rehearsed in a throwaway `nginx -t` container attached to both
  networks before the live proxy saw it — a missing cert path would
  have crash-looped the proxy and taken the other site down.
- **One real deploy lesson:** the stage-B config change silently did
  not apply — `docker compose up -d` does not recreate a container
  whose only change is a single-file bind mount's content (new inode
  after rsync). Fixed with `--force-recreate proxy`; recorded in the
  cohabiting bundle's README as a standing gotcha.
- **Verified end-to-end:** `https://fapd.info` and `https://www.fapd.info`
  serve the placeholder over HTTP/2 with correct SANs; `http://` 301s;
  the other site unaffected throughout; all three containers healthy;
  `fapd-web`'s network list is exactly `fapd_edge`. Renewal dry-run
  in flight at entry time (certbot's random jitter delay); verdict
  recorded in the next entry if not green.
- **No firewall changes were needed** — 80/443 were already open and
  the webroot flow rides the existing proxy.

**Decisions:** Everything containerized (operator); segmentation as
architecture, not convention — the public-facing container *cannot*
reach the backend or the internet, enforced by Docker network
topology rather than discipline. Hosting question from the launch
checklist: resolved.

**Open questions / next steps:** backend container (collector
supervisor + EOD finalizer) per docs/continuous-ingestion.md — next
push; real site content replaces the placeholder via the fapd-site
volume when it lands.

## 2026-07-30 08:05 PDT — Email sources: gate-3 evaluation and the first seven activations

**Context:** GUIDE §3 gate 5 makes status changes worklog events. This
entry records the gate-3 content evaluation of the 30 registered email
sources and the resulting activations, per the operator's
evidence-based-subset decision.

**The evidence (from the 2026-07-29 mailbox polls, ~45 minutes of
observation):** 20 bulletins from 7 senders produced 38 ingested items,
DKIM verified 38/38 with every verifying key archived. Per source:
usattorneys-email 3 bulletins → 25 items (20 full, 5 teaser; one
bulletin carried sixteen district releases); treasury-email 5 → 5;
justice-email 7 → 3 (heavy cross-channel dedup against the active
justice-newsroom RSS feed — intended first-recorded-wins behavior for a
corroborating channel — plus administrivia filtering); agriculture-email
2 → 2; fsis-email, uscis-email, usps-oig-email 1 → 1 each.

**Activated (7):** usattorneys-email, treasury-email, justice-email,
agriculture-email, fsis-email, uscis-email, usps-oig-email — each with
its gate-3 coverage answer written into the entry notes, as the GUIDE
requires. The usattorneys open question is resolved: district releases
are listed individually (the adapter already parses them so), and the
coverage statement counts every item. The activation also corrects a
disclosure inaccuracy: report.py's AGENCYPR rule text says "all such
releases from active sources are listed," and email items were flowing
under it from planned sources.

**Honest statement about the other 23:** they stay `planned`. Every one
is a confirmed subscription, but ~45 minutes of evening observation
cannot answer gate 3's question — silence in that window is not
evidence of anything. Each entry now carries a dated note: subscription
confirmed, no bulletin observed, window open, activate on first parsed
bulletin.

**Two data corrections in the same pass:** (1) ofr-email and
usattorneys-email carried each other's signup-URL provenance sentences
(the List-Unsubscribe-recovered USDOJUSAO account belongs to
usattorneys; the did-not-resolve caveat belongs to OFR) — swapped back,
with a correction marker in both notes. (2) All 30 email entries'
method strings still said the adapter was "pending build" three
sessions after it shipped; they now name src/fapd/email_sources.py and
its capture/DKIM behavior. PLAW's "would sync once enabled" method
string got the same staleness fix in the validation commit.

**Decisions:** Activation threshold is parsed evidence, not confirmed
subscription — the same standard that kept these entries `planned` on
07-29 now admits exactly seven. The 23 flips happen one at a time as
bulletins arrive, each a worklog event.

**Open questions / next steps:** watch the mailbox over the coming days
and flip silent sources as they deliver; the usattorneys volume
question (does 25 items/day hold?) answers itself in coverage
accounting; component-list splits (USDA, Treasury) wait on observed
distinct streams.

## 2026-07-30 07:20 PDT — Four operator decisions: fapd.info, VPS runtime, API backend, evidence-based email activation

**Context:** Following the morning's state-of-the-project review, the
operator resolved the open decisions blocking the launch path and
scoped a work push.

**Decisions (operator):**
- **Domain: `fapd.info`.** With it, a standing branding rule: public
  surfaces always carry the full name — "Free Agentic Publication
  Digester (FAPD)" — not the bare acronym. Site *hosting* is
  deliberately deferred; this push wires `SITE_BASE_URL` only.
- **Runtime: VPS, not GH-native.** The GH-Actions-only track adopted
  2026-07-29 is superseded before its T2–T5 evaluation ran — the
  operator's judgment, not a failed measurement. The pipeline will run
  on a VPS; GitHub remains the public repo, CI, and the committed
  digest/manifest integrity record (the role GUIDE §7 always assigned
  it). The stable-IP/rDNS identity argument that favored the VPS in the
  original deliberation becomes the plan's centerpiece.
  docs/vps-runtime-plan.md is the active plan; gh-native-plan.md
  carries a superseded header; the gh-native branch stays unmerged as
  evaluation evidence; ci.yml is the one artifact promoted to main.
- **LLM backend: build the Anthropic-API backend now**, behind
  `LLM_BACKEND=api|cli` (CLI stays the local default), with a per-tier
  model mapping (env-overridable) so different models can be tried
  without code edits. GUIDE §6 rule 7 amended accordingly (backends are
  pluggable; ledger records backend + resolved model).
- **Email sources: evidence-based activation.** Only the 7 sources with
  observed, parsed, DKIM-verified bulletins flip to active; the 23
  confirmed-but-silent stay planned with dated notes — the observation
  window (~45 minutes on 07-29) cannot answer gate 3 for them.

**Work performed (docs-first, per the working agreement):** GUIDE §6
rule 7 amendment + §8 "Phase R — Hosted runtime"; gh-native-plan.md
superseded header; vps-runtime-plan.md written (decision, rationale,
what was kept/dropped from GH-native, deployment outline including the
first-run API smoke, reversal criteria); pre-publication-todo.md
domain item closed and scheduling item rewritten to the VPS track.

**Push scope (implementation follows this entry):** CI workflow on
main; domain + branding wiring (including a real bug found in planning:
config.py reads SITE_BASE_URL *before* load_dotenv, so a .env value was
silently ignored); the LLM backend abstraction; registry validation
hardening (adapter membership by type, sender rules with global
uniqueness, notes required for active status); the email flip with
gate-3 notes (plus correcting swapped provenance notes between
ofr-email and usattorneys-email, and 30 stale "pending build" method
strings); test-debt paydown (dedicated test_rules.py, compose_sections
coverage, a stage-split refactor of run_pipeline with its first tests);
then, held to last, a full pipeline run — which renders the 2026-07-29
digest, the newest complete day.

**Open questions / next steps:** VPS provisioning is a later push (the
deployment outline is written); site hosting decision still open; the
GUIDE §6 rule-8 cap still waits on a decision from the measured
baseline.

## 2026-07-30 06:34 PDT — State-of-the-project review: full context pass before new work

**Context:** New work session opened with a fresh review of the whole
project — code, governing documents, research, registry, and data state
— to re-establish context and record where things stand before the next
build phase.

**Work performed:** Read-through of README, GUIDE, the launch checklist
(docs/pre-publication-todo.md), the GH-native plan, recent worklog
entries, and a structured sweep of all 21 modules in src/fapd, the 13
scripts, the 19 test files, and the registry. No code changed; this
entry is the resulting assessment.

**Where the project stands (summary of progress to date):**

- **The pipeline is complete end to end and validated.** Six days from
  inception (07-24) to a full run: sync (govinfo delta, watermarked) →
  agency RSS (per-host concurrent) → email bulletins (IMAP, DKIM-
  verified) → extract (five collection parsers + FR graphics) →
  mechanical selection (versioned rules, party-blind) → three
  independently-versioned LLM layers → deterministic render with four
  hard validation gates → static site with agent surfaces. ~4,700 LOC,
  257 tests passing, four digests committed, provenance manifests
  hash-chained.
- **The editorial machinery is real, not aspirational.** Selection is
  code (rules.py registry, one rule per item, registry order as
  precedence); the Coverage Statement reconciles arithmetically against
  SQL; the banned-lexicon gate masks official text before scanning our
  prose; a failed gate blocks publication with no override. The one
  acknowledged gap in the source is disclosed in the digest itself (the
  FR graphics vision pass, report.py:1110) and pinned by a test.
- **The source universe is measured: 127 registered, 19 active, 19
  unavailable, 87 planned, 2 evaluated-excluded.** The access story has
  become the project's most distinctive pillar: refusals recorded as
  data, the email channel re-opening 11 blocked agencies through the
  publishers' own bulletins (37 items from 9 agencies on the first
  live run, DKIM 37/37), and an advocacy agenda (M-23-22 letters, Web
  Bot Auth) queued behind GUIDE amendments.
- **Token economics found its baseline.** The 07-29 judicial-heavy run
  measured 1.53M input tokens; the ledger traced 42% to single-item
  plain-speak retries, and the group-first/isolate-last escalation
  landed the same night (~500K/day recovered). The GUIDE §6 rule-8 cap
  can now be set from data, as rule 8 always intended.
- **Launch posture:** licenses decided and committed (Apache-2.0 /
  CC BY 4.0), history audit passed, AI-transparency page published,
  rebrand done. What gates the public flip is infrastructure, not
  content: domain decision, CI + Pages workflows, the AnthropicBackend
  for hosted runs, community files, and the STATUS snapshot.

**Assessment — strengths worth preserving:** the GUIDE-first working
agreement is visibly holding (module docstrings cite section numbers;
amendments precede implementation); incomplete work lives in tracked
TODO docs rather than code markers (a grep of src/scripts/tests finds
essentially none); verification culture is catching real defects
(live-output checks found the email adapter's fabricated-item and
wrong-citation bugs that green tests missed).

**Assessment — gaps and frictions found in this pass:**

1. **The registry's `adapter: govdelivery` field is decorative.** 24
   email entries declare it, but no such key exists in
   `agencies.ADAPTERS` and email_sources.py never reads the field.
   Harmless today (all 24 are planned and routed by sender allowlist),
   but `sources._validate` doesn't check `adapter` values against known
   adapters, and a mistyped entry would surface as a KeyError at poll
   time instead of a validation failure at load time.
2. **scripts/ is untested** — including run_pipeline.py's stage wiring,
   the `from digest import default_date` cross-script import, and the
   mailbox-outage fallback. The pipeline's connective tissue relies on
   live runs for verification.
3. **Rule coverage is discoverability-hostile:** the selection registry
   — the most safety-critical module — is tested inside
   test_analyze.py rather than a test_rules.py of its own.
4. **compose.py is the thinnest-tested module** (290 LOC, 4 tests).
5. **PLAW is in COLLECTIONS with a parser but data/raw has no PLAW/
   directory** — the collection has produced no archived packages yet;
   worth confirming this is delta-sync timing rather than a silent
   filter.
6. Email sources remain `planned` pending gate-3 coverage evaluation —
   correct per the five-gate discipline, but the few-days bulletin
   accumulation clock is running and should be checked deliberately,
   not remembered accidentally.

**Decisions:** none — assessment session only.

**Open questions / next steps:** the launch checklist is the map. The
critical path to the flip: (a) domain decision (operator), then
SITE_BASE_URL; (b) gh-native branch backlog — AnthropicBackend,
run-summary emitter, state steps, T2–T5 evaluation with the per-source
403 measurement; (c) community files; (d) STATUS snapshot; (e) set the
§6 rule-8 cap from the measured baseline. Alongside: gate-3 evaluation
of the email sources once a few days of bulletins accumulate, and the
small hardening items above (adapter-field validation, a smoke test
for run_pipeline's wiring).

## 2026-07-29 23:45 PDT — Retry escalation: group-first, isolate-last (the 42% token burn)

**Context:** The 2026-07-29 ledger showed `plain:retry` consuming
645,778 input tokens across 25 single-item calls — 42% of a 1.53M-token
day — to recover items that had merely been truncated out of a batch
response.

**Work performed:** Both LLM layers now escalate isolation instead of
jumping to it. A batch miss goes first to a **group retry**
(`MAX_RETRY_BATCH_ITEMS = 5`), and only what is still missing gets a
single-item call. The reliability the old path provided is intact —
per-item isolation still happens, just last instead of first — while
the common case (a truncated tail) costs one call rather than N. On the
measured day that is roughly 25 calls collapsing to 5: about 500K input
tokens recovered. Applied to the map layer too, which shared the
pattern. Purposes renamed to `retry-group` / `retry-single` so the
ledger shows which path a token went to.

**Root-cause instrumentation:** the plain harvester now logs when a
response covers fewer items than requested, so the next run produces
evidence for whether truncation (and not unparseable content) is the
real driver — measure before tuning batch size, per §6 rule 8.

**Digest re-rendered and site rebuilt** (analyze is idempotent, so zero
LLM calls). 257 tests passing.

**Open questions / next steps:** with a run's worth of shortfall logs,
decide whether `MAX_PLAIN_BATCH_ITEMS` (25) should come down; then set
the §6 rule-8 daily cap.

## 2026-07-29 23:20 PDT — Full pipeline run with email sources wired in; token ledger yields its first real cap baseline

**Context:** First end-to-end run including the new email channel.

**Work performed:**
- **Wired stage 1c (EMAIL BULLETINS) into run_pipeline** between the RSS
  poll and extract; degrades to a reported skip when the mailbox is not
  configured, and a mailbox outage is reported without costing the run.
- **Fixed a live gap found while watching the run:** stage 1b still
  called the serial `agencies.run()`, so gao.gov's 420-second
  crawl-delay serialized every other agency behind it — the exact
  problem per-host concurrency solved. Stage 1b now uses
  `run_concurrent()`. The observed cost of the bug: 1,091s for a stage
  that should take under a minute.
- **Run result (validation PASSED):** govinfo sync 448 requests
  (USCOURTS listed 6,085, 100 downloaded, 2,312 still queued — the
  resumable pending queue holding); agency RSS 47 new items; email 4
  bulletins; extract 179 packages / 420 records / 5.6M chars; analyze
  114 selected, 93 model summaries; digest 2026-07-28 rendered and site
  rebuilt.
- **Two presentation/data defects fixed:** agency claimed dates rendered
  as truncated RFC-822 headers ("Tue, 28 Jul 26 1" — misstating the
  year); now the parsed UTC day. And two real-data smoke tests broke on
  newly synced data, both correctly: the Federal Register issue for
  07-29 contains a **correction document** (`C1-2026-13124`), a granule
  shape we had never seen, and CREC returned 47 granules on a light
  session day. The FR pattern now accepts the `C<n>-` correction prefix;
  the CREC volume floor was removed entirely — issue size is a property
  of Congress, not of the parser.

**Token finding — the measure-first baseline the GUIDE was waiting
for.** This run cost **1,532,325 input / 128,455 output tokens**, the
largest yet, on a judicial-heavy day (90 court opinions summarized).
The ledger exposed where it went: `plain:retry` consumed **645,778
input tokens across 25 single-item retries — 42% of the day's total**.
The plain-speak layer batches 25 items per call, and when an item comes
back unparseable it is retried alone, re-paying the fixed ~25K prompt
overhead each time. Reliability is fine (93/93 written, 0 failures);
the cost is not. Retrying in small groups instead of singly would cut
roughly 500K tokens off a day like this. Recorded as the top token
finding; not changed in this run.

**Open questions / next steps:** batch the plain-speak retries; set the
§6 rule-8 cap from this baseline now that a judicial-heavy day is
measured; activate email sources after gate-3 coverage evaluation.

## 2026-07-29 22:15 PDT — Email adapter built, tested, and running: 37 items from 9 agencies

**Context:** With the mailbox subscribed and registered, the email
channel needed its adapter.

**Work performed:**
- **Probed before coding** (GUIDE §3 gate 2): pulled real bulletins
  read-only and read their bytes. Findings that shaped everything —
  bulletins are often *multi-item digests* (one U.S. Attorneys message
  carried sixteen district releases); the plain-text part has clean
  canonical .gov URLs but runs titles and summaries together with no
  delimiter; the HTML part carries the exact title as anchor text and
  the canonical URL percent-encoded inside the platform tracking
  wrapper. Decoding that wrapper statically is the same technique the
  USPS adapter uses — never a redirect fetch.
- **`src/fapd/email_sources.py`**: read-only IMAP client (readonly
  select, BODY.PEEK — the mailbox is never mutated; our watermark lives
  in a new `mailbox_state` table), registry-driven sender allowlist
  **applied to headers before any body is downloaded**, raw RFC-5322
  bytes as the content-addressed capture, DKIM verification with the
  verifying DNS key archived beside it, per-item dating, cross-channel
  dedup, and per-message error isolation.
- **`scripts/ingest_email.py`** with `--dry-run`, `--limit`, `--ids`,
  and `--since-uid` (first run skips mail predating the subscriptions).
- **Two defects caught by verifying the live output rather than
  trusting green tests.** (1) For single-release bulletins the anchor
  rule fabricated items from inline citations and footer links —
  "Contact us" became a publication. Fixed with the date-marker
  discriminator between digest and article shapes. (2) Worse, a
  single-release item could cite a page the release merely linked to;
  now an anchor is used only when it plainly refers to the release, and
  otherwise the item carries no URL with the captured bulletin as its
  source of record. A missing citation is honest; a wrong one is not.
  Both runs were purged and re-ingested.
- **Administrivia filter**: welcome and confirmation mail is counted and
  disclosed, never ingested — platform plumbing is not government
  action.
- **report.py** renders email items with their channel and DKIM state,
  and unlinked when no canonical page exists.

**Live result:** 37 items from 9 agencies (U.S. Attorneys 25, Treasury
5, Agriculture 2, Justice 2, FSIS 1, USCIS 1, USPS OIG 1), 30 with
canonical citations, DKIM verified 37/37 with every key archived, 36
messages ignored without their bodies ever leaving the server. 249
tests passing.

**Open questions / next steps:** activate the email sources once a few
days of bulletins confirm coverage (gate 3), then wire the poll into
run_pipeline; the nine pending confirmations still gate HHS, SEC, DHS
and others.

## 2026-07-29 16:05 PDT — Email subscriptions confirmed and registered: 30 sources, 11 blocked agencies re-opened

**Context:** The operator completed the manual subscription pass using
the project mailbox (the public attribution identity) and confirmed
IMAP access. This session verified the mailbox against ground truth and
brought the source registry into alignment with what is actually
subscribed.

**Work performed:**
- **Mailbox verification (read-only):** 178 messages since 2026-07-29
  across ~85 senders; classified 77 confirmed subscriptions against 9
  still awaiting the publisher's confirmation click (HHS departmental,
  SEC, DHS main, ICE, E-Verify, Census, DEA Diversion Control, and two
  others). Real bulletins already arriving from U.S. Attorneys and the
  USPS Inspector General.
- **Schema:** `TYPES` gained `email`; `URL_KEYS` gained `signup`.
- **Registry 97 -> 127:** 30 `type: email` entries, all `status:
  planned` (the adapter has not parsed a bulletin yet, so gate 2 is
  incomplete and activation would be a false claim). 22 web entries
  cross-reference their new email sibling; **11 sources previously
  carrying no working input now have one** (Treasury, USDA, EPA, SSA,
  DOT, FAA, NHTSA, DEA, ATF, USCG, HUD-OIG partial).
- **Correction to earlier research:** ATF *does* operate its own
  bulletin account; the 2026-07-29 access-alternatives report concluded
  it did not, because the guessed account code 404'd. Recorded in the
  entry notes.
- **Self-audit against project standards, prompted mid-session.** Two
  real defects in my own work, both fixed before commit: (1) I had
  populated `signup:` URLs by inferring account codes from sender
  addresses rather than verifying them — a live check found 8 of them
  404, so those URLs were removed and the entries now assert only the
  confirmed sender, with a note saying exactly that; the HUD-OIG signup
  page 403s our client and is recorded as observed, not evaded. (2)
  Four descriptions carried unverified superlatives or rhetorical
  framing ("the largest single stream", "roughly a third of national
  health spending", "determine payments to tens of millions") — all
  replaced with plain statements, and the whole email set was scanned
  against the banned lexicon (clean).
- **Public alignment:** README, About, and Methods described only web
  and API access; all three now describe the subscription channel and
  its bright line — a bulletin is not permission to crawl the site that
  refused us, and the refusal stays on the record.

**Decisions:** Email entries are siblings, never replacements; a
success on one channel never erases a recorded refusal on another.
Program-outreach newsletters (MyPlate, Ticket to Work, education
campaigns) were deliberately not registered — the registry lists
sources of official actions, and that scope line is worth holding.

**Open questions / next steps:** operator to clear the 9 pending
confirmations (HHS matters most) and retry HUD-NEWS-L, CBO, and FERC in
a browser; then the adapter build (IMAP poll, raw-message captures,
DKIM verify-and-archive, email-full/email-teaser modes) against the
bulletins now accumulating in the mailbox.

## 2026-07-29 13:10 PDT — Scheduling deliberation resolved: GH-native runtime plan, evaluated on a branch

**Context:** After the licensing and access-research work, the
scheduling question came to a head through three shapes in one
afternoon: self-hosted runner on the operator machine → Dockerized
runner on a VPS (consistent IPv4 + rDNS as crawler identity) → plain
VPS cron with results pushed to the repo. Assessing the last, we
established that GitHub Actions run logs are operational convenience,
not accountability (90-day retention, admin-deletable, private-scoped)
— our committed manifests + fetch logs already outclass them, and a
committed daily run-summary would give the public better execution
transparency than Actions logs ever could. The operator's direction:
not settled on the VPS; the real desire is for FAPD to **live
completely on GitHub**. Decision: pursue a GH-Actions-only runtime,
built and proven on a branch before main changes at all.

**Work performed:** docs/gh-native-plan.md written and adopted as the
active track — design principle "git history for evidence, Releases for
state" (measured: fapd.db 80 MB, raw 800 MB — rolling pipeline-state
Release assets, monthly S4-style bundles; evidence commits stay in
git with a bot identity; new committed run-summary artifact); LLM stage
via an AnthropicBackend behind LLM_BACKEND=api|cli (cli default
locally); workflows ci/pipeline/pages born on the gh-native branch;
the honest trade stated (shared runner IPs vs our identified-client
posture) with a measurement plan (per-source 403 delta in T4) and a
decision rule (material coverage loss + signing doesn't recover it →
revisit VPS with evidence). Branch isolation is a hard rule: main gets
documentation only until T1–T5 pass and a reviewed PR promotes the
runtime. VPS shape documented in the plan as the considered,
not-settled alternative. gh-native branch scaffolded with ci.yml
(complete) + pipeline.yml skeleton; first CI run on GitHub
infrastructure verified from the branch.

**Decisions:** Accountability lives in our own committed artifacts, not
platform logs. State is public (Releases) — the fetch log was built
key-redacted from day one for exactly this kind of exposure. Web Bot
Auth signing rises in priority: on hosted runners, cryptographic
identity must do what stable IP identity can't.

**Open questions / next steps:** branch backlog in the plan doc
(AnthropicBackend, run-summary emitter, state steps, T2–T5); the
per-source 403 measurement will decide the architecture with data.

## 2026-07-29 08:40 PDT — Publication-readiness: audit passed, access-advocacy pillar, AI-transparency page, launch TODO

**Context:** NotebookLM renderings of the project (audio overview +
briefing doc, archived under research/) prompted a full pre-publication
review. The operator's key takeaway from the audio: our safety-conscious
access methods leave significant agency sourcing closed, and our public
philosophy said nothing about doing anything about it. Second operator
decision: own the AI-assisted development story openly, with a dedicated
public page.

**Work performed:**
- **History audit: PASS.** All 26 commits, blobs, dangling objects,
  reflog: no personal email, no local paths, no secrets, no databases —
  the §9 discipline held end to end. Two structural gaps fixed:
  research/ and .claude/ were ignored only by non-cloneable local
  mechanisms; both now in tracked .gitignore.
- **Access-advocacy pillar** (GUIDE §1 + §3 first, then About, Methods,
  agents surface, README): the closed share of the source universe
  (22/72 non-govinfo at the 07-26 probe) is the standing engagement
  agenda — documented-channel research, re-probes, direct agency
  outreach; `unavailable` records double as the outreach worklist;
  coverage grows by doors opening, never evasion.
- **AI-transparency page**: docs/site/ai-development.md → site
  ("How AI Built This"): the operator/agent division of labor, the
  past-syntax-toward-intent thesis, built-for-agents/built-with-agents
  symmetry, and what it does NOT mean. GUIDE §9 records the policy;
  README points to it; devnotes README carries the standing theme.
  Worklog stays unrewritten, on principle.
- **Public-register cleanup**: "operator's call"/"Operator steps"
  phrasing removed from registry notes that render on sources.html.
- **SITE_BASE_URL** (config + publish): sitemap <loc>, feed links,
  robots Sitemap directive, llms.txt links, digests.json html values all
  absolutize when a domain is set (they formally require absolute URLs);
  root-relative fallback unchanged for local viewing. Tested both ways.
- **pyproject**: readme, urls (repo/issues), keywords added; license
  field deliberately waits on the license decision.
- **Two documents**: docs/publication-readiness-2026-07-29.md (audit +
  NotebookLM briefing fact-check: 227 tests not 226; NO token cap exists
  — measure-first, ~1M is a working figure; 31% = 22/72 @07-26 snapshot,
  partly superseded; tier/active counts confirmed) and
  docs/pre-publication-todo.md (launch checklist: license decisions
  [rec: Apache-2.0 code, CC-BY 4.0 content], domain, Pages + CI
  workflows, LLM backend swap, scheduling, community files, flip-time
  edits, STATUS snapshot, probe shortlist, first agency outreach).

**Decisions:** Transparency over curation for the AI narrative; the
worklog is never retroactively edited. Continued engagement is
philosophy, not marketing garnish. External-AI misreadings traced to our
own stale numbers → dated STATUS snapshot queued.

**Open questions / next steps:** the two operator decisions (licenses,
domain), then the build items in pre-publication-todo.md, then the flip.

## 2026-07-28 19:20 PDT — Rebrand: Free Agentic Publication Digester (FAPD)

**Context:** Repo pushed to GitHub (private) as
`davidkarnowski/free-agentic-publication-digester`; the user settled the
project name — **Free Agentic Publication Digester (FAPD)** — replacing
the working title "Information Intelligence". Full scrub approved in plan
mode.

**Work performed:** Package renamed `info_intel` → `fapd` (src dir,
imports across scripts/tests, logger names, dynamic parser-import
strings, pyproject distribution name, lockfile; `data/info_intel.db`
moved to `data/fapd.db` — audit.py smoke-verified against the moved
file). Display surfaces: SITE_TITLE "Free Agentic Publication Digester —
Daily Federal Digest", nav brand "FAPD", README/GUIDE/WORKLOG H1s,
about.md opening. Wire identity changed now, in the only free window
(site unpublished, zero feed subscribers): User-Agent
`fapd/0.1 (Free Agentic Publication Digester; …)` and Atom IDs
`tag:fapd…`. Docs path refs (schema.md, registry comment) updated;
SOURCES.md + site regenerated. **Worklog history deliberately untouched**
— older entries keep the working name (falsifying a timestamped record is
not a rebrand); a naming note in GUIDE §1 bridges the two. 226 tests
passing.

**Decisions:** Feed IDs and UA are permanent identity once anyone
subscribes or servers profile us — changing them pre-publication was the
whole reason to do this now rather than later.

## 2026-07-28 15:05 PDT — Agency dating rule: digests list what was published that day, not what we first observed

**Context:** Operator caught the bootstrap defect in the committed digest:
section 6 keyed on observation date, so newly activated sources' feed
backfill (releases dated as far back as March) rendered as "today's"
announcements.

**Work performed:** GUIDE §3 dating rule first, then code: a digest for
day D lists only releases the agency itself dates on D (claimed
publication date parsed to a UTC day — RFC 822 and ISO forms; timezone
converted). Observed-on-D-but-dated-elsewhere items are excluded under
new rule **AGENCYPR-EX-01** — never silently: section 6 discloses the
count in place, the Coverage Statement carries it as excluded, and the
validator reconciles it (single source of truth: `_agency_rows`).
Items with no parseable agency date fall back to observation date,
disclosed per item as "dated by first observation". Claimed vs observed
dates remain separately stored per §7 T3/T4. Tests: backfill exclusion +
coverage arithmetic, RFC822/ISO/garbage date parsing, fallback listing.
226 passing. Real effect on 2026-07-28: 282 observed → 41 listed (dated
today) + 241 disclosed backfill. Digest re-rendered, site rebuilt.

**Decisions:** The digest answers "what did the government publish on day
D per its own dating," with our observation record as the audit trail —
not the reverse. Backfill is accounting data, not news.

## 2026-07-28 14:20 PDT — Bootstrap ingest landed (282 items, 14 sources); five sources activated by probe; DOJ challenge lesson; GAO feed-only economics; digest + S2 commit

**Context:** Closing out the day's arc: the S2 bootstrap ingest, the probe
wave over research candidates, the DVIDS multi-modal deep dive, and the
operator's directives to speed GAO within server limits and commit S2.

**Work performed:**
- **Probes (gate 2)** on nine documented-feed candidates: five passed
  end-to-end and were activated (justice-newsroom, nist-news,
  uscourts-news, cisa-advisories — where the researched RSS-retirement
  turned out not to apply, the feed is alive with full advisory text —
  and noaa-news feed-only, articles WAF'd). USSC's feed is live but
  currently empty (stays planned); BLS and ODNI URL guesses 404'd (real
  feed URLs to be read from their docs pages); FCC's api2 host answered
  504 (retry later, not a verdict). Registry notes carry the evidence.
- **DOJ challenge lesson:** first full ingest revealed justice.gov answers
  sustained article fetching with Akamai bm-verify challenge interstitials
  (single probes pass; 25 sequential fetches get challenged). Following
  the challenge URL is bot-check circumvention — never. DOJ flipped to
  feed-only; the 25 mis-stored items repaired via targeted re-poll
  (--ids flag added to ingest_agencies.py); challenge pages retained as
  captured evidence. Generic fix: empty extraction can never be stored as
  mode 'full' — loop-level fallback with disclosure, tested.
- **GAO economics:** operator asked for a shorter rhythm within server
  limits. GAO's User-agent:* Crawl-delay: 420 IS the server limit — not
  shortenable honestly. Chosen instead: fewer requests — gao-reports
  flipped to feed-only permanently (its ~4,000-char descriptions are
  GAO's own report summaries); remaining 12 backfill items ingested in
  one feed request instead of 84 minutes of paced fetches.
- **DVIDS deep dive** (sub-agent, resumed across a session limit):
  docs/dvids-multimodal-research-2026-07-28.md — API/TOS/copyright read
  verbatim ('free for commercial use'; public domain unless indicated;
  no-endorsement rule), VIRIN documented, stable_id design
  (dvids:{type}:{id}), video posture (captions+thumbnail+metadata, no
  A/V), asset_posture as a proposed fifth adapter decision, six proposed
  GUIDE amendments awaiting operator approval, and a survey verdict:
  DVIDS is structurally unique; NASA Image Library is second. Registry
  97 sources (nasa-image-library, nps-api planned; nara-catalog, loc-api
  evaluated-excluded as archives).
- **Final ingest accounting:** 282 AGENCYPR items across 14 active
  sources; 193 full-text; footprint 360/500 agency, 100/100 wayback (40
  corroborations recorded before exhaustion), 420/2000 govinfo.
- **Digest 2026-07-28 re-rendered** — and the validation gate earned its
  keep twice before passing: (1) agency titles are attributed official
  speech and are now masked like official summaries (live trigger: DoD's
  'Historic Multinational Medical Team...'); (2) link URLs are citations,
  not prose — slugs echoing source headlines (war.gov/.../historic-...)
  are stripped before the lexicon scan. Both fixes tested. Final digest:
  21 selected items, 19 official summaries, 282-item agency section with
  reconciled coverage row.
- **Site rebuilt:** 4 digests + about/methods/agents/sources + machine
  surfaces. 224 tests passing.

**Decisions:** No fetch-rhythm ever set below a server's declared limit —
speed comes from fewer requests, not faster ones. The lexicon gate
polices only our prose: official titles masked, URLs never scanned.
DVIDS build gated on operator key signup + GUIDE amendment approval.

**Open questions / next steps:** Wayback top-up for today's ~180
uncorroborated captures (later days' budgets); FCC api2 re-probe; BLS/ODNI
feed-URL reads; USSC activation when its feed populates; DVIDS key +
amendments; GovDelivery-pattern probe (FDIC); S3 re-check pass.

## 2026-07-28 11:45 PDT — Per-host concurrency; ingest observability; public site pages; source-research sprint (81→93)

**Context:** The S2 bootstrap ingest surfaced gao.gov's 420-second robots
crawl-delay, which serialized the entire nine-source run behind one host's
sleep timer (~3h projected). Operator asked for (a) a safe speed-up, (b) more
live verbosity in the ingest, (c) sub-agent research to expand the source
universe including re-evaluating previously-discounted sources, and (d)
blog-ready development notes. Separately, the public-pages sub-agent
delivered About/Methods, and the Wayback URL was manually verifiable after a
firewall fix.

**Work performed:**
- **GUIDE §4 amendment first**: pacing is per host; concurrency across
  hosts only, never against one; budgets stay global (read-before-request
  check can overshoot by ≤ worker count — documented). Then
  `agencies.host_groups()` + `run_concurrent()`: one worker per feed-host
  group, each with its own AgencyClient/WaybackClient (own pacing clock,
  own crawl-delay obedience) and own SQLite connection (WAL +
  busy_timeout added to both DBs). Manifest still exports once after all
  workers join. `ingest_agencies.py` concurrent by default, `--serial`
  fallback. Result: 8 of 9 newsrooms done in <1 min; GAO takes GAO's time.
- **Resume trap found and handled**: interrupted runs leave feed ETags in
  feed_state; the next poll 304s and silently skips unfinished feeds.
  Restarts now clear the pilot feed_state rows (cheap re-fetch; item-level
  dedupe absorbs overlap). Two restarts performed losslessly.
- **Observability**: per-source "feed has N items; M new" + "[i/N] ingested"
  + per-source done-summaries; worker start/finish lines; crawl-delay
  announced once per host at INFO; pacing sleeps ≥30s at INFO with reason.
- **Wayback verified end-to-end**: recorded snapshot (DOL/ETA release,
  16:46:22 UTC) resolves HTTP 200 with `x-archive-orig-*` headers and a
  title identical to our captured item. Budget reality: 100/day exhausted
  after 40 corroborations on bootstrap volume; GUIDE §7 threat-table wording
  softened to match PROVENANCE.md ("within its daily budget, best-effort").
- **Public pages** (sub-agent, reviewed line-by-line): docs/site/about.md +
  methods.md → about.html/methods.html via a generalized publish.py
  (any docs/site/*.md becomes a nav-linked page; llms.txt + sitemap wired).
  One factual fix: "cosponsor counts" → "recorded votes taken" (no
  cosponsor rule exists in code; GUIDE §2's example list is aspirational).
- **Source-research sprint** (three parallel sub-agents, documentation-first,
  no probing): synthesis in docs/source-research-2026-07-28.md. Registry
  81→93: 12 new planned entries (federal-register-api incl. public
  inspection, regulations-gov-api, congress-gov-api, govinfo-billstatus,
  senate-xml, house-clerk-votes, docs-house-gov, dvids, bls-news, odni-news,
  cisa-advisories, ofac-recent-actions) + 17 corrections (DOJ/uscourts/USSC
  were moved-not-blocked with documented feeds; FCC/Commerce/NOAA have
  documented channels on non-WAF hosts/paths; NIST feed documented but not
  autodiscoverable; CRS re-pointed to the api.congress.gov crsreport
  endpoint; GovDelivery likely email-only — one FDIC probe settles it).
  Schema: TYPES += api, xml-index, bulkdata. Key negative findings recorded
  (no CHRG/CRPT in bulkdata; HUD has no press RSS; supremecourt.gov has no
  feed; PACER parked pending J3 + fee policy).
- **Devnotes series started** (docs/devnotes/): blog-ready narrative of the
  adapter seam, the USPS interstitial, the GAO crawl-delay economics, the
  resume trap, and the Wayback budget-vs-promise correction.

**Decisions:** Politeness is per-server — concurrency across hosts is
consistent with §4 and now codified there. govinfo rate NOT raised (not a
bottleneck; 420/2000 requests used). GAO's 7-minute pace honored without
exception. Probes of the 12 new candidates await operator go-ahead
(onboarding gate 2 is operator-visible by design).

**Open questions / next steps:** ingest completion → digest re-render with
section 6 → site rebuild → privacy scan → S2 commit (single bundle). Probe
shortlist Tier A: federal-register-api, congress-gov-api, dvids,
justice-newsroom, uscourts-news/ussc-news. GovDelivery email-adapter class
needs a GUIDE decision if the FDIC feed probe fails. Wayback top-up for
today's 60 uncorroborated captures on a later day's budget.

## 2026-07-28 10:30 PDT — S2 built; SourceAdapter abstraction; USPS adapter; access/transformation philosophy
<!-- timestamp corrected 11:45 PDT: originally logged as 17:30 PDT, which was the UTC clock time -->


**Context:** User approved S2 implementation, then directed: a source-
level abstraction for unique publication interfaces (USPS as the worked
case, via sub-agent), extensibility docs for pointing the codebase at
other governments, mission framing (citizens' ease of access to what
governments publish to be public), and — final refinement — the codified
access hierarchy (directed programmatic access first, basic web access
second, impersonation never) with adapter-owned smart deterministic
transformation and LLM inference strictly secondary.

**Built:**

1. **S2 agency ingestion:** `agencies.py` — conditional feed polls
   (feed_state ETags), items through provenance documents/captures, the
   AGENCYPR collection, per-source isolation, daily manifest export;
   `WaybackClient` (own budget bucket) submits every new capture to
   Save-Page-Now, snapshot URLs recorded; digest **section 6 "Agency
   Announcements"** (zero-LLM: attributed linked titles by agency,
   claimed dates, independent-archive links, AGENCYPR coverage row,
   mutability disclosure); `scripts/ingest_agencies.py` + run_pipeline
   stage 1b; 9 pilot sources → active (14 active total).
2. **SourceAdapter abstraction:** identity / fetch-posture / extraction /
   fallback as the single seam for interface irregularity; registry
   `adapter:` field; defense-newsroom = first adapter (rss-feed-only).
3. **USPS adapter (sub-agent), with a probe correction:** the "script-
   rendered article" was actually a JS redirect interstitial —
   `/newsroom/rssrequest.htm` carries no content; real article pages were
   never reached (extractability unknown, not proven bad; registry says
   so). Adapter: statically mirrors the redirect arithmetic for identity
   (668 GUID-less items stay distinct while URL noise collapses),
   feed-metadata-only posture (never re-fetch known-contentless bytes),
   defensive extract with lede-paragraph fallback. Speculative JSON-LD
   parsing explicitly declined — findings-free code refused.
4. **Docs:** GUIDE §1 legitimacy framing (official publications = the
   record made to be public; we ease access, incl. agentic; forkable per
   jurisdiction); GUIDE §3 Source adapters section incl. the **access
   hierarchy** and **transformation ownership** rules (deterministic
   smart shaping first; LLM secondary, budgeted/ledgered/versioned and
   marked model-derived); `docs/adding-sources.md` how-to (five gates,
   adapter table, other-government layering map); README links.
5. **Tests: 212 passing.** Bootstrap ingest run in progress at time of
   entry (first-run Wayback submissions are the slow tail); results
   recorded in the next entry.

---

## 2026-07-28 15:10 PDT — Dual-audience philosophy: an agentic publishing house

**Context:** User direction: codify that this project publishes for
humans AND AI agents — agents researching fedgov actions should ingest
our summarized, cited digests instead of crawling official sites — and
make agentic access clean, guided, and explicitly advertised (domain →
GH Pages planned).

**Work performed:**

1. **GUIDE §1 "Dual audience" amendment:** the substitution argument
   (one polite disciplined crawler feeding many agents beats many
   crawlers hitting government servers), plus five standing commitments:
   explicit invitation, machine-first stable surfaces, honesty travels
   with the data (labels/citations/coverage in every ingested surface),
   guided onward citation (cite govinfo for claims, us for aggregation),
   and reciprocity (we ask visiting agents the courtesy our crawler
   practices).
2. **Agent surfaces built into the site** (publish.py, tested):
   `llms.txt` (agent guidance convention), `digests.json` (machine
   index), `feed.xml` (Atom, change discovery), `robots.txt` (explicit
   welcome + sitemap), `sitemap.xml`, and `/agents.html` — a full access
   guide covering URL patterns, official-vs-generated text labeling,
   citation guidance, and courtesy expectations. "For agents" in site
   nav; README rewritten dual-audience. 200 tests passing.

**Flagged for user decision before domain launch:** a content license
(the underlying government text is public domain; our compilation/
summaries need an explicit grant — CC0 or CC-BY recommended for the
agent-ingestion mission).

**Next:** S2 pilot implementation (plan revised this session).

---

## 2026-07-28 12:40 PDT — Digest refinement: PLAW active, section quick-reads, table of contents

**Context:** User direction: full coverage for Enacted Laws (section 4 was
a placeholder), plain-speak quick-reads under section titles (user chose
keeping per-item lines too), a clickable ToC leading each digest, and
confirmation that agency newsroom ingestion is still pre-S2 (it is —
probed, not yet wired; answered honestly).

**Built:**

1. **PLAW activated (delta-only per user choice):** collection added to
   sync scope with USLM format preference (uslmLink — PLAW has no plain
   xmlLink; empirically sampled PLAW-119publ101); `parsers/plaw.py`
   (USLM meta: citation, docNumber, approvedDate; txt fallback);
   PLAW-SEL-01 (all laws listed); real section 4 renderer with citations
   and approval dates; PLAW coverage row; registry entry → active
   (5 active sources); watermark bootstrapped (3-day window — empty, as
   expected between enactments; newest law was 07-11).
2. **Section quick-reads:** `compose.compose_sections` — one batched
   cheap-tier call per date producing one-sentence synopses per populated
   section (strict JSON, stored in new section_summaries keyed by date +
   key + SECTION_PROMPT_VERSION, invalidated when newer item summaries
   arrive). Rendered as "*In plain terms: …*" directly under each section
   heading via post-processing injection — per-item plain lines retained
   per user choice. LLM prose → linted un-masked automatically.
3. **Table of contents:** mechanical post-processing pass building a
   clickable Contents block from the digest's actual top-level headings,
   placed ahead of Day in Review; `toc` extension added to the site
   renderer so heading ids exist and anchors work in HTML (verified: 9
   live in-page links).
4. **Both digests regenerated** under the new layout (~54K tokens total —
   map/plain idempotent; only section synopses + re-render ran). TEMPLATE
   updated (ToC slot, quick-read slots, active section 4).
5. **Tests: 199 passing** (PLAW parser ×2, section-4 render, ToC+blurb
   placement, updated active-source counts).

**Next:** unchanged — S2 agency ingestion pilot; scheduling; cap decision.

---

## 2026-07-28 09:50 PDT — run_pipeline entrypoint; API key incident; newest-complete-day fix; two digests

**Context:** User requested a full verbose pipeline run for "today" with
live per-call visibility.

**Work performed:**

1. **`scripts/run_pipeline.py`** — the daily entrypoint: all five stages
   (sync → extract → analyze/plain/compose → render+validate → site) with
   stage banners, forced-verbose per-call narration (console + the daily
   access log), per-stage timings, and an end-of-run detail report
   (requests by client incl. errors, LLM tokens by purpose, validation
   outcome).
2. **API key incident (2026-07-27):** first run attempt failed immediately
   with govinfo `API_KEY_INVALID` — server-side invalidation of the
   original key after ~1,300 successful requests over three days. Crash
   safety held (listing 401 → watermark untouched, failure logged). User
   provisioned a new key; single-request verification passed.
3. **Healthy full run (07-28):** sync 415 requests (Monday's Record,
   3 FR packages, 56 bills, USCOURTS delta of 7,800 listed — churn
   auto-skipped, 100 newest downloaded); extract 160 packages → 703
   records + 413 graphics, 0 failures; FR-day digest for 07-28 generated
   and validated at 86.5K in / 11K out over 3 LLM calls.
4. **Date-logic defect found in the run and fixed:** default digest date
   was MAX(date_issued) — which selects *today* once the same-morning FR
   issue arrives, contradicting the recorded newest-complete-day decision
   (2026-07-25). Both entrypoints now use MAX(date_issued) strictly
   before today (UTC). The premature-but-honest 07-28 FR-only digest is
   retained; tomorrow's run completes it via summary idempotency +
   compose invalidation.
5. **Proper daily digest for 2026-07-27 generated:** first complete
   three-branch digest under the full source stack — House floor +
   recorded votes, FR (5 rules/6 proposed/85 notices), judicial section;
   15 items (11 official / 4 LLM), 15/15 plain lines, validation passed;
   89K in / 10.5K out. Site rebuilt: 4 digest pages + sources guide.
6. **Test recalibration:** CREC real-day smoke asserted >150 granules;
   Monday's light session has 124 (parser correct) — threshold lowered to
   >50 with comment. **Suite: 195 passing.**

**Measured:** a normal weekday full-pipeline day ≈ 415 govinfo requests
(~21% budget) + ~176K LLM in / 21.5K out for two digest dates — cap
discussion data accumulating.

---

## 2026-07-26 18:30 PDT — Source probe sprint: 72 sources verified end-to-end; guidelines shored up

**Context:** User direction: poll every newly added source verifying full
retrieve→ingest, spend analysis effort liberally on input/output
evaluation, ensure comprehensive content evaluation at onboarding, shore
up guidelines for source iteration and plain-speak prompting, produce
guide-quality source descriptions, and render the source guide into the
site.

**Built & run:**

1. **`probe.py` + `scripts/check_sources.py`:** end-to-end source probe —
   robots verdict, fetch (captured into provenance: our first real
   mutable-source observations, incl. refusals/errors per the
   absence-is-an-assertion rule), format sniffing with RSS/Atom
   autodiscovery, item enumeration with field inventory, one sample
   article fetched + text-extracted. 4 probe tests; crash-isolated sweep.
2. **The sweep:** 72 sources, 193 requests (~39% of the agency bucket),
   all paced/logged/captured; committed manifest for 2026-07-26 carries
   every observation. Verdicts: **10 feed-ok / 34 html-only / 13 WAF-403 /
   6 wrong-URL-404 / 9 robots-refused.**
3. **Analysis report** (`docs/source-probe-2026-07.md`): the
   ingestion-ready cohort (GAO best-in-class with near-full-text feed;
   FDA/SEC/FTC/NASA/Fed/Labor/VA clean; Defense feed-only — articles
   WAF'd, feed links resolve to war.gov; USPS script-rendered articles +
   0/668 GUIDs = identity handling required); and the accountability
   finding: **31% of the Tier 1–2 universe (22/72) is closed to
   honestly-identified automated access** — all military service branches
   + Treasury/USDA/EPA via robots.txt; CBO and CRS (the public-analysis
   agencies!) via WAF 403. Zero evasion; every refusal honored and
   recorded.
4. **Registry rewritten from ground truth** (sub-agent; JSON-wins
   discipline): 23 sources → `unavailable` with observed behavior;
   feed-ok cohort carries verified feed URLs + probe metrics; 404 cohort
   flagged correct-and-re-probe; **all 81 descriptions rewritten to guide
   quality** (institution + content types + form/cadence, probe-informed).
   Notable JSON-won corrections: FDA teaser-not-fulltext; VA feed mixes
   feature stories with releases.
5. **Guidelines (GUIDE):** §3 Source Onboarding Lifecycle (5 gates;
   gate 3 = content evaluation answering "what does the source publish
   vs what will we see", disclosed before activation); §3a Prompt
   Governance (inventory of the three prompt surfaces + independent
   versions; the plain-speak contract spelled out; iteration procedure —
   version bump, worklog regeneration-scope statement, gates never
   loosened, spot-audit before next publish).
6. **Site:** SOURCES.md now renders as styled `site/sources.html`, linked
   from index + digest nav (graceful when absent; 2 new publish tests).
7. **Suite: 194 passing.**

**Decisions:** unavailable-to-honest-clients is published data, not a
problem to engineer around; USPS type corrected to rss (verified);
military-branch fallback (GovDelivery/DVIDS) noted for later evaluation.

**Next:** S2 ingestion pilot over the 8-clean-feed cohort (+Defense
feed-only), Wayback corroboration live, digest section 6; re-probe 404
cohort after URL corrections; monthly re-probe of unavailable cohort.

---

## 2026-07-26 16:10 PDT — Registry extended to the Tier 1–2 universe (81 sources)

**Context:** Sources review found seven systematic gap clusters
(legislative support agencies; sub-agency newsrooms that don't flow
through parent departments; financial regulators; other regulators; the
White House briefing room; the IG/oversight aggregator; judicial
administration). User direction: seed the extended universe.

**Work performed:**

1. **GUIDE §3 amendments:** tier definitions (comprehensiveness is
   claimed per tier against a defined universe — the full federal agency
   count is famously unknowable, FR ~441 vs ACUS 115 vs FOIA.gov 252);
   report-publisher class (GAO/CBO/CRS — official analyses, attributed,
   nonpartisan mandate noted); aggregator class (oversight.gov —
   transport not origin; citations must point to the originating IG).
2. **Registry** (sub-agent): tier field with strict validation (bool
   rejected), aggregator type; 46 new planned entries — 5 Tier 1
   (GAO, CBO, CRS, White House briefing room, oversight.gov) and 41
   Tier 2 (Fed/FDIC/OCC/CFPB/CFTC/NCUA/FHFA; NRC/FERC/EEOC/SBA/NSF/
   USTR/USPS; CDC/FDA/NIH/CMS; IRS; FBI/DEA/ATF; FEMA/ICE/CBP/TSA/
   USCIS/USCG; FAA/NHTSA; Census/NOAA/NIST/USPTO; five service
   branches; uscourts-news, USSC). **Totals: 81 sources — Tier 1:
   40 (4 active), Tier 2: 41 (0 active).** ~16 URLs flagged
   low-confidence in notes (post-2023 site redesigns), to be resolved by
   the S2 viability probe, per the no-guessing convention.
3. SOURCES.md regenerated with per-tier coverage lines; sync guard
   holding; **188 tests passing.**

**Next:** unchanged — S2 (viability probe upgrading these 77 planned
statuses from live checks, feed poller, first ingest, digest section 6).

---

## 2026-07-26 14:40 PDT — Sources expansion S1: registry, provenance layer, client generalization

**Context:** User direction: a living sources document tracking every
fedgov source (ingesting or not, with method); agency newsroom ingestion
(RSS + direct HTML, respectfully); content preservation + hashing for
mutable sources with tamper-evidence in mind ("information fuckery":
stealth edits, removals, backdating, fabrication accusations); storage
leaning on GitHub. Branding/design explicitly on hold. Planned in plan
mode; user chose Wayback Machine corroboration and declined
OpenTimestamps. An adversarial design review (sub-agent) landed post-
approval; nearly all findings adopted (noted below).

**Built (S1):**

1. **GUIDE:** §2 attributed-speech rule (agency statements are official
   advocacy — always attributed, never repackaged as fact); §3 agency-
   newsrooms source class (registry as scope authority; viability checked
   never presumed; NO WAF evasion — blocked-to-honest-clients is itself
   recorded accountability data); new **§7 Provenance & Tamper-Evidence**
   (threat table T1–T7, two-hash strategy, attempt-level manifests with
   prev-day hash chain, honest limits). Sections renumbered (Roadmap→8,
   Open-Source→9, Working Agreements→10; cross-refs fixed).
2. **Sources registry** (sub-agent): sources/registry.yaml — 35 entries
   spanning the known universe (4 active: CREC/BILLS/FR/USCOURTS; planned:
   govinfo collections, SCOTUS J2, 15 cabinet newsrooms, 10 independents)
   with per-entry method/status/notes; sources.py loader w/ strict
   validation; generated SOURCES.md (coverage stats per branch) with a
   sync-guard test so the doc can never drift from the registry. Seeded
   URLs carry confidence notes; the viability-check phase upgrades them.
3. **Provenance core** (provenance.py): content-addressed capture store
   (data/captures/<sha[:2]>/<sha>.bin, dedupes); documents table keyed by
   stable identity (feed GUID else URL) with claimed_published_at vs
   first_seen_at kept separate; captures record every ATTEMPT (304s,
   robots refusals, errors) with two hashes (raw bytes = evidence;
   normalized text = change signal, normalizer-versioned), response-header
   subset, split change_kind enum (incl. bytes_changed for template noise
   and conservative missing/removed states for the future re-check pass);
   daily manifests to provenance/manifests/ with previous-day hash chain;
   verify_stored() self-check. PROVENANCE.md states exactly what the
   records prove and — prominently — what they do not ("as served to our
   identified client"; first-seen ≠ published-at; anchoring declined and
   revisitable).
4. **Client generalization:** HttpClient base extracted (pacing, budget,
   logging, retries incl. HTTP-date Retry-After — a pre-existing gap);
   GovinfoClient behavior identical (all 12 pre-existing tests passed
   unchanged as the refactor gate); new AgencyClient: robots.txt fetched
   through the client itself (paced/budgeted/logged), parsed with protego
   (RFC 9309 — stdlib robotparser mishandles wildcards), 4xx=allow /
   5xx=temporary-disallow, crawl-delay honored, per-host cache;
   conditional-GET (304 passthrough); **separate daily budget buckets**
   via additive fetch_log migration (client column; NULL = historical
   govinfo rows) so agency crawling can never consume the govinfo budget.
5. **Review-agent findings adopted:** attempt-level manifests, hash
   chain, documents-not-URLs identity, two-hash split change semantics,
   unchanged_304 distinction, normalizer_version, header forensics,
   per-client budgets, protego, robots-via-client, Retry-After date form,
   S1-scope inversion (GH Releases + activation deferred to S2). Declined:
   promoting OpenTimestamps to S1 (user decision stands; recorded in
   PROVENANCE.md as revisitable).
6. **Tests: 181 passing** (+9 sources, +6 provenance, +7 client/agency,
   fixture fidelity improved to raise real requests.HTTPError).

**Next (S2):** agencies.py feed poller + article ingestion through
AgencyClient with capture; viability check script upgrading registry
statuses from live probes; Wayback SPN submission; digest section 6
(zero-LLM: counts + attributed titles); first real ingest run; site
rebuild. Then S3 re-check/change-detection pass, S4 GH Release bundles.

---

## 2026-07-26 10:30 PDT — Static HTML site: derived presentation layer

**Context:** Digests read poorly as raw Markdown in a browser; user wants
modern HTML output for local viewing and the envisioned GitHub Pages
publication. Planned in plan mode; implemented per approved plan.

**Work performed:**

1. **`publish.py` + `scripts/build_site.py`:** canonical digests/*.md →
   `site/` — one HTML page per digest + index, via the `markdown` library
   (tables extension; new dependency). Strictly derived output: zero LLM,
   zero network, idempotent, regenerable.
2. **Design:** no JavaScript, no external resources — renders identically
   from file://, GitHub Pages, or any static host. Shared `style.css`:
   system font stack, 46rem reading measure, deep-blue accent, automatic
   light/dark via prefers-color-scheme, striped scrollable tables (mobile-
   safe), responsive images, card-style index with Day-in-Review teaser
   sentences (extracted from the md), prev/next navigation, footer naming
   the canonical Markdown source and GUIDE §2. `.nojekyll` written for
   Pages.
3. **Asset handling:** digests' relative `assets/<date>/` layout is
   preserved by copying — no path rewriting of the canonical Markdown.
4. **Tests:** 6 new (structure, table/image conversion, nav, teasers
   newest-first, TEMPLATE exclusion, idempotent rebuild, real-data smoke);
   **suite: 159 passing.** Real build: 2 pages + 7 assets.

**Decisions:** `site/` is committed (published artifact, like digests/);
canonical output remains the Markdown — the GUIDE §5 REPORT paragraph now
says so explicitly. build_site is a separate stage, appended to the future
scheduled chain rather than run inside digest.py.

**Open questions / next steps:** unchanged, plus: GH Pages deploy workflow
(actions/deploy-pages over site/) when the repo goes public.

---

## 2026-07-25 18:05 PDT — Phase J1: judicial branch coverage via USCOURTS

**Context:** User direction to extend coverage to the judicial branch.
GUIDE §3 amended first (judicial coverage section: J1/J2/J3 phasing, the
MANDATORY completeness disclosure, filed-date semantics), then built.

**Empirical findings that shaped the build:**
- USCOURTS packages are case-shaped: one package per case,
  `pdf/<granule>.pdf` per opinion + mods.xml metadata; listing carries
  date_issued (opinion date) — both the digest date axis and a fetch
  filter for free.
- **9,401 changed packages in a 3-day delta window, 76% lastModified churn
  on years-old cases** (GPO backfill). Named rule **USCOURTS-FETCH-01**:
  only packages issued within 7 days are archived; churn is listed, marked
  'skipped' (the §4 status built for this), disclosed in the digest.
- **Publication lag confirmed live:** 8 packages for 07-24 vs 468 for
  07-23 at fetch time (Friday's opinions largely unposted) — the §3 lag
  disclosure is not theoretical.
- USCOURTS ZIPs are generated on-demand: ~9–22% of download requests
  returned 503+Retry-After, all honored (slow but respectful; ~38–60
  retries logged). Two user-initiated stops of the fetch were absorbed
  losslessly by the pending-queue design; 353 packages (07-23/24) archived,
  2,035 pending drain in future daily runs or age out of the window.
- Downloads now run newest-first across all collections.

**Built:**
1. `parsers/uscourts.py` (sub-agent): case ZIP → per-opinion records
   (granule = opinion id, doc_type = APPELLATE/DISTRICT/BANKRUPTCY/NATIONAL
   from mods with package-id fallback, case metadata incl. per-opinion
   date_filed, PDF text via pypdf, never aborts a package for one bad PDF).
2. Rules + renderer (sub-agent): USCOURTS-SEL-01/02 (appellate + national
   all listed), USCOURTS-EX-01/02 (district/bankruptcy counted); digest
   section "5. Judicial Activity" with the standing completeness
   disclosure, per-court item groups, category counts + FETCH-01 skipped
   disclosure; Coverage row + publication-lag known-gap; TEMPLATE updated.
3. Both build agents were killed mid-flight by a session usage limit;
   their on-disk work was verified directly (parser complete with 15
   passing tests; renderer complete, one line-wrap test assertion fixed).
4. **Extraction:** 353 packages → 1,264 opinion records, 16.2M chars, 0
   failures. Distribution: 49 APPELLATE / 1,207 DISTRICT / 8 BANKRUPTCY.
5. **Digests regenerated.** 07-24: judicial counts section, zero LLM cost.
   07-23: 101 items selected (was 51), 49 appellate opinions summarized +
   plain-lined (1 plain failure rendered without its line, per design);
   **compose invalidation fired in production** ("newer item summaries
   found — recomposing").
6. **Compose defect found and fixed:** the Day in Review prompt hard-coded
   a two-paragraph floor+executive structure, so judicial items were fed in
   but structurally squeezed out. Fix: three-branch prompt (judicial
   paragraph only when items exist) + **COMPOSE_PROMPT_VERSION** decoupled
   from PROMPT_VERSION (same lesson as the plain layer: prompt iterations
   must never regenerate item summaries). Recomposed both dates; 07-23 now
   opens with all three branches incl. Fourth Circuit holdings.
7. **Tests: 153 passing.**

**Measured (uncapped by design):** the judicial-heavy 07-23 re-run cost
**1.30M input / 88K output tokens (43 calls)** — the first day to exceed
the 1M working figure. Composition: ~50 opinions × 12K-char map inputs at
6/batch dominates. Cap-setting note: either the cap lands nearer 1.5–2M,
or opinion map inputs get a tighter excerpt strategy (opening + disposition
instead of first 12K chars) — decide after more ledger days. A normal
(non-backfill) judicial day is projected far lower (~49 appellate was a
full day's circuit output; the backfill doubled everything else on top).

**Open questions / next steps:**
- [ ] Cap decision with judicial data in the ledger (see above); consider
      opinion excerpt strategy for map inputs.
- [ ] J2: SCOTUS direct source (syllabus-first). Scheduling. Vision pass.
      Editorial spot-audit incl. judicial summaries (highest-risk prose).

---

## 2026-07-25 11:05 PDT — First full daily pipeline run; compose staleness fix

**Context:** First end-to-end rehearsal of the daily job (sync → extract →
digest) on live data, then a fix for a design gap the run exposed.

**Work performed:**

1. **Pipeline run:** sync 124 requests (58 new bill texts, 2 FR packages
   incl. FR-2026-07-25, zero failures); extract 59 packages → 235 records +
   17 graphic assets; digest generated for 2026-07-24 (newest complete day
   — the Record lags a morning).
2. **No CREC-2026-07-24 exists on govinfo** (chambers apparently not in
   session Friday). The system handled absence correctly: "no items" lines
   rendered, and the Day in Review states "no floor activity in the
   materials available" — then gives a clean account of the 82-document FR
   day (Title VI disparate-impact rescissions at three departments, four
   FDA device classifications, fishery closures, airworthiness directives).
   All 23 selected items carried official summaries — zero map calls; a
   quiet FR-only day costs ~57K tokens (1 plain batch + 1 compose).
3. **Design gap exposed and fixed:** day_summaries idempotency would have
   kept a stale Day in Review if the missing Record arrived in a later
   sync. compose_day now invalidates the stored composition when any item
   summary for the date is newer than it (timestamp-prefix comparison
   across the two stored formats), recomposes, and settles — proven by a
   clock-controlled test (compose → late summary → recompose → settle).
   133 tests passing.

**Decisions:** digest date for the daily run = newest *complete* day
(Record availability), not newest date with any data — an FR-only digest
for today would misrepresent a day whose congressional record hasn't
published yet.

**Open questions / next steps:** unchanged (scheduling with overlap guard;
cap from ledger data; vision pass; editorial spot-audit).

---

## 2026-07-25 10:20 PDT — Plain-speak layer: per-item plain-language renderings + readability mechanics

**Context:** User assessment of the first digest: accurate but hard to
parse as a human (verbatim official FR summaries are acronym-dense;
ALL-CAPS Record headings; unexplained procedural jargon). Planned in plan
mode with a design-review sub-agent; user chose per-item plain lines
covering all summarized items.

**Work performed:**

1. **Design deviation (improvement) from the approved plan, adopted from
   the design-review agent:** instead of extending the map-call contract +
   a summaries column + a PROMPT_VERSION bump, the plain layer is a
   **decoupled restatement pass**: new `plain_summaries` table keyed by
   (package, granule, PLAIN_PROMPT_VERSION, source_prompt_version), fed
   only by *stored summaries*. Wins: no migration (table auto-creates);
   phrasing iterations never regenerate factual summaries (~85K vs ~180K+
   tokens per iteration); editorially stronger — every plain line is
   checkable against the adjacent summary it restates; the 07-23 re-run
   cost only the plain pass. PROMPT_VERSION stays 1.
2. **GUIDE first** (§2 + §6 rule 9): plain renderings are labeled
   interpretation — derived only from the stored summary, no new facts, no
   significance judgments, visually distinct, linted un-masked, and an
   item whose restatement fails renders without one (presentation aid,
   never fabricated, never blocks the digest).
3. **`analyze.run_plain`**: batched (25 items/call — inputs are ~170-token
   summaries), cheap tier, strict-JSON, one-retry-then-honest-failure,
   idempotent; ledger purposes `plain:batchN`/`plain:retry`.
4. **Renderer**: `*In plain terms:*` line under every item (CREC, BILLS,
   FR); smart display-casing for ALL-CAPS headings (acronym/digit/dotted
   tokens preserved; disclosed in Methodology); static 15-term procedural
   glossary → "Terms Used Today" section listing only terms present
   (zero tokens); Methodology now states both version numbers and the
   plain-layer provenance. Banned list extended with plain-register
   evaluative framing (red tape, crackdown, slams, loophole).
5. **Validator caught my own bug during development:** glossary entries
   formatted `- **term**` matched the item-block pattern and were rejected
   for lacking inclusion-rule lines — exactly the class of error the gate
   exists for. Fixed by italic term formatting.
6. **Verification run:** only the plain pass executed (map + compose
   idempotent) — 3 Haiku calls, 86,311 in / 10,959 out tokens, **51/51
   plain lines, 0 failures**, validation passed. Spot-check: the
   suppressors interim final rule now reads "The Commerce Department is
   revising export controls to transfer firearm silencers ... to less
   restrictive Commerce controls..." — factual, jargon-free, neutral.
7. **Tests: 131 passing** (+4 run_plain, +5 report incl. un-masked-lint
   proof: a banned term in a plain line fails validation; a banned term in
   an official summary does not).

**Measured:** full-day bill with plain layer ≈ 235K in / 18K out
(149K map+compose + 86K plain) — ~24% of the 1M working figure; still
overhead-dominated (25K/call × ~7 calls).

**Open questions / next steps:** unchanged (cap after more ledger days;
scheduling; vision pass; periodic §2 editorial spot-audit — now including
plain lines).

---

## 2026-07-24 13:20 PDT — Phase 3 built; first digest generated (uncapped test run)

**Context:** Phase 3 (Analyze & report) built and test-run in one session:
LLM client + token ledger (main thread), analysis and rendering layers
(two concurrent sub-agents), compose stage added mid-build on user
direction (a full-day synthesis pass over the final outputs). Per GUIDE §6
rule 8 (amended today): uncapped, measure-first.

**Work performed:**

1. **`llm.py`** — LLM client backed by the `claude` CLI in headless mode
   (usage bills to the operator's Claude subscription; no API key), with a
   persistent token ledger (`data/llm_ledger.db`) mirroring the fetch log:
   every call recorded (model, purpose, package ids, tokens, duration,
   errors). Smoke test surfaced the decisive measurement: **~25K input
   tokens fixed overhead per headless call** — which dictated batching the
   map stage (≤6 items/call) before any real run happened.
2. **`rules.py` / `analyze.py`** (sub-agent): named mechanical rule
   registry (CREC-SEL-01 floor-time ≥15K chars; CREC-SEL-02 recorded votes
   always listed — regex calibrated on real Record text incl. a pinned
   false-positive guard for demanded-but-not-taken votes; BILLS-SEL-01
   reached-stage; FR-SEL-01/02/03 all rules/proposed/presidential) plus
   named exclusions for coverage. Map stage: official-summary-first (FR
   SUMMARY preambles stored verbatim at zero tokens), batched strict-JSON
   Haiku calls for the rest, one-retry-then-honest-failure, idempotent by
   (package, granule, prompt_version).
3. **`compose.py`** (main thread, user-directed scope addition): one
   strong-model "Day in Review" pass whose inputs are the stored item
   summaries + mechanical counts only — never the raw corpus. Stored in
   `day_summaries`; idempotent; rendered at the top of the digest; linted
   UN-masked by the banned-lexicon validator.
4. **`report.py` / `scripts/digest.py`** (sub-agent): fully deterministic
   zero-LLM render of TEMPLATE.md — header with git version + watermarks,
   CREC per chamber + votes, BILLS stage table, FR by agency with embedded
   graphics (TIFF→PNG via Pillow, ≤2/item + disclosure), SQL-computed
   Coverage Statement, methodology footer. Validation gate before any file
   is written: citation resolution against the DB, coverage arithmetic
   reconciliation (recomputed independently), banned-lexicon scan (official
   summaries masked; LLM prose not), inclusion-rule line on every item.
5. **Test run (uncapped), digest for 2026-07-23:** 51 items selected
   (33 official / 18 LLM), 4 LLM calls total — 3 Haiku map batches + 1 Opus
   compose — **148,571 input / 6,890 output tokens**, ~75 seconds of model
   time. Validation passed; digests/2026-07-23.md written (366 lines,
   51 inclusion-rule lines, 7 graphics embedded as PNG with the remainder
   disclosed). Day in Review reads factual and party-blind on inspection
   (recorded-vote tallies, proclamations, rule actions — no editorializing).
6. **Test suite: 125 passing** (llm 4, compose 3, analyze 14, report 11 +
   all prior), ruff clean.

**Measured baseline (the point of running uncapped):**
- ~150K input tokens/day for a full busy-day digest — **~15% of the 1M/day
  working figure**; two-thirds of it is CLI fixed overhead (4 × ~25K), so
  the marginal content cost is ~50K/day.
- Implication for the future cap: 500K/day would already carry ~3× margin;
  decision deferred until a few scheduled days accumulate in the ledger.

**Decisions:**
- Compose stage restored to the design (user direction; matches GUIDE §6
  rule 6's original tiering) — synthesis over stored outputs, never over
  raw corpus; strictest lint applied to it.
- Backend choice (claude CLI vs API SDK) recorded as revisitable: the CLI
  binds usage to the Max plan; if per-call overhead ever matters, an SDK
  backend on `llm.py`'s interface is a drop-in change.

**Open questions / next steps:**
- [ ] Accumulate a few days of ledger data, then set the cap (§6 rule 8).
- [ ] Schedule the daily pipeline: sync → extract → digest (launchd/cron,
      overlap guard).
- [ ] Vision pass on selected items' graphics (currently disclosed as "not
      yet implemented" in the Coverage Statement).
- [ ] Review the generated digest's editorial quality against §2 with fresh
      eyes after a few days of output.

---

## 2026-07-24 12:50 PDT — Phase 2 complete: extraction layer built and run over the full archive

**Context:** Phase 2 (Extract) built in one session: three collection
parsers and the graphics asset extractor developed concurrently by four
sub-agents against the real archive, with schema + orchestrator built in
the main thread, then integrated and run end-to-end.

**Work performed:**

1. **Schema** (db.py + docs/schema.md "Extraction layer" section):
   `extracted_texts` — one row per FR document / CREC granule / whole bill,
   composite key (package_id, granule_id), doc_type as the selection axis,
   JSON metadata (incl. official FR `SUMMARY:` abstracts per GUIDE §6),
   FR-GPH-01 graphic counts, extracted_at + extractor_version for
   staleness; `graphic_assets` — per-`<GPH>` inventory with classification,
   printed page, repo-relative asset path, status.
2. **Orchestrator** (`extract.py` + `scripts/extract.py`): staleness query
   (missing / raw re-fetched / version bump), per-package replace-on-rerun,
   per-package failure isolation, FR graphics inventory + image extraction
   to `data/assets/FR/<date>/<pid>/`. 6 orchestrator tests via fake parsers.
3. **Parsers** (sub-agents; pure functions, no DB; stdlib only):
   - `parsers/fr.py` — walks the full tree (sections are NOT reliably
     top-level: `NEWPART` nesting, `PRESDOC` wrappers); FRDOC regex
     extraction (PRESDOCU splits the wrapper across siblings); DATES vs
     EFFDATE variants; official SUMMARY captured to metadata. 743 documents
     across 7 issues, doc count == FRDOC count in every file.
   - `parsers/crec.py` — granule htm from the daily ZIP (files live under
     `html/` despite docs saying `htm/`; matched by filename pattern);
     verbatim text with line structure and page markers preserved, GPO
     header boilerplate dropped; issue-order sorting. 838 granules over 4
     days, 100% section-typed, zero empty texts. Granule `<title>` tags are
     issue-level boilerplate → titles come from our granules table instead.
   - `parsers/bills.py` — longest-type-first package-id decomposition
     (hconres before hr), stage attribute from either root form, sponsors
     (absent on 50/209 — post-introduction versions drop the block).
     209/209 parse; 9 stage values; two 118th-Congress bills present
     (lastModified revision tracking, same effect as the old FR issues).
4. **Graphics** (`graphics.py`, sub-agent): 103/103 substantive graphics
   extracted from the six companion PDFs (~10.5 MB; 100 TIFF, 3 PNG), all
   verified pixel-decodable; 8 boilerplate correctly skipped without
   opening a PDF. Notable engineering: pypdf's CCITT `get_data()` writes a
   corrupt TIFF header (missing next-IFD terminator) — module builds its
   own minimal TIFF around the raw Group-4 stream; FR PDFs carry no
   /PageLabels, so printed pages are recovered by scanning page-header text
   (a constant offset is provably wrong: unnumbered part-divider pages
   interleave mid-issue).
5. **Full run:** 220/220 packages extracted, **1,790 records, 22.7M chars,
   0 failures**; DB totals reconcile exactly with each agent's
   independently-reported per-file counts. FR doc-type distribution:
   566 NOTICE / 102 RULE / 67 PRORULE / 8 PRESDOCU.
6. **Test suite: 90 passing** (client 10, sync 14, extract 6, parsers 48,
   graphics 12), ruff clean.

**Decisions:**
- Parsers are pure `parse(raw_path, package) -> iter[record]` functions;
  the orchestrator owns all DB writes. Kept parsers standalone (FR-GPH-01
  regex duplicated locally rather than importing sync).
- Graphic assets stored as extracted (TIFF/PNG); conversion to
  web-embeddable format is a Phase 3 (REPORT) concern, at embed time.

**Open questions / next steps:**
- [ ] Phase 3: selection rules → mechanical aggregation → token ledger +
      1M/day cap → tiered summarization → digest generation per
      TEMPLATE.md (convert embedded graphics TIFF→PNG at embed time).
- [ ] Schedule the daily pipeline (sync → extract) via launchd/cron with
      the run-overlap guard.

---

## 2026-07-24 11:45 PDT — Graphics classification: rule FR-GPH-01 (boilerplate vs content)

**Context:** User inspected the fetched FR PDFs and observed graphics that
looked like boilerplate — the official seal, the President's signature —
questioning whether the PDF fetch is warranted. Investigated empirically.

**Work performed:**

1. **Ground truth from the XML.** FR `<GPH>` elements carry a `<GID>`
   filename that encodes what the graphic is. Content graphics use a
   section-coded pattern (`EN23JY26.004` etc. — EN/ER/EP/ED + date + seq):
   in our window these are *rate formulas rendered as images* (small,
   DEEP=15–30), agency forms, and full-page executive-order annexes
   (DEEP≈640). Signature graphics use non-conforming names — every
   boilerplate instance found was `Trump.EPS` (DEEP=80, right-aligned,
   following "IN WITNESS WHEREOF..." text). Key negative finding: image
   *size* is NOT a usable signal (equations are tiny but substantive);
   the GID naming convention is.
2. **Classification across the archive:** 111 flagged graphics = 103
   substantive + 8 signature boilerplate (all 8 in FR-2026-07-23's
   presidential documents). So the user-observed signatures are real but
   the minority; the companion PDFs remain justified — every one of the 6
   archived PDFs has ≥1 substantive graphic, so no pruning or re-sync was
   needed.
3. **Rule FR-GPH-01 implemented** (`classify_graphics()` in sync.py): PDF
   fetch now triggers only on ≥1 *substantive* graphic. Signature-only
   documents never cost a request, never get vision, never get embedded;
   boilerplate exclusions are logged and will be disclosed in the Coverage
   Statement. Codified in GUIDE §6 rule 1; TEMPLATE.md coverage line now
   splits observed graphics into content vs boilerplate-excluded.
4. **Tests:** fixtures updated to real GID structures; new signature-only
   test proves no PDF request is made; classifier unit test. 24 passing.

**Decisions:**
- Classification is by GID filename pattern — mechanical, party-blind, zero
  tokens — not by image size (provably misleading) and not by an LLM.
- The rule is named (FR-GPH-01) so digest exclusion disclosures can cite it,
  per the §2 pattern of named mechanical rules.

**Open questions / next steps:** unchanged (Phase 2 extraction; its graphic
inventory now records the substantive/boilerplate split per document).

---

## 2026-07-24 11:22 PDT — Graphics fetch implemented; FR re-synced with companion PDFs

**Context:** Implementing the fetch-layer half of the graphics scope change,
then re-syncing FR to backfill graphic content for already-held packages.

**Work performed:**

1. **`sync.py`: conditional companion-PDF fetch.** After an FR package's XML
   is archived, the bytes are scanned for `<GPH>`; if flagged, the package's
   PDF is also downloaded to a sibling path
   (`data/raw/FR/<date>/<pid>.pdf`). XML remains the primary artifact
   (`download_format` unchanged); no-graphics packages make no extra
   request; an already-present PDF is not re-fetched (idempotent). CREC
   needs no equivalent — its ZIPs already contain the PDFs.
2. **2 new tests** (22 total, all passing): flagged FR package archives both
   XML and PDF; unflagged package skips the PDF *and provably makes no PDF
   request*.
3. **FR re-sync** using the designed re-download path (flip `fetch_status`
   to `pending`, run `--collections FR`): 7/7 re-fetched, 0 failures,
   28 requests (day total 488/2000, ~24% of budget). Result: 6 of 7 issues
   carry graphics — companion PDFs archived for all 6 (111 flagged graphics
   total; FR-2026-07-23 alone has 54). FR-2026-07-24 (0 graphics) correctly
   skipped its PDF — the conditional verified live, both directions.

**Decisions:**
- Companion PDF presence is derivable (sibling path exists) rather than a
  new `packages` column — Phase 2's extractor checks the filesystem; if
  extraction later needs richer bookkeeping (per-graphic rows), that
  belongs in the Phase 2 schema addition, not a stopgap column now.

**Open questions / next steps:** unchanged — Phase 2 extraction (parsers,
graphic inventory + image-asset extraction from the now-present PDFs).

---

## 2026-07-24 10:55 PDT — Scope change: graphics become first-class (multimodal analysis + embedded in digests)

**Context:** Investigated whether XML-only extraction misses visual content.
Empirical answer from our archive: CREC and BILLS are pure text (BILLS
"graphic" grep hits were words like "geographic"); FR tables come through as
structured `<GPOTABLE>` XML (better than PDF for analysis); but FR carries
real graphics — 0–54 `<GPH>` elements per issue (maps, form facsimiles,
labeling examples, diagrams) whose content exists only outside the XML.
User direction: graphics are in scope — multimodal analysis, and final
digests should include relevant source graphics.

**Work performed (GUIDE first, per working agreement):**

1. **GUIDE §5 architecture** updated across all four stages: FETCH may pull
   PDF where graphics require it; EXTRACT inventories `<GPH>` per document
   and extracts individual image assets; ANALYZE runs a vision pass on
   selected items' graphics; REPORT embeds relevant graphics in digests
   (self-contained under `digests/assets/<date>/`).
2. **GUIDE §6 rule 1 amended** — was "PDFs never reach a model," now "whole
   PDFs never reach a model": text still comes from XML only, but
   individually-extracted graphics may go to vision, gated by the same
   selection rules as text, with image tokens counted against the daily cap
   and logged in the ledger.
3. **GUIDE §6 new rule 9** — graphics in digests are cited evidence, not
   decoration: embedded only for summarized items, carrying full citations;
   unrendered graphics are disclosed with a count and source-PDF link (§2
   no-silent-omission applies to images).
4. **Roadmap** Phase 2/3 items updated (graphic inventory + asset
   extraction; vision pass + embedding).
5. **digests/TEMPLATE.md** — FR item slots gain embedded-graphic blocks with
   captions, per-graphic citations, and a required disclosure line for
   unrendered graphics; Coverage Statement gains a source-graphics
   accounting line (observed / vision-analyzed / embedded).

**Decisions:**
- Graphics equal citizens editorially: same selection gating, citation
  discipline, and omission accounting as text. Factual captions only
  (§2 opinion-agnostic prose applies).
- Digest self-containment: selected graphics are copied into
  `digests/assets/` (committed) rather than hotlinked, so the published
  archive stands alone; volume is naturally small (only summarized items'
  graphics).

**Open questions / next steps:**
- [ ] Fetch-layer implication: FR currently downloads XML only. Phase 2 must
      add "fetch the PDF (or graphic files) when a package's XML flags
      `<GPH>`" — a second, conditional download per flagged package, well
      within request budget (graphics-bearing FR issues are a handful/week).
- [ ] Choose image-extraction approach from FR PDFs at Phase 2 build time
      (e.g., pypdf/pdfplumber image extraction vs page-region rendering).

---

## 2026-07-24 10:40 PDT — Token economics: measured the corpus, codified LLM budget rules

**Context:** User raised the right pre-Phase-3 question: can a daily archive
that measures 215 MB be summarized within a monthly Claude Code Max plan?
Answered empirically, then codified the answer as guidance.

**Work performed:**

1. **Measured the real text volume** (from our own archive, not estimates):
   a ~49 MB CREC day decomposes into ~46.6 MB of PDF page images and only
   ~2 MB of XML text. Per publication day: CREC ~2 MB, FR ~2.6 MB, BILLS
   ~2 MB text. Verbatim-everything ceiling ≈ 1.5–2M input tokens/day;
   with mechanical selection + official-summary-first drafting, realistic
   load is ~300–800K input / 10–20K output tokens/day. Conclusion: easily
   within a Max plan's daily headless run (limits are shared with
   interactive use and not token-denominated, so contention — not
   feasibility — is the consideration); even API pay-per-token would be
   ~$1–2/day, halved via batch processing.
2. **New GUIDE.md §6 "Token Economics (LLM Budget Discipline)"** — mirrors
   §4's philosophy (budgets as code): PDFs never reach a model; mechanical
   work costs zero tokens (an LLM call that could be SQL is a bug);
   official summaries (FR abstracts, CREC Daily Digest, bill titles) before
   our own; selection always precedes summarization; summarize-once-store-
   forever keyed by content version; model tiering (cheap map, strong final
   compose); a token ledger paralleling the fetch log with its own audit
   report; a hard daily input-token cap (initial 1M/day) whose overflow
   queues to tomorrow and is named in the Coverage Statement (a budget stop
   must never be a silent omission); batch-friendly, resumable analysis.
3. **Renumbering:** Roadmap → §7, Open-Source Readiness → §8, Working
   Agreements → §9. Cross-references updated in docs/schema.md; earlier
   worklog entries citing "§7" refer to the numbering current at their
   timestamps and are left as written.

**Decisions:**
- Daily LLM input cap set at 1M tokens (~half the verbatim ceiling, ~2×
  expected load) — enforced by the analysis runner when built, same
  hard-stop pattern as the HTTP client's request budget.
- Token spend gets the same two-layer accountability as server access:
  structured ledger + audit script.

**Open questions / next steps:**
- [ ] Phase 2 extraction unchanged; Phase 3 must implement the §6 rules as
      code (ledger, cap, tiering) alongside the first digest generation.

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

# Publication-readiness evaluation — 2026-07-29

Prompted by two external AI renderings of the project (a NotebookLM
audio overview and briefing document, generated from the project's own
documentation) and a full repository audit ahead of taking the repo
public. Companion checklist: `docs/pre-publication-todo.md`.

## 1. Sensitive-content audit: PASS

Audited all 26 commits of history, every tracked file, dangling objects,
and the reflog:

- The personal email appears **nowhere** — not in any blob, commit, or
  unreachable object. All commits are authored and committed as the
  public identity (David D. Karnowski, hustleyourcity address in
  metadata only; no tracked file asserts any personal address).
- **No absolute local paths** in any revision — the only `/Users/...`
  strings ever committed are the two policy sentences that tell us to
  check for them.
- **No secrets**: `.env` never committed; `.env.example` blank-valued
  (its one pre-commit near-miss was caught and is documented in the
  worklog — and verified absent from history); no key-shaped strings; no
  databases ever tracked. The only long hex strings are SHA-256 digests
  in provenance manifests, by design.
- digests/, site/, docs/: no paths, no emails, no internal hostnames.

GUIDE §9's discipline demonstrably worked. Two *structural* gaps were
found and fixed 2026-07-29: `research/` and `.claude/` were ignored only
by local, non-cloneable mechanisms (`.git/info/exclude`, global git
ignore) — both now in the tracked `.gitignore`, restoring the
"structurally impossible to commit" standard.

## 2. Editorial exposure: resolved by decision, not deletion

The worklog and commit history document the AI-assisted development
process in detail (agent-run research sprints, a subscription-cost
analysis, co-author trailers on all commits, and the pipeline's own
`claude` CLI backend in code). Decision (2026-07-29): **own it openly.**
A project whose editorial code requires labeling machine-generated prose
does not hide its machine authorship. The statement now lives at
`docs/site/ai-development.md` ("How AI Built This", published on the
site), GUIDE §9 records the policy, and the worklog remains untouched —
rewriting a timestamped record is not curation, it is falsification.

Two spots where *internal* vocabulary had leaked onto public pages
("operator's call before activation", "Operator steps before probe")
were rephrased to public register in the registry notes.

## 3. Fact-check of the external briefing (NotebookLM)

The generated briefing was largely faithful — its structure, philosophy
sections, and wire-behavior descriptions are accurate. Errors found,
with ground truth:

| Briefing claim | Ground truth |
|---|---|
| "226 passing tests" | **227** collected (193 test functions + parametrization) |
| "Hard caps (currently set at 1M)" on tokens | **No cap exists.** GUIDE §6 rule 8 is explicitly measure-first: "no hard cap is enforced until real test runs establish a measured baseline"; ~1M/day is a *working figure* for a future cap |
| "~150K input tokens" normal day / "1.3M" judicial day | Neither figure appears in project documents; measured runs were ~86–89K in/day; GUIDE's estimate range is 300–800K |
| "31% of the Tier 1–2 universe" (presented as current) | 22/72 **non-govinfo sources at the 2026-07-26 snapshot** (registry then 81, now 97); partly superseded — later research re-opened several via documented channels |
| Tier 1 "47 of 97", 19 active | **Correct** (47 tier-1, 47 tier-2, 3 tier-3; 19 active) |

**Lesson adopted:** external AI readers average whatever numbers they
find, including stale worklog snapshots (195/200 test counts, 81/93
registry sizes all appear in history). Remedy on the TODO list: a dated
"current state" block (STATUS section or file), regenerated with the
site, so there is exactly one authoritative snapshot to quote.

## 4. The access gap, elevated to philosophy

The most consequential external observation (operator's, from the audio
overview): significant agency/department sourcing is missing because
those web systems don't work with our safety-conscious access methods —
and nothing in our public materials said what we intend to do about it.
Now adopted (2026-07-29) in GUIDE §1 and §3 and on every public surface
(About, Methods, agents page, README): **continued engagement is a
mission pillar.** Documented-channel research, periodic re-probes, and
direct outreach to agency web/API teams; the registry's `unavailable`
records double as the outreach worklist; coverage grows by doors
opening, never by evasion. The evidence base is honest: documentation
research alone re-opened FCC, Commerce, NOAA, DOJ, US Courts, and USSC
candidates that probes had recorded as dead.

## 5. OSS hygiene and publication mechanics: the remaining work

None of it blocks correctness; all of it blocks *launch*. Zero of the
standard community files exist (LICENSE most importantly — and the
content-license decision for digests is the project's own
agent-ingestion promise left unstated); no CI runs the 227-test suite;
no workflow can deploy `site/` (wrong directory for branch-based Pages);
machine surfaces assumed domain-root URLs (fixed 2026-07-29 via
`SITE_BASE_URL`, pending a domain choice); the daily pipeline has never
been scheduled and its LLM stage requires the local `claude` CLI, which
cannot run in hosted CI without the planned API-backend swap. The
site's agents/about pages say "public repository" — true only after the
flip; flagged to change at flip time, not before.

Full itemization with recommendations: `docs/pre-publication-todo.md`.

## Verdict

**Content: publishable today.** History is clean, the register is
public-ready, and the one editorial question (AI-development narrative)
is resolved in favor of transparency with its own published page.
**Infrastructure: not yet.** The path to launch is the checklist — with
license selection and domain choice as the two decisions only the
operator can make.

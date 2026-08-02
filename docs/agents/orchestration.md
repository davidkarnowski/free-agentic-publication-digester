# Orchestration — dispatching section agents

How the main session (the orchestrator) hands work to section agents and
integrates what comes back. Modeled on a pattern proven in the operator's
Spiralyst project; adapted to one repo and Task-tool launches.

## 1. The one rule that prevents the worst incidents

**Section agents stage and report; only the orchestrator commits.** One
process calls `git commit`, by design — commit bundling and mixed
evidence/code commits are structurally impossible when only one actor
ever commits. (FAPD's own history has the motivating incident: merge-
conflict markers committed to WORKLOG.md on 2026-07-31 because a failed
`cd` short-circuited a shell chain and the next command staged blind.)

The evidence exemption (CLAUDE.md §8) is unchanged and belongs to the
*pipeline*, not to agents: automated evidence commits are made by the VPS
finalizer, never by a section agent.

## 2. File ownership

Every repo file has exactly one owner. The matrix below is the edit
surface each section file states in its own words; `tests/` follow the
code they test (an agent editing `analyze.py` owns `tests/test_analyze.py`
for the duration of its task).

| Owner | Files |
|---|---|
| Acquisition | `src/fapd/client.py`, `sync.py`, `agencies.py`, `email_sources.py`, `probe.py`, `sources.py` · `sources/registry.yaml` · `scripts/check_sources.py`, `scripts/sources_doc.py` · `docs/adding-sources.md`, `docs/email-sources.md` |
| Corpus & Provenance | `src/fapd/db.py`, `extract.py`, `graphics.py`, `provenance.py`, `src/fapd/parsers/*` · `docs/schema.md`, `PROVENANCE.md` |
| Editorial | `src/fapd/rules.py`, `analyze.py`, `compose.py`, `tags.py`, `insight.py`, `llm.py` |
| Publication | `src/fapd/report.py`, `publish.py`, `fedcal.py` · `digests/TEMPLATE.md` · `docs/accessibility.md`, `docs/site/*` |
| Operations | `src/fapd/collect.py`, `health.py` · `scripts/run_pipeline.py`, `scripts/collect.py`, `scripts/audit.py` · `deploy/vps/*` · `docs/ops/*`, `docs/continuous-ingestion.md` |

**Shared resources — orchestrator-owned. No section agent edits these;
the exit report carries the exact desired diff instead:**

| File | Why it is shared |
|---|---|
| `src/fapd/config.py` | Constants are policy (GUIDE §4); every section reads them, budget changes are operator decisions |
| `GUIDE.md` | The editorial constitution; amendments are the operator's alone and precede implementation (§10) |
| `CLAUDE.md`, `WORKLOG.md` | Cross-section governance and the append-only log; WORKLOG entries are written by the orchestrator with the merge |
| `src/fapd/db.py` `_DDL` block | Corpus owns the file, but DDL touches every section's queries — schema changes are coordinated through the orchestrator and `docs/schema.md` first |
| `tests/conftest.py` | The shared corpus fixture spans every section's tests |
| `pyproject.toml`, `.gitignore` | Dependency policy is deliberately minimal; one owner keeps it that way |
| `sources/registry.yaml` activations | Acquisition owns the file, but flipping a source to `active` requires gate-3 evidence the orchestrator verifies (GUIDE §3) |

## 3. Dispatch prompt template

Use this shape verbatim when launching a section agent (fill the
bracketed parts):

```
You are the FAPD [SECTION] agent. Read docs/agents/[section].md IN FULL
before doing anything else — it is your instruction source of truth and
this prompt does not repeat it.

TASK: [one paragraph: the outcome wanted, not the method]

CONTEXT: [what the orchestrator knows that the file doesn't: recent
incidents, related in-flight work, relevant review-finding IDs]

CONTRACT (non-negotiable):
1. Edit only files your section owns (your file §1 lists them). If the
   task seems to require editing a shared or foreign file, STOP work on
   that part and put the exact desired diff in your exit report instead.
2. Stage nothing, commit nothing. Leave the working tree modified.
3. Run `uv run ruff check .` and `uv run pytest -q` before reporting;
   report the actual numbers, including failures.
4. Follow docs/code-standards.md; match surrounding idiom.
5. New behavior gets a test that fails without the change.
6. If blocked, exit and report the blocker — do not improvise around it.

EXIT REPORT (required shape):
- Files modified (list)
- Shared-file diffs needed (exact diffs, or "none")
- Verification: ruff + pytest output tails, plus any manual checks run
- Deviations from the task, with rationale
- What a human should look at before this merges
```

## 4. Integration

The orchestrator, on receiving an exit report: reviews the diff, applies
any shared-file diffs itself, runs the full gates again, writes the
WORKLOG entry, commits with a narrative body (CLAUDE.md §8), and merges
per the branching rules. Feedback goes back to the same agent via
SendMessage rather than spawning a fresh one — the context is the asset.

## 5. Escalation boundaries (any section)

These always go to the operator, never decided by an agent at any level:
raising request budgets, loosening validation gates, evading an access
refusal, GUIDE amendments, VPS actions, making the repo's posture more
public, and anything in CLAUDE.md §10's confirm-gates.

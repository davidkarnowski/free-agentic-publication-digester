# Contributing

Thanks for your interest. This project has an unusual governance rule
that shapes every contribution:

## GUIDE.md comes first

**GUIDE.md is the editorial constitution.** Changes to editorial
behavior — what gets selected, how it is summarized, what the digest
promises its readers — are made in GUIDE.md *before* they are made in
code (GUIDE §10). A pull request that changes editorial behavior
without a corresponding GUIDE amendment will be asked to split into
two: the amendment first, the implementation second. Engineering
conventions live in `CLAUDE.md` and `docs/code-standards.md`; if they
ever disagree with GUIDE.md, GUIDE.md wins.

Some things are not open to loosening by PR at all: request budgets,
crawl-delay compliance, the validation gates (a digest that fails one
is not published — there is no override), and the banned-lexicon gate.
These are the project's identity, not tuning knobs.

## Practical rules

- **Branches:** main is sacred for code. Work on `feature/…`, `bug/…`,
  or `arch/…` branches; CI must be green before a fast-forward merge.
  (Pipeline evidence — `digests/`, `provenance/`, `site/`, `SOURCES.md`
  — commits direct to main by design; never mix evidence and code in
  one commit.)
- **Tests:** `uv run pytest -q` (the suite is 350+ tests and runs in
  seconds; no test touches the network). New behavior needs tests;
  contracts others rely on get pinned by them.
- **Lint:** `uv run ruff check src/ scripts/ tests/` (line length 100).
- **Commits:** `area: plain-English subject` with a narrative body —
  the why, the tradeoffs, what was verified. The log is documentation.
- **Adding a source:** read `docs/adding-sources.md` first. Sources
  activate on evidence, and a recorded refusal is never erased.
- **Worklog:** `WORKLOG.md` is append-only and never retroactively
  edited.

## AI involvement

This project is built with AI agents under an operator's direction, in
the open (see the site's "How AI built this" page). Human and AI
contributions are equally welcome and get the same review; AI-assisted
PRs should say so, and every commit derived from agent work carries a
co-author trailer.

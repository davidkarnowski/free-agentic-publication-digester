# Section agents — the router

FAPD is segmented into five sections with explicit boundaries so that work
can be split across focused agents (or focused human sessions) without any
of them needing the whole system in context. Each section has one
instruction file here; `orchestration.md` governs how work is dispatched
and how results come back.

**If you are a section agent:** read your section file in full before
touching anything. It is your source of truth; CLAUDE.md and GUIDE.md bind
you through it.

**If you are the orchestrator (the main session):** read
`orchestration.md` before dispatching, and use its prompt template
verbatim.

| Section | File | Owns, in one line | Launch for |
|---|---|---|---|
| Acquisition | [acquisition.md](acquisition.md) | HTTP clients, sync, adapters, email ingest, the source registry | New sources, adapter work, politeness/budget mechanics, probes |
| Corpus & Provenance | [corpus.md](corpus.md) | Schema, extraction, parsers, captures, manifests | Schema changes, parser fixes, provenance/integrity work |
| Editorial | [editorial.md](editorial.md) | Selection rules, model layers, prompts, the LLM client | Rule changes, prompt versions, token economics, summarization |
| Publication | [publication.md](publication.md) | Digest render + validation gates, the whole site | Digest layout, /today, accessibility, validation gates |
| Operations | [operations.md](operations.md) | The supervisor, health, the pipeline script, deploy | Worker/scheduling bugs, VPS stack, runbooks, budgets-in-motion |

Boundaries are by concern first, directory second. Every file in the repo
has exactly one owning section; the shared files no section may edit are
listed in `orchestration.md` §2 — for those, agents write the exact
desired diff in their exit report and the orchestrator applies it.

The section files each carry a **Current backlog** of findings from the
2026-08-02 code review (`docs/code-review-2026-08-02-amended.md`), so a
freshly launched agent knows the known defects in its area before adding
new work on top of them.

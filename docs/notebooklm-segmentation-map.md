# NotebookLM prompt — FAPD segmentation map

A ready-to-paste prompt for generating a visual map of the project's
five-section segmentation and agent roles. Written 2026-08-02, the day
the segmentation landed.

## Sources to add to the notebook (in this order)

1. `docs/agents/README.md` — the router
2. `docs/agents/orchestration.md` — ownership matrix + dispatch contract
3. `docs/agents/acquisition.md`
4. `docs/agents/corpus.md`
5. `docs/agents/editorial.md`
6. `docs/agents/publication.md`
7. `docs/agents/operations.md`
8. `CLAUDE.md` — §11 (the router table) and §9 (intentional decisions)
9. `GUIDE.md` — the editorial constitution the sections answer to

## The prompt (paste verbatim; works for Mind Map, Infographic, or a
## described diagram you can hand to any image tool)

---

Create a system map of the Free Agentic Publication Digester (FAPD)
showing its five-section segmentation and the agents that own each
section. Use ONLY the loaded sources. Structure the map exactly as
follows.

**Center:** "FAPD — Free Agentic Publication Digester" with the
one-line mission: an automated, citation-bound, opinion-agnostic daily
digest of official US federal publications, for humans and AI agents.

**Ring 1 — the pipeline as a left-to-right flow** (this is the data
path, and the sections sit ON it):

ACQUISITION → CORPUS & PROVENANCE → EDITORIAL → PUBLICATION
with OPERATIONS drawn beneath all four as the platform they run on.

**Ring 2 — for each of the five sections, a card with exactly four
elements**, pulled from that section's own instruction file:

1. *Mission* (its one-line "owns" statement from the router table)
2. *Edit surface* (3–5 representative files, e.g. Acquisition:
   client.py, sync.py, agencies.py, registry.yaml)
3. *The two rules that override everything* (each file's §"Two rules"
   — quote them tightly, e.g. Editorial: "no model sees an item a
   rules.py rule did not promote"; Operations: "VPS actions only on the
   operator's explicit ask in the current session")
4. *One defining incident* (the dated event that shaped it:
   Acquisition — 528 robots refetches/day, F-007; Editorial — 39.7M
   tokens on retries, 2026-07-31; Publication — 721 archive items
   rendered as today's news; Operations — 35 duplicate pipeline runs,
   2026-08-01; Corpus — the live-WAL copy that arrived corrupt,
   2026-07-30)

**Ring 3 — the orchestrator**, drawn above the sections with three
labeled arrows down to them:
- "dispatches with a fixed contract" (the verbatim prompt template)
- "owns the shared files" (config.py = policy, GUIDE.md = operator
  only, WORKLOG.md, the DDL block, conftest.py)
- "alone commits" — label this arrow with the rule verbatim: "section
  agents stage and report; only the orchestrator commits"

**Edges to draw between sections** (the coupling that boundaries must
respect):
- Acquisition → Corpus: "fetched bytes, captures" 
- Corpus → Editorial: "extracted_texts (selection reads, never writes)"
- Editorial → Publication: "summaries, versioned by prompt"
- Publication → the public: "digest (validated, frozen at EOD) and
  /today (derived, disposable)" — mark this edge with the gate: "a
  digest that fails validation is never published, no override"
- Operations → all: "budgets, reserves, worker clocks, deploy"

**Legend box:** three governing layers in precedence order — GUIDE.md
(constitution, operator amends), CLAUDE.md (working guide),
docs/agents/*.md (per-section law). And one motto that appears in the
sources and should anchor the graphic: "every rule is either grep-able
or carries the dated incident that created it."

Style: clean, technical, no decorative imagery; the five sections in
five distinct muted colors; incidents in small red-tinted callouts;
the only-the-orchestrator-commits rule visually unmistakable.

---

## Follow-up prompts that work well in the same notebook

- "For each section, list its current review-backlog items (the D/R
  identifiers) as a table — section, item, one-line description."
- "Draw the day in the life of one document: from a govinfo listing to
  its line in the published digest, naming which section touches it at
  each step and which rule admits or excludes it."
- "Quiz me on the two overriding rules of each section until I can
  recite all ten."

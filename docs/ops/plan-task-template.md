# Plan-task template

*Required shape for any plan task that touches production, governing
documents, or the editorial gates (CLAUDE.md §12). Adopted 2026-07-30
from the operator's sibling project.*

Each task states:

- **Why** — one-sentence rationale.
- **Files** — exact paths touched.
- **Diff sketch** — the intended change, concrete enough to apply;
  re-anchor if the file has drifted.
- **Justification** — why *this exact* change; naming, placement, size.
- **Alternatives considered** — rejected paths, with brief reasons.
- **Risk / blast radius** — what else could break; the test surface.
- **Verification** — concrete commands that confirm success.
- **Rollback** — how to undo.
- **Dependencies** — tasks that must precede.

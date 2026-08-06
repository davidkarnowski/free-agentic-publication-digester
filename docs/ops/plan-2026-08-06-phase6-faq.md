# P6 — FAQ page (backend-file-first; zero render code)

**Files:** `docs/site/faq.md` (new), `docs/pre-publication-todo.md`.

The doc-page pipeline already does everything: `publish._doc_sources`
(publish.py:1212) globs `docs/site/*.md` → `faq.html` + nav ("More")
+ llms.txt + sitemap automatically. Markdown is the versioned backend
file; HTML is derived. No publish.py edits.

`docs/site/faq.md` first entries (H1 `# Frequently Asked Questions`):
1. **FAPD's three clocks** — the operator's formulation verbatim
   (Action / Publication / Observation, what may be missing, why
   observation is the source of truth for filing and sequencing).
2. **How our collectors work** — third-grade level: polite readers
   that visit official government sites on fixed clocks, never faster
   than a site allows, and write down what they saw and exactly when.
3. **How often we look** (→ observation windows) — table from config:
   agency/email/analyze workers ~15-min cycles (±15 min windows);
   live page rebuilds ≤5 min; govinfo collections on the hourly sync;
   gao.gov feed-only under its 420-second crawl-delay; the digest
   freezes at midnight Eastern. Each row phrased as "observed within
   about X of appearing".
4. Cross-link target for §1's three-clock line (`faq.html#three-clocks`
   — verify the toc extension's anchor ids).

`pre-publication-todo.md` sub-task (filed 2026-08-06): **develop the
FAQ page** — grow beyond these entries (selection rules, funding
guardrails, forking); backend-file rule stated: site prose pages are
always authored as `docs/site/*.md`, never hand-written HTML.

**Verify:** local `build_site` renders faq.html with nav + sitemap
entries; anchors resolve.

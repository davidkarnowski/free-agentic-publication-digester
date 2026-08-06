# Observation-day filing — index & context

**Why.** Every automatically-frozen digest has an empty §1. Verified
2026-08-06 against production: CREC-2026-08-04 was fully processed
(62/62 extracted, 5 passed threshold, 5 summarized) and the summaries
are published nowhere — the 08-04 digest froze 04:47Z, the Record
arrived 11:42Z. Thresholds ruled out by data. BILLS shows the same
morning-after pattern; USCOURTS trickles 4–5 days.

**Operator ruling.** Filing key = **Date of Observation** — the only
timestamp FAPD defines precisely from its own worker metadata. The
three clocks: Date of Action (from text; may be absent), Date of
Publication (publisher metadata; may be absent), Date of Observation
(ours; absolute; THE filing key). Outage rationale: publisher-metadata
filing can drop a late-stamped document into a frozen day;
observation filing cannot drop anything, ever. Watermark sync keeps
observation ≈ publication (+8–17 min median, measured). FR is the one
exception (cover-date; govinfo posts it early — FR-2026-08-03 observed
08-01). Orphans (CREC issues observed 08-04/08-05): forward-only,
dated methodology note. Cutover encoded in data so frozen digests
re-render identically.

**Phases.** P0 governance · P1 schema+backfill · P2 query seam ·
P3 renderings/disclosure · P4 tests · P5 deploy+prove tonight ·
P6 FAQ page · P7 edge-log rotation · P8 record. Per-phase files:
`plan-2026-08-06-phase{N}-*.md` beside this index.

**Global verification.** `uv run pytest -q` (607+) and ruff clean at
every phase boundary; dev-stack render before deploy; tonight's digest
2026-08-06 §1 carries the Record observed 08-06 or states honestly
that none was observed.

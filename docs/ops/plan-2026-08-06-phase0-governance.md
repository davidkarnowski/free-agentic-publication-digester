# P0 — GUIDE amendment + CLAUDE.md (precedes all code, GUIDE §10)

**Files:** `GUIDE.md`, `CLAUDE.md`, (schema doc changes live in P1).

**1. GUIDE §3, after the "Dating rule" bullet in the agency-newsrooms
subsection is NOT the spot** — this is govinfo-collection filing. Add a
new Pattern-C amendment block at the END of `### Primary: govinfo
(GPO)` (GUIDE.md ~line 162–189, before `### Collections of interest`):

```markdown
**Amended 2026-08-06 — observation-day filing (operator).** A govinfo
package is filed under the Eastern publication day of its FIRST
OBSERVATION by our collector (`sync.publication_date_of(first_seen_at)`),
written once and never re-derived — a later revision re-fetch never
re-files a document. FAPD's three clocks, in disclosure order:
*Date of Action* (as described in the text — proceedings date, opinion
issue date; may be unavailable), *Date of Publication* (publisher
metadata; may be unavailable), *Date of Observation* (ours — the only
timestamp defined precisely from our own worker metadata, and the
source of truth for filing and sequencing). Why observation and not
publisher metadata: a source outage under metadata filing files a
document into a day whose digest is already frozen — dropped from the
record; under observation filing nothing observed can ever miss its
digest. Per-collection policy: CREC, BILLS, USCOURTS, PLAW file by
observation day; FR files by its cover date (the FR is legally
published on its cover date, and govinfo posts it early — the
2026-08-03 issue was observed 2026-08-01); AGENCYPR keeps the §3
agency dating rule unchanged (filing agency feeds by observation is
the 721-item backfill failure of 2026-07-31). Every observation-filed
item or section states the document's own date, and the publisher
stamp where available, beside the digest day. Cutover: filing changed
with digest 2026-08-06; rows first seen earlier keep cover-date filing
so every frozen digest re-renders identically (§5 reproducibility).
The two Record issues observed 2026-08-04/05 (proceedings of
08-03/08-04) predate the cutover and appear in no digest — their
summaries remain in the corpus and day views; disclosed, not
backfilled.
```

**2. GUIDE §5** — append one sentence to the 2026-08-05 supersession
amendment: "*(2026-08-06: observation-day filing removes the CREC case
that motivated this amendment; it remains for genuine corrections.)*"

**3. CLAUDE.md §9** — amend two entries: the BILLACTIONS "Bill actions
are dated by the publisher…" note gains "(2026-08-06: BILLS-the-
collection now files by observation day — the §3 amendment; the
BILLACTIONS section is unchanged.)"; add a new bullet: "**Digest
filing for govinfo collections is by observation day**
(`packages.digest_day`, GUIDE §3 amended 2026-08-06); `date_issued`
remains the document's own date for display and the USCOURTS fetch
window — do not 'simplify' queries back onto it."

**4. CLAUDE.md §14** decision log entry (dated 2026-08-06):
observation-day filing, three clocks, FR exception, forward-only
cutover.

**Verify:** prose only — `uv run pytest -q` unaffected; read the diff
aloud against the operator's ruling. **Rollback:** git revert.

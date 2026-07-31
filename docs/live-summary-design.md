# Live-page plain-speak summarization — design memo

*2026-07-31. Status: proposal — design exploration only, nothing here is
built. No code, test, prompt, or GUIDE text was changed to write this.
Companion to `docs/continuous-ingestion.md` (§4 the token trade, §8 the
`/today` renderer) and GUIDE §2 (labeling, banned lexicon), §3a (prompt
governance), §5 (two-artifact model), §6 (token economics). Last
reviewed: 2026-07-31.*

## §1 The question, and the reader-facing gap

The operator's question, verbatim:

> "Live-page plain-speak summarization. Let's use some measured way to
> provide plain-speak update for the day, so-far, or as significant
> publications are published. I feel like we need a basic and low-token
> way of providing summaries before the digest for the entire day is
> made."

`/today.html` fetched 2026-07-31 at 17:54 ET shows the shape of the gap.
The page carries its GUIDE §5 disclosure, an explanation of the Eastern
publication day, the line "238 item(s) observed so far · 0 item(s)
awaiting model summary", 42 keyword filter chips with counts (executive
238, notice 107, press release 90, u.s. attorneys news (email) 64), and
then 238 entries newest-first. The first two read:

- "Illegal Alien Pleads Guilty to Cocaine Trafficking Charge" — agency
  announcement via email bulletin, followed by the unedited opening of
  the official text.
- "Federal Jury Finds Man Guilty of Four Robberies with a Firearm" —
  the same shape.

Every mechanical fact a reader could want is on that page. What is
missing is one honest sentence answering *what the day amounts to so
far*. The page is a ledger of arrivals; a reader who opens it at lunch
learns that 238 things happened, in what order, tagged how — and must
read 238 entries to learn anything else. The Day in Review that would
answer the question exists only at end of day, by design (GUIDE §6 rule
12: compose describes a completed day, and its staleness rule would
recompose on nearly every intraday batch).

Two structural facts constrain what any intraday text can honestly say,
and both belong in the design before the options do:

1. **Most `/today` items carry no summary at all.** Agency releases
   (`AGENCYPR`) and recorded votes (`VOTES`) have no entry in
   `rules.RULES`; `rules.select_items` never promotes them, so
   `analyze.run` never sees them. The digest lists them by title, link,
   agency, and dating rule (`report.py:470-530`). Federal Register
   notices are excluded from summarization too (`FR-EX-01`, counted not
   summarized). On the page above that accounts for 90 agency releases
   (64 of them email bulletins from a single source) and 107 notices —
   197 of 238 items with no summary layer beneath them. The remaining
   41 match the 41 summaries `provenance/runs/insight-2026-07-30.md`
   records for 2026-07-31. Any "day so far" text is therefore composed
   over a minority of the day's items and must say which minority.
2. **The legislative and judicial record arrives late.** The
   Congressional Record for day D publishes the following morning — the
   2026-07-29 digest was generated 2026-07-30T19:37Z. Court opinions
   post with disclosed lag (GUIDE §3, judicial date semantics). An
   intraday brief for day D can describe the Federal Register issue,
   agency announcements, presidential documents, enacted laws and
   same-day recorded votes. It structurally cannot describe today's
   floor proceedings. That limit has to be stated in the text itself,
   not buried in a methods page, or the brief silently misrepresents
   the legislative branch as quiet.

## §2 The economics that decide this

The design variable is the **number of calls**, not the size of the
prompt. Our own ledger says so with unusual clarity. Grouping
`data/llm_ledger.db` by purpose:

| purpose | calls | min input | mean input | payload |
|---|---|---|---|---|
| `smoke-test` | 1 | 25,246 | 25,246 | a few words |
| `plain:retry` (single item) | 27 | 25,710 | 25,832 | one stored summary, ~170 tokens |
| `plain:batch1` (25 items) | 8 | 26,386 | 29,255 | 25 stored summaries |
| `map:batch1` (6 items, full text) | 8 | 28,737 | 36,625 | up to 6 × 12,000 chars |

A call carrying twenty-five items costs **13% more** than a call
carrying one. The floor for a call carrying almost nothing is 25,246
tokens. Daily means over the whole local ledger sit between 28,361 and
30,646 tokens per call regardless of what the day's calls were doing.
GUIDE §6 rule 14 uses ~29K as the working figure; that is what this
memo prices against.

The consequences, already recorded in the constitution:

- Run day 2026-07-30: 17,441,543 input tokens, 79.5% retries, 366
  single-item retries costing 10,860,137 — 62% of the day — to buy
  summaries of roughly 800 tokens each. This produced rule 13 (analyze
  only the current publication day and the one before) and rule 14 (a
  ceiling on single retries).
- Run day 2026-07-31, `provenance/runs/insight-2026-07-30.md`:
  65,800,226 input tokens across 2,091 calls, 1,345 of them
  `map:retry-single` at 39,712,610 tokens. The ceiling landed at
  16:16 UTC that day; most of those retries predate it.

Two denominators are available and neither is a steady state we have
actually observed:

- **The design target.** GUIDE §6 puts realistic daily load at
  300–800K input tokens. At ~29K/call that is roughly 10–28 calls a
  day: 2–3 map batches, 1–2 plain batches, one compose, one sections,
  one tags, one insight, and a few retries.
- **The measured days.** 17.4M and 65.8M input tokens, both
  pathological, both now addressed by rules 13 and 14.

Every option below is priced against both, honestly, because pricing a
new surface only against a 65.8M-token day would make anything look
free.

**One arithmetic hazard worth naming before designing anything
intraday.** Under continuous ingestion, "per run" is not "per day". The
retry ceiling `MAX_SINGLE_RETRIES_PER_RUN = 12` is applied inside
`analyze.run` and `analyze.run_plain`, each of which the `AnalyzeWorker`
may call once per pending date per cycle, with cycles spaced only
`ANALYZE_MIN_INTERVAL_MIN = 15` apart — up to 96 cycles a day, over two
dates, over two layers. Nothing in this memo proposes changing that; it
is noted because it is the reason **any intraday design must count its
calls per day, enforced from the ledger**, exactly as request budgets
are counted from the fetch log. A ceiling expressed per cycle is not a
ceiling.

## §3 The zero-token baseline: what SQL already knows

GUIDE §6 rule 2 is not a preference: an LLM call that could have been a
SQL query is a bug. So the mechanical option is the incumbent, and the
model has to beat it on merit.

Everything below is available from `item_journal`, `extracted_texts`,
`packages`, `summaries` and `rules.py` at zero tokens, on every render
cycle (~5 minutes), with no new dependency:

- **Branch and class roll-up.** "So far today: 7 final rules, 3
  proposed rules, 107 notices, 2 presidential documents, 90 agency
  releases from 21 agencies, 64 email bulletins, no recorded votes, no
  Congressional Record issue yet." Every number is a `GROUP BY`.
- **Named mechanical classes, listed in full.** Enacted laws
  (`PLAW-SEL-01`), presidential documents (`FR-SEL-03`), recorded votes
  (`VOTES`) — each a discrete, dated act, each already listed by
  existence rather than by judgement. Titles are verbatim official text
  and cost nothing.
- **Agency league table.** Releases per agency, descending, mechanical.
- **Arrival rate.** "38 items in the last hour; 96 in the last three
  hours" — `observed_at` is indexed and the render already runs on a
  5-minute clock.
- **Coverage-so-far.** "238 observed · 41 carry a summary · 0 awaiting
  model summary" — `today_status` computes two of the three today.
- **"What arrived since you last looked."** For agents this is already
  solved and needs no new work: `today.json` carries `observed_at` per
  item and `last_observed_at` for the page, so a polling client
  computes its own delta. For humans, with no JavaScript and no server
  compute, per-reader state is not available; the honest approximation
  is the arrival-rate line plus hour-bucketed anchors in the stream.

What the baseline cannot do: say what a document *says*. "7 final
rules" is not "the FAA grounded a variant of a Boeing airplane, the FDA
reclassified a device, and USDA changed how wetlands are determined."
Federal Register titles are the clearest evidence of the limit —
"Airworthiness Directives; The Boeing Company Airplanes" is a precise
official title and tells an ordinary reader almost nothing. The gap
between a count and a sentence is exactly the gap the operator
described, and it is the only thing a model is being bought for here.

## §4 Candidate designs

### Option A — Mechanical "day so far" board (zero tokens)

**Trigger:** every `/today` render (already every ~5 minutes, and only
when the journal watermark moved).
**Prompt shape:** none.
**Calls/day:** 0. **Tokens/day:** 0.
**Produces:** the §3 board, rendered above the stream: class counts,
enacted laws and presidential documents and recorded votes listed by
title, an agency table, arrival rate, and the coverage-so-far line.
**Degrades:** it does not. There is no model in the path; it fails only
when the page itself fails.

This is a strict improvement on the current page and should be built
whether or not anything model-generated ever is. It is also the
fallback surface every other option needs.

### Option B — One-call "day so far" brief on a fixed Eastern clock

**Trigger:** two scheduled slots on the publication clock, ~11:00 ET
(after the Federal Register's 08:45 ET release has been polled,
extracted, and given its zero-token official summaries) and ~17:00 ET
(after the working day's agency flow). Both gated by zero-cost skip
conditions evaluated in SQL first: skip when fewer than a floor number
of stored summaries exist for the date, and skip when no new summary
has been written since the last brief.
**Prompt shape:** the compose contract, re-pointed at a partial day.
Inputs are **stored summaries only** plus mechanical counts — never raw
text, never outside knowledge, the same discipline `compose.compose_day`
already keeps. Output is 2–3 short paragraphs in present tense with an
explicit "so far today" frame, a mandatory clause naming what has not
arrived yet (the Congressional Record for the day, court opinions), and
the §2 constraints restated inside the prompt as every other surface
restates them.
**Calls/day:** 2 (hard ceiling 3, see Option C).
**Tokens/day:** 2 × 29,000 = **58,000 input**, plus roughly 1,400
output per call ≈ 2,800 output.
**Produces:** a labeled, visually distinct paragraph block at the top of
`/today`, and a matching object in `today.json`, both stamped with the
observation time they cover and the fraction of items they saw.
**Degrades:** the model is a dependency of the paragraph, not of the
page. On an `LLMError` nothing is written; the page shows the previous
brief with its own timestamp ("as of 11:04 ET, covering 41 of 238
items observed through 10:58 ET") or, before the first brief of the
day, shows no brief at all. The Option A board is unaffected. This is
the posture GUIDE §2 already sets for plain-language lines: an item
whose plain rendering fails renders without one.

The property that makes this option safe is that **its cost is flat in
the size of the day**. Two calls on a 7-item Saturday, two calls on
2026-07-28's 2,678 journaled items. The prompt grows with the number of
*summarized* items — 126 on that flood day, about 50K characters at the
400-character truncation `compose.py` already uses, well inside one
call — and the payload is 13% of the price anyway.

### Option C — Significance-triggered brief

**Trigger:** a mechanically coded event class lands in the journal (see
§6): a public law, a recorded vote, a presidential document.
**Prompt shape:** as Option B, plus the triggering item named.
**Calls/day, uncapped:** unbounded in exactly the wrong direction —
the classes clump. Laws are signed in batches; the Senate takes ten to
twenty roll-call votes on a heavy day; 2026-07-29 carried two
presidential documents. An uncapped trigger could fire 20+ times, or
580,000+ input tokens, on precisely the days when map and plain are
also busiest.
**Calls/day, capped:** whatever the cap is, which means the cap is the
design and the trigger is decoration.
**Produces:** timelier text after a discrete event.
**Degrades:** as Option B, plus a new failure of its own — a trigger
storm during a model outage leaves a queue of firings that must be
collapsed rather than replayed.

Option C is not viable standing alone. It is viable as a **pull-forward
mechanic inside Option B**: a trigger-class arrival may cause the next
scheduled slot to run early, consuming that slot; it may never add a
slot. A third slot exists only to absorb an evening trigger after the
17:00 brief. The ceiling is then `MAX_LIVE_BRIEFS_PER_DAY = 3` = 87,000
input tokens, counted from the ledger the way request budgets are
counted from the fetch log, so it holds across processes and restarts
and cannot be bypassed by a restart loop.

### Option D — Summarize the agency stream so every live item has a line

**Trigger:** the existing batch-threshold-or-age trigger, with
`AGENCYPR` promoted by a new selection rule.
**Calls/day:** the 2026-07-31 page carried 90 agency items by 17:54 ET;
the local journal records 282 for 2026-07-28. At `MAX_BATCH_ITEMS = 6`
that is 15–47 map calls, and the plain layer at 25 per call adds 4–12
more: **19–59 calls a day**.
**Tokens/day:** **551,000 to 1,711,000 input** — between two-thirds of
the design-target day and more than twice it, before any retry, and
retries are where both measured days went wrong.
**Produces:** a plain line under every live item, which is genuinely
what a stream reader wants.
**Governance:** promoting `AGENCYPR` to a selection rule is a GUIDE §6
rule 4 change and a §2 coverage-symmetry question (which agencies? all
of them? then the volume is the volume), not a live-page feature.

Rejected here, but recorded because it is the design most likely to be
proposed next and it should be costed before it is, not after.

## §5 Recommendation

**Build Option A unconditionally. Add Option B at two slots with
Option C's pull-forward as the only event responsiveness, hard-ceilinged
at three calls a day.**

The reasoning, stated so it can be argued with:

1. **The baseline is not sufficient, and the reason is specific.** Rule
   2 says an LLM call that could have been SQL is a bug. A count is not
   a sentence, and no amount of SQL turns "Airworthiness Directives;
   The Boeing Company Airplanes" into ordinary words. That
   transformation is the one thing being bought, and it is the same
   thing the digest already buys at end of day. The baseline is
   nonetheless built first and stays permanently, because it answers
   "how much" and "from whom" better than prose does and it is what
   remains when the model is unavailable.
2. **Two calls is the smallest purchase that answers the question at
   all.** One call cannot cover both the morning regulatory picture and
   the afternoon agency flow; a reader arriving at 16:00 would read a
   brief describing a day that was a quarter old. Three or more buys
   granularity nobody asked for at 29K a step.
3. **The cost is flat and knowable.** 2 × 29,000 = **58,000 input
   tokens/day**; ceiling 3 × 29,000 = **87,000**. Against GUIDE §6's
   design target of 300–800K that is **7–19%** of a day (and **+2 calls
   on a day of roughly 10–28**, a 7–20% increase in call count).
   Against run day 2026-07-30's measured 17,441,543 it is **0.33%**;
   against run day 2026-07-31's 65,800,226, **0.09%**. The skip
   conditions mean quiet days cost zero, so the weekly average is below
   58K/day, not at it.
4. **It does not touch the expensive path.** The retry ladder is where
   both measured disasters happened. A live brief has no retry ladder:
   one call, one output, no per-item recovery, no isolation fallback.
   If the call fails it is simply not shown. This is deliberate — a
   surface with a retry ladder is a surface that can cost 39.7M tokens.
5. **It cannot become the record.** Everything it writes lands in the
   gitignored pipeline database and the gitignored `site/today.html` /
   `site/today.json` (`.gitignore:26-29`). Nothing enters `digests/`,
   `provenance/`, or the committed part of `site/`.

## §6 How significance would be decided

Only by a coded rule, versioned beside the selection rules, or not at
all. GUIDE §2 makes selection mechanical and party-blind, and §3's
justification for listing every recorded vote is the template: *a
discrete, dated, consequential act, selected by existence rather than by
importance*.

**Defensible today, from data already stored:**

| Proposed id | Coded condition | Already a rule |
|---|---|---|
| `LIVE-TRIG-01` | a `PLAW` package for the date is journaled | `PLAW-SEL-01` (all laws listed) |
| `LIVE-TRIG-02` | a `VOTES` item for the date is journaled | GUIDE §3, recorded votes |
| `LIVE-TRIG-03` | an `FR` item with `doc_type = PRESDOCU` is journaled | `FR-SEL-03` (all listed) |

Each is a `WHERE` clause over `item_journal`. None ranks, weighs, or
prefers a subject. Adding a class later cannot inflate cost, because
the trigger only pulls a scheduled brief forward.

**Not defensible today, and I will not pretend otherwise.** GUIDE §2
names "regulatory economic-significance designation" as a legitimate
mechanical criterion, and it is the one a reader would most expect here.
We do not store it. The govinfo `FR` material we extract carries the
agency `SUMMARY` preamble and document class; the Executive Order 12866
significance designation is a field of the **federalregister.gov API**,
listed in GUIDE §3 as a secondary source and not ingested. So
`LIVE-TRIG-04 (economically significant rule)` is **blocked on a source,
not on a rule** — it becomes available if and when that API is
ingested and the flag is stored per document, at which point it joins
the table above with no change to the trigger mechanics.

**Never triggers, and this should be written down before someone
proposes one:** subject-matter keyword lists ("immigration", "tariffs",
"AI"), agency prestige rankings, item volume as a proxy for importance,
outside news attention, and — most of all — a model asked which of
today's items matter. Any of those is subject-matter preference, which
§2 bans outright. If a coded rule cannot express it, it is not
significance; it is an opinion, and this project does not publish
opinions.

## §7 Governance: exactly what would have to change

This is a sixth model surface. Under GUIDE §3a that is a documented
change, not an implementation detail.

**GUIDE.md**

- **§3a Inventory** — the sentence "Five prompt surfaces exist" is an
  enumeration, so it is edited, not appended to: six surfaces, the new
  one being the live day-so-far prompt (`live._PROMPT`, versioned by
  `LIVE_PROMPT_VERSION`). Its contract belongs beside the plain-speak
  contract: input is stored summaries and mechanical counts only;
  present tense; a mandatory partial-day frame; a mandatory clause
  naming the classes that have not arrived; §2 restated in the prompt
  and enforced un-masked by the lexicon gate.
- **§5 Architecture / two-artifact model** — the paragraph describing
  `/today` as derived-only currently implies it carries no composed
  prose. It must state that `/today` may carry a labeled, preliminary,
  model-generated day-so-far note; that the note is **not** the Day in
  Review and never carries that name; that it is never committed, never
  enters a manifest, and has no permalink; and that the dated digest
  remains the record without qualification.
- **§6 Token economics** — a new rule in the shape of 13 and 14: the
  intraday layer is capped at a fixed number of calls per publication
  day, counted from the ledger, with named zero-cost skip conditions,
  and it has no retry ladder. The cap belongs in the constitution
  because the cap *is* the design.
- **§2** — no change of principle, but the labeling rule now binds a
  surface the report validator does not currently see (below).

**Code and config (none of it written here)**

- `src/fapd/live.py` — new module: prompt, version constant, one
  `run(conn, llm, date)`, no retries.
- `config.py` — `LIVE_PROMPT_VERSION`, `MAX_LIVE_BRIEFS_PER_DAY`,
  `LIVE_SLOTS_ET`, `LIVE_MIN_SUMMARIZED_ITEMS`, `LIVE_MODEL` (cheap
  tier: the input is already-compressed stored summaries, which is what
  §6 rule 6 reserves the strong tier's expense *against*).
- **Ledger purpose string** `live:day-so-far`, with `package_id`
  `LIVE-<date>`, so `insight.py`'s per-purpose table shows the layer
  separately from day one and any future cap can see it.
- **Storage:** a `live_summaries` table (date, prompt_version, model,
  slot, generated_at, through_observed_at, items_covered,
  items_observed, summary, tokens), append-only per generation so each
  rendered brief is reproducible and the history is auditable.
  `docs/schema.md` is the design authority and would be changed first.
- **The lexicon gate needs a seam.** `report._validate_lexicon` is
  digest-shaped (it takes the whole markdown, masks verbatim official
  summaries, and raises). The live path needs a small public scan over
  one string against the existing `_BANNED_RE`; a brief that trips it
  is discarded and not shown, matching the plain-line posture. Two
  independent layers, prompt-side and validator-side, exactly as §3a
  requires for plain-speak.
- **`collect.py` keeps its structural invariant.** The module contains
  no `compose_day` / `compose_sections` call and must continue not to —
  the staleness rule that motivated the ban still applies. A
  `LiveWorker` calling `live.run` is a different module with a
  different staleness model (time-slotted, never invalidated by new
  items) and does not weaken it. The docstring's claim should be
  narrowed to name compose specifically rather than model composition
  in general.
- **`RenderWorker` has a real bug waiting here.** It rebuilds only when
  the journal watermark moved. A brief written while no new item
  arrived would not be rendered until the next arrival. Its watermark
  must become the later of the journal watermark and the newest brief's
  `generated_at`.
- **`_TODAY_DISCLOSURE`** (`publish.py:1760`) says "The Day in Review
  and section synopses are composed at end of day and do not appear
  here." That sentence becomes false and must be rewritten in the same
  commit, distinguishing the preliminary note from the Day in Review
  that still does not appear.
- **`today.json`** gains a `day_so_far` object: `text`, `generated`,
  `through_observed_at`, `items_covered`, `items_observed`, `model`,
  `prompt_version`, `method: "llm"`, and `is_record: false` with a
  pointer to the dated digest. Agents must not be able to mistake it.

**Other documents**

- `docs/continuous-ingestion.md` §4 ("Compose: EOD-only, enforced
  structurally") and §8 ("No Day-in-Review, no section synopses") both
  become inaccurate as written and are amended in the same commit.
- `CLAUDE.md` §9 gains an entry: the live brief has no retry ladder and
  a per-day ledger-counted ceiling, both deliberate.
- `WORKLOG.md` entry stating the regeneration scope per §3a step 3 —
  which for this surface is *nothing*: briefs are ephemeral and are
  never regenerated, so a prompt iteration costs one call at the next
  slot.
- The public methods page and `llms.txt` need the same disclosure the
  page carries.

## §8 Failure modes

**A quiet day.** Recess weekends have shown 7 and 12 journaled items.
The skip conditions fire first and the day costs zero. This matters
more than it looks: a brief that says "little was published" costs
29,000 tokens to restate a line the mechanical board already renders
for free, which is a rule 2 violation dressed as prose.

**A flood day.** 2,678 items were journaled for 2026-07-28, of which
126 carried summaries. The call count does not move — two calls. The
prompt grows to roughly 126 × 400 characters and stays inside one call.
What must be handled is honesty, not cost: the brief covers 126 of
2,678 items and the coverage line has to say so in the reader's units
("composed from 126 summarized items of 2,678 observed so far"), or the
page implies a completeness it does not have. If the summarized set
ever outgrows one call, the correct response is to truncate the input
with disclosure — never to split into two calls, which doubles the
price for the same paragraph.

**A model outage.** No brief is written. The page shows the last brief
with its own "as of" stamp, or no brief block at all. The mechanical
board and the item stream are unaffected, because nothing in them
depends on a model. The `collector_state` error streak already surfaces
the outage on the health page. Nothing is fabricated and no retry
ladder exists to convert an outage into a token bill.

**The intraday text and the end-of-day Day in Review disagree.** This
is the hazard worth confronting directly, and the honest position is
that they *will* differ and that this is correct rather than a defect.
They describe different evidence: a partial day against a complete one;
before the dating rule re-dates late arrivals; before `AGENCYPR-EX-01`
excludes backfill; before the validation gates run; and with a
different summarized subset beneath them. A brief that agreed with the
digest by construction would be a brief that had waited until end of
day, which is the artifact we already have.

Four properties keep the disagreement from becoming an editorial
failure, and three of them already exist:

1. **They are never published side by side.** `EOD_ET_HOUR = 0` and
   `EODWorker.eod_due` target the publication day that just closed,
   while `build_today` always renders `publication_date()` — the
   current day. At 00:0x ET the live page has already rolled to D+1
   (empty) and the finalizer then publishes D. The brief for D is off
   the page before the digest for D exists.
2. **The brief has no permalink and no archive.** One URL,
   `/today.html`, always meaning the current day. There is no
   `/2026-07-31-live.html` for a reader to cite against the digest,
   and it appears in no feed, no `digests.json`, and no manifest.
3. **Naming is enforced.** It is a "day so far" note, never a "Day in
   Review". Two names for two artifacts, in the prose, in the HTML
   class, in `today.json`, and in the prompt.
4. **The brief never feeds the digest.** Composing the Day in Review
   from, or in awareness of, the intraday text would launder
   preliminary prose into the record and could anchor a completed day's
   synthesis on a partial one. `compose_day`'s inputs stay exactly what
   they are.

**Cache and copy.** An agent or a reader may retain the brief past
rollover. `is_record: false` plus the pointer to the dated digest is
the mitigation available on a static site; it is honest labeling, not
enforcement, and the memo should not claim more.

## §9 What I would not do

- **Fire on every analyze cycle, every render, or every N items.**
  `ANALYZE_MIN_INTERVAL_MIN = 15` permits up to 96 cycles a day; at
  29K each that is 2.8M input tokens, more than a whole design-target
  day, to refresh a paragraph most readers load once. This is the exact
  anti-pattern rules 9, 12 and 14 exist to prevent, and it is the
  design that feels most natural for a "live" page.
- **Give the brief a retry ladder.** One call, or nothing. Both
  measured token disasters were retries.
- **Extend the brief incrementally as items arrive** (a call per new
  item to append a sentence). Per-item calls re-pay the fixed overhead
  the batching exists to amortize.
- **Summarize the whole agency stream to feed the live page**
  (Option D, 551K–1.71M/day). If per-item plain lines for agency releases
  are wanted, that is a selection-rule proposal under §6 rule 4, costed
  and argued on its own.
- **Let the model choose what is significant, rank the day's items, or
  lead with what it finds notable.** §2, without exception.
- **Publish the brief anywhere durable** — Atom feed, `digests.json`,
  sitemap, manifests, or a committed file. It stays in the two
  gitignored artifacts.
- **Use the strong tier.** The input is already-compressed stored
  summaries; §6 rule 6 reserves the strong model for the final
  composition pass, and the fixed per-call cost dominates the tier
  choice on the CLI backend anyway.
- **Add a verification pass comparing the brief to the digest.** It
  would cost another 29K to measure a difference that is expected by
  design, and it invites editing the record to match a preliminary
  note.
- **Ship the model layer before the mechanical board.** If Option A
  turns out to satisfy the operator's question, the correct number of
  new model surfaces is zero, and that outcome should be reachable.

## §10 Open questions for the operator

1. **Two slots, or one?** 11:00 and 17:00 ET is 58,000 input tokens a
   day, 7–19% of the design-target day. A single 15:00 ET brief halves
   that and still covers the Federal Register issue and most of the
   agency flow, at the cost of leaving the morning uncovered. This is
   an editorial judgement about who reads the page and when, and it is
   the operator's, not mine.
2. **Is a sixth model surface the right answer at all, or is the
   mechanical board plus a better-organized stream enough?** The gap in
   §1 is real, but a large part of it — "what arrived, from whom, how
   much, how recently" — closes at zero tokens. The part only a model
   closes is turning official titles into ordinary words for the
   *unsummarized* majority, which Option B does not do either: it
   describes the summarized minority. It is worth deciding whether the
   brief is worth 58K/day given that limit, before §3a gains an entry
   that is difficult to remove.

Two further items, lower priority but noted while measuring:

3. `MAX_SINGLE_RETRIES_PER_RUN` is enforced per `analyze.run` call, and
   the collector may call it up to 96 times a day over two dates and
   two layers. Whether rule 14's ceiling was intended as per-run or
   per-day is a question for the operator; if per-day, it wants the
   ledger-counted treatment §7 proposes for the live layer.
4. `insight-2026-07-30.md` records two ledger rows with
   `duration_api_ms: 0` and `input_tokens: 0` on errors. If a failed
   call can bill without being recorded as billing, any ledger-counted
   ceiling — including this proposal's — undercounts. Worth confirming
   before a cap of any kind is enforced from the ledger.

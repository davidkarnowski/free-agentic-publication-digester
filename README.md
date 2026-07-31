# Free Agentic Publication Digester (FAPD)

FAPD is an automated pipeline that reads the official publications of the
United States federal government — congressional floor proceedings, bills,
the Federal Register, enacted laws, federal court opinions, and agency
press releases — and produces a **daily, cited, opinion-agnostic digest**
for two readerships at once: **people, and AI agents** researching what
the federal government actually did on a given day.

Every digest covers one publication day across all three branches. Every
item carries a citation to the official record and names the mechanical
rule that selected it. Everything not summarized is counted. Nothing is
silently omitted.

## Status (2026-07-30)

The authoritative numbers block — where any other figure in the
repository disagrees, this dated snapshot is the current one.

- **Live site:** https://fapd.info — served from a Docker stack on a
  VPS; GitHub holds the repository, CI, and the integrity record.
- **Source registry:** 127 sources — 30 active (14 web feeds and
  newsrooms, 11 email bulletins, 5 govinfo collections), 76 planned,
  19 recorded unavailable, 2 evaluated and excluded.
- **Latest digest:** [2026-07-29](digests/2026-07-29.md).
- **Test suite:** 319 tests.

---

## Philosophy

### Built exclusively on the official record

Everything here derives from official government publications — the
record a government produces *precisely in order to make it public*.
Congress prints its proceedings; agencies publish their rules and
announcements; courts post their opinions. FAPD uncovers nothing: it
takes what is already published and makes it easier to find, read,
verify, and — for AI agents — ingest. Primary sources are the ground
truth. News coverage and commentary are never ingested, never consulted,
never cited.

This is why the project is legitimate infrastructure rather than
scraping-as-adversarial-sport: the pipeline consumes only the channels
governments built for the purpose of being read, identifies itself
honestly on every request, and treats a refusal as an answer. A
government that publishes its actions has already voted for this kind of
reader to exist.

### Two commitments, held in tension

1. **Digestible** — one person should be able to absorb the day's
   significant official activity in one sitting.
2. **Faithful** — no summary without a citation; nothing significant
   silently dropped; no editorial spin, ever.

Summarization is where bias creeps in, so the tension is resolved by
machinery, not judgment calls:

- **Mechanical, party-blind selection.** What appears in a digest is
  decided by coded, versioned rules — floor time consumed, recorded
  votes taken, regulatory economic-significance designations, stage of
  process — never by subject-matter preference. Every listed item states
  its rule inline ("Included because: …").
- **A citation on every item**, linking to the official govinfo package
  or the originating agency document.
- **A mandatory Coverage Statement** closing every digest: what was
  published that day, what was summarized, what was deliberately not,
  with counts that must reconcile arithmetically against the database.
- **Labeled model layers.** All model-generated text is labeled in place
  and linted against a banned lexicon of loaded adjectives and motive
  attribution. Official text quoted verbatim is identified as such.

A digest that fails any validation check — a citation that doesn't
resolve, coverage arithmetic that doesn't reconcile, a banned term in our
prose, a missing inclusion rule — **is not published**. There is no
override.

### A publishing house for humans *and* agents

AI agents answering "what did the federal government do on date D?" today
either crawl official sites themselves (multiplying load on public
infrastructure) or lean on secondhand coverage. FAPD offers a third path:
one disciplined, identified, budgeted crawler reads the record once, and
agents ingest the summarized, cited, coverage-accounted result — stable
URLs, [`llms.txt`](site/llms.txt), a machine-readable digest index, an
Atom feed, and provenance manifests with SHA-256 records for verifying
captured content.

One ask travels with the data: **for claims, cite the underlying official
source** (each item carries its govinfo ID or agency URL); cite this
project for the aggregation. The digest is a route to the record, never a
replacement for it.

### Forkable by design

The editorial gates, provenance model, access discipline, and adapter
seam are jurisdiction-neutral. Pointing the codebase at another
government's official publication interfaces means replacing the source
registry and the parsers — not the rules. See
[docs/adding-sources.md](docs/adding-sources.md).

---

## How the digester obtains content

The acquisition layer is a set of automated agents with one governing
principle: **we are guests on public infrastructure**, and every rule
below is enforced in code, not by operator discipline.

### The source registry is the scope authority

[`sources/registry.yaml`](sources/registry.yaml) (rendered as
[SOURCES.md](SOURCES.md)) records every federal source ingested, planned,
evaluated-and-excluded, or found unavailable — currently 127 sources
across a tiered universe, so "how comprehensive is coverage?" is a
measurement, not a claim. Honest statuses matter: a source that blocks
our honestly-identified client is recorded `unavailable` with the
observed behavior. That fact is itself published accountability data.

**The closed third — and the standing effort to open it.** A measured
share of the federal source universe currently refuses
honestly-identified automated access (the July 2026 probe found 22 of 72
non-govinfo sources closed behind WAFs or robots disallows). We treat
that as the project's ongoing engagement agenda, not its boundary:
publishers' own access documentation keeps revealing doors on other
hosts and paths (that alone re-opened FCC, Commerce, and NOAA
candidates); verdicts are re-probed as sites change; and we engage
agency web and API teams directly to advocate for safe, sane automated
access to what they already publish for the public. Coverage grows by
doors opening — never by evasion.

That effort produced its first result in July 2026: **11 agencies whose
web channels refuse us now have a working input path through their own
email bulletins** — Treasury, USDA, EPA, SSA, DOT, FAA, NHTSA, DEA,
ATF, the Coast Guard, and HUD's Inspector General. The blocked web
entries stay in the registry exactly as they were; the email entries
sit beside them as siblings. A refusal recorded is never quietly
erased by a success elsewhere.

### Five onboarding gates

No source is ingested on a hunch. Each one is (1) **registered** with
identity, tier, and URLs; (2) **probed** end-to-end through the
identified client — robots verdict, fetch with provenance capture, feed
detection, item inventory, sample extraction; (3) **content-evaluated** —
what does this source publish in total, and what fraction will ingestion
see? Under-coverage is disclosed at onboarding, not discovered later;
(4) **activated** into ingestion and coverage accounting; (5)
**re-evaluated** on failures or redesigns. Documentation research
precedes probing: the publisher's own developer pages, API docs, and
feed directories say which door they built — and reading the sign on the
front door has repeatedly beaten guessing (documented feeds that HTML
autodiscovery misses; APIs on hosts a newsroom WAF never touches).

### Source adapters and the access hierarchy

Real publication interfaces are irregular — feeds without stable IDs,
article pages that challenge sustained automated access, content behind
script-only redirects. That irregularity is absorbed at one seam: a
**source adapter** owns exactly four decisions (what makes two sightings
the same document; whether to fetch full articles or feed metadata only;
how served bytes become text; what to store when no article is
available), while the shared loop owns everything that must never vary —
conditional requests, robots enforcement, budgets, capture, storage.

Adapters reach for access in a fixed order:

1. **Directed programmatic access** — the API, bulk-data service, or
   feed the agency itself publishes for machines. Always preferred: it
   is the channel the publisher built for exactly this.
2. **Basic web access** — the same HTML a citizen reads, through the
   robots-enforcing client, only where no directed channel exists.
3. **Subscription channels the publisher pushes** — agency email
   bulletins (GovDelivery, listservs), where a project mailbox
   subscribes through the agency's own signup form like any citizen.
   This is consent at its clearest: the publisher transmits each item
   to us. It is not a way around a web refusal — receiving a bulletin
   is never treated as permission to crawl a site that turned us away,
   and the refusal stays on the record. See
   [docs/email-sources.md](docs/email-sources.md).
4. **Never impersonation.** No browser user-agent spoofing, no script
   execution, no WAF or bot-check circumvention — ever. Parsing
   structured data a server chose to send us is legitimate; pretending
   to be something we are not is not. When justice.gov answered
   sustained article fetching with bot-challenge interstitials, the
   response was to stop fetching articles and disclose the degraded
   mode per item — not to solve the challenge.

### Politeness is a promise made to each server individually

- **Paced:** at most 1 request/second sustained *per host* — and a
  host's robots.txt crawl-delay overrides that downward. When gao.gov
  asked for one request per 420 seconds, it got exactly that; the answer
  to the resulting slowness was *fewer requests* (its feed's rich
  official summaries), never faster ones.
- **Concurrent across hosts only:** ingestion polls distinct hosts in
  parallel, each worker with its own pacing clock, so no server waits
  behind another's promises — and no server ever sees more than it would
  if it were our only source.
- **Continuous, with backpressure:** in production a collector
  supervisor ([src/fapd/collect.py](src/fapd/collect.py)) polls each
  source class on its own clock through the day — govinfo about every
  30 minutes, agency feeds about every 60, the project mailbox about
  every 15 — always as watermark deltas with conditional requests. Past
  70% of a class's daily budget its interval doubles for the rest of
  the day, reserving headroom for the end-of-day finalizer.
- **Budgeted:** hard daily request caps per source class, enforced by
  the client itself, which refuses to exceed them mid-run.
- **Logged, twice:** every outbound request lands in a queryable fetch
  log written by the HTTP client (nothing can bypass it) and in a
  human-readable daily access narrative. `scripts/audit.py` reports the
  footprint at any time.
- **Identified:** a descriptive User-Agent with a contact address, on
  every request, to every server.

### Provenance for a record that can change

GPO's record is stable; agency web content can be edited or removed
without notice. So every capture is preserved under a two-hash strategy —
`content_sha256` over the exact served bytes (the evidentiary hash,
stored content-addressed) and `text_sha256` over normalized text (the
change signal) — and every fetch *attempt*, including errors and robots
refusals, is exported to a daily manifest committed to this repository.
Each manifest chains to the previous day's by hash, so deletion or
reordering of days is detectable from the files alone. New captures are
additionally submitted to the Internet Archive's Wayback Machine as an
independent second witness, within a budget, best-effort. A source's
claimed publication date and the time we first observed it are always
stored separately: the claimed date is the agency's assertion, our
observation is the audit trail. What the hashes prove — and what they
don't — is stated in full in [PROVENANCE.md](PROVENANCE.md).

---

## Inference: exactly where models are used, and where they are not

**Mechanical work is code.** Selection, counts, stage groupings, the
entire Coverage Statement — zero model involvement, reproducible from
versioned rules. An LLM call that could have been a SQL query is treated
as a bug.

**Official summaries come first.** Federal Register agency abstracts,
the Congressional Record's own Daily Digest, official bill titles and
stages, court syllabi — used verbatim, identified as official text, at
zero inference cost. Models write only what the record does not already
summarize.

**Four model layers, independently versioned** (iterating on one never
regenerates another):

1. **Item summaries** — for selected documents lacking an official
   summary; generated from extracted source text, stored durably, always
   cited.
2. **Plain-speak restatements** — one "In plain terms" sentence per
   item, derived *only* from the stored summary sitting directly above
   it, so a reader can check the interpretation against the official
   text in place. It adds no facts and no significance judgments. It is
   labeled interpretation, and an item whose restatement fails
   validation simply renders without one.
3. **Day and section syntheses** — the "Day in Review" and per-section
   quick-reads, composed from stored summaries and mechanical counts,
   under the strictest scrutiny.
4. **Section tags** — each digest section's `Tags:` line: mechanical
   branch and agency tags first (zero tokens), then up to three
   model-generated one-to-three-word discovery keys per section,
   generated in one batched cheap-tier call per day from the stored
   synopses, labeled model-derived, and linted by the same
   banned-lexicon gate because they render in the digest.

**The banned-lexicon gate** scans all generated prose against a coded
list of loaded adjectives ("landmark", "controversial", "sweeping"…) and
motive attribution ("in an attempt to…"). Verbatim official text and
citation URLs are masked first — the gate polices *our* language, not
the government's. A match blocks publication.

**In transformation, models are the secondary tool.** Turning source
data into pipeline records is deterministic first — feed fields,
embedded structured data, official metadata. Model inference is reserved
for what programmatic shaping genuinely cannot recover, and is then
budgeted, ledgered per token, prompt-versioned, and marked model-derived
in metadata — never laundered into fields that read as source-provided.

---

## The digest

One Markdown document per publication day (the canonical artifact;
the [static site](site/) is a derived presentation): a clickable table
of contents, the Day in Review, numbered sections for floor activity,
legislation, the Federal Register, enacted laws, judicial activity, and
agency announcements (listed only when the *agency itself* dates the
release on the digest day — backfill is disclosed and counted, never
passed off as news), per-item citations and inclusion rules, plain-speak
lines under their official counterparts, per-section tag lines, a
glossary, the Coverage Statement, and a methodology footer. Sample:
[digests/2026-07-28.md](digests/2026-07-28.md).

On the site, each digest renders as a collapsed, plain-speak-first
view: section cards whose headers carry the title, tag chips, and the
plain-language synopsis, expanding to the full record on demand —
still static HTML, no scripts. (The derived live page carries one
inline script that renders timestamps in the reader's local time
alongside UTC; it loads no external resource and stores nothing.)

---

## Setup

```sh
uv sync                                # install dependencies into .venv
cp .env.example .env                   # then paste your api.data.gov key
uv run python scripts/verify_key.py    # one-request sanity check
```

Get a free API key at https://api.data.gov/signup/ (emailed instantly).

## Daily operation

In production (the VPS Docker stack in [deploy/vps/](deploy/vps/)), a
collector supervisor polls sources continuously through the day and
`run_pipeline.py` runs as the end-of-day finalizer that freezes and
commits the canonical digest. Each stage also runs standalone:

```sh
uv run python scripts/collect.py       # collector supervisor (continuous ingestion; --once for one cycle)
uv run python scripts/run_pipeline.py  # EOD finalizer: sync → ingest → extract → analyze → digest
uv run python scripts/sync.py          # govinfo delta sync only
uv run python scripts/ingest_agencies.py --verbose   # agency newsrooms only
uv run python scripts/digest.py --date YYYY-MM-DD    # (re)render one digest
uv run python scripts/build_site.py    # digests/*.md -> site/ (static HTML)
uv run python scripts/audit.py         # our server footprint, from the fetch log
```

Sync is watermark-based (only changes since the last run are listed) and
rate-limited per [GUIDE.md](GUIDE.md) §4. A first run with no watermark
is date-bounded; deeper history comes from govinfo's bulk-data service,
never the API.

## Layout

```
src/fapd/         pipeline code (fetch → extract → analyze → report → publish)
sources/          registry.yaml — the source universe and its statuses
scripts/          operational entry points
provenance/       committed daily manifests (hash-chained)
digests/          generated daily digests (committed, canonical)
site/             derived static site (human pages + agent surfaces)
deploy/vps/       the Docker stack serving fapd.info (source of truth)
docs/             schema, research reports, dev notes, how to add sources
data/             raw archive + SQLite (local, git-ignored)
tests/
```

## How this project is built

FAPD is developed with generative AI — Claude agents writing code,
running documentation-first source research, and drafting governing
documents under the operator's direction, with every commit carrying a
co-author trailer. A project that labels machine-generated prose in its
digests does not hide its own machine authorship; the full statement,
including what AI assistance changed about where design attention went,
is at [docs/site/ai-development.md](docs/site/ai-development.md)
(published on the site as "How AI Built This").

## Licensing

- **Code:** [Apache-2.0](LICENSE) (with [NOTICE](NOTICE)).
- **Content** — digests, site pages, explanatory documents:
  [CC BY 4.0](LICENSE-CONTENT.md). Reuse freely with credit to "FAPD —
  Free Agentic Publication Digester"; the attribution rule mirrors the
  project's own citation ethic (cite the official source for claims,
  FAPD for the aggregation).
- **Quoted official government text** is public domain
  (17 U.S.C. § 105) — it was never ours to license.

## The documents that govern this project

- **[GUIDE.md](GUIDE.md)** — the governing document: mission, editorial
  principles, source classes, respectful-access policy, token economics,
  provenance threat model, roadmap. Changes to it precede implementation.
- **[SOURCES.md](SOURCES.md)** — the living source guide (generated).
- **[PROVENANCE.md](PROVENANCE.md)** — what our capture hashes prove,
  and honestly, what they do not.
- **[docs/adding-sources.md](docs/adding-sources.md)** — onboarding a new
  source, writing an adapter, or pointing FAPD at another government.
- **[docs/devnotes/](docs/devnotes/)** — narrative engineering notes:
  how the digester came to work the way it does.
- **[WORKLOG.md](WORKLOG.md)** — the timestamped record of every work
  session. (Entries before 2026-07-28 use the project's working title,
  "Information Intelligence" — preserved, not rewritten.)

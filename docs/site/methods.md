# Methods

How the Free Agentic Publication Digester (FAPD) makes each digest, in
pipeline order: where documents come from
(Sourcing), how they are fetched and preserved (Ingestion), exactly where
language models are and are not used (Inference), and how a digest is
assembled and validated before it is published (Publication). Each
section stands alone; agents may ingest them independently.

## Sourcing

**The registry is the scope authority.** Every source ingested, planned,
evaluated, or found unavailable is recorded in a versioned registry —
currently 127 sources — and coverage of the federal source universe is
measured there, never assumed. Sources are tiered so comprehensiveness
can be stated against a defined universe: Tier 1 (cabinet departments,
top independent agencies, legislative support agencies, the White House
briefing room, core govinfo collections), Tier 2 (major sub-agency
newsrooms and regulator clusters whose output does not flow through a
parent department), Tier 3 (the long tail, added opportunistically). The
registry currently spans all three tiers. Statuses are honest: alongside
`active` and `planned`, a source that blocks our honestly-identified
client is recorded `unavailable` with the observed behavior — that fact
is itself accountability data, and such a source is never evaded or
retried into submission. It is also not abandoned: every `unavailable`
verdict feeds a standing engagement effort — searching the publisher's
own access documentation for doors on other hosts or paths (which alone
has re-opened several sources), re-probing as sites change, and direct
outreach to agency web and API teams advocating for machine-readable
channels. The published [source guide](sources.html) renders the full
registry, closed doors included.

**Five onboarding gates.** Adding a source is an evaluation, not a URL
paste: (1) *Registered* — identity, tier, URLs, status `planned`, so the
gap is visible; (2) *Probed* — a script exercises the whole ingestion
chain through our identified client (robots verdict, fetch with
provenance capture, format detection, item inventory, one sample article
extracted) and stores structured findings; (3) *Content-evaluated* — the
probe findings must answer, in the registry entry, what the source
publishes in total and what fraction ingestion will see, so
under-coverage is disclosed at onboarding rather than discovered later;
(4) *Active* — wired into ingestion and Coverage Statement accounting;
(5) *Re-evaluated* — persistent failures or redesigns drop the source
back to `unavailable` or re-probe. No source is activated before its
probe passes.

**Source adapters and the access hierarchy.** Real publication
interfaces are irregular — feeds without GUIDs, article pages that
refuse identified clients, content embedded in static JSON. That
irregularity is absorbed at one seam: a source adapter owns exactly four
decisions (what makes two sightings the same document; whether to fetch
full articles or feed metadata only; how served bytes become text; what
to store when no article text is available), while a shared loop owns
everything else — conditional requests, robots enforcement, budgets,
capture, provenance, storage. Adapters reach for access methods in a
fixed order and record which rung they stand on:

1. **Directed programmatic access** — the API, bulk data, RSS/Atom feed,
   or sitemap the agency itself publishes for machines: the channel the
   publisher built for the purpose, and always preferred.
2. **Basic web access** — plain fetches of the same HTML pages a citizen
   reads, through the robots-enforcing client, only where no directed
   channel exists.
3. **Subscription channels** — agency email bulletins (GovDelivery
   accounts, listservs), where a single identified project mailbox
   subscribes through the agency's own signup form. This is the
   consent-maximal channel: the publisher sends each item to us. What
   arrives is ingested; what it links to on a site that refuses our
   client is not fetched. Where a web source is blocked and an email
   subscription exists, both are registered — the email entry as a
   sibling, the refusal left standing on the record.
4. **Never** browser impersonation, script execution, or any access the
   source refuses to identified clients. Parsing structured data a
   server sent us (for example, JSON-LD embedded in a page) is
   legitimate; pretending to be a browser is not.

## Ingestion

**govinfo delta sync with watermarks.** The primary source is the U.S.
Government Publishing Office's govinfo system, polled per collection
with a "what changed since timestamp X" query — under continuous
operation, repeated through the day at roughly 30-minute intervals
rather than once. The watermark
is always a server-side last-modified value, never our clock, and it
advances only after a listing completes — a failed sync re-lists the
same window. A first sync with no watermark is date-bounded to a 3-day
lookback; older history is only ever acquired as a deliberate bulk-data
backfill, never an open-ended crawl. Requests are paced at 1 per second
with a 2,000-per-day cap (roughly 1% of what govinfo permits), unchanged
content is never re-downloaded, and server signals (Retry-After, rate
headers, 5xx backoff) are honored exactly.

**Agency polling.** Agency newsrooms and report publishers are polled
through their feeds with conditional requests (ETag / If-Modified-Since)
under their own daily budget, so agency crawling can never consume the
govinfo budget or vice versa. Under continuous operation the feed poll
runs about hourly, and the project mailbox for email-distributed sources
is checked about every 15 minutes — a poll that touches no government
server at all.

**Continuous collection, end-of-day finalization.** A single collector
supervisor runs the polls above on per-source-class clocks through the
day, journaling arrivals with observation timestamps. The binding
politeness invariants do not loosen with frequency: at most one request
per second per host (a robots.txt crawl-delay overrides that downward),
per-class daily budgets enforced by the client, every request logged,
identified User-Agent. Past 70% of a class's daily budget the collector
doubles its polling interval for the rest of the day, reserving
headroom for the end-of-day finalizer — the run that assembles,
validates, and freezes the canonical dated digest.

**Capture-everything provenance.** Unlike the GPO record, agency web
content can be edited or removed without notice, so every capture is
preserved under a two-hash strategy:

- `content_sha256` — the SHA-256 of the exact decoded response bytes,
  stored content-addressed. This is the evidentiary hash: anyone holding
  the bytes can recompute it against the committed record.
- `text_sha256` — the SHA-256 of the normalized extracted text, tagged
  with the normalizer version. This drives change detection, because raw
  web pages churn with tokens and rotating asset URLs while the words
  stay the same.

Both are recorded, so "the bytes changed" and "the words changed" are
separately supportable. Every fetch *attempt* — including 304s, robots
refusals, and errors — is exported into a daily manifest committed to
the repository, and each manifest's header carries the SHA-256 of the
previous day's manifest, forming a chain from which deletion or
reordering of days is detectable. Where enabled, each new capture also
triggers a Wayback Machine snapshot as an independent second witness. A
source's claimed publication date and the time we first observed the
document are always stored separately, never conflated.

**What the hashes prove — and don't.** A hash proves what was served to
our identified client, from our network position, at that time — not
what every visitor saw. Our timestamps are ordered by git history and
corroborated by Wayback snapshots, not third-party notarized. We can
prove when we first saw a document; we cannot independently prove when
it was actually published. These limits are stated in full, with
verification instructions, in the repository's `PROVENANCE.md`.

## Inference

Exactly where language models are used, and where they are not.

**Mechanical work is code, not models.** Selection of what appears in a
digest, all counts and stage groupings, and the entire Coverage
Statement are computed mechanically — zero model involvement. No model
ever sees an item that has not already passed a party-blind selection
rule, and the rules are versioned in the open repository, so "why did
this item make the digest?" always has a reproducible answer.

**Official summaries come first.** Federal Register agency abstracts,
the Congressional Record's own Daily Digest, and official bill titles
and stage designations are the first drafting inputs, used verbatim and
identified as official text. Model-written summaries exist only for
selected items that lack an official summary.

**Four model layers, independently versioned.** Where models are used,
each layer carries its own prompt version so iterating on one never
regenerates the artifacts of another:

1. **Item summaries** — for selected documents without an official
   summary, generated from extracted source text, stored durably keyed
   by document ID and content version, always cited.
2. **Plain-language restatements** — one "In plain terms" sentence per
   item, derived only from the item's stored summary (never raw text or
   outside knowledge, so a reader can check it against the adjacent
   official text in place); it adds no facts and no significance
   judgments, and an item whose restatement fails the lexicon gate
   simply renders without one.
3. **Day and section syntheses** — the Day in Review and per-section
   quick-reads, composed from stored summaries and mechanical counts,
   and subjected to the strictest lexicon scrutiny.
4. **Section tags** — each section's `Tags:` line leads with mechanical
   tags (branch, agency — derived from the collection and registry
   metadata at zero model involvement), followed by up to three
   model-generated one-to-three-word discovery keys describing the
   section's content for search and agent retrieval, produced in one
   batched call per digest day from the stored synopses. Tags are
   navigational metadata, never judgments; model keys are labeled as
   such, and a section whose keys fail validation renders with
   mechanical tags only.

**The banned-lexicon gate.** Generated prose is scanned against a coded
banned lexicon (currently 16 terms and phrases: loaded adjectives such
as "landmark" and "controversial", motive attribution such as "in an
attempt to", and evaluative plain-register framing). Verbatim official
text is masked before scanning — the gate polices our prose, not the
government's. A match blocks publication; the gate is never loosened to
accommodate a prompt change.

**Models are the secondary tool everywhere else.** Turning source data
into pipeline records is deterministic first — feed fields, embedded
structured data, official metadata — with model inference reserved for
cases programmatic shaping genuinely cannot handle, and then budgeted,
logged to a token ledger, prompt-versioned, and marked model-derived in
metadata, never laundered into fields that read as source-provided.
Everything model-derived in a digest is labeled in place.

## Publication

**Digest anatomy.** Each digest is one Markdown document with a fixed
skeleton: a metadata header (digest date, data date range, pipeline
version, per-collection sync watermarks); a table of contents; the Day
in Review; numbered sections 1–6 (Congressional Floor Activity;
Legislation; Federal Register; Enacted Laws; Judicial Activity; Agency
Announcements, which appears as active agency sources contribute); an
italicized quick-read and a `Tags:` line at the top of major sections;
a Terms Used Today glossary; the Coverage Statement; and a Methodology
footer restating the selection and labeling rules. Every item carries
its citation and an "Included because" line naming the mechanical rule
that selected it.

**Canonical Markdown, derived HTML.** The Markdown digest in the
repository is the canonical artifact. The HTML site — including this
page — is a derived, zero-model presentation layer, regenerable at any
time without touching data or models. On the site, each digest renders
as a collapsed, plain-speak-first view: section cards whose headers
carry the title, tag chips, and the plain-language synopsis, expanding
to the full record on demand — static HTML with no JavaScript.

**The validation gate.** Before publication, each digest must pass four
coded checks: every govinfo citation resolves to a stored record; the
Coverage Statement's arithmetic reconciles internally and against the
database; generated prose clears the banned-lexicon scan (with verbatim
official text masked); and every rendered item states its inclusion
rule. A digest that fails any check is not published — there is no
override.

# Free Agentic Publication Digester (FAPD) — Project Guide

> The governing document for this project. All design, code, and editorial
> decisions should be checkable against this guide. When we change direction,
> we change this document first and record why in `WORKLOG.md`.

---

## 1. Mission

*Naming: built under the working title "Information Intelligence";
renamed **Free Agentic Publication Digester (FAPD)** on 2026-07-28 —
older worklog entries use the working name.*

Build an automated pipeline that monitors official United States government
publications — congressional transcripts, bills, the Federal Register, and
related primary sources — and produces a **daily digest** that a single person
can ingest with reasonable effort, while preserving a path back to the full,
unadulterated source record for every claim made.

**Why this is legitimate infrastructure:** this project exists to give
citizens ease of access to their government's actions, and it is built
*exclusively* on official government publications — the record a
government produces precisely in order to make it public. We do not
uncover anything; we make what is already published easier to find, read,
verify, and (for AI agents) ingest. The same design generalizes: the
pipeline's source registry, adapters, and editorial gates are intended to
be pointable at *any* government's official publication interfaces by
anyone who forks this codebase for their own jurisdiction.

**Opening the closed sources is standing work (added 2026-07-29).** A
substantial share of federal publication channels is currently closed to
honestly-identified automated clients — WAFs, robots disallows, bot
challenges (the 2026-07-26 probe measured 22 of 72 non-govinfo sources
closed). We treat that not as a final state but as the project's ongoing
engagement agenda: keep reading each publisher's own access
documentation for doors we missed; re-probe on documented channels as
sites change; and engage agency web and API teams directly through their
published contact routes to advocate for safe, sane automated access to
what they already publish for the public. The registry's `unavailable`
records are simultaneously accountability data and the outreach
worklist. Coverage is expected to grow continuously after launch — by
agencies opening doors, never by us picking locks.

Two goals in tension, both mandatory:

1. **Digestible** — summarized and aggregated so the day's most significant
   official activity fits in one sitting.
2. **Faithful** — nothing summarized without a citation to the primary source;
   nothing significant silently dropped; no editorial spin introduced.

### Dual audience: humans and AI agents (amended 2026-07-28)

This project is a publishing house for **two readerships**: people, and AI
agents researching federal government actions. An agent that needs "what
did the government do on date D" should be able to ingest our digest —
summarized, cited, coverage-accounted — instead of crawling a dozen
official sites itself. That substitution is a feature we actively
advertise, and it is respectful infrastructure twice over: agents get
clean structured access, and government servers get one polite,
disciplined crawler (ours) instead of many.

Standing commitments for agentic access:

- **Explicit invitation.** Public-facing documentation states plainly that
  this data is built for agent ingestion; the site's robots.txt allows
  automated access, and an `llms.txt` guide plus a dedicated access page
  tell agents what exists, where, and how to use it.
- **Clean, stable, machine-first surfaces:** canonical Markdown in the
  repository; static no-JS/no-auth HTML with stable URL patterns
  (`/<YYYY-MM-DD>.html`); a machine-readable digest index
  (`digests.json`); an Atom feed for change discovery; the source guide
  and provenance manifests published alongside.
- **Honesty travels with the data.** Every surface an agent ingests
  carries the same disclosures humans get: citations to the official
  record, inclusion rules, coverage statements, which text is verbatim
  official vs. model-generated, and the §7 provenance trail for
  verification.
- **Guided onward citation.** We ask agents to cite the underlying
  official sources (the govinfo IDs we carry) for claims, and us for the
  aggregation — the digest is a route to the record, never a replacement
  for it.
- **Reciprocity.** We ask of visiting agents exactly the courtesy our own
  crawler practices (§4): honest identification and conditional requests.
  The site is static and cheap to serve precisely so heavy agent traffic
  is harmless.

## 2. Editorial Principles (non-negotiable)

These exist because summarization is where bias creeps in. Every analysis or
reporting component must comply.

- **Primary sources only.** We ingest official government publications, not
  news coverage, not commentary. The source record *is* the product's ground
  truth.
- **Opinion-agnostic output.** Summaries describe what was published, said, or
  enacted — never whether it was good or bad. Banned in generated prose:
  loaded adjectives ("controversial", "landmark", "extreme"), motive
  attribution ("in an attempt to..."), and predictions of political outcomes.
  The canonical banned-term list is `config.BANNED_TERMS`: every prompt
  restates it from that constant and the render-time lexicon gate compiles
  its scan from it — two independent layers that cannot drift.
  - *Scope (amended 2026-08-02, operator).* The ban binds the digest's OWN
    voice only. Official source text — titles, official summaries, captions,
    quoted action sentences — renders verbatim and is never gated, altered,
    or suppressed on lexicon grounds. The rule exists to keep what we write
    unbiased, never to censor what the government published.
  - *Official-name exemption (same amendment).* Generated prose may contain
    a banned term only where it occurs inside an exact occurrence of an
    official title or name stored in the corpus for that digest day — a
    statute name ("National Historic Preservation Act"), a case caption
    ("Landmark Legal Foundation v. EPA"), a document title. Naming the
    record is stating a fact. The same term outside such a span remains a
    violation, and the exemption is positional: it never blinds the gate to
    the surrounding prose.
- **Coverage symmetry.** Selection criteria for "what matters today" must be
  mechanical and party-blind: e.g., floor time consumed, number of cosponsors,
  regulatory economic-significance designation, stage of legislative process —
  never subject-matter preference.
- **Cite everything.** Every summarized item links to its govinfo package ID /
  permanent URL. A reader must always be able to check our summary against the
  original in one click.
- **Completeness accounting.** Each digest ends with a coverage statement:
  what was published that day, what we summarized, and what we deliberately
  did not (with counts). Silent omission is the failure mode we most guard
  against.
- **Digest sections are append-only in numbering (added 2026-07-31).** A new
  section is added at the end of the substantive sections, before the
  Glossary — never inserted, because section numbers are anchors and a
  reader who cited `#3-federal-register` in a published digest must not find
  a different subject there tomorrow. Reading order therefore reflects the
  order sections were added, not a hierarchy of importance; nothing in the
  digest ranks its own contents. **Recorded Votes** is the first section
  added under this rule; **Bill Actions** (§8, added the same day) is the
  second.
- **Separate the layers.** Raw data → extracted facts → summaries are stored
  as distinct artifacts. The summary layer can be regenerated or audited
  without re-fetching anything.
- **Method transparency.** Prompts, selection rules, and ranking heuristics
  live in this repo, versioned. If someone asks "why did this item make the
  digest?", the answer must be reproducible.
- **Agency statements are attributed speech, never established fact.**
  Press releases and newsroom content are primary sources for what an
  agency *said* — official advocacy, not neutral record. All digest prose
  derived from them must attribute ("the Department stated…", "according
  to the release…") and must never repackage an agency's claims as
  facts the digest itself asserts. Titles quoted verbatim are quoted, not
  endorsed.
- **Plain-language renderings are labeled interpretation.** A digest may
  carry a model-generated "In plain terms" line per item to make official
  register parseable. Constraints: it is derived ONLY from the item's
  stored summary (never from raw text or outside knowledge, so the reader
  can check it against the adjacent official text in place); it adds no
  facts and no significance judgments; it is always visually distinct and
  labeled as our rendering; it is linted un-masked by the banned-lexicon
  gate; an item whose plain rendering fails simply renders without one —
  plain language is a presentation aid, never a substitute for the cited
  summary.
- **Machine-transcribed and machine-described media are derived text, never
  the record (added 2026-08-05).** Audio, video, and images an agency
  publishes are official publications; a machine's transcription or
  description of them is not. Where the publisher supplies an official
  transcript or a caption file, that text *is* the record and is treated
  like any other official text. Where it does not, speech-to-text and
  vision output may enter the corpus to drive selection and summarization,
  under three constraints: it is stored in fields that mark it derived and
  never in fields that read as source-provided (§3, transformation
  ownership); it is never quoted as what the government said, and no digest
  prose may attribute its wording to the agency; and it always renders with
  the producing model and prompt version beside it, like every other model
  surface (§3a). An item whose only text is machine-derived is disclosed as
  such in the coverage accounting. The reader must never have to work out
  whether they are reading the record or a machine's rendering of it.

## 3. Data Sources

### Primary: govinfo (GPO)

- **govinfo API** — `https://api.govinfo.gov` — content and metadata for
  publications from all three branches, in self-describing "packages."
  - Requires a free API key from **api.data.gov** (stored in `.env`, never
    committed).
  - Default rate limits: 36,000 req/hour, 1,200 req/minute, 40 req/second.
    (We will operate far below these — see §4.)
  - Key services:
    - `collections` — list packages by collection code **and last-modified
      date**. This is our change-detection mechanism: poll "what changed since
      timestamp X" instead of re-scanning.
    - `published` — packages by official issue date.
    - `packages` / `granules` — package summaries and sub-documents (e.g.,
      individual Congressional Record sections), with formats: XML, PDF, HTML
      (htm), MODS, PREMIS, ZIP.
    - `search` — POST search service (use sparingly; discovery via
      `collections` is cheaper and deterministic).
  - Pagination: `offsetMark` (start with `*`) + `pageSize` (max 1,000).
  - Quirk: ZIP/MODS may return **503 + Retry-After** while generated
    on-demand; honor the header exactly.
- **govinfo Bulk Data** — `https://www.govinfo.gov/bulkdata` — direct XML for
  BILLS (113th Congress forward), Federal Register, CFR/eCFR, Congressional
  Record, and bill status. Append `/xml` or `/json` to a bulkdata URL for a
  machine-readable directory listing; set proper `Accept` headers or expect
  406. Prefer bulk data over the API for large backfills.
  Docs: `github.com/usgpo/api`, `github.com/usgpo/bulk-data`.

**Amended 2026-08-06 — observation-day filing (operator).** A govinfo
package is filed under the Eastern publication day of its FIRST
OBSERVATION by our collector
(`sync.publication_date_of(first_seen_at)`), written once and never
re-derived — a later revision re-fetch never re-files a document.
FAPD's three clocks, in disclosure order: *Date of Action* (as
described in the text — proceedings date, opinion issue date; may be
unavailable), *Date of Publication* (publisher metadata; may be
unavailable), *Date of Observation* (ours — the only timestamp defined
precisely from our own worker metadata, and the source of truth for
filing and sequencing). Why observation and not publisher metadata: a
source outage under metadata filing files a document into a day whose
digest is already frozen — dropped from the record; under observation
filing nothing observed can ever miss its digest. Per-collection
policy: CREC, BILLS, USCOURTS, PLAW file by observation day; FR files
by its cover date (the FR is legally published on its cover date, and
govinfo posts it early — the 2026-08-03 issue was observed
2026-08-01); AGENCYPR keeps the §3 agency dating rule unchanged
(filing agency feeds by observation is the 721-item backfill failure
of 2026-07-31). Every observation-filed item or section states the
document's own date, and the publisher stamp where available, beside
the digest day. Cutover: filing changed with digest 2026-08-06; rows
first seen earlier keep cover-date filing so every frozen digest
re-renders identically (§5 reproducibility). The two Record issues
observed 2026-08-04/05 (proceedings of 08-03/08-04) predate the
cutover and appear in no digest — their summaries remain in the corpus
and day views; disclosed, not backfilled.

### Collections of interest (initial scope)

| Code | Collection | Why |
|------|-----------|-----|
| `CREC` | Congressional Record (daily) | Floor proceedings & debate — the core transcript source |
| `BILLS` | Congressional Bills | Text of introduced/engrossed/enrolled legislation |
| `FR` | Federal Register | Rules, proposed rules, notices, presidential documents |
| `PLAW` | Public and Private Laws | What actually became law |
| `CHRG` | Congressional Hearings | Committee transcripts (published with lag) |
| `CRPT` | Congressional Reports | Committee analysis accompanying bills |
| `DCPD` | Daily Compilation of Presidential Documents | Executive statements, orders, remarks |
| `USCOURTS` | United States Courts Opinions | Judicial branch: opinions from participating federal courts |

Start with `CREC`, `BILLS`, `FR`; add the rest once the pipeline is stable.

*(Status note, 2026-08-02: this table is the adoption plan, not the
running inventory. Synced today: `CREC`, `BILLS`, `FR`, `USCOURTS`,
`PLAW` (`config.COLLECTIONS`), plus the two later collections defined
below this table — `VOTES` and `BILLACTIONS`. `CHRG`, `CRPT`, and
`DCPD` remain unstarted. The code constant is the inventory; this
table records why each collection is in scope.)*

### Recorded votes (added 2026-07-31)

| Code | Collection | Why |
|------|-----------|-----|
| `VOTES` | Senate and House roll-call votes | What each chamber actually decided, and how each member voted |

Roll-call votes are published by the chambers themselves as structured
XML — the Senate's vote menu and per-vote records, the House Clerk's
roll-call index — not through govinfo, so they arrive through the agency
poll loop with an `xml-index` adapter rather than a collection sync. They
are nonetheless **legislative record, not agency communication**, and are
stored under their own collection code so they never enter the
`AGENCYPR` accounting, the agency dating rule, or the executive-branch
tagging that class carries.

Why they are in scope at all: the Congressional Record carries floor
*proceedings* and BILLS carries the *text*, but neither states the
outcome in a form a reader can count. A recorded vote is a discrete,
dated, consequential act — exactly the shape mechanical selection can
include without judgement. Selection is by existence, not by importance:
every recorded vote of the day is listed, in vote-number order, with no
rule that could prefer one question over another.

**An index is not a feed.** A chamber's vote index lists an entire
session. Ingestion is bounded to a lookback window
(`config.INDEX_LOOKBACK_DAYS`); older votes are outside the window, not
excluded by judgement, and the §3 dating rule governs what a given digest
day lists exactly as it does for every other source.

### Bill actions (added 2026-07-31)

| Code | Collection | Why |
|------|-----------|-----|
| `BILLACTIONS` | Bill actions from the Library of Congress's bill-status record | What a chamber actually did with a bill on a given day — referred, reported, agreed to, rejected |

`BILLS` carries the *text* of legislation as printed and `CREC` carries
the floor *proceedings*; neither states, in a form a reader can count,
what happened to a particular bill on a particular day. The Library of
Congress publishes exactly that through the Congress.gov API: one dated,
plain-language action per bill (*"Committee on Finance. Ordered to be
reported"*, *"Motion to proceed to consideration of measure rejected in
Senate"*). It is a discrete, dated, consequential act — the shape
mechanical selection can include without judgement. **Selection is by
existence, not by importance:** every bill action inside the window is
listed, in bill-designation order, with no rule that could prefer one
measure over another. The API is reached with the same api.data.gov key
the govinfo client already holds, and the key rides in request
*parameters* so §4's redaction keeps it out of the fetch log.

**These items are dated by the publisher, not by observation.** The
record dates each action by the day the chamber took it (`actionDate`)
and publishes it the *following* morning: measured 2026-07-31, of the
250 most recently updated bill records, 97 carried an action dated
07-30 and **none** carried an action dated 07-31, and the bulk of a
day's actions entered the API between 08:00 and 12:00 UTC the next day.
Bill actions are therefore dated exactly as `CREC`, `FR` and `PLAW` are
dated — by the publisher's own date, so a digest for day D lists the
actions the record says happened on D — and *not* by the agency-newsroom
dating rule above, which exists for a source class that publishes
same-day. The lag is a standing disclosure in the section and under
Known gaps, like the judicial publication lag it resembles.

**An index is not a feed** applies here as it does to votes: the bill
endpoint enumerates the entire corpus (429,331 records on 2026-07-31)
in update-date order. Ingestion reads one page of the most recently
updated records per poll and bounds itself to
`config.INDEX_LOOKBACK_DAYS` by action date; anything older is outside
the window, not excluded by judgement.

### Judicial branch coverage (amended 2026-07-25)

The digest covers all three branches. Judicial coverage is phased:

- **J1 (active):** the govinfo `USCOURTS` collection — opinions from ~140
  participating appellate, district, bankruptcy, and national courts.
  **Structural completeness disclosure (mandatory, standing):** unlike CREC
  and FR, which are the complete official record of their branches,
  USCOURTS is participation-based and is *not* the complete federal
  judicial record. Every digest's judicial section and Coverage Statement
  must carry this disclosure. Mechanical selection leans on the courts' own
  published/precedential designations and court type (appellate summarized;
  district/bankruptcy counted).
- **J2 (planned):** Supreme Court slip opinions and order lists directly
  from supremecourt.gov — our first non-govinfo primary source, admitted
  deliberately because SCOTUS does not publish via USCOURTS; the official
  syllabus serves as the zero-token drafting input (§6 rule 3).
- **J3 (deferred):** docket/filing activity (PACER/RECAP/CourtListener) —
  partial by nature and outside the official-publication model; revisit
  only with a deliberate GUIDE change.
- **Date semantics:** court packages are case-shaped, not day-shaped; a
  digest's judicial items are opinions *filed* on the digest date, and
  publication lag (courts post with delay) is disclosed under Known gaps.

### Agency newsrooms (amended 2026-07-26)

A second non-GPO source class: official agency press releases, statements,
and announcements published on agency websites (RSS feeds preferred;
direct HTML index pages where no feed exists). Governing rules:

- **The registry is the scope authority.** `sources/registry.yaml` (and
  its generated `SOURCES.md`) records every source ingested, planned,
  evaluated-excluded, or unavailable — coverage of the federal source
  universe is measured there, never assumed.
- **Viability is checked, not presumed, and never forced.** A source
  becomes `active` only after a passing robots.txt + feed check through
  our identified client. **No WAF evasion ever** — no browser user-agent
  spoofing, no header games. A site that blocks honestly-identified
  automated access is recorded `unavailable` with the observed behavior:
  that fact is itself accountability data.
- **Continued engagement (added 2026-07-29).** An `unavailable` verdict
  is a snapshot, not a sentence. For each closed source, the standing
  playbook is: (1) search the publisher's own access documentation for a
  door on another host or path (this alone re-opened FCC, Commerce, and
  NOAA candidates); (2) re-probe when documentation, site redesigns, or
  time suggest the verdict may be stale; (3) engage the agency directly
  — webmaster/developer contacts, API feedback addresses, GovDelivery
  teams — to request or encourage a machine-readable channel, always as
  an identified project with a stated public-interest purpose. Outcomes,
  including refusals, are recorded in the registry notes. §1's rule
  governs throughout: coverage grows by doors opening, never by evasion.
- **Mutable-source disclosure.** Unlike the GPO record, agency web content
  can be edited or removed without notice. Digest sections built on this
  class carry a standing disclosure, and §7 (Provenance) governs how
  captures are preserved and how changes are detected and disclosed.
- **The federal publication day (amended 2026-07-30).** A publication
  day runs **midnight to midnight Eastern time in Washington, D.C.**
  (`America/New_York`, DST handled by the zone), because that is the
  clock the publishers keep: the Federal Register's morning release,
  floor proceedings, opinion postings, agency announcements. This is
  the boundary for every digest date, for the live `/today` view, and
  for the end-of-day finalizer's target.

  The rule replaces dating by UTC day, which was wrong in a specific and
  visible way: midnight UTC is 8 p.m. Eastern, so an agency release
  issued at 8:30 p.m. Eastern was filed under the *following*
  publication day — a day the government had not yet begun — and the
  live view rolled over while Washington was still working.

  **Observation timestamps remain UTC** and are stored, rendered
  (`<time datetime>`), and served in machine surfaces as UTC: what is
  Eastern is the *day a document belongs to*, never the record of when
  we saw it. govinfo material is unaffected — its `dateIssued` is the
  publisher's own, already Eastern-based; the change binds the sources
  we date ourselves (agency web and email releases).

  **Applied forward only.** Items already dated under the UTC rule are
  not re-dated: the published record is never rewritten to match a later
  policy (§7). The transition date is named in the worklog and on the
  public methods page, so a reader comparing an old digest to a new one
  can see why a boundary moved.
- **Dating rule (added 2026-07-28; boundary amended 2026-07-30).** A
  digest for day D lists only releases the agency itself dates on D
  (claimed publication date, resolved to a federal publication day). Items *first observed* on D but claimed earlier — feed
  backfill, newly activated sources, bootstrap sweeps — are **not**
  today's news and are excluded from the listing under `AGENCYPR-EX-01`,
  but they are never silent: the coverage accounting names their count,
  and their captures/documents are stored normally. An item carrying no
  parseable claimed date falls back to the observed date (listed on the
  publication day we first saw it, disclosed as dated by observation —
  the only honest option **for a feed**, whose publisher bounds it to
  what was just published). **Amended 2026-08-02, ratifying the
  behavior shipped with the index adapters on 2026-07-31:** for an
  **index or listing page** — which carries months of undated archive,
  not just what is new — the same fallback would file dozens of old
  releases as today's news in a way `AGENCYPR-EX-01` cannot catch
  (their claimed day would equal the digest day). An undated index
  entry is therefore **dropped, never observation-dated**, and the
  adapter logs the drop count on every poll; a source that mostly
  drops is a source that should not be active. Claimed dates and
  observed dates remain separately
  stored, always (§7 T3/T4: a claimed date is the agency's assertion, not
  our finding).
- **Multi-channel corroboration (added 2026-08-03, operator decision).**
  Several channels can deliver the same document — a DOJ release
  arrives through the newsroom feed AND the subscription email
  (observed 2026-08-03: three such pairs in one day, the email first
  each time). Same-day items sharing a **normalized canonical URL** are
  one document observed through more than one ingestion channel:
  presentation lists it **once**, marked corroborated with the other
  channels named in place — independent receipt is evidence worth
  stating, never a judgment about the content — while EVERY observation
  stays captured, hashed, counted in the coverage accounting, and
  present in the machine surfaces flagged `duplicate_of` (the
  `is_backfill` precedent: agents get the full observation record).
  The merge key is the URL and only the URL, one shared normalization
  used by every surface; **title similarity never merges** (measured
  the same day: three distinct DOJ job postings shared one title), and
  an item without a URL never merges. The merge is presentation, not
  identity: the two package records, their captures, and their
  manifests remain distinct — de-duplicating at ingest would erase the
  corroborating observation, which is the opposite of its value.
- Ingestion obeys §4 unchanged: paced, budgeted (its own daily bucket),
  fully logged, conditional requests wherever the server supports them,
  robots.txt honored via an RFC 9309 parser with crawl-delay respected.
- **Tiers (amended 2026-07-26).** The registry classifies sources by tier
  so comprehensiveness is measurable against a defined universe rather
  than the famously uncountable full agency list: **Tier 1** — cabinet
  departments, top independents, legislative support agencies (GAO, CBO,
  CRS), the White House briefing room, and core govinfo collections;
  **Tier 2** — major sub-agency newsrooms (CDC, FDA, IRS, FBI, FEMA,
  FAA, service branches, …) and regulator clusters (Federal Reserve,
  FDIC, CFPB, NRC, …) whose output does not flow through their parent
  department's newsroom; **Tier 3** — the long tail, added
  opportunistically. Coverage claims are always stated per tier.
- **Report publishers.** GAO, CBO, and CRS publish *reports*, not press
  releases — closer in character to the GPO record than to newsrooms.
  They are ingested through the same registry/capture machinery, and
  their documents are treated editorially like official analyses:
  attributed to their institution, with its nonpartisan mandate noted.
- **Aggregator sources.** An aggregator (e.g. oversight.gov, which
  collects reports from ~70 Inspectors General) is transport, not origin:
  digest citations must point to the originating agency's document, and
  the aggregator's role is disclosed.

### Email-distributed sources (added 2026-07-29)

A third non-GPO source class: official publications an agency *pushes*
to subscribers — GovDelivery/Granicus bulletins and agency-run
listservs. This is the consent-maximal channel (the publisher
affirmatively transmits the content over its own chosen distribution
system) and the primary path for re-opening newsroom sources whose web
channels refuse identified clients (see
`docs/access-alternatives-research-2026-07-29.md`). Governing rules:

- **Subscribe as ourselves, like any citizen.** One dedicated project
  mailbox, held under the public attribution identity (§9) — never a
  personal address — subscribes through each agency's own signup flow.
  The mailbox address is project infrastructure: recorded in `.env`
  (git-ignored) like other credentials, never committed.
- **Registry integration.** Each subscription is its own registry entry
  (`type: email`, adapter named per platform, e.g. `govdelivery`),
  sibling to — never replacing — the blocked web entry, whose
  `unavailable` record stands as accountability data. The five
  onboarding gates apply, adapted: the "probe" is subscribing and
  parsing the first real bulletins end-to-end; the content evaluation
  compares bulletin coverage against the agency's visible newsroom
  output and discloses the gap (per-topic subscriptions rarely equal
  the full newsroom).
- **The raw message is the capture.** The full RFC-5322 message bytes
  are stored content-addressed, exactly like a web capture:
  `content_sha256` over the raw message is the evidentiary hash;
  normalized extracted text drives change detection as usual.
- **DKIM verification is the corroboration layer (§7).** Each message's
  DKIM signature is verified at ingest and the result recorded; the
  selector's DNS public key is archived alongside the capture (keys
  rotate — the key that verified must be preserved, or the signature
  becomes uncheckable later). A verifying signature over stored raw
  bytes is cryptographic evidence that the agency's chosen distributor
  sent exactly this content — this replaces Wayback corroboration,
  which does not apply to email (GovDelivery's bulletin archives are
  login-walled). Messages that fail DKIM are still ingested but marked
  `dkim: fail` and excluded from any tamper-evidence claims.
- **Dating.** The message's `Date` header (and any bulletin-stated
  date) is `claimed_published_at`; receipt time is our observation.
  The §3 dating rule applies unchanged: digests list what the agency
  dates on the digest day; backfill (e.g. a subscription's welcome
  batch) is disclosed under AGENCYPR-EX-01, never passed off as news.
- **Ingest what is offered — the web refusal still stands.** Bulletins
  are often teasers linking to the newsroom page that refuses our
  client. We ingest the bulletin's own content (mode disclosed:
  `email-full` vs `email-teaser`) and never fetch a link whose host
  blocks us — receiving an email is not consent to crawl the site it
  links to. If the agency later opens the web channel, the adapter
  posture is re-evaluated (gate 5).
- **Our mailbox, our budget.** Polling our own mailbox costs government
  servers nothing; §4's request budgets don't apply to it. It is still
  paced (bounded intraday polls — ~15-minute cadence under continuous
  ingestion, amended 2026-07-30), logged in the access narrative, and
  per-message ingest events are recorded like any fetch attempt in the
  daily manifest — absence must remain an assertion.
- **Consent is revocable.** An unsubscribe request, list removal, or
  bounce-out by the agency is honored immediately and recorded in the
  registry notes — the same standing the no-evasion rule gives a 403.
- **Attribution and register are unchanged.** Bulletins are agency
  advocacy: §2's attributed-speech rule applies exactly as it does to
  newsroom releases.

### Multi-media publications (added 2026-08-05)

A growing share of what agencies publish is not text: audio news
bulletins (USDA's radio service and its peers), image feeds (NASA's
image of the day), and video (DVIDS is the dominant federal source).
These are official publications and belong in scope. The class is
admitted here so the work can begin; each medium still passes the §3
onboarding gates like any other source, and nothing below is a
commitment to ingest a specific site.

- **Text first, always.** The ingest question for every media item is
  what *published* text accompanies it: an official transcript, a
  caption or subtitle file, a supplied caption, alt text, a description
  field in the feed. That text is the record. Machine transcription and
  machine description are the fallback rung only (§3, media
  transformation), and what they produce is derived text under §2 —
  marked, never quoted as the agency's words.
- **We link, we do not rehost.** The digest embeds or links media at the
  publisher's own URL. We do not mirror audio or video, and the point of
  ingesting them is inference and summarization, not redistribution. The
  §4 budgets bind media fetches like any other request, and media is
  heavy: a source whose items cost megabytes each is a source that needs
  a stated byte posture in its registry entry before activation.
- **Integrity applies to bytes, not just text.** A media asset we rely
  on is hashed and recorded like extracted document text (§7), so that a
  file replaced at a stable URL is detectable rather than silent. An
  agency swapping an image or re-cutting a video is exactly the kind of
  change the provenance chain exists to catch.
- **Volume is an editorial problem before it is a token problem.** A
  source like DVIDS publishes far more than a daily digest can carry;
  selection must be mechanical and party-blind (§2) and must happen
  *before* any model sees a transcript or a frame (§6 rule 4). A media
  source that can only be filtered by asking a model what matters is a
  source we are not yet ready to ingest.

### Source adapters (amended 2026-07-28)

Real publication interfaces are irregular: feeds without GUIDs, article
pages that block identified clients, script-rendered sites whose content
lives in embedded JSON, report indexes instead of newsrooms. The pipeline
absorbs this irregularity at **one seam**: the `SourceAdapter` abstraction
(`agencies.py`). A registry entry may name an adapter (`adapter:` field;
default `rss`), and the adapter owns exactly six decisions while the
shared loop owns everything else (conditional GETs, robots, budgets,
capture, provenance, storage, disclosure):

0. **Enumeration** (`items`, added 2026-07-31) — how the fetched index
   bytes become the item list, so a source that is not an RSS feed (an
   XML index, a JSON API) reuses every invariant the loop owns. An
   `items()` reading an index bounds itself to
   `config.INDEX_LOOKBACK_DAYS`: a feed is bounded by its publisher, an
   index is not.
0a. **Request parameters** (`request_params`, added 2026-07-31) — the
   query the index URL is fetched with, for sources whose directed
   channel is an API: page size, sort order, and any credential. Keys
   ride here and nowhere else, because §4's redaction operates on
   parameters — a key pasted into a URL string would be logged.
1. **Identity** (`stable_id`) — what makes two sightings the same
   document (feed GUID; else normalized URL).
2. **Fetch posture** (`wants_article`) — full article fetch, or
   feed-metadata-only (e.g. a source whose articles refuse identified
   clients: we ingest what is offered, never force what is refused).
3. **Text extraction** (`extract_text`) — how served bytes become plain
   text (default HTML stripping; specializations may parse content the
   server embeds statically, e.g. JSON-LD `articleBody` — parsing bytes
   we were sent is legitimate; executing scripts or impersonating a
   browser is not).
4. **Fallback** (`fallback_text`) — what to store when no article text is
   available (title + feed description), always disclosed via the stored
   mode.

**Access hierarchy (amended 2026-07-28).** An adapter reaches for access
methods in this order, and records which rung it stands on:

1. **Directed programmatic access** — whatever the agency itself offers
   for machines: a documented API, bulk data, RSS/Atom feeds, sitemaps.
   Using the channel the publisher built for the purpose is both the most
   respectful and the most stable choice.
2. **Basic web access** — plain fetches of the same HTML pages a citizen
   reads, through the robots-enforcing client, only where no directed
   channel exists.
3. Never: browser impersonation, script execution, or any access the
   source refuses to identified clients.

**Transformation ownership.** The adapter owns the shaping of source data
into the pipeline's schema (documents/captures → packages/extracted_texts
and the analysis context). That shaping should be **as smart as the
source data allows, deterministically**: exploit every structure the
source provides — feed fields, embedded structured data (JSON-LD,
microdata), consistent markup, official metadata — before falling back to
generic text stripping. **LLM inference is the secondary tool**, used
only where programmatic transformation genuinely cannot recover the
context (e.g. classifying an unstructured page's document type, or
repairing text order from a hostile layout) — and when used, it is
budgeted, ledgered, versioned like every other prompt surface (§3a), and
its output is marked model-derived in metadata, never laundered into
fields that read as source-provided.

**Media transformation specifically (added 2026-08-05).** The same order
applies with a sharper edge, because the gap between the record and our
rendering of it is widest here. An official transcript or caption file,
where the publisher offers one, always beats speech-to-text; published
alt text or a supplied caption always beats a generated description.
Machine transcription and machine description are the fallback rung,
never the first reach, and a source is probed for the official artifact
before any model is pointed at the media. What they produce is derived
text under §2 — marked, never quoted as the record.

General guidance (see `docs/adding-sources.md` for the how-to): prefer
configuration (registry fields) over code; write an adapter only when
identity, posture, or transformation genuinely differ; ground it in probe
evidence (captured bytes, not assumptions); keep §2/§7 invariants —
attribution, capture-before-extract, honest disclosure of what could not
be extracted. The worked example is the USPS adapter (no GUIDs +
redirect-interstitial links).

### Source onboarding lifecycle (amended 2026-07-26)

Adding a source is an evaluation, not a URL paste. Every source moves
through these gates, each recorded in the registry entry:

1. **Registered** (`planned`): identity, description, best-known URLs,
   tier — added to the registry so the gap is visible.
2. **Probed:** `scripts/check_sources.py` exercises the *whole* ingestion
   chain through our identified client — robots verdict, fetch (captured
   into provenance), format detection with feed autodiscovery, item
   enumeration with field inventory (GUIDs? dates? full text or
   teasers?), and one sample article fetched and text-extracted. Findings
   are stored as structured JSON; failures record exactly what was
   observed (never retried into submission, never evaded).
3. **Content-evaluated:** before activation, someone (human or model)
   reviews the probe findings and answers, in the registry entry's notes:
   *what does this source publish in total, and what fraction will our
   ingestion see?* (e.g. a feed carrying only the latest 10 items of a
   40/day newsroom under-covers it; an index page may expose categories
   the feed omits). Under-coverage is disclosed, not discovered later.
4. **Active:** ingestion wired, appearing in digests, coverage-statement
   accounting includes it.
5. **Re-evaluated:** any persistent fetch failure or site redesign drops
   the source to `unavailable`/re-probe; status changes are worklog
   events.

## 3a. Prompt Governance (amended 2026-07-26)

All LLM prompts are code, versioned, and change through procedure:

- **Inventory** (amended 2026-07-30; source surfaces added 2026-08-03).
  Seven prompt surfaces exist: the map/summarization preamble
  (`analyze._PREAMBLE`, versioned by `PROMPT_VERSION`), the plain-speak
  restatement preamble (`analyze._PLAIN_PREAMBLE`,
  `PLAIN_PROMPT_VERSION`), the Day-in-Review compose prompt
  (`compose._PROMPT`, `COMPOSE_PROMPT_VERSION`), the section quick-read
  prompt (`compose._SECTION_PROMPT`, `SECTION_PROMPT_VERSION`), the
  section discovery-key prompt (`tags._TAG_PROMPT`,
  `TAG_PROMPT_VERSION`, added with §6 rule 12a), the developer-insight
  suggestions prompt (`insight._PROMPT`, `INSIGHT_PROMPT_VERSION`), and
  the source-page surfaces below (`SOURCE_ASSESS_PROMPT_VERSION`,
  `SOURCE_DESC_PROMPT_VERSION`). Each layer versions independently — a
  deliberate design so iterating on one never regenerates the artifacts
  of another.
- **Source-page model surfaces (added 2026-08-03, operator-approved
  plan).** Two reader-facing prose layers on the per-source pages, both
  cheap-tier, batched, ledgered, restating the §2 banned list from
  `config.BANNED_TERMS` AND scanned by the same gate regex **before
  storage** — a failed scan stores nothing and the page renders without
  that block; the gates are never loosened for them. Both render
  labeled model-derived with date, model, version, and trigger.
  - **Source assessment** (`SOURCE_ASSESS_PROMPT_VERSION`): a prose
    restatement of OUR measured ingestion relationship — formats seen,
    cadence, delivery quirks, incident history from registry notes,
    what changed since the last assessment. Input is the measured
    stats, the registry entry, and the source's own previous stored
    assessment ONLY — the prior text is our own derived artifact and is
    what "what changed" is measured against; outside knowledge stays
    excluded. It obeys the health-page law:
    it reports our observation of our own ingestion, never an opinion
    about the publisher — no quality judgments of an agency, ever.
    Regenerated when none exists, at 30 days of age, or when the
    source's health label changes.
  - **Source description** (`SOURCE_DESC_PROMPT_VERSION`): what the
    source IS — a short summary (1–2 sentences) and a 250–500 word
    orientation for readers. This is the ONE surface licensed to draw
    on the model's general knowledge of public institutions (a registry
    entry cannot say what the FDA is), and it carries that license's
    price: it is labeled a model-written orientation, never presented
    as official-record content, and it must remain factual and
    opinion-agnostic about the institution it describes. Regenerated
    only when the registry entry changes or the version bumps — never
    on a timer.
- **Media model surfaces (admitted 2026-08-05, not yet built).** The
  multi-media class (§3) will need up to three further surfaces:
  transcription of audio and video that arrives without an official
  transcript, description of images that arrive without published alt text
  or a caption, and summarization over a transcript or sampled frames.
  They are named here so the governance lands before the code rather than
  after it. Each arrives with its own version constant, its own ledger
  rows, the §2 banned list restated in-prompt, the same storage-time gate
  the source-page surfaces use, and the derived-text marking §2 requires.
  Until they exist the Inventory above stays at seven — this bullet is a
  commitment, not a claim.
- **The insight surface is developer-facing, never editorial.** Its
  output appears only in the daily operations report under
  `provenance/runs/` — never in a digest, the site's reader pages, or
  any coverage claim. It is labeled model output (§2) and its input is
  the run's own mechanical metrics, never document content. Because it
  is outside the published digest, the render-time lexicon gate does not
  apply to it; the labeling rule still does.
- **The plain-speak contract specifically** (the most iterated surface):
  input is ONLY the stored summary (never raw text, never outside
  knowledge); output is one sentence ≤ ~35 words; jargon is expanded into
  ordinary words; dates/deadlines preserved; the §2 banned list restated
  inside the prompt AND enforced un-masked by the render-time lexicon
  gate — two independent layers, prompt-side and validator-side.
- **Iteration procedure:** (1) edit the prompt text in code; (2) bump
  that surface's version constant; (3) state the regeneration scope in
  the worklog entry (what re-runs, what it costs — the version keying
  makes this precise); (4) the validation gates are never loosened to
  accommodate a prompt change — if new prose trips the lexicon, the
  prompt is wrong, not the gate; (5) spot-audit a sample of regenerated
  output against §2 before the next digest publishes.
- **Measured-cost discipline:** prompt iterations are cheap by design
  (plain-layer rephrase ≈ 85K tokens/day of data; compose ≈ 30K) —
  this cheapness exists because of the version decoupling and must be
  preserved by it.

### Secondary (later phases)

- **Congress.gov API** (`api.congress.gov`, same api.data.gov key) — bill
  status, actions, cosponsors, votes metadata. **Partly promoted
  2026-07-31:** the `bill` endpoint is active and supplies the
  `BILLACTIONS` collection above; committee meetings, nominations,
  treaties and the beta House roll-call endpoint remain later phases.
- **FederalRegister.gov API** — richer FR metadata (agencies, significance
  flags), no key required.

## 4. Respectful Access Policy

We are guests on public infrastructure. Rules, enforced in code, not by
discipline:

- **Self-imposed budget:** max **1 request/second sustained per host**, an
  **hourly ceiling**, and a daily cap. The client refuses to exceed any of
  them, counting from the fetch log so the limits hold across processes and
  restarts.

  **Amended 2026-07-31 (operator-authorised, on evidence).** The govinfo
  daily cap rises from 2,000 to **6,000 requests/day**, and a ceiling of
  **500 requests/hour** is added. The evidence, recorded because a budget
  change is not made on preference: api.data.gov — the shared GSA service
  govinfo runs on — documents **1,000 requests per hour per key** and
  answers **429** when that is exceeded. In three days of logs we have
  received **no 429 of any kind**, and at 2,000/day we averaged about **83
  requests per hour**, roughly 8% of the allowance. The hourly ceiling is
  half of what the publisher permits and is the limit that actually keeps
  us clear of theirs; the daily figure is bounded by it. The ceiling binds
  every client including the end-of-day finalizer — it is the publisher's
  limit, not ours, and nothing exempts anyone from it.

  **What this amendment does not do.** It does not raise the per-second
  pace, does not weaken any crawl-delay, and does not change the rule that
  the answer to slowness is fewer requests. **Failed attempts still count
  against the budget** — a 503 cost the server a request whatever it
  returned to us. On 2026-07-30, 882 of 4,868 govinfo requests were 503s,
  so roughly a fifth of the day's allowance was spent on the server's own
  unavailability; the response to that is fewer requests, never faster
  retries.

  **Agency class raised 500 -> 1,500/day (amended 2026-07-31,
  operator-authorised).** The condition set was "as long as we aren't
  violating any bot/server restraints set by source servers", so the
  evidence is what those servers actually declare. **No publisher
  declares a daily request cap** — robots.txt has no such directive, and
  none of our hosts sets the `Request-rate` or `Visit-time` extensions.
  What they declare is **crawl-delay**, which governs spacing, not volume,
  and which we honor exactly and unchanged: gao.gov 420s, fda.gov 30s,
  fema.gov 15s, justice.gov and odni.gov 10s, ftc.gov 5s. At hourly
  polling each host receives about **24 requests a day — one an hour**.

  The raise was made **after** removing the waste it would otherwise have
  funded: the robots cache lived on a client instance while the collector
  built a fresh client every cycle, so a 24-hour TTL never survived one
  poll and roughly half of every cycle re-asked permission already
  granted (F-007). Fixing that first is the §4 principle applied to
  ourselves — fewer requests before more allowance.

  **Agency class raised 1,500 -> 3,000/day (amended 2026-08-06,
  operator-authorised).** Same condition, same evidence discipline,
  re-measured on production rather than assumed. What the publishers
  declare is unchanged: across the 18 hosts whose robots.txt we hold,
  **none declares `Request-rate` and none declares `Visit-time`** — no
  daily cap exists to be near. Eight declare crawl-delay (gao.gov 420s
  down to nasa.gov 1s), which is spacing and is enforced per host by the
  client independently of this number: raising the daily allowance
  cannot make a single host receive requests any faster.

  What we do, measured over the seven days to 2026-08-06: **~42-46
  requests per host per day, about 1.8 an hour** — roughly one request
  every 33 minutes to a federal web server. Refusals over the project's
  whole history: **zero 429 responses from any government host** (all
  178 recorded 429s are web.archive.org, a separate corroboration budget
  with its own cap), and 17 real content refusals across 25 hosts — the
  other 103 4xx responses are robots.txt fetches, which under RFC 9309
  mean *allow*.

  The trigger was arithmetic, not appetite. Production reached 1,287
  agency requests on 2026-08-06 against a collector ceiling of 1,275
  (85% of 1,500; the remainder is the §4 EOD reserve), and refused to
  poll three newly activated sources. At roughly 29 requests per source
  per day, 1,500 supports about 44 sources and the registry had already
  passed that. 3,000 supports about 88, against 27 planned entries still
  waiting — and leaves the per-host rate exactly where it is, because
  budget buys *breadth*, never speed.

  **What this amendment does not do.** It does not touch crawl-delay,
  the per-host pacing clock, the govinfo budget, the hourly govinfo
  ceiling, or the EOD reserve fraction. It does not license article
  fetches a source's posture excludes. And it does not change the
  standing rule that a refusal is honored, never evaded and never
  retried into submission.

  **Finalizer reserve (added 2026-07-31).** Continuous collectors may spend
  only **85%** of a daily budget; the remainder is reserved for the
  end-of-day finalizer. On 2026-07-30 the collectors spent all 2,000
  govinfo requests on historical backlog and the finalizer could not sync
  the day it was finalizing, so that day's digest carries no Congressional
  Record, no bills and no public laws at all. A day already collected is
  published even if its top-up sync cannot run; the gap is disclosed.
- **Concurrency across hosts only — never against one.** Ingestion may poll
  distinct hosts in parallel (added 2026-07-28: one worker per host group,
  each with its own client), because politeness is a promise made to each
  server individually: every host still sees at most 1 request/second, its
  robots.txt crawl-delay, and conditional requests, exactly as if it were
  the only source. Two sources sharing a host always share one worker and
  one client, so their pacing clocks are common. Daily budgets remain
  global across workers (counted from the shared fetch log); the check is
  read-before-request, so concurrency can overshoot a cap by at most the
  worker count — budgets are set with headroom for exactly this reason.
- **Poll, don't hammer (amended 2026-07-30 for continuous ingestion):**
  polling is watermark-delta at bounded intervals — each ask remains "what
  changed since my last watermark," now repeated through the day on
  per-source-class clocks (govinfo ~30 min, agency feeds ~60 min via
  conditional requests, our own mailbox ~15 min) instead of once. **The
  binding invariants do not loosen:** at most 1 request/second per host with
  crawl-delay overriding downward, per-class daily budgets enforced by the
  client, every request logged, identified UA. Frequency is additionally
  governed by **backpressure** *(scope stated precisely, 2026-08-02)*:
  past 70% of the **agency class's** daily budget its host collectors
  double their interval for the rest of the UTC day. The govinfo class
  is governed differently and deliberately: its collectors may spend
  only 85% of the daily budget (the finalizer reserve, below) and every
  govinfo client — finalizer included — obeys the 500/hour publisher
  ceiling. Extending interval-doubling to the govinfo collector is an
  open item, not an assumed behavior. Either way the invariant is the
  same: continuous polling must never starve the canonical run.
- **Date-bound every sync.** A sync with no stored watermark (first run, or a
  reset) must not walk open-ended history: it starts at now minus a small
  fixed lookback window (`INITIAL_SYNC_LOOKBACK_DAYS`, currently 3 days) and
  sets the watermark from there. Older history is only ever acquired as a
  deliberate bulkdata backfill, never as an accidental API crawl.
- **Never re-download unchanged content.** Cache everything fetched, keyed by
  package ID + lastModified. Honor HTTP caching (ETag/If-Modified-Since)
  where offered.
- **Honor server signals:** back off exponentially on 5xx, respect
  `Retry-After` exactly, watch `X-RateLimit-Remaining` and stop early if it
  drops unexpectedly.
- **Bulk data for bulk needs.** Any backfill of more than a few days of
  history uses the bulkdata endpoints (built for this), run off-peak
  (overnight US Eastern), throttled.
- **Identify ourselves:** descriptive `User-Agent` with contact email.
- **Log every request, twice.** Accountability has two layers, both with the
  API key redacted:
  1. `data/fetch_log.db` — the canonical, queryable record of every outbound
     request (URL, UTC timestamp, status, bytes, elapsed ms, attempt, error),
     written by the HTTP client itself so nothing can bypass it.
  2. `data/logs/access-YYYY-MM-DD.log` — a human-readable narrative at DEBUG
     level (every request, pacing sleeps, retries and why, watermark moves,
     per-package outcomes), regardless of console verbosity.
  `scripts/audit.py` reports our footprint from layer 1 at any time:
  requests/day vs. budget, status mix, bytes, retries, recent errors.

## 5. Architecture Concept

Four stages, each writing durable artifacts so any stage can be re-run
without touching upstream:

```
[1 FETCH]  scheduled sync → govinfo collections delta → download new/changed
           packages → store raw (XML preferred; PDF where graphics require)
           + metadata + fetch log
                │
[2 EXTRACT] parse raw XML → normalized records (speaker, chamber, bill ids,
           agency, doc type, dates, full text) → local store (SQLite to
           start). Graphics flagged in the source (FR <GPH>) are inventoried
           per document and extracted as individual image assets.
                │
[3 ANALYZE] mechanical aggregation first (counts, stages, cross-references);
           LLM summarization second, constrained by §2 rules, always with
           citations back to package/granule IDs. Selected items' graphics
           get a vision pass (see §6) so visual content informs the summary.
                │
[4 REPORT]  daily digest (Markdown): headline activity, per-chamber summary,
           new rules/laws, tracked-item updates, coverage statement.
           Digests embed relevant source graphics (stored under
           digests/assets/, cited like text) rather than only linking out.
           A static HTML site (site/, built by scripts/build_site.py) is a
           derived, zero-LLM presentation layer over the canonical
           Markdown — regenerable at any time, suitable for local viewing
           and GitHub Pages.
```

- **Continuous operation and the two-artifact model (amended
  2026-07-30):** ingestion runs continuously — a single supervisor
  process (`src/fapd/collect.py`) with per-source-class workers on their
  own clocks (a 420-second crawl-delay host simply lives on its own
  clock without delaying anyone), journaling arrivals into
  `item_journal` with observation timestamps. Presentation splits into
  two artifacts: a **live `/today` page** — derived-only, never
  committed, updating through the day, carrying a mandatory disclosure
  block ("preliminary; items may be re-dated, re-summarized, or
  excluded by end-of-day editorial gates; the dated digest is the
  record") — and the **canonical dated digest**, produced by the
  end-of-day finalizer run (`run_pipeline.py`), frozen by its
  validation gates, and committed as the §7 integrity record. Intraday
  state never bypasses a gate: whatever `/today` showed, the canonical
  digest is what the validation gates passed.

  **Amended 2026-08-02 — what the live page may do.** `/today` is not
  raw arrivals: it applies the *mechanical* editorial layer, and must,
  because a live page that ignores the §3 dating rule lists archive
  backfill as today's news (observed 2026-07-31, 721 items). The
  license and its limits: the live page MAY apply any zero-LLM,
  deterministic rule the digest also applies — and must do so through
  the **same shared function**, never a reimplementation — and MAY
  carry mechanical reader context: the §3 backfill split (counted and
  disclosed in place), the federal working calendar
  (`src/fapd/fedcal.py`: the eleven 5 U.S.C. 6103 holidays with OPM
  observed shifts, pure and dependency-free — a quiet Sunday is the
  publishers resting, and saying so is disclosure, not editorializing),
  and mechanical display gates (e.g. the prose check that keeps scraped
  navigation chrome out of an item's visible body; the suppressed text
  stays verbatim in today.json). The live page may NOT: run a model,
  compose, rank, or apply any judgment that is not a named deterministic
  rule. The machine surface (today.json) always carries the same
  computed values as the human page, labeled.

  **Amended 2026-08-03 — the frozen day view, and the digest's calendar
  line (operator-approved plan).** A third artifact joins the model:
  the **frozen day view** `/day/YYYY-MM-DD.html` + `.json` — the same
  full-entry listing the live page shows, rendered by the *same*
  `build_today` machinery (never a reimplementation) at end of day from
  the frozen database state, committed with the evidence, and linked
  from that day's digest. It is a standardized programmatic URL for
  humans and agents; its disclosure block states what it is: the
  complete observed listing for the day, mechanical rules applied — the
  dated digest remains the canonical record. Days before the item
  journal existed have no day view; the gap is disclosed, not
  backfilled. And the canonical digest MAY carry the same mechanical
  calendar context the live page carries (`fedcal.py`, the same shared
  function): a weekend or federal-holiday digest states so in its
  header — a quiet Sunday is the publishers resting, and saying so in
  the record is disclosure, not editorializing.

  **Amended 2026-08-05 — supersession of a frozen day (operator).** The
  freeze is correct and the freeze is early. A publisher-dated collection
  can be published by its source *after* our end-of-day boundary has
  passed, and when that happens the frozen digest reports the day as
  empty when it was not. The measured case is the Congressional Record:
  govinfo posts a day's issue 8–22 hours after that day ends
  (CREC-2026-08-04, 62 granules, first seen 2026-08-05T11:42Z against an
  04:47Z freeze; CREC-2026-08-03, 154 granules, first seen
  2026-08-04T12:27Z against an 04:06Z freeze), so since automatic
  midnight-Eastern finalization began on 2026-08-02 every session-day
  digest has published an empty §1 while the Record for that day existed.
  A digest MAY therefore be re-rendered and republished when a
  publisher-dated collection for its day arrives late. The superseding
  digest carries a dated amendment notice saying what changed and why,
  and the superseded revision is preserved and stays addressable — the
  record of what we published at the time is itself part of the record.

  **What this amendment does not do.** It does not reopen a day for
  *observation-dated* sources: an agency release that arrives late is
  dated by §3's rule and belongs to the day it arrived, not to an
  amendment — the two dating regimes stay separate for the reason §3
  gives. It does not make the freeze advisory; the first publication
  still passes every validation gate on its own and stands as published.
  And it does not license a silent re-render: changing a published
  digest without saying so is precisely the failure this rule exists to
  prevent. Until the mechanism ships, the obligation is disclosure —
  a section with no data because its source had not published yet must
  say that, and must never render as a count of zero that reads as
  "nothing happened." *(2026-08-06: observation-day filing — the §3
  amendment — removes the CREC case that motivated this amendment; it
  remains for genuine corrections.)*
- **Storage:** filesystem for raw documents (`data/raw/<collection>/<date>/`),
  SQLite for metadata and extracted records. No cloud dependency to start.
- **Language:** Python (mature XML tooling, easy scheduling). Decide at first
  implementation step; record in worklog.
- **Digest output:** `digests/YYYY-MM-DD.md` — accumulates as a browsable
  archive.

## 6. Token Economics (LLM Budget Discipline)

The analysis layer (§5 stage 3) uses LLM calls, which are the pipeline's only
meaningfully metered resource. Same philosophy as §4: budgets are properties
of the code, not of operator discipline.

### Measured reality (2026-07-24, from our own archive)

- Raw archive size wildly overstates LLM-relevant volume: a ~49 MB CREC day
  is ~46.6 MB PDF page images and only ~2 MB XML text.
- Actual text per publication day: CREC ~2 MB, FR ~2.6 MB, BILLS ~2 MB
  (~28 KB/bill × 60–70). Verbatim-everything ceiling ≈ **1.5–2M input
  tokens/day**. A full day therefore exceeds every single-call context
  window — per-item map-reduce is structurally required.
- With mechanical selection and official-summary-first drafting, realistic
  daily load is **~300–800K input / ~10–20K output tokens**.

### Rules (enforced in code when the analysis layer is built)

1. **Whole PDFs never reach a model.** Text always comes from XML — a PDF
   page is ~an order of magnitude more tokens than its text. Graphics are
   the exception, handled as *individual extracted images*, not PDF pages:
   documents that flag graphics (FR `<GPH>`; measured 0–54/issue) get their
   images extracted at the EXTRACT stage, and a **vision pass runs only on
   graphics belonging to items already promoted by a selection rule** —
   rule 4 applies to images exactly as to text. Image tokens count against
   the daily cap and are logged in the ledger like any other call.
   - **Rule FR-GPH-01 (boilerplate graphics).** FR content graphics carry
     section-coded GIDs (e.g. `EN23JY26.004` — equations, forms, maps,
     annex pages; measured 103 of 111 in our first window). Non-conforming
     GIDs (e.g. `Trump.EPS` — signatures, seals) are boilerplate: they
     never trigger a PDF fetch, never get a vision pass, and are never
     embedded. Excluded counts are disclosed in the Coverage Statement —
     the classification is mechanical (a filename pattern), party-blind,
     and costs zero tokens.
2. **Mechanical work costs zero tokens.** Counts, stages, vote tallies,
   groupings, and the entire Coverage Statement are computed in code. An LLM
   call that could have been a SQL query is a bug.
3. **Official summaries before our summaries.** FR agency abstracts, the
   CREC Daily Digest section, and official bill titles/stage codes are the
   first drafting inputs. We summarize verbatim primary text only for items
   a selection rule promoted — this is cheaper *and* editorially safer.
4. **Selection before summarization, always.** No model ever sees an item
   that hasn't passed a §2 mechanical selection rule. The rules bound the
   token spend; loosening a rule is a GUIDE change, not a tweak.
5. **Summarize once, store forever.** Summaries are durable artifacts keyed
   by package/granule ID + content version. Regeneration happens only when
   the source's lastModified changes or the prompt version bumps —
   never as a side effect of re-running the digest.
6. **Tier the models.** Cheap/fast models for per-item map work
   (classification, per-item compression); the strongest model only for the
   final digest composition pass, which sees already-compressed input.
7. **Token ledger, like the fetch log.** Every LLM call is logged (UTC
   timestamp, model, purpose, input/output tokens, package IDs touched) to a
   local ledger. A self-audit report (like `scripts/audit.py`) answers "what
   did analysis cost this week?" at any time. The LLM layer is
   backend-pluggable (amended 2026-07-30): the `claude` CLI remains the
   default for operator-machine runs, and an Anthropic-API backend serves
   hosted runs; callers name model *tiers*, a config table resolves the
   concrete model per backend, and the ledger records both the backend and
   the resolved model for every call — budget rules apply identically to
   both.

   *Provider redundancy and segmentation (amended 2026-08-05, operator).*
   The pluggability exists to be used: additional providers beyond
   Anthropic are permitted and wanted, so that a single vendor's outage or
   refusal cannot stop the digest. Three conditions bind them. The
   ledger's `backend` column is the provenance of which provider produced
   a given output and stays populated for every call, including failures.
   Failover between providers is explicit and logged — a run that silently
   changed providers would make the ledger's cost history unreadable and
   the digest's model attribution false. And the §2 gates are
   provider-blind: banned-lexicon enforcement, labeling of model-derived
   prose, and the storage-time scans apply identically whoever answered,
   because a gate that trusted one vendor more than another would be a
   gate we could not describe honestly.
8. **Measure first, then cap.** The token ledger (rule 7) runs from the
   analysis layer's very first call, but **no hard cap is enforced until
   real test runs establish a measured baseline** — capping against
   estimates risks tuning the digest around a guess (decided 2026-07-24).
   Once a few days of ledger data exist, a daily input-token cap is set
   from observed load (working figure: ~1M/day) and enforced with a hard
   stop: overflow items stay queued for the next day and are named in the
   Coverage Statement's known gaps — a budget stop must never become a
   silent omission (§2). *(2026-08-02: the measured baseline this rule
   was waiting for exists — the ledger now holds ordinary days (~90K
   in), judicial-heavy days (~1.5M), and three runaway incidents (17.4M,
   39.7M, and a re-fire day) that a cap would have stopped. Building the
   enforcement is ops-backlog OB-4 / review R1; the cap VALUE is set by
   the operator from the ledger when that lands.)* *(2026-08-02, later,
   operator ruling: NO standing daily cap — "the value stays the
   operator's" includes the value none. The enforcement exists as an
   on-demand throttle instead: `FAPD_DAILY_TOKEN_THROTTLE`, unset by
   default; when set, an LLM call that would start past the day's
   input-token figure — counted from the ledger, so nothing bypasses it
   and it holds across processes — raises the same pause-type
   backpressure the workers apply to our HTTP budgets: paused, queued to
   the next day, disclosed. Engaging or clearing it is an operational
   action on the box, never a code change. A per-call prompt-size guard
   is standing policy regardless: one call must never carry an unbounded
   prompt.)*
9. **Plain-speak is a decoupled, batched restatement pass.** The per-item
   plain-language layer (§2) is generated by its own batched pass over
   *stored summaries only* (~170 tokens/item, ~25 items/call), versioned
   independently (`PLAIN_PROMPT_VERSION`) so phrasing iterations never
   regenerate factual summaries. Cheap tier, ledgered like everything else.
10. **Graphics in digests are cited evidence, not decoration.** A digest
   embeds a source graphic only when it belongs to a summarized item, and
   it carries the same citation discipline as text (package/granule ID +
   permanent URL). Selected graphics are copied to `digests/assets/<date>/`
   so the published digest is self-contained; items whose remaining
   graphics were *not* rendered still disclose the count with a link to the
   source PDF — the §2 no-silent-omission rule applies to images too.
11. **Batch-friendly by design.** The daily job is not latency-sensitive:
   structure analysis as batchable per-item calls so it can run on
   discounted/off-peak capacity, and so a partial day's work is resumable —
   mirroring the fetch layer's pending-queue semantics.
12a. **Section tags are a fourth model surface (added 2026-07-30).**
   Each digest section carries a `Tags:` line: mechanical tags first
   (branch, agency — derived from collection and registry metadata at
   zero tokens), then up to three model-generated one-to-three-word
   discovery keys describing the section's content for search and
   agent retrieval. The key layer is independently versioned
   (`TAG_PROMPT_VERSION`), generated in one batched cheap-tier call
   per digest day from the stored section synopses, ledgered, and —
   because tags render inside the digest — linted by the same
   banned-lexicon gate as all generated prose. Tags are navigational
   metadata, never judgments; a section whose keys fail validation
   renders with mechanical tags only.
12. **Continuous operation preserves batching (added 2026-07-30).**
   Under continuous ingestion, "fully continuous" is honored **by
   layer**: mechanical layers (item listing, official summaries, counts,
   rendering) update on every arrival at zero tokens; model map/plain
   layers fire only on batch-threshold-or-age triggers (a full batch, or
   the oldest pending item exceeding a latency bound), never per item —
   per-item calls would re-pay the fixed prompt overhead rule 9's
   batching exists to amortize. Day/section composition runs **only** in
   the end-of-day finalizer: its staleness rule would otherwise
   recompose on nearly every intraday batch, and the Day in Review
   describes a completed day by definition.

- **Rule 13 — we do not buy days we will not publish (added
  2026-07-31).** The analyze layer works only on the current publication
  day and the one before it (the day the end-of-day finalizer freezes).
  Post-dated digests are not published, so a token spent on an older day
  is taken from the day that will be. Items older than the window stay
  pending and are disclosed by the coverage accounting; they are never
  silently dropped. Evidence: on 2026-07-30 the layer wrote 184 summaries
  across eleven dates reaching back to 2024-06-18 while the digest day
  itself received none.
- **Rule 14 — the retry ladder has a ceiling (added 2026-07-31; amended
  2026-08-02 to state the whole mechanism).** Group
  retries first (rule unchanged); single-item retries stop at a configured
  ceiling per run — **and at a durable ceiling per ITEM**
  (`MAX_ITEM_SUMMARY_ATTEMPTS`, remembered in `summary_attempts`),
  because a per-run ceiling alone resets every collector cycle: analyze
  runs every 15 minutes per pending date, so a permanently
  unsummarizable item was retried indefinitely — 1,345 single retries
  and 39.7M input tokens in one day. Past either ceiling the item is
  left unsummarized and said so.
  A backend with a large fixed per-call cost makes single retries almost
  pure overhead: measured 2026-07-30 on the CLI backend, ~29K input tokens
  per call regardless of payload, and 366 single retries cost 10,860,137
  input tokens — 62% of the day — to buy summaries of ~800 tokens each.
  Disclosure is cheaper than completeness bought at that price, and the
  coverage statement is where it is disclosed.

## 7. Provenance & Tamper-Evidence

For mutable sources (§3 agency newsrooms), the archive must support the
claim: *this content was served at this URL at this time, and here is
exactly what it said.* Anticipated interference and mitigations:

| Threat | Mitigation |
|---|---|
| Stealth edit after publication | two-hash captures + re-check pass → `modified` events with both versions retained |
| Silent removal | conservative `missing`→`removed` promotion (≥3 failures over ≥48h), captures retained; `restored` tracked |
| Backdating / retro-insertion | `claimed_published_at` vs our `first_seen_at`, always stored separately; claimed dates inside a demonstrably covered window are a flagged anomaly |
| URL churn | document identity keyed by stable id (feed GUID / normalized URL); url + final_url recorded |
| Content served differently to us | Wayback Machine snapshot for new captures, within its daily budget (§4) — an independent second witness; best-effort, never blocking, gaps topped up by later passes |
| "You fabricated the archive" | attempt-level daily manifests (committed) with a hash chain over retained manifests, PLUS git/GitHub history ordering and Wayback corroboration — the three together, because the chain alone has stated limits (below) |

Mechanics:
- **Two hashes per capture:** `content_sha256` (exact decoded entity
  bytes — the evidentiary hash; bytes stored content-addressed under
  `data/captures/`) and `text_sha256` (normalized extracted text,
  versioned by `normalizer_version` — drives change detection, because
  raw agency HTML churns with tokens and asset URLs). Both recorded, so
  both "the bytes changed" and "the words changed" are supportable and
  distinguishable.
- **Attempt-level manifests:** `provenance/manifests/YYYY-MM-DD.jsonl`
  (committed) records every *attempt* — captures, 304s, robots refusals,
  errors — because absence must be an assertion (§2): a gap in monitoring
  is on the record as a gap, never ambiguous. Each manifest's header
  carries the sha256 of the most recent earlier manifest on file.
  **Honest scope (stated 2026-08-02):** the chain proves a retained
  middle manifest was not altered; because the header names no
  predecessor date, it cannot by itself prove the newest day was not
  truncated or that a day was never written — git history and Wayback
  are the current witnesses for those cases, and strengthening the
  header with the predecessor's date is on the development backlog. A
  provenance claim overstated is a provenance claim broken (§2 applies
  to our own claims too).
- **DKIM as corroboration for email-distributed sources (added
  2026-07-29):** for the §3 email class, the stored raw message plus a
  verifying DKIM signature — with the verifying DNS public key archived
  at ingest, since selectors rotate — is cryptographic evidence that the
  agency's chosen distributor sent exactly these bytes. It plays the
  independent-witness role Wayback plays for web captures (and is
  arguably stronger: the signature covers the content itself). Honest
  limit: DKIM proves the *distributor* (e.g. GovDelivery on the
  agency's behalf) signed the message, not that the agency's newsroom
  page said the same thing.
- **Honest limits (stated wherever provenance is claimed):** hashes prove
  what was served **to our identified client** — not what every visitor
  saw; our timestamps are backed by git/GitHub history and Wayback
  corroboration, not third-party notarization (external anchoring, e.g.
  OpenTimestamps, was considered and declined 2026-07-26; revisitable).
  Full statement in `PROVENANCE.md`.

## 8. Roadmap

- **Phase 0 — Foundation (now):** this guide, worklog, repo scaffolding,
  obtain API key, verify access with a handful of hand-run requests.
- **Phase 1 — Fetch & store:** rate-limited govinfo client, daily delta sync
  for CREC/BILLS/FR, raw archive + fetch log.
- **Phase 2 — Extract:** XML parsers per collection, normalized SQLite
  schema; graphic inventory (`<GPH>` counts per document) and image-asset
  extraction for flagged documents.
- **Phase 3 — Analyze & report:** mechanical aggregation, citation-bound
  summarization, vision pass on selected items' graphics, first real daily
  digest with embedded source graphics; iterate on digest format.
- **Phase J1 — Judicial via govinfo (active):** USCOURTS collection through
  the existing pipeline; opinion extraction from case packages; selection by
  court type + published designation; digest section 5 with the standing
  completeness disclosure.
- **Phase J2 — Supreme Court direct:** supremecourt.gov slip opinions and
  orders, syllabus-first drafting.
- **Phase 4 — Broaden & harden:** add PLAW/CHRG/CRPT/DCPD, Congress.gov
  metadata, backfill via bulk data, bias/faithfulness spot-audits
  (periodically diff a digest item against its full source).
- **Phase R — Hosted runtime (adopted 2026-07-30):** a VPS runs the daily
  pipeline on a schedule (cron/systemd timer) and pushes evidence commits
  with a bot identity; GitHub remains the public repository, CI, and the
  integrity witness for committed digests and manifests (§7). The VPS's
  stable IPv4 and reverse-DNS serve as crawler identity infrastructure.
  Plan: `docs/vps-runtime-plan.md`.

## 9. Open-Source Readiness

This repo may be published on GitHub at any time. Everything committed is
written as if it were already public:

- **Licensing (decided 2026-07-29).** Code: **Apache-2.0** (`LICENSE` +
  `NOTICE`; the patent grant and contribution clarity suit the
  fork-this-for-your-government mission). Content — digests, site,
  explanatory docs: **CC BY 4.0** (`LICENSE-CONTENT.md`; attribution is
  exactly the onward-citation ask we already make of agents). Quoted
  official government text is public domain (17 U.S.C. § 105) and is
  never claimed. Stated in the site footer, llms.txt, the agents page,
  and each digest's methodology footer.
- **How this project is built is itself public (decided 2026-07-29).**
  FAPD is developed with generative AI (Claude agents; every commit
  carries a co-author trailer), and we say so plainly rather than
  scrubbing the worklog: a project whose editorial code requires labeling
  machine-generated prose does not hide its own machine authorship. The
  full statement — including the working thesis that AI assistance let
  design attention go to content and intent (editorial rules, provenance,
  access ethics) rather than syntax, and how building *for* agentic
  readers informed building *with* agents — lives in
  `docs/site/ai-development.md`, published on the site. The worklog's
  development narrative is part of that transparency and is never
  retroactively curated.

- **No personal details in tracked files.** Real email addresses, names,
  account identifiers, and machine hostnames live only in `.env` (git-ignored)
  and are read via `config.py`. Committed examples use blank or placeholder
  values.
- **No private/absolute paths.** Code and docs use repo-relative paths only
  (`config.py` derives everything from its own location — keep it that way).
- **Secrets are structurally impossible to commit:** they exist solely in
  `.env`, which is git-ignored; code fails loudly if they're missing rather
  than falling back to embedded defaults.
- **Worklog is public-ready.** Write `WORKLOG.md` entries with publication in
  mind — describe work and decisions, not personal circumstances.
- **Pre-commit habit:** skim the diff for emails, keys, tokens, home paths
  (`/Users/...`), and IPs before every commit.
- **Author attribution convention:** wherever the author's name appears in
  content we control (git identity, package metadata, license, docs), use
  **"David D. Karnowski"** — the middle initial disambiguates from other
  David Karnowskis in tech. Contact email in public-facing metadata is the
  dedicated project address (repo-local `git config user.email`), never a
  personal or GitHub-credential address.

## 10. Working Agreements

- `WORKLOG.md` gets a timestamped, verbose entry for every work session:
  what was done, why, decisions made, dead ends included.
- Decisions that change scope, sources, or editorial rules are made in this
  file first, then implemented.
- Secrets (API keys) live in `.env`, git-ignored, never in code or logs.
- **main is sacred — for code (adopted 2026-07-30).** All engineering work
  (code, tests, governing documents, config) happens on `feature/`, `bug/`,
  or `arch/` branches; CI must be green before promotion; merges are
  fast-forward. An agent about to edit code on `main` STOPS and confirms a
  branch name with the operator first.
- **Evidence exemption (scoped by path, not by author):** pipeline evidence
  commits — `digests/`, `provenance/`, `site/`, and `SOURCES.md` as produced
  by pipeline runs — commit directly to `main` as data. GitHub history is
  the §7 integrity witness; parking evidence on a branch would delay the
  ordering timestamp it exists to provide. A commit that mixes evidence
  paths with code paths is a rule violation, not an exemption.
- **Engineering practice is governed by `CLAUDE.md`** (the agent working
  guide) **and `docs/code-standards.md`** (code rules), adopted 2026-07-30
  from the operator's sibling projects. This GUIDE remains the editorial
  constitution and always prevails on conflict.
- **Operational runbooks live under `docs/ops/`**; production-affecting
  actions follow the authorization gates stated there — a VPS write happens
  only on the operator's explicit ask in the current session, never inferred
  from prior approval or a generic "looks good."

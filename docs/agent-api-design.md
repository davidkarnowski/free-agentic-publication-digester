# Agent-facing API surfaces at year scale — design memo

*2026-07-30. Status: proposal — design exploration only, nothing here is
built. Companion to `docs/continuous-ingestion.md` (the two-artifact
model this API exposes) and GUIDE §1 (dual audience), §5, §7. Last
reviewed: 2026-07-30.*

## §1 Problem statement

The operator's question, verbatim: **"When I look at the flat JSON
digest listing, how will we manage this when the project is a year
old?"**

Today `site/digests.json` is one flat array of every digest ever
published. At 5 digest days that is 1.7 KB and ideal. The same design at
day 365 is a ~100 KB file that every polling agent re-downloads whole to
learn one fact ("is there a new day?"), and at day 3000 it is a file
larger than many agents' working context. The flat listing is the most
visible instance of a general pattern: several of our surfaces are
whole-history artifacts rewritten wholesale on every build, which is
exactly the wrong shape for a site whose history only grows and whose
past never changes. This memo designs the year-scale replacement within
the project's hard constraints:

- **Static hosting only.** nginx serving flat files; zero server-side
  compute; zero JavaScript; no query evaluation at request time.
  Everything is pre-rendered by the pipeline.
- **Filesystem-clone complete.** The site must remain fully functional
  opened from a local clone, with no server at all.
- **Deterministic, zero-LLM rendering** (docs/code-standards.md); the
  canonical dated digest stays the record (GUIDE §5); provenance
  disclosures travel with every machine surface (GUIDE §1).

## §2 Current surface inventory (measured 2026-07-30, 5 digest days)

| Surface | Bytes | Shape | Rewritten when |
|---|---|---|---|
| `site/digests.json` | 1,681 | flat array, all days, ~283 B/entry + ~250 B envelope | every build (embeds `generated`) |
| `site/feed.xml` | 2,026 | Atom, capped at 20 newest entries | every build |
| `site/sitemap.xml` | 849 | flat urlset, ~65 B/URL (13 URLs) | every build |
| `site/llms.txt` | 1,537 | agent guidance | every build |
| `site/robots.txt` | 126 | allow-all + sitemap pointer | every build |
| `site/index.html` | 3,051 | one card per day, ~300 B/card | every build |
| `site/2026-07-29.html` (typical digest page) | 93,183 | full styled day | **every build** (footer `Generated` stamp) |
| `digests/2026-07-29.md` (canonical) | 73,429 | frozen at EOD | never |
| `provenance/manifests/2026-07-29.jsonl` | 21,076 | frozen, hash-chained | never |
| `site/today.json` | not in checkout (derived-only, gitignored) | per-item detail, live day | every collector render cycle |

Per-day item detail sized from the live database using exactly the
`build_today` serialization (items array, `indent=1`; envelope adds
~1 KB):

| Date | Items | Bytes | Avg B/item |
|---|---|---|---|
| 2026-07-28 (catch-up day) | 1,206 | 1,280,497 | 979 |
| 2026-07-29 | 230 | 251,037 | 1,007 |
| 2026-07-30 (partial, intraday) | 177 | 187,373 | 973 |

Two structural facts fall out of the inventory:

1. **The richest machine-readable data we produce exists only for one
   day at a time.** `today.json` carries per-item citations,
   official URLs, channel labels (including DKIM verification status),
   mechanical tags, labeled summaries, and verbatim openings — then is
   overwritten when the date rolls. The finalized days, our actual
   product, expose none of this as JSON; an agent wanting item-level
   structure for 2026-07-12 has to parse Markdown or HTML.
2. **Every page is volatile.** `build_site` rewrites every digest page
   on every run because the footer embeds build time, and `digests.json`
   embeds `generated`. Cache validators (ETag/Last-Modified) therefore
   churn even when content is identical, and the daily evidence commit
   touches every existing page — at day *n* the commit diff is *n*
   files, so total rewritten blobs grow quadratically (~66,000 page
   rewrites in year one alone).

## §3 What breaks, and when

Growth math at ~283 B per `digests.json` entry, ~300 B per index card,
~65 B per sitemap URL, ~93 KB per digest page, ~250 KB per day-detail
file (typical day, `indent=1`). Token figures use the rough constant of
~4 bytes/token for English JSON.

| Surface | 365 days | 1,095 days (3 y) | 1,825 days (5 y) | 3,000 days |
|---|---|---|---|---|
| `digests.json` | 104 KB | 310 KB | 517 KB | 849 KB |
| — tokens to ingest whole | ~26 K | ~78 K | ~130 K | ~212 K |
| `index.html` | ~110 KB | ~330 KB | ~550 KB | ~900 KB |
| `sitemap.xml` | 24 KB | 71 KB | 119 KB | 195 KB |
| `feed.xml` (20-entry cap) | ~8 KB | ~8 KB | ~8 KB | ~8 KB |
| digest HTML, cumulative | 34 MB | 102 MB | 170 MB | 279 MB |
| day-detail JSON, cumulative (if built) | 91 MB | 274 MB | 456 MB | 750 MB |

Failure modes, in order of onset:

- **Now → month 3: polling waste.** Every agent checking for a new day
  re-downloads the whole of `digests.json`. The fix is a small
  newest-first file plus conditional GETs, not a bigger pipe.
- **Month 6 → year 1: flat-file ingestion cost.** An agent that ingests
  `digests.json` to *find* something pays tens of thousands of tokens
  for an index scan SQL would do for free on our side at render time.
  `index.html` reaches the size where human page load and scan both
  degrade; it needs year/month archive pages (a human-surface sibling of
  this API, noted but not designed here).
- **Year 1+: git churn.** The quadratic page-rewrite pattern makes the
  daily evidence commit noisy (every page "changed") and bloats history
  with byte-identical-but-for-timestamp blobs. This is a build-behavior
  bug at scale even though each individual build is correct.
- **Never (within horizon): sitemap limits.** The protocol caps a
  sitemap at 50,000 URLs / 50 MB. At one page per day plus a handful of
  doc pages we reach ~3,000 URLs at day 3000. Sitemap sharding via a
  sitemap index file is standard and trivial, but it is not needed for
  decades; we should not build it now.
- **Structural, not scale: the missing per-day detail file.** Not a
  breakage but the largest gap this redesign should close — see §2
  fact 1. Once the DB ages or a clone lacks `data/`, item-level detail
  for past days is unreconstructable unless it was frozen to a file at
  EOD.

## §4 Proposed layout — `/api/v1/`

A small stable root that never grows, shards that grow only within
their year, a bounded newest-first file for polling, and one frozen
detail file per finalized day:

```
site/
  api/
    v1/
      index.json                  # root: tiny, near-static; the one URL agents learn
      latest.json                 # newest 30 days, newest-first; the polling target
      digests/
        2026.json                 # one shard per calendar year, oldest-first
        2027.json                 # past years become immutable on Jan 1
      days/
        2026-07-23.json           # frozen per-day detail, written once at EOD
        2026-07-24.json
        ...
  digests.json                    # kept, unchanged shape + a pointer field (§10)
  feed.xml                        # kept, current Atom document (20 entries)
  feed/
    archive-2026-07.xml           # RFC 5005 archived feed pages, immutable (§6)
  today.json                      # unchanged: live day, preliminary, gitignored
```

Design properties, each load-bearing:

- **The root is stable.** `index.json` changes only when a year shard is
  added or the API itself changes — not daily. Agents can hardcode one
  URL and never re-learn the layout.
- **Volatility is quarantined.** Exactly two files change on an ordinary
  day: `latest.json` and the current year's shard (plus one new
  `days/` file, which is a creation, not a rewrite). Everything else
  304s forever.
- **Past years are immutable.** A shard for a completed year is never
  rewritten; a `days/` file is never rewritten after EOD. Immutable
  files are what make conditional GETs, git history, and the "sync five
  years cheaply" story all work at once.
- **Granularity matches the product.** The day is FAPD's unit of
  publication; one detail file per day mirrors one digest per day and
  one manifest per day. (Per-item files were considered and rejected —
  §12.)
- **Year shards, not month shards.** A year shard at ~350 B/entry
  (lean shape, §5) is ~128 KB complete — one fetch syncs a year, and a
  12× file-count increase buys nothing since intra-year freshness comes
  from `latest.json` and conditional GETs, not shard granularity.

## §5 Schema sketches

All payloads carry `api_version` so the version survives file copies
that lose the URL path. Consumers are asked (in agents.html) to ignore
unknown fields; we promise additive-only changes within v1 (§9).

### Root — `api/v1/index.json` (~1 KB, near-static)

```json
{
 "api_version": "1",
 "title": "Free Agentic Publication Digester — Daily Federal Digest",
 "documentation": "https://fapd.info/agents.html",
 "latest": "https://fapd.info/api/v1/latest.json",
 "today": {
   "url": "https://fapd.info/today.json",
   "status": "preliminary — items may change until end-of-day gates freeze the dated digest"
 },
 "day_url_template": "https://fapd.info/api/v1/days/{YYYY-MM-DD}.json",
 "shards": [
   {"year": "2026", "url": "https://fapd.info/api/v1/digests/2026.json",
    "first_date": "2026-07-23", "immutable": false}
 ],
 "feed": "https://fapd.info/feed.xml",
 "canonical_repository_paths": {
   "digest_markdown": "digests/{YYYY-MM-DD}.md",
   "provenance_manifest": "provenance/manifests/{YYYY-MM-DD}.jsonl"
 },
 "legacy_flat_index": "https://fapd.info/digests.json"
}
```

`immutable: true` on completed years is a published promise, and the
only field of a past shard's entry that ever flips.

### Shard — `api/v1/digests/2026.json` (lean, oldest-first, ~350 B/day)

```json
{
 "api_version": "1",
 "year": "2026",
 "immutable": false,
 "digests": [
  {"date": "2026-07-29",
   "html": "https://fapd.info/2026-07-29.html",
   "canonical_markdown": "digests/2026-07-29.md",
   "detail": "https://fapd.info/api/v1/days/2026-07-29.json",
   "teaser": "The Congressional Record for the day is Senate-side, …",
   "tags": {"mechanical": ["senate", "federal-register"], "model": ["…"]}}
 ]
}
```

Entry shape = the current `digests.json` entry + `detail` pointer +
the OB-9 tag arrays (model keys labeled by segregation into their own
array, per GUIDE §2). Counts and everything item-level live in the day
file, keeping the shard an index, not a payload. No `generated`
timestamp — the shard's content is fully determined by its days, so an
unchanged shard is byte-identical across builds (this is what makes
ETags honest).

### Latest — `api/v1/latest.json` (bounded, newest-first, ~12–15 KB)

Same entry shape as a shard, newest first, window of 30 days, plus the
only volatile envelope in the API:

```json
{
 "api_version": "1",
 "window_days": 30,
 "newest_date": "2026-07-29",
 "today": {"url": "https://fapd.info/today.json", "status": "preliminary"},
 "digests": [ …30 entries, newest first… ]
}
```

The polling contract: conditional GET on `latest.json`; a 304 means no
new finalized day. Its size is constant forever.

### Per-day detail — `api/v1/days/YYYY-MM-DD.json` (~250 KB typical)

The finalized sibling of `today.json`: same per-item richness, frozen
at EOD by the finalizer, `status: "final"`, plus the provenance block
`today.json` cannot have:

```json
{
 "api_version": "1",
 "date": "2026-07-29",
 "status": "final",
 "generated_at": "2026-07-29T23:58:41Z",
 "pipeline_version": "…",
 "prompt_version": "…",
 "digest": {
   "html": "https://fapd.info/2026-07-29.html",
   "canonical_markdown": "digests/2026-07-29.md",
   "sha256": "…of the canonical Markdown…"
 },
 "provenance": {
   "manifest": "provenance/manifests/2026-07-29.jsonl",
   "sha256": "…",
   "note": "manifests are hash-chained day to day; see PROVENANCE.md"
 },
 "labels": {
   "summary_method": "official = agency/GPO text; llm = model-generated, labeled",
   "opening_verbatim": "first ~240 chars of the official text, unedited",
   "tags": "mechanical (branch, document type, agency) plus labeled model discovery keys"
 },
 "counts": {"CREC/HOUSE": 12, "FR/RULE": 9},
 "items": [
  {"package_id": "…", "granule_id": "…",
   "collection": "FR", "doc_type": "RULE",
   "title": "…", "agency": "…",
   "source_id": null, "source_class": "govinfo",
   "channel_label": "govinfo API",
   "official_url": "https://www.govinfo.gov/app/details/…",
   "observed_at": "2026-07-29T14:31:02Z",
   "claimed_published_at": null,
   "inclusion_rule": "FR-SIG-01",
   "summary": "…", "summary_method": "official",
   "opening_verbatim": "…present only when the item has no summary…",
   "tags": ["executive", "final rule", "environmental protection agency"]}
 ]
}
```

Honesty rules carried over intact: `summary_method` labels official vs
model text in place; `opening_verbatim` is unedited official text;
email items carry their `dkim_result`; `observed_at` and
`claimed_published_at` stay separate fields (GUIDE §7 backdating
defense). One deliberate trim versus `today.json`: `opening_verbatim`
is emitted only when the item has no summary (its render-time role is
fallback), saving ~240 B on most items. Files keep `indent=1` — the
diffability and hand-inspection value outweighs ~20% size, and
transfer cost is gzip's problem (§7).

## §6 Feed and sitemap at scale

**feed.xml — RFC 5005 archived feed.** The current document keeps its
URL and its 20-entry cap forever. It gains:

- `<link rel="current" href=".../feed.xml"/>` and
  `<link rel="prev-archive" href=".../feed/archive-2026-07.xml"/>`;
- monthly archive documents `feed/archive-YYYY-MM.xml`, each marked
  `<fh:archive/>` (namespace `http://purl.org/syndication/history/1.0`)
  and chained to its predecessor via `rel="prev-archive"`.

A completed month's archive is immutable, so a feed reader (or agent)
can walk the whole history once and then only ever poll the small
current document. This is the standards-track answer to "feed history"
— no invented pagination. Entry `<updated>` values stay the synthetic
`T12:00:00Z` day-stamp already in use (deterministic; a real freeze
timestamp can be adopted when day files exist to source it from).

**sitemap.xml — leave alone.** 195 KB at day 3000 against protocol
limits of 50,000 URLs / 50 MB. Adopt a sitemap index file only if the
URL count ever approaches ~10,000; noting the threshold here is the
whole build.

## §7 Caching: what nginx gives us free, what it doesn't

Verified against the pinned `nginx:1.30-alpine` in
`deploy/vps/docker-compose.yml`:

- **Free today:** static file serving emits `ETag` (on by default since
  nginx 1.3.3) and `Last-Modified` (file mtime), and honors
  `If-None-Match` / `If-Modified-Since` with 304 responses. The
  conditional-GET economy in §11 requires zero configuration.
- **Not free: gzip.** The stock image config ships with gzip commented
  out, and it defaults to `text/html` only. A one-file `conf.d` drop-in
  is needed: `gzip on;` plus `gzip_types application/json
  application/xml text/plain;` and a sane `gzip_min_length`. JSON
  compresses at roughly 8–10×, so a 250 KB day file transfers at
  ~25–30 KB. (nginx downgrades the strong ETag to a weak one on
  gzipped responses; weak ETags still satisfy `If-None-Match`, so the
  304 economy survives.) Pre-compressed `.json.gz` + `gzip_static` was
  considered and deferred — on-the-fly gzip of a 250 KB file is cheap
  and keeps the build simpler.
- **Undermined by our own build:** validators are only as good as file
  stability. Because every page is rewritten with a fresh footer stamp,
  mtimes and ETags change sitewide daily even where content didn't.
  The build must become **write-if-unchanged** (compare bytes before
  writing) and page-embedded timestamps must derive from content (a
  digest page's stamp = its day's freeze time, not the build's wall
  clock). This also collapses the §2 quadratic git churn: the daily
  evidence commit shrinks to the files that actually changed. Note:
  this touches presentation of every page and the `digests.json`
  `generated` field — flagged as its own confirm-gated work item, not
  smuggled in with the API build (see CLAUDE.md §10's standing caution
  on timestamp formats).

The filesystem-clone requirement is unaffected throughout: every API
file is a plain committed file with relative structure; nothing above
depends on headers to *function*, only to be cheap.

## §8 Evidence or derived? Where frozen day files live

The design tension: `site/` is documented as "derived, regenerable at
any time from `digests/*.md`" — but per-day detail (citations,
`observed_at`, channel labels, DKIM results, per-item tags) comes from
the database, not from the canonical Markdown. `data/` is gitignored
local state; once it ages out or on any fresh clone, an uncommitted day
file is unreconstructable. So the day file cannot be "derived" in the
existing sense. Two coherent positions:

1. **Evidence artifact (recommended).** `api/v1/days/YYYY-MM-DD.json`
   is written once by the EOD finalizer — the same event that freezes
   the digest and the manifest — and committed under the evidence
   exemption, exactly like `digests/` and `provenance/`. `build_site`
   treats `days/` as append-only and never rewrites an existing file
   (pinned by a test). This satisfies filesystem-clone completeness and
   makes the file citable: it is part of the record, frozen by the same
   gates, at the same moment.
2. **Derived artifact.** Regenerate from the DB on every build; accept
   that clones and the far future lose item-level JSON for old days.
   This contradicts the purpose in §2 fact 1 and is rejected here, but
   the choice is the operator's — it is a GUIDE §5 matter.

Repo growth under position 1, honestly stated: ~91 MB/year of raw JSON
in the working tree (~250 KB × 365). Because each file is written once
and never modified, git history cost is the one-time packed size —
JSON packs at roughly 10–15%, so ~10–14 MB/year added to `.git`.
Five years: ~456 MB working tree, ~60 MB pack — alongside ~170 MB of
digest HTML the site already accumulates. Static hosting is indifferent
to this; clone size is the real cost and should be monitored (an
`audit`-style annual size line in the ops runbook would keep it
visible). If it ever matters, the escape hatch is moving `days/` to a
separate evidence repository — a structural change no earlier design
decision forecloses, precisely because day files are immutable.

Provenance chain interaction: the day file *references* its manifest
and the canonical Markdown by path + sha256 (one direction, no cycles
— the manifest freezes before the day file is written and cannot embed
its hash). The day file itself is covered the way all committed
evidence is: git history ordering plus the manifest chain around it.

## §9 Discovery, versioning, stability promises

**Discovery.** Three pointers, all existing surfaces:

- `llms.txt` gains an `## API` block naming `api/v1/index.json`,
  `latest.json`, and the day-URL template — this is the convention
  agents actually read first.
- `agents.html` gains the schema documentation: field meanings, the
  labels contract (official vs model text), the immutability promises,
  and the consumer requests (ignore unknown fields; use conditional
  requests; identify honestly).
- `digests.json` gains an `api` pointer field (§10).

`.well-known/` was considered and rejected: RFC 8615 paths are
registered, none fits this, and an unregistered one is a convention
nobody polls. `index.json` at a documented path plus llms.txt does the
same job inside conventions that exist.

**Versioning.** Belt and suspenders: the `/api/v1/` path prefix (so v2
can coexist during migration) and an `api_version` field in every
payload (so a copied file self-describes). Within v1 the promise is
**additive-only**: new fields may appear; existing fields never change
meaning or type; entry shapes never lose fields. A breaking change
mints `/api/v2/` with v1 frozen but served in parallel for at least six
months, announced in the feed and on agents.html. URL stability
promises published on agents.html: digest pages `/<YYYY-MM-DD>.html`,
day files `/api/v1/days/<date>.json`, and `latest.json` are permanent
URLs; completed-year shards and completed-month feed archives are
immutable content.

Machine-readable JSON Schema files (`api/v1/schema/*.json`) are a
phase-3 nicety, not a launch requirement — prose documentation on
agents.html is the binding contract either way.

## §10 Backward compatibility — `digests.json`

The file keeps working. Concretely:

- **Now (phase 1):** shape unchanged, still the complete flat array;
  two additive fields in the envelope:
  `"api": "api/v1/index.json"` and
  `"api_note": "preferred interface; this flat file grows with the
  archive and remains for compatibility"`.
- **Standing policy question (operator decision, revisit at day ~365):**
  either (a) keep generating the full flat file indefinitely — cost is
  ~100 KB/year of bytes, no correctness risk, maximal compatibility —
  or (b) after a documented deprecation window, freeze or window it.
  Option (b) silently changes semantics under consumers who assumed
  "complete history" and is the kind of quiet narrowing this project
  avoids; the memo recommends (a), with the `api_note` doing the
  steering. Either way `digests.json` never 404s.

The Atom feed needs no compatibility work: its URL and 20-entry shape
are unchanged; RFC 5005 links are additive metadata existing readers
ignore.

## §11 Token economics for consumers (worked examples)

Costs assume gzip transfer (~8–10× on JSON) and ~4 bytes/token for
ingested text. "Requests" count round trips, the scarcer agent
resource.

| Task | Requests | Transfer | Tokens ingested |
|---|---|---|---|
| "What happened on 2026-05-12?" — narrative | 1 (`digests/2026-05-12.md` or `.html`) | ~9 KB gz | ~18 K |
| Same — item-level structure | 1 (`api/v1/days/2026-05-12.json`) | ~28 KB gz | ~62 K, or a fraction after field-filtering |
| Same — existence + teaser only | 1 (year shard, cached) | 0 if 304 | ~90 per entry |
| "Anything new since yesterday?" | 1 conditional GET `latest.json` | 0 on 304, ~2 KB gz on change | 0 or ~3–4 K |
| First-time sync of one year's index | 2 (`index.json` + year shard) | ~15 KB gz | ~33 K |
| Re-sync after N months away | 1 + shards changed (past years 304) | proportional to change only | proportional to change only |
| Same tasks against status-quo `digests.json` at year 3 | 1 | ~35 KB gz **every poll** | ~78 K **every ingestion** |

The design targets in the operator's framing: one small fetch for one
day; no re-download of unchanged history, enforced by immutability plus
the free 304 machinery of §7 rather than by any custom protocol.

## §12 Considered and rejected

- **Any server-side API (REST backend, GraphQL, search endpoint).**
  Rejected on the hard constraint, and the constraint is the product:
  zero request-time compute is why the site is cheap enough to invite
  unlimited agent traffic, why it works from a filesystem clone, and
  why there is no attack or failure surface at read time. A GraphQL
  resolver over three SQLite files is a second system with none of
  those properties.
- **Query parameters (`?from=…&to=…`, `?page=2`).** Meaningless on
  static files — nginx serves the same bytes regardless. Paged and
  partitioned *file names* are the static equivalent and are the whole
  of §4.
- **Search.** Request-time search requires compute we don't have.
  Agents can implement their own search over shards + day files (that
  is what the token math in §11 buys); humans get year archive pages.
  A pre-built static index (e.g. per-tag listing pages) is possible
  future work once OB-9 item tags exist, and is deliberately out of
  scope here.
- **Per-item JSON files.** ~200–1,200 files per day; inode churn, a
  commit tree that dwarfs the data, and agents forced into request
  storms to reassemble a day. The day is the publication unit; the item
  is addressed *within* the day file by `package_id`/`granule_id`.
- **Month shards.** 12× the files of year shards to optimize a fetch
  (~128 KB/year, lean) that doesn't need optimizing; freshness comes
  from `latest.json`, not shard granularity.
- **Publishing SQLite files as the API.** The DBs are internal state
  (schema evolves by `IF NOT EXISTS` DDL, contains operational tables);
  publishing them would turn every schema change into a breaking API
  change and export data (fetch logs, mailbox state) that isn't part of
  the editorial product.
- **JSON Feed alongside Atom.** A second feed format doubles
  maintenance and pins another shape forever for consumers Atom + the
  JSON index already serve. Revisit only on demonstrated demand.
- **`.well-known` discovery.** See §9.
- **External CDN / compression services.** Out of scope and against
  posture; the VPS static stack already serves this design.

## §13 Phased implementation backlog

**Phase 1 — next code push (the API skeleton):**
1. `publish.py`: emit `api/v1/index.json`, `latest.json` (window 30),
   current-year shard. Deterministic, no volatile envelope fields
   except `latest.json`'s.
2. Finalizer: write `api/v1/days/<date>.json` at EOD (the `today.json`
   serialization + `status: final` + digest/provenance hash block +
   the `opening_verbatim` trim). Backfill the existing finalized days
   from the live DB **now, while the data still exists**.
3. `build_site`: treat `days/` as append-only — never rewrite an
   existing day file (pinned by a test that builds twice and asserts
   byte-identity, and one that plants a sentinel day file and asserts
   survival).
4. `digests.json`: add `api` + `api_note` fields (additive).
5. `llms.txt` + `agents.html`: document the API, the labels contract,
   the immutability and additive-only promises.
6. Tests: shard/flat-index consistency (same dates, same teasers),
   schema-shape snapshots, determinism (two builds, identical bytes for
   everything but `latest.json`'s envelope).
7. `deploy/vps`: gzip drop-in prepared in the repo (applies at the next
   operator-authorized deploy — the VPS gate holds; nothing in phase 1
   requires it, transfers are merely larger until then).

**Phase 2 — the stability push:**
8. Write-if-unchanged site build + content-derived page stamps
   (confirm-gated; see §7 — this is the fix for sitewide ETag churn
   and quadratic evidence commits).
9. RFC 5005 feed archives (`feed/archive-YYYY-MM.xml`), links added to
   `feed.xml`.
10. Human archive pages for `index.html` (per-year listing pages,
    index shows the newest window) — sibling work, same partitioning
    logic.

**Phase 3 — enrichment and horizon items:**
11. Tag arrays in shard entries and item tags in day files, when OB-9's
    item layer lands (schema slot already reserved in §5).
12. Static JSON Schema files under `api/v1/schema/`.
13. `digests.json` long-term policy decision at ~day 365 (§10).
14. Sitemap index — only at the ~10,000-URL threshold; year-2031-class
    work.
15. Annual repo-size line in the ops runbook (§8 monitoring).

GUIDE precedence: phases 1–2 touch GUIDE §1's enumerated agent
surfaces and §5's derived-artifact description; the corresponding GUIDE
amendment (day files as EOD-frozen evidence; the API added to the
standing commitments list) precedes the phase-1 build, per §10 of the
GUIDE.

## §14 Open questions for the operator

1. **Evidence status of day files (§8):** confirm position 1 — frozen
   at EOD, committed forever under the evidence exemption, ~10–14
   MB/year of packed history — or direct otherwise. This is the one
   decision the rest of the design leans on.
2. **`digests.json` end state (§10):** full flat file forever
   (recommended), or a dated deprecation-and-freeze plan?
3. **Volatile page stamps (§7, phase 2):** approve moving every page's
   footer stamp from build-wall-clock to content-derived time and
   making the build write-if-unchanged? It rewrites history *behavior*
   (not history), touches every rendered page once, and is the
   precondition for honest sitewide caching.
4. **`latest.json` window and shard granularity (§4/§5):** 30 days and
   year shards are proposed defaults; any operational reason to prefer
   other values before they ossify into the v1 contract?
5. **`opening_verbatim` trim (§5):** acceptable that the frozen day
   file omits the verbatim opening for items that carry a summary, or
   should the day file preserve the full `today.json` shape at ~240 B
   × items extra?

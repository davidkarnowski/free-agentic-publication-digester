# Adding a Source (including your own government's)

This pipeline is built to be pointed at official government publication
interfaces — the U.S. federal ones it ships with, or your own
jurisdiction's if you fork it. The premise (GUIDE §1): official
publications are the record a government produces *in order to be
public*; this codebase just makes that record easier to read, verify,
and ingest, for people and for AI agents. Everything below serves that
premise — and its ethical floor: honest identification, robots.txt
obedience, paced budgeted requests, and disclosure of everything we
could not or chose not to ingest.

## The five gates (GUIDE §3, Source onboarding lifecycle)

1. **Register** the source in `sources/registry.yaml` — identity, branch,
   tier, description, best-known URLs, `status: planned`. Run
   `scripts/sources_doc.py`; the sync-guard test enforces that SOURCES.md
   matches the registry.
2. **Probe** it: `scripts/check_sources.py --ids your-source`. This
   exercises the full chain (robots → fetch → capture → format detection
   with feed autodiscovery → item inventory → one sample article
   extracted) and writes structured findings under `data/probe/`. A
   blocked source is recorded `unavailable` with the observed behavior —
   never evaded, never retried into submission.
3. **Content-evaluate:** from the probe findings, answer in the entry's
   notes: what does this source publish in total, and what fraction will
   ingestion see? (Feed depth vs. publication volume; teasers vs. full
   text; GUIDs present?) Under-coverage is disclosed at onboarding.
4. **Activate:** set `status: active`. RSS sources are picked up by
   `scripts/ingest_agencies.py` automatically. Items flow through
   provenance capture (hashes, Wayback corroboration), the AGENCYPR
   collection, digest section 6, and the coverage statement.
5. **Re-evaluate** on failures or redesigns; status changes are worklog
   events.

## When the interface is irregular: write an adapter

An adapter owns five decisions. `items()` is the newest (2026-07-31) and
the one that makes non-feed sources possible at all: it turns the fetched
index bytes into the item list, so an XML index or a JSON API can reuse
every invariant the loop owns. **An index is not a feed** — a feed is
bounded by its publisher, but an index can list an entire congressional
session, so an `items()` reading an index must bound itself to
`config.INDEX_LOOKBACK_DAYS` before returning. Skipping that buys
hundreds of article fetches for items the §3 dating rule then excludes as
backfill.

Most sources need **no code** — the default RSS adapter handles them. An
adapter (subclass of `agencies.SourceAdapter`, registered in
`agencies.ADAPTERS`, named by the entry's `adapter:` field) is warranted
only when one of four things genuinely differs:

| Hook | Question it answers | Example specialization |
|---|---|---|
| `stable_id` | What makes two sightings the same document? | Feed has no GUIDs → normalized URL (strip query/fragment/case) |
| `wants_article` | Fetch the page, or feed metadata only? | Article pages 403 identified clients → `False` (`rss-feed-only`) |
| `extract_text` | How do served bytes become text? | Script-rendered site embedding JSON-LD `articleBody` → parse the embedded JSON (static parsing of bytes we were sent — never script execution, never browser impersonation) |
| `fallback_text` | What to store with no article text? | Title + feed description, mode disclosed |

### Access hierarchy and transformation (GUIDE §3)

Reach for access in this order, and note the rung in the registry entry:
**1) directed programmatic access** — the API, bulk data, or feed the
agency itself publishes for machines (always preferred: it is the channel
the publisher built for exactly this); **2) basic web access** — the same
HTML a citizen reads, via the robots-enforcing client; **never** browser
impersonation or script execution.

The adapter owns turning source data into the pipeline's schema, and that
transformation should be as smart as the source's own structure allows,
**deterministically first**: use feed fields, embedded structured data
(JSON-LD/microdata), consistent markup, official metadata. Reach for
**LLM inference only secondarily**, where programmatic shaping genuinely
cannot recover the context — and then budgeted, ledgered, prompt-versioned
(GUIDE §3a), with output marked model-derived in metadata.

Method: **probe first, then read the captured bytes** (they're in
`data/captures/`, content-addressed from the probe), and build the
adapter against evidence. Add tests beside `tests/test_agencies.py`
using its fakes. Keep the invariants: capture before extract, attributed
speech, honest disclosure of extraction limits in the registry notes.

### Authoring an adapter well

Lessons from the adapters built so far, in the order they will bite you:

- **Identity is a compatibility contract.** Package ids derive from
  `stable_id`'s output, and dedupe keys on them. Once a source is active,
  changing what `stable_id` returns for an already-seen item — including
  "harmless" URL normalization — re-mints identities and re-ingests
  history as duplicates. Design identity *before* activation: prefer the
  publisher's own identifier (GUID, VIRIN, docket number); normalize URLs
  aggressively (scheme/host case, query, fragment, trailing slash) only
  while the source has no history. The library default's raw-URL fallback
  is frozen for exactly this reason — five live sources depend on it
  byte-for-byte.
- **`wants_article` is a budget decision, not just an access decision.**
  Every article fetch costs one paced request *at the host's price*:
  gao.gov's robots crawl-delay makes each fetch cost 420 seconds of wall
  clock. Weigh what the feed already carries (GAO descriptions run ~4,000
  characters) against what the article adds, and say which you chose in
  the registry notes. Whatever the choice, the stored mode discloses it.
- **`extract_text` should be defensive; the loop makes failure honest.**
  A raising `extract_text` degrades that one item to `fallback_text` with
  mode `extract-fallback` (the raw capture is already stored — evidence
  survives extraction bugs). Don't let one malformed page cost a source's
  remaining items; equally, don't silently return empty text — empty or
  sentinel output should fall back explicitly, the way `UspsAdapter`
  treats its known contentless interstitial.
- **Every ingestion mode is disclosed, per item.** The stored metadata's
  `mode` field is the honesty mechanism: `full` (article fetched and
  extracted), `feed-only` (chosen never to fetch), `feed-fallback`
  (fetch refused/failed), `extract-fallback` (fetched but unparseable).
  Digest coverage language leans on these — an adapter must never launder
  a degraded mode into looking like `full`.
- **Static parsing of served bytes is the ceiling.** Mirroring redirect
  arithmetic that a served page's own script performs (`UspsAdapter`),
  reading embedded JSON-LD, parsing data attributes — all legitimate:
  the server sent us those bytes. Executing scripts, following what only
  a browser would do, or fetching what robots.txt refuses is not, no
  matter how mechanical the workaround looks.

## Email-distributed sources

Publications an agency *pushes* by email (GovDelivery bulletins,
listservs) are their own source class — the consent-maximal channel,
and often the first door worth opening for sources whose web channels
refuse identified clients. Full normative guide, from mailbox setup
through DKIM key archival to the fork checklist:
**[docs/email-sources.md](email-sources.md)** (rules: GUIDE §3
"Email-distributed sources" + §7 DKIM corroboration).

## Pointing at another government entirely

The layering to reuse: `HttpClient` (pacing/budget/logging) →
`AgencyClient` (robots/conditional GET) or a new API client like
`GovinfoClient` → registry + adapters (sources) → provenance (captures,
manifests) → extraction → rules (mechanical, party-blind selection — your
jurisdiction's equivalents of "all final rules" / "all enacted laws") →
analysis (summaries with official-summary-first) → report (citations,
coverage statement, plain-language layers) → site (human + agent
surfaces). The editorial gates (GUIDE §2) and provenance model (GUIDE §7)
are jurisdiction-neutral by design; what you replace is the source list
and the parsers.

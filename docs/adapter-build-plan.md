# Adapter and source build-out plan

*2026-07-31. Status: approved by the operator, not yet built. Any agent
may pick this up phase by phase. Companion to `docs/adding-sources.md`
(the five gates), `docs/code-standards.md` (§1 seams, §2 rules), and
GUIDE §3 (source lifecycle) / §4 (respectful access). Evidence behind
every claim: `data/probe/2026-07-31/`. Last reviewed: 2026-07-31.*

## Context

127 registered sources; 35 active, 70 planned. The 2026-07-31 probe sweep
(42 web sources, 92 requests, findings in `data/probe/2026-07-31/`) showed the
planned list is **not** a list of doors held shut:

- **33 of 42** answer HTTP 200 with robots permitting and simply advertise no
  feed — blocked on an adapter we have not written, not on a publisher.
- **4** are our own stale URLs (Interior, Education, BLS, ODNI all 404).
- **1** real refusal (commerce.gov 403 → `unavailable`), **1** transient 504.
- Separately verified reachable, no credential missing: Senate roll-call XML,
  House Clerk roll-call index, the Federal Register API (keyless), and
  Congress.gov (authenticates on the api.data.gov key we already hold).

The pipeline can ingest exactly one shape today: an RSS/Atom feed.
`agencies.poll_source` reads `urls.feed`, calls `probe.parse_feed` on the
bytes, and requires items shaped `{title, link, guid, claimed_date,
description}`. Everything else — conditional GET, robots, pacing, budgets,
capture and hashing, Wayback, dedupe, storage, mode disclosure, manifest — is
already shape-agnostic.

**Outcome:** one new seam unlocks three adapter families; the Federal Register
and roll-call votes fill the thin legislative sections that prompted the
"digests feel empty" observation.

## Architecture: one seam, then adapters

`SourceAdapter` (`src/fapd/agencies.py:25-72`) covers `stable_id` /
`wants_article` / `extract_text` / `fallback_text`. It has no hook for
**enumeration** — that is hard-coded at `agencies.py:282-287`. Add it:

```python
# agencies.py — on SourceAdapter; the base preserves today's behaviour exactly
def items(self, body, content_type):
    """(format_name, [item dicts]) from the index/feed bytes. Items use the
    probe.parse_feed shape: title, link, guid, claimed_date, description.
    Returning (None, []) marks the response unparsable, which the caller
    records and discloses. Must not raise."""
    return parse_feed(body)
```

Then `poll_source` becomes `fmt, items = adapter.items(resp.content or b"",
resp.headers.get("Content-Type"))`. Every existing adapter is unchanged and
every existing test must still pass — that is the acceptance bar for Phase 0.

Two supporting changes, both small:

- **URL resolution.** `poll_source:246` and `host_groups:381-389` both read
  `urls.feed` only. Add a module-level `source_url(entry)` returning
  `urls.feed or urls.index or urls.collection`, used in both, so grouping and
  fetching can never disagree.
- **Type gating.** Three sites filter `type == "rss"`:
  `scripts/ingest_agencies.py:44`, `stage_agencies` in
  `scripts/run_pipeline.py:81-96`, and the active-source filter feeding
  `collect.AgencyHostWorker`. Replace with one exported
  `agencies.INGESTIBLE_TYPES` so widening happens in a single place.

**Item budget discipline (binding on every new adapter).** A feed carries
recent items; an index carries the whole session — Senate's vote menu lists
every vote of the Congress. `items()` implementations **must** bound themselves
to a lookback window (new `config.INDEX_LOOKBACK_DAYS`, mirroring
`INITIAL_SYNC_LOOKBACK_DAYS` at `config.py:45`) before the per-item article
fetch, or first activation spends hundreds of requests ingesting material the
dating rule will exclude as backfill anyway.

## Phase 0 — the seam (no new sources)

**Files:** `src/fapd/agencies.py`, `src/fapd/config.py`,
`scripts/ingest_agencies.py`, `scripts/run_pipeline.py`, `src/fapd/collect.py`,
`docs/code-standards.md` (§1 seams row), `tests/test_agencies.py`.

**Acceptance:** whole suite green with zero behavioural change, plus one test
registering a stub adapter via `monkeypatch.setitem(agencies.ADAPTERS, ...)`
(the sanctioned pattern, `tests/test_agencies.py:151`) proving a non-feed
`items()` reaches storage.

## Phase 1 — stale URLs (registry only, no code) — **DONE 2026-07-31**

**Outcome: 1 of 4 recovered.** `odni-news` is active (RSS, 54 items, all
dated and with guids, sample article 8,082 chars). The other three stayed
planned, and what they taught is worth more than the count:

- **ODNI had not moved a path, it moved publishers.** Every
  `dni.gov/index.php/*` address 301s to an archive domain and 404s there;
  the live newsroom is on `odni.gov` — Joomla to WordPress, different
  domain. Generalise it: **a 404 is an unanswered question about a
  publisher, not evidence about a path.**
- **Empty-but-valid feeds are a category this plan lacked.** Interior
  advertises one feed; it is well-formed, rebuilt daily, and carries zero
  items. It was deliberately *not* registered as `urls.feed`, because
  `source_url()` prefers feed over index and would aim the poller at a
  door yielding nothing while the material sits on the index. Phase 5's
  "35 advertise no feed" should read **no *usable* feed**.
- **BLS is not a URL fix and is in no phase.** It publishes ~55 feeds,
  none agency-wide — ~42 per-program release feeds plus data rollups.
  `empsit.rss` is Atom with guids, dates and real release links; genuinely
  ingestible. Fixing `bls-news` needs a **fan-out to one registry entry per
  program feed** (empsit, cpi, ppi, jolts, eci first) or a multi-feed
  adapter. That is a new-source decision requiring the operator, not a
  correction.
- **Reading a publisher's own documentation may need our own client.**
  `bls.gov`, `dni.gov`/`odni.gov` and `ed.gov` all answer 403 to generic
  research fetchers but 200 to `AgencyClient`. GUIDE §3's
  continued-engagement step therefore runs through the project's identified
  client, not a browser-shaped one.

Original scope, for the record: Interior, Education, BLS, ODNI. Find each publisher's current address from its
own documentation, update `urls` in `sources/registry.yaml`, re-probe with
`scripts/check_sources.py --ids …`, record the dated finding in `notes`,
regenerate `SOURCES.md` in the same commit (code-standards §7.5). Cheapest
possible recovery — do it first.

## Phase 2 — `xml-index` adapter + roll-call votes — SENATE SHIPPED 2026-07-31

**Status:** `SenateVotesAdapter` built and `senate-xml` activated; live run
ingested 8 votes for 10 agency requests (robots + index + 8 records).
**House deferred:** the plan assumed an XML index. It is not one —
`clerk.house.gov/evs/2026/index.asp` is a 7 KB HTML `<TABLE>` of the ~15
most recent votes linking to `cgi-bin/vote.asp`, `index.xml` 404s, and
`clerk.house.gov/Votes` is a 249 KB JavaScript application. The per-vote
`roll<NNN>.xml` files are real (82 KB, full member positions) and the host
publishes no robots.txt at all, so the House is blocked on the Phase 5
`html-index` adapter, not on the publisher. `house-clerk-votes` stays
`planned` with that finding recorded. Two other plan assumptions moved:
the collection is an ADAPTER attribute rather than a registry field (a
registry field would need `sources.OPTIONAL_FIELDS` to change, which this
plan defers to Phase 5, and would let an entry declare a collection its
adapter does not produce), and no rule was added to `rules.py` — votes
follow the AGENCYPR precedent of rendering from `extracted_texts` at zero
LLM cost, so `VOTES-SEL-01`/`VOTES-EX-01` live in `report.RULE_DESCRIPTIONS`
only. Putting them in `rules.RULES` would route every vote through the
analyze layer for a summary the published record already states.

**New collection `VOTES`** — these are not agency announcements, and
`_store_item` (`agencies.py:204-239`) hard-codes `collection='AGENCYPR'`.
Parameterise it from the entry, defaulting to `AGENCYPR` so nothing else moves.

**Adapters:** `SenateVotesAdapter`, `HouseVotesAdapter` in `agencies.py`;
register in `ADAPTERS` (`:151`) **and** `sources.WEB_ADAPTERS`
(`src/fapd/sources.py:50`) or the drift test
`test_web_adapters_match_agencies_registry` (`tests/test_sources.py:253`) fails.

- `items()`: parse the vote menu/index XML, yield one item per vote —
  `title` = question/issue, `link` = per-vote XML URL, `guid` = vote number,
  `claimed_date` = vote date. **Date format matters**: `report._claimed_day`
  (`report.py:404`) parses RFC 822 or an ISO-prefixed string only; anything
  else silently dates the item by observation.
- `wants_article()` → `True`; `extract_text()` parses the per-vote XML into
  prose (question, result, tallies), defensively, never returning blank — the
  loop degrades blanks to `extract-fallback` (`agencies.py:335`).
- Apply the lookback bound inside `items()`.

**Digest integration** (operator decision: append as §7, no renumbering):

| Touch point | File:line |
|---|---|
| `VOTES-SEL-01/02` in `RULES` **and** `_MATCHERS`, same order | `src/fapd/rules.py:46-89`, `:157-167` (assert at `:169`) |
| Reader-facing rule text | `report.RULE_DESCRIPTIONS:40-60` (KeyError at `:1012` if missing) |
| `_votes_lines()` modelled on `_plaw_lines` | `report.py:844-863`; call from `render` `:1436-1448` after `_agency_lines` |
| The three collection tuples | `report.py:257`, `:1000`, `:1234` |
| `_coverage` block assigning `excluded`/`counted`/`rules` | follow the PLAW block, `report.py:308-311` |
| Section key, branch tag, live-page labels | `compose.SECTION_KEYS:147-157`, `tags.SECTION_BRANCH:18-28`, `publish._TODAY_COLLECTION_LABELS:1769` |
| Heading list, template | `tests/test_report.py:209`, `digests/TEMPLATE.md` |

Coverage arithmetic must reconcile — `report.py:1247-1252` raises otherwise,
and that is a publication-blocking gate.

## Phase 3 — `api` adapter (**revised 2026-07-31**)

**Operator decision, 2026-07-31: public-inspection documents are out of
scope.** "Don't fold the filed docs into the FR count, let's work with
published docs only." That settles the open question by removing it: the
Coverage Statement continues to state exactly what the government
published, and nothing filed-but-unpublished enters it. The
`fr-public-inspection` adapter is therefore **not built**, and the
Federal Register API adds nothing we do not already receive through the
govinfo FR collection.

**The api adapter's first target becomes Congress.gov**, which adds
legislative material we genuinely lack rather than duplicating what we
have.

**Congress.gov** reuses the adapter with a key — already in `.env` as
`GOVINFO_API_KEY`, verified against `api.congress.gov/v3` on 2026-07-31. It
must ride through `AgencyClient.get(url, params=…)` so the key is redacted in
the fetch log (`_redacted_params`, `client.py:275-276`); GUIDE §4 requires it.
Ship FR public inspection first; Congress.gov is a second registry entry
against the same adapter.

## Phase 4 — DCPD (independent of the adapter work)

Presidential documents through the existing govinfo sync path; the registry
entry `govinfo-dcpd` already exists (`sources/registry.yaml:112-124`).

1. `config.COLLECTIONS` (`config.py:141`) — append `"DCPD"`.
2. `sync._FORMAT_PREFERENCE_BY_COLLECTION` (`sync.py:26`) — add a DCPD entry if
   `xmlLink` is absent from its summary payload. Leave `_GRANULE_COLLECTIONS`
   and `_GRAPHICS_COLLECTIONS` alone (one document per package, no GIDs).
3. New `src/fapd/parsers/dcpd.py` with `parse(raw_path, package)` yielding the
   eight-key record — **copy `src/fapd/parsers/plaw.py` as the template**, it
   is the simplest complete parser. Register at `extract._PARSER_MODULES:24-30`.
4. Rules, `RULE_DESCRIPTIONS`, `_dcpd_lines()`, the three coverage tuples,
   `SECTION_KEYS`, `SECTION_BRANCH` — same table as Phase 2.
5. Registry → `active`, regenerate `SOURCES.md`, update the hard-coded active
   set and Tier-1 count (`tests/test_sources.py:55-73`, `:99-108`).
6. Corpus: `tests/conftest.py` `seed_corpus` + `EXPECTED_RULES`, and
   `tests/test_rules.py` exclusion-key expectations.

## Phase 5 — `html-index` adapter (35 sources) — gated

Highest unlock, highest cost. **Do not start until the request-budget question
is settled**: 35 sources fetching an index plus article pages materially
changes daily load, and the agency class hit 500/500 on 2026-07-31.

When it proceeds: `items()` extracts `(title, link, date)` from a listing page
heuristically (anchors inside repeated article/li structures) with an optional
per-source CSS selector in the registry — which needs a new optional field, so
`sources.OPTIONAL_FIELDS` (`sources.py:20`) changes first, because unknown
fields are rejected (`sources.py:90-92`). Build against the bytes the probe
already captured in `data/captures/` (`docs/adding-sources.md:67-71`) rather
than fetching live.

## Governance gates (first, per GUIDE §10)

- **GUIDE §3**: add `VOTES` (and DCPD) to the collections/scope list.
- **GUIDE §2**: the new digest section, and the public-inspection labelling
  decision. Adding a section is a GUIDE change, not a tweak.
- **`docs/code-standards.md` §1**: add the `items()` seam row, same commit.
- **`docs/adding-sources.md`**: document `items()` in the adapter table
  (`:43-48`) and the lookback obligation.
- **`CLAUDE.md` §9**: record that index adapters must bound their lookback.
- **Branching** (`CLAUDE.md` §8): one branch per phase —
  `arch/adapter-items-seam`, then `feature/…` per phase; CI green before each
  fast-forward merge; never mix registry/code commits with evidence paths.

## Invariants that must not break

- `SourceAdapter.stable_id`'s default is **frozen byte-for-byte** — 67 of 231
  stored documents depend on it (`agencies.py:25-55`). Changing it re-mints
  package ids and re-ingests history as duplicates.
- Never bypass `AgencyClient`: robots, pacing, budgets and the fetch log are
  enforced there, and GUIDE §4 says nothing may bypass logging.
- `stable_id` and `fallback_text` must not raise; `extract_text` may (it
  degrades) but must never silently return blank.
- Modes are disclosed per item and never laundered into `full`.
- Do not write a `channel` key in agency metadata — `collect.py:32-36` uses its
  absence to distinguish web from email.
- Publication days are Eastern, observation stamps UTC (`sync.publication_date`).

## Verification

Per phase, in order:

1. `uv run ruff check src/ scripts/ tests/` and `uv run pytest -q` — green.
2. Probe before activating: `uv run python scripts/check_sources.py --ids <id>`
   (`--ids` bypasses the type filter, so it already works for xml-index and api
   entries); read `data/probe/<date>/<id>.json`.
3. Registry drift: `uv run python scripts/sources_doc.py`, then
   `test_sources_md_in_sync_with_registry` and
   `test_registry_seeds_expected_active_sources` pass.
4. End-to-end on this machine, off the server budget:
   `uv run python scripts/ingest_agencies.py --ids <id>`, then inspect
   `extracted_texts` for `mode`, `char_count`, `claimed_published_at`.
5. Render: `uv run python scripts/digest.py --date <today>` — the new section
   appears, the Coverage Statement reconciles (it raises otherwise), citations
   resolve.
6. Deploy only after a green local render; the VPS gate in `CLAUDE.md` §12
   applies.

## Open items for the operator

1. ~~Public-inspection counting (Phase 3)~~ — **settled 2026-07-31**: out of
   scope, published documents only. The FR count states what was published.
2. Phase 5 budget: 35 html-index sources against a class budget that hit its
   ceiling on 2026-07-31.
3. regulations.gov needs its own key registration — an operator action; its
   documentation does not sanction reusing the api.data.gov key.
4. **BLS fan-out (new, from Phase 1)** — one registry entry per program feed,
   or a multi-feed adapter? ~55 feeds exist, none agency-wide. Needs an
   operator decision on how many programs are in scope before any code.

# Plan — acting on the MCP field report (2026-09-14)

*Status: **Wave A in progress since 2026-09-14** (operator: "Begin"); Waves B and C wait. Follows
[plan-task-template.md](plan-task-template.md). Parent:
[plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md)
(Phase 5 complete 2026-09-14). Last reviewed: 2026-09-14.*

## 0. Pre-launch evaluation (2026-09-14)

Before launch the plan was checked task by task against the code, the
live service and the published data. The first draft had six defects;
each is corrected below, and the evidence is kept here so the next
reader can see why the plan changed.

| # | Draft said | Found | Correction |
|---|---|---|---|
| E1 | MF-10: publish atomically by building a new tree and swapping a `current` symlink | Three breakages. **(a)** `static_mcp.handlers.Store.__init__` resolves its root once (`Path(root).resolve()`), so after the first swap every file resolves outside that root: containment errors or not-found on every MCP request. **(b)** `evidence-commit.sh` runs `git add … site/` on the same volume, so the symlink and the build trees would enter the repository. **(c)** `build_today` and the render worker rewrite single files every cycle; a whole-tree swap races them and loses writes | Replaced by **per-file atomic writes** (write a dot-temp in the same directory, `os.replace`). Publication-only, no infrastructure change, moves to Wave C |
| E2 | MF-2: give `text_file` results a `structuredContent` holding the file text | Duplicates the payload. The largest digest (2026-08-06) is 244,712 bytes, 249,083 JSON-escaped; twice that is **498,166 bytes against the 524,288-byte result cap** — the next larger digest would fail. The payload-first order alone fixes the failure the report describes | `text_file` and `static_text` stay content-only. `outputSchema` only on tools that already return structured content |
| E3 | MF-4: add `published_day`, sourced "from `package_id`" | "Publication day" is this project's name for the **digest day** (GUIDE §3), which is the `date` field; the new field would contradict the glossary. GUIDE §3's own words for this value are "the document's own date". `package_id` carries a date only for FR and CREC; the stored value is `packages.date_issued`, which the listing query (`collect.today_status`) does not join today | Field named **`document_date`**; sourced from the publisher stamp (`claimed_day`) when present, else `packages.date_issued` via a join added to `today_status` |
| E4 | MF-1: "the agents page section regenerates from the manifest (no edit)"; "the pattern forbids `/`" | The "No search … filter on a named collection" sentence is hand-written prose in `publish._mcp_agents_md`, pinned by a test. The draft's pattern *does* allow `/`; the package's path-probe rule applies only to parameters used in file templates, which `agency` is not | Files list gains `publish.py`, its test, and the live-day skill; the false sentence removed |
| E5 | Versions: "1.1.0 not yet" for Wave A; 1.1.0 for Wave B | Wave A adds optional inputs and narrows `collection` (a behavior change); Wave B changes result order, which breaks any client that reads content by position (our own rehearsal row M3 does) | **Wave A → 1.1.0, Wave B → 2.0.0**, the registry re-published after each so the card and the listing never disagree |
| E6 | MF-6: section slugs "to be read off a real digest"; MF-8: collection set "verify" | Read now. Digest level-2 headings: a header block before `## Contents`, `Contents`, `Day in Review` (when composed), `1.`–`9.`, `Terms Used Today`, `Coverage Statement`, `Methodology`. Collections: `config.COLLECTIONS` (CREC, BILLS, FR, USCOURTS, PLAW) plus the adapters' `COLLECTION` attributes (AGENCYPR, BILLACTIONS, PRESACT, VOTES) | Both written into the tasks, each with a drift test against its source |

Facts confirmed that the plan relies on, all 2026-09-14:

- **The agency filter will answer the report's question.** Federal
  Register items carry `agency` in upper case
  (`ENVIRONMENTAL PROTECTION AGENCY`), agency releases carry the source
  name (`NASA News Releases`), and `facets.tags` lists both in lower
  case. A case-insensitive exact match makes a facet value usable
  verbatim. Today's live file has five EPA items, all Federal Register.
- **`facets` exists in both files** the two listing tools read:
  `today.json` (1,789 bytes) and `day/<date>.json` (288 bytes on a
  court-heavy day).
- **Writes are in place today:** `build_site` never deletes and writes
  through 29 `write_text`, 3 `write_bytes` and 3 `shutil.copy2` calls;
  `write_text` truncates before writing, so a reader can get a short or
  empty file. That is the real mechanism behind F10; the report's
  "200 carrying a 404 body" remains unexplained and unreproduced.
- **nginx refuses dotfiles** outside `.well-known`
  (`location ~ /\.(?!well-known(/|$)) { return 404; }`), and the MCP
  `file_listing` regex is anchored on `\.json$`, so dot-temp files named
  `.<name>.tmp-…` are never served or listed.
- **Considered and not added:** compact JSON in the text twin of
  structured results saves 12% on a 100-item page — below the bar for a
  second result-format change.
- **Baseline:** `main` at d9bb279, `uv run pytest -q` → 1,389 passed,
  1 skipped.

## 1. Why this exists

On 2026-09-14, hours after the MCP service went live, an outside coding
agent used it end to end from discovery to a real research question
("what did EPA publish this week") and wrote a field report with ten
findings (the operator's private research tree,
`research/Cloudflare_Access/FAPD MCP Field Report.html`). Each was
verified against the live endpoint the same evening: eight valid, two
not what they claim. The operator asked for all ten to be handled, the
invalid ones by a recorded dismissal.

The headline number is the one to fix: one ordinary agency question
took **about 90 requests and 12 MB**, because the listing tools filter
on one collection only. The quiet observation matters as much: the
disclosure block comes first in every result, and a client that reads
only the first block reported the digests as empty.

## 2. Findings, verdicts, and the task that answers each

| # | Finding (shortened) | Verdict (verified 2026-09-14) | Task |
|---|---|---|---|
| F1 | No agency or tag filter; no cross-day query | **Valid.** Items carry `agency`; both listing files publish `facets`, which the tools drop | MF-1; MF-11 defers the cross-day tool |
| F2 | Disclosure first, payload second; no structured content for `get_digest` | **Valid.** Preamble is `content[0]` by the package's own spec (A.3.3) | MF-2 |
| F3 | The advertised 2026-07-28 `server/discover` answers `-32601` | **Dismissed as a bug.** The request lacked the 2026-07-28 request form (`params._meta` version, client info and capabilities; `MCP-Protocol-Version` and `Mcp-Method` headers). Without them it is a legacy-era request, under which the method does not exist; with them it answers 200. **Valid as friction:** the message does not say so | MF-3 |
| F4 | Federal Register items have no day | **Valid.** `claimed_*` are the agency-release dating fields; nothing carries the document's own date for govinfo items | MF-4 |
| F5 | Nothing steers from the digest to the day listing | **Valid.** | MF-5 |
| F6 | The digest is one blob; no section fetch | **Valid.** Largest digest 244,712 bytes | MF-6 |
| F7 | The home page never says "MCP" | **Valid.** | MF-7 |
| F8 | An unknown `collection` returns an empty success | **Valid.** `collection: "EPA"` → 0 items, no error | MF-8 |
| F9 | `list_sources` ships hourly activity buckets | **Dismissed.** A 50-item page is 80,739 bytes with thirteen identity and health fields per source and no `daily_activity`; the reviewer most likely read the `sources.json` resource, which is the whole file by design | MF-9 |
| F10 | A 200 carrying a 404 body during a publish | **Mechanism valid** (in-place truncating writes); the exact symptom unreproduced | MF-10 |

The report also confirms, without saying so, that ~90 POSTs from one
address in twenty minutes drew no 429 and no ban, and that the honesty
labels did their job in the reviewer's own words.

## 3. Governance, versions, gates

- **GUIDE §2a rule 4** bounds `/mcp` to reads of published files, with
  "a search index" named as a widening that needs a ruling. MF-1 is an
  equality match on a field the file carries; MF-6 is a heading-bounded
  slice of the same bytes. Neither is a search index or a model call;
  no GUIDE amendment. The deferred cross-day tool (MF-11) reads many
  files per request and is recorded as a future ruling.
- **GUIDE §3 clocks:** MF-4 adds a display field named in GUIDE's own
  words and changes no filing; `digest_day` stays write-once.
- **MCP surface versions** (manifest `server.version`, which the server
  card and the registry carry): Wave A **1.1.0** (additive inputs, the
  collection enum); Wave B **2.0.0** (result order). The operator
  re-publishes the registry listing after each deploy: log in again if
  the token has expired, regenerate `server.json` with `static-mcp
  registry-json`, `mcp-publisher publish` from `secrets/mcp-registry/`.
- **VPS gates (CLAUDE.md §13):** every wave's deploy waits for the
  operator's "deploy" in the session. The laptop's Docker daemon is
  down, so Waves B and C, which change rehearsal rows or the nginx
  `Link` header, run `rehearse.sh` on the box as on 2026-09-14 — that
  needs the operator's VPS-testing approval again. No deploy between
  03:30 and 06:00 UTC.
- **Security posture:** new parameters pass the existing validation
  layer (patterns, enums, ceilings); MF-6 reads under the same
  containment; MF-10 changes how bytes land, not what is served. The
  security review's threat table is re-read at the end.
- **Sections touched:** Operations (package, manifests, nginx include,
  `collect.today_status`), Publication (`publish.py`, skills, schemas),
  Editorial none. Performed in the main session (operator direction,
  2026-09-14). Package commits stay separate from FAPD commits so
  `packages/static-mcp/` remains free of project strings (pinned).
- **Commits:** one trailer, `Co-Authored-By: Claude <the model writing
  the commit> <noreply@anthropic.com>`; no session line (operator's
  standing rule).

## 4. Tasks

IDs `MF-n`. Each task: why, files, diff sketch, justification,
alternatives, risk, verification, rollback, dependencies.

### MF-1 — Agency filter and facets on the listing tools (F1)

- **Why:** "what did agency X publish" costs ~90 requests today.
- **Files:** both manifests; package `handlers.py` (`_apply_filters`),
  `manifest.py` (`_parse_filters`), `README.md`, package tests;
  `src/fapd/publish.py` (`_mcp_agents_md` "No search" bullet);
  `tests/test_mcp_manifest.py`, `tests/test_mcp_surfaces.py`;
  `docs/site/agent-skills/fapd-live-day/SKILL.md` (step 9);
  `docs/mcp-server.md`.
- **Diff sketch:**
  - Manifest: global param `agency` — `string`, pattern
    `^[^\x00-\x1f\x7f]{1,120}$` (any printable characters: registry
    source names carry an em dash and a plus sign, and the value only
    ever feeds an equality compare, never a path), description "Keep
    only items whose agency equals this whole value, ignoring case; take
    it from `facets.tags` or `items[].agency`".
    `get_live_day` and `get_day_listing` gain `agency` (optional) and
    the filter `{"param": "agency", "match_field": "agency",
    "case_insensitive": true}`; both `envelope` lists gain `"facets"`.
  - Package: `_parse_filters` accepts optional boolean
    `case_insensitive` on `match_field` (added to its `_require_keys`
    set; default false); `_apply_filters` compares `casefold()` values
    when set and both sides are strings.
  - Page prose: "No search. The tools list and page, filter on a
    collection or an exact agency name, and fetch by date or source id."
  - Skill step 9 names `agency` and `facets.tags`.
- **Justification:** the field exists and is mechanical; `match_field`
  is an existing handler option, so the change is one flag. Case is
  ignored because Federal Register agencies are upper case and the
  facets lower case.
- **Alternatives:** filter on `tags` (a list; a new `match_list` kind,
  more code for the same answer); substring match (a search, §2a).
- **Risk:** additive; the corpus and fuzz tests cover the new argument.
  An agency with no items returns `total: 0`, and `facets` tells the
  agent what is present.
- **Verification:** package tests (case-insensitive match; flag refused
  on `exclude_where`; flag refused on a non-string param); a test that
  every registry source name and every agency value in the fixture
  build matches the pattern;
  `test_mcp_manifest.py` calls both tools with `agency` on the fixture
  and asserts `facets` is present; live, recorded in the WORKLOG next
  to the report's 90: the EPA question as seven `get_day_listing` calls
  plus one `get_live_day`, request count and bytes.
- **Rollback:** remove the param, filter and envelope key; the package
  flag is inert unused.
- **Dependencies:** none.

### MF-2 — Payload first; output schemas where results are structured (F2)

- **Why:** a client reading `content[0].text` gets the disclosure and
  fails silently.
- **Files:** package `handlers.py` (`_finish`, the `text_file` and
  `static_text` branches of `run_tool`), `dispatch.py` (tool definitions
  emit `outputSchema`), `manifest.py` (generate the schema per handler
  shape), `README.md`; package tests `test_protocol_modern.py` (lines
  73, 93), `test_protocol_legacy.py` (62), `test_handlers.py`, the era
  transcripts; `tests/test_mcp_manifest.py` (lines 183–211);
  `deploy/vps/nginx/rehearse.sh` row M3 (reads `content[1]`);
  both manifests (`server.version` 2.0.0); `docs/mcp-server.md`
  (result shape, changelog).
- **Diff sketch:**
  - Every result: payload block(s) first, the preamble as the **last**
    text block.
  - `outputSchema` (JSON Schema, `additionalProperties: true`) on tools
    whose handler returns `structuredContent`, generated from the shape
    the handler already produces: paged list → envelope keys, `items`
    (array), `offset`, `limit`, `total`, `next_offset`, optional
    `truncated` and `truncation_note`; found item → envelope keys,
    `item` (object); whole document → object; `file_listing` → `items`
    (array of strings) with the same paging keys.
  - `text_file` and `static_text`: no `structuredContent`, no
    `outputSchema` (E2).
  - Every tool description gains, before the data sentence: "The
    payload is the first content block; a disclosure, when present, is
    the last."
- **Justification:** the order is what the report's failure needs; the
  schemas describe structured content that already exists; duplicating
  text would push busy digests to the result cap.
- **Alternatives:** document the old order only (the report shows
  descriptions are not read before parsing); move the preamble into
  `_meta` (older clients drop unknown `_meta`; the preamble carries the
  citation rule and must stay visible).
- **Risk:** a breaking change for position-reading clients, hence
  2.0.0; `isError` results carry no `structuredContent` — confirm
  before release that a client validating `outputSchema` (MCP
  Inspector, which uses the TypeScript SDK) accepts an error result
  without it, and record what was observed.
- **Verification:** package tests for order and schemas (the schema
  validated by the repository's stdlib schema-subset validator against
  real results); `test_mcp_manifest.py`: `get_digest` block 0 begins
  `# Daily Digest`, the last block is the preamble; rehearsal M3
  updated and green on the box; live: Claude Code and MCP Inspector
  calls repeated, including one `isError` case, and recorded.
- **Rollback:** revert the package commit; version back to 1.1.0.
- **Dependencies:** Wave A merged (shares the manifests).

### MF-3 — Dismiss F3 as a bug; make the error say why (F3)

- **Why:** the method exists; the message should name the missing
  request form.
- **Files:** package `dispatch.py` (`_not_found_method`), package tests
  (one corpus entry), `README.md`; `src/fapd/publish.py`
  (`_mcp_agents_md` protocol bullet); `docs/mcp-server.md`.
- **Diff sketch:** when the era is legacy and the method is in the
  modern-only method set, keep status 200 and `-32601`; the message
  becomes "server/discover is a 2026-07-28 method: send
  params._meta with io.modelcontextprotocol/protocolVersion,
  clientInfo and clientCapabilities, and the MCP-Protocol-Version and
  Mcp-Method headers"; `data: {"supported": [...]}`. Page bullet gains:
  "a request without them is answered under the older revisions".
- **Justification:** message text is free under the spec; answering a
  legacy request with a modern result would misstate the era.
- **Risk:** none.
- **Verification:** the report's exact request → 200, `-32601`, message
  names `params._meta`; the spec form still 200 with a result.
- **Rollback:** revert. **Dependencies:** none.

### MF-4 — `document_date` on every listing item (F4)

- **Why:** an agent had to parse a package id to date a Federal
  Register item.
- **Files:** `src/fapd/collect.py` (`today_status`: `LEFT JOIN packages
  p USING (package_id)`, select `p.date_issued`); `src/fapd/publish.py`
  (`build_today` item rows, `_TODAY_LABELS`, `_today_schema`);
  `tests/test_publish.py`, `tests/test_agent_discovery.py` (schemas
  validate real files); `docs/site/agent-skills/fapd-live-day/SKILL.md`
  ("Fields worth knowing"); `docs/mcp-server.md`.
- **Diff sketch:** `document_date` (`YYYY-MM-DD` or null) =
  `claimed_day` when present (the publisher's stamp), else the first ten
  characters of `date_issued` when it parses as a date, else null. Label:
  "the document's own date as its source gives it (govinfo's issued
  date; an agency's stated release date) — GUIDE §3; `date` is the
  digest day, which for most collections is the day we first observed
  the item". Schema: optional, nullable (frozen day views written before
  the change do not carry it, and frozen files are never rewritten).
- **Justification:** GUIDE's words, the stored value, no re-dating;
  `claimed_*` unchanged.
- **Alternatives:** document the `package_id` convention (not a field;
  absent for USCOURTS and BILLS).
- **Risk:** the extra join is on the primary key; a test pins the query
  plan does not scan (or simply the row count is unchanged on the
  fixture).
- **Verification:** one fixture item per collection with the expected
  date; the schema validates `today.json`; live `get_live_day` shows the
  field on a Federal Register item.
- **Rollback:** revert. **Dependencies:** none.

### MF-5 — Which tool answers which question (F5)

- **Why:** the digest is "the record", so agents reach for it and miss
  the counted-only items.
- **Files:** both manifests (`server.instructions`; `get_digest` and
  `get_day_listing` descriptions); `src/fapd/publish.py`
  (`_mcp_agents_md`: a third captioned table, `_MCP_TABLE_CAPTIONS`);
  `tests/test_mcp_surfaces.py` (lines 175 and 181 pin two tables →
  three); `docs/mcp-server.md`; both MCP-aware skills.
- **Diff sketch:** instructions gain: "The digest summarizes a
  rule-selected subset and counts the rest. For every item an agency or
  collection published on a day, use get_day_listing (finished days) or
  get_live_day (today); the digest's Coverage Statement says what was
  counted only and why." `get_digest` gains the first sentence. The
  table: question → tool (four rows).
- **Risk:** none; descriptions pass the hidden-instruction scan.
- **Verification:** manifest and page tests. **Rollback:** revert.
- **Dependencies:** none; ships in Wave B so descriptions change once.

### MF-6 — `get_digest` section slicing (F6)

- **Why:** an agent wanting one section pays for the whole digest.
- **Files:** package `handlers.py` (`text_file` gains an optional
  section map), `manifest.py` (validate it), `README.md`, package tests
  (fixture Markdown); both manifests; `tests/test_mcp_manifest.py`;
  `docs/mcp-server.md`.
- **Diff sketch:** handler option `sections: {"param": "section",
  "level": 2, "map": {"header": null, "contents": "Contents",
  "day-in-review": "Day in Review", "1": "1. ", …, "9": "9. ",
  "terms": "Terms Used Today", "coverage": "Coverage Statement",
  "methodology": "Methodology"}}`. A value selects the level-2 heading
  whose text starts with the mapped prefix and returns the lines up to
  the next heading of level 2 or level 1, verbatim; `header` (null)
  returns the text before the first level-2 heading, which holds the
  Inference row. Headings inside fenced code blocks are ignored. The
  `section` parameter's schema is an enum of the map's keys (MF-8's
  enum support). The result-size check applies to the slice. A missing
  section on a given day (no Day in Review) returns `isError` naming
  the sections present.
- **Justification:** a slice of the same file keeps the verbatim
  guarantee; a prefix map keeps the package generic.
- **Alternatives:** per-section files (multiplies the published tree
  for one consumer).
- **Risk:** the renderer's headings become an interface; a test renders
  a fixture digest with `report.py` and asserts every map entry is
  found, so a renamed section fails the build.
- **Verification:** package tests on fixture Markdown (with a fenced
  block containing `## `); the FAPD manifest test slices `coverage` and
  `header`; live: `section: "coverage"` returns a few kilobytes.
- **Rollback:** remove the param. **Dependencies:** MF-8 (enum type).

### MF-7 — Every page names the MCP service (F7)

- **Why:** a summarizing fetch of the home page reported no MCP
  service.
- **Files:** `src/fapd/publish.py` (`_PAGE` shell: a head link and a
  footer line, both filled only when the manifest exists);
  `tests/test_agent_discovery.py` (head links), `tests/test_publish.py`
  (footer); `deploy/vps/nginx/fapd-discovery-headers.inc`;
  `tests/test_web_conf.py::test_link_header_matches_the_master_plan_contract`;
  the master plan §8.3 contract (dated amendment first);
  `docs/accessibility.md` not needed (existing page class).
- **Diff sketch:** head `<link rel="service-desc"
  type="application/mcp-server-card+json" href="mcp/server-card">`
  (rebased on subdirectory pages); footer paragraph "AI agents: a
  read-only <a href="agents.html#mcp">MCP service</a> answers at
  `https://fapd.info/mcp`."; `Link` header gains
  `</mcp/server-card>; rel="service-desc"; type="application/mcp-server-card+json"`.
- **Justification:** the shell is shared, so every page an agent lands
  on says it, not only the home page; the link text makes sense out of
  context (accessibility doctrine: read before any HTML change).
- **Risk:** the head-links-equal-header test must change in the same
  commit; RFC 8288 allows two `service-desc` links of different types.
- **Verification:** `curl -sI https://fapd.info/ | grep -i '^link'`
  shows six relations; the home page HTML contains the footer line;
  rehearsal rows 1 and 23 on the box.
- **Rollback:** revert. **Dependencies:** none.

### MF-8 — `collection` becomes an enum (F8)

- **Why:** a guessed collection name gets an empty page instead of a
  correction.
- **Files:** package `manifest.py` (`ParamSpec.enum`; `_parse_param`
  accepts `enum` for strings, each value must satisfy the pattern;
  `schema()` emits it; `validate_value` refuses a non-member with
  `-32602` naming the parameter and listing the allowed values — values
  that are ours, not the client's), `card.describe_markdown` ("one of:
  …"), `README.md`, package tests; both manifests;
  `src/fapd/publish.py` (`_mcp_tool_rows` renders the enum identically —
  the drift test compares them); `tests/test_mcp_manifest.py` (drift:
  the manifest enum equals `config.COLLECTIONS` plus every `COLLECTION`
  attribute in `agencies.py` and `email_sources.py`).
- **Diff sketch:** `collection.enum` = `["AGENCYPR", "BILLACTIONS",
  "BILLS", "CREC", "FR", "PLAW", "PRESACT", "USCOURTS", "VOTES"]`.
- **Justification:** the set is fixed by code, so the schema can say so.
- **Alternatives:** `isError` on zero matches (an empty day for a real
  collection is a true answer).
- **Risk:** a new collection without a manifest update fails the drift
  test — intended.
- **Verification:** package tests; live `collection: "EPA"` → `-32602`
  listing the nine values.
- **Rollback:** remove `enum`. **Dependencies:** none.

### MF-9 — Dismiss F9; say what `list_sources` returns (F9)

- **Files:** both manifests (`list_sources` description: "A summary per
  source: identity, method, status and health. get_source returns the
  full record, including daily activity; the sources.json resource is
  the whole file."); `docs/mcp-server.md`; the WORKLOG dismissal with
  the measured page.
- **Verification:** manifest checks pass. **Dependencies:** none.

### MF-10 — Atomic file writes for the published site (F10)

- **Why:** a reader during a rebuild can get a truncated file, and
  agents treat a 200 as truth.
- **Files:** `src/fapd/publish.py` (a helper pair
  `_atomic_write_bytes(path, data)` / `_atomic_write_text(path, text)`;
  every `write_text`, `write_bytes`, `_dump_json`, `_write_twin` and the
  three `shutil.copy2` asset copies go through it); `.gitignore`
  (`site/**/.*.tmp-*`); `tests/test_publish.py`.
- **Diff sketch:** write to `path.parent / f".{path.name}.tmp-{pid}-{n}"`,
  flush, `os.replace(tmp, path)`; on error, remove the temp and
  re-raise. Asset copies: `shutil.copyfile` to the temp, then replace.
- **Justification:** `os.replace` on one filesystem is atomic, so a
  path is always either the old complete file or the new one. Temp
  names start with a dot (nginx refuses them) and do not end in the real
  extension (never listed by the MCP service); the ignore rule keeps a
  crash-left temp out of an evidence commit. The MCP JSON cache keys on
  modification time and size, so it refreshes on replace. No
  infrastructure change.
- **Alternatives:** the symlink tree swap (E1: breaks the MCP root,
  the evidence commit, and the per-cycle writers).
- **Risk:** during a rebuild, two related files (a digest and its twin)
  may briefly be from different builds; each is complete. Disk use
  grows by one file at a time.
- **Verification:** a test with a reader thread that repeatedly reads a
  file while a writer rewrites it a thousand times sees only complete
  old or new contents; a static test fails on any bare `.write_text(`,
  `.write_bytes(` or `shutil.copy2(` in `publish.py` outside the helper;
  full suite; after deploy, a health pass.
- **Rollback:** revert. **Dependencies:** none.

### MF-11 — Record the deferred cross-day tool

- **Files:** `docs/ops/ops-backlog.md` (OB-26).
- **Content:** the report's `find_items(from, to, collection, agency)`;
  the GUIDE §2a ruling it needs (one request reading up to 31 day files,
  capped); the trigger (an agent still needing more than ten requests
  for an agency-week after MF-1).

## 5. Sequencing

| Wave | Tasks | Ships as | Operator steps |
|---|---|---|---|
| A | MF-1, MF-8, MF-3, MF-9, MF-11 — **deployed 2026-09-14** (package 0.2.0, surface 1.1.0, main 6c76115; the EPA question live in 8 requests / 117 KB, 23 items — DoD 1 met) | package change + manifests; surface **1.1.0** | "deploy"; registry re-publish |
| B | MF-2, MF-5, MF-6 — **built 2026-09-14** (package 0.3.0, surface 2.0.0; rehearsal on the box 42/0/1, M3 green; branch `feature/mcp-wave-b`) | package change + manifests; surface **2.0.0** | "deploy"; registry re-publish |
| C | MF-7, MF-4, MF-10 | Publication and Operations changes; no surface version change | VPS-testing approval (rehearsal rows 1 and 23); "deploy" |

Each wave: branch (`feature/mcp-wave-a` and so on) → tests → PR → CI →
fast-forward → deploy → live check → WORKLOG. Wave A's WORKLOG entry
carries the F3 and F9 dismissals with evidence.

## 6. Definition of done

1. The report's EPA question answered in eight requests (seven day
   listings and the live day), with bytes recorded beside the report's
   90 requests and 12 MB.
2. `content[0]` of every tool result is the payload; every structured
   tool declares an `outputSchema`; the surface is 2.0.0 and the
   registry lists it.
3. The report's exact `server/discover` request gets a message naming
   the 2026-07-28 request form.
4. `collection: "EPA"` is refused with the allowed values.
5. Every new listing item carries `document_date`.
6. Every page's head and footer, and the `Link` header, name the MCP
   service.
7. `get_digest` returns one section on request, including `header`.
8. No site write leaves a truncated file, proven by the concurrent-read
   test and the static scan.
9. F3 and F9 dismissed in the WORKLOG with evidence; OB-26 recorded.

## 7. Launch readiness (2026-09-14)

- `main` clean at d9bb279; baseline 1,389 passed, 1 skipped.
- Progress log: `research/agent-logs/mcp-field-report-orchestrator-20260914.md`
  (gitignored), START entry written; resume from its `NEXT:`.
- Performed in the main session; no sub-agents.
- Waiting on the operator: the go for Wave A. Later: "deploy" per wave,
  VPS-testing approval for Waves B and C while the laptop's Docker is
  down, the registry re-publish after Waves A and B.

## 8. Change log of this plan

- 2026-09-14 (later): pre-launch evaluation (§0) against the code, the
  live service and the data. MF-10 redesigned (symlink swap would have
  broken the MCP root, the evidence commit and the per-cycle writers);
  MF-2 narrowed (no duplicated text; the largest digest doubled sits
  within 26 KB of the result cap); MF-4 renamed and re-sourced
  (`document_date`, GUIDE §3 vocabulary; the join the query lacks);
  MF-1 files and pattern corrected; versions set (1.1.0, 2.0.0);
  section slugs and collection codes read off the code; Wave E folded
  into Wave C; launch readiness added.
- 2026-09-14: written from the verified findings; not started.

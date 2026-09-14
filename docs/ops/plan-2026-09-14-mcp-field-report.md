# Plan — acting on the MCP field report (2026-09-14)

*Status: **planned, not started** (operator: "generate a plan now … but
do not start work yet"). Follows [plan-task-template.md](plan-task-template.md).
Parent: [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md)
(Phase 5 complete 2026-09-14). Last reviewed: 2026-09-14.*

## 1. Why this exists

On 2026-09-14, hours after the MCP service went live, an outside coding
agent used it end to end from discovery to a real research question
("what did EPA publish this week") and wrote a field report with ten
findings (the operator's private research tree,
`research/Cloudflare_Access/FAPD MCP Field Report.html`). The
orchestrator verified each finding against the live endpoint the same
evening. Eight are valid; two are not what they claim. The operator
asked for all ten to be handled, the invalid ones by a recorded
dismissal. This plan is that handling.

The report's headline number is the one to fix: answering one ordinary
agency question took **about 90 requests and 12 MB**, because the
listing tools filter on one collection only and nothing spans a day.
The report's most useful observation is the quiet one: the disclosure
block comes first in every result, and a client that reads only the
first block reports the digest as empty.

## 2. Findings, verdicts, and the task that answers each

| # | Finding (report's words, shortened) | Verdict (verified 2026-09-14) | Task |
|---|---|---|---|
| F1 | No agency or tag filter; no cross-day query | **Valid.** Items carry a scalar `agency` and an agency tag; `today.json` publishes `facets.tags`, which the tool envelope drops | MF-1 (filter + facets); MF-11 records the cross-day tool as deferred |
| F2 | Disclosure block first, payload second; no structured content for `get_digest` | **Valid, by design that turned out wrong.** Preamble is `content[0]` (package spec A.3.3) | MF-2 |
| F3 | The advertised 2026-07-28 `server/discover` answers `-32601` | **Not a bug.** The reviewer's request lacked the 2026-07-28 request form (`params._meta` version + `MCP-Protocol-Version`/`Mcp-Method` headers). Without them the request is legacy-era, under which the method does not exist. With the spec form it answers 200, every check today. **Valid as friction:** the error is unhelpful | MF-3 (dismiss the bug; fix the message) |
| F4 | Federal Register items have `claimed_day` null | **Valid.** `claimed_*` are the agency-release dating fields; govinfo items carry their date only in `package_id`/URL | MF-4 |
| F5 | Nothing steers an agent from the digest to the day listing | **Valid.** | MF-5 |
| F6 | The digest is one 215 KB blob; no section fetch | **Valid.** Busy days approach the 512 KiB result cap | MF-6 |
| F7 | The home page never says "MCP" | **Valid.** | MF-7 |
| F8 | An unknown `collection` returns a normal empty result | **Valid.** `collection: "EPA"` → 0 items, 0 total, no error (verified) | MF-8 |
| F9 | `list_sources` ships hourly activity buckets | **Not true of the tool.** A 50-item page is 80 KB with thirteen identity/health fields per source and no `daily_activity` (verified). The reviewer likely read the raw `sources.json` resource, which is the full file by design | MF-9 (dismiss; one clarifying sentence) |
| F10 | Once: HTTP 200 with a 404 HTML body for `agents.md` during a publish | **Mechanism valid, symptom unverified.** The site is rebuilt in place, so a fetch during the rebuild can see a missing file; the "200 with a 404 body" cannot be reproduced or explained from the config | MF-10 |

Two things the report confirms without saying so: about 90 POSTs from
one address in twenty minutes drew no 429 and no ban, which is the
limit zone and the jail behaving as designed for an honest client; and
the honesty labels (`is_backfill`, `duplicate_of`, `summary_method`,
`day_context`, the coverage statement, the source records' stated
reasons for absence) did their job in the reviewer's own words.

## 3. Governance check

- **GUIDE §2a rule 4** bounds `/mcp` to reads of published files with
  no search index. MF-1's agency filter and MF-6's section slice are
  filters over stored files (an equality match on a field the file
  already carries; a heading-bounded slice of the same bytes). Neither
  is a search index or a model call. The MCP guide's "No search"
  sentence stays true and gains a clause saying what filtering means.
  No GUIDE amendment. The deferred cross-day tool (MF-11) *would* walk
  many files per request; it is recorded as a future ruling, not done.
- **GUIDE §6 r15 / the Inference row:** MF-4's `published_day` is
  mechanical (from `package_id` and the filing policy); no model.
- **Result-shape change (MF-2)** is a change to what real clients
  receive. It goes out as MCP surface **version 1.1.0** (manifest
  `server.version`), noted in `docs/mcp-server.md`'s changelog, and the
  registry listing is re-published by the operator (checkpoint C-4
  again: `mcp-publisher publish` from `secrets/mcp-registry/` with the
  regenerated `server.json`).
- **Security posture:** every new parameter goes through the existing
  validation layer (patterns, enums, ceilings); MF-6 reads the same
  file under the same containment; MF-10 changes how files land in the
  volume, not what is served. The security review's threat table is
  re-read at the end and amended only if a row changed.
- **Who performs:** the main session, per the operator's 2026-09-14
  direction (no fresh sub-agents; each costs the plan re-read). Package
  work and FAPD work are separate commits so `packages/static-mcp/`
  stays reusable and free of FAPD strings (pinned).

## 4. Tasks

IDs `MF-n` ("MCP field report"). Every task: why, files, diff sketch,
justification, alternatives, risk, verification, rollback, dependencies.

### MF-1 — Agency filter and facets on the listing tools (F1)

- **Why:** the most natural question an agent asks a government digest
  ("what did agency X publish") costs ~90 requests today.
- **Files:** `deploy/vps/mcp/fapd.manifest.json`, `deploy/dev/mcp/fapd.manifest.json`;
  `packages/static-mcp/src/static_mcp/handlers.py` (one filter option),
  `manifest.py` (validate it), `README.md`, package tests;
  `tests/test_mcp_manifest.py`; `docs/mcp-server.md`; the agents page
  section regenerates from the manifest (no edit).
- **Diff sketch:**
  - Manifest: a global param `agency` (`string`, pattern
    `^[A-Za-z0-9][A-Za-z0-9 .,'&()/-]{0,119}$`, description "Keep only
    items whose agency equals this, case-insensitively; see the
    `facets.tags` block for the agencies present"); `get_live_day` and
    `get_day_listing` gain `agency` (optional) and a filter
    `{"param": "agency", "match_field": "agency", "case_insensitive": true}`;
    both tools' `envelope` gains `"facets"`.
  - Package: `_parse_filters` accepts an optional boolean
    `case_insensitive` on `match_field` filters (default false);
    `_apply_filters` compares `str(value).casefold()` when set and the
    field is a string. README manifest reference documents it.
- **Justification:** the item field already exists and is mechanical;
  a `match_field` filter is the handler kind the package already has,
  so the change is one flag. Case-insensitive because agency names are
  typed by agents from memory. The pattern forbids `/`, `\`, `..`
  (validator rule) and keeps the value short.
- **Alternatives:** filtering on `tags` (a list; would need a new
  `match_list` kind — more code for the same answer); a free-text
  `contains` match (a search, ruled out by §2a).
- **Risk / blast radius:** none to existing calls (new optional param);
  the corpus and fuzz tests cover the new argument; an agency value
  with no matches returns an empty page with `total: 0` — MF-8's
  enum treatment does not apply (agencies vary by day), so the facets
  block is the agent's guide.
- **Verification:** package tests (new: case-insensitive match; case
  flag rejected on `exclude_where`); `tests/test_mcp_manifest.py`
  calls `get_live_day` with `agency` against the fixture and asserts
  the facets block is present; live: the EPA question in **≤ 8
  requests** (one `get_day_listing` per day with `agency`), recorded in
  the WORKLOG beside the report's 90.
- **Rollback:** remove the param and filter from the manifests; the
  package flag is inert when unused.
- **Dependencies:** none.

### MF-2 — Payload first; structured content and output schemas (F2)

- **Why:** a client that reads `content[0].text` gets the disclosure,
  not the data, and fails silently.
- **Files:** `packages/static-mcp/src/static_mcp/handlers.py`
  (`_finish`, `run_tool`), `dispatch.py` (tool definitions gain
  `outputSchema`), `manifest.py` (optional `output_schema` per tool;
  generated defaults per handler kind), `README.md`, package tests and
  transcripts; `deploy/vps/nginx/rehearse.sh` row M3 (reads
  `content[1]` today); `docs/mcp-server.md` (changelog, result shape);
  `deploy/vps/mcp/fapd.manifest.json` `server.version` → `1.1.0`;
  `tests/test_mcp_manifest.py`.
- **Diff sketch:**
  - Content order: payload block(s) first; the preamble becomes the
    **last** text block. (Not `_meta`: legacy clients drop unknown
    `_meta`; not an annotation: the spec's content annotations are
    audience/priority hints, not prose.)
  - `text_file` results gain `structuredContent`:
    `{"text": <the file>, "mime_type": …, "preamble": <or null>, "file": <relative name>}`,
    and for FAPD's `get_digest` the manifest-declared params are echoed
    (`{"date": …}`) so an agent can join results to requests.
  - Every tool definition carries `outputSchema` (JSON Schema for its
    `structuredContent`), generated from the handler kind: `json_file`
    page → `{items|<select>: array, total, offset, limit, next_offset, truncated?}`
    plus the envelope keys as free-form; `text_file` → the object
    above; `file_listing` → `{keys: array of string, total, …}`;
    `static_text` → `{text}`.
  - Every tool description ends (before the data sentence) with:
    "Result: the payload is the first content block; a disclosure
    sentence, if any, is the last."
- **Justification:** the spec's `structuredContent`/`outputSchema` pair
  exists for exactly this; putting the payload first serves the naive
  reader without hurting the careful one; keeping the preamble as a
  block (last) keeps it visible to clients that ignore structured
  content.
- **Alternatives:** keep first and only document it (rejected: the
  report shows documentation was not read before parsing); drop the
  preamble (rejected: it carries the citation rule).
- **Risk / blast radius:** every existing client that hard-coded
  `content[1]` (ours: rehearsal M3, the 4B real-client transcript
  notes) — updated in the same change; the MCP surface version bumps
  to 1.1.0 and the registry is re-published (operator).
- **Verification:** package tests (order, schema validity against the
  package's own schema-subset validator, transcripts regenerated);
  `test_mcp_manifest.py` asserts `get_digest` result: block 0 begins
  `# Daily Digest`, last block is the preamble, `structuredContent.text`
  equals the file; rehearsal M3 updated and green on the box; live:
  Claude Code and Inspector calls repeated and recorded.
- **Rollback:** revert the package commit; the manifest version returns
  to 1.0.0; the registry keeps 1.0.0 as latest if 1.1.0 was never
  published.
- **Dependencies:** none; ships in the same release as MF-3.

### MF-3 — Dismiss F3 as a bug; make the error say why (F3)

- **Why:** the method exists and answered correctly; a client that
  sends the modern method in the legacy request form deserves a
  message that names the missing form, not "Method not found".
- **Files:** `packages/static-mcp/src/static_mcp/dispatch.py`
  (legacy unknown-method path), `protocol.py` if the modern-only method
  set lives there, package tests (a corpus entry), README; the agents
  page's protocol-versions bullet gains one clause (generated in
  `publish._mcp_agents_md`); `docs/mcp-server.md` "How to connect".
- **Diff sketch:** when a legacy-era request names a method that
  exists only under a modern revision (`server/discover`), answer the
  same `-32601` with `message`: "server/discover exists under
  2026-07-28 only: send params._meta.io.modelcontextprotocol/protocolVersion
  = 2026-07-28 with clientInfo and clientCapabilities, and the
  MCP-Protocol-Version and Mcp-Method headers" and `data.hint` naming
  the agents page. Code and HTTP status unchanged (spec: unknown method
  under legacy → 200/-32601). Page text: "(2026-07-28 requests carry
  the version in `params._meta` and in the `MCP-Protocol-Version` and
  `Mcp-Method` headers; a request without them is answered under the
  legacy revisions)".
- **Justification:** the spec allows any message text; a hint costs
  nothing and turns a dead end into a correction. The finding's
  "bug" label is dismissed in the WORKLOG with the two request forms
  side by side as evidence.
- **Alternatives:** accept `server/discover` without `_meta` (rejected:
  the 2026-07-28 revision requires `_meta`, and answering a legacy
  request with a modern result would be a false claim of era).
- **Risk:** none; message text only.
- **Verification:** package test: the reviewer's exact request →
  200, `-32601`, message contains "params._meta"; the spec form still
  200 with a result.
- **Rollback:** revert.
- **Dependencies:** none.

### MF-4 — `published_day` on every day-listing item (F4)

- **Why:** an agent had to parse a package id to date a Federal
  Register item.
- **Files:** `src/fapd/publish.py` (`build_today`'s item assembly, the
  `labels` block, `_today_schema`), `tests/test_publish.py`,
  `tests/test_agent_discovery.py` (schema validation),
  `docs/site/agent-skills/fapd-live-day/SKILL.md` ("Fields worth
  knowing"), `docs/mcp-server.md`.
- **Diff sketch:** each item gains `published_day` (`YYYY-MM-DD` or
  null): for govinfo collections the package's `date_issued` (the
  document's own date, already stored — CLAUDE.md §9: `date_issued`
  remains the document's own date for display); for agency releases
  `claimed_day`; for email items the claimed day when present. A label
  explains it: "the day the publisher gives the document; filing is by
  observation day (`date`) — see the three clocks". The schema adds the
  property with that description. `claimed_*` fields are unchanged.
- **Justification:** one normalized field beside the source-specific
  ones, no re-dating of anything (GUIDE §3 filing is untouched; this is
  display data the page already knows).
- **Alternatives:** documenting the `package_id` convention (rejected:
  a convention is not a field).
- **Risk / blast radius:** `today.json` and `day/<date>.json` shapes
  gain a key; the frozen day views are written at EOD, so existing
  frozen files lack it until… they are not regenerated (frozen means
  frozen). The schema marks it optional-nullable; the label says frozen
  days before 2026-09-XX may omit it.
- **Verification:** unit test per collection; schema validates real
  files; live `get_live_day` shows the field.
- **Rollback:** revert; a frozen file with the key is harmless.
- **Dependencies:** none. Ships as a normal Publication change (no
  MCP version bump — the manifest is unchanged).

### MF-5 — Guidance: which tool answers which question (F5)

- **Why:** the digest is "the record", so agents reach for it first
  and miss the counted-only items in the day listing.
- **Files:** both manifests (`server.instructions`, `get_digest` and
  `get_day_listing` descriptions), `src/fapd/publish.py`
  (`_mcp_agents_md`: a small captioned table "Which tool for which
  question"), `tests/test_mcp_surfaces.py` (caption count becomes
  three), `docs/mcp-server.md`, both MCP-aware skills.
- **Diff sketch:** instructions gain: "The digest summarizes a
  rule-selected subset and counts the rest; for every item an agency or
  collection published on a day, use get_day_listing (finished days) or
  get_live_day (today). The digest's Coverage Statement says what was
  counted only and why." `get_digest`'s description gains the first
  sentence. The agents page table: question → tool (three or four
  rows).
- **Justification:** text where the agent reads before parsing (the
  descriptions) and where a human reads (the page).
- **Alternatives:** including the coverage table in the day listing's
  structured content (deferred: the counts already exist in
  `counts`; the per-rule coverage table lives in the digest and
  belongs to it).
- **Risk:** none.
- **Verification:** manifest tests (descriptions pass the
  hidden-instruction scan); page test for the third table.
- **Rollback:** revert.
- **Dependencies:** MF-2 (description tail sentence lands with it) —
  or ships first as text only; either order.

### MF-6 — `get_digest` section slicing (F6)

- **Why:** an agent wanting one section pays for 215 KB, and busy days
  approach the 512 KiB cap.
- **Files:** `packages/static-mcp/src/static_mcp/handlers.py`
  (`text_file` handler gains an optional `section` slice),
  `manifest.py` (handler option `sections: {"param": "<name>", "level": 2}`),
  README, package tests (fixture Markdown with numbered headings);
  both manifests (`get_digest` gains `section`, pattern
  `^(?:[1-9]|contents|day-in-review|coverage|methodology)$` — the exact
  slugs to be read off a real digest before writing), `docs/mcp-server.md`.
- **Diff sketch:** with `section` given, the handler returns the
  subtree from the matching heading (level-2 `## N.` numbered or the
  named blocks) to the next heading of the same or higher level,
  verbatim; `not_found` text when absent. `structuredContent` (MF-2)
  carries `section`.
- **Justification:** a slice of the same bytes preserves the verbatim
  guarantee; heading-bounded slicing needs no parser beyond a line
  scan.
- **Alternatives:** publishing per-section files (rejected: multiplies
  the twins for one consumer).
- **Risk / blast radius:** the digest's heading structure becomes an
  interface; a test pins the slugs against a real digest and fails if
  the renderer renames a section.
- **Verification:** package tests on a fixture; manifest test slices
  the fixture digest's Coverage Statement; live: `get_digest` with
  `section` returns a few KB.
- **Rollback:** remove the param; the handler option is inert unused.
- **Dependencies:** MF-2 (structured content shape).

### MF-7 — The home page names the MCP service (F7)

- **Why:** a summarizing fetch of the home page reported no MCP
  service.
- **Files:** `src/fapd/publish.py` (the shared page shell's head links
  and the home page footer), `tests/test_agent_discovery.py` (head
  links), `tests/test_publish.py` (footer), `deploy/vps/nginx/fapd-discovery-headers.inc`
  (the `Link` header gains the server-card relation), `tests/test_web_conf.py`.
- **Diff sketch:** head: `<link rel="service-desc" type="application/mcp-server-card+json" href="mcp/server-card">`
  when the manifest exists; footer: one line "MCP service for agents:
  `https://fapd.info/mcp` — read-only, no inference"; `Link` header:
  `</mcp/server-card>; rel="service-desc"; type="application/mcp-server-card+json"`.
  Master plan §8.3's relation list is amended first (contract).
- **Justification:** both survive summarization; the header keeps the
  in-document links and the headers identical, which §8.3 requires.
- **Alternatives:** a paragraph on the home page (rejected: the home
  page is the digest index, not an access guide).
- **Risk:** the head-links ≡ header test must be updated in the same
  commit or it fails.
- **Verification:** `curl -sI https://fapd.info/ | grep -i link` shows
  six relations; the home page HTML contains the footer line.
- **Rollback:** revert.
- **Dependencies:** none.

### MF-8 — `collection` becomes an enum (F8)

- **Why:** a guessed collection name gets an empty page instead of a
  correction.
- **Files:** `packages/static-mcp/src/static_mcp/manifest.py`
  (`ParamSpec` gains `enum: list[str] | None` for strings; validated
  against the pattern; emitted in `inputSchema`), `validate_value`
  (`-32602` naming the parameter and the allowed values — the one
  place a message may list values, because they are ours, not the
  client's), README, package tests; both manifests (`collection.enum`
  = the set of collection codes the day listing can carry, read off the
  code before writing — `config.FILING_POLICY` lists only the two
  cover-date exceptions, so the authority is the collection constants
  in `config.py` plus the observed `counts` keys of a real `today.json`:
  CREC, BILLS, FR, PLAW, USCOURTS, AGENCYPR, PRESACT, BILLACTIONS,
  VOTES — verify); `tests/test_mcp_manifest.py` pins the manifest enum
  equals that set (drift test).
- **Justification:** the set is fixed by code, so the schema can say
  so; an agent reading `inputSchema` sees the values before guessing.
- **Alternatives:** `isError` on zero matches (rejected: an empty day
  for a real collection is a true answer, not an error).
- **Risk:** a new collection code added to the code without the
  manifest fails the drift test — intended.
- **Verification:** package tests (enum accepted/rejected; schema
  carries it); live: `collection: "EPA"` → `-32602` naming the values.
- **Rollback:** remove `enum` from the manifest; the field is optional.
- **Dependencies:** none; same package release as MF-1.

### MF-9 — Dismiss F9; say what `list_sources` is (F9)

- **Why:** the tool already projects away the activity arrays; the
  reviewer read the full resource.
- **Files:** both manifests (`list_sources` description: "A summary per
  source (identity, method, status, health); `get_source` returns the
  full record including daily activity; the `sources.json` resource is
  the whole file"), `docs/mcp-server.md`; WORKLOG dismissal with the
  measured 80 KB / thirteen fields.
- **Verification:** the description passes the manifest checks; nothing
  else changes.
- **Dependencies:** none.

### MF-10 — Atomic site publish (F10)

- **Why:** a fetch during a rebuild can see a missing file; agents
  treat what they get as truth.
- **Files:** `src/fapd/publish.py` (`build_site` writes to a sibling
  directory and swaps), `deploy/vps/docker-compose.yml` / nginx `root`
  (a symlink inside the volume, `current` → the built tree; nginx
  `root /usr/share/nginx/html/current`; the MCP service's `--root`
  likewise), `scripts/build_site.py`, `RenderWorker._refresh_health`
  (writes into the current tree), `deploy/vps/scripts/deploy.sh`
  (first-run migration), `tests/test_publish.py`, `tests/test_dev_stack.py`,
  `tests/test_web_conf.py`, `docs/ops/OPS-GUIDE.md` (the OB-19
  retirement runbook changes: stale outputs vanish with the swap).
- **Diff sketch:** build into `<volume>/.build-<stamp>/`, then
  `os.replace` a `current` symlink (atomic on the same filesystem);
  delete the previous tree after the swap; nginx and `fapd-mcp` serve
  through the symlink (`disable_symlinks off` is nginx's default;
  confirm the MCP containment check resolves through the link — the
  package resolves paths with `strict=True` and requires the resolved
  path under the resolved root, so the root must be given as the
  symlink target or the check must resolve the root first — the
  package already does `root.resolve()`).
- **Justification:** rename-based swaps are the standard atomic
  publish; it also closes the OB-19 class (retired pages no longer
  survive in the volume) as a side effect.
- **Alternatives:** per-file temp-and-rename (rejected: the window
  becomes per-file instead of per-site but cross-file consistency,
  e.g. a digest and its twin, is not guaranteed).
- **Risk / blast radius:** high — every reader (nginx, fapd-mcp, the
  live-page writer, the evidence commit's `git add site/`, the dev
  stack) depends on the volume layout. Needs the rehearsal and the dev
  stack before deploy, and a deploy-time migration for the existing
  flat volume. **Scheduled last, as its own change with its own
  rehearsal rows.** The unverified "200 with a 404 body" symptom is
  recorded as such; if it recurs, capture headers.
- **Verification:** a test that builds twice and asserts a reader
  opening files during the second build sees only complete files from
  one tree; rehearsal rows for the symlink root; post-deploy health
  pass.
- **Rollback:** revert the compose/nginx root and the builder; the
  flat layout returns on the next build.
- **Dependencies:** everything else merged and quiet.

### MF-11 — Record the deferred cross-day tool

- **Why:** the report's `find_items(from, to, collection, agency)` is
  the right shape for the question but walks many files per request
  and is a new capability under GUIDE §2a rule 4.
- **Files:** `docs/ops/ops-backlog.md` (new entry, OB-26), this plan.
- **Diff sketch:** OB-26: the design, the ruling it needs, the trigger
  (an agent still needing more than ~10 requests for an agency-week
  after MF-1), the cost model (one request may read up to 366 files; a
  cap of 31 days per call would bound it).
- **Dependencies:** none.

## 5. Sequencing

| Wave | Tasks | Ships as | Needs the operator |
|---|---|---|---|
| A | MF-1, MF-8, MF-3, MF-9 | one package release + manifest change; MCP surface 1.1.0 not yet (no shape change) | no |
| B | MF-2, MF-5, MF-6 | one package release + manifest change; **surface 1.1.0**; re-publish the registry listing | yes: `mcp-publisher publish` after deploy |
| C | MF-7, MF-4 | Publication changes, no MCP version change | no |
| D | MF-11 | backlog entry | no |
| E | MF-10 | its own change, own rehearsal, own deploy | "deploy" and a quiet hour (not 03:30–06:00 UTC) |

Each wave: branch → tests → PR → CI → fast-forward → deploy → live
check → WORKLOG. The WORKLOG entry for Wave A carries the dismissal of
F3 and F9 with the evidence.

## 6. Definition of done

1. The EPA question from the report answered in **≤ 8 requests** and
   under 1 MB, recorded with the request list.
2. `content[0]` of every tool result is the payload; every tool has an
   `outputSchema`; the surface is 1.1.0 and the registry shows it.
3. The reviewer's exact `server/discover` request gets a message naming
   the 2026-07-28 request form.
4. `collection: "EPA"` is refused by name with the allowed values.
5. Every day-listing item has `published_day`.
6. The home page head, footer and `Link` header name the MCP service.
7. `get_digest` returns one section on request.
8. The site publishes atomically, verified by the rehearsal and a
   health pass.
9. F3 and F9 dismissed in the WORKLOG with evidence; MF-11 in the
   backlog.

## 7. Change log of this plan

- 2026-09-14: written from the verified findings; not started.

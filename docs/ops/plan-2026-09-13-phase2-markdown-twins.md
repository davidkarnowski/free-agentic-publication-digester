# Phase 2 — Markdown twins (agent discovery)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md)
(the master plan; read §7 and §8.2 first). Tasks AD-9, AD-10. Performed
by the **`fapd-publication`** agent, **continued from Phase 1** (send it
this phase via SendMessage; don't spawn a fresh agent). Depends on Phase
1 merged. Runs in parallel with Phase 3 and 4A. Last reviewed:
2026-09-13.*

## 0. Outcome

Every page in the master plan §8.2 eligibility table has a Markdown
**twin** next to it in the build output, and every page that has a twin
names it in its head (`<link rel="alternate" type="text/markdown">`).
Phase 3 then routes `Accept: text/markdown` requests to the twins.
Cloudflare measured agents using Markdown-negotiating docs spending 31%
fewer tokens and finishing 66% faster. For a digest, the twin **is** the
canonical record, byte for byte.

## 1. Ownership for this phase

**May edit:** `src/fapd/publish.py`; `tests/test_publish.py`;
`tests/test_agent_discovery.py` (created in Phase 1); new
`tests/test_markdown_twins.py`.

**Read-only:** everything else. `config.py` changes go in the exit report
as diffs. Don't commit `site/`.

## 2. Background (code anchors, 2026-09-13)

- `build_site()` (~3445): renders each digest (`digests/<date>.md` →
  `<date>.html`) in a loop; calls `_build_doc_pages` (~1728, from
  `_doc_sources` ~1696: `docs/site/*.md` + `README.md` as `readme`),
  `_build_sources_page` (~2247), `_build_source_pages` (~2937),
  `_build_blog` (~3124, from `_blog_sources` ~3057: allowlisted
  `docs/devnotes/*.md`), `_build_archive_pages` (~3409), and
  `_build_agent_surfaces` (~4679, which writes `agents.html` from
  `_AGENTS_MD`). The index page body is assembled at the end of
  `build_site`.
- `_render_page(title, body_html, nav_links, canonical, description=None, head_extra="")`
  (~1473) is the only page shell. **Add a keyword parameter
  `markdown_twin=None`**: when set, the head gets
  `<link rel="alternate" type="text/markdown" href="{twin}">`. Pass it
  through `head_extra` or a new `_PAGE` placeholder; whichever you
  choose, `_rebase_page` must rebase the href on subdirectory pages
  (it will, if the href is relative).
- `refresh_sources()` (~3169) rebuilds `sources.html` and
  `sources/<id>.html` on a clock, outside `build_site`
  (RenderWorker). **It must write the twins too**, or they go stale
  between site builds. `build_today()` is **not** eligible (§8.2), so it
  writes no twin.
- `_rebase_page` + `_REL_URL_ATTR_RE` (~1500).

## 3. Twin content rules

| Page | Twin file | Twin content | Rule |
|---|---|---|---|
| `<date>.html` | `<date>.md` | **byte-identical copy** of `digests/<date>.md` | The digest *is* its Markdown. No header, no footer, no edits. Git stores identical content once, so the twin costs no repository space. |
| doc pages `<stem>.html` (from `docs/site/<stem>.md`) | `<stem>.md` | the source Markdown **as the page renders it** (i.e. after `_textualize_external_images`), preceded by the standard header block (§3.1) | Same text the page shows |
| `readme.html` | `readme.md` | `_rewrite_readme_links(_textualize_external_images(README.md))`, plus header | Same transforms as the page |
| `agents.html` | `agents.md` | `_AGENTS_MD`, plus header | |
| blog `blog-<slug>.html` | `blog-<slug>.md` | the devnote Markdown the page renders, plus header, plus the commentary disclosure (the blog page's own "not the official record" sentence) | Blog disclosure must travel |
| `blog.html` | `blog.md` | generated list: title, date, teaser, link to each post's `.md` twin; plus header | from `_blog_sources()` |
| `index.html` | `index.md` | generated: tagline; live-page line (with the PRELIMINARY wording from the HTML callout); the recent-days list (same `RECENT_DIGEST_DAYS` window, same teasers); the archive pointer; the source-guide pointer; header | **built from the same variables as `index.html`**, in the same function, so the two can't disagree |
| `archive.html`, `archive/<YYYY>.html` | `archive.md`, `archive/<YYYY>.md` | generated: per month, a list of `- [<date>](<date>.md)` for published days (link **the `.md` twins**, rebased `../` in `archive/`); header | from the same `published` set as the calendars |
| `sources.html` | `sources.md` | generated from `_sources_body`'s inputs: the scope disclosure ("describes our ingestion, not any agency") first, then each group (active / planned / unavailable) as a list of `- **<name>** (<id>) — <status>; <method>; [page](sources/<id>.md)` plus the health label and window numbers where the HTML shows them; header | same `entries` and `health` objects as the HTML |
| `sources/<id>.html` | `sources/<id>.md` | generated: identity, method, politeness posture, status, the stats windows as Markdown tables, health label history, and any model-written orientation/assessment blocks **with the same "model-written" labels the HTML carries**; header | from `_source_page_body`'s inputs |
| `today.html`, `day/*.html`, `50x.html` | none | — | not eligible (§8.2) |

### 3.1 The standard header block (non-digest twins only)

```markdown
<!-- Markdown twin of {base}/{page}.html · Free Agentic Publication Digester -->
> This is the Markdown form of {base}/{page}.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `{canonical}` in {REPO_URL}.

```

It carries the same facts as the HTML footer (`_PAGE` footer), so the
disclosures travel with the data (GUIDE §1). Nothing that changes per
build goes in it: no `generated` time.

### 3.2 The single-source rule

`docs/agents/publication.md`: *never let two surfaces answer the same
editorial question with different code* (the 721-backfill incident of
2026-07-31). For every **generated** twin, compute the data once and pass
it to both the HTML renderer and the Markdown renderer. Where an HTML
helper both computes and formats, split it: `_x_data(...)` → dict, then
`_x_html(data)` and `_x_md(data)`. Don't re-query or re-derive in the
Markdown path.

### 3.3 Accessibility note

Twins are not an "accessible version" (GUIDE §2a rule 7 forbids those).
They're an alternate representation of the same resource for software,
selected by content negotiation, and a person browsing never sees one. No
HTML page class changes except the added head `<link>`. No findings entry
is needed, but say so in the exit report.

## 4. Tasks

### AD-9 — twins for pages that already have a Markdown source

Digests, doc pages, `readme`, `agents`, blog posts. Add `markdown_twin=`
to their `_render_page` calls.

**Tests** (`tests/test_markdown_twins.py`):
1. Fixture build: `<date>.md` bytes == `digests/<date>.md` bytes for both
   fixture digests.
2. Each doc page's twin starts with the header comment and contains the
   page's H1 text.
3. The blog twin contains the commentary disclosure (use the same string
   constant as the HTML page; if none exists, create it and use it in
   both).
4. The head link exists on each twinned page and is absent on
   `today.html` and `day/<date>.html`.

### AD-10 — generated twins

`index`, `blog` index, `archive` pages, `sources`, `sources/<id>`.
`refresh_sources()` writes the sources twins as well.

**Tests:**
1. **Coverage invariant (the one Phase 3 relies on):** after a fixture
   `build_site`, every file matching the §8.2 eligibility patterns
   (`index.html`; root `*.html` except `today.html` and `50x.html`;
   `sources/*.html`; `archive/*.html`) has a sibling `.md`. Implement the
   patterns as regexes **copied verbatim from master plan §8.2** into a
   module constant `TWIN_ELIGIBLE_PATTERNS`, so Phase 3's test can import
   and reuse them.
2. Set equality: dates in `index.md` == dates in `index.html`'s recent
   list; dates in `archive/<YYYY>.md` == linked dates in
   `archive/<YYYY>.html`; source ids in `sources.md` == ids on
   `sources.html`.
3. `refresh_sources()` alone regenerates `sources.md` (write a sentinel,
   call it, assert the sentinel is gone).
4. Determinism: two builds give byte-identical twins.
5. Banned-lexicon scan over generated twin text; the sources twin
   contains the ingestion-scope disclosure.

## 5. Acceptance criteria

1. Coverage invariant test passes; `TWIN_ELIGIBLE_PATTERNS` matches
   master plan §8.2 exactly.
2. Digest twins are byte-identical to the canonical Markdown.
3. Every twinned HTML page names its twin in `<head>`, with correct
   `../` prefixes in subdirectories; non-eligible pages don't.
4. Generated twins come from the same data objects as their HTML (review
   the diff for any second query or derivation).
5. Twins carry the disclosures their HTML pages carry.
6. `refresh_sources()` keeps sources twins current.
7. Ruff clean, full pytest green (report counts).

## 6. Manual check (paste into exit report)

```sh
uv run python - <<'PY'
import tempfile, pathlib, filecmp
from fapd import publish, config
out = pathlib.Path(tempfile.mkdtemp()) / "site"
publish.build_site(out_dir=out)
digs = sorted(pathlib.Path(config.DIGEST_DIR).glob("20*.md"))
print("digest twins identical:", all(filecmp.cmp(d, out / d.name, shallow=False) for d in digs))
print("root twins:", len(list(out.glob("*.md"))), "sources twins:", len(list((out/"sources").glob("*.md"))))
print((out / "index.md").read_text()[:800])
PY
```

## 7. Rollback

Revert. Leftover `.md` files in a deployed site volume are harmless, but
`build_site` never deletes stale output (OB-19/F-009 class). If rolled
back after a deploy, delete them from the volume in a staged script.

## 8. Dispatch (SendMessage to the Phase 1 Publication agent)

```
Phase 1 is merged (commit <hash>). Continue with Phase 2 of the
agent-discovery plan: Markdown twins, exactly as specified in
docs/ops/plan-2026-09-13-phase2-markdown-twins.md, meeting every
acceptance criterion in its §5. Same contract and exit-report shape as
before. Start a new progress log
research/agent-logs/agent-discovery-phase2-<YYYYMMDD>.md and write its
first entry before touching any file. Phase 3 (Operations) will import
TWIN_ELIGIBLE_PATTERNS from your code for its routing test, so name and
shape it exactly as §4 AD-10 says.
```

"""Static-site presentation layer: canonical Markdown digests -> site/.

Derived output only (GUIDE §5): zero LLM calls, regenerable at any time
from digests/*.md. Pages are plain HTML5 + one shared stylesheet — no
JavaScript, no external resources — so they render identically from the
filesystem, GitHub Pages, or any static host, on desktop and mobile.
"""

import html
import re
import shutil
from pathlib import Path

import markdown

from . import config, sources
from .sync import utc_now_iso

SITE_TITLE = "Free Agentic Publication Digester — Daily Federal Digest"
SITE_TAGLINE = (
    "An automated, citation-bound, opinion-agnostic daily digest of official "
    "United States government publications — congressional, executive, and "
    "judicial — built only from primary sources."
)

_MD = markdown.Markdown(extensions=["tables", "toc"])

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <nav>
    <a class="brand" href="index.html" title="Free Agentic Publication Digester"
       aria-label="Free Agentic Publication Digester (FAPD)">FAPD</a>
    <span class="nav-links">{nav_links}</span>
  </nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <p>Generated {generated} (UTC). Canonical source:
  <code>{canonical}</code> in the repository. Selection is mechanical and
  every item cites its official source; methodology in
  <code>GUIDE.md</code> §2.</p>
  <p>Content licensed
  <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> —
  reuse with attribution to FAPD (Free Agentic Publication Digester);
  quoted official government text is
  public domain (17 U.S.C. § 105). Code licensed Apache-2.0.</p>
</footer>
</body>
</html>
"""

_STYLE = """\
:root {
  --bg: #fdfdfc;
  --fg: #1b1f24;
  --muted: #57606a;
  --accent: #1f4e79;
  --accent-soft: #e8eff6;
  --border: #d8dde3;
  --stripe: #f4f6f8;
  --card: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #101418;
    --fg: #e6e9ec;
    --muted: #9aa4af;
    --accent: #7ab3e0;
    --accent-soft: #1a2733;
    --border: #2c343c;
    --stripe: #171d23;
    --card: #151a20;
  }
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  line-height: 1.6;
  font-size: 1rem;
}
.site-header {
  border-bottom: 1px solid var(--border);
  background: var(--accent-soft);
}
.site-header nav {
  max-width: 46rem;
  margin: 0 auto;
  padding: 0.6rem 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  align-items: baseline;
  justify-content: space-between;
}
.brand {
  font-weight: 700;
  text-decoration: none;
  color: var(--accent);
  letter-spacing: 0.01em;
}
.nav-links {
  display: inline-flex; flex-wrap: wrap; gap: 0.15rem 0;
  font-size: 0.85rem;
}
.nav-links a {
  color: var(--muted);
  text-decoration: none;
  margin-left: 0.9rem;
  white-space: nowrap;   /* multi-word labels never break mid-name */
}
.nav-links a:hover, .brand:hover { text-decoration: underline; }
main {
  max-width: 46rem;
  margin: 0 auto;
  padding: 1.2rem 1rem 3rem;
}
h1 { font-size: 1.65rem; line-height: 1.25; margin: 1.2rem 0 0.8rem; }
h2 {
  font-size: 1.25rem;
  margin: 2rem 0 0.7rem;
  padding-bottom: 0.25rem;
  border-bottom: 2px solid var(--accent-soft);
  color: var(--accent);
}
h3 { font-size: 1.08rem; margin: 1.4rem 0 0.5rem; }
h4 {
  font-size: 0.92rem;
  margin: 1.2rem 0 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}
a { color: var(--accent); }
hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }
em { color: var(--muted); }
code {
  background: var(--stripe);
  padding: 0.1em 0.35em;
  border-radius: 4px;
  font-size: 0.9em;
}
ul { padding-left: 1.3rem; }
li { margin: 0.35rem 0; }
li > ul { margin-top: 0.15rem; }
li li { font-size: 0.95rem; }
table {
  display: block;
  overflow-x: auto;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.92rem;
}
th, td {
  border: 1px solid var(--border);
  padding: 0.4rem 0.7rem;
  text-align: left;
}
th { background: var(--accent-soft); }
tr:nth-child(even) td { background: var(--stripe); }
img {
  max-width: 100%;
  height: auto;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: #fff;
}
/* Digest structure layer: compact header, tag chips, collapsible sections
   (native details/summary — the site remains JS-free). */
.digest-meta {
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.4rem 1rem;
  margin: 0.4rem 0 1.4rem; padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.meta-generated { font-size: 0.8rem; color: var(--muted); }
.meta-more { font-size: 0.8rem; color: var(--muted); }
.meta-more summary { cursor: pointer; color: var(--accent); }
.meta-more dl { margin: 0.4rem 0 0; }
.meta-more dt { font-weight: 600; margin-top: 0.3rem; }
.meta-more dd { margin: 0; overflow-wrap: anywhere; }
.tags { margin: 0.35rem 0; line-height: 1.9; }
.tag {
  display: inline-block; padding: 0.05rem 0.55rem; margin-right: 0.3rem;
  border: 1px solid var(--border); border-radius: 999px;
  background: var(--stripe); color: var(--muted);
  font-size: 0.72rem; letter-spacing: 0.02em; white-space: nowrap;
}
.tag-model { border-style: dashed; font-style: italic; }
details.digest-section {
  border: 1px solid var(--border); border-radius: 8px;
  background: var(--card); margin: 0.7rem 0; padding: 0;
}
details.digest-section > summary {
  cursor: pointer; padding: 0.7rem 0.9rem; list-style: none;
  display: flex; flex-direction: column; gap: 0.25rem;
}
details.digest-section > summary::-webkit-details-marker { display: none; }
.sec-title { font-weight: 650; font-size: 1.05rem; }
.sec-title::before { content: "▸ "; color: var(--accent); font-size: 0.85em; }
details.digest-section[open] .sec-title::before { content: "▾ "; }
summary .sec-blurb { font-size: 0.92rem; color: var(--fg); opacity: 0.85; }
details.digest-section > *:not(summary) { margin-left: 0.9rem; margin-right: 0.9rem; }
details.digest-section > .sec-heading { font-size: 1.15rem; margin-top: 0.6rem; }
details.digest-section[open] > summary .sec-blurb,
details.digest-section[open] > summary .tags { display: none; }

/* Digest readability layer (derived presentation; canonical md unstyled).
   Plain-speak = interpretation register; rule/source = subtle metadata. */
.plain {
  background: var(--accent-soft);
  border-left: 3px solid var(--accent);
  border-radius: 0 4px 4px 0;
  padding: 0.35rem 0.6rem;
  margin: 0.3rem 0;
  list-style: none;
  font-size: 0.95rem;
}
.plain-label {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--accent);
  margin-right: 0.45rem;
}
.plain-label::after { content: ":"; }
li.rule-note, li.source-note {
  font-size: 0.78rem;
  color: var(--muted);
  list-style: none;
  margin: 0.1rem 0;
}
li.source-note a { color: var(--muted); }
.rule-id {
  border-bottom: 1px dotted var(--muted);
  cursor: help;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.74rem;
}
.site-footer {
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.85rem;
}
.site-footer p { max-width: 46rem; margin: 0 auto; padding: 1rem; }
.digest-list { list-style: none; padding: 0; }
.digest-list li {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.9rem 1.1rem;
  margin: 0.8rem 0;
}
.digest-list a.date {
  font-weight: 700;
  font-size: 1.05rem;
  text-decoration: none;
}
.digest-list p.teaser {
  margin: 0.4rem 0 0;
  color: var(--muted);
  font-size: 0.95rem;
}
.tagline { color: var(--muted); }
/* Source directory (sources.html): the registry rendered as grouped cards.
   Chips reuse .tag; the record folds into a native details (still JS-free). */
.src-counts { font-size: 1.02rem; }
.status-key {
  display: grid; grid-template-columns: max-content 1fr;
  gap: 0.35rem 0.7rem; margin: 0.8rem 0 1.2rem;
}
.status-key dt { margin: 0; }
.status-key dd { margin: 0; font-size: 0.9rem; color: var(--muted); }
.src-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.8rem 1rem;
  margin: 0.8rem 0;
}
.src-card .src-name {
  margin: 0; font-size: 1.02rem;
  text-transform: none; letter-spacing: normal; color: var(--fg);
}
.src-name a { text-decoration: none; }
.src-name a:hover { text-decoration: underline; }
.src-sub { margin: 0.25rem 0 0; font-size: 0.8rem; color: var(--muted); }
.src-desc { margin: 0.45rem 0 0; font-size: 0.92rem; }
.src-links { margin: 0.35rem 0 0; font-size: 0.85rem; }
.src-more { margin-top: 0.45rem; font-size: 0.8rem; color: var(--muted); }
.src-more summary { cursor: pointer; color: var(--accent); }
.src-more dl { margin: 0.4rem 0 0; }
.src-more dt { font-weight: 600; margin-top: 0.3rem; }
.src-more dd { margin: 0; overflow-wrap: anywhere; }
.tag-status-active {
  background: var(--accent-soft); color: var(--accent);
  border-color: var(--accent);
}
.tag-status-unavailable { border-style: dashed; }
.tag-status-excluded { border-style: dotted; }
"""

_DATE_MD_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
_TEASER_RE = re.compile(r"^## Day in Review\s*$", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def _digest_files(digest_dir):
    return sorted(
        (p for p in Path(digest_dir).glob("*.md") if _DATE_MD_RE.match(p.name)),
        key=lambda p: p.stem,
    )


def _teaser(md_text):
    """First sentence of the Day in Review, for index cards."""
    match = _TEASER_RE.search(md_text)
    if not match:
        return None
    rest = md_text[match.end():].strip()
    para = rest.split("\n\n", 1)[0].replace("\n", " ").strip()
    sentence = re.split(r"(?<=[.;])\s", para, maxsplit=1)[0]
    return sentence or None


_PLAIN_LI_RE = re.compile(r"<li><em>In plain terms:</em>\s*(.*?)</li>", re.DOTALL)
_PLAIN_P_RE = re.compile(r"<p><em>In plain terms:\s*(.*?)</em></p>", re.DOTALL)
_RULE_LI_RE = re.compile(
    r"<li>Included because:\s*([A-Z]+-[A-Z]+-\d+)\s*—\s*(.*?)</li>", re.DOTALL)
_SOURCE_LI_RE = re.compile(r"<li>Source:\s*(.*?)</li>", re.DOTALL)


_META_TABLE_RE = re.compile(r"<table>.*?Digest date.*?</table>", re.DOTALL)
_META_ROW_RE = re.compile(
    r"<td>(?:<strong>)?(Digest date|Data date range|Generated at|"
    r"Pipeline version|Source watermarks)(?:</strong>)?</td>\s*<td>(.*?)</td>",
    re.DOTALL)
_TAGS_P_RE = re.compile(r"<p>Tags: (.*?)</p>", re.DOTALL)
_CONTENTS_RE = re.compile(r"<h2[^>]*>Contents</h2>\s*<ul>.*?</ul>\s*(<hr\s*/?>)?",
                          re.DOTALL)
# Sections that collapse: numbered sections plus the appendix blocks.
_COLLAPSIBLE_H2_RE = re.compile(
    r'<h2 id="([^"]+)">(\d+\..*?|Glossary.*?|Coverage Statement.*?|Methodology.*?)</h2>',
    re.DOTALL)


def _compact_meta(html_body):
    """The leading metadata table becomes a compact strip: the date reads
    large, generation info small, and the provenance detail (pipeline
    version, watermarks, range) folds into a native <details>."""
    match = _META_TABLE_RE.search(html_body)
    if not match:
        return html_body
    fields = dict(_META_ROW_RE.findall(match.group(0)))
    if "Digest date" not in fields:
        return html_body
    strip = (
        '<div class="digest-meta">'
        f'<span class="meta-generated">Generated {fields.get("Generated at", "")}'
        "</span>"
        '<details class="meta-more"><summary>Provenance</summary><dl>'
        f'<dt>Data date range</dt><dd>{fields.get("Data date range", "")}</dd>'
        f'<dt>Pipeline version</dt><dd>{fields.get("Pipeline version", "")}</dd>'
        f'<dt>Source watermarks</dt><dd>{fields.get("Source watermarks", "")}</dd>'
        "</dl></details></div>"
    )
    return html_body[:match.start()] + strip + html_body[match.end():]


def _chip_tags(html_body):
    """`Tags: a · b · model keys: x · y` paragraphs become chip rows; the
    model-derived keys keep their in-place label as a visually distinct
    chip class (GUIDE §2 labeling carried into the presentation)."""

    def _sub(match):
        text = match.group(1)
        mech_part, _, model_part = text.partition("model keys:")
        chips = [f'<span class="tag">{t.strip()}</span>'
                 for t in mech_part.split("·") if t.strip()]
        chips += [f'<span class="tag tag-model" title="model-generated key">'
                  f"{t.strip()}</span>"
                  for t in model_part.split("·") if t.strip()]
        return f'<p class="tags">{"".join(chips)}</p>'

    return _TAGS_P_RE.sub(_sub, html_body)


def _collapse_sections(html_body):
    """Numbered sections and appendix blocks fold into native <details>
    cards whose summary carries the title, the section's tag chips, and
    its plain-speak synopsis — so the initial page is the day in plain
    speak, and the full record expands on demand. The h2's anchor id
    moves to the details element so ToC-style deep links keep working."""
    parts = re.split(r"(?=<h2 )", html_body)
    out = [parts[0]]
    for chunk in parts[1:]:
        match = _COLLAPSIBLE_H2_RE.match(chunk)
        if not match:
            out.append(chunk)
            continue
        anchor, title = match.group(1), re.sub(r"<[^>]+>", "", match.group(2))
        body = chunk[match.end():]
        tags_m = re.search(r'<p class="tags">.*?</p>', body, re.DOTALL)
        blurb_m = re.search(
            r'<p class="plain plain-para">'
            r'<span class="plain-label">In plain terms</span>\s*(.*?)</p>',
            body, re.DOTALL)
        summary = f'<span class="sec-title">{title}</span>'
        if tags_m:
            summary += tags_m.group(0).replace('<p class="tags">', '<span class="tags">') \
                                      .replace("</p>", "</span>")
        if blurb_m:
            summary += f'<span class="sec-blurb">{blurb_m.group(1)}</span>'
        out.append(
            f'<details class="digest-section" id="{anchor}">'
            f"<summary>{summary}</summary>"
            f'<h2 class="sec-heading">{title}</h2>{body}</details>')
    return "".join(out)


def _style_digest_body(html_body):
    """Readability layer for digest pages (derived presentation only — the
    canonical Markdown is untouched, per GUIDE §5): plain-speak lines get
    their own visual register, and the mechanical notations (inclusion
    rule, citation) shrink to subtle metadata. The rule description folds
    into a tooltip on the rule id — the compact "rule mapping" — while
    staying verbatim in the canonical file."""
    html_body = _PLAIN_LI_RE.sub(
        r'<li class="plain"><span class="plain-label">In plain terms</span> \1</li>',
        html_body)
    html_body = _PLAIN_P_RE.sub(
        r'<p class="plain plain-para"><span class="plain-label">In plain terms</span> \1</p>',
        html_body)

    def _rule(match):
        rule_id, desc = match.group(1), match.group(2)
        title = html.escape(re.sub(r"<[^>]+>", "", desc), quote=True)
        return (f'<li class="rule-note">Included because: '
                f'<span class="rule-id" title="{title}">{rule_id}</span></li>')

    html_body = _RULE_LI_RE.sub(_rule, html_body)
    html_body = _SOURCE_LI_RE.sub(
        r'<li class="source-note">Source: \1</li>', html_body)
    html_body = _compact_meta(html_body)
    html_body = _chip_tags(html_body)
    html_body = _CONTENTS_RE.sub("", html_body, count=1)
    html_body = _collapse_sections(html_body)
    return html_body


def _render_page(title, body_html, nav_links, canonical):
    return _PAGE.format(
        title=html.escape(title),
        nav_links=nav_links,
        body=body_html,
        generated=utc_now_iso(),
        canonical=html.escape(canonical),
    )


# Compact nav labels where a stem's .capitalize() reads badly.
_NAV_LABELS = {"ai-development": "AI development"}


def _doc_nav_links(doc_pages):
    """Nav anchors for the docs/site explanatory pages (About, Methods, …)."""
    return "".join(
        f'<a href="{stem}.html">'
        f'{html.escape(_NAV_LABELS.get(stem, stem.capitalize()))}</a>'
        for stem, _title in doc_pages
    )


def _nav_for(dates, i, doc_pages=()):
    links = []
    if i > 0:
        links.append(f'<a href="{dates[i - 1]}.html">&larr; {dates[i - 1]}</a>')
    if i < len(dates) - 1:
        links.append(f'<a href="{dates[i + 1]}.html">{dates[i + 1]} &rarr;</a>')
    links.append('<a href="index.html">All digests</a>')
    links.append('<a href="sources.html">Sources</a>')
    links.append(_doc_nav_links(doc_pages))
    links.append('<a href="agents.html">For agents</a>')
    return "".join(links)


# README → site link rewriting: repo-relative links that have a site
# equivalent are pointed at it; the rest degrade to plain code text (the
# canonical footer names the repo file, and the repo is not yet public).
_README_LINK_REWRITES = (
    (re.compile(r"\]\(digests/(\d{4}-\d{2}-\d{2})\.md\)"), r"](\1.html)"),
    (re.compile(r"\]\(site/\)"), r"](index.html)"),
    (re.compile(r"\]\(site/([A-Za-z0-9_.-]+)\)"), r"](\1)"),
    (re.compile(r"\]\(SOURCES\.md\)"), r"](sources.html)"),
)
_README_PLAIN_LINK = re.compile(
    r"\[([^\]]+)\]\((?!https?://|#|[a-z0-9-]+\.html\b|llms\.txt|digests\.json"
    r"|feed\.xml)[^)]+\)"
)


def _rewrite_readme_links(md_text):
    for pattern, repl in _README_LINK_REWRITES:
        md_text = pattern.sub(repl, md_text)
    return _README_PLAIN_LINK.sub(r"`\1`", md_text)


def _build_doc_pages(out_dir):
    """Render every docs/site/*.md explanatory page (About, Methods, …) plus
    the repo-root README (as readme.html, repo links rewritten to their site
    equivalents) to site/<stem>.html. Returns a sorted list of (stem, title)
    for pages built; absent sources simply yield no pages."""
    docs = []
    doc_dir = config.PROJECT_ROOT / "docs" / "site"
    if doc_dir.is_dir():
        for path in sorted(doc_dir.glob("*.md"), key=lambda p: p.stem):
            md_text = path.read_text(encoding="utf-8")
            match = _H1_RE.search(md_text)
            title = match.group(1) if match else path.stem.capitalize()
            docs.append((md_text, path.stem, title, f"docs/site/{path.name}"))
    readme = config.PROJECT_ROOT / "README.md"
    if readme.exists():
        md_text = _rewrite_readme_links(readme.read_text(encoding="utf-8"))
        match = _H1_RE.search(md_text)
        title = match.group(1) if match else "README"
        docs.append((md_text, "readme", title, "README.md"))
    doc_pages = [(stem, title) for _t, stem, title, _c in docs]
    brand = SITE_TITLE.split(" — ")[0]
    for md_text, stem, title, canonical in docs:
        _MD.reset()
        body = _MD.convert(md_text)
        page = _render_page(
            # No brand suffix when the page title already carries it (README)
            title if brand in title else f"{title} — {SITE_TITLE}",
            body,
            '<a href="index.html">All digests</a><a href="sources.html">Sources</a>'
            + _doc_nav_links(p for p in doc_pages if p[0] != stem)
            + '<a href="agents.html">For agents</a>',
            canonical,
        )
        (out_dir / f"{stem}.html").write_text(page, encoding="utf-8")
    return doc_pages


# ---------------------------------------------------------------------------
# Source guide page (sources.html)
# ---------------------------------------------------------------------------
# Rendered directly from sources/registry.yaml — the same registry that
# generates the committed SOURCES.md evidence artifact (which is unchanged
# by this page). Deterministic, zero-LLM: a directory of grouped cards
# instead of one large table.

_TYPE_LABELS = {
    "govinfo-collection": "govinfo collection",
    "rss": "RSS feed",
    "html-index": "HTML index",
    "xml-index": "XML index",
    "api": "API",
    "aggregator": "aggregator",
    "bulkdata": "bulk data",
    "email": "email bulletin",
}
_WEB_TYPES = ("rss", "html-index", "xml-index", "api", "aggregator", "bulkdata")
_STATUS_CHIPS = {
    "active": ("active", "tag-status-active"),
    "planned": ("planned", "tag-status-planned"),
    "unavailable": ("unavailable", "tag-status-unavailable"),
    "evaluated-excluded": ("excluded", "tag-status-excluded"),
}
_STATUS_PHRASES = {
    "active": "active",
    "planned": "planned",
    "unavailable": "unavailable",
    "evaluated-excluded": "evaluated and excluded",
}
_STATUS_DEFS = (
    ("active", ("ingested by the pipeline today; each active entry carries a "
                "dated coverage evaluation in its registry notes")),
    ("planned", ("registered so the coverage gap is visible; activation waits "
                 "on the source's probe and content evaluation")),
    ("unavailable", ("the publisher's site refuses the project's "
                     "honestly-identified automated client; the refusal is "
                     "recorded as observed, never evaded, and re-checked as "
                     "sites change")),
    ("evaluated-excluded", ("examined and found outside the project's scope "
                            "of newly published federal government actions; "
                            "kept on the record")),
)
# Email addresses never render on the site: the project mailbox and the
# per-source sender allowlist stay in the registry (GUIDE §9 posture).
# Registry notes that quote a sender keep their evidence value with the
# address withheld in place.
_EMAIL_ADDR_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _redact_addresses(text):
    return _EMAIL_ADDR_RE.sub("[address withheld]", text)


def _status_chip(status):
    label, css_class = _STATUS_CHIPS[status]
    return f'<span class="tag {css_class}">{label}</span>'


def _source_card(entry):
    """One registry entry as a card: linked name, status chip + subtitle,
    the registry's descriptive text, and the full registry record (id,
    added date, method, notes) folded into a native <details>."""
    urls = entry["urls"]
    link = urls.get("home") or next(iter(urls.values()))
    subtitle = html.escape(
        f"{entry['branch'].capitalize()} · Tier {entry['tier']} · "
        f"{_TYPE_LABELS.get(entry['type'], entry['type'])} · {entry['parent_org']}"
    )
    signup = ""
    if entry["type"] == "email" and "signup" in urls:
        signup = (
            f'<p class="src-links"><a href="{html.escape(urls["signup"], quote=True)}">'
            "Agency signup page</a> (the same public form the project "
            "subscribed through)</p>"
        )
    record = [
        f"<dt>Registry id</dt><dd><code>{html.escape(entry['id'])}</code></dd>",
        f"<dt>Added</dt><dd>{html.escape(entry['added'])}</dd>",
        f"<dt>Method</dt><dd>{html.escape(_redact_addresses(entry['method']))}</dd>",
    ]
    notes = entry["notes"].strip()
    if notes:
        record.append(
            f"<dt>Notes</dt><dd>{html.escape(_redact_addresses(notes))}</dd>")
    return (
        f'<article class="src-card" id="src-{html.escape(entry["id"])}">'
        f'<h4 class="src-name"><a href="{html.escape(link, quote=True)}">'
        f"{html.escape(entry['name'])}</a></h4>"
        f'<p class="src-sub">{_status_chip(entry["status"])} {subtitle}</p>'
        f'<p class="src-desc">{html.escape(entry["description"])}</p>'
        f"{signup}"
        f'<details class="src-more"><summary>Registry record</summary>'
        f'<dl>{"".join(record)}</dl></details>'
        "</article>"
    )


def _source_section(anchor, title, intro_html, group_entries):
    """A source group as h2 + intro + Active/Planned h3 subgroups of cards
    (registry order within each subgroup — registry order is precedence)."""
    parts = [f'<h2 id="{anchor}">{title}</h2>', intro_html]
    for status in ("active", "planned"):
        subset = [e for e in group_entries if e["status"] == status]
        if not subset:
            continue
        parts.append(f"<h3>{status.capitalize()} ({len(subset)})</h3>")
        parts.extend(_source_card(e) for e in subset)
    return "".join(parts)


def _sources_body(entries):
    counts = {s: sum(1 for e in entries if e["status"] == s)
              for s in sources.STATUSES}
    # Counts read in page order (the order sections appear), not enum order.
    counts_text = ", ".join(
        f"{counts[s]} {_STATUS_PHRASES[s]}" for s, _d in _STATUS_DEFS if counts[s])
    status_key = "".join(
        f"<dt>{_status_chip(s)}</dt><dd>{d}.</dd>" for s, d in _STATUS_DEFS)
    # Tier semantics come from the registry module so this page and
    # SOURCES.md state the same universe.
    tiers_text = "; ".join(
        f"Tier {t} — {sources._TIER_SEMANTICS[t]}" for t in sources.TIERS)

    parts = [
        "<h1>Sources</h1>",
        ("<p>The Free Agentic Publication Digester builds its daily digest "
         "only from official federal publication channels. This page is the "
         "source directory: every source the project ingests, plans to "
         "ingest, or has evaluated, rendered from the registry "
         "(<code>sources/registry.yaml</code>) that governs the pipeline's "
         "scope. Entries are never deleted — a source that refuses automated "
         "access stays listed, because the refusal is part of the coverage "
         "record.</p>"),
        (f'<p class="src-counts"><strong>{len(entries)}</strong> sources '
         f"registered — {counts_text}.</p>"),
        f'<dl class="status-key">{status_key}</dl>',
        (f'<p class="tagline">Tiers state coverage against a defined '
         f"universe: {tiers_text}.</p>"),
    ]

    listed = [e for e in entries if e["status"] in ("active", "planned")]
    parts.append(_source_section(
        "govinfo-collections", "Official govinfo collections",
        "<p>Structured document collections published by the Government "
        "Publishing Office through govinfo.gov — the core official record "
        "the digest is built from. Each collection syncs through the "
        "govinfo collections API with per-collection watermarks.</p>",
        [e for e in listed if e["type"] == "govinfo-collection"]))
    parts.append(_source_section(
        "agency-web-channels", "Agency newsrooms and web channels",
        "<p>Press-release feeds and indexes, APIs, and bulk data that "
        "agencies publish on the web, read through the project's "
        "robots-respecting identified client. The subtitle on each card "
        "names the channel type.</p>",
        [e for e in listed if e["type"] in _WEB_TYPES]))
    parts.append(_source_section(
        "agency-email-bulletins", "Agency email bulletins",
        "<p>Bulletins the agencies themselves distribute by subscription "
        "email (GovDelivery and similar services), delivered to a single "
        "identified project mailbox, DKIM-verified on arrival, and ingested "
        "from the message body. Sender and mailbox addresses are recorded "
        "in the registry, not republished here; where a registry note "
        "quotes one, it appears as [address withheld].</p>",
        [e for e in listed if e["type"] == "email"]))

    unavailable = [e for e in entries if e["status"] == "unavailable"]
    if unavailable:
        parts.append(
            f'<h2 id="unavailable-sources">Unavailable sources '
            f"({len(unavailable)})</h2>"
            "<p>These publishers currently refuse the project's "
            "honestly-identified automated client — a robots.txt disallow "
            "or an HTTP block on the listed path. Project policy "
            '(<a href="methods.html">Methods</a>) is to record the refusal '
            "exactly as observed and never work around it: no browser "
            "impersonation, no unidentified fetching. Each entry stays "
            "listed because a closed door is coverage information; where an "
            "agency offers a subscription email channel instead, a sibling "
            "entry appears above and the refusal here stands on the "
            "record.</p>")
        parts.extend(_source_card(e) for e in unavailable)

    excluded = [e for e in entries if e["status"] == "evaluated-excluded"]
    if excluded:
        parts.append(
            f'<h2 id="evaluated-and-excluded">Evaluated and excluded '
            f"({len(excluded)})</h2>"
            "<p>Sources examined and found outside the project's scope — "
            "they do not publish new federal government actions. The "
            "evaluation is kept so the decision stays visible and "
            "revisitable.</p>")
        parts.extend(_source_card(e) for e in excluded)

    return "".join(parts)


def _build_sources_page(out_dir, doc_pages=()):
    """Render the source guide as a human-readable directory derived from
    sources/registry.yaml at build time. Returns True if the page was built."""
    registry_path = config.PROJECT_ROOT / "sources" / "registry.yaml"
    if not registry_path.exists():
        return False
    entries = sources.load_registry(registry_path)
    page = _render_page(
        f"Sources — {SITE_TITLE}",
        _sources_body(entries),
        '<a href="index.html">All digests</a>' + _doc_nav_links(doc_pages)
        + '<a href="agents.html">For agents</a>',
        "sources/registry.yaml",
    )
    (out_dir / "sources.html").write_text(page, encoding="utf-8")
    return True


def build_site(digest_dir=None, out_dir=None):
    """Convert every digest to HTML plus an index. Returns stats."""
    digest_dir = Path(digest_dir or config.DIGEST_DIR)
    out_dir = Path(out_dir or config.SITE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = _digest_files(digest_dir)
    dates = [p.stem for p in files]
    teasers = {}
    assets_copied = 0
    doc_pages = _build_doc_pages(out_dir)

    for i, path in enumerate(files):
        md_text = path.read_text(encoding="utf-8")
        teasers[path.stem] = _teaser(md_text)
        _MD.reset()
        body = _style_digest_body(_MD.convert(md_text))
        page = _render_page(
            f"Daily Digest {path.stem} — {SITE_TITLE}",
            body,
            _nav_for(dates, i, doc_pages),
            f"digests/{path.name}",
        )
        (out_dir / f"{path.stem}.html").write_text(page, encoding="utf-8")

        asset_src = digest_dir / "assets" / path.stem
        if asset_src.is_dir():
            asset_dst = out_dir / "assets" / path.stem
            asset_dst.mkdir(parents=True, exist_ok=True)
            for f in asset_src.iterdir():
                if f.is_file():
                    shutil.copy2(f, asset_dst / f.name)
                    assets_copied += 1

    cards = []
    for date in reversed(dates):
        teaser = teasers.get(date)
        teaser_html = (
            f'<p class="teaser">{html.escape(teaser)}</p>' if teaser else ""
        )
        cards.append(
            f'<li><a class="date" href="{date}.html">Daily Digest — {date}</a>'
            f"{teaser_html}</li>"
        )
    sources_built = _build_sources_page(out_dir, doc_pages)
    _build_agent_surfaces(out_dir, dates, teasers, doc_pages,
                          base=config.SITE_BASE_URL)
    sources_link = (
        '<p class="tagline"><a href="sources.html">Source guide</a> — every '
        "federal source we ingest, plan to ingest, or have evaluated, with "
        "method and status.</p>" if sources_built else ""
    )
    index_body = (
        f"<h1>{html.escape(SITE_TITLE)}</h1>"
        f'<p class="tagline">{html.escape(SITE_TAGLINE)}</p>'
        f"{sources_link}"
        f'<ul class="digest-list">{"".join(cards)}</ul>'
    )
    index = _render_page(
        SITE_TITLE, index_body,
        ('<a href="sources.html">Sources</a>' if sources_built else "")
        + _doc_nav_links(doc_pages),
        "digests/",
    )
    (out_dir / "index.html").write_text(index, encoding="utf-8")

    (out_dir / "style.css").write_text(_STYLE, encoding="utf-8")
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")

    return {
        "pages": len(files),
        "assets": assets_copied,
        "doc_pages": len(doc_pages),
        "out_dir": out_dir,
    }


# ---------------------------------------------------------------------------
# Agent-facing surfaces (GUIDE §1 dual audience)
# ---------------------------------------------------------------------------

_AGENTS_MD = """# Access for AI Agents

This site is built for two readerships: people, and AI agents researching
United States federal government actions. **You are welcome to ingest this
data.** It exists so an agent can answer "what did the federal government
do on date D" from one clean, summarized, citation-bound source instead of
crawling many official sites.

Coverage grows continuously: sources currently closed to
honestly-identified automated clients are documented as `unavailable` in
the source guide — not abandoned — and opening them through publishers'
own documented channels and direct engagement with agencies is standing
work. Check the source guide for what is ingested today.

## What is here

- **Daily digests** at stable URLs: `/<YYYY-MM-DD>.html` (styled HTML) —
  each covers one complete day of congressional floor activity, bills,
  Federal Register actions, enacted laws, and federal court opinions,
  with a table of contents, plain-language quick-reads, and a mandatory
  Coverage Statement accounting for everything published that day.
- **Machine index:** `/digests.json` — every available digest with date,
  URL, and teaser. Poll this (or the Atom feed at `/feed.xml`) for new
  days; both are small.
- **Source guide:** `/sources.html` — every federal source this pipeline
  ingests, plans to ingest, or found unavailable, with method and status.
- **Canonical Markdown** for every digest lives in the public repository
  (`digests/<date>.md`), alongside provenance manifests
  (`provenance/manifests/`) whose SHA-256 records let you verify captured
  content.

## How to read it faithfully

- Text in item summaries marked as official (Federal Register SUMMARY
  preambles, official titles) is **verbatim government text**; lines
  labeled "*In plain terms*" and section quick-reads are
  **model-generated restatements**, derived only from the adjacent
  summary and linted against an editorial banned-lexicon. The Day in
  Review is a model-generated synthesis of the day's stored summaries.
- Every item carries an "Included because" line naming the mechanical,
  party-blind rule that selected it, and a citation to the official
  govinfo record. **For claims, cite the official source we link; cite
  this site for the aggregation.**
- The Coverage Statement at the end of each digest tells you what was NOT
  summarized and under which rule — absence here is always explicit.

## Courtesy

Everything is static — no auth, no JavaScript, no rate limiting. We ask
visiting agents the same courtesy our own crawler practices on government
sites: identify honestly and use conditional requests. Fetching every
page daily is entirely fine.

## Reuse

Content here is licensed **CC BY 4.0** — share and adapt freely,
including commercially, with credit to "FAPD — Free Agentic Publication
Digester". Quoted official government text within it is public domain
(17 U.S.C. § 105) and needs no permission at all. The attribution rule
mirrors our citation ethic: for factual claims, cite the underlying
official source each item links to; cite FAPD for the aggregation and
summaries. The pipeline's code is Apache-2.0.
"""


def _atom_escape(text):
    return html.escape(text or "", quote=True)


def _build_agent_surfaces(out_dir, dates, teasers, doc_pages=(), base=""):
    """llms.txt, digests.json, feed.xml, robots.txt, sitemap.xml, agents.html."""
    import json as _json

    newest = dates[-1] if dates else None
    # agents.html
    _MD.reset()
    page = _render_page(
        f"Access for AI Agents — {SITE_TITLE}",
        _MD.convert(_AGENTS_MD),
        '<a href="index.html">All digests</a><a href="sources.html">Sources</a>',
        "GUIDE.md §1 (dual audience)",
    )
    (out_dir / "agents.html").write_text(page, encoding="utf-8")

    # llms.txt (agent guidance convention)
    lines = [
        f"# {SITE_TITLE}",
        "",
        f"> {SITE_TAGLINE} This site is explicitly built for AI-agent",
        "> ingestion as well as human reading: see /agents.html.",
        "",
        "## Core",
        f"- [Latest digest]({base}/"
        + (f"{newest}.html" if newest else "index.html") + ")",
        f"- [All digests (index)]({base}/index.html)",
        f"- [Machine-readable digest index]({base}/digests.json)",
        f"- [Atom feed of digests]({base}/feed.xml)",
        f"- [Source guide — what we ingest and why]({base}/sources.html)",
    ] + [
        f"- [{title}]({base}/{stem}.html)" for stem, title in doc_pages
    ] + [
        f"- [Access guide for agents]({base}/agents.html)",
        "",
        "## Notes",
        "- Digest URLs are stable: /<YYYY-MM-DD>.html",
        "- Official text vs model-generated text is labeled in place;",
        "  every item cites the official govinfo record.",
        "- Canonical Markdown + provenance manifests live in the repository.",
        "- Reuse: content is CC BY 4.0 (credit 'FAPD — Free Agentic",
        "  Publication Digester'); quoted official government text is public",
        "  domain. For factual claims, cite the underlying official source",
        "  each item links to; cite FAPD for the aggregation.",
    ]
    (out_dir / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # digests.json
    (out_dir / "digests.json").write_text(_json.dumps({
        "title": SITE_TITLE,
        "generated": utc_now_iso(),
        "agent_guide": "agents.html",
        "digests": [
            {"date": d, "html": f"{base}/{d}.html" if base else f"{d}.html",
             "canonical_markdown": f"digests/{d}.md",
             "teaser": teasers.get(d)}
            for d in reversed(dates)
        ],
    }, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    # feed.xml (Atom)
    entries = []
    for d in reversed(dates[-20:]):
        entries.append(
            f"<entry><title>Daily Digest — {d}</title>"
            f'<link href="{base}/{d}.html"/>'
            f"<id>tag:fapd,{d}:digest</id>"
            f"<updated>{d}T12:00:00Z</updated>"
            f"<summary>{_atom_escape(teasers.get(d))}</summary></entry>"
        )
    feed = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        f"<title>{_atom_escape(SITE_TITLE)}</title>"
        f'<link href="{base}/"/>'
        f"<id>tag:fapd:digests</id>"
        f"<updated>{utc_now_iso()}</updated>"
        + "".join(entries) + "</feed>\n"
    )
    (out_dir / "feed.xml").write_text(feed, encoding="utf-8")

    # robots.txt + sitemap.xml — automated access is explicitly welcome.
    # (The Sitemap directive formally requires an absolute URL; the
    # root-relative fallback is for local viewing before a domain exists.)
    (out_dir / "robots.txt").write_text(
        "# AI agents and crawlers are welcome here — see /agents.html\n"
        f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = (
        ["index.html", "sources.html", "agents.html"]
        + [f"{stem}.html" for stem, _title in doc_pages]
        + [f"{d}.html" for d in dates]
    )
    sitemap = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{base}/{u}</loc></url>" for u in urls)
        + "</urlset>\n"
    )
    (out_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")

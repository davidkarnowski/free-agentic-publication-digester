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

REPO_URL = ("https://github.com/davidkarnowski/"
            "free-agentic-publication-digester")

_MD = markdown.Markdown(extensions=["tables", "toc"])

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow">
<link rel="alternate" type="text/plain" href="llms.txt"
      title="LLM guide — this is an AI-first digest of official US federal publications">
<link rel="stylesheet" href="style.css">
{head_extra}</head>
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
  <code>{canonical}</code> in the
  <a href="{repo_url}">public repository</a>. Selection is mechanical and
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
/* Branch colors — deliberately not the red/blue party palette. */
.tag-branch-legislative {
  background: rgba(99, 102, 241, 0.14); color: #5a5fd0;
  border-color: rgba(99, 102, 241, 0.55);
}
.tag-branch-executive {
  background: rgba(13, 148, 136, 0.14); color: #0f9488;
  border-color: rgba(13, 148, 136, 0.55);
}
.tag-branch-judicial {
  background: rgba(217, 119, 6, 0.14); color: #c07207;
  border-color: rgba(217, 119, 6, 0.55);
}
.tag-branch-cross {
  background: rgba(107, 114, 128, 0.14);
  border-color: rgba(107, 114, 128, 0.55);
}
@media (prefers-color-scheme: dark) {
  .tag-branch-legislative { color: #9fa0f2; }
  .tag-branch-executive { color: #2dd4bf; }
  .tag-branch-judicial { color: #fbbf24; }
}
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
.today-disclosure {
  border: 1px solid var(--rule); border-left: 3px solid var(--accent);
  padding: 0.6rem 0.85rem; font-size: 0.88rem; color: var(--muted);
  border-radius: 4px;
}
.today-meta { font-size: 0.85rem; color: var(--muted); }
.today-list { list-style: none; padding-left: 0; }
.today-item { margin: 0.55rem 0; }
.today-time {
  font-family: ui-monospace, monospace; font-size: 0.78rem;
  color: var(--muted); margin-right: 0.35rem;
}
/* Local time is appended client-side beside the server-rendered UTC
   stamp; with scripting off, the UTC stamp simply stands alone. */
.localtime { color: var(--muted); font-size: 0.78rem; }
.today-summary { margin: 0.2rem 0 0 2.4rem; font-size: 0.92rem; }
.today-opening { color: var(--muted); }
.today-chips { margin: 0.15rem 0 0.1rem; }
.today-chips .tag { margin-right: 0.25rem; }
.today-item-meta {
  margin-left: 2.4rem; font-size: 0.78rem; color: var(--muted);
  overflow-wrap: anywhere;
}
/* Keyword filter (pure CSS :target — the site stays JavaScript-free).
   The per-keyword rules are generated into today.html's own <style>. */
/* Visually hidden but focusable: keyboard users still reach every chip. */
.filter-cb {
  position: absolute; width: 1px; height: 1px;
  opacity: 0; pointer-events: none;
}
.filter-bar {
  border: 1px solid var(--border); border-radius: 6px;
  background: var(--stripe); padding: 0.6rem 0.75rem; margin: 1rem 0;
}
.filter-lead {
  margin: 0 0 0.45rem; font-size: 0.85rem; font-weight: 600;
}
.filter-chip { cursor: pointer; text-decoration: none; }
.filter-n {
  margin-left: 0.35rem; opacity: 0.7; font-variant-numeric: tabular-nums;
}
.filter-clear {
  display: none; margin-left: 0.6rem; font-size: 0.78rem; font-weight: 400;
  padding: 0.1rem 0.6rem; border: 1px solid var(--border); border-radius: 999px;
  background: var(--card); color: var(--accent); cursor: pointer;
  font-family: inherit;
}
.filter-row { margin-top: 0.35rem; line-height: 2.1; }
.filter-branches {
  padding-bottom: 0.4rem; margin-bottom: 0.1rem;
  border-bottom: 1px dashed var(--border);
}
.filter-chip, .chip-toggle { cursor: pointer; user-select: none; }
.chip-toggle:hover { border-color: var(--accent); }
.filter-note {
  display: block; margin-top: 0.4rem; font-size: 0.75rem; color: var(--muted);
}
@media print {
  /* never print a filtered subset that could read as the whole day */
  .today-item { display: list-item !important; }
  .filter-bar { display: none; }
}
.live-callout {
  border: 1px solid var(--border); border-left: 3px solid #0f9488;
  border-radius: 4px; background: var(--card);
  padding: 0.6rem 0.85rem; font-size: 0.92rem;
}
.live-callout a { font-weight: 650; text-decoration: none; }
.live-callout a:hover { text-decoration: underline; }
.live-dot {
  display: inline-block; width: 0.55em; height: 0.55em;
  border-radius: 50%; background: #0f9488; margin-right: 0.4em;
}
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


# The three branches get stable colors everywhere tags render. The hues
# deliberately avoid the red/blue party palette — selection is party-blind
# and the presentation must not imply otherwise.
_BRANCH_CHIP_CLASSES = {
    "legislative": "tag-branch-legislative",
    "executive": "tag-branch-executive",
    "judicial": "tag-branch-judicial",
    "cross-branch": "tag-branch-cross",
}


def _tag_classes(text, extra_class=""):
    """Chip classes for a tag — branch tags carry their site-wide color
    wherever they appear, listing entry or filter control."""
    classes = "tag"
    branch = _BRANCH_CHIP_CLASSES.get(text.strip().lower())
    if branch:
        classes += f" {branch}"
    if extra_class:
        classes += f" {extra_class}"
    return classes


def _tag_chip(text, extra_class="", title=""):
    classes = _tag_classes(text, extra_class)
    title_attr = f' title="{html.escape(title)}"' if title else ""
    return f'<span class="{classes}"{title_attr}>{html.escape(text)}</span>'


def _chip_tags(html_body):
    """`Tags: a · b · model keys: x · y` paragraphs become chip rows; the
    model-derived keys keep their in-place label as a visually distinct
    chip class (GUIDE §2 labeling carried into the presentation), and
    branch tags carry their site-wide colors."""

    def _sub(match):
        text = match.group(1)
        mech_part, _, model_part = text.partition("model keys:")
        chips = [_tag_chip(t.strip())
                 for t in mech_part.split("·") if t.strip()]
        chips += [_tag_chip(t.strip(), "tag-model", "model-generated key")
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


_A_TAG_RE = re.compile(r"<a\b([^>]*)>", re.IGNORECASE)
_HREF_ATTR_RE = re.compile(r'href="([^"]*)"', re.IGNORECASE)


def _site_host(base=None):
    from urllib.parse import urlsplit

    host = urlsplit(base if base is not None else config.SITE_BASE_URL).netloc
    return host.lower().removeprefix("www.")


def _externalize_links(page_html, base=None):
    """Every link that leaves this site opens in a new tab — a reader
    following a citation to the official record never loses the digest
    they were reading. Applied to whole rendered pages (one seam, so
    Markdown-authored citation links, hand-built cards, and the footer
    all obey the same rule). Same-site links, fragments, and non-HTTP
    schemes such as mailto: keep default behavior; `rel` blocks the
    opened page's access to ours and its referrer."""
    from urllib.parse import urlsplit

    site = _site_host(base)

    def _sub(match):
        attrs = match.group(1)
        if "target=" in attrs.lower():
            return match.group(0)
        href = _HREF_ATTR_RE.search(attrs)
        if not href:
            return match.group(0)
        parts = urlsplit(href.group(1))
        if parts.scheme.lower() not in ("http", "https"):
            return match.group(0)
        if site and parts.netloc.lower().removeprefix("www.") == site:
            return match.group(0)
        return f'<a{attrs} target="_blank" rel="noopener noreferrer">'

    return _A_TAG_RE.sub(_sub, page_html)


def _render_page(title, body_html, nav_links, canonical, description=None,
                 head_extra=""):
    return _externalize_links(_PAGE.format(
        title=html.escape(title),
        head_extra=head_extra,
        description=html.escape(
            description
            or f"{SITE_TAGLINE} Built for human readers and AI agents;"
               " agents start at /llms.txt."),
        nav_links=nav_links,
        body=body_html,
        generated=utc_now_iso(),
        canonical=html.escape(canonical),
        repo_url=REPO_URL,
    ))


# Compact nav labels where a stem's .capitalize() reads badly.
_NAV_LABELS = {"ai-development": "AI development"}


def _doc_nav_links(doc_pages):
    """Nav anchors for the docs/site explanatory pages (About, Methods, …)."""
    return "".join(
        f'<a href="{stem}.html">'
        f'{html.escape(_NAV_LABELS.get(stem, stem.capitalize()))}</a>'
        for stem, _title in doc_pages
    )


def _registry_exists():
    """Whether sources.html will exist — the source guide is rendered from
    the registry, so an absent registry means no page to link to."""
    return (config.PROJECT_ROOT / "sources" / "registry.yaml").exists()


def _site_nav(doc_pages=(), *, skip_stem=None, current=None):
    """The site header, identical everywhere (operator, 2026-07-30): the
    digest archive, the live view, the source guide, every explanatory
    page, and the agent guide. `current` omits the page's own link, and
    a link is never emitted for a page that was not built."""
    links = []
    if current != "index":
        links.append('<a href="index.html">All digests</a>')
    if current != "today":
        links.append('<a href="today.html">Today (live)</a>')
    if current != "sources" and _registry_exists():
        links.append('<a href="sources.html">Sources</a>')
    links.append(_doc_nav_links(p for p in doc_pages if p[0] != skip_stem))
    if current != "agents":
        links.append('<a href="agents.html">For agents</a>')
    return "".join(links)


def _nav_for(dates, i, doc_pages=()):
    links = []
    if i > 0:
        links.append(f'<a href="{dates[i - 1]}.html">&larr; {dates[i - 1]}</a>')
    if i < len(dates) - 1:
        links.append(f'<a href="{dates[i + 1]}.html">{dates[i + 1]} &rarr;</a>')
    links.append(_site_nav(doc_pages))
    return "".join(links)


# README → site link rewriting: repo-relative links that have a site
# equivalent are pointed at it; the rest degrade to plain code text (the
# canonical footer links the public repository).
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


def _doc_sources():
    """[(markdown, stem, title, canonical)] for every explanatory page —
    docs/site/*.md plus the repo README. Separated from rendering so any
    page (notably the independently-rebuilt /today) can construct the
    same navigation without re-rendering the site."""
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
    return docs


def _doc_page_index():
    """[(stem, title)] — the nav's view of the explanatory pages."""
    return [(stem, title) for _t, stem, title, _c in _doc_sources()]


def _build_doc_pages(out_dir):
    """Render every explanatory page to site/<stem>.html; returns the
    (stem, title) index. Absent sources simply yield no pages."""
    docs = _doc_sources()
    doc_pages = [(stem, title) for _t, stem, title, _c in docs]
    brand = SITE_TITLE.split(" — ")[0]
    for md_text, stem, title, canonical in docs:
        _MD.reset()
        body = _MD.convert(md_text)
        page = _render_page(
            # No brand suffix when the page title already carries it (README)
            title if brand in title else f"{title} — {SITE_TITLE}",
            body,
            _site_nav(doc_pages, skip_stem=stem),
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
        _site_nav(doc_pages, current="sources"),
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
    live_callout = (
        '<p class="live-callout"><a href="today.html">'
        '<span class="live-dot"></span>Today — live</a> '
        "watch official publications arrive through the day, newest first "
        "(preliminary until the end-of-day digest freezes the record).</p>"
    )
    index_body = (
        f"<h1>{html.escape(SITE_TITLE)}</h1>"
        f'<p class="tagline">{html.escape(SITE_TAGLINE)}</p>'
        f"{live_callout}"
        f"{sources_link}"
        f'<ul class="digest-list">{"".join(cards)}</ul>'
    )
    index = _render_page(
        SITE_TITLE, index_body,
        _site_nav(doc_pages, current="index"),
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
# /today — the live in-progress day (GUIDE §5 two-artifact model)
# ---------------------------------------------------------------------------

# Mandatory disclosure wording (GUIDE §5, amended 2026-07-30). The page is
# derived-only and never committed; the dated digest is the record.
_TODAY_DISCLOSURE = (
    "This page is preliminary. Items may be re-dated, re-summarized, or "
    "excluded by the end-of-day editorial gates; the dated digest is the "
    "record. The Day in Review and section synopses are composed at end "
    "of day and do not appear here."
)

# Journal collection -> the label each stream entry leads with (the
# stream is one chronological listing, so items self-describe).
_TODAY_COLLECTION_LABELS = {
    "CREC": "Congressional Record",
    "BILLS": "Legislation",
    "PLAW": "Enacted law",
    "FR": "Federal Register",
    "USCOURTS": "Judicial opinion",
    "AGENCYPR": "Agency announcement",
}


# Mechanical per-item metadata (zero LLM). Branch by collection; document
# type expanded into plain words; channel from the journal source class.
_TODAY_BRANCH = {"CREC": "legislative", "BILLS": "legislative",
                 "PLAW": "legislative", "FR": "executive",
                 "USCOURTS": "judicial", "AGENCYPR": "executive"}
_TODAY_DOC_TYPES = {
    "RULE": "final rule", "PRORULE": "proposed rule", "NOTICE": "notice",
    "PRESDOCU": "presidential document", "SENATE": "senate floor",
    "HOUSE": "house floor", "EXTENSIONS": "extensions of remarks",
    "DAILYDIGEST": "daily digest", "PRESS": "press release",
}


def _et_clock(utc_stamp):
    """HH:MM:SS in Washington for a stored UTC stamp — the clock the
    publishers keep, to the second we actually recorded. The
    machine-readable UTC value stays in the element's datetime
    attribute, and the page's one script appends the reader's own local
    time beside it."""
    import datetime as _dt

    try:
        when = _dt.datetime.fromisoformat(utc_stamp)
    except ValueError:
        return utc_stamp[11:19]
    return when.astimezone(config.PUBLICATION_TZ).strftime("%H:%M:%S")


def _today_doc_label(item):
    if item["collection"] == "USCOURTS":
        return "court opinion"
    if item["collection"] == "PLAW":
        return "public law"
    if item["collection"] == "BILLS":
        v = (item["doc_type"] or "").lower()
        return f"bill text ({v})" if v else "bill text"
    dt_ = item["doc_type"] or ""
    return _TODAY_DOC_TYPES.get(dt_, dt_.lower() or "document")


def _today_item_tags(item):
    """Mechanical tags: branch, plain-words document type, and the agency
    (FR metadata) or the source's registry stem (agency/email classes).
    The model discovery-key layer for items stays backlogged; nothing
    here costs a token."""
    tags = [_TODAY_BRANCH.get(item["collection"], "cross-branch"),
            _today_doc_label(item)]
    if item["agency"]:
        tags.append(item["agency"].strip().lower())
    elif item["source_id"]:
        tags.append(item["source_id"].split("-")[0])
    return list(dict.fromkeys(t for t in tags if t))


def _today_official_url(item):
    """Best official link we can construct without a request: the item's
    own captured URL for agency items, the govinfo details page for
    govinfo collections, none for URL-less email bulletins."""
    if item["url"]:
        return item["url"]
    if item["source_class"] == "govinfo":
        base = f"https://www.govinfo.gov/app/details/{item['package_id']}"
        return base + (f"/{item['granule_id']}" if item["granule_id"] else "")
    return None


def _today_channel_label(item):
    if item["source_class"] == "govinfo":
        return "govinfo API"
    if item["channel"] == "email":
        verified = " (DKIM-verified)" if item["dkim_result"] == "pass" else ""
        return f"email bulletin{verified}"
    return "web feed"


def _entry_tag_chip(tag, filterable):
    """An entry's tag is a control when the day offers it as a filter:
    a <label> for the very checkbox the filter bar drives, so clicking a
    tag on an entry and clicking it in the bar are the same act and the
    two stay in sync with no state of their own. Tags outside the
    offered set stay inert spans rather than dead controls."""
    slug = _slug(tag)
    if slug in filterable:
        return (f'<label class="{_tag_classes(tag, "chip-toggle")}" '
                f'for="f-{slug}">{html.escape(tag)}</label>')
    return _tag_chip(tag)


def _today_item_row(item, filterable=()):
    title = (item["title"] or "").strip() or item["package_id"]
    gran = item["granule_id"]
    cite = item["package_id"] + (f" / {gran}" if gran else "")
    stamp = item["observed_at"] or ""
    observed = (f'<time class="utc" datetime="{html.escape(stamp)}">'
                f"{html.escape(_et_clock(stamp))} ET</time>" if stamp else "")
    url = _today_official_url(item)
    title_html = (f'<a href="{html.escape(url)}">{html.escape(title)}</a>'
                  if url else html.escape(title))
    chips = "".join(_entry_tag_chip(t, filterable)
                    for t in _today_item_tags(item))

    coll_label = _TODAY_COLLECTION_LABELS.get(
        item["collection"], item["collection"] or "publication")
    meta_bits = [coll_label, _today_channel_label(item)]
    if item["agency"]:
        meta_bits.append(item["agency"].strip())
    elif item["source_id"]:
        meta_bits.append(item["source_id"])
    meta_bits.append(cite)
    if item["claimed_published_at"]:
        meta_bits.append(f"publisher-dated {item['claimed_published_at']}")
    meta = html.escape(" · ".join(meta_bits))

    if item["summary"]:
        label = ("official summary" if item["summary_method"] == "official"
                 else "model summary")
        rule = (f' <span class="rule-note">{html.escape(item["inclusion_rule"])}'
                "</span>" if item["inclusion_rule"] else "")
        body = (f'<p class="today-summary"><span class="plain-label">'
                f"{label}:</span> {html.escape(item['summary'])}{rule}</p>")
    elif item["opening"]:
        snippet = " ".join(item["opening"].split())
        if len(snippet) > 200:
            snippet = snippet[:200].rsplit(" ", 1)[0] + "…"
        body = (f'<p class="today-summary today-opening">'
                f'<span class="plain-label">opening text (verbatim):</span> '
                f"{html.escape(snippet)}</p>")
    else:
        body = ""
    # Keyword classes drive the CSS :target filter (no JavaScript).
    keys = " ".join(f"k-{_slug(t)}" for t in _today_item_tags(item))
    return (
        f'<li class="today-item {keys}">'
        f'<span class="today-time">{observed}</span> '
        f"<strong>{title_html}</strong> "
        f'<span class="today-chips">{chips}</span>'
        f'<div class="today-item-meta">{meta}</div>{body}</li>'
    )


# Keyword filtering on /today is pure CSS, so the site stays script-free.
# The state lives in hidden checkboxes rather than URL fragments (:target,
# used until 2026-07-30): a fragment link makes the browser scroll to the
# anchor, and it cannot be un-clicked. A checkbox toggles off when its
# chip is clicked again, moves the viewport not at all, and a native
# reset button clears every selection without a line of JavaScript.
# Selecting several keywords narrows to items carrying all of them.
# Safety ceiling only — the bar lists every keyword the day produced
# (operator, 2026-07-30: "a full listing, not a truncated listing").
# If a day ever exceeded this the bar would say so in place.
MAX_FILTER_KEYWORDS = 400
_BRANCH_ORDER = ("legislative", "executive", "judicial", "cross-branch")


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _today_filter_facets(items):
    """keyword -> count, ordered by count then name. Mechanical tags only
    (branch, document type, agency): model-generated discovery keys are
    section-level, so they cannot honestly filter individual items."""
    counts = {}
    for item in items:
        for tag in _today_item_tags(item):
            counts[tag] = counts.get(tag, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def _today_filter_pairs(items):
    """keyword -> the keywords that share an entry with it (including
    itself). This is what lets the bar narrow itself: once a keyword is
    chosen, any keyword that never appears alongside it could only
    produce an empty stream, so the bar stops offering it.

    Carried as classes rather than per-pair CSS rules on purpose. Naming
    the pairs that DO occur costs one class per real pairing (each entry
    has about three tags), while ruling out the pairs that do not would
    cost a rule per absent pair — quadratic in the day's keyword count.
    Measured on 2026-07-30: 291 entries, 58 keywords, 292 real pairings
    (~6.6 KB of classes, 58 rules) against 3,364 possible pairs.

    Known limit: narrowing is pairwise. With two keywords chosen, the bar
    hides anything that pairs with neither, but a keyword that pairs with
    each of them separately — on different entries — stays on offer and
    can still yield an empty stream. Exactness would need a rule per
    combination, which is the explosion this design avoids; the reset
    button is always one click away."""
    pairs = {}
    for item in items:
        tags = _today_item_tags(item)
        for tag in tags:
            pairs.setdefault(tag, set()).update(tags)
    return pairs


def _filter_chip(tag, count, pairs=None):
    """A chip is a <label> for its hidden checkbox, wearing exactly the
    classes the same tag wears on a listing entry — so a branch keeps its
    color whether you are reading it or filtering by it — plus one class
    per keyword it shares an entry with, which drives the narrowing."""
    partners = "".join(f" c-{_slug(p)}"
                       for p in sorted((pairs or {}).get(tag, {tag})))
    return (f'<label class="{_tag_classes(tag, "filter-chip")}{partners}" '
            f'for="f-{_slug(tag)}">{html.escape(tag)}'
            f'<span class="filter-n">{count}</span></label>')


def _today_filter_bar(facets, total, pairs=None):
    """(inputs, bar_html, css) for the day's keywords: branches on their
    own row, then every remaining keyword in one full listing. Choosing
    a keyword narrows the offered set to keywords that actually share an
    entry with it, so no combination on offer leads to an empty page."""
    offered = list(facets.items())[:MAX_FILTER_KEYWORDS]
    dropped = len(facets) - len(offered)
    if not offered:
        return "", "", ""

    inputs, css = [], []
    for tag, _n in offered:
        slug = _slug(tag)
        inputs.append(f'<input type="checkbox" class="filter-cb" id="f-{slug}">')
        css.append(
            f"#f-{slug}:checked ~ .today-list > .today-item:not(.k-{slug})"
            "{display:none}\n"
            f'#f-{slug}:checked ~ .filter-bar label[for="f-{slug}"],\n'
            f'#f-{slug}:checked ~ .today-list label[for="f-{slug}"]'
            "{background:var(--accent);color:#fff;border-color:var(--accent)}\n"
            f'#f-{slug}:focus-visible ~ .filter-bar label[for="f-{slug}"]'
            "{outline:2px solid var(--accent);outline-offset:2px}\n"
            f"#f-{slug}:checked ~ .filter-bar .filter-clear"
            "{display:inline-block}\n"
            # narrow the remaining options to keywords seen alongside this one
            f"#f-{slug}:checked ~ .filter-bar label:not(.c-{slug})"
            "{display:none}\n")

    branches = [(t_, n) for t_, n in offered if t_ in _BRANCH_ORDER]
    branches.sort(key=lambda kv: _BRANCH_ORDER.index(kv[0]))
    rest = [(t_, n) for t_, n in offered if t_ not in _BRANCH_ORDER]

    rows = ""
    if branches:
        rows += ('<div class="filter-row filter-branches">'
                 + "".join(_filter_chip(t_, n, pairs) for t_, n in branches)
                 + "</div>")
    if rest:
        rows += ('<div class="filter-row">'
                 + "".join(_filter_chip(t_, n, pairs) for t_, n in rest)
                 + "</div>")
    note = (f'<span class="filter-note">Showing {len(offered)} of '
            f"{len(facets)} keywords.</span>" if dropped else "")
    bar = (
        '<nav class="filter-bar" aria-label="Filter the stream by keyword">'
        '<p class="filter-lead">Filter by keyword '
        '<span class="rule-note">click to select, click again to clear — '
        "here or on any entry's own tags · choosing several narrows to "
        "items carrying all of them, and the remaining keywords narrow "
        "to those that appear alongside your choice · counts are for the "
        "unfiltered day · "
        f"{total} item(s) unfiltered</span>"
        '<button type="reset" class="filter-clear">clear filters</button></p>'
        f"{rows}{note}</nav>"
    )
    return "".join(inputs), bar, "".join(css)


# The site's one script (operator request, 2026-07-30): UTC stamps are
# server-rendered and complete on their own; this only APPENDS the
# reader's local equivalent. Inline (no external resource, nothing to
# block), no network, no storage, no cookies, no tracking — with
# scripting off the page is exactly what it was before.
_LOCAL_TIME_JS = """<script>
(function () {
  var f;
  try {
    f = new Intl.DateTimeFormat(undefined,
      {hour: "2-digit", minute: "2-digit", second: "2-digit",
       timeZoneName: "short"});
  } catch (e) { return; }
  document.querySelectorAll("time.utc[datetime]").forEach(function (el) {
    var d = new Date(el.getAttribute("datetime"));
    if (isNaN(d)) { return; }
    var s = document.createElement("span");
    s.className = "localtime";
    s.textContent = " (" + f.format(d) + ")";
    el.after(s);
  });
})();
</script>
"""


def build_today(conn, out_dir=None, date=None):
    """Render site/today.html + today.json from collect.today_status —
    mechanical, zero LLM, derived-only (never committed; gitignored).
    Empty days render on purpose: disclosure, then 'no items yet'."""
    import json as _json

    from .collect import today_status

    out_dir = Path(out_dir or config.SITE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    from .sync import publication_date
    date = date or publication_date()
    status = today_status(conn, date)
    now = utc_now_iso()

    # Day-so-far chips (GUIDE §6 r12a): the date's stored section tags,
    # rolled into one row above the stream — the stream itself is one
    # chronological listing, so each item self-describes instead of
    # sitting under a section heading. Present once the tag layer has
    # run for the date; absent (not faked) before that.
    from .tags import get_section_tags
    stored = get_section_tags(conn, date)
    mech, model = [], []
    for bucket in stored.values():
        mech += bucket.get("mechanical", [])
        model += bucket.get("llm", [])
    day_chips = [_tag_chip(t) for t in dict.fromkeys(mech)]
    day_chips += [_tag_chip(t, "tag-model", "model-generated discovery key")
                  for t in dict.fromkeys(model)]

    recent = sorted(
        (p.stem for p in Path(config.DIGEST_DIR).glob("*.md")
         if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem)), reverse=True)[:3]
    recent_links = " · ".join(f'<a href="{d}.html">{d}</a>' for d in recent)
    intro = (
        "<p>This is the <strong>live view</strong> of the Free Agentic "
        "Publication Digester: official United States federal publications "
        "as our collectors observe them, newest first. Sources are polled "
        "continuously — the govinfo API about every half hour, agency "
        "newsrooms about hourly, and agency email bulletins about every "
        "fifteen minutes — and this page refreshes within minutes of a new "
        "arrival. Each entry shows the time we observed it, a link to the "
        "official record, the channel it arrived through, mechanical tags "
        "(branch of government, document type, agency), and either a "
        "labeled summary or the unedited opening words of the official "
        "text. Those tags are clickable: selecting one here or in the "
        "filter bar narrows the stream to matching entries, and picking "
        "several narrows to entries carrying all of them.</p>"
        "<p><strong>About the dates and times on this page.</strong> A "
        "publication day here runs on <strong>Eastern time in "
        "Washington, D.C.</strong> — the clock the publishers themselves "
        "keep, from the Federal Register's morning release to the close "
        "of floor proceedings. This page therefore covers midnight to "
        "midnight Eastern, and rolls over to the next day at midnight "
        "Eastern. Times are shown in Eastern; if your browser runs "
        "scripts, your own local time appears beside each one. The "
        "underlying timestamps are UTC and are readable in the page "
        "markup and in today.json.</p>"
        "<p>For whole-day context, read the <strong>dated digests</strong> — "
        "each one a validated, frozen record of a complete publication day "
        "with plain-language summaries, coverage accounting, and a Day in "
        f"Review. Most recent: {recent_links} · "
        '<a href="index.html">all digests</a>. AI agents: start at '
        '<a href="llms.txt">/llms.txt</a>.</p>'
    ) if recent_links else (
        "<p>This is the live view: official federal publications as our "
        "collectors observe them, newest first. Dated, validated digests "
        'are on the <a href="index.html">main page</a>.</p>')
    parts = [
        f"<h1>Today — {date} (in progress)</h1>",
        f'<p class="today-disclosure">{html.escape(_TODAY_DISCLOSURE)}</p>',
        intro,
        (f'<p class="today-meta">Last updated <time class="utc"'
         f' datetime="{html.escape(now)}">{html.escape(_et_clock(now))} ET'
         f"</time> · {len(status['items'])} item(s) observed so far · "
         f"{status['pending_llm']} item(s) awaiting model summary.</p>"),
    ]
    if day_chips:
        parts.append('<p class="today-chips">Day so far: '
                     + "".join(day_chips) + "</p>")
    facets = _today_filter_facets(status["items"])
    inputs, filter_bar, filter_css = _today_filter_bar(
        facets, len(status["items"]), _today_filter_pairs(status["items"]))
    filterable = {_slug(k) for k in list(facets)[:MAX_FILTER_KEYWORDS]}
    if not status["items"]:
        parts.append("<p>No items observed yet for this publication day. "
                     "Collectors poll continuously; check back.</p>")
    else:
        # The form is what makes filtering work without script: the
        # checkboxes, the bar, and the stream are siblings inside it (so
        # the CSS sibling combinator reaches the list), and its native
        # reset button clears every selection at once. One chronological
        # stream, newest first — no section headings; every entry names
        # its own branch, agency, and document type.
        parts.append(
            '<form class="today-stream" action="today.html" method="get">'
            + inputs + filter_bar
            + '<ul class="today-list">'
            + "".join(_today_item_row(i, filterable)
                      for i in status["items"])
            + "</ul></form>")

    nav = _site_nav(_doc_page_index(), current="today")
    head_extra = (f"<style>\n{filter_css}</style>\n" if filter_css else "")
    head_extra += _LOCAL_TIME_JS
    page = _render_page(f"Today (live) — {SITE_TITLE}", "".join(parts), nav,
                        "derived-only: not part of the committed record",
                        head_extra=head_extra)
    (out_dir / "today.html").write_text(page, encoding="utf-8")

    json_items = []
    for i in status["items"]:
        row = {k: v for k, v in i.items() if k != "opening"}
        row["opening_verbatim"] = i["opening"]  # official text, unedited
        row["official_url"] = _today_official_url(i)
        row["channel_label"] = _today_channel_label(i)
        row["tags"] = _today_item_tags(i)       # mechanical, zero-LLM
        json_items.append(row)
    (out_dir / "today.json").write_text(_json.dumps({
        "date": date,
        "generated": now,
        "disclosure": _TODAY_DISCLOSURE,
        "canonical_record": "the dated digest, frozen at end of day",
        "labels": {"summary_method": "official = agency/GPO text;"
                                     " llm = model-generated, labeled",
                   "opening_verbatim": "first ~240 chars of the official"
                                       " text, unedited",
                   "tags": "mechanical (branch, document type, agency);"
                           " no model-generated item tags yet"},
        "counts": status["counts"],
        "facets": {"tags": facets,
                   "note": "filter items client-side on items[].tags;"
                           " the human page offers the same keywords as"
                           " toggles"},
        "pending_llm": status["pending_llm"],
        "last_observed_at": status["last_observed_at"],
        "items": json_items,
    }, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return {"date": date, "items": len(status["items"]),
            "pending_llm": status["pending_llm"], "out_dir": out_dir}


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
  at
  [github.com/davidkarnowski/free-agentic-publication-digester](https://github.com/davidkarnowski/free-agentic-publication-digester)
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

Everything is static — no auth, no rate limiting, and nothing an
agent needs to execute. We ask
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
        _site_nav(doc_pages, current="agents"),
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
        (f"- [Today — live in-progress day, PRELIMINARY]({base}/today.html)"
         " (also /today.json, whose `facets.tags` gives keyword counts and"
         " whose items carry the same tags for client-side filtering."
         " Items may change until the end-of-day gates freeze the dated"
         " digest)"),
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
        ("- Canonical Markdown + provenance manifests live in the public"
         f" repository: {REPO_URL}"),
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
        "# AI agents and crawlers are welcome here — indexing is\n"
        "# encouraged. This is an AI-first digest of official US federal\n"
        "# publications, built for machine ingestion as much as human\n"
        "# reading.\n"
        "#   Agent guide:  /agents.html\n"
        "#   LLM guide:    /llms.txt\n"
        "#   Machine index: /digests.json   Atom: /feed.xml\n"
        "# /today.html is a PRELIMINARY live view; the dated digests are\n"
        "# the record.\n"
        f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = (
        ["index.html", "today.html", "sources.html", "agents.html"]
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

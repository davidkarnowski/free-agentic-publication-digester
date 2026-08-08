"""Static-site presentation layer: canonical Markdown digests -> site/.

Derived output only (GUIDE §5): zero LLM calls, regenerable at any time
from digests/*.md. Pages are plain HTML5 + one shared stylesheet, no
external resources, and exactly one script — _LOCAL_TIME_JS on the live
page, which appends the reader's local time beside published stamps and
loads/stores nothing (code-standards §2 r10). Everything renders
identically from the filesystem, GitHub Pages, or any static host.
"""

import html
import json as _json_mod
import re
import shutil
from pathlib import Path

import markdown

from . import config, sources
from . import health as health_mod
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
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <nav aria-label="Site">
    <a class="brand" href="index.html"
       aria-label="Free Agentic Publication Digester (FAPD)">FAPD<span
       class="brand-full"> &mdash; Free Agentic Publication Digester</span></a>
    <span class="nav-links">{nav_links}</span>
  </nav>
</header>
<main id="main" tabindex="-1">
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
  --accent-on: #ffffff;      /* text on an --accent fill: 8.66:1 */
  --control-border: #868f99; /* control boundary: 3.22:1 vs --bg */
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
    /* white on the dark accent measured 2.25:1 — the worst number on the
       site, and it carried the "which filters are on" signal. 8.46:1. */
    --accent-on: #0b1116;
    --control-border: #646f7a;   /* 3.61:1 vs --bg */
  }
}
* { box-sizing: border-box; }
/* Visually hidden but present for assistive technology: the one utility
   several accessibility fixes share. clip-path rather than clip, and a
   1px box rather than display:none, so the text stays in the
   accessibility tree and inside inline layout. */
.vh {
  position: absolute !important;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}
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
.skip-link {
  position: absolute; left: -9999px; top: 0; z-index: 10;
  padding: 0.5rem 0.9rem;
  background: var(--card); color: var(--accent);
  border: 2px solid var(--accent); border-radius: 0 0 6px 0;
  font-size: 0.95rem; text-decoration: none;
}
.skip-link:focus { left: 0; }
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
/* The acronym is always expanded in the header (branding rule). Lighter
   weight so the mark still reads as the mark, and it wraps rather than
   pushing the nav off a narrow screen. */
.brand-full { font-weight: 400; font-size: 0.92em; }
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
/* The live view is the site's most-visited destination; its link leads
   the nav and carries the live dot. Secondary pages collapse into a
   native <details> so twelve undifferentiated links stop wrapping into
   rows of grey text above every page's h1 (no JS — details is HTML). */
.nav-links a[href="today.html"] { color: var(--accent); font-weight: 600; }
.nav-more { display: inline-block; }
.nav-more summary {
  cursor: pointer; color: var(--muted); margin-left: 0.9rem;
  white-space: nowrap;
}
.nav-more summary:hover { text-decoration: underline; }
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
/* `display: block` on a <table> strips the table, row, and cell roles
   from the accessibility tree, so a counts table is announced as a flat
   run of numbers with no headers. The horizontal-scroll job moves to a
   wrapper element, which is also focusable so it can be scrolled from
   the keyboard (A11Y-03). */
table {
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.92rem;
}
.table-scroll { overflow-x: auto; margin: 1rem 0; }
.table-scroll:focus-visible {
  outline: 3px solid var(--accent); outline-offset: 2px;
}
/* The site's own focus indicator: the user-agent ring's contrast against
   --accent-soft and --card is not ours to control. --accent measures
   8.51:1 on --bg (light) and 8.24:1 (dark); :where() keeps specificity
   at zero so nothing existing is overridden. */
:where(a, button, summary, [tabindex]):focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
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
/* Filter chips are user interface components, so their boundary needs
   3:1 (1.4.11): --border measured 1.34:1. Also 2.5.8 Target Size — an
   entry chip computed 22.0 px tall, and the entry chips are the ones a
   reader taps while reading an item. 11.52 x 1.6 + 2 x 4.8 + 2 = 30.0 px.
   Placed BEFORE the branch block on purpose: equal specificity, so the
   branch rules' currentColor border must come later to win. */
.filter-chip, .chip-toggle {
  cursor: pointer; user-select: none;
  padding-top: 0.3rem; padding-bottom: 0.3rem;
  border-color: var(--control-border);
}
/* Branch colors — deliberately not the red/blue party palette. */
/* Light-theme hues darkened to clear 4.5:1 (measured 5.02-5.71:1); the
   hues themselves are unchanged, so branches stay off the party palette.
   currentColor borders also lift the 3:1 non-text contrast floor. */
.tag-branch-legislative {
  background: rgba(99, 102, 241, 0.14); color: #4448b8;
  border-color: currentColor;
}
.tag-branch-executive {
  background: rgba(13, 148, 136, 0.14); color: #0b6b62;
  border-color: currentColor;
}
.tag-branch-judicial {
  background: rgba(217, 119, 6, 0.14); color: #8a5206;
  border-color: currentColor;
}
.tag-branch-cross {
  background: rgba(107, 114, 128, 0.14);
  border-color: currentColor;
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
/* The section title IS the <summary>'s heading (A11Y-04): a closed
   <details> keeps its contents out of the accessibility tree, so a
   heading placed after the summary is invisible to heading navigation
   and the anchor id it carries scrolls to a collapsed section. Restated
   here so a real <h2> keeps the summary's compact look. */
h2.sec-title {
  font-size: 1.05rem; font-weight: 650;
  margin: 0; padding: 0; border: 0; color: inherit;
}
/* `/ ""` is CSS alternative text: the triangle stays visible and stops
   being announced as "black right-pointing small triangle" (A11Y-15). */
h2.sec-title::before { content: "\\25B8\\00a0" / ""; color: var(--accent);
  font-size: 0.85em; }
details.digest-section[open] h2.sec-title::before {
  content: "\\25BE\\00a0" / "";
}
summary .sec-blurb { font-size: 0.92rem; color: var(--fg); opacity: 0.85; }
details.digest-section > *:not(summary) { margin-left: 0.9rem; margin-right: 0.9rem; }
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
.plain-label::after { content: ":" / ""; }
/* Type styles apply wherever these appear; several call sites emit
   <span class="rule-note">, which the old li-only selector never
   reached, so those notes rendered at body size in full contrast. */
.rule-note, .source-note {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0.1rem 0;
}
li.rule-note, li.source-note { list-style: none; }
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
/* Source health indicators. State is ALWAYS carried by three signals at
   once — the word, a glyph, and the colour — because colour alone fails
   1.4.1, grayscale printing, and forced-colors mode. Contrast measured
   over the composited chip tint on both --card and --stripe, in both
   themes: worst case 4.93:1 (delivering on stripe, light). The tint hue
   stays constant across themes and only the text colour flips, the same
   pattern the branch chips use. Quiet and no-data keep the plain --muted
   chip and are distinguished by border style, because neither is an
   observation of trouble and neither should look like one. */
.tag-health-delivering {
  background: rgba(26, 107, 60, 0.14); color: #1a6b3c;
  border-color: currentColor;
}
.tag-health-degraded {
  background: rgba(138, 75, 0, 0.14); color: #8a4b00;
  border-color: currentColor;
}
.tag-health-no-response {
  background: rgba(154, 42, 30, 0.14); color: #9a2a1e;
  border-color: currentColor;
}
.tag-health-quiet { border-style: dashed; }
.tag-health-no-data { border-style: dotted; }
@media (prefers-color-scheme: dark) {
  .tag-health-delivering { color: #6ee7a5; }
  .tag-health-degraded { color: #fbbf24; }
  .tag-health-no-response { color: #f7a394; }
}
.health-glyph { margin-right: 0.25em; }
.src-stats {
  margin: 0.5rem 0 0; padding: 0.45rem 0.7rem;
  background: var(--stripe); border: 1px solid var(--border);
  border-radius: 6px; font-size: 0.82rem;
}
.src-stats p { margin: 0.12rem 0; }
.src-stat-label { color: var(--muted); }
.src-unmeasured { color: var(--muted); }
.health-lead { margin: 0.6rem 0; }
.health-note { font-size: 0.82rem; color: var(--muted); }
.today-disclosure {
  border: 1px solid var(--border); border-left: 3px solid var(--accent);
  padding: 0.6rem 0.85rem; font-size: 0.88rem; color: var(--muted);
  border-radius: 4px;
}
.today-meta { font-size: 0.85rem; color: var(--muted); }
.today-list { list-style: none; padding-left: 0; margin: 0 0 0.6rem; }
/* A real two-column grid: the time in its own track, the content in the
   other — actual alignment, replacing the old approximated 2.4rem
   left-margins. The border is what delimits one item from the next in a
   long stream. */
.today-item {
  display: grid; grid-template-columns: 5.2rem 1fr; gap: 0 0.6rem;
  margin: 0; padding: 0.45rem 0;
  border-bottom: 1px solid var(--border);
}
.today-item:last-child { border-bottom: 0; }
.today-time {
  font-family: ui-monospace, monospace; font-size: 0.78rem;
  color: var(--muted); padding-top: 0.15rem;
}
/* Local time is appended client-side beside the server-rendered UTC
   stamp; with scripting off, the UTC stamp simply stands alone. It
   lands inside .today-time, so the grid column holds both. */
.localtime { color: var(--muted); font-size: 0.78rem; }
.today-body { min-width: 0; }
.today-summary { margin: 0.2rem 0 0; font-size: 0.92rem; }
.today-opening { color: var(--muted); }
.today-chips { margin: 0.15rem 0 0.1rem; }
.today-chips .tag { margin-right: 0.25rem; }
.today-item-meta {
  font-size: 0.78rem; color: var(--muted);
  overflow-wrap: anywhere;
}
/* Hour headings inside the stream — scannable structure for a 300-item
   day, and a quiet evening visible as absence. */
.today-hour {
  margin: 1.1rem 0 0.2rem; padding: 0; border: 0;
  font-size: 0.78rem; font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--muted);
}
/* The collapsed how-it-works explainer. */
.today-about { margin: 0.6rem 0; }
.today-about summary {
  cursor: pointer; color: var(--accent); font-size: 0.9rem;
}
.today-context { margin: 0.6rem 0; }
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
/* The lead is a real heading (A11Y-13) so the filter is reachable by
   heading navigation on a page that otherwise had exactly one heading;
   the h2 defaults are restated away so the bar looks unchanged. */
h2.filter-lead {
  margin: 0 0 0.45rem; padding: 0; border: 0;
  font-size: 0.85rem; font-weight: 600; color: inherit;
}
.filter-chip { cursor: pointer; text-decoration: none; }
/* opacity: 0.7 over a tinted chip measured 2.11–3.10:1 (light) — the
   count inherits the chip's own compliant color instead (A11Y-05). */
.filter-n {
  margin-left: 0.4rem; font-weight: 600;
  font-variant-numeric: tabular-nums;
}
/* Which keywords are active, in words. Pre-rendered and revealed by CSS
   without any second script; on an engine without :has() the readout
   is simply absent, which shows the day unfiltered. */
.filter-status { margin: 0.4rem 0 0; font-size: 0.8rem; color: var(--muted); }
.filter-status > span { display: none; }
.today-stream:not(:has(.filter-cb:checked)) .fs-none { display: inline; }
.today-stream:has(.filter-cb:checked) .fs-lead { display: inline; }
/* A CSS counter over the items still displayed: counters do not
   increment for display:none elements, and counter scope reaches an
   element's following siblings, so a paragraph after the list can state
   how many survived the filter. Generated content, so it is a visual
   readout only — screen readers treat it inconsistently. The reset
   lives on the FORM, not the list: the stream is now several per-hour
   lists, and a per-list reset would count only the last one. */
.today-stream { counter-reset: shown 0; }
.today-list > .today-item { counter-increment: shown; }
.filter-count {
  margin: 0.5rem 0 0; font-size: 0.8rem; color: var(--muted);
}
.filter-count::after { content: counter(shown) " item(s) shown."; }
/* Always visible (was display:none until a box was checked): the escape
   hatch the bar's own prose promises must exist before it is needed. */
.filter-clear {
  margin-left: 0.6rem; font-size: 0.78rem; font-weight: 400;
  padding: 0.1rem 0.6rem; border: 1px solid var(--border); border-radius: 999px;
  background: var(--card); color: var(--accent); cursor: pointer;
  font-family: inherit;
}
.filter-row { margin-top: 0.35rem; line-height: 2.1; }
.filter-branches {
  padding-bottom: 0.4rem; margin-bottom: 0.1rem;
  border-bottom: 1px dashed var(--border);
}
.chip-toggle:hover { border-color: var(--accent); }
.filter-note {
  display: block; margin-top: 0.4rem; font-size: 0.75rem; color: var(--muted);
}
@media (forced-colors: active) {
  /* Author colors are replaced by the system palette here: every chip
     tint collapses to Canvas and the :checked accent fill is discarded,
     so the check glyph is what carries "this filter is on". Background-
     coloured shapes (.live-dot) and any border drawn in a custom token
     need a system colour to stay visible at all. */
  .tag { border: 1px solid CanvasText; }
  .filter-chip, .chip-toggle { border: 1px solid ButtonBorder; }
  .filter-cb:checked ~ .filter-bar label { border-width: 3px; }
  .live-dot { outline: 1px solid CanvasText; }
  .skip-link { border: 2px solid CanvasText; }
  .plain { border-left: 3px solid Highlight; }
  .today-disclosure { border: 1px solid CanvasText; }
  a:focus-visible, button:focus-visible, .table-scroll:focus-visible,
  summary:focus-visible { outline: 3px solid Highlight; outline-offset: 2px; }
}
@media print {
  /* never print a filtered subset that could read as the whole day */
  .today-item { display: list-item !important; }
  .filter-bar { display: none; }
}
/* The site's first breakpoint (there was none): the item grid stacks —
   time above title — and dense rows get room to breathe. 40rem covers
   phones without touching tablets or the 46rem column. */
@media (max-width: 40rem) {
  .today-item { grid-template-columns: 1fr; gap: 0; }
  .today-time { padding-top: 0; }
  .filter-row { line-height: 2.4; }
  .nav-links { font-size: 0.9rem; }
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
/* Blog (blog.html + blog-<slug>.html): commentary about the project, kept
   visually separate from digest content. Cards mirror the digest-list card
   shape rather than sharing its selector, so the two can diverge. */
.post-list { list-style: none; padding: 0; }
.post-list li {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.9rem 1.1rem;
  margin: 0.8rem 0;
}
.post-list a.post-title {
  font-weight: 700;
  font-size: 1.05rem;
  text-decoration: none;
}
.post-list .post-date {
  display: block;
  font-size: 0.8rem;
  color: var(--muted);
}
.post-list p.teaser {
  margin: 0.4rem 0 0;
  color: var(--muted);
  font-size: 0.95rem;
}
.post-meta {
  margin: 0.2rem 0 1.4rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--border);
  font-size: 0.85rem;
  color: var(--muted);
}
.post-back {
  margin-top: 2.4rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border);
  font-size: 0.9rem;
}
/* ---- Long-form post typography -------------------------------------
   Everything here is scoped to .post so none of it can reach a digest
   page, whose layout is dense reference material with its own rules
   (_style_digest_body). All colour comes from the theme variables, so
   light and dark follow the viewer with no second rule set.

   Measure: `main` is 46rem, which suits the digest's tables and citation
   lines but runs near 90 characters for continuous prose. A post narrows
   its text and sets it slightly larger, landing close to the 65-75
   character line that sustained reading wants. It stays centred inside
   main rather than flush left, so the header and footer still frame it. */
.post {
  max-width: 34rem;
  margin: 0 auto;
  font-size: 1.06rem;
  line-height: 1.7;
}
.post p { margin: 0 0 1.15rem; }
/* Section heads read as parts of an article, not as the digest's labelled
   data sections: a rule ABOVE the head separates what came before, where
   the digest's rule sits below to bind a heading to its table. The base
   h2's bottom border is therefore reset, not inherited. */
.post h2 {
  margin: 2.6rem 0 0.8rem;
  padding: 1.3rem 0 0;
  border-top: 1px solid var(--border);
  border-bottom: 0;
  font-size: 1.3rem;
  line-height: 1.3;
  color: var(--accent);
}
.post h3 {
  margin: 1.9rem 0 0.5rem;
  font-size: 1.08rem;
  line-height: 1.35;
  color: var(--fg);
}
/* The dateline: the post's own italic standfirst, which Markdown emits as
   the paragraph immediately after the inserted .post-meta line. Coupled
   to that construction in _blog_post_body on purpose — there is no class
   to hang it on without putting HTML in the author's Markdown. */
.post > .post-meta + p {
  margin-top: -0.4rem;
  font-size: 1.02rem;
  color: var(--muted);
}
.post > .post-meta + p em { font-style: normal; }
/* Pull quote. An accent rule rather than italics or quotation marks:
   these are quotations of our OWN prose — a statement being given weight,
   not an aside and not someone else's words. Left border only, so the
   quote stays in the reading column instead of becoming a card. */
.post blockquote {
  margin: 1.9rem 0;
  padding: 0.1rem 0 0.1rem 1.2rem;
  border-left: 3px solid var(--accent);
  font-size: 1.16rem;
  line-height: 1.55;
  color: var(--fg);
}
.post blockquote p { margin: 0.5rem 0; }
.post blockquote em { color: var(--muted); }
.post blockquote strong { color: var(--accent); }
.post ul, .post ol { margin: 0 0 1.15rem; padding-left: 1.4rem; }
.post li { margin: 0.4rem 0; }
/* In-prose links are underlined. In the digest, citations sit in
   predictable positions and colour alone is enough; in running prose a
   link has no such position, and colour alone is not an accessible
   distinction (WCAG 1.4.1). */
.post p a, .post li a, .post blockquote a {
  text-decoration: underline;
  text-underline-offset: 0.15em;
}
.post hr { margin: 2.4rem 0; }
.post .post-meta { margin-bottom: 1.6rem; }
@media (max-width: 40rem) {
  .post { max-width: 100%; font-size: 1.02rem; }
  .post blockquote { font-size: 1.08rem; }
}
/* Per-source pages (sources/<id>.html). Model-derived prose renders in
   its own visual register — dashed border, the same convention the
   tag-model chip established — and each block leads with an explicit
   in-words label (GUIDE §2/§3a: model text is labeled in place, never
   presented as official-record content). */
.model-block {
  border: 1px dashed var(--control-border);
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
  background: var(--accent-soft);
  padding: 0.6rem 0.85rem;
  margin: 0.8rem 0;
}
.model-block-label {
  display: block;
  font-size: 0.72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.04em;
  color: var(--accent);
  margin-bottom: 0.3rem;
}
.model-block p { margin: 0.4rem 0; }
.model-provenance { font-size: 0.78rem; color: var(--muted); margin: 0.4rem 0 0; }
/* Per-source fact lists (Identity, How we ingest it): a two-column
   term/value grid — the same shape .status-key established — so a fact
   reads across one visual row instead of a term line followed by an
   indent-less value line ("return -> tab", operator, 2026-08-03).
   max-content keeps the term column exactly as wide as its longest
   label; values wrap in place beside their term. */
.src-facts {
  display: grid; grid-template-columns: max-content 1fr;
  gap: 0.4rem 1.1rem;
  margin: 0.8rem 0;
}
.src-facts dt { font-weight: 600; margin: 0; }
.src-facts dd { margin: 0; overflow-wrap: anywhere; }
/* On a phone the two columns would squeeze the value into a sliver;
   stack instead, keeping term-over-value pairs visually grouped. */
@media (max-width: 40rem) {
  .src-facts { display: block; }
  .src-facts dt { margin-top: 0.6rem; }
  .src-facts dd { margin: 0.1rem 0 0; }
}
.stat-note { font-size: 0.82rem; color: var(--muted); }
/* Inline SVG charts: one series per chart, drawn in the site accent so
   both themes inherit the right ink from the shared tokens. The SVG is
   decorative duplication — the visually-hidden table beside it is the
   accessible representation — so it is aria-hidden and its container
   scrolls rather than the page. */
.chart { margin: 1rem 0; }
.chart svg { width: 100%; height: auto; display: block; }
.chart-bar { fill: var(--accent); }
.chart-line { stroke: var(--accent); fill: none; stroke-width: 2; }
.chart-baseline { stroke: var(--border); stroke-width: 1; }
.chart-label { fill: var(--muted); font-size: 10px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Arial, sans-serif; }
.chart figcaption { font-size: 0.82rem; color: var(--muted); margin-top: 0.25rem; }
@media (forced-colors: active) {
  /* Author fills are replaced by the system palette elsewhere on the
     page; SVG fills are not forced, so the data marks must opt in. */
  .chart-bar { fill: CanvasText; }
  .chart-line { stroke: CanvasText; }
  .chart-baseline { stroke: CanvasText; }
  .chart-label { fill: CanvasText; }
  .model-block { border: 1px dashed CanvasText;
    border-left: 3px solid Highlight; }
}
@media print {
  /* The accent prints as a mid grey; keep marks legible on paper. */
  .chart-bar { fill: #444; }
  .chart-line { stroke: #444; }
  .model-block { border: 1px dashed #444; }
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
    """A chip, plus its `title` repeated as visually-hidden text. The
    model-generated marker was carried by a dashed border, an italic, and
    a `title` attribute — none of which a screen reader conveys, and a
    `title` is unavailable to keyboard and touch entirely. GUIDE §2 wants
    model-generated text labeled in place; this is that label, in words
    (A11Y-11)."""
    classes = _tag_classes(text, extra_class)
    title_attr = f' title="{html.escape(title)}"' if title else ""
    note = f'<span class="vh"> ({html.escape(title)})</span>' if title else ""
    return (f'<span class="{classes}"{title_attr}>'
            f"{html.escape(text)}{note}</span>")


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


_TABLE_EL_RE = re.compile(r"<table>(.*?)</table>", re.DOTALL)
_TH_RE = re.compile(r"<th(?=[\s>])")
_HEAD_ID_RE = re.compile(r'<h[23] id="([^"]+)"')


def _accessible_tables(html_body):
    """Tables keep their semantics: the scroll container moves to a
    wrapper (display:block on a <table> strips its table, row, and cell
    roles from the accessibility tree, so a counts table is announced as
    a flat run of numbers), header cells get scope, and the wrapper is a
    focusable labelled region so a keyboard-only reader can scroll a wide
    table (A11Y-03).

    Ordering constraint: `_compact_meta` matches
    `<table>.*?Digest date.*?</table>` and must run BEFORE this helper,
    or the wrapper markup lands between it and its table."""
    out, pos = [], 0
    for match in _TABLE_EL_RE.finditer(html_body):
        out.append(html_body[pos:match.start()])
        heads = _HEAD_ID_RE.findall(html_body[:match.start()])
        label = (f' aria-labelledby="{heads[-1]}"' if heads
                 else ' aria-label="Data table"')
        inner = _TH_RE.sub('<th scope="col"', match.group(1))
        out.append(f'<div class="table-scroll" role="region" tabindex="0"'
                   f"{label}><table>{inner}</table></div>")
        pos = match.end()
    out.append(html_body[pos:])
    return "".join(out)


def _collapse_sections(html_body):
    """Numbered sections and appendix blocks fold into native <details>
    cards whose summary carries the title, the section's tag chips, and
    its plain-speak synopsis — so the initial page is the day in plain
    speak, and the full record expands on demand.

    The title is the section's <h2> and it lives INSIDE the <summary>,
    carrying the anchor id (A11Y-04). A closed <details> keeps its
    contents out of the accessibility tree, so a heading placed after the
    summary left a 25-heading digest exposing two headings, and the
    fragment-revealing algorithm opens a target's <details> ancestors,
    not the target — so an id on the <details> itself scrolled to a
    section that stayed shut. The id string is unchanged, so existing
    deep links keep their form and now open what they point at."""
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
        summary = f'<h2 class="sec-title" id="{anchor}">{title}</h2>'
        if tags_m:
            summary += tags_m.group(0).replace('<p class="tags">', '<span class="tags">') \
                                      .replace("</p>", "</span>")
        if blurb_m:
            summary += f'<span class="sec-blurb">{blurb_m.group(1)}</span>'
        out.append(
            f'<details class="digest-section">'
            f"<summary>{summary}</summary>{body}</details>")
    return "".join(out)


def _inject_day_view_link(body, date, md_text, out_dir):
    """Offer the frozen day view from EVERY digest page that has one
    (operator, 2026-08-03). Digests rendered since the feature carry the
    link in their canonical markdown (report._header_lines); the seven
    digests frozen before it never will — their markdown is evidence and
    is not re-rendered — so the derived page supplies the same paragraph
    when day/<date>.html exists on disk. Injection skips markdown that
    already links the day view, so a new digest never shows it twice,
    and links only what was actually built (the site-wide rule). Neutral
    wording — a backfilled day view discloses its own reconstructed
    provenance; the digest page does not claim it was frozen live."""
    href = f"day/{date}.html"
    if href in md_text or not (out_dir / "day" / f"{date}.html").exists():
        return body
    para = (f'<p><a href="{href}">Full observed listing for this day</a>'
            " &mdash; every item our collectors observed for this"
            " publication day, mechanical rules applied. This digest is"
            " the canonical record.</p>")
    # The same position the markdown-emitted paragraph lands in: right
    # after the compact header strip, or after the title when a digest
    # has no metadata table.
    marker = '<div class="digest-meta">'
    if marker in body:
        end = body.index("</div>", body.index(marker)) + len("</div>")
        return body[:end] + para + body[end:]
    head, sep, tail = body.partition("</h1>")
    return head + sep + para + tail if sep else para + body


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
        # The description folds into a tooltip visually, and is restored
        # as visually-hidden text for assistive technology (A11Y-11): why
        # an item was selected is the project's core accountability
        # claim, and a `title` attribute reaches neither keyboard nor
        # touch. The canonical Markdown was never touched either way.
        rule_id, desc = match.group(1), match.group(2)
        title = html.escape(re.sub(r"<[^>]+>", "", desc), quote=True)
        return (f'<li class="rule-note">Included because: '
                f'<span class="rule-id" title="{title}">{rule_id}'
                f'<span class="vh"> — {title}</span></span></li>')

    html_body = _RULE_LI_RE.sub(_rule, html_body)
    html_body = _SOURCE_LI_RE.sub(
        r'<li class="source-note">Source: \1</li>', html_body)
    html_body = _compact_meta(html_body)
    html_body = _chip_tags(html_body)
    html_body = _CONTENTS_RE.sub("", html_body, count=1)
    html_body = _accessible_tables(html_body)
    html_body = _collapse_sections(html_body)
    return html_body


# The whole element, not just the opening tag: the new-tab notice
# (A11Y-12) has to be appended where convention puts it, immediately
# before </a>. Widening is safe because <a> cannot nest.
_A_TAG_RE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.IGNORECASE | re.DOTALL)
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
    opened page's access to ours and its referrer.

    A new tab opened without notice is disorienting: focus context
    changes with no announcement, a magnification user's viewport
    changes wholesale, and Back stops working. So each such link also
    states it, in visually-hidden text (3.2.5 technique G201, A11Y-12).
    The alternative — one page-level sentence — is quieter but leaves a
    reader who arrives at a single link by link navigation with no
    warning at all."""
    from urllib.parse import urlsplit

    site = _site_host(base)

    def _sub(match):
        attrs, inner = match.group(1), match.group(2)
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
        return (f'<a{attrs} target="_blank" rel="noopener noreferrer">'
                f'{inner}<span class="vh"> (opens in a new tab)</span></a>')

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


# Pages that live one directory below the site root (sources/<id>.html,
# day/<date>.html) are rendered exactly like root pages — same _PAGE
# shell, same nav, same relative hrefs — and then rebased: every
# document-relative URL reference gains a ../ prefix. One seam, applied
# to the whole rendered page, so the shell's hardcoded style.css/llms.txt
# links, the nav, and body links all obey the same rule. Fragment-only
# hrefs (#main, the skip links), absolute URLs, schemes (mailto:), and
# already-rebased ../ paths are untouched. Chosen over <base href="../">
# because a <base> also rebases fragment-only links, which breaks
# in-page anchors.
_REL_URL_ATTR_RE = re.compile(
    r'\b(href|src|action)="(?!(?:[a-z][a-z0-9+.-]*:|//|/|#|\.\./))([^"]*)"',
    re.IGNORECASE)


def _rebase_page(page_html, depth=1):
    prefix = "../" * depth
    return _REL_URL_ATTR_RE.sub(
        lambda m: f'{m.group(1)}="{prefix}{m.group(2)}"', page_html)


# Compact nav labels where a stem's .capitalize() reads badly.
_NAV_LABELS = {"ai-development": "AI development"}


def _nav_link(href, label, here=None):
    """One nav anchor, marked `aria-current="page"` when it is the page
    being rendered. Every page emits every link, in the same order — a
    page linking to itself is the orientation cue a screen reader user
    arriving mid-site otherwise has to infer (3.2.3, A11Y open q. 8)."""
    mark = ' aria-current="page"' if here and href == here else ""
    return f'<a href="{href}"{mark}>{label}</a>'


def _doc_nav_links(doc_pages, here=None):
    """Nav anchors for the docs/site explanatory pages (About, Methods, …)."""
    return "".join(
        _nav_link(f"{stem}.html",
                  html.escape(_NAV_LABELS.get(stem, stem.capitalize())), here)
        for stem, _title in doc_pages
    )


def _registry_exists():
    """Whether sources.html will exist — the source guide is rendered from
    the registry, so an absent registry means no page to link to."""
    return (config.PROJECT_ROOT / "sources" / "registry.yaml").exists()


_CURRENT_HREFS = {"index": "index.html", "today": "today.html",
                  "sources": "sources.html", "blog": "blog.html",
                  "agents": "agents.html"}


# Explanatory pages that stay on the primary nav row; the rest collapse
# into the "More" disclosure (still every page, still one order — the
# operator's identical-header rule holds, the row just stops wrapping
# into three lines of grey links above every h1).
_PRIMARY_DOC_STEMS = ("about",)


def _site_nav(doc_pages=(), *, skip_stem=None, current=None):
    """The site header, identical everywhere (operator, 2026-07-30): the
    live view first (the site's most-visited destination, carrying the
    live dot), the digest archive, the source guide, the blog, About and
    the agent guide, then the remaining explanatory pages inside a
    native <details>. Every page renders every link in the same order;
    the page's own link is marked `aria-current` rather than dropped. A
    link is never emitted for a page that was not built."""
    here = f"{skip_stem}.html" if skip_stem else _CURRENT_HREFS.get(current)
    today_mark = ' aria-current="page"' if here == "today.html" else ""
    links = [(f'<a href="today.html"{today_mark}>'
              '<span class="live-dot" aria-hidden="true"></span>'
              "Today (live)</a>"),
             _nav_link("index.html", "All digests", here)]
    if _registry_exists():
        links.append(_nav_link("sources.html", "Sources", here))
    if _blog_exists():
        links.append(_nav_link("blog.html", "Blog", here))
    primary = [p for p in doc_pages if p[0] in _PRIMARY_DOC_STEMS]
    more = [p for p in doc_pages if p[0] not in _PRIMARY_DOC_STEMS]
    links.append(_doc_nav_links(primary, here))
    links.append(_nav_link("agents.html", "For agents", here))
    if more:
        links.append('<details class="nav-more"><summary>More</summary>'
                     + _doc_nav_links(more, here) + "</details>")
    return "".join(links)


def _nav_for(dates, i, doc_pages=()):
    """Prev/next digest links. Out of context — which is how a screen
    reader's link list presents them — `← 2026-07-28` is a bare date, so
    each carries its purpose in visually-hidden text (2.4.4, A11Y-16)."""
    links = []
    if i > 0:
        links.append(f'<a href="{dates[i - 1]}.html">&larr; '
                     f'<span class="vh">Digest for </span>{dates[i - 1]}</a>')
    if i < len(dates) - 1:
        links.append(f'<a href="{dates[i + 1]}.html">'
                     f'<span class="vh">Digest for </span>{dates[i + 1]}'
                     f" &rarr;</a>")
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


# Off-site images are demoted to their alt text before any page renders.
# A README badge is an ordinary open-source convention on GitHub, but the
# same markdown rendered into readme.html would make every visitor's
# browser fetch an image from a third party — exactly what
# docs/site/privacy.md promises never happens ("no external fonts,
# scripts, images, or embeds"). Dropping the <img> and keeping the words
# leaves the surrounding link intact and clickable, so the badge still
# does its job here; only the outbound request is gone. Stated as a rule
# over any off-site host — including protocol-relative `//host/...` — so
# the next badge someone adds is handled without a code change.
_EXTERNAL_IMAGE = re.compile(r"!\[([^\]]*)\]\(\s*(?:https?:)?//[^)]*\)")


def _textualize_external_images(md_text):
    return _EXTERNAL_IMAGE.sub(lambda m: m.group(1).strip() or "image", md_text)


def _doc_sources():
    """[(markdown, stem, title, canonical)] for every explanatory page —
    docs/site/*.md plus the repo README. Separated from rendering so any
    page (notably the independently-rebuilt /today) can construct the
    same navigation without re-rendering the site."""
    docs = []
    doc_dir = config.PROJECT_ROOT / "docs" / "site"
    if doc_dir.is_dir():
        for path in sorted(doc_dir.glob("*.md"), key=lambda p: p.stem):
            md_text = _textualize_external_images(
                path.read_text(encoding="utf-8"))
            match = _H1_RE.search(md_text)
            title = match.group(1) if match else path.stem.capitalize()
            docs.append((md_text, path.stem, title, f"docs/site/{path.name}"))
    readme = config.PROJECT_ROOT / "README.md"
    if readme.exists():
        # Images first: an image's URL is not a link the rewriter should
        # reason about, and demoting it early keeps a badge's own link the
        # only link left on that line.
        md_text = _rewrite_readme_links(
            _textualize_external_images(readme.read_text(encoding="utf-8")))
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


# ---------------------------------------------------------------------------
# Source health rendering (fapd.health computes; this only renders)
# ---------------------------------------------------------------------------
# Editorial constraint, stated where the code is so it cannot be lost: every
# label and every sentence below describes OUR INGESTION of a source, never
# the publisher. "No response on 12 of 40 requests" is an observation we
# recorded; "unreliable agency" is an opinion, is not derivable from
# anything in the databases, and is not publishable here (GUIDE §2). The
# glyphs are decorative duplicates of the words beside them, so they are
# hidden from assistive technology rather than spoken as box-drawing names.

_HEALTH_GLYPHS = {
    "delivering": "●",    # filled circle
    "quiet": "○",         # hollow circle
    "degraded": "▲",      # triangle
    "no-response": "✕",   # multiplication x
    "no-data": "—",       # em dash
}
_HEALTH_WORDS = {
    "delivering": "delivering",
    "quiet": "quiet",
    "degraded": "degraded",
    "no-response": "no response",
    "no-data": "no data",
}


def _health_chip(label):
    """Colour + glyph + word, in that order of redundancy. The visually
    hidden prefix supplies the noun: out of context, "quiet" alone does
    not say what is quiet (1.3.1)."""
    word = _HEALTH_WORDS.get(label, label)
    glyph = _HEALTH_GLYPHS.get(label, "")
    return (f'<span class="tag tag-health-{label}">'
            f'<span class="health-glyph" aria-hidden="true">{glyph}</span>'
            f'<span class="vh">Ingestion health: </span>'
            f"{html.escape(word)}</span>")


def _n(value):
    """Thousands-separated integer, or an em dash when we have no value."""
    return f"{value:,}" if isinstance(value, int) else "&mdash;"


def _fetch_sentence(fetch):
    """The request outcomes for one host, by status class. Every number is
    a count of requests WE made; none of them measures the publisher."""
    bits = [
        f"{_n(fetch['attempts'])} request(s)",
        f"{_n(fetch['answered'])} answered",
        f"{_n(fetch['client_error'])} declined (4xx)",
        f"{_n(fetch['server_error'])} server declined (5xx)",
        f"{_n(fetch['no_response'])} no response",
    ]
    line = (f'<p><span class="src-stat-label">Our requests to '
            f"{html.escape(fetch['host'])}:</span> " + " · ".join(bits)
            + f" &mdash; {fetch['error_rate_pct']}% returned no content</p>")
    extra = []
    if fetch.get("last_ok_at"):
        extra.append("last answered request "
                     f"{html.escape(fetch['last_ok_at'])} UTC")
    if fetch.get("shared_with_sources", 1) > 1:
        extra.append(f"this host serves {fetch['shared_with_sources']} "
                     "registered sources, so these figures are host-wide")
    if extra:
        line += f'<p class="src-stat-label">{"; ".join(extra)}.</p>'
    return line


def _health_block(record):
    """The per-card statistics panel. Renders only what was actually
    measured: an absent number is omitted or shown as an em dash, never
    filled in with a zero that would read as an observation."""
    if not record:
        return ""
    if not record["measured"]:
        return (f'<p class="src-stats src-unmeasured">'
                f"{html.escape(record['health_reason'])} Ingestion "
                f"statistics are shown for active sources only.</p>")

    parts = []
    if record["items"]:
        parts.append(
            f'<p><span class="src-stat-label">Items ingested:</span> '
            f"{_n(record['items'])} in {record['window_days']} days "
            f"({record['items_per_day']} per day) · most recent "
            f"{html.escape(record['last_item_date'] or '')}</p>")
    else:
        recent = (f"most recent {html.escape(record['last_item_date'])}"
                  if record["last_item_date"] else
                  "none recorded in the lookback period")
        parts.append(
            f'<p><span class="src-stat-label">Items ingested:</span> '
            f"none in the last {record['window_days']} days &mdash; "
            f"{recent}</p>")
    if record["avg_chars"] is not None:
        parts.append(
            f'<p><span class="src-stat-label">Content length:</span> '
            f"{_n(record['avg_chars'])} characters average, "
            f"{_n(record['median_chars'])} median "
            f"(shortest {_n(record['min_chars'])}, "
            f"longest {_n(record['max_chars'])})</p>")
    if record["delivery_mode"]:
        note = record.get("delivery_mode_note")
        parts.append(
            f'<p><span class="src-stat-label">Delivery mode:</span> '
            f"<code>{html.escape(record['delivery_mode'])}</code>"
            + (f" &mdash; {html.escape(note)}" if note else "") + "</p>")
    if record["fetch"]:
        parts.append(_fetch_sentence(record["fetch"]))
    elif record.get("fetch_note"):
        parts.append(f'<p class="src-stat-label">'
                     f"{html.escape(record['fetch_note'])}</p>")
    collector = record.get("collector")
    if collector and collector.get("consecutive_errors"):
        parts.append(
            f'<p><span class="src-stat-label">Collector:</span> '
            f"{collector['consecutive_errors']} consecutive cycle(s) ended "
            f"in an error; last completed cycle "
            f"{html.escape(collector.get('last_ok_at') or 'not recorded')}</p>")
    # The label itself already sits in the card's subtitle; repeating the
    # chip here would announce it twice. What belongs here is only the
    # sentence that shows how the label follows from the numbers above.
    parts.append(f'<p class="src-stat-label">'
                 f"{html.escape(record['health_reason'])}</p>")
    return f'<div class="src-stats">{"".join(parts)}</div>'


def _source_card(entry, health_record=None):
    """One registry entry as a card: linked name, status chip + subtitle,
    the registry's descriptive text, its measured ingestion statistics and
    health indicator, and the full registry record (id, added date,
    method, notes) folded into a native <details>."""
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
    chip = (f" {_health_chip(health_record['health'])}"
            if health_record and health_record.get("health") else "")
    # The TITLE is the way into OUR page for the source (operator,
    # 2026-08-03): every entry — active, planned, and unavailable alike —
    # links its own sources/<id>.html, where the full statistics, method,
    # and history live. The publisher's own site stays one small link
    # below the title, so a reader is directed to the information page
    # first and to the official site deliberately, not by accident.
    official = (f'<p class="src-links"><a href='
                f'"{html.escape(link, quote=True)}">Official site</a></p>')
    return (
        f'<article class="src-card" id="src-{html.escape(entry["id"])}">'
        f'<h4 class="src-name"><a href="sources/'
        f'{html.escape(entry["id"], quote=True)}.html">'
        f"{html.escape(entry['name'])}</a></h4>"
        f'<p class="src-sub">{_status_chip(entry["status"])}{chip} {subtitle}</p>'
        f"{official}"
        f'<p class="src-desc">{html.escape(entry["description"])}</p>'
        f"{signup}"
        f"{_card_stats_block(health_record)}"
        f'<details class="src-more"><summary>Registry record</summary>'
        f'<dl>{"".join(record)}</dl></details>'
        "</article>"
    )


def _source_section(anchor, title, intro_html, group_entries, health=None):
    """A source group as h2 + intro + Active/Planned h3 subgroups of cards
    (registry order within each subgroup — registry order is precedence)."""
    parts = [f'<h2 id="{anchor}">{title}</h2>', intro_html]
    for status in ("active", "planned"):
        subset = [e for e in group_entries if e["status"] == status]
        if not subset:
            continue
        parts.append(f"<h3>{status.capitalize()} ({len(subset)})</h3>")
        parts.extend(_source_card(e, (health or {}).get(e["id"]))
                     for e in subset)
    return "".join(parts)


def _health_section(health):
    """The directory-wide health summary: what the labels mean, how many
    sources wear each one, and the aggregate volume — placed before the
    cards so a reader knows where to look before scrolling 127 of them.

    Renders a disclosed "not available" when the databases are absent
    (a fresh clone, or CI), because the alternative is a page of zeroes
    that reads as an outage."""
    parts = ['<h2 id="source-health">Source health and statistics</h2>']
    if not health or not health.get("available"):
        reason = (health or {}).get("unavailable_reason",
                                    "no pipeline database in this build")
        parts.append(
            "<p>Per-source statistics are not available in this build &mdash; "
            f"{html.escape(reason)}. The directory below is rendered from "
            "the registry alone.</p>")
        return "".join(parts)

    summary = health["summary"]
    counts = summary["health_counts"]
    defs = health["label_definitions"]
    t = health["thresholds"]

    parts.append(
        "<p>These figures describe <strong>this project's ingestion of "
        "each source</strong>, and nothing else. They are counts of items "
        "we recorded and of requests we made, taken mechanically from the "
        "pipeline's own databases at build time. They are not a "
        "measurement of any agency, department, or publisher, and no "
        "label below is a judgement about one.</p>")
    parts.append(
        f'<p class="src-counts"><strong>{summary["delivering"]}</strong> of '
        f'{summary["sources_measured"]} active sources delivered items in '
        f'the {summary["window_days"]} days ending '
        f'{html.escape(health["window_end"])} &mdash; '
        f'{_n(summary["items_window"])} item(s) in all, about '
        f'{summary["items_per_day"]} per day across the directory. '
        f'{summary["sources_with_fetch_errors"]} source(s) recorded '
        f'requests that returned no content, across '
        f'{len(summary["hosts_with_fetch_errors"])} host(s), out of '
        f'{_n(summary["requests_window"])} request(s) we made.</p>')

    rows = "".join(
        f"<tr><td>{_health_chip(label)}</td>"
        f"<td>{html.escape(defs[label])}</td>"
        f'<td>{counts[label]}</td></tr>'
        for label in health_mod.HEALTH_ORDER)
    parts.append(
        "<table><thead><tr><th>Indicator</th><th>What we observed</th>"
        "<th>Active sources</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>")

    parts.append(
        f'<p class="health-note">Thresholds, so any label can be checked '
        f'against the numbers on its card: the window is the last '
        f'{t["window_days"]} days; a source with no item for more than '
        f'{t["quiet_after_days"]} days is <em>quiet</em>; ingestion is '
        f'<em>degraded</em> when {t["degraded_error_rate_pct"]}% or more of '
        f'our requests returned no content (counted only once at least '
        f'{t["min_attempts_for_rate"]} requests were made), or when the '
        f'collector recorded {t["degraded_consecutive_errors"]} or more '
        f'consecutive failed cycles. "Most recent item" looks back up to '
        f'{t["recency_lookback_days"]} days. Item counts are dated by '
        f'publication day in Washington; request counts are stamped UTC.</p>')
    parts.append(f'<p class="health-note">{html.escape(health_mod.FETCH_DISCLAIMER)}'
                 "</p>")
    if not health.get("fetch_log_available"):
        parts.append('<p class="health-note">The request log is not present '
                     "in this build, so request statistics are omitted "
                     "rather than shown as zero.</p>")
    return "".join(parts)


def _sources_body(entries, health=None):
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
        _health_section(health),
    ]

    records = (health or {}).get("sources") or {}
    listed = [e for e in entries if e["status"] in ("active", "planned")]
    parts.append(_source_section(
        "govinfo-collections", "Official govinfo collections",
        "<p>Structured document collections published by the Government "
        "Publishing Office through govinfo.gov — the core official record "
        "the digest is built from. Each collection syncs through the "
        "govinfo collections API with per-collection watermarks.</p>",
        [e for e in listed if e["type"] == "govinfo-collection"], records))
    parts.append(_source_section(
        "agency-web-channels", "Agency newsrooms and web channels",
        "<p>Press-release feeds and indexes, APIs, and bulk data that "
        "agencies publish on the web, read through the project's "
        "robots-respecting identified client. The subtitle on each card "
        "names the channel type.</p>",
        [e for e in listed if e["type"] in _WEB_TYPES], records))
    parts.append(_source_section(
        "agency-email-bulletins", "Agency email bulletins",
        "<p>Bulletins the agencies themselves distribute by subscription "
        "email (GovDelivery and similar services), delivered to a single "
        "identified project mailbox and ingested from the message body. "
        "Every message's DKIM signature is checked on arrival and the "
        "result is disclosed on each item — a failing signature is "
        "labeled, never silently dropped, because official content is "
        "not discarded over a mail-infrastructure hiccup. Sender and "
        "mailbox addresses are recorded "
        "in the registry, not republished here; where a registry note "
        "quotes one, it appears as [address withheld].</p>",
        [e for e in listed if e["type"] == "email"], records))

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
        parts.extend(_source_card(e, records.get(e["id"]))
                     for e in unavailable)

    excluded = [e for e in entries if e["status"] == "evaluated-excluded"]
    if excluded:
        parts.append(
            f'<h2 id="evaluated-and-excluded">Evaluated and excluded '
            f"({len(excluded)})</h2>"
            "<p>Sources examined and found outside the project's scope — "
            "they do not publish new federal government actions. The "
            "evaluation is kept so the decision stays visible and "
            "revisitable.</p>")
        parts.extend(_source_card(e, records.get(e["id"]))
                     for e in excluded)

    # The health key is the page's only table; it goes through the same
    # helper the digest pages use so its scroll wrapper, region label,
    # and `scope` attributes are the ones already audited (A11Y-03).
    return _accessible_tables("".join(parts))


def _registry_entries():
    """The validated registry, or [] when there is none on disk — the same
    contract as `_registry_exists`, but returning the data so the page and
    the health computation read the file once between them."""
    registry_path = config.PROJECT_ROOT / "sources" / "registry.yaml"
    if not registry_path.exists():
        return []
    return sources.load_registry(registry_path)


def _build_sources_page(out_dir, doc_pages=(), entries=(), health=None):
    """Render the source guide as a human-readable directory derived from
    sources/registry.yaml at build time. Returns True if the page was built."""
    if not entries:
        return False
    page = _render_page(
        f"Sources — {SITE_TITLE}",
        _sources_body(entries, health),
        _site_nav(doc_pages, current="sources"),
        "sources/registry.yaml",
        description=("Every federal source the Free Agentic Publication "
                     "Digester ingests, plans to ingest, or has evaluated — "
                     "with the items, content lengths, and request outcomes "
                     "we recorded for each."),
    )
    (out_dir / "sources.html").write_text(page, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Per-source pages (sources/<source-id>.html)
# ---------------------------------------------------------------------------
# One page per registry entry — active, planned, unavailable, and excluded
# alike: a refusal is accountability data, and an unavailable source's page
# shows its refusal history from the registry notes. Everything mechanical
# is rendered from the registry, config constants, and the health payload;
# the two OPTIONAL model-derived blocks (description, assessment) come from
# the database via fapd.assess and the page renders cleanly without them
# (GUIDE §3a source surfaces, 2026-08-03).

def _ro_conn(path):
    """Read-only sqlite connection, or None when the file is absent or
    unreadable — callers render 'not available', never a crash."""
    import sqlite3

    p = Path(path)
    if not p.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


#: Daily-series window for the per-source charts.
CHART_WINDOW_DAYS = 30

#: Where published request statistics begin (operator, 2026-08-03). The
#: production cutover was 2026-07-30; fetch-log rows before it are the
#: development machine's traffic, migrated with the databases, and are
#: not observations of the production service. All-time figures and the
#: per-source request charts start here; item counts are the corpus
#: record and are not floored.
ALL_TIME_STATS_SINCE = "2026-07-30"

#: The all-time figures' honest limits, stated wherever they render:
#: the floor above, and source-probe traffic unlabeled before the probe
#: client existed.
ALL_TIME_PROBE_NOTE = (
    f"Request counts begin {ALL_TIME_STATS_SINCE}, the day this service "
    "went into production; earlier development-machine traffic is "
    "excluded. Counts before 2026-08-03 include unmarked source-probe "
    "traffic; probes are labeled and excluded thereafter."
)

_DAILY_ITEMS_SQL = """
SELECT p.collection AS collection,
       json_extract(e.metadata, '$.source_id') AS source_id,
       p.digest_day AS day, COUNT(*) AS n
FROM extracted_texts e
JOIN packages p USING (package_id)
WHERE p.digest_day >= ? AND p.digest_day <= ?
GROUP BY 1, 2, 3
"""


def _daily_items(conn, start_day, end_day):
    """{(kind, key): {day: items}} over the chart window, keyed like
    health.source_key."""
    import sqlite3

    out = {}
    try:
        for row in conn.execute(_DAILY_ITEMS_SQL, (start_day, end_day)):
            key = (("source_id", row["source_id"]) if row["source_id"]
                   else ("collection", row["collection"]))
            out.setdefault(key, {})[row["day"]] = row["n"]
    except sqlite3.Error:
        return {}
    return out


_DAILY_FETCH_SQL = """
WITH parsed AS (
    SELECT substr(url, instr(url, '//') + 2) AS rest,
           substr(ts_utc, 1, 10) AS day, {elapsed} AS elapsed_ms
    FROM fetch_log
    WHERE ts_utc >= ? AND {probe}
)
SELECT lower(CASE WHEN instr(rest, '/') > 0
                  THEN substr(rest, 1, instr(rest, '/') - 1)
                  ELSE rest END) AS host,
       day, COUNT(*) AS n, AVG(elapsed_ms) AS avg_ms
FROM parsed
GROUP BY 1, 2
"""


def _daily_fetches(conn, start_ts):
    """{host: {day: {"n": requests, "avg_ms": mean elapsed or None}}} over
    the chart window, probe traffic excluded (same predicate as every
    fetch figure in fapd.health). Tolerates a log from before the
    elapsed_ms column existed — the sparkline is then simply absent."""
    import sqlite3

    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(fetch_log)")}
        elapsed = "elapsed_ms" if "elapsed_ms" in cols else "NULL"
        sql = _DAILY_FETCH_SQL.format(
            elapsed=elapsed, probe=health_mod._probe_filter(conn))
        out = {}
        for row in conn.execute(sql, (start_ts,)):
            out.setdefault(row["host"], {})[row["day"]] = {
                "n": row["n"],
                "avg_ms": (round(row["avg_ms"]) if row["avg_ms"] is not None
                           else None),
            }
        return out
    except sqlite3.Error:
        return {}


def _chart_days(end_day, n=CHART_WINDOW_DAYS):
    """The n calendar days ending at end_day, oldest first."""
    import datetime as _dt

    end = _dt.date.fromisoformat(end_day)
    return [(end - _dt.timedelta(days=i)).isoformat()
            for i in range(n - 1, -1, -1)]


_CHART_W, _CHART_H = 600, 120


def _vh_series_table(caption, days, values, unit):
    """The accessible representation of a chart: a visually-hidden table
    with one row per day (docs/accessibility.md — the SVG itself is
    decorative duplication and is hidden from assistive technology)."""
    rows = "".join(
        f"<tr><td>{html.escape(d)}</td><td>{v if v is not None else '—'}</td></tr>"
        for d, v in zip(days, values))
    return (f'<table class="vh"><caption>{html.escape(caption)}</caption>'
            f"<thead><tr><th scope=\"col\">Day</th>"
            f"<th scope=\"col\">{html.escape(unit)}</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>")


def _svg_bar_chart(days, values, *, title, unit):
    """A 30-day daily bar chart as inline SVG — plain string building,
    no dependency, no script. One series in the site accent (both themes
    inherit the token); a visually-hidden table carries the data for
    assistive technology; per-bar <title> gives a native hover value.
    Returns '' when every value is zero — an all-zero chart would read
    as an outage where the prose already states 'none recorded'."""
    if not any(values):
        return ""
    vmax = max(values)
    pad_l, pad_r, pad_t, pad_b = 34, 4, 8, 16
    plot_w = _CHART_W - pad_l - pad_r
    plot_h = _CHART_H - pad_t - pad_b
    step = plot_w / len(days)
    bar_w = max(1.0, step - 2)
    bars = []
    for i, (day, val) in enumerate(zip(days, values)):
        h = round(plot_h * val / vmax, 1) if vmax else 0.0
        x = round(pad_l + i * step, 1)
        y = round(pad_t + plot_h - h, 1)
        bars.append(
            f'<rect class="chart-bar" x="{x}" y="{y}" width="{bar_w:.1f}"'
            f' height="{h}" rx="1"><title>{html.escape(day)}: {val} '
            f"{html.escape(unit)}</title></rect>")
    base_y = pad_t + plot_h
    axis = (
        f'<line class="chart-baseline" x1="{pad_l}" y1="{base_y}"'
        f' x2="{_CHART_W - pad_r}" y2="{base_y}"/>'
        f'<text class="chart-label" x="{pad_l - 5}" y="{pad_t + 8}"'
        f' text-anchor="end">{vmax}</text>'
        f'<text class="chart-label" x="{pad_l}" y="{_CHART_H - 3}">'
        f"{html.escape(days[0])}</text>"
        f'<text class="chart-label" x="{_CHART_W - pad_r}" y="{_CHART_H - 3}"'
        f' text-anchor="end">{html.escape(days[-1])}</text>')
    total = sum(values)
    peak_day = days[values.index(vmax)]
    caption = (f"{title}: {total:,} {unit} over the last {len(days)} days "
               f"(peak {vmax:,} on {peak_day}).")
    svg = (f'<svg viewBox="0 0 {_CHART_W} {_CHART_H}" aria-hidden="true"'
           f' focusable="false">{axis}{"".join(bars)}</svg>')
    return (f'<figure class="chart">'
            f"<figcaption>{html.escape(caption)}</figcaption>{svg}"
            f'{_vh_series_table(caption, days, values, unit)}</figure>')


def _svg_sparkline(days, values, *, title, unit="ms"):
    """A response-time sparkline (daily mean) as inline SVG. Days with no
    timed request are gaps in the line, not zeroes. Returns '' below two
    measured days — a one-point line draws nothing honest."""
    points = [(i, v) for i, v in enumerate(values) if v is not None]
    if len(points) < 2:
        return ""
    vmax = max(v for _i, v in points)
    vmin = min(v for _i, v in points)
    span = (vmax - vmin) or 1
    pad_l, pad_r, pad_t, pad_b = 34, 4, 8, 16
    plot_w = _CHART_W - pad_l - pad_r
    plot_h = _CHART_H - pad_t - pad_b
    step = plot_w / max(1, len(days) - 1)
    coords = " ".join(
        f"{round(pad_l + i * step, 1)},"
        f"{round(pad_t + plot_h - plot_h * (v - vmin) / span, 1)}"
        for i, v in points)
    axis = (
        f'<text class="chart-label" x="{pad_l - 5}" y="{pad_t + 8}"'
        f' text-anchor="end">{vmax}</text>'
        f'<text class="chart-label" x="{pad_l - 5}" y="{pad_t + plot_h}"'
        f' text-anchor="end">{vmin}</text>'
        f'<text class="chart-label" x="{pad_l}" y="{_CHART_H - 3}">'
        f"{html.escape(days[0])}</text>"
        f'<text class="chart-label" x="{_CHART_W - pad_r}" y="{_CHART_H - 3}"'
        f' text-anchor="end">{html.escape(days[-1])}</text>')
    caption = (f"{title}: between {vmin:,} and {vmax:,} {unit} across the "
               f"last {len(days)} days (days without a timed request are "
               "gaps, not zeroes).")
    svg = (f'<svg viewBox="0 0 {_CHART_W} {_CHART_H}" aria-hidden="true"'
           f' focusable="false">{axis}'
           f'<polyline class="chart-line" points="{coords}"/></svg>')
    return (f'<figure class="chart">'
            f"<figcaption>{html.escape(caption)}</figcaption>{svg}"
            f'{_vh_series_table(caption, days, values, unit)}</figure>')


def _recent_sentence(record):
    """The trailing-24-hour figures as one sentence. Request counts are
    host-wide (the same attribution as every fetch figure) and None where
    no requests are made for the source — an absent number is omitted,
    never shown as zero traffic."""
    recent = (record or {}).get("recent")
    if not recent:
        return ""
    bits = []
    if recent.get("requests") is not None:
        # A zero is a true observation (a cold snapshot, a quiet host)
        # and reads better as words than as "0 request(s) (0 answered,
        # 0 returned no content)" — the parenthetical earns its place
        # only when there were requests to classify.
        if recent["requests"]:
            bits.append(f"{_n(recent['requests'])} request(s) "
                        f"({_n(recent['ok'])} answered, "
                        f"{_n(recent['failed'])} returned no content)")
        else:
            bits.append("no requests made")
    items = recent.get("items", 0)
    bits.append(f"{_n(items)} item(s) ingested" if items
                else "no items ingested")
    return (f'<p><span class="src-stat-label">Last {recent["hours"]} '
            f'hours:</span> {" · ".join(bits)}</p>')


def _card_stats_block(record):
    """The compact statistics panel on a sources.html card: the 24-hour
    recent block plus the health-reason sentence. The 14-day view — and
    everything else — lives on the per-source page now."""
    if not record:
        return ""
    if not record["measured"]:
        return (f'<p class="src-stats src-unmeasured">'
                f"{html.escape(record['health_reason'])} Ingestion "
                f"statistics are shown for active sources only.</p>")
    parts = [_recent_sentence(record)]
    fetch = record.get("fetch")
    if fetch and fetch.get("shared_with_sources", 1) > 1:
        parts.append(
            f'<p class="src-stat-label">Request figures are host-wide: '
            f"this host serves {fetch['shared_with_sources']} registered "
            "sources.</p>")
    parts.append(f'<p class="src-stat-label">'
                 f"{html.escape(record['health_reason'])}</p>")
    return f'<div class="src-stats">{"".join(parts)}</div>'


def _model_text_block(label, paragraphs, provenance):
    """A model-derived prose block, visually distinct and labeled in
    words with its provenance (GUIDE §3a: date, model, version — and
    trigger, for assessments). Everything is escaped; the block is never
    presented as official-record content."""
    body = "".join(f"<p>{html.escape(p)}</p>" for p in paragraphs if p)
    return (f'<div class="model-block">'
            f'<span class="model-block-label">{html.escape(label)}</span>'
            f"{body}"
            f'<p class="model-provenance">{html.escape(provenance)}</p>'
            "</div>")


def _description_block(desc):
    if not desc:
        return ""
    prov = (f"Model-written orientation, generated {desc['generated_at'][:10]}"
            f" by {desc.get('model') or 'unrecorded model'}, prompt version "
            f"{desc['prompt_version']}. It may draw on general knowledge of "
            "public institutions and is not official-record content.")
    paragraphs = [desc["summary"]] + [
        p.strip() for p in (desc["description"] or "").split("\n\n")]
    return _model_text_block("Model-written orientation", paragraphs, prov)


def _assessment_block(assessment):
    if not assessment:
        return ""
    prov = (f"Model-written assessment of our own ingestion, generated "
            f"{assessment['generated_at'][:10]} by "
            f"{assessment.get('model') or 'unrecorded model'}, prompt version "
            f"{assessment['prompt_version']}, trigger: "
            f"{assessment.get('trigger_reason') or 'unrecorded'}. It restates "
            "our measured figures and is not official-record content.")
    return _model_text_block("Model-written ingestion assessment",
                             [assessment["assessment"]], prov)


def _methods_rows(entry):
    """(term, description) rows for the 'How we ingest it' section —
    assembled from registry and config facts, so the page can never
    claim a politeness posture the constants do not implement."""
    kind = entry["type"]
    active = entry["status"] == "active"
    rows = [("Channel", _TYPE_LABELS.get(kind, kind)),
            ("Method", _redact_addresses(entry["method"]))]
    if entry.get("adapter"):
        rows.append(("Adapter", entry["adapter"]))
    if kind == "govinfo-collection":
        if active:
            rows.append(("Poll cadence",
                         (f"about every {config.GOVINFO_POLL_INTERVAL_MIN} "
                          "minutes while the collector runs")))
        rows.append((
            "Request budget",
            (f"the govinfo class: at most {config.MAX_REQUESTS_PER_DAY:,} "
             f"requests per day and {config.MAX_GOVINFO_REQUESTS_PER_HOUR:,} "
             "per hour, counted from the fetch log (failed requests count "
             "too); collectors stop at "
             f"{round((1 - config.EOD_BUDGET_RESERVE_FRACTION) * 100)}% so "
             "the end-of-day finalizer always has headroom")))
        rows.append(("Politeness",
                     ("keyed govinfo API access; every request is logged "
                      "before it is made and identified as "
                      f"{config.USER_AGENT}")))
    elif kind == "email":
        if active:
            rows.append(("Poll cadence",
                         ("the project mailbox is read about every "
                          f"{config.EMAIL_POLL_INTERVAL_MIN} minutes")))
        rows.append(("Requests",
                     ("none — bulletins are delivered to the project "
                      "mailbox by the agency's own subscription service")))
        rows.append(("Authenticity",
                     ("every message's DKIM signature is checked on "
                      "arrival and the result is disclosed on each item; "
                      "a failing signature is labeled, never silently "
                      "dropped")))
    else:
        if active:
            rows.append(("Poll cadence",
                         (f"about every {config.AGENCY_POLL_INTERVAL_MIN} "
                          "minutes while the collector runs")))
        rows.append((
            "Request budget",
            (f"the agency class: at most "
             f"{config.MAX_AGENCY_REQUESTS_PER_DAY:,} requests per day "
             "shared across every agency web source, counted from the "
             "fetch log (failed requests count too)")))
        rows.append(("Politeness",
                     ("robots.txt is honored as observed — including each "
                      "host's crawl-delay, exactly — and every request "
                      f"identifies itself as {config.USER_AGENT}; a refusal "
                      "is recorded, never evaded")))
    rows.append(("Capture and hash",
                 ("captured raw content is hashed (SHA-256) into the day's "
                  "committed provenance manifest, hash-chained day to day "
                  "(PROVENANCE.md)")))
    return rows


def _all_time_block(entry, record, all_time, fetch_log_present):
    """Lifetime request figures for the source's host, with the
    host-sharing and unmarked-probe disclosures. Host-keyed, so it can
    exist even for a source that is not currently measured — a refusal's
    request history is accountability data."""
    if entry["type"] == "email":
        return (f'<p class="stat-note">{html.escape(health_mod.EMAIL_FETCH_NOTE)}'
                "</p>")
    host = health_mod.fetch_host(entry)
    if not host:
        return ('<p class="stat-note">No request host is registered for '
                "this source.</p>")
    if not fetch_log_present:
        return ('<p class="stat-note">The request log is not present in '
                "this build, so all-time request statistics are omitted "
                "rather than shown as zero.</p>")
    rec = all_time.get(host)
    if not rec:
        return (f'<p class="stat-note">No requests to {html.escape(host)} '
                "are recorded in the request log.</p>")
    parts = [
        (f'<p><span class="src-stat-label">Our requests to '
         f"{html.escape(host)}, all time (since "
         f"{html.escape((rec.get('first_seen') or '')[:10] or 'the log began')}"
         f"):</span> {_n(rec['requests'])} request(s) · {_n(rec['ok'])} "
         f"answered · {_n(rec['failures'])} returned no content</p>")]
    fetch = (record or {}).get("fetch")
    if fetch and fetch.get("shared_with_sources", 1) > 1:
        parts.append(
            f'<p class="src-stat-label">This host serves '
            f"{fetch['shared_with_sources']} registered sources, so these "
            "figures are host-wide.</p>")
    parts.append(f'<p class="stat-note">{html.escape(ALL_TIME_PROBE_NOTE)}</p>')
    return "".join(parts)


def _source_page_body(entry, record, *, description, assessment, state,
                     all_time, fetch_log_present, days, fetch_days,
                     items_by_day, fetch_by_day):
    """The whole per-source page body. Every section renders from what
    exists: absent model text, absent databases, and unmeasured registry
    statuses each degrade to a stated absence, never to a crash or an
    invented zero."""
    sid = entry["id"]
    urls = entry["urls"]
    link = urls.get("home") or next(iter(urls.values()))
    subtitle = html.escape(
        f"{entry['branch'].capitalize()} · Tier {entry['tier']} · "
        f"{_TYPE_LABELS.get(entry['type'], entry['type'])} · "
        f"{entry['parent_org']}")
    chip = (f" {_health_chip(record['health'])}"
            if record and record.get("health") else "")
    parts = [
        f"<h1>{html.escape(entry['name'])}</h1>",
        f'<p class="src-sub">{_status_chip(entry["status"])}{chip} {subtitle}</p>',
        (f'<p class="src-links"><a href="{html.escape(link, quote=True)}">'
         "Official site</a> · "
         '<a href="sources.html">All sources</a></p>'),
        # -- What this source is ------------------------------------------
        "<h2>What this source is</h2>",
        f'<p class="src-desc">{html.escape(entry["description"])}</p>',
        _description_block(description),
        # -- Identity & registry record -----------------------------------
        "<h2>Identity and registry record</h2>",
        '<dl class="src-facts">',
        f"<dt>Registry id</dt><dd><code>{html.escape(sid)}</code></dd>",
        (f"<dt>Agency / parent organization</dt>"
         f"<dd>{html.escape(entry['parent_org'])}</dd>"),
        f"<dt>Branch</dt><dd>{html.escape(entry['branch'])}</dd>",
        (f"<dt>Type</dt><dd>"
         f"{html.escape(_TYPE_LABELS.get(entry['type'], entry['type']))}"
         "</dd>"),
        f"<dt>Status</dt><dd>{html.escape(entry['status'])}</dd>",
        f"<dt>Tier</dt><dd>{entry['tier']}</dd>",
    ]
    for kind, url in sorted(entry["urls"].items()):
        parts.append(
            f"<dt>URL ({html.escape(kind)})</dt>"
            f'<dd><a href="{html.escape(url, quote=True)}">'
            f"{html.escape(url)}</a></dd>")
    parts.append(f"<dt>Registered</dt><dd>{html.escape(entry['added'])}</dd>")
    notes = entry["notes"].strip()
    if notes:
        # Visible on the page (not folded): for an unavailable source the
        # notes ARE the refusal history, and a refusal is accountability
        # data (GUIDE §3 — the registry keeps unavailable entries forever).
        parts.append(f"<dt>Registry notes</dt>"
                     f"<dd>{html.escape(_redact_addresses(notes))}</dd>")
    parts.append("</dl>")
    # -- Methods ----------------------------------------------------------
    parts.append("<h2>How we ingest it</h2>")
    parts.append('<dl class="src-facts">')
    parts.extend(f"<dt>{html.escape(term)}</dt><dd>{html.escape(desc)}</dd>"
                 for term, desc in _methods_rows(entry))
    parts.append("</dl>")
    # -- Health -----------------------------------------------------------
    # Health leads the measured half of the page (operator, 2026-08-03):
    # the label and its reason are the reader's summary; the statistics
    # below are the numbers that back it.
    parts.append("<h2>Ingestion health</h2>")
    if record and record.get("health"):
        parts.append(f'<p class="health-lead">{_health_chip(record["health"])} '
                     f"{html.escape(record['health_reason'])}</p>")
        st = state.get(sid)
        if st:
            parts.append(
                f'<p class="health-note">This label has held since '
                f"{html.escape(st['since'])} (UTC) and was last re-checked "
                f"{html.escape(st['last_checked'])} (UTC).</p>")
        parts.append(f'<p class="health-note">'
                     f"{html.escape(health_mod.FETCH_DISCLAIMER)}</p>")
    else:
        reason = (record or {}).get("health_reason") or (
            "No health label is computed in this build.")
        parts.append(f'<p class="health-note">{html.escape(reason)}</p>')
    # -- Statistics -------------------------------------------------------
    parts.append("<h2>Ingestion statistics</h2>")
    parts.append(
        "<p>These figures describe <strong>this project's ingestion of "
        "this source</strong> — items we recorded and requests we made — "
        "and nothing else. They are not a measurement of the publisher.</p>")
    if not record:
        parts.append('<p class="stat-note">Statistics are not available '
                     "in this build.</p>")
    elif not record["measured"]:
        parts.append(f'<p class="src-stats src-unmeasured">'
                     f"{html.escape(record['health_reason'])} Ingestion "
                     "statistics are measured for active sources only.</p>")
    else:
        parts.append(f"<h3>Last {health_mod.RECENT_WINDOW_HOURS} hours</h3>")
        recent = _recent_sentence(record)
        parts.append(f'<div class="src-stats">{recent}</div>' if recent else
                     '<p class="stat-note">No trailing-24-hour figures are '
                     "available in this build.</p>")
        parts.append(f"<h3>Last {record['window_days']} days</h3>")
        parts.append(_health_block(record))
    parts.append("<h3>All time</h3>")
    parts.append(f'<div class="src-stats">'
                 f"{_all_time_block(entry, record, all_time, fetch_log_present)}"
                 "</div>")
    # -- Charts -----------------------------------------------------------
    if days:
        host = health_mod.fetch_host(entry)
        host_days = fetch_by_day.get(host, {}) if host else {}
        # Request-derived series run on the floored axis (see
        # ALL_TIME_STATS_SINCE): pre-production days are absent from the
        # chart, not drawn as observed zeroes.
        req_values = [host_days.get(d, {}).get("n", 0) for d in fetch_days]
        ms_values = [host_days.get(d, {}).get("avg_ms") for d in fetch_days]
        key = health_mod.source_key(entry)
        item_days = items_by_day.get(key, {})
        item_values = [item_days.get(d, 0) for d in days]
        charts = []
        if host and entry["type"] != "email" and fetch_days:
            shared_note = ""
            fetch = (record or {}).get("fetch")
            if fetch and fetch.get("shared_with_sources", 1) > 1:
                shared_note = " (host-wide)"
            charts.append(_svg_bar_chart(
                fetch_days, req_values,
                title=f"Requests per day to {host}{shared_note}",
                unit="requests"))
        charts.append(_svg_bar_chart(
            days, item_values, title="Items ingested per day",
            unit="items"))
        if host and entry["type"] != "email" and fetch_days:
            charts.append(_svg_sparkline(
                fetch_days, ms_values,
                title=f"Daily mean response time of {host}"))
        charts = [c for c in charts if c]
        parts.append(f"<h3>Last {CHART_WINDOW_DAYS} days, day by day</h3>")
        if charts:
            parts.extend(charts)
        else:
            parts.append('<p class="stat-note">No requests and no items '
                         f"were recorded in the last {CHART_WINDOW_DAYS} "
                         "days, so there is nothing to chart.</p>")
    # -- Assessment (optional model block) --------------------------------
    if assessment:
        parts.append("<h2>Our ingestion assessment</h2>")
        parts.append(_assessment_block(assessment))
    return "".join(parts)


def _build_source_pages(out_dir, entries, health, doc_pages=(), *,
                        pipeline_db=None, fetch_db=None):
    """Render sources/<source-id>.html for EVERY registry entry. Returns
    the number of pages written (0 with no registry)."""
    if not entries:
        return 0
    sub = out_dir / "sources"
    sub.mkdir(parents=True, exist_ok=True)
    records = (health or {}).get("sources") or {}
    fetch_log_present = bool((health or {}).get("fetch_log_available"))

    descriptions, assessments, state, items_by_day = {}, {}, {}, {}
    pconn = _ro_conn(pipeline_db or config.PIPELINE_DB)
    end_day = (health or {}).get("window_end")
    if end_day is None:
        from .sync import publication_date
        end_day = publication_date()
    days = _chart_days(end_day)
    if pconn is not None:
        try:
            import sqlite3

            from . import assess
            try:
                descriptions = assess.latest_descriptions(pconn)
                assessments = assess.latest_assessments(pconn)
            except sqlite3.Error:
                descriptions, assessments = {}, {}
            state = health_mod.health_state(pconn)
            items_by_day = _daily_items(pconn, days[0], days[-1])
        finally:
            pconn.close()
    # Request-derived figures start at the production floor (see
    # ALL_TIME_STATS_SINCE): the daily series' query starts at the later
    # of the chart window and the floor, and the request/response charts
    # clip their day axis to it so a pre-floor day renders as absent,
    # never as an observed zero.
    fetch_days = [d for d in days if d >= ALL_TIME_STATS_SINCE]
    fetch_by_day = {}
    fconn = _ro_conn(fetch_db or config.FETCH_LOG_DB)
    if fconn is not None and fetch_days:
        try:
            fetch_by_day = _daily_fetches(fconn, f"{fetch_days[0]}T00:00:00Z")
        finally:
            fconn.close()
    all_time = health_mod.fetch_stats_all_time(
        fetch_db=fetch_db or config.FETCH_LOG_DB,
        since=ALL_TIME_STATS_SINCE)

    for entry in entries:
        body = _source_page_body(
            entry, records.get(entry["id"]),
            description=descriptions.get(entry["id"]),
            assessment=assessments.get(entry["id"]),
            state=state, all_time=all_time,
            fetch_log_present=fetch_log_present,
            days=days, fetch_days=fetch_days, items_by_day=items_by_day,
            fetch_by_day=fetch_by_day)
        page = _render_page(
            f"{entry['name']} — source page — {SITE_TITLE}",
            body,
            _site_nav(doc_pages, current="sources"),
            f"sources/registry.yaml (id: {entry['id']})",
            description=(f"How the Free Agentic Publication Digester ingests "
                         f"{entry['name']}: method, status, measured "
                         "statistics, and health history."),
        )
        (sub / f"{entry['id']}.html").write_text(
            _rebase_page(page), encoding="utf-8")
    return len(entries)


# ---------------------------------------------------------------------------
# Blog (blog.html + blog-<slug>.html)
# ---------------------------------------------------------------------------
# Commentary about the project — how it is built and why — deliberately
# separate from the digests, which are the official-record surface. Nothing
# here enters digests.json or the Atom feed; mixing commentary into those
# would misrepresent what they contain.
#
# PUBLICATION IS BY ALLOWLIST, NEVER BY GLOB.  docs/devnotes/ is the
# project's INTERNAL development-narrative directory: working notes, drafts,
# and its own README all live there and are written for contributors, not
# readers of fapd.info. A devnote becomes public only when a person adds it
# to `_BLOG_POSTS` below, on purpose, with a slug and a publication date.
# Do not replace this tuple with a directory scan, and do not add an entry
# just because a file exists — that would publish internal notes the moment
# somebody wrote one.
#
# URL layout: `blog.html` for the index, `blog-<slug>.html` for each post,
# flat in the site root. Digest URLs are exactly `/<YYYY-MM-DD>.html`, so the
# `blog-` prefix cannot collide with them (or with a doc page's stem), and
# staying flat keeps every page on the same relative paths the shared shell
# already emits — `style.css`, `index.html`, `llms.txt` — so posts need no
# second rendering path. A `blog/` subdirectory would have required one.
_BLOG_DIR = ("docs", "devnotes")

# (source filename in docs/devnotes/, url slug, publication date)
_BLOG_POSTS = (
    ("2026-08-08-a-note-from-the-machine-side.md", "machine-side", "2026-08-08"),
    ("2026-08-05-human-side-of-the-team.md", "human-side", "2026-08-05"),
    ("2026-07-30-launch-article.md", "launch", "2026-07-30"),
)


def _post_teaser(md_text):
    """First sentence of a post's own opening prose, for index cards — the
    blog counterpart of `_teaser` for digests. The title, an italic
    dateline, section headings, quotes and lists are skipped; the first
    ordinary paragraph supplies the sentence."""
    for block in md_text.split("\n\n"):
        para = " ".join(block.split())
        if not para or para[0] in "#*_>-|":
            continue
        return re.split(r"(?<=[.;])\s", para, maxsplit=1)[0] or None
    return None


def _blog_sources():
    """[(slug, date, title, teaser, markdown, canonical)] for the allowlisted
    posts that exist on disk, newest first. An allowlisted file that is
    missing is skipped rather than fatal, so a rename degrades to no page
    instead of a broken link. Files NOT in `_BLOG_POSTS` are never read."""
    posts = []
    for filename, slug, date in _BLOG_POSTS:
        path = config.PROJECT_ROOT.joinpath(*_BLOG_DIR, filename)
        if not path.is_file():
            continue
        md_text = path.read_text(encoding="utf-8")
        match = _H1_RE.search(md_text)
        title = match.group(1) if match else slug.replace("-", " ").capitalize()
        posts.append((slug, date, title, _post_teaser(md_text), md_text,
                      "/".join(_BLOG_DIR) + f"/{filename}"))
    return sorted(posts, key=lambda p: p[1], reverse=True)


def _blog_exists():
    """Whether blog.html will exist — the nav must not link a page that was
    not built (same contract as `_registry_exists`)."""
    return any(config.PROJECT_ROOT.joinpath(*_BLOG_DIR, f).is_file()
               for f, _slug, _date in _BLOG_POSTS)


def _blog_body(posts):
    cards = []
    for slug, date, title, teaser, _md, _canonical in posts:
        teaser_html = (f'<p class="teaser">{html.escape(teaser)}</p>'
                       if teaser else "")
        cards.append(
            f'<li><a class="post-title" href="blog-{slug}.html">'
            f"{html.escape(title)}</a>"
            f'<span class="post-date">{html.escape(date)}</span>'
            f"{teaser_html}</li>")
    return (
        "<h1>Blog</h1>"
        "<p>Notes on how the Free Agentic Publication Digester is built: "
        "the pipeline, the editorial gates, and the access policy it keeps "
        "with the servers it reads. These posts are commentary about the "
        "project. They are not part of the daily digest and not part of the "
        'official record — for what the government published, read the '
        '<a href="index.html">dated digests</a>.</p>'
        f'<ul class="post-list">{"".join(cards)}</ul>'
    )


def _blog_post_body(date, md_text):
    """A post rendered through the site's ordinary Markdown pipeline: the
    article's own words, an explicit publication date under its title, and a
    link back to the index. No digest readability layer — that layer encodes
    digest conventions (inclusion rules, citations) a post does not have."""
    _MD.reset()
    body = _MD.convert(md_text)
    meta = (f'<p class="post-meta">Published {html.escape(date)} · '
            "commentary about the project, not part of the daily digest or "
            "the official record</p>")
    head, sep, tail = body.partition("</h1>")
    body = head + sep + meta + tail if sep else meta + body
    # Wrapped so long-form typography (section headings, pull quotes) is
    # scoped to posts. The digest body is dense reference layout styled by
    # _style_digest_body; neither register should leak into the other.
    return ('<article class="post">' + body
            + '<p class="post-back"><a href="blog.html">'
              "&larr; All posts</a></p></article>")


def _build_blog(out_dir, doc_pages=()):
    """Render blog.html plus one page per allowlisted post. Returns
    [(slug, date, title)] for the machine surfaces; an empty list means no
    index page was written and nothing links to one."""
    posts = _blog_sources()
    if not posts:
        return []
    brand = SITE_TITLE.split(" — ")[0]
    for slug, date, title, _teaser, md_text, canonical in posts:
        # A post's own images, if any, live beside it in
        # docs/devnotes/assets/<slug>/ (tracked, so they also render on
        # GitHub's own view of the source file) and are mirrored here under
        # the same slug so the relative markdown path resolves once flattened
        # into the site root — the same copy shape build_site already uses
        # for digests/assets/<date>/ (never digest dates, so no collision).
        post_assets = config.PROJECT_ROOT.joinpath(*_BLOG_DIR, "assets", slug)
        if post_assets.is_dir():
            asset_dst = out_dir / "assets" / slug
            asset_dst.mkdir(parents=True, exist_ok=True)
            for f in post_assets.iterdir():
                if f.is_file():
                    shutil.copy2(f, asset_dst / f.name)
        page = _render_page(
            # No brand suffix when the post's own title already carries it.
            title if brand in title else f"{title} — {SITE_TITLE}",
            _blog_post_body(date, md_text),
            # A post keeps the Blog nav link (it is not the index); only the
            # index omits its own.
            _site_nav(doc_pages),
            canonical,
        )
        (out_dir / f"blog-{slug}.html").write_text(page, encoding="utf-8")
    index = _render_page(
        f"Blog — {SITE_TITLE}",
        _blog_body(posts),
        _site_nav(doc_pages, current="blog"),
        "/".join(_BLOG_DIR) + "/ (allowlisted posts only)",
        description=("Notes on how the Free Agentic Publication Digester is "
                     "built — commentary about the project, not part of the "
                     "daily digest."),
    )
    (out_dir / "blog.html").write_text(index, encoding="utf-8")
    return [(slug, date, title) for slug, date, title, _t, _m, _c in posts]


def refresh_sources(out_dir=None, *, pipeline_db=None, fetch_db=None,
                    doc_pages=None):
    """Rebuild sources.html and sources.json alone — the health figures,
    not the whole site.

    build_site() runs once a day in the end-of-day finalizer, which is
    the wrong cadence for health: a source that starts failing produces
    NO journal movement, so the live page's watermark trigger cannot see
    it either, and the outage would sit unreported until the next EOD.
    This path is SQL plus a render, no tokens and no requests, so the
    collector can call it on its own clock (docs/code-standards §2 r5:
    re-rendering must always cost zero tokens)."""
    out_dir = Path(out_dir or config.SITE_DIR)
    registry_path = config.PROJECT_ROOT / "sources" / "registry.yaml"
    if not registry_path.exists():
        return {"built": False, "reason": "no registry"}
    entries = sources.load_registry(registry_path)
    hp = health_mod.source_health(entries, pipeline_db=pipeline_db,
                              fetch_db=fetch_db)
    if doc_pages is None:
        doc_pages = _doc_page_index()
    _build_sources_page(out_dir, doc_pages, entries, hp)
    _build_source_pages(out_dir, entries, hp, doc_pages,
                        pipeline_db=pipeline_db, fetch_db=fetch_db)
    (out_dir / "sources.json").write_text(
        _json_mod.dumps(_sources_json(entries, hp, config.SITE_BASE_URL),
                        indent=1, sort_keys=True) + "\n", encoding="utf-8")
    # The computed payload travels with the result so the caller (the
    # collector's RenderWorker persisting health labels) never has to
    # recompute it — one computation per cycle, one truth.
    return {"built": True, "sources": len(entries),
            "measured": bool(getattr(hp, "available", True)),
            "health": hp}


def build_site(digest_dir=None, out_dir=None, *, pipeline_db=None,
               fetch_db=None):
    """Convert every digest to HTML plus an index. Returns stats.

    The database paths are injected (docs/code-standards.md §2 rule 3) so
    a test can point the source-health computation at throwaway SQLite
    files. Absent databases are not an error: `health.source_health`
    reports itself unavailable and the source guide says so in place."""
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
        body = _inject_day_view_link(body, path.stem, md_text, out_dir)
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
    registry_entries = _registry_entries()
    # Computed once and shared by the human page and the machine surface,
    # so the two can never disagree about a number.
    source_stats = (
        health_mod.source_health(registry_entries, pipeline_db=pipeline_db,
                                 fetch_db=fetch_db)
        if registry_entries else None)
    sources_built = _build_sources_page(out_dir, doc_pages, registry_entries,
                                        source_stats)
    source_pages = _build_source_pages(out_dir, registry_entries, source_stats,
                                       doc_pages, pipeline_db=pipeline_db,
                                       fetch_db=fetch_db)
    blog_posts = _build_blog(out_dir, doc_pages)
    _build_agent_surfaces(out_dir, dates, teasers, doc_pages,
                          base=config.SITE_BASE_URL, blog_posts=blog_posts,
                          entries=registry_entries, health=source_stats)
    sources_link = (
        '<p class="tagline"><a href="sources.html">Source guide</a> — every '
        "federal source we ingest, plan to ingest, or have evaluated, with "
        "method, status, and the items and request outcomes we recorded "
        "for each.</p>" if sources_built else ""
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
        "blog_posts": len(blog_posts),
        "source_pages": source_pages,
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


def _day_disclosure(date, reconstructed_on=None):
    """The frozen day view's disclosure (GUIDE §5, amended 2026-08-03):
    what the page is, when it was frozen, and that the dated digest is
    the canonical record. `reconstructed_on` is for the one-shot
    backfill of past days from the stored observation journal — the
    render date is disclosed so a reconstructed listing never presents
    itself as having been frozen live at end of day."""
    frozen = ("frozen at end of day" if not reconstructed_on else
              "reconstructed from the stored observation journal on "
              f"{reconstructed_on}")
    return (
        f"This is the complete observed listing for publication day {date}: "
        "every item our collectors recorded for this day, with the "
        "mechanical rules applied, " + frozen + ". It is not the digest — "
        "the dated digest is the canonical record for this day."
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
    "VOTES": "Recorded vote",
    "BILLACTIONS": "Bill action",
}


# Mechanical per-item metadata (zero LLM). Branch by collection; document
# type expanded into plain words; channel from the journal source class.
_TODAY_BRANCH = {"CREC": "legislative", "BILLS": "legislative",
                 "PLAW": "legislative", "FR": "executive",
                 "USCOURTS": "judicial", "AGENCYPR": "executive",
                 "VOTES": "legislative", "BILLACTIONS": "legislative",
                 # The President's own instruments (GUIDE §3, 2026-08-06).
                 "PRESACT": "executive"}
_TODAY_DOC_TYPES = {
    "RULE": "final rule", "PRORULE": "proposed rule", "NOTICE": "notice",
    "PRESDOCU": "presidential document", "SENATE": "senate floor",
    "HOUSE": "house floor", "EXTENSIONS": "extensions of remarks",
    "DAILYDIGEST": "daily digest", "PRESS": "press release",
    "ROLLCALL": "roll-call vote", "BILLACTION": "bill action",
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


# Openings are the first ~240 chars of extracted text; for some agency
# pages that is scraped navigation chrome, not prose (live 2026-08-02:
# nasa items showed "Explore Search News & Events News & Events Recently
# Published Video Series…"). A mechanical prose check gates display:
# real openings carry sentence punctuation and mostly-lowercase running
# words; chrome carries neither. Suppressed openings stay available
# verbatim in today.json (opening_verbatim).
_MIN_PROSE_LOWER_RATIO = 0.5


def _looks_like_prose(text):
    words = (text or "").split()
    if len(words) < 8:
        return False
    if not re.search(r"[.!?](\s|$)", text):
        return False
    lower = sum(1 for w in words if w[:1].islower())
    return lower / len(words) >= _MIN_PROSE_LOWER_RATIO


def _et_hour_label(utc_stamp):
    """'2 PM Eastern' for the ET hour a stamp falls in, or None when the
    stamp is unparseable — the stream's hour headings, so a 300-item day
    has scannable structure and a quiet evening is visible as absence."""
    import datetime as _dt

    try:
        when = _dt.datetime.fromisoformat(utc_stamp)
    except (TypeError, ValueError):
        return None
    when = when.astimezone(config.PUBLICATION_TZ)
    hour = when.hour % 12 or 12
    return f"{hour} {'AM' if when.hour < 12 else 'PM'} Eastern"


def _today_display_title(item):
    """The reader-facing label for one listing row.

    Deliberately the digest's chain and the digest's helpers
    (report._crec_item_lines): the live page and the dated digest must
    never disagree about what a document is called. _display_title
    re-cases ALL-CAPS source headings — the Congressional Record's
    Extensions titles arrive shouting ("HONORING THE SERVICE OF ...") —
    and is the same normalization the lexicon gate reasons about
    (report.py, banned-term forms).

    package_id is the LAST resort and only honest for whole-package
    documents, where the journal's granule_id is '' and the package
    genuinely is the document (BILLS). For a granule-level collection it
    is the whole day's issue, identical on every row: until 2026-08-07
    this function's predecessor fell straight to it, and a day's entire
    Congressional Record listed as 155 rows all titled "CREC-2026-08-06"
    (F-022).
    """
    from .report import _display_title, _first_nonempty_line, _truncate

    raw = ((item["title"] or "").strip()
           or _first_nonempty_line(item.get("opening"))
           or item["granule_id"]
           or item["package_id"])
    return _truncate(_display_title(raw))


def _today_item_row(item, filterable=()):
    title = _today_display_title(item)
    gran = item["granule_id"]
    cite = item["package_id"] + (f" / {gran}" if gran else "")
    stamp = item["observed_at"] or ""
    # A bare clock reading followed by two letters says nothing about
    # what the number is, and the distinction this project cares about
    # most — observation time, not publication time — was nowhere in the
    # markup (1.3.1, A11Y-14). "ET" stays visible and is spoken in full.
    observed = (f'<time class="utc" datetime="{html.escape(stamp)}">'
                f'<span class="vh">Observed at </span>'
                f"{html.escape(_et_clock(stamp))}"
                f'<span class="vh"> Eastern time</span>'
                f'<span aria-hidden="true"> ET</span></time>'
                if stamp else "")
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
    # A govinfo package id IS the citation and stays on screen; the
    # synthetic PR-… hash id is an internal artifact — it lives in
    # today.json, not in a reader's meta line.
    if item["source_class"] == "govinfo":
        meta_bits.append(cite)
    # The publisher's date as the parsed publication day, never the raw
    # RFC-822 header ("Sun, 02 Aug 2026 04:05:00 +0000" is a wire
    # format, not reader text). An unparseable claim is omitted here and
    # preserved verbatim in today.json.
    if item.get("claimed_day"):
        meta_bits.append(f"publisher-dated {item['claimed_day']}")
    # Multi-channel corroboration (GUIDE §3, 2026-08-03): the mark is a
    # reader-facing fact — this document was received independently
    # through another channel — never a judgment about the content.
    for c in item.get("corroborated_by") or ():
        meta_bits.append(f"corroborated: also received via "
                         f"{c['channel_label']}")
    meta = html.escape(" · ".join(meta_bits))

    if item["summary"]:
        # "FAPD-AI" names the writer rather than describing the method
        # (operator, 2026-08-07). GUIDE §2's obligation is that
        # machine-generated prose does not hide its own authorship, not
        # that it use a particular wording — and "AI" is in the name. The
        # "How this live view works" prose names both labels explicitly
        # so a first-time reader does not have to infer it from branding.
        label = ("official summary" if item["summary_method"] == "official"
                 else "FAPD-AI")
        rule = (f' <span class="rule-note">{html.escape(item["inclusion_rule"])}'
                "</span>" if item["inclusion_rule"] else "")
        body = (f'<p class="today-summary"><span class="plain-label">'
                f"{label}:</span> {html.escape(item['summary'])}{rule}</p>")
    elif item["opening"] and _looks_like_prose(item["opening"]):
        snippet = " ".join(item["opening"].split())
        if len(snippet) > 200:
            snippet = snippet[:200].rsplit(" ", 1)[0] + "…"
        body = (f'<p class="today-summary today-opening">'
                f'<span class="plain-label">opening text (verbatim):</span> '
                f"{html.escape(snippet)}</p>")
    else:
        body = ""
    # Keyword classes drive the CSS checkbox filter (no JavaScript). The
    # time sits in its own grid column; everything else is wrapped so the
    # two-column layout is real alignment, not an approximated margin.
    keys = " ".join(f"k-{_slug(t)}" for t in _today_item_tags(item))
    return (
        f'<li class="today-item {keys}">'
        f'<span class="today-time">{observed}</span>'
        f'<div class="today-body">'
        f"<strong>{title_html}</strong> "
        f'<span class="today-chips">{chips}</span>'
        f'<div class="today-item-meta">{meta}</div>{body}</div></li>'
    )


# Keyword filtering on /today is pure CSS — no script beyond the one
# local-time snippet the page already carries (code-standards §2 r10).
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
# Below this many items the filter bar is pure overhead — a wall of
# chips each reading "1" to filter a stream shorter than the bar itself
# (live 2026-08-02: a full bar rendered above exactly one item).
MIN_FILTER_ITEMS = 5
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
    # "executive 285" is spoken as a name and a bare number; the unit is
    # supplied in visually-hidden text (1.3.1, A11Y-14).
    return (f'<label class="{_tag_classes(tag, "filter-chip")}{partners}" '
            f'for="f-{_slug(tag)}">{html.escape(tag)}'
            f'<span class="filter-n"><span class="vh">, </span>{count}'
            f'<span class="vh"> items</span></span></label>')


def _today_filter_bar(facets, total, pairs=None):
    """(inputs, bar_html, css) for the day's keywords: branches on their
    own row, then every remaining keyword in one full listing. Choosing
    a keyword narrows the offered set to keywords that actually share an
    entry with it, so no combination on offer leads to an empty page.

    The bar is a labelled `role="group"`, not a `<nav>` (A11Y-13): a
    58-control form group is not navigation, and listing it as such put
    it in the screen reader's landmark and navigation-region lists."""
    offered = list(facets.items())[:MAX_FILTER_KEYWORDS]
    dropped = len(facets) - len(offered)
    if not offered:
        return "", "", ""

    inputs, css = [], []
    for tag, n in offered:
        slug = _slug(tag)
        # One checkbox is referenced by a <label> in the bar AND by one on
        # every matching entry — hundreds of them. HTML-AAM concatenates
        # every label's text into the accessible name, so without this
        # aria-label the control announces its keyword hundreds of times
        # (measured: ~2,600 characters for "executive"). aria-label wins
        # over <label>, so the shared-label design survives intact.
        inputs.append(
            f'<input type="checkbox" class="filter-cb" id="f-{slug}"'
            f' aria-label="Filter to {html.escape(tag, quote=True)}'
            f' — {n} item(s)">')
        css.append(
            f"#f-{slug}:checked ~ .today-list > .today-item:not(.k-{slug})"
            "{display:none}\n"
            f'#f-{slug}:checked ~ .filter-bar label[for="f-{slug}"],\n'
            f'#f-{slug}:checked ~ .today-list label[for="f-{slug}"]'
            "{background:var(--accent);color:var(--accent-on);border-color:var(--accent)}\n"
            f'#f-{slug}:focus-visible ~ .filter-bar label[for="f-{slug}"]'
            "{outline:2px solid var(--accent);outline-offset:2px}\n"
            # narrow the remaining options to keywords seen alongside this one
            f"#f-{slug}:checked ~ .filter-bar label:not(.c-{slug})"
            "{display:none}\n"
            # a glyph, not only a color, marks what is selected — and it
            # is the signal that survives grayscale and forced-colors
            f'#f-{slug}:checked ~ .filter-bar label[for="f-{slug}"]::before,\n'
            f'#f-{slug}:checked ~ .today-list label[for="f-{slug}"]::before'
            '{content:"\\2713\\00a0"}\n'
            # ...and the status line names it in words, so the change is
            # stated and not only shown (4.1.3)
            f".today-stream:has(#f-{slug}:checked) .fs-{slug}"
            "{display:inline}\n")

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
    # Selecting a keyword changes what is on the page and nothing said so
    # — the bar's "N item(s) unfiltered" is the before number and never
    # moves (4.1.3, A11Y-07). One pre-rendered span per keyword, each
    # revealed by its own checkbox, names the active filters in words.
    # Whether a live region announces a child that changes from
    # display:none to display:inline is browser- and AT-dependent; this
    # is a visible readout that MAY announce, and the public statement
    # says exactly that.
    status = (
        '<p class="filter-status" role="status">'
        f'<span class="fs-none">No keyword filter is selected; all {total} '
        "item(s) are shown.</span>"
        '<span class="fs-lead">Filtered to items tagged: </span>'
        + "".join(f'<span class="fs-{_slug(t_)}">{html.escape(t_)} </span>'
                  for t_, _n in offered)
        + "</p>"
    )
    bar = (
        '<div class="filter-bar" role="group" aria-labelledby="filter-heading">'
        '<h2 class="filter-lead" id="filter-heading">Filter by keyword '
        '<span class="rule-note">click to select, again to clear; '
        "several selected narrows to items carrying all of them · "
        f"{total} item(s) unfiltered</span>"
        '<button type="reset" class="filter-clear">clear filters</button></h2>'
        f"{rows}{status}{note}</div>"
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
    from .sync import publication_date

    return _build_day_page(conn, date or publication_date(),
                           Path(out_dir or config.SITE_DIR), live=True)


def build_day(conn, date, out_dir=None, *, reconstructed_on=None):
    """Render the frozen day view — site/day/<date>.html + .json (GUIDE
    §5, amended 2026-08-03): the same full-entry listing the live page
    shows, rendered by the SAME machinery (this function and build_today
    share _build_day_page — parameterized, never a reimplementation),
    frozen from the database state at call time and committed with the
    evidence. Differs from /today only in its disclosure (complete
    observed listing, frozen at end of day, the dated digest is the
    canonical record) and in carrying no live affordances.

    A date the item journal does not cover renders a designed absent
    state disclosing why — days before the journal existed have no day
    view; the gap is disclosed, not backfilled. `reconstructed_on` is
    for the one-shot journal-backfill of past days: it swaps the
    disclosure's "frozen at end of day" for "reconstructed from the
    stored observation journal on <date>"."""
    return _build_day_page(conn, str(date), Path(out_dir or config.SITE_DIR),
                           live=False, reconstructed_on=reconstructed_on)


def _day_absent_page(date, first, out_dir):
    """The designed absent state: a date before the observation journal
    existed has no day view, and the page says exactly why instead of
    rendering an empty listing that would read as a quiet day."""
    reason = (
        f"No day view exists for {date}. The observation journal that "
        "records item arrivals "
        + (f"began on {first}" if first else "has not recorded any items")
        + ", and days before it have no observed listing to freeze — the "
        "gap is disclosed, not backfilled. The dated digest, where one "
        "exists, is the record for this day.")
    body = (
        f"<h1>Observed listing — {html.escape(date)}</h1>"
        f'<p class="today-disclosure">{html.escape(reason)}</p>'
        '<p><a href="index.html">All digests</a></p>')
    page = _render_page(
        f"Observed listing {date} — {SITE_TITLE}", body,
        _site_nav(_doc_page_index()),
        f"no day view exists for {date} (observation journal coverage)",
        description=reason)
    day_dir = out_dir / "day"
    day_dir.mkdir(parents=True, exist_ok=True)
    (day_dir / f"{date}.html").write_text(_rebase_page(page),
                                          encoding="utf-8")
    (day_dir / f"{date}.json").write_text(_json_mod.dumps({
        "date": date,
        "generated": utc_now_iso(),
        "available": False,
        "unavailable_reason": reason,
        "canonical_record": f"the dated digest for {date}, where one exists",
        "items": [],
    }, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return {"date": date, "items": 0, "available": False, "out_dir": out_dir}


def _build_day_page(conn, date, out_dir, *, live, reconstructed_on=None):
    import json as _json

    from .collect import today_status

    out_dir.mkdir(parents=True, exist_ok=True)
    if not live:
        from .report import _journal_first_day
        first = _journal_first_day(conn)
        if first is None or date < first:
            return _day_absent_page(date, first, out_dir)
    status = today_status(conn, date)
    # The live page must apply the SAME dating discipline the digest does.
    # It keys off the journal's digest_date, which for agency items is our
    # OBSERVATION day — so first-activation backfill (usps-newsroom shipped
    # 664 items dated back to 2021, odni-news 54) rendered as though it were
    # today's news, while the digest correctly excluded it under
    # AGENCYPR-EX-01. Same helper as report.py, so the two cannot drift.
    from .report import _claimed_day

    todays, backfill = [], []
    for _i in status["items"]:
        try:
            meta = _json_mod.loads(_i.get("metadata") or "{}")
        except (TypeError, ValueError):
            meta = {}
        claimed = _claimed_day(meta) if meta else None
        if claimed is None:
            claimed = _claimed_day({"claimed_published_at":
                                    _i.get("claimed_published_at")})
        _i["claimed_day"] = claimed
        _i["is_backfill"] = bool(claimed and claimed != date)
        (backfill if _i["is_backfill"] else todays).append(_i)
    # One document, several channels (GUIDE §3 corroboration amendment,
    # 2026-08-03): items sharing a canonical URL merge to one listing,
    # marked corroborated; the machine surface keeps EVERY observation,
    # flagged — the is_backfill precedent. Same shared helper as the
    # digest's section 6, so the surfaces cannot disagree.
    from .report import corroborate
    merged = corroborate(todays,
                         url_of=lambda i: i.get("url"),
                         is_email=lambda i: i.get("channel") == "email")
    todays, duplicates = [], []
    for primary, dups in merged:
        if dups:
            primary["corroborated_by"] = [
                {"package_id": d["package_id"],
                 "channel_label": _today_channel_label(d),
                 "observed_at": d["observed_at"],
                 "dkim_result": d.get("dkim_result")} for d in dups]
            for d in dups:
                d["duplicate_of"] = primary["package_id"]
            duplicates.extend(dups)
        todays.append(primary)
    status["items"] = todays
    status["backfill"] = backfill
    status["duplicates"] = duplicates

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
    digest_exists = (Path(config.DIGEST_DIR) / f"{date}.md").exists()
    # Bare dates are unusable in a screen reader's link list (2.4.4).
    recent_links = " · ".join(
        f'<a href="{d}.html"><span class="vh">Digest for </span>{d}</a>'
        for d in recent)
    about = (
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
        "text. A summary labeled <strong>official summary</strong> is the "
        "publisher\u2019s own; one labeled <strong>FAPD-AI</strong> was "
        "written by this project\u2019s AI from the official text and is "
        "ours, not the government\u2019s. Those tags are clickable: selecting one here or in the "
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
    # One sentence stays visible; the full explanation collapses into a
    # native <details> (no JS). Three paragraphs of standing prose pushed
    # the stream below the fold on every load, forever.
    if live:
        intro = (
            "<p>Official federal publications as our collectors observe "
            "them, newest first — refreshed within minutes of arrival. "
            "Times are Eastern (Washington's clock).</p>"
            '<details class="today-about"><summary>How this live view works'
            f"</summary>{about}</details>")
    else:
        digest_link = (
            f' Read the <a href="{date}.html"><span class="vh">Daily '
            f"Digest for </span>{date} digest</a>."
            if digest_exists else "")
        intro = (
            "<p>Official federal publications as our collectors observed "
            "them through this day, newest first. Times are Eastern "
            "(Washington's clock). This listing does not update."
            f"{digest_link}</p>")
    # The federal working calendar explains a quiet stream before a
    # reader (or an agent reading today.json) wonders if the pipeline is
    # broken: a Sunday /today with one item is the publishers resting,
    # not us failing (observed live, 2026-08-02).
    from . import fedcal
    day_context = fedcal.reduced_publishing(date)
    if live:
        heading = f"Today — {date} (in progress)"
        disclosure_text = _TODAY_DISCLOSURE
    else:
        heading = f"Observed listing — {date}"
        disclosure_text = _day_disclosure(date, reconstructed_on)
    disclosure_html = html.escape(disclosure_text)
    if not live and digest_exists:
        disclosure_html += (f' <a href="{date}.html">Daily Digest &mdash; '
                            f"{date}</a>.")
    parts = [
        f"<h1>{html.escape(heading)}</h1>",
    ]
    if day_context:
        label = ("Weekend note" if day_context["kind"] == "weekend"
                 else "Federal holiday note")
        parts.append(
            f'<div class="live-callout today-context"><strong>{label}:'
            f"</strong> {html.escape(day_context['note'])}</div>")
    if live:
        meta = (f'<p class="today-meta">Last updated <time class="utc"'
                f' datetime="{html.escape(now)}">{html.escape(_et_clock(now))}'
                f" ET</time> · {len(status['items'])} item(s) observed so far"
                f" · {status['pending_llm']} item(s) awaiting an FAPD-AI summary.")
    else:
        meta = (f'<p class="today-meta">Generated <time class="utc"'
                f' datetime="{html.escape(now)}">{html.escape(_et_clock(now))}'
                f" ET</time> · {len(status['items'])} item(s) observed for "
                f"this day · {status['pending_llm']} item(s) without a "
                "stored FAPD-AI summary (a disclosed gap, not pending work).")
    arrived = "arrived today" if live else "arrived during this day"
    parts += [
        f'<p class="today-disclosure">{disclosure_html}</p>',
        intro,
        (meta
         + (f" A further {len(status['backfill'])} item(s) {arrived}"
            " that their publishers date earlier; they are not this day's"
            " news and are listed in the dated digest's coverage"
            " accounting, not here."
            if status.get("backfill") else "")
         + (f" {len(status['duplicates'])} item(s) arrived through a"
            " second ingestion channel (the same canonical URL twice);"
            " each is listed once below, marked corroborated, with every"
            " observation kept in the machine surface."
            if status.get("duplicates") else "")
         + "</p>"),
    ]
    if day_chips:
        parts.append('<p class="today-chips">Day so far: '
                     + "".join(day_chips) + "</p>")
    facets = _today_filter_facets(status["items"])
    if len(status["items"]) >= MIN_FILTER_ITEMS:
        inputs, filter_bar, filter_css = _today_filter_bar(
            facets, len(status["items"]), _today_filter_pairs(status["items"]))
    else:
        # A bar of chips each reading "1" above a stream shorter than the
        # bar is overhead, not filtering.
        inputs = filter_bar = filter_css = ""
    filterable = ({_slug(k) for k in list(facets)[:MAX_FILTER_KEYWORDS]}
                  if filter_bar else set())
    if not status["items"]:
        parts.append('<h2 id="today-stream" tabindex="-1">'
                     "Observed publications</h2>")
        if live:
            parts.append(
                '<div class="live-callout">No items observed yet for this '
                "publication day. Collectors poll continuously — govinfo "
                "about every half hour, agency newsrooms about hourly, email "
                "bulletins about every fifteen minutes — and this page "
                "rebuilds within about five minutes of a new arrival.</div>")
        else:
            parts.append(
                '<div class="live-callout">No items were observed for this '
                "publication day — an explicit empty record, not an "
                "omission. Weekends and federal holidays are ordinary "
                "reasons for a quiet day.</div>")
    else:
        # The form is what makes filtering work without script: the
        # checkboxes, the bar, and the stream are siblings inside it (so
        # the CSS sibling combinator reaches the list), and its native
        # reset button clears every selection at once. One chronological
        # stream, newest first — hour headings for scanability, no
        # section headings; every entry names its own branch, agency,
        # and document type.
        if filter_bar:
            parts.append(
                f'<a class="skip-link" href="#today-stream">Skip '
                f"{len(facets)} keyword filters and go to the stream</a>")
        # Group consecutive items (already newest-first) by the ET hour
        # they were observed in. Each hour is its own <ul>; the filter
        # CSS reaches every list via the general-sibling combinator, and
        # the shown-counter scope lives on the form so it totals across
        # lists. Known limit, accepted: an hour heading stays visible
        # when a filter hides its whole group — CSS cannot know — while
        # the count line stays truthful.
        stream = []
        current_hour = object()
        for i in status["items"]:
            hour = _et_hour_label(i["observed_at"] or "")
            if hour != current_hour:
                if stream:
                    stream.append("</ul>")
                if hour:
                    stream.append(f'<h3 class="today-hour">{hour}</h3>')
                stream.append('<ul class="today-list">')
                current_hour = hour
            stream.append(_today_item_row(i, filterable))
        stream.append("</ul>")
        form_action = "today.html" if live else f"day/{date}.html"
        parts.append(
            f'<form class="today-stream" action="{form_action}" method="get">'
            + inputs + filter_bar
            # The stream gets its own heading (A11Y-13): the page had
            # exactly one heading for 400 KB of content, so there was no
            # way to reach either the filter or the list by heading. It
            # sits inside the form as a general sibling of the
            # checkboxes, which the `~` filter rules require.
            + '<h2 id="today-stream" tabindex="-1">Observed publications</h2>'
            + "".join(stream)
            # A CSS counter over the items still displayed — the only
            # script-free way to state how many survived the filter.
            + '<p class="filter-count"></p></form>')

    nav = _site_nav(_doc_page_index(), current="today" if live else None)
    head_extra = (f"<style>\n{filter_css}</style>\n" if filter_css else "")
    if live:
        # The site's one script lives on /today.html only (docs/
        # code-standards §2 r10); the frozen day view ships none — its
        # server-rendered Eastern stamps stand alone.
        head_extra += _LOCAL_TIME_JS
    if live:
        page = _render_page(f"Today (live) — {SITE_TITLE}", "".join(parts),
                            nav,
                            "derived-only: not part of the committed record",
                            head_extra=head_extra)
        html_path = out_dir / "today.html"
        json_path = out_dir / "today.json"
        html_path.write_text(page, encoding="utf-8")
    else:
        page = _render_page(f"Observed listing {date} — {SITE_TITLE}",
                            "".join(parts), nav,
                            f"site/day/{date}.html (frozen day view; the "
                            f"canonical record is digests/{date}.md)",
                            head_extra=head_extra)
        day_dir = out_dir / "day"
        day_dir.mkdir(parents=True, exist_ok=True)
        html_path = day_dir / f"{date}.html"
        json_path = day_dir / f"{date}.json"
        html_path.write_text(_rebase_page(page), encoding="utf-8")

    json_items = []
    for i in (list(status["items"]) + list(status.get("duplicates") or [])
              + list(status.get("backfill") or [])):
        row = {k: v for k, v in i.items() if k != "opening"}
        row["opening_verbatim"] = i["opening"]  # official text, unedited
        row["official_url"] = _today_official_url(i)
        row["channel_label"] = _today_channel_label(i)
        row["tags"] = _today_item_tags(i)       # mechanical, zero-LLM
        row["claimed_day"] = i.get("claimed_day")
        row["is_backfill"] = bool(i.get("is_backfill"))
        json_items.append(row)
    payload = {
        "date": date,
        "generated": now,
        "disclosure": disclosure_text,
        "canonical_record": "the dated digest, frozen at end of day",
        "labels": {"summary_method": "official = agency/GPO text;"
                                     " llm = model-generated, labeled",
                   "opening_verbatim": "first ~240 chars of the official"
                                       " text, unedited",
                   "tags": "mechanical (branch, document type, agency);"
                           " no model-generated item tags yet",
                   "items": "ALL observed items including backfill —"
                            " filter on is_backfill=false to match the"
                            " human page's listing",
                   "is_backfill": "true = the publisher dates this item"
                                  " on another day (claimed_day); not"
                                  " part of this day's news",
                   "corroborated_by": "on a listed item: the OTHER"
                                      " ingestion channels the same"
                                      " document (same canonical URL)"
                                      " arrived through — independent"
                                      " receipt, not a content judgment",
                   "duplicate_of": "on a non-listed item: the package_id"
                                   " of the listed twin; the human pages"
                                   " show that one entry, marked"
                                   " corroborated — filter these out to"
                                   " match the human listing",
                   "counts": "whole-day observation counts by"
                             " collection/doc_type, backfill included",
                   "day_context": "null on federal business days; on"
                                  " weekends/federal holidays an object"
                                  " {kind, name, note} explaining why"
                                  " the stream may be short"},
        "counts": status["counts"],
        # Same computed value the human banner renders (fedcal): an agent
        # reading a one-item Sunday has exactly the same "is the pipeline
        # broken?" ambiguity the banner resolves. null on business days.
        "day_context": day_context,
        "backfill_count": len(status.get("backfill") or []),
        "corroborated_count": len(status.get("duplicates") or []),
        "backfill_note": ("items observed today that their publisher dates"
                          " earlier; the human page excludes them from the"
                          " day's listing under the GUIDE §3 dating rule."
                          " THIS FILE'S items[] includes them, flagged"
                          " is_backfill=true, because an agent may"
                          " legitimately want the full observation record;"
                          " they are reported in the dated digest's"
                          " coverage accounting, never as the day's news"),
        "facets": {"tags": facets,
                   "note": "filter items client-side on items[].tags;"
                           " the human page offers the same keywords as"
                           " toggles"},
        "pending_llm": status["pending_llm"],
        "last_observed_at": status["last_observed_at"],
        "items": json_items,
    }
    if not live:
        # Mirrors today.json's shape and labels exactly; the frozen flag
        # (and, for journal-backfilled renders, the reconstruction date)
        # is additive, so an agent's today.json reader works unchanged.
        payload["frozen"] = True
        if reconstructed_on:
            payload["reconstructed_on"] = reconstructed_on
    json_path.write_text(_json.dumps(payload, indent=1, sort_keys=True) + "\n",
                         encoding="utf-8")
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
  Federal Register actions, enacted laws, federal court opinions,
  agency announcements, recorded roll-call votes, and bill actions,
  with a table of contents, plain-language quick-reads, and a mandatory
  Coverage Statement accounting for everything published that day.
- **Machine index:** `/digests.json` — every available digest with date,
  URL, and teaser. Poll this (or the Atom feed at `/feed.xml`) for new
  days; both are small.
- **Source guide:** `/sources.html` — every federal source this pipeline
  ingests, plans to ingest, or found unavailable, with method and status,
  plus what we actually received from each: items ingested over a trailing
  window, their average and median length, the delivery mode, and how the
  source's server answered our requests.
- **Source statistics:** `/sources.json` — the same facts, machine-readable,
  with the classification thresholds included so any health label can be
  recomputed from the numbers beside it. Read these as **a description of
  our ingestion**, not as a measurement of an agency: a 4xx or 5xx is a
  server declining to return content, and why it declined is not visible
  to us. This file is not part of the official record and must never be
  cited as government publication.
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
  party-blind rule that selected it, and a citation to its official
  record — the govinfo package for the govinfo collections; the
  agency's, chamber's, or Congress.gov's own page for agency releases,
  recorded votes, bill actions, and presidential actions. **For claims, cite the official
  source we link; cite this site for the aggregation.**
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


def _sources_json(entries, health, base=""):
    """The machine twin of sources.html: the registry plus the same
    mechanical statistics and the same health labels, with the thresholds
    that produced them included so an agent can recompute any label from
    the numbers in the same document.

    Deliberately its own file rather than a section of digests.json: that
    surface and the Atom feed enumerate the OFFICIAL RECORD, and an agent
    polling them must never receive our operational statistics as though
    they were something the government published."""
    records = (health or {}).get("sources") or {}
    listed = []
    for entry in entries:
        record = dict(records.get(entry["id"], {"id": entry["id"],
                                                "name": entry["name"]}))
        record["description"] = entry["description"]
        record["method"] = _redact_addresses(entry["method"])
        record["notes"] = _redact_addresses(entry["notes"])
        record["urls"] = dict(entry["urls"])
        record["added"] = entry["added"]
        record["card"] = (f"{base}/sources.html#src-{entry['id']}" if base
                          else f"sources.html#src-{entry['id']}")
        record["page"] = (f"{base}/sources/{entry['id']}.html" if base
                          else f"sources/{entry['id']}.html")
        listed.append(record)
    payload = {
        "title": f"{SITE_TITLE} — source directory and ingestion statistics",
        "generated": utc_now_iso(),
        "canonical": "sources/registry.yaml",
        "human_page": f"{base}/sources.html" if base else "sources.html",
        "available": bool(health and health.get("available")),
        "scope": (
            "Statistics describe THIS PROJECT'S INGESTION of each source — "
            "items we recorded and requests we made. They are not a "
            "measurement of any agency, department, or publisher, and no "
            "health label is a judgement about one. An HTTP 4xx or 5xx is "
            "a server declining to return content; the reason is not "
            "visible to us and is not inferred."),
        "measurement": (
            "Health is computed for sources whose registry status is "
            "'active'; every other entry carries measured: false. Item "
            "counts are dated by publication day in Washington, D.C.; "
            "request counts are stamped UTC and include retries. Requests "
            "are attributed by host, so sources sharing a host report the "
            "same request figures (see fetch.shared_with_sources)."),
        "sources": listed,
    }
    if health:
        payload.update({
            "window": {"days": health["window_days"],
                       "start": health["window_start"],
                       "end": health["window_end"]},
            "thresholds": health["thresholds"],
            "health_labels": health["label_definitions"],
            "summary": health["summary"],
        })
        if not health.get("available"):
            payload["unavailable_reason"] = health.get("unavailable_reason")
    return payload


def _build_agent_surfaces(out_dir, dates, teasers, doc_pages=(), base="",
                          blog_posts=(), entries=(), health=None):
    """llms.txt, digests.json, sources.json, feed.xml, robots.txt,
    sitemap.xml, agents.html.

    Blog posts reach the discovery surfaces (llms.txt, sitemap.xml) and
    stay out of the record surfaces (digests.json, feed.xml) on purpose:
    those two enumerate official-record digests, and an agent polling them
    must never receive project commentary as though it were one. The same
    rule keeps sources.json separate: it is what we ingested and how, not
    what the government published."""
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
         " READ THE FLAGS: items[] includes entries the human page"
         " excludes — filter on is_backfill=false for the day's own news"
         " (backfill_count states how many are excluded), and check"
         " day_context (null on federal business days; a weekend/holiday"
         " object explains a quiet stream). Items may change until the"
         " end-of-day gates freeze the dated digest)"),
        f"- [Source guide — what we ingest and why]({base}/sources.html)",
    ] + ([
        (f"- Per-source pages: {base}/sources/<source-id>.html — one page"
         " per registry entry (active, planned, and unavailable alike):"
         " identity, ingestion method and politeness posture, measured"
         " statistics at 24-hour / 14-day / all-time windows with"
         " day-by-day charts, health label history, and — where stored —"
         " model-written orientation and assessment blocks, labeled as"
         " such. Source ids are listed in /sources.json."),
    ] if entries else []) + [
        (f"- Frozen day views: {base}/day/YYYY-MM-DD.html and"
         f" {base}/day/YYYY-MM-DD.json — the complete observed listing"
         " for a finished publication day, mechanical rules applied,"
         " frozen at end of day (or reconstructed from the stored"
         " observation journal, disclosed in place). The dated digest at"
         " /<YYYY-MM-DD>.html remains the canonical record; days before"
         " the observation journal began have no day view, and the JSON"
         " mirrors today.json's shape and labels."),
    ] + ([
        (f"- [Source health and statistics, machine-readable]({base}/sources.json)"
         " (per source: items ingested over a trailing window and their"
         " per-day rate, average/median content length, delivery mode,"
         " our request outcomes by HTTP status class, and a health label"
         " with the thresholds that produced it, so any label can be"
         " recomputed from the numbers in the same file. These describe"
         " OUR INGESTION — items we recorded and requests we made — and"
         " are not a measurement of any agency or publisher. Not part of"
         " the official record; do not cite as government publication.)"),
    ] if entries else []) + ([
        (f"- [Blog — notes on how this project is built]({base}/blog.html)"
         " (commentary ABOUT the project: not digest content, not part of"
         " the official record, and not government publication. Cite it as"
         " commentary, never as a source for what the government did.)"),
    ] if blog_posts else []) + [
        f"- [{title}]({base}/{stem}.html)" for stem, title in doc_pages
    ] + [
        f"- [Access guide for agents]({base}/agents.html)",
        "",
        "## Notes",
        "- Digest URLs are stable: /<YYYY-MM-DD>.html",
        "- Official text vs model-generated text is labeled in place;",
        "  every item cites its official record (govinfo for the govinfo",
        "  collections; the publisher's own page for agency releases,",
        "  recorded votes, bill actions, and presidential actions).",
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

    # sources.json — the source directory and our ingestion statistics.
    # Written only when a registry exists, matching sources.html: the nav
    # and llms.txt must never point at a file that was not built.
    if entries:
        (out_dir / "sources.json").write_text(
            _json.dumps(_sources_json(entries, health, base), indent=1,
                        sort_keys=True) + "\n", encoding="utf-8")

    # feed.xml (Atom)
    feed_entries = []
    for d in reversed(dates[-20:]):
        feed_entries.append(
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
        + "".join(feed_entries) + "</feed>\n"
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
        "#   Source stats:  /sources.json  (our ingestion, not the record)\n"
        "# /today.html is a PRELIMINARY live view; the dated digests are\n"
        "# the record.\n"
        f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n",
        encoding="utf-8",
    )
    # Day views are enumerated from what actually exists on disk — the
    # EOD wiring (and the one-shot journal backfill) writes them, so the
    # site build cannot know the set any other way, and a link is never
    # emitted for a page that was not built.
    day_pages = sorted(
        f"day/{p.stem}.html" for p in (out_dir / "day").glob("*.html")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem)
    ) if (out_dir / "day").is_dir() else []
    urls = (
        ["index.html", "today.html", "sources.html", "agents.html"]
        + [f"{stem}.html" for stem, _title in doc_pages]
        + [f"sources/{e['id']}.html" for e in entries]
        + (["blog.html"] if blog_posts else [])
        + [f"blog-{slug}.html" for slug, _date, _title in blog_posts]
        + [f"{d}.html" for d in dates]
        + day_pages
    )
    sitemap = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{base}/{u}</loc></url>" for u in urls)
        + "</urlset>\n"
    )
    (out_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")

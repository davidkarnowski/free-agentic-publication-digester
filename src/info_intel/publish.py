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

from . import config
from .sync import utc_now_iso

SITE_TITLE = "Information Intelligence — Daily Federal Digest"
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
    <a class="brand" href="index.html">Information&nbsp;Intelligence</a>
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
.nav-links a {
  color: var(--muted);
  text-decoration: none;
  margin-left: 0.9rem;
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
"""

_DATE_MD_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
_TEASER_RE = re.compile(r"^## Day in Review\s*$", re.MULTILINE)


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


def _render_page(title, body_html, nav_links, canonical):
    return _PAGE.format(
        title=html.escape(title),
        nav_links=nav_links,
        body=body_html,
        generated=utc_now_iso(),
        canonical=html.escape(canonical),
    )


def _nav_for(dates, i):
    links = []
    if i > 0:
        links.append(f'<a href="{dates[i - 1]}.html">&larr; {dates[i - 1]}</a>')
    if i < len(dates) - 1:
        links.append(f'<a href="{dates[i + 1]}.html">{dates[i + 1]} &rarr;</a>')
    links.append('<a href="index.html">All digests</a>')
    links.append('<a href="sources.html">Sources</a>')
    links.append('<a href="agents.html">For agents</a>')
    return "".join(links)


def _build_sources_page(out_dir):
    """Render the source guide (SOURCES.md, generated from the registry)
    into the site. Returns True if the page was built."""
    sources_md = config.PROJECT_ROOT / "SOURCES.md"
    if not sources_md.exists():
        return False
    _MD.reset()
    body = _MD.convert(sources_md.read_text(encoding="utf-8"))
    page = _render_page(
        f"Sources — {SITE_TITLE}",
        body,
        '<a href="index.html">All digests</a>',
        "SOURCES.md (generated from sources/registry.yaml)",
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

    for i, path in enumerate(files):
        md_text = path.read_text(encoding="utf-8")
        teasers[path.stem] = _teaser(md_text)
        _MD.reset()
        body = _MD.convert(md_text)
        page = _render_page(
            f"Daily Digest {path.stem} — {SITE_TITLE}",
            body,
            _nav_for(dates, i),
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
    sources_built = _build_sources_page(out_dir)
    _build_agent_surfaces(out_dir, dates, teasers)
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
        '<a href="sources.html">Sources</a>' if sources_built else "",
        "digests/",
    )
    (out_dir / "index.html").write_text(index, encoding="utf-8")

    (out_dir / "style.css").write_text(_STYLE, encoding="utf-8")
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")

    return {"pages": len(files), "assets": assets_copied, "out_dir": out_dir}


# ---------------------------------------------------------------------------
# Agent-facing surfaces (GUIDE §1 dual audience)
# ---------------------------------------------------------------------------

_AGENTS_MD = """# Access for AI Agents

This site is built for two readerships: people, and AI agents researching
United States federal government actions. **You are welcome to ingest this
data.** It exists so an agent can answer "what did the federal government
do on date D" from one clean, summarized, citation-bound source instead of
crawling many official sites.

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
"""


def _atom_escape(text):
    return html.escape(text or "", quote=True)


def _build_agent_surfaces(out_dir, dates, teasers, base=""):
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
        "- [Latest digest](/" + (f"{newest}.html" if newest else "index.html") + ")",
        "- [All digests (index)](/index.html)",
        "- [Machine-readable digest index](/digests.json)",
        "- [Atom feed of digests](/feed.xml)",
        "- [Source guide — what we ingest and why](/sources.html)",
        "- [Access guide for agents](/agents.html)",
        "",
        "## Notes",
        "- Digest URLs are stable: /<YYYY-MM-DD>.html",
        "- Official text vs model-generated text is labeled in place;",
        "  every item cites the official govinfo record.",
        "- Canonical Markdown + provenance manifests live in the repository.",
    ]
    (out_dir / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # digests.json
    (out_dir / "digests.json").write_text(_json.dumps({
        "title": SITE_TITLE,
        "generated": utc_now_iso(),
        "agent_guide": "agents.html",
        "digests": [
            {"date": d, "html": f"{d}.html", "canonical_markdown": f"digests/{d}.md",
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
            f"<id>tag:info-intel,{d}:digest</id>"
            f"<updated>{d}T12:00:00Z</updated>"
            f"<summary>{_atom_escape(teasers.get(d))}</summary></entry>"
        )
    feed = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">'
        f"<title>{_atom_escape(SITE_TITLE)}</title>"
        f'<link href="{base}/"/>'
        f"<id>tag:info-intel:digests</id>"
        f"<updated>{utc_now_iso()}</updated>"
        + "".join(entries) + "</feed>\n"
    )
    (out_dir / "feed.xml").write_text(feed, encoding="utf-8")

    # robots.txt + sitemap.xml — automated access is explicitly welcome.
    (out_dir / "robots.txt").write_text(
        "# AI agents and crawlers are welcome here — see /agents.html\n"
        "User-agent: *\nAllow: /\n\nSitemap: /sitemap.xml\n",
        encoding="utf-8",
    )
    urls = ["index.html", "sources.html", "agents.html"] + [f"{d}.html" for d in dates]
    sitemap = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{base}/{u}</loc></url>" for u in urls)
        + "</urlset>\n"
    )
    (out_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")

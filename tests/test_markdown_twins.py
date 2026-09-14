"""Phase 2 of the agent-discovery plan (docs/ops/plan-2026-09-13-phase2-
markdown-twins.md): every eligible page has a Markdown twin, names it in
its head, and — for generated twins — says the same things as the HTML
from the same data. The coverage invariant here is the one Phase 3's
routing relies on: a negotiated request can never 404.
"""

import re

import pytest
from conftest import DATE
from test_publish import (  # noqa: F401
    CLEAN_FETCHES,
    DELIVERING_ITEMS,
    _seed_today,
    devnotes_root,
    digests,
    health_site,
    registry_root,
)

from fapd import config, publish
from fapd.publish import TWIN_ELIGIBLE_PATTERNS, markdown_twin_for

__all__ = ["TWIN_ELIGIBLE_PATTERNS"]   # Phase 3's routing test imports it

_TWIN_LINK = '<link rel="alternate" type="text/markdown" href="{href}">'
_BANNED_RES = [re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
               for term in config.BANNED_TERMS]


@pytest.fixture(autouse=True)
def _local_build(monkeypatch):
    """The local-build case (no SITE_BASE_URL): a developer's .env may set
    one, and the header block would then carry the absolute URL."""
    monkeypatch.setattr(config, "SITE_BASE_URL", "")


def _head(page):
    return page.split("</head>", 1)[0]


def _generated_twins(out):
    """Every twin the build generated (not copied from a Markdown source)."""
    names = ["index.md", "blog.md", "sources.md", "archive.md"]
    return ([out / n for n in names if (out / n).exists()]
            + list((out / "sources").glob("*.md"))
            + list((out / "archive").glob("*.md")))


# ------------------------------------------------------------- AD-9 -------


def test_digest_twins_are_byte_identical_to_the_canonical_markdown(digests, tmp_path):  # noqa: F811
    out = tmp_path / "site"
    publish.build_site(digests, out)
    for date in ("2026-07-01", "2026-07-02"):
        assert (out / f"{date}.md").read_bytes() == (digests / f"{date}.md").read_bytes()
        assert _TWIN_LINK.format(href=f"{date}.md") in _head(
            (out / f"{date}.html").read_text(encoding="utf-8"))


def test_doc_page_twins_carry_the_header_and_the_page_h1(digests, tmp_path):  # noqa: F811
    out = tmp_path / "site"
    publish.build_site(digests, out)
    docs = publish._doc_sources()
    assert docs
    for _md, stem, title, canonical in docs:
        twin = (out / f"{stem}.md").read_text(encoding="utf-8")
        assert twin.startswith(f"<!-- Markdown twin of /{stem}.html"), stem
        assert f"`{canonical}`" in twin
        assert publish.REPO_URL in twin
        assert title in twin, stem
        assert _TWIN_LINK.format(href=f"{stem}.md") in _head(
            (out / f"{stem}.html").read_text(encoding="utf-8"))


def test_agents_twin_is_the_agents_markdown(digests, tmp_path):  # noqa: F811
    out = tmp_path / "site"
    publish.build_site(digests, out)
    twin = (out / "agents.md").read_text(encoding="utf-8")
    assert twin.endswith(publish._agents_md(publish._mcp_manifest()))
    assert '<h2 id="mcp">MCP service</h2>' in twin


def test_blog_twins_carry_the_commentary_disclosure(digests, devnotes_root, tmp_path):  # noqa: F811
    out = tmp_path / "site"
    publish.build_site(digests, out)
    post = (out / "blog-launch.md").read_text(encoding="utf-8")
    assert publish._BLOG_POST_DISCLOSURE in post
    assert publish._BLOG_POST_DISCLOSURE in (out / "blog-launch.html").read_text(
        encoding="utf-8")
    assert "Published 2026-07-30" in post
    index = (out / "blog.md").read_text(encoding="utf-8")
    assert publish._BLOG_INDEX_DISCLOSURE in index
    assert "[" in index and "](blog-launch.md) — 2026-07-30" in index
    for name in ("blog.html", "blog-launch.html"):
        assert _TWIN_LINK.format(href=name[:-5] + ".md") in _head(
            (out / name).read_text(encoding="utf-8"))


def test_non_eligible_pages_name_no_twin(conn, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIGEST_DIR", tmp_path / "no-digests")
    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    publish.build_day(conn, DATE, out_dir=tmp_path)
    for rel in ("today.html", f"day/{DATE}.html"):
        assert 'type="text/markdown"' not in _head(
            (tmp_path / rel).read_text(encoding="utf-8")), rel
    assert not (tmp_path / "today.md").exists()
    assert not (tmp_path / "day" / f"{DATE}.md").exists()


# ------------------------------------------------------------ AD-10 -------


def test_eligibility_patterns_match_master_plan_8_2():
    assert markdown_twin_for("/") == "/index.md"
    assert markdown_twin_for("/index.html") == "/index.md"
    assert markdown_twin_for("/2026-07-01.html") == "/2026-07-01.md"
    assert markdown_twin_for("/blog-launch.html") == "/blog-launch.md"
    assert markdown_twin_for("/sources/govinfo-test.html") == "/sources/govinfo-test.md"
    assert markdown_twin_for("/archive/2025.html") == "/archive/2025.md"
    for path in ("/today.html", "/50x.html", "/day/2026-07-01.html",
                 "/style.css", "/digests.json", "/sources/", "/archive/x.html",
                 "/a b.html", "/today.md"):
        assert markdown_twin_for(path) is None, path
    assert len(TWIN_ELIGIBLE_PATTERNS) == 4


def test_every_eligible_page_has_a_twin(digests, registry_root, devnotes_root,  # noqa: F811
                                        tmp_path):
    """The coverage invariant Phase 3 relies on: `Accept: text/markdown`
    on any eligible path can be answered from disk."""
    (digests / "2025-12-30.md").write_text("# Daily Digest — 2025-12-30\n")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    pages = ["/" + p.relative_to(out).as_posix() for p in out.rglob("*.html")]
    eligible = [p for p in pages if markdown_twin_for(p)]
    assert any(p.startswith("/sources/") for p in eligible)
    assert any(p.startswith("/archive/") for p in eligible)
    assert "/blog.html" in eligible
    for page in eligible:
        twin = out / markdown_twin_for(page).lstrip("/")
        assert twin.is_file(), f"{page} has no twin"
        depth = page.count("/") - 1
        href = "../" * depth + markdown_twin_for(page).lstrip("/")
        assert _TWIN_LINK.format(href=href) in _head(
            (out / page.lstrip("/")).read_text(encoding="utf-8")), page


def test_index_twin_lists_the_same_recent_days(digests, tmp_path):  # noqa: F811
    out = tmp_path / "site"
    publish.build_site(digests, out)
    index_html = (out / "index.html").read_text(encoding="utf-8")
    index_md = (out / "index.md").read_text(encoding="utf-8")
    html_dates = re.findall(r'<a class="date" href="(\d{4}-\d{2}-\d{2})\.html">',
                            index_html)
    md_dates = re.findall(r"^- \[Daily Digest — (\d{4}-\d{2}-\d{2})\]\(\1\.md\)",
                          index_md, re.MULTILINE)
    assert html_dates and md_dates == html_dates
    assert publish._LIVE_CALLOUT_TEXT in index_html
    assert publish._LIVE_CALLOUT_TEXT in index_md
    assert "(archive.md)" in index_md
    # the teaser the card shows is the teaser the twin shows
    assert "The House passed two measures" in index_md


def test_archive_twins_list_the_same_days_as_the_calendars(digests, tmp_path):  # noqa: F811
    (digests / "2025-12-30.md").write_text("# Daily Digest — 2025-12-30\n")
    (digests / "2025-11-03.md").write_text("# Daily Digest — 2025-11-03\n")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    year_html = (out / "archive" / "2025.html").read_text(encoding="utf-8")
    year_md = (out / "archive" / "2025.md").read_text(encoding="utf-8")
    html_days = set(re.findall(r'href="\.\./(\d{4}-\d{2}-\d{2})\.html"', year_html))
    md_days = set(re.findall(r"^- \[(\d{4}-\d{2}-\d{2})\]\(\.\./\1\.md\)", year_md,
                             re.MULTILINE))
    assert html_days == md_days == {"2025-12-30", "2025-11-03"}
    assert "## November 2025" in year_md and "## December 2025" in year_md
    assert "## October 2025" not in year_md      # only months with digests
    assert "- [2026](../archive.md)" in year_md
    root_md = (out / "archive.md").read_text(encoding="utf-8")
    assert "- [2026-07-01](2026-07-01.md)" in root_md
    assert "- [2025](archive/2025.md)" in root_md


def test_sources_twin_lists_the_same_ids_with_the_scope_disclosure(
        digests, registry_root, tmp_path):  # noqa: F811
    out = tmp_path / "site"
    publish.build_site(digests, out)
    listing = (out / "sources.html").read_text(encoding="utf-8")
    twin = (out / "sources.md").read_text(encoding="utf-8")
    html_ids = set(re.findall(r'id="src-([^"]+)"', listing))
    md_ids = set(re.findall(r"^- \*\*.+?\*\* \(`([^`]+)`\)", twin, re.MULTILINE))
    assert html_ids and md_ids == html_ids
    # The twin carries the scope disclosure whether or not statistics were
    # computed; the HTML says it inside its health section, which this
    # database-less build replaces with "not available" (see the
    # health_site test below for the two agreeing).
    assert publish._INGESTION_SCOPE_SENTENCE in twin
    assert "not available in this build" in twin
    assert "[page](sources/blocked-newsroom.md)" in twin
    assert "## Unavailable sources" in twin
    for entry_id in md_ids:
        assert (out / "sources" / f"{entry_id}.md").is_file()


def test_source_page_twin_states_the_same_figures(health_site):  # noqa: F811
    out = health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
    page = (out / "sources" / "example-newsroom.html").read_text(encoding="utf-8")
    twin = (out / "sources" / "example-newsroom.md").read_text(encoding="utf-8")
    assert twin.startswith("<!-- Markdown twin of /sources/example-newsroom.html")
    for text in ("Our requests to feeds.example.gov", "### Last 24 hours",
                 "### Last 14 days", "### All time", "all time (since",
                 "unmarked source-probe traffic", "| Items ingested |",
                 "## How we ingest it", "## Ingestion health"):
        assert text in twin, text
    # the same 14-day figures, from the same record
    items_html = re.search(r"Items ingested:</span> (\d+ in \d+ days)", page)
    assert items_html and f"| Items ingested | {items_html.group(1)}" in twin
    assert "[sources.md](../sources.md)" in twin
    assert _TWIN_LINK.format(href="../sources/example-newsroom.md") in _head(page)
    # with statistics computed, listing and twin state the scope sentence
    listing = (out / "sources.html").read_text(encoding="utf-8")
    assert "<strong>this project's ingestion of each source</strong>" in listing
    assert publish._INGESTION_SCOPE_SENTENCE in (out / "sources.md").read_text(
        encoding="utf-8")


def test_source_twin_labels_model_written_blocks(digests, registry_root, tmp_path):  # noqa: F811
    out = tmp_path / "site"
    data = publish._description_data({
        "summary": "A summary.", "description": "Para one.\n\nPara two.",
        "generated_at": "2026-08-03T10:00:00Z", "model": "test-model",
        "prompt_version": 1})
    md = publish._model_text_md(*data)
    assert md.startswith("**Model-written orientation**")
    assert "Para one." in md and "Para two." in md
    assert "_Model-written orientation, generated 2026-08-03 by test-model" in md
    assert "not official-record content" in md
    # the HTML block is built from the very same data object
    assert "Model-written orientation" in publish._model_text_block(*data)
    publish.build_site(digests, out)   # no stored blocks: no label appears
    assert "Model-written" not in (out / "sources" / "govinfo-test.md").read_text(
        encoding="utf-8")


def test_refresh_sources_regenerates_the_sources_twins(digests, registry_root,  # noqa: F811
                                                       tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    sentinel = "SENTINEL-STALE-TWIN"
    (out / "sources.md").write_text(sentinel, encoding="utf-8")
    (out / "sources" / "govinfo-test.md").write_text(sentinel, encoding="utf-8")
    result = publish.refresh_sources(out_dir=out)
    assert result["built"]
    assert sentinel not in (out / "sources.md").read_text(encoding="utf-8")
    assert sentinel not in (out / "sources" / "govinfo-test.md").read_text(
        encoding="utf-8")
    assert "# Sources" in (out / "sources.md").read_text(encoding="utf-8")


def test_twins_are_deterministic(digests, registry_root, tmp_path):  # noqa: F811
    (digests / "2025-12-30.md").write_text("# Daily Digest — 2025-12-30\n")
    first, second = tmp_path / "one", tmp_path / "two"
    publish.build_site(digests, first)
    publish.build_site(digests, second)
    twins = [p.relative_to(first) for p in first.rglob("*.md")]
    assert len(twins) > 10
    for rel in twins:
        assert (first / rel).read_bytes() == (second / rel).read_bytes(), rel
        assert "generated" not in (first / rel).read_text(encoding="utf-8")[:400]


def test_generated_twins_clear_the_banned_lexicon(digests, registry_root,  # noqa: F811
                                                  devnotes_root, tmp_path):  # noqa: F811
    (digests / "2025-12-30.md").write_text("# Daily Digest — 2025-12-30\n")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    generated = _generated_twins(out)
    assert len(generated) >= 5
    for path in generated:
        text = path.read_text(encoding="utf-8")
        for pattern in _BANNED_RES:
            assert not pattern.search(text), f"{pattern.pattern} in {path}"


def test_twin_header_uses_the_site_base_url(monkeypatch):
    monkeypatch.setattr(config, "SITE_BASE_URL", "https://example.test")
    header = publish._twin_header("sources/x", "sources/registry.yaml")
    assert header.startswith(
        "<!-- Markdown twin of https://example.test/sources/x.html ·")
    assert "> This is the Markdown form of https://example.test/sources/x.html." in header
    assert header.endswith("\n\n")
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    assert publish._twin_header("about", "docs/site/about.md").startswith(
        "<!-- Markdown twin of /about.html ·")


@pytest.mark.parametrize("path", ["/index.html", "/sources/a.html", "/archive/2025.html"])
def test_render_page_twin_link_is_relative_and_rebases(path):
    twin = markdown_twin_for(path).lstrip("/")
    page = publish._render_page("T", "<p>b</p>", "", "c", markdown_twin=twin)
    assert _TWIN_LINK.format(href=twin) in _head(page)
    if "/" in twin:
        assert _TWIN_LINK.format(href="../" + twin) in _head(publish._rebase_page(page))

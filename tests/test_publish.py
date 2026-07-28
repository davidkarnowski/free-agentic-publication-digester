"""Static-site builder tests: synthetic digests in tmp; no network."""

import pytest

from info_intel import publish

DIGEST_A = """# Daily Digest — 2026-07-01

| | |
|---|---|
| **Digest date** | 2026-07-01 |

---

## Day in Review

The House passed two measures by recorded vote; the Senate confirmed one
nomination. The Federal Register carried 40 documents.

---

## 1. Congressional Floor Activity

- **An Item** — A summary sentence.
  - *In plain terms:* a plain sentence.
  - Included because: CREC-SEL-01 — floor item
  - Source: [X / Y](https://www.govinfo.gov/app/details/X/Y)

![Graphic from 2026-1 (printed page 1)](assets/2026-07-01/g.png)
"""

DIGEST_B = """# Daily Digest — 2026-07-02

## Day in Review

Quiet day. Nothing else happened.
"""


@pytest.fixture
def digests(tmp_path):
    d = tmp_path / "digests"
    (d / "assets" / "2026-07-01").mkdir(parents=True)
    (d / "assets" / "2026-07-01" / "g.png").write_bytes(b"\x89PNG fake")
    (d / "2026-07-01.md").write_text(DIGEST_A)
    (d / "2026-07-02.md").write_text(DIGEST_B)
    (d / "TEMPLATE.md").write_text("# not a digest")
    return d


def test_builds_pages_index_and_assets(digests, tmp_path):
    out = tmp_path / "site"
    stats = publish.build_site(digests, out)
    assert stats["pages"] == 2
    assert stats["assets"] == 1
    assert stats["out_dir"] == out
    assert stats["doc_pages"] >= 2  # real docs/site: about.md + methods.md
    assert (out / "2026-07-01.html").exists()
    assert (out / "2026-07-02.html").exists()
    assert (out / "index.html").exists()
    assert not (out / "TEMPLATE.html").exists()
    assert (out / "assets" / "2026-07-01" / "g.png").read_bytes() == b"\x89PNG fake"
    assert (out / "style.css").exists()
    assert (out / ".nojekyll").exists()


def test_page_shell_and_markdown_conversion(digests, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "2026-07-01.html").read_text()
    assert '<meta name="viewport"' in page
    assert '<link rel="stylesheet" href="style.css">' in page
    assert "<table>" in page  # tables extension active
    assert '<img alt="Graphic from 2026-1 (printed page 1)" src="assets/2026-07-01/g.png"' in page
    assert "<em>In plain terms:</em>" in page
    assert "digests/2026-07-01.md" in page  # canonical-source footer


def test_prev_next_navigation(digests, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    first = (out / "2026-07-01.html").read_text()
    second = (out / "2026-07-02.html").read_text()
    assert '2026-07-02.html">2026-07-02' in first  # next
    assert '2026-07-01.html">&larr; 2026-07-01' in second  # prev
    assert 'href="index.html">All digests</a>' in first


def test_index_teasers_newest_first(digests, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    index = (out / "index.html").read_text()
    assert index.index("2026-07-02") < index.index("2026-07-01")  # newest first
    assert "Quiet day." in index  # first sentence only
    assert "Nothing else happened" not in index
    assert "The House passed two measures by recorded vote;" in index


def test_rebuild_is_idempotent(digests, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    first = (out / "2026-07-01.html").read_text()
    publish.build_site(digests, out)
    second = (out / "2026-07-01.html").read_text()
    # Only the generation timestamp may differ.
    strip = lambda t: "\n".join(x for x in t.splitlines() if "Generated" not in x)
    assert strip(first) == strip(second)


def test_real_digests_build(tmp_path):
    from info_intel import config

    if not any(config.DIGEST_DIR.glob("2026-*.md")):
        pytest.skip("no real digests on disk")
    stats = publish.build_site(config.DIGEST_DIR, tmp_path / "site")
    assert stats["pages"] >= 2
    assert stats["assets"] >= 7
    index = (tmp_path / "site" / "index.html").read_text()
    assert "Daily Digest — 2026-07-23" in index


def test_sources_page_built_and_linked(digests, tmp_path, monkeypatch):
    from info_intel import config

    root = tmp_path / "root"
    root.mkdir()
    (root / "SOURCES.md").write_text(
        "# Sources\n\n| Name | Status |\n|---|---|\n| GAO | planned |\n"
    )
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "sources.html").read_text()
    assert "<table>" in page and "GAO" in page
    index = (out / "index.html").read_text()
    assert 'href="sources.html"' in index
    digest_page = (out / "2026-07-01.html").read_text()
    assert 'href="sources.html">Sources</a>' in digest_page


def test_no_sources_md_degrades_gracefully(digests, tmp_path, monkeypatch):
    from info_intel import config

    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    monkeypatch.setattr(config, "PROJECT_ROOT", empty_root)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    assert not (out / "sources.html").exists()
    assert 'href="sources.html"' not in (out / "index.html").read_text()


def test_doc_pages_built_from_docs_site(digests, tmp_path, monkeypatch):
    """docs/site/*.md render generically: title from the first h1, canonical
    footer naming the markdown source."""
    from info_intel import config

    root = tmp_path / "root"
    (root / "docs" / "site").mkdir(parents=True)
    (root / "docs" / "site" / "about.md").write_text("# About this project\n\nBody A.\n")
    (root / "docs" / "site" / "zzz.md").write_text("no h1 here\n")
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    out = tmp_path / "site"
    stats = publish.build_site(digests, out)
    assert stats["doc_pages"] == 2
    about = (out / "about.html").read_text()
    assert "<title>About this project" in about  # title from first h1
    assert "Body A." in about
    assert "docs/site/about.md" in about  # canonical-source footer
    zzz = (out / "zzz.html").read_text()
    assert "<title>Zzz" in zzz  # stem fallback when no h1


def test_doc_nav_links_on_digest_pages_and_index(digests, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    for name in ("2026-07-01.html", "index.html"):
        page = (out / name).read_text()
        assert 'href="about.html">About</a>' in page
        assert 'href="methods.html">Methods</a>' in page


def test_llms_and_sitemap_include_doc_pages(digests, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    llms = (out / "llms.txt").read_text()
    assert "(/about.html)" in llms and "(/methods.html)" in llms
    sitemap = (out / "sitemap.xml").read_text()
    assert "/about.html" in sitemap and "/methods.html" in sitemap


def test_no_docs_site_degrades_gracefully(digests, tmp_path, monkeypatch):
    from info_intel import config

    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    monkeypatch.setattr(config, "PROJECT_ROOT", empty_root)
    out = tmp_path / "site"
    stats = publish.build_site(digests, out)
    assert stats["doc_pages"] == 0
    assert not (out / "about.html").exists()
    assert 'href="about.html"' not in (out / "2026-07-01.html").read_text()
    assert 'href="about.html"' not in (out / "index.html").read_text()
    assert "about.html" not in (out / "sitemap.xml").read_text()
    assert "about.html" not in (out / "llms.txt").read_text()


def test_about_and_methods_content(digests, tmp_path):
    """Spot-check the real explanatory pages for their load-bearing claims."""
    out = tmp_path / "site"
    publish.build_site(digests, out)
    about = (out / "about.html").read_text()
    assert "in order to be public" in about  # GUIDE §1 legitimacy framing
    assert "cite the underlying official" in about  # onward-citation ask
    methods = (out / "methods.html").read_text()
    assert "two-hash" in methods
    assert "Directed programmatic access" in methods  # access hierarchy
    assert "Basic web access" in methods
    assert "browser impersonation" in methods
    assert "Coverage Statement" in methods
    # section-wise structure for agent ingestion
    for h2 in ("Sourcing", "Ingestion", "Inference", "Publication"):
        assert f">{h2}<" in methods or f">{h2}</h2>" in methods


def test_agent_surfaces_built(digests, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    llms = (out / "llms.txt").read_text()
    assert "AI-agent" in llms and "/digests.json" in llms
    assert "2026-07-02.html" in llms  # latest digest linked

    import json as _json

    idx = _json.loads((out / "digests.json").read_text())
    assert [d["date"] for d in idx["digests"]] == ["2026-07-02", "2026-07-01"]
    assert idx["digests"][1]["canonical_markdown"] == "digests/2026-07-01.md"

    feed = (out / "feed.xml").read_text()
    assert "<feed" in feed and "Daily Digest — 2026-07-02" in feed

    robots = (out / "robots.txt").read_text()
    assert "Allow: /" in robots and "welcome" in robots
    assert "2026-07-01.html" in (out / "sitemap.xml").read_text()

    agents = (out / "agents.html").read_text()
    assert "welcome to ingest" in agents
    assert "Coverage Statement" in agents
    # navigation reaches the agents page from digest pages
    assert 'href="agents.html">For agents</a>' in (out / "2026-07-01.html").read_text()

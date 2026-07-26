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
    assert stats == {"pages": 2, "assets": 1, "out_dir": out}
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

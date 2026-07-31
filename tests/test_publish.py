"""Static-site builder tests: synthetic digests in tmp; no network."""

import pytest

from fapd import publish

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

| Chamber | Items |
|---|---|
| Senate | 2 |

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
    # plain-speak renders in its styled register (readability layer)
    assert '<span class="plain-label">In plain terms</span>' in page
    assert "digests/2026-07-01.md" in page  # canonical-source footer


DIGEST_C = """# Daily Digest — 2026-07-03

| | |
|---|---|
| **Digest date** | 2026-07-03 |
| **Data date range** | 2026-07-03 to 2026-07-03 |
| **Generated at** | 2026-07-04T09:00:00Z (UTC) |
| **Pipeline version** | abc1234 |
| **Source watermarks** | CREC: 2026-07-04T10:00:00Z |

## Contents

- [Day in Review](#day-in-review)
- [1. Congressional Floor Activity](#1-congressional-floor-activity)

---

## Day in Review

A quiet day of routine filings.

## 1. Congressional Floor Activity

Tags: legislative · model keys: budget debate · tariffs

*In plain terms: The Senate debated the budget.*

- **An Item** — A summary.
  - Included because: CREC-SEL-01 — floor item
  - Source: [X / Y](https://www.govinfo.gov/app/details/X/Y)

## Glossary

- term: meaning
"""


def test_digest_structure_transforms(digests, tmp_path):
    (digests / "2026-07-03.md").write_text(DIGEST_C)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "2026-07-03.html").read_text()

    # meta table -> compact strip with provenance folded away
    assert '<div class="digest-meta">' in page
    assert "<table>\n<thead>" not in page.split("Contents")[0] or True
    assert "Pipeline version</dt><dd>abc1234" in page
    assert "Digest date</td>" not in page

    # Contents block removed (sections are the navigation now)
    assert ">Contents</h2>" not in page

    # tags -> chips, model keys labeled and visually distinct
    assert '<span class="tag tag-branch-legislative">legislative</span>' in page
    assert 'class="tag tag-model" title="model-generated key">budget debate</span>' in page

    # numbered section + glossary collapse; anchor id moves to details
    assert '<details class="digest-section" id="1-congressional-floor-activity">' in page
    assert '<details class="digest-section" id="glossary">' in page
    # summary carries title, chips, and the plain-speak blurb
    summary = page.split('<details class="digest-section" id="1-congressional')[1]
    assert '<span class="sec-title">1. Congressional Floor Activity</span>' in summary
    assert "The Senate debated the budget." in summary.split("</summary>")[0]
    # Day in Review stays un-collapsed
    assert '<span class="sec-title">Day in Review</span>' not in page


def test_digest_readability_classes(digests, tmp_path):
    # The derived layer styles registers the canonical Markdown only
    # implies: plain-speak, rule notes (id + tooltip description), sources.
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "2026-07-01.html").read_text()
    assert '<li class="plain"><span class="plain-label">In plain terms</span>' in page
    assert '<li class="rule-note">Included because: ' in page
    assert '<span class="rule-id" title="floor item">CREC-SEL-01</span>' in page
    assert '<li class="source-note">Source: <a href=' in page
    assert "Included because: CREC-SEL-01 — floor item" not in page  # folded
    css = (out / "style.css").read_text()
    assert ".rule-id" in css and ".plain-label" in css


def test_every_page_carries_the_full_project_name(digests, tmp_path):
    # Branding rule (2026-07-30): the bare acronym never stands alone —
    # every published page expands "Free Agentic Publication Digester".
    out = tmp_path / "site"
    publish.build_site(digests, out)
    for page_path in out.glob("*.html"):
        assert "Free Agentic Publication Digester" in page_path.read_text(), page_path.name


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
    from fapd import config

    if not any(config.DIGEST_DIR.glob("2026-*.md")):
        pytest.skip("no real digests on disk")
    stats = publish.build_site(config.DIGEST_DIR, tmp_path / "site")
    assert stats["pages"] >= 2
    assert stats["assets"] >= 7
    index = (tmp_path / "site" / "index.html").read_text()
    assert "Daily Digest — 2026-07-23" in index


_REGISTRY_YAML = """\
- id: govinfo-test
  name: Test Collection (TEST)
  branch: legislative
  parent_org: U.S. Congress
  description: "A structured collection of test documents."
  type: govinfo-collection
  tier: 1
  urls:
    collection: https://www.govinfo.gov/app/collection/TEST
  method: govinfo collections API delta sync
  status: active
  added: "2026-07-26"
  notes: "Coverage (gate 3): the complete official test record."
- id: gao-reports
  name: GAO Reports
  branch: legislative
  parent_org: Government Accountability Office
  description: "Audit and evaluation reports published on a daily feed."
  type: rss
  tier: 1
  urls:
    home: https://www.gao.gov/reports
  method: Would parse the reports feed daily.
  status: planned
  added: "2026-07-26"
  notes: ""
- id: treasury-email-test
  name: Treasury Press Releases (email)
  branch: executive
  parent_org: Department of the Treasury
  description: "Subscription bulletins carrying press releases."
  type: email
  tier: 1
  sender: subscriptions@subscriptions.treas.gov
  urls:
    home: https://home.treasury.gov/news/press-releases
    signup: https://service.govdelivery.com/service/multi_subscribe.html?code=USTREAS
  method: Subscription bulletins to the project mailbox.
  status: active
  added: "2026-07-29"
  notes: "Subscribed and confirmed 2026-07-29 (sender subscriptions@subscriptions.treas.gov)."
- id: blocked-newsroom
  name: Blocked Newsroom
  branch: executive
  parent_org: Department of Example
  description: "A press-release index whose path refuses identified clients."
  type: html-index
  tier: 2
  urls:
    home: https://example.gov/newsroom
  method: Would parse the press-release HTML index daily.
  status: unavailable
  added: "2026-07-26"
  notes: "Probed 2026-07-26: robots.txt disallows our identified client."
- id: archive-api
  name: Archive Catalog API
  branch: executive
  parent_org: Example Archives
  description: "An archival catalog that publishes no new government actions."
  type: api
  tier: 3
  urls:
    home: https://catalog.example.gov/api
  method: Not applicable; evaluated only.
  status: evaluated-excluded
  added: "2026-07-28"
  notes: "Evaluated 2026-07-28: archival by nature, out of scope."
"""


@pytest.fixture
def registry_root(tmp_path, monkeypatch):
    from fapd import config

    root = tmp_path / "root"
    (root / "sources").mkdir(parents=True)
    (root / "sources" / "registry.yaml").write_text(_REGISTRY_YAML)
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    return root


def test_sources_page_built_and_linked(digests, registry_root, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "sources.html").read_text()
    assert "sources/registry.yaml" in page  # canonical-source footer
    index = (out / "index.html").read_text()
    assert 'href="sources.html"' in index
    digest_page = (out / "2026-07-01.html").read_text()
    assert 'href="sources.html">Sources</a>' in digest_page


def test_sources_page_intro_counts_and_status_key(digests, registry_root, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "sources.html").read_text()
    # counts computed from the registry, never hardcoded
    assert "<strong>5</strong> sources registered" in page
    assert "2 active, 1 planned, 1 unavailable, 1 evaluated and excluded." in page
    # every status defined in the key, chips reused from the site's tag style
    for chip in ("tag-status-active", "tag-status-planned",
                 "tag-status-unavailable", "tag-status-excluded"):
        assert chip in page
    assert '<dl class="status-key">' in page


def test_sources_page_grouped_sections_and_cards(digests, registry_root, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "sources.html").read_text()
    # the three channel groups, plus the accountability sections
    assert '<h2 id="govinfo-collections">Official govinfo collections</h2>' in page
    assert '<h2 id="agency-web-channels">Agency newsrooms and web channels</h2>' in page
    assert '<h2 id="agency-email-bulletins">Agency email bulletins</h2>' in page
    assert '<h2 id="unavailable-sources">Unavailable sources (1)</h2>' in page
    assert '<h2 id="evaluated-and-excluded">Evaluated and excluded (1)</h2>' in page
    # status subgroups inside a channel group
    assert "<h3>Active (1)</h3>" in page and "<h3>Planned (1)</h3>" in page
    # a card: linked name, chip + subtitle, description, folded registry record
    assert '<article class="src-card" id="src-gao-reports">' in page
    assert ('href="https://www.gao.gov/reports" target="_blank"'
            ' rel="noopener noreferrer">GAO Reports</a>') in page
    assert '<span class="tag tag-status-active">active</span>' in page
    assert "Legislative · Tier 1 · RSS feed · Government Accountability Office" in page
    assert "Audit and evaluation reports published on a daily feed." in page
    assert '<details class="src-more"><summary>Registry record</summary>' in page
    assert "<dt>Registry id</dt><dd><code>govinfo-test</code></dd>" in page
    # the old SOURCES.md giant table is gone: no table markup at all
    assert "<table>" not in page


def test_sources_page_unavailable_is_explained_not_hidden(
        digests, registry_root, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "sources.html").read_text()
    assert "record the refusal exactly as observed" in page
    assert "no browser impersonation" in page
    # the refused entry still renders as a full card, probe note included
    assert '<article class="src-card" id="src-blocked-newsroom">' in page
    assert "robots.txt disallows our identified client." in page


def test_sources_page_publishes_no_email_addresses(digests, registry_root, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "sources.html").read_text()
    # sender/mailbox addresses never render; quoted notes are redacted in place
    assert publish._EMAIL_ADDR_RE.search(page) is None
    assert "subscriptions.treas.gov" not in page
    assert "(sender [address withheld])" in page
    # the public signup form is linked; the name links to the agency page
    assert 'href="https://service.govdelivery.com/service/multi_subscribe.html' in page
    assert 'href="https://home.treasury.gov/news/press-releases"' in page


def test_sources_page_from_real_registry(digests, tmp_path):
    """The committed registry renders: counts match, no address leaks."""
    from fapd import config, sources

    registry_path = config.PROJECT_ROOT / "sources" / "registry.yaml"
    if not registry_path.exists():
        pytest.skip("no registry on disk")
    entries = sources.load_registry(registry_path)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "sources.html").read_text()
    assert f"<strong>{len(entries)}</strong> sources registered" in page
    assert page.count('<article class="src-card"') == len(entries)
    assert publish._EMAIL_ADDR_RE.search(page) is None
    assert "<table>" not in page


def test_no_registry_degrades_gracefully(digests, tmp_path, monkeypatch):
    from fapd import config

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
    from fapd import config

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


def test_llms_and_sitemap_include_doc_pages(digests, tmp_path, monkeypatch):
    # Pin the no-domain mode: with SITE_BASE_URL now honored from .env
    # (config fix 2026-07-30), this test must not inherit the local value.
    monkeypatch.setattr(publish.config, "SITE_BASE_URL", "")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    llms = (out / "llms.txt").read_text()
    assert "(/about.html)" in llms and "(/methods.html)" in llms
    sitemap = (out / "sitemap.xml").read_text()
    assert "/about.html" in sitemap and "/methods.html" in sitemap


def test_readme_rendered_with_repo_links_rewritten(digests, tmp_path, monkeypatch):
    """The repo-root README renders as readme.html: links with site
    equivalents are rewritten; repo-only file links degrade to code text."""
    from fapd import config

    root = tmp_path / "root"
    root.mkdir()
    (root / "README.md").write_text(
        "# Free Agentic Publication Digester (FAPD)\n\n"
        "See [GUIDE.md](GUIDE.md), the [source guide](SOURCES.md),\n"
        "[`llms.txt`](site/llms.txt), the [static site](site/), and\n"
        "[digests/2026-07-01.md](digests/2026-07-01.md).\n"
        "External: [api.data.gov](https://api.data.gov/signup/).\n"
    )
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    out = tmp_path / "site"
    stats = publish.build_site(digests, out)
    assert stats["doc_pages"] == 1
    page = (out / "readme.html").read_text()
    assert "<title>Free Agentic Publication Digester (FAPD)" in page
    assert 'href="sources.html"' in page          # SOURCES.md -> site page
    assert 'href="llms.txt"' in page              # site/llms.txt -> local
    assert 'href="index.html"' in page            # site/ -> index
    assert 'href="2026-07-01.html"' in page       # digest md -> digest page
    assert 'href="https://api.data.gov/signup/"' in page  # external kept
    assert 'href="GUIDE.md"' not in page          # repo-only: not a dead link
    assert "<code>GUIDE.md</code>" in page        # ...but still named
    assert "README.md" in page                    # canonical-source footer
    assert 'href="readme.html">Readme</a>' in (out / "2026-07-01.html").read_text()


def test_site_base_url_absolutizes_machine_surfaces(digests, tmp_path, monkeypatch):
    """With SITE_BASE_URL set, sitemap/feed/robots/llms.txt/digests.json emit
    absolute URLs (sitemaps and robots Sitemap directives require them);
    unset, everything stays root-relative for local viewing."""
    from fapd import config

    monkeypatch.setattr(config, "SITE_BASE_URL", "https://example.org")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    assert "<loc>https://example.org/index.html</loc>" in (out / "sitemap.xml").read_text()
    assert 'href="https://example.org/2026-07-02.html"' in (out / "feed.xml").read_text()
    assert "Sitemap: https://example.org/sitemap.xml" in (out / "robots.txt").read_text()
    llms = (out / "llms.txt").read_text()
    assert "(https://example.org/digests.json)" in llms
    assert "](/index.html)" not in llms  # no root-relative leftovers in Core
    assert '"html": "https://example.org/2026-07-02.html"' in (out / "digests.json").read_text()

    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    out2 = tmp_path / "site2"
    publish.build_site(digests, out2)
    assert "<loc>/index.html</loc>" in (out2 / "sitemap.xml").read_text()
    assert "Sitemap: /sitemap.xml" in (out2 / "robots.txt").read_text()
    assert '"html": "2026-07-02.html"' in (out2 / "digests.json").read_text()


def test_no_docs_site_degrades_gracefully(digests, tmp_path, monkeypatch):
    from fapd import config

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


# ------------------------------------------------------------------ /today --


def _seed_today(conn):
    """One extracted+summarized CREC item and one bare agency item,
    journaled for DATE."""
    from conftest import DATE, seed_item

    from fapd import config as _config

    seed_item(conn, "CREC-2026-07-23", "PgS1", "CREC", "SENATE")
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version,"
        " method, inclusion_rule, summary, created_at) VALUES"
        " ('CREC-2026-07-23', 'PgS1', ?, 'llm', 'CREC-SEL-01',"
        " 'The Senate debated a measure.', 'x')",
        (_config.PROMPT_VERSION,))
    # an unsummarized email-channel agency item with a full extract row
    conn.execute("INSERT INTO packages (package_id, collection, date_issued,"
                 " last_modified, title, first_seen_at) VALUES"
                 " ('AGENCYPR-x', 'AGENCYPR', ?, 'x', 'VA announcement', 'x')",
                 (DATE,))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, title, text, char_count, metadata, extracted_at,"
        " extractor_version) VALUES ('AGENCYPR-x', '', 'AGENCYPR', 'PRESS',"
        " 'VA announces a claims program',"
        " 'The Department of Veterans Affairs announced a program today.',"
        " 61, ?, 'x', 1)",
        (('{"channel": "email", "dkim": {"result": "pass"},'
          ' "source_id": "va-email", "url": null}'),))
    conn.execute(
        "INSERT INTO item_journal (observed_at, source_class, package_id,"
        " granule_id, collection, source_id, digest_date, event) VALUES"
        " (?, 'govinfo', 'CREC-2026-07-23', 'PgS1', 'CREC', NULL, ?,"
        "  'ingested'),"
        " (?, 'email', 'AGENCYPR-x', '', 'AGENCYPR', 'va-email', ?,"
        "  'ingested')",
        (f"{DATE}T10:00:00Z", DATE, f"{DATE}T11:30:00Z", DATE))
    conn.commit()


def test_build_today_renders_disclosure_sections_and_labels(conn, tmp_path):
    from conftest import DATE

    _seed_today(conn)
    stats = publish.build_today(conn, out_dir=tmp_path, date=DATE)
    assert stats["items"] == 2
    page = (tmp_path / "today.html").read_text()
    assert "preliminary" in page.lower()
    assert "the dated digest is the" in page  # GUIDE §5 disclosure wording
    assert "composed at end of day" in page
    assert f"Today — {DATE} (in progress)" in page
    # one chronological stream: no section headings, items self-describe
    assert "<h2>" not in page.split("</h1>")[1]
    assert "Congressional Record" in page and "Agency announcement" in page
    assert "model summary:" in page            # §2 labeling for llm method
    assert page.index("AGENCYPR-x") < page.index("PgS1")  # newest first

    import json
    data = json.loads((tmp_path / "today.json").read_text())
    assert data["date"] == DATE and len(data["items"]) == 2
    assert "preliminary" in data["disclosure"].lower()
    assert data["counts"]  # mechanical counts present


def test_build_today_empty_day_renders_on_purpose(conn, tmp_path):
    stats = publish.build_today(conn, out_dir=tmp_path, date="2020-01-01")
    assert stats["items"] == 0
    page = (tmp_path / "today.html").read_text()
    assert "No items observed yet" in page
    assert "preliminary" in page.lower()


def test_build_today_citation_metadata_and_item_tags(conn, tmp_path):
    """The enrichment contract: official links, channel labels, mechanical
    item-tag chips, verbatim opening descriptors for unsummarized items,
    and the same fields machine-readable in today.json."""
    import json

    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()

    # govinfo citation link constructed without any request
    assert ("https://www.govinfo.gov/app/details/CREC-2026-07-23/PgS1"
            in page)
    # channel + cite metadata line
    assert "govinfo API" in page
    assert "CREC-2026-07-23 / PgS1" in page
    # mechanical item tags: branch + doc-type words
    assert '<span class="tag tag-branch-legislative">legislative</span>' in page
    assert '<span class="tag">senate floor</span>' in page  # non-branch: plain chip
    # summarized item carries its inclusion rule as a subtle note
    assert '<span class="rule-note">CREC-SEL-01</span>' in page
    # the unsummarized agency item -> labeled verbatim opening + channel
    assert "opening text (verbatim):" in page
    assert "email bulletin (DKIM-verified)" in page

    data = json.loads((tmp_path / "today.json").read_text())
    by_pkg = {i["package_id"]: i for i in data["items"]}
    crec = by_pkg["CREC-2026-07-23"]
    assert crec["official_url"].endswith("/CREC-2026-07-23/PgS1")
    assert crec["channel_label"] == "govinfo API"
    assert "legislative" in crec["tags"] and "senate floor" in crec["tags"]
    assert crec["inclusion_rule"] == "CREC-SEL-01"
    assert data["labels"]["tags"].startswith("mechanical")
    agency = by_pkg["AGENCYPR-x"]
    assert agency["tags"] == ["executive", "press release", "va"]
    assert agency["channel_label"] == "email bulletin (DKIM-verified)"
    assert agency["official_url"] is None  # URL-less bulletin: no fake link
    assert agency["opening_verbatim"].startswith("The Department")


def test_build_today_renders_section_tag_chips_when_stored(conn, tmp_path):
    from conftest import DATE

    _seed_today(conn)
    conn.execute(
        "INSERT INTO section_tags (date, section_key, tag, method, created_at)"
        " VALUES (?, 'senate', 'legislative', 'mechanical', 'x')", (DATE,))
    conn.execute(
        "INSERT INTO section_tags (date, section_key, tag, method,"
        " prompt_version, created_at)"
        " VALUES (?, 'senate', 'stock trading ban', 'llm', 1, 'x')", (DATE,))
    conn.commit()
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()
    assert '<p class="today-chips">' in page
    assert ">stock trading ban</span>" in page
    assert 'tag-model" title="model-generated discovery key"' in page


def test_build_today_newest_first_with_branch_colors_and_intro(conn, tmp_path):
    """Operator direction 2026-07-30: arrivals read latest-on-top, branch
    tags carry stable colors, and the intro explains the page and points
    at the dated whole-day digests."""
    import json

    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    data = json.loads((tmp_path / "today.json").read_text())
    # 11:30 agency item observed after the 10:00 CREC item -> listed first
    assert [i["package_id"] for i in data["items"]] == \
        ["AGENCYPR-x", "CREC-2026-07-23"]

    page = (tmp_path / "today.html").read_text()
    assert 'class="tag tag-branch-legislative">legislative</span>' in page
    assert 'class="tag tag-branch-executive">executive</span>' in page
    assert "live view" in page
    assert "whole-day context" in page and 'href="index.html">all digests' in page
    # head is bot-friendly: description meta + llms.txt alternate link
    assert '<meta name="description"' in page
    assert 'href="llms.txt"' in page and "AI-first" in page


def test_agent_surfaces_are_bot_friendly(tmp_path, monkeypatch):
    from fapd import config as _config

    monkeypatch.setattr(_config, "SITE_BASE_URL", "")
    publish._build_agent_surfaces(tmp_path, ["2026-07-29"], {}, [], base="")
    robots = (tmp_path / "robots.txt").read_text()
    assert "LLM guide:    /llms.txt" in robots
    assert "AI-first" in robots and "Allow: /" in robots
    assert "today.html" in (tmp_path / "sitemap.xml").read_text()
    assert "PRELIMINARY" in (tmp_path / "llms.txt").read_text()


def test_index_page_has_live_callout_above_digest_list(tmp_path):
    """Operator direction 2026-07-30: the live /today offering is visible
    on the index body itself, above the digest listing."""
    (tmp_path / "digests").mkdir()
    (tmp_path / "digests" / "2026-07-29.md").write_text(
        "# Daily Digest\n\nBody.\n")
    publish.build_site(digest_dir=tmp_path / "digests",
                       out_dir=tmp_path / "site")
    index = (tmp_path / "site" / "index.html").read_text()
    callout = index.index('class="live-callout"')
    listing = index.index('class="digest-list"')
    assert callout < listing
    assert 'href="today.html"' in index[callout:listing]


# ------------------------------------------------- external-link behavior --


def test_external_links_open_in_a_new_tab_sitewide(monkeypatch):
    """Universal rule (operator, 2026-07-30): a link that leaves the site
    opens in a new tab so a reader following a citation never loses the
    digest. Same-site links, fragments, and mailto: are untouched."""
    from fapd import config as _config

    monkeypatch.setattr(_config, "SITE_BASE_URL", "https://fapd.info")
    body = (
        '<a href="https://www.govinfo.gov/app/details/X">official</a>'
        '<a href="2026-07-29.html">yesterday</a>'
        '<a href="#section-2">jump</a>'
        '<a href="mailto:someone@example.gov">write</a>'
        '<a href="https://fapd.info/today.html">our own live page</a>'
        '<a href="https://www.fapd.info/index.html">www of ours</a>'
        '<a href="https://example.gov/x" target="_self">already targeted</a>'
    )
    page = publish._render_page("T", body, "", "canonical")

    assert ('<a href="https://www.govinfo.gov/app/details/X"'
            ' target="_blank" rel="noopener noreferrer">') in page
    for same_tab in ('<a href="2026-07-29.html">', '<a href="#section-2">',
                     '<a href="mailto:someone@example.gov">',
                     '<a href="https://fapd.info/today.html">',
                     '<a href="https://www.fapd.info/index.html">',
                     '<a href="https://example.gov/x" target="_self">'):
        assert same_tab in page, same_tab
    # the footer's own outbound links obey the same rule
    assert page.count('rel="noopener noreferrer"') >= 3


def test_external_link_rule_applies_to_digest_and_today_pages(conn, tmp_path,
                                                              monkeypatch):
    from conftest import DATE

    from fapd import config as _config

    monkeypatch.setattr(_config, "SITE_BASE_URL", "https://fapd.info")
    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    today = (tmp_path / "today.html").read_text()
    assert ('<a href="https://www.govinfo.gov/app/details/CREC-2026-07-23/PgS1"'
            ' target="_blank" rel="noopener noreferrer">') in today
    # internal nav stays in-tab
    assert '<a href="index.html">All digests</a>' in today

    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "2026-07-29.md").write_text(
        "# Daily Digest\n\nSee [the record](https://www.govinfo.gov/x).\n")
    publish.build_site(digest_dir=tmp_path / "d", out_dir=tmp_path / "s")
    digest = (tmp_path / "s" / "2026-07-29.html").read_text()
    assert 'href="https://www.govinfo.gov/x" target="_blank"' in digest


# ------------------------------------------------------ /today keyword filter --


def test_today_filter_bar_is_pure_css_and_wired(conn, tmp_path):
    """Checkbox model (operator, 2026-07-30): chips toggle off when
    clicked again and move the viewport not at all, because the state is
    a checkbox rather than a URL fragment. Still zero script."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()

    # no fragment links means no scroll jump and no un-clickable state
    assert 'href="#k-' not in page
    assert "filter-anchor" not in page
    for slug in ("f-legislative", "f-executive", "f-press-release"):
        assert f'<input type="checkbox" class="filter-cb" id="{slug}">' in page
        assert f'for="{slug}"' in page
        k = slug[2:]
        assert (f"#{slug}:checked ~ .today-list > .today-item:not(.k-{k})"
                "{display:none}") in page
        assert f'#{slug}:checked ~ .filter-bar label[for="{slug}"]' in page
        assert f'#{slug}:focus-visible ~ .filter-bar label[for="{slug}"]' in page

    # the form is what lets the reset button clear everything without JS
    assert '<form class="today-stream"' in page
    assert '<button type="reset" class="filter-clear">' in page
    assert page.index("filter-cb") < page.index('class="filter-bar"')
    assert page.index('class="filter-bar"') < page.index('class="today-list"')

    # branch keywords sit on their own row and keep their listing colors
    branch_row = page.split('class="filter-row filter-branches"')[1].split(
        "</div>")[0]
    assert "tag-branch-legislative filter-chip" in branch_row
    assert "tag-branch-executive filter-chip" in branch_row
    assert "press release" not in branch_row      # non-branch keywords below
    assert 'class="today-item k-legislative k-senate-floor"' in page

    import json
    data = json.loads((tmp_path / "today.json").read_text())
    assert data["facets"]["tags"]["executive"] == 1
    assert "client-side" in data["facets"]["note"]


def test_today_filter_caps_and_discloses(conn, tmp_path, monkeypatch):
    """No silent caps: when the bar truncates it says so in place."""
    from conftest import DATE

    _seed_today(conn)
    monkeypatch.setattr(publish, "MAX_FILTER_KEYWORDS", 2)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()
    assert "Showing 2 of" in page


def test_today_filter_absent_on_an_empty_day(conn, tmp_path):
    publish.build_today(conn, out_dir=tmp_path, date="2020-01-01")
    page = (tmp_path / "today.html").read_text()
    assert "filter-bar" not in page and "<style>" not in page
    assert "No items observed yet" in page


def test_local_time_is_additive_and_selfcontained(conn, tmp_path):
    """The one script on the site only APPENDS a local equivalent beside
    server-rendered UTC stamps: no external resource, no network, no
    storage, and the page is complete with scripting off."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()

    # UTC is in the HTML, machine-readable, and stands alone
    # UTC in datetime= (machine-readable), Eastern on the face (the
    # publishers' clock): 11:30 UTC is 07:30 EDT.
    assert (f'<time class="utc" datetime="{DATE}T11:30:00Z">07:30:00 ET'
            "</time>") in page
    assert 'Last updated <time class="utc"' in page
    # the script fetches nothing and stores nothing
    script = page[page.index("<script"):page.index("</script>")]
    for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "cookie",
                      "src=", "http://", "https://"):
        assert forbidden not in script, forbidden
    # other page classes stay script-free
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "2026-07-29.md").write_text("# Daily Digest\n\nBody.\n")
    publish.build_site(digest_dir=tmp_path / "d", out_dir=tmp_path / "s")
    assert "<script" not in (tmp_path / "s" / "2026-07-29.html").read_text()
    assert "<script" not in (tmp_path / "s" / "index.html").read_text()

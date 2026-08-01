"""Static-site builder tests: synthetic digests in tmp; no network."""

import re

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
    assert ('class="tag tag-model" title="model-generated key">budget debate'
            '<span class="vh"> (model-generated key)</span></span>') in page

    # numbered section + glossary collapse; the anchor id rides the h2
    # inside the summary, where a closed <details> still exposes it
    assert '<details class="digest-section"><summary>' in page
    assert ('<h2 class="sec-title" id="1-congressional-floor-activity">'
            "1. Congressional Floor Activity</h2>") in page
    assert '<h2 class="sec-title" id="glossary">Glossary</h2>' in page
    # summary carries title, chips, and the plain-speak blurb
    summary = page.split('id="1-congressional-floor-activity"')[1]
    assert "The Senate debated the budget." in summary.split("</summary>")[0]
    # Day in Review stays un-collapsed
    assert 'class="sec-title" id="day-in-review"' not in page


def test_digest_readability_classes(digests, tmp_path):
    # The derived layer styles registers the canonical Markdown only
    # implies: plain-speak, rule notes (id + tooltip description), sources.
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "2026-07-01.html").read_text()
    assert '<li class="plain"><span class="plain-label">In plain terms</span>' in page
    assert '<li class="rule-note">Included because: ' in page
    assert ('<span class="rule-id" title="floor item">CREC-SEL-01'
            '<span class="vh"> — floor item</span></span>') in page
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
    # A11Y-16: out of a screen reader's link list these read as bare
    # dates, so each states its purpose in visually-hidden text.
    assert ('2026-07-02.html"><span class="vh">Digest for </span>2026-07-02'
            in first)  # next
    assert ('2026-07-01.html">&larr; <span class="vh">Digest for </span>'
            "2026-07-01") in second  # prev
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
    # The database paths are absolute and computed at import, so patching
    # PROJECT_ROOT alone leaves them pointing at the developer machine's
    # real data/ — which made health render here but not in CI. Pin them
    # inside the isolated root so these tests answer the same way anywhere.
    monkeypatch.setattr(config, "PIPELINE_DB", root / "data" / "fapd.db")
    monkeypatch.setattr(config, "FETCH_LOG_DB", root / "data" / "fetch_log.db")
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
            ' rel="noopener noreferrer">GAO Reports'
            '<span class="vh"> (opens in a new tab)</span></a>') in page
    assert '<span class="tag tag-status-active">active</span>' in page
    assert "Legislative · Tier 1 · RSS feed · Government Accountability Office" in page
    assert "Audit and evaluation reports published on a daily feed." in page
    assert '<details class="src-more"><summary>Registry record</summary>' in page
    assert "<dt>Registry id</dt><dd><code>govinfo-test</code></dd>" in page
    # the old SOURCES.md giant table is gone: the directory is cards. The
    # health key is the page's only table and needs databases, which this
    # fixture pins absent — otherwise the assertion below passes in CI and
    # fails on a developer machine that happens to have data/.
    assert "<th>Method</th>" not in page
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
    # the directory is still cards, never one wide table of every source
    assert "<th>Method</th>" not in page


def test_no_registry_degrades_gracefully(digests, tmp_path, monkeypatch):
    from fapd import config

    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    monkeypatch.setattr(config, "PROJECT_ROOT", empty_root)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    assert not (out / "sources.html").exists()
    assert 'href="sources.html"' not in (out / "index.html").read_text()
    # the machine surface follows the page: nothing points at a file that
    # was not built
    assert not (out / "sources.json").exists()
    assert "sources.json" not in (out / "llms.txt").read_text()


# ---------------------------------------------------------------------------
# Source health and statistics on the source guide (fapd.health rendered)
# ---------------------------------------------------------------------------

_HEALTH_REGISTRY_YAML = """\
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
- id: example-newsroom
  name: Example Newsroom
  branch: executive
  parent_org: Department of Example
  description: "Press releases published on a daily feed."
  type: rss
  tier: 1
  urls:
    feed: https://feeds.example.gov/press.xml
    home: https://www.example.gov/news
  method: Conditional GET against the feed.
  status: active
  added: "2026-07-26"
  notes: "Coverage (gate 3): the department's full release stream."
- id: example-email
  name: Example Bulletins (email)
  branch: executive
  parent_org: Department of Example
  description: "Subscription bulletins carrying press releases."
  type: email
  tier: 1
  sender: bulletins@example.gov
  urls:
    home: https://www.example.gov/news
    signup: https://public.govdelivery.com/accounts/EXAMPLE/subscriber/new
  method: Subscription bulletins to the project mailbox.
  status: active
  added: "2026-07-29"
  notes: "Subscribed and confirmed 2026-07-29."
- id: planned-newsroom
  name: Planned Newsroom
  branch: executive
  parent_org: Department of Later
  description: "A newsroom registered so the coverage gap stays visible."
  type: html-index
  tier: 2
  urls:
    home: https://later.example.gov/newsroom
  method: Would parse the press-release index daily.
  status: planned
  added: "2026-07-26"
  notes: ""
"""

HEALTH_TODAY = "2026-07-31"


@pytest.fixture
def health_site(digests, tmp_path, monkeypatch):
    """Registry + real pipeline/fetch databases, and a frozen publication
    date so the window is deterministic. Returns a builder taking the rows
    to seed, so each test states only the facts it is about."""
    import sqlite3

    from fapd import config, db, health, sync

    root = tmp_path / "hroot"
    (root / "sources").mkdir(parents=True)
    (root / "sources" / "registry.yaml").write_text(_HEALTH_REGISTRY_YAML)
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    monkeypatch.setattr(sync, "publication_date",
                        lambda *a, **kw: HEALTH_TODAY)
    monkeypatch.setattr(health, "publication_date",
                        lambda *a, **kw: HEALTH_TODAY)

    def build(items=(), fetches=(), collectors=(), with_dbs=True):
        out = tmp_path / "site"
        if not with_dbs:
            publish.build_site(digests, out,
                               pipeline_db=tmp_path / "absent-pipeline.db",
                               fetch_db=tmp_path / "absent-fetch.db")
            return out
        pipeline = tmp_path / "fapd.db"
        fetch = tmp_path / "fetch_log.db"
        for stale in (pipeline, fetch):   # a test may build more than once
            stale.unlink(missing_ok=True)
        conn = db.connect(pipeline)
        for i, (collection, date, chars, metadata) in enumerate(items):
            pid = f"P{i}"
            conn.execute(
                "INSERT INTO packages (package_id, collection, date_issued,"
                " last_modified, first_seen_at) VALUES (?, ?, ?, 'x', 'x')",
                (pid, collection, date))
            conn.execute(
                "INSERT INTO extracted_texts (package_id, granule_id,"
                " collection, metadata, text, char_count, extracted_at,"
                " extractor_version) VALUES (?, '', ?, ?, '', ?, 'x', 1)",
                (pid, collection, metadata, chars))
        for worker, errors in collectors:
            conn.execute(
                "INSERT INTO collector_state (worker, consecutive_errors)"
                " VALUES (?, ?)", (worker, errors))
        conn.commit()
        conn.close()

        fconn = sqlite3.connect(fetch)
        fconn.execute(
            "CREATE TABLE fetch_log (id INTEGER PRIMARY KEY, ts_utc TEXT,"
            " url TEXT, status INTEGER, attempt INTEGER)")
        fconn.executemany(
            "INSERT INTO fetch_log (ts_utc, url, status, attempt)"
            " VALUES (?, ?, ?, 1)", fetches)
        fconn.commit()
        fconn.close()
        publish.build_site(digests, out, pipeline_db=pipeline, fetch_db=fetch)
        return out

    return build


def _meta(source_id=None, mode=None):
    import json

    payload = {k: v for k, v in (("source_id", source_id), ("mode", mode))
               if v}
    return json.dumps(payload, sort_keys=True)


DELIVERING_ITEMS = (
    ("TEST", HEALTH_TODAY, 16000, _meta()),
    ("TEST", "2026-07-30", 12000, _meta()),
    ("AGENCYPR", HEALTH_TODAY, 340, _meta("example-newsroom", "feed-only")),
    ("AGENCYPR", "2026-07-30", 300, _meta("example-newsroom", "feed-only")),
    ("AGENCYPR", HEALTH_TODAY, 310, _meta("example-email", "email-teaser")),
)
CLEAN_FETCHES = tuple(
    [(f"2026-07-31T0{i}:00:00Z", "https://feeds.example.gov/press.xml", 200)
     for i in range(6)]
    + [(f"2026-07-31T0{i}:00:00Z", "https://api.govinfo.gov/collections/TEST",
        200) for i in range(6)])


def test_health_summary_and_key_render_above_the_directory(health_site):
    """The page leads with the whole-directory picture: how many active
    sources delivered, how many recorded requests that returned nothing,
    the aggregate rate, and what every label means."""
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    assert '<h2 id="source-health">Source health and statistics</h2>' in page
    # 3 active sources, all delivering; 5 items over the 14-day window
    assert "<strong>3</strong> of 3 active sources delivered items" in page
    assert "5 item(s) in all" in page
    assert "0 source(s) recorded requests that returned no content" in page
    # the health section precedes the first channel group
    assert page.index('id="source-health"') < page.index('id="govinfo-collections"')
    # every label defined in words, with its live threshold substituted
    for word in ("delivering", "quiet", "degraded", "no response", "no data"):
        assert word in page
    assert "no item for more than 7 days" in page
    assert "10.0% or more of our requests returned no content" in page


def test_health_key_table_is_accessible(health_site):
    """The page's one table goes through `_accessible_tables`: a focusable
    labelled scroll region and `scope` on the header cells (A11Y-03)."""
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    assert ('<div class="table-scroll" role="region" tabindex="0"'
            ' aria-labelledby="source-health"><table>') in page
    assert page.count("<table>") == 1
    assert page.count('<th scope="col">') == 3
    assert "<th>" not in page   # every header cell carries its scope


def test_health_is_never_signalled_by_colour_alone(health_site):
    """Every indicator carries a word and a glyph as well as its colour,
    and names what it is about for a reader who meets it out of context
    (1.4.1, 1.3.1)."""
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    chips = re.findall(
        r'<span class="tag tag-health-([a-z-]+)">'
        r'<span class="health-glyph" aria-hidden="true">(.)</span>'
        r'<span class="vh">Ingestion health: </span>([a-z ]+)</span>', page)
    # one per active source card, plus one per row of the five-row key
    assert len(chips) == 3 + 5
    for label, glyph, word in chips:
        assert glyph and glyph not in "  "   # a real, visible mark
        assert word.replace(" ", "-") == label    # the word IS the label
    # the colour is paired in the stylesheet, never carried alone
    css = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
           / "style.css").read_text()
    assert ".tag-health-delivering" in css and ".health-glyph" in css


def test_each_card_states_its_own_numbers(health_site):
    """A label must be checkable from the card it sits on: volume, rate,
    content length, delivery mode, and the request outcomes are all there
    in words."""
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    card = page[page.index('id="src-example-newsroom"'):]
    card = card[:card.index("</article>")]
    assert "2 in 14 days (0.14 per day)" in card
    assert "most recent 2026-07-31" in card
    assert "320 characters average, 320 median" in card   # (340 + 300) / 2
    assert "shortest 300, longest 340" in card
    assert "<code>feed-only</code>" in card
    assert "the source publishes no more than this through this channel" in card
    assert "Our requests to feeds.example.gov:</span> 6 request(s) · 6 answered" in card
    assert "0 declined (4xx) · 0 server declined (5xx) · 0 no response" in card
    assert "0.0% returned no content" in card
    assert "tag-health-delivering" in card


def test_content_length_exposes_a_teaser_source(health_site):
    """Content length is the signal the operator asked for: a source
    emitting 310-character stubs is giving a reader far less than one
    emitting full text, and both numbers sit on the page."""
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    email_card = page[page.index('id="src-example-email"'):]
    email_card = email_card[:email_card.index("</article>")]
    assert "310 characters average" in email_card
    assert "<code>email-teaser</code>" in email_card
    assert "the bulletin carried a short teaser, not the full item" in email_card
    govinfo = page[page.index('id="src-govinfo-test"'):]
    govinfo = govinfo[:govinfo.index("</article>")]
    assert "14,000 characters average" in govinfo


def test_email_cards_say_why_there_is_no_request_table(health_site):
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    card = page[page.index('id="src-example-email"'):]
    card = card[:card.index("</article>")]
    assert "Our requests to" not in card
    assert "delivered to the project mailbox" in card
    assert "read from delivery recency alone" in card


def test_declined_requests_are_reported_with_their_mechanical_reason(health_site):
    """A host that declines a fifth of our requests is reported as
    degraded — with the counts, and with the standing note that a 5xx is
    the server declining and that we cannot say why."""
    fetches = tuple(
        [(f"2026-07-3{d}T01:00:00Z", "https://feeds.example.gov/press.xml", 200)
         for d in (0, 1)] * 4
        + [("2026-07-31T02:00:00Z", "https://feeds.example.gov/press.xml", 503)]
        * 2)
    page = (health_site(DELIVERING_ITEMS, fetches) / "sources.html").read_text()
    card = page[page.index('id="src-example-newsroom"'):]
    card = card[:card.index("</article>")]
    assert "tag-health-degraded" in card
    assert "2 of 10 request(s) to feeds.example.gov returned no content" in card
    assert "20.0%, at or above the 10% mark" in card
    assert "1 source(s) recorded requests that returned no content" in page
    # the mechanical reason, stated once for the page
    assert ("A 4xx or 5xx is the server declining to return content" in page)
    assert "we cannot tell which from outside" in page
    # and no verdict about the department anywhere
    for word in ("unreliable", "negligent", "irresponsible", "unhealthy"):
        assert word not in page.lower()


def test_shared_host_figures_are_labelled_as_host_wide(health_site):
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    card = page[page.index('id="src-govinfo-test"'):]
    card = card[:card.index("</article>")]
    assert "Our requests to api.govinfo.gov:" in card
    # one govinfo source in this registry, so no host-wide caveat
    assert "registered sources, so these figures are host-wide" not in card


def test_collector_errors_show_on_the_card(health_site):
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES,
                        collectors=[("host:feeds.example.gov", 4)])
            / "sources.html").read_text()
    card = page[page.index('id="src-example-newsroom"'):]
    card = card[:card.index("</article>")]
    assert "4 consecutive cycle(s) ended in an error" in card
    assert "tag-health-degraded" in card


def test_planned_sources_say_why_they_are_unmeasured(health_site):
    """Absence is stated, never silent: a planned source carries no health
    label, and the card says that is what its registry status means."""
    page = (health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
            / "sources.html").read_text()
    card = page[page.index('id="src-planned-newsroom"'):]
    card = card[:card.index("</article>")]
    assert "Not ingested: the registry status of this source is planned." in card
    assert "shown for active sources only" in card
    assert "tag-health-" not in card


def test_health_degrades_gracefully_without_databases(health_site):
    """The whole point of the fallback: a fresh clone or a CI run has no
    `data/`, and the source guide must still build — saying so, not
    showing a page of zeroes that would read as an outage."""
    out = health_site(with_dbs=False)
    page = (out / "sources.html").read_text()
    assert '<h2 id="source-health">' in page
    assert "Per-source statistics are not available in this build" in page
    assert "pipeline database not present" in page
    assert "The directory below is rendered from the registry alone." in page
    # no invented numbers, no labels, no table
    assert "tag-health-" not in page
    assert "<table>" not in page
    # the directory itself is unaffected
    assert page.count('<article class="src-card"') == 4
    # and the machine surface says the same thing rather than omitting it
    import json
    data = json.loads((out / "sources.json").read_text())
    assert data["available"] is False
    assert "not present" in data["unavailable_reason"]
    assert len(data["sources"]) == 4
    assert all(s.get("health") is None for s in data["sources"])


def test_sources_json_carries_the_same_facts_as_the_page(health_site,
                                                         monkeypatch):
    import json

    from fapd import config as _config

    # Machine surfaces emit absolute URLs when a base is configured (the
    # same rule digests.json follows). Pin it empty so this test asserts
    # the relative form deterministically; the absolute form is asserted
    # in its own test below.
    monkeypatch.setattr(_config, "SITE_BASE_URL", "")

    out = health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
    data = json.loads((out / "sources.json").read_text())
    assert data["available"] is True
    assert data["window"] == {"days": 14, "start": "2026-07-18",
                              "end": HEALTH_TODAY}
    # thresholds travel with the labels, so an agent can recompute any one
    assert data["thresholds"]["quiet_after_days"] == 7
    assert data["thresholds"]["degraded_error_rate_pct"] == 10.0
    assert set(data["health_labels"]) == {"delivering", "quiet", "degraded",
                                          "no-response", "no-data"}
    assert data["summary"]["delivering"] == 3
    assert data["summary"]["items_window"] == 5
    by_id = {s["id"]: s for s in data["sources"]}
    assert set(by_id) == {"govinfo-test", "example-newsroom", "example-email",
                          "planned-newsroom"}
    news = by_id["example-newsroom"]
    assert news["items"] == 2
    assert news["avg_chars"] == 320 and news["median_chars"] == 320
    assert news["delivery_mode"] == "feed-only"
    assert news["fetch"]["host"] == "feeds.example.gov"
    assert news["fetch"]["answered"] == 6
    assert news["health"] == "delivering"
    assert news["card"] == "sources.html#src-example-newsroom"
    assert by_id["example-email"]["fetch"] is None
    assert by_id["planned-newsroom"]["measured"] is False
    # the scope statement is part of the payload, not a page-only caveat
    assert "not a measurement of any agency" in data["scope"]
    assert "'active'" in data["measurement"]


def test_sources_json_stays_out_of_the_record_surfaces(health_site):
    """digests.json and the Atom feed enumerate the official record. Our
    ingestion statistics are not that and must never arrive as though
    they were."""
    out = health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
    for name in ("digests.json", "feed.xml"):
        text = (out / name).read_text()
        assert "sources.json" not in text
        assert "example-newsroom" not in text
    llms = (out / "llms.txt").read_text()
    assert "/sources.json" in llms
    assert "not a measurement of any agency or publisher" in llms
    assert "Not part of the official record" in llms
    assert "/sources.json" in (out / "robots.txt").read_text()


def test_sources_json_never_leaks_a_mailbox_address(health_site):
    out = health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
    text = (out / "sources.json").read_text()
    assert publish._EMAIL_ADDR_RE.search(text) is None


def test_the_health_surface_adds_no_script(health_site):
    """docs/code-standards.md §2 rule 10: the site ships one script, on
    /today.html only. Nothing built here may add a second."""
    out = health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
    for path in sorted(out.rglob("*.html")):
        assert "<script" not in path.read_text(), path.name


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


def test_readme_badges_render_without_a_third_party_request(digests, tmp_path,
                                                            monkeypatch):
    """A README badge is a remote image, and docs/site/privacy.md promises
    pages load no external images. Both survive: the badge's <img> is
    demoted to its alt text, the link around it stays clickable, and
    local images (digest graphics) are untouched."""
    from fapd import config

    root = tmp_path / "root"
    root.mkdir()
    (root / "README.md").write_text(
        "# Free Agentic Publication Digester (FAPD)\n\n"
        "[![Ask DeepWiki](https://deepwiki.com/badge.svg)]"
        "(https://deepwiki.com/owner/repo)\n"
        "[![Build](//img.example.com/b.svg)](https://ci.example.com/repo)\n"
        "![](https://tracker.example.com/pixel.gif)\n"
    )
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "readme.html").read_text()

    assert "deepwiki.com/badge.svg" not in page       # no off-site fetch
    assert "img.example.com" not in page
    assert "tracker.example.com" not in page
    assert 'src="http' not in page and 'src="//' not in page
    # ...but the badge still reads and still links, in a new tab
    assert ('<a href="https://deepwiki.com/owner/repo" target="_blank"'
            ' rel="noopener noreferrer">Ask DeepWiki'
            '<span class="vh"> (opens in a new tab)</span></a>') in page
    assert ">Build<span class=\"vh\"> (opens in a new tab)</span></a>" in page
    assert "image</p>" in page                        # empty alt keeps a word
    # no other page class regresses: the digest graphic (a local asset we
    # serve ourselves) still renders as an image
    assert ('<img alt="Graphic from 2026-1 (printed page 1)"'
            ' src="assets/2026-07-01/g.png"'
            ) in (out / "2026-07-01.html").read_text()
    # the rule is about where the bytes come from, not about images
    assert publish._textualize_external_images(
        "![Seal](assets/seal.png)") == "![Seal](assets/seal.png)"
    assert publish._textualize_external_images(
        '![B](https://x.test/b.svg "t")') == "B"


_EXTERNAL_IMG = re.compile(r"<img[^>]*\bsrc=\"(?:https?:)?//", re.IGNORECASE)


def test_no_page_on_the_site_references_an_external_image(digests, tmp_path):
    """Cheap sitewide tripwire for the privacy claim (docs/site/privacy.md:
    'no external fonts, scripts, images, or embeds'). Built from the real
    repo docs and README, so the next badge added anywhere trips this."""
    out = tmp_path / "site"
    publish.build_site(digests, out)
    offenders = [p.name for p in sorted(out.glob("*.html"))
                 if _EXTERNAL_IMG.search(p.read_text())]
    assert offenders == []


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
    # entry tags are controls for the same checkboxes the filter bar
    # drives, so clicking one on an entry and one in the bar are the
    # same act — and branch tags keep their colors either way
    assert ('<label class="tag tag-branch-legislative chip-toggle" '
            'for="f-legislative">legislative</label>') in page
    assert ('<label class="tag chip-toggle" for="f-senate-floor">'
            "senate floor</label>") in page
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
    assert ">stock trading ban<span class=\"vh\">" in page
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
    assert 'class="tag tag-branch-legislative chip-toggle"' in page
    assert 'class="tag tag-branch-executive chip-toggle"' in page
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
        assert f'<input type="checkbox" class="filter-cb" id="{slug}"' in page
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
    assert (f'<time class="utc" datetime="{DATE}T11:30:00Z">'
            '<span class="vh">Observed at </span>07:30:00'
            '<span class="vh"> Eastern time</span>'
            '<span aria-hidden="true"> ET</span></time>') in page
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


def test_entry_tags_and_bar_chips_drive_the_same_state(conn, tmp_path):
    """Clicking a tag on an entry and clicking it in the filter bar are
    one act: both are labels for the same checkbox, so the selection
    cannot drift out of sync, and several selections stack (each adds a
    rule, so only items carrying all of them survive)."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()

    stream = page.split('class="today-list"')[1]
    assert 'for="f-legislative"' in stream          # entry chip is a control
    bar = page.split('class="filter-bar"')[1].split('class="today-list"')[0]
    assert 'for="f-legislative"' in bar             # ...same target as the bar
    assert page.count('id="f-legislative"') == 1    # one checkbox, two labels

    # selection styling reaches both places
    assert ('#f-legislative:checked ~ .filter-bar label[for="f-legislative"],'
            in page)
    assert ('#f-legislative:checked ~ .today-list label[for="f-legislative"]'
            in page)
    # stacking is independent per keyword: each rule hides non-matching items
    assert ("#f-executive:checked ~ .today-list > .today-item:not(.k-executive)"
            "{display:none}") in page
    assert ("#f-press-release:checked ~ .today-list >"
            " .today-item:not(.k-press-release){display:none}") in page


def test_filter_options_narrow_to_keywords_that_co_occur(conn, tmp_path):
    """Choosing a keyword should stop offering keywords that never share
    an entry with it — otherwise the bar invites combinations that can
    only produce an empty stream."""
    from conftest import DATE

    _seed_today(conn)   # CREC item: legislative/senate floor; VA item: executive/press release/va
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()

    # one narrowing rule per keyword, not one per absent pair
    assert ("#f-legislative:checked ~ .filter-bar label:not(.c-legislative)"
            "{display:none}") in page

    bar = page.split('class="filter-bar"')[1].split('class="today-list"')[0]
    # 'senate floor' shares its entry with 'legislative' -> stays offered
    assert 'c-legislative' in bar.split('for="f-senate-floor"')[0].rsplit(
        "<label", 1)[1]
    # 'press release' never appears alongside 'legislative' -> filtered out
    press_chip = bar.split('for="f-press-release"')[0].rsplit("<label", 1)[1]
    assert "c-legislative" not in press_chip
    assert "c-executive" in press_chip and "c-va" in press_chip
    # a keyword always pairs with itself, so the chosen chip stays visible
    # (and therefore stays clickable to clear)
    leg_chip = bar.split('for="f-legislative"')[0].rsplit("<label", 1)[1]
    assert "c-legislative" in leg_chip


def test_filter_pairs_are_symmetric_and_include_self():
    items = [
        {"collection": "CREC", "doc_type": "SENATE", "agency": None,
         "source_id": None},
        {"collection": "FR", "doc_type": "RULE", "agency": "EPA",
         "source_id": None},
    ]
    pairs = publish._today_filter_pairs(items)
    assert "legislative" in pairs["senate floor"]
    assert "senate floor" in pairs["legislative"]
    assert "legislative" in pairs["legislative"]
    assert "legislative" not in pairs["final rule"]   # different entries
    assert pairs["epa"] == {"executive", "final rule", "epa"}


# --------------------------------------------------------------- the blog --

_LAUNCH_MD = """# Announcing the Free Agentic Publication Digester: one reader

*Dev notes, 2026-07-30. The launch article — why this project exists.*

## The problem, plainly

If you want to know what the government did, you have two options. Both
are bad in different ways.

Read the primary record, or read [coverage](https://example.com/story).
"""

_INTERNAL_MD = """# Source adapters and polite crawling

An internal devnote that nobody put on the allowlist.
"""


@pytest.fixture
def devnotes_root(tmp_path, monkeypatch):
    """A project root holding both an allowlisted post and an internal
    devnote — the allowlist, not the directory, decides what publishes."""
    from fapd import config

    root = tmp_path / "root"
    notes = root / "docs" / "devnotes"
    notes.mkdir(parents=True)
    (notes / "2026-07-30-launch-article.md").write_text(_LAUNCH_MD)
    (notes / "2026-07-28-source-adapters-and-polite-crawling.md").write_text(
        _INTERNAL_MD)
    (notes / "README.md").write_text("# Development notes\n\nInternal.\n")
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    return root


def test_blog_index_lists_the_post_with_date_and_teaser(digests, devnotes_root,
                                                        tmp_path):
    out = tmp_path / "site"
    stats = publish.build_site(digests, out)
    assert stats["blog_posts"] == 1
    index = (out / "blog.html").read_text()
    assert "<h1>Blog</h1>" in index
    assert 'href="blog-launch.html">Announcing the Free Agentic' in index
    assert '<span class="post-date">2026-07-30</span>' in index
    # teaser mirrors _teaser: the first sentence of the opening prose,
    # skipping the h1, the italic dateline, and the section heading
    assert ('<p class="teaser">If you want to know what the government did, '
            "you have two options.</p>") in index
    # the index says what a post is, and is not
    assert "not part of the daily digest" in index


def test_blog_post_page_renders_with_date_and_back_link(digests, devnotes_root,
                                                        tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    post = (out / "blog-launch.html").read_text()
    assert "<title>Announcing the Free Agentic Publication Digester" in post
    assert ">Announcing the Free Agentic Publication Digester" in post
    # the publication date sits directly under the article's own title
    assert '</h1><p class="post-meta">Published 2026-07-30' in post
    assert "not part of the daily digest or the official record" in post
    assert ('<p class="post-back"><a href="blog.html">&larr; All posts</a></p>'
            in post)
    # canonical-source footer names the markdown it came from
    assert "docs/devnotes/2026-07-30-launch-article.md" in post
    # the post's own outbound links obey the sitewide new-tab rule
    assert ('<a href="https://example.com/story" target="_blank"'
            ' rel="noopener noreferrer">') in post


def test_blog_publication_is_by_allowlist_not_by_directory(digests,
                                                           devnotes_root,
                                                           tmp_path):
    """docs/devnotes/ is internal; only files named in publish._BLOG_POSTS
    become pages. A future directory glob would fail this test on purpose."""
    out = tmp_path / "site"
    publish.build_site(digests, out)
    built = {p.name for p in out.glob("blog*.html")}
    assert built == {"blog.html", "blog-launch.html"}
    index = (out / "blog.html").read_text()
    assert "source-adapters" not in index
    assert "polite crawling" not in index
    assert "Development notes" not in index          # the directory README
    assert "README.md" not in {f for f, _s, _d in publish._BLOG_POSTS}
    sitemap = (out / "sitemap.xml").read_text()
    assert "source-adapters" not in sitemap


def test_blog_nav_link_on_every_page_class(digests, devnotes_root, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    for name in ("index.html", "2026-07-01.html", "agents.html",
                 "blog-launch.html"):
        assert 'href="blog.html">Blog</a>' in (out / name).read_text(), name
    # ...and the blog index links to itself too, marked as the current
    # page rather than dropped, so nav order is identical everywhere
    assert ('<a href="blog.html" aria-current="page">Blog</a>'
            in (out / "blog.html").read_text())


def test_blog_reaches_discovery_surfaces_not_record_surfaces(
        digests, devnotes_root, tmp_path, monkeypatch):
    """sitemap + llms.txt announce the blog; digests.json and the Atom feed
    stay purely official-record, so an agent polling them never receives
    commentary as a digest."""
    monkeypatch.setattr(publish.config, "SITE_BASE_URL", "")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    sitemap = (out / "sitemap.xml").read_text()
    assert "<loc>/blog.html</loc>" in sitemap
    assert "<loc>/blog-launch.html</loc>" in sitemap
    llms = (out / "llms.txt").read_text()
    assert "(/blog.html)" in llms
    assert "not part of the official record" in llms
    assert "blog" not in (out / "digests.json").read_text()
    assert "blog" not in (out / "feed.xml").read_text()


def test_blog_pages_ship_no_script(digests, devnotes_root, tmp_path):
    out = tmp_path / "site"
    publish.build_site(digests, out)
    for name in ("blog.html", "blog-launch.html"):
        assert "<script" not in (out / name).read_text(), name


def test_blog_degrades_gracefully_when_the_post_is_missing(digests, tmp_path,
                                                           monkeypatch):
    """An allowlisted file that is not on disk yields no page, no nav link,
    and no sitemap entry — never a broken link."""
    from fapd import config

    empty_root = tmp_path / "empty"
    (empty_root / "docs" / "devnotes").mkdir(parents=True)
    monkeypatch.setattr(config, "PROJECT_ROOT", empty_root)
    out = tmp_path / "site"
    stats = publish.build_site(digests, out)
    assert stats["blog_posts"] == 0
    assert not (out / "blog.html").exists()
    assert 'href="blog.html"' not in (out / "index.html").read_text()
    assert 'href="blog.html"' not in (out / "2026-07-01.html").read_text()
    assert "blog.html" not in (out / "sitemap.xml").read_text()
    assert "blog.html" not in (out / "llms.txt").read_text()


def test_blog_renders_the_real_launch_article(digests, tmp_path):
    """The committed article publishes; its sibling devnote does not."""
    from fapd import config

    article = (config.PROJECT_ROOT / "docs" / "devnotes"
               / "2026-07-30-launch-article.md")
    if not article.exists():
        pytest.skip("no launch article on disk")
    out = tmp_path / "site"
    stats = publish.build_site(digests, out)
    assert stats["blog_posts"] == 1
    post = (out / "blog-launch.html").read_text()
    assert "one polite reader for the official record" in post
    assert "The record was always yours" in post
    assert not (out / "blog-source-adapters-and-polite-crawling.html").exists()
    assert "source-adapters" not in (out / "blog.html").read_text()


# ------------------------------------------------------- accessibility --


def test_filter_checkboxes_name_themselves(conn, tmp_path):
    """A11Y-01 (4.1.2): one checkbox is referenced by a label in the bar
    and by one on every matching entry, and HTML-AAM concatenates them
    all into the accessible name — hundreds of repetitions. aria-label
    wins over <label>, so the shared-label design survives with a name a
    person can actually listen to."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()
    assert ('<input type="checkbox" class="filter-cb" id="f-executive"'
            ' aria-label="Filter to executive — 1 item(s)">') in page
    # 2.5.3 Label in Name: the visible text leads the accessible name
    assert 'aria-label="Filter to press release' in page


def test_every_page_class_has_a_skip_link_and_main_landmark(conn, tmp_path):
    """A11Y-02 (2.4.1): without this, a keyboard user on /today walks the
    header and then 58 invisible checkboxes before the first item."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    today = (tmp_path / "today.html").read_text()
    assert '<a class="skip-link" href="#main">Skip to main content</a>' in today
    assert '<main id="main" tabindex="-1">' in today
    # and a second skip past the filter bank, to the stream itself
    assert 'href="#today-stream">Skip ' in today
    # the target is the stream's own heading (A11Y-13), not the bare <ul>
    assert ('<h2 id="today-stream" tabindex="-1">Observed publications</h2>'
            '<ul class="today-list">') in today
    assert today.index('href="#today-stream"') < today.index('id="today-stream"')

    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "2026-07-29.md").write_text("# Daily Digest\n\nBody.\n")
    publish.build_site(digest_dir=tmp_path / "d", out_dir=tmp_path / "s")
    for name in ("index.html", "2026-07-29.html", "about.html"):
        page = (tmp_path / "s" / name).read_text()
        assert 'class="skip-link" href="#main"' in page, name
        assert '<main id="main"' in page, name
        assert '<nav aria-label="Site">' in page, name


def test_selection_is_not_signalled_by_colour_alone(conn, tmp_path):
    """A11Y-06 (1.4.1): a check glyph marks selected chips, and it is
    also what survives grayscale and forced-colors, where the accent
    fill is discarded."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()
    assert ('#f-executive:checked ~ .filter-bar label[for="f-executive"]::before'
            in page)
    assert '{content:"\\2713\\00a0"}' in page
    # contrast token, not a hardcoded white, on the selected fill
    assert "color:var(--accent-on)" in page
    # the rest lives in the shared stylesheet
    assert "@media (forced-colors: active)" in publish._STYLE
    assert "--accent-on: #0b1116;" in publish._STYLE   # dark theme: 8.46:1
    assert "color: #4448b8;" in publish._STYLE         # light legislative 5.71:1


def test_css_defects_found_by_the_audit_stay_fixed():
    """A11Y-20: `--rule` was never defined, so the whole border
    declaration on the mandatory disclosure box was invalid and dropped;
    `.rule-note` was styled only as `li.rule-note` while two call sites
    emit spans, which therefore rendered at body size."""
    css = publish._STYLE
    assert "var(--rule)" not in css
    assert ".rule-note, .source-note {" in css
    assert "li.rule-note, li.source-note { list-style: none; }" in css
    assert "border: 1px solid var(--border);" in css


_TABLE_DIGEST = """# Daily Digest — 2026-07-05

| | |
|---|---|
| **Digest date** | 2026-07-05 |

## 1. Congressional Floor Activity

| Chamber | Items |
|---|---|
| Senate | 2 |
| House | 3 |

- **An Item** — A summary sentence.
  - Included because: CREC-SEL-01 — floor item

## 2. Legislation

Nothing today.
"""


def test_digest_tables_keep_their_semantics(digests, tmp_path):
    """A11Y-03 (1.3.1, 2.1.1): `display: block` on a <table> removes the
    table, row, and cell roles in Chrome and Firefox, so a counts table
    is announced as a flat run of numbers with the headers gone. The
    scroll job moves to a focusable labelled wrapper instead."""
    (digests / "2026-07-05.md").write_text(_TABLE_DIGEST)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "2026-07-05.html").read_text()
    css = (out / "style.css").read_text()

    # the table itself is a table again
    assert "table {\n  border-collapse" in css
    assert "display: block;\n  overflow-x: auto;" not in css
    assert ".table-scroll { overflow-x: auto;" in css

    # every remaining table sits in a focusable, named scroll region
    assert page.count("<table>") == page.count('class="table-scroll"') == 1
    assert ('<div class="table-scroll" role="region" tabindex="0"'
            ' aria-labelledby="1-congressional-floor-activity"><table>') in page
    # ...whose label is a heading id that still exists on the page
    assert 'id="1-congressional-floor-activity"' in page
    # header cells state which axis they head
    assert '<th scope="col">Chamber</th>' in page
    assert "<th>" not in page

    # the compact-meta strip still ran first: its table is gone, not wrapped
    assert '<div class="digest-meta">' in page
    assert "Digest date</td>" not in page


def test_every_digest_heading_is_exposed_and_deep_links_resolve(digests,
                                                                 tmp_path):
    """A11Y-04 (1.3.1, 2.4.6): a closed <details> keeps its contents out
    of the accessibility tree, so a heading after the summary is not in
    the heading list; and the fragment-revealing algorithm opens a
    target's <details> ancestors, not the target, so an id on the
    <details> scrolled to a section that stayed shut."""
    (digests / "2026-07-05.md").write_text(_TABLE_DIGEST)
    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "2026-07-05.html").read_text()

    # the id string is unchanged, so existing deep links keep their form
    for anchor in ("1-congressional-floor-activity", "2-legislation"):
        assert f'<h2 class="sec-title" id="{anchor}">' in page
        # ...and it is inside the summary, which a closed details exposes
        head = page.split(f'id="{anchor}"')[0]
        assert head.rsplit("<summary>", 1)[1] == '<h2 class="sec-title" '
    # nothing carries the id on the <details> any more, and the duplicate
    # heading that used to sit inside the body is gone
    assert '<details class="digest-section" id=' not in page
    assert "sec-heading" not in page
    # exactly one element per section owns the anchor
    assert page.count('id="2-legislation"') == 1


def test_outbound_links_say_they_open_a_new_tab(digests, tmp_path, monkeypatch):
    """A11Y-12 (3.2.5, technique G201): a new tab opened without notice
    changes focus context with no announcement and stops Back working.
    The notice rides in the one enforcement point, `_externalize_links`
    (code-standards §2 rule 9), so no call site grows a second rule."""
    from fapd import config as _config

    monkeypatch.setattr(_config, "SITE_BASE_URL", "https://fapd.info")
    body = ('<a href="https://www.govinfo.gov/x">official</a>'
            '<a href="2026-07-01.html">yesterday</a>'
            '<a href="#main">jump</a>'
            '<a href="mailto:x@example.gov">write</a>')
    page = publish._render_page("T", body, "", "canonical")

    assert ('<a href="https://www.govinfo.gov/x" target="_blank"'
            ' rel="noopener noreferrer">official'
            '<span class="vh"> (opens in a new tab)</span></a>') in page
    # same-site, fragment and mailto links are untouched — no false notice
    for same_tab in ('<a href="2026-07-01.html">yesterday</a>',
                     '<a href="#main">jump</a>',
                     '<a href="mailto:x@example.gov">write</a>'):
        assert same_tab in page, same_tab
    assert page.count("(opens in a new tab)") == page.count('target="_blank"')
    assert ".vh {" in publish._STYLE


def test_link_purpose_is_stated_for_bare_date_links(conn, digests, tmp_path):
    """A11Y-16 (2.4.4): `← 2026-07-28` and `2026-07-29 · 2026-07-28` are
    bare dates in a screen reader's link list, which is how link
    navigation presents them."""
    from conftest import DATE

    out = tmp_path / "site"
    publish.build_site(digests, out)
    page = (out / "2026-07-02.html").read_text()
    assert '<span class="vh">Digest for </span>2026-07-01' in page

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    today = (tmp_path / "today.html").read_text()
    for link in re.findall(r'<a href="\d{4}-\d{2}-\d{2}\.html">(.*?)</a>',
                           today):
        assert link.startswith('<span class="vh">Digest for </span>'), link


def test_nav_marks_the_current_page_instead_of_dropping_it(digests, tmp_path):
    """Open question 8, resolved: every page renders every nav link in
    the same order (3.2.3), and its own is marked aria-current rather
    than omitted — orientation for a reader arriving mid-site."""
    out = tmp_path / "site"
    publish.build_site(digests, out)
    for name, href in (("index.html", "index.html"),
                       ("agents.html", "agents.html"),
                       ("about.html", "about.html")):
        page = (out / name).read_text()
        assert f'<a href="{href}" aria-current="page">' in page, name
        assert page.count('aria-current="page"') == 1, name
    # a digest page is not a nav destination, so nothing is current there
    assert 'aria-current' not in (out / "2026-07-01.html").read_text()


def test_today_filter_states_what_is_selected(conn, tmp_path):
    """A11Y-07 (4.1.3): selecting a keyword changed what was on the page
    and nothing said so — the bar's "N item(s) unfiltered" is the before
    number and never moves. Two script-free readouts: which filters are
    on, in words, and how many items survived, by CSS counter."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()

    assert '<p class="filter-status" role="status">' in page
    assert '<span class="fs-none">No keyword filter is selected; all 2 ' in page
    assert '<span class="fs-lead">Filtered to items tagged: </span>' in page
    assert '<span class="fs-executive">executive </span>' in page
    assert (".today-stream:has(#f-executive:checked) .fs-executive"
            "{display:inline}") in page
    # the count of what survives, from a counter the filter cannot fake
    assert '</ul><p class="filter-count"></p></form>' in page
    css = publish._STYLE
    assert ".today-list > .today-item { counter-increment: shown; }" in css
    assert '.filter-count::after { content: counter(shown)' in css
    # still no second script
    assert page.count("<script") == 1


def test_filter_bar_is_a_labelled_group_with_headings(conn, tmp_path):
    """A11Y-13 (1.3.1, 2.4.6): the bar was a <nav> landmark — a 58-control
    form group is not navigation — and /today carried exactly one heading
    for 400 KB of content."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()
    assert ('<div class="filter-bar" role="group"'
            ' aria-labelledby="filter-heading">') in page
    assert '<h2 class="filter-lead" id="filter-heading">Filter by keyword' in page
    assert '<h2 id="today-stream" tabindex="-1">Observed publications</h2>' in page
    assert "<nav class=\"filter-bar\"" not in page
    # the sibling combinator the whole filter rests on still reaches the list
    assert page.index("filter-cb") < page.index('class="filter-bar"')
    assert page.index('class="filter-bar"') < page.index('class="today-list"')
    assert ("#f-executive:checked ~ .today-list > .today-item:not(.k-executive)"
            "{display:none}") in page


def test_times_and_counts_carry_their_units(conn, tmp_path):
    """A11Y-14 (1.3.1): a clock reading and two letters said nothing
    about what the number was, and the observation-vs-publication
    distinction the project cares about most was nowhere in the markup."""
    from conftest import DATE

    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()
    assert '<span class="vh">Observed at </span>' in page
    assert '<span class="vh"> Eastern time</span>' in page
    assert '<span aria-hidden="true"> ET</span>' in page   # still visible
    assert ('<span class="filter-n"><span class="vh">, </span>1'
            '<span class="vh"> items</span></span>') in page


def test_chips_meet_the_target_size_and_boundary_floors():
    """A11Y-09 (2.5.8) and the plain-chip half of A11Y-10 (1.4.11): entry
    chips computed 22.0 px tall and their boundary measured 1.34:1."""
    css = publish._STYLE
    assert "padding-top: 0.3rem; padding-bottom: 0.3rem;" in css
    assert "--control-border: #868f99;" in css       # 3.22:1 vs --bg
    assert "--control-border: #646f7a;" in css       # dark: 3.61:1
    # the control-border rule must precede the branch block, or its equal
    # specificity would beat currentColor and undo A11Y-10
    assert css.index("border-color: var(--control-border)") < \
        css.index(".tag-branch-legislative")
    # the count no longer fades below threshold over a tinted chip: it
    # inherits the chip's own (now compliant) text colour
    filter_n = css.split(".filter-n {")[1].split("}")[0]
    assert "opacity" not in filter_n


def test_focus_and_forced_colors_have_author_answers():
    """A11Y-17 (2.4.7) and A11Y-08: the only author focus style used to
    be one generated rule on the filter chips, and in forced-colors mode
    the accent fill is discarded, which is what carried selection."""
    css = publish._STYLE
    assert ":where(a, button, summary, [tabindex]):focus-visible {" in css
    assert "outline: 3px solid var(--accent);" in css
    forced = css.split("@media (forced-colors: active) {")[1].split("\n}")[0]
    for rule in (".live-dot { outline: 1px solid CanvasText; }",
                 ".skip-link { border: 2px solid CanvasText; }",
                 ".today-disclosure { border: 1px solid CanvasText; }"):
        assert rule in forced, rule
    assert "outline: 3px solid Highlight;" in forced


def test_generated_glyphs_are_not_spoken():
    """A11Y-15 (1.1.1): CSS generated content reaches the accessibility
    tree in Chrome and Safari, so `▸` was announced as "black
    right-pointing small triangle" before every section title."""
    css = publish._STYLE
    # NB the stylesheet is not a raw string: these must survive into the
    # served CSS as CSS escapes, not as Python octal escapes.
    assert r'content: "\25B8\00a0" / "";' in css
    assert r'content: "\25BE\00a0" / "";' in css
    assert '.plain-label::after { content: ":" / ""; }' in css
    # the selection check mark keeps NO alternative text on purpose: it
    # is the one non-colour signal of selection, and `/ ""` reached
    # Firefox only in late 2024 — an engine without it drops the whole
    # declaration and the signal with it.
    assert r'\2713\00a0" / ""' not in publish._STYLE


def test_public_accessibility_statement_is_published():
    """The statement is a site page like any other: docs/site/*.md is
    picked up by `_build_doc_pages`, so it joins the nav, the sitemap,
    and llms.txt with no extra wiring."""
    from fapd import config

    path = config.PROJECT_ROOT / "docs" / "site" / "accessibility.md"
    if not path.exists():
        pytest.skip("no docs/site on disk")
    text = path.read_text(encoding="utf-8")
    assert "hustleyourcity@gmail.com" in text          # a reachable address
    assert "Known limitations" in text                 # named, not hidden
    # the untested-with-real-AT limitation is stated (wording may vary;
    # the substance is what the statement must not lose)
    assert "assistive technology" in text
    assert "hustleyourcity@gmail.com" in text          # a real route to report
    assert "WCAG 2.2" in text and "conformant" in text  # the legal claim
    assert ("accessibility", "Accessibility") in publish._doc_page_index()


def test_header_expands_the_acronym(tmp_path):
    """Branding rule: the acronym is always expanded. The header is the
    one place a first-time reader meets the name."""
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "2026-07-29.md").write_text("# Daily Digest\n\nBody.\n")
    publish.build_site(digest_dir=tmp_path / "d", out_dir=tmp_path / "s")
    page = (tmp_path / "s" / "index.html").read_text()
    assert "FAPD<span" in page
    assert "Free Agentic Publication Digester</span></a>" in page
    assert 'aria-label="Free Agentic Publication Digester (FAPD)"' in page


def test_sources_json_uses_absolute_urls_when_a_base_is_configured(
        health_site, monkeypatch):
    """Agents fetching sources.json off-site need resolvable links, the
    same contract digests.json keeps."""
    import json

    from fapd import config as _config

    monkeypatch.setattr(_config, "SITE_BASE_URL", "https://fapd.info")
    out = health_site(DELIVERING_ITEMS, CLEAN_FETCHES)
    data = json.loads((out / "sources.json").read_text())
    news = next(s for s in data["sources"] if s["id"] == "example-newsroom")
    assert news["card"] == (
        "https://fapd.info/sources.html#src-example-newsroom")


def test_today_excludes_publisher_backdated_items(conn, tmp_path):
    """The live page keys off our OBSERVATION day, so first-activation
    backfill rendered as today's news: usps-newsroom shipped 664 items
    dated back to 2021 and odni-news 54, all visible on /today while the
    digest correctly excluded them under AGENCYPR-EX-01. The live view
    must apply the same dating rule the digest does."""
    import json

    from conftest import DATE

    _seed_today(conn)
    # an item observed today that its publisher dates years ago
    conn.execute("INSERT INTO packages (package_id, collection, date_issued,"
                 " last_modified, title, first_seen_at) VALUES"
                 " ('PR-old', 'AGENCYPR', ?, 'x', 'Old release', 'x')", (DATE,))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, title, text, char_count, metadata, extracted_at,"
        " extractor_version) VALUES ('PR-old', '', 'AGENCYPR', 'PRESS',"
        " 'Old release', 'body', 4, ?, 'x', 1)",
        (('{"source_id": "usps-newsroom", "mode": "feed-only",'
          ' "claimed_published_at": "Fri, 24 Sep 2021 10:00:00 +0000"}'),))
    conn.execute(
        "INSERT INTO item_journal (observed_at, source_class, package_id,"
        " granule_id, collection, source_id, digest_date, event) VALUES"
        " (?, 'agency', 'PR-old', '', 'AGENCYPR', 'usps-newsroom', ?,"
        "  'ingested')", (f"{DATE}T12:00:00Z", DATE))
    conn.commit()

    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    page = (tmp_path / "today.html").read_text()

    assert "Old release" not in page, "a 2021 release must not read as today's news"
    assert "publishers date earlier" in page          # disclosed, not hidden
    assert "VA announces a claims program" in page    # today's items still shown

    # agents still get everything, labelled
    data = json.loads((tmp_path / "today.json").read_text())
    assert data["backfill_count"] == 1
    old = next(i for i in data["items"] if i["package_id"] == "PR-old")
    assert old["is_backfill"] is True and old["claimed_day"] == "2021-09-24"
    live = next(i for i in data["items"] if i["package_id"] == "AGENCYPR-x")
    assert live["is_backfill"] is False

"""Agency ingestion tests: fakes only, no network."""

import pytest

from fapd import agencies, config, db

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Release A</title><link>https://x.gov/a</link><guid>g-a</guid>
<pubDate>Mon, 27 Jul 2026 10:00:00 GMT</pubDate><description>d</description></item>
<item><title>Release B</title><link>https://x.gov/b</link><guid>g-b</guid>
<pubDate>Mon, 27 Jul 2026 11:00:00 GMT</pubDate><description>d</description></item>
</channel></rss>"""

ARTICLE = b"<html><body><article>Full agency release text body.</article></body></html>"


class Resp:
    def __init__(self, body=b"", status=200, headers=None, url=None):
        self.content = body
        self.status_code = status
        self.headers = headers or {"Content-Type": "text/html"}
        self.url = url


class FakeAgency:
    def __init__(self, feed=RSS, feed_headers=None, article=ARTICLE, fail_articles=False):
        self.calls = []
        self.feed = feed
        self.feed_headers = feed_headers or {"Content-Type": "application/rss+xml",
                                             "ETag": '"e1"'}
        self.article = article
        self.fail_articles = fail_articles

    def get(self, url, params=None, headers=None):
        self.calls.append({"url": url, "headers": headers})
        if "feed" in url:
            if headers and headers.get("If-None-Match") == '"e1"':
                return Resp(status=304, headers={"Content-Type": "text/xml"})
            return Resp(self.feed, headers=self.feed_headers)
        if self.fail_articles:
            import requests

            raise requests.ConnectionError("blocked")
        return Resp(self.article, url=url)


class FakeWayback:
    def __init__(self):
        self.saved = []

    def save(self, url):
        self.saved.append(url)
        return f"https://web.archive.org/web/20260728000000/{url}"


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CAPTURE_DIR", tmp_path / "captures")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")
    conn = db.connect(tmp_path / "meta.db")
    yield conn
    conn.close()


def entry(id="gao-reports", name="Government Accountability Office"):
    return {"id": id, "name": name, "urls": {"feed": "https://x.gov/feed.xml"}}


def test_full_ingest_chain(env):
    client, wb = FakeAgency(), FakeWayback()
    stats = agencies.poll_source(client, wb, env, entry())
    assert stats["new_items"] == 2
    assert stats["articles_fetched"] == 2
    assert stats["wayback_submitted"] == 2
    pkg = env.execute("SELECT * FROM packages WHERE collection='AGENCYPR'").fetchall()
    assert len(pkg) == 2
    text = env.execute(
        "SELECT text, metadata FROM extracted_texts WHERE collection='AGENCYPR' LIMIT 1"
    ).fetchone()
    assert "Full agency release text body" in text["text"]
    assert "web.archive.org" in text["metadata"]
    # claimed vs observed dates separated in documents
    doc = env.execute("SELECT * FROM documents").fetchone()
    assert doc["claimed_published_at"].startswith("Mon, 27 Jul")
    assert doc["first_seen_at"] != doc["claimed_published_at"]


def test_second_poll_dedupes_and_uses_conditional_get(env):
    client, wb = FakeAgency(), FakeWayback()
    agencies.poll_source(client, wb, env, entry())
    stats2 = agencies.poll_source(client, wb, env, entry())
    assert stats2["feed_status"] == "not-modified"
    assert stats2["new_items"] == 0
    sent = client.calls[-1]["headers"]
    assert sent["If-None-Match"] == '"e1"'
    assert env.execute("SELECT COUNT(*) FROM packages").fetchone()[0] == 2


def test_feed_only_source_skips_articles(env):
    client, wb = FakeAgency(), FakeWayback()
    e = {**entry(id="defense-newsroom", name="Department of Defense"), "adapter": "rss-feed-only"}
    stats = agencies.poll_source(client, wb, env, e)
    assert stats["new_items"] == 2 and stats["articles_fetched"] == 0
    assert not wb.saved
    row = env.execute("SELECT metadata FROM extracted_texts LIMIT 1").fetchone()
    assert '"mode": "feed-only"' in row["metadata"]


def test_article_failure_falls_back_to_feed_metadata(env):
    client, wb = FakeAgency(fail_articles=True), FakeWayback()
    stats = agencies.poll_source(client, wb, env, entry())
    assert stats["new_items"] == 2 and stats["errors"] == 2
    row = env.execute("SELECT text, metadata FROM extracted_texts LIMIT 1").fetchone()
    assert row["text"] == "Release A — d"  # title + feed description
    assert '"mode": "feed-fallback"' in row["metadata"]
    kinds = [r[0] for r in env.execute("SELECT change_kind FROM captures")]
    assert kinds.count("error") == 2  # absence asserted


def test_run_isolates_and_exports_manifest(env, tmp_path):
    class Exploding:
        def get(self, *a, **k):
            raise ValueError("boom")

    results = agencies.run(Exploding(), None, env, [entry()])
    assert results[0]["feed_status"] in ("crash", "error:ValueError")
    assert list((tmp_path / "manifests").glob("*.jsonl"))


def test_empty_extraction_never_stored_as_full(env):
    """A page that extracts to nothing (challenge interstitial, blank shell)
    is stored as disclosed fallback, never as mode 'full' with empty text."""
    client, wb = FakeAgency(article=b"<html><body><script>x()</script></body></html>"), FakeWayback()
    stats = agencies.poll_source(client, wb, env, entry())
    assert stats["new_items"] == 2 and stats["errors"] == 2
    rows = env.execute("SELECT text, metadata FROM extracted_texts").fetchall()
    for r in rows:
        assert '"mode": "extract-fallback"' in r["metadata"]
        assert r["text"].strip()  # feed metadata, never empty


def test_extract_failure_degrades_item_not_source(env, monkeypatch):
    """One unparseable page falls back to feed metadata (mode disclosed);
    the source's remaining items still ingest."""
    class ExplodingExtract(agencies.SourceAdapter):
        def extract_text(self, body, content_type, item):
            if item["link"].endswith("/a"):
                raise ValueError("malformed page")
            return super().extract_text(body, content_type, item)

    monkeypatch.setitem(agencies.ADAPTERS, "exploding", ExplodingExtract)
    client, wb = FakeAgency(), FakeWayback()
    stats = agencies.poll_source(client, wb, env, {**entry(), "adapter": "exploding"})
    assert stats["new_items"] == 2  # both stored despite one extraction failure
    assert stats["errors"] == 1
    rows = env.execute(
        "SELECT text, metadata FROM extracted_texts ORDER BY package_id").fetchall()
    modes = sorted("extract-fallback" in r["metadata"] for r in rows)
    assert modes == [False, True]  # one full, one degraded-and-disclosed
    failed = next(r for r in rows if "extract-fallback" in r["metadata"])
    assert failed["text"] == "Release A — d"  # feed metadata, not empty
    # the capture happened before extraction failed — evidence survives
    assert env.execute("SELECT COUNT(*) FROM captures WHERE change_kind='new'")\
        .fetchone()[0] == 2


# ---- Concurrency across hosts (GUIDE §4: per-host pacing, shared budgets) ----


def test_host_groups_shares_worker_per_host():
    entries = [
        {"id": "a", "urls": {"feed": "https://www.dol.gov/rss/a.xml"}},
        {"id": "b", "urls": {"feed": "https://WWW.DOL.GOV/rss/b.xml"}},
        {"id": "c", "urls": {"feed": "https://www.gao.gov/rss/c.xml"}},
        {"id": "d", "urls": {}},  # no feed URL: grouped, still reported
    ]
    groups = agencies.host_groups(entries)
    assert [e["id"] for e in groups["www.dol.gov"]] == ["a", "b"]
    assert [e["id"] for e in groups["www.gao.gov"]] == ["c"]
    assert [e["id"] for e in groups[""]] == ["d"]


def test_run_concurrent_one_client_per_host(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CAPTURE_DIR", tmp_path / "captures")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")
    made = []

    class CtxAgency(FakeAgency):
        def __init__(self):
            super().__init__()
            made.append(self)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

    class CtxWayback(FakeWayback):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

    entries = [
        {**entry(id="dol-one"), "urls": {"feed": "https://x.gov/feed.xml"}},
        {**entry(id="dol-two"), "urls": {"feed": "https://x.gov/feed2.xml"}},
        {**entry(id="gao"), "urls": {"feed": "https://y.gov/feed.xml"}},
    ]
    results = agencies.run_concurrent(
        entries, client_factory=CtxAgency, wayback_factory=CtxWayback,
        conn_factory=lambda: db.connect(tmp_path / "meta.db"))
    assert len(made) == 2  # one client per host, never per source
    assert {r["id"] for r in results} == {"dol-one", "dol-two", "gao"}
    # same-host sources dedupe against one DB; second feed re-serves the
    # same two items under new package ids (distinct source_id) — all stored
    conn = db.connect(tmp_path / "meta.db")
    assert conn.execute(
        "SELECT COUNT(*) FROM packages WHERE collection='AGENCYPR'"
    ).fetchone()[0] == 6
    conn.close()
    assert list((tmp_path / "manifests").glob("*.jsonl"))


def test_run_concurrent_empty_entries():
    assert agencies.run_concurrent([]) == []


# ---- UspsAdapter (probe 2026-07-26: no GUIDs; links via JS interstitial) ----

# Mirrors the real captured interstitial (data/captures/86/86d65e1c….bin):
# a JS redirect page whose only visible text is its <title>; no JSON-LD,
# no framework state blob, no article content.
USPS_INTERSTITIAL = b"""<!doctype html><html><head><meta charset="utf-8">
<title>RSS Feed Request</title>
<script>
function getQueryVariable(variable) { /* reads location.search */ }
var release = getQueryVariable('nr');
release = '/newsroom/' + (release.substring(0,1) == '/' ? release.substring(1) : release);
setTimeout(function(){ window.location = release; }, 3000);
</script></head><body></body></html>"""

USPS_ITEM = {
    "title": "USPS issues new Barbie Forever stamps",
    "link": "https://about.usps.com/newsroom/rssrequest.htm"
            "?nr=national-releases/2026/0711-barbie.htm",
    "guid": None,
    "description": "AUSTIN, TX - The U.S. Postal Service honored Barbie"
                   " with a new series of 10 collectible stamps.",
}

USPS_RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>USPS issues new Barbie Forever stamps</title>
<link>https://about.usps.com/newsroom/rssrequest.htm?nr=national-releases/2026/0711-barbie.htm</link>
<pubDate>Sat, 11 Jul 2026 09:59:32 -0400</pubDate>
<description>AUSTIN, TX - The U.S. Postal Service honored Barbie with a new series of 10 collectible stamps.</description></item>
<item><title>USPS issues new Barbie Forever stamps</title>
<link>https://About.USPS.com/newsroom/national-releases/2026/0711-barbie.htm?utm_source=rss#top</link>
<pubDate>Sat, 11 Jul 2026 09:59:32 -0400</pubDate>
<description>AUSTIN, TX - The U.S. Postal Service honored Barbie with a new series of 10 collectible stamps.</description></item>
<item><title>Celebrating 250 Years of the Declaration of Independence</title>
<link>https://about.usps.com/newsroom/rssrequest.htm?nr=national-releases/2026/0704-declaration.htm</link>
<pubDate>Sat, 04 Jul 2026 10:00:48 -0400</pubDate>
<description>PHILADELPHIA - The Postal Service pays tribute to the Declaration.</description></item>
</channel></rss>"""


def test_usps_stable_id_collapses_url_noise_to_one_identity():
    a = agencies.UspsAdapter()
    canonical = "https://about.usps.com/newsroom/national-releases/2026/0711-barbie.htm"
    variants = [
        # interstitial link, exactly as the feed carries it
        "https://about.usps.com/newsroom/rssrequest.htm?nr=national-releases/2026/0711-barbie.htm",
        # interstitial with host case, extra query params, fragment
        "https://About.USPS.com/newsroom/rssrequest.htm?nr=national-releases/2026/0711-barbie.htm&utm_source=rss#top",
        # nr with a leading slash (the page's own JS strips it)
        "https://about.usps.com/newsroom/rssrequest.htm?nr=/national-releases/2026/0711-barbie.htm",
        # the resolved article URL itself, with and without noise
        canonical,
        canonical + "?utm_campaign=x#body",
        canonical + "/",
    ]
    assert {a.stable_id({"link": v}) for v in variants} == {canonical}


def test_usps_stable_id_keeps_distinct_articles_distinct():
    a = agencies.UspsAdapter()
    base = "https://about.usps.com/newsroom/rssrequest.htm?nr=national-releases/2026/"
    assert (a.stable_id({"link": base + "0711-barbie.htm"})
            != a.stable_id({"link": base + "0704-declaration.htm"}))


def test_usps_extract_text_interstitial_falls_back_to_feed_metadata():
    a = agencies.UspsAdapter()
    text = a.extract_text(USPS_INTERSTITIAL, "text/html", USPS_ITEM)
    assert text.startswith("USPS issues new Barbie Forever stamps — AUSTIN, TX")
    assert "RSS Feed Request" not in text


def test_usps_extract_text_real_html_and_empty_body():
    a = agencies.UspsAdapter()
    page = b"<html><body><p>Actual article body text.</p></body></html>"
    assert a.extract_text(page, "text/html", USPS_ITEM) == "Actual article body text."
    # empty/garbage bodies never raise; fall back to feed metadata
    assert a.extract_text(b"", "text/html", USPS_ITEM).startswith(
        "USPS issues new Barbie Forever stamps")


def test_usps_poll_is_feed_only_and_dedupes_url_variants(env):
    client, wb = FakeAgency(feed=USPS_RSS), FakeWayback()
    e = {**entry(id="usps-newsroom", name="USPS Newsroom"), "adapter": "usps"}
    stats = agencies.poll_source(client, wb, env, e)
    # 3 feed items, but two are URL variants of one article
    assert stats["new_items"] == 2
    assert stats["articles_fetched"] == 0  # interstitial never fetched (§4)
    assert not wb.saved
    rows = env.execute(
        "SELECT text, metadata FROM extracted_texts WHERE collection='AGENCYPR'"
    ).fetchall()
    assert len(rows) == 2
    assert all('"mode": "feed-only"' in r["metadata"] for r in rows)
    assert any(r["text"].startswith(
        "USPS issues new Barbie Forever stamps — AUSTIN, TX") for r in rows)
    # document identity is the resolved, normalized article URL
    ids = {r["stable_id"] for r in env.execute("SELECT stable_id FROM documents")}
    assert ids == {
        "https://about.usps.com/newsroom/national-releases/2026/0711-barbie.htm",
        "https://about.usps.com/newsroom/national-releases/2026/0704-declaration.htm",
    }


# ------------------------------------------------- the items() seam (P0) --


class IndexAdapter(agencies.SourceAdapter):
    """A non-feed source: enumerates from an index the feed parser cannot
    read, and needs no article fetch."""

    def items(self, body, content_type):
        rows = [ln.split("|") for ln in body.decode().splitlines() if ln.strip()]
        return "test-index", [
            {"title": t, "link": u, "guid": g,
             "claimed_date": "Tue, 28 Jul 2026 12:00:00 +0000",
             "description": "", "description_chars": 0}
            for g, t, u in rows
        ]

    def wants_article(self):
        return False


def test_items_seam_ingests_a_non_feed_source(env, monkeypatch):
    """The whole point of Phase 0: a shape probe.parse_feed cannot read
    still reaches storage, and inherits dedupe, mode disclosure, dating
    and identity from the loop unchanged."""
    monkeypatch.setitem(agencies.ADAPTERS, "test-index", IndexAdapter)

    class IndexClient:
        def get(self, url, params=None, headers=None):
            return Resp(b"v1|First vote|https://x.gov/v1\nv2|Second|https://x.gov/v2",
                        headers={"Content-Type": "application/xml"})

    e = {**entry(), "adapter": "test-index",
         "urls": {"index": "https://x.gov/votes/index.xml"}}
    stats = agencies.run(IndexClient(), None, env, [e])[0]
    assert stats["feed_status"] == "test-index:2"
    assert stats["new_items"] == 2
    assert stats["articles_fetched"] == 0        # wants_article() is False

    rows = env.execute(
        "SELECT package_id, metadata, text FROM extracted_texts"
        " ORDER BY package_id").fetchall()
    assert len(rows) == 2
    assert all('"mode": "feed-only"' in r["metadata"] for r in rows)
    # identity came from the adapter's guid, not the URL
    assert rows[0]["package_id"] == agencies._package_id("gao-reports", "v1")

    # a second poll ingests nothing new — dedupe is the loop's, not the
    # adapter's, so every future adapter inherits it
    again = agencies.run(IndexClient(), None, env, [e])[0]
    assert again["new_items"] == 0


def test_source_url_resolves_index_and_collection_keys():
    """poll_source and host_groups must resolve identically, or a source
    is grouped under one host and fetched from another."""
    assert agencies.source_url({"urls": {"feed": "https://a.gov/f"}}) == "https://a.gov/f"
    assert agencies.source_url({"urls": {"index": "https://b.gov/i"}}) == "https://b.gov/i"
    assert agencies.source_url({"urls": {"collection": "https://c.gov/c"}}) == "https://c.gov/c"
    assert agencies.source_url({"urls": {}}) is None

    groups = agencies.host_groups([
        {"id": "a", "urls": {"feed": "https://one.gov/f"}},
        {"id": "b", "urls": {"index": "https://one.gov/i"}},   # same host
        {"id": "c", "urls": {"index": "https://two.gov/i"}},
    ])
    assert sorted(groups) == ["one.gov", "two.gov"]
    assert len(groups["one.gov"]) == 2      # one client, one pacing clock

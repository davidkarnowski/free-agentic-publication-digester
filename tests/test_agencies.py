"""Agency ingestion tests: fakes only, no network."""

import json
import datetime as dt
import pathlib

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


# ---- Senate roll-call votes (xml-index adapter, GUIDE §3 recorded votes) ----

# Shapes copied from the live bytes fetched 2026-07-31: no year on the menu's
# vote_date, an always-empty vote_tally, and an en-bloc row that carries no
# issue/question/result at all.
VOTE_MENU = b"""<?xml version="1.0" encoding="UTF-8"?>
<vote_summary>
  <congress>119</congress><session>2</session><congress_year>2026</congress_year>
  <votes>
    <vote><vote_number>00217</vote_number><vote_date>30-Jul</vote_date>
      <issue>S.Res. 817</issue><question>On the Resolution
         </question><result>Agreed to</result><vote_tally>
        </vote_tally><title>S. Res. 817; An executive resolution.</title></vote>
    <vote><vote_number>00216</vote_number><vote_date>29-Jul</vote_date>
      <issue>S.J.Res. 181</issue><question>On the Motion to Discharge</question>
      <result>Rejected</result><vote_tally/>
      <title>Motion to Discharge S.J. Res. 181.</title></vote>
    <vote><vote_number>00124</vote_number><vote_date>14-May</vote_date>
      <en_bloc/><vote_tally/><title>Confirmation: En Bloc Nominations.</title></vote>
    <vote><vote_number>00003</vote_number><vote_date>garbage</vote_date>
      <issue>PN1</issue><question>On the Nomination</question>
      <result>Confirmed</result><title>Confirmation: someone.</title></vote>
  </votes>
</vote_summary>"""

VOTE_RECORD = b"""<?xml version="1.0" encoding="UTF-8"?><roll_call_vote>
  <congress>119</congress><session>2</session><congress_year>2026</congress_year>
  <vote_number>217</vote_number><vote_date>July 30, 2026,  01:46 PM</vote_date>
  <vote_question_text>On the Resolution S.Res. 817</vote_question_text>
  <vote_document_text>An executive resolution.</vote_document_text>
  <vote_result_text>Resolution Agreed to (2-1)</vote_result_text>
  <question>On the Resolution</question><vote_title>S. Res. 817</vote_title>
  <vote_result>Resolution Agreed to</vote_result>
  <count><yeas>2</yeas><nays>1</nays><present/><absent>1</absent></count>
  <members>
    <member><member_full>Banks (R-IN)</member_full><vote_cast>Yea</vote_cast></member>
    <member><member_full>Armstrong (R-OK)</member_full><vote_cast>Yea</vote_cast></member>
    <member><member_full>Baldwin (D-WI)</member_full><vote_cast>Nay</vote_cast></member>
    <member><member_full>Alsobrooks (D-MD)</member_full>
      <vote_cast>Not Voting</vote_cast></member>
  </members>
</roll_call_vote>"""


class FakeSenate:
    """Serves the menu at the index URL and the record at every vote URL."""

    def __init__(self, menu=VOTE_MENU, record=VOTE_RECORD):
        self.menu, self.record, self.calls = menu, record, []

    def get(self, url, params=None, headers=None):
        self.calls.append(url)
        body = self.menu if "roll_call_lists" in url else self.record
        return Resp(body, headers={"Content-Type": "text/xml"}, url=url)


def senate_entry():
    return {"id": "senate-xml", "name": "Senate.gov XML services",
            "adapter": "senate-votes",
            "urls": {"index": "https://www.senate.gov/legislative/LIS/"
                              "roll_call_lists/vote_menu_119_2.xml"}}


@pytest.fixture
def senate_today(monkeypatch):
    """Freeze the publication day so the lookback window is deterministic."""
    monkeypatch.setattr(agencies, "publication_date", lambda: "2026-07-31")


def test_vote_menu_is_bounded_to_the_lookback_window(senate_today):
    """AN INDEX IS NOT A FEED: the live menu carries a whole session (217
    votes on 2026-07-31). Only votes inside INDEX_LOOKBACK_DAYS come back,
    so first activation costs a handful of article fetches, not hundreds."""
    fmt, items = agencies.SenateVotesAdapter().items(VOTE_MENU, "text/xml")
    assert fmt == "senate-vote-menu"
    # 00124 is months old; 00003's date is unreadable — neither is returned.
    assert [i["extra"]["vote_number"] for i in items] == ["00216", "00217"]


def test_vote_dates_are_iso_so_the_digest_can_read_them(senate_today):
    """The menu writes '30-Jul' with no year; report._claimed_day parses
    RFC 822 or an ISO prefix and nothing else, so an unconverted menu date
    would silently date every vote by observation instead of by when the
    Senate actually voted."""
    from fapd import report

    _fmt, items = agencies.SenateVotesAdapter().items(VOTE_MENU, "text/xml")
    claimed = [i["claimed_date"] for i in items]
    assert claimed == ["2026-07-29", "2026-07-30"]
    assert [report._claimed_day({"claimed_published_at": c}) for c in claimed] \
        == ["2026-07-29", "2026-07-30"]


def test_vote_menu_urls_and_identity(senate_today):
    _fmt, items = agencies.SenateVotesAdapter().items(VOTE_MENU, "text/xml")
    latest = items[-1]
    assert latest["link"] == ("https://www.senate.gov/legislative/LIS/roll_call_votes/"
                              "vote1192/vote_119_2_00217.xml")
    assert latest["guid"] == "senate-vote-119-2-00217"


def test_unparsable_menu_is_disclosed_not_raised():
    """items() must not raise — the loop records 'unparsable' and discloses."""
    assert agencies.SenateVotesAdapter().items(b"<html>nope", "text/html") == (None, [])
    assert agencies.SenateVotesAdapter().items(b"<other/>", "text/xml") == (None, [])


def test_vote_record_extracts_tally_and_positions(senate_today):
    adapter = agencies.SenateVotesAdapter()
    _fmt, items = adapter.items(VOTE_MENU, "text/xml")
    item = items[-1]
    text = adapter.extract_text(VOTE_RECORD, "text/xml", item)
    assert "Result: Resolution Agreed to (2-1)" in text
    assert "Tally: Yea 2; Nay 1; Present 0; Not Voting 1" in text
    assert "Yea (2): Armstrong (R-OK), Banks (R-IN)" in text   # sorted roster
    assert "Not Voting (1): Alsobrooks (D-MD)" in text
    # structured fields reach metadata so the digest never re-parses prose
    assert item["extra"]["tally"] == {"Yea": 2, "Nay": 1, "Present": 0,
                                      "Not Voting": 1}
    assert item["extra"]["result"] == "Resolution Agreed to (2-1)"
    assert item["extra"]["chamber"] == "United States Senate"


def test_vote_record_mismatch_is_disclosed_not_reconciled(senate_today):
    """A published count that disagrees with the member list is reported as
    served, never silently corrected to whichever we prefer."""
    adapter = agencies.SenateVotesAdapter()
    _fmt, items = adapter.items(VOTE_MENU, "text/xml")
    skewed = VOTE_RECORD.replace(b"<yeas>2</yeas>", b"<yeas>9</yeas>")
    text = adapter.extract_text(skewed, "text/xml", items[-1])
    assert "the published count records 9 Yea, the member list 2" in text


def test_malformed_vote_record_degrades_the_item_not_the_source(senate_today):
    """extract_text may raise; the loop stores menu metadata instead, and
    fallback_text must never raise and never come back blank."""
    adapter = agencies.SenateVotesAdapter()
    _fmt, items = adapter.items(VOTE_MENU, "text/xml")
    with pytest.raises(ValueError):
        adapter.extract_text(b"<not_a_vote/>", "text/xml", items[-1])
    assert adapter.fallback_text(items[-1]).strip()


def test_senate_votes_ingest_stores_its_own_collection(env, senate_today):
    """Votes are legislative record: they must never land in AGENCYPR, whose
    accounting, dating rule and executive-branch tagging are not theirs."""
    import json as _json

    client, wb = FakeSenate(), FakeWayback()
    stats = agencies.poll_source(client, wb, env, senate_entry())
    assert stats["feed_status"] == "senate-vote-menu:2"
    assert stats["new_items"] == 2
    assert stats["articles_fetched"] == 2
    # one index fetch + one per in-window vote; nothing for the rest
    assert len(client.calls) == 3

    rows = env.execute(
        "SELECT collection, doc_type, title, text, char_count, metadata"
        " FROM extracted_texts ORDER BY package_id").fetchall()
    assert {r["collection"] for r in rows} == {"VOTES"}
    assert {r["doc_type"] for r in rows} == {"ROLLCALL"}
    assert env.execute(
        "SELECT COUNT(*) FROM packages WHERE collection='AGENCYPR'").fetchone()[0] == 0
    meta = _json.loads(rows[0]["metadata"])
    assert meta["mode"] == "full"
    assert meta["details"]["chamber"] == "United States Senate"
    assert meta["claimed_published_at"] in ("2026-07-29", "2026-07-30")
    assert "channel" not in meta  # collect.py keys web-vs-email on its absence
    assert rows[0]["char_count"] == len(rows[0]["text"]) > 0


# ---- Congress.gov bill actions (api adapter, GUIDE §3 bill actions) --------

# Shapes copied from the live payload fetched 2026-07-31: latestAction is
# the ONLY action exposed, and actionDate is unrelated to updateDate — a
# record updated today can describe an action from 2014.
BILL_PAYLOAD = json.dumps({
    "pagination": {"count": 429331},
    "bills": [
        {"congress": 119, "type": "S", "number": "3010",
         "title": "21st Century Dyslexia Act", "originChamber": "Senate",
         "updateDate": "2026-07-31",
         "url": "https://api.congress.gov/v3/bill/119/s/3010?format=json",
         "latestAction": {"actionDate": "2026-07-30",
                          "text": "Committee on Health, Education, Labor, and "
                                  "Pensions. Ordered to be reported."}},
        {"congress": 119, "type": "SJRES", "number": "199",
         "title": "A joint resolution providing for congressional disapproval.",
         "originChamber": "Senate", "updateDate": "2026-07-31",
         "latestAction": {"actionDate": "2026-07-29", "actionTime": "13:46:00",
                          "text": "Motion to proceed to consideration of measure "
                                  "rejected in Senate by Yea-Nay Vote. 47 - 52."}},
        {"congress": 119, "type": "HR", "number": "7831",
         "title": "License to Drill Act", "originChamber": "House",
         "updateDate": "2026-07-31",
         "latestAction": {"actionDate": "2026-07-29",
                          "text": "Committee on Energy and Natural Resources."}},
        # updated today, but the action is from 2014 — outside the window
        {"congress": 113, "type": "HR", "number": "83", "title": "An old bill.",
         "originChamber": "House", "updateDate": "2026-07-31",
         "latestAction": {"actionDate": "2014-07-16", "text": "Became Public Law."}},
        # a shape we cannot date: skipped, never dated by observation
        {"congress": 119, "type": "S", "number": "1", "title": "No date.",
         "latestAction": {"text": "Something happened."}},
    ],
}).encode()


class FakeCongress:
    def __init__(self, payload=BILL_PAYLOAD):
        self.payload, self.calls = payload, []

    def get(self, url, params=None, headers=None):
        self.calls.append({"url": url, "params": params})
        return Resp(self.payload, headers={"Content-Type": "application/json"},
                    url=url)


def congress_entry():
    return {"id": "congress-gov-api", "name": "Congress.gov API",
            "type": "api", "adapter": "congress-bill-actions",
            "urls": {"index": "https://api.congress.gov/v3/bill"}}


@pytest.fixture
def congress_today(monkeypatch):
    """Freeze the publication day and supply a key the adapter can read."""
    monkeypatch.setattr(agencies, "publication_date", lambda: "2026-07-31")
    monkeypatch.setenv("GOVINFO_API_KEY", "TESTKEY-abc123")


def test_bill_actions_are_bounded_and_dated_by_action_not_update(congress_today):
    """updateDate is when the RECORD changed; actionDate is when the thing
    happened. All five rows were updated today; only the three whose ACTION
    falls inside INDEX_LOOKBACK_DAYS come back."""
    fmt, items = agencies.CongressBillActionsAdapter().items(
        BILL_PAYLOAD, "application/json")
    assert fmt == "congress-bill-actions"
    assert [i["extra"]["designation"] for i in items] == [
        "H.R. 7831", "S.J.Res. 199", "S. 3010"]      # by action date, then type
    assert [i["claimed_date"] for i in items] == [
        "2026-07-29", "2026-07-29", "2026-07-30"]


def test_bill_action_identity_changes_only_when_the_action_does(congress_today):
    adapter = agencies.CongressBillActionsAdapter()
    _fmt, items = adapter.items(BILL_PAYLOAD, "application/json")
    guids = {i["extra"]["designation"]: i["guid"] for i in items}
    assert guids["S. 3010"] == "congress-action-119-s-3010:2026-07-30"
    moved = BILL_PAYLOAD.replace(b'"actionDate": "2026-07-30"',
                                 b'"actionDate": "2026-07-31"')
    _fmt, again = adapter.items(moved, "application/json")
    assert "congress-action-119-s-3010:2026-07-31" in {i["guid"] for i in again}


def test_bill_action_citation_is_the_public_bill_page(congress_today):
    """The API URL would demand a key; a citation is for a reader with a
    browser (GUIDE §2 cite everything)."""
    _fmt, items = agencies.CongressBillActionsAdapter().items(
        BILL_PAYLOAD, "application/json")
    links = {i["extra"]["designation"]: i["link"] for i in items}
    assert links["S. 3010"] == \
        "https://www.congress.gov/bill/119th-congress/senate-bill/3010"
    assert links["S.J.Res. 199"] == \
        "https://www.congress.gov/bill/119th-congress/senate-joint-resolution/199"


def test_ordinal_congress_numbers():
    assert [agencies._ordinal(n) for n in (111, 112, 113, 119, 121, 122, 123)] == \
        ["111th", "112th", "113th", "119th", "121st", "122nd", "123rd"]


def test_unparsable_bill_payload_is_disclosed_not_raised():
    """items() must not raise — the loop records 'unparsable' and discloses."""
    adapter = agencies.CongressBillActionsAdapter()
    assert adapter.items(b"<html>nope", "text/html") == (None, [])
    assert adapter.items(b'{"error": "no key"}', "application/json") == (None, [])


def test_bill_action_fallback_text_never_blank(congress_today):
    adapter = agencies.CongressBillActionsAdapter()
    _fmt, items = adapter.items(BILL_PAYLOAD, "application/json")
    text = adapter.fallback_text(items[-1])
    assert "S. 3010 — 21st Century Dyslexia Act" in text
    assert "Ordered to be reported" in text
    assert adapter.fallback_text({}).strip()      # must not raise on a bare item


def test_bill_actions_ingest_dated_by_publisher(env, congress_today):
    """The record publishes a day's actions the morning after; dating these
    by observation would file every one under a day nothing happened on."""
    client = FakeCongress()
    stats = agencies.poll_source(client, None, env, congress_entry())
    assert stats["feed_status"] == "congress-bill-actions:3"
    assert stats["new_items"] == 3
    assert stats["articles_fetched"] == 0          # wants_article() is False
    assert len(client.calls) == 1                  # one page, no article fetches

    # the key rides in params (where the client redacts it), never the URL
    assert client.calls[0]["url"] == "https://api.congress.gov/v3/bill"
    assert client.calls[0]["params"]["api_key"] == "TESTKEY-abc123"
    assert client.calls[0]["params"]["sort"] == "updateDate desc"

    rows = env.execute(
        "SELECT p.date_issued, e.collection, e.doc_type, e.metadata"
        " FROM extracted_texts e JOIN packages p USING (package_id)"
        " ORDER BY p.date_issued, e.package_id").fetchall()
    assert {r["collection"] for r in rows} == {"BILLACTIONS"}
    assert {r["doc_type"] for r in rows} == {"BILLACTION"}
    # filed under the day the chamber acted, not the day we polled (07-31)
    assert [r["date_issued"] for r in rows] == ["2026-07-29", "2026-07-29",
                                                "2026-07-30"]
    meta = json.loads(rows[-1]["metadata"])
    assert meta["mode"] == "feed-only"
    assert meta["details"]["action_text"].startswith("Committee on Health")
    assert "channel" not in meta  # collect.py keys web-vs-email on its absence


def test_publisher_dating_is_opt_in_per_adapter(env):
    """Agency releases keep the GUIDE §3 dating rule: they are filed under
    the day we observed them, whatever the feed claims."""
    assert agencies.SourceAdapter.DATED_BY_PUBLISHER is False
    assert agencies._issue_day({"claimed_date": "2020-01-01"}, False) \
        == agencies.publication_date()
    assert agencies._issue_day({"claimed_date": "2020-01-01"}, True) == "2020-01-01"
    # an unreadable claim falls back to observation, never to a guess
    assert agencies._issue_day({"claimed_date": "whenever"}, True) \
        == agencies.publication_date()
# ------------------------------------------- the html-index adapter (P5) --
#
# Fixtures are verbatim slices of the listing regions of the bytes those
# five publishers served on 2026-07-31, captured by the probe sweep and
# stored content-addressed under data/captures. Nothing in them is
# rewritten: an adapter tested against markup we invented would only be
# tested against our idea of what a listing page looks like, and the four
# shapes below (USWDS collection list, Drupal views rows, a date-headed
# grouping, and an HTML table) differ from each other more than any
# invented pair would have.

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "html_index"


def index_entry(source_id, url, **extra):
    return {"id": source_id, "name": source_id, "type": "html-index",
            "adapter": "html-index", "urls": {"index": url}, **extra}


def fixture(name):
    return (FIXTURES / f"{name}.html").read_bytes()


@pytest.fixture
def index_today(monkeypatch):
    """Freeze the publication day: the fixtures were served 2026-07-31, so
    the lookback window has to be evaluated as of that day forever."""
    monkeypatch.setattr(agencies, "publication_date", lambda: "2026-07-31")


def parse_fixture(name, url, **extra):
    adapter = agencies.HtmlIndexAdapter(index_entry(name, url, **extra))
    return adapter.items(fixture(name), "text/html; charset=utf-8")


def test_html_index_reads_a_uswds_collection_list(index_today):
    """dhs.gov: each entry is an <li> holding a <time datetime> and two
    links to the same release (calendar tile and headline)."""
    fmt, items = parse_fixture("dhs-newsroom", "https://www.dhs.gov/news-releases")
    assert fmt == "html-index"
    assert [i["claimed_date"] for i in items] == ["2026-07-31", "2026-07-30"]
    assert items[0]["title"] == ("DHS Announces the Addition of 43 Companies to"
                                " the UFLPA Entity List")
    assert items[0]["link"] == ("https://www.dhs.gov/news/2026/07/31/"
                                "dhs-announces-addition-43-companies-uflpa-entity-list")
    assert items[0]["extra"]["date_syntax"] == "time-attribute"
    # the listing's own teaser is the item's content: no article is fetched
    assert "Forced Labor Enforcement Task Force" in items[0]["description"]


def test_html_index_reads_drupal_views_rows(index_today):
    """fema.gov: title, body and a <time datetime> carrying a full
    timestamp, in three sibling divs rather than one nested block."""
    _fmt, items = parse_fixture(
        "fema-news", "https://www.fema.gov/about/news-multimedia/press-releases")
    assert [i["claimed_date"] for i in items] == ["2026-07-31", "2026-07-30",
                                                 "2026-07-30"]
    assert items[0]["extra"]["date_text"] == "2026-07-31T09:30:00Z"
    assert items[0]["description"].startswith("BATON ROUGE, La.")


def test_html_index_reads_a_table_and_us_slash_dates(index_today):
    """cftc.gov: a <table> whose date cell and link cell are siblings, and
    whose visible date is 07/31/2026 — read month-first, as a US federal
    publisher writing for a US audience."""
    _fmt, items = parse_fixture("cftc-press",
                               "https://www.cftc.gov/PressRoom/PressReleases")
    assert [i["claimed_date"] for i in items] == ["2026-07-31", "2026-07-30"]
    assert items[0]["link"].endswith("/PressRoom/PressReleases/9275-26")


def test_html_index_reads_prose_dates_and_drops_repeated_links(index_today):
    """ofac.treasury.gov: no <time> element anywhere — the day is prose,
    "July 30, 2026". Each entry also links the same "Sanctions List
    Updates" category page from inside its own block, otherwise
    indistinguishable from a release; it is dropped for repeating."""
    _fmt, items = parse_fixture("ofac-recent-actions",
                               "https://ofac.treasury.gov/recent-actions")
    assert [i["claimed_date"] for i in items] == ["2026-07-30", "2026-07-29",
                                                 "2026-07-27"]
    assert all(i["extra"]["date_syntax"] == "month-day-year" for i in items)
    assert not any("sanctions-list-updates" in i["link"] for i in items)


def test_html_index_drops_undated_entries_rather_than_dating_them(index_today):
    """THE FAILURE THIS ADAPTER EXISTS TO AVOID. nrc.gov's news index is a
    menu of year archives: many links, and exactly one date on the page —
    "Page Last Reviewed/Updated Tuesday, January 06, 2026" in the footer.
    A nearest-date parser would stamp that day onto every link. Dating them
    by observation instead would be worse: they would enter the digest as
    today's news and AGENCYPR-EX-01 could not exclude them, because their
    claimed day would equal the digest day. The honest answer is no items."""
    fmt, items = parse_fixture("nrc-news",
                              "https://www.nrc.gov/reading-rm/doc-collections/news/")
    assert fmt == "html-index"          # parsed fine; it just states no entries
    assert items == []


def test_html_index_lookback_bounds_what_a_listing_can_cost(index_today, monkeypatch):
    """An index is not a feed: it reaches back months. Bounded to the
    current day, the same FEMA listing yields only that day's releases."""
    monkeypatch.setattr(config, "INDEX_LOOKBACK_DAYS", 0)
    _fmt, items = parse_fixture(
        "fema-news", "https://www.fema.gov/about/news-multimedia/press-releases")
    assert [i["claimed_date"] for i in items] == ["2026-07-31"]


def test_html_index_item_path_hint_filters_to_the_release_section(index_today):
    """The one per-source hint is a URL path prefix, and it is a filter:
    a prefix that matches nothing must leave nothing, not everything."""
    _fmt, items = parse_fixture("dhs-newsroom", "https://www.dhs.gov/news-releases",
                                index_item_path="/news/2026/07/31/")
    assert [i["claimed_date"] for i in items] == ["2026-07-31"]
    _fmt, none = parse_fixture("dhs-newsroom", "https://www.dhs.gov/news-releases",
                               index_item_path="/nothing-here/")
    assert none == []


def test_html_index_identity_is_the_normalized_url(index_today):
    """These sources start with no history, so identity normalizes from the
    first poll (GUIDE §7 T5) — but the query string is kept, because some
    listings identify an entry only by ?id=."""
    adapter = agencies.HtmlIndexAdapter(index_entry("x", "https://x.gov/news"))
    assert adapter.stable_id({"link": "HTTPS://X.GOV/News/a/#top"}) \
        == "https://x.gov/News/a"
    assert adapter.stable_id({"link": "https://x.gov/n?id=7"}) == "https://x.gov/n?id=7"
    # guid wins when items() set one, so identity survives a link rewrite
    assert adapter.stable_id({"guid": "g", "link": "https://x.gov/z"}) == "g"


def test_html_index_never_raises_and_never_fetches_articles(index_today):
    """items(), stable_id() and fallback_text() run before any storage
    exists, so none of them may raise; wants_article() is False by design."""
    adapter = agencies.HtmlIndexAdapter(index_entry("x", "https://x.gov/news"))
    assert adapter.wants_article() is False
    assert adapter.items(b"\xff\xfe not html at all", "text/html") == ("html-index", [])
    assert adapter.items(b"<div><a href='/a'>", "text/html") == ("html-index", [])
    assert adapter.fallback_text({"title": "T", "description": "D"}) == "T — D"
    assert adapter.fallback_text({"link": "https://x.gov/a"}) == "https://x.gov/a"


def test_html_index_dates_are_iso_so_the_digest_can_read_them(index_today):
    """report._claimed_day parses RFC 822 or an ISO prefix and nothing
    else. "July 30, 2026" straight off the page would be unreadable to it,
    and the item would be dated by observation — the exact lie this
    adapter refuses to tell."""
    from fapd import report

    _fmt, items = parse_fixture("ofac-recent-actions",
                               "https://ofac.treasury.gov/recent-actions")
    assert [report._claimed_day({"claimed_published_at": i["claimed_date"]})
            for i in items] == ["2026-07-30", "2026-07-29", "2026-07-27"]


def test_html_index_date_syntaxes_are_locale_independent():
    """strptime('%b') reads LC_TIME; a month table does not. Every syntax
    seen across the 33 captured listings, read the same on any machine."""
    assert agencies._find_dates("July 30, 2026")[0][0] == dt.date(2026, 7, 30)
    assert agencies._find_dates("Jul. 30, 2026")[0][0] == dt.date(2026, 7, 30)
    assert agencies._find_dates("Sept 3, 2026")[0][0] == dt.date(2026, 9, 3)
    assert agencies._find_dates("30 July 2026")[0][0] == dt.date(2026, 7, 30)
    assert agencies._find_dates("2026-07-30")[0][0] == dt.date(2026, 7, 30)
    assert agencies._find_dates("07/30/2026")[0][0] == dt.date(2026, 7, 30)
    assert agencies._find_dates("7/30/26")[0][0] == dt.date(2026, 7, 30)
    # not a date: no year, an impossible day, a version-looking string
    assert agencies._find_dates("Jul 30") == []
    assert agencies._find_dates("February 31, 2026") == []
    assert agencies._find_dates("release 13/45/2026") == []


def test_html_index_ingest_stores_agency_releases_feed_only(env, index_today):
    """End to end through the shared loop: one request for the listing and
    none for the entries, AGENCYPR collection, mode disclosed as feed-only."""
    import json as _json

    class FakeIndex:
        def __init__(self):
            self.calls = []

        def get(self, url, params=None, headers=None):
            self.calls.append(url)
            return Resp(fixture("fema-news"),
                        headers={"Content-Type": "text/html; charset=utf-8"})

    entry = {**index_entry(
        "fema-news", "https://www.fema.gov/about/news-multimedia/press-releases"),
        "name": "FEMA"}
    client = FakeIndex()
    stats = agencies.poll_source(client, FakeWayback(), env, entry)
    assert stats["feed_status"] == "html-index:3"
    assert stats["new_items"] == 3
    assert stats["articles_fetched"] == 0
    assert len(client.calls) == 1        # the listing, and nothing else

    rows = env.execute(
        "SELECT collection, doc_type, title, text, metadata FROM extracted_texts"
        " ORDER BY package_id").fetchall()
    assert {r["collection"] for r in rows} == {"AGENCYPR"}
    assert {r["doc_type"] for r in rows} == {"PRESS"}
    metas = [_json.loads(r["metadata"]) for r in rows]
    assert {m["mode"] for m in metas} == {"feed-only"}
    assert all(m["claimed_published_at"].startswith("2026-07-3") for m in metas)
    assert all("channel" not in m for m in metas)   # collect.py keys on absence
    assert all(m["details"]["date_syntax"] == "time-attribute" for m in metas)
    assert all(r["text"].strip() for r in rows)

    # a second poll ingests nothing: identity is the normalized URL
    assert agencies.poll_source(client, FakeWayback(), env, entry)["new_items"] == 0

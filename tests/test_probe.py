"""Probe tests: feed parsing, autodiscovery, sample-article chain, error
recording. Fake client; provenance goes to tmp paths."""

import json

import pytest

from fapd import config, db, probe

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>N</title>
<item><title>Release One</title><link>https://x.gov/one</link>
<guid>g1</guid><pubDate>Sat, 25 Jul 2026 10:00:00 GMT</pubDate>
<description>Summary text here</description></item>
<item><title>Release Two</title><link>https://x.gov/two</link>
<guid>g2</guid><pubDate>Fri, 24 Jul 2026 10:00:00 GMT</pubDate>
<description>More text</description></item></channel></rss>"""

HTML_WITH_FEED = (b'<html><head><link rel="alternate" type="application/rss+xml"'
                  b' href="/newsroom/feed.xml"></head><body>News index</body></html>')

ARTICLE = b"<html><body><article>Full press release body text.</article></body></html>"


class Resp:
    def __init__(self, body, ctype, status=200, url=None):
        self.content = body
        self.status_code = status
        self.headers = {"Content-Type": ctype}
        self.url = url


class FakeAgencyClient:
    def __init__(self, responses):
        self.responses = responses  # url -> Resp | Exception
        self.calls = []

    def get(self, url, params=None, headers=None):
        self.calls.append(url)
        r = self.responses[url]
        if isinstance(r, Exception):
            raise r
        return r


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CAPTURE_DIR", tmp_path / "captures")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    conn = db.connect(tmp_path / "meta.db")
    yield conn
    conn.close()


def entry(id="doj", type="rss", urls=None):
    return {"id": id, "type": type,
            "urls": urls or {"feed": "https://x.gov/feed.xml"}}


def test_feed_probe_full_chain(env):
    client = FakeAgencyClient({
        "https://x.gov/feed.xml": Resp(RSS, "application/rss+xml"),
        "https://x.gov/one": Resp(ARTICLE, "text/html"),
    })
    f = probe.probe_source(client, env, entry())
    assert f["verdict"] == "feed-ok"
    assert f["feed"]["format"] == "rss" and f["feed"]["items"] == 2
    assert f["feed"]["with_guid"] == 2
    assert f["sample_item"]["text_chars"] > 10
    assert "Full press release body" in f["sample_item"]["text_head"]
    # Everything captured through provenance
    n = env.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
    assert n == 2  # feed + article


def test_html_autodiscovery(env):
    client = FakeAgencyClient({
        "https://x.gov/news": Resp(HTML_WITH_FEED, "text/html",
                                   url="https://x.gov/news"),
        "https://x.gov/newsroom/feed.xml": Resp(RSS, "application/xml"),
        "https://x.gov/one": Resp(ARTICLE, "text/html"),
    })
    f = probe.probe_source(client, env,
                           entry(type="html-index", urls={"index": "https://x.gov/news"}))
    assert f["autodiscovered_feed"] == "https://x.gov/newsroom/feed.xml"
    assert f["verdict"] == "feed-ok"


def test_http_error_recorded_not_raised(env):
    import requests

    class R:  # minimal response carrier for HTTPError
        status_code = 403

    client = FakeAgencyClient({
        "https://x.gov/feed.xml": requests.HTTPError("HTTP 403", response=R()),
    })
    f = probe.probe_source(client, env, entry())
    assert f["verdict"] == "http_error"
    assert f["fetches"][0]["status"] == 403
    row = env.execute("SELECT change_kind FROM captures").fetchone()
    assert row["change_kind"] == "error"  # absence asserted in provenance


def test_run_isolates_crashes_and_writes_summary(env, tmp_path):
    class Exploding:
        def get(self, url, **kw):
            raise ValueError("boom")

    _out, summary = probe.run(Exploding(), env, [entry()], out_dir=tmp_path / "p")
    assert summary[0]["verdict"] == "probe-crash"
    data = json.loads((tmp_path / "p" / "doj.json").read_text())
    assert "boom" in data["error"]

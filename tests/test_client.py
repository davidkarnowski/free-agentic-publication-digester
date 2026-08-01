"""Tests for the rate-limited client. No network: HTTP session and clock are
faked, and the fetch-log DB goes to a tmp path."""

import pytest

from fapd import config
from fapd.client import BudgetExceededError, GovinfoClient, RateLimitFloorError


class FakeResponse:
    def __init__(self, status=200, headers=None, body=b'{"ok": true}'):
        self.status_code = status
        self.headers = headers or {}
        self.content = body

    @property
    def text(self):
        return self.content.decode("utf-8", errors="replace")

    def json(self):
        import json

        return json.loads(self.content)

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": params, "headers": headers})
        return self.responses.pop(0)

    def close(self):
        pass


class FakeClock:
    """Deterministic monotonic clock; sleep() advances it and records calls."""

    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.t

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.t += seconds


@pytest.fixture(autouse=True)
def _test_key(monkeypatch):
    monkeypatch.setenv("GOVINFO_API_KEY", "TESTKEY-abc123")


def make_client(tmp_path, responses):
    clock = FakeClock()
    session = FakeSession(responses)
    client = GovinfoClient(
        db_path=tmp_path / "fetch_log.db",
        session=session,
        sleep=clock.sleep,
        monotonic=clock.monotonic,
    )
    return client, session, clock


def test_paces_consecutive_requests_to_one_per_second(tmp_path):
    client, _, clock = make_client(tmp_path, [FakeResponse(), FakeResponse()])
    client.get("collections")
    client.get("collections")
    assert clock.sleeps == [pytest.approx(1.0 / config.MAX_REQUESTS_PER_SECOND)]


def test_daily_budget_enforced_from_persistent_log(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EOD_BUDGET_RESERVE_FRACTION", 0.0)
    monkeypatch.setattr(config, "MAX_REQUESTS_PER_DAY", 2)
    client, _, _ = make_client(tmp_path, [FakeResponse(), FakeResponse(), FakeResponse()])
    client.get("collections")
    client.get("collections")
    with pytest.raises(BudgetExceededError):
        client.get("collections")
    # Budget survives a "restart": a new client over the same DB still refuses.
    client2 = GovinfoClient(db_path=tmp_path / "fetch_log.db", session=FakeSession([]))
    with pytest.raises(BudgetExceededError):
        client2.get("collections")


def test_retry_after_header_honored_exactly(tmp_path):
    client, _, clock = make_client(
        tmp_path, [FakeResponse(503, headers={"Retry-After": "7"}), FakeResponse()]
    )
    resp = client.get("packages/CREC-2026-07-23/summary")
    assert resp.status_code == 200
    assert 7.0 in clock.sleeps


def test_5xx_exponential_backoff_then_success(tmp_path):
    client, session, clock = make_client(
        tmp_path, [FakeResponse(500), FakeResponse(500), FakeResponse()]
    )
    resp = client.get("collections")
    assert resp.status_code == 200
    assert len(session.calls) == 3
    backoffs = [s for s in clock.sleeps if s != 1.0]  # exclude pacing sleeps
    assert backoffs == [2.0, 4.0]


def test_gives_up_after_max_attempts(tmp_path):
    client, session, _ = make_client(tmp_path, [FakeResponse(500)] * config.MAX_ATTEMPTS)
    import requests

    with pytest.raises(requests.HTTPError, match="HTTP 500"):
        client.get("collections")
    assert len(session.calls) == config.MAX_ATTEMPTS


def test_api_key_never_appears_in_fetch_log(tmp_path):
    client, _, _ = make_client(tmp_path, [FakeResponse()])
    client.get("collections", params={"pageSize": 10})
    rows = client._db.execute("SELECT url FROM fetch_log").fetchall()
    assert rows, "expected the request to be logged"
    for (url,) in rows:
        assert "TESTKEY" not in url
        assert "pageSize=10" in url  # non-secret params ARE logged


def test_api_key_redaction_is_the_base_clients_rule(tmp_path):
    """Not a govinfo-only concern: the agency client began carrying an
    api.data.gov key on 2026-07-31 (Congress.gov), and GUIDE §4 says the
    key is never in the log whichever client sends it."""
    from fapd.client import AgencyClient, HttpClient

    for cls in (HttpClient, AgencyClient):
        shown = cls._redacted_params(
            object.__new__(cls), {"api_key": "TESTKEY-abc123", "limit": 250})
        assert shown == {"limit": 250}


def test_every_attempt_is_logged(tmp_path):
    client, _, _ = make_client(tmp_path, [FakeResponse(500), FakeResponse()])
    client.get("collections")
    (n,) = client._db.execute("SELECT COUNT(*) FROM fetch_log").fetchone()
    assert n == 2
    assert client.requests_today() == 2


def test_halts_when_server_remaining_below_floor(tmp_path):
    low = str(config.MIN_SERVER_REMAINING - 1)
    client, _, _ = make_client(
        tmp_path,
        [FakeResponse(headers={"X-RateLimit-Remaining": low}), FakeResponse()],
    )
    resp = client.get("collections")  # the triggering response is still returned
    assert resp.status_code == 200
    with pytest.raises(RateLimitFloorError):
        client.get("collections")


def test_paginate_follows_next_page_and_strips_echoed_key(tmp_path):
    page1 = b'{"packages": [1], "nextPage": "https://api.govinfo.gov/collections/CREC?offsetMark=AAA&pageSize=100&api_key=ECHOED"}'
    page2 = b'{"packages": [2]}'
    client, session, _ = make_client(
        tmp_path, [FakeResponse(body=page1), FakeResponse(body=page2)]
    )
    pages = list(client.paginate("collections/CREC"))
    assert len(pages) == 2
    second_call = session.calls[1]
    assert second_call["params"]["offsetMark"] == "AAA"
    assert second_call["params"]["api_key"] == "TESTKEY-abc123"  # ours, not the echoed one
    assert "ECHOED" not in str(second_call["params"].values())


def test_user_agent_sent(tmp_path):
    client, session, _ = make_client(tmp_path, [FakeResponse()])
    client.get("collections")
    assert session.calls[0]["headers"]["User-Agent"].startswith("fapd/")


# ---------------------------------------------------------------------------
# HttpClient base extensions + AgencyClient (sources expansion)
# ---------------------------------------------------------------------------

from fapd.client import AgencyClient, RobotsDisallowedError


def make_agency(tmp_path, responses):
    clock = FakeClock()
    session = FakeSession(responses)
    client = AgencyClient(
        db_path=tmp_path / "fetch_log.db", session=session,
        sleep=clock.sleep, monotonic=clock.monotonic,
    )
    return client, session, clock


def robots_resp(body, status=200):
    return FakeResponse(status=status, body=body.encode(), headers={})


def test_budget_buckets_are_separate(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EOD_BUDGET_RESERVE_FRACTION", 0.0)
    monkeypatch.setattr(config, "MAX_REQUESTS_PER_DAY", 1)
    monkeypatch.setattr(config, "MAX_AGENCY_REQUESTS_PER_DAY", 3)
    gov = GovinfoClient(db_path=tmp_path / "fetch_log.db",
                        session=FakeSession([FakeResponse()]))
    gov.get("collections")  # govinfo bucket now full (1/1)
    agency, _, _ = make_agency(
        tmp_path,
        [robots_resp("User-agent: *\nAllow: /"), FakeResponse()],
    )
    resp = agency.get("https://example.gov/news/item")  # must NOT be blocked
    assert resp.status_code == 200
    assert gov.requests_today() == 1
    assert agency.requests_today() == 2  # robots fetch + page fetch


def test_legacy_null_client_rows_count_as_govinfo(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "EOD_BUDGET_RESERVE_FRACTION", 0.0)
    monkeypatch.setattr(config, "MAX_REQUESTS_PER_DAY", 2)
    import datetime as dt
    import sqlite3

    db = sqlite3.connect(tmp_path / "fetch_log.db")
    db.execute("CREATE TABLE fetch_log (id INTEGER PRIMARY KEY, ts_utc TEXT NOT NULL,"
               " url TEXT NOT NULL, status INTEGER, bytes INTEGER NOT NULL DEFAULT 0,"
               " elapsed_ms INTEGER, attempt INTEGER NOT NULL, error TEXT)")
    db.execute("INSERT INTO fetch_log (ts_utc, url, attempt) VALUES (?, 'x', 1)",
               (dt.datetime.now(dt.UTC).isoformat(),))
    db.commit(); db.close()
    gov = GovinfoClient(db_path=tmp_path / "fetch_log.db",
                        session=FakeSession([FakeResponse(), FakeResponse()]))
    assert gov.requests_today() == 1  # pre-migration row counted for govinfo
    gov.get("collections")
    with pytest.raises(BudgetExceededError):
        gov.get("collections")  # 2/2 reached incl. legacy row


def test_robots_disallow_blocks_and_logs(tmp_path):
    client, session, _ = make_agency(
        tmp_path, [robots_resp("User-agent: *\nDisallow: /news/")]
    )
    with pytest.raises(RobotsDisallowedError):
        client.get("https://example.gov/news/item")
    assert len(session.calls) == 1  # only robots.txt was fetched
    rows = client._db.execute(
        "SELECT url, error FROM fetch_log ORDER BY id"
    ).fetchall()
    assert rows[-1][1] == "robots disallowed"


def test_robots_404_treated_as_allow(tmp_path):
    client, _, _ = make_agency(
        tmp_path,
        [FakeResponse(status=404, body=b"nope"), FakeResponse()],
    )
    assert client.get("https://example.gov/news/item").status_code == 200


def test_robots_cached_across_requests(tmp_path):
    client, session, _ = make_agency(
        tmp_path,
        [robots_resp("User-agent: *\nAllow: /"), FakeResponse(), FakeResponse()],
    )
    client.get("https://example.gov/a")
    client.get("https://example.gov/b")
    robots_fetches = [c for c in session.calls if "robots.txt" in c["url"]]
    assert len(robots_fetches) == 1


def test_conditional_get_304_returned(tmp_path):
    client, session, _ = make_agency(
        tmp_path,
        [robots_resp("User-agent: *\nAllow: /"),
         FakeResponse(status=304, body=b"")],
    )
    resp = client.get("https://example.gov/feed.xml",
                      headers={"If-None-Match": '"abc"'})
    assert resp.status_code == 304
    assert session.calls[-1]["headers"]["If-None-Match"] == '"abc"'


def test_retry_after_http_date_form(tmp_path):
    import datetime as dt
    import email.utils

    when = email.utils.format_datetime(
        dt.datetime.now(dt.UTC) + dt.timedelta(seconds=90)
    )
    client, _, clock = make_client(
        tmp_path, [FakeResponse(503, headers={"Retry-After": when}), FakeResponse()]
    )
    client.get("collections")
    assert any(80 <= s <= 91 for s in clock.sleeps)  # honored the date form


def test_collectors_stop_short_of_the_finalizer_reserve(tmp_path, monkeypatch):
    """2026-07-30: collectors spent all 2,000 govinfo requests on backlog
    and the finalizer could not sync the day it was finalizing. The
    reserve is the fix — collectors see a smaller budget than the
    finalizer does."""
    monkeypatch.setattr(config, "MAX_REQUESTS_PER_DAY", 10)
    monkeypatch.setattr(config, "EOD_BUDGET_RESERVE_FRACTION", 0.2)
    collector, _, _ = make_client(tmp_path, [FakeResponse() for _ in range(12)])
    assert collector._effective_daily_budget() == 8      # 10 - 20%
    for _ in range(8):
        collector.get("collections")
    with pytest.raises(BudgetExceededError):
        collector.get("collections")

    # the finalizer may spend into the reserve the collectors were kept out of
    finalizer = GovinfoClient(db_path=tmp_path / "fetch_log.db",
                              session=FakeSession([FakeResponse()]),
                              sleep=lambda s: None, reserve_exempt=True)
    assert finalizer._effective_daily_budget() == 10
    finalizer.get("collections")                          # 9th — allowed


def test_hourly_ceiling_keeps_us_far_from_the_documented_limit(tmp_path,
                                                               monkeypatch):
    """api.data.gov documents 1,000 requests/hour and answers 429 above
    it. Our ceiling is half that, enforced from the fetch log so it holds
    across processes — it is what makes a larger daily budget safe."""
    monkeypatch.setattr(config, "MAX_GOVINFO_REQUESTS_PER_HOUR", 3)
    monkeypatch.setattr(config, "EOD_BUDGET_RESERVE_FRACTION", 0.0)
    client, _, _ = make_client(tmp_path, [FakeResponse() for _ in range(5)])
    for _ in range(3):
        client.get("collections")
    with pytest.raises(BudgetExceededError, match="hourly ceiling"):
        client.get("collections")
    # the ceiling binds the finalizer too: it is the publisher's limit,
    # not ours, and no reserve exempts anyone from it
    finalizer = GovinfoClient(db_path=tmp_path / "fetch_log.db",
                              session=FakeSession([FakeResponse()]),
                              sleep=lambda s: None, reserve_exempt=True)
    with pytest.raises(BudgetExceededError, match="hourly ceiling"):
        finalizer.get("collections")


def test_robots_cache_survives_a_new_client(tmp_path, monkeypatch):
    """F-007: the cache lived on the instance while the collector builds a
    fresh client every cycle, so a 24-hour TTL never survived one poll.
    At hourly polling that is 528 robots fetches a day where 22 will do."""
    monkeypatch.setattr(config, "EOD_BUDGET_RESERVE_FRACTION", 0.0)
    responses = [robots_resp("User-agent: *\nAllow: /"), FakeResponse(),
                 FakeResponse()]
    first, _, _ = make_agency(tmp_path, responses)
    first.get("https://x.gov/a")
    fetched_by_first = [c for c in first._session.calls
                        if "robots" in c["url"]]
    assert len(fetched_by_first) == 1

    # a second client over the same fetch-log DB must NOT re-ask
    second = AgencyClient(db_path=tmp_path / "fetch_log.db",
                          session=FakeSession([FakeResponse()]),
                          sleep=lambda s: None)
    second.get("https://x.gov/b")
    assert not [c for c in second._session.calls
                if "robots" in c["url"]], \
        "the second client re-fetched robots.txt the first already cached"
    second.close()


def test_a_temporary_disallow_is_not_persisted(tmp_path, monkeypatch):
    """A 5xx is a statement about this moment, not about the host —
    caching it for 24 hours would outlive the outage and lock us out."""
    import requests as _requests

    monkeypatch.setattr(config, "EOD_BUDGET_RESERVE_FRACTION", 0.0)
    class DownSession:
        def __init__(self):
            self.calls = []

        def get(self, url, params=None, headers=None, timeout=None):
            raise _requests.ConnectionError("host down")

    client = AgencyClient(db_path=tmp_path / "fetch_log.db",
                          session=DownSession(), sleep=lambda s: None)
    with pytest.raises(RobotsDisallowedError):
        client.get("https://y.gov/a")
    row = client._db.execute(
        "SELECT COUNT(*) FROM robots_cache WHERE host = 'y.gov'").fetchone()
    assert row[0] == 0, "a temporary disallow must not be cached"

"""Tests for the rate-limited client. No network: HTTP session and clock are
faked, and the fetch-log DB goes to a tmp path."""

import pytest

from info_intel import config
from info_intel.client import BudgetExceededError, GovinfoClient, RateLimitFloorError


class FakeResponse:
    def __init__(self, status=200, headers=None, body=b'{"ok": true}'):
        self.status_code = status
        self.headers = headers or {}
        self.content = body

    def json(self):
        import json

        return json.loads(self.content)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


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
    with pytest.raises(RuntimeError, match="HTTP 500"):
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
    assert session.calls[0]["headers"]["User-Agent"].startswith("info-intel/")

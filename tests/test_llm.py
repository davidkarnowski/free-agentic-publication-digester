"""LLM client tests: ledger recording, token accounting, failure paths.
The claude CLI is faked via an injected runner; the Anthropic SDK via an
injected fake client — no monkeypatching of either backend's internals."""

import json
import sqlite3
from types import SimpleNamespace

import pytest

from fapd import config, llm
from fapd.llm import AnthropicBackend, CLIBackend, LLMClient, LLMError


class FakeProc:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def cli_json(text="a summary", inp=100, out=20):
    return json.dumps({
        "type": "result",
        "result": text,
        "usage": {"input_tokens": inp, "output_tokens": out,
                  "cache_read_input_tokens": 5, "cache_creation_input_tokens": 3},
    })


def make_client(tmp_path, procs):
    calls = []

    def runner(cmd, **kwargs):
        calls.append({"cmd": cmd, "input": kwargs.get("input")})
        return procs.pop(0)

    client = LLMClient(db_path=tmp_path / "ledger.db", runner=runner)
    return client, calls


def test_complete_returns_text_and_logs_tokens(tmp_path):
    client, calls = make_client(tmp_path, [FakeProc(stdout=cli_json())])
    r = client.complete("summarize this", purpose="map:test", package_id="P1")
    assert r["text"] == "a summary"
    assert r["input_tokens"] == 108  # input + cache read + cache creation
    assert r["output_tokens"] == 20
    assert calls[0]["input"] == "summarize this"
    assert "--output-format" in calls[0]["cmd"]
    inp, out, n = client.tokens_today()
    assert (inp, out, n) == (108, 20, 1)


def test_cli_failure_is_logged_and_raises(tmp_path):
    client, _ = make_client(tmp_path, [FakeProc(stderr="boom", returncode=1)])
    with pytest.raises(LLMError):
        client.complete("x", purpose="map:test")
    row = client._db.execute("SELECT error, input_tokens FROM llm_calls").fetchone()
    assert row[0] == "boom" and row[1] == 0


def test_ledger_accumulates_across_calls(tmp_path):
    client, _ = make_client(
        tmp_path, [FakeProc(stdout=cli_json(inp=1000, out=50)),
                   FakeProc(stdout=cli_json(inp=2000, out=70))]
    )
    client.complete("a", purpose="map:1")
    client.complete("b", purpose="map:2")
    inp, out, n = client.tokens_today()
    assert n == 2 and inp == 1008 + 2008 and out == 120


def test_model_selection(tmp_path):
    client, calls = make_client(tmp_path, [FakeProc(stdout=cli_json())])
    client.complete("x", purpose="compose", model="opus")
    assert calls[0]["cmd"][calls[0]["cmd"].index("--model") + 1] == "opus"


# ---- API backend (fake SDK client, constructor-injected)


def api_response(text="api summary", stop_reason="end_turn"):
    return SimpleNamespace(
        stop_reason=stop_reason,
        content=[SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=100, output_tokens=20,
                              cache_read_input_tokens=5,
                              cache_creation_input_tokens=3),
    )


class FakeAnthropic:
    def __init__(self, responses=None, error=None):
        self.calls = []
        self._responses = responses or []
        self._error = error
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        return self._responses.pop(0)


def make_api_client(tmp_path, **fake_kwargs):
    fake = FakeAnthropic(**fake_kwargs)
    client = LLMClient(db_path=tmp_path / "ledger.db",
                       backend=AnthropicBackend(client=fake))
    return client, fake


def test_api_backend_resolves_tier_and_ledgers_backend(tmp_path):
    client, fake = make_api_client(tmp_path, responses=[api_response()])
    r = client.complete("summarize", purpose="map:test", model=config.MAP_MODEL)
    assert fake.calls[0]["model"] == config.LLM_MODELS["api"]["haiku"]
    assert fake.calls[0]["max_tokens"] == config.LLM_MAX_OUTPUT_TOKENS
    assert r["text"] == "api summary"
    assert r["input_tokens"] == 108  # input + cache read + cache creation
    assert r["model"] == config.LLM_MODELS["api"]["haiku"]  # resolved, not the alias
    row = client._db.execute("SELECT backend, model FROM llm_calls").fetchone()
    assert row == ("api", config.LLM_MODELS["api"]["haiku"])


def test_api_failure_is_ledgered_and_raises(tmp_path):
    client, _ = make_api_client(tmp_path, error=RuntimeError("api down"))
    with pytest.raises(LLMError):
        client.complete("x", purpose="map:test")
    row = client._db.execute(
        "SELECT backend, error, input_tokens FROM llm_calls").fetchone()
    assert row[0] == "api" and "api down" in row[1] and row[2] == 0


def test_api_refusal_is_ledgered_and_raises(tmp_path):
    client, _ = make_api_client(
        tmp_path, responses=[api_response(stop_reason="refusal")])
    with pytest.raises(LLMError, match="refusal"):
        client.complete("x", purpose="map:test")
    row = client._db.execute("SELECT error FROM llm_calls").fetchone()
    assert "refusal" in row[0]


def test_concrete_model_id_passes_through_unresolved(tmp_path):
    # A name outside the tier table is a deliberate pin, not an error.
    client, fake = make_api_client(tmp_path, responses=[api_response()])
    client.complete("x", purpose="compose", model="claude-sonnet-5")
    assert fake.calls[0]["model"] == "claude-sonnet-5"


def test_backend_selected_from_config(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LLM_BACKEND", "cli")
    assert isinstance(LLMClient(db_path=tmp_path / "a.db")._backend, CLIBackend)

    created = []
    monkeypatch.setattr(llm, "AnthropicBackend",
                        lambda: created.append(True) or SimpleNamespace(name="api"))
    monkeypatch.setattr(config, "LLM_BACKEND", "api")
    LLMClient(db_path=tmp_path / "b.db")
    assert created == [True]


def test_ledger_migrates_pre_backend_schema(tmp_path):
    # A ledger created before 2026-07-30 lacks the backend column; opening
    # it must add the column without losing rows.
    db_path = tmp_path / "old.db"
    old = sqlite3.connect(db_path)
    old.executescript("""
        CREATE TABLE llm_calls (
            id INTEGER PRIMARY KEY, ts_utc TEXT NOT NULL, model TEXT NOT NULL,
            purpose TEXT NOT NULL, package_id TEXT, granule_id TEXT,
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            duration_ms INTEGER, error TEXT);
        INSERT INTO llm_calls (ts_utc, model, purpose, input_tokens, output_tokens)
        VALUES ('2026-07-29T12:00:00.000', 'haiku', 'map:old', 500, 40);
    """)
    old.commit()
    old.close()

    client = LLMClient(db_path=db_path,
                       runner=lambda *a, **kw: FakeProc(stdout=cli_json()))
    client.complete("new call", purpose="map:new")
    rows = client._db.execute(
        "SELECT purpose, backend FROM llm_calls ORDER BY id").fetchall()
    assert rows == [("map:old", "cli"), ("map:new", "cli")]


def test_throttle_unset_means_unlimited(tmp_path):
    # The default: DAILY_TOKEN_THROTTLE is None and no start gate fires.
    assert config.DAILY_TOKEN_THROTTLE is None
    client, calls = make_client(tmp_path, [FakeProc(stdout=cli_json())])
    client.complete("x", purpose="map:test")
    assert len(calls) == 1


def test_throttle_pauses_at_the_ledger_figure(tmp_path, monkeypatch):
    """GUIDE §6 r8 (operator, 2026-08-02): the on-demand throttle. Counted
    from the ledger — the fetch-log budget pattern — and it gates call
    STARTS: the call that crosses the figure completes; the next refuses."""
    monkeypatch.setattr(config, "DAILY_TOKEN_THROTTLE", 200)
    client, calls = make_client(
        tmp_path, [FakeProc(stdout=cli_json(inp=250)), FakeProc(stdout=cli_json())])
    client.complete("first", purpose="map:test")   # 258 in-tokens logged
    with pytest.raises(llm.TokenBudgetExceededError):
        client.complete("second", purpose="map:test")
    assert len(calls) == 1, "the backend must not be reached once throttled"


def test_throttle_error_is_the_pause_kind(tmp_path):
    """Worker.run_cycle records BudgetExceededError as paused-not-failed;
    the throttle must ride that path, not the error streak."""
    from fapd.client import BudgetExceededError

    assert issubclass(llm.TokenBudgetExceededError, BudgetExceededError)


def test_throttle_counts_across_clients_via_the_ledger(tmp_path, monkeypatch):
    """Enforcement is cross-process by construction: a second client over
    the same ledger sees the first client's spend."""
    monkeypatch.setattr(config, "DAILY_TOKEN_THROTTLE", 100)
    first, _ = make_client(tmp_path, [FakeProc(stdout=cli_json(inp=250))])
    first.complete("x", purpose="map:test")
    second, calls = make_client(tmp_path, [FakeProc(stdout=cli_json())])
    with pytest.raises(llm.TokenBudgetExceededError):
        second.complete("y", purpose="map:test")
    assert not calls


def test_prompt_size_guard_fails_loudly_and_is_ledgered(tmp_path, monkeypatch):
    """Review R1/D3: one call must never carry an unbounded prompt. The
    refusal is ledgered (nothing bypasses logging) and raises an LLMError
    so the r14/R3 ceilings bound any retries."""
    monkeypatch.setattr(config, "LLM_MAX_PROMPT_CHARS", 50)
    client, calls = make_client(tmp_path, [FakeProc(stdout=cli_json())])
    with pytest.raises(llm.PromptSizeError):
        client.complete("y" * 51, purpose="compose:day")
    assert not calls, "the backend must not see an oversized prompt"
    row = client._db.execute("SELECT error, input_tokens FROM llm_calls").fetchone()
    assert "prompt size guard" in row[0] and row[1] == 0
    assert issubclass(llm.PromptSizeError, LLMError)


# ------------------------------------------- transient zero-billed retry --


def _error_envelope(billed=0):
    """The 2026-08-03 failure shape: is_error, no API time, no billing."""
    usage = {"input_tokens": billed, "output_tokens": 0,
             "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    return json.dumps({"is_error": True, "duration_api_ms": 0,
                       "num_turns": 1, "stop_reason": "stop_sequence",
                       "usage": usage, "modelUsage": {}, "result": ""})


def test_zero_billed_cli_failure_retries_once_and_succeeds(tmp_path):
    """The 2026-08-03 insight failure, replayed: the envelope reports
    zero tokens billed, so one free retry runs — and both attempts are
    in the ledger, because nothing bypasses logging."""
    client, calls = make_client(tmp_path, [
        FakeProc(stdout=_error_envelope(), returncode=1),
        FakeProc(stdout=cli_json("recovered")),
    ])
    r = client.complete("x", purpose="insight:suggestions")
    assert r["text"] == "recovered"
    assert len(calls) == 2
    rows = client._db.execute(
        "SELECT error, input_tokens FROM llm_calls ORDER BY id").fetchall()
    assert len(rows) == 2
    assert "zero tokens billed" in rows[0][0]
    assert rows[1][0] is None and rows[1][1] == 108


def test_transient_failures_raise_after_the_bounded_ladder(tmp_path, monkeypatch):
    """Updated 2026-08-24 (BUG-1): the ladder is config.LLM_TRANSIENT_ATTEMPTS
    calls with a wait between them, not exactly one immediate retry —
    still zero-billed only, still every attempt ledgered."""
    monkeypatch.setattr(config, "LLM_TRANSIENT_ATTEMPTS", 3)
    client, calls = make_client(tmp_path, [
        FakeProc(stdout=_error_envelope(), returncode=1),
        FakeProc(stdout=_error_envelope(), returncode=1),
        FakeProc(stdout=_error_envelope(), returncode=1),
    ])
    waits = []
    client._sleep = waits.append
    with pytest.raises(LLMError, match="after 3 zero-billed attempt"):
        client.complete("x", purpose="insight:suggestions")
    assert len(calls) == 3                      # the ladder, never more
    assert waits == [2.0, 4.0]                  # 2**attempt, no provider hint
    n = client._db.execute("SELECT COUNT(*) FROM llm_calls").fetchone()[0]
    assert n == 3                               # every attempt ledgered
    assert client.unavailable is None           # an outage, not a refusal


def test_billed_envelope_failure_is_never_retried(tmp_path):
    """An is_error envelope that DID bill tokens may have done real work
    server-side; re-sending it automatically is the expensive path the
    project forbids (GUIDE §6) — one call, immediate raise."""
    client, calls = make_client(tmp_path, [
        FakeProc(stdout=_error_envelope(billed=5000), returncode=1),
    ])
    with pytest.raises(LLMError, match="not retried"):
        client.complete("x", purpose="map:test")
    assert len(calls) == 1


def test_plain_cli_failure_is_never_retried(tmp_path):
    """A non-envelope failure (no usage report) cannot prove it was
    unbilled: no retry — the pre-existing behavior, pinned."""
    client, calls = make_client(tmp_path, [
        FakeProc(stderr="boom", returncode=1)])
    with pytest.raises(LLMError):
        client.complete("x", purpose="map:test")
    assert len(calls) == 1


def test_zero_exit_error_envelope_is_not_silent_garbage(tmp_path):
    """The CLI can exit 0 while reporting is_error in the envelope; that
    must raise (and retry, when unbilled), never return empty text as a
    completion."""
    client, calls = make_client(tmp_path, [
        FakeProc(stdout=_error_envelope(), returncode=0),
        FakeProc(stdout=cli_json("recovered")),
    ])
    r = client.complete("x", purpose="map:test")
    assert r["text"] == "recovered"
    assert len(calls) == 2


# ---- Gemini / Google AI Studio backend tests


class FakeGeminiResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text or json.dumps(self._json_data)

    def json(self):
        return self._json_data


def gemini_json(text="gemini summary", inp=120, out=30, finish_reason="STOP"):
    return {
        "candidates": [
            {
                "content": {"parts": [{"text": text}], "role": "model"},
                "finishReason": finish_reason,
            }
        ],
        "usageMetadata": {
            "promptTokenCount": inp,
            "candidatesTokenCount": out,
            "totalTokenCount": inp + out,
        },
    }


class FakeGeminiRequester:
    def __init__(self, responses=None, error=None):
        self.calls = []
        self._responses = responses or []
        self._error = error

    def __call__(self, url, json=None, headers=None, timeout=None):
        self.calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        if self._error is not None:
            raise self._error
        return self._responses.pop(0)


def make_gemini_client(tmp_path, **fake_kwargs):
    fake = FakeGeminiRequester(**fake_kwargs)
    backend = llm.GeminiBackend(api_key="fake-gemini-key", requester=fake)
    client = LLMClient(db_path=tmp_path / "ledger.db", backend=backend)
    return client, fake


def test_gemini_backend_resolves_tier_and_ledgers_backend(tmp_path):
    client, fake = make_gemini_client(
        tmp_path, responses=[FakeGeminiResponse(json_data=gemini_json())]
    )
    r = client.complete("summarize", purpose="map:test", model=config.MAP_MODEL)
    assert "gemini-2.5-flash" in fake.calls[0]["url"]
    assert fake.calls[0]["json"]["contents"][0]["parts"][0]["text"] == "summarize"
    assert r["text"] == "gemini summary"
    assert r["input_tokens"] == 120
    assert r["output_tokens"] == 30
    assert r["model"] == config.LLM_MODELS["gemini"]["haiku"]
    row = client._db.execute("SELECT backend, model FROM llm_calls").fetchone()
    assert row == ("gemini", config.LLM_MODELS["gemini"]["haiku"])


def test_gemini_failure_is_ledgered_and_raises(tmp_path):
    client, _ = make_gemini_client(
        tmp_path,
        responses=[FakeGeminiResponse(status_code=500, text="Internal Server Error")
                   for _ in range(config.LLM_TRANSIENT_ATTEMPTS)],
    )
    client._sleep = lambda s: None
    with pytest.raises(LLMError, match="HTTP 500"):
        client.complete("x", purpose="map:test")
    row = client._db.execute("SELECT backend, error, input_tokens FROM llm_calls").fetchone()
    assert row[0] == "gemini" and "HTTP 500" in row[1] and row[2] == 0
    assert client.unavailable is None           # a 5xx outage never trips the breaker


def test_gemini_5xx_outage_does_not_trip_the_breaker_but_quota_429_does(tmp_path):
    client, fake = make_gemini_client(
        tmp_path,
        responses=[FakeGeminiResponse(status_code=503, text="overloaded"),
                   FakeGeminiResponse(json_data=gemini_json("back"))],
    )
    client._sleep = lambda s: None
    assert client.complete("x", purpose="map:test")["text"] == "back"
    assert client.unavailable is None

    quota = FakeGeminiResponse(status_code=429, text=_GEMINI_QUOTA_BODY)
    client, fake = make_gemini_client(
        tmp_path, responses=[quota] * config.LLM_TRANSIENT_ATTEMPTS)
    waits = []
    client._sleep = waits.append
    with pytest.raises(llm.ProviderUnavailableError) as info:
        client.complete("x", purpose="map:batch1")
    assert info.value.reason == "quota exhausted"
    assert client.unavailable == "quota exhausted"
    assert len(fake.calls) == config.LLM_TRANSIENT_ATTEMPTS
    assert waits == [37.0] * (config.LLM_TRANSIENT_ATTEMPTS - 1)  # the provider's hint
    # …and the next call never reaches the provider: ledgered, zero, raised.
    with pytest.raises(llm.ProviderUnavailableError):
        client.complete("y", purpose="map:batch2")
    assert len(fake.calls) == config.LLM_TRANSIENT_ATTEMPTS
    rows = client._db.execute(
        "SELECT error, input_tokens FROM llm_calls ORDER BY id").fetchall()
    assert rows[-1][0] == "provider unavailable: quota exhausted (short-circuit)"
    assert all(r[1] == 0 for r in rows if r[0])   # every failed attempt, zero-billed
    assert client.status() == {"backend": "gemini",
                               "unavailable": "quota exhausted",
                               "models_used": []}


_GEMINI_QUOTA_BODY = json.dumps({"error": {
    "code": 429,
    "message": ("You exceeded your current quota, please check your plan and"
                " billing details.\n* Quota exceeded for metric:"
                " generativelanguage.googleapis.com/generate_content_free_tier_requests,"
                " limit: 20, model: gemini-2.5-flash\nPlease retry in 36.962849995s."),
    "status": "RESOURCE_EXHAUSTED",
    "details": [{"@type": "type.googleapis.com/google.rpc.RetryInfo",
                 "retryDelay": "37s"}],
}})


def test_retry_hint_parsing():
    assert llm.parse_retry_hint(_GEMINI_QUOTA_BODY) == 37.0        # retryDelay wins
    assert llm.parse_retry_hint('{"error": {"message": "Please retry in 36.96s."}}') == 36.96
    assert llm.parse_retry_hint("plain text, retry in 5s please") == 5.0
    assert llm.parse_retry_hint("nothing here") is None
    assert llm.parse_retry_hint(None, {"Retry-After": "12"}) == 12.0
    assert llm.parse_retry_hint(None, {"retry-after": "Wed, 21 Oct 2026 07:28:00 GMT"}) is None


def test_gemini_retry_after_header_is_honored_and_capped(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LLM_RETRY_MAX_WAIT_S", 10)
    monkeypatch.setattr(config, "LLM_TRANSIENT_ATTEMPTS", 2)
    hinted = FakeGeminiResponse(status_code=503, text="busy")
    hinted.headers = {"Retry-After": "600"}
    client, _ = make_gemini_client(
        tmp_path, responses=[hinted, FakeGeminiResponse(json_data=gemini_json("ok"))])
    waits = []
    client._sleep = waits.append
    assert client.complete("x", purpose="map:test")["text"] == "ok"
    assert waits == [10.0]                      # header 600 s, capped at the policy max
    assert client.status()["models_used"] == [config.LLM_MODELS["gemini"]["haiku"]]


def test_gemini_auth_failure_trips_immediately(tmp_path):
    client, fake = make_gemini_client(
        tmp_path, responses=[FakeGeminiResponse(status_code=403, text="PERMISSION_DENIED")])
    with pytest.raises(llm.ProviderUnavailableError) as info:
        client.complete("x", purpose="map:test")
    assert info.value.reason == "not authenticated"
    assert len(fake.calls) == 1                 # not a transient: no ladder


def test_gemini_missing_key_is_unavailable_at_construction(tmp_path, monkeypatch):
    for var in ("GOOGLE_GEMINI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    fake = FakeGeminiRequester(responses=[])
    client = LLMClient(db_path=tmp_path / "g.db",
                       backend=llm.GeminiBackend(requester=fake))
    assert client.unavailable == "not authenticated"
    with pytest.raises(llm.ProviderUnavailableError):
        client.complete("x", purpose="map:test")
    assert fake.calls == []
    row = client._db.execute("SELECT backend, error FROM llm_calls").fetchone()
    assert row == ("gemini", "provider unavailable: not authenticated (short-circuit)")


# ---------------------------------------- the CLI refusal and the breaker --


def _refusal_envelope():
    """The 2026-08-14 envelope: zero-billed, and it would have said the
    same thing 35 more times (it did)."""
    data = json.loads(_error_envelope())
    data["result"] = ("Your organization has disabled Claude subscription access"
                      " for Claude Code · Use an Anthropic API key instead")
    return json.dumps(data)


def test_cli_subscription_refusal_trips_the_breaker(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LLM_TRANSIENT_ATTEMPTS", 2)
    client, calls = make_client(tmp_path, [
        FakeProc(stdout=_refusal_envelope(), returncode=1),
        FakeProc(stdout=_refusal_envelope(), returncode=1),
        FakeProc(stdout=cli_json("never asked")),
    ])
    client._sleep = lambda s: None
    with pytest.raises(llm.ProviderUnavailableError) as info:
        client.complete("x", purpose="map:batch1")
    assert info.value.reason == "provider refused"
    with pytest.raises(llm.ProviderUnavailableError):
        client.complete("y", purpose="map:batch2")
    assert len(calls) == 2                      # the third proc was never run
    assert client.status()["unavailable"] == "provider refused"


def test_classify_unavailable_table():
    f = llm.classify_unavailable
    assert f("Your organization has disabled Claude subscription access") == "provider refused"
    assert f("Not logged in · run claude login") == "not authenticated"
    assert f("Invalid API key") == "not authenticated"
    assert f("anything", 401) == "not authenticated"
    assert f("Your credit balance is too low") == "quota exhausted"
    assert f(_GEMINI_QUOTA_BODY, 429) == "quota exhausted"
    assert f("Rate limit exceeded", 429) == "quota exhausted"
    assert f("Rate limit exceeded", None) is None   # bare text, no status: not decisive
    assert f("Internal Server Error", 500) is None
    assert f("refusal: the model declined") is None


# ------------------------------------------------ NullBackend / selection --


def test_null_backend_ledgers_and_raises(tmp_path):
    client = LLMClient(db_path=tmp_path / "n.db", backend=llm.NullBackend())
    assert client.unavailable == "disabled"
    with pytest.raises(llm.ProviderUnavailableError) as info:
        client.complete("x", purpose="map:batch1", package_id="P1")
    assert info.value.reason == "disabled"
    row = client._db.execute(
        "SELECT backend, model, error, input_tokens, package_id FROM llm_calls").fetchone()
    assert row == ("none", config.LLM_MODELS.get("none", {}).get("haiku", "haiku"),
                   "provider unavailable: disabled (short-circuit)", 0, "P1")
    assert client.status() == {"backend": "none", "unavailable": "disabled",
                               "models_used": []}


def test_null_backend_reason_is_free_text_for_the_ledger(tmp_path):
    client = LLMClient(db_path=tmp_path / "n.db",
                       backend=llm.NullBackend("disabled by operator"))
    with pytest.raises(llm.ProviderUnavailableError):
        client.complete("x", purpose="compose:day-in-review")
    row = client._db.execute("SELECT error FROM llm_calls").fetchone()
    assert "disabled by operator" in row[0]


def test_none_selects_the_null_backend(tmp_path, monkeypatch):
    for value in ("none", "off", "disabled", "NONE "):
        monkeypatch.setattr(config, "LLM_BACKEND", value.strip().lower())
        client = LLMClient(db_path=tmp_path / "n.db")
        assert isinstance(client._backend, llm.NullBackend)
        assert client.unavailable == "disabled"


def test_unknown_backend_is_a_configuration_error(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LLM_BACKEND", "gemni")   # the typo that used to bill the CLI
    with pytest.raises(ValueError, match="not a backend; accepted: api, cli"):
        LLMClient(db_path=tmp_path / "x.db")
    monkeypatch.setattr(config, "LLM_BACKEND", "")
    assert isinstance(LLMClient(db_path=tmp_path / "y.db")._backend, CLIBackend)


def test_api_backend_missing_key_is_unavailable_at_construction(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    backend = AnthropicBackend()
    assert backend.unavailable == "not authenticated"
    client = LLMClient(db_path=tmp_path / "a.db", backend=backend)
    with pytest.raises(llm.ProviderUnavailableError):
        client.complete("x", purpose="map:test")


def test_api_rate_limit_and_auth_errors_trip_the_breaker(tmp_path):
    class RateLimited(RuntimeError):
        status_code = 429

    client, fake = make_api_client(tmp_path, error=RateLimited("rate_limit_error"))
    with pytest.raises(llm.ProviderUnavailableError) as info:
        client.complete("x", purpose="map:test")
    assert info.value.reason == "quota exhausted"
    assert len(fake.calls) == 1                 # the SDK already retried; we do not
    assert client.unavailable == "quota exhausted"


def test_status_tracks_models_used(tmp_path):
    client, _ = make_client(tmp_path, [FakeProc(stdout=cli_json()),
                                       FakeProc(stdout=cli_json())])
    assert client.status()["models_used"] == []
    client.complete("a", purpose="map:test", model="haiku")
    client.complete("b", purpose="compose:day-in-review", model="opus")
    assert client.status() == {"backend": "cli", "unavailable": None,
                               "models_used": ["haiku", "opus"]}


def test_provider_unavailable_is_an_llm_error():
    exc = llm.ProviderUnavailableError("quota exhausted")
    assert isinstance(exc, LLMError)
    assert exc.reason == "quota exhausted" and exc.unavailable == "quota exhausted"
    assert exc.reason in llm.UNAVAILABLE_REASONS


def test_gemini_429_is_transient_error_and_retries(tmp_path):
    client, fake = make_gemini_client(
        tmp_path,
        responses=[
            FakeGeminiResponse(status_code=429, text="Rate limit exceeded"),
            FakeGeminiResponse(json_data=gemini_json("recovered")),
        ],
    )
    r = client.complete("x", purpose="map:test")
    assert r["text"] == "recovered"
    assert len(fake.calls) == 2
    rows = client._db.execute("SELECT error, input_tokens FROM llm_calls ORDER BY id").fetchall()
    assert len(rows) == 2
    assert "429" in rows[0][0]


def test_gemini_refusal_is_ledgered_and_raises(tmp_path):
    client, _ = make_gemini_client(
        tmp_path,
        responses=[FakeGeminiResponse(json_data=gemini_json(finish_reason="SAFETY"))],
    )
    with pytest.raises(LLMError, match="refusal"):
        client.complete("x", purpose="map:test")
    row = client._db.execute("SELECT error FROM llm_calls").fetchone()
    assert "refusal" in row[0]


def test_gemini_backend_selected_from_config(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LLM_BACKEND", "gemini")
    monkeypatch.setenv("GOOGLE_GEMINI_API_KEY", "dummy-key")
    client = LLMClient(db_path=tmp_path / "g.db")
    assert isinstance(client._backend, llm.GeminiBackend)


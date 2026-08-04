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


def test_second_transient_failure_raises_and_is_bounded(tmp_path):
    client, calls = make_client(tmp_path, [
        FakeProc(stdout=_error_envelope(), returncode=1),
        FakeProc(stdout=_error_envelope(), returncode=1),
    ])
    with pytest.raises(LLMError, match="after a zero-billed retry"):
        client.complete("x", purpose="insight:suggestions")
    assert len(calls) == 2                      # exactly one retry, never more
    n = client._db.execute("SELECT COUNT(*) FROM llm_calls").fetchone()[0]
    assert n == 2                               # both attempts ledgered


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

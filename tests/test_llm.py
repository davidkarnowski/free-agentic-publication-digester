"""LLM client tests: ledger recording, token accounting, failure paths.
The claude CLI is faked via an injected runner."""

import json

import pytest

from fapd.llm import LLMClient, LLMError


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

"""Per-call usage in the LLM ledger and the live usage snapshot (2026-10-08).

Every response's full usage is recorded beside the original two token
columns: fresh input, cache read, cache write (with the 5-minute / 1-hour
split where reported), billed output, thinking, the exact model id, and the
provider's own cost figure. NULL means "not reported"; 0 means reported
zero. After each ledger write a totals-only JSON snapshot is rewritten
beside the ledger. Backends are faked by injection, as in test_llm.py."""

import datetime as dt
import json
import sqlite3
import subprocess
from types import SimpleNamespace

import pytest

from fapd import config, llm
from fapd.llm import LLMClient, LLMError


class FakeProc:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def envelope(**over):
    """A CLI JSON envelope shaped like the real one (checked 2026-10-08)."""
    data = {
        "type": "result",
        "is_error": False,
        "result": "a summary",
        "total_cost_usd": 0.0123,
        "usage": {
            "input_tokens": 40,
            "cache_read_input_tokens": 500,
            "cache_creation_input_tokens": 1200,
            "output_tokens": 90,
            "output_tokens_details": {"thinking_tokens": 30},
            "cache_creation": {"ephemeral_5m_input_tokens": 200,
                               "ephemeral_1h_input_tokens": 1000},
        },
        "modelUsage": {"claude-haiku-test-1": {"inputTokens": 40}},
    }
    data.update(over)
    return json.dumps(data)


def cli_client(tmp_path, procs):
    def runner(cmd, **kwargs):
        item = procs.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    return LLMClient(db_path=tmp_path / "ledger.db", runner=runner,
                     sleeper=lambda s: None)


def last_row(tmp_path):
    db = sqlite3.connect(tmp_path / "ledger.db")
    db.row_factory = sqlite3.Row
    return dict(db.execute("SELECT * FROM llm_calls ORDER BY id DESC LIMIT 1").fetchone())


def snapshot(tmp_path):
    return json.loads((tmp_path / llm.USAGE_SNAPSHOT_NAME).read_text())


# ---- CLI


def test_cli_records_the_full_split(tmp_path):
    client = cli_client(tmp_path, [FakeProc(stdout=envelope())])
    r = client.complete("p", purpose="map:batch1", package_id="PKG-1")
    row = last_row(tmp_path)
    # The original columns keep their meaning: input is the lumped sum.
    assert r["input_tokens"] == row["input_tokens"] == 40 + 500 + 1200
    assert row["output_tokens"] == 90
    assert row["fresh_input_tokens"] == 40
    assert row["cache_read_tokens"] == 500
    assert row["cache_write_tokens"] == 1200
    assert row["cache_write_5m_tokens"] == 200
    assert row["cache_write_1h_tokens"] == 1000
    assert row["output_billed_tokens"] == 90  # thinking is inside Anthropic output
    assert row["thinking_tokens"] == 30
    assert row["model_id"] == "claude-haiku-test-1"
    assert row["model"] == "haiku"  # the alias stays beside the exact id
    assert row["reported_cost_usd"] == pytest.approx(0.0123)


def test_cli_envelope_without_split_leaves_split_null(tmp_path):
    data = json.loads(envelope())
    del data["usage"]["cache_creation"], data["usage"]["output_tokens_details"]
    del data["modelUsage"], data["total_cost_usd"]
    client = cli_client(tmp_path, [FakeProc(stdout=json.dumps(data))])
    client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert row["cache_write_tokens"] == 1200
    assert row["cache_write_5m_tokens"] is None
    assert row["cache_write_1h_tokens"] is None
    assert row["thinking_tokens"] is None
    assert row["model_id"] is None
    assert row["reported_cost_usd"] is None


def test_cli_lists_every_model_the_envelope_names(tmp_path):
    client = cli_client(tmp_path, [FakeProc(stdout=envelope(
        modelUsage={"model-b": {}, "model-a": {}}))])
    client.complete("p", purpose="map:t")
    assert last_row(tmp_path)["model_id"] == "model-a,model-b"


def test_cli_billed_failure_records_its_usage(tmp_path):
    """A failure that billed tokens is counted: the row carries the
    envelope's usage while input_tokens keeps its old meaning (0 on a
    failed row), so the throttle reads what it always read."""
    failed = envelope(is_error=True, result="something broke",
                      stop_reason="max_tokens")
    client = cli_client(tmp_path, [FakeProc(stdout=failed)])
    with pytest.raises(LLMError):
        client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert row["error"]
    assert row["input_tokens"] == 0 and row["output_tokens"] == 0
    assert row["fresh_input_tokens"] == 40
    assert row["output_billed_tokens"] == 90


def test_cli_zero_billed_failure_records_known_zero(tmp_path):
    zero = json.dumps({"type": "result", "is_error": True, "result": "hiccup",
                       "usage": {"input_tokens": 0, "output_tokens": 0,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0},
                       "modelUsage": {}})
    n = max(1, config.LLM_TRANSIENT_ATTEMPTS)
    client = cli_client(tmp_path, [FakeProc(stdout=zero) for _ in range(n)])
    with pytest.raises(LLMError):
        client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert row["fresh_input_tokens"] == 0
    assert row["output_billed_tokens"] == 0


def test_cli_timeout_records_usage_unknown(tmp_path):
    """The envelope arrives only at the end, so a timeout knows nothing:
    NULL, never a made-up zero."""
    client = cli_client(tmp_path, [subprocess.TimeoutExpired(["claude"], 5)])
    with pytest.raises(LLMError):
        client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert row["error"]
    for key in ("fresh_input_tokens", "cache_read_tokens", "output_billed_tokens"):
        assert row[key] is None
    snap = snapshot(tmp_path)
    assert snap["daily"][0]["errors_usage_unknown"] == 1


# ---- Anthropic SDK


class FakeAnthropic:
    def __init__(self, response):
        self.messages = SimpleNamespace(create=lambda **kw: response)


def test_api_records_the_split_and_model(tmp_path):
    resp = SimpleNamespace(
        stop_reason="end_turn", model="claude-haiku-test-2",
        content=[SimpleNamespace(type="text", text="ok")],
        usage=SimpleNamespace(
            input_tokens=10, output_tokens=7, cache_read_input_tokens=20,
            cache_creation_input_tokens=30,
            cache_creation=SimpleNamespace(ephemeral_5m_input_tokens=30,
                                           ephemeral_1h_input_tokens=0)))
    client = LLMClient(db_path=tmp_path / "ledger.db",
                       backend=llm.AnthropicBackend(client=FakeAnthropic(resp)))
    client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert row["input_tokens"] == 60
    assert (row["fresh_input_tokens"], row["cache_read_tokens"],
            row["cache_write_tokens"]) == (10, 20, 30)
    assert (row["cache_write_5m_tokens"], row["cache_write_1h_tokens"]) == (30, 0)
    assert row["model_id"] == "claude-haiku-test-2"
    assert row["reported_cost_usd"] is None


# ---- Gemini


class FakeGeminiResponse:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text or json.dumps(self._data)
        self.headers = {}

    def json(self):
        return self._data


def gemini_client(tmp_path, responses):
    def requester(url, json=None, headers=None, timeout=None):
        return responses.pop(0)

    return LLMClient(db_path=tmp_path / "ledger.db", sleeper=lambda s: None,
                     backend=llm.GeminiBackend(api_key="k", requester=requester))


def test_gemini_counts_thinking_and_cache(tmp_path):
    data = {
        "candidates": [{"content": {"parts": [{"text": "g"}]}, "finishReason": "STOP"}],
        "usageMetadata": {"promptTokenCount": 1000, "cachedContentTokenCount": 400,
                          "candidatesTokenCount": 50, "thoughtsTokenCount": 300},
        "modelVersion": "gemini-test-flash",
    }
    client = gemini_client(tmp_path, [FakeGeminiResponse(data=data)])
    r = client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert r["input_tokens"] == row["input_tokens"] == 1000  # unchanged meaning
    assert row["output_tokens"] == 50                          # unchanged meaning
    assert row["fresh_input_tokens"] == 600
    assert row["cache_read_tokens"] == 400
    assert row["cache_write_tokens"] == 0
    assert row["thinking_tokens"] == 300
    assert row["output_billed_tokens"] == 350  # thinking is billed as output
    assert row["model_id"] == "gemini-test-flash"


def test_gemini_omitted_counts_are_zero(tmp_path):
    data = {"candidates": [{"content": {"parts": [{"text": "g"}]}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 2}}
    client = gemini_client(tmp_path, [FakeGeminiResponse(data=data)])
    client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert (row["cache_read_tokens"], row["thinking_tokens"]) == (0, 0)
    assert row["output_billed_tokens"] == 2


def test_gemini_http_refusal_is_known_zero(tmp_path):
    client = gemini_client(tmp_path, [FakeGeminiResponse(status_code=400, text="bad")])
    with pytest.raises(LLMError):
        client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert row["fresh_input_tokens"] == 0 and row["output_billed_tokens"] == 0


# ---- Rows that sent no request, and the migration


def test_short_circuit_rows_are_known_zero(tmp_path):
    client = LLMClient(db_path=tmp_path / "ledger.db", backend=llm.NullBackend())
    with pytest.raises(llm.ProviderUnavailableError):
        client.complete("p", purpose="map:t")
    row = last_row(tmp_path)
    assert row["fresh_input_tokens"] == 0
    assert row["model_id"] is None


def test_old_ledger_gains_the_columns_with_null_history(tmp_path):
    db = sqlite3.connect(tmp_path / "ledger.db")
    db.executescript(llm._SCHEMA)
    db.execute("INSERT INTO llm_calls (ts_utc, model, purpose, input_tokens,"
               " output_tokens) VALUES (?, 'haiku', 'map:old', 900, 80)",
               (dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds"),))
    db.commit()
    db.close()
    client = cli_client(tmp_path, [FakeProc(stdout=envelope())])
    cols = {r[1] for r in client._db.execute("PRAGMA table_info(llm_calls)")}
    assert set(llm._USAGE_KEYS) <= cols
    old = client._db.execute(
        "SELECT fresh_input_tokens, model_id FROM llm_calls WHERE purpose='map:old'"
    ).fetchone()
    assert old == (None, None)
    client.complete("p", purpose="map:new")
    day = snapshot(tmp_path)["daily"][0]
    # The old row counts by its lumped input; the new one by its split.
    assert day["input_tokens"] == 900 + 1740
    assert day["output_tokens"] == 80 + 90
    assert day["calls_without_split"] == 1
    assert day["fresh_input_tokens"] == 40


# ---- The snapshot


def test_snapshot_is_written_after_each_call_and_totals_only(tmp_path):
    client = cli_client(tmp_path, [FakeProc(stdout=envelope()),
                                   FakeProc(stdout=envelope())])
    client.complete("p", purpose="map:batch1", package_id="PKG-SECRETLESS-1",
                    granule_id="GRANULE-1")
    assert snapshot(tmp_path)["daily"][0]["calls"] == 1
    client.complete("p", purpose="plain:x")
    snap = snapshot(tmp_path)
    assert snap["schema"] == 2 and snap["clock"] == "UTC"
    assert (snap["hours"], snap["days"]) == (48, 14)
    day, hour = snap["daily"][0], snap["hourly"][0]
    for row in (day, hour):
        assert row["backend"] == "cli" and row["model"] == "haiku"
        assert row["model_ids"] == ["claude-haiku-test-1"]
        assert row["calls"] == row["ok"] == 2
        assert row["input_tokens"] == 2 * 1740
        assert row["cache_write_1h_tokens"] == 2000
        assert row["thinking_tokens"] == 60
        assert row["reported_cost_usd"] == pytest.approx(0.0246)
    assert len(hour["hour"]) == 13 and len(day["day"]) == 10
    raw = (tmp_path / llm.USAGE_SNAPSHOT_NAME).read_text()
    for leak in ("PKG-SECRETLESS-1", "GRANULE-1", "map:batch1", "a summary"):
        assert leak not in raw
    # The temp file never lingers beside the snapshot.
    assert [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp")] == []


def test_snapshot_windows(tmp_path):
    db = sqlite3.connect(tmp_path / "ledger.db")
    LLMClient(db_path=tmp_path / "ledger.db", backend=llm.NullBackend()).close()
    now = dt.datetime(2026, 10, 8, 12, 30, tzinfo=dt.UTC)

    def add(when):
        db.execute("INSERT INTO llm_calls (ts_utc, backend, model, purpose,"
                   " input_tokens, output_tokens) VALUES (?, 'cli', 'haiku', 'map:t', 1, 1)",
                   (when.isoformat(timespec="milliseconds"),))

    add(now - dt.timedelta(hours=1))   # in both
    add(now - dt.timedelta(hours=60))  # daily only
    add(now - dt.timedelta(days=20))   # neither
    db.commit()
    snap = llm.build_usage_snapshot(db, now=now)
    assert sum(r["calls"] for r in snap["hourly"]) == 1
    assert sum(r["calls"] for r in snap["daily"]) == 2


def test_snapshot_failure_never_costs_the_call(tmp_path, caplog):
    client = LLMClient(db_path=tmp_path / "ledger.db",
                       snapshot_path=tmp_path / "missing-dir" / "u.json",
                       runner=lambda cmd, **kw: FakeProc(stdout=envelope()))
    r = client.complete("p", purpose="map:t")
    assert r["text"] == "a summary"
    assert last_row(tmp_path)["fresh_input_tokens"] == 40
    assert "snapshot not written" in caplog.text

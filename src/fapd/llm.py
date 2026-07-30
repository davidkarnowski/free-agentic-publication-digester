"""LLM access with a persistent token ledger (GUIDE §6 rules 7–8).

Backends are pluggable (§6 rule 7, amended 2026-07-30). Callers name model
*tiers* (config.MAP_MODEL / COMPOSE_MODEL); config.LLM_MODELS resolves the
concrete model for the selected backend:

- CLIBackend (default): the `claude` CLI in headless mode (`claude -p
  --output-format json`), billed to the operator's Claude subscription.
- AnthropicBackend: the official Anthropic SDK (ANTHROPIC_API_KEY), for
  hosted/VPS runs where no CLI subscription exists.

The ledger (data/llm_ledger.db) is the accountability layer, paralleling
fetch_log.db: every call is recorded — including failures — with the
backend and the resolved model, before anyone looks at the response. Per
§6 rule 8 no cap is enforced yet; the ledger's totals are what will
eventually set it.
"""

import datetime as dt
import json
import logging
import sqlite3
import subprocess
import time

from . import config

logger = logging.getLogger("fapd.llm")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS llm_calls (
    id INTEGER PRIMARY KEY,
    ts_utc TEXT NOT NULL,
    backend TEXT NOT NULL DEFAULT 'cli',
    model TEXT NOT NULL,
    purpose TEXT NOT NULL,
    package_id TEXT,
    granule_id TEXT,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_llm_calls_ts ON llm_calls (ts_utc);
"""


class LLMError(RuntimeError):
    pass


class CLIBackend:
    """The `claude` CLI, headless. Returns {"text", "input_tokens",
    "output_tokens"} or raises LLMError."""

    name = "cli"

    def __init__(self, runner=None):
        self._runner = runner or subprocess.run

    def complete(self, prompt, *, model, timeout):
        cmd = ["claude", "-p", "--model", model, "--output-format", "json"]
        try:
            proc = self._runner(
                cmd, input=prompt, capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise LLMError(repr(exc)) from exc
        if proc.returncode != 0:
            raise LLMError((proc.stderr or proc.stdout or "").strip()[:500])
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(f"unparseable CLI output: {exc}") from exc
        usage = data.get("usage") or {}
        return {
            "text": (data.get("result") or "").strip(),
            "input_tokens": (
                usage.get("input_tokens", 0)
                + usage.get("cache_read_input_tokens", 0)
                + usage.get("cache_creation_input_tokens", 0)
            ),
            "output_tokens": usage.get("output_tokens", 0),
        }


class AnthropicBackend:
    """The official Anthropic SDK. The client is injectable for tests; the
    SDK import is deferred so CLI-only installs never touch it."""

    name = "api"

    def __init__(self, client=None):
        if client is None:
            import anthropic

            client = anthropic.Anthropic()  # ANTHROPIC_API_KEY from env
        self._client = client

    def complete(self, prompt, *, model, timeout):
        try:
            resp = self._client.messages.create(
                model=model,
                max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )
        except Exception as exc:  # anthropic.APIError family; SDK retried 429/5xx
            raise LLMError(str(exc)[:500]) from exc
        if getattr(resp, "stop_reason", None) == "refusal":
            raise LLMError("refusal: the model declined to complete this request")
        usage = resp.usage
        return {
            "text": "".join(
                block.text for block in resp.content
                if getattr(block, "type", "") == "text"
            ).strip(),
            "input_tokens": (
                usage.input_tokens
                + (getattr(usage, "cache_read_input_tokens", 0) or 0)
                + (getattr(usage, "cache_creation_input_tokens", 0) or 0)
            ),
            "output_tokens": usage.output_tokens,
        }


class LLMClient:
    def __init__(self, db_path=None, runner=None, backend=None):
        self._db_path = db_path or config.LLM_LEDGER_DB
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self._db_path)
        self._db.executescript(_SCHEMA)
        self._ensure_backend_column()
        if backend is not None:
            self._backend = backend
        elif runner is not None:
            self._backend = CLIBackend(runner)  # existing test seam
        elif config.LLM_BACKEND == "api":
            self._backend = AnthropicBackend()
        else:
            self._backend = CLIBackend()

    def complete(self, prompt, *, purpose, model=None, package_id=None,
                 granule_id=None, timeout=None):
        """One text-in/text-out completion. Records the call in the ledger
        (success or failure) and returns
        {"text", "input_tokens", "output_tokens", "model"} — "model" is the
        resolved concrete model, not the tier alias."""
        tier = model or config.MAP_MODEL
        resolved = config.LLM_MODELS.get(self._backend.name, {}).get(tier, tier)
        started = time.monotonic()
        try:
            result = self._backend.complete(
                prompt, model=resolved, timeout=timeout or config.LLM_TIMEOUT,
            )
        except LLMError as exc:
            self._log(resolved, purpose, package_id, granule_id, 0, 0,
                      int((time.monotonic() - started) * 1000),
                      error=str(exc)[:500])
            raise LLMError(
                f"{self._backend.name} backend failed ({purpose}): {exc}"
            ) from exc
        duration_ms = int((time.monotonic() - started) * 1000)
        self._log(resolved, purpose, package_id, granule_id,
                  result["input_tokens"], result["output_tokens"], duration_ms)
        logger.info(
            "LLM %s/%s [%s] -> %d in / %d out tokens, %d ms [today: %s in]",
            self._backend.name, resolved, purpose,
            result["input_tokens"], result["output_tokens"], duration_ms,
            f"{self.tokens_today()[0]:,}",
        )
        return {**result, "model": resolved}

    def tokens_today(self):
        """(input_tokens, output_tokens, calls) for the current UTC day."""
        day_start = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT00:00:00")
        row = self._db.execute(
            "SELECT COALESCE(SUM(input_tokens),0), COALESCE(SUM(output_tokens),0),"
            " COUNT(*) FROM llm_calls WHERE ts_utc >= ?",
            (day_start,),
        ).fetchone()
        return row[0], row[1], row[2]

    def close(self):
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _ensure_backend_column(self):
        # Ledgers created before 2026-07-30 predate the backend column;
        # CREATE TABLE IF NOT EXISTS won't add it to an existing table.
        cols = {row[1] for row in self._db.execute("PRAGMA table_info(llm_calls)")}
        if "backend" not in cols:
            self._db.execute(
                "ALTER TABLE llm_calls ADD COLUMN backend TEXT NOT NULL DEFAULT 'cli'"
            )
            self._db.commit()

    def _log(self, model, purpose, package_id, granule_id,
             input_tokens, output_tokens, duration_ms, error=None):
        self._db.execute(
            "INSERT INTO llm_calls (ts_utc, backend, model, purpose, package_id,"
            " granule_id, input_tokens, output_tokens, duration_ms, error)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds"),
             self._backend.name, model, purpose, package_id, granule_id,
             input_tokens, output_tokens, duration_ms, error),
        )
        self._db.commit()

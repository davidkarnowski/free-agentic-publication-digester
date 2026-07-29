"""LLM access with a persistent token ledger (GUIDE §6 rules 7–8).

Backend: the `claude` CLI in headless mode (`claude -p --output-format
json`), so pipeline usage is billed to the operator's Claude subscription —
no separate API key. The ledger (data/llm_ledger.db) is the accountability
layer, paralleling fetch_log.db: every call is recorded, including
failures, before anyone looks at the response. Per §6 rule 8 no cap is
enforced yet — the ledger's totals are what will eventually set it.
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


class LLMClient:
    def __init__(self, db_path=None, runner=subprocess.run):
        self._db_path = db_path or config.LLM_LEDGER_DB
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self._db_path)
        self._db.executescript(_SCHEMA)
        self._runner = runner

    def complete(self, prompt, *, purpose, model=None, package_id=None,
                 granule_id=None, timeout=None):
        """One text-in/text-out completion. Records the call in the ledger
        (success or failure) and returns
        {"text", "input_tokens", "output_tokens", "model"}."""
        model = model or config.MAP_MODEL
        cmd = ["claude", "-p", "--model", model, "--output-format", "json"]
        started = time.monotonic()
        try:
            proc = self._runner(
                cmd, input=prompt, capture_output=True, text=True,
                timeout=timeout or config.LLM_TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            self._log(model, purpose, package_id, granule_id, 0, 0,
                      int((time.monotonic() - started) * 1000), error=repr(exc))
            raise LLMError(f"LLM call timed out ({purpose})") from exc
        duration_ms = int((time.monotonic() - started) * 1000)

        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()[:500]
            self._log(model, purpose, package_id, granule_id, 0, 0, duration_ms, error=err)
            raise LLMError(f"claude CLI failed ({purpose}): {err}")

        data = json.loads(proc.stdout)
        text = (data.get("result") or "").strip()
        usage = data.get("usage") or {}
        input_tokens = (
            usage.get("input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
        )
        output_tokens = usage.get("output_tokens", 0)
        self._log(model, purpose, package_id, granule_id,
                  input_tokens, output_tokens, duration_ms)
        logger.info(
            "LLM %s [%s] -> %d in / %d out tokens, %d ms [today: %s in]",
            model, purpose, input_tokens, output_tokens, duration_ms,
            f"{self.tokens_today()[0]:,}",
        )
        return {"text": text, "input_tokens": input_tokens,
                "output_tokens": output_tokens, "model": model}

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

    def _log(self, model, purpose, package_id, granule_id,
             input_tokens, output_tokens, duration_ms, error=None):
        self._db.execute(
            "INSERT INTO llm_calls (ts_utc, model, purpose, package_id, granule_id,"
            " input_tokens, output_tokens, duration_ms, error)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds"),
             model, purpose, package_id, granule_id,
             input_tokens, output_tokens, duration_ms, error),
        )
        self._db.commit()

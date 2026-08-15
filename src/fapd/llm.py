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
import os
import sqlite3
import subprocess
import time

import requests

from . import config
from .client import BudgetExceededError

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


class TokenBudgetExceededError(BudgetExceededError):
    """The on-demand daily token throttle refused to start a call (GUIDE
    §6 r8, operator ruling 2026-08-02). Subclasses the HTTP budget error
    deliberately: Worker.run_cycle already records that as paused-not-
    failed — our own budget refusing us is the policy working."""


class TransientLLMError(LLMError):
    """A backend failure whose failed attempt verifiably consumed ZERO
    tokens — the CLI's error envelope reports no usage, no per-model
    billing, and no API time. Retrying such a failure once is free, and
    it is the class that cost the 2026-08-03 insight report (is_error
    envelope, duration_api_ms=0, empty modelUsage; the manual re-run
    succeeded first try). Anything that MAY have billed tokens stays a
    plain LLMError and is never re-sent automatically — retries are the
    expensive path by design (GUIDE §6), and the per-item attempt
    ceilings above this layer stay the authority for those."""


class PromptSizeError(LLMError):
    """A single prompt exceeded config.LLM_MAX_PROMPT_CHARS (review
    R1/D3). An LLMError so the existing retry/ceiling machinery bounds
    it: per-item summaries hit the r14 attempt ceiling, and a compose
    failure at EOD hits the R3 finalizer hard stop — loud either way."""


#: Client-level retries for zero-billed transient failures ONLY (see
#: TransientLLMError). Exactly one: a second consecutive envelope
#: failure is a real outage the caller's own failure posture should
#: see, not something to hammer.
_TRANSIENT_RETRIES = 1


class CLIBackend:
    """The `claude` CLI, headless. Returns {"text", "input_tokens",
    "output_tokens"} or raises LLMError."""

    name = "cli"

    def __init__(self, runner=None):
        self._runner = runner or subprocess.run

    def complete(self, prompt, *, model, timeout):
        cmd = ["claude", "-p", "--model", model, "--output-format", "json"]
        # The CLI backend means subscription billing by definition: an
        # ANTHROPIC_API_KEY in the environment would silently take
        # precedence over the CLI's login/token and switch billing (the
        # shadowing hazard, .env.example) — strip it for the subprocess.
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        try:
            proc = self._runner(
                cmd, input=prompt, capture_output=True, text=True,
                timeout=timeout, env=env,
            )
        except subprocess.TimeoutExpired as exc:
            # A timeout may have consumed tokens server-side before the
            # clock ran out: never classified transient, never retried.
            raise LLMError(repr(exc)) from exc
        if proc.returncode != 0:
            raise self._cli_error(proc)
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(f"unparseable CLI output: {exc}") from exc
        if isinstance(data, dict) and data.get("is_error"):
            # The CLI can exit 0 while reporting failure in the envelope;
            # returning its empty `result` as a completion would hand the
            # caller silent garbage (found diagnosing 2026-08-03).
            raise self._envelope_error(data)
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

    def _cli_error(self, proc):
        """The LLMError for a non-zero CLI exit. When stdout carries the
        CLI's JSON error envelope, classify it (transient when zero
        tokens were billed); otherwise the raw stderr/stdout, as ever."""
        raw = (proc.stderr or proc.stdout or "").strip()
        try:
            data = json.loads(proc.stdout or "")
        except (TypeError, json.JSONDecodeError):
            return LLMError(raw[:500])
        if isinstance(data, dict) and data.get("is_error"):
            return self._envelope_error(data)
        return LLMError(raw[:500])

    @staticmethod
    def _envelope_error(data):
        """A compact, readable error from the CLI's envelope — the
        2026-08-03 failure logged 500 chars of raw JSON that still had
        to be diagnosed by eye. Transient iff verifiably zero-billed."""
        usage = data.get("usage") or {}
        billed = (usage.get("input_tokens", 0)
                  + usage.get("output_tokens", 0)
                  + usage.get("cache_read_input_tokens", 0)
                  + usage.get("cache_creation_input_tokens", 0))
        msg = (f"CLI error envelope: stop_reason={data.get('stop_reason')!r},"
               f" api_ms={data.get('duration_api_ms')},"
               f" result={str(data.get('result') or '')[:200]!r}")
        if billed == 0 and not data.get("modelUsage"):
            return TransientLLMError(msg + " — zero tokens billed")
        return LLMError(msg + f" — {billed} token(s) billed, not retried")


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


class GeminiBackend:
    """Google AI Studio / Gemini REST API backend.
    
    Uses standard requests HTTP API (https://generativelanguage.googleapis.com).
    The requester is injectable for tests.
    """

    name = "gemini"

    def __init__(self, api_key=None, requester=None):
        self._api_key = (
            api_key
            or os.environ.get("GOOGLE_GEMINI_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        self._requester = requester or requests.post

    def complete(self, prompt, *, model, timeout):
        if not self._api_key:
            raise LLMError(
                "Gemini API key not found. Set GOOGLE_GEMINI_API_KEY or"
                " GEMINI_API_KEY in environment."
            )

        model_name = model.removeprefix("models/")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            f"?key={self._api_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": config.LLM_MAX_OUTPUT_TOKENS,
            },
        }
        headers = {"Content-Type": "application/json"}

        try:
            resp = self._requester(
                url,
                json=payload,
                headers=headers,
                timeout=timeout,
            )
        except Exception as exc:
            raise LLMError(f"Gemini API HTTP request failed: {str(exc)[:500]}") from exc

        status_code = getattr(resp, "status_code", 200)
        if status_code != 200:
            err_text = getattr(resp, "text", str(resp))[:500]
            if status_code == 429:
                raise TransientLLMError(
                    f"Gemini API rate limit 429: {err_text} — zero tokens billed"
                )
            raise LLMError(f"Gemini API error (HTTP {status_code}): {err_text}")

        try:
            data = resp.json() if callable(getattr(resp, "json", None)) else json.loads(resp.text)
        except Exception as exc:
            raise LLMError(f"unparseable Gemini API output: {exc}") from exc

        candidates = data.get("candidates") or []
        if not candidates:
            prompt_feedback = data.get("promptFeedback")
            raise LLMError(f"Gemini returned no candidates. Feedback: {prompt_feedback}")

        candidate = candidates[0]
        finish_reason = candidate.get("finishReason")
        if finish_reason in ("SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII"):
            raise LLMError(
                f"refusal: Gemini model output blocked due to finishReason={finish_reason}"
            )

        content = candidate.get("content") or {}
        parts = content.get("parts") or []
        text = "".join(part.get("text", "") for part in parts).strip()

        usage = data.get("usageMetadata") or {}
        input_tokens = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)

        return {
            "text": text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
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
        elif config.LLM_BACKEND in ("gemini", "google"):
            self._backend = GeminiBackend()
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
        # Start gates, before any backend work. The throttle is counted
        # from the ledger (the fetch-log budget pattern: nothing bypasses
        # logging, enforcement holds across processes) and gates call
        # STARTS — an in-flight call is never aborted mid-stream.
        if config.DAILY_TOKEN_THROTTLE:
            spent = self.tokens_today()[0]
            if spent >= config.DAILY_TOKEN_THROTTLE:
                raise TokenBudgetExceededError(
                    f"daily token throttle engaged: {spent:,} input tokens"
                    f" today >= FAPD_DAILY_TOKEN_THROTTLE"
                    f" ({config.DAILY_TOKEN_THROTTLE:,}); paused until the"
                    " next UTC day")
        if len(prompt) > config.LLM_MAX_PROMPT_CHARS:
            self._log(resolved, purpose, package_id, granule_id, 0, 0, 0,
                      error=f"prompt size guard: {len(prompt):,} chars"[:500])
            raise PromptSizeError(
                f"prompt for {purpose!r} is {len(prompt):,} chars, past the"
                f" {config.LLM_MAX_PROMPT_CHARS:,}-char guard — one call"
                " must never carry an unbounded prompt (GUIDE §6 r8)")
        # One free retry for verifiably zero-billed transient failures
        # (TransientLLMError): the failed attempt cost nothing, so the
        # retry cannot double-spend, and a single CLI hiccup stops
        # costing a surface its whole day (the 2026-08-03 insight
        # report). Every attempt is ledgered — nothing bypasses logging
        # — and anything that may have billed tokens raises immediately,
        # leaving the per-item attempt ceilings above this layer as the
        # only retry authority for expensive failures.
        attempts_left = 1 + _TRANSIENT_RETRIES
        while True:
            attempts_left -= 1
            started = time.monotonic()
            try:
                result = self._backend.complete(
                    prompt, model=resolved,
                    timeout=timeout or config.LLM_TIMEOUT,
                )
                break
            except TransientLLMError as exc:
                self._log(resolved, purpose, package_id, granule_id, 0, 0,
                          int((time.monotonic() - started) * 1000),
                          error=str(exc)[:500])
                if not attempts_left:
                    raise LLMError(
                        f"{self._backend.name} backend failed ({purpose})"
                        f" after a zero-billed retry: {exc}") from exc
                logger.warning(
                    "LLM %s [%s]: transient zero-billed failure, retrying"
                    " once: %s", self._backend.name, purpose, exc)
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

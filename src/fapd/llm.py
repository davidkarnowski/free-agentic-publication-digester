"""LLM access with a persistent token ledger (GUIDE §6 rules 7–8).

Backends are pluggable (§6 rule 7, amended 2026-07-30). Callers name model
*tiers* (config.MAP_MODEL / COMPOSE_MODEL); config.LLM_MODELS resolves the
concrete model for the selected backend:

- CLIBackend (default): the `claude` CLI in headless mode (`claude -p
  --output-format json`), billed to the operator's Claude subscription.
- AnthropicBackend: the official Anthropic SDK (ANTHROPIC_API_KEY), for
  hosted/VPS runs where no CLI subscription exists.
- GeminiBackend: Google AI Studio over REST (GOOGLE_GEMINI_API_KEY);
  production 2026-08-15 → 08-24 after the CLI backend lost its
  subscription access.
- NullBackend (LLM_BACKEND=none): no provider at all. Every call is
  ledgered and refused, so the pipeline finalizes the day mechanically
  (GUIDE §6 r15) and the ledger still shows what would have been asked.

The ledger (data/llm_ledger.db) is the accountability layer, paralleling
fetch_log.db: every call is recorded — including failures — with the
backend and the resolved model, before anyone looks at the response. Per
§6 rule 8 no cap is enforced yet; the ledger's totals are what will
eventually set it.

Provider availability is a state the client carries, not just an
exception it throws (plan 2026-08-24, FEAT-1): once a quota- or
auth-class failure survives the bounded retry ladder, the client marks
itself unavailable and every later call short-circuits — ledgered, zero
tokens, no HTTP — instead of paying the same refusal thirty more times.
"""

import datetime as dt
import json
import logging
import os
import re
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
    """Any backend failure. `unavailable` is set by the backend when the
    failure is a quota- or auth-class refusal (see LLMClient's breaker):
    a short reason string, or None for an ordinary failure."""

    def __init__(self, message="", *, unavailable=None):
        super().__init__(message)
        self.unavailable = unavailable


class ProviderUnavailableError(LLMError):
    """No inference provider can answer this client for the rest of the
    run: none configured (LLM_BACKEND=none), not authenticated, quota
    exhausted, or the provider refused us. The pipeline reads this — and
    LLMClient.status() — to finalize the day mechanically instead of
    dying (GUIDE §6 r15): every model layer becomes a disclosed gap, the
    render still runs, the gates still judge. `reason` is one of the
    short strings in UNAVAILABLE_REASONS; it goes to the ledger, the
    manifest and the operations report — never into the digest, which
    says only that no inference was available (operator ruling
    2026-08-24)."""

    def __init__(self, reason, message=None):
        super().__init__(message or f"provider unavailable: {reason}",
                         unavailable=reason)
        self.reason = reason


#: The closed set of ProviderUnavailableError.reason values.
UNAVAILABLE_REASONS = ("disabled", "not authenticated", "quota exhausted",
                       "provider refused")


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
    ceilings above this layer stay the authority for those.

    `retry_after`: the provider's own wait hint in seconds (Gemini's
    `retryDelay` / "Please retry in Ns", an HTTP Retry-After), or None.
    LLMClient honors it, capped by config.LLM_RETRY_MAX_WAIT_S."""

    def __init__(self, message="", *, retry_after=None, unavailable=None):
        super().__init__(message, unavailable=unavailable)
        self.retry_after = retry_after


class PromptSizeError(LLMError):
    """A single prompt exceeded config.LLM_MAX_PROMPT_CHARS (review
    R1/D3). An LLMError so the existing retry/ceiling machinery bounds
    it: per-item summaries hit the r14 attempt ceiling, and a compose
    failure at EOD hits the R3 finalizer hard stop — loud either way."""


_RETRY_IN_RE = re.compile(r"retry in\s+([0-9]+(?:\.[0-9]+)?)\s*s", re.IGNORECASE)
_DURATION_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*s?\s*$")


def _seconds(value):
    """'37s' / '36.96s' / '12' -> float seconds, else None."""
    if value is None:
        return None
    m = _DURATION_RE.match(str(value))
    return float(m.group(1)) if m else None


def parse_retry_hint(body_text=None, headers=None):
    """The provider's own wait hint, in seconds, or None.

    Three places it can live: an HTTP Retry-After header (integer
    seconds — the HTTP-date form is not worth the parse here, the cap
    bounds us anyway); Gemini's structured `error.details[].retryDelay`
    ("37s"); and Gemini's message text ("Please retry in 36.96s"). The
    first found wins. Never raises — a hint is a courtesy, not a
    contract."""
    if headers:
        for key, value in headers.items():
            if str(key).lower() == "retry-after":
                secs = _seconds(value)
                if secs is not None:
                    return secs
    if not body_text:
        return None
    try:
        data = json.loads(body_text)
    except (TypeError, ValueError):
        data = None
    if isinstance(data, dict):
        err = data.get("error") or {}
        for detail in err.get("details") or []:
            if isinstance(detail, dict) and detail.get("retryDelay"):
                secs = _seconds(detail["retryDelay"])
                if secs is not None:
                    return secs
        message = str(err.get("message") or "")
        m = _RETRY_IN_RE.search(message)
        if m:
            return float(m.group(1))
    m = _RETRY_IN_RE.search(str(body_text))
    return float(m.group(1)) if m else None


#: Message fragments that mean the provider will refuse every call this
#: run, not just this one — the breaker's classification table for text
#: we cannot classify by HTTP status. Ordered: first match wins.
_UNAVAILABLE_PATTERNS = (
    ("organization has disabled", "provider refused"),
    ("not logged in", "not authenticated"),
    ("invalid api key", "not authenticated"),
    ("authentication", "not authenticated"),
    ("credit balance", "quota exhausted"),
    ("resource_exhausted", "quota exhausted"),
    ("quota", "quota exhausted"),
)


def classify_unavailable(text, status_code=None):
    """Quota/auth-class reason for a failure, or None (an ordinary
    failure — a 5xx, a refusal of one prompt, a parse error). 401/403
    are auth by status; 429 is quota only when the body says so (a bare
    per-minute 429 is a transient the ladder handles). Text patterns
    cover the CLI envelope, which carries no status."""
    if status_code in (401, 403):
        return "not authenticated"
    lowered = (text or "").lower()
    for needle, reason in _UNAVAILABLE_PATTERNS:
        if needle in lowered:
            return reason
    if status_code == 429 and "rate limit" in lowered:
        return "quota exhausted"
    return None


class NullBackend:
    """No provider (LLM_BACKEND=none). Every call raises
    ProviderUnavailableError; LLMClient still ledgers each one, so the
    day's would-be calls are visible in the ledger and the operations
    report even though nothing was asked of anyone. This is the operator's
    deliberate mechanical mode (`--no-llm`), distinct from a provider that
    failed: same digest wording, different ledger reason."""

    name = "none"

    def __init__(self, reason="disabled"):
        self.unavailable = reason

    def complete(self, prompt, *, model, timeout):
        raise ProviderUnavailableError(self.unavailable)


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
        # The 2026-08-14 envelope ("Your organization has disabled Claude
        # subscription access for Claude Code") was zero-billed and
        # therefore retried — 35 times over the next day, identically.
        # Classify it so the breaker stops the run after the ladder.
        unavailable = classify_unavailable(str(data.get("result") or ""))
        if billed == 0 and not data.get("modelUsage"):
            return TransientLLMError(msg + " — zero tokens billed",
                                     unavailable=unavailable)
        return LLMError(msg + f" — {billed} token(s) billed, not retried",
                        unavailable=unavailable)


class AnthropicBackend:
    """The official Anthropic SDK. The client is injectable for tests; the
    SDK import is deferred so CLI-only installs never touch it."""

    name = "api"

    def __init__(self, client=None):
        self.unavailable = None
        if client is None:
            if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
                # The SDK only discovers a missing key on the first
                # request; surface it at construction so the pipeline can
                # decide (mechanical day) before any layer starts.
                self.unavailable = "not authenticated"
                self._client = None
                return
            import anthropic

            client = anthropic.Anthropic()  # ANTHROPIC_API_KEY from env
        self._client = client

    def complete(self, prompt, *, model, timeout):
        if self._client is None:
            raise ProviderUnavailableError(self.unavailable or "not authenticated")
        try:
            resp = self._client.messages.create(
                model=model,
                max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )
        except Exception as exc:  # anthropic.APIError family
            # The SDK already retried 429/5xx internally (its default
            # max_retries=2, honoring retry-after), so no client-side
            # transient retry here — that would double up on a provider
            # that has already told us to wait. What survives the SDK is
            # classified: 401/403 and a rate-limit/credit 429 mean the
            # rest of the run would fail the same way.
            status = getattr(exc, "status_code", None)
            text = str(exc)[:500]
            unavailable = classify_unavailable(text, status)
            if status == 429 and unavailable is None:
                unavailable = "quota exhausted"
            raise LLMError(text, unavailable=unavailable) from exc
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
        # Known at construction, decided by the pipeline (mechanical
        # day), not discovered mid-batch as a stack trace.
        self.unavailable = None if self._api_key else "not authenticated"

    def complete(self, prompt, *, model, timeout):
        if not self._api_key:
            raise ProviderUnavailableError(
                "not authenticated",
                "Gemini API key not found. Set GOOGLE_GEMINI_API_KEY or"
                " GEMINI_API_KEY in environment.",
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
            full_text = getattr(resp, "text", str(resp)) or ""
            err_text = full_text[:500]
            # Zero-billed by definition (no candidates were generated), so
            # the client's ladder may retry — waiting as long as the body
            # asks ("Please retry in 37s" / retryDelay), which the
            # 2026-08-15..23 finalizer runs never read: two calls ~1 s
            # apart, then a dead day. A 429 that names a quota is also
            # the breaker's signal: the free tier's daily count does not
            # come back until midnight Pacific.
            if status_code in (429, 500, 502, 503, 504):
                raise TransientLLMError(
                    f"Gemini API transient error (HTTP {status_code}): {err_text}"
                    " — zero tokens billed",
                    retry_after=parse_retry_hint(
                        full_text, getattr(resp, "headers", None)),
                    unavailable=(classify_unavailable(full_text, status_code)
                                 if status_code == 429 else None),
                )
            raise LLMError(f"Gemini API error (HTTP {status_code}): {err_text}",
                           unavailable=classify_unavailable(full_text, status_code))

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


#: Accepted LLM_BACKEND values -> constructor. "" (unset) means the CLI
#: default; anything else is a configuration error, raised at construction
#: — the old silent fall-through to the CLI (pre-publication-todo
#: "provider-segmented inference") made a typo in .env change billing.
_BACKENDS = {  # thunks: resolved at call time, so the module-level names
    "": lambda: CLIBackend(),  # stay a test seam (test_backend_selected_from_config)
    "cli": lambda: CLIBackend(),
    "api": lambda: AnthropicBackend(),
    "gemini": lambda: GeminiBackend(),
    "google": lambda: GeminiBackend(),
    "none": lambda: NullBackend(),
    "off": lambda: NullBackend(),
    "disabled": lambda: NullBackend(),
}


def backend_from_config(name=None):
    """The backend named by LLM_BACKEND (or `name`), or ValueError."""
    key = (config.LLM_BACKEND if name is None else name).strip().lower()
    try:
        return _BACKENDS[key]()
    except KeyError:
        raise ValueError(
            f"LLM_BACKEND={key!r} is not a backend; accepted:"
            f" {', '.join(sorted(k for k in _BACKENDS if k))}") from None


class LLMClient:
    def __init__(self, db_path=None, runner=None, backend=None, sleeper=None):
        self._db_path = db_path or config.LLM_LEDGER_DB
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self._db_path)
        self._db.executescript(_SCHEMA)
        self._ensure_backend_column()
        if backend is not None:
            self._backend = backend
        elif runner is not None:
            self._backend = CLIBackend(runner)  # existing test seam
        else:
            self._backend = backend_from_config()
        self._sleep = sleeper or time.sleep
        # The per-run breaker (FEAT-1). A backend that already knows it
        # cannot serve (no key, LLM_BACKEND=none) starts tripped; a
        # quota/auth-class failure that survives the ladder trips it
        # later. Once tripped, complete() never touches the backend
        # again on this client — the ledger records each refusal.
        self.unavailable = getattr(self._backend, "unavailable", None)
        self._models_used = set()

    def status(self):
        """What the pipeline discloses and the health surface reads:
        {"backend", "unavailable": reason|None, "models_used": [...]}
        — models_used lists resolved model names that returned a
        completion on THIS client (the r7 attribution the digest owes),
        so a client that never got an answer reports an empty list."""
        return {"backend": self._backend.name,
                "unavailable": self.unavailable,
                "models_used": sorted(self._models_used)}

    def _trip(self, reason, purpose):
        if not self.unavailable:
            logger.error(
                "LLM %s: provider unavailable for the rest of this run"
                " (%s) — first seen on %s; later calls short-circuit",
                self._backend.name, reason, purpose)
            self.unavailable = reason

    def complete(self, prompt, *, purpose, model=None, package_id=None,
                 granule_id=None, timeout=None):
        """One text-in/text-out completion. Records the call in the ledger
        (success or failure) and returns
        {"text", "input_tokens", "output_tokens", "model"} — "model" is the
        resolved concrete model, not the tier alias."""
        tier = model or config.MAP_MODEL
        resolved = config.LLM_MODELS.get(self._backend.name, {}).get(tier, tier)
        if self.unavailable:
            # Short-circuit: ledgered (nothing bypasses logging), no
            # backend work, no wait. The reason is the breaker's, and
            # "(short-circuit)" tells the ledger reader this row cost no
            # HTTP request — the earlier row without it did.
            self._log(resolved, purpose, package_id, granule_id, 0, 0, 0,
                      error=f"provider unavailable: {self.unavailable}"
                            " (short-circuit)")
            raise ProviderUnavailableError(self.unavailable)
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
        # Bounded retries for verifiably zero-billed transient failures
        # (TransientLLMError) ONLY: a failed attempt that cost nothing
        # cannot double-spend, so a hiccup stops costing a surface its
        # whole day (the 2026-08-03 insight report). Up to
        # config.LLM_TRANSIENT_ATTEMPTS calls, waiting the provider's own
        # hint when it gave one (else 2**attempt s), capped at
        # LLM_RETRY_MAX_WAIT_S. History: one immediate retry, ~1 s after
        # a 429 asking for 37 s, was the whole ladder from 2026-08-16
        # (3e88577) to 08-24 — eight halted finalizers. Every attempt is
        # ledgered — nothing bypasses logging — and anything that may
        # have billed tokens raises immediately, leaving the per-item
        # attempt ceilings above this layer as the only retry authority
        # for expensive failures.
        max_attempts = max(1, config.LLM_TRANSIENT_ATTEMPTS)
        attempt = 0
        while True:
            attempt += 1
            started = time.monotonic()
            try:
                result = self._backend.complete(
                    prompt, model=resolved,
                    timeout=timeout or config.LLM_TIMEOUT,
                )
                break
            except ProviderUnavailableError as exc:
                # The backend itself knows it cannot serve (NullBackend,
                # a key that is missing) — trip without a ladder.
                self._log(resolved, purpose, package_id, granule_id, 0, 0,
                          int((time.monotonic() - started) * 1000),
                          error=f"provider unavailable: {exc.reason}")
                self._trip(exc.reason, purpose)
                raise
            except TransientLLMError as exc:
                self._log(resolved, purpose, package_id, granule_id, 0, 0,
                          int((time.monotonic() - started) * 1000),
                          error=str(exc)[:500])
                if attempt >= max_attempts:
                    if exc.unavailable:
                        # The ladder is exhausted on a refusal that will
                        # not change this run: quota, auth. Trip.
                        self._trip(exc.unavailable, purpose)
                        raise ProviderUnavailableError(
                            exc.unavailable,
                            f"{self._backend.name} backend unavailable"
                            f" ({purpose}) after {attempt} zero-billed"
                            f" attempt(s): {exc}") from exc
                    raise LLMError(
                        f"{self._backend.name} backend failed ({purpose})"
                        f" after {attempt} zero-billed attempt(s): {exc}"
                    ) from exc
                wait = exc.retry_after if exc.retry_after else float(2 ** attempt)
                wait = min(wait, float(config.LLM_RETRY_MAX_WAIT_S))
                logger.warning(
                    "LLM %s [%s]: transient zero-billed failure (attempt"
                    " %d/%d), waiting %.0fs%s: %s", self._backend.name,
                    purpose, attempt, max_attempts, wait,
                    " (provider hint)" if exc.retry_after else "", exc)
                self._sleep(wait)
            except LLMError as exc:
                self._log(resolved, purpose, package_id, granule_id, 0, 0,
                          int((time.monotonic() - started) * 1000),
                          error=str(exc)[:500])
                if exc.unavailable:
                    self._trip(exc.unavailable, purpose)
                    raise ProviderUnavailableError(
                        exc.unavailable,
                        f"{self._backend.name} backend unavailable"
                        f" ({purpose}): {exc}") from exc
                raise LLMError(
                    f"{self._backend.name} backend failed ({purpose}): {exc}"
                ) from exc
        duration_ms = int((time.monotonic() - started) * 1000)
        self._models_used.add(resolved)
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

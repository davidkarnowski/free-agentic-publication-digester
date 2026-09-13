"""The validation layer, stages L1 (pure part), L2 and L3.

Pure functions of ``(headers, body_bytes, manifest)``: no socket, no
filesystem. ``server.py`` calls :func:`validate_headers` before it reads a
request body (so an oversize or mis-typed request is refused without
reading it) and :func:`validate_body` afterwards; tests call
:func:`validate_request` for both in one step.

Stages (see the package README, "Security model"):

* **L1 HTTP** — ``Content-Length`` present and within the cap;
  ``Content-Type`` is ``application/json`` (optional ``charset=utf-8``);
  ``Accept`` absent or listing ``application/json`` or ``*/*``; ``Host``
  in ``allowed_hosts``; ``Origin`` absent-and-allowed or in
  ``allowed_origins``; every ``Mcp-*`` header at most 1,024 bytes of
  visible ASCII.
* **L2 bytes → JSON** — strict UTF-8; nesting depth at most 32, measured by
  a scanner over the raw text before the recursive parser runs; ``NaN`` /
  ``Infinity`` rejected; integers capped at 20 digits; floats finite;
  duplicate keys rejected; then one walk rejecting control characters
  (other than tab, newline, carriage return) in any string, strings over
  8 KiB, objects over 256 keys, arrays over 1,024 items. Failure → 400,
  ``-32700``, ``"id": null``.
* **L3 JSON-RPC envelope** — a single object (an array is "batching is not
  supported"); ``jsonrpc == "2.0"``; ``method`` matches
  ``^[a-z][a-zA-Z0-9_/]{0,63}$``; ``id`` absent (notification), a string of
  at most 128 characters, or an integer within ±2^53; ``params`` absent or
  an object; no other top-level keys; ``params._meta`` (if present) an
  object of at most 64 spec-shaped keys and at most 8 KiB serialized.
  Failure → 400, ``-32600``, ``"id": null`` (a rejected id is never echoed).
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from static_mcp.errors import (
    HEADER_MISMATCH,
    INVALID_REQUEST,
    PARSE_ERROR,
    Rejection,
)

MAX_DEPTH = 32
MAX_STRING_BYTES = 8192
MAX_OBJECT_KEYS = 256
MAX_ARRAY_ITEMS = 1024
MAX_INT_DIGITS = 20
MAX_FLOAT_CHARS = 64
MAX_ID_CHARS = 128
MAX_SAFE_INT = 2**53
MAX_HEADER_BYTES = 1024
MAX_META_KEYS = 64
MAX_META_BYTES = 8192

METHOD_RE = re.compile(r"^[a-z][a-zA-Z0-9_/]{0,63}$", re.ASCII)

# _meta key names (basic/index.mdx "General fields > _meta"): an optional
# dotted-label prefix ending in "/", then a name that begins and ends with
# an alphanumeric and may contain "-", "_", "." in between (or is empty).
_LABEL = r"[A-Za-z](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
META_KEY_RE = re.compile(
    rf"^(?:{_LABEL}(?:\.{_LABEL})*/)?(?:[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)?$",
    re.ASCII,
)

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_VISIBLE_ASCII_RE = re.compile(r"^[\x20-\x7e]*$")


@dataclass(frozen=True)
class Envelope:
    """A JSON-RPC request or notification that passed L2 and L3."""

    method: str
    rpc_id: Any  # None for a notification; otherwise a str or int
    is_notification: bool
    params: dict[str, Any] | None
    meta: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- helpers


def lower_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Return a copy of ``headers`` with lower-cased names."""
    return {str(k).lower(): str(v) for k, v in headers.items()}


def _host_without_port(host: str) -> str:
    host = host.strip()
    if host.startswith("["):
        end = host.find("]")
        return host[1 : end if end > 0 else len(host)].lower()
    name, sep, port = host.rpartition(":")
    if sep and port.isdigit():
        return name.lower()
    return host.lower()


def _content_type_is_json(value: str) -> bool:
    media, _, rest = value.partition(";")
    if media.strip().lower() != "application/json":
        return False
    for param in rest.split(";"):
        param = param.strip()
        if not param:
            continue
        name, _, val = param.partition("=")
        if name.strip().lower() != "charset":
            return False
        if val.strip().strip('"').lower() != "utf-8":
            return False
    return True


def _accept_allows_json(value: str) -> bool:
    for entry in value.split(","):
        media, _, rest = entry.partition(";")
        media = media.strip().lower()
        if media not in ("application/json", "*/*", "application/*"):
            continue
        q_zero = False
        for param in rest.split(";"):
            name, _, val = param.strip().partition("=")
            if name.strip().lower() == "q":
                try:
                    q_zero = float(val.strip()) <= 0.0
                except ValueError:
                    q_zero = True
        if not q_zero:
            return True
    return False


# --------------------------------------------------------------------------- L1


def validate_headers(headers: Mapping[str, str], manifest: Any) -> int:
    """Stage L1 (the pure part). Returns the declared ``Content-Length``.

    ``manifest`` needs ``.http`` with ``allowed_hosts``, ``allowed_origins``,
    ``allow_missing_origin`` and ``max_body_bytes``.
    """
    h = lower_headers(headers)
    http = manifest.http

    host = h.get("host")
    if host is None or _host_without_port(host) not in http.allowed_hosts:
        raise Rejection(403, INVALID_REQUEST, "Host not allowed", stage="L1", event="l1.host")

    origin = h.get("origin")
    if origin is None:
        if not http.allow_missing_origin:
            raise Rejection(403, INVALID_REQUEST, "Origin required", stage="L1", event="l1.origin")
    elif origin.strip().lower() not in http.allowed_origins:
        raise Rejection(403, INVALID_REQUEST, "Origin not allowed", stage="L1", event="l1.origin")

    length_text = h.get("content-length")
    if length_text is None:
        raise Rejection(411, INVALID_REQUEST, "Content-Length required", stage="L1")
    if not length_text.strip().isdigit():
        raise Rejection(400, INVALID_REQUEST, "Content-Length invalid", stage="L1")
    length = int(length_text.strip())
    if length > http.max_body_bytes:
        raise Rejection(413, INVALID_REQUEST, "Request body too large", stage="L1")

    content_type = h.get("content-type")
    if content_type is None or not _content_type_is_json(content_type):
        raise Rejection(415, INVALID_REQUEST, "Content-Type must be application/json", stage="L1")

    accept = h.get("accept")
    if accept is not None and not _accept_allows_json(accept):
        raise Rejection(406, INVALID_REQUEST, "Accept must allow application/json", stage="L1")

    for name, value in h.items():
        if not name.startswith("mcp-"):
            continue
        if len(value.encode("utf-8", "surrogateescape")) > MAX_HEADER_BYTES:
            raise Rejection(
                400, HEADER_MISMATCH, f"Header {name} too long", stage="L1", event="l1.header"
            )
        if not _VISIBLE_ASCII_RE.match(value):
            raise Rejection(
                400,
                HEADER_MISMATCH,
                f"Header {name} contains invalid characters",
                stage="L1",
                event="l1.header",
            )
    return length


# --------------------------------------------------------------------------- L2


def _reject_constant(name: str) -> Any:
    raise ValueError(f"non-finite number {name}")


def _capped_int(text: str) -> int:
    if len(text.lstrip("-")) > MAX_INT_DIGITS:
        raise ValueError("integer too long")
    return int(text)


def _finite_float(text: str) -> float:
    if len(text) > MAX_FLOAT_CHARS:
        raise ValueError("number too long")
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("non-finite number")
    return value


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def scan_depth(text: str) -> int:
    """Return the maximum bracket nesting depth of ``text``, ignoring strings.

    A linear scan; it never recurses, so a 64 KiB body of ``[[[[…`` is
    measured, not parsed. Runs before ``json.loads``.
    """
    depth = 0
    deepest = 0
    in_string = False
    escaped = False
    for ch in text:
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "[{":
            depth += 1
            if depth > deepest:
                deepest = depth
                if deepest > MAX_DEPTH:
                    return deepest
        elif ch in "]}":
            depth -= 1
    return deepest


def _walk(value: Any) -> None:
    """Reject control characters, long strings, wide objects and long arrays."""
    if isinstance(value, str):
        _check_string(value)
    elif isinstance(value, dict):
        if len(value) > MAX_OBJECT_KEYS:
            raise ValueError("object too large")
        for key, item in value.items():
            _check_string(key)
            _walk(item)
    elif isinstance(value, list):
        if len(value) > MAX_ARRAY_ITEMS:
            raise ValueError("array too large")
        for item in value:
            _walk(item)


def _check_string(value: str) -> None:
    if _CONTROL_RE.search(value):
        raise ValueError("control character in string")
    if len(value) > MAX_STRING_BYTES or len(value.encode("utf-8")) > MAX_STRING_BYTES:
        raise ValueError("string too long")


def parse_json(body: bytes) -> Any:
    """Stage L2. Returns the parsed value or raises :class:`Rejection` (-32700)."""
    try:
        text = body.decode("utf-8", "strict")
    except UnicodeDecodeError:
        raise Rejection(400, PARSE_ERROR, "Body is not valid UTF-8", rpc_id=None, stage="L2")
    if scan_depth(text) > MAX_DEPTH:
        raise Rejection(400, PARSE_ERROR, "JSON nesting too deep", rpc_id=None, stage="L2")
    try:
        value = json.loads(
            text,
            parse_constant=_reject_constant,
            parse_int=_capped_int,
            parse_float=_finite_float,
            object_pairs_hook=_no_duplicates,
        )
        _walk(value)
    except (ValueError, RecursionError, TypeError):
        raise Rejection(400, PARSE_ERROR, "Body is not acceptable JSON", rpc_id=None, stage="L2")
    return value


# --------------------------------------------------------------------------- L3


def _invalid(message: str) -> Rejection:
    return Rejection(400, INVALID_REQUEST, message, rpc_id=None, stage="L3")


def validate_envelope(value: Any) -> Envelope:
    """Stage L3. Returns an :class:`Envelope` or raises :class:`Rejection` (-32600)."""
    if isinstance(value, list):
        raise _invalid("Batching is not supported")
    if not isinstance(value, dict):
        raise _invalid("Request must be a JSON object")
    extra = set(value) - {"jsonrpc", "id", "method", "params"}
    if extra:
        raise _invalid("Unexpected member in request")
    if value.get("jsonrpc") != "2.0":
        raise _invalid("jsonrpc must be \"2.0\"")
    method = value.get("method")
    if not isinstance(method, str) or not METHOD_RE.match(method):
        raise _invalid("method is missing or malformed")

    is_notification = "id" not in value
    rpc_id: Any = None
    if not is_notification:
        rpc_id = value["id"]
        if isinstance(rpc_id, bool):
            raise _invalid("id must be a string or an integer")
        if isinstance(rpc_id, int):
            if abs(rpc_id) > MAX_SAFE_INT:
                raise _invalid("id out of range")
        elif isinstance(rpc_id, str):
            if len(rpc_id) > MAX_ID_CHARS:
                raise _invalid("id too long")
        else:
            raise _invalid("id must be a string or an integer")

    params = value.get("params")
    if params is not None and not isinstance(params, dict):
        raise _invalid("params must be an object")

    meta: dict[str, Any] = {}
    if params is not None and "_meta" in params:
        raw_meta = params["_meta"]
        if not isinstance(raw_meta, dict):
            raise _invalid("params._meta must be an object")
        if len(raw_meta) > MAX_META_KEYS:
            raise _invalid("params._meta has too many keys")
        for key in raw_meta:
            if not key or not META_KEY_RE.match(key):
                raise _invalid("params._meta contains a malformed key")
        if len(json.dumps(raw_meta, ensure_ascii=False).encode("utf-8")) > MAX_META_BYTES:
            raise _invalid("params._meta too large")
        meta = {k: v for k, v in raw_meta.items() if k.startswith("io.modelcontextprotocol/")}

    return Envelope(
        method=method,
        rpc_id=rpc_id,
        is_notification=is_notification,
        params=params,
        meta=meta,
    )


def validate_body(body: bytes, *, max_body_bytes: int | None = None) -> Envelope:
    """Stages L2 and L3 on a body that has already been read."""
    if max_body_bytes is not None and len(body) > max_body_bytes:
        raise Rejection(413, INVALID_REQUEST, "Request body too large", stage="L1")
    return validate_envelope(parse_json(body))


def validate_request(headers: Mapping[str, str], body: bytes, manifest: Any) -> Envelope:
    """L1 (pure part) + L2 + L3 in order. The testable whole."""
    validate_headers(headers, manifest)
    return validate_body(body, max_body_bytes=manifest.http.max_body_bytes)

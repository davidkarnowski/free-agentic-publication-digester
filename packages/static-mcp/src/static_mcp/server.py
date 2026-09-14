"""The HTTP layer (stage L1, socket part): limits, Origin/Host checks, logging, /healthz.

Built on ``http.server.ThreadingHTTPServer`` with ``HTTP/1.1`` (every
response carries ``Content-Length``). The standard library's HTTP server
is not hardened for direct internet exposure; the design assumes a
reverse proxy in front that buffers request bodies and applies timeouts
and rate limits (README, "Put a reverse proxy in front").

Behavior:

* ``GET /healthz`` → 200 ``ok`` (text/plain), for container health checks.
* ``POST <endpoint_path>`` → the validation layer
  (:func:`static_mcp.dispatch.handle_request`) after the pure L1 header
  checks; an oversize, mis-typed or unlisted-Host request is refused
  before its body is read.
* ``GET`` / ``DELETE`` / anything else on the endpoint → 405 ``Allow: POST``.
* any other path → 404. ``max_concurrency`` requests in flight → 503
  ``Retry-After: 1``.
* Every response: ``Cache-Control: no-store``, ``X-Content-Type-Options:
  nosniff``. Never SSE; ``Mcp-Session-Id`` and ``Last-Event-ID`` request
  headers are ignored and no session header is ever sent.

Logging: one JSON object per request on the injected writer (stdout by
default): ``ts``, ``http_method``, ``path``, ``status``, ``rpc_method``,
``mcp_name``, ``era``, ``protocol_version``, ``duration_ms``,
``response_bytes``, ``user_agent`` (200 chars), ``event``. Never logged:
the client address, the request body, arguments, or any other header.
The base class's own request logging (which prints the client address)
is disabled.

Seams (optional keyword parameters): ``log_writer``, ``error_writer``,
``clock`` (monotonic seconds), ``utcnow`` (aware datetime).
"""

from __future__ import annotations

import json
import re
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from static_mcp.dispatch import Response, handle_request
from static_mcp.errors import HEADER_MISMATCH, INVALID_REQUEST, Rejection, error_body
from static_mcp.handlers import Store
from static_mcp.manifest import Manifest

_UA_CLEAN_RE = re.compile(r"[^\x20-\x7e]")
_MAX_UA = 200
# A proxy-assigned request id is an opaque token; anything else is logged
# as "(invalid)" so a client cannot write free text into the log field.
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_LOG_FIELDS = (
    "ts",
    "http_method",
    "path",
    "status",
    "rpc_method",
    "mcp_name",
    "era",
    "protocol_version",
    "duration_ms",
    "response_bytes",
    "user_agent",
    "request_id",
    "event",
)


class App:
    """Everything a request handler needs, shared across handler threads."""

    def __init__(
        self,
        manifest: Manifest,
        store: Store,
        *,
        log_writer: Callable[[str], Any] | None = None,
        error_writer: Callable[[str], Any] | None = None,
        clock: Callable[[], float] | None = None,
        utcnow: Callable[[], datetime] | None = None,
    ) -> None:
        self.manifest = manifest
        self.store = store
        self.log_writer = log_writer or _stdout_writer
        self.error_writer = error_writer or _stderr_writer
        self.clock = clock or time.monotonic
        self.utcnow = utcnow or (lambda: datetime.now(UTC))
        self.slots = threading.BoundedSemaphore(manifest.http.max_concurrency)
        self.timeout = manifest.http.request_timeout_seconds

    def log(self, fields: dict[str, Any]) -> None:
        line = {name: fields.get(name) for name in _LOG_FIELDS}
        self.log_writer(json.dumps(line, ensure_ascii=True, separators=(",", ":")) + "\n")


def _stdout_writer(line: str) -> None:
    import sys

    sys.stdout.write(line)
    sys.stdout.flush()


def _stderr_writer(text: str) -> None:
    import sys

    sys.stderr.write(text)
    sys.stderr.flush()


class StaticMcpServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], app: App) -> None:
        self.app = app
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "static-mcp"
    sys_version = ""
    error_message_format = '{"jsonrpc":"2.0","error":{"code":-32600,"message":"%(explain)s"}}'
    error_content_type = "application/json"

    server: StaticMcpServer  # type: ignore[assignment]

    # -- silence the base class (it would print the client address) ---------

    def log_message(self, format: str, *args: Any) -> None:
        return

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        return

    def version_string(self) -> str:
        return "static-mcp"

    def setup(self) -> None:
        self.timeout = self.server.app.timeout
        super().setup()

    # -- plumbing --------------------------------------------------------------

    def _write(
        self,
        status: int,
        body: bytes | None,
        *,
        content_type: str = "application/json",
        extra: dict[str, str] | None = None,
        close: bool = False,
    ) -> int:
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body) if body is not None else 0))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        if close:
            self.send_header("Connection", "close")
            self.close_connection = True
        self.end_headers()
        if body:
            self.wfile.write(body)
        return len(body) if body is not None else 0

    def _log(self, status: int, size: int, started: float, fields: dict[str, Any]) -> None:
        app = self.server.app
        ua = self.headers.get("User-Agent", "") or ""
        rid_header = app.manifest.http.request_id_header
        request_id = None
        if rid_header:
            raw_rid = self.headers.get(rid_header)
            if raw_rid is not None:
                request_id = raw_rid if _REQUEST_ID_RE.match(raw_rid) else "(invalid)"
        record = {
            "ts": app.utcnow().isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "http_method": self.command,
            "path": self._safe_path(),
            "status": status,
            "duration_ms": round((app.clock() - started) * 1000, 3),
            "response_bytes": size,
            "user_agent": _UA_CLEAN_RE.sub("", ua)[:_MAX_UA],
            "request_id": request_id,
            **fields,
        }
        app.log(record)

    def _safe_path(self) -> str:
        """The path is client-controlled; log it only when it names something we serve."""
        if self.path == self.server.app.manifest.endpoint_path:
            return self.path
        if self.path == "/healthz":
            return self.path
        return "(other)"

    def _rejection(self, rej: Rejection, started: float, *, close: bool) -> None:
        body = json.dumps(rej.body(), ensure_ascii=False, separators=(",", ":")).encode()
        size = self._write(rej.http_status, body, close=close)
        self._log(rej.http_status, size, started, {"event": rej.event or f"rejected.{rej.stage}"})

    # -- methods ---------------------------------------------------------------

    def do_GET(self) -> None:
        started = self.server.app.clock()
        if self.path == "/healthz":
            size = self._write(200, b"ok", content_type="text/plain; charset=utf-8")
            self._log(200, size, started, {})
            return
        self._not_post(started)

    def do_POST(self) -> None:
        app = self.server.app
        started = app.clock()
        if self.path != app.manifest.endpoint_path:
            size = self._write(404, _plain_error("Not found"), close=True)
            self._log(404, size, started, {})
            return
        if not app.slots.acquire(blocking=False):
            size = self._write(
                503, _plain_error("Too many requests in flight"),
                extra={"Retry-After": "1"}, close=True,
            )
            self._log(503, size, started, {"event": "l1.concurrency"})
            return
        try:
            self._post(started)
        finally:
            app.slots.release()

    def _post(self, started: float) -> None:
        app = self.server.app
        headers: dict[str, str] = {}
        for name, value in self.headers.items():
            lname = name.lower()
            if lname in headers:
                if lname.startswith("mcp-"):
                    self._rejection(
                        Rejection(400, HEADER_MISMATCH, f"Duplicate header {lname}",
                                  stage="L1", event="l1.header"),
                        started, close=True,
                    )
                    return
                continue
            headers[lname] = value
        from static_mcp.validate import validate_headers

        try:
            length = validate_headers(headers, app.manifest)
        except Rejection as rej:
            self._rejection(rej, started, close=True)
            return
        try:
            body = self.rfile.read(length)
        except TimeoutError:
            self._rejection(
                Rejection(408, INVALID_REQUEST, "Request body timed out", stage="L1",
                          event="l1.timeout"),
                started, close=True,
            )
            return
        except OSError:
            self.close_connection = True
            return
        if len(body) != length:
            self._rejection(
                Rejection(400, INVALID_REQUEST, "Request body incomplete", stage="L1"),
                started, close=True,
            )
            return
        response: Response = handle_request(
            headers, body, app.manifest, app.store, error_writer=app.error_writer
        )
        extra: dict[str, str] = {}
        if response.status == 503:
            extra["Retry-After"] = "1"
        size = self._write(response.status, response.body, extra=extra)
        self._log(response.status, size, started, response.log)

    def _not_post(self, started: float) -> None:
        if self.path == self.server.app.manifest.endpoint_path:
            size = self._write(
                405, _plain_error("Use POST"), extra={"Allow": "POST"}, close=True
            )
            self._log(405, size, started, {})
            return
        size = self._write(404, _plain_error("Not found"), close=True)
        self._log(404, size, started, {})

    def do_DELETE(self) -> None:
        self._not_post(self.server.app.clock())

    def do_PUT(self) -> None:
        self._not_post(self.server.app.clock())

    def do_PATCH(self) -> None:
        self._not_post(self.server.app.clock())

    def do_HEAD(self) -> None:
        self._not_post(self.server.app.clock())

    def do_OPTIONS(self) -> None:
        self._not_post(self.server.app.clock())


def _plain_error(message: str) -> bytes:
    return json.dumps(
        error_body(INVALID_REQUEST, message), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def make_server(
    manifest: Manifest,
    store: Store,
    host: str = "127.0.0.1",
    port: int = 8080,
    **seams: Any,
) -> StaticMcpServer:
    """Bind a server (port 0 picks an ephemeral port). Call ``serve_forever`` to run it."""
    return StaticMcpServer((host, port), App(manifest, store, **seams))

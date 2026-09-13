"""Shared helpers for the static-mcp tests (a plain module, imported by name).

Kept out of ``conftest.py`` so test modules can import it explicitly:
another repository's test tree may carry its own rootless ``conftest``
module, and ``from conftest import …`` would then depend on import order.
"""

from __future__ import annotations

import http.client
import json
import socket
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parent
SRC = PACKAGE_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from static_mcp.handlers import Store
from static_mcp.manifest import Manifest, parse_manifest
from static_mcp.server import make_server

FIXTURES = HERE / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"
EXAMPLE_MANIFEST_PATH = PACKAGE_ROOT / "examples" / "docs-site.manifest.json"

MODERN = "2026-07-28"
MODERN_META = {
    "io.modelcontextprotocol/protocolVersion": MODERN,
    "io.modelcontextprotocol/clientInfo": {"name": "tests", "version": "0"},
    "io.modelcontextprotocol/clientCapabilities": {},
}
BASE_HEADERS = {
    "Host": "localhost",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def manifest_dict() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def build_manifest(**overrides: Any) -> Manifest:
    """The fixture manifest with top-level keys replaced (one-level merge for dicts)."""
    data = manifest_dict()
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(data.get(key), dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    return parse_manifest(data)


def modern_headers(method: str, name: str | None = None) -> dict[str, str]:
    h = {"MCP-Protocol-Version": MODERN, "Mcp-Method": method}
    if name is not None:
        h["Mcp-Name"] = name
    return h


def modern_request(rpc_id: Any, method: str, params: dict | None = None) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "method": method,
        "params": {**(params or {}), "_meta": dict(MODERN_META)},
    }


def legacy_request(rpc_id: Any, method: str, params: dict | None = None) -> dict:
    msg: dict[str, Any] = {"jsonrpc": "2.0", "id": rpc_id, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


def in_process(manifest: Manifest, store: Store, msg: Any, headers: dict | None = None,
               *, raw: bytes | None = None):
    """Run one request through ``handle_request``; returns (status, decoded body, log)."""
    from static_mcp.dispatch import handle_request

    body = raw if raw is not None else json.dumps(msg).encode("utf-8")
    h = {**BASE_HEADERS, "Content-Length": str(len(body)), **(headers or {})}
    h = {k: v for k, v in h.items() if v is not None}
    resp = handle_request(h, body, manifest, store)
    decoded = json.loads(resp.body) if resp.body else None
    return resp.status, decoded, resp.log


@dataclass
class RunningServer:
    server: Any
    port: int
    log_lines: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def endpoint(self) -> str:
        return self.server.app.manifest.endpoint_path

    @property
    def store(self) -> Store:
        return self.server.app.store

    def post(self, body: bytes | dict | list, headers: dict[str, str] | None = None, *,
             path: str | None = None) -> tuple[int, dict[str, str], bytes]:
        """POST with http.client (which sets Content-Length itself)."""
        raw = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        h = {**BASE_HEADERS, **(headers or {})}
        h = {k: v for k, v in h.items() if v is not None}
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.request("POST", path or self.endpoint, body=raw, headers=h)
            resp = conn.getresponse()
            return resp.status, {k.lower(): v for k, v in resp.getheaders()}, resp.read()
        finally:
            conn.close()

    def request(self, method: str, path: str, headers: dict[str, str] | None = None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.request(method, path, headers={"Host": "localhost", **(headers or {})})
            resp = conn.getresponse()
            return resp.status, {k.lower(): v for k, v in resp.getheaders()}, resp.read()
        finally:
            conn.close()

    def raw(self, headers: list[tuple[str, str]], body: bytes, *, method: str = "POST",
            path: str | None = None, timeout: float = 10) -> tuple[int, dict[str, str], bytes]:
        """Send an exact request over a socket; nothing is added or normalized."""
        lines = [f"{method} {path or self.endpoint} HTTP/1.1"]
        lines += [f"{k}: {v}" for k, v in headers]
        head = ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1")
        with socket.create_connection(("127.0.0.1", self.port), timeout=timeout) as sock:
            sock.sendall(head + body)
            resp = http.client.HTTPResponse(sock, method=method)
            resp.begin()
            data = resp.read()
            return resp.status, {k.lower(): v for k, v in resp.getheaders()}, data

    def logs(self) -> list[dict[str, Any]]:
        return [json.loads(line) for line in self.log_lines]

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def start_server(manifest: Manifest, store: Store) -> RunningServer:
    handle = RunningServer(server=None, port=0)
    server = make_server(
        manifest, store, "127.0.0.1", 0,
        log_writer=handle.log_lines.append, error_writer=handle.errors.append,
    )
    handle.server = server
    handle.port = server.server_address[1]
    # A short poll interval keeps shutdown() (called in every teardown) from
    # waiting out the 0.5 s default.
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02},
                     daemon=True).start()
    return handle

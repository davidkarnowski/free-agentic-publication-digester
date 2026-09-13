"""Security (A.6 #6): containment through a permissive test-only handler, oversize body,
slow client, concurrency cap, no tracebacks in responses, logs without body/args/address."""

from __future__ import annotations

import json
import re
import socket
import time

import pytest
from support_static_mcp import (
    build_manifest,
    legacy_request,
    modern_headers,
    modern_request,
    start_server,
)

from static_mcp.errors import ContainmentError
from static_mcp.handlers import Store, run_tool
from static_mcp.manifest import ParamSpec, ToolParam, ToolSpec


def _permissive_tool() -> ToolSpec:
    """A handler the manifest validator would never accept: the path is the argument."""
    spec = ParamSpec("path", "string", "any", "^.*$", re.compile("^.*$"), None, None, 4096)
    return ToolSpec(
        name="raw", title="raw", description="raw", params={"path": ToolParam(spec, True)},
        preamble=None, input_schema={},
        handler={"kind": "text_file", "file": "{path}", "mime_type": "text/plain",
                 "not_found": "missing"},
    )


@pytest.mark.parametrize("path", ["../outside.txt", "notes/../../outside.txt", "notes/escape.md",
                                  "pages/2026-02-02.md"])
def test_resolve_check_alone_stops_escape(store, path):
    with pytest.raises(ContainmentError):
        run_tool(store, _permissive_tool(), {"path": path})


def test_resolve_check_stops_absolute_path(store, tmp_path):
    with pytest.raises(ContainmentError):
        run_tool(store, _permissive_tool(), {"path": str(tmp_path / "outside.txt")})


def test_escape_through_http_is_internal_error_with_security_event(running):
    status, _, body = running.post(
        modern_request(1, "tools/call", {"name": "get_note", "arguments": {"slug": "escape"}}),
        modern_headers("tools/call", "get_note"),
    )
    data = json.loads(body)
    assert status == 200 and data["error"] == {"code": -32603, "message": "Internal error"}
    assert data["id"] == 1
    assert running.logs()[-1]["event"] == "security.path_escape"
    uri = "https://fixture.example.org/pages/2026-02-02.md"
    status, _, body = running.post(modern_request(2, "resources/read", {"uri": uri}),
                                   modern_headers("resources/read", uri))
    assert json.loads(body)["error"]["code"] == -32603
    assert "outside" not in body.decode()


def test_oversize_body_is_413_before_reading(running):
    big = b"[" + b"1," * 40000 + b"1]"
    status, headers, _ = running.post(big)
    assert status == 413 and headers.get("connection") == "close"


def test_slow_client_hits_timeout(site, manifest):
    server = start_server(build_manifest(http={"request_timeout_seconds": 1}),
                          Store(site, manifest.limits))
    try:
        started = time.monotonic()
        status, _, _ = server.raw(
            [("Host", "localhost"), ("Content-Type", "application/json"),
             ("Content-Length", "100")],
            b'{"jsonrpc"',
            timeout=10,
        )
        assert status == 408
        assert time.monotonic() - started < 5
    finally:
        server.stop()


def test_concurrency_cap_yields_503(site, manifest):
    server = start_server(build_manifest(http={"max_concurrency": 1, "request_timeout_seconds": 5}),
                          Store(site, manifest.limits))
    try:
        holder = socket.create_connection(("127.0.0.1", server.port), timeout=10)
        holder.sendall(
            f"POST {server.endpoint} HTTP/1.1\r\nHost: localhost\r\n"
            "Content-Type: application/json\r\nContent-Length: 50\r\n\r\n{".encode()
        )
        time.sleep(0.2)  # let the holder occupy the only slot
        status, headers, body = server.post(legacy_request(1, "ping"))
        assert status == 503
        assert headers["retry-after"] == "1"
        assert "error" in json.loads(body)
        holder.close()
        time.sleep(0.2)
        assert server.post(legacy_request(2, "ping"))[0] == 200
        assert any(line["event"] == "l1.concurrency" for line in server.logs())
    finally:
        server.stop()


def test_no_traceback_in_response(running):
    def boom(rel):
        raise RuntimeError("secret detail /srv/site")

    running.store.read_text = boom  # a direct substitution on the test's own store object
    status, _, body = running.post(
        modern_request(3, "tools/call", {"name": "get_page", "arguments": {"date": "2026-01-01"}}),
        modern_headers("tools/call", "get_page"),
    )
    text = body.decode()
    assert status == 200
    assert json.loads(body)["error"] == {"code": -32603, "message": "Internal error"}
    assert "Traceback" not in text and "secret detail" not in text and "/srv/site" not in text
    assert any("Traceback" in e and "secret detail" in e for e in running.errors)
    assert running.logs()[-1]["event"] == "internal_error"


def test_logs_carry_no_body_arguments_or_address(running):
    token = "zz9f8e7d6c5b"
    running.post(
        modern_request("id-" + token, "tools/call",
                       {"name": "get_note", "arguments": {"slug": token}}),
        modern_headers("tools/call", "get_note"),
        )
    running.post(legacy_request(1, "tools/call", {"name": "get_note",
                                                  "arguments": {"bogus_" + token: 1}}))
    running.post(legacy_request(1, "resources/read",
                                {"uri": "https://fixture.example.org/notes/" + token + ".md"}))
    running.post(legacy_request(1, "tools/call", {"name": token, "arguments": {}}))
    joined = "\n".join(running.log_lines)
    assert token not in joined
    assert "127.0.0.1" not in joined
    assert '"jsonrpc"' not in joined
    assert "Authorization" not in joined


def test_error_messages_never_echo_client_values(running):
    token = "zz9f8e7d6c5b"
    responses = [
        running.post(legacy_request(1, "tools/call", {"name": token}))[2],
        running.post(legacy_request(1, "tools/call", {"name": "get_note",
                                                      "arguments": {token: 1}}))[2],
        running.post(legacy_request(1, "tools/call", {"name": "get_note",
                                                      "arguments": {"slug": token.upper()}}))[2],
        running.post(legacy_request(1, "resources/read", {"uri": "x:" + token}))[2],
        running.post(modern_request(1, "tools/call", {"name": "about", "arguments": {}}),
                     modern_headers("tools/call", token))[2],
        running.post(legacy_request(1, token))[2],
    ]
    for body in responses:
        data = json.loads(body)
        assert "error" in data
        assert token not in body.decode().lower()

"""HTTP behavior (A.6 #5): every row of A.3.5 against a server on an ephemeral port."""

from __future__ import annotations

import http.client
import json

from support_static_mcp import (
    BASE_HEADERS,
    build_manifest,
    legacy_request,
    modern_headers,
    modern_request,
    start_server,
)

from static_mcp.handlers import Store


def _err(body: bytes) -> dict:
    data = json.loads(body)
    assert data["jsonrpc"] == "2.0" and "error" in data
    return data


def test_healthz(running):
    status, headers, body = running.request("GET", "/healthz")
    assert (status, body) == (200, b"ok")
    assert headers["content-type"].startswith("text/plain")
    assert headers["cache-control"] == "no-store"


def test_foreign_host_is_403_without_id(running):
    status, _, body = running.post(legacy_request(1, "ping"), {"Host": "evil.example"})
    assert status == 403
    data = _err(body)
    assert "id" not in data
    assert data["error"]["message"] == "Host not allowed"


def test_host_with_port_is_stripped(running):
    status, _, _ = running.post(legacy_request(1, "ping"), {"Host": f"localhost:{running.port}"})
    assert status == 200


def test_origin_rules(running, manifest, site):
    status, _, body = running.post(legacy_request(1, "ping"), {"Origin": "https://evil.example"})
    assert status == 403 and "id" not in _err(body)
    status, _, _ = running.post(legacy_request(1, "ping"), {"Origin": "https://fixture.example.org"})
    assert status == 200
    status, _, _ = running.post(legacy_request(1, "ping"), {"Origin": "null"})
    assert status == 403
    strict = start_server(build_manifest(http={"allow_missing_origin": False}),
                          Store(site, manifest.limits))
    try:
        status, _, _ = strict.post(legacy_request(1, "ping"))
        assert status == 403
        status, _, _ = strict.post(legacy_request(1, "ping"), {"Origin": "https://fixture.example.org"})
        assert status == 200
    finally:
        strict.stop()


def test_missing_content_length_is_411(running):
    status, _, body = running.raw(
        [("Host", "localhost"), ("Content-Type", "application/json"),
         ("Transfer-Encoding", "chunked")],
        b"0\r\n\r\n",
    )
    assert status == 411 and "id" not in _err(body)


def test_oversize_content_length_is_413(running):
    status, headers, _ = running.raw(
        [("Host", "localhost"), ("Content-Type", "application/json"),
         ("Content-Length", "70000")],
        b"{}",
    )
    assert status == 413 and headers.get("connection") == "close"


def test_content_type_rules(running):
    status, _, _ = running.post(legacy_request(1, "ping"), {"Content-Type": "text/plain"})
    assert status == 415
    status, _, _ = running.post(legacy_request(1, "ping"),
                                {"Content-Type": "application/json; charset=utf-8"})
    assert status == 200
    status, _, _ = running.post(legacy_request(1, "ping"),
                                {"Content-Type": "application/json; charset=latin-1"})
    assert status == 415
    status, _, _ = running.post(legacy_request(1, "ping"), {"Content-Type": None})
    assert status == 415


def test_accept_rules(running):
    status, _, _ = running.post(legacy_request(1, "ping"), {"Accept": "text/html"})
    assert status == 406
    status, _, _ = running.post(legacy_request(1, "ping"), {"Accept": None})
    assert status == 200
    status, _, _ = running.post(legacy_request(1, "ping"), {"Accept": "*/*"})
    assert status == 200
    status, _, _ = running.post(legacy_request(1, "ping"),
                                {"Accept": "text/event-stream, application/json;q=0"})
    assert status == 406


def test_long_mcp_header_is_400_32020(running):
    status, _, body = running.post(legacy_request(1, "ping"), {"Mcp-Name": "a" * 1025})
    assert status == 400 and _err(body)["error"]["code"] == -32020


def test_invalid_json_and_batch(running):
    status, _, body = running.post(b"{not json")
    assert status == 400
    data = _err(body)
    assert (data["id"], data["error"]["code"]) == (None, -32700)
    status, _, body = running.post([legacy_request(1, "ping")])
    data = _err(body)
    assert (status, data["id"], data["error"]["code"]) == (400, None, -32600)


def test_notification_is_202_with_empty_body(running):
    status, headers, body = running.post({"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert (status, body) == (202, b"")
    assert headers["content-length"] == "0"


def test_request_response_headers_and_id_echo(running):
    for rpc_id in ("str-id", 42):
        status, headers, body = running.post(modern_request(rpc_id, "server/discover"),
                                             modern_headers("server/discover"))
        assert status == 200
        data = json.loads(body)
        assert data["id"] == rpc_id
        assert headers["content-type"] == "application/json"
        assert int(headers["content-length"]) == len(body)
        assert headers["cache-control"] == "no-store"
        assert headers["x-content-type-options"] == "nosniff"
        assert headers["server"] == "static-mcp"
        assert "mcp-session-id" not in headers


def test_session_headers_are_ignored(running):
    status, headers, _ = running.post(
        legacy_request(1, "tools/list"), {"Mcp-Session-Id": "abc", "Last-Event-ID": "9"}
    )
    assert status == 200 and "mcp-session-id" not in headers


def test_get_delete_put_on_endpoint_are_405(running):
    for method in ("GET", "DELETE", "PUT", "PATCH", "OPTIONS"):
        status, headers, body = running.request(method, running.endpoint)
        assert status == 405, method
        assert headers["allow"] == "POST"
        assert "error" in json.loads(body)


def test_other_paths_are_404(running):
    assert running.request("GET", "/nope")[0] == 404
    assert running.post(legacy_request(1, "ping"), path="/nope")[0] == 404
    assert running.post(legacy_request(1, "ping"), path=running.endpoint + "?x=1")[0] == 404
    assert running.logs()[-1]["path"] == "(other)"


def test_duplicate_mcp_header_is_400(running):
    status, _, body = running.raw(
        [("Host", "localhost"), ("Content-Type", "application/json"), ("Content-Length", "2"),
         ("Mcp-Method", "ping"), ("Mcp-Method", "tools/list")],
        b"{}",
    )
    assert status == 400 and _err(body)["error"]["code"] == -32020


def test_keep_alive_serves_two_requests_on_one_connection(running):
    conn = http.client.HTTPConnection("127.0.0.1", running.port, timeout=10)
    try:
        for n in (1, 2):
            raw = json.dumps(legacy_request(n, "ping")).encode()
            conn.request("POST", running.endpoint, body=raw, headers=BASE_HEADERS)
            resp = conn.getresponse()
            assert resp.status == 200 and json.loads(resp.read())["id"] == n
    finally:
        conn.close()


def test_log_line_fields(running):
    running.post(modern_request("x", "tools/call", {"name": "about", "arguments": {}}),
                 modern_headers("tools/call", "about"))
    line = running.logs()[-1]
    assert set(line) == {"ts", "http_method", "path", "status", "rpc_method", "mcp_name", "era",
                         "protocol_version", "duration_ms", "response_bytes", "user_agent",
                         "event"}
    assert line["http_method"] == "POST" and line["path"] == running.endpoint
    assert line["status"] == 200 and line["rpc_method"] == "tools/call"
    assert line["mcp_name"] == "about" and line["era"] == "modern"
    assert line["ts"].endswith("Z") and line["response_bytes"] > 0

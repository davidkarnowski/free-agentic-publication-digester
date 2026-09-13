"""Legacy era, MCP 2025-11-25 and 2025-06-18 without sessions (A.6 #4), in process."""

from __future__ import annotations

import pytest
from support_static_mcp import MODERN, in_process, legacy_request

SERVER_INFO = {"name": "org.example/fixture", "title": "Fixture Site", "version": "1.2.3"}


def _init(manifest, store, requested):
    params = {"capabilities": {}, "clientInfo": {"name": "c", "version": "1"}}
    if requested is not None:
        params["protocolVersion"] = requested
    return in_process(manifest, store, legacy_request(1, "initialize", params))


@pytest.mark.parametrize("requested, negotiated", [
    ("2025-11-25", "2025-11-25"),
    ("2025-06-18", "2025-06-18"),
    ("2024-11-05", "2025-11-25"),   # unknown → newest legacy
    (MODERN, "2025-11-25"),         # modern named through the handshake → newest legacy
    (None, "2025-11-25"),
    (17, "2025-11-25"),
])
def test_initialize_negotiation(manifest, store, requested, negotiated):
    status, body, log = _init(manifest, store, requested)
    assert status == 200
    r = body["result"]
    assert r["protocolVersion"] == negotiated
    assert r["capabilities"] == {"tools": {"listChanged": False},
                                 "resources": {"listChanged": False, "subscribe": False}}
    assert r["serverInfo"] == SERVER_INFO
    assert "instructions" in r
    assert "resultType" not in r and "_meta" not in r and "ttlMs" not in r
    assert log["era"] == "legacy" and log["protocol_version"] == negotiated


def test_initialized_notification_is_202(manifest, store):
    status, body, _ = in_process(manifest, store,
                                 {"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert (status, body) == (202, None)


def test_ping(manifest, store):
    status, body, _ = in_process(manifest, store, legacy_request("p", "ping"))
    assert status == 200 and body == {"jsonrpc": "2.0", "id": "p", "result": {}}


def test_tools_list_without_meta_has_no_modern_fields(manifest, store):
    _, body, _ = in_process(manifest, store, legacy_request(2, "tools/list"))
    r = body["result"]
    assert [t["name"] for t in r["tools"]] == [t.name for t in manifest.tools]
    assert r["tools"][0]["annotations"]["readOnlyHint"] is True
    assert set(r) == {"tools"}


def test_tools_call_and_resources_without_meta(manifest, store):
    _, body, _ = in_process(manifest, store, legacy_request(3, "tools/call", {
        "name": "get_note", "arguments": {"slug": "beta"}}))
    r = body["result"]
    assert r["isError"] is False and r["content"][0]["text"].startswith("# Beta note")
    assert set(r) == {"content", "isError"}
    _, body, _ = in_process(manifest, store, legacy_request(4, "resources/read", {
        "uri": "https://fixture.example.org/index.json"}))
    assert set(body["result"]) == {"contents"}
    assert body["result"]["contents"][0]["mimeType"] == "application/json"
    _, body, _ = in_process(manifest, store, legacy_request(5, "resources/templates/list"))
    assert set(body["result"]) == {"resourceTemplates"}


def test_resource_not_found_is_32002(manifest, store):
    status, body, _ = in_process(manifest, store, legacy_request(6, "resources/read", {
        "uri": "https://fixture.example.org/notes/missing.md"}))
    assert status == 200
    assert body["error"]["code"] == -32002
    assert body["id"] == 6


def test_modern_version_header_without_meta_is_400_32020(manifest, store):
    status, body, _ = in_process(manifest, store, legacy_request(7, "tools/list"),
                                 {"MCP-Protocol-Version": MODERN})
    assert (status, body["error"]["code"]) == (400, -32020)
    assert body["id"] == 7


def test_legacy_version_header_selects_that_version(manifest, store):
    status, _, log = in_process(manifest, store, legacy_request(8, "ping"),
                                   {"MCP-Protocol-Version": "2025-06-18"})
    assert status == 200 and log["protocol_version"] == "2025-06-18"


def test_unsupported_legacy_version_header_is_400_32600(manifest, store):
    status, body, _ = in_process(manifest, store, legacy_request(9, "ping"),
                                 {"MCP-Protocol-Version": "2024-11-05"})
    assert (status, body["error"]["code"]) == (400, -32600)
    assert body["error"]["data"] == {"supported": [MODERN, "2025-11-25", "2025-06-18"]}


@pytest.mark.parametrize("method", ["server/discover", "prompts/list", "resources/subscribe",
                                    "logging/setLevel", "completion/complete"])
def test_unknown_legacy_method_is_200_32601(manifest, store, method):
    status, body, _ = in_process(manifest, store, legacy_request(10, method))
    assert status == 200
    assert body["error"]["code"] == -32601
    assert body["id"] == 10


def test_no_session_state_between_requests(manifest, store):
    # A follow-on works without any initialize having happened, and carries no session.
    status, body, _ = in_process(manifest, store, legacy_request(11, "tools/list"),
                                 {"Mcp-Session-Id": "whatever", "Last-Event-ID": "3"})
    assert status == 200 and "tools" in body["result"]

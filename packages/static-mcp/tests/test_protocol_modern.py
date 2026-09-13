"""Modern era, MCP 2026-07-28 (A.6 #3), in process; determinism (A.6 #11)."""

from __future__ import annotations

import base64
import json

import pytest
from support_static_mcp import (
    MODERN,
    MODERN_META,
    build_manifest,
    in_process,
    modern_headers,
    modern_request,
)

from static_mcp.dispatch import handle_request
from static_mcp.manifest import DATA_SENTENCE

SERVER_INFO = {"name": "org.example/fixture", "title": "Fixture Site", "version": "1.2.3"}


def test_server_discover_shape(manifest, store):
    status, body, log = in_process(
        manifest, store, modern_request("d1", "server/discover"), modern_headers("server/discover")
    )
    assert status == 200
    assert body["id"] == "d1"
    r = body["result"]
    assert r["resultType"] == "complete"
    assert r["supportedVersions"] == [MODERN]
    assert r["capabilities"] == {"tools": {}, "resources": {}}
    assert r["instructions"].endswith(DATA_SENTENCE)
    assert r["_meta"] == {"io.modelcontextprotocol/serverInfo": SERVER_INFO}
    assert (r["ttlMs"], r["cacheScope"]) == (60000, "public")
    assert log["era"] == "modern" and log["protocol_version"] == MODERN


def test_tools_list_shape_and_order(manifest, store):
    _, body, _ = in_process(manifest, store, modern_request(1, "tools/list"),
                            modern_headers("tools/list"))
    r = body["result"]
    assert [t["name"] for t in r["tools"]] == [t.name for t in manifest.tools]
    for t in r["tools"]:
        assert t["annotations"] == {"readOnlyHint": True, "destructiveHint": False,
                                    "idempotentHint": True, "openWorldHint": False}
        assert t["inputSchema"]["type"] == "object"
        assert t["description"].endswith(DATA_SENTENCE)
    assert r["resultType"] == "complete"
    assert (r["ttlMs"], r["cacheScope"]) == (60000, "public")
    assert r["_meta"]["io.modelcontextprotocol/serverInfo"] == SERVER_INFO


def test_tools_list_is_byte_identical_between_calls(manifest, store):
    body = json.dumps(modern_request(7, "tools/list")).encode()
    h = {"Host": "localhost", "Content-Type": "application/json",
         "Content-Length": str(len(body)), **modern_headers("tools/list")}
    a = handle_request(h, body, manifest, store).body
    b = handle_request(h, body, manifest, store).body
    assert a == b


def test_tools_call_success_and_is_error(manifest, store):
    status, body, log = in_process(
        manifest, store,
        modern_request(2, "tools/call", {"name": "get_page", "arguments": {"date": "2026-01-02"}}),
        modern_headers("tools/call", "get_page"),
    )
    assert status == 200
    r = body["result"]
    assert r["resultType"] == "complete" and r["isError"] is False
    assert r["content"][1]["text"].startswith("# Page for 2026-01-02")
    assert "ttlMs" not in r
    assert log["mcp_name"] == "get_page"

    _, body, _ = in_process(
        manifest, store,
        modern_request(3, "tools/call", {"name": "get_page", "arguments": {"date": "2031-01-01"}}),
        modern_headers("tools/call", "get_page"),
    )
    assert body["result"]["isError"] is True
    assert "No page exists for 2031-01-01" in body["result"]["content"][0]["text"]


def test_tools_call_structured_content_has_text_twin(manifest, store):
    _, body, _ = in_process(
        manifest, store,
        modern_request(4, "tools/call", {"name": "get_entry", "arguments": {"slug": "alpha"}}),
        modern_headers("tools/call", "get_entry"),
    )
    r = body["result"]
    assert json.loads(r["content"][0]["text"]) == r["structuredContent"]
    assert r["structuredContent"]["item"]["slug"] == "alpha"


def test_resources_list_templates_list_and_read(manifest, store):
    _, body, _ = in_process(manifest, store, modern_request(5, "resources/list"),
                            modern_headers("resources/list"))
    r = body["result"]
    assert [x["uri"] for x in r["resources"]] == [x.uri for x in manifest.resources]
    assert r["resources"][0] == {"uri": "https://fixture.example.org/guide.txt", "name": "guide",
                                 "title": "Guide", "description": "The site guide.",
                                 "mimeType": "text/plain"}
    assert (r["ttlMs"], r["cacheScope"], r["resultType"]) == (60000, "public", "complete")

    _, body, _ = in_process(manifest, store, modern_request(6, "resources/templates/list"),
                            modern_headers("resources/templates/list"))
    r = body["result"]
    assert r["resourceTemplates"][0]["uriTemplate"] == "https://fixture.example.org/pages/{date}.md"
    assert "ttlMs" in r

    uri = "https://fixture.example.org/guide.txt"
    _, body, log = in_process(manifest, store, modern_request(7, "resources/read", {"uri": uri}),
                              modern_headers("resources/read", uri))
    r = body["result"]
    assert r["contents"] == [{"uri": uri, "mimeType": "text/plain",
                              "text": "Example site guide.\n\nThis is a plain-text guide used by the fixture site.\n"}]
    assert (r["ttlMs"], r["cacheScope"]) == (60000, "public")
    assert log["mcp_name"] == uri

    uri = "https://fixture.example.org/pages/2026-01-03.md"
    _, body, log = in_process(manifest, store, modern_request(8, "resources/read", {"uri": uri}),
                              modern_headers("resources/read", uri))
    assert body["result"]["contents"][0]["mimeType"] == "text/markdown"
    assert log["mcp_name"] == "page"


def test_resources_read_unknown_is_32602(manifest, store):
    for uri in ("https://fixture.example.org/nope.txt",
                "https://fixture.example.org/pages/2030-01-01.md",
                "file:///etc/passwd"):
        status, body, _ = in_process(manifest, store,
                                     modern_request(9, "resources/read", {"uri": uri}),
                                     modern_headers("resources/read", uri))
        assert status == 200
        assert body["error"]["code"] == -32602
        assert body["error"]["message"] == "Resource not found"
        assert "data" not in body["error"]
        assert body["id"] == 9


def test_unsupported_version_is_400_32022(manifest, store):
    msg = modern_request(10, "server/discover")
    msg["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] = "2027-01-01"
    status, body, _ = in_process(manifest, store, msg,
                                 {"MCP-Protocol-Version": "2027-01-01",
                                  "Mcp-Method": "server/discover"})
    assert status == 400
    assert body["error"]["code"] == -32022
    assert body["error"]["data"] == {"supported": [MODERN, "2025-11-25", "2025-06-18"],
                                     "requested": "2027-01-01"}
    assert body["id"] == 10


def test_missing_client_capabilities_is_400_32602(manifest, store):
    msg = modern_request(11, "server/discover")
    del msg["params"]["_meta"]["io.modelcontextprotocol/clientCapabilities"]
    status, body, _ = in_process(manifest, store, msg, modern_headers("server/discover"))
    assert (status, body["error"]["code"]) == (400, -32602)
    assert "clientCapabilities" in body["error"]["message"]


@pytest.mark.parametrize(
    "headers, fragment",
    [
        ({"Mcp-Method": "server/discover"}, "Missing MCP-Protocol-Version"),
        ({"MCP-Protocol-Version": "2025-11-25", "Mcp-Method": "server/discover"},
         "does not match _meta"),
        ({"MCP-Protocol-Version": MODERN}, "Missing Mcp-Method"),
        ({"MCP-Protocol-Version": MODERN, "Mcp-Method": "tools/list"}, "does not match method"),
    ],
)
def test_header_mismatch_cases(manifest, store, headers, fragment):
    status, body, log = in_process(manifest, store, modern_request(12, "server/discover"), headers)
    assert status == 400
    assert body["error"]["code"] == -32020
    assert fragment in body["error"]["message"]
    assert body["id"] == 12
    assert log["event"] == "l4.header"


def test_tools_call_requires_mcp_name(manifest, store):
    msg = modern_request(13, "tools/call", {"name": "about", "arguments": {}})
    status, body, _ = in_process(manifest, store, msg, modern_headers("tools/call"))
    assert (status, body["error"]["code"]) == (400, -32020)
    assert "Missing Mcp-Name" in body["error"]["message"]
    status, body, _ = in_process(manifest, store, msg, modern_headers("tools/call", "get_page"))
    assert (status, body["error"]["code"]) == (400, -32020)
    assert "does not match params.name" in body["error"]["message"]
    assert "about" not in body["error"]["message"] and "get_page" not in body["error"]["message"]


def test_base64_sentinel_mcp_name_is_decoded(manifest, store):
    msg = modern_request(14, "tools/call", {"name": "about", "arguments": {}})
    encoded = "=?base64?" + base64.b64encode(b"about").decode() + "?="
    status, body, _ = in_process(manifest, store, msg, modern_headers("tools/call", encoded))
    assert status == 200 and body["result"]["isError"] is False
    uri = "https://fixture.example.org/guide.txt"
    encoded = "=?base64?" + base64.b64encode(uri.encode()).decode() + "?="
    status, body, _ = in_process(manifest, store, modern_request(15, "resources/read", {"uri": uri}),
                                 modern_headers("resources/read", encoded))
    assert status == 200 and "contents" in body["result"]
    status, body, _ = in_process(manifest, store, msg, modern_headers("tools/call", "=?base64?!!?="))
    assert (status, body["error"]["code"]) == (400, -32020)


@pytest.mark.parametrize("method", ["initialize", "ping", "subscriptions/listen",
                                    "prompts/list", "logging/setLevel", "nope"])
def test_unknown_modern_methods_are_404(manifest, store, method):
    params = {"protocolVersion": "2025-11-25"} if method == "initialize" else {}
    status, body, _ = in_process(manifest, store, modern_request(16, method, params),
                                 modern_headers(method))
    assert status == 404
    assert body["error"]["code"] == -32601
    assert body["id"] == 16


def test_id_is_echoed_exactly(manifest, store):
    for rpc_id in ("abc", 0, 2**53, -5, "0"):
        _, body, _ = in_process(manifest, store, modern_request(rpc_id, "server/discover"),
                                modern_headers("server/discover"))
        assert body["id"] == rpc_id and type(body["id"]) is type(rpc_id)


def test_notification_is_202(manifest, store):
    msg = {"jsonrpc": "2.0", "method": "notifications/cancelled",
           "params": {"_meta": dict(MODERN_META)}}
    status, body, _ = in_process(manifest, store, msg, modern_headers("notifications/cancelled"))
    assert (status, body) == (202, None)
    status, body, _ = in_process(manifest, store, msg, {})
    assert (status, body) == (202, None)


def test_cursor_and_unexpected_params_are_32602(manifest, store):
    status, body, _ = in_process(manifest, store, modern_request(17, "tools/list", {"cursor": "x"}),
                                 modern_headers("tools/list"))
    assert (status, body["error"]["code"]) == (200, -32602)
    status, body, _ = in_process(manifest, store, modern_request(18, "tools/list", {"extra": 1}),
                                 modern_headers("tools/list"))
    assert (status, body["error"]["code"]) == (200, -32602)


def test_foreign_meta_keys_are_ignored(manifest, store):
    msg = modern_request(19, "server/discover")
    msg["params"]["_meta"]["traceparent"] = "00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01"
    msg["params"]["_meta"]["com.example/x"] = {"anything": True}
    status, body, _ = in_process(manifest, store, msg, modern_headers("server/discover"))
    assert status == 200 and "result" in body


def test_modern_only_manifest_names_versions_on_initialize(store):
    manifest = build_manifest(protocol_versions={"modern": [MODERN], "legacy": []})
    status, body, _ = in_process(manifest, store, {"jsonrpc": "2.0", "id": 1,
                                                   "method": "initialize",
                                                   "params": {"protocolVersion": "2025-11-25"}})
    assert (status, body["error"]["code"]) == (404, -32601)
    assert body["error"]["data"] == {"supported": [MODERN]}

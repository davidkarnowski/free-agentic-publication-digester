"""Adversarial corpus (A.6 #13): every payload runs through the in-process validator and
the HTTP server; both must agree on (http_status, jsonrpc_code) and on the id rule."""

from __future__ import annotations

import json

import pytest
from support_static_mcp import BASE_HEADERS, FIXTURES

from static_mcp.dispatch import handle_request

CORPUS = json.loads((FIXTURES / "adversarial.json").read_text(encoding="utf-8"))
IDS = [e["name"] for e in CORPUS]

_LEGACY_PING = {"jsonrpc": "2.0", "id": 1, "method": "ping"}


def _generate(spec: dict) -> bytes:
    kind = spec["kind"]
    if kind == "nested":
        return ("[" * spec["depth"] + "]" * spec["depth"]).encode()
    if kind == "nested_objects":
        return ('{"a":' * spec["depth"] + "1" + "}" * spec["depth"]).encode()
    if kind == "overlong":
        # C0 AE is an overlong encoding of "." — invalid UTF-8, rejected before parsing.
        return b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":"\xc0\xae"}}'
    if kind == "long_string":
        msg = {**_LEGACY_PING, "params": {"s": "a" * spec["chars"]}}
    elif kind == "big_object":
        msg = {**_LEGACY_PING, "params": {f"k{i}": i for i in range(spec["keys"])}}
    elif kind == "long_array":
        msg = {**_LEGACY_PING, "params": {"a": [0] * spec["items"]}}
    elif kind == "long_id":
        msg = {**_LEGACY_PING, "id": "i" * spec["chars"]}
    elif kind == "long_method":
        msg = {**_LEGACY_PING, "method": "m" * spec["chars"]}
    elif kind == "meta_keys":
        msg = {**_LEGACY_PING, "params": {"_meta": {f"k{i}": 1 for i in range(spec["count"])}}}
    elif kind == "long_name":
        msg = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": "n" * spec["chars"], "arguments": {}}}
    elif kind == "long_uri":
        msg = {"jsonrpc": "2.0", "id": 1, "method": "resources/read",
               "params": {"uri": "https://fixture.example.org/" + "u" * spec["chars"]}}
    elif kind == "long_arg":
        msg = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": "get_note", "arguments": {"slug": "a" * spec["chars"]}}}
    else:  # pragma: no cover - a typo in the corpus
        raise ValueError(kind)
    return json.dumps(msg).encode()


def build(entry: dict) -> tuple[dict[str, str], bytes, dict | None]:
    """Return (headers, body, decoded request or None) for a corpus entry."""
    if "body_hex" in entry:
        body = bytes.fromhex(entry["body_hex"])
    elif "body_text" in entry:
        body = entry["body_text"].encode("utf-8")
    elif "body_gen" in entry:
        body = _generate(entry["body_gen"])
    else:
        body = json.dumps(entry["body"], ensure_ascii=False).encode("utf-8")
    headers = {**BASE_HEADERS, "Content-Length": str(len(body))}
    for name, value in (entry.get("headers") or {}).items():
        if value is None:
            headers.pop(name, None)
        elif isinstance(value, dict):
            headers[name] = value["repeat"] * value["count"]
        else:
            headers[name] = value
    try:
        decoded = json.loads(body)
    except ValueError:
        decoded = None
    return headers, body, decoded if isinstance(decoded, dict) else None


def check(entry: dict, status: int, raw: bytes, decoded_request: dict | None, event: str | None):
    expect = entry["expect"]
    assert status == expect["status"], (entry["name"], status, raw[:200])
    assert status < 500
    body = json.loads(raw)
    assert body["jsonrpc"] == "2.0"
    assert body["error"]["code"] == expect["code"], (entry["name"], body)
    assert isinstance(body["error"]["message"], str)
    stage = entry["stage"]
    if stage == "L1":
        assert "id" not in body, entry["name"]
    elif stage in ("L2", "L3"):
        assert body["id"] is None, entry["name"]
    else:
        assert body["id"] == decoded_request["id"], entry["name"]
    if "event" in expect:
        assert event == expect["event"], entry["name"]
    assert "Traceback" not in raw.decode("utf-8", "replace")


def test_corpus_size_and_stage_coverage():
    assert len(CORPUS) >= 60
    assert {e["stage"] for e in CORPUS} == {"L1", "L2", "L3", "L4", "L5", "L6", "L7"}
    assert len(IDS) == len(set(IDS))


@pytest.mark.parametrize("entry", CORPUS, ids=IDS)
def test_in_process(entry, manifest, store):
    headers, body, decoded = build(entry)
    resp = handle_request(headers, body, manifest, store)
    check(entry, resp.status, resp.body, decoded, resp.log.get("event"))


@pytest.mark.parametrize("entry", CORPUS, ids=IDS)
def test_over_http(entry, running):
    if entry.get("http") is False:
        pytest.skip("cannot be sent as a well-formed HTTP request")
    headers, body, decoded = build(entry)
    status, _, raw = running.raw(list(headers.items()), body)
    event = running.logs()[-1]["event"] if running.logs() else None
    check(entry, status, raw, decoded, event)

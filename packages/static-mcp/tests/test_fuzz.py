"""Fuzz smoke (A.6 #14): 2,000 seeded random mutations of valid modern and legacy requests.

Asserts: no unhandled exception, no 5xx, every response body is well-formed
JSON-RPC, and a valid id is echoed whenever the envelope was valid.
"""

from __future__ import annotations

import json
import random

from support_static_mcp import BASE_HEADERS, legacy_request, modern_headers, modern_request

from static_mcp.dispatch import handle_request
from static_mcp.errors import Rejection
from static_mcp.validate import validate_body

SEED = 20260913
ROUNDS = 2000

BASES = [
    (modern_headers("server/discover"), modern_request(1, "server/discover")),
    (modern_headers("tools/call", "get_page"),
     modern_request("m2", "tools/call", {"name": "get_page", "arguments": {"date": "2026-01-01"}})),
    (modern_headers("resources/read", "https://fixture.example.org/guide.txt"),
     modern_request(3, "resources/read", {"uri": "https://fixture.example.org/guide.txt"})),
    ({}, legacy_request(4, "initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                          "clientInfo": {"name": "f", "version": "1"}})),
    ({}, legacy_request("l5", "tools/call", {"name": "list_entries",
                                             "arguments": {"limit": 3, "kind": "note"}})),
    ({}, legacy_request(6, "resources/read", {"uri": "https://fixture.example.org/notes/alpha.md"})),
    ({}, legacy_request(7, "tools/call", {"name": "list_pages", "arguments": {}})),
]

SWAP_VALUES = [None, True, False, 0, -1, 2**60, 1.5, "", "x", [], {}, [1, 2], {"a": 1}, "../../x"]


def _random_path(rng: random.Random, value, path=()):
    """Pick a random (container, key) inside a JSON value."""
    choices = []

    def walk(node, p):
        if isinstance(node, dict):
            for k, v in node.items():
                choices.append((node, k))
                walk(v, p + (k,))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                choices.append((node, i))
                walk(v, p + (i,))

    walk(value, path)
    return rng.choice(choices) if choices else None


def mutate(rng: random.Random, headers: dict, msg: dict) -> tuple[dict, bytes]:
    headers = dict(headers)
    msg = json.loads(json.dumps(msg))
    kind = rng.choice(["byte_flip", "truncate", "delete_key", "type_swap", "value_grow",
                       "header_drop", "header_garble", "combo"])
    body = json.dumps(msg).encode()
    if kind in ("delete_key", "combo"):
        target = _random_path(rng, msg)
        if target is not None:
            container, key = target
            del container[key]
        body = json.dumps(msg).encode()
    if kind in ("type_swap", "combo"):
        target = _random_path(rng, msg)
        if target is not None:
            container, key = target
            container[key] = rng.choice(SWAP_VALUES)
        body = json.dumps(msg).encode()
    if kind == "value_grow":
        target = _random_path(rng, msg)
        if target is not None:
            container, key = target
            v = container[key]
            if isinstance(v, str):
                container[key] = v * rng.choice([2, 50, 400])
            elif isinstance(v, int) and not isinstance(v, bool):
                container[key] = v * 10 ** rng.choice([3, 10, 30])
            elif isinstance(v, list):
                container[key] = v * 300
            elif isinstance(v, dict):
                container[key] = {**v, **{f"g{i}": i for i in range(rng.choice([10, 300]))}}
        body = json.dumps(msg).encode()
    if kind == "byte_flip":
        arr = bytearray(body)
        for _ in range(rng.randint(1, 4)):
            i = rng.randrange(len(arr))
            arr[i] = rng.randrange(256)
        body = bytes(arr)
    if kind == "truncate":
        body = body[: rng.randrange(len(body))]
    if kind in ("header_drop", "combo") and headers:
        headers.pop(rng.choice(list(headers)), None)
    if kind == "header_garble" and headers:
        name = rng.choice(list(headers))
        headers[name] = rng.choice(["", "x" * 2000, "2027-01-01", "tools/call", "é", "=?base64?!?="])
    return headers, body


def test_fuzz_smoke(manifest, store):
    rng = random.Random(SEED)
    statuses: dict[int, int] = {}
    for _ in range(ROUNDS):
        base_headers, base_msg = rng.choice(BASES)
        headers, body = mutate(rng, base_headers, base_msg)
        full = {**BASE_HEADERS, "Content-Length": str(len(body)), **headers}
        resp = handle_request(full, body, manifest, store)  # never raises by contract
        statuses[resp.status] = statuses.get(resp.status, 0) + 1
        assert resp.status < 500, (resp.status, body[:120])
        if resp.status == 202:
            assert resp.body is None
            continue
        data = json.loads(resp.body)
        assert data["jsonrpc"] == "2.0"
        assert ("result" in data) != ("error" in data)
        if "error" in data:
            assert isinstance(data["error"]["code"], int)
            assert isinstance(data["error"]["message"], str)
            assert "Traceback" not in data["error"]["message"]
        try:
            env = validate_body(body, max_body_bytes=manifest.http.max_body_bytes)
        except Rejection:
            env = None
        if env is not None and not env.is_notification and "id" in data:
            assert data["id"] == env.rpc_id
    assert statuses.get(200, 0) > 0 and statuses.get(400, 0) > 0

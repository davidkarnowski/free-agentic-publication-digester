"""Stages L5 (method parameters) and L8 (output assembly); the in-process request pipeline.

:func:`handle_request` is the whole server minus the socket: a pure
function of ``(headers, body_bytes, manifest, store)`` returning a
:class:`Response`. ``server.py`` wraps it; the tests call it directly,
and the adversarial corpus runs every payload through both and requires
them to agree.

Method tables (per era):

* modern (2026-07-28): ``server/discover``, ``tools/list``, ``tools/call``,
  ``resources/list``, ``resources/read``, ``resources/templates/list``;
  anything else → HTTP 404, ``-32601``.
* legacy (2025-11-25, 2025-06-18): ``initialize``, ``ping``, ``tools/list``,
  ``tools/call``, ``resources/list``, ``resources/read``,
  ``resources/templates/list``; anything else → HTTP 200, ``-32601``.

L5 checks: a per-method allow-list of ``params`` keys; ``tools/call.name``
matches the tool-name pattern and names a declared tool; ``arguments`` is
an object; ``resources/read.uri`` is a string of at most 2,048 characters
that equals a declared resource URI or matches a template's compiled
regex. A URI is never treated as a path.

L8: results are assembled from Python objects and serialized once;
client-sent strings never reach an error message; a log field is only
ever a value the manifest declared or a validated method name.
"""

from __future__ import annotations

import json
import traceback
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from static_mcp.errors import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    LEGACY_RESOURCE_NOT_FOUND,
    METHOD_NOT_FOUND,
    OMIT_ID,
    ContainmentError,
    Rejection,
)
from static_mcp.handlers import NotFound, NotText, Store, TooLarge, read_resource, run_tool
from static_mcp.manifest import TOOL_NAME_RE, Manifest, match_template, validate_arguments
from static_mcp.protocol import MODERN, Context, classify, envelope_result
from static_mcp.validate import Envelope, validate_body, validate_headers

MAX_URI_CHARS = 2048

MODERN_METHODS = frozenset(
    {
        "server/discover",
        "tools/list",
        "tools/call",
        "resources/list",
        "resources/read",
        "resources/templates/list",
    }
)
LEGACY_METHODS = frozenset(
    {
        "initialize",
        "ping",
        "tools/list",
        "tools/call",
        "resources/list",
        "resources/read",
        "resources/templates/list",
    }
)
PARAM_KEYS: dict[str, frozenset[str]] = {
    "server/discover": frozenset(),
    "ping": frozenset(),
    "initialize": frozenset({"protocolVersion", "capabilities", "clientInfo"}),
    "tools/list": frozenset({"cursor"}),
    "tools/call": frozenset({"name", "arguments"}),
    "resources/list": frozenset({"cursor"}),
    "resources/read": frozenset({"uri"}),
    "resources/templates/list": frozenset({"cursor"}),
}


@dataclass
class Response:
    status: int
    body: bytes | None  # None: no body (202)
    log: dict[str, Any] = field(default_factory=dict)


def encode(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


# --------------------------------------------------------------------------- L5


def _invalid(message: str, rpc_id: Any) -> Rejection:
    return Rejection(200, INVALID_PARAMS, message, rpc_id=rpc_id, stage="L5")


def _check_params(env: Envelope) -> dict[str, Any]:
    params = dict(env.params or {})
    params.pop("_meta", None)
    allowed = PARAM_KEYS[env.method]
    if set(params) - allowed:
        raise _invalid(f"Unexpected parameter for {env.method}", env.rpc_id)
    if "cursor" in params and params["cursor"] is not None:
        raise _invalid("Unknown cursor; this server returns every item on one page", env.rpc_id)
    return params


def _not_found_method(ctx: Context, env: Envelope, manifest: Manifest) -> Rejection:
    status = 404 if ctx.era == MODERN else 200
    return Rejection(
        status,
        METHOD_NOT_FOUND,
        "Method not found",
        data={"supported": manifest.all_versions} if env.method == "initialize" else None,
        rpc_id=env.rpc_id,
        stage="L5",
    )


# --------------------------------------------------------------------------- methods


def _discover(ctx: Context, manifest: Manifest) -> dict:
    return envelope_result(
        ctx,
        manifest,
        {
            "supportedVersions": list(manifest.modern_versions),
            "capabilities": {"tools": {}, "resources": {}},
            "instructions": manifest.server.instructions,
        },
        cacheable=True,
    )


def _initialize(ctx: Context, manifest: Manifest) -> dict:
    return {
        "protocolVersion": ctx.version,
        "capabilities": {
            "tools": {"listChanged": False},
            "resources": {"listChanged": False, "subscribe": False},
        },
        "serverInfo": manifest.server.implementation(),
        "instructions": manifest.server.instructions,
    }


def _tools_list(ctx: Context, manifest: Manifest) -> dict:
    return envelope_result(
        ctx, manifest, {"tools": [t.definition() for t in manifest.tools]}, cacheable=True
    )


def _resources_list(ctx: Context, manifest: Manifest) -> dict:
    return envelope_result(
        ctx, manifest, {"resources": [r.definition() for r in manifest.resources]}, cacheable=True
    )


def _templates_list(ctx: Context, manifest: Manifest) -> dict:
    return envelope_result(
        ctx,
        manifest,
        {"resourceTemplates": [t.definition() for t in manifest.templates]},
        cacheable=True,
    )


def _tools_call(
    ctx: Context, env: Envelope, params: dict, manifest: Manifest, store: Store, log: dict
) -> dict:
    name = params.get("name")
    if not isinstance(name, str) or not TOOL_NAME_RE.match(name) or name not in manifest.tools_by_name:
        raise _invalid("Unknown tool", env.rpc_id)
    tool = manifest.tools_by_name[name]
    log["mcp_name"] = tool.name
    args = validate_arguments(tool, params.get("arguments"))
    outcome = run_tool(store, tool, args)
    return envelope_result(ctx, manifest, outcome.result(), cacheable=False)


def _resources_read(
    ctx: Context, env: Envelope, params: dict, manifest: Manifest, store: Store, log: dict
) -> dict:
    uri = params.get("uri")
    if not isinstance(uri, str) or not uri or len(uri) > MAX_URI_CHARS:
        raise _invalid("uri must be a string of at most 2048 characters", env.rpc_id)
    not_found_code = INVALID_PARAMS if ctx.era == MODERN else LEGACY_RESOURCE_NOT_FOUND
    item: Any = manifest.resources_by_uri.get(uri)
    values: dict[str, str] = {}
    if item is not None:
        log["mcp_name"] = item.uri
    else:
        for template in manifest.templates:
            matched = match_template(template, uri)
            if matched is not None:
                item, values = template, matched
                log["mcp_name"] = template.name
                break
    if item is None:
        raise Rejection(200, not_found_code, "Resource not found", rpc_id=env.rpc_id, stage="L5")
    try:
        block = read_resource(store, item, uri, values)
    except NotFound:
        raise Rejection(200, not_found_code, "Resource not found", rpc_id=env.rpc_id, stage="L7")
    except (TooLarge, NotText):
        raise Rejection(
            200, INTERNAL_ERROR, "Resource could not be read", rpc_id=env.rpc_id, stage="L7"
        )
    return envelope_result(ctx, manifest, {"contents": [block]}, cacheable=True)


def dispatch(
    ctx: Context, env: Envelope, manifest: Manifest, store: Store, log: dict
) -> tuple[int, dict]:
    """Route one classified request. Returns ``(http_status, json_rpc_response)``."""
    methods = MODERN_METHODS if ctx.era == MODERN else LEGACY_METHODS
    if env.method not in methods:
        raise _not_found_method(ctx, env, manifest)
    params = _check_params(env)
    if env.method == "server/discover":
        result = _discover(ctx, manifest)
    elif env.method == "initialize":
        result = _initialize(ctx, manifest)
    elif env.method == "ping":
        result = {}
    elif env.method == "tools/list":
        result = _tools_list(ctx, manifest)
    elif env.method == "resources/list":
        result = _resources_list(ctx, manifest)
    elif env.method == "resources/templates/list":
        result = _templates_list(ctx, manifest)
    elif env.method == "tools/call":
        result = _tools_call(ctx, env, params, manifest, store, log)
    else:
        result = _resources_read(ctx, env, params, manifest, store, log)
    return 200, {"jsonrpc": "2.0", "id": env.rpc_id, "result": result}


# --------------------------------------------------------------------------- pipeline


def handle_request(
    headers: Mapping[str, str],
    body: bytes,
    manifest: Manifest,
    store: Store,
    *,
    error_writer: Callable[[str], Any] | None = None,
) -> Response:
    """Run one POST body through L1 (pure part) … L8. Never raises."""
    log: dict[str, Any] = {}
    rpc_id: Any = OMIT_ID
    try:
        validate_headers(headers, manifest)
        env = validate_body(body, max_body_bytes=manifest.http.max_body_bytes)
        log["rpc_method"] = env.method
        if env.is_notification:
            return Response(202, None, log)
        rpc_id = env.rpc_id
        ctx = classify(env, headers, manifest)
        log["era"] = ctx.era
        log["protocol_version"] = ctx.version
        status, payload = dispatch(ctx, env, manifest, store, log)
        return Response(status, encode(payload), log)
    except Rejection as rej:
        if rej.rpc_id is OMIT_ID and rpc_id is not OMIT_ID:
            rej = rej.with_id(rpc_id)
        log["event"] = rej.event or f"rejected.{rej.stage}"
        return Response(rej.http_status, encode(rej.body()), log)
    except ContainmentError:
        log["event"] = "security.path_escape"
        rej = Rejection(200, INTERNAL_ERROR, "Internal error", rpc_id=rpc_id)
        return Response(200, encode(rej.body()), log)
    except Exception:  # noqa: BLE001 - the boundary; the traceback is logged, never returned
        log["event"] = "internal_error"
        if error_writer is not None:
            error_writer(traceback.format_exc())
        rej = Rejection(200, INTERNAL_ERROR, "Internal error", rpc_id=rpc_id)
        return Response(200, encode(rej.body()), log)

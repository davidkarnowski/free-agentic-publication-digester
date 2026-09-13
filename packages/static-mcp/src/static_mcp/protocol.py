"""Stage L4: era classification, version negotiation, header/body mirroring, result envelopes.

Implements the dual-era rules of MCP 2026-07-28 ``basic/versioning.mdx``
("A dual-era server selects its behavior from how the client opens") and
the Streamable HTTP request-metadata rules of
``basic/transports/streamable-http.mdx``:

1. A request whose ``params._meta`` carries
   ``io.modelcontextprotocol/protocolVersion`` is **modern**. The version
   must be one the manifest lists as modern (else 400 / ``-32022`` with
   ``data.supported`` and ``data.requested``);
   ``io.modelcontextprotocol/clientCapabilities`` must be present and an
   object (else 400 / ``-32602``, per ``basic/index.mdx``); and the
   ``MCP-Protocol-Version``, ``Mcp-Method`` and (for ``tools/call`` /
   ``resources/read``) ``Mcp-Name`` headers must mirror the body, with the
   ``=?base64?…?=`` sentinel decoded first (else 400 / ``-32020``).
2. Otherwise a request whose method is ``initialize`` is a **legacy
   handshake**: the negotiated version is the requested one if the
   manifest lists it, else the newest legacy version.
3. Otherwise it is a **legacy follow-on**: an ``MCP-Protocol-Version``
   header naming a modern version without ``_meta`` is 400 / ``-32020``; a
   header naming an unsupported version is 400 / ``-32600``; no header
   means the newest legacy version (the spec lets a server assume a
   default).

No state is kept between requests in either era; no session is minted.
"""

from __future__ import annotations

import base64
import binascii
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from static_mcp.errors import (
    HEADER_MISMATCH,
    INVALID_PARAMS,
    INVALID_REQUEST,
    UNSUPPORTED_PROTOCOL_VERSION,
    Rejection,
)
from static_mcp.manifest import Manifest
from static_mcp.validate import Envelope, lower_headers

META_VERSION = "io.modelcontextprotocol/protocolVersion"
META_CLIENT_CAPS = "io.modelcontextprotocol/clientCapabilities"
META_CLIENT_INFO = "io.modelcontextprotocol/clientInfo"
META_SERVER_INFO = "io.modelcontextprotocol/serverInfo"

MODERN = "modern"
LEGACY = "legacy"

_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class Context:
    era: str  # MODERN or LEGACY
    version: str
    handshake: bool = False  # True for a legacy ``initialize`` request


def decode_mcp_name(value: str) -> str | None:
    """Decode the ``=?base64?…?=`` sentinel form; plain values pass through.

    Returns None when the encoded value is not valid Base64, not valid
    UTF-8, or contains control characters.
    """
    if value.startswith("=?base64?") and value.endswith("?="):
        inner = value[len("=?base64?") : -2]
        try:
            raw = base64.b64decode(inner, validate=True)
            decoded = raw.decode("utf-8", "strict")
        except (binascii.Error, ValueError):
            return None
        if _CONTROL_RE.search(decoded):
            return None
        return decoded
    return value


def _mismatch(message: str, rpc_id: Any) -> Rejection:
    return Rejection(400, HEADER_MISMATCH, message, rpc_id=rpc_id, stage="L4", event="l4.header")


def _check_mirrors(env: Envelope, h: Mapping[str, str], version: str) -> None:
    rpc_id = env.rpc_id
    if h.get("mcp-protocol-version") is None:
        raise _mismatch("Missing MCP-Protocol-Version header", rpc_id)
    if h["mcp-protocol-version"].strip() != version:
        raise _mismatch("MCP-Protocol-Version header does not match _meta", rpc_id)
    if h.get("mcp-method") is None:
        raise _mismatch("Missing Mcp-Method header", rpc_id)
    if h["mcp-method"].strip() != env.method:
        raise _mismatch("Mcp-Method header does not match method", rpc_id)
    if env.method in ("tools/call", "resources/read"):
        field = "name" if env.method == "tools/call" else "uri"
        body_value = (env.params or {}).get(field)
        header_value = h.get("mcp-name")
        if header_value is None:
            raise _mismatch("Missing Mcp-Name header", rpc_id)
        decoded = decode_mcp_name(header_value.strip())
        if decoded is None:
            raise _mismatch("Mcp-Name header is not decodable", rpc_id)
        if not isinstance(body_value, str) or decoded != body_value:
            raise _mismatch(f"Mcp-Name header does not match params.{field}", rpc_id)


def classify(env: Envelope, headers: Mapping[str, str], manifest: Manifest) -> Context:
    """Decide the era and protocol version for one request, or raise a Rejection."""
    h = lower_headers(headers)
    rpc_id = env.rpc_id

    if META_VERSION in env.meta:
        version = env.meta[META_VERSION]
        if not isinstance(version, str):
            raise Rejection(
                400, INVALID_REQUEST, "protocolVersion in _meta must be a string",
                rpc_id=rpc_id, stage="L4",
            )
        if version not in manifest.modern_versions:
            raise Rejection(
                400,
                UNSUPPORTED_PROTOCOL_VERSION,
                "Unsupported protocol version",
                data={"supported": manifest.all_versions, "requested": version},
                rpc_id=rpc_id,
                stage="L4",
            )
        caps = env.meta.get(META_CLIENT_CAPS)
        if not isinstance(caps, dict):
            raise Rejection(
                400,
                INVALID_PARAMS,
                "Missing or malformed io.modelcontextprotocol/clientCapabilities in _meta",
                rpc_id=rpc_id,
                stage="L4",
            )
        _check_mirrors(env, h, version)
        return Context(MODERN, version)

    if env.method == "initialize":
        requested = (env.params or {}).get("protocolVersion")
        if isinstance(requested, str) and requested in manifest.legacy_versions:
            negotiated = requested
        else:
            negotiated = manifest.newest_legacy
        if negotiated is None:
            raise Rejection(
                404,
                -32601,
                "Method not found; this server speaks only the listed protocol versions",
                data={"supported": manifest.all_versions},
                rpc_id=rpc_id,
                stage="L4",
            )
        return Context(LEGACY, negotiated, handshake=True)

    header_version = h.get("mcp-protocol-version")
    if header_version is not None:
        header_version = header_version.strip()
        if header_version in manifest.modern_versions:
            raise _mismatch("Modern MCP-Protocol-Version header without _meta protocolVersion",
                            rpc_id)
        if header_version not in manifest.legacy_versions:
            raise Rejection(
                400,
                INVALID_REQUEST,
                "Unsupported MCP-Protocol-Version header",
                data={"supported": manifest.all_versions},
                rpc_id=rpc_id,
                stage="L4",
            )
        return Context(LEGACY, header_version)
    if manifest.newest_legacy is None:
        raise Rejection(
            400,
            INVALID_REQUEST,
            "MCP-Protocol-Version header required",
            data={"supported": manifest.all_versions},
            rpc_id=rpc_id,
            stage="L4",
        )
    return Context(LEGACY, manifest.newest_legacy)


def envelope_result(ctx: Context, manifest: Manifest, result: dict, *, cacheable: bool) -> dict:
    """Add the era's result fields: modern gets resultType, serverInfo, and caching hints."""
    if ctx.era != MODERN:
        return result
    out: dict[str, Any] = {"resultType": "complete", **result}
    if cacheable:
        out["ttlMs"] = manifest.cache_ttl_ms
        out["cacheScope"] = manifest.cache_scope
    out["_meta"] = {META_SERVER_INFO: manifest.server.implementation()}
    return out

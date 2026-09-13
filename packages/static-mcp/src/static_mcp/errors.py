"""JSON-RPC and MCP error codes, and the exception that carries a rejection.

Every stage of the validation layer rejects a request by raising
:class:`Rejection`. A rejection knows its HTTP status, its JSON-RPC error
code, a message that names a header or parameter but never a client-sent
value, and how the ``id`` member must appear in the error body:

* ``OMIT_ID`` — no ``id`` member at all (HTTP-level rejections, where the
  spec allows a JSON-RPC error "that has no id");
* ``None`` — ``"id": null`` (the id could not be read or was itself
  invalid);
* a string or integer — the request id, echoed exactly.
"""

from __future__ import annotations

from typing import Any

# JSON-RPC 2.0
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# MCP 2026-07-28 (reserved sub-range -32020..-32099)
HEADER_MISMATCH = -32020
UNSUPPORTED_PROTOCOL_VERSION = -32022

# MCP 2025-11-25 and earlier: resource not found. Never emitted to a modern client.
LEGACY_RESOURCE_NOT_FOUND = -32002


class _OmitId:
    """Sentinel: the error body carries no ``id`` member."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "OMIT_ID"


OMIT_ID: Any = _OmitId()


class ManifestError(ValueError):
    """The manifest is invalid. Raised at load time; the server refuses to start."""


class Rejection(Exception):
    """A request was rejected by one validation stage.

    ``stage`` names the stage (``L1``..``L7``) for logs and tests; ``event``
    is an optional security-event label written to the log line.
    """

    def __init__(
        self,
        http_status: int,
        code: int,
        message: str,
        *,
        data: Any = None,
        rpc_id: Any = OMIT_ID,
        stage: str = "",
        event: str | None = None,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.code = code
        self.message = message
        self.data = data
        self.rpc_id = rpc_id
        self.stage = stage
        self.event = event

    def with_id(self, rpc_id: Any) -> Rejection:
        """Return a copy that echoes ``rpc_id`` (used once the id is known valid)."""
        return Rejection(
            self.http_status,
            self.code,
            self.message,
            data=self.data,
            rpc_id=rpc_id,
            stage=self.stage,
            event=self.event,
        )

    def body(self) -> dict[str, Any]:
        return error_body(self.code, self.message, data=self.data, rpc_id=self.rpc_id)


class ContainmentError(Exception):
    """A resolved path escaped the root. Logged as a security event, returned as -32603."""


def error_body(code: int, message: str, *, data: Any = None, rpc_id: Any = OMIT_ID) -> dict:
    """Build a JSON-RPC error response object."""
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    body: dict[str, Any] = {"jsonrpc": "2.0"}
    if rpc_id is not OMIT_ID:
        body["id"] = rpc_id
    body["error"] = error
    return body

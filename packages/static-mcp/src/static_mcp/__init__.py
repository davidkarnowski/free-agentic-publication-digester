"""static-mcp: a read-only Model Context Protocol server over a directory of static files.

The package turns a directory plus a declarative JSON manifest into a
dual-era (2026-07-28 stateless; 2025-11-25 / 2025-06-18 without sessions)
MCP server over Streamable HTTP. It uses the Python standard library only,
never writes, never calls a model, never opens an outbound connection, and
never mints a session.
"""

__version__ = "0.2.0"

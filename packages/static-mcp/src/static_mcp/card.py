"""Publication surfaces derived from the manifest: Server Card, Registry JSON, Markdown description.

* :func:`build_card` — an MCP Server Card (SEP-2127; schema
  ``https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json``).
  A card describes remote connectivity only; it never lists tools.
* :func:`build_registry_server_json` — the MCP Registry ``server.json``
  shape (``$schema`` supplied by the caller, since the registry's schema
  URL is date-stamped and verified at publish time).
* :func:`describe_markdown` — a Markdown table of tools, parameters and
  resources for documentation pages.

All three are pure functions of the manifest.
"""

from __future__ import annotations

from typing import Any

from static_mcp.manifest import DATA_SENTENCE, Manifest

SERVER_CARD_SCHEMA = "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json"


def _remotes(manifest: Manifest) -> list[dict[str, Any]]:
    return [
        {
            "type": "streamable-http",
            "url": manifest.endpoint_url,
            "supportedProtocolVersions": manifest.all_versions,
        }
    ]


def build_card(manifest: Manifest) -> dict[str, Any]:
    """The Server Card dict, keys in schema order."""
    s = manifest.server
    card: dict[str, Any] = {
        "$schema": SERVER_CARD_SCHEMA,
        "name": s.name,
        "version": s.version,
        "description": s.description,
        "title": s.title,
    }
    if s.website_url:
        card["websiteUrl"] = s.website_url
    if s.repository:
        card["repository"] = dict(s.repository)
    card["remotes"] = _remotes(manifest)
    return card


def build_registry_server_json(manifest: Manifest, schema_url: str) -> dict[str, Any]:
    """The MCP Registry ``server.json`` dict."""
    s = manifest.server
    out: dict[str, Any] = {
        "$schema": schema_url,
        "name": s.name,
        "title": s.title,
        "description": s.description,
        "version": s.version,
    }
    if s.website_url:
        out["websiteUrl"] = s.website_url
    if s.repository:
        out["repository"] = dict(s.repository)
    out["remotes"] = _remotes(manifest)
    return out


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _strip_sentence(text: str) -> str:
    return text.replace(DATA_SENTENCE, "").strip()


def describe_markdown(manifest: Manifest) -> str:
    """Markdown tables: tools (name, returns, parameters) and resources."""
    lines = [
        f"## {manifest.server.title} — MCP tools",
        "",
        (
            f"Endpoint: `{manifest.endpoint_url}` (Streamable HTTP, POST). "
            f"Protocol versions: {', '.join(manifest.all_versions)}. "
            "Every tool is read-only, idempotent and closed-world."
        ),
        "",
        "| Tool | Returns | Parameters |",
        "|---|---|---|",
    ]
    for tool in manifest.tools:
        params = []
        for name, p in tool.params.items():
            spec = p.spec
            bits = [spec.type]
            if spec.type == "integer":
                bits.append(f"{spec.minimum}…{spec.maximum}")
            if spec.has_default:
                bits.append(f"default {spec.default!r}")
            if p.required:
                bits.append("required")
            params.append(f"`{name}` ({', '.join(bits)})")
        lines.append(
            f"| `{tool.name}` | {_cell(_strip_sentence(tool.description))} | "
            f"{_cell('; '.join(params)) or '—'} |"
        )
    if manifest.resources or manifest.templates:
        lines += ["", "| Resource | URI | Type |", "|---|---|---|"]
        for r in manifest.resources:
            lines.append(f"| {_cell(r.title)} | `{r.uri}` | `{r.mime_type}` |")
        for t in manifest.templates:
            lines.append(f"| {_cell(t.title)} (template) | `{t.uri_template}` | `{t.mime_type}` |")
    return "\n".join(lines) + "\n"

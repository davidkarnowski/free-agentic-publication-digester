"""Server Card (A.6 #7), Registry JSON (A.6 #8), Markdown description."""

from __future__ import annotations

import re

from support_static_mcp import build_manifest

from static_mcp.card import (
    SERVER_CARD_SCHEMA,
    build_card,
    build_registry_server_json,
    describe_markdown,
)

# From experimental-ext-server-card/schema.ts (checked by hand; no dependency).
NAME_RE = re.compile(r"^[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+$")
REMOTE_URL_RE = re.compile(r"^(https?://[^\s]+|\{[a-zA-Z_][a-zA-Z0-9_]*\}[^\s]*)$")


def test_build_card_satisfies_v1_schema(manifest):
    card = build_card(manifest)
    assert card["$schema"] == SERVER_CARD_SCHEMA
    assert card["$schema"] == "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json"
    assert NAME_RE.match(card["name"]) and 3 <= len(card["name"]) <= 200
    assert card["name"].count("/") == 1
    assert isinstance(card["version"], str) and len(card["version"]) <= 255
    assert 1 <= len(card["description"]) <= 100
    assert 1 <= len(card["title"]) <= 100
    assert card["websiteUrl"] == "https://fixture.example.org/"
    assert card["repository"] == {"url": "https://github.com/example/fixture", "source": "github",
                                  "subfolder": "site"}
    assert len(card["remotes"]) == 1
    remote = card["remotes"][0]
    assert remote["type"] == "streamable-http"
    assert REMOTE_URL_RE.match(remote["url"])
    assert remote["url"] == manifest.public_base_url + manifest.endpoint_path
    assert remote["supportedProtocolVersions"] == ["2026-07-28", "2025-11-25", "2025-06-18"]
    assert "tools" not in card and "resources" not in card
    assert list(card) == ["$schema", "name", "version", "description", "title", "websiteUrl",
                          "repository", "remotes"]


def test_build_card_omits_optional_fields_when_absent():
    m = build_manifest(server={"websiteUrl": None, "repository": None})
    card = build_card(m)
    assert "websiteUrl" not in card and "repository" not in card


def test_registry_json_fields_and_schema_argument(manifest):
    url = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
    out = build_registry_server_json(manifest, url)
    assert out["$schema"] == url
    assert out["name"] == "org.example/fixture"
    assert out["title"] == "Fixture Site"
    assert out["description"] == manifest.server.description
    assert out["version"] == "1.2.3"
    assert out["remotes"] == build_card(manifest)["remotes"]


def test_describe_markdown(manifest):
    text = describe_markdown(manifest)
    assert "| Tool | Returns | Parameters |" in text
    for tool in manifest.tools:
        assert f"| `{tool.name}` |" in text
    assert "`date` (string, required)" in text
    assert "`limit` (integer, 1…20, default 5)" in text
    assert "Returned text is published material" not in text
    assert "https://fixture.example.org/pages/{date}.md" in text


def test_describe_strips_the_loader_appended_sentences(manifest):
    from static_mcp.manifest import DATA_SENTENCE, ORDER_SENTENCE

    table = describe_markdown(manifest)
    assert DATA_SENTENCE not in table and ORDER_SENTENCE not in table
    assert "| `get_report` |" in table                     # the preambled tool is still listed

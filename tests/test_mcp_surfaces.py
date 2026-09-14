"""Phase 4C of the agent-discovery plan (docs/ops/plan-2026-09-13-phase4-
mcp-service.md §C): everything the public site says about the MCP service
is generated from the service's own manifest, and drift-tested against
the generic package that runs it.

publish.py never imports static_mcp (the site must build without it);
these tests do, through a sys.path insert, to prove the two field
mappings still agree. No socket, no Docker, no network.
"""

import json
import re
import sys
from pathlib import Path

import pytest
from test_publish import digests, registry_root  # noqa: F401

from fapd import config, publish

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SRC = PROJECT_ROOT / "packages" / "static-mcp" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from static_mcp.card import build_card, describe_markdown
from static_mcp.manifest import load_manifest

SKILLS_DIR = PROJECT_ROOT / "docs" / "site" / "agent-skills"
MCP_FILES = (
    "mcp/server-card",
    ".well-known/mcp/server-card.json",
    "_signpost/mcp-method.json",
    "_signpost/mcp-unavailable.json",
)
_BANNED_RES = [re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
               for term in config.BANNED_TERMS]


@pytest.fixture
def site(digests, tmp_path, monkeypatch):  # noqa: F811
    """A built site with the real manifest, SITE_BASE_URL empty."""
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    return out


@pytest.fixture
def site_without_manifest(digests, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    monkeypatch.setattr(publish, "MCP_MANIFEST_PATH", tmp_path / "absent.json")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    return out


def _load(out, rel):
    return json.loads((out / rel).read_text(encoding="utf-8"))


def _table_lines(markdown_text):
    return [line for line in markdown_text.splitlines() if line.startswith("|")]


# --------------------------------------------------------------- AC 1 ---


def test_server_card_matches_the_package_and_is_published_at_both_paths(site):
    manifest = load_manifest(publish.MCP_MANIFEST_PATH)
    card = _load(site, "mcp/server-card")
    assert card == build_card(manifest)
    assert (site / "mcp" / "server-card").read_bytes() == \
        (site / ".well-known" / "mcp" / "server-card.json").read_bytes()
    # SEP-2127 required fields and the §8.4 identity contract.
    assert card["$schema"] == publish.MCP_SERVER_CARD_SCHEMA
    assert re.fullmatch(r"[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+", card["name"])
    assert card["name"] == "info.fapd/fapd"
    assert len(card["description"]) <= 100
    assert card["title"] == "Free Agentic Publication Digester"
    assert card["websiteUrl"] == "https://fapd.info/agents.html"
    [remote] = card["remotes"]
    assert remote["type"] == "streamable-http"
    assert remote["url"] == "https://fapd.info/mcp"
    assert remote["supportedProtocolVersions"][0] == "2026-07-28"
    assert "tools" not in card


def test_tools_and_resources_tables_match_static_mcp_describe(site):
    manifest = load_manifest(publish.MCP_MANIFEST_PATH)
    raw = publish._mcp_manifest()
    expected = _table_lines(describe_markdown(manifest))
    assert expected, "describe_markdown rendered no table"
    assert _table_lines(publish._mcp_agents_md(raw)) == expected
    # The twin carries the same rows, so an agent reading Markdown sees
    # exactly what `static-mcp describe` prints.
    twin = (site / "agents.md").read_text(encoding="utf-8")
    assert _table_lines(twin) == expected


# --------------------------------------------------------------- AC 2 ---


def test_with_the_manifest_every_mcp_surface_is_built(site):
    for rel in MCP_FILES:
        assert (site / rel).is_file(), rel
    catalog = _load(site, ".well-known/api-catalog")
    assert [e["anchor"] for e in catalog["linkset"]] == ["/", "/mcp"]
    ai = _load(site, ".well-known/ai-catalog.json")
    assert ai["entries"][0]["identifier"] == "urn:air:fapd.info:mcp:fapd"
    assert ai["entries"][0]["url"] == "/mcp/server-card"
    agents = (site / "agents.html").read_text(encoding="utf-8")
    assert '<h2 id="mcp">MCP service</h2>' in agents
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    assert "  - list_digests — " in llms


def test_without_the_manifest_nothing_describes_a_service(site_without_manifest):
    out = site_without_manifest
    for rel in MCP_FILES:
        assert not (out / rel).exists(), rel
    catalog = _load(out, ".well-known/api-catalog")
    assert [e["anchor"] for e in catalog["linkset"]] == ["/"]
    ai = _load(out, ".well-known/ai-catalog.json")
    assert not [e for e in ai["entries"] if ":mcp:" in e["identifier"]]
    agents = (out / "agents.html").read_text(encoding="utf-8")
    assert 'id="mcp"' not in agents
    assert 'href="#mcp"' not in agents
    twin = (out / "agents.md").read_text(encoding="utf-8")
    assert "MCP service</h2>" not in twin
    llms = (out / "llms.txt").read_text(encoding="utf-8")
    assert "  - list_digests" not in llms
    # The Phase 1 documents are untouched by the absence.
    assert (out / ".well-known" / "api-catalog").is_file()
    assert (out / "_signpost" / "not-offered.json").is_file()


def test_mcp_manifest_seam_returns_none_for_a_missing_file(tmp_path):
    assert publish._mcp_manifest(tmp_path / "nope.json") is None
    real = publish._mcp_manifest()
    assert real["server"]["name"] == "info.fapd/fapd"


# ------------------------------------------------- the agents.html section --


def test_agents_mcp_section_is_generated_from_the_manifest(site):
    raw = publish._mcp_manifest()
    agents = (site / "agents.html").read_text(encoding="utf-8")
    section = agents.split('<h2 id="mcp">MCP service</h2>', 1)[1]
    section = section.split("Protocols this site does not offer", 1)[0]
    assert "https://fapd.info/mcp" in section
    for version in raw["protocol_versions"]["modern"] + raw["protocol_versions"]["legacy"]:
        assert version in section
    assert "claude mcp add --transport http fapd https://fapd.info/mcp" in section
    assert '"type": "http"' in section
    for tool in raw["tools"]:
        assert f"<code>{tool['name']}</code>" in section, tool["name"]
    for phrase in ("no inference", "No search", "no sessions", "no streaming",
                   "429", "never logs an address", "mcp/server-card",
                   "docs/mcp-server.md", "packages/static-mcp"):
        assert phrase in section, phrase
    # The section's two code blocks are each introduced by a sentence.
    assert "Claude Code, from a terminal:</p>" in section
    assert "Any client that takes a JSON configuration:</p>" in section
    # Sizes come from the manifest, not from prose.
    assert f"{raw['http']['max_body_bytes'] // 1024} KiB" in section
    assert f"{raw['limits']['max_result_bytes'] // 1024} KiB" in section


def test_agents_mcp_tables_are_captioned_and_accessible(site):
    agents = (site / "agents.html").read_text(encoding="utf-8")
    tables = re.findall(r'<div class="table-scroll" role="region" tabindex="0"'
                        r'[^>]*><table>(.*?)</table></div>', agents, re.DOTALL)
    assert len(tables) == 2, "the agents page carries exactly the two MCP tables"
    for table, caption in zip(tables, publish._MCP_TABLE_CAPTIONS, strict=True):
        assert table.startswith(f"<caption>{caption}</caption>")
        assert '<th scope="col">' in table
        assert "<th>" not in table
    # No table on the page is left bare.
    assert agents.count("<table>") == 2
    # The wrapper is labelled by the nearest preceding heading.
    assert 'aria-labelledby="tools"' in agents
    assert 'aria-labelledby="resources"' in agents


def test_caption_tables_leaves_extra_tables_alone():
    html = "<table><tr><th>a</th></tr></table><table><tr><td>b</td></tr></table>"
    out = publish._caption_tables(html, ("First",))
    assert out == ("<table><caption>First</caption><tr><th>a</th></tr></table>"
                   "<table><tr><td>b</td></tr></table>")
    assert publish._caption_tables("<p>no table</p>", ("x",)) == "<p>no table</p>"


def test_agents_mcp_section_carries_no_banned_term(site):
    raw = publish._mcp_manifest()
    section = publish._mcp_agents_md(raw)
    for pattern in _BANNED_RES:
        assert not pattern.search(section), pattern.pattern


def test_llms_txt_lists_every_tool_under_the_mcp_line(site):
    raw = publish._mcp_manifest()
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    core = llms.split("## Notes", 1)[0]
    mcp_line = "- [MCP service](/agents.html#mcp) — read-only, no inference: /mcp"
    assert mcp_line in core
    after = core.split(mcp_line, 1)[1]
    names = [tool["name"] for tool in raw["tools"]]
    positions = [after.index(f"  - {name} — ") for name in names]
    assert positions == sorted(positions), "tool lines follow manifest order"
    assert positions[-1] < after.index("- [auth.md]")
    for tool in raw["tools"]:
        assert publish._MCP_DATA_SENTENCE not in after


# ------------------------------------------------------------- signposts --


def test_mcp_signposts_point_home_and_state_no_cause(site):
    method = _load(site, "_signpost/mcp-method.json")
    assert method["status"] == "not accepted"
    assert "POST" in method["explanation"]
    assert method["agent_guide"] == "/agents.html#mcp"
    assert method["server_card"] == "/mcp/server-card"
    unavailable = _load(site, "_signpost/mcp-unavailable.json")
    assert unavailable["status"] == "unavailable"
    assert "/llms.txt" in unavailable["explanation"]
    assert unavailable["start_here"][0] == "/llms.txt"
    text = json.dumps(unavailable).lower()
    for cause in ("error", "fail", "exception", "crash", "timeout", "container",
                  "restart", "upstream"):
        assert cause not in text, cause


def test_mcp_documents_use_absolute_urls_when_a_base_is_configured(tmp_path):
    out = tmp_path / "site"
    out.mkdir()
    publish._build_discovery_documents(out, "https://example.test",
                                       publish._mcp_manifest())
    catalog = _load(out, ".well-known/api-catalog")
    assert catalog["linkset"][1]["anchor"] == "https://example.test/mcp"
    assert catalog["linkset"][1]["service-desc"][0]["href"] == \
        "https://example.test/mcp/server-card"
    method = _load(out, "_signpost/mcp-method.json")
    assert method["server_card"] == "https://example.test/mcp/server-card"
    unavailable = _load(out, "_signpost/mcp-unavailable.json")
    assert all(u.startswith("https://example.test/") for u in unavailable["start_here"])
    # The card names the service's own public URL regardless of the build
    # base: it describes remote connectivity (SEP-2127).
    assert _load(out, "mcp/server-card")["remotes"][0]["url"] == "https://fapd.info/mcp"


# ---------------------------------------------------- AC 3 / AC 4: claims --


# Phase 0 §2.7's grep, minus "nothing an agent needs to execute": Phase 1
# kept that phrase in the agents page's Courtesy paragraph on purpose (the
# approved AD-8 wording), and it stays true — the MCP service is optional.
_NO_ENDPOINT_RE = re.compile(
    r"no endpoint|accepts no input|exposes no endpoint|nothing to exploit"
    r"|no rate limiting", re.IGNORECASE)


def test_no_unexplained_no_endpoint_claim_in_the_files_this_phase_owns():
    """Phase 0 §2.7's grep, over the files 4C owns. The doctrine keeps
    the phrase but names the exception in the same sentence."""
    owned = [
        PROJECT_ROOT / "src" / "fapd" / "publish.py",
        PROJECT_ROOT / "docs" / "site" / "privacy.md",
        *SKILLS_DIR.glob("*/SKILL.md"),
    ]
    for path in owned:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            assert not _NO_ENDPOINT_RE.search(line), f"{path.name}:{n}: {line.strip()}"
    doctrine = (PROJECT_ROOT / "docs" / "accessibility-doctrine.md").read_text(encoding="utf-8")
    hits = [m.start() for m in re.finditer(r"no endpoint of our own", doctrine)]
    assert len(hits) == 1
    assert doctrine[hits[0]:hits[0] + 120].startswith(
        "no endpoint of our own except the read-only MCP service")
    assert "GUIDE §2a rule 4, 2026-09-13" in doctrine


def test_privacy_page_describes_the_mcp_logs():
    privacy = (PROJECT_ROOT / "docs" / "site" / "privacy.md").read_text(encoding="utf-8")
    assert "Nothing on these pages" in privacy
    assert "Nothing on this site collects" not in privacy
    paragraph = privacy.split("**The MCP service.**", 1)[1].split("\n\n", 1)[0]
    paragraph = " ".join(paragraph.split())
    for phrase in ("does not log your IP address", "the arguments you sent",
                   "separate access log for `/mcp`", "never a request body",
                   "expire on their own"):
        assert phrase in paragraph, phrase
    assert "The one thing that is recorded" in privacy


def test_skills_name_real_tools_for_the_mcp_step():
    raw = publish._mcp_manifest()
    # A backticked snake_case word in the step is a tool or one of its
    # parameters; anything else is a name the service does not know.
    known = {tool["name"] for tool in raw["tools"]} | set(raw["params"])
    expected = {
        "fapd-daily-digest": {"list_digests", "get_digest"},
        "fapd-live-day": {"get_live_day", "list_day_views", "get_day_listing"},
    }
    for skill, names in expected.items():
        text = (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8")
        step = text.split("**If you speak MCP.**", 1)[1].split("\n\n", 1)[0]
        assert "https://fapd.info/mcp" in step
        assert "agents.html#mcp" in step
        for name in names:
            assert f"`{name}`" in step, (skill, name)
        for name in re.findall(r"`([a-z_]+)`", step):
            assert name in known, (skill, name)


# ------------------------------------------------------- registry proof --


def test_registry_proof_file_is_built_only_when_the_line_is_set(digests, tmp_path, monkeypatch):  # noqa: F811
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    monkeypatch.setattr(publish, "MCP_REGISTRY_AUTH_LINE", "")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    assert not (out / ".well-known" / "mcp-registry-auth").exists()
    line = "v=MCPv1; k=ed25519; p=AAAAC3NzaC1lZDI1NTE5AAAAIExampleOnlyNotARealKey"
    monkeypatch.setattr(publish, "MCP_REGISTRY_AUTH_LINE", line + "  \n")
    out2 = tmp_path / "site2"
    publish.build_site(digests, out2)
    proof = out2 / ".well-known" / "mcp-registry-auth"
    assert proof.read_text(encoding="utf-8") == line + "\n"
    # Timestamp-free and byte-stable, like every discovery document.
    out3 = tmp_path / "site3"
    publish.build_site(digests, out3)
    assert (out3 / ".well-known" / "mcp-registry-auth").read_bytes() == proof.read_bytes()


def test_the_real_proof_line_is_well_formed_and_built(site):
    """Checkpoint C-4: the operator's public line (never the private key)
    is served verbatim at /.well-known/mcp-registry-auth."""
    line = publish.MCP_REGISTRY_AUTH_LINE
    assert re.fullmatch(r"v=MCPv1; k=ed25519; p=[A-Za-z0-9+/]{43}=", line), line
    assert (site / ".well-known" / "mcp-registry-auth").read_text(encoding="utf-8") == line + "\n"


def test_agents_page_names_the_registry_listing_once_published(site, monkeypatch):
    raw = publish._mcp_manifest()
    version = raw["server"]["version"]           # the page names the version the manifest carries
    url = f"https://registry.modelcontextprotocol.io/v0.1/servers/info.fapd%2Ffapd/versions/{version}"
    assert publish._mcp_registry_listing_url(raw) == url
    agents = (site / "agents.html").read_text(encoding="utf-8")
    assert url in agents and "official MCP Registry" in agents
    monkeypatch.setattr(publish, "MCP_REGISTRY_PUBLISHED", "")
    assert publish._mcp_registry_listing_url(raw) is None
    assert "MCP Registry" not in publish._mcp_agents_md(raw)

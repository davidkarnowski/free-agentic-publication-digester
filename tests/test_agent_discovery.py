"""Phase 1 of the agent-discovery plan (docs/ops/plan-2026-09-13-phase1-
discovery-documents.md): the static discovery documents, pinned.

Every document here is a static file a site build writes with zero LLM
calls and no timestamp, so two builds are byte-identical. Nothing in
these tests touches the network: the Agent Skills schema URL and the
JSON Schema meta-schema URL are string identifiers, never fetched.
"""

import hashlib
import json
import re

import protego
import pytest
import yaml
from conftest import DATE
from schema_subset import SchemaError, ValidationError, validate
from test_publish import _seed_today, digests, registry_root  # noqa: F401

from fapd import config, publish

# Paths that are never files: the MCP endpoint answers POST only (master
# plan §8.1). A reference to it is documented, not broken. (The server
# card it references is a built file since Phase 4C; test_mcp_surfaces
# pins it.)
NON_FILE_PATHS = {"/mcp"}

# The live day is written by build_today (the collector's render seam),
# never by build_site, so a site-only fixture cannot contain it;
# test_live_and_day_pages_carry_the_discovery_links proves build_today
# writes both files.
LIVE_PATHS = {"/today.json", "/today.html"}

# Every file Phase 1 owns in master plan §8.1, relative to the site root.
P1_PATHS = (
    "robots.txt",
    "openapi.json",
    "schema/digests.schema.json",
    "schema/today.schema.json",
    "schema/day.schema.json",
    "schema/sources.schema.json",
    ".well-known/api-catalog",
    "auth.md",
    ".well-known/agent-skills/index.json",
    ".well-known/ai-catalog.json",
    "favicon.ico",
    "_signpost/not-offered.json",
)

_BANNED_RES = [re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
               for term in config.BANNED_TERMS]


@pytest.fixture
def site(digests, tmp_path, monkeypatch):  # noqa: F811
    """A built site from the real docs/site (so the four SKILL.md sources
    are found) with SITE_BASE_URL empty, the local-build case."""
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    return out


def _load(out, rel):
    return json.loads((out / rel).read_text(encoding="utf-8"))


def _strip_base(url):
    """A document URL -> the site-relative path it names, fragment dropped."""
    for prefix in ("https://fapd.info", config.SITE_BASE_URL):
        if prefix and url.startswith(prefix):
            url = url[len(prefix):]
    return url.split("#", 1)[0]


def _assert_resolves(out, url, *, where):
    path = _strip_base(url)
    if path in NON_FILE_PATHS or path in LIVE_PATHS:
        return
    assert path.startswith("/"), f"{where}: {url!r} is not root-relative"
    target = out / path.lstrip("/")
    if path == "/":
        target = out / "index.html"
    assert target.is_file(), f"{where}: {url} -> {target} is not built"


def _walk_strings(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_strings(value)
    elif isinstance(node, str):
        yield node


# ---------------------------------------------------------------- AC 1 ---


def test_every_p1_path_is_built(site):
    for rel in P1_PATHS:
        assert (site / rel).is_file(), rel
    skills = site / ".well-known" / "agent-skills"
    assert sorted(p.name for p in skills.iterdir() if p.is_dir()) == [
        "fapd-daily-digest", "fapd-live-day", "fapd-source-coverage",
        "fapd-verify-the-record"]


def test_two_builds_are_byte_identical(digests, tmp_path, monkeypatch):  # noqa: F811
    """No timestamp in any discovery document: `generated` stays on the
    surfaces that already carry it, never on these."""
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    first, second = tmp_path / "one", tmp_path / "two"
    publish.build_site(digests, first)
    publish.build_site(digests, second)
    skill_files = [str(p.relative_to(first))
                   for p in (first / ".well-known" / "agent-skills").rglob("*")
                   if p.is_file()]
    for rel in list(P1_PATHS) + skill_files:
        assert (first / rel).read_bytes() == (second / rel).read_bytes(), rel


# ---------------------------------------------------------------- AC 2 ---


def test_robots_content_signal_sits_inside_the_star_group(site):
    robots = (site / "robots.txt").read_text(encoding="utf-8")
    assert robots.count("Content-Signal:") == 1
    group = robots.split("User-agent: *\n", 1)[1].split("\n\n", 1)[0]
    assert "Content-Signal: search=yes, ai-input=yes, ai-train=yes" in group
    assert "Allow: /" in group
    assert re.search(r"^Sitemap: \S*/sitemap\.xml$", robots, re.MULTILINE)
    assert re.search(r"^Agentmap: \S*/\.well-known/ai-catalog\.json$", robots,
                     re.MULTILINE)
    parsed = protego.Protego.parse(robots)
    for agent in ("GPTBot", "ClaudeBot", "Googlebot", "*"):
        assert parsed.can_fetch("/", agent), agent
        assert parsed.can_fetch("/2026-07-01.html", agent), agent


# ---------------------------------------------------------------- AC 3 ---


def test_openapi_is_3_1_get_only_and_every_ref_resolves(site):
    doc = _load(site, "openapi.json")
    assert doc["openapi"] == "3.1.0"
    assert doc["security"] == []
    assert doc["info"]["license"] == {"name": "CC BY 4.0",
                                      "identifier": "CC-BY-4.0"}
    assert doc["servers"] == [{"url": "/"}]
    for path, item in doc["paths"].items():
        assert list(item) == ["get"], path
        assert "operationId" in item["get"] and "summary" in item["get"]
        if "{" in path:
            assert "404" in item["get"]["responses"], path
            assert item["get"]["parameters"][0]["name"] == "date"
    refs = [s for s in _walk_strings(doc) if s.startswith("/schema/")]
    assert len(refs) == 4
    for ref in refs:
        assert (site / ref.lstrip("/")).is_file(), ref
    assert set(doc["paths"]) >= {"/digests.json", "/today.json",
                                 "/day/{date}.json", "/sources.json",
                                 "/{date}.md", "/feed.xml", "/llms.txt"}
    assert "PRELIMINARY" in doc["paths"]["/today.json"]["get"]["description"]
    assert "is_backfill" in doc["paths"]["/today.json"]["get"]["description"]


def test_real_index_and_source_files_validate(digests, registry_root,  # noqa: F811
                                              tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    validate(_load(out, "digests.json"), _load(out, "schema/digests.schema.json"))
    validate(_load(out, "sources.json"), _load(out, "schema/sources.schema.json"))


def test_real_today_and_day_files_validate(conn, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIGEST_DIR", tmp_path / "no-digests")
    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    publish.build_day(conn, DATE, out_dir=tmp_path)
    publish.build_day(conn, "2020-01-01", out_dir=tmp_path)   # absent state
    schemas = publish._json_schemas("")
    validate(_load(tmp_path, "today.json"), schemas["today.schema.json"])
    validate(_load(tmp_path, f"day/{DATE}.json"), schemas["day.schema.json"])
    validate(_load(tmp_path, "day/2020-01-01.json"), schemas["day.schema.json"])
    with pytest.raises(ValidationError):
        validate(_load(tmp_path, "today.json"), schemas["day.schema.json"])


def test_schema_descriptions_carry_the_payload_labels():
    """GUIDE §1: the honesty disclosures travel with the schema — from the
    same constant the payload writes, so they cannot drift."""
    today = publish._json_schemas("")["today.schema.json"]
    item = today["properties"]["items"]["items"]["properties"]
    labels = publish._TODAY_LABELS
    assert today["properties"]["items"]["description"] == labels["items"]
    assert today["properties"]["counts"]["description"] == labels["counts"]
    assert today["properties"]["day_context"]["description"] == labels["day_context"]
    for key in ("is_backfill", "opening_verbatim", "summary_method", "tags",
                "corroborated_by", "duplicate_of"):
        assert item[key]["description"] == labels[key], key


def test_validator_rejects_keywords_outside_the_subset():
    with pytest.raises(SchemaError):
        validate({}, {"$ref": "#/x"})
    with pytest.raises(ValidationError):
        validate({"date": "yesterday"},
                 {"properties": {"date": {"pattern": r"^\d{4}-\d{2}-\d{2}$"}}})
    validate({"a": 1, "b": None}, {"type": "object",
                                   "properties": {"b": {"type": ["string", "null"]}},
                                   "required": ["a"]})


# ---------------------------------------------------------------- AC 4 ---


def test_api_catalog_is_a_linkset_with_no_status_relation(site):
    catalog = _load(site, ".well-known/api-catalog")
    assert list(catalog) == ["linkset"]
    anchors = [entry["anchor"] for entry in catalog["linkset"]]
    assert anchors == ["/", "/mcp"]
    for entry in catalog["linkset"]:
        assert "status" not in entry
        for relation, links in entry.items():
            if relation == "anchor":
                continue
            for link in links:
                assert set(link) == {"href", "type"}
                _assert_resolves(site, link["href"], where=relation)
    root = catalog["linkset"][0]
    assert root["service-desc"] == [{"href": "/openapi.json",
                                     "type": "application/vnd.oai.openapi+json"}]
    assert catalog["linkset"][1]["service-desc"][0]["href"] == "/mcp/server-card"
    assert "status" not in json.dumps(catalog)


_AI_IDENTIFIER_RE = re.compile(r"^urn:air:fapd\.info:[a-z]+:[a-z0-9-]+$")


def test_ai_catalog_meets_the_spec_and_scanner_rules(site):
    catalog = _load(site, ".well-known/ai-catalog.json")
    assert catalog["specVersion"] == "1.0"
    assert catalog["host"]["displayName"] == "Free Agentic Publication Digester"
    assert catalog["host"]["identifier"] == "fapd.info"
    assert not catalog["host"]["identifier"].startswith("did:")
    identifiers = [e["identifier"] for e in catalog["entries"]]
    assert len(identifiers) == len(set(identifiers))
    assert identifiers[:2] == ["urn:air:fapd.info:mcp:fapd",
                               "urn:air:fapd.info:api:static-read-api"]
    assert sum(1 for i in identifiers if ":skill:" in i) == 4
    for entry in catalog["entries"]:
        assert _AI_IDENTIFIER_RE.match(entry["identifier"]), entry["identifier"]
        assert ("url" in entry) != ("data" in entry), entry["identifier"]
        assert 2 <= len(entry["representativeQueries"]) <= 5, entry["identifier"]
        assert entry["type"] and entry["displayName"] and entry["description"]
        _assert_resolves(site, entry["url"], where=entry["identifier"])
    # (2026-09-04 is a date in a query, never a party or an official.)
    mcp = catalog["entries"][0]
    assert mcp["type"] == "application/mcp-server-card+json"
    assert mcp["url"] == "/mcp/server-card"


def test_ai_catalog_skill_entries_come_from_the_skill_sources(site):
    catalog = _load(site, ".well-known/ai-catalog.json")
    index = _load(site, ".well-known/agent-skills/index.json")
    by_url = {e["url"]: e for e in catalog["entries"] if ":skill:" in e["identifier"]}
    for skill in index["skills"]:
        entry = by_url[skill["url"]]
        assert entry["description"] == skill["description"]
        assert entry["type"] == "application/agent-skills+md"


# ---------------------------------------------------------------- AC 5 ---


_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# `>` stays allowed so a templated `<YYYY-MM-DD>` placeholder survives.
_FAPD_URL_RE = re.compile(r"https://fapd\.info[^\s)\]`\"']*")


def _templated_paths(site):
    """Paths openapi.json documents with a {date} placeholder, in the
    <YYYY-MM-DD> spelling the skills and llms.txt use."""
    doc = _load(site, "openapi.json")
    return {p.replace("{date}", "<YYYY-MM-DD>") for p in doc["paths"] if "{" in p}


def test_agent_skills_index_matches_the_served_bytes(site):
    index = _load(site, ".well-known/agent-skills/index.json")
    assert index["$schema"] == (
        "https://schemas.agentskills.io/discovery/0.2.0/schema.json")
    names = [s["name"] for s in index["skills"]]
    assert names == sorted(names) and len(names) == 4
    for skill in index["skills"]:
        assert 1 <= len(skill["name"]) <= 64
        assert _SKILL_NAME_RE.match(skill["name"]), skill["name"]
        assert skill["type"] == "skill-md"
        assert skill["url"] == f"/.well-known/agent-skills/{skill['name']}/SKILL.md"
        served = (site / skill["url"].lstrip("/")).read_bytes()
        assert skill["digest"] == "sha256:" + hashlib.sha256(served).hexdigest()
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", skill["digest"])
        text = served.decode("utf-8")
        assert text.startswith("---\n")
        front = yaml.safe_load(text.split("---\n", 2)[1])
        assert front["name"] == skill["name"]
        assert front["description"] == skill["description"]
        assert text.count("\n") < 130, f"{skill['name']} is over ~120 lines"


def test_skill_sources_are_copied_byte_for_byte(site):
    src_dir = config.PROJECT_ROOT / "docs" / "site" / "agent-skills"
    for src in sorted(src_dir.glob("*/SKILL.md")):
        served = site / ".well-known" / "agent-skills" / src.parent.name / "SKILL.md"
        assert served.read_bytes() == src.read_bytes(), src


def test_every_url_a_skill_names_is_real_or_documented(site):
    templated = _templated_paths(site)
    for skill_file in (site / ".well-known" / "agent-skills").glob("*/SKILL.md"):
        for url in _FAPD_URL_RE.findall(skill_file.read_text(encoding="utf-8")):
            path = _strip_base(url).rstrip(".,;")
            if path in templated:
                continue
            _assert_resolves(site, path, where=skill_file.parent.name)


def test_a_malformed_skill_fails_the_build(tmp_path, monkeypatch):
    root = tmp_path / "root"
    bad = root / "docs" / "site" / "agent-skills" / "fapd-x"
    bad.mkdir(parents=True)
    bad.joinpath("SKILL.md").write_text("---\nname: other-name\n"
                                        "description: d\n---\n# x\n")
    monkeypatch.setattr(config, "PROJECT_ROOT", root)
    with pytest.raises(ValueError, match="must equal the directory name"):
        publish._skill_sources()
    bad.joinpath("SKILL.md").write_text("# no front matter\n")
    with pytest.raises(ValueError, match="front matter"):
        publish._skill_sources()


def test_a_skill_without_representative_queries_fails_the_build():
    with pytest.raises(ValueError, match="representative queries"):
        publish._ai_catalog("", [("fapd-unlisted", b"", "d")])


# ---------------------------------------------------------------- AC 6 ---


_HEAD_LINKS = (
    '<link rel="api-catalog" href="{p}.well-known/api-catalog">',
    ('<link rel="service-desc" type="application/vnd.oai.openapi+json"'
     ' href="{p}openapi.json">'),
    '<link rel="service-doc" type="text/html" href="{p}agents.html">',
    ('<link rel="ai-catalog" type="application/ai-catalog+json"'
     ' href="{p}.well-known/ai-catalog.json">'),
    '<link rel="icon" href="{p}favicon.ico" sizes="32x32">',
    '<link rel="alternate" type="text/plain" href="{p}llms.txt"',
)


def _assert_head_links(page, prefix):
    head = page.split("</head>", 1)[0]
    for link in _HEAD_LINKS:
        assert link.format(p=prefix) in head, link
    assert head.count('rel="alternate" type="text/plain"') == 1


def test_root_pages_carry_the_discovery_links(site):
    for name in ("index.html", "2026-07-01.html", "agents.html", "archive.html"):
        _assert_head_links((site / name).read_text(encoding="utf-8"), "")


def test_subdirectory_pages_rebase_the_discovery_links(digests, registry_root,  # noqa: F811
                                                      tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SITE_BASE_URL", "")
    # A per-year archive page exists only for years before the newest
    # digest's, so the fixture needs a second year.
    (digests / "2025-12-30.md").write_text("# Daily Digest — 2025-12-30\n\n"
                                          "## Day in Review\n\nQuiet.\n")
    out = tmp_path / "site"
    publish.build_site(digests, out)
    source_pages = list((out / "sources").glob("*.html"))
    assert source_pages
    _assert_head_links(source_pages[0].read_text(encoding="utf-8"), "../")
    archive_pages = list((out / "archive").glob("*.html"))
    assert archive_pages
    _assert_head_links(archive_pages[0].read_text(encoding="utf-8"), "../")


def test_live_and_day_pages_carry_the_discovery_links(conn, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DIGEST_DIR", tmp_path / "no-digests")
    _seed_today(conn)
    publish.build_today(conn, out_dir=tmp_path, date=DATE)
    publish.build_day(conn, DATE, out_dir=tmp_path)
    for rel in LIVE_PATHS:            # the paths _assert_resolves exempts
        assert (tmp_path / rel.lstrip("/")).is_file(), rel
    _assert_head_links((tmp_path / "today.html").read_text(encoding="utf-8"), "")
    _assert_head_links((tmp_path / "day" / f"{DATE}.html").read_text(encoding="utf-8"),
                       "../")


# ---------------------------------------------------------------- AC 7 ---


def test_agents_page_has_the_new_sections_and_the_corrected_courtesy(site):
    agents = (site / "agents.html").read_text(encoding="utf-8")
    assert "Discovery for agents" in agents
    assert '<h2 id="mcp">MCP service</h2>' in agents
    assert 'href="#mcp"' in agents
    assert "Protocols this site does not offer, and why" in agents
    for declined in ("OAuth", "A2A agent card", "WebMCP", "x402"):
        assert declined in agents
    assert "receive a 404 whose" in agents
    assert "Everything is static except the read-only MCP service" in agents
    assert "per-address rate limit" in agents
    assert "Content-Signal" in agents or "Content Signals" in agents
    assert "Accept: text/markdown" in agents


def test_llms_txt_has_the_discovery_lines(site):
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    core, notes = llms.split("## Notes", 1)
    for line in (("- [API catalog (RFC 9727)](/.well-known/api-catalog) and"
                  " [OpenAPI description](/openapi.json)"),
                 "- [AI catalog](/.well-known/ai-catalog.json)",
                 ("- [Agent skills](/.well-known/agent-skills/index.json) —"
                  " step-by-step instructions for reading and citing the digest"),
                 ("- [MCP service](/agents.html#mcp) — read-only, no inference:"
                  " /mcp"),
                 "- [auth.md](/auth.md) — no authentication exists"):
        assert line in core, line
    assert core.index("feed.xml") < core.index("api-catalog") < core.index("today.html")
    assert ("- Markdown: append .md to a digest URL (/<YYYY-MM-DD>.md is the"
            " canonical record), or send Accept: text/markdown.") in notes
    assert ("- Declined protocols (OAuth, A2A, WebMCP, payments) and why:"
            " /agents.html") in notes


def test_no_rate_limiting_overclaim_anywhere_in_the_site(site):
    """Master plan §4: the edge applies a per-address limit, so the old
    sentence was false."""
    for path in site.rglob("*"):
        if path.is_file() and path.suffix in (".html", ".txt", ".md", ".json"):
            assert "no rate limiting" not in path.read_text(encoding="utf-8"), path


# ---------------------------------------------------------------- AC 8 ---


def test_no_banned_lexicon_term_in_any_new_document(site):
    """GUIDE §2: every sentence in these documents is our own prose."""
    files = [site / p for p in P1_PATHS if not p.endswith(".ico")]
    files += list((site / ".well-known" / "agent-skills").rglob("SKILL.md"))
    files += [site / "agents.html", site / "llms.txt"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for pattern in _BANNED_RES:
            assert not pattern.search(text), f"{pattern.pattern} in {path}"


# ---------------------------------------------------- auth.md, signpost ---


def test_auth_md_says_there_is_none(site):
    auth = (site / "auth.md").read_text(encoding="utf-8")
    assert auth.startswith("# auth.md")
    assert "you do not" in auth
    for word in ("register", "token", "authorize", "oauth"):
        assert not re.search(rf"\S+/{word}\b", auth), word
    for start in ("/llms.txt", "/.well-known/api-catalog", "/agents.html"):
        assert start in auth


def test_signpost_body_points_home(site):
    body = _load(site, "_signpost/not-offered.json")
    assert body["status"] == "not offered"
    assert "/mcp" in body["explanation"]
    assert len(body["start_here"]) == 5
    for url in body["start_here"] + [body["declined_protocols"]]:
        _assert_resolves(site, url, where="signpost")


# ----------------------------------------------------------------- favicon --


def test_favicon_is_a_deterministic_ico(site, tmp_path):
    ico = (site / "favicon.ico").read_bytes()
    assert ico.startswith(b"\x00\x00\x01\x00")
    assert ico == publish._favicon_ico()
    assert len(ico) == 22 + 40 + 32 * 32 * 4 + 32 * 4
    assert ico[6:8] == b"\x20\x20"          # 32 × 32
    assert ico[12:14] == b"\x20\x00"        # 32 bits per pixel


# -------------------------------------------------- absolute-URL variant ---


def test_documents_use_absolute_urls_when_a_base_is_configured(tmp_path):
    out = tmp_path / "site"
    out.mkdir()
    publish._build_discovery_documents(out, "https://example.test")
    catalog = _load(out, ".well-known/api-catalog")
    assert catalog["linkset"][0]["anchor"] == "https://example.test/"
    openapi = _load(out, "openapi.json")
    assert openapi["servers"] == [{"url": "https://example.test"}]
    assert openapi["externalDocs"]["url"] == "https://example.test/agents.html"
    schema = _load(out, "schema/today.schema.json")
    assert schema["$id"] == "https://example.test/schema/today.schema.json"
    ai = _load(out, ".well-known/ai-catalog.json")
    assert ai["host"]["documentationUrl"] == "https://example.test/agents.html"
    for url in _walk_strings(_load(out, "_signpost/not-offered.json")):
        if url.startswith("http"):
            assert url.startswith("https://example.test/")

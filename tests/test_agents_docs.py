"""Drift guards for the section-agent layer (docs/agents/).

The segmentation only works while its paper matches the repo: a launcher
pointing at a deleted instruction file, or an ownership matrix naming a
renamed module, silently strands the next agent launched with it. These
tests fail the moment either drifts.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENT_DOCS = PROJECT_ROOT / "docs" / "agents"
LAUNCHERS = PROJECT_ROOT / ".claude" / "agents"

SECTIONS = ("acquisition", "corpus", "editorial", "publication", "operations")


def test_every_section_has_doc_and_launcher():
    for section in SECTIONS:
        assert (AGENT_DOCS / f"{section}.md").is_file(), section
        assert (LAUNCHERS / f"fapd-{section}.md").is_file(), section
    assert (AGENT_DOCS / "README.md").is_file()
    assert (AGENT_DOCS / "orchestration.md").is_file()


def test_launchers_point_at_existing_docs():
    """Each thin launcher names its docs/agents file; the reference is the
    launcher's entire job, so a stale one is worse than none."""
    for path in sorted(LAUNCHERS.glob("fapd-*.md")):
        body = path.read_text(encoding="utf-8")
        refs = re.findall(r"docs/agents/([a-z]+\.md)", body)
        assert refs, f"{path.name} references no docs/agents file"
        for ref in refs:
            assert (AGENT_DOCS / ref).is_file(), f"{path.name} -> {ref} missing"


def test_ownership_matrix_paths_exist():
    """Every backticked path in orchestration.md's ownership matrix exists
    (globs must match at least one file). Catches renames breaking the
    matrix silently."""
    text = (AGENT_DOCS / "orchestration.md").read_text(encoding="utf-8")
    matrix = text.split("## 2. File ownership", 1)[1].split("## 3.", 1)[0]
    paths = re.findall(r"`([^`]+)`", matrix)
    # Bare filenames in matrix rows ("src/fapd/client.py, sync.py") elide
    # their directory; resolve against the directories the matrix uses.
    candidates = (".", "src/fapd", "src/fapd/parsers", "scripts", "docs")
    checked = 0
    for raw in paths:
        p = raw.strip()
        if not re.match(r"^[\w./*-]+$", p) or ("." not in p and "*" not in p):
            continue  # prose fragments like `active`
        if "*" in p:
            assert list(PROJECT_ROOT.glob(p)), f"matrix glob matches nothing: {raw}"
        elif "/" in p:
            assert (PROJECT_ROOT / p).exists(), f"matrix path missing: {raw}"
        else:
            assert any((PROJECT_ROOT / d / p).exists() for d in candidates), (
                f"matrix filename not found in any expected directory: {raw}"
            )
        checked += 1
    assert checked >= 20, f"matrix parse looks broken: only {checked} paths found"


def test_claude_md_router_names_all_sections():
    body = (PROJECT_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for section in SECTIONS:
        assert f"docs/agents/{section}.md" in body, section

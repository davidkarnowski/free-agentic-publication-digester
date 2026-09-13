"""No project strings (A.6 #12): the package stays reusable. Every file under the package is
scanned, case-insensitively, for the words that would tie it to the project it was built in."""

from __future__ import annotations

from pathlib import Path

from support_static_mcp import PACKAGE_ROOT

# Assembled from pieces so this file does not match itself.
FORBIDDEN = ("fa" + "pd", "fed" + "eral", "dig" + "est")
SKIP_DIRS = {"__pycache__", ".ruff_cache", ".pytest_cache", ".git"}


def _files() -> list[Path]:
    out = []
    for path in sorted(PACKAGE_ROOT.rglob("*")):
        if not path.is_file() or SKIP_DIRS & set(path.relative_to(PACKAGE_ROOT).parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        out.append(path)
    return out


def test_package_has_files():
    names = {p.name for p in _files()}
    assert {"README.md", "Dockerfile", "pyproject.toml", "LICENSE", "server.py"} <= names


def test_no_project_strings_anywhere():
    hits = []
    for path in _files():
        try:
            text = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            text = path.read_bytes().decode("latin-1").lower()
        for word in FORBIDDEN:
            if word in text:
                line = text[: text.index(word)].count("\n") + 1
                hits.append(f"{path.relative_to(PACKAGE_ROOT)}:{line}: {word}")
    assert hits == []

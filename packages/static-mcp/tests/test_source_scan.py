"""Source scans (A.6 #15, #16, SR-14): the package has no interpreter path and no network
client. Pinned by reading the source, so the guarantee cannot regress silently."""

from __future__ import annotations

import re

from support_static_mcp import SRC

SOURCE_FILES = sorted((SRC / "static_mcp").glob("*.py"))

INTERPRETER_PATTERNS = [
    r"sub" + r"process",
    r"os\.system",
    r"os\.popen",
    r"(?<![\w.])eval\(",
    r"(?<![\w.])exec\(",
    r"(?<![\w.])compile\(",
    r"pick" + r"le",
    r"mar" + r"shal",
    r"\by" + r"aml\b",
    r"shell" + r"=",
    r"c" + r"types",
]
NETWORK_PATTERNS = [
    r"urllib\.request",
    r"http\.client",
    r"socket\.create_connection",
    r"\bssl\.",
    r"^\s*(?:import|from)\s+requests\b",
]


def _scan(patterns: list[str]) -> list[str]:
    hits = []
    for path in SOURCE_FILES:
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.MULTILINE):
                line = text.count("\n", 0, m.start()) + 1
                hits.append(f"{path.name}:{line}: {m.group(0)!r}")
    return hits


def test_source_files_are_present():
    names = {p.name for p in SOURCE_FILES}
    assert {"server.py", "dispatch.py", "validate.py", "handlers.py", "manifest.py"} <= names


def test_no_interpreter_path():
    assert _scan(INTERPRETER_PATTERNS) == []


def test_no_network_client():
    assert _scan(NETWORK_PATTERNS) == []


def test_scan_catches_a_planted_hit(tmp_path):
    planted = tmp_path / "x.py"
    planted.write_text("import sub" + "process\nurllib.request.urlopen('x')\n", encoding="utf-8")
    text = planted.read_text()
    assert any(re.search(p, text, re.MULTILINE) for p in INTERPRETER_PATTERNS)
    assert any(re.search(p, text, re.MULTILINE) for p in NETWORK_PATTERNS)


def test_re_compile_is_not_a_false_positive():
    assert not re.search(r"(?<![\w.])compile\(", "regex = re.compile(pattern)")
    assert re.search(r"(?<![\w.])compile\(", "code = compile(src, 'x', 'exec')")

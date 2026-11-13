"""Every image FAPD builds starts from a base pinned by hash, and every tool the
backend installs outside uv.lock is pinned to an exact version (operator's
package rule; LeanOnMe dependency review, 2026-11-13).

A tag can be rebuilt under the same name, and a bare `pip install uv` takes
whatever is newest on the day of the build; either one changes what runs
without a commit saying so.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILES = [
    ROOT / "deploy/vps/Dockerfile.backend",
    ROOT / "deploy/vps/web-image/Dockerfile",
    ROOT / "packages/static-mcp/Dockerfile",
]
HASH = re.compile(r"^FROM \S+:\S+@sha256:[0-9a-f]{64}\b", re.MULTILINE)


def test_every_base_image_is_pinned_by_hash():
    for path in DOCKERFILES:
        text = path.read_text(encoding="utf-8")
        froms = re.findall(r"^FROM .*$", text, re.MULTILINE)
        assert froms, path
        assert len(HASH.findall(text)) == len(froms), f"{path}: {froms}"


def test_backend_tools_outside_the_lockfile_are_pinned_exactly():
    text = (ROOT / "deploy/vps/Dockerfile.backend").read_text(encoding="utf-8")
    assert re.search(r"pip install --no-cache-dir uv==\d+\.\d+\.\d+\b", text)
    assert re.search(r"@anthropic-ai/claude-code@\d+\.\d+\.\d+\b", text)
    assert not re.search(r"pip install[^\n]*\buv\s*(\\|$|&)", text, re.MULTILINE)

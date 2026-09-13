"""Fixtures for the static-mcp tests.

The fixture site under ``tests/fixtures/site`` is copied to ``tmp_path``
for every test that needs it; the copy gains a generated ``big.json``
(too large to commit, large enough to exceed the fixture manifest's
``max_result_bytes``) and two planted symlinks that point outside the
site root, so containment can be proved through the real handlers.
Helpers live in ``support_static_mcp.py``.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

# This directory is a package (see __init__.py: it keeps this conftest from
# shadowing the repository's rootless tests/conftest.py in a full-repo
# run), so pytest no longer puts it on sys.path. The helpers module and
# the package source are added here, once, before anything imports them.
_HERE = Path(__file__).resolve().parent
for _p in (_HERE, _HERE.parent / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pytest
from support_static_mcp import MANIFEST_PATH, start_server

from static_mcp.handlers import Store
from static_mcp.manifest import Manifest, load_manifest


@pytest.fixture
def site(tmp_path: Path) -> Path:
    from support_static_mcp import FIXTURES

    dest = tmp_path / "site"
    shutil.copytree(FIXTURES / "site", dest)
    rows = [{"i": n, "text": "x" * 40} for n in range(3000)]
    (dest / "big.json").write_text(json.dumps({"rows": rows}), encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret outside the root\n", encoding="utf-8")
    (dest / "notes" / "escape.md").symlink_to(outside)
    (dest / "pages" / "2026-02-02.md").symlink_to(outside)
    return dest


@pytest.fixture
def manifest() -> Manifest:
    return load_manifest(MANIFEST_PATH)


@pytest.fixture
def store(site: Path, manifest: Manifest) -> Store:
    return Store(site, manifest.limits)


@pytest.fixture
def running(manifest: Manifest, store: Store):
    handle = start_server(manifest, store)
    try:
        yield handle
    finally:
        handle.stop()

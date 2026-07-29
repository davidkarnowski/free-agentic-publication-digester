"""Regenerate SOURCES.md from sources/registry.yaml.

The document is a deterministic rendering of the registry (no timestamps);
tests/test_sources.py fails if the committed SOURCES.md drifts from the
registry, so run this after any registry edit.

Usage: uv run python scripts/sources_doc.py
"""

from pathlib import Path

from fapd import sources


def main() -> int:
    entries = sources.load_registry()
    out_path = Path(__file__).resolve().parents[1] / "SOURCES.md"
    out_path.write_text(sources.render_doc(entries), encoding="utf-8")
    print(f"Wrote SOURCES.md ({len(entries)} sources).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

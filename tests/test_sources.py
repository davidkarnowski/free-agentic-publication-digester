"""Sources registry tests: schema validation, coverage stats, and the
registry↔SOURCES.md sync guard (regenerate the doc whenever the registry
changes)."""

from pathlib import Path

import pytest
import yaml

from info_intel import sources

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def make_entry(**overrides) -> dict:
    entry = {
        "id": "test-source",
        "name": "Test Source",
        "branch": "legislative",
        "parent_org": "U.S. Congress",
        "description": "A test source.",
        "type": "govinfo-collection",
        "urls": {"collection": "https://www.govinfo.gov/app/collection/TEST"},
        "method": "govinfo collections API delta sync",
        "status": "active",
        "added": "2026-07-26",
        "notes": "",
    }
    entry.update(overrides)
    return entry


# ------------------------------------------------------------ real registry --


def test_registry_loads_and_validates():
    entries = sources.load_registry()
    assert len(entries) >= 30

    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "ids must be unique"

    for entry in entries:
        for field in sources.REQUIRED_FIELDS:
            assert field in entry, f"{entry['id']} missing {field}"
        assert entry["branch"] in sources.BRANCHES
        assert entry["status"] in sources.STATUSES
        assert entry["type"] in sources.TYPES
        assert set(entry["urls"]) <= set(sources.URL_KEYS)


def test_registry_seeds_expected_active_sources():
    entries = sources.load_registry()
    active = {e["id"] for e in entries if e["status"] == "active"}
    assert active == {"govinfo-crec", "govinfo-bills", "govinfo-fr", "govinfo-uscourts"}


# ------------------------------------------------------------ coverage_stats --


def test_coverage_stats_counts():
    entries = [
        make_entry(id="a", branch="legislative", status="active"),
        make_entry(id="b", branch="legislative", status="planned"),
        make_entry(id="c", branch="legislative", status="planned"),
        make_entry(id="d", branch="judicial", status="unavailable"),
    ]
    assert sources.coverage_stats(entries) == {
        "legislative": {"active": 1, "planned": 2},
        "judicial": {"unavailable": 1},
    }


def test_coverage_stats_empty():
    assert sources.coverage_stats([]) == {}


# ---------------------------------------------------------------- render_doc --


def test_render_doc_deterministic():
    entries = sources.load_registry()
    assert sources.render_doc(entries) == sources.render_doc(entries)


def test_sources_md_in_sync_with_registry():
    """The committed SOURCES.md must be exactly what the registry renders.

    If this fails, run: uv run python scripts/sources_doc.py
    """
    committed = (PROJECT_ROOT / "SOURCES.md").read_text(encoding="utf-8")
    assert committed == sources.render_doc(sources.load_registry())


# ---------------------------------------------------------------- validation --


def test_missing_field_raises_with_entry_id(tmp_path):
    entry = make_entry(id="broken-entry")
    del entry["method"]
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump([entry]), encoding="utf-8")
    with pytest.raises(ValueError, match="broken-entry.*method"):
        sources.load_registry(path)


def test_bad_status_raises(tmp_path):
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump([make_entry(status="someday")]), encoding="utf-8")
    with pytest.raises(ValueError, match="test-source.*status"):
        sources.load_registry(path)


def test_duplicate_id_raises(tmp_path):
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump([make_entry(), make_entry()]), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate id"):
        sources.load_registry(path)

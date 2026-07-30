"""Sources registry tests: schema validation, coverage stats, and the
registry↔SOURCES.md sync guard (regenerate the doc whenever the registry
changes)."""

from pathlib import Path

import pytest
import yaml

from fapd import sources

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def make_entry(**overrides) -> dict:
    entry = {
        "id": "test-source",
        "name": "Test Source",
        "branch": "legislative",
        "parent_org": "U.S. Congress",
        "description": "A test source.",
        "type": "govinfo-collection",
        "tier": 1,
        "urls": {"collection": "https://www.govinfo.gov/app/collection/TEST"},
        "method": "govinfo collections API delta sync",
        "status": "active",
        "added": "2026-07-26",
        # Non-empty because active entries require a gate-3 note (2026-07-30).
        "notes": "Coverage: complete test fixture.",
    }
    entry.update(overrides)
    return entry


# ------------------------------------------------------------ real registry --


def test_registry_loads_and_validates():
    entries = sources.load_registry()
    assert len(entries) >= 80

    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "ids must be unique"

    for entry in entries:
        for field in sources.REQUIRED_FIELDS:
            assert field in entry, f"{entry['id']} missing {field}"
        assert entry["branch"] in sources.BRANCHES
        assert entry["status"] in sources.STATUSES
        assert entry["type"] in sources.TYPES
        assert entry["tier"] in sources.TIERS
        assert set(entry["urls"]) <= set(sources.URL_KEYS)


def test_registry_seeds_expected_active_sources():
    entries = sources.load_registry()
    active = {e["id"] for e in entries if e["status"] == "active"}
    assert active == {"govinfo-crec", "govinfo-bills", "govinfo-fr", "govinfo-uscourts", "govinfo-plaw", "gao-reports", "fda-press",
        "sec-newsroom", "ftc-newsroom", "nasa-newsroom", "federal-reserve-news",
        "labor-newsroom", "va-newsroom", "defense-newsroom",
        # activated 2026-07-28 after documentation-led re-probes:
        "justice-newsroom", "nist-news", "uscourts-news", "cisa-advisories",
        "noaa-news",
        # email channel, activated 2026-07-30 on gate-3 evidence (parsed,
        # DKIM-verified bulletins from the 2026-07-29 window):
        "usattorneys-email", "treasury-email", "justice-email",
        "agriculture-email", "fsis-email", "uscis-email", "usps-oig-email"}


# ------------------------------------------------------------ coverage_stats --


def test_coverage_stats_counts():
    entries = [
        make_entry(id="a", branch="legislative", status="active", tier=1),
        make_entry(id="b", branch="legislative", status="planned", tier=2),
        make_entry(id="c", branch="legislative", status="planned", tier=2),
        make_entry(id="d", branch="judicial", status="unavailable", tier=3),
    ]
    assert sources.coverage_stats(entries) == {
        "branch": {
            "legislative": {"active": 1, "planned": 2},
            "judicial": {"unavailable": 1},
        },
        "tier": {
            1: {"active": 1},
            2: {"planned": 2},
            3: {"unavailable": 1},
        },
    }


def test_coverage_stats_per_tier_on_real_registry():
    """Every registered source lands in exactly one tier bucket."""
    entries = sources.load_registry()
    by_tier = sources.coverage_stats(entries)["tier"]
    assert set(by_tier) <= set(sources.TIERS)
    assert sum(sum(by.values()) for by in by_tier.values()) == len(entries)
    # Tier 1 carries the active govinfo collections seeded at project start.
    # govinfo 5 + 7 S2 pilots + DOJ (07-28) + treasury/justice/USDA email (07-30)
    assert by_tier[1].get("active", 0) == 16


def test_coverage_stats_empty():
    assert sources.coverage_stats([]) == {"branch": {}, "tier": {}}


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


@pytest.mark.parametrize("bad_tier", [0, 4, "1", None, True])
def test_bad_tier_raises(tmp_path, bad_tier):
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump([make_entry(tier=bad_tier)]), encoding="utf-8")
    with pytest.raises(ValueError, match="test-source.*tier"):
        sources.load_registry(path)


def test_aggregator_type_validates(tmp_path):
    entry = make_entry(
        id="test-aggregator",
        type="aggregator",
        urls={"home": "https://www.oversight.gov/"},
        status="planned",
    )
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump([entry]), encoding="utf-8")
    assert sources.load_registry(path)[0]["type"] == "aggregator"


# ------------------------------------- validation hardening (2026-07-30) ----


def load_one(tmp_path, *entries):
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(list(entries)), encoding="utf-8")
    return sources.load_registry(path)


def email_entry(**overrides) -> dict:
    entry = make_entry(
        id="test-email",
        type="email",
        status="planned",
        urls={"home": "https://www.example.gov/"},
        sender="press@example.gov",
    )
    entry.update(overrides)
    return entry


def test_active_requires_nonempty_notes(tmp_path):
    with pytest.raises(ValueError, match="test-source.*notes"):
        load_one(tmp_path, make_entry(notes=""))
    # planned may still carry empty notes (gap is visible, gate 3 not claimed)
    assert load_one(tmp_path, make_entry(status="planned", notes=""))


def test_unknown_web_adapter_rejected(tmp_path):
    with pytest.raises(ValueError, match="rss-feed-onlt"):
        load_one(tmp_path, make_entry(type="rss", adapter="rss-feed-onlt"))
    assert load_one(tmp_path, make_entry(type="rss", adapter="rss-feed-only"))


def test_email_adapter_scoped_to_platforms(tmp_path):
    assert load_one(tmp_path, email_entry(adapter="govdelivery"))
    assert load_one(tmp_path, email_entry())  # platform unknown: adapter absent
    with pytest.raises(ValueError, match="adapter 'rss'"):
        load_one(tmp_path, email_entry(adapter="rss"))
    # web entries may not claim an email platform
    with pytest.raises(ValueError, match="adapter 'govdelivery'"):
        load_one(tmp_path, make_entry(type="rss", adapter="govdelivery"))


def test_email_requires_sender(tmp_path):
    entry = email_entry()
    del entry["sender"]
    with pytest.raises(ValueError, match="test-email.*sender"):
        load_one(tmp_path, entry)


def test_sender_must_look_like_an_address(tmp_path):
    with pytest.raises(ValueError, match="not an email address"):
        load_one(tmp_path, email_entry(sender="not-an-address"))


def test_sender_list_accepted(tmp_path):
    entry = email_entry(sender=["a@example.gov", "b@example.gov"])
    assert load_one(tmp_path, entry)[0]["sender"] == ["a@example.gov", "b@example.gov"]


def test_duplicate_sender_across_entries_rejected(tmp_path):
    # The allowlist maps address -> source; a duplicate would silently
    # attribute one source's bulletins to another (last-wins in _sender_map).
    a = email_entry(id="email-a")
    b = email_entry(id="email-b", sender="Press@Example.gov")  # case-insensitive
    with pytest.raises(ValueError, match="email-b.*already registered.*email-a"):
        load_one(tmp_path, a, b)


def test_sender_forbidden_on_non_email_types(tmp_path):
    with pytest.raises(ValueError, match="only valid on type 'email'"):
        load_one(tmp_path, make_entry(sender="press@example.gov"))


def test_web_adapters_match_agencies_registry():
    # sources.py must not import agencies (HTTP deps), so the two constants
    # are pinned equal here instead.
    from fapd import agencies

    assert set(sources.WEB_ADAPTERS) == set(agencies.ADAPTERS)

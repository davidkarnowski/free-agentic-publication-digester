"""Orchestrator tests: staleness selection, idempotent replace, failure
isolation. Parsers are faked via the module registry; no real archive needed."""

import json

import pytest

from info_intel import db, extract


class FakeParserModule:
    def __init__(self, records_by_package=None, error_for=None):
        self.records_by_package = records_by_package or {}
        self.error_for = error_for or set()
        self.calls = []

    def parse(self, raw_path, package):
        self.calls.append(package["package_id"])
        if package["package_id"] in self.error_for:
            raise ValueError("corrupt xml")
        yield from self.records_by_package.get(
            package["package_id"],
            [rec(f"{package['package_id']}-g1")],
        )


def rec(granule_id="", **over):
    base = {
        "granule_id": granule_id,
        "doc_type": "RULE",
        "title": "A title",
        "agency": "Agency",
        "metadata": {"k": "v"},
        "text": "some text",
        "graphics_substantive": 0,
        "graphics_boilerplate": 0,
    }
    base.update(over)
    return base


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "meta.db")
    yield c
    c.close()


@pytest.fixture
def fake_parsers(monkeypatch):
    mod = FakeParserModule()
    monkeypatch.setattr(extract, "_parser_for", lambda collection: mod.parse)
    return mod


def add_package(conn, pid, collection="BILLS", fetched_at="2026-07-24T16:00:00Z",
                status="fetched"):
    conn.execute(
        "INSERT INTO packages (package_id, collection, last_modified, first_seen_at,"
        " fetch_status, fetched_at, raw_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (pid, collection, "2026-07-24T15:00:00Z", "2026-07-24T15:00:00Z",
         status, fetched_at, f"data/raw/{collection}/x/{pid}.xml"),
    )
    conn.commit()


def test_only_fetched_packages_are_pending(conn):
    add_package(conn, "A")
    add_package(conn, "B", status="pending", fetched_at=None)
    pending = extract.pending_packages(conn)
    assert [r["package_id"] for r in pending] == ["A"]


def test_extraction_is_recorded_and_not_repeated(conn, fake_parsers):
    add_package(conn, "A")
    assert extract.run(conn)["packages"] == 1
    assert extract.run(conn)["packages"] == 0  # second run: nothing pending
    assert fake_parsers.calls == ["A"]
    row = conn.execute("SELECT * FROM extracted_texts").fetchone()
    assert row["char_count"] == len("some text")
    assert json.loads(row["metadata"]) == {"k": "v"}
    assert row["extractor_version"] == extract.EXTRACTOR_VERSION


def test_refetched_package_is_reextracted_with_replace(conn, fake_parsers):
    add_package(conn, "A")
    extract.run(conn)
    # Simulate a re-fetch after the extraction happened
    conn.execute("UPDATE packages SET fetched_at = '2027-01-01T00:00:00Z'")
    conn.commit()
    fake_parsers.records_by_package["A"] = [rec("g-new")]
    assert extract.run(conn)["packages"] == 1
    rows = conn.execute("SELECT granule_id FROM extracted_texts").fetchall()
    assert [r["granule_id"] for r in rows] == ["g-new"]  # replaced, not appended


def test_version_bump_triggers_reextraction(conn, fake_parsers, monkeypatch):
    add_package(conn, "A")
    extract.run(conn)
    monkeypatch.setattr(extract, "EXTRACTOR_VERSION", extract.EXTRACTOR_VERSION + 1)
    assert extract.run(conn)["packages"] == 1


def test_one_bad_package_does_not_kill_run(conn, monkeypatch):
    mod = FakeParserModule(error_for={"BAD"})
    monkeypatch.setattr(extract, "_parser_for", lambda c: mod.parse)
    add_package(conn, "BAD")
    add_package(conn, "GOOD")
    results = extract.run(conn)
    assert results["failed"] == 1 and results["packages"] == 1
    rows = conn.execute("SELECT package_id FROM extracted_texts").fetchall()
    assert [r["package_id"] for r in rows] == ["GOOD"]


def test_collection_filter(conn, fake_parsers):
    add_package(conn, "A", collection="BILLS")
    add_package(conn, "B", collection="CREC")
    results = extract.run(conn, collections={"CREC"})
    assert results["packages"] == 1
    assert fake_parsers.calls == ["B"]

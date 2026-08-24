"""Orchestrator tests: staleness selection, idempotent replace, failure
isolation. Parsers are faked via the module registry; no real archive needed."""

import json

import pytest
from conftest import install_digest_day_default

from fapd import db, extract


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
    c = install_digest_day_default(db.connect(tmp_path / "meta.db"))
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


# ------------------------------------ the extraction attempt ceiling --
# 2026-08-24: FR-1995-01-04 (a ZIP that is not XML) was re-parsed every
# ~30-minute govinfo cycle for eighteen days because a failed extraction
# wrote nothing. Same shape as MAX_PACKAGE_FETCH_ATTEMPTS (2026-08-10).


def _attempts(conn, pid):
    return conn.execute(
        "SELECT extract_attempts, extract_error, last_extract_attempt_at"
        " FROM packages WHERE package_id = ?", (pid,)).fetchone()


def test_a_failing_package_is_retried_until_the_ceiling_then_excluded(
        conn, monkeypatch, caplog):
    import logging as _logging

    from fapd import config

    mod = FakeParserModule(error_for={"BAD"})
    monkeypatch.setattr(extract, "_parser_for", lambda c: mod.parse)
    monkeypatch.setattr(config, "MAX_PACKAGE_EXTRACT_ATTEMPTS", 3)
    add_package(conn, "BAD")

    with caplog.at_level(_logging.WARNING, logger="fapd.extract"):
        for n in range(1, 4):
            results = extract.run(conn)
            assert results["failed"] == 1
            row = _attempts(conn, "BAD")
            assert row["extract_attempts"] == n
            assert "corrupt xml" in row["extract_error"]
            assert row["last_extract_attempt_at"] is not None
        assert results["exhausted"] == 1
    assert caplog.text.count("extraction exhausted") == 1, "logged once, at the crossing"

    # past the ceiling: not pending, not re-parsed, still 'fetched'
    assert extract.pending_packages(conn) == []
    assert extract.run(conn)["failed"] == 0
    assert mod.calls == ["BAD"] * 3
    status = conn.execute(
        "SELECT fetch_status FROM packages WHERE package_id = 'BAD'").fetchone()
    assert status["fetch_status"] == "fetched", "no new fetch_status value"


def test_a_success_resets_the_extraction_ladder(conn, monkeypatch):
    mod = FakeParserModule(error_for={"A"})
    monkeypatch.setattr(extract, "_parser_for", lambda c: mod.parse)
    add_package(conn, "A")
    extract.run(conn)
    assert _attempts(conn, "A")["extract_attempts"] == 1

    mod.error_for = set()  # the parser was fixed
    assert extract.run(conn)["packages"] == 1
    row = _attempts(conn, "A")
    assert row["extract_attempts"] == 0 and row["extract_error"] is None


def test_a_refetch_resets_the_extraction_ladder(conn, monkeypatch):
    """A re-download is new bytes: the ceiling starts over, the same way
    fetch_attempts does on a content revision."""
    from fapd import config

    mod = FakeParserModule(error_for={"A"})
    monkeypatch.setattr(extract, "_parser_for", lambda c: mod.parse)
    monkeypatch.setattr(config, "MAX_PACKAGE_EXTRACT_ATTEMPTS", 2)
    add_package(conn, "A")
    extract.run(conn)
    extract.run(conn)
    assert extract.pending_packages(conn) == []

    # what _download_package writes on a successful re-fetch
    conn.execute(
        "UPDATE packages SET fetched_at = '2027-01-01T00:00:00Z',"
        " extract_attempts = 0, extract_error = NULL WHERE package_id = 'A'")
    conn.commit()
    assert [r["package_id"] for r in extract.pending_packages(conn)] == ["A"]


def test_the_ceiling_bookkeeping_survives_the_rollback(conn, monkeypatch):
    """The failed extraction is rolled back; the attempt record must not
    be — it is written in its own transaction afterwards."""
    mod = FakeParserModule(error_for={"A"})
    monkeypatch.setattr(extract, "_parser_for", lambda c: mod.parse)
    add_package(conn, "A")
    extract.run(conn)
    # a fresh connection sees the committed bookkeeping
    from pathlib import Path

    other = db.connect(Path(conn.execute("PRAGMA database_list").fetchone()["file"]))
    assert other.execute(
        "SELECT extract_attempts FROM packages WHERE package_id = 'A'"
    ).fetchone()["extract_attempts"] == 1
    other.close()

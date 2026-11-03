"""Raw-download retention (GUIDE §5, amended 2026-11-03): fingerprints at
download, superseded copies removed, eligible files pruned with their
fingerprint kept, and nothing pending ever deleted."""

import datetime as dt
import hashlib

import pytest
from test_sync import FakeClient, bill, listing

from fapd import config, extract, retention, sync

NOW = dt.datetime(2026, 12, 15, 12, 0, tzinfo=dt.UTC)


@pytest.fixture
def root(tmp_path):
    saved = (config.PROJECT_ROOT, config.RAW_DIR)
    config.PROJECT_ROOT, config.RAW_DIR = tmp_path, tmp_path / "data" / "raw"
    yield tmp_path
    config.PROJECT_ROOT, config.RAW_DIR = saved


def _summary(client, pid, date):
    client.json_by_path[f"packages/{pid}/summary"] = {
        "dateIssued": date, "title": pid,
        "download": {"xmlLink": f"https://x/{pid}/xml"}}


def _package(conn, root, pid, *, fetched, extracted=None, version=None, body=b"<x/>"):
    rel = f"data/raw/BILLS/2026-10-01/{pid}.xml"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, raw_path, fetch_status, fetched_at)"
        " VALUES (?, 'BILLS', '2026-10-01', ?, ?, ?, 'fetched', ?)",
        (pid, fetched, fetched, rel, fetched))
    if extracted:
        conn.execute(
            "INSERT INTO extracted_texts (package_id, granule_id, collection, text,"
            " char_count, extracted_at, extractor_version)"
            " VALUES (?, '', 'BILLS', 't', 1, ?, ?)",
            (pid, extracted, version or extract.EXTRACTOR_VERSION))
    conn.commit()
    return path


def test_download_records_the_fingerprint(conn, root):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-1", "2026-07-23T10:00:00Z")])
    _summary(client, "BILLS-1", "2026-07-23")
    client.content_by_url["https://x/BILLS-1/xml"] = b"<bill>text</bill>"
    sync.sync_collection(client, conn, "BILLS")
    row = conn.execute("SELECT * FROM packages").fetchone()
    assert row["raw_sha256"] == hashlib.sha256(b"<bill>text</bill>").hexdigest()
    assert row["raw_bytes"] == len(b"<bill>text</bill>")
    assert row["raw_pruned_at"] is None


def test_refiled_package_removes_its_superseded_copy(conn, root):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-2", "2026-07-23T10:00:00Z")])
    _summary(client, "BILLS-2", "2026-07-23")
    sync.sync_collection(client, conn, "BILLS")
    old = root / "data/raw/BILLS/2026-07-23/BILLS-2.xml"
    assert old.exists()
    # The publisher re-dates the package; the revision lands in a new folder.
    client.pages["collections/BILLS/"] = listing(
        [bill("BILLS-2", "2026-07-25T10:00:00Z", date="2026-07-24")])
    _summary(client, "BILLS-2", "2026-07-24")
    sync.sync_collection(client, conn, "BILLS")
    new = root / "data/raw/BILLS/2026-07-24/BILLS-2.xml"
    assert new.exists() and not old.exists()
    row = conn.execute("SELECT raw_path FROM packages").fetchone()
    assert row["raw_path"] == "data/raw/BILLS/2026-07-24/BILLS-2.xml"


def test_prune_deletes_only_old_extracted_files_and_keeps_the_fingerprint(conn, root):
    old = _package(conn, root, "OLD", fetched="2026-10-01T00:00:00Z",
                   extracted="2026-10-01T01:00:00Z", body=b"old-bytes")
    recent = _package(conn, root, "RECENT", fetched="2026-12-01T00:00:00Z",
                      extracted="2026-12-01T01:00:00Z")
    unextracted = _package(conn, root, "PENDING", fetched="2026-10-01T00:00:00Z")
    stale = _package(conn, root, "STALE", fetched="2026-10-05T00:00:00Z",
                     extracted="2026-10-01T00:00:00Z")  # extracted before the re-fetch
    stats = retention.prune_raw(conn, now=NOW)
    assert stats["pruned"] == 1
    assert not old.exists()
    assert recent.exists() and unextracted.exists() and stale.exists()
    row = conn.execute("SELECT * FROM packages WHERE package_id = 'OLD'").fetchone()
    assert row["raw_sha256"] == hashlib.sha256(b"old-bytes").hexdigest()
    assert row["raw_bytes"] == len(b"old-bytes") and row["raw_pruned_at"]
    assert row["raw_path"]                     # the record of where it was stays


def test_prune_never_touches_an_older_extractor_version(conn, root):
    saved = extract.EXTRACTOR_VERSION
    path = _package(conn, root, "V-OLD", fetched="2026-10-01T00:00:00Z",
                    extracted="2026-10-01T01:00:00Z", version=saved)
    extract.EXTRACTOR_VERSION = saved + 1     # a bump makes this text pending
    try:
        assert retention.prune_raw(conn, now=NOW)["pruned"] == 0
        assert path.exists()
    finally:
        extract.EXTRACTOR_VERSION = saved


def test_prune_is_bounded_and_marks_files_already_gone(conn, root):
    paths = [_package(conn, root, f"P{i}", fetched="2026-10-01T00:00:00Z",
                      extracted="2026-10-02T00:00:00Z") for i in range(5)]
    paths[0].unlink()                          # pruned by the 2026-11-03 one-time job
    stats = retention.prune_raw(conn, now=NOW, max_files=2)
    assert stats == {"pruned": 2, "bytes": stats["bytes"], "already_gone": 1}
    assert sum(p.exists() for p in paths) == 2
    assert retention.prune_raw(conn, now=NOW, max_files=2)["pruned"] == 2


def test_a_pruned_package_is_not_pending_extraction(conn, root):
    _package(conn, root, "GONE", fetched="2026-10-01T00:00:00Z",
             extracted="2026-10-01T01:00:00Z")
    retention.prune_raw(conn, now=NOW)
    conn.execute("UPDATE extracted_texts SET extracted_at = '2026-09-01T00:00:00Z'")
    conn.commit()
    assert [r["package_id"] for r in extract.pending_packages(conn)] == []

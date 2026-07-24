"""Tests for the delta-sync algorithm. No network: the client is faked; the
metadata DB is real SQLite at a tmp path."""


import pytest

from info_intel import config, db, sync
from info_intel.client import BudgetExceededError


class FakeClient:
    """Programmable stand-in for GovinfoClient's read methods."""

    def __init__(self):
        self.pages = {}  # path prefix -> list of page dicts
        self.json_by_path = {}  # exact path -> dict
        self.content_by_url = {}  # exact url -> bytes
        self.calls = []
        self.raise_on = {}  # path/url -> exception to raise

    def paginate(self, path, params=None):
        self.calls.append(("paginate", path))
        self._maybe_raise(path)
        for prefix, pages in self.pages.items():
            if path.startswith(prefix):
                yield from pages
                return
        yield {}

    def get_json(self, path, params=None):
        self.calls.append(("get_json", path))
        self._maybe_raise(path)
        return self.json_by_path[path]

    def get(self, url, params=None):
        self.calls.append(("get", url))
        self._maybe_raise(url)

        class R:
            content = self.content_by_url.get(url, b"<doc/>")

        return R()

    def _maybe_raise(self, key):
        if key in self.raise_on:
            raise self.raise_on[key]


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "meta.db")
    yield c
    c.close()


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(config, "RAW_DIR", tmp_path / "data" / "raw")
    return tmp_path / "data" / "raw"


def listing(pkgs):
    return [{"packages": pkgs}]


def bill(pid, lastmod, date="2026-07-23"):
    return {
        "packageId": pid,
        "lastModified": lastmod,
        "dateIssued": date,
        "title": f"title of {pid}",
        "packageLink": f"https://api.govinfo.gov/packages/{pid}/summary",
    }


def with_summary(client, pid, xml_url=True):
    links = {"pdfLink": f"https://x/{pid}/pdf"}
    if xml_url:
        links["xmlLink"] = f"https://x/{pid}/xml"
    client.json_by_path[f"packages/{pid}/summary"] = {
        "dateIssued": "2026-07-23",
        "title": f"title of {pid}",
        "download": links,
    }


def test_first_sync_uses_date_bounded_start(conn):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([])
    sync.sync_collection(client, conn, "BILLS", list_only=True)
    (_, path) = client.calls[0]
    # collections/BILLS/{start} — start must be a bounded ISO stamp, not epoch
    start = path.split("/")[-1]
    assert start.endswith("T00:00:00Z")
    assert start > "2026-07-01"  # bounded near now, not open-ended history


def test_listing_upserts_and_advances_watermark(conn):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing(
        [bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z"), bill("BILLS-119s2is", "2026-07-24T09:00:00Z")]
    )
    stats = sync.sync_collection(client, conn, "BILLS", list_only=True)
    assert stats["listed"] == 2
    assert stats["pending_remaining"] == 2
    wm = conn.execute("SELECT * FROM sync_state WHERE collection='BILLS'").fetchone()
    assert wm["last_modified_watermark"] == "2026-07-24T09:00:00Z"
    assert wm["last_sync_completed_at"] is not None
    assert wm["last_sync_package_count"] == 2


def test_second_sync_resumes_from_watermark(conn):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([])
    conn.execute(
        "INSERT INTO sync_state (collection, last_modified_watermark) VALUES (?, ?)",
        ("BILLS", "2026-07-20T12:34:56Z"),
    )
    sync.sync_collection(client, conn, "BILLS", list_only=True)
    assert ("paginate", "collections/BILLS/2026-07-20T12:34:56Z") in client.calls


def test_newer_lastmodified_flips_fetched_back_to_pending(conn):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z")])
    sync.sync_collection(client, conn, "BILLS", list_only=True)
    conn.execute("UPDATE packages SET fetch_status='fetched'")
    conn.commit()

    # Same lastModified re-listed (inclusive watermark boundary) -> no-op
    sync.sync_collection(client, conn, "BILLS", list_only=True)
    row = conn.execute("SELECT fetch_status FROM packages").fetchone()
    assert row["fetch_status"] == "fetched"

    # Newer lastModified -> back to pending
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-25T08:00:00Z")])
    sync.sync_collection(client, conn, "BILLS", list_only=True)
    row = conn.execute("SELECT fetch_status, last_modified FROM packages").fetchone()
    assert row["fetch_status"] == "pending"
    assert row["last_modified"] == "2026-07-25T08:00:00Z"


def test_listing_failure_leaves_watermark_untouched(conn):
    client = FakeClient()
    conn.execute(
        "INSERT INTO sync_state (collection, last_modified_watermark) VALUES (?, ?)",
        ("BILLS", "2026-07-20T12:34:56Z"),
    )
    conn.commit()
    client.raise_on["collections/BILLS/2026-07-20T12:34:56Z"] = RuntimeError("HTTP 500")
    with pytest.raises(RuntimeError):
        sync.sync_collection(client, conn, "BILLS", list_only=True)
    wm = conn.execute("SELECT * FROM sync_state WHERE collection='BILLS'").fetchone()
    assert wm["last_modified_watermark"] == "2026-07-20T12:34:56Z"
    assert wm["last_sync_completed_at"] is None
    assert wm["last_sync_started_at"] is not None  # the started/completed gap = died mid-run


def test_download_writes_file_and_marks_fetched(conn, raw_dir):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z")])
    with_summary(client, "BILLS-119hr1ih")
    client.content_by_url["https://x/BILLS-119hr1ih/xml"] = b"<bill>text</bill>"

    stats = sync.sync_collection(client, conn, "BILLS")
    assert stats["downloaded"] == 1 and stats["failed"] == 0
    row = conn.execute("SELECT * FROM packages").fetchone()
    assert row["fetch_status"] == "fetched"
    assert row["download_format"] == "xml"
    assert row["fetched_last_modified"] == row["last_modified"]
    stored = raw_dir / "BILLS" / "2026-07-23" / "BILLS-119hr1ih.xml"
    assert stored.read_bytes() == b"<bill>text</bill>"
    assert row["raw_path"] == "data/raw/BILLS/2026-07-23/BILLS-119hr1ih.xml"  # repo-relative


def test_failed_download_marked_and_run_continues(conn, raw_dir):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing(
        [bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z"), bill("BILLS-119s2is", "2026-07-23T11:00:00Z")]
    )
    with_summary(client, "BILLS-119hr1ih")
    with_summary(client, "BILLS-119s2is")
    client.raise_on["https://x/BILLS-119hr1ih/xml"] = RuntimeError("HTTP 404")

    stats = sync.sync_collection(client, conn, "BILLS")
    assert stats == {
        "collection": "BILLS", "listed": 2, "downloaded": 1, "failed": 1, "pending_remaining": 1,
    }
    failed = conn.execute(
        "SELECT fetch_status, last_error FROM packages WHERE package_id='BILLS-119hr1ih'"
    ).fetchone()
    assert failed["fetch_status"] == "failed"
    assert "404" in failed["last_error"]


def test_budget_exhaustion_aborts_run_and_preserves_queue(conn, raw_dir):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z")])
    client.raise_on["packages/BILLS-119hr1ih/summary"] = BudgetExceededError("budget")
    with pytest.raises(BudgetExceededError):
        sync.sync_collection(client, conn, "BILLS")
    row = conn.execute("SELECT fetch_status FROM packages").fetchone()
    assert row["fetch_status"] == "pending"  # not marked failed; queue intact


def test_max_downloads_caps_run_leaving_rest_pending(conn, raw_dir):
    client = FakeClient()
    pkgs = [bill(f"BILLS-119hr{i}ih", f"2026-07-23T1{i}:00:00Z") for i in range(3)]
    client.pages["collections/BILLS/"] = listing(pkgs)
    for p in pkgs:
        with_summary(client, p["packageId"])
    stats = sync.sync_collection(client, conn, "BILLS", max_downloads=2)
    assert stats["downloaded"] == 2
    assert stats["pending_remaining"] == 1


def test_crec_download_inventories_granules(conn, raw_dir):
    client = FakeClient()
    client.pages["collections/CREC/"] = listing(
        [{"packageId": "CREC-2026-07-23", "lastModified": "2026-07-24T02:00:00Z",
          "dateIssued": "2026-07-23"}]
    )
    client.json_by_path["packages/CREC-2026-07-23/summary"] = {
        "dateIssued": "2026-07-23",
        "title": "Congressional Record Volume 172, Issue 121",
        "download": {"zipLink": "https://x/CREC-2026-07-23/zip"},
    }
    client.pages["packages/CREC-2026-07-23/granules"] = [
        {"granules": [
            {"granuleId": "CREC-2026-07-23-pt1-PgS1", "granuleClass": "SENATE", "title": "A"},
            {"granuleId": "CREC-2026-07-23-pt1-PgH1", "granuleClass": "HOUSE", "title": "B"},
        ]}
    ]
    stats = sync.sync_collection(client, conn, "CREC")
    assert stats["downloaded"] == 1
    rows = conn.execute("SELECT granule_class FROM granules ORDER BY granule_id").fetchall()
    assert [r["granule_class"] for r in rows] == ["HOUSE", "SENATE"]
    pkg = conn.execute("SELECT download_format FROM packages").fetchone()
    assert pkg["download_format"] == "zip"  # CREC has no package-level XML

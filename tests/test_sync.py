"""Tests for the delta-sync algorithm. No network: the client is faked; the
metadata DB is real SQLite at a tmp path."""


import pytest
from conftest import install_digest_day_default

from fapd import config, db, sync
from fapd.client import BudgetExceededError


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
    c = install_digest_day_default(db.connect(tmp_path / "meta.db"))
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


def fr_package(client, pid, xml_body):
    client.pages["collections/FR/"] = listing(
        [{"packageId": pid, "lastModified": "2026-07-24T02:00:00Z", "dateIssued": "2026-07-23"}]
    )
    client.json_by_path[f"packages/{pid}/summary"] = {
        "dateIssued": "2026-07-23",
        "title": "Federal Register issue",
        "download": {"xmlLink": f"https://x/{pid}/xml", "pdfLink": f"https://x/{pid}/pdf"},
    }
    client.content_by_url[f"https://x/{pid}/xml"] = xml_body
    client.content_by_url[f"https://x/{pid}/pdf"] = b"%PDF-fake"
    client.pages[f"packages/{pid}/granules"] = [{"granules": []}]


def test_fr_with_substantive_graphics_archives_companion_pdf(conn, raw_dir):
    client = FakeClient()
    fr_package(
        client, "FR-2026-07-23",
        b'<FR><RULE><GPH DEEP="30"><GID>EN23JY26.004</GID></GPH>'
        b'<GPH DEEP="640"><GID>ED23JY26.063</GID></GPH></RULE>'
        b'<PRESDOC><GPH DEEP="80"><GID>Trump.EPS</GID></GPH></PRESDOC></FR>',
    )
    stats = sync.sync_collection(client, conn, "FR")
    assert stats["downloaded"] == 1
    day_dir = raw_dir / "FR" / "2026-07-23"
    assert (day_dir / "FR-2026-07-23.xml").exists()
    assert (day_dir / "FR-2026-07-23.pdf").read_bytes() == b"%PDF-fake"
    row = conn.execute("SELECT download_format FROM packages").fetchone()
    assert row["download_format"] == "xml"  # XML stays the primary artifact


def test_fr_without_graphics_skips_pdf(conn, raw_dir):
    client = FakeClient()
    fr_package(client, "FR-2026-07-24", b"<FR><NOTICE>text only</NOTICE></FR>")
    sync.sync_collection(client, conn, "FR")
    day_dir = raw_dir / "FR" / "2026-07-23"
    assert (day_dir / "FR-2026-07-24.xml").exists()
    assert not (day_dir / "FR-2026-07-24.pdf").exists()
    assert ("get", "https://x/FR-2026-07-24/pdf") not in client.calls  # no wasted request


def test_fr_signature_only_graphics_skip_pdf(conn, raw_dir):
    # Boilerplate-only (FR-GPH-01): a presidential signature is not content.
    client = FakeClient()
    fr_package(
        client, "FR-2026-07-25",
        b'<FR><PRESDOC><GPH DEEP="80" HTYPE="RIGHT"><GID>Trump.EPS</GID></GPH>'
        b'<GPH DEEP="80" HTYPE="RIGHT"><GID>Trump.EPS</GID></GPH></PRESDOC></FR>',
    )
    sync.sync_collection(client, conn, "FR")
    assert not (raw_dir / "FR" / "2026-07-23" / "FR-2026-07-25.pdf").exists()
    assert ("get", "https://x/FR-2026-07-25/pdf") not in client.calls


def test_classify_graphics_rule():
    subs, boil = sync.classify_graphics(
        b"<GID>EN23JY26.004</GID><GID> ER01JA26.123 </GID>"
        b"<GID>Trump.EPS</GID><GID>SomeSeal.EPS</GID>"
    )
    assert (subs, boil) == (2, 2)


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


def test_uscourts_fetch_policy_skips_old_cases(conn):
    # Rule USCOURTS-FETCH-01: churn on old cases is listed but not archived.
    # The window the rule enforces is measured from now(), so the in-window
    # case has to be too: a literal date here passes until the calendar
    # walks past it and then fails for reasons that have nothing to do with
    # the rule (it did, on 2026-08-01, having been written on 2026-07-25).
    import datetime as _dt

    recent = (_dt.datetime.now(_dt.UTC) - _dt.timedelta(days=1)).strftime("%Y-%m-%d")
    client = FakeClient()
    client.pages["collections/USCOURTS/"] = listing([
        {"packageId": "USCOURTS-ca9-1_26-cv-1", "lastModified": "2026-07-25T01:00:00Z",
         "dateIssued": recent},
        {"packageId": "USCOURTS-idb-1_04-bk-1", "lastModified": "2026-07-25T01:00:00Z",
         "dateIssued": "2011-03-02"},
    ])
    sync.sync_collection(client, conn, "USCOURTS", list_only=True)
    rows = dict(conn.execute("SELECT package_id, fetch_status FROM packages"))
    assert rows["USCOURTS-ca9-1_26-cv-1"] == "pending"
    assert rows["USCOURTS-idb-1_04-bk-1"] == "skipped"
    err = conn.execute(
        "SELECT last_error FROM packages WHERE package_id='USCOURTS-idb-1_04-bk-1'"
    ).fetchone()[0]
    assert "USCOURTS-FETCH-01" in err


def test_download_order_is_newest_first(conn, raw_dir):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([
        bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z", date="2026-07-20"),
        bill("BILLS-119s2is", "2026-07-23T11:00:00Z", date="2026-07-24"),
    ])
    for p in ("BILLS-119hr1ih", "BILLS-119s2is"):
        with_summary(client, p)
    sync.sync_collection(client, conn, "BILLS", max_downloads=1)
    fetched = conn.execute(
        "SELECT package_id FROM packages WHERE fetch_status='fetched'"
    ).fetchall()
    assert [r[0] for r in fetched] == ["BILLS-119s2is"]  # newest date first


# ---------------------------------------------------------------- filing --
# Observation-day filing (GUIDE §3, amended 2026-08-06): the three-clocks
# doctrine. digest_day is OUR clock, set at first sight, write-once.


def test_observation_filing_uses_our_clock_not_the_cover_date(conn):
    """A CREC issue observed today files under today, whatever its own
    proceedings date says — the exact CREC-2026-08-04 case (observed
    08-05, proceedings 08-04) that left every frozen digest's section 1
    empty."""
    sync._upsert_package(conn, "CREC", {
        "packageId": "CREC-2026-08-04", "dateIssued": "2026-08-04",
        "lastModified": "2026-08-05T11:34:54Z"})
    row = conn.execute(
        "SELECT date_issued, digest_day FROM packages"
        " WHERE package_id='CREC-2026-08-04'").fetchone()
    assert row["date_issued"] == "2026-08-04"
    assert row["digest_day"] == sync.publication_date()  # today, Eastern


def test_cover_filing_for_fr_keeps_the_legal_publication_date(conn):
    """FR is legally published on its cover date and govinfo posts it
    early (FR-2026-08-03 was observed 08-01) — observation filing would
    misfile it, so config.FILING_POLICY pins it to cover."""
    sync._upsert_package(conn, "FR", {
        "packageId": "FR-2099-01-05", "dateIssued": "2099-01-05",
        "lastModified": "2098-12-30T05:00:00Z"})
    row = conn.execute(
        "SELECT digest_day FROM packages WHERE package_id='FR-2099-01-05'"
    ).fetchone()
    assert row["digest_day"] == "2099-01-05"


def test_digest_day_is_write_once_across_revision_resyncs(conn):
    """A revision re-fetch advances last_modified and re-pends the fetch,
    but must never re-file the document into a later digest — the upsert
    omits digest_day from its ON CONFLICT clause on purpose."""
    pkg = {"packageId": "BILLS-119hr1ih", "dateIssued": "2026-08-01",
           "lastModified": "2026-08-02T00:00:00Z"}
    sync._upsert_package(conn, "BILLS", pkg)
    first = conn.execute(
        "SELECT digest_day FROM packages WHERE package_id='BILLS-119hr1ih'"
    ).fetchone()["digest_day"]
    sync._upsert_package(conn, "BILLS", {**pkg, "lastModified": "2099-01-01T00:00:00Z"})
    row = conn.execute(
        "SELECT digest_day, fetch_status, last_modified FROM packages"
        " WHERE package_id='BILLS-119hr1ih'").fetchone()
    assert row["digest_day"] == first          # never re-filed
    assert row["fetch_status"] == "pending"    # but the revision re-pends
    assert row["last_modified"] == "2099-01-01T00:00:00Z"


# ------------------------------------------------- retry ceiling (GUIDE §4) --
# A permanently-failing package must not be re-attempted forever across
# collector cycles (amended 2026-08-10, the sync-layer analogue of rule 14's
# MAX_ITEM_SUMMARY_ATTEMPTS). Each test below simulates one or more separate
# sync_collection calls as separate collector cycles.


def test_ceiling_marks_package_exhausted_after_max_attempts(conn, raw_dir, monkeypatch):
    monkeypatch.setattr(config, "MAX_PACKAGE_FETCH_ATTEMPTS", 2)
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z")])
    with_summary(client, "BILLS-119hr1ih")
    client.raise_on["https://x/BILLS-119hr1ih/xml"] = RuntimeError("HTTP 503")

    sync.sync_collection(client, conn, "BILLS")  # cycle 1: 1/2 -> failed
    row = conn.execute("SELECT fetch_status, fetch_attempts FROM packages").fetchone()
    assert (row["fetch_status"], row["fetch_attempts"]) == ("failed", 1)

    sync.sync_collection(client, conn, "BILLS")  # cycle 2: 2/2 -> exhausted
    row = conn.execute("SELECT fetch_status, fetch_attempts FROM packages").fetchone()
    assert (row["fetch_status"], row["fetch_attempts"]) == ("exhausted", 2)

    def download_attempts():
        return sum(1 for c in client.calls if c[1] == "https://x/BILLS-119hr1ih/xml")

    before = download_attempts()
    sync.sync_collection(client, conn, "BILLS")  # cycle 3: must not re-attempt
    assert download_attempts() == before  # dropped out of the query entirely


def test_package_succeeding_before_ceiling_is_unaffected(conn, raw_dir):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z")])
    with_summary(client, "BILLS-119hr1ih")
    client.raise_on["https://x/BILLS-119hr1ih/xml"] = RuntimeError("HTTP 503")
    client.content_by_url["https://x/BILLS-119hr1ih/xml"] = b"<bill>text</bill>"

    sync.sync_collection(client, conn, "BILLS")
    row = conn.execute("SELECT fetch_status, fetch_attempts FROM packages").fetchone()
    assert (row["fetch_status"], row["fetch_attempts"]) == ("failed", 1)

    del client.raise_on["https://x/BILLS-119hr1ih/xml"]
    sync.sync_collection(client, conn, "BILLS")
    row = conn.execute("SELECT fetch_status, fetch_attempts FROM packages").fetchone()
    assert (row["fetch_status"], row["fetch_attempts"]) == ("fetched", 0)  # reset, not just unset


def test_fresh_pending_packages_unaffected_by_ceiling(conn, raw_dir):
    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z")])
    with_summary(client, "BILLS-119hr1ih")
    client.content_by_url["https://x/BILLS-119hr1ih/xml"] = b"<bill>text</bill>"

    stats = sync.sync_collection(client, conn, "BILLS")
    assert stats["downloaded"] == 1
    row = conn.execute("SELECT fetch_status, fetch_attempts FROM packages").fetchone()
    assert (row["fetch_status"], row["fetch_attempts"]) == ("fetched", 0)


def test_max_downloads_excludes_exhausted_packages_from_cap(conn, raw_dir):
    # Directly seeded exhausted package (bypassing the ceremony of getting
    # there) alongside one fresh pending package under a 1-slot cap.
    conn.execute(
        "INSERT INTO packages (package_id, collection, last_modified, fetch_status,"
        " first_seen_at, digest_day, fetch_attempts, date_issued)"
        " VALUES ('BILLS-stuck', 'BILLS', '2026-07-23T23:00:00Z', 'exhausted',"
        " '2026-07-23T00:00:00Z', '2026-07-23', ?, '2026-07-23')",
        (config.MAX_PACKAGE_FETCH_ATTEMPTS,),
    )
    conn.commit()

    client = FakeClient()
    client.pages["collections/BILLS/"] = listing([bill("BILLS-119hr1ih", "2026-07-23T10:00:00Z")])
    with_summary(client, "BILLS-119hr1ih")
    client.content_by_url["https://x/BILLS-119hr1ih/xml"] = b"<bill>text</bill>"

    stats = sync.sync_collection(client, conn, "BILLS", max_downloads=1)
    assert stats["downloaded"] == 1
    fetched = conn.execute(
        "SELECT package_id FROM packages WHERE fetch_status='fetched'").fetchall()
    assert [r[0] for r in fetched] == ["BILLS-119hr1ih"]  # got the only slot
    stuck = conn.execute(
        "SELECT fetch_status FROM packages WHERE package_id='BILLS-stuck'").fetchone()
    assert stuck["fetch_status"] == "exhausted"  # never competed for it


def test_revision_after_exhaustion_gets_a_fresh_ceiling(conn):
    conn.execute(
        "INSERT INTO packages (package_id, collection, last_modified, fetch_status,"
        " first_seen_at, digest_day, fetch_attempts, last_attempt_at, date_issued)"
        " VALUES ('BILLS-119hr1ih', 'BILLS', '2026-07-23T10:00:00Z', 'exhausted',"
        " '2026-07-23T00:00:00Z', '2026-07-23', ?, '2026-07-23T10:00:00Z', '2026-07-23')",
        (config.MAX_PACKAGE_FETCH_ATTEMPTS,),
    )
    conn.commit()

    sync._upsert_package(conn, "BILLS", {
        "packageId": "BILLS-119hr1ih", "dateIssued": "2026-07-23",
        "lastModified": "2026-08-01T00:00:00Z"})
    row = conn.execute(
        "SELECT fetch_status, fetch_attempts, last_attempt_at FROM packages"
        " WHERE package_id='BILLS-119hr1ih'").fetchone()
    assert row["fetch_status"] == "pending"      # a revision is a new problem
    assert row["fetch_attempts"] == 0
    assert row["last_attempt_at"] is None


# ---------------------------------------------------------------------------
# The publication clock (GUIDE §3, amended 2026-08-26): one knob, three uses
# ---------------------------------------------------------------------------

TOKYO = __import__("zoneinfo").ZoneInfo("Asia/Tokyo")


def test_publication_day_hour_buckets_on_the_publication_clock():
    """A 03:30Z stamp in summer is 23:30 the evening before in
    Washington: it lands on the PREVIOUS publication day, hour 23 —
    the bar the digest for that day covers, not the next UTC day's."""
    assert sync.publication_day_hour("2026-07-31T03:30:00Z") == ("2026-07-30", 23)
    # winter: 03:30Z is 22:30 EST the evening before
    assert sync.publication_day_hour("2026-01-15T03:30:00Z") == ("2026-01-14", 22)
    # an offset form parses the same way; a bare stamp is UTC
    assert sync.publication_day_hour("2026-07-31T03:30:00+00:00") == ("2026-07-30", 23)
    assert sync.publication_day_hour("2026-07-31T03:30:00") == ("2026-07-30", 23)
    assert sync.publication_day_hour("") is None
    assert sync.publication_day_hour("not a stamp") is None


def test_publication_clock_is_the_configured_zone_not_a_constant():
    """The abstraction, proved rather than asserted: the same code under
    a different zone buckets differently. `tz=` is the seam; the default
    is config.PUBLICATION_TZ read at call time."""
    import datetime as dt

    assert sync.publication_day_hour("2026-07-31T03:30:00Z", tz=TOKYO) == ("2026-07-31", 12)
    assert sync.publication_date(dt.datetime(2026, 7, 31, 3, 30, tzinfo=dt.UTC),
                                 tz=TOKYO) == "2026-07-31"
    assert sync.publication_day_start_utc("2026-07-31", tz=TOKYO) == "2026-07-30T15:00:00Z"


def test_publication_clock_read_at_call_time(monkeypatch):
    """A replaced config attribute holds — the seam every renderer test
    relies on, and what makes FAPD_PUBLICATION_TZ a one-place change."""
    monkeypatch.setattr(config, "PUBLICATION_TZ", TOKYO)
    assert sync.publication_day_hour("2026-07-31T03:30:00Z") == ("2026-07-31", 12)
    assert sync.publication_day_start_utc("2026-07-31") == "2026-07-30T15:00:00Z"


def test_publication_day_start_utc_is_in_the_writers_stamp_format():
    """Bounds a query against stored stamps as a string, so it must be
    the exact ...Z format sync.utc_now_iso writes (CLAUDE.md §10)."""
    assert sync.publication_day_start_utc("2026-07-31") == "2026-07-31T04:00:00Z"   # EDT
    assert sync.publication_day_start_utc("2026-01-15") == "2026-01-15T05:00:00Z"   # EST


def test_dst_nights_are_counted_not_normalized():
    """The publication day has 25 hours on the fall-back night and 23 on
    the spring-forward night; a graph states that instead of hiding it.
    The two 01:30 readings on 2026-11-01 (EDT, then EST) both bucket
    into wall-clock hour 1 — one bar carrying two hours, disclosed."""
    assert sync.publication_day_hours("2026-11-01") == 25
    assert sync.publication_day_hours("2026-03-08") == 23
    assert sync.publication_day_hours("2026-08-26") == 24
    assert sync.publication_day_hour("2026-11-01T05:30:00Z") == ("2026-11-01", 1)
    assert sync.publication_day_hour("2026-11-01T06:30:00Z") == ("2026-11-01", 1)
    assert sync.publication_day_hours("2026-11-01", tz=TOKYO) == 24


def test_fapd_publication_tz_env_knob_reaches_config_and_the_helpers():
    """End to end through the environment, in a fresh interpreter: the
    IANA name, the labels the table does not know derived honestly (a
    zone without a daylight shift keeps its own abbreviation), and the
    bucketing helpers following the knob. An unknown zone fails loud."""
    import os
    import subprocess
    import sys

    probe = (
        "from fapd import config, sync;"
        "print(config.PUBLICATION_TZ.key, config.PUBLICATION_TZ_ABBREV,"
        " config.PUBLICATION_TZ_PLACE, config.PUBLICATION_TZ_LABEL,"
        " sync.publication_day_hour('2026-07-31T03:30:00Z'), sep='|')"
    )
    env = {**os.environ, "FAPD_PUBLICATION_TZ": "Asia/Tokyo"}
    out = subprocess.run([sys.executable, "-c", probe], env=env,
                         capture_output=True, text=True, check=True).stdout.strip()
    assert out == "Asia/Tokyo|JST|Tokyo|Tokyo time|('2026-07-31', 12)"

    env["FAPD_PUBLICATION_TZ_LABEL"] = "Japan Standard Time"
    env["FAPD_PUBLICATION_TZ_ABBREV"] = "JT"
    env["FAPD_PUBLICATION_TZ_PLACE"] = "Tokyo, Japan"
    out = subprocess.run([sys.executable, "-c", probe], env=env,
                         capture_output=True, text=True, check=True).stdout.strip()
    assert out == "Asia/Tokyo|JT|Tokyo, Japan|Japan Standard Time|('2026-07-31', 12)"

    bad = subprocess.run([sys.executable, "-c", probe],
                         env={**os.environ, "FAPD_PUBLICATION_TZ": "Not/AZone"},
                         capture_output=True, text=True, check=False)
    assert bad.returncode != 0
    assert "Not/AZone" in bad.stderr


def test_the_default_clock_is_washingtons():
    """Production's clock, and the labels the digests already print."""
    assert config.PUBLICATION_TZ.key == "America/New_York"
    assert (config.PUBLICATION_TZ_LABEL, config.PUBLICATION_TZ_ABBREV,
            config.PUBLICATION_TZ_PLACE) == ("Eastern time", "ET", "Washington, D.C.")


def test_unknown_zone_labels_derive_from_the_city():
    """A fork that sets only FAPD_PUBLICATION_TZ gets an honest, readable
    label rather than a wrong 'ET' or a raw IANA string (adopted from the
    parallel 2026-08-26 branch): the curated entry for the default, the
    city otherwise, and a seasonal abbreviation never leaks through."""
    from fapd import config

    assert config.publication_tz_names("America/New_York") == (
        "Eastern time", "ET", "Washington, D.C.")
    assert config.publication_tz_names("America/Denver") == (
        "Denver time", "Denver", "Denver")          # MST/MDT flips -> city
    assert config.publication_tz_names("Asia/Tokyo") == (
        "Tokyo time", "JST", "Tokyo")               # fixed JST is kept
    assert config.publication_tz_names("Asia/Ho_Chi_Minh")[0] == "Ho Chi Minh time"

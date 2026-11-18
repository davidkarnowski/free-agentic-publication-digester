"""The item counts read only the count indexes (db._COUNT_INDEXES).

On 2026-11-17 the source-health refresh ran five counts every 15 minutes,
and each one read about 2.3 GiB of production's 2.4 GB database: every
lookup into extracted_texts (a WITHOUT ROWID table whose rows hold the
full text) compared whole rows. These tests pin that every count is
answered from the indexes alone, so a later edit that reads another
extracted_texts column fails here instead of on the server.
"""

import sqlite3

import pytest

from fapd import collect, db, health, publish

_DAY = ("2026-11-01", "2026-11-14")
_STAMP = ("2026-11-13T05:00:00Z", "2026-11-14T05:00:00Z")

COUNTS = {
    "window_rows": (health._WINDOW_ROWS_SQL, _DAY),
    "recency": (health._RECENCY_SQL, ("2026-05-18", "2026-11-14")),
    "recent_items": (health._RECENT_ITEMS_SQL, _STAMP),
    "hourly_items": (health._HOURLY_ITEMS_SQL.format(klen=13), _STAMP),
    "hourly_items_minute": (health._HOURLY_ITEMS_SQL.format(klen=16), _STAMP),
    "daily_items": (publish._DAILY_ITEMS_SQL, _DAY),
}


def _plan(conn, sql, params):
    return [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params)]


@pytest.mark.parametrize("name", sorted(COUNTS))
def test_count_is_answered_from_the_indexes_alone(tmp_path, name):
    conn = db.connect(tmp_path / "fapd.db")
    sql, params = COUNTS[name]
    plan = _plan(conn, sql, params)
    steps = {}
    for line in plan:
        words = line.split()
        if words and words[0] in ("SCAN", "SEARCH"):
            steps[words[1]] = line
    assert set(steps) == {"e", "p"}, plan
    assert "USING COVERING INDEX idx_extracted_counts" in steps["e"], plan
    assert "USING COVERING INDEX idx_packages_" in steps["p"], plan
    conn.close()


def test_counts_are_unchanged_by_the_indexes(tmp_path):
    """Same rows with and without the indexes: they change how a count is
    read, never what it says."""
    conn = db.connect(tmp_path / "fapd.db")
    rows = [
        ("CREC-2026-11-03", "CREC", "2026-11-03", "2026-11-03T15:00:00Z",
         [("g1", '{"mode": "full"}', 1200), ("g2", "{}", 40)]),
        ("AGENCYPR-x", "AGENCYPR", "2026-11-13", "2026-11-13T09:30:00Z",
         [("", '{"mode": "feed", "source_id": "omb-saps"}', 300)]),
        ("FR-2026-04-01", "FR", "2026-04-01", "2026-04-01T11:00:00Z",
         [("doc", '{"source_id": null}', 9000)]),
    ]
    for pkg, coll, day, seen, granules in rows:
        conn.execute(
            "INSERT INTO packages (package_id, collection, last_modified,"
            " first_seen_at, digest_day) VALUES (?, ?, ?, ?, ?)",
            (pkg, coll, seen, seen, day))
        for gid, meta, chars in granules:
            conn.execute(
                "INSERT INTO extracted_texts (package_id, granule_id,"
                " collection, metadata, text, char_count, extracted_at,"
                " extractor_version) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                (pkg, gid, coll, meta, "x" * chars, chars, seen))
    conn.commit()

    def every_count():
        return {name: sorted(tuple(r) for r in conn.execute(sql, params))
                for name, (sql, params) in COUNTS.items()}

    with_indexes = every_count()
    for name in ("idx_packages_digest_day", "idx_packages_first_seen",
                 "idx_extracted_counts"):
        conn.execute(f"DROP INDEX {name}")
    assert every_count() == with_indexes
    assert with_indexes["window_rows"]  # the fixture reaches the windows
    assert with_indexes["recent_items"]
    conn.close()


def test_indexes_build_on_a_database_from_before_digest_day(tmp_path):
    """digest_day is a migrated column (2026-08-06), so its index is
    created after the migrations; a pre-cutover database still opens."""
    path = tmp_path / "old.db"
    raw = sqlite3.connect(path)
    raw.execute(
        "CREATE TABLE packages (package_id TEXT PRIMARY KEY,"
        " collection TEXT NOT NULL, date_issued TEXT,"
        " last_modified TEXT NOT NULL, title TEXT, package_link TEXT,"
        " download_url TEXT, download_format TEXT, raw_path TEXT,"
        " fetch_status TEXT NOT NULL DEFAULT 'pending',"
        " first_seen_at TEXT NOT NULL, fetched_at TEXT,"
        " fetched_last_modified TEXT, last_error TEXT,"
        " fetch_attempts INTEGER NOT NULL DEFAULT 0, last_attempt_at TEXT)")
    raw.commit()
    raw.close()
    conn = db.connect(path)
    names = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index'")}
    assert {"idx_packages_digest_day", "idx_packages_first_seen",
            "idx_extracted_counts"} <= names
    conn.close()


def test_run_forever_opens_the_database_before_any_worker_starts():
    """The index build reads the whole table once; it must run before the
    workers start, not under the first of them while the rest wait."""
    events = []

    class FakeConn:
        def close(self):
            events.append("closed")

    def conn_factory():
        events.append("opened")
        return FakeConn()

    class FakeWorker:
        name = "fake"

        def loop(self, stop_event):
            events.append("worker")

    sup = collect.Supervisor.__new__(collect.Supervisor)
    sup.conn_factory = conn_factory
    sup.workers = [FakeWorker()]
    stop, threads = sup.run_forever()
    for t in threads:
        t.join(timeout=5)
    stop.set()
    assert events == ["opened", "closed", "worker"]


def test_run_forever_starts_workers_when_the_first_open_fails():
    started = []

    def conn_factory():
        raise sqlite3.OperationalError("database is locked")

    class FakeWorker:
        name = "fake"

        def loop(self, stop_event):
            started.append(True)

    sup = collect.Supervisor.__new__(collect.Supervisor)
    sup.conn_factory = conn_factory
    sup.workers = [FakeWorker()]
    stop, threads = sup.run_forever()
    for t in threads:
        t.join(timeout=5)
    stop.set()
    assert started == [True]

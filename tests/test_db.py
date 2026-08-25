"""Schema tests: the self-migrating connect() contract and the
continuous-ingestion tables (docs/schema.md is the design authority)."""

import sqlite3

import pytest

from fapd import db


def table_names(conn):
    return {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}


def test_connect_creates_continuous_ingestion_tables(conn):
    assert {"item_journal", "collector_state", "item_tags"} <= table_names(conn)


def test_connect_twice_is_idempotent(tmp_path):
    # The migration mechanism IS re-running the DDL on connect; a second
    # connect against an existing DB must be a no-op, not an error.
    path = tmp_path / "meta.db"
    c1 = db.connect(path)
    c1.execute(
        "INSERT INTO collector_state (worker, last_ok_at) VALUES ('govinfo', 'x')")
    c1.commit()
    c1.close()
    c2 = db.connect(path)
    assert c2.execute("SELECT COUNT(*) FROM collector_state").fetchone()[0] == 1
    c2.close()


def test_item_journal_unique_per_item_and_event(conn):
    row = ("2026-07-30T12:00:00Z", "agency", "P1", "G1", "AGENCYPR",
           "gao-reports", "2026-07-30", "ingested", "c1")
    ins = ("INSERT INTO item_journal (observed_at, source_class, package_id,"
           " granule_id, collection, source_id, digest_date, event, cycle_id)"
           " VALUES (?,?,?,?,?,?,?,?,?)")
    conn.execute(ins, row)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(ins, row)  # same (package, granule, event)
    # a different event for the same item is a new row, by design
    conn.execute(ins, row[:7] + ("summarized", "c2"))
    assert conn.execute("SELECT COUNT(*) FROM item_journal").fetchone()[0] == 2


def test_item_journal_rejects_unknown_source_class_and_event(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO item_journal (observed_at, source_class, package_id, event)"
            " VALUES ('x', 'carrier-pigeon', 'P1', 'ingested')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO item_journal (observed_at, source_class, package_id, event)"
            " VALUES ('x', 'agency', 'P1', 'vibed')")


def test_item_tags_key_and_method_constraints(conn):
    conn.execute(
        "INSERT INTO item_tags (package_id, granule_id, tag_kind, tag, method,"
        " created_at) VALUES ('P1', '', 'branch', 'legislative', 'mechanical', 'x')")
    with pytest.raises(sqlite3.IntegrityError):  # duplicate tag row
        conn.execute(
            "INSERT INTO item_tags (package_id, granule_id, tag_kind, tag, method,"
            " created_at) VALUES ('P1', '', 'branch', 'legislative', 'mechanical', 'x')")
    with pytest.raises(sqlite3.IntegrityError):  # unknown kind
        conn.execute(
            "INSERT INTO item_tags (package_id, granule_id, tag_kind, tag, method,"
            " created_at) VALUES ('P1', '', 'vibe', 'x', 'mechanical', 'x')")


# ------------------------------------------ the start-up migration race --
# Deploy 2026-08-25 01:19Z: three new packages columns, ~30 supervisor
# connections opening at once, 25 worker threads dead on "duplicate
# column name" before their first cycle.


class _StalePragmaConn:
    """A connection whose PRAGMA table_info answers as if the columns were
    still missing — the losing side of the race, deterministically."""

    def __init__(self, real, hide):
        self._real = real
        self._hide = hide

    def execute(self, sql, *a):
        cur = self._real.execute(sql, *a)
        if sql.startswith("PRAGMA table_info"):
            rows = [r for r in cur.fetchall() if r["name"] not in self._hide]
            return rows
        return cur

    def commit(self):
        self._real.commit()


def test_ensure_columns_tolerates_losing_the_race(tmp_path):
    from fapd import db

    real = db.connect(tmp_path / "race.db")
    real.execute("CREATE TABLE t (id INTEGER PRIMARY KEY)")
    real.execute("ALTER TABLE t ADD COLUMN c1 TEXT")   # "another connection" won
    real.commit()

    db._ensure_columns(_StalePragmaConn(real, {"c1"}), "t", {"c1": "TEXT", "c2": "TEXT"})
    cols = {r["name"] for r in real.execute("PRAGMA table_info(t)")}
    assert cols == {"id", "c1", "c2"}, "c1 already there is success; c2 still added"
    real.close()


def test_ensure_columns_still_raises_real_errors(tmp_path):
    import sqlite3

    import pytest

    from fapd import db

    real = db.connect(tmp_path / "race2.db")
    with pytest.raises(sqlite3.OperationalError):
        db._ensure_columns(real, "no_such_table", {"c1": "TEXT"})
    real.close()

"""Tests for scripts/audit.py's repeat-failures diagnostic (GUIDE §4,
amended 2026-08-10) — the view that makes the per-package retry ceiling's
effect measurable, distinct from fetch_log's per-attempt rows."""

import audit

from fapd import db


def seed_package(conn, package_id, *, fetch_status="failed", fetch_attempts=1,
                 last_attempt_at="2026-08-10T12:00:00Z", collection="BILLS",
                 last_error="HTTP 503"):
    conn.execute(
        "INSERT INTO packages (package_id, collection, last_modified, fetch_status,"
        " first_seen_at, fetch_attempts, last_attempt_at, last_error)"
        " VALUES (?, ?, '2026-08-10T00:00:00Z', ?, '2026-08-10T00:00:00Z', ?, ?, ?)",
        (package_id, collection, fetch_status, fetch_attempts, last_attempt_at, last_error),
    )
    conn.commit()


def test_repeat_failures_report_orders_by_attempts_descending(tmp_path):
    db_path = tmp_path / "fapd.db"
    conn = db.connect(db_path)
    seed_package(conn, "BILLS-low", fetch_attempts=2, last_attempt_at="2026-08-10T10:00:00Z")
    seed_package(conn, "BILLS-high", fetch_attempts=40, last_attempt_at="2026-08-10T11:00:00Z")
    seed_package(conn, "BILLS-untouched", fetch_attempts=0)  # never attempted
    conn.close()

    rows = audit.repeat_failures_report(db_path)
    assert [r["package_id"] for r in rows] == ["BILLS-high", "BILLS-low"]
    assert rows[0]["fetch_attempts"] == 40
    assert rows[0]["last_error"] == "HTTP 503"


def test_repeat_failures_report_respects_limit(tmp_path):
    db_path = tmp_path / "fapd.db"
    conn = db.connect(db_path)
    for i in range(5):
        seed_package(conn, f"BILLS-{i}", fetch_attempts=i + 1)
    conn.close()

    rows = audit.repeat_failures_report(db_path, limit=3)
    assert len(rows) == 3


def test_repeat_failures_report_empty_database(tmp_path):
    db_path = tmp_path / "fapd.db"
    conn = db.connect(db_path)
    conn.close()

    assert audit.repeat_failures_report(db_path) == []


# ------------------------------------- extraction repeat failures (2026-08-24) --


def seed_extraction_failure(conn, package_id, *, attempts, at, error="ParseError"):
    conn.execute(
        "INSERT INTO packages (package_id, collection, last_modified, fetch_status,"
        " first_seen_at, extract_attempts, last_extract_attempt_at, extract_error)"
        " VALUES (?, 'FR', '2026-08-06T00:00:00Z', 'fetched', '2026-08-06T00:00:00Z',"
        " ?, ?, ?)",
        (package_id, attempts, at, error),
    )
    conn.commit()


def test_extraction_repeat_failures_report_lists_repeaters_by_attempts(tmp_path):
    db_path = tmp_path / "fapd.db"
    conn = db.connect(db_path)
    seed_extraction_failure(conn, "FR-1995-01-04", attempts=5,
                            at="2026-08-24T19:14:39Z",
                            error="ParseError('not well-formed')")
    seed_extraction_failure(conn, "FR-once", attempts=1, at="2026-08-24T18:00:00Z")
    seed_package(conn, "BILLS-fetch-only", fetch_attempts=3)  # fetch-layer, not ours
    conn.close()

    rows = audit.extraction_repeat_failures_report(db_path)
    assert [r["package_id"] for r in rows] == ["FR-1995-01-04", "FR-once"]
    assert rows[0]["extract_attempts"] == 5
    assert "ParseError" in rows[0]["extract_error"]
    # and the fetch-layer report does not see extraction failures
    assert [r["package_id"] for r in audit.repeat_failures_report(db_path)] == [
        "BILLS-fetch-only"]

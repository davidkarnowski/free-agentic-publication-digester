"""Operator notices (2026-11-12): what an end-of-day event writes, and that
writing one can never fail the work that raised it. No network: notices
are files; delivering them is the operator's, outside this repository."""

import datetime as dt
import json
import os
import stat

import pytest
from test_collect import make_supervisor

from fapd import collect, config, notices

AT = dt.datetime(2026, 11, 12, 5, 13, 15, tzinfo=dt.UTC)


def _read(folder):
    files = sorted(p for p in folder.iterdir() if not p.name.startswith("."))
    return [json.loads(p.read_text(encoding="utf-8")) for p in files]


def test_off_when_no_directory_is_configured(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "NOTICE_DIR", "")
    assert notices.emit("eod.published", "2026-11-11", "t") is None
    assert list(tmp_path.iterdir()) == []


def test_a_notice_has_the_common_shape_and_leaves_no_temp_file(tmp_path):
    path = notices.emit("eod.halted", "2026-11-11", "FAPD 2026-11-11: halted",
                        "Fix it.", {"Attempts": "4 of 4"},
                        notice_dir=tmp_path, now=AT)
    assert path is not None and path.parent == tmp_path
    assert [p.name for p in tmp_path.iterdir() if p.name.startswith(".")] == []
    (n,) = _read(tmp_path)
    assert n["v"] == 1 and n["kind"] == "fapd-eod-halted" and n["level"] == "alert"
    assert n["subject"] == n["title"] == "FAPD 2026-11-11: halted"  # emit(): subject defaults to title
    assert n["fields"] == {"Day": "2026-11-11", "Attempts": "4 of 4", "Detail": "Fix it."}
    assert n["queued_at"] == "2026-11-12T05:13:15Z"
    assert (n["source"], n["event"], n["day"]) == ("fapd", "eod.halted", "2026-11-11")
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o640


def test_text_is_one_line_and_bounded(tmp_path):
    notices.emit("eod.failed", "2026-11-11", "a\nb " + "x" * 500, "line\none",
                 {"K\n": "v\r\nw"}, notice_dir=tmp_path)
    (n,) = _read(tmp_path)
    assert "\n" not in json.dumps(n["title"]) and len(n["title"]) <= 160
    assert len(n["subject"]) <= 110
    assert n["fields"]["K"] == "v w" and n["fields"]["Detail"] == "line one"


def test_only_https_links_are_written(tmp_path):
    notices.emit("eod.published", "d", "t", link="javascript:alert(1)", notice_dir=tmp_path)
    notices.emit("eod.published", "d", "t", link="https://example.org/d.html", notice_dir=tmp_path)
    links = sorted(n.get("link") or "" for n in _read(tmp_path))
    assert links == ["", "https://example.org/d.html"]


def test_an_unwritable_or_unknown_notice_never_raises(tmp_path, caplog):
    assert notices.emit("eod.unknown", "d", "t", notice_dir=tmp_path) is None
    assert notices.emit("eod.failed", "d", "t", notice_dir=tmp_path / "missing") is None
    assert "not written" in caplog.text


@pytest.mark.parametrize("attempts, event", [(1, "eod.failed"), (2, None), (3, None),
                                              (4, "eod.halted"), (5, "eod.halted")])
def test_a_failing_night_sends_the_first_failure_and_the_halt(tmp_path, attempts, event,
                                                              monkeypatch):
    monkeypatch.setattr(config, "NOTICE_DIR", str(tmp_path))
    notices.finalize_failed("2026-11-11", attempts, 4, 1)
    assert [n["event"] for n in _read(tmp_path)] == ([event] if event else [])


@pytest.mark.parametrize("attempts, event", [(1, "eod.push_failed"), (2, None),
                                              (3, "eod.push_halted")])
def test_a_failing_push_sends_the_first_failure_and_the_halt(tmp_path, attempts, event,
                                                             monkeypatch):
    monkeypatch.setattr(config, "NOTICE_DIR", str(tmp_path))
    notices.evidence_push_failed("2026-11-11", attempts, 3, 5)
    assert [n["event"] for n in _read(tmp_path)] == ([event] if event else [])


def test_published_names_a_recovery_and_links_the_day(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "NOTICE_DIR", str(tmp_path))
    monkeypatch.setattr(config, "SITE_BASE_URL", "https://example.org")
    notices.published("2026-11-11", pushed=True, failed_attempts=4)
    (n,) = _read(tmp_path)
    assert n["subject"] == "2026-11-11: digest published after 4 failed attempt(s)"
    assert n["title"] == "FAPD 2026-11-11: digest published after 4 failed attempt(s)"
    assert n["level"] == "ok" and n["link"] == "https://example.org/2026-11-11.html"
    assert n["fields"]["Repository"] == "pushed"


# -- through the end-of-day worker ---------------------------------------------


def _worker(tmp_path, monkeypatch, *, finalize_rc=0, push_rc=0, push=True):
    sup, conn_factory = make_supervisor(tmp_path, monkeypatch)
    sup.finalizer_runner = lambda date=None: finalize_rc
    sup.evidence_runner = lambda: push_rc
    monkeypatch.setattr(config, "EVIDENCE_PUSH", push)
    box = tmp_path / "notices"
    box.mkdir()
    monkeypatch.setattr(config, "NOTICE_DIR", str(box))
    return collect.EODWorker(sup, 10), conn_factory(), box


def test_a_published_night_sends_one_ok_notice(tmp_path, monkeypatch):
    worker, conn, box = _worker(tmp_path, monkeypatch)
    worker.finalize_now(conn, "c1", "2026-11-11")
    assert [(n["event"], n["fields"]["Repository"]) for n in _read(box)] == [
        ("eod.published", "pushed")]


def test_failures_then_a_recovery(tmp_path, monkeypatch):
    worker, conn, box = _worker(tmp_path, monkeypatch, finalize_rc=1)
    for _ in range(config.EOD_MAX_FINALIZE_ATTEMPTS):
        with pytest.raises(RuntimeError):
            worker.finalize_now(conn, "c", "2026-11-11")
    worker.sup.finalizer_runner = lambda date=None: 0
    worker.finalize_now(conn, "c", "2026-11-11")
    got = [(n["event"], n["subject"]) for n in _read(box)]
    assert [e for e, _ in got] == ["eod.failed", "eod.halted", "eod.published"]
    assert got[-1][1].endswith(f"after {config.EOD_MAX_FINALIZE_ATTEMPTS} failed attempt(s)")


def test_a_failed_push_sends_a_push_notice_not_a_published_one(tmp_path, monkeypatch):
    worker, conn, box = _worker(tmp_path, monkeypatch, push_rc=4)
    worker.finalize_now(conn, "c1", "2026-11-11")
    assert [n["event"] for n in _read(box)] == ["eod.push_failed"]


def test_a_notice_failure_never_fails_the_finalize(tmp_path, monkeypatch):
    worker, conn, _box = _worker(tmp_path, monkeypatch)
    monkeypatch.setattr(config, "NOTICE_DIR", str(tmp_path / "gone"))
    result = worker.finalize_now(conn, "c1", "2026-11-11")
    assert result["ran"] and result["pushed"]
    row = conn.execute("SELECT finalized_date FROM collector_state WHERE worker='eod'").fetchone()
    assert row["finalized_date"] == "2026-11-11"


def test_end_of_day_subjects_name_the_day_not_the_project(tmp_path, monkeypatch):
    """Whatever delivers a notice labels its source; the subject carries
    the day and the event, the title adds the project for the body."""
    monkeypatch.setattr(config, "NOTICE_DIR", str(tmp_path))
    notices.finalize_failed("2026-11-11", 4, 4, 1)
    notices.evidence_push_failed("2026-11-11", 1, 3, 4)
    for n in _read(tmp_path):
        assert n["subject"].startswith("2026-11-11: ") and not n["subject"].startswith("FAPD")
        assert n["title"] == "FAPD " + n["subject"]

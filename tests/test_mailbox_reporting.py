"""Mailbox reporting (plan-2026-09-26-mailbox-reporting T3/T5): health,
the source pages, and the nightly insight report read mailbox_messages.
Fakes and a temporary database only."""

import json

import pytest

from fapd import db, health, insight, publish


def _row(conn, uid, outcome, *, source_id="epa-email", sender="x@govdelivery.epa.gov",
         items=0, no_url=0, mailbox="INBOX", at="2026-09-26T12:00:00Z"):
    conn.execute(
        "INSERT INTO mailbox_messages (mailbox, uid_validity, uid, observed_at,"
        " source_id, sender, outcome, items, duplicates, no_url_items, dkim)"
        " VALUES (?, 1, ?, ?, ?, ?, ?, ?, 0, ?, 'pass')",
        (mailbox, uid, at, source_id, sender, outcome, items, no_url))
    conn.commit()


@pytest.fixture
def conn(tmp_path):
    c = db.connect(tmp_path / "p.db")
    yield c
    c.close()


def test_planned_email_sources_are_measured_planned_web_are_not():
    assert health.is_measured({"status": "planned", "type": "email"})
    assert not health.is_measured({"status": "planned", "type": "rss"})
    assert health.is_measured({"status": "active", "type": "rss"})


def test_collect_mailbox_counts_outcomes(conn):
    for uid, outcome in enumerate(["ingested", "administrative", "administrative",
                                   "refused", "empty"], 1):
        _row(conn, uid, outcome)
    conn.row_factory = __import__("sqlite3").Row
    box = health._collect_mailbox(conn, "2026-09-01T00:00:00")["epa-email"]
    assert box == {"messages": 5, "bulletins": 2, "administrative": 2,
                   "refused": 1, "errors": 0,
                   "last_message_at": "2026-09-26T12:00:00Z"}


def test_notice_only_subscription_reads_differently_from_silence():
    label, reason = health.classify(
        items=0, last_item_date=None, days_since_item=None, fetch=None,
        collector=None, is_email=True,
        mailbox={"administrative": 2, "bulletins": 0})
    assert label == health.NO_DATA
    assert reason.startswith("Subscription confirmed (2 subscription notice(s)")
    _label, silent = health.classify(
        items=0, last_item_date=None, days_since_item=None, fetch=None,
        collector=None, is_email=True, mailbox={"administrative": 0, "bulletins": 0})
    assert silent.startswith("No bulletin recorded")


def test_mailbox_sentence_on_cards_and_pages():
    record = {"window_days": 14, "mailbox": {
        "messages": 5, "bulletins": 3, "administrative": 1, "refused": 1,
        "errors": 0, "last_message_at": "2026-09-26T12:00:00Z"}}
    text = publish._mailbox_sentence(record)
    assert text == ("3 bulletin(s), 1 subscription notice(s), 1 junk-folder "
                    "message(s) refused on a failed or unaligned DKIM signature "
                    "in the last 14 days; most recent message 2026-09-26")
    assert publish._mailbox_sentence({"mailbox": None}) is None


def test_insight_email_section_flags_misclassification(conn):
    entries = [{"id": "epa-email", "type": "email", "status": "planned"},
               {"id": "cpsc-email", "type": "email", "status": "planned"}]
    _row(conn, 1, "ingested", items=2, no_url=1)
    _row(conn, 2, "empty")
    _row(conn, 3, "refused", mailbox="Junk")
    _row(conn, 4, "administrative", source_id="cpsc-email", sender="a@info.cpsc.gov")
    _row(conn, 5, "unregistered", source_id=None, sender="news@new.example.gov")
    email = insight.gather_email(conn, "2026-09-26T00:00:00", "2026-09-27T00:00:00",
                                 entries)
    flags = "\n".join(email["flags"])
    assert "epa-email: 1 bulletin(s) yielded no item" in flags
    assert "epa-email: 1 item(s) stored without a URL" in flags
    assert "epa-email: 1 junk-folder message(s) refused" in flags
    assert "cpsc-email: only subscription notices" in flags
    assert "1 government list sender(s) seen for the first time" in flags
    assert email["unregistered"] == {"messages": 1, "senders": 1, "new_senders": 1}


def test_insight_email_section_never_prints_an_address(conn):
    _row(conn, 1, "ingested", items=1)
    _row(conn, 2, "unregistered", source_id=None, sender="news@new.example.gov")
    email = insight.gather_email(conn, "2026-09-26T00:00:00", "2026-09-27T00:00:00",
                                 [{"id": "epa-email", "type": "email", "status": "planned"}])
    text = "\n".join(insight.render_email(email)) + json.dumps(email)
    assert "@" not in text


def test_insight_email_section_without_the_table():
    import sqlite3
    bare = sqlite3.connect(":memory:")
    assert insight.gather_email(bare, "a", "b", []) == {"available": False}
    assert "not present" in "\n".join(insight.render_email({"available": False}))

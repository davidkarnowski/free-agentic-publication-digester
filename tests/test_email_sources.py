"""Email-source ingestion tests: fakes only, no network, no live mailbox.

Bulletin fixtures mirror the structure of real captured messages
(2026-07-29): a multi-item GovDelivery digest whose HTML anchors carry the
title plus a tracking-wrapped canonical URL, and whose plain-text part runs
summaries and the next title together on one line.
"""

import email
import email.policy

import pytest
from conftest import install_digest_day_default

from fapd import config, db, email_sources

TRACK = "https://links-2.govdelivery.com/CL0/https:%2F%2Fwww.justice.gov%2Fusao-edva%2Fpr%2Fglen-allen/1/010101/x"
TRACK2 = "https://links-2.govdelivery.com/CL0/https:%2F%2Fwww.justice.gov%2Fusao-edla%2Fpr%2Ftexas-man/1/010101/x"

MULTI = f"""From: Offices of the United States Attorneys <usattorneys@public.govdelivery.com>
To: mailbox@example.org
Subject: U.S. Attorneys News News Update
Date: Wed, 29 Jul 2026 21:16:55 +0000
Message-ID: <bulletin-1@public.govdelivery.com>
DKIM-Signature: v=1; a=rsa-sha256; d=public.govdelivery.com; s=sel1;
 h=from:subject; b=AAAA
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="B"

--B
Content-Type: text/plain; charset="utf-8"

You are subscribed to U.S. Attorneys News news updates.

Glen Allen man sentenced [ https://www.justice.gov/usao-edva/pr/glen-allen ] 07/29/2026 08:00 AM EDT
Phillip Michael Taft, 40, was sentenced to nineteen years and seven months in prison for distribution of unlawful material. Texas Man Sentenced for Misprision [ https://www.justice.gov/usao-edla/pr/texas-man ] 07/29/2026 09:30 AM EDT
ELDER CAMACHO, age 36, a resident of Texas, was sentenced on July 29 after previously pleading guilty to the charge.

________________________________________________________________________

Manage your Subscriptions [ https://public.govdelivery.com/accounts/USDOJUSAO/subscriber/new?preferences=true ]

--B
Content-Type: text/html; charset="utf-8"

<html><body>
<a href="{TRACK}">Glen Allen man sentenced</a>
<a href="{TRACK2}">Texas Man Sentenced for Misprision</a>
<a href="https://public.govdelivery.com/accounts/USDOJUSAO/subscriber/new?preferences=true">Manage your Subscriptions</a>
<a href="https://twitter.com/usattorneys">Twitter</a>
</body></html>
--B--
""".encode()

SINGLE = b"""From: USPS Office of Inspector General <uspsoig@public.govdelivery.com>
To: mailbox@example.org
Subject: OIG Audit Assesses the Vetting Process
Date: Wed, 29 Jul 2026 20:00:09 +0000
Message-ID: <bulletin-2@public.govdelivery.com>
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="B"

--B
Content-Type: text/plain; charset="utf-8"

GovDel Header

OIG Audit Assesses the Vetting Process [ https://www.uspsoig.gov/reports/audit-reports/vetting ]

From fiscal years 2023 through 2025 the Postal Service hired 371,937 employees nationwide. Our latest audit assesses the background screening process.

--B
Content-Type: text/html; charset="utf-8"

<html><body>
<a href="https://links-2.govdelivery.com/CL0/https:%2F%2Fwww.uspsoig.gov%2Freports%2Faudit-reports%2Fvetting/1/01/x">OIG Audit Assesses the Vetting Process</a>
</body></html>
--B--
"""

PERSONAL = b"""From: A Friend <friend@example.com>
To: mailbox@example.org
Subject: dinner plans
Date: Wed, 29 Jul 2026 18:00:00 +0000
Message-ID: <personal-1@example.com>

Private content that must never be fetched or parsed.
"""


def entry(id="usattorneys-email", sender="usattorneys@public.govdelivery.com",
          name="Offices of the United States Attorneys"):
    return {"id": id, "name": name, "sender": sender, "type": "email",
            "status": "planned"}


class FakeMailbox:
    """Stands in for MailboxClient; records which bodies were fetched so the
    allowlist-before-download guarantee can be asserted."""

    folder = "INBOX"

    def __init__(self, messages, uid_validity=42):
        self.messages = dict(enumerate(messages, start=1))
        self._uid_validity = uid_validity
        self.bodies_fetched = []

    def uid_validity(self):
        return self._uid_validity

    def uids_since(self, last_uid):
        return [u for u in sorted(self.messages) if u > int(last_uid)]

    def headers(self, uid):
        raw = self.messages[uid]
        head = raw.split(b"\n\n", 1)[0]
        return email.message_from_bytes(head, policy=email.policy.default)

    def raw(self, uid):
        self.bodies_fetched.append(uid)
        return self.messages[uid]


def no_dkim(raw):
    return {"result": "pass", "domain": "public.govdelivery.com",
            "selector": "sel1", "key_record": "v=DKIM1; k=rsa; p=TESTKEY"}


@pytest.fixture
def conn(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CAPTURE_DIR", tmp_path / "captures")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")
    connection = install_digest_day_default(db.connect(tmp_path / "meta.db"))
    yield connection
    connection.close()


# ------------------------------------------------------------------ parsing --


def test_tracking_url_decoded_never_fetched():
    """The canonical URL is recovered by static decode of the wrapper the
    publisher sent — following the redirect would be a fetch."""
    assert (email_sources.decode_tracking_url(TRACK)
            == "https://www.justice.gov/usao-edva/pr/glen-allen")
    # a plain URL passes through untouched
    assert email_sources.decode_tracking_url("https://x.gov/a") == "https://x.gov/a"


def test_multi_item_bulletin_splits_into_items():
    msg = email.message_from_bytes(MULTI, policy=email.policy.default)
    items = email_sources.parse_bulletin(msg)
    assert len(items) == 2  # platform + social anchors excluded
    first, second = items
    assert first["title"] == "Glen Allen man sentenced"
    assert first["url"] == "https://www.justice.gov/usao-edva/pr/glen-allen"
    assert "Phillip Michael Taft" in first["summary"]
    # the next item's title must not bleed into this summary
    assert "Texas Man Sentenced" not in first["summary"]
    assert first["claimed_date"] == "2026-07-29T08:00:00"  # per-item, not header
    assert second["title"] == "Texas Man Sentenced for Misprision"
    assert "ELDER CAMACHO" in second["summary"]


def test_single_item_bulletin():
    msg = email.message_from_bytes(SINGLE, policy=email.policy.default)
    items = email_sources.parse_bulletin(msg)
    assert len(items) == 1
    assert items[0]["url"] == "https://www.uspsoig.gov/reports/audit-reports/vetting"
    assert "371,937 employees" in items[0]["summary"]


def test_boilerplate_stripped():
    out = email_sources.strip_boilerplate(
        "You are subscribed to X news updates.\nReal content here.\n"
        + "_" * 40 + "\nManage your Subscriptions")
    assert out == "Real content here."


def test_bulletin_without_item_structure_falls_back_to_whole_body():
    raw = SINGLE.replace(b"<html><body>", b"<html><body><!--").replace(
        b"</body></html>", b"--></body></html>")
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    items = email_sources.parse_bulletin(msg)
    assert len(items) == 1
    assert items[0]["title"] == "OIG Audit Assesses the Vetting Process"
    assert "371,937" in items[0]["summary"]


# ------------------------------------------------------------------ ingest --


def test_ingest_stores_items_capture_and_dkim(conn):
    box = FakeMailbox([MULTI])
    results = email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    assert results[0]["messages"] == 1 and results[0]["items"] == 2

    rows = conn.execute(
        "SELECT title, text, metadata FROM extracted_texts ORDER BY title").fetchall()
    assert len(rows) == 2
    import json
    meta = json.loads(rows[0]["metadata"])
    assert meta["channel"] == "email"
    assert meta["mode"] in ("email-full", "email-teaser")
    assert meta["dkim"]["result"] == "pass"
    assert meta["dkim"]["key_record"] == "v=DKIM1; k=rsa; p=TESTKEY"  # key archived
    assert meta["url"].startswith("https://www.justice.gov/")

    # the raw message is the capture, content-addressed and hashed
    cap = conn.execute("SELECT * FROM captures").fetchone()
    assert cap["change_kind"] == "new"
    assert cap["content_type"] == "message/rfc822"
    assert email_sources.provenance.verify_stored(cap["content_sha256"])


def test_unregistered_sender_body_is_never_fetched(conn):
    box = FakeMailbox([PERSONAL, MULTI])
    email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    assert box.bodies_fetched == [2]  # only the registered bulletin
    assert conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0] == 2
    stored = " ".join(r[0] for r in conn.execute("SELECT text FROM extracted_texts"))
    assert "Private content" not in stored


def test_second_poll_is_idempotent(conn):
    box = FakeMailbox([MULTI])
    email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    again = email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    assert again == []  # UID watermark: nothing new to look at
    assert conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0] == 2


def test_uid_validity_reset_forces_rescan(conn):
    box = FakeMailbox([MULTI])
    email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    box._uid_validity = 99  # server reissued UIDs
    email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    # rescanned, but item identity dedupes — no duplicate packages
    assert conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0] == 2


def test_item_already_ingested_via_another_channel_is_skipped(conn):
    """First-recorded wins across channels; the duplicate is counted."""
    import json
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES ('PR-justice-newsroom-web',"
        " 'AGENCYPR', '2026-07-29', 'x', 'x', 'fetched')")
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES ('PR-justice-newsroom-web', '', 'AGENCYPR', 'PRESS', 'Glen Allen',"
        " 'DOJ', ?, 'body', 4, 'x', 1)",
        (json.dumps({"url": "https://www.justice.gov/usao-edva/pr/glen-allen"}),))
    conn.commit()
    box = FakeMailbox([MULTI])
    results = email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    assert results[0]["items"] == 1 and results[0]["duplicates"] == 1


def test_bad_message_does_not_stop_the_poll(conn):
    box = FakeMailbox([b"From: usattorneys@public.govdelivery.com\n\nnot a bulletin",
                       MULTI])

    def exploding(raw):
        if b"not a bulletin" in raw:
            raise ValueError("boom")
        return no_dkim(raw)

    results = email_sources.poll_mailbox(box, conn, [entry()],
                                         dkim_verifier=exploding)
    assert results[0]["errors"] == 1
    assert results[0]["items"] == 2  # the good bulletin still ingested


def test_dkim_missing_signature_records_none():
    out = email_sources.verify_dkim(b"From: a@b.gov\nSubject: x\n\nbody")
    assert out["result"] == "none" and out["domain"] is None


def test_sender_map_accepts_string_or_list():
    allow = email_sources._sender_map([
        entry(), entry(id="va-email", sender=["a@va.gov", "B@VA.GOV"])])
    assert allow["a@va.gov"]["id"] == "va-email"
    assert allow["b@va.gov"]["id"] == "va-email"  # case-normalized


def test_subscription_administrivia_is_not_a_publication(conn):
    """Welcome and confirmation mail is platform plumbing, not an official
    action: counted and disclosed, never ingested as an item."""
    admin = MULTI.replace(b"Subject: U.S. Attorneys News News Update",
                          b"Subject: Welcome New User")
    box = FakeMailbox([admin])
    results = email_sources.poll_mailbox(box, conn, [entry()], dkim_verifier=no_dkim)
    assert results[0]["administrative"] == 1
    assert results[0]["items"] == 0
    assert conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0] == 0


@pytest.mark.parametrize("subject", [
    "Welcome New User", "Subscription Change Confirmation",
    "Welcome and thank you for subscribing", "(Please confirm your email) Welcome",
    "Your email subscriptions have changed", "New User Confirmation",
])
def test_administrative_subjects_detected(subject):
    msg = email.message_from_bytes(
        f"Subject: {subject}\n\nbody".encode(), policy=email.policy.default)
    assert email_sources.is_administrative(msg)


def test_real_bulletin_subjects_not_flagged_administrative():
    for subject in ("OIG Audit Assesses the USPS Vetting Process",
                    "FSIS Issues Public Health Alert for Steak Burrito Products",
                    "U.S. Attorneys News News Update",
                    "Daily Treasury Yield Curve Rates"):
        msg = email.message_from_bytes(
            f"Subject: {subject}\n\nbody".encode(), policy=email.policy.default)
        assert not email_sources.is_administrative(msg), subject


# ------------------------------------------- digest vs single-release shape --

ARTICLE = b"""From: USDA <usda@public.govdelivery.com>
To: mailbox@example.org
Subject: Secretary Launches Initiative to Recruit Veterans
Date: Wed, 29 Jul 2026 21:06:26 +0000
Message-ID: <bulletin-3@public.govdelivery.com>
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="B"

--B
Content-Type: text/plain; charset="utf-8"

Secretary Launches Initiative to Recruit Veterans

The Department announced a partnership today. The military spouse unemployment rate [ https://download.militaryonesource.mil/12038/report.pdf ] remains a concern, officials said.

Contact us [ https://ask.usda.gov/s/contactsupport ] www.usda.gov/veterans [ https://www.usda.gov/veterans ]

--B
Content-Type: text/html; charset="utf-8"

<html><body>
<p>The Department announced a partnership today. The military spouse
<a href="https://download.militaryonesource.mil/12038/report.pdf">unemployment rate</a> remains a concern.</p>
<a href="https://ask.usda.gov/s/contactsupport">Contact us</a>
<a href="https://www.usda.gov/veterans">www.usda.gov/veterans</a>
</body></html>
--B--
"""


def test_article_bulletin_is_one_item_not_one_per_inline_link():
    """A single release whose body cites other pages must not fabricate an
    item per citation (defect found in the first live run, 2026-07-29)."""
    msg = email.message_from_bytes(ARTICLE, policy=email.policy.default)
    items = email_sources.parse_bulletin(msg)
    assert len(items) == 1
    assert items[0]["title"] == "Secretary Launches Initiative to Recruit Veterans"
    assert "partnership today" in items[0]["summary"]
    titles = [i["title"] for i in items]
    assert "unemployment rate" not in titles and "Contact us" not in titles


def test_generic_link_titles_never_become_items():
    msg = email.message_from_bytes(ARTICLE, policy=email.policy.default)
    items = email_sources.parse_bulletin(msg)
    # the citation link is not the citation URL of record either
    assert items[0]["url"] != "https://ask.usda.gov/s/contactsupport"


def test_digest_still_splits_when_date_markers_present():
    msg = email.message_from_bytes(MULTI, policy=email.policy.default)
    assert len(email_sources.parse_bulletin(msg)) == 2

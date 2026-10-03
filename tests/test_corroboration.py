"""Cross-time cross-source corroboration (GUIDE §3, 2026-10-02).

Covers the matcher (title key + the two-number body check), the
direction/backfill guard, the 30-day window edge, the secondary-check
reject, write-once idempotence, the render-read helpers, and the
manifest selection.
"""

import json

import pytest
from conftest import install_digest_day_default

from fapd import corroboration, db

# A plausible presidential-action body. The Federal Register copy wraps
# the same text in compilation boilerplate (the EO number in the title,
# a filing/billing code, a document number) — a genuine duplicate whose
# bodies differ in length, which is exactly why the overlap coefficient,
# not symmetric Jaccard alone, carries the confirmation.
BODY = (
    "the president of the united states orders that each executive agency "
    "shall review its existing regulations and submit a written report to "
    "the office of management and budget within ninety days describing "
    "measures to reduce administrative burden and improve service to the "
    "american people consistent with applicable law and the availability of "
    "appropriations as directed in this order"
)
PRESACT_TEXT = BODY
FR_TEXT = (
    "executive order 14321 " + BODY + " billing code 3095 01 filed with the "
    "federal register document number 2026 12345 signed at the white house"
)
# A completely unrelated body: shares no three-word run with BODY, so a
# title-key collision between two different documents is rejected.
UNRELATED_TEXT = (
    "annual proclamation recognizing national maritime history month "
    "honoring sailors shipbuilders and coastal communities across every "
    "generation of seafaring tradition and commerce throughout the republic"
)

PA_TITLE = "Inaugurating the Era of Super Intelligence"
# The FR prepends the assigned EO number; _title_key must collapse the two.
FR_TITLE = "Executive Order 14321—Inaugurating the Era of Super Intelligence"


@pytest.fixture
def conn(tmp_path):
    c = install_digest_day_default(db.connect(tmp_path / "fapd.db"))
    yield c
    c.close()


def _add(conn, package_id, collection, doc_type, title, text, digest_day,
         *, granule_id="", url=None):
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued,"
        " last_modified, first_seen_at, fetch_status, digest_day)"
        " VALUES (?, ?, ?, ?, ?, 'fetched', ?)",
        (package_id, collection, digest_day, digest_day + "T12:00:00Z",
         digest_day + "T12:00:00Z", digest_day),
    )
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, title, metadata, text, char_count, extracted_at,"
        " extractor_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
        (package_id, granule_id, collection, doc_type, title,
         json.dumps({"url": url} if url else {}), text, len(text),
         digest_day + "T13:00:00Z"),
    )
    conn.commit()


def _presact(conn, digest_day, *, title=PA_TITLE, text=PRESACT_TEXT,
             package_id=None, url="https://www.whitehouse.gov/eo/super-intel"):
    _add(conn, package_id or f"PRESACT-{digest_day}", "PRESACT", "EO",
         title, text, digest_day, url=url)


def _fr_presdocu(conn, digest_day, *, title=FR_TITLE, text=FR_TEXT,
                 package_id="FR-2026-10-02", granule_id="2026-21000"):
    _add(conn, package_id, "FR", "PRESDOCU", title, text, digest_day,
         granule_id=granule_id, url="https://www.federalregister.gov/d/2026-12345")


# --- the matcher -----------------------------------------------------------


def test_title_key_strips_eo_number_and_punctuation():
    assert corroboration._title_key(FR_TITLE) == corroboration._title_key(PA_TITLE)
    assert corroboration._title_key("  Labor Day, 2026! ") == "labor day 2026"
    assert corroboration._title_key(None) == ""


def test_same_document_confirms_a_genuine_duplicate():
    ok, jaccard = corroboration._same_document(FR_TEXT, PRESACT_TEXT)
    assert ok
    assert jaccard >= corroboration.JACCARD_MIN


def test_same_document_rejects_unrelated_bodies():
    ok, _ = corroboration._same_document(FR_TEXT, UNRELATED_TEXT)
    assert not ok


def test_same_document_handles_empty_text():
    assert corroboration._same_document("", PRESACT_TEXT) == (False, 0.0)


# --- detection -------------------------------------------------------------


def test_records_fr_to_presact_link(conn):
    _presact(conn, "2026-09-29")
    _fr_presdocu(conn, "2026-10-02")
    created = corroboration.record_cross_source(conn, "2026-10-02")
    assert len(created) == 1
    link = created[0]
    assert link["package_id"] == "FR-2026-10-02"
    assert link["prior_package_id"] == "PRESACT-2026-09-29"
    assert link["prior_collection"] == "PRESACT"
    assert link["prior_source"] == "the White House"
    assert link["prior_date"] == "2026-09-29"
    assert link["prior_url"] == "https://www.whitehouse.gov/eo/super-intel"
    assert link["similarity"] >= corroboration.JACCARD_MIN
    # Stored, keyed later->prior.
    row = conn.execute(
        "SELECT prior_package_id FROM corroborations WHERE package_id = ?",
        ("FR-2026-10-02",),
    ).fetchone()
    assert row["prior_package_id"] == "PRESACT-2026-09-29"


def test_direction_is_fr_later_only_backfill_safe(conn):
    """The 2026-08-06 activation shape: a PRESACT observed AFTER the FR
    copy. PRESACT is never the later side of this rule, so finalizing the
    PRESACT day records nothing — no spurious back-link."""
    _fr_presdocu(conn, "2026-07-20")
    _presact(conn, "2026-08-06")  # observed late (welcome-batch backfill)
    assert corroboration.record_cross_source(conn, "2026-08-06") == []
    assert conn.execute("SELECT COUNT(*) FROM corroborations").fetchone()[0] == 0


def test_window_edge(conn):
    _fr_presdocu(conn, "2026-10-02")
    # 31 days earlier — just outside the 30-day window.
    _presact(conn, "2026-09-01", package_id="PRESACT-old")
    assert corroboration.record_cross_source(conn, "2026-10-02") == []
    # 29 days earlier — inside the window.
    _presact(conn, "2026-09-03", package_id="PRESACT-in")
    created = corroboration.record_cross_source(conn, "2026-10-02")
    assert len(created) == 1
    assert created[0]["prior_package_id"] == "PRESACT-in"


def test_secondary_check_rejects_title_collision(conn):
    """Same title key, genuinely different document body -> no link,
    even though the normalized titles match (operator decision 4)."""
    _presact(conn, "2026-09-29", text=UNRELATED_TEXT)
    _fr_presdocu(conn, "2026-10-02")
    assert corroboration.record_cross_source(conn, "2026-10-02") == []


def test_write_once_idempotent(conn):
    _presact(conn, "2026-09-29")
    _fr_presdocu(conn, "2026-10-02")
    assert len(corroboration.record_cross_source(conn, "2026-10-02")) == 1
    # A re-finalize of the same day records nothing new.
    assert corroboration.record_cross_source(conn, "2026-10-02") == []
    assert conn.execute("SELECT COUNT(*) FROM corroborations").fetchone()[0] == 1


def test_no_candidates_returns_empty(conn):
    _fr_presdocu(conn, "2026-10-02")  # no prior PRESACT at all
    assert corroboration.record_cross_source(conn, "2026-10-02") == []


# --- render-read + manifest helpers ---------------------------------------


def test_prior_links_and_attach(conn):
    _presact(conn, "2026-09-29")
    _fr_presdocu(conn, "2026-10-02")
    corroboration.record_cross_source(conn, "2026-10-02")
    links = corroboration.prior_links(conn, [("FR-2026-10-02", "2026-21000")])
    assert ("FR-2026-10-02", "2026-21000") in links
    assert links[("FR-2026-10-02", "2026-21000")][0]["prior_source"] == "the White House"

    items = [{"package_id": "FR-2026-10-02", "granule_id": "2026-21000"},
             {"package_id": "OTHER", "granule_id": ""}]
    corroboration.attach_prior_links(conn, items)
    assert "_prior_publication" in items[0]
    assert "_prior_publication" not in items[1]


def test_links_for_manifest_filters_by_utc_day(conn):
    _presact(conn, "2026-09-29")
    _fr_presdocu(conn, "2026-10-02")
    created = corroboration.record_cross_source(
        conn, "2026-10-02", now="2026-10-02T04:30:00Z")
    assert created
    assert len(corroboration.links_for_manifest(conn, "2026-10-02")) == 1
    assert corroboration.links_for_manifest(conn, "2026-10-01") == []

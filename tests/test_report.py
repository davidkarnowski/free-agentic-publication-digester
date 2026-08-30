"""REPORT stage tests: full render against a seeded temporary database.

No LLM calls, no network, no touching data/ — config.PROJECT_ROOT and
config.DIGEST_DIR are monkeypatched to a tmp directory and the graphic
assets are tiny real TIFFs generated with Pillow.
"""

import json
import re

import pytest
from conftest import install_digest_day_default
from PIL import Image

from fapd import config, db, inference, report

DATE = "2026-07-23"
CREC_PKG = "CREC-2026-07-23"
FR_PKG = "FR-2026-07-23"
SENATE_GID = "CREC-2026-07-23-pt1-PgS4101"
VOTE_GID = "CREC-2026-07-23-pt1-PgH6220"


def add_package(conn, package_id, collection, status="fetched", date=DATE):
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES (?, ?, ?, ?, ?, ?)",
        (package_id, collection, date, "2026-07-23T12:00:00Z", "2026-07-23T12:00:00Z", status),
    )


def add_text(conn, package_id, granule_id, collection, doc_type, *, title=None,
             agency=None, metadata=None, chars=1000, text="Body line one.\nMore text."):
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
        (package_id, granule_id, collection, doc_type, title, agency,
         json.dumps(metadata or {}), text, chars, "2026-07-23T13:00:00Z"),
    )


def add_summary(conn, package_id, granule_id, rule, text, method="llm"):
    conn.execute(
        "INSERT INTO summaries (package_id, granule_id, prompt_version, method, model,"
        " inclusion_rule, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (package_id, granule_id, config.PROMPT_VERSION, method,
         "haiku" if method == "llm" else None, rule, text, "2026-07-23T14:00:00Z"),
    )


def add_graphic(conn, package_id, gid, page, asset_path, status="extracted",
                classification="substantive"):
    conn.execute(
        "INSERT INTO graphic_assets (package_id, granule_id, gid, classification,"
        " page, asset_path, status) VALUES (?, '', ?, ?, ?, ?, ?)",
        (package_id, gid, classification, page, asset_path, status),
    )


def seed(conn, project_root):
    # --- CREC: 5 granules; 1 floor item, 1 recorded vote, 1 below-threshold
    # floor granule (CREC-EX-01), extensions + daily digest (CREC-EX-02).
    add_package(conn, CREC_PKG, "CREC")
    conn.execute(
        "INSERT INTO granules (package_id, granule_id, granule_class, title, first_seen_at)"
        " VALUES (?, ?, 'SENATE', ?, '2026-07-23T12:00:00Z')",
        (CREC_PKG, SENATE_GID, "Consideration of S. 9999, Interstate Bridge Inspection Act"),
    )
    add_text(conn, CREC_PKG, SENATE_GID, "CREC", "SENATE", chars=20000)
    add_summary(conn, CREC_PKG, SENATE_GID, "CREC-SEL-01",
                "The Senate resumed consideration of S. 9999; two amendments were offered.")
    add_text(conn, CREC_PKG, VOTE_GID, "CREC", "HOUSE", chars=8000,
             text="ROLL CALL 512 ON PASSAGE OF H.R. 8888\nThe vote details follow.")
    add_summary(conn, CREC_PKG, VOTE_GID, "CREC-SEL-02",
                "House Roll Call 512 on passage of H.R. 8888: passed 301-120.")
    add_text(conn, CREC_PKG, "CREC-2026-07-23-pt1-PgH6100", "CREC", "HOUSE", chars=5000)
    add_text(conn, CREC_PKG, "CREC-2026-07-23-pt1-PgE800", "CREC", "EXTENSIONS", chars=3000)
    add_text(conn, CREC_PKG, "CREC-2026-07-23-pt1-PgD900", "CREC", "DAILYDIGEST", chars=4000)

    # --- BILLS: one selected (enrolled, official summary), one counted only.
    add_package(conn, "BILLS-119hr8888enr", "BILLS")
    add_text(conn, "BILLS-119hr8888enr", "", "BILLS", "enr",
             title="Rural Broadband Mapping Act",
             metadata={"legis_num": "H. R. 8888", "bill_version": "enr"}, chars=30000)
    add_summary(conn, "BILLS-119hr8888enr", "", "BILLS-SEL-01",
                "Directs the Federal Communications Commission to update broadband maps.",
                method="official")
    add_package(conn, "BILLS-119hr1ih", "BILLS")
    add_text(conn, "BILLS-119hr1ih", "", "BILLS", "ih", title="A bill", chars=2000)

    # --- FR: 2 rules, 1 proposed rule, 2 notices (FR-EX-01), 1 presidential.
    add_package(conn, FR_PKG, "FR")
    add_text(conn, FR_PKG, "2026-11111", "FR", "RULE",
             title="Energy Conservation Standards", agency="Department of Energy",
             metadata={"cfr": "10 CFR Part 430", "action": "Final rule",
                       "dates": "Effective 2026-09-01",
                       "pages": {"first": "100", "last": "102"}}, chars=12000)
    add_summary(conn, FR_PKG, "2026-11111", "FR-SEL-01",
                "A final rule amending conservation standards for consumer appliances.",
                method="official")
    add_text(conn, FR_PKG, "2026-22222", "FR", "RULE", title="Test Procedure Update",
             chars=9000)
    add_summary(conn, FR_PKG, "2026-22222", "FR-SEL-01",
                "A final rule updating test procedures for certain equipment.")
    add_text(conn, FR_PKG, "2026-33333", "FR", "PRORULE", title="Crop Insurance Amendments",
             agency="Department of Agriculture",
             metadata={"dates": "Comments due 2026-10-01"}, chars=7000)
    add_summary(conn, FR_PKG, "2026-33333", "FR-SEL-02",
                "A proposed rule revising crop insurance program provisions.")
    add_text(conn, FR_PKG, "2026-44444", "FR", "NOTICE", title="Meeting Notice", chars=1000)
    add_text(conn, FR_PKG, "2026-55555", "FR", "NOTICE", title="Information Collection",
             chars=1200)
    add_text(conn, FR_PKG, "2026-66666", "FR", "PRESDOCU",
             title="Proclamation on National Parks Month", chars=2500)
    add_summary(conn, FR_PKG, "2026-66666", "FR-SEL-03",
                "A proclamation designating National Parks Month.", method="official")

    # --- USCOURTS: 2 appellate opinions (summarized, with plain lines),
    # 1 district (USCOURTS-EX-01) and 1 bankruptcy (USCOURTS-EX-02) counted
    # only, plus a package outside the archive window (USCOURTS-FETCH-01,
    # fetch_status='skipped', earlier date_issued).
    add_package(conn, "USCOURTS-ca1-26-00042", "USCOURTS")
    add_text(conn, "USCOURTS-ca1-26-00042", "USCOURTS-ca1-26-00042-0",
             "USCOURTS", "APPELLATE", title="Doe v. Example Agency",
             metadata={"court_code": "ca1",
                       "court_name": "United States Court of Appeals"
                                     " for the First Circuit",
                       "case_number": "26-00042", "date_filed": DATE},
             chars=18000)
    add_summary(conn, "USCOURTS-ca1-26-00042", "USCOURTS-ca1-26-00042-0",
                "USCOURTS-SEL-01",
                "The court affirmed the district court's grant of summary judgment.")
    seed_plain(conn, "USCOURTS-ca1-26-00042", "USCOURTS-ca1-26-00042-0",
               "The appeals court agreed with the lower court's decision.")
    add_package(conn, "USCOURTS-ca9-26-01234", "USCOURTS")
    add_text(conn, "USCOURTS-ca9-26-01234", "USCOURTS-ca9-26-01234-0",
             "USCOURTS", "APPELLATE", title="Roe v. Sample Board",
             metadata={"court_code": "ca9",
                       "court_name": "United States Court of Appeals"
                                     " for the Ninth Circuit",
                       "case_number": "26-01234", "date_filed": DATE},
             chars=22000)
    add_summary(conn, "USCOURTS-ca9-26-01234", "USCOURTS-ca9-26-01234-0",
                "USCOURTS-SEL-01",
                "The court reversed and remanded for further proceedings.")
    seed_plain(conn, "USCOURTS-ca9-26-01234", "USCOURTS-ca9-26-01234-0",
               "The appeals court sent the case back to the lower court.")
    add_package(conn, "USCOURTS-txnd-26-00777", "USCOURTS")
    add_text(conn, "USCOURTS-txnd-26-00777", "USCOURTS-txnd-26-00777-0",
             "USCOURTS", "DISTRICT", title="Smith v. Jones",
             metadata={"court_code": "txnd",
                       "court_name": "United States District Court for the"
                                     " Northern District of Texas",
                       "case_number": "26-00777", "date_filed": DATE},
             chars=6000)
    add_package(conn, "USCOURTS-nysb-26-00888", "USCOURTS")
    add_text(conn, "USCOURTS-nysb-26-00888", "USCOURTS-nysb-26-00888-0",
             "USCOURTS", "BANKRUPTCY", title="In re Example Corp.",
             metadata={"court_code": "nysb",
                       "court_name": "United States Bankruptcy Court for the"
                                     " Southern District of New York",
                       "case_number": "26-00888", "date_filed": DATE},
             chars=4000)
    add_package(conn, "USCOURTS-ca9-19-99999", "USCOURTS", status="skipped",
                date="2019-01-15")

    # --- Graphics: 3 substantive extracted TIFFs on the rule's pages, 1
    # boilerplate signature (skipped by FR-GPH-01).
    assets_dir = project_root / "data" / "assets" / "FR" / DATE / FR_PKG
    assets_dir.mkdir(parents=True)
    for gid, page in (("EN23JY26.001", "100"), ("EN23JY26.002", "101"),
                      ("EN23JY26.003", "102")):
        path = assets_dir / f"{gid}.tif"
        Image.new("1", (4, 4), 1).save(path)
        add_graphic(conn, FR_PKG, gid, page, str(path.relative_to(project_root)))
    add_graphic(conn, FR_PKG, "Trump.EPS", "103", None, status="skipped",
                classification="boilerplate")

    for collection in ("CREC", "BILLS", "FR", "USCOURTS"):
        conn.execute(
            "INSERT INTO sync_state (collection, last_modified_watermark,"
            " last_sync_completed_at, last_sync_package_count) VALUES (?, ?, ?, 3)",
            (collection, "2026-07-23T18:00:00Z", "2026-07-23T18:05:00Z"),
        )
    conn.commit()


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(config, "DIGEST_DIR", tmp_path / "digests")
    return tmp_path


@pytest.fixture
def conn(project):
    connection = install_digest_day_default(
        db.connect(project / "data" / "fapd.db"))
    seed(connection, project)
    yield connection
    connection.close()


@pytest.fixture
def digest(conn):
    path = report.render(conn, DATE)
    return path, path.read_text(encoding="utf-8")


def test_render_structure(digest):
    path, md = digest
    assert path == config.DIGEST_DIR / f"{DATE}.md"
    for heading in (
        f"# Daily Digest — {DATE}",
        "## 1. Congressional Floor Activity",
        "### 1.1 Senate",
        "### 1.2 House of Representatives",
        "### 1.3 Recorded Votes",
        "## 2. Legislation",
        "### 2.1 Counts by Stage",
        "### 2.2 Bills Listed by Mechanical Rule",
        "## 3. Federal Register",
        "### 3.1 Counts by Document Type",
        "### 3.2 Rules Published",
        "### 3.3 Proposed Rules Published",
        "### 3.4 Notices and Presidential Documents",
        "## 4. Enacted Laws",
        "## 5. Judicial Activity",
        "### 5.1 Appellate and National Court Opinions",
        "### 5.2 Counts by Court Category",
        "## 6. Agency Announcements",
        "## 7. Recorded Votes",
        "## 8. Bill Actions",
        "## Coverage Statement",
        "## Methodology",
    ):
        assert heading in md
    # Header metadata and watermarks.
    assert f"| **Digest date** | {DATE} |" in md
    assert "CREC: 2026-07-23T18:00:00Z" in md
    # An empty subsection renders its explicit none-line, never silence.
    assert "No House floor items met the selection thresholds" in md
    assert "No laws were published in this range." in md  # PLAW active, empty day
    # No template scaffolding leaks into real output.
    assert "EXAMPLE" not in md
    assert "<!--" not in md


def test_counts_tables(digest):
    _, md = digest
    assert "| Introduced (ih/is) | 1 |" in md
    assert "| Enrolled (enr) | 1 |" in md
    assert "| **Total bill texts published** | **2** |" in md
    assert "| Rules | 2 |" in md
    assert "| Proposed rules | 1 |" in md
    assert "| Notices | 2 |" in md
    assert "| Presidential documents | 1 |" in md
    assert "| **Total FR documents** | **6** |" in md


def test_citations_and_titles(digest):
    _, md = digest
    assert f"https://www.govinfo.gov/app/details/{CREC_PKG}/{SENATE_GID}" in md
    assert "[BILLS-119hr8888enr](https://www.govinfo.gov/app/details/BILLS-119hr8888enr)" in md
    assert f"https://www.govinfo.gov/app/details/{FR_PKG}/2026-11111" in md
    # Title from granules.title when present; from the first text line otherwise.
    assert "**Consideration of S. 9999, Interstate Bridge Inspection Act**" in md
    assert "**Roll Call 512 on Passage of H.R. 8888**" in md  # display-cased
    # FR item carries doc number, CFR citation, and preamble metadata.
    assert "(2026-11111; 10 CFR Part 430)" in md
    assert "Dates: Effective 2026-09-01." in md
    # Agencies alphabetical; unstated agency grouped last.
    assert "#### Department of Energy" in md
    assert "#### (agency not stated)" in md
    assert md.index("#### Department of Energy") < md.index("#### (agency not stated)")


def test_every_item_states_its_inclusion_rule(digest):
    _, md = digest
    items = md.count("\n- **")
    because = md.count("Included because:")
    # 1 floor + 1 vote + 1 bill + 2 rules + 1 prorule + 1 presdocu + 2 appellate
    assert items == because == 9
    # CREC-SEL-01 carries its mechanical evidence (the actual char count).
    assert "CREC-SEL-01 — floor item ≥ threshold floor time (20,000 characters)" in md
    assert "CREC-SEL-02 — recorded vote (all recorded votes are listed)" in md
    assert "BILLS-SEL-01 — reached stage: reported/enrolled/calendar" in md
    assert "FR-SEL-01 — document type: final rule (all listed)" in md
    assert "USCOURTS-SEL-01 — appellate court opinion (all listed)" in md


def test_graphics_embedded_with_disclosure(digest):
    path, md = digest
    assets = path.parent / "assets" / DATE
    for gid in ("EN23JY26.001", "EN23JY26.002"):
        png = assets / f"{gid}.png"
        assert png.is_file()
        with Image.open(png) as img:
            assert img.format == "PNG"
            assert img.mode != "1"  # 1-bit sources are converted before saving
    assert not (assets / "EN23JY26.003.png").exists()  # beyond the 2-per-item cap
    assert (
        f"![Graphic from 2026-11111 (printed page 100)](assets/{DATE}/EN23JY26.001.png)"
        in md
    )
    assert "*Source graphic 1 of 3 from 2026-11111.*" in md
    assert (
        "*Graphics not rendered here: 1 of 3 — see the [source PDF]"
        f"(https://www.govinfo.gov/content/pkg/{FR_PKG}/pdf/{FR_PKG}.pdf).*"
    ) in md


def test_coverage_statement_reconciles(digest):
    _, md = digest
    assert "| CREC | 1 | 5 | 2 | 2 | 1 |" in md
    assert "| BILLS | 2 | — | 1 | 1 | 0 |" in md
    assert "| FR | 1 | 6 | 4 | 2 | 0 |" in md
    # 4 packages for the date (the skipped one is 2019); 4 opinions =
    # 2 summarized appellate + 2 counted (district + bankruptcy).
    assert "| USCOURTS | 4 | 4 | 2 | 2 | 0 |" in md
    assert "CREC-EX-01: floor granule below floor-time threshold — 1 item(s)" in md
    assert "CREC-EX-02: extensions/daily-digest sections (counted) — 2 item(s)" in md
    assert "FR-EX-01: notices counted, not individually summarized — 2 item(s)" in md
    assert ("USCOURTS-EX-01: district court opinions counted, not individually"
            " summarized — 1 item(s)") in md
    assert ("USCOURTS-EX-02: bankruptcy court opinions counted, not individually"
            " summarized — 1 item(s)") in md
    assert "4 graphic(s) flagged" in md
    assert "3 content graphic(s)" in md
    assert "1 boilerplate" in md
    assert "0 were analyzed via vision pass (vision pass not yet implemented)" in md
    assert "2 embedded above" in md
    # The judicial publication-lag line is a STANDING known-gaps entry
    # whenever USCOURTS data is present.
    assert ("**Known gaps:** courts post opinions with delay; opinions filed on"
            " this date may appear in later syncs." in md)


def test_judicial_section_disclosure_and_items(digest):
    _, md = digest
    # Section 5 sits between Enacted Laws and the Coverage Statement, and
    # carries the MANDATORY standing completeness disclosure (GUIDE §3).
    assert (md.index("## 4. Enacted Laws")
            < md.index("## 5. Judicial Activity")
            < md.index("## Coverage Statement"))
    assert "approximately 140 participating" in md
    assert "USCOURTS is participation-based and is NOT the complete federal judicial" in md
    # Opinions grouped by court, courts alphabetical.
    first = md.index("#### United States Court of Appeals for the First Circuit")
    ninth = md.index("#### United States Court of Appeals for the Ninth Circuit")
    assert first < ninth
    assert ("**Doe v. Example Agency** (No. 26-00042; filed 2026-07-23) — The"
            " court affirmed the district court's grant of summary judgment.") in md
    assert "*In plain terms:* The appeals court agreed with the lower court's decision." in md
    # Citations resolve to package/granule details URLs like every other item.
    assert ("https://www.govinfo.gov/app/details/USCOURTS-ca1-26-00042/"
            "USCOURTS-ca1-26-00042-0") in md
    assert ("https://www.govinfo.gov/app/details/USCOURTS-ca9-26-01234/"
            "USCOURTS-ca9-26-01234-0") in md


def test_judicial_counts_table_and_skipped_disclosure(digest):
    _, md = digest
    assert "| Appellate | 2 |" in md
    assert "| District | 1 |" in md
    assert "| Bankruptcy | 1 |" in md
    assert "| National | 0 |" in md
    assert "| **Total opinions extracted** | **4** |" in md
    # USCOURTS-FETCH-01: the skipped package is disclosed as a global
    # running count, not a per-date figure.
    assert "Archive-window disclosure (rule USCOURTS-FETCH-01): 1 USCOURTS" in md
    assert "global running count across all syncs" in md


def test_judicial_if_none_line_and_coverage(conn, tmp_path):
    conn.execute("DELETE FROM summaries WHERE package_id LIKE 'USCOURTS%'")
    conn.execute("DELETE FROM plain_summaries WHERE package_id LIKE 'USCOURTS%'")
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text(encoding="utf-8")
    # Since GUIDE §6 r15 (2026-08-24) the selected-but-unsummarized
    # opinions are LISTED from the record, not hidden behind the
    # none-matched line — which is reserved for a day where no opinion
    # matched a rule at all.
    assert "No appellate or national court opinions matched a listing rule" not in md
    assert "- **Doe v. Example Agency** (No. 26-00042; filed 2026-07-23) — "\
           "*listed from the record*" in md
    assert "Items marked *listed from the record* are listed without a summary." in md
    # Coverage arithmetic is untouched: unsummarized appellate opinions
    # still land in the excluded remainder; district + bankruptcy stay
    # counted-only. 0 + 2 + 2 == 4 units.
    assert "| USCOURTS | 4 | 4 | 0 | 2 | 2 |" in md


def test_validator_rejects_unknown_citation(digest, conn):
    _, md = digest
    bad = md.replace("2026-11111", "2026-99999")
    assert bad != md
    with pytest.raises(report.ValidationError, match="citation"):
        report.validate(bad, conn, DATE)


def test_validator_rejects_nonreconciling_coverage(digest, conn):
    _, md = digest
    bad = md.replace("| CREC | 1 | 5 | 2 | 2 | 1 |", "| CREC | 1 | 5 | 3 | 2 | 1 |")
    assert bad != md
    with pytest.raises(report.ValidationError, match="coverage"):
        report.validate(bad, conn, DATE)


def test_banned_word_in_llm_summary_blocks_render(conn):
    conn.execute(
        "UPDATE summaries SET summary = 'A sweeping change to test procedures.'"
        " WHERE package_id = ? AND granule_id = '2026-22222'",
        (FR_PKG,),
    )
    conn.commit()
    with pytest.raises(report.ValidationError, match="sweeping"):
        report.render(conn, DATE)
    assert not (config.DIGEST_DIR / f"{DATE}.md").exists()  # nothing written


def test_banned_word_in_official_summary_is_masked(conn):
    # Verbatim official text is quoted source material, not generated prose:
    # the lexicon scan must mask it, not reject it.
    conn.execute(
        "UPDATE summaries SET summary = 'A landmark provision, per the agency abstract.'"
        " WHERE package_id = ? AND granule_id = '2026-11111'",
        (FR_PKG,),
    )
    conn.commit()
    path = report.render(conn, DATE)
    assert "landmark provision" in path.read_text(encoding="utf-8")


# ------------------------------- find_lexicon_violation (GUIDE §6 r14a) --


def test_find_lexicon_violation_identifies_map_summary(conn):
    conn.execute(
        "UPDATE summaries SET summary = 'A sweeping change to test procedures.'"
        " WHERE package_id = ? AND granule_id = '2026-22222'",
        (FR_PKG,),
    )
    conn.commit()
    assert report.find_lexicon_violation(conn, DATE) == {
        "package_id": FR_PKG, "granule_id": "2026-22222",
        "layer": "map", "term": "sweeping",
    }


def test_find_lexicon_violation_identifies_plain_line(conn):
    # The map summary itself is clean; only the plain restatement fails.
    seed_plain(conn, FR_PKG, "2026-22222", "A controversial update to test procedures.")
    assert report.find_lexicon_violation(conn, DATE) == {
        "package_id": FR_PKG, "granule_id": "2026-22222",
        "layer": "plain", "term": "controversial",
    }


def test_find_lexicon_violation_returns_none_for_compose_prose(conn):
    """Compose-level prose (Day in Review) has no package/granule identity
    to correct against — rule 14a scopes it out on purpose; every seeded
    item summary/plain is clean, so the only violation on the day lives
    where find_lexicon_violation deliberately never looks."""
    conn.execute(
        "INSERT INTO day_summaries (date, prompt_version, model, summary, created_at)"
        " VALUES (?, ?, 'haiku', 'A sweeping day in review.', 'x')",
        (DATE, config.PROMPT_VERSION),
    )
    conn.commit()
    assert report.find_lexicon_violation(conn, DATE) is None


def test_find_lexicon_violation_exempts_official_title_quote(conn):
    """The same positional exemption _validate_lexicon applies at whole-
    markdown scan time must hold at the per-item scan too, or a
    legitimate title quote would be misdiagnosed as a correctable
    violation."""
    add_package(conn, "USCOURTS-ca5-26-05555", "USCOURTS")
    add_text(conn, "USCOURTS-ca5-26-05555", "USCOURTS-ca5-26-05555-0",
             "USCOURTS", "APPELLATE", title="Landmark Legal Foundation v. EPA",
             metadata={"court_code": "ca5",
                       "court_name": "United States Court of Appeals"
                                     " for the Fifth Circuit",
                       "case_number": "26-05555", "date_filed": DATE},
             chars=9000)
    add_summary(conn, "USCOURTS-ca5-26-05555", "USCOURTS-ca5-26-05555-0",
                "USCOURTS-SEL-01",
                "The court ruled in Landmark Legal Foundation v. EPA,"
                " affirming the lower court.")
    assert report.find_lexicon_violation(conn, DATE) is None


# ------------------------- phrase-scoped exemption (GUIDE §2, 2026-08-30) --
# 2026-08-28/29: two bills renaming sites whose official titles contain
# "historic" as a proper-noun component were withdrawn because the map
# summary named the same place in wording that was not a byte-identical
# copy of the WHOLE title. These pin the fix directly against
# report._official_spans (no DB, fast) plus the incidents replayed
# end-to-end through find_lexicon_violation below.


def test_official_spans_exempts_a_partial_quote_of_a_title():
    """The 2026-08-28 incident, replayed directly: the summary paraphrases
    the title's wrapper sentence but names the site in an exact,
    word-bounded quote of it — no longer required to recite the whole
    title to earn the exemption."""
    title = ('105 HR 1693 RH: To redesignate the National Historic Trails'
             ' Interpretive Center in Casper, Wyoming, as the "Barbara L.'
             ' Cubin National Historic Trails Interpretive Center".')
    summary = ("This bill designates the National Historic Trails"
               " Interpretive Center in Casper, Wyoming, in honor of"
               " Barbara L. Cubin.")
    matches = list(report._BANNED_RE.finditer(summary))
    assert len(matches) == 1
    spans = report._official_spans(summary, [title])
    assert any(a <= matches[0].start() and matches[0].end() <= b for a, b in spans)


def test_official_spans_exempts_the_2026_08_29_incident_shape():
    title = ('119 HR 8121 RH: To designate the Christiansted Bandstand at'
             ' the Christiansted National Historic Site, St. Croix,'
             ' Virgin Islands, as the "Peter G. Thurland, Sr., Bandstand".')
    summary = ("This bill names the bandstand at Christiansted National"
               " Historic Site after Peter G. Thurland, Sr.")
    spans = report._official_spans(summary, [title])
    match = next(report._BANNED_RE.finditer(summary))
    assert any(a <= match.start() and match.end() <= b for a, b in spans)


def test_official_spans_still_rejects_genuine_editorializing():
    """A title containing the word does not license OUR sentence to use
    it in unconnected, unquoted wording."""
    title = "An Act to designate the National Historic Trails Center."
    summary = "This is a truly historic moment for the committee."
    assert report._official_spans(summary, [title]) == []


def test_official_spans_rejects_a_bare_word_borrowed_from_another_item():
    """Cross-item abuse: item B's editorializing must not exempt itself
    just because SOME title that day happens to share the word,
    unconnected to it."""
    title_a = "An Act to designate the National Historic Trails Center."
    summary_b = "This historic legislation updates funding formulas."
    assert report._official_spans(summary_b, [title_a, "Some Other Bill"]) == []


def test_official_spans_requires_a_content_word_not_a_bare_stopword():
    """'a historic' recurs by chance in unrelated official text
    constantly (it is just an article plus the adjective) — the floor
    must be a CONTENT word, or this bigram alone would exempt almost
    anything. 'historic day', reused verbatim, is a real quotation and
    does exempt; 'historic moment', never quoted, does not."""
    source = "The floor proceedings included a historic day for the Senate."
    exempted = "Today was a historic day for the Senate."
    not_exempted = "It was truly a historic moment for the committee."
    assert report._official_spans(exempted, [source]) != []
    assert report._official_spans(not_exempted, [source]) == []


def test_official_spans_never_crosses_a_sentence_boundary():
    source = "Section one is historic. Section two addresses funding for roads."
    summary = "The report addresses funding for roads in a historic way."
    assert report._official_spans(summary, [source]) == []


def test_official_spans_full_string_case_still_works():
    """The pre-2026-08-30 shape — a complete quotation — must keep
    working; the change adds a narrower floor, it does not remove the
    wider one."""
    caption = "Landmark Legal Foundation v. EPA"
    summary = f"The court in {caption} ruled against the agency."
    assert report._official_spans(summary, [caption]) != []


def test_official_spans_multiword_banned_phrase_partial_quote():
    """A multi-word banned term ('in an attempt to') is a motive-
    attribution phrase, not a proper noun — the same rule still applies:
    the exempted span is scoped to the phrase itself, so a paraphrase of
    what comes AFTER it (an ordinary word, not a banned one) is
    irrelevant to whether the phrase itself was quoted."""
    source = "The agency acted in an attempt to resolve the dispute quickly."
    summary = ("The filing states the agency acted in an attempt to"
               " resolve the matter.")
    assert report._official_spans(summary, [source]) != []


def test_lexicon_officials_includes_extracted_document_body(conn):
    """The 2026-08-30 corpus broadening: a summary quoting a phrase from
    the document's own BODY — not its title, not an official abstract —
    now has an exemption path. Before this, the only official text a map
    summary could quote was a title or an FR abstract."""
    add_package(conn, "USCOURTS-ca9-26-77777", "USCOURTS")
    add_text(
        conn, "USCOURTS-ca9-26-77777", "USCOURTS-ca9-26-77777-0",
        "USCOURTS", "APPELLATE", title="United States v. Doe",
        metadata={"court_code": "ca9", "case_number": "26-77777",
                  "date_filed": DATE},
        chars=9000,
        text="The panel found the agency's action to be an unprecedented"
             " expansion of its own authority under the statute.",
    )
    add_summary(
        conn, "USCOURTS-ca9-26-77777", "USCOURTS-ca9-26-77777-0",
        "USCOURTS-SEL-01",
        "The panel described an unprecedented expansion of agency"
        " authority under the statute.",
    )
    assert report.find_lexicon_violation(conn, DATE) is None


def test_lexicon_officials_excludes_other_items_own_llm_summaries(conn):
    """Model output is never a source of exemption for model output — an
    item cannot borrow license from a DIFFERENT item's stored (LLM)
    summary, only from text the digest itself did not write."""
    add_package(conn, "USCOURTS-ca9-26-88888", "USCOURTS")
    add_text(
        conn, "USCOURTS-ca9-26-88888", "USCOURTS-ca9-26-88888-0",
        "USCOURTS", "APPELLATE", title="United States v. Roe",
        metadata={"court_code": "ca9", "case_number": "26-88888",
                  "date_filed": DATE},
        chars=9000,
    )
    add_summary(
        conn, "USCOURTS-ca9-26-88888", "USCOURTS-ca9-26-88888-0",
        "USCOURTS-SEL-01",
        "The panel called this a truly historic ruling for the circuit.",
    )
    violation = report.find_lexicon_violation(conn, DATE)
    assert violation is not None and violation["term"] == "historic"


def test_presact_item_renders_stored_summary_and_plain(conn, tmp_path):
    """Added 2026-08-09: PRESACT items are selected and LLM-summarized
    like any other collection (PRESACT-SEL-01..04 are ordinary
    rules.py matchers); this section now renders that stored summary
    and plain restatement the way FR/CREC already do. Previously the
    summary was generated and paid for on every run and never shown."""
    _add_presact(conn, "PA-summ-1", "Securing Rural Broadband Access", "EO",
                 "Thu, 23 Jul 2026 21:07:00 +0000")
    add_summary(conn, "PA-summ-1", "", "PRESACT-SEL-01",
                "The order directs agencies to expand rural broadband access.")
    seed_plain(conn, "PA-summ-1", "",
              "The order tells agencies to expand internet access in rural areas.")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "directs agencies to expand rural broadband access" in md
    assert ("*In plain terms:* The order tells agencies to expand internet"
            " access in rural areas.") in md


def test_empty_day_still_renders_mandatory_sections(project):
    connection = db.connect(project / "data" / "empty.db")
    try:
        path = report.render(connection, "2026-01-01")
        md = path.read_text(encoding="utf-8")
        assert "## Coverage Statement" in md
        assert "| CREC | 0 | 0 | 0 | 0 | 0 |" in md
        assert "| USCOURTS | 0 | 0 | 0 | 0 | 0 |" in md
        assert "No recorded votes were published" in md
        assert "No rules were published in this issue." in md
        assert "No bill texts published in this range matched a listing rule; all 0 are" in md
        # Section 5 and its standing disclosure render even on an empty day.
        assert "## 5. Judicial Activity" in md
        assert "NOT the complete federal judicial record" in " ".join(md.split())
        assert "No appellate or national court opinions matched a listing rule" in md
        # No USCOURTS data and no sync_state row: no publication-lag gap line.
        assert "**Known gaps:** none identified." in md
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# Plain-speak layer, title normalization, glossary
# ---------------------------------------------------------------------------


def seed_plain(conn, pid, gid, plain):
    conn.execute(
        "INSERT INTO plain_summaries (package_id, granule_id, plain_version,"
        " source_prompt_version, plain, created_at) VALUES (?, ?, ?, ?, ?, 'x')",
        (pid, gid, config.PLAIN_PROMPT_VERSION, config.PROMPT_VERSION, plain),
    )
    conn.commit()


def test_plain_line_rendered_when_present(conn, tmp_path):
    seed_plain(conn, FR_PKG, "2026-11111",
               "A one-sentence plain rendering of the rule.")
    path = report.render(conn, DATE, out_dir=tmp_path)
    text = path.read_text()
    assert "*In plain terms:* A one-sentence plain rendering of the rule." in text


def test_missing_plain_degrades_gracefully(conn, tmp_path):
    conn.execute("DELETE FROM plain_summaries")  # drop the seeded USCOURTS plain rows
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    assert "*In plain terms:*" not in path.read_text()  # omitted, never fabricated


def test_banned_term_in_plain_line_fails_validation(conn, tmp_path):
    seed_plain(conn, FR_PKG, "2026-11111",
               "A landmark change to the rules.")
    with pytest.raises(report.ValidationError):
        report.render(conn, DATE, out_dir=tmp_path)


def test_display_title_normalizes_all_caps():
    assert report._display_title(
        "DIRECTING THE REMOVAL OF UNITED STATES ARMED FORCES FROM HOSTILITIES"
    ) == "Directing the Removal of United States Armed Forces from Hostilities"
    # acronyms, digits, and dotted tokens survive
    assert report._display_title("NDAA FOR FY 2027 UNDER H.R. 5334") == (
        "NDAA for FY 2027 Under H.R. 5334"
    )
    # mixed-case titles pass through untouched
    assert report._display_title("Special Local Regulation; Lake Erie") == (
        "Special Local Regulation; Lake Erie"
    )


def test_glossary_lists_only_present_terms(conn, tmp_path):
    seed_plain(conn, FR_PKG, "2026-11111",
               "A rule that takes effect now; this interim final rule accepts comments.")
    path = report.render(conn, DATE, out_dir=tmp_path)
    text = path.read_text()
    assert "## Terms Used Today" in text
    assert "- *interim final rule* —" in text
    assert "cloture" not in text  # absent terms are not listed


def test_toc_and_section_blurbs(conn, tmp_path):
    conn.execute(
        "INSERT INTO section_summaries (date, section_key, prompt_version, model,"
        " synopsis, created_at) VALUES (?, 'rules', ?, 'haiku',"
        " 'Two final rules today, led by an export-control change.', 'x')",
        (DATE, config.SECTION_PROMPT_VERSION),
    )
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text()
    # ToC leads the digest and links to real anchors
    assert md.index("## Contents") < md.index("## Day in Review") if "## Day in Review" in md else True
    assert "- [4. Enacted Laws](#4-enacted-laws)" in md
    assert "- [Coverage Statement](#coverage-statement)" in md
    # Blurb sits under its section heading
    rules_pos = md.index("### 3.2 Rules Published")
    blurb_pos = md.index("*In plain terms: Two final rules today")
    assert 0 < blurb_pos - rules_pos < 120


def test_plaw_item_renders_in_section_4(conn, tmp_path):
    add_package(conn, "PLAW-119publ101", "PLAW")
    conn.execute("UPDATE packages SET date_issued = ? WHERE package_id = 'PLAW-119publ101'",
                 (DATE,))
    add_text(conn, "PLAW-119publ101", "", "PLAW", "PUBLIC",
             title="Public Law 119-101: Housing supply.",
             metadata={"citations": ["Public Law 119-101"], "approved_date": "2026-07-11"})
    add_summary(conn, "PLAW-119publ101", "", "PLAW-SEL-01",
                "Directs agencies to increase housing supply.", method="llm")
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text()
    assert "- **Public Law 119-101 — Public Law 119-101: Housing supply.**" in md
    assert "Approved: 2026-07-11." in md
    assert "PLAW-SEL-01 — enacted into law" in md


def test_agency_announcements_section(conn, tmp_path):
    now = "2026-07-23T15:00:00Z"
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES ('PR-gao-reports-abc12345',"
        " 'AGENCYPR', ?, ?, ?, 'fetched')", (DATE, now, now))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES ('PR-gao-reports-abc12345', '', 'AGENCYPR', 'PRESS',"
        " 'Audit of Example Program', 'Government Accountability Office',"
        " ?, 'body', 4, ?, 1)",
        (json.dumps({"source_id": "gao-reports", "url": "https://gao.gov/x",
                     "claimed_published_at": "2026-07-23T09:00:00",
                     "wayback_url": "https://web.archive.org/web/20260723/https://gao.gov/x"}),
         now))
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text()
    assert "## 6. Agency Announcements" in md
    assert "official advocacy, quoted and" in md
    assert "**[Audit of Example Program](https://gao.gov/x)**" in md
    assert "AGENCYPR-SEL-01" in md
    assert "[independent archive](https://web.archive.org/web/20260723/https://gao.gov/x)" in md
    assert "- [6. Agency Announcements](#6-agency-announcements)" in md  # ToC
    assert "| AGENCYPR |" in md  # coverage row


def add_vote(conn, package_id, *, number, claimed, title, result="Agreed to (50-47)",
             issue="S.Res. 817", question="On the Resolution", tally=None,
             wayback=None):
    now = "2026-07-23T15:00:00Z"
    url = ("https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/"
           f"vote_119_2_{number}.xml")
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES (?, 'VOTES', ?, ?, ?, 'fetched')",
        (package_id, DATE, now, now))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, '', 'VOTES', 'ROLLCALL', ?, 'Senate.gov XML services',"
        " ?, 'body', 4, ?, 1)",
        (package_id, title,
         json.dumps({"source_id": "senate-xml", "url": url,
                     "claimed_published_at": claimed, "mode": "full",
                     "wayback_url": wayback,
                     "details": {"chamber": "United States Senate",
                                 "vote_number": number, "issue": issue,
                                 "question": question, "result": result,
                                 "tally": tally or {"Yea": 50, "Nay": 47}}}),
         now))
    conn.commit()


def test_recorded_votes_section(conn, tmp_path):
    add_vote(conn, "PR-senate-xml-11111111", number="00217", claimed=DATE,
             title="S. Res. 817; An executive resolution.",
             # stored sort_keys-first, so the renderer must reorder it
             tally={"Nay": 47, "Not Voting": 3, "Present": 0, "Yea": 50},
             wayback="https://web.archive.org/web/20260723/https://senate.gov/v")
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text()
    assert "## 7. Recorded Votes" in md
    assert "#### United States Senate" in md
    assert "**[Vote 217 — S.Res. 817: On the Resolution]" in md
    assert "— Agreed to (50-47)." in md
    assert "  - Tally: Yea 50 · Nay 47 · Present 0 · Not Voting 3" in md
    assert "VOTES-SEL-01 — recorded vote of this day" in md
    assert "selection is by existence, not by importance" in md
    assert "- [7. Recorded Votes](#7-recorded-votes)" in md  # ToC
    assert "| VOTES |" in md  # coverage row


def test_recorded_votes_listed_in_vote_number_order(conn, tmp_path):
    """GUIDE §3: vote-number order, no rule that ranks one question above
    another. The index hands them back newest-first."""
    add_vote(conn, "PR-senate-xml-bbbbbbbb", number="00217", claimed=DATE,
             title="Later vote.")
    add_vote(conn, "PR-senate-xml-aaaaaaaa", number="00099", claimed=DATE,
             title="Earlier vote.")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert md.index("Vote 99 ") < md.index("Vote 217 ")


def test_vote_dated_another_day_is_counted_not_listed(conn, tmp_path):
    """The lookback window reaches back further than one day; VOTES-EX-01
    keeps those out of today's list and inside the arithmetic."""
    add_vote(conn, "PR-senate-xml-cccccccc", number="00210", claimed="2026-07-21",
             title="A vote from earlier in the week.")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "A vote from earlier in the week." not in md
    assert "1 recorded vote(s) the chambers date on other days" in md
    assert "VOTES-EX-01" in md
    row = re.search(r"^\| VOTES \| (.+) \|$", md, re.MULTILINE).group(1)
    assert [c.strip() for c in row.split("|")] == ["1", "1", "0", "0", "1"]


def test_recorded_votes_empty_state_renders(digest):
    """Empty sections are disclosure, not a bug (CLAUDE.md §9)."""
    _path, md = digest
    assert "## 7. Recorded Votes" in md
    assert "No recorded votes dated this day were observed." in md
    assert "| VOTES | 0 | 0 | 0 | 0 | 0 |" in md


def test_banned_word_in_vote_title_is_masked(conn, tmp_path):
    """A measure's own title is the chamber's text, quoted not endorsed."""
    add_vote(conn, "PR-senate-xml-dddddddd", number="00218", claimed=DATE,
             title="A joint resolution on the historic landmark reserve.")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "historic landmark reserve" in md


def add_bill_action(conn, package_id, *, bill_type="S", number="3010",
                    congress="119", title="21st Century Dyslexia Act",
                    action="Committee on Finance. Ordered to be reported.",
                    action_date=DATE, chamber="Senate", designation=None):
    now = "2026-07-23T15:00:00Z"
    designation = designation or f"{bill_type}. {number}"
    url = ("https://www.congress.gov/bill/119th-congress/senate-bill/" + number)
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES (?, 'BILLACTIONS', ?, ?, ?, 'fetched')",
        (package_id, action_date, now, now))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, '', 'BILLACTIONS', 'BILLACTION', ?, 'Congress.gov API',"
        " ?, 'body', 4, ?, 1)",
        (package_id, f"{designation} — {title}",
         json.dumps({"source_id": "congress-gov-api", "url": url,
                     "claimed_published_at": action_date, "mode": "feed-only",
                     "details": {"publisher": "Library of Congress",
                                 "congress": congress, "bill_type": bill_type,
                                 "bill_number": number, "designation": designation,
                                 "bill_title": title, "origin_chamber": chamber,
                                 "action_date": action_date, "action_text": action}}),
         now))
    conn.commit()


def test_bill_actions_section(conn, tmp_path):
    add_bill_action(conn, "PR-congress-gov-api-11111111")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "## 8. Bill Actions" in md
    assert ("- **[S. 3010 — 21st Century Dyslexia Act]"
            "(https://www.congress.gov/bill/119th-congress/senate-bill/3010)**") in md
    assert "  - Action: Committee on Finance. Ordered to be reported." in md
    assert "  - 119th Congress · originated in the Senate" in md
    assert "BILLACTIONS-SEL-01 — action the Library of Congress" in md
    assert "selection is by existence, not importance" in md
    assert "- [8. Bill Actions](#8-bill-actions)" in md  # ToC
    assert "| BILLACTIONS | 1 | 1 | 0 | 1 | 0 |" in md   # coverage reconciles
    # the measured publication lag is a standing Known-gaps disclosure
    assert "publishes a day's bill actions the following morning" in md


def test_bill_actions_listed_in_designation_order(conn, tmp_path):
    """House measures then Senate, bill before resolution, by number — a
    clerical ordering, not a ranking (GUIDE §3)."""
    add_bill_action(conn, "PR-congress-gov-api-aaaaaaaa", bill_type="SJRES",
                    number="199", designation="S.J.Res. 199", title="Later.")
    add_bill_action(conn, "PR-congress-gov-api-bbbbbbbb", bill_type="HR",
                    number="7831", designation="H.R. 7831", title="First.",
                    chamber="House")
    add_bill_action(conn, "PR-congress-gov-api-cccccccc", bill_type="S",
                    number="12", designation="S. 12", title="Middle.")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert md.index("H.R. 7831") < md.index("S. 12") < md.index("S.J.Res. 199")


def test_bill_action_dated_another_day_is_not_this_digest(conn, tmp_path):
    """These are dated by the publisher (GUIDE §3 "Bill actions"), so an
    action from another day belongs to that day's digest — it is neither
    listed nor counted here, and no exclusion rule pretends otherwise."""
    add_bill_action(conn, "PR-congress-gov-api-dddddddd", number="5183",
                    title="An action from earlier in the week.",
                    action_date="2026-07-21")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "An action from earlier in the week." not in md
    assert "| BILLACTIONS | 0 | 0 | 0 | 0 | 0 |" in md


def test_bill_actions_empty_state_renders(digest):
    """Empty sections are disclosure, not a bug (CLAUDE.md §9)."""
    _path, md = digest
    assert "## 8. Bill Actions" in md
    assert "No bill actions dated this day were observed." in md
    assert "| BILLACTIONS | 0 | 0 | 0 | 0 | 0 |" in md


def test_banned_word_in_bill_title_and_action_is_masked(conn, tmp_path):
    """A measure's title and the record's action sentence are the
    government's own words, quoted not endorsed — the gate polices our
    prose. Without masking, "Historic Preservation" would block the day."""
    add_bill_action(conn, "PR-congress-gov-api-eeeeeeee", number="4242",
                    title="Historic Preservation Fund Act",
                    action="Referred to the Subcommittee on Landmark Sites.")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "Historic Preservation Fund Act" in md
    assert "Subcommittee on Landmark Sites" in md


def test_banned_word_in_agency_title_is_masked(conn, tmp_path):
    # Agency titles are attributed official speech quoted verbatim (§2);
    # the lexicon gate polices our prose, not the government's (found live
    # 2026-07-28: a DoD release titled "Historic Multinational...").
    now = "2026-07-23T15:00:00Z"
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES ('PR-defense-newsroom-def67890',"
        " 'AGENCYPR', ?, ?, ?, 'fetched')", (DATE, now, now))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES ('PR-defense-newsroom-def67890', '', 'AGENCYPR', 'PRESS',"
        " 'Historic Landmark Exercise Concludes', 'Department of Defense',"
        " ?, 'body', 4, ?, 1)",
        (json.dumps({"source_id": "defense-newsroom", "url": "https://x.gov/hx",
                     "claimed_published_at": None, "wayback_url": None}), now))
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    assert "Historic Landmark Exercise Concludes" in path.read_text()


def test_banned_word_in_govinfo_title_is_exempt(conn, tmp_path):
    """Review D21: the old mask covered only three collections' titles —
    an FR title or court case caption containing a banned word blocked
    the entire digest. Official titles from EVERY collection are quoted,
    not endorsed, and never gated (GUIDE §2 scope, 2026-08-02)."""
    conn.execute(
        "UPDATE extracted_texts SET title ="
        " 'Landmark Legal Foundation v. EPA; Historic Preservation Notice'"
        " WHERE package_id = ? AND granule_id = '2026-11111'", (FR_PKG,))
    conn.commit()
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "Landmark Legal Foundation v. EPA" in md  # rendered, not hidden


def test_official_name_in_model_prose_is_exempt(conn, tmp_path):
    """GUIDE §2 official-name exemption (operator, 2026-08-02): model
    prose may name a statute or case whose official name contains a
    banned word — verbatim only. Naming the record is stating a fact."""
    conn.execute(
        "UPDATE extracted_texts SET title ="
        " 'National Historic Preservation Act Compliance Rule'"
        " WHERE package_id = ? AND granule_id = '2026-22222'", (FR_PKG,))
    conn.execute(
        "UPDATE summaries SET summary = 'The rule implements the National"
        " Historic Preservation Act Compliance Rule review steps.'"
        " WHERE package_id = ? AND granule_id = '2026-22222'", (FR_PKG,))
    conn.commit()
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "National Historic Preservation Act Compliance Rule review" in md


def test_free_banned_word_beside_official_name_still_fails(conn):
    """The exemption is positional: quoting the official name does not
    license the word elsewhere in the same sentence — the failure mode
    the old global str.replace masking was blind to (review D8)."""
    conn.execute(
        "UPDATE extracted_texts SET title ="
        " 'National Historic Preservation Act Compliance Rule'"
        " WHERE package_id = ? AND granule_id = '2026-22222'", (FR_PKG,))
    conn.execute(
        "UPDATE summaries SET summary = 'A historic change under the National"
        " Historic Preservation Act Compliance Rule.'"
        " WHERE package_id = ? AND granule_id = '2026-22222'", (FR_PKG,))
    conn.commit()
    with pytest.raises(report.ValidationError, match="historic"):
        report.render(conn, DATE)


def test_banned_word_in_link_url_is_not_prose(conn, tmp_path):
    # Link slugs echo source headlines (found live 2026-07-28:
    # war.gov/.../historic-multinational-.../) — URLs are citations, never
    # scanned as our prose.
    now = "2026-07-23T15:00:00Z"
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES ('PR-nist-news-aaa11111',"
        " 'AGENCYPR', ?, ?, ?, 'fetched')", (DATE, now, now))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES ('PR-nist-news-aaa11111', '', 'AGENCYPR', 'PRESS',"
        " 'Chip Packaging Advance', 'NIST', ?, 'body', 4, ?, 1)",
        (json.dumps({"source_id": "nist-news",
                     "url": "https://x.gov/withstand-extreme-sweeping-crackdown",
                     "claimed_published_at": None, "wayback_url": None}), now))
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    assert "withstand-extreme-sweeping-crackdown" in path.read_text()


def _insert_agency_item(conn, pkg_id, title, claimed, source="gao-reports"):
    now = "2026-07-23T15:00:00Z"
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES (?, 'AGENCYPR', ?, ?, ?, 'fetched')",
        (pkg_id, DATE, now, now))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection, doc_type,"
        " title, agency, metadata, text, char_count, extracted_at, extractor_version)"
        " VALUES (?, '', 'AGENCYPR', 'PRESS', ?, 'Test Agency', ?, 'body', 4, ?, 1)",
        (pkg_id, title,
         json.dumps({"source_id": source, "url": f"https://x.gov/{pkg_id}",
                     "claimed_published_at": claimed, "wayback_url": None}), now))
    conn.commit()


def test_agency_dating_rule_excludes_backfill(conn, tmp_path):
    """GUIDE §3 dating rule: only releases the agency dates on the digest
    day are listed; observed-today-but-dated-earlier items are counted
    under AGENCYPR-EX-01, never listed as today's news."""
    _insert_agency_item(conn, "PR-t-today001", "Todays Release",
                        "Thu, 23 Jul 2026 09:00:00 +0000")
    _insert_agency_item(conn, "PR-t-evening1", "Evening Release",
                        "Thu, 23 Jul 2026 21:30:00 -0400")  # UTC day is Jul 24
    _insert_agency_item(conn, "PR-t-backfil1", "March Release",
                        "Mon, 30 Mar 2026 12:00:00 +0000")
    _insert_agency_item(conn, "PR-t-nodate01", "Undated Release", None)
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text()
    assert "Todays Release" in md
    # Review D1 regression: an evening release the agency dates on the digest
    # day is listed — the UTC comparison used to misfile it as backfill.
    assert "Evening Release" in md
    assert "Undated Release" in md  # no claimed date -> observed-day fallback
    assert "dated by first observation" in md
    assert "March Release" not in md  # backfill: never listed
    assert "1 release(s) the agencies date on other days" in md
    # Review D2 regression: the Coverage Statement's fired-rules list names
    # AGENCYPR-EX-01 itself, not only section 6's prose several screens up.
    assert re.search(
        r"^- AGENCYPR-EX-01: .+ — 1 item\(s\)$", md, re.MULTILINE)
    # coverage reconciles: 4 units = 0 summarized + 3 counted + 1 excluded
    assert re.search(r"^\| AGENCYPR \| 4 \| 4 \| 0 \| 3 \| 1 \|$", md, re.MULTILINE)


def test_agency_claimed_day_parses_both_forms():
    assert report._claimed_day(
        {"claimed_published_at": "Tue, 28 Jul 2026 23:30:00 -0400"}
    ) == "2026-07-28"  # Eastern publication day, not the rolled-over UTC day
    assert report._claimed_day(
        {"claimed_published_at": "2026-07-28T09:00:00"}) == "2026-07-28"
    assert report._claimed_day({"claimed_published_at": "gibberish"}) is None
    assert report._claimed_day({}) is None


def test_agency_claimed_day_is_the_eastern_day():
    """Review D1: `date_issued` is the Eastern publication day, so the
    claimed day must be computed on the same clock. The UTC conversion
    misfiled every 20:00–23:59 ET release as backfill (the measured
    2026-08-01 case below), and a late UTC stamp is still the prior
    Eastern day."""
    assert report._claimed_day(
        {"claimed_published_at": "Sat, 01 Aug 2026 20:30:00 -0400"}
    ) == "2026-08-01"  # the exact case measured in the review
    assert report._claimed_day(
        {"claimed_published_at": "Sun, 02 Aug 2026 01:00:00 +0000"}
    ) == "2026-08-01"  # 21:00 ET Aug 1 — UTC already rolled over


def test_agency_section_empty_renders_none_line(digest):
    _, md = digest
    assert "No releases dated this day were observed from active" in md


def test_email_channel_item_cites_the_captured_bulletin(conn, tmp_path):
    """Email items disclose their channel and DKIM state; one that names no
    canonical page renders unlinked rather than citing something unrelated."""
    now = "2026-07-23T15:00:00Z"
    for pkg, url in (("PR-treasury-email-aaa", None),
                     ("PR-fsis-email-bbb", "https://www.fsis.usda.gov/recalls/x")):
        conn.execute(
            "INSERT INTO packages (package_id, collection, date_issued,"
            " last_modified, first_seen_at, fetch_status) VALUES (?, 'AGENCYPR',"
            " ?, ?, ?, 'fetched')", (pkg, DATE, now, now))
        conn.execute(
            "INSERT INTO extracted_texts (package_id, granule_id, collection,"
            " doc_type, title, agency, metadata, text, char_count, extracted_at,"
            " extractor_version) VALUES (?, '', 'AGENCYPR', 'PRESS', ?, 'Agency',"
            " ?, 'body', 4, ?, 1)",
            (pkg, f"Release for {pkg}",
             json.dumps({"source_id": "x-email", "url": url, "channel": "email",
                         "claimed_published_at": "Thu, 23 Jul 2026 09:00:00 +0000",
                         "dkim": {"result": "pass"}, "mode": "email-full"}), now))
    conn.commit()
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "agency email bulletin to this project's subscription" in md
    assert "DKIM-verified" in md
    assert "the bulletin named no canonical page" in md
    assert "**[Release for PR-fsis-email-bbb](https://www.fsis.usda.gov/recalls/x)**" in md
    assert "**Release for PR-treasury-email-aaa**" in md  # unlinked, not [x](None)
    assert "](None)" not in md


def test_agency_claimed_date_renders_as_a_real_date(conn, tmp_path):
    """RFC-822 headers must render as the parsed day, never truncated
    mid-year (live defect 2026-07-29: 'Tue, 28 Jul 26 1')."""
    _insert_agency_item(conn, "PR-t-datefmt1", "Dated Release",
                        "Tue, 23 Jul 2026 12:00:00 +0000")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "dated 2026-07-23 by the agency" in md
    assert "Jul 26 1" not in md


# ---------------------------------------------- calendar note + day link --


def test_weekend_digest_carries_the_fedcal_note(conn):
    """GUIDE §5 (amended 2026-08-03): a weekend digest states the federal
    calendar context in its header — the SAME fedcal sentence /today
    shows, through the same shared function."""
    md = report.render(conn, "2026-07-26").read_text()   # a Sunday
    assert "**Weekend note:**" in md
    assert "Sunday is not a federal business day." in md


def test_weekday_digest_carries_no_calendar_note(digest):
    _path, md = digest                                    # DATE is a Thursday
    assert "**Weekend note:**" not in md
    assert "**Federal holiday note:**" not in md


def test_holiday_digest_carries_the_fedcal_note(conn):
    md = report.render(conn, "2026-07-03").read_text()   # July 4 observed (Fri)
    assert "**Federal holiday note:**" in md
    assert "Independence Day (observed)" in md


def test_digest_links_day_view_only_when_journal_covers(conn):
    """The header's 'Full observed listing' link is emitted exactly for
    days the item journal covers — never for days before it existed."""
    md = report.render(conn, DATE).read_text()
    assert "Full observed listing" not in md             # no journal rows yet
    conn.execute(
        "INSERT INTO item_journal (observed_at, source_class, package_id,"
        " granule_id, collection, digest_date, event) VALUES"
        " (?, 'govinfo', ?, ?, 'CREC', ?, 'ingested')",
        (f"{DATE}T10:00:00Z", CREC_PKG, SENATE_GID, DATE))
    conn.commit()
    md = report.render(conn, DATE).read_text()
    assert (f"[Full observed listing for this day](day/{DATE}.html)" in md)
    assert "This digest is the canonical record." in md
    # a date before journal coverage still gets no link
    md_before = report.render(conn, "2026-07-22").read_text()
    assert "Full observed listing" not in md_before


# ---------------------------------------------- multi-channel corroboration --


def test_normalize_official_url_is_conservative():
    n = report._normalize_official_url
    a = n("https://www.justice.gov/opa/pr/x-settles/")
    assert a == n("http://justice.gov/opa/pr/x-settles")
    assert a == n("https://JUSTICE.gov/opa/pr/x-settles#top")
    assert a == n("https://justice.gov/opa/pr/x-settles?utm_source=feed")
    # distinct paths never merge (the DOJ job-posting lesson)
    assert n("https://justice.gov/job/ausa-338") != n("https://justice.gov/job/ausa-339")
    # substantive query params are identity
    assert n("https://a.gov/p?id=1") != n("https://a.gov/p?id=2")
    assert n(None) is None and n("") is None and n("mailto:x@a.gov") is None


def _add_agency_release(conn, pid, title, url, channel, dkim=None):
    add_package(conn, pid, "AGENCYPR")
    meta = {"url": url, "channel": channel}
    if dkim:
        meta["dkim"] = {"result": dkim}
    add_text(conn, pid, "", "AGENCYPR", "PRESS", title=title,
             agency="Department of Justice", metadata=meta)


def test_agency_section_merges_same_url_and_marks_corroborated(conn):
    """GUIDE §3 corroboration (2026-08-03): one canonical URL through two
    channels lists once, marked; every capture stays counted."""
    url = "https://www.justice.gov/opa/pr/settlement-announced"
    _add_agency_release(conn, "PR-web-1", "Settlement Announced", url, None)
    _add_agency_release(conn, "PR-eml-1", "Settlement Announced",
                        "https://justice.gov/opa/pr/settlement-announced/",
                        "email", dkim="pass")
    md = report.render(conn, DATE).read_text()
    assert md.count("[Settlement Announced]") == 1          # listed once
    assert "Corroborated: the same release (same canonical URL)" in md
    assert "email bulletin to this project's subscription, DKIM-verified" in md
    assert "1 release(s) above arrived through more than one ingestion channel" in md
    assert "the merge is presentation, not omission" in md
    # the web page is the primary listing (canonical full text)
    assert f"[Settlement Announced]({url})" in md


def test_agency_section_never_merges_on_title_or_missing_url(conn):
    _add_agency_release(conn, "PR-job-1", "Assistant United States Attorney",
                        "https://justice.gov/job/ausa-338", None)
    _add_agency_release(conn, "PR-job-2", "Assistant United States Attorney",
                        "https://justice.gov/job/ausa-339", None)
    _add_agency_release(conn, "PR-nul-1", "EOIR Decision", None, "email")
    _add_agency_release(conn, "PR-nul-2", "EOIR Decision", None, "email")
    md = report.render(conn, DATE).read_text()
    assert md.count("[Assistant United States Attorney]") == 2
    assert md.count("**EOIR Decision**") == 2
    assert "Corroborated:" not in md


# ---------------------------------------------------------------- filing --
# Observation-day filing (GUIDE §3, amended 2026-08-06): section 1 keys on
# digest_day; each issue names its proceedings date; an empty day says so
# in words, never as a zero that reads as "Congress was idle".


def _add_late_crec_issue(conn, proceedings_date="2026-07-22"):
    """A Record issue observed on DATE covering an earlier day's
    proceedings — the CREC-2026-08-04 shape that exposed the gap."""
    pkg = f"CREC-{proceedings_date}"
    gid = f"CREC-{proceedings_date}-pt1-PgS9001"
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued,"
        " last_modified, first_seen_at, fetch_status, digest_day)"
        " VALUES (?, 'CREC', ?, '2026-07-23T11:34:54Z',"
        " '2026-07-23T11:42:42Z', 'fetched', ?)",
        (pkg, proceedings_date, DATE))
    add_text(conn, pkg, gid, "CREC", "SENATE", chars=16000,
             text=("floor debate " * 1200)[:16000])
    add_summary(conn, pkg, gid, "CREC-SEL-01", "A floor debate occurred.")
    conn.commit()
    return pkg, gid


def test_late_observed_crec_renders_with_all_three_clocks(conn, tmp_path):
    _add_late_crec_issue(conn)
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert f"issue observed {DATE}" in md
    assert "covering proceedings of 2026-07-22" in md
    assert "Published by govinfo 2026-07-23T11:34:54Z" in md
    assert "(document dated 2026-07-22)" in md          # the item clause
    assert "A floor debate occurred." in md


def test_crec_issue_does_not_render_on_its_proceedings_day(conn, tmp_path):
    """The same issue must NOT appear when rendering the proceedings
    date — filing is by observation, once."""
    _add_late_crec_issue(conn)
    md = report.render(conn, "2026-07-22", out_dir=tmp_path).read_text()
    assert "A floor debate occurred." not in md
    assert "No Congressional Record issue was observed" in md


def test_empty_crec_day_states_the_absence_in_words(conn, tmp_path):
    # A day with no observed CREC issue at all (the fixture seeds DATE,
    # so render a different, empty day).
    md = report.render(conn, "2026-07-25", out_dir=tmp_path).read_text()
    assert "No Congressional Record issue was observed on this day." in md
    assert "Total issue size: 0 granule(s)" not in md


# ------------------------------------------------ §9 presidential actions --
# whitehouse.gov feeds, activated 2026-08-06. The publisher states each
# action's class; the digest never infers it.


def _add_presact(conn, pkg, title, doc_type, claimed, url=None, source="whitehouse-presidential-actions"):
    now = "2026-07-23T12:00:00Z"
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued,"
        " last_modified, first_seen_at, fetch_status, digest_day)"
        " VALUES (?, 'PRESACT', ?, ?, ?, 'fetched', ?)",
        (pkg, DATE, now, now, DATE))
    conn.execute(
        "INSERT INTO extracted_texts (package_id, granule_id, collection,"
        " doc_type, title, agency, metadata, text, char_count, extracted_at,"
        " extractor_version) VALUES (?, '', 'PRESACT', ?, ?, 'The White House',"
        " ?, 'body', 4, ?, 1)",
        (pkg, doc_type, title,
         json.dumps({"source_id": source,
                     "url": url or f"https://www.whitehouse.gov/{pkg}",
                     "claimed_published_at": claimed, "wayback_url": None}),
         now))
    conn.commit()


def test_presidential_actions_render_by_publisher_class(conn, tmp_path):
    _add_presact(conn, "PA-eo-1", "Ending Birth Tourism", "EO",
                 "Thu, 23 Jul 2026 21:07:00 +0000")
    _add_presact(conn, "PA-pr-1", "National Purple Heart Day, 2026",
                 "PROCLAMATION", "Thu, 23 Jul 2026 20:54:00 +0000")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "## 9. Presidential Actions" in md
    assert "### 9.1 Executive Orders" in md
    assert "### 9.2 Proclamations" in md
    # The title is the publisher's words, verbatim — never reworded.
    assert "Ending Birth Tourism" in md
    assert "PRESACT-SEL-01" in md and "PRESACT-SEL-02" in md


def test_presidential_action_dated_earlier_is_counted_not_listed(conn, tmp_path):
    """GUIDE §3 dating rule, as for agency releases: the feeds carry months
    of history, and first activation must not list it all as today's news."""
    _add_presact(conn, "PA-old-1", "An Older Order", "EO",
                 "Mon, 30 Mar 2026 12:00:00 +0000")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "An Older Order" not in md
    assert "PRESACT-EX-01" in md
    assert "| PRESACT | 1 | 1 | 0 | 0 | 1 |" in md   # coverage identity holds


def test_same_order_in_both_feeds_lists_once_marked(conn, tmp_path):
    """Both whitehouse.gov feeds carry executive orders; an order in both
    shares its canonical URL and merges under the standing corroboration
    rule rather than listing twice."""
    url = "https://www.whitehouse.gov/presidential-actions/2026/07/x/"
    _add_presact(conn, "PA-dup-1", "Ending Birth Tourism", "EO",
                 "Thu, 23 Jul 2026 21:07:00 +0000", url=url)
    _add_presact(conn, "PA-dup-2", "Ending Birth Tourism", "EO",
                 "Thu, 23 Jul 2026 21:07:00 +0000", url=url,
                 source="whitehouse-executive-orders")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert md.count("**[Ending Birth Tourism]") == 1
    assert "Corroborated:" in md


def test_presidential_action_titles_bypass_the_lexicon_gate(conn, tmp_path):
    """An order the President titles with a banned term is still titled
    that: GUIDE §2's gate binds our prose, never the publisher's."""
    _add_presact(conn, "PA-lex-1", "A Historic and Unprecedented Order", "EO",
                 "Thu, 23 Jul 2026 21:07:00 +0000")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "A Historic and Unprecedented Order" in md


# ------------------------------------------------- the third dating tier --
# GUIDE §3, added 2026-08-06. Drupal sites emit their site date format in
# <pubDate>; an unreadable date falls back to observation, which the
# dating split treats as TODAY — so a feed spanning weeks would publish
# all of it as today's news.


def test_claimed_day_reads_drupal_slash_dates():
    """NIH's feed: 'Wed, 08/05/2026 - 08:00'. Looks like RFC 822 and is
    not; email.utils rejects it."""
    assert report._claimed_day(
        {"claimed_published_at": "Wed, 08/05/2026 - 08:00"}) == "2026-08-05"
    assert report._claimed_day(
        {"claimed_published_at": "Fri, 07/31/2026 - 09:00"}) == "2026-07-31"


def test_claimed_day_reads_long_month_dates():
    """TSA's feed: 'July 17, 2026'."""
    assert report._claimed_day(
        {"claimed_published_at": "July 17, 2026"}) == "2026-07-17"


def test_claimed_day_slash_dates_are_us_ordered():
    """Every publisher in this registry is a US federal body writing for
    a US audience. The assumption is auditable, not incidental: 08/05 is
    5 August, never 8 May."""
    assert report._claimed_day(
        {"claimed_published_at": "08/05/2026"}) == "2026-08-05"


def test_claimed_day_rejects_impossible_dates():
    """A string that states no valid calendar date keeps returning None,
    and None keeps its meaning — we could not read it."""
    for raw in ("13/45/2026", "not a date at all", "", "Month 99, 2026"):
        assert report._claimed_day({"claimed_published_at": raw}) is None


def test_existing_date_formats_are_unchanged():
    """The new tier runs only after RFC 822 and ISO both fail, so no
    currently-parsing source can move."""
    assert report._claimed_day(
        {"claimed_published_at": "Thu, 06 Aug 2026 21:07:11 +0000"}) == "2026-08-06"
    assert report._claimed_day({"claimed_published_at": "2026-08-05"}) == "2026-08-05"
    # Zone-aware evening release stays on its Eastern day (review D1).
    assert report._claimed_day(
        {"claimed_published_at": "Thu, 23 Jul 2026 21:30:00 -0400"}) == "2026-07-23"


def test_drupal_dated_backfill_is_counted_not_listed(conn, tmp_path):
    """The whole point: with the date readable, an older release sorts
    into backfill instead of being published as today's news."""
    _insert_agency_item(conn, "PR-dr-today", "Todays NIH Release",
                        "Thu, 07/23/2026 - 08:00")     # DATE is 2026-07-23
    _insert_agency_item(conn, "PR-dr-old", "Six Weeks Old",
                        "Mon, 06/15/2026 - 09:15")
    md = report.render(conn, DATE, out_dir=tmp_path).read_text()
    assert "Todays NIH Release" in md
    assert "Six Weeks Old" not in md
    assert "AGENCYPR-EX-01" in md


def test_display_title_preserves_nicknames_and_apostrophised_surnames():
    """F-022 follow-on: the naive first-character upper() mangled the two
    shapes Extensions of Remarks are made of. Latent until the live page
    began titling every CREC granule — floor-debate headings carry
    neither."""
    assert report._display_title(
        'HONORING THE SERVICE OF SAMUEL "SAM" DOUGHERTY') == (
        'Honoring the Service of Samuel "Sam" Dougherty')
    assert report._display_title(
        'RECOGNIZING MARTIN JOSEPH "JOE" O\'ROURKE') == (
        'Recognizing Martin Joseph "Joe" O\'Rourke')
    # a trailing possessive s is not a new word
    assert report._display_title("HONORING SAMUEL'S SERVICE") == (
        "Honoring Samuel's Service")
    # hyphenated surnames capitalize on both sides
    assert report._display_title("HONORING JANE SMITH-JONES") == (
        "Honoring Jane Smith-Jones")
    # the typographic apostrophe behaves like the ASCII one
    assert report._display_title("RECOGNIZING PAT O’BRIEN") == (
        "Recognizing Pat O’Brien")


# ---------------------------------------------------------------------------
# GUIDE §6 r15 (2026-08-24): the digest stands without inference
# ---------------------------------------------------------------------------


def _strip_generated(md):
    return "\n".join(l for l in md.splitlines() if not l.startswith("| **Generated at**"))


def test_zero_summary_day_renders_mechanically_and_validates(conn, tmp_path):
    conn.execute("DELETE FROM summaries")
    conn.execute("DELETE FROM plain_summaries")
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text(encoding="utf-8")
    # The header says exactly the ruled sentence, and no cause.
    assert f"| **Inference** | {inference.NO_INFERENCE} |" in md
    # Every selected item still appears, with its citation and rule,
    # marked from the record — sections 1, 2, 3, 5 all carry one.
    assert "- **Consideration of S. 9999, Interstate Bridge Inspection Act** — "\
           "*listed from the record*" in md
    assert "- **H. R. 8888 (enr) — Rural Broadband Mapping Act** — "\
           "*listed from the record*" in md
    assert "- **Energy Conservation Standards** (2026-11111; 10 CFR Part 430) — "\
           "*listed from the record*" in md
    assert "- **Doe v. Example Agency** (No. 26-00042; filed 2026-07-23) — "\
           "*listed from the record*" in md
    assert "*In plain terms:*" not in md
    assert md.count("Items marked *listed from the record* are listed without a summary.") == 4
    # Coverage arithmetic unchanged: nothing summarized, everything accounted
    # for (CREC: the two sub-threshold floor granules — the roll-call one
    # included, now that its SEL-02 summary is gone — are CREC-EX-01).
    assert "| CREC | 1 | 5 | 0 | 3 | 2 |" in md
    assert "| BILLS | 2 | — | 0 | 2 | 0 |" in md
    assert "| FR | 1 | 6 | 0 | 2 | 4 |" in md
    assert "| USCOURTS | 4 | 4 | 0 | 2 | 2 |" in md
    # No reason text anywhere near the marker.
    for line in md.splitlines():
        if "listed from the record" in line:
            assert "error" not in line.lower() and "quota" not in line.lower()


def test_mixed_day_lists_both_forms_and_reconciles(conn, tmp_path):
    conn.execute("DELETE FROM summaries WHERE granule_id = '2026-22222'")
    conn.commit()
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text(encoding="utf-8")
    assert "- **Test Procedure Update** (2026-22222) — *listed from the record*" in md
    assert ("- **Energy Conservation Standards** (2026-11111; 10 CFR Part 430) — "
            "A final rule amending conservation standards") in md
    # The note appears once, in the section that needs it, not elsewhere.
    assert md.count("Items marked *listed from the record* are listed without a summary.") == 1
    assert md.index("## 3. Federal Register") < md.index("Items marked *listed from the record*")
    assert md.index("Items marked *listed from the record*") < md.index("## 4. Enacted Laws")
    # FR: 6 units, 3 summarized (was 4), notices 2 counted, remainder excluded.
    assert "| FR | 1 | 6 | 3 | 2 | 1 |" in md


def test_recorded_status_renders_attribution(conn, tmp_path):
    inference.record(conn, DATE, backend="cli", models=["haiku", "opus"],
                     layers=dict.fromkeys(inference.LAYERS, "ran"))
    md = report.render(conn, DATE, out_dir=tmp_path).read_text(encoding="utf-8")
    assert "| **Inference** | model layers ran — cli/haiku, opus |" in md


def test_partial_status_names_layers_not_causes(conn, tmp_path):
    inference.record(conn, DATE, backend="gemini", models=["gemini-2.5-flash"],
                     layers={"map": "ran", "plain": "failed", "compose": "skipped",
                             "sections": "ran", "tags": "ran"})
    md = report.render(conn, DATE, out_dir=tmp_path).read_text(encoding="utf-8")
    assert ("| **Inference** | model layers ran in part — gemini/gemini-2.5-flash;"
            " not available: plain-language lines, Day in Review |") in md
    assert "failed" not in md.split("## Contents")[0]


def test_recorded_no_inference_uses_the_ruled_sentence_only(conn, tmp_path):
    inference.record(conn, DATE, backend="gemini", models=[],
                     layers=dict.fromkeys(inference.LAYERS, "failed"))
    md = report.render(conn, DATE, out_dir=tmp_path).read_text(encoding="utf-8")
    header = md.split("## Contents")[0]
    assert inference.NO_INFERENCE in header
    assert "gemini" not in header and "failed" not in header


def test_unrecorded_day_with_model_prose_says_so(digest):
    _, md = digest  # seeded summaries, no day_inference row: pre-r15 shape
    assert ("| **Inference** | model layers ran (inference status not recorded"
            " for this day) |") in md


def test_empty_unrecorded_day_carries_the_no_inference_row(project):
    connection = db.connect(project / "data" / "empty.db")
    try:
        md = report.render(connection, "2026-01-01").read_text(encoding="utf-8")
        assert f"| **Inference** | {inference.NO_INFERENCE} |" in md
    finally:
        connection.close()


def test_banned_word_in_unsummarized_official_title_passes_the_gate(conn, tmp_path):
    add_text(conn, FR_PKG, "2026-77777", "FR", "RULE",
             title="Landmark Appliance Standards", chars=5000)
    conn.commit()
    md = report.render(conn, DATE, out_dir=tmp_path).read_text(encoding="utf-8")
    assert "- **Landmark Appliance Standards** (2026-77777) — *listed from the record*" in md


def test_methodology_quotes_rule_15_verbatim(digest):
    _, md = digest
    assert ("*Inference (GUIDE §6 r15, standing): The pipeline finalizes every\n"
            "publication day with or without an inference provider.") in md
    assert "prose is not\nbackfilled into a frozen digest.*" in md


def test_render_is_deterministic_with_and_without_summaries(conn, tmp_path):
    first = _strip_generated(report.render(conn, DATE, out_dir=tmp_path).read_text())
    second = _strip_generated(report.render(conn, DATE, out_dir=tmp_path).read_text())
    assert first == second
    conn.execute("DELETE FROM summaries")
    conn.execute("DELETE FROM plain_summaries")
    conn.commit()
    bare1 = _strip_generated(report.render(conn, DATE, out_dir=tmp_path).read_text())
    bare2 = _strip_generated(report.render(conn, DATE, out_dir=tmp_path).read_text())
    assert bare1 == bare2 and bare1 != first

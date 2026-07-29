"""REPORT stage tests: full render against a seeded temporary database.

No LLM calls, no network, no touching data/ — config.PROJECT_ROOT and
config.DIGEST_DIR are monkeypatched to a tmp directory and the graphic
assets are tiny real TIFFs generated with Pillow.
"""

import json
import re

import pytest
from PIL import Image

from fapd import config, db, report

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
    connection = db.connect(project / "data" / "fapd.db")
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
    assert "No appellate or national court opinions matched a listing rule" in md
    # Unsummarized appellate opinions land in the excluded remainder;
    # district + bankruptcy stay counted-only. 0 + 2 + 2 == 4 units.
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
    _insert_agency_item(conn, "PR-t-backfil1", "March Release",
                        "Mon, 30 Mar 2026 12:00:00 +0000")
    _insert_agency_item(conn, "PR-t-nodate01", "Undated Release", None)
    path = report.render(conn, DATE, out_dir=tmp_path)
    md = path.read_text()
    assert "Todays Release" in md
    assert "Undated Release" in md  # no claimed date -> observed-day fallback
    assert "dated by first observation" in md
    assert "March Release" not in md  # backfill: never listed
    assert "1 release(s) the agencies date on other days" in md
    assert "AGENCYPR-EX-01" in md
    # coverage reconciles: 3 units = 0 summarized + 2 counted + 1 excluded
    assert re.search(r"^\| AGENCYPR \| 3 \| 3 \| 0 \| 2 \| 1 \|$", md, re.MULTILINE)


def test_agency_claimed_day_parses_both_forms():
    assert report._claimed_day(
        {"claimed_published_at": "Tue, 28 Jul 2026 23:30:00 -0400"}
    ) == "2026-07-29"  # timezone conversion to UTC day
    assert report._claimed_day(
        {"claimed_published_at": "2026-07-28T09:00:00"}) == "2026-07-28"
    assert report._claimed_day({"claimed_published_at": "gibberish"}) is None
    assert report._claimed_day({}) is None


def test_agency_section_empty_renders_none_line(digest):
    _, md = digest
    assert "No releases dated this day were observed from active" in md

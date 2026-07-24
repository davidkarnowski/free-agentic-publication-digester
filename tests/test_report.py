"""REPORT stage tests: full render against a seeded temporary database.

No LLM calls, no network, no touching data/ — config.PROJECT_ROOT and
config.DIGEST_DIR are monkeypatched to a tmp directory and the graphic
assets are tiny real TIFFs generated with Pillow.
"""

import json

import pytest
from PIL import Image

from info_intel import config, db, report

DATE = "2026-07-23"
CREC_PKG = "CREC-2026-07-23"
FR_PKG = "FR-2026-07-23"
SENATE_GID = "CREC-2026-07-23-pt1-PgS4101"
VOTE_GID = "CREC-2026-07-23-pt1-PgH6220"


def add_package(conn, package_id, collection, status="fetched"):
    conn.execute(
        "INSERT INTO packages (package_id, collection, date_issued, last_modified,"
        " first_seen_at, fetch_status) VALUES (?, ?, ?, ?, ?, ?)",
        (package_id, collection, DATE, "2026-07-23T12:00:00Z", "2026-07-23T12:00:00Z", status),
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

    for collection in ("CREC", "BILLS", "FR"):
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
    connection = db.connect(project / "data" / "info_intel.db")
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
        "## Coverage Statement",
        "## Methodology",
    ):
        assert heading in md
    # Header metadata and watermarks.
    assert f"| **Digest date** | {DATE} |" in md
    assert "CREC: 2026-07-23T18:00:00Z" in md
    # An empty subsection renders its explicit none-line, never silence.
    assert "No House floor items met the selection thresholds" in md
    assert "PLAW is not yet ingested" in md
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
    assert "**ROLL CALL 512 ON PASSAGE OF H.R. 8888**" in md
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
    assert items == because == 7  # 1 floor + 1 vote + 1 bill + 2 rules + 1 prorule + 1 presdocu
    # CREC-SEL-01 carries its mechanical evidence (the actual char count).
    assert "CREC-SEL-01 — floor item ≥ threshold floor time (20,000 characters)" in md
    assert "CREC-SEL-02 — recorded vote (all recorded votes are listed)" in md
    assert "BILLS-SEL-01 — reached stage: reported/enrolled/calendar" in md
    assert "FR-SEL-01 — document type: final rule (all listed)" in md


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
    assert "CREC-EX-01: floor granule below floor-time threshold — 1 item(s)" in md
    assert "CREC-EX-02: extensions/daily-digest sections (counted) — 2 item(s)" in md
    assert "FR-EX-01: notices counted, not individually summarized — 2 item(s)" in md
    assert "4 graphic(s) flagged" in md
    assert "3 content graphic(s)" in md
    assert "1 boilerplate" in md
    assert "0 were analyzed via vision pass (vision pass not yet implemented)" in md
    assert "2 embedded above" in md
    assert "**Known gaps:** none identified." in md


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
        assert "No recorded votes were published" in md
        assert "No rules were published in this issue." in md
        assert "No bill texts published in this range matched a listing rule; all 0 are" in md
    finally:
        connection.close()

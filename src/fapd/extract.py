"""Extraction orchestrator: fetched raw packages -> extracted_texts rows
(+ graphic asset inventory/extraction for FR).

Staleness rules mirror the fetch layer's watermark thinking: a package needs
(re-)extraction when it has no extraction, its raw file was re-fetched after
the last extraction, or EXTRACTOR_VERSION was bumped. Re-extraction is
replace-on-rerun per package (delete + insert), so the operation is
idempotent and partial failures re-run harmlessly.
"""

import importlib
import json
import logging
from pathlib import Path

from . import config
from .client import redact_secrets
from .sync import utc_now_iso

logger = logging.getLogger("fapd.extract")

# Bump to force re-extraction of everything (recorded per row).
EXTRACTOR_VERSION = 1

_PARSER_MODULES = {
    "FR": "fapd.parsers.fr",
    "CREC": "fapd.parsers.crec",
    "BILLS": "fapd.parsers.bills",
    "USCOURTS": "fapd.parsers.uscourts",
    "PLAW": "fapd.parsers.plaw",
}


def _parser_for(collection):
    return importlib.import_module(_PARSER_MODULES[collection]).parse


def pending_packages(conn, collections=None):
    rows = conn.execute(
        """
        SELECT p.* FROM packages p
        LEFT JOIN (
            SELECT package_id, MAX(extracted_at) AS extracted_at,
                   MIN(extractor_version) AS min_version
            FROM extracted_texts GROUP BY package_id
        ) e USING (package_id)
        WHERE p.fetch_status = 'fetched'
          AND (e.extracted_at IS NULL
               OR e.extracted_at < p.fetched_at
               OR e.min_version < ?)
          -- The per-package ceiling (2026-08-24): a package past it is a
          -- disclosed gap (the coverage statement's "fetched but not
          -- extracted" line), not pending work. Same shape as
          -- MAX_PACKAGE_FETCH_ATTEMPTS one layer down.
          AND p.extract_attempts < ?
        ORDER BY p.package_id
        """,
        (EXTRACTOR_VERSION, config.MAX_PACKAGE_EXTRACT_ATTEMPTS),
    ).fetchall()
    if collections:
        rows = [r for r in rows if r["collection"] in collections]
    return rows


def extract_package(conn, package_row):
    """Extract one package. Returns a stats dict; raises on parser failure
    (caller decides isolation policy)."""
    package = dict(package_row)
    raw_path = config.PROJECT_ROOT / package["raw_path"]
    parse = _parser_for(package["collection"])
    records = list(parse(raw_path, package))
    now = utc_now_iso()

    conn.execute("DELETE FROM extracted_texts WHERE package_id = ?", (package["package_id"],))
    conn.executemany(
        """
        INSERT INTO extracted_texts
            (package_id, granule_id, collection, doc_type, title, agency, metadata,
             text, char_count, graphics_substantive, graphics_boilerplate,
             extracted_at, extractor_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                package["package_id"],
                r["granule_id"],
                package["collection"],
                r.get("doc_type"),
                r.get("title"),
                r.get("agency"),
                json.dumps(r.get("metadata") or {}, sort_keys=True),
                r["text"],
                len(r["text"]),
                r.get("graphics_substantive", 0),
                r.get("graphics_boilerplate", 0),
                now,
                EXTRACTOR_VERSION,
            )
            for r in records
        ],
    )

    stats = {
        "package_id": package["package_id"],
        "records": len(records),
        "chars": sum(len(r["text"]) for r in records),
        "assets_extracted": 0,
        "assets_failed": 0,
    }
    if package["collection"] == "FR":
        _process_graphics(conn, package, raw_path, stats)
    # A success starts the ceiling over (the fetch_attempts rule).
    conn.execute(
        "UPDATE packages SET extract_attempts = 0, extract_error = NULL"
        " WHERE package_id = ?",
        (package["package_id"],),
    )
    conn.commit()
    logger.info(
        "%s: %d record(s), %d chars extracted%s",
        package["package_id"], stats["records"], stats["chars"],
        f", {stats['assets_extracted']} graphic asset(s)" if stats["assets_extracted"] else "",
    )
    return stats


def _process_graphics(conn, package, xml_path, stats):
    from . import graphics

    items = graphics.inventory(xml_path.read_bytes())
    if not items:
        return
    pdf_path = xml_path.with_suffix(".pdf")
    results = []
    if pdf_path.exists():
        out_dir = (
            config.DATA_DIR / "assets" / "FR"
            / (package.get("date_issued") or "unknown-date") / package["package_id"]
        )
        results = graphics.extract_assets(pdf_path, items, out_dir)
    # extract_assets returns one result per input item, in order.
    conn.execute("DELETE FROM graphic_assets WHERE package_id = ?", (package["package_id"],))
    for i, item in enumerate(items):
        result = results[i] if i < len(results) else None
        asset_path = (result or {}).get("asset_path")
        status = (result or {}).get("status") or (
            "skipped" if item["classification"] == "boilerplate" else "inventoried"
        )
        if asset_path:
            p = Path(asset_path)
            if p.is_absolute():
                asset_path = str(p.relative_to(config.PROJECT_ROOT))
        conn.execute(
            "INSERT INTO graphic_assets"
            " (package_id, granule_id, gid, classification, page, asset_path, status)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                package["package_id"], "", item["gid"], item["classification"],
                item.get("page"), asset_path, status,
            ),
        )
        if status == "extracted":
            stats["assets_extracted"] += 1
        elif status == "failed":
            stats["assets_failed"] += 1


def _record_failure(conn, package_id, exc):
    """Advance the per-package extraction ladder (2026-08-24). Runs AFTER
    the failed extraction's rollback, in its own short transaction, so the
    bookkeeping survives it. Returns the new attempt count.

    Before this the failure path wrote nothing, so pending_packages()
    reselected the package every govinfo cycle forever — FR-1995-01-04,
    a ZIP that is not XML, was re-parsed every ~30 minutes for eighteen
    days. The identical bug shape the sync layer fixed on 2026-08-10
    (MAX_PACKAGE_FETCH_ATTEMPTS) and the LLM layer fixed in July
    (MAX_ITEM_SUMMARY_ATTEMPTS); the pattern had not crossed over here."""
    row = conn.execute(
        "SELECT extract_attempts FROM packages WHERE package_id = ?", (package_id,)
    ).fetchone()
    attempts = (row["extract_attempts"] or 0) + 1
    conn.execute(
        "UPDATE packages SET extract_attempts = ?, extract_error = ?,"
        " last_extract_attempt_at = ? WHERE package_id = ?",
        (attempts, redact_secrets(repr(exc))[:500], utc_now_iso(), package_id),
    )
    conn.commit()
    return attempts


def run(conn, collections=None):
    """Extract all pending packages. One bad package doesn't kill the run,
    and one bad package doesn't get retried forever either
    (config.MAX_PACKAGE_EXTRACT_ATTEMPTS)."""
    results = {"packages": 0, "records": 0, "chars": 0, "failed": 0,
               "exhausted": 0, "assets_extracted": 0, "assets_failed": 0}
    for row in pending_packages(conn, collections):
        try:
            stats = extract_package(conn, row)
        except Exception as exc:  # noqa: BLE001 — isolation per package
            conn.rollback()
            results["failed"] += 1
            attempts = _record_failure(conn, row["package_id"], exc)
            if attempts >= config.MAX_PACKAGE_EXTRACT_ATTEMPTS:
                # Logged once, here, at the moment it crosses: from the
                # next cycle on the package is not selected, so this
                # line cannot repeat every 30 minutes the way the
                # failure itself did.
                results["exhausted"] += 1
                logger.warning(
                    "%s: extraction exhausted after %d attempts — disclosed,"
                    " not retried (a re-fetch or content revision resets it): %r",
                    row["package_id"], attempts, exc)
            else:
                logger.warning("%s: extraction failed (%d/%d attempts): %r",
                               row["package_id"], attempts,
                               config.MAX_PACKAGE_EXTRACT_ATTEMPTS, exc)
            continue
        results["packages"] += 1
        results["records"] += stats["records"]
        results["chars"] += stats["chars"]
        results["assets_extracted"] += stats["assets_extracted"]
        results["assets_failed"] += stats["assets_failed"]
    return results

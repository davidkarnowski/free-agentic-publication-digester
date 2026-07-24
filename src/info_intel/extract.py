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
from .sync import utc_now_iso

logger = logging.getLogger("info_intel.extract")

# Bump to force re-extraction of everything (recorded per row).
EXTRACTOR_VERSION = 1

_PARSER_MODULES = {
    "FR": "info_intel.parsers.fr",
    "CREC": "info_intel.parsers.crec",
    "BILLS": "info_intel.parsers.bills",
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
        ORDER BY p.package_id
        """,
        (EXTRACTOR_VERSION,),
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


def run(conn, collections=None):
    """Extract all pending packages. One bad package doesn't kill the run."""
    results = {"packages": 0, "records": 0, "chars": 0, "failed": 0,
               "assets_extracted": 0, "assets_failed": 0}
    for row in pending_packages(conn, collections):
        try:
            stats = extract_package(conn, row)
        except Exception as exc:  # noqa: BLE001 — isolation per package
            conn.rollback()
            results["failed"] += 1
            logger.warning("%s: extraction failed: %r", row["package_id"], exc)
            continue
        results["packages"] += 1
        results["records"] += stats["records"]
        results["chars"] += stats["chars"]
        results["assets_extracted"] += stats["assets_extracted"]
        results["assets_failed"] += stats["assets_failed"]
    return results

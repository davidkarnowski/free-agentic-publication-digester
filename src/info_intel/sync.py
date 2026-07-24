"""Delta sync: govinfo collections service -> metadata store -> raw archive.

Implements the algorithm in docs/schema.md (`sync_state` section):
list changed packages since the watermark, upsert idempotently, download
what's pending, and advance the watermark only after the listing completed.
The watermark is always a server-side lastModified value, never our clock.
A first sync (no watermark row) is date-bounded to INITIAL_SYNC_LOOKBACK_DAYS
per GUIDE.md §4.
"""

import datetime as dt
import logging

from . import config
from .client import BudgetExceededError, RateLimitFloorError

logger = logging.getLogger("info_intel.sync")

# Package-level download preference. XML is what Phase 2 parses; ZIP is the
# fallback for collections (like CREC) whose package-level content is only
# offered zipped; PDF is last resort, kept for archive completeness only.
_FORMAT_PREFERENCE = (("xmlLink", "xml"), ("zipLink", "zip"), ("pdfLink", "pdf"))

# Collections whose packages have granules worth inventorying (docs/schema.md).
_GRANULE_COLLECTIONS = {"CREC", "FR"}


def utc_now_iso():
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sync_collection(client, conn, collection, *, list_only=False, max_downloads=None):
    """One delta-sync run for one collection. Returns a stats dict."""
    started_at = utc_now_iso()
    start, is_first_run = _watermark_or_bounded_start(conn, collection)
    logger.info(
        "%s: sync starting from watermark %s%s (list_only=%s, max_downloads=%s)",
        collection, start,
        " [first run: date-bounded per GUIDE §4]" if is_first_run else "",
        list_only, max_downloads,
    )
    conn.execute(
        "INSERT INTO sync_state (collection, last_modified_watermark, last_sync_started_at)"
        " VALUES (?, ?, ?)"
        " ON CONFLICT(collection) DO UPDATE SET last_sync_started_at = excluded.last_sync_started_at",
        (collection, start, started_at),
    )
    conn.commit()

    # Step 3: list changed packages since the watermark. Any exception here
    # propagates before the watermark moves — next run re-lists this window.
    listed = 0
    max_seen = None
    for page in client.paginate(f"collections/{collection}/{start}", {"pageSize": 100}):
        for pkg in page.get("packages", []):
            _upsert_package(conn, collection, pkg)
            listed += 1
            lm = pkg.get("lastModified")
            if lm and (max_seen is None or lm > max_seen):
                max_seen = lm
        conn.commit()

    # Step 6 (listing succeeded): advance the watermark. Downloads below can
    # fail without forcing a re-list — pending rows are the queue.
    conn.execute(
        "UPDATE sync_state SET last_modified_watermark = ?,"
        " last_sync_completed_at = ?, last_sync_package_count = ?"
        " WHERE collection = ?",
        (max_seen or start, utc_now_iso(), listed, collection),
    )
    conn.commit()
    logger.info(
        "%s: listing complete — %d changed package(s); watermark advanced to %s",
        collection, listed, max_seen or start,
    )

    stats = {"collection": collection, "listed": listed, "downloaded": 0, "failed": 0}
    if not list_only:
        _download_pending(client, conn, collection, stats, max_downloads)
    stats["pending_remaining"] = conn.execute(
        "SELECT COUNT(*) FROM packages WHERE collection = ?"
        " AND fetch_status IN ('pending', 'failed')",
        (collection,),
    ).fetchone()[0]
    return stats


def _watermark_or_bounded_start(conn, collection):
    """Returns (start, is_first_run)."""
    row = conn.execute(
        "SELECT last_modified_watermark FROM sync_state WHERE collection = ?", (collection,)
    ).fetchone()
    if row:
        return row["last_modified_watermark"], False
    bounded = dt.datetime.now(dt.UTC) - dt.timedelta(days=config.INITIAL_SYNC_LOOKBACK_DAYS)
    return bounded.strftime("%Y-%m-%dT00:00:00Z"), True


def _upsert_package(conn, collection, pkg):
    conn.execute(
        """
        INSERT INTO packages (package_id, collection, last_modified, title, package_link,
                              date_issued, first_seen_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(package_id) DO UPDATE SET
            fetch_status  = CASE WHEN excluded.last_modified > packages.last_modified
                                 THEN 'pending' ELSE packages.fetch_status END,
            last_modified = MAX(packages.last_modified, excluded.last_modified),
            title         = COALESCE(excluded.title, packages.title),
            package_link  = COALESCE(excluded.package_link, packages.package_link),
            date_issued   = COALESCE(excluded.date_issued, packages.date_issued)
        """,
        (
            pkg["packageId"],
            collection,
            pkg.get("lastModified", ""),
            pkg.get("title"),
            pkg.get("packageLink"),
            pkg.get("dateIssued"),
            utc_now_iso(),
        ),
    )


def _download_pending(client, conn, collection, stats, max_downloads):
    rows = conn.execute(
        "SELECT package_id FROM packages WHERE collection = ?"
        " AND fetch_status IN ('pending', 'failed') ORDER BY package_id",
        (collection,),
    ).fetchall()
    capped = rows if max_downloads is None else rows[: max_downloads - stats["downloaded"]]
    if len(capped) < len(rows):
        logger.info(
            "%s: download cap %s limits this run to %d of %d queued; the rest stay pending",
            collection, max_downloads, len(capped), len(rows),
        )
    for row in capped:
        pid = row["package_id"]
        try:
            _download_package(client, conn, collection, pid)
            stats["downloaded"] += 1
        except (BudgetExceededError, RateLimitFloorError):
            # Budget/rate-floor: stop the whole run, leave the queue pending.
            conn.rollback()
            logger.error(
                "%s: run aborted by client halt after %d download(s); queue preserved",
                collection, stats["downloaded"],
            )
            raise
        except Exception as exc:  # noqa: BLE001 — one bad package must not kill the run
            conn.execute(
                "UPDATE packages SET fetch_status = 'failed', last_error = ?"
                " WHERE package_id = ?",
                (repr(exc)[:500], pid),
            )
            conn.commit()
            stats["failed"] += 1
            logger.warning("%s: download failed, marked 'failed' for retry: %r", pid, exc)


def _download_package(client, conn, collection, package_id):
    summary = client.get_json(f"packages/{package_id}/summary")
    date_issued = summary.get("dateIssued")
    links = summary.get("download") or {}
    url, fmt = None, None
    for key, ext in _FORMAT_PREFERENCE:
        if links.get(key):
            url, fmt = links[key], ext
            break
    if url is None:
        raise ValueError(f"no downloadable format among {sorted(links)}")

    resp = client.get(url)
    raw_dir = config.RAW_DIR / collection / (date_issued or "unknown-date")
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{package_id}.{fmt}"
    raw_path.write_bytes(resp.content)

    granule_count = None
    if collection in _GRANULE_COLLECTIONS:
        granule_count = _refresh_granules(client, conn, package_id)
    logger.info(
        "%s: archived as %s (%d B)%s",
        package_id, raw_path.name, len(resp.content),
        f", {granule_count} granules inventoried" if granule_count is not None else "",
    )

    conn.execute(
        "UPDATE packages SET date_issued = COALESCE(?, date_issued),"
        " title = COALESCE(?, title), download_url = ?, download_format = ?,"
        " raw_path = ?, fetch_status = 'fetched', fetched_at = ?,"
        " fetched_last_modified = last_modified, last_error = NULL"
        " WHERE package_id = ?",
        (
            date_issued,
            summary.get("title"),
            url,
            fmt,
            str(raw_path.relative_to(config.PROJECT_ROOT)),
            utc_now_iso(),
            package_id,
        ),
    )
    conn.commit()


def _refresh_granules(client, conn, package_id):
    # Replace-on-refetch (docs/schema.md): granule rows carry no local state.
    seen_at = utc_now_iso()
    granules = []
    for page in client.paginate(f"packages/{package_id}/granules", {"pageSize": 1000}):
        granules.extend(page.get("granules", []))
    conn.execute("DELETE FROM granules WHERE package_id = ?", (package_id,))
    conn.executemany(
        "INSERT INTO granules (package_id, granule_id, granule_class, title, first_seen_at)"
        " VALUES (?, ?, ?, ?, ?)",
        [
            (package_id, g["granuleId"], g.get("granuleClass"), g.get("title"), seen_at)
            for g in granules
        ],
    )
    return len(granules)

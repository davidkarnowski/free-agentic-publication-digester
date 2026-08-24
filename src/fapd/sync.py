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
import re

from . import config
from .client import BudgetExceededError, RateLimitFloorError

logger = logging.getLogger("fapd.sync")

# Package-level download preference. XML is what Phase 2 parses; ZIP is the
# fallback for collections (like CREC) whose package-level content is only
# offered zipped; PDF is last resort, kept for archive completeness only.
_FORMAT_PREFERENCE = (("xmlLink", "xml"), ("zipLink", "zip"), ("pdfLink", "pdf"))
# USCOURTS case packages: the ZIP bundles opinion PDFs + mods.xml case
# metadata in one request — preferred over the bare PDF.
_FORMAT_PREFERENCE_BY_COLLECTION = {
    "USCOURTS": (("zipLink", "zip"), ("pdfLink", "pdf")),
    # PLAW offers USLM XML (no plain xmlLink); text as last-resort parse.
    "PLAW": (("uslmLink", "xml"), ("txtLink", "txt"), ("pdfLink", "pdf")),
}

# Collections whose packages have granules worth inventorying (docs/schema.md).
_GRANULE_COLLECTIONS = {"CREC", "FR"}

# Collections whose XML can flag graphics (GUIDE §5/§6: graphics are content;
# their pixels live only in the PDF, so flagged packages get a companion PDF).
_GRAPHICS_COLLECTIONS = {"FR"}

# FR graphic GIDs follow a section-coded pattern (e.g. EN23JY26.004) for
# document content — equations, forms, maps, annex pages. Non-conforming GIDs
# (e.g. Trump.EPS) are signatures/seals: boilerplate, never worth a PDF fetch,
# a vision pass, or an embed (rule FR-GPH-01; GUIDE §6).
_GID_RE = re.compile(rb"<GID>\s*([^<]*?)\s*</GID>")
_SUBSTANTIVE_GID_RE = re.compile(rb"^E[A-Z]\d{2}[A-Z]{2}\d{2}\.\d+$")


def utc_now_iso():
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def publication_date(when=None):
    """The federal publication day (GUIDE §3, amended 2026-07-30): the
    calendar date in Washington, D.C., because that is the clock the
    publishers keep — the Federal Register's 8:45 a.m. release, floor
    proceedings, opinion postings. Midnight UTC is 8 p.m. Eastern, so
    dating by UTC filed an evening release under the next publication
    day and rolled the live view over while Washington was still
    working. Observation timestamps stay UTC; only the day a document
    belongs to is Eastern. DST is handled by the zone itself."""
    when = when or dt.datetime.now(dt.UTC)
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt.UTC)
    return when.astimezone(config.PUBLICATION_TZ).strftime("%Y-%m-%d")


def publication_date_of(iso_stamp):
    """Publication day for a stored UTC stamp ('...Z' or offset form).
    Returns None when the stamp is unparseable — callers fall back to
    the current publication day rather than inventing one."""
    if not iso_stamp:
        return None
    try:
        return publication_date(dt.datetime.fromisoformat(iso_stamp))
    except ValueError:
        return None


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
    _apply_fetch_policy(conn, collection, stats)
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
    now = utc_now_iso()
    # GUIDE §3 (amended 2026-08-06): the digest-filing day. Observation
    # policy files under the Eastern day of THIS first sight; cover
    # policy files under the document's own date. digest_day is absent
    # from the DO UPDATE clause on purpose — write-once, so a revision
    # re-fetch never re-files a document into a later digest.
    policy = config.FILING_POLICY.get(collection, config.FILING_DEFAULT)
    if policy == "cover":
        digest_day = pkg.get("dateIssued") or publication_date_of(now)
    else:
        digest_day = publication_date_of(now)
    conn.execute(
        """
        INSERT INTO packages (package_id, collection, last_modified, title, package_link,
                              date_issued, first_seen_at, digest_day)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(package_id) DO UPDATE SET
            fetch_status  = CASE WHEN excluded.last_modified > packages.last_modified
                                 THEN 'pending' ELSE packages.fetch_status END,
            -- A content revision is a new problem, not a continuation of an
            -- old retry ceiling (GUIDE §4, amended 2026-08-10) -- reset in
            -- lockstep with the fetch_status flip above, never unconditionally
            -- (this runs on every listing pass, not just on revisions).
            fetch_attempts  = CASE WHEN excluded.last_modified > packages.last_modified
                                   THEN 0 ELSE packages.fetch_attempts END,
            last_attempt_at = CASE WHEN excluded.last_modified > packages.last_modified
                                   THEN NULL ELSE packages.last_attempt_at END,
            -- The extraction ceiling (2026-08-24) follows the same rule:
            -- new content, fresh ladder.
            extract_attempts = CASE WHEN excluded.last_modified > packages.last_modified
                                    THEN 0 ELSE packages.extract_attempts END,
            extract_error    = CASE WHEN excluded.last_modified > packages.last_modified
                                    THEN NULL ELSE packages.extract_error END,
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
            now,
            digest_day,
        ),
    )


def _apply_fetch_policy(conn, collection, stats):
    """Named per-collection fetch policies (GUIDE §4 'skipped': listed for
    the record, deliberately not archived, always disclosed)."""
    if collection != "USCOURTS":
        return
    cutoff = (
        dt.datetime.now(dt.UTC)
        - dt.timedelta(days=config.USCOURTS_FETCH_WINDOW_DAYS)
    ).strftime("%Y-%m-%d")
    cur = conn.execute(
        "UPDATE packages SET fetch_status = 'skipped',"
        " last_error = 'USCOURTS-FETCH-01: outside archive window'"
        " WHERE collection = 'USCOURTS' AND fetch_status = 'pending'"
        " AND (date_issued IS NULL OR date_issued < ?)",
        (cutoff,),
    )
    conn.commit()
    if cur.rowcount:
        stats["policy_skipped"] = cur.rowcount
        logger.info(
            "USCOURTS: %d package(s) outside the %d-day archive window marked"
            " skipped (rule USCOURTS-FETCH-01)",
            cur.rowcount, config.USCOURTS_FETCH_WINDOW_DAYS,
        )


def _download_pending(client, conn, collection, stats, max_downloads):
    # Newest first: digest-relevant days get covered before the queue tail.
    rows = conn.execute(
        "SELECT package_id FROM packages WHERE collection = ?"
        " AND fetch_status IN ('pending', 'failed')"
        " ORDER BY date_issued DESC, package_id",
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
            # GUIDE §4, amended 2026-08-10: a per-package retry ceiling.
            # Without this, a permanently-failing package re-entered this
            # same query every cycle forever (the identical bug shape rule
            # 14/MAX_ITEM_SUMMARY_ATTEMPTS already fixes for the LLM
            # layer) -- distinct from govinfo's per-call retry/backoff
            # (client.py), which already ran to exhaustion before this
            # exception was ever raised.
            row = conn.execute(
                "SELECT fetch_attempts FROM packages WHERE package_id = ?", (pid,)
            ).fetchone()
            attempts = (row["fetch_attempts"] or 0) + 1
            status = ("exhausted" if attempts >= config.MAX_PACKAGE_FETCH_ATTEMPTS
                     else "failed")
            conn.execute(
                "UPDATE packages SET fetch_status = ?, last_error = ?,"
                " fetch_attempts = ?, last_attempt_at = ? WHERE package_id = ?",
                (status, repr(exc)[:500], attempts, utc_now_iso(), pid),
            )
            conn.commit()
            stats["failed"] += 1
            if status == "exhausted":
                stats["exhausted"] = stats.get("exhausted", 0) + 1
            logger.warning(
                "%s: download failed (%d/%d attempts), marked %r: %r",
                pid, attempts, config.MAX_PACKAGE_FETCH_ATTEMPTS, status, exc,
            )


def _download_package(client, conn, collection, package_id):
    summary = client.get_json(f"packages/{package_id}/summary")
    date_issued = summary.get("dateIssued")
    links = summary.get("download") or {}
    url, fmt = None, None
    preference = _FORMAT_PREFERENCE_BY_COLLECTION.get(collection, _FORMAT_PREFERENCE)
    for key, ext in preference:
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

    if collection in _GRAPHICS_COLLECTIONS and fmt == "xml":
        _maybe_fetch_graphics_pdf(client, package_id, resp.content, links, raw_dir)

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
        " fetched_last_modified = last_modified, last_error = NULL,"
        " fetch_attempts = 0, last_attempt_at = NULL,"
        " extract_attempts = 0, extract_error = NULL"
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


def classify_graphics(xml_bytes):
    """Split a document's flagged graphics into content vs boilerplate.

    Returns (substantive, boilerplate) counts. Substantive = GID matches the
    FR section-coded naming pattern (equations, forms, maps, annex pages);
    boilerplate = anything else (signatures, seals — rule FR-GPH-01).
    """
    substantive = boilerplate = 0
    for gid in _GID_RE.findall(xml_bytes):
        if _SUBSTANTIVE_GID_RE.match(gid):
            substantive += 1
        else:
            boilerplate += 1
    return substantive, boilerplate


def _maybe_fetch_graphics_pdf(client, package_id, xml_bytes, links, raw_dir):
    """Archive the companion PDF only when the XML flags *substantive*
    graphics — signature/seal-only documents never cost a PDF fetch."""
    substantive, boilerplate = classify_graphics(xml_bytes)
    if not substantive:
        if boilerplate:
            logger.info(
                "%s: %d graphic(s) are boilerplate only (FR-GPH-01) — no PDF fetched",
                package_id, boilerplate,
            )
        return
    pdf_url = links.get("pdfLink")
    if not pdf_url:
        logger.warning(
            "%s: %d substantive graphic(s) but no pdfLink offered", package_id, substantive
        )
        return
    pdf_path = raw_dir / f"{package_id}.pdf"
    if pdf_path.exists():
        logger.debug("%s: companion PDF already on disk", package_id)
        return
    pdf_resp = client.get(pdf_url)
    pdf_path.write_bytes(pdf_resp.content)
    logger.info(
        "%s: %d substantive graphic(s) (+%d boilerplate excluded by FR-GPH-01)"
        " — archived companion PDF (%d B)",
        package_id, substantive, boilerplate, len(pdf_resp.content),
    )


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

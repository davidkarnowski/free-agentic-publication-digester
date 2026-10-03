"""Delta sync: govinfo collections service -> metadata store -> raw archive.

Implements the algorithm in docs/schema.md (`sync_state` section):
list changed packages since the watermark, upsert idempotently, download
what's pending, and advance the watermark only after the listing completed.
The watermark is always a server-side lastModified value, never our clock.
A first sync (no watermark row) is date-bounded to INITIAL_SYNC_LOOKBACK_DAYS
per GUIDE.md §4.

The download pass rotates (GUIDE §4, amended 2026-10-03): a package the
server says is not ready is set aside while the rest of the queue is
served, and revisited afterwards, never sooner than the server asked. See
`_download_pending`.
"""

import datetime as dt
import heapq
import itertools
import logging
import re

from . import config
from .client import (
    BudgetExceededError,
    RateLimitFloorError,
    RetryLaterError,
    redact_secrets,
)

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


def publication_date(when=None, tz=None):
    """The publication day (GUIDE §3, amended 2026-07-30): the calendar
    date on the publication clock (`config.PUBLICATION_TZ`, Washington's
    in production), because that is the clock the publishers keep — the
    Federal Register's 8:45 a.m. release, floor proceedings, opinion
    postings. Midnight UTC is 8 p.m. Eastern, so dating by UTC filed an
    evening release under the next publication day and rolled the live
    view over while Washington was still working. Observation timestamps
    stay UTC; only the day a document belongs to is on the publication
    clock. DST is handled by the zone itself. `tz` is the test seam; the
    default is read at call time so a replaced config attribute holds."""
    when = when or dt.datetime.now(dt.UTC)
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt.UTC)
    return when.astimezone(tz or config.PUBLICATION_TZ).strftime("%Y-%m-%d")


def publication_day_hour(iso_stamp, tz=None):
    """(publication day, wall-clock hour 0-23) for a stored UTC stamp —
    the ONE conversion GUIDE §3 (2026-08-26) licenses: presentation
    bucketing of activity on the publication clock, never storage or
    dating. A stamp with no zone is UTC, as every writer stores it.
    Returns None for an unparseable stamp so a caller drops the row
    rather than inventing a bucket. On the night the zone falls back,
    two UTC hours land in one wall-clock hour; on the night it springs
    forward, one wall-clock hour receives nothing — see
    `publication_day_hours` for the day's honest hour count."""
    if not iso_stamp:
        return None
    try:
        when = dt.datetime.fromisoformat(iso_stamp)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt.UTC)
    local = when.astimezone(tz or config.PUBLICATION_TZ)
    return local.strftime("%Y-%m-%d"), local.hour


def publication_day_start_utc(day, tz=None):
    """The UTC instant at which publication day `day` ('YYYY-MM-DD')
    begins, in the exact stamp format the pipeline's writers use
    (`utc_now_iso`: ...Z) so it can bound a query against stored stamps
    as a string (CLAUDE.md §10: never introduce a new timestamp format)."""
    local_midnight = dt.datetime.combine(
        dt.date.fromisoformat(day), dt.time(0), tzinfo=tz or config.PUBLICATION_TZ)
    return local_midnight.astimezone(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def publication_day_hours(day, tz=None):
    """How many wall-clock hours publication day `day` holds: 24, or 23
    and 25 on the zone's two shift nights — the number a graph states
    beside a DST day instead of silently normalizing it."""
    zone = tz or config.PUBLICATION_TZ
    start = dt.datetime.combine(dt.date.fromisoformat(day), dt.time(0), tzinfo=zone)
    end = dt.datetime.combine(dt.date.fromisoformat(day) + dt.timedelta(days=1),
                              dt.time(0), tzinfo=zone)
    return round((end.astimezone(dt.UTC) - start.astimezone(dt.UTC)).total_seconds() / 3600)


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


class _Queued:
    """One package's place in a single download pass."""

    __slots__ = ("error", "not_before", "package_id", "plan", "prior", "tries")

    def __init__(self, package_id, prior):
        self.package_id = package_id
        self.prior = prior        # failed cycles before this one
        self.plan = None          # the summary's answer; asked for once
        self.tries = 0            # content requests made this cycle
        self.not_before = 0.0     # client clock: earliest permitted return
        self.error = None         # the last "not ready" answer

    @property
    def second_chance(self):
        """True once the package has been turned down before, this cycle
        or an earlier one. Only second chances say anything about whether
        the source is available: a first try that is not ready is the
        publisher building a file, which is ordinary."""
        return bool(self.prior or self.tries)


def _download_pending(client, conn, collection, stats, max_downloads):
    """Download what is queued, without letting a package the server is
    not ready to serve hold up the ones it is (GUIDE §4, amended
    2026-10-03).

    The pass has two halves. The first tries every queued package once,
    in order: never-failed packages first, then by fewest failed cycles,
    newest first within each. A "not ready" answer (503 with Retry-After,
    a 429, another 5xx, or no connection) sets the package aside and the
    pass moves on. The second half revisits what was set aside, earliest
    permitted return first, and waits only when nothing else is left to
    do — never returning sooner than the server asked, and never waiting
    longer than `config.MAX_RETRY_WAIT_SECONDS` for it.

    Two bounds keep an outage cheap for the publisher. A package gets at
    most `config.GOVINFO_DOWNLOAD_TRIES_PER_CYCLE` tries a cycle. And
    when `config.SOURCE_UNAVAILABLE_STREAK` second chances in a row are
    turned down, the source is treated as unavailable for this cycle:
    packages that already failed an earlier cycle are no longer tried or
    revisited, and stay queued for the next one. A package new to this
    cycle is never skipped for that reason — a new document always gets
    its tries.

    What a cycle costs a package is unchanged: one failed cycle counts
    once toward `config.MAX_PACKAGE_FETCH_ATTEMPTS`, however many tries
    it took. A package the pass never reached is not charged at all."""
    # Fewest failed cycles first: a document nobody has asked for yet is
    # never queued behind one that keeps failing, and when the source is
    # down the probes rotate through the stuck set instead of hammering
    # the same few. Newest first within a tier, as before.
    rows = conn.execute(
        "SELECT package_id, COALESCE(fetch_attempts, 0) AS prior FROM packages"
        " WHERE collection = ? AND fetch_status IN ('pending', 'failed')"
        " ORDER BY COALESCE(fetch_attempts, 0), date_issued DESC, package_id",
        (collection,),
    ).fetchall()
    capped = rows if max_downloads is None else rows[: max_downloads - stats["downloaded"]]
    if len(capped) < len(rows):
        logger.info(
            "%s: download cap %s limits this run to %d of %d queued; the rest stay pending",
            collection, max_downloads, len(capped), len(rows),
        )

    waiting = []                  # heap of (not_before, order, _Queued)
    order = itertools.count()     # heap tie-break: first set aside, first back
    set_aside = 0                 # packages told "not ready" at least once
    arrived_late = 0              # of those, fetched on a later try
    streak = 0                    # second chances in a row turned down

    def attempt(item):
        """One try at one package: 'fetched', 'not_ready' or 'failed'."""
        nonlocal set_aside, arrived_late
        try:
            if item.plan is None:
                item.plan = _plan_download(client, collection, item.package_id)
            item.tries += 1
            _fetch_planned(client, conn, collection, item.package_id,
                           item.plan, item.tries)
        except RetryLaterError as exc:
            item.error = exc
            if item.tries == 1:
                set_aside += 1
            if item.tries >= config.GOVINFO_DOWNLOAD_TRIES_PER_CYCLE:
                _record_failed_cycle(conn, item.package_id, exc, stats)
                return "not_ready"
            item.not_before = client.monotonic() + exc.retry_after
            heapq.heappush(waiting, (item.not_before, next(order), item))
            logger.debug(
                "%s: not ready (try %d) — set aside for %.0fs, the queue continues",
                item.package_id, item.tries, exc.retry_after)
            return "not_ready"
        except (BudgetExceededError, RateLimitFloorError):
            # Budget/rate-floor: stop the whole run, leave the queue pending.
            conn.rollback()
            logger.error(
                "%s: run aborted by client halt after %d download(s); queue preserved",
                collection, stats["downloaded"],
            )
            raise
        except Exception as exc:  # noqa: BLE001 — one bad package must not kill the run
            _record_failed_cycle(conn, item.package_id, exc, stats)
            return "failed"
        stats["downloaded"] += 1
        if item.tries > 1:
            arrived_late += 1
        return "fetched"

    def after(streak, was_second_chance, outcome):
        if outcome == "fetched":
            return 0
        if outcome == "not_ready" and was_second_chance:
            return streak + 1
        return streak

    limit = config.SOURCE_UNAVAILABLE_STREAK
    reached = 0
    for row in capped:                                    # the first half
        item = _Queued(row["package_id"], row["prior"])
        if item.prior and streak >= limit:
            # Everything from here on failed an earlier cycle (the order
            # above), and the source has just turned down `limit` second
            # chances in a row. Stop asking; none of these is charged.
            break
        reached += 1
        chance = item.second_chance
        streak = after(streak, chance, attempt(item))
    not_tried = len(capped) - reached

    not_revisited = 0
    while waiting:                                        # the second half
        _, _, item = heapq.heappop(waiting)
        if item.prior and streak >= limit:
            # Tried this cycle and turned down: that is a failed cycle.
            _record_failed_cycle(conn, item.package_id, item.error, stats)
            not_revisited += 1
            continue
        remaining = item.not_before - client.monotonic()
        if remaining > config.MAX_RETRY_WAIT_SECONDS:
            # The server asked for longer than a cycle holds a worker.
            # Not asking again this cycle is how that request is honored.
            _record_failed_cycle(conn, item.package_id, item.error, stats)
            continue
        client.wait(remaining)   # only now is nothing else left to do
        streak = after(streak, True, attempt(item))

    if not_tried or not_revisited:
        stats["source_unavailable"] = True
        logger.warning(
            "%s: %d second chances in a row were turned down — treating the"
            " source as unavailable for this cycle; %d package(s) that failed"
            " an earlier cycle were not tried and %d were not revisited, all"
            " still queued",
            collection, limit, not_tried, not_revisited,
        )
    if set_aside:
        stats["not_ready"] = set_aside
        logger.info(
            "%s: %d package(s) were not ready on the first try and were set"
            " aside while the queue continued; %d arrived on a later try",
            collection, set_aside, arrived_late,
        )


def _record_failed_cycle(conn, package_id, exc, stats):
    """A package ends this cycle unfetched: count the cycle once.

    GUIDE §4, amended 2026-08-10: a per-package retry ceiling. Without
    it, a permanently-failing package re-entered the download query every
    cycle forever (the identical bug shape rule 14 /
    MAX_ITEM_SUMMARY_ATTEMPTS already fixes for the LLM layer). The count
    is of cycles, not of requests: three tries in one cycle are one
    failed cycle, exactly as five tries in the old in-place ladder were."""
    row = conn.execute(
        "SELECT fetch_attempts FROM packages WHERE package_id = ?", (package_id,)
    ).fetchone()
    attempts = (row["fetch_attempts"] or 0) + 1
    status = ("exhausted" if attempts >= config.MAX_PACKAGE_FETCH_ATTEMPTS
              else "failed")
    conn.execute(
        "UPDATE packages SET fetch_status = ?, last_error = ?,"
        " fetch_attempts = ?, last_attempt_at = ? WHERE package_id = ?",
        (status, redact_secrets(repr(exc))[:500], attempts, utc_now_iso(), package_id),
    )
    conn.commit()
    stats["failed"] += 1
    if status == "exhausted":
        stats["exhausted"] = stats.get("exhausted", 0) + 1
    logger.warning(
        "%s: download failed (%d/%d attempts), marked %r: %r",
        package_id, attempts, config.MAX_PACKAGE_FETCH_ATTEMPTS, status, exc,
    )


def _plan_download(client, collection, package_id):
    """Ask the package's summary which file to fetch. This is everything
    a download needs that does not have to be asked again when the file
    itself is not ready yet: a revisit repeats one request, not two."""
    summary = client.get_json(f"packages/{package_id}/summary")
    links = summary.get("download") or {}
    preference = _FORMAT_PREFERENCE_BY_COLLECTION.get(collection, _FORMAT_PREFERENCE)
    for key, ext in preference:
        if links.get(key):
            return {"summary": summary, "links": links, "url": links[key], "fmt": ext}
    raise ValueError(f"no downloadable format among {sorted(links)}")


def _fetch_planned(client, conn, collection, package_id, plan, attempt_no):
    """Fetch and store one planned download. The content request is made
    once; a "not ready" answer surfaces as RetryLaterError for
    `_download_pending` to schedule (GUIDE §4, amended 2026-10-03)."""
    summary, links = plan["summary"], plan["links"]
    url, fmt = plan["url"], plan["fmt"]
    date_issued = summary.get("dateIssued")

    resp = client.get(url, defer_retry=True, attempt_no=attempt_no)
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

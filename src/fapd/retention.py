"""Raw-download retention (GUIDE §5, amended 2026-11-03).

A raw package file is a working cache: extraction reads it once, and every
published surface is built from the database, the committed evidence and the
captures. A file is pruned when its package

  - was fetched more than ``config.RAW_RETENTION_DAYS`` days ago, and
  - has extracted text written at or after that fetch, at the current
    ``extract.EXTRACTOR_VERSION`` (so nothing pending is ever deleted).

Before a file is deleted its sha256 and size are recorded on the row if the
download did not already record them (rows fetched before 2026-11-03), and
``raw_pruned_at`` is set. A row whose file is already missing (the one-time
prune of 2026-11-03, whose fingerprints are in that prune's manifest) is
marked pruned without a hash. Each call deletes at most
``config.RAW_PRUNE_MAX_PER_CYCLE`` files; the collector calls it once per
govinfo cycle, so a backlog drains over a few cycles and a normal day's
work is a few hundred files. No request is made and no row's other columns
change.
"""

import datetime as dt
import hashlib
import logging

from . import config
from .sync import utc_now_iso

logger = logging.getLogger("fapd.retention")


def _cutoff(now, days):
    return (now - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")


def eligible(conn, *, now=None, days=None):
    """Rows whose raw file may be pruned, oldest fetch first."""
    from .extract import EXTRACTOR_VERSION

    now = now or dt.datetime.now(dt.UTC)
    days = config.RAW_RETENTION_DAYS if days is None else days
    return conn.execute(
        """
        SELECT p.package_id, p.raw_path, p.raw_sha256, p.fetched_at
        FROM packages p
        JOIN (
            SELECT package_id, MAX(extracted_at) AS extracted_at,
                   MIN(extractor_version) AS min_version
            FROM extracted_texts GROUP BY package_id
        ) e USING (package_id)
        WHERE p.fetch_status = 'fetched'
          AND p.raw_path IS NOT NULL
          AND p.raw_pruned_at IS NULL
          AND p.fetched_at IS NOT NULL
          AND substr(p.fetched_at, 1, 19) < ?
          AND substr(e.extracted_at, 1, 19) >= substr(p.fetched_at, 1, 19)
          AND e.min_version >= ?
        ORDER BY p.fetched_at
        """,
        (_cutoff(now, days), EXTRACTOR_VERSION),
    ).fetchall()


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prune_raw(conn, *, now=None, days=None, max_files=None):
    """Prune eligible raw files. Returns counts for the cycle's stats."""
    max_files = config.RAW_PRUNE_MAX_PER_CYCLE if max_files is None else max_files
    stats = {"pruned": 0, "bytes": 0, "already_gone": 0}
    stamp = utc_now_iso()
    for row in eligible(conn, now=now, days=days):
        path = config.PROJECT_ROOT / row["raw_path"]
        siblings = [p for p in (path.with_suffix(".pdf"),) if p != path]
        if not path.exists():
            conn.execute("UPDATE packages SET raw_pruned_at = ? WHERE package_id = ?",
                         (stamp, row["package_id"]))
            stats["already_gone"] += 1
            continue
        if stats["pruned"] >= max_files:
            continue
        size = path.stat().st_size
        sha = row["raw_sha256"] or _sha256(path)
        conn.execute(
            "UPDATE packages SET raw_sha256 = ?, raw_bytes = COALESCE(raw_bytes, ?),"
            " raw_pruned_at = ? WHERE package_id = ?",
            (sha, size, stamp, row["package_id"]))
        conn.commit()          # the fingerprint is durable before the file goes
        path.unlink(missing_ok=True)
        for extra in siblings:
            if extra.exists():
                size += extra.stat().st_size
                extra.unlink()
        stats["pruned"] += 1
        stats["bytes"] += size
    conn.commit()
    if stats["pruned"] or stats["already_gone"]:
        logger.info("raw retention: pruned %d files (%.1f MB), marked %d already gone",
                    stats["pruned"], stats["bytes"] / 1e6, stats["already_gone"])
    return stats

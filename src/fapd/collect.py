"""Continuous-ingestion collector core (GUIDE §4/§5/§6 rule 12, amended
2026-07-30; design authority: docs/continuous-ingestion.md).

This module contains the journal reconciliation, the analyze trigger
predicates, the /today data contract, and collector-state bookkeeping —
plus the Supervisor/worker loop (docs §2). Collectors call only the
existing collection functions; nothing here fetches, parses, or prompts
on its own. **There is deliberately no compose call anywhere in this
module** (§6 rule 12: day/section composition is end-of-day only).
"""

import datetime as dt
import json
import logging

from . import config
from .sync import utc_now_iso

logger = logging.getLogger("fapd.collect")

# ---------------------------------------------------------------------------
# Journal reconciliation (docs/continuous-ingestion.md §3)
# ---------------------------------------------------------------------------

# Class predicates over extracted_texts rows. Agency and email items share
# the AGENCYPR collection; the channel lives in item metadata.
_CLASS_WHERE = {
    "govinfo": "e.collection != 'AGENCYPR'",
    "agency": ("e.collection = 'AGENCYPR' AND COALESCE("
               "json_extract(e.metadata, '$.channel'), '') != 'email'"),
    "email": ("e.collection = 'AGENCYPR' AND "
              "json_extract(e.metadata, '$.channel') = 'email'"),
}


def journal_new(conn, source_class, cycle_id):
    """Insert 'ingested' journal rows for items of one class not yet
    journaled. Reconciliation by observation — zero changes to the
    collection functions. Returns rows inserted."""
    where = _CLASS_WHERE[source_class]
    cur = conn.execute(
        f"""
        INSERT INTO item_journal (observed_at, source_class, package_id,
            granule_id, collection, source_id, digest_date, event, cycle_id)
        SELECT COALESCE(e.extracted_at, ?), ?, e.package_id, e.granule_id,
               e.collection, json_extract(e.metadata, '$.source_id'),
               p.date_issued, 'ingested', ?
        FROM extracted_texts e JOIN packages p USING (package_id)
        WHERE {where}
          AND NOT EXISTS (SELECT 1 FROM item_journal j
                          WHERE j.package_id = e.package_id
                            AND j.granule_id = e.granule_id
                            AND j.event = 'ingested')
        """,
        (utc_now_iso(), source_class, cycle_id),
    )
    conn.commit()
    if cur.rowcount:
        logger.info("journal: %d new %s item(s) [cycle %s]",
                    cur.rowcount, source_class, cycle_id)
    return cur.rowcount


def journal_model_events(conn, cycle_id):
    """Insert 'summarized'/'plain' journal rows for model outputs not yet
    journaled (fired after an analyze cycle). Returns total inserted."""
    total = 0
    for event, table, version_col, version in (
        ("summarized", "summaries", "prompt_version", config.PROMPT_VERSION),
        ("plain", "plain_summaries", "plain_version", config.PLAIN_PROMPT_VERSION),
    ):
        cur = conn.execute(
            f"""
            INSERT INTO item_journal (observed_at, source_class, package_id,
                granule_id, collection, source_id, digest_date, event, cycle_id)
            SELECT s.created_at, COALESCE(ij.source_class, 'govinfo'),
                   s.package_id, s.granule_id, ij.collection, ij.source_id,
                   ij.digest_date, ?, ?
            FROM {table} s
            LEFT JOIN item_journal ij ON ij.package_id = s.package_id
                 AND ij.granule_id = s.granule_id AND ij.event = 'ingested'
            WHERE s.{version_col} = ?
              AND NOT EXISTS (SELECT 1 FROM item_journal j
                              WHERE j.package_id = s.package_id
                                AND j.granule_id = s.granule_id
                                AND j.event = ?)
            """,
            (event, cycle_id, version, event),
        )
        total += cur.rowcount
    conn.commit()
    return total


# ---------------------------------------------------------------------------
# Analyze trigger (docs §4 — batch-threshold-or-age, spaced)
# ---------------------------------------------------------------------------


def _minutes_since(iso_ts, now=None):
    now = now or dt.datetime.now(dt.UTC)
    then = dt.datetime.fromisoformat(iso_ts)  # 3.12: parses trailing 'Z'
    if then.tzinfo is None:
        then = then.replace(tzinfo=dt.UTC)
    return (now - then).total_seconds() / 60.0


def pending_map_items(conn, date):
    """Selected items on `date` with no summary row at the current prompt
    version — what an analyze cycle would actually pay for."""
    from . import rules  # deferred: rules pulls nothing heavy, but keep parity

    selected = rules.select_items(conn, date)
    pending = []
    for item in selected:
        row = conn.execute(
            "SELECT 1 FROM summaries WHERE package_id = ? AND granule_id = ?"
            " AND prompt_version = ?",
            (item["package_id"], item["granule_id"], config.PROMPT_VERSION),
        ).fetchone()
        if not row:
            pending.append(item)
    return pending


def trigger_fires(conn, date, *, now=None):
    """True when the model layers should run for `date` (docs §4):
    a full batch pending, or the oldest pending item past the latency
    bound — and at least ANALYZE_MIN_INTERVAL_MIN since the last analyze
    cycle."""
    last = conn.execute(
        "SELECT last_cycle_at FROM collector_state WHERE worker = 'analyze'"
    ).fetchone()
    if last and last["last_cycle_at"] and (
        _minutes_since(last["last_cycle_at"], now) < config.ANALYZE_MIN_INTERVAL_MIN
    ):
        return False

    pending = pending_map_items(conn, date)
    if not pending:
        return False
    if len(pending) >= 6:  # analyze.MAX_BATCH_ITEMS; import avoided (heavy module)
        return True
    oldest = conn.execute(
        """
        SELECT MIN(e.extracted_at) AS oldest FROM extracted_texts e
        JOIN packages p USING (package_id) WHERE p.date_issued = ?
        """,
        (date,),
    ).fetchone()
    return bool(
        oldest and oldest["oldest"]
        and _minutes_since(oldest["oldest"], now) >= config.ANALYZE_MAX_LATENCY_MIN
    )


def dates_with_pending(conn):
    """Digest dates that have journaled items newer than their model
    coverage — candidates for an analyze cycle (newest first)."""
    return [r["digest_date"] for r in conn.execute(
        """
        SELECT DISTINCT digest_date FROM item_journal
        WHERE event = 'ingested' AND digest_date IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM item_journal j2
                          WHERE j2.package_id = item_journal.package_id
                            AND j2.granule_id = item_journal.granule_id
                            AND j2.event = 'summarized')
        ORDER BY digest_date DESC
        """
    )]


# ---------------------------------------------------------------------------
# /today data contract (docs §8 — consumed by build_today, next push)
# ---------------------------------------------------------------------------


def today_status(conn, date):
    """Everything the /today renderer needs, mechanically (zero LLM)."""
    items = [dict(r) for r in conn.execute(
        """
        SELECT j.observed_at, j.source_class, j.package_id, j.granule_id,
               j.collection, j.source_id, e.doc_type, e.title,
               s.summary, s.method AS summary_method
        FROM item_journal j
        LEFT JOIN extracted_texts e USING (package_id, granule_id)
        LEFT JOIN summaries s ON s.package_id = j.package_id
             AND s.granule_id = j.granule_id AND s.prompt_version = ?
        WHERE j.digest_date = ? AND j.event = 'ingested'
        ORDER BY j.observed_at, j.package_id, j.granule_id
        """,
        (config.PROMPT_VERSION, date),
    )]
    counts = {}
    for item in items:
        key = f"{item['collection'] or '?'}/{item['doc_type'] or '?'}"
        counts[key] = counts.get(key, 0) + 1
    return {
        "date": date,
        "items": items,
        "counts": counts,
        "pending_llm": len(pending_map_items(conn, date)),
        "last_observed_at": max((i["observed_at"] for i in items), default=None),
    }


# ---------------------------------------------------------------------------
# Collector state (health surface)
# ---------------------------------------------------------------------------


def record_state(conn, worker, *, ok, stats=None, error=None):
    now = utc_now_iso()
    conn.execute(
        """
        INSERT INTO collector_state (worker, last_cycle_at, last_ok_at,
            last_result, consecutive_errors)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (worker) DO UPDATE SET
            last_cycle_at = excluded.last_cycle_at,
            last_ok_at = COALESCE(excluded.last_ok_at, last_ok_at),
            last_result = excluded.last_result,
            consecutive_errors = CASE WHEN excluded.consecutive_errors = 0
                                      THEN 0 ELSE consecutive_errors + 1 END
        """,
        (worker, now, now if ok else None,
         json.dumps({"error": error} if error else (stats or {})),
         0 if ok else 1),
    )
    conn.commit()

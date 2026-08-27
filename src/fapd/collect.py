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
import functools
import json
import logging
import random
import threading
import uuid

from . import config, health
from .client import BudgetExceededError
from .sync import publication_date, utc_now_iso

logger = logging.getLogger("fapd.collect")

# ---------------------------------------------------------------------------
# Journal reconciliation (docs/continuous-ingestion.md §3)
# ---------------------------------------------------------------------------

# Class predicates over extracted_texts rows. Agency and email items share
# the AGENCYPR collection; the channel lives in item metadata. VOTES and
# BILLACTIONS ride the same web poll loop (xml-index and api adapters,
# GUIDE §3 recorded votes / bill actions) but under their own collection
# codes, so they are agency-CLASS work — the worker and the budget — while
# never being agency CONTENT.
# Collections produced by the agency-class web pollers (AgencyHostWorker),
# as opposed to the govinfo sync. Derived from the adapters themselves so
# a new collection cannot be forgotten here: agencies.ADAPTERS is the one
# place a COLLECTION is declared, and tests/test_collect.py asserts this
# set matches it. Before 2026-08-06 the govinfo clause was a DENYLIST
# ("NOT IN (...)"), which meant a newly added collection silently fell
# into whichever class polled first — PRESACT was ingested 60 times and
# journaled zero times, so the White House's executive orders reached
# the corpus and never reached /today, the day views, or the journal
# accounting. A denylist cannot fail loudly; this set can.
_AGENCY_CLASS_COLLECTIONS = ("AGENCYPR", "VOTES", "BILLACTIONS", "PRESACT")
_AGENCY_IN = ", ".join(f"'{c}'" for c in _AGENCY_CLASS_COLLECTIONS)
# Only AGENCYPR carries an email channel; every other agency-class
# collection is web-polled, so the channel test applies to it alone.
_CLASS_WHERE = {
    "govinfo": f"e.collection NOT IN ({_AGENCY_IN})",
    "agency": (f"(e.collection IN ({_AGENCY_IN})"
               " AND COALESCE(json_extract(e.metadata, '$.channel'), '')"
               " != 'email')"),
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
               COALESCE(p.digest_day, p.date_issued), 'ingested', ?
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
        if row:
            continue
        # An item we have already failed on N times is not pending work,
        # it is a disclosed gap (GUIDE §6 r14). Without this the ladder
        # re-ran every 15 minutes forever at ~29K input tokens a retry.
        spent = conn.execute(
            "SELECT attempts FROM summary_attempts WHERE package_id = ?"
            " AND granule_id = ? AND prompt_version = ? AND layer = 'map'",
            (item["package_id"], item["granule_id"], config.PROMPT_VERSION),
        ).fetchone()
        if spent and spent[0] >= config.MAX_ITEM_SUMMARY_ATTEMPTS:
            continue
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
        JOIN packages p USING (package_id) WHERE p.digest_day = ?
        """,
        (date,),
    ).fetchone()
    return bool(
        oldest and oldest["oldest"]
        and _minutes_since(oldest["oldest"], now) >= config.ANALYZE_MAX_LATENCY_MIN
    )


def dates_with_pending(conn, max_age_days=None):
    """Digest dates that have journaled items newer than their model
    coverage — candidates for an analyze cycle (newest first).

    Bounded to the last `max_age_days + 1` publication days
    (config.ANALYZE_MAX_AGE_DAYS by default). We do not publish
    post-dated digests, so tokens spent on a day that will never be
    published are taken from the day that will: on 2026-07-30 the worker
    wrote 184 summaries across eleven dates reaching back to 2024-06-18
    while the digest day itself received none. Older pending items stay
    pending and are disclosed by the coverage accounting rather than
    quietly bought."""
    if max_age_days is None:
        max_age_days = config.ANALYZE_MAX_AGE_DAYS
    floor = (dt.datetime.now(dt.UTC)
             - dt.timedelta(days=max_age_days + 1)).astimezone(
                 config.PUBLICATION_TZ).strftime("%Y-%m-%d")
    return [d for d in _all_dates_with_pending(conn) if d >= floor]


def _all_dates_with_pending(conn):
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
    """Everything the /today renderer needs, mechanically (zero LLM).
    Items are newest-first — the live page reads as arrivals, latest on
    top."""
    items = [dict(r) for r in conn.execute(
        """
        SELECT j.observed_at, j.source_class, j.package_id, j.granule_id,
               j.collection, j.source_id, e.doc_type,
               -- The document's official title, from whichever record
               -- carries it. CREC needs the second arm: every granule's
               -- <title> in the GPO ZIP is the ISSUE's boilerplate
               -- ("Congressional Record, Volume 172 Issue 124 (...)"),
               -- identical across the whole issue, so
               -- parsers.crec._clean_title strips it to nothing and
               -- returns None for the entire collection — 1,836 rows on
               -- 2026-08-07, the only collection with any missing. The
               -- real heading comes from the govinfo granules API and
               -- has been stored in granules.title all along; report.py
               -- section 1 has read it since the beginning. This is the
               -- live page catching up (F-022).
               COALESCE(NULLIF(e.title, ''), NULLIF(g.title, '')) AS title,
               e.agency,
               substr(e.text, 1, 240) AS opening,
               json_extract(e.metadata, '$.url') AS url,
               json_extract(e.metadata, '$.channel') AS channel,
               json_extract(e.metadata, '$.dkim.result') AS dkim_result,
               json_extract(e.metadata, '$.claimed_published_at')
                   AS claimed_published_at,
               s.summary, s.method AS summary_method,
               s.inclusion_rule
        FROM item_journal j
        LEFT JOIN extracted_texts e USING (package_id, granule_id)
        LEFT JOIN granules g USING (package_id, granule_id)
        LEFT JOIN summaries s ON s.package_id = j.package_id
             AND s.granule_id = j.granule_id AND s.prompt_version = ?
        WHERE j.digest_date = ? AND j.event = 'ingested'
        ORDER BY j.observed_at DESC, j.package_id, j.granule_id
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


# ---------------------------------------------------------------------------
# Workers and the supervisor (docs §2, §5)
# ---------------------------------------------------------------------------


class Worker:
    """One collector loop: cycle() + interval + error backoff. Each cycle
    opens its own connection (thread- and process-safe under WAL)."""

    name = "worker"
    #: Doubling backoff on consecutive errors (2**n, capped at 8x). The
    #: EOD worker turns this off: its spacing is the finalize ladder
    #: (config.EOD_FINALIZE_RETRY_MINUTES), a policy, not a multiplier —
    #: the multiplier put all three 2026-08-22 attempts before 06:12Z.
    backoff_on_errors = True

    def __init__(self, supervisor, interval_min):
        self.sup = supervisor
        self.base_interval_min = interval_min

    def cycle(self, conn, cycle_id):  # pragma: no cover — abstract
        raise NotImplementedError

    def interval_min(self, conn):
        """Current interval; subclasses apply budget backpressure here."""
        return self.base_interval_min

    def run_cycle(self):
        cycle_id = uuid.uuid4().hex[:12]
        try:
            conn = self.sup.conn_factory()
        except Exception as exc:  # noqa: BLE001 — a connect failure must not
            # kill the worker thread either. Nothing can be recorded without
            # a connection, so the log line is the whole signal; the loop's
            # normal interval brings the next attempt. Before 2026-08-25 this
            # call sat outside the try, and a start-up migration race killed
            # 25 of 29 threads — eod, govinfo, analyze and render among them —
            # silently, with every collector_state row still reading clean.
            logger.error("%s: could not open the database: %r — skipping"
                         " this cycle", self.name, exc)
            return None
        try:
            stats = self.cycle(conn, cycle_id)
            record_state(conn, self.name, ok=True, stats=stats)
            return stats
        except BudgetExceededError as exc:
            # Our own budget refusing us is the policy working, not a
            # failure: the worker is alive and behaving. Recording it as
            # an error inflated the backoff and — once the source-health
            # page started reading consecutive_errors — reported the
            # publisher as degraded because WE were pacing ourselves.
            logger.info("%s: paused by our own budget — %s", self.name, exc)
            record_state(conn, self.name, ok=True,
                         stats={"paused": "budget", "detail": str(exc)})
            return {"paused": "budget"}
        except Exception as exc:  # noqa: BLE001 — a worker failure must not
            # kill the supervisor; the error streak is the health signal.
            logger.warning("%s cycle failed: %r — continuing", self.name, exc)
            record_state(conn, self.name, ok=False, error=repr(exc))
            return None
        finally:
            conn.close()

    def loop(self, stop_event):
        while not stop_event.is_set():
            if self.sup.pause_event.is_set() and self.name != "eod":
                # The EOD finalizer holds the floor (docs §7 serialization);
                # collectors sit out and re-check shortly.
                stop_event.wait(30)
                continue
            # A thread that dies is a worker that stops forever with no
            # health signal (collector_state only records what a cycle
            # wrote). Nothing below may raise past this point.
            try:
                self.run_cycle()
                conn = self.sup.conn_factory()
                try:
                    errors = conn.execute(
                        "SELECT consecutive_errors FROM collector_state WHERE worker = ?",
                        (self.name,)).fetchone()
                    streak = errors["consecutive_errors"] if errors else 0
                    minutes = self.interval_min(conn) * (
                        2 ** min(streak, 3) if self.backoff_on_errors else 1)
                finally:
                    conn.close()
            except Exception as exc:  # noqa: BLE001 — see above
                logger.error("%s: loop iteration failed: %r — retrying after"
                             " the base interval", self.name, exc)
                minutes = self.base_interval_min
            # jitter ±10% so worker clocks don't align into bursts
            stop_event.wait(minutes * 60 * random.uniform(0.9, 1.1))


class GovinfoWorker(Worker):
    name = "govinfo"

    def cycle(self, conn, cycle_id):
        from . import extract, sync

        stats = {}
        with self.sup.govinfo_factory() as client:
            for collection in config.COLLECTIONS:
                s = sync.sync_collection(client, conn, collection, max_downloads=50)
                stats[collection] = {"listed": s["listed"], "downloaded": s["downloaded"]}
        ex = extract.run(conn)
        stats["extracted"] = ex["records"]
        stats["journaled"] = journal_new(conn, "govinfo", cycle_id)
        return stats


class AgencyHostWorker(Worker):
    """One worker per host group — a slow crawl-delay host lives on its
    own clock without delaying anyone (GUIDE §4)."""

    def __init__(self, supervisor, host, entries, interval_min):
        super().__init__(supervisor, interval_min)
        self.name = f"host:{host}"
        self.entries = entries

    def interval_min(self, conn):
        # Budget backpressure (GUIDE §4 amendment): past the threshold
        # fraction of the agency class budget, double the interval — the
        # EOD finalizer's headroom is reserved. The budget lives in
        # fetch_log.db (written by the client itself), not the pipeline DB.
        used = self.sup.agency_requests_today()
        if used >= config.MAX_AGENCY_REQUESTS_PER_DAY * config.BUDGET_BACKPRESSURE_FRACTION:
            return self.base_interval_min * 2
        return self.base_interval_min

    def cycle(self, conn, cycle_id):
        from . import agencies, provenance

        with self.sup.agency_factory() as client, self.sup.wayback_factory() as wayback:
            results = [agencies._poll_isolated(client, wayback, conn, e)
                       for e in self.entries]
        stats = {"new_items": sum(r["new_items"] for r in results),
                 "journaled": journal_new(conn, "agency", cycle_id)}
        if stats["new_items"]:
            provenance.export_manifest(conn)
        return stats


class EmailWorker(Worker):
    name = "email"

    def cycle(self, conn, cycle_id):
        if not (config.IMAP_HOST and config.IMAP_USER and config.IMAP_PASSWORD):
            return {"configured": False}
        entries = [e for e in self.sup.registry()
                   if e["type"] == "email"
                   and e["status"] in ("active", "planned")
                   and e.get("sender")]
        with self.sup.mailbox_factory() as mbox:
            results = self.sup.poll(mbox, conn, entries)
        return {"configured": True,
                "bulletins": sum(r["messages"] for r in results),
                "items": sum(r["items"] for r in results),
                "journaled": journal_new(conn, "email", cycle_id)}


class AnalyzeWorker(Worker):
    """Model layers on trigger. NO compose call exists here (§6 r12)."""

    name = "analyze"

    def cycle(self, conn, cycle_id):
        from . import analyze
        from .llm import ProviderUnavailableError

        stats = {"dates": 0, "summarized": 0, "plain": 0}
        if not self.sup.llm_enabled:
            return stats
        # A finalized day is frozen (GUIDE §5, §6 r15 — no backfill): a
        # summary paid for after the freeze would sit unpublished, the
        # F-013 shape. Rule 13's window still bounds the rest.
        frozen_through = last_finalized_date(conn)
        for date in dates_with_pending(conn):
            if frozen_through and date <= frozen_through:
                continue
            if not trigger_fires(conn, date):
                continue
            try:
                with self.sup.llm_factory() as lclient:
                    a = analyze.run(conn, lclient, date)
                    p = analyze.run_plain(conn, lclient, date)
            except ProviderUnavailableError as exc:
                # The provider's breaker tripped (GUIDE §6 r15) — on the
                # daytime worker that is the CLI's rolling session window
                # (2026-08-25/26), expected to recur on a heavy day. It
                # is the vendor pacing us, not a fault of ours: recorded
                # paused, like our own budget in run_cycle, so the error
                # streak and its backoff stay meaningful. The breaker is
                # per client and each date builds a fresh one, so stop
                # here rather than pay the same refusal for the next
                # date; the next cycle, on its normal interval, is the
                # retry.
                logger.warning("%s: %s — provider unavailable (%s); pausing"
                               " this cycle", self.name, date, exc.reason)
                stats["paused"] = "provider"
                stats["detail"] = str(exc)[:300]
                break
            stats["dates"] += 1
            stats["summarized"] += a["llm_summarized"] + a["official"]
            stats["plain"] += p["plain_written"]
        stats["journaled"] = journal_model_events(conn, cycle_id)
        return stats


class RenderWorker(Worker):
    """The /today re-renderer (docs §8, OB-8): zero tokens, zero requests.
    Rebuilds site/today.html + today.json only when the journal has
    something newer than the last render (or the UTC day rolled over) —
    "after any cycle that journaled ≥ 1 item", observed via the journal
    watermark instead of cross-thread hooks."""

    name = "render"

    def _refresh_health(self, conn, prev, now):
        """Source health on a clock, not on the journal watermark — a
        failing source produces no journal movement, so the watermark
        would never trigger for the case the page exists to show."""
        last = prev.get("health_at")
        if last:
            age = (dt.datetime.fromisoformat(now)
                   - dt.datetime.fromisoformat(last)).total_seconds() / 60
            if age < config.SOURCE_HEALTH_REFRESH_MIN:
                return None
        result = None
        try:
            result = self.sup.sources_builder()
        except Exception as exc:  # noqa: BLE001 — health reporting must
            # never cost the live page; the gap shows as a stale stamp.
            logger.warning("source health refresh failed: %r", exc)
        self._persist_health_state(conn, now,
                                   payload=(result or {}).get("health"))
        return result

    def _persist_health_state(self, conn, now, payload=None):
        """Labels into source_health_state on the refresh clock. A label
        TRANSITION is durable state a downstream assessment layer
        regenerates on ('health-change'), so it gets its own table — not
        the page artifact, not last_result (the D5 lesson). The page
        builder now hands its computed health payload back across the
        seam (refresh_sources returns it under "health"), so the normal
        path persists what was rendered — one computation, no drift; the
        recompute remains as the fallback for seam-injected builders
        that return only a status dict. Persistence must never cost the
        live page."""
        try:
            if not payload or "sources" not in payload:
                entries = self.sup.registry()
                if not entries:
                    return
                payload = health.source_health(entries)
            if payload.get("available"):
                health.record_health_state(conn, payload["sources"], now=now)
        except Exception as exc:  # noqa: BLE001
            logger.warning("health state persist failed: %r", exc)

    def cycle(self, conn, cycle_id):
        date = publication_date()
        newest = conn.execute(
            "SELECT MAX(observed_at) FROM item_journal WHERE digest_date = ?",
            (date,)).fetchone()[0] or ""
        row = conn.execute(
            "SELECT last_result FROM collector_state WHERE worker = 'render'"
        ).fetchone()
        prev = json.loads(row["last_result"]) if row and row["last_result"] else {}
        now = utc_now_iso()
        refreshed = self._refresh_health(conn, prev, now)
        health_at = now if refreshed else prev.get("health_at")
        if (prev.get("date") == date and prev.get("through") == newest
                and (config.SITE_DIR / "today.html").exists()):
            return {"date": date, "rebuilt": False, "through": newest,
                    "health_refreshed": bool(refreshed), "health_at": health_at}
        stats = self.sup.today_builder(conn, date=date)
        return {"date": date, "rebuilt": True, "through": newest,
                "items": stats["items"], "pending_llm": stats["pending_llm"],
                "health_refreshed": bool(refreshed), "health_at": health_at}


def last_finalized_date(conn):
    """Newest finalized publication day, or None: the dedicated column
    (review D5 — no last_result writer can touch it), falling back to
    the JSON `finalized`/`date` keys only for rows written before the
    column existed. Module-level because two workers read it: the EOD
    worker to know what is due, the analyze worker to leave frozen days
    alone (GUIDE §6 r15)."""
    row = conn.execute(
        "SELECT finalized_date, last_result FROM collector_state"
        " WHERE worker = 'eod'").fetchone()
    if not row:
        return None
    if row["finalized_date"]:
        return row["finalized_date"]
    if row["last_result"]:
        prev = json.loads(row["last_result"])
        return prev.get("finalized") or prev.get("date")
    return None


class EODWorker(Worker):
    """The end-of-day finalizer, in-supervisor (docs §9): once per
    publication day, at/after config.EOD_ET_HOUR on Washington's clock,
    it pauses the collectors, runs the finalizer (run_pipeline as a
    subprocess — its own process, its own connections), pushes the
    evidence commit when enabled, and resumes. Only added when the
    supervisor is constructed with eod_enabled=True (the container path)
    — never implicitly in --once runs.

    Retry spacing is config.EOD_FINALIZE_RETRY_MINUTES, not the generic
    error-doubling: the ladder exists for validation failures and
    crashes (a provider outage no longer fails the run — GUIDE §6 r15),
    and its later rungs are deliberately hours apart so a transient
    cause has time to clear."""

    name = "eod"
    backoff_on_errors = False

    def interval_min(self, conn):
        row = conn.execute(
            "SELECT finalize_target, finalize_attempts FROM collector_state"
            " WHERE worker = 'eod'").fetchone()
        attempts = row["finalize_attempts"] if row and row["finalize_target"] else 0
        if attempts <= 0:
            return self.base_interval_min
        rungs = config.EOD_FINALIZE_RETRY_MINUTES
        return rungs[min(attempts, len(rungs)) - 1]

    def eod_due(self, conn, now=None):
        """The publication day to finalize, or None. Due once that day
        has closed in Washington, has not been finalized yet, and has not
        hit the failed-attempt hard stop — the hour gate is read on
        Eastern, so it means the same clock time year-round
        (config.EOD_ET_HOUR = 0: run when the day ends)."""
        now = now or dt.datetime.now(dt.UTC)
        if now.astimezone(config.PUBLICATION_TZ).hour < config.EOD_ET_HOUR:
            return None
        # The publication day that just closed in Washington — computed
        # from Eastern so a DST shift can never target the wrong day.
        target = publication_date(now - dt.timedelta(days=1))
        done_date = self._last_finalized(conn)
        if done_date and done_date >= target:
            return None
        row = conn.execute(
            "SELECT finalize_target, finalize_attempts FROM collector_state"
            " WHERE worker = 'eod'").fetchone()
        if (row and row["finalize_target"] == target
                and row["finalize_attempts"] >= config.EOD_MAX_FINALIZE_ATTEMPTS):
            # Halted (review D5): the day stays unfinalized as a disclosed
            # gap. The loud logging happened when the ladder topped out;
            # repeating it every idle check would bury the signal.
            return None
        return target

    def _last_finalized(self, conn):
        return last_finalized_date(conn)

    def _record_finalized(self, conn, target):
        """Durable success marker + ladder reset, in the columns
        record_state never writes — an error or idle cycle replacing
        last_result cannot erase this. The marker only moves forward: a
        manual --finalize of an older day (a recovered HALT) must not
        rewind it, or every day in between would come due again."""
        conn.execute(
            """
            INSERT INTO collector_state (worker, finalized_date,
                finalize_target, finalize_attempts)
            VALUES ('eod', ?, NULL, 0)
            ON CONFLICT (worker) DO UPDATE SET
                finalized_date = CASE
                    WHEN finalized_date IS NULL
                      OR excluded.finalized_date > finalized_date
                    THEN excluded.finalized_date ELSE finalized_date END,
                finalize_target = NULL,
                finalize_attempts = 0
            """,
            (target,),
        )
        conn.commit()

    def _record_finalize_failure(self, conn, target):
        """Advance the per-target attempt ladder; returns the new count.
        A different target starts a fresh ladder — the hard stop is per
        day, so a stuck Tuesday never blocks Wednesday's one fair try."""
        conn.execute(
            """
            INSERT INTO collector_state (worker, finalize_target,
                finalize_attempts)
            VALUES ('eod', ?, 1)
            ON CONFLICT (worker) DO UPDATE SET
                finalize_attempts = CASE WHEN finalize_target = excluded.finalize_target
                                         THEN finalize_attempts + 1 ELSE 1 END,
                finalize_target = excluded.finalize_target
            """,
            (target,),
        )
        conn.commit()
        return conn.execute(
            "SELECT finalize_attempts FROM collector_state WHERE worker = 'eod'"
        ).fetchone()["finalize_attempts"]

    def _record_evidence_push(self, conn, ok, error=None):
        """Durable evidence-push state, in columns record_state never
        writes — the finalize-marker lesson (review D5) applied one step
        later. Success clears the ladder; failure advances it and keeps
        the reason visible until a push succeeds."""
        # Upsert, not UPDATE: on the very first finalize of a fresh
        # database this runs BEFORE _record_finalized creates the row, so
        # a bare UPDATE silently matched nothing — the exact silence this
        # whole change exists to remove.
        if ok:
            conn.execute(
                """
                INSERT INTO collector_state (worker, evidence_pushed_at,
                    evidence_push_error, evidence_push_attempts)
                VALUES ('eod', ?, NULL, 0)
                ON CONFLICT (worker) DO UPDATE SET
                    evidence_pushed_at = excluded.evidence_pushed_at,
                    evidence_push_error = NULL,
                    evidence_push_attempts = 0
                """, (utc_now_iso(),))
        else:
            conn.execute(
                """
                INSERT INTO collector_state (worker, evidence_push_error,
                    evidence_push_attempts)
                VALUES ('eod', ?, 1)
                ON CONFLICT (worker) DO UPDATE SET
                    evidence_push_error = excluded.evidence_push_error,
                    evidence_push_attempts =
                        collector_state.evidence_push_attempts + 1
                """, (error,))
        conn.commit()

    def _push_evidence(self, conn, target):
        """Run the evidence commit and record what happened. Returns True
        on a push that reached the remote."""
        rc = self.sup.evidence_runner()
        pushed = rc == 0
        self._record_evidence_push(conn, pushed,
                                   None if pushed else f"exit {rc}")
        if not pushed:
            logger.error(
                "EVIDENCE PUSH FAILED for %s (exit %s) — the digest is LIVE"
                " on the site but the repository does not have it. The"
                " commit is in the container's writable layer; .git is not"
                " a volume, so a rebuild DESTROYS it. Fix the cause, then"
                " run deploy/vps/scripts/evidence-commit.sh.", target, rc)
        return pushed

    def _retry_pending_push(self, conn, finalized):
        """A finalized day whose evidence never reached the repository.

        eod_due() returns None once finalized_date is set, so before this
        existed the next attempt was the NEXT DAY's EOD — which failed
        identically, forever, until a deploy (F-021). The retry is the
        push alone: never a finalizer run, which would re-render and
        re-spend tokens for a day already paid for."""
        idle = {"ran": False, "finalized": finalized}
        if not config.EVIDENCE_PUSH:
            return idle
        row = conn.execute(
            "SELECT evidence_push_error, evidence_push_attempts,"
            " evidence_pushed_at, finalized_date"
            " FROM collector_state WHERE worker = 'eod'").fetchone()
        if not row:
            return idle
        # Two shapes of "never reached the repository": a push that ran
        # and failed (error set), and a finalized day whose push never
        # ran at all (pushes were off, or the process died between the
        # two). 2026-08-15..23: nine hand-finalized days sat unpushed
        # with this row reading clean, because only the first shape was
        # retried.
        never_pushed = bool(row["finalized_date"]) and not row["evidence_pushed_at"]
        if not row["evidence_push_error"] and not never_pushed:
            return idle
        if row["evidence_push_attempts"] >= config.EVIDENCE_PUSH_MAX_ATTEMPTS:
            # Disclosed gap, not a silent retry loop (GUIDE §2 applied to
            # operations). Logged once at exhaustion — repeating it every
            # idle check would bury the signal, the same reasoning
            # eod_due uses for the finalizer halt.
            return idle
        logger.warning("evidence push pending for %s (attempt %d) — retrying",
                       finalized, row["evidence_push_attempts"] + 1)
        pushed = self._push_evidence(conn, finalized)
        if not pushed:
            attempts = conn.execute(
                "SELECT evidence_push_attempts FROM collector_state"
                " WHERE worker = 'eod'").fetchone()["evidence_push_attempts"]
            if attempts >= config.EVIDENCE_PUSH_MAX_ATTEMPTS:
                logger.error(
                    "EVIDENCE PUSH HALTED for %s after %d attempts — the"
                    " day is published on the site but NOT in the"
                    " repository, and will not be retried. Fix the cause,"
                    " then run deploy/vps/scripts/evidence-commit.sh.",
                    finalized, attempts)
        return {**idle, "pushed": pushed}

    def cycle(self, conn, cycle_id):
        # The durable finalized marker lives in its own column
        # (_record_finalized); the `finalized` key returned here is a
        # status line for the health surface. History: when the marker
        # lived in last_result, a bare {"ran": False} erased it and the
        # pipeline re-ran every ~20 minutes (2026-08-01, 35 duplicate
        # evidence commits) — and the error path had the same hole, which
        # is why nothing load-bearing reads last_result anymore.
        finalized = self._last_finalized(conn)
        target = self.eod_due(conn)
        if not target:
            return self._retry_pending_push(conn, finalized)
        return self._finalize(conn, cycle_id, target)

    def finalize_now(self, conn, cycle_id, target):
        """The manual recovery (`scripts/collect.py --finalize D`): the
        same finalizer, durable marker, and evidence push as the nightly
        path, for a day the operator names — bypassing the due check and
        the halt, since the operator is the one who fixed the cause. A
        bare run_pipeline.py renders the day and records nothing, which
        is how nine days went unpushed in August 2026."""
        logger.info("manual finalize requested for %s", target)
        return self._finalize(conn, cycle_id, target)

    def _finalize(self, conn, cycle_id, target):
        logger.info("EOD finalizer firing for %s — pausing collectors", target)
        self.sup.pause_event.set()
        try:
            exit_code = self.sup.finalizer_runner(target)
            pushed = None
            if exit_code == 0 and config.EVIDENCE_PUSH:
                pushed = self._push_evidence(conn, target)
            if exit_code != 0:
                attempts = self._record_finalize_failure(conn, target)
                if attempts >= config.EOD_MAX_FINALIZE_ATTEMPTS:
                    # The loud disclosure the hard stop owes (GUIDE §2
                    # no-silent-omission, applied to operations): the day
                    # is now a named gap, not a silent retry loop.
                    logger.error(
                        "EOD finalizer HALTED for %s after %d failed"
                        " attempts — the day remains unfinalized and will"
                        " NOT be retried; fix the cause, then run"
                        " scripts/collect.py --finalize %s (a bare"
                        " run_pipeline.py renders but records and pushes"
                        " nothing)", target, attempts, target)
                raise RuntimeError(f"finalizer exited {exit_code} for {target}")
            self._record_finalized(conn, target)
            journal_new(conn, "govinfo", cycle_id)  # late finalizer items
            journal_model_events(conn, cycle_id)
            return {"ran": True, "date": target, "finalized": target,
                    "pushed": pushed}
        finally:
            self.sup.pause_event.clear()


def _run_finalizer(date=None, *, no_llm=False):
    """Run the daily pipeline for a specific publication day.

    The date is passed explicitly: run_pipeline otherwise picks its own
    via digest.default_date(), and the two disagreed — on 2026-08-02 the
    EOD target was 2026-07-31 while the run published 2026-08-01.
    no_llm mirrors the supervisor's --no-llm into the finalizer, so a
    mechanical-only collector finalizes a mechanical-only day (r15)."""
    import subprocess
    import sys

    cmd = [sys.executable, "scripts/run_pipeline.py"]
    if date:
        cmd += ["--date", date]
    if no_llm:
        cmd += ["--no-llm"]
    return subprocess.run(cmd, cwd=config.PROJECT_ROOT, check=False).returncode


def _run_evidence_commit():
    import subprocess

    return subprocess.run(
        ["bash", "deploy/vps/scripts/evidence-commit.sh"],
        cwd=config.PROJECT_ROOT, check=False).returncode


class Supervisor:
    """One process, per-source-class workers (docs §2). Every dependency
    is an optional constructor parameter with a config/module default —
    the project seam pattern (code-standards §1)."""

    def __init__(self, *, registry=None, conn_factory=None,
                 govinfo_factory=None, agency_factory=None,
                 wayback_factory=None, mailbox_factory=None, poll=None,
                 llm_factory=None, llm_enabled=True, intervals=None,
                 eod_enabled=False, finalizer_runner=None,
                 evidence_runner=None, today_builder=None,
                 sources_builder=None):
        from . import db, email_sources
        from .client import AgencyClient, GovinfoClient
        from .sources import load_registry

        self.registry = registry or load_registry
        self.conn_factory = conn_factory or db.connect
        self.govinfo_factory = govinfo_factory or GovinfoClient
        self.agency_factory = agency_factory or AgencyClient
        self.wayback_factory = wayback_factory or self._default_wayback
        self.mailbox_factory = mailbox_factory or email_sources.MailboxClient
        self.poll = poll or email_sources.poll_mailbox
        self.llm_factory = llm_factory or self._default_llm
        self.llm_enabled = llm_enabled
        self.pause_event = threading.Event()
        self.finalizer_runner = finalizer_runner or functools.partial(
            _run_finalizer, no_llm=not llm_enabled)
        self.evidence_runner = evidence_runner or _run_evidence_commit
        self.today_builder = today_builder or self._default_today_builder
        self.sources_builder = sources_builder or self._default_sources_builder
        self.eod_enabled = eod_enabled
        iv = intervals or {}
        self.workers = self._build_workers(iv)

    @staticmethod
    def _default_wayback():
        from .agencies import WaybackClient

        return WaybackClient()

    @staticmethod
    def agency_requests_today():
        """Agency-class requests today, read from the fetch log (the
        budget authority). 0 when the log doesn't exist yet."""
        import sqlite3

        try:
            fdb = sqlite3.connect(f"file:{config.FETCH_LOG_DB}?mode=ro", uri=True)
            n = fdb.execute(
                "SELECT COUNT(*) FROM fetch_log WHERE client = 'agency'"
                " AND ts_utc >= date('now')").fetchone()[0]
            fdb.close()
            return n
        except sqlite3.Error:
            return 0

    @staticmethod
    def _default_llm():
        from . import llm

        return llm.LLMClient()

    @staticmethod
    def _default_today_builder(conn, *, date=None):
        from .publish import build_today

        return build_today(conn, date=date)

    @staticmethod
    def _default_sources_builder():
        from .publish import refresh_sources

        return refresh_sources()

    def _build_workers(self, iv):
        from . import agencies
        from .agencies import host_groups

        workers = [
            GovinfoWorker(self, iv.get("govinfo", config.GOVINFO_POLL_INTERVAL_MIN)),
            EmailWorker(self, iv.get("email", config.EMAIL_POLL_INTERVAL_MIN)),
        ]
        rss = [e for e in self.registry()
               if e["status"] == "active"
               and e["type"] in agencies.INGESTIBLE_TYPES]
        for host, entries in sorted(host_groups(rss).items()):
            workers.append(AgencyHostWorker(
                self, host, entries,
                iv.get("agency", config.AGENCY_POLL_INTERVAL_MIN)))
        workers.append(AnalyzeWorker(
            self, iv.get("analyze", config.ANALYZE_MIN_INTERVAL_MIN)))
        workers.append(RenderWorker(
            self, iv.get("render", config.TODAY_RENDER_INTERVAL_MIN)))
        if self.eod_enabled:
            workers.append(EODWorker(self, iv.get("eod", 10)))
        return workers

    def run_once(self):
        """Every worker exactly one serial cycle — the testable path and
        the cron-compatible fallback shape."""
        return {w.name: w.run_cycle() for w in self.workers}

    def finalize_now(self, target):
        """`scripts/collect.py --finalize D`: one EOD cycle for the named
        day through the worker's own code (ladder bookkeeping, durable
        marker, evidence push). Returns the cycle's stats dict, or None
        when the finalizer failed (recorded on the ladder like any
        nightly failure)."""
        worker = next((w for w in self.workers if w.name == "eod"), None)
        if worker is None:
            worker = EODWorker(self, 10)
        cycle_id = uuid.uuid4().hex[:12]
        conn = self.conn_factory()
        try:
            stats = worker.finalize_now(conn, cycle_id, target)
            record_state(conn, "eod", ok=True, stats=stats)
            return stats
        except Exception as exc:  # noqa: BLE001 — same containment as run_cycle
            logger.warning("manual finalize failed: %r", exc)
            record_state(conn, "eod", ok=False, error=repr(exc))
            return None
        finally:
            conn.close()

    def run_forever(self):
        stop = threading.Event()
        threads = [threading.Thread(target=w.loop, args=(stop,),
                                    name=w.name, daemon=True)
                   for w in self.workers]
        for t in threads:
            t.start()
        return stop, threads

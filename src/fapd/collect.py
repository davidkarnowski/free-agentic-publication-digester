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
import random
import threading
import uuid

from . import config
from .client import BudgetExceededError
from .sync import publication_date, utc_now_iso

logger = logging.getLogger("fapd.collect")

# ---------------------------------------------------------------------------
# Journal reconciliation (docs/continuous-ingestion.md §3)
# ---------------------------------------------------------------------------

# Class predicates over extracted_texts rows. Agency and email items share
# the AGENCYPR collection; the channel lives in item metadata. VOTES rides
# the same web poll loop (an xml-index adapter, GUIDE §3 recorded votes) but
# under its own collection code, so it is agency-CLASS work — the worker and
# the budget — while never being agency CONTENT.
_CLASS_WHERE = {
    "govinfo": "e.collection NOT IN ('AGENCYPR', 'VOTES')",
    "agency": ("(e.collection = 'VOTES' OR (e.collection = 'AGENCYPR' AND COALESCE("
               "json_extract(e.metadata, '$.channel'), '') != 'email'))"),
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
        JOIN packages p USING (package_id) WHERE p.date_issued = ?
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
               j.collection, j.source_id, e.doc_type, e.title, e.agency,
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
        conn = self.sup.conn_factory()
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
            self.run_cycle()
            conn = self.sup.conn_factory()
            try:
                errors = conn.execute(
                    "SELECT consecutive_errors FROM collector_state WHERE worker = ?",
                    (self.name,)).fetchone()
                minutes = self.interval_min(conn) * (
                    2 ** min(errors["consecutive_errors"] if errors else 0, 3))
            finally:
                conn.close()
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

        stats = {"dates": 0, "summarized": 0, "plain": 0}
        if not self.sup.llm_enabled:
            return stats
        for date in dates_with_pending(conn):
            if not trigger_fires(conn, date):
                continue
            with self.sup.llm_factory() as lclient:
                a = analyze.run(conn, lclient, date)
                p = analyze.run_plain(conn, lclient, date)
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

    def _refresh_health(self, prev, now):
        """Source health on a clock, not on the journal watermark — a
        failing source produces no journal movement, so the watermark
        would never trigger for the case the page exists to show."""
        last = prev.get("health_at")
        if last:
            age = (dt.datetime.fromisoformat(now)
                   - dt.datetime.fromisoformat(last)).total_seconds() / 60
            if age < config.SOURCE_HEALTH_REFRESH_MIN:
                return None
        try:
            return self.sup.sources_builder()
        except Exception as exc:  # noqa: BLE001 — health reporting must
            # never cost the live page; the gap shows as a stale stamp.
            logger.warning("source health refresh failed: %r", exc)
            return None

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
        health = self._refresh_health(prev, now)
        health_at = now if health else prev.get("health_at")
        if (prev.get("date") == date and prev.get("through") == newest
                and (config.SITE_DIR / "today.html").exists()):
            return {"date": date, "rebuilt": False, "through": newest,
                    "health_refreshed": bool(health), "health_at": health_at}
        stats = self.sup.today_builder(conn, date=date)
        return {"date": date, "rebuilt": True, "through": newest,
                "items": stats["items"], "pending_llm": stats["pending_llm"],
                "health_refreshed": bool(health), "health_at": health_at}


class EODWorker(Worker):
    """The end-of-day finalizer, in-supervisor (docs §9): once per UTC
    day at/after config.EOD_UTC_HOUR it pauses the collectors, runs the
    finalizer (run_pipeline as a subprocess — its own process, its own
    connections), pushes the evidence commit when enabled, and resumes.
    Only added when the supervisor is constructed with eod_enabled=True
    (the container path) — never implicitly in --once runs."""

    name = "eod"

    def eod_due(self, conn, now=None):
        """The publication day to finalize, or None. Due once that day
        has closed in Washington and has not been finalized yet — the
        hour gate is read on Eastern, so it means the same clock time
        year-round (config.EOD_ET_HOUR = 0: run when the day ends)."""
        now = now or dt.datetime.now(dt.UTC)
        if now.astimezone(config.PUBLICATION_TZ).hour < config.EOD_ET_HOUR:
            return None
        # The publication day that just closed in Washington — computed
        # from Eastern so a DST shift can never target the wrong day.
        target = publication_date(now - dt.timedelta(days=1))
        row = conn.execute(
            "SELECT last_result FROM collector_state WHERE worker = 'eod'"
        ).fetchone()
        if row and row["last_result"]:
            done_date = json.loads(row["last_result"]).get("date")
            if done_date and done_date >= target:
                return None
        return target

    def cycle(self, conn, cycle_id):
        target = self.eod_due(conn)
        if not target:
            return {"ran": False}
        logger.info("EOD finalizer firing for %s — pausing collectors", target)
        self.sup.pause_event.set()
        try:
            exit_code = self.sup.finalizer_runner()
            pushed = None
            if exit_code == 0 and config.EVIDENCE_PUSH:
                pushed = self.sup.evidence_runner() == 0
            if exit_code != 0:
                raise RuntimeError(f"finalizer exited {exit_code} for {target}")
            journal_new(conn, "govinfo", cycle_id)  # late finalizer items
            journal_model_events(conn, cycle_id)
            return {"ran": True, "date": target, "pushed": pushed}
        finally:
            self.sup.pause_event.clear()


def _run_finalizer():
    import subprocess
    import sys

    return subprocess.run(
        [sys.executable, "scripts/run_pipeline.py"],
        cwd=config.PROJECT_ROOT, check=False).returncode


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
        self.finalizer_runner = finalizer_runner or _run_finalizer
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

    def run_forever(self):
        stop = threading.Event()
        threads = [threading.Thread(target=w.loop, args=(stop,),
                                    name=w.name, daemon=True)
                   for w in self.workers]
        for t in threads:
            t.start()
        return stop, threads

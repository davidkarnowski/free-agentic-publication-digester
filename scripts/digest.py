"""Run the ANALYZE + REPORT stages and produce digests/<date>.md.

Usage:
  uv run python scripts/digest.py [--date YYYY-MM-DD] [--verbose]

Default date: the most recent date_issued that has extracted data. The
analysis layer (analyze/rules/llm) is imported lazily inside main() so the
report stage can be exercised on stored summaries even while the analysis
modules are still being built; report rendering itself performs zero LLM
calls (GUIDE.md §6 rule 2).
"""

import argparse
import sys

from fapd import config, db, logging_setup, report


def default_date(conn):
    """Newest COMPLETE day: the latest date_issued strictly before the
    current PUBLICATION day. A date's record is only complete once the day
    has ended and the next-morning publications (esp. the Congressional
    Record) have had a sync to arrive — digesting today's date early would
    misrepresent it (worklog 2026-07-25).

    "Today" is Washington's day, not UTC's (GUIDE §3, amended 2026-07-30).
    This function was written when UTC *was* the boundary and was missed by
    that amendment: between 20:00 ET and midnight ET, UTC has already
    rolled over, so it treated the day still in progress as complete. That
    is a four-hour window every day, and on 2026-08-02 it published an
    Aug 1 digest at 22:39 ET on Aug 1."""
    from fapd.sync import publication_date

    today = publication_date()
    return conn.execute(
        "SELECT MAX(p.date_issued) FROM packages p"
        " JOIN extracted_texts e USING (package_id)"
        " WHERE p.date_issued < ?", (today,)
    ).fetchone()[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: latest extracted day)")
    ap.add_argument("--no-llm", action="store_true",
                    help="render from stored rows only; model layers are"
                         " recorded as skipped (GUIDE §6 r15)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    logging_setup.setup(verbose=args.verbose)

    conn = db.connect()
    date = args.date or default_date(conn)
    if not date:
        print("no extracted data found; run scripts/sync.py and scripts/extract.py first")
        conn.close()
        return 1

    run_input = run_output = 0
    day_tokens = None
    try:
        # Built concurrently with this script; report-only runs must still work.
        from fapd import finalize, llm
    except ImportError as exc:
        print(
            f"analysis layer unavailable ({exc}); "
            "rendering the digest from already-stored summaries only"
        )
    else:
        # The same layer runner the finalizer uses (GUIDE §6 r15): every
        # layer attempted and recorded, a provider outage never a
        # traceback — the render below works on whatever is stored.
        if args.no_llm:
            client = llm.LLMClient(backend=llm.NullBackend("disabled by operator"))
        else:
            # A re-render is a finalizer-class run, so it gets the same
            # GUIDE §6 r7 failover as run_pipeline.py — unset by default.
            client = llm.LLMClient(fallback=config.LLM_BACKEND_FALLBACK)
        with client:
            before = client.tokens_today()
            result = finalize.run_model_layers(conn, client, date)
            after = client.tokens_today()
        plain_stats = result["stats"].get("plain")
        if plain_stats:
            print(
                f"plain: {plain_stats['plain_written']}/{plain_stats['plain_pending']}"
                f" written ({len(plain_stats['failed_items'])} failed)"
            )
        print(finalize.summary_line(result))
        run_input = after[0] - before[0]
        run_output = after[1] - before[1]
        day_tokens = after

    try:
        out_path = report.render(conn, date)
    except report.ValidationError as exc:
        print(f"digest validation failed; nothing written: {exc}")
        conn.close()
        return 1

    method_counts = dict(
        conn.execute(
            "SELECT s.method, COUNT(*) FROM summaries s JOIN packages p USING (package_id)"
            " WHERE p.digest_day = ? AND s.prompt_version = ? GROUP BY s.method",
            (date, config.PROMPT_VERSION),
        )
    )
    official = method_counts.get("official", 0)
    llm_count = method_counts.get("llm", 0)
    print(f"date={date} selected={official + llm_count} official={official} llm={llm_count}")
    line = f"tokens: run={run_input:,} in / {run_output:,} out"
    if day_tokens is not None:
        line += (
            f"; today={day_tokens[0]:,} in / {day_tokens[1]:,} out"
            f" ({day_tokens[2]} call(s))"
        )
    print(line)
    print(f"digest: {out_path}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

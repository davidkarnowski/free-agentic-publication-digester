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

from info_intel import config, db, logging_setup, report


def default_date(conn):
    """Latest date_issued with extracted records, or None."""
    return conn.execute(
        "SELECT MAX(p.date_issued) FROM packages p JOIN extracted_texts e USING (package_id)"
    ).fetchone()[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: latest extracted day)")
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
        from info_intel import analyze, compose, llm
    except ImportError as exc:
        print(
            f"analysis layer unavailable ({exc}); "
            "rendering the digest from already-stored summaries only"
        )
    else:
        with llm.LLMClient() as client:
            before = client.tokens_today()
            analyze.run(conn, client, date)
            compose.compose_day(conn, client, date)
            after = client.tokens_today()
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
            " WHERE p.date_issued = ? AND s.prompt_version = ? GROUP BY s.method",
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

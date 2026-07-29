"""Self-audit report of our API footprint, from the canonical fetch log.

Answers "have we been respectful?" from our own records (GUIDE.md §4):
requests per UTC day vs. budget, status mix, bytes transferred, timing,
retry volume, and recent errors.

Usage: uv run python scripts/audit.py [--days N]
"""

import argparse
import sqlite3
import sys

from fapd import config


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7, help="how many UTC days back to report")
    args = ap.parse_args()

    if not config.FETCH_LOG_DB.exists():
        print("No fetch log yet — no requests have been made.")
        return 0
    db = sqlite3.connect(f"file:{config.FETCH_LOG_DB}?mode=ro", uri=True)

    print(f"API footprint, last {args.days} UTC day(s)"
          f" (budget: {config.MAX_REQUESTS_PER_DAY}/day, {config.MAX_REQUESTS_PER_SECOND} req/s)\n")

    print(f"{'day (UTC)':12} {'reqs':>6} {'% budget':>9} {'MB':>8} {'avg ms':>7}"
          f" {'2xx':>5} {'4xx':>5} {'5xx':>5} {'retries':>8}")
    rows = db.execute(
        """
        SELECT substr(ts_utc, 1, 10) AS day,
               COUNT(*) AS reqs,
               SUM(bytes) / 1048576.0 AS mb,
               AVG(elapsed_ms) AS avg_ms,
               SUM(status BETWEEN 200 AND 299) AS ok,
               SUM(status BETWEEN 400 AND 499) AS c4,
               SUM(status >= 500) AS c5,
               SUM(attempt > 1) AS retries
        FROM fetch_log
        WHERE ts_utc >= date('now', ?)
        GROUP BY day ORDER BY day DESC
        """,
        (f"-{args.days} days",),
    ).fetchall()
    for day, reqs, mb, avg_ms, ok, c4, c5, retries in rows:
        pct = 100.0 * reqs / config.MAX_REQUESTS_PER_DAY
        print(f"{day:12} {reqs:>6} {pct:>8.1f}% {mb or 0:>8.2f} {avg_ms or 0:>7.0f}"
              f" {ok or 0:>5} {c4 or 0:>5} {c5 or 0:>5} {retries or 0:>8}")
    if not rows:
        print("(no requests in window)")

    errors = db.execute(
        "SELECT ts_utc, url, status, error FROM fetch_log"
        " WHERE (error IS NOT NULL OR status >= 400) AND ts_utc >= date('now', ?)"
        " ORDER BY ts_utc DESC LIMIT 10",
        (f"-{args.days} days",),
    ).fetchall()
    if errors:
        print("\nMost recent errors/non-2xx (up to 10):")
        for ts, url, status, error in errors:
            print(f"  {ts}  {status or '—'}  {url}" + (f"  {error}" if error else ""))
    else:
        print("\nNo errors or non-2xx responses in window.")

    print("\nBusiest endpoints in window:")
    for path, n in db.execute(
        """
        SELECT CASE WHEN instr(url, '?') > 0 THEN substr(url, 1, instr(url, '?') - 1)
                    ELSE url END AS path, COUNT(*) AS n
        FROM fetch_log WHERE ts_utc >= date('now', ?)
        GROUP BY path ORDER BY n DESC LIMIT 8
        """,
        (f"-{args.days} days",),
    ):
        print(f"  {n:>6}  {path}")
    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

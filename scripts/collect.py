"""Continuous-ingestion collector supervisor (docs/continuous-ingestion.md).

Usage:
  uv run python scripts/collect.py                 # run forever (SIGTERM to stop)
  uv run python scripts/collect.py --once          # one serial cycle of every worker
  uv run python scripts/collect.py --once --no-llm # mechanical-only cycle

Workers: govinfo delta, one per agency host (each on its own pacing
clock), email, analyze-on-trigger. Compose never runs here — the
end-of-day finalizer (run_pipeline.py) owns it (GUIDE §6 rule 12).
"""

import argparse
import signal
import sys

from fapd import logging_setup
from fapd.collect import Supervisor


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true",
                    help="one serial cycle of every worker, then exit")
    ap.add_argument("--no-llm", action="store_true",
                    help="mechanical-only: skip the analyze worker's model calls")
    ap.add_argument("--interval-govinfo", type=int, metavar="MIN")
    ap.add_argument("--interval-agency", type=int, metavar="MIN")
    ap.add_argument("--interval-email", type=int, metavar="MIN")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)
    logging_setup.setup(verbose=args.verbose or args.once)

    intervals = {k: v for k, v in (
        ("govinfo", args.interval_govinfo),
        ("agency", args.interval_agency),
        ("email", args.interval_email),
    ) if v}
    sup = Supervisor(llm_enabled=not args.no_llm, intervals=intervals)

    if args.once:
        results = sup.run_once()
        failed = [name for name, stats in results.items() if stats is None]
        for name, stats in results.items():
            print(f"   {name:24} {stats if stats is not None else 'FAILED (see log)'}")
        return 1 if failed else 0

    stop, threads = sup.run_forever()
    print(f"fapd-collect: {len(threads)} worker(s) running — SIGTERM/Ctrl-C to stop",
          flush=True)
    signal.signal(signal.SIGTERM, lambda *a: stop.set())
    try:
        while not stop.wait(60):
            pass
    except KeyboardInterrupt:
        stop.set()
    for t in threads:
        t.join(timeout=30)
    print("fapd-collect: stopped", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

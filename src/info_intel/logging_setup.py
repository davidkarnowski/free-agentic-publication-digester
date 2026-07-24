"""Logging for pipeline runs: console + a daily file under data/logs/.

Two accountability layers (GUIDE.md §4 "log every request"):
- data/fetch_log.db — canonical, queryable record of every outbound request
  (owned by the HTTP client; see scripts/audit.py for reporting).
- data/logs/access-YYYY-MM-DD.log — the human-readable narrative this module
  configures: what we asked for, how we paced, when and why we backed off.

File handler captures DEBUG regardless of console verbosity, so the on-disk
narrative is always complete. All timestamps UTC.
"""

import datetime as dt
import logging
import time

from . import config


def setup(verbose=False):
    root = logging.getLogger("info_intel")
    root.setLevel(logging.DEBUG)
    if root.handlers:  # idempotent across repeated calls in one process
        return root

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_fmt = logging.Formatter("%(asctime)sZ %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    console_fmt.converter = time.gmtime
    console.setFormatter(console_fmt)
    root.addHandler(console)

    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(config.LOG_DIR / f"access-{day}.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)sZ %(levelname)-7s %(name)s: %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"
    )
    file_fmt.converter = time.gmtime
    file_handler.setFormatter(file_fmt)
    root.addHandler(file_handler)
    return root

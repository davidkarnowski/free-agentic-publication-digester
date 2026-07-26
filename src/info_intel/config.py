"""Central configuration. Secrets come from .env; access-policy constants
are code, per GUIDE.md §4 — respectful access is a property of the client,
not operator discipline."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DIGEST_DIR = PROJECT_ROOT / "digests"

load_dotenv(PROJECT_ROOT / ".env")

API_BASE = "https://api.govinfo.gov"
BULKDATA_BASE = "https://www.govinfo.gov/bulkdata"

# GUIDE.md §4: ~1% of GPO's permitted rate. Do not raise without a GUIDE change.
MAX_REQUESTS_PER_SECOND = 1.0
MAX_REQUESTS_PER_DAY = 2000

# GUIDE.md §4: a sync with no stored watermark must NOT walk open-ended history
# (BILLS alone is ~289k packages). First pull starts at now minus this window;
# anything older is a deliberate, throttled bulkdata backfill.
INITIAL_SYNC_LOOKBACK_DAYS = 3

REQUEST_TIMEOUT = 30  # seconds
MAX_ATTEMPTS = 5  # total tries per request, including the first
BACKOFF_BASE_SECONDS = 2.0  # 2, 4, 8, 16 between retries
# If the server reports fewer remaining requests than this, something is very
# wrong with our usage pattern (our budget is ~1% of theirs) — halt the client.
MIN_SERVER_REMAINING = 1000

FETCH_LOG_DB = DATA_DIR / "fetch_log.db"
PIPELINE_DB = DATA_DIR / "info_intel.db"
LOG_DIR = DATA_DIR / "logs"
LLM_LEDGER_DB = DATA_DIR / "llm_ledger.db"

# GUIDE §6 rule 6: tiered models — cheap map tier, strong compose tier.
# Backend is the `claude` CLI (headless), billed to the operator's plan.
MAP_MODEL = "haiku"
COMPOSE_MODEL = "opus"
# Bump when summarization prompts change; stored per summary row (§6 rule 5).
PROMPT_VERSION = 1
# Plain-speak layer versions independently (§6 rule 9): phrasing iterations
# never regenerate factual summaries.
PLAIN_PROMPT_VERSION = 1
# Day-in-Review compose prompt versions independently for the same reason.
# v2: adds the judicial paragraph (J1).
COMPOSE_PROMPT_VERSION = 2
PLAIN_MODEL = MAP_MODEL  # restatement is compression work — cheap tier
MAX_PLAIN_BATCH_ITEMS = 25  # inputs are stored summaries (~170 tokens each)
LLM_TIMEOUT = 300  # seconds per call

# GUIDE.md §3: scope. Order is sync order. USCOURTS added 2026-07-25 (J1).
COLLECTIONS = ("CREC", "BILLS", "FR", "USCOURTS")

# Rule USCOURTS-FETCH-01 (GUIDE §3 judicial): USCOURTS delta listings carry
# heavy lastModified churn on years-old cases (measured 7,178 of 9,401 in a
# 3-day window). Only packages whose date_issued falls within this window
# are archived; older ones are listed, marked 'skipped', and disclosed.
USCOURTS_FETCH_WINDOW_DAYS = 7

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
USER_AGENT = f"info-intel/0.1 (personal daily-digest research; contact: {CONTACT_EMAIL})"


def api_key() -> str:
    key = os.environ.get("GOVINFO_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "GOVINFO_API_KEY is not set. Copy .env.example to .env and add your "
            "key from https://api.data.gov/signup/"
        )
    return key

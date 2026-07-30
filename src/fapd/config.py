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
SITE_DIR = PROJECT_ROOT / "site"

# .env must load before any os.environ read below — a value set only in
# .env is otherwise silently ignored (bug found 2026-07-30: SITE_BASE_URL
# was read above this line and never saw .env).
load_dotenv(PROJECT_ROOT / ".env")

# Absolute base URL for published machine surfaces (sitemap <loc>, feed
# links, robots Sitemap directive, llms.txt) — e.g. "https://fapd.info".
# Empty (default) emits root-relative paths, correct for local viewing and
# domain-root hosting. Sitemaps and robots Sitemap directives formally
# require absolute URLs.
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "").rstrip("/")

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
PIPELINE_DB = DATA_DIR / "fapd.db"
LOG_DIR = DATA_DIR / "logs"
CAPTURE_DIR = DATA_DIR / "captures"  # content-addressed raw bytes (gitignored)
MANIFEST_DIR = PROJECT_ROOT / "provenance" / "manifests"  # committed
SOURCES_REGISTRY = PROJECT_ROOT / "sources" / "registry.yaml"

# GUIDE §3/§4: agency newsrooms get their own daily request bucket so agency
# crawling can never consume the govinfo budget (or vice versa).
MAX_AGENCY_REQUESTS_PER_DAY = 500
# GUIDE §7: bump when the text-normalization/extraction logic changes;
# text_sha256 values are only comparable within one normalizer version.
NORMALIZER_VERSION = 1
# Wayback Save-Page-Now corroboration budget (its own tiny bucket).
MAX_WAYBACK_REQUESTS_PER_DAY = 100
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
# Section quick-read synopses version independently (§3a).
SECTION_PROMPT_VERSION = 1
PLAIN_MODEL = MAP_MODEL  # restatement is compression work — cheap tier
MAX_PLAIN_BATCH_ITEMS = 25  # inputs are stored summaries (~170 tokens each)
# Retries escalate isolation in groups before falling back to one call per
# item. Every call re-pays the backend's fixed prompt overhead (~25K tokens),
# so retrying singly is the expensive path: measured 2026-07-29, 25
# single-item plain retries cost 645,778 input tokens — 42% of that day's
# spend — to recover items the first pass had merely truncated away.
MAX_RETRY_BATCH_ITEMS = 5
LLM_TIMEOUT = 300  # seconds per call

# GUIDE.md §3: scope. Order is sync order. USCOURTS added 2026-07-25 (J1).
COLLECTIONS = ("CREC", "BILLS", "FR", "USCOURTS", "PLAW")

# Rule USCOURTS-FETCH-01 (GUIDE §3 judicial): USCOURTS delta listings carry
# heavy lastModified churn on years-old cases (measured 7,178 of 9,401 in a
# 3-day window). Only packages whose date_issued falls within this window
# are archived; older ones are listed, marked 'skipped', and disclosed.
USCOURTS_FETCH_WINDOW_DAYS = 7

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")

# Project mailbox for email-distributed sources (GUIDE §3 email class;
# docs/email-sources.md). Credentials live only in .env.
IMAP_HOST = os.environ.get("IMAP_HOST", "")
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
USER_AGENT = (f"fapd/0.1 (Free Agentic Publication Digester; personal"
              f" daily-digest research; contact: {CONTACT_EMAIL})")


def api_key() -> str:
    key = os.environ.get("GOVINFO_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "GOVINFO_API_KEY is not set. Copy .env.example to .env and add your "
            "key from https://api.data.gov/signup/"
        )
    return key

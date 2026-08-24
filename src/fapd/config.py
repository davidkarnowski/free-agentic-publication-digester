"""Central configuration. Secrets come from .env; access-policy constants
are code, per GUIDE.md §4 — respectful access is a property of the client,
not operator discipline."""

import os
from pathlib import Path
from zoneinfo import ZoneInfo

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
# Raised 2,000 -> 6,000 on 2026-07-31 (operator-authorised, GUIDE §4
# amended with the evidence): api.data.gov documents 1,000 requests per
# HOUR per key and answers 429 above it; we have never received a 429, and
# at 2,000/day we averaged ~83/hour, about 8% of the allowance. The daily
# figure is bounded by MAX_GOVINFO_REQUESTS_PER_HOUR below, which is what
# actually keeps us away from the publisher's limit.
MAX_REQUESTS_PER_DAY = 6000

# GUIDE.md §4: a sync with no stored watermark must NOT walk open-ended history
# (BILLS alone is ~289k packages). First pull starts at now minus this window;
# anything older is a deliberate, throttled bulkdata backfill.
INITIAL_SYNC_LOOKBACK_DAYS = 3

# An index is not a feed (GUIDE §3): a feed is bounded by its publisher,
# an index can list an entire congressional session. Adapters reading an
# index bound themselves to this window before the per-item article
# fetch — otherwise first activation buys hundreds of requests' worth of
# items the dating rule then excludes as backfill.
INDEX_LOOKBACK_DAYS = 7

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
# Raised 500 -> 1500 on 2026-07-31 (operator-authorised: "at least hourly
# update cycles as long as we aren't violating any bot/server restraints
# set by source servers", GUIDE §4 amended with the evidence). Hourly
# across the active hosts is ~24 requests per host per day — one an hour.
# No publisher declares a daily cap: robots.txt has no such directive,
# and none of ours sets Request-rate or Visit-time. What they DO declare
# is crawl-delay, which is spacing, and which we honor exactly and
# separately (gao.gov 420s, fda.gov 30s, fema.gov 15s, justice.gov and
# odni.gov 10s, ftc.gov 5s). The raise was made only after removing the
# waste it would otherwise have paid for — see F-007, the robots cache.
#
# Raised 1500 -> 3000 on 2026-08-06 (operator-authorised, GUIDE §4
# amended with the evidence). Production reached 1,287 agency requests
# that day against a collector ceiling of 1,275 (85% of 1,500; the rest
# is the EOD reserve) and refused to poll three newly activated sources.
# Re-measured before raising: no host declares Request-rate or
# Visit-time — there is no publisher cap to approach — and across seven
# days each host received ~42-46 requests a day, about one every 33
# minutes. Zero 429s from any government host in the project's history
# (the 178 on record are all web.archive.org, its own budget). At ~29
# requests per source per day this carries ~88 sources against 27 still
# planned. Per-host pacing is unaffected: crawl-delay is enforced by the
# client per host, so a bigger daily number buys breadth, never speed.
MAX_AGENCY_REQUESTS_PER_DAY = 3000

# Hourly ceiling (GUIDE §4, added 2026-07-31). api.data.gov — the shared GSA
# service govinfo runs on — documents 1,000 requests per hour per key and
# answers 429 when it is exceeded. We have never seen a 429. This ceiling is
# half of what the key permits, enforced from the fetch log so it holds
# across processes, and it is what makes a larger DAILY budget safe: the day
# can grow without any hour approaching the publisher's stated limit.
MAX_GOVINFO_REQUESTS_PER_HOUR = 500
# Reserved for the end-of-day finalizer. Collectors stop at this fraction of
# the daily budget; only the finalizer may spend the remainder. On
# 2026-07-30 the collectors spent all 2,000 govinfo requests on backlog and
# the finalizer then could not sync the day it was finalizing.
EOD_BUDGET_RESERVE_FRACTION = 0.15
# GUIDE §7: bump when the text-normalization/extraction logic changes;
# text_sha256 values are only comparable within one normalizer version.
NORMALIZER_VERSION = 1
# Wayback Save-Page-Now corroboration budget (its own tiny bucket).
MAX_WAYBACK_REQUESTS_PER_DAY = 100
LLM_LEDGER_DB = DATA_DIR / "llm_ledger.db"

# GUIDE §6 rule 6: tiered models — cheap map tier, strong compose tier.
# The LLM layer is backend-pluggable (§6 rule 7, amended 2026-07-30):
#   "cli" — the `claude` CLI (headless), billed to the operator's plan;
#   "api" — the Anthropic API (ANTHROPIC_API_KEY), for hosted/VPS runs;
#   "gemini" / "google" — Google AI Studio (GOOGLE_GEMINI_API_KEY).
LLM_BACKEND = os.environ.get("LLM_BACKEND", "cli").strip().lower()
MAP_MODEL = "haiku"
COMPOSE_MODEL = "opus"
# Tier alias -> concrete model, per backend. Env-overridable so models can
# be tried without code edits; a name not in the table passes through
# unresolved, so a caller may pin a concrete model id directly.
LLM_MODELS = {
    "cli": {
        "haiku": os.environ.get("FAPD_MAP_MODEL_CLI", "haiku"),
        "opus": os.environ.get("FAPD_COMPOSE_MODEL_CLI", "opus"),
    },
    "api": {
        "haiku": os.environ.get("FAPD_MAP_MODEL_API", "claude-haiku-4-5-20251001"),
        "opus": os.environ.get("FAPD_COMPOSE_MODEL_API", "claude-opus-5"),
    },
    "gemini": {
        "haiku": os.environ.get("FAPD_MAP_MODEL_GEMINI", "gemini-2.5-flash"),
        "opus": os.environ.get("FAPD_COMPOSE_MODEL_GEMINI", "gemini-2.5-flash"),
    },
    "google": {
        "haiku": os.environ.get("FAPD_MAP_MODEL_GEMINI", "gemini-2.5-flash"),
        "opus": os.environ.get("FAPD_COMPOSE_MODEL_GEMINI", "gemini-2.5-flash"),
    },
}
# API-backend response cap. On models with extended thinking on by default
# the cap covers thinking + text together, so it is deliberately generous.
LLM_MAX_OUTPUT_TOKENS = 16000
# Transient-retry ladder for verifiably ZERO-BILLED failures only (plan
# 2026-08-24, BUG-1; GUIDE §6 r14's "retries are the expensive path" is
# untouched because these attempts cost nothing). Total calls per
# completion, and the cap on how long one wait may be — the provider's
# own hint ("Please retry in 37s", Retry-After) is honored up to the cap,
# else 2**attempt seconds. 2026-08-16..24 the ladder was two calls ~1 s
# apart against a quota asking for 3-40 s: eight halted finalizers.
LLM_TRANSIENT_ATTEMPTS = int(os.environ.get("FAPD_LLM_TRANSIENT_ATTEMPTS", "3"))
LLM_RETRY_MAX_WAIT_S = int(os.environ.get("FAPD_LLM_RETRY_MAX_WAIT_S", "60"))
# GUIDE §6 r8 (operator ruling 2026-08-02): NO standing daily token cap —
# this is an on-demand THROTTLE. Unset (the default) means unlimited; set
# an input-token integer on the box to engage backpressure: a call that
# would start past the day's ledger-counted figure pauses like an HTTP
# budget stop (queued to the next day, disclosed, never silent). Counted
# from the ledger so it holds across processes and nothing bypasses it.
DAILY_TOKEN_THROTTLE = int(os.environ.get("FAPD_DAILY_TOKEN_THROTTLE", "0")) or None
# Per-call prompt-size guard (review R1/D3, standing policy regardless of
# the throttle): compose_day builds its prompt from every summary of the
# day, so a runaway day must fail one call loudly rather than ship an
# unbounded prompt. ~150K tokens' worth of characters — several times any
# measured day, under the model context ceiling.
LLM_MAX_PROMPT_CHARS = 600_000
# GUIDE §2 opinion-agnostic lexicon — THE canonical banned-term list.
# Single source of truth (review D8): every prose prompt restates it from
# this constant and report's render-time gate compiles its scan regex
# from it, so the two enforcement layers cannot drift. It binds ONLY our
# generated prose — official titles and summaries are quoted verbatim and
# never gated (GUIDE §2 scope amendment, 2026-08-02). Phrases tolerate
# any whitespace between words. Editing this list is a prompt change for
# every surface at once: bump EVERY prompt version below (§3a).
BANNED_TERMS = (
    "landmark",
    "controversial",
    "historic",
    "unprecedented",
    "sweeping",
    "radical",
    "extreme",
    "momentous",
    "alarming",
    "in an attempt to",
    "aims to appease",
    # Plain-register evaluative framing (the plain-speak layer's failure
    # modes) — GUIDE §2 plain-language rules.
    "red tape",
    "crackdown",
    "cracks down",
    "slams",
    "loophole",
)

# Bump when summarization prompts change; stored per summary row (§6 rule 5).
# v2: banned-term list generated verbatim from BANNED_TERMS (review D8).
PROMPT_VERSION = 2
# Plain-speak layer versions independently (§6 rule 9): phrasing iterations
# never regenerate factual summaries. v2: full banned list from BANNED_TERMS.
PLAIN_PROMPT_VERSION = 2
# Day-in-Review compose prompt versions independently for the same reason.
# v2: adds the judicial paragraph (J1). v3: full banned list from
# BANNED_TERMS — the compose model was told 10 of 16 terms (review D8).
COMPOSE_PROMPT_VERSION = 4  # v4 2026-08-06: observation framing — counts are observations, never "issued today"
# Section quick-read synopses version independently (§3a).
# v2: full banned list from BANNED_TERMS.
SECTION_PROMPT_VERSION = 2
# Section discovery-key tags (§6 rule 12a): independently versioned,
# cheap tier, one batched call per digest day. v2: full banned list.
TAG_PROMPT_VERSION = 2
# Developer-insight suggestions (§3a): dev-facing surface, one cheap-tier
# call per EOD over the run's own metrics — never document content.
INSIGHT_PROMPT_VERSION = 1
# Source-page surfaces (§3a, 2026-08-03): assessment = our measured
# ingestion relationship, refreshed at 30 days or on a health-label
# change; description = what the source is, regenerated only when its
# registry entry changes. Both cheap tier, batched, lexicon-scanned
# before storage.
SOURCE_ASSESS_PROMPT_VERSION = 1
SOURCE_DESC_PROMPT_VERSION = 1
SOURCE_ASSESS_MAX_AGE_DAYS = 30
PLAIN_MODEL = MAP_MODEL  # restatement is compression work — cheap tier
MAX_PLAIN_BATCH_ITEMS = 25  # inputs are stored summaries (~170 tokens each)
# Retries escalate isolation in groups before falling back to one call per
# item. Every call re-pays the backend's fixed prompt overhead (~25K tokens),
# so retrying singly is the expensive path: measured 2026-07-29, 25
# single-item plain retries cost 645,778 input tokens — 42% of that day's
# spend — to recover items the first pass had merely truncated away.
MAX_RETRY_BATCH_ITEMS = 5
# Ceiling on single-item retries per run (GUIDE §6, added 2026-07-31). The
# CLI backend costs ~29K input tokens per call whatever the payload, so a
# single retry buys one ~800-token summary for the price of a full batch.
# Measured 2026-07-30: 366 single retries burned 10,860,137 input tokens —
# 62% of that day's spend. Past this ceiling an item is left unsummarized
# and disclosed by the coverage accounting, which is what it is for.
MAX_SINGLE_RETRIES_PER_RUN = 12
# ...and a per-ITEM ceiling, because the per-run one resets every cycle.
# The collector runs analyze every 15 minutes for each pending date, so a
# permanently unsummarizable item was retried indefinitely: on 2026-07-31
# that produced 1,345 single retries and 39.7M input tokens, 60% of the
# day. After this many attempts an item is left unsummarized and
# disclosed by the coverage accounting, which is what rule 14 intends.
MAX_ITEM_SUMMARY_ATTEMPTS = 3

# GUIDE §6 rule 14a (incident 2026-08-08, CREC-2026-07-13-pt1-PgH4403,
# "extreme"): ceiling on corrective rewrites for an item whose STORED
# summary tripped the render-time lexicon gate — a different failure
# class and a different ceiling than MAX_ITEM_SUMMARY_ATTEMPTS above
# (that one is for a call that never returned a usable summary at all).
# Kept low deliberately: a corrective call carries the full source text
# plus error context, a materially more expensive intervention per
# attempt than an ordinary retry.
MAX_LEXICON_CORRECTION_ATTEMPTS = 2

# GUIDE §4 amendment 2026-08-10: sync.py had no cross-cycle retry ceiling
# for package downloads, so a permanently-stuck package (distinct from
# govinfo's normal on-demand ZIP/MODS generation delay) was re-attempted
# every ~30-minute cycle forever, inflating the accepted 18.1% baseline
# govinfo error rate (2026-07-31) to a measured 22-26% (2026-08-04..09).
# ~24 hours of cycles is a generous grace period before calling a package
# a disclosed gap rather than still-generating.
MAX_PACKAGE_FETCH_ATTEMPTS = 48

LLM_TIMEOUT = 300  # seconds per call

# GUIDE.md §3: scope. Order is sync order. USCOURTS added 2026-07-25 (J1).
COLLECTIONS = ("CREC", "BILLS", "FR", "USCOURTS", "PLAW")

# Continuous ingestion (GUIDE §4/§6 r12 amendments 2026-07-30;
# docs/continuous-ingestion.md §4-§5). Intervals are minutes, jittered.
GOVINFO_POLL_INTERVAL_MIN = 30
AGENCY_POLL_INTERVAL_MIN = 60
EMAIL_POLL_INTERVAL_MIN = 15
# /today re-render check (zero tokens, zero requests — journal watermark
# comparison; rebuilds only when a cycle journaled something new).
TODAY_RENDER_INTERVAL_MIN = 5
# Source-health refresh. Deliberately on a CLOCK, not on the journal
# watermark: a source that starts failing journals nothing, so a
# watermark trigger would refresh health for every case except the one
# that matters. Zero tokens, zero requests — SQL and a render (~1.3s).
SOURCE_HEALTH_REFRESH_MIN = 15
# Model layers fire on batch-threshold-or-age, never per item (§6 r12):
# a full map batch, or the oldest pending item older than the latency
# bound; successive analyze cycles at least MIN_INTERVAL apart.
ANALYZE_MAX_LATENCY_MIN = 60
ANALYZE_MIN_INTERVAL_MIN = 15
# How far back the analyze worker will look (GUIDE §6, added 2026-07-31).
# We do not publish post-dated digests, so spending on a day that will never
# be published starves the day that will: on 2026-07-30 the worker produced
# 184 summaries across eleven dates back to 2024-06-18 while the digest day
# itself received none. 1 = the current publication day and the one before
# it, which is the day the finalizer freezes just after midnight.
ANALYZE_MAX_AGE_DAYS = 1
# Past this fraction of a class's daily request budget, its collector
# doubles its interval for the rest of the UTC day (EOD headroom).
BUDGET_BACKPRESSURE_FRACTION = 0.7
# The federal publication day (GUIDE §3, amended 2026-07-30). Washington's
# clock is the publishers' clock; dating by UTC filed evening releases
# under the following day. Observation timestamps stay UTC — only the
# publication day a document belongs to is Eastern.
PUBLICATION_TZ = ZoneInfo("America/New_York")
PUBLICATION_TZ_LABEL = "Eastern time (Washington, D.C.)"

# EOD finalizer (in-supervisor, docs/continuous-ingestion.md §9): fires
# once per publication day at/after this hour, read on WASHINGTON's
# clock — 0 means the finalizer runs when the publication day it
# finalizes actually ends (operator, 2026-07-30). Expressed in Eastern,
# not UTC, because midnight ET is 04:00 UTC in summer and 05:00 in
# winter; a fixed UTC hour would drift by an hour twice a year. Still
# inside the §4 off-peak window. Evidence pushes gate on
# FAPD_EVIDENCE_PUSH=1.
EOD_ET_HOUR = 0
EVIDENCE_PUSH = os.environ.get("FAPD_EVIDENCE_PUSH", "") == "1"

# Hard stop for a repeatedly failing finalizer (review D5/R3, same shape
# as MAX_ITEM_SUMMARY_ATTEMPTS): after this many failed finalize attempts
# for ONE target day, that day is loudly disclosed as halted and not
# retried — without it, a digest that persistently fails validation buys
# a full pipeline run (sync, analyze, compose on the strong tier) every
# backoff interval, forever (~18 runs/day). A new day gets a fresh
# ladder; operator intervention (fix, then `scripts/collect.py
# --finalize D`) clears it.
#
# Spacing (2026-08-24, GUIDE §6 r15): minutes to wait after the 1st,
# 2nd, 3rd... failed attempt. Before this the EOD worker used the
# generic error-doubling (10/20/40 min), which spent all three attempts
# by 06:12Z on 2026-08-22 and -23 — before the provider's quota reset at
# 07:00Z. A provider outage no longer fails the run at all (r15), so the
# ladder now exists for validation failures and crashes; its later rungs
# are hours apart so a transient cause has time to clear. With four
# attempts: ≈04:00, 04:15, 05:15, 08:35 UTC.
EOD_MAX_FINALIZE_ATTEMPTS = 4
EOD_FINALIZE_RETRY_MINUTES = (15, 60, 200)

# Bounded retry for a failing evidence push (F-021, 2026-08-07), same
# shape as the ladder above. A push failure is either transient (GitHub
# unreachable) or structural (the box diverged from origin) — retrying on
# the next EOD cycle heals the first in minutes, while the second needs a
# human, so the ladder ends and says so instead of hammering the remote
# nightly. Cheap where the finalizer ladder is expensive: this buys one
# git push, not a full pipeline run. The digest is already rendered,
# validated and live either way; this governs publication to the
# repository, never the record itself.
EVIDENCE_PUSH_MAX_ATTEMPTS = 3

# Rule USCOURTS-FETCH-01 (GUIDE §3 judicial): USCOURTS delta listings carry
# heavy lastModified churn on years-old cases (measured 7,178 of 9,401 in a
# 3-day window). Only packages whose date_issued falls within this window
# are archived; older ones are listed, marked 'skipped', and disclosed.
USCOURTS_FETCH_WINDOW_DAYS = 7

# GUIDE §3 (amended 2026-08-06): per-collection digest-filing policy.
# "observation" files a package under the Eastern day our collector
# first observed it (the only timestamp we define precisely — the three
# clocks doctrine); "cover" files under the document's own date_issued.
# FR publishes on its cover date and govinfo posts it early (measured:
# the 2026-08-03 issue was observed 08-01), so observation would misfile
# it; AGENCYPR keeps the §3 agency dating rule. digest_day is write-once
# at first sight — a revision re-fetch never re-files a document.
FILING_POLICY = {"FR": "cover", "AGENCYPR": "cover"}
FILING_DEFAULT = "observation"

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")

# Multi-modal Text-to-Speech (TTS) configuration (GUIDE §6 multi-modal accessibility)
TTS_PROVIDER = os.environ.get("TTS_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
TTS_MODEL = os.environ.get("TTS_MODEL", "tts-1")
TTS_VOICE = os.environ.get("TTS_VOICE", "nova")

# Project mailbox for email-distributed sources (GUIDE §3 email class;
# docs/email-sources.md). Credentials live only in .env.
IMAP_HOST = os.environ.get("IMAP_HOST", "")
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
# The +URL is the crawler-transparency page (docs/site/bot.md) — the
# standard convention so a sec-ops reader of a server log lands on the
# explanation in one step.
USER_AGENT = (f"fapd/0.1 (Free Agentic Publication Digester;"
              f" +https://fapd.info/bot.html; contact: {CONTACT_EMAIL})")


def api_key() -> str:
    key = os.environ.get("GOVINFO_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "GOVINFO_API_KEY is not set. Copy .env.example to .env and add your "
            "key from https://api.data.gov/signup/"
        )
    return key


"""Living sources registry (GUIDE.md §3).

`sources/registry.yaml` is the single canonical map of every federal source
this project ingests, plans to ingest, or has evaluated. This module loads
and validates it, computes coverage statistics, and renders `SOURCES.md`
(written by ``scripts/sources_doc.py``). The rendering is deterministic —
a pure function of the registry — so a test can assert the committed
document is in sync with the registry.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "sources" / "registry.yaml"

OPTIONAL_FIELDS = ("adapter", "sender", "index_item_path")
# per-source strategy (GUIDE §3).
# `sender`: for type: email, the confirmed From address(es) — a string or a
# list. It is the allowlist the mailbox adapter matches against: a message
# whose sender maps to no registered source is never parsed.
# `index_item_path`: for type: html-index, a URL PATH PREFIX that an
# anchor must match to count as a listing entry (e.g. "/newsroom/") —
# added 2026-07-31 with the html-index adapter. Deliberately a prefix and
# not a selector expression: a query language in the registry would put
# page-structure knowledge where no test can exercise it, and every hint
# added so far has been "the releases live under this path, the navigation
# does not". Anything a prefix cannot express belongs in an adapter
# subclass, where it can be tested against captured bytes.
REQUIRED_FIELDS = (
    "id",
    "name",
    "branch",
    "parent_org",
    "description",
    "type",
    "tier",
    "urls",
    "method",
    "status",
    "added",
    "notes",
)
BRANCHES = ("legislative", "executive", "judicial", "cross-branch")
STATUSES = ("active", "planned", "evaluated-excluded", "unavailable")
TYPES = ("govinfo-collection", "rss", "html-index", "aggregator",
         "api", "xml-index", "bulkdata", "email")
TIERS = (1, 2, 3)
URL_KEYS = ("collection", "feed", "index", "home", "signup")
# Valid `adapter` values, scoped by dispatch mechanism. Web types dispatch
# through agencies.ADAPTERS (a drift test asserts these stay equal — this
# module must not import agencies, which pulls the HTTP stack). Email
# entries dispatch by `sender`, never by adapter: their adapter value is
# platform documentation (GUIDE §3), and absence is meaningful — it says
# the platform is not yet known, so nothing may assume one.
WEB_ADAPTERS = ("rss", "rss-feed-only", "usps", "senate-votes",
                "congress-bill-actions", "html-index",
                "presidential-actions")
EMAIL_PLATFORMS = ("govdelivery",)

_KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_STATUS_BADGES = {
    "active": "**ACTIVE**",
    "planned": "planned",
    "evaluated-excluded": "excluded",
    "unavailable": "UNAVAILABLE",
}
_BRANCH_TITLES = {
    "legislative": "Legislative",
    "executive": "Executive",
    "judicial": "Judicial",
    "cross-branch": "Cross-branch",
}
_TIER_SEMANTICS = {
    1: (
        "cabinet departments, top independents, legislative support agencies, "
        "the White House, and core govinfo collections"
    ),
    2: "major sub-agency newsrooms and regulator clusters",
    3: "long tail, added opportunistically",
}


def _fail(entry: dict, problem: str) -> None:
    label = entry.get("id") or entry.get("name") or "<no id>"
    raise ValueError(f"registry entry {label!r}: {problem}")


def _validate(entry: dict, seen_ids: set[str], seen_senders: dict[str, str]) -> None:
    if not isinstance(entry, dict):
        # ValueError, not TypeError: the contract is ValueError for any invalid entry
        raise ValueError(f"registry entry {entry!r}: not a mapping")  # noqa: TRY004
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if missing:
        _fail(entry, f"missing required field(s) {', '.join(missing)}")
    unknown = [k for k in entry if k not in REQUIRED_FIELDS + OPTIONAL_FIELDS]
    if unknown:
        _fail(entry, f"unknown field(s) {', '.join(unknown)}")

    for field in REQUIRED_FIELDS:
        if field in ("urls", "tier"):
            continue
        if not isinstance(entry[field], str):
            _fail(entry, f"field {field!r} must be a string")
    for field in ("id", "name", "branch", "parent_org", "description", "method", "status", "added"):
        if not entry[field].strip():
            _fail(entry, f"field {field!r} must be non-empty")

    if not _KEBAB_RE.match(entry["id"]):
        _fail(entry, f"id {entry['id']!r} is not kebab-case")
    if entry["id"] in seen_ids:
        _fail(entry, "duplicate id")
    if entry["branch"] not in BRANCHES:
        _fail(entry, f"branch {entry['branch']!r} not in {BRANCHES}")
    if entry["status"] not in STATUSES:
        _fail(entry, f"status {entry['status']!r} not in {STATUSES}")
    if entry["type"] not in TYPES:
        _fail(entry, f"type {entry['type']!r} not in {TYPES}")
    if isinstance(entry["tier"], bool) or entry["tier"] not in TIERS:
        _fail(entry, f"tier {entry['tier']!r} not in {TIERS}")
    if not _DATE_RE.match(entry["added"]):
        _fail(entry, f"added {entry['added']!r} is not YYYY-MM-DD")

    urls = entry["urls"]
    if not isinstance(urls, dict) or not urls:
        _fail(entry, "urls must be a non-empty mapping")
    bad_keys = [k for k in urls if k not in URL_KEYS]
    if bad_keys:
        _fail(entry, f"urls key(s) {', '.join(bad_keys)} not in {URL_KEYS}")
    for key, url in urls.items():
        if not isinstance(url, str) or not url.startswith("http"):
            _fail(entry, f"urls[{key!r}] must be an http(s) URL string")

    # Gate 3 lives in `notes` (GUIDE §3): an active source without a written
    # coverage evaluation is a claim without evidence.
    if entry["status"] == "active" and not entry["notes"].strip():
        _fail(entry, "status 'active' requires a non-empty notes field "
                     "(the gate-3 coverage evaluation lives there, GUIDE §3)")

    adapter = entry.get("adapter")
    if adapter is not None:
        if not isinstance(adapter, str):
            _fail(entry, "field 'adapter' must be a string")
        allowed = EMAIL_PLATFORMS if entry["type"] == "email" else WEB_ADAPTERS
        if adapter not in allowed:
            _fail(entry, f"adapter {adapter!r} not in {allowed} "
                         f"for type {entry['type']!r}")

    hint = entry.get("index_item_path")
    if hint is not None:
        if entry["type"] != "html-index":
            _fail(entry, "field 'index_item_path' is only valid on type "
                         "'html-index' entries")
        if not isinstance(hint, str) or not hint.startswith("/"):
            _fail(entry, f"index_item_path {hint!r} must be a URL path prefix "
                         f"beginning with '/'")

    _validate_sender(entry, seen_senders)


def _validate_sender(entry: dict, seen_senders: dict[str, str]) -> None:
    sender = entry.get("sender")
    if entry["type"] != "email":
        if sender is not None:
            _fail(entry, "field 'sender' is only valid on type 'email' entries")
        return
    if sender is None:
        _fail(entry, "type 'email' requires a 'sender' (the mailbox allowlist)")
    addresses = sender if isinstance(sender, list) else [sender]
    if not addresses:
        _fail(entry, "field 'sender' must not be an empty list")
    for address in addresses:
        if not isinstance(address, str) or "@" not in address:
            _fail(entry, f"sender {address!r} is not an email address")
        key = address.strip().lower()
        if key in seen_senders:
            # The mailbox allowlist maps address -> source; a duplicate would
            # silently attribute one source's bulletins to another.
            _fail(entry, f"sender {address!r} already registered on "
                         f"{seen_senders[key]!r}")
        seen_senders[key] = entry["id"]


def load_registry(path: str | Path | None = None) -> list[dict]:
    """Parse and validate the registry; raise ValueError naming any bad entry."""
    registry_path = Path(path) if path is not None else REGISTRY_PATH
    with open(registry_path, encoding="utf-8") as fh:
        entries = yaml.safe_load(fh)
    if not isinstance(entries, list):
        # ValueError, not TypeError: the contract is ValueError for any invalid registry
        raise ValueError(f"{registry_path}: top level must be a list of entries")  # noqa: TRY004
    seen_ids: set[str] = set()
    seen_senders: dict[str, str] = {}
    for entry in entries:
        _validate(entry, seen_ids, seen_senders)
        seen_ids.add(entry["id"])
    return entries


def coverage_stats(entries: list[dict]) -> dict:
    """Counts by status, per branch and per tier.

    Returns {"branch": {branch: {status: count}}, "tier": {tier: {status: count}}}
    — enough to state, e.g., "Tier 1: X of Y registered, Z active".
    """
    by_branch: dict[str, dict[str, int]] = {}
    by_tier: dict[int, dict[str, int]] = {}
    for entry in entries:
        for stats, key in ((by_branch, entry["branch"]), (by_tier, entry["tier"])):
            by_status = stats.setdefault(key, {})
            by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1
    return {"branch": by_branch, "tier": by_tier}


def _cell(text: str) -> str:
    """Make a string safe inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _linked_name(entry: dict) -> str:
    urls = entry["urls"]
    url = urls.get("home") or next(iter(urls.values()))
    return f"[{_cell(entry['name'])}]({url})"


def render_doc(entries: list[dict]) -> str:
    """Render the full SOURCES.md markdown (deterministic — no timestamps)."""
    stats = coverage_stats(entries)
    branch_stats = stats["branch"]
    tier_stats = stats["tier"]
    total = len(entries)
    active = sum(by.get("active", 0) for by in branch_stats.values())

    lines = [
        "# Sources",
        "",
        "Living map of every federal source this project ingests, plans to ingest,",
        "or has evaluated; regenerated from `sources/registry.yaml` — do not edit",
        "by hand.",
        "",
        "*Generated by `scripts/sources_doc.py`. Output is a pure function of the",
        "registry (no timestamp), so `tests/test_sources.py` verifies this file",
        "stays in sync.*",
        "",
        "## Coverage summary",
        "",
        "| Branch | Active | Planned | Excluded | Unavailable | Total |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for branch in BRANCHES:
        by = branch_stats.get(branch, {})
        counts = [by.get(status, 0) for status in STATUSES]
        row = " | ".join(str(c) for c in counts)
        lines.append(f"| {_BRANCH_TITLES[branch]} | {row} | {sum(counts)} |")
    totals = [sum(by.get(status, 0) for by in branch_stats.values()) for status in STATUSES]
    lines.append(f"| **Total** | {' | '.join(str(c) for c in totals)} | {total} |")
    lines += ["", f"**{active} of {total} sources active.**", "", "Per tier:", ""]
    for tier in TIERS:
        by = tier_stats.get(tier, {})
        registered = sum(by.values())
        lines.append(
            f"- **Tier {tier}** ({_TIER_SEMANTICS[tier]}): "
            f"{registered} of {total} registered, {by.get('active', 0)} active"
        )

    for branch in BRANCHES:
        branch_entries = [e for e in entries if e["branch"] == branch]
        if not branch_entries:
            continue
        lines += [
            "",
            f"## {_BRANCH_TITLES[branch]}",
            "",
            "| Name | Parent | Tier | Type | Status | Method | Notes |",
            "|---|---|---:|---|---|---|---|",
        ]
        for e in branch_entries:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _linked_name(e),
                        _cell(e["parent_org"]),
                        str(e["tier"]),
                        _cell(e["type"]),
                        _STATUS_BADGES[e["status"]],
                        _cell(e["method"]),
                        _cell(e["notes"]),
                    ]
                )
                + " |"
            )

    return "\n".join(lines) + "\n"

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
TYPES = ("govinfo-collection", "rss", "html-index", "aggregator")
TIERS = (1, 2, 3)
URL_KEYS = ("collection", "feed", "index", "home")

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


def _validate(entry: dict, seen_ids: set[str]) -> None:
    if not isinstance(entry, dict):
        # ValueError, not TypeError: the contract is ValueError for any invalid entry
        raise ValueError(f"registry entry {entry!r}: not a mapping")  # noqa: TRY004
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if missing:
        _fail(entry, f"missing required field(s) {', '.join(missing)}")
    unknown = [k for k in entry if k not in REQUIRED_FIELDS]
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


def load_registry(path: str | Path | None = None) -> list[dict]:
    """Parse and validate the registry; raise ValueError naming any bad entry."""
    registry_path = Path(path) if path is not None else REGISTRY_PATH
    with open(registry_path, encoding="utf-8") as fh:
        entries = yaml.safe_load(fh)
    if not isinstance(entries, list):
        # ValueError, not TypeError: the contract is ValueError for any invalid registry
        raise ValueError(f"{registry_path}: top level must be a list of entries")  # noqa: TRY004
    seen_ids: set[str] = set()
    for entry in entries:
        _validate(entry, seen_ids)
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

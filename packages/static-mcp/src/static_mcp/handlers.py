"""Handler kinds (stage L7, file containment) and result assembly for tools and resources.

Every handler is a function of ``(store, item, validated arguments)``; the
store is the only object that touches the filesystem, and it touches it
read-only. File access — the security core — is :meth:`Store.resolve`:

1. substitute validated arguments into the template;
2. ``candidate = (root / rel).resolve(strict=True)`` — a missing file is
   "not found";
3. require ``candidate.is_relative_to(root.resolve())`` — otherwise raise
   :class:`~static_mcp.errors.ContainmentError`, which the dispatcher logs
   as a security event and answers with ``-32603`` and no path;
4. require a regular file no larger than ``max_file_bytes``;
5. read bytes, decode UTF-8 (JSON via ``json.loads``); a failure is a tool
   error naming nothing but the tool;
6. parsed JSON is cached by ``(path, st_mtime_ns, st_size)`` in a small LRU.

Truncation is never silent: a paged result that would exceed
``max_result_bytes`` shrinks its page and says so; an unpaged result over
the limit is a tool error naming the size and the limit.
"""

from __future__ import annotations

import json
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from static_mcp.errors import ContainmentError
from static_mcp.manifest import Limits, ResourceSpec, TemplateSpec, ToolSpec, substitute

TRUNCATION_NOTE = (
    "The page was reduced to fit the result size limit; reduce limit or page with offset."
)


class NotFound(Exception):
    """The requested file does not exist (or the selected item was not found)."""


class TooLarge(Exception):
    """A file exceeds ``max_file_bytes``. Carries (size, limit)."""

    def __init__(self, size: int, limit: int) -> None:
        super().__init__(f"{size} > {limit}")
        self.size = size
        self.limit = limit


class NotText(Exception):
    """A file is not valid UTF-8, or not valid JSON where JSON was required."""


@dataclass
class ToolOutcome:
    content: list[dict[str, Any]] = field(default_factory=list)
    structured: Any = None
    has_structured: bool = False
    is_error: bool = False

    def result(self) -> dict[str, Any]:
        out: dict[str, Any] = {"content": self.content}
        if self.has_structured:
            out["structuredContent"] = self.structured
        out["isError"] = self.is_error
        return out


def _dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _pretty(value: Any) -> str:
    return json.dumps(value, indent=1, ensure_ascii=False)


class Store:
    """Read-only access to files under one root, with containment and a parsed-JSON cache."""

    def __init__(self, root: str | Path, limits: Limits, *, cache_size: int = 16) -> None:
        self.root = Path(root).resolve()
        self.limits = limits
        self._cache: OrderedDict[tuple[str, int, int], Any] = OrderedDict()
        self._cache_size = cache_size
        self._lock = threading.Lock()

    # -- containment -------------------------------------------------------

    def resolve(self, rel: str) -> Path:
        """Resolve ``rel`` under the root or raise NotFound / ContainmentError / TooLarge."""
        try:
            candidate = (self.root / rel).resolve(strict=True)
        except FileNotFoundError:
            raise NotFound(rel)
        except (OSError, RuntimeError):
            raise NotFound(rel)
        if not candidate.is_relative_to(self.root):
            raise ContainmentError("resolved path escaped the root")
        if not candidate.is_file():
            raise NotFound(rel)
        size = candidate.stat().st_size
        if size > self.limits.max_file_bytes:
            raise TooLarge(size, self.limits.max_file_bytes)
        return candidate

    def read_text(self, rel: str) -> str:
        path = self.resolve(rel)
        try:
            return path.read_bytes().decode("utf-8", "strict")
        except UnicodeDecodeError:
            raise NotText(rel)

    def read_json(self, rel: str) -> Any:
        path = self.resolve(rel)
        st = path.stat()
        key = (str(path), st.st_mtime_ns, st.st_size)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
        try:
            value = json.loads(path.read_bytes().decode("utf-8", "strict"))
        except (UnicodeDecodeError, ValueError, RecursionError):
            raise NotText(rel)
        with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)
            while len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)
        return value

    def list_keys(self, glob: str, name_regex: Any) -> list[str]:
        """Names under the root matching ``glob`` whose basename matches ``name_regex``."""
        keys: list[str] = []
        for path in self.root.glob(glob):
            m = name_regex.fullmatch(path.name)
            if m is None:
                continue
            try:
                resolved = path.resolve(strict=True)
            except OSError:
                continue
            if not resolved.is_relative_to(self.root) or not resolved.is_file():
                continue
            keys.append(m.group("key"))
        return sorted(keys)


# --------------------------------------------------------------------------- tools


def _text(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}


def _error(text: str) -> ToolOutcome:
    return ToolOutcome(content=[_text(text)], is_error=True)


def _size(outcome: ToolOutcome) -> int:
    return len(_dumps(outcome.result()).encode("utf-8"))


def _select(doc: Any, path: str | None) -> Any:
    if path is None:
        return doc
    value = doc
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            raise NotFound(path)
        value = value[part]
    return value


def _apply_filters(items: list[Any], filters: list[dict[str, Any]], args: dict[str, Any]) -> list:
    for f in filters:
        if f["param"] not in args:
            continue
        arg = args[f["param"]]
        if f["kind"] == "exclude_where":
            if arg == f["when"]:
                items = [
                    it
                    for it in items
                    if not (isinstance(it, dict) and it.get(f["field"]) == f["equals"])
                ]
        elif f.get("case_insensitive") and isinstance(arg, str):  # match_field, folded
            wanted = arg.casefold()
            items = [
                it
                for it in items
                if isinstance(it, dict)
                and isinstance(it.get(f["field"]), str)
                and it[f["field"]].casefold() == wanted
            ]
        else:  # match_field
            items = [it for it in items if isinstance(it, dict) and it.get(f["field"]) == arg]
    return items


def _project(items: list[Any], fields: list[str] | None) -> list[Any]:
    if fields is None:
        return items
    return [{k: it[k] for k in fields if k in it} if isinstance(it, dict) else it for it in items]


def _envelope(doc: Any, keys: list[str] | None) -> dict[str, Any]:
    if not keys or not isinstance(doc, dict):
        return {}
    return {k: doc[k] for k in keys if k in doc}


def _finish(
    outcome_structured: dict[str, Any], preamble: str | None, limits: Limits
) -> ToolOutcome:
    """Assemble a structured outcome with its text twin."""
    content: list[dict[str, Any]] = []
    if preamble:
        content.append(_text(preamble))
    content.append(_text(_pretty(outcome_structured)))
    return ToolOutcome(content=content, structured=outcome_structured, has_structured=True)


def _paged(
    items: list[Any],
    envelope: dict[str, Any],
    offset: int,
    limit: int,
    preamble: str | None,
    limits: Limits,
) -> ToolOutcome:
    """Page ``items`` and shrink the page until the result fits ``max_result_bytes``."""
    total = len(items)
    effective = limit
    while True:
        page = items[offset : offset + effective]
        next_offset = offset + effective if offset + effective < total else None
        structured: dict[str, Any] = {
            **envelope,
            "items": page,
            "offset": offset,
            "limit": effective,
            "total": total,
            "next_offset": next_offset,
        }
        if effective < limit:
            structured["truncated"] = True
            structured["truncation_note"] = TRUNCATION_NOTE
        outcome = _finish(structured, preamble, limits)
        if _size(outcome) <= limits.max_result_bytes or effective <= 1:
            if _size(outcome) > limits.max_result_bytes:
                return _error(
                    f"A single item exceeds the result size limit of "
                    f"{limits.max_result_bytes} bytes."
                )
            return outcome
        effective = max(1, effective // 2)


def _bounded(outcome: ToolOutcome, limits: Limits, what: str) -> ToolOutcome:
    size = _size(outcome)
    if size > limits.max_result_bytes:
        return _error(
            f"{what} is {size} bytes, over the result size limit of "
            f"{limits.max_result_bytes} bytes."
        )
    return outcome


def run_tool(store: Store, tool: ToolSpec, args: dict[str, Any]) -> ToolOutcome:
    """Run ``tool`` with validated ``args``. Raises ContainmentError only on a security event."""
    h = tool.handler
    kind = h["kind"]
    limits = store.limits
    preamble = tool.preamble

    if kind == "static_text":
        content = [_text(preamble)] if preamble else []
        content.append(_text(substitute(h["text"], args)))
        return _bounded(ToolOutcome(content=content), limits, "The text")

    if kind == "text_file":
        try:
            text = store.read_text(substitute(h["file"], args))
        except NotFound:
            return _error(substitute(h["not_found"], args))
        except TooLarge as exc:
            return _error(
                f"The file is {exc.size} bytes, over the file size limit of {exc.limit} bytes."
            )
        except NotText:
            return _error(f"The file behind {tool.name} is not readable as UTF-8 text.")
        content = [_text(preamble)] if preamble else []
        content.append(_text(text))
        return _bounded(ToolOutcome(content=content), limits, "The file")

    if kind == "file_listing":
        keys = store.list_keys(h["glob"], h["name_regex"])
        if h["order"] == "desc":
            keys.reverse()
        if h["page"]:
            return _paged(
                keys, {}, args[h["page"]["offset"]], args[h["page"]["limit"]], preamble, limits
            )
        return _bounded(_finish({"items": keys, "total": len(keys)}, preamble, limits), limits,
                        "The listing")

    # json_file
    try:
        doc = store.read_json(substitute(h["file"], args))
    except NotFound:
        return _error(substitute(h["not_found"], args))
    except TooLarge as exc:
        return _error(
            f"The file is {exc.size} bytes, over the file size limit of {exc.limit} bytes."
        )
    except NotText:
        return _error(f"The file behind {tool.name} is not readable as JSON.")

    if h["select"] is None:
        return _bounded(_finish(doc, preamble, limits), limits, "The document")
    try:
        selected = _select(doc, h["select"])
    except NotFound:
        return _error(substitute(h["not_found"], args))
    envelope = _envelope(doc, h["envelope"])

    if not isinstance(selected, list):
        item = _project([selected], h["fields"])[0]
        return _bounded(_finish({**envelope, "item": item}, preamble, limits), limits, "The item")

    items = _apply_filters(list(selected), h["filters"], args)
    if h["order"] == "desc":
        items.reverse()
    if h["find"]:
        wanted = args.get(h["find"]["param"])
        for it in items:
            if isinstance(it, dict) and it.get(h["find"]["field"]) == wanted:
                item = _project([it], h["fields"])[0]
                return _bounded(
                    _finish({**envelope, "item": item}, preamble, limits), limits, "The item"
                )
        return _error(substitute(h["not_found"], args))
    items = _project(items, h["fields"])
    if h["page"]:
        return _paged(
            items, envelope, args[h["page"]["offset"]], args[h["page"]["limit"]], preamble, limits
        )
    return _bounded(
        _finish({**envelope, "items": items, "total": len(items)}, preamble, limits),
        limits,
        "The list",
    )


# --------------------------------------------------------------------------- resources


def read_resource(store: Store, item: ResourceSpec | TemplateSpec, uri: str, values: dict) -> dict:
    """Read one resource; returns a text contents block. Raises NotFound/TooLarge/NotText."""
    text = store.read_text(substitute(item.file, values))
    return {"uri": uri, "mimeType": item.mime_type, "text": text}

"""Handler kinds (A.6 #2): every kind, every filter, find, paging, projection, not_found,
JSON cache invalidation, truncation; plus the file-containment core (A.6 #6, store level)."""

from __future__ import annotations

import json
import os

import pytest

from static_mcp.errors import ContainmentError
from static_mcp.handlers import TRUNCATION_NOTE, NotFound, Store, run_tool
from static_mcp.manifest import Limits, validate_arguments


def call(store, manifest, name, **args):
    tool = manifest.tools_by_name[name]
    return run_tool(store, tool, validate_arguments(tool, args))


def test_static_text(store, manifest):
    out = call(store, manifest, "about")
    assert out.is_error is False
    assert out.content == [{"type": "text", "text": "See https://fixture.example.org/ for documentation."}]
    assert out.has_structured is False


def test_text_file_with_preamble_and_not_found(store, manifest):
    out = call(store, manifest, "get_page", date="2026-01-01")
    assert out.content[0]["text"] == "Page text follows verbatim."
    assert out.content[1]["text"].startswith("# Page for 2026-01-01")
    missing = call(store, manifest, "get_page", date="2030-01-01")
    assert missing.is_error is True
    assert missing.content == [{"type": "text", "text":
                                "No page exists for 2030-01-01. Call list_pages for available dates."}]


def test_text_file_directory_is_not_found(store, manifest):
    # "pages" exists but is a directory; the regular-file rule turns it into not_found.
    out = call(store, manifest, "get_note", slug="alpha")
    assert out.is_error is False
    os.mkdir(store.root / "notes" / "dir")
    out = call(store, manifest, "get_note", slug="dir")
    assert out.is_error is True and "No note named dir." in out.content[0]["text"]


def test_text_file_not_utf8_is_a_tool_error(store, manifest):
    (store.root / "notes" / "bin.md").write_bytes(b"\xff\xfe\x00bad")
    out = call(store, manifest, "get_note", slug="bin")
    assert out.is_error is True
    assert "get_note" in out.content[0]["text"]
    assert "bin.md" not in out.content[0]["text"]


def test_json_file_whole_document_and_dotted_select(store, manifest):
    whole = call(store, manifest, "get_index")
    assert whole.structured["title"] == "Example index"
    assert json.loads(whole.content[0]["text"]) == whole.structured
    meta = call(store, manifest, "get_meta")
    assert meta.structured == {"item": {"value": 42}}


def test_json_file_filters_projection_order_and_paging(store, manifest):
    out = call(store, manifest, "list_entries")
    s = out.structured
    assert s["title"] == "Example index" and s["generated"] == "2026-01-03T00:00:00Z"
    assert [e["slug"] for e in s["items"]] == ["zeta", "delta", "beta", "alpha"]  # drafts out, desc
    assert set(s["items"][0]) == {"slug", "kind", "title"}  # projection
    assert (s["offset"], s["limit"], s["total"], s["next_offset"]) == (0, 10, 4, None)

    with_drafts = call(store, manifest, "list_entries", include_drafts=True)
    assert with_drafts.structured["total"] == 6
    notes = call(store, manifest, "list_entries", kind="note")
    assert [e["slug"] for e in notes.structured["items"]] == ["beta", "alpha"]
    page2 = call(store, manifest, "list_entries", offset=1, limit=2)
    assert [e["slug"] for e in page2.structured["items"]] == ["delta", "beta"]
    assert page2.structured["next_offset"] == 3
    last = call(store, manifest, "list_entries", offset=3, limit=2)
    assert last.structured["next_offset"] is None
    beyond = call(store, manifest, "list_entries", offset=100)
    assert beyond.structured["items"] == [] and beyond.structured["total"] == 4


def test_json_file_find_and_not_found(store, manifest):
    found = call(store, manifest, "get_entry", slug="delta")
    assert found.structured == {"title": "Example index",
                                "item": {"slug": "delta", "kind": "page", "draft": False,
                                         "title": "Delta", "words": 40}}
    missing = call(store, manifest, "get_entry", slug="nope")
    assert missing.is_error and missing.content[0]["text"] == "No entry named nope."


def test_json_file_select_missing_key_is_not_found(store, manifest):
    (store.root / "index.json").write_text('{"title": "x"}', encoding="utf-8")
    out = call(store, manifest, "list_entries")
    assert out.is_error and out.content[0]["text"] == "The index is not available."


def test_json_file_invalid_json_is_a_tool_error(store, manifest):
    (store.root / "index.json").write_text("{nope", encoding="utf-8")
    out = call(store, manifest, "get_index")
    assert out.is_error and "not readable as JSON" in out.content[0]["text"]


def test_file_listing_desc_and_paged(store, manifest):
    out = call(store, manifest, "list_pages")
    # README.txt and the planted symlink (which points outside the root) are excluded.
    assert out.structured["items"] == ["2026-01-03", "2026-01-02", "2026-01-01"]
    assert out.structured["total"] == 3 and out.structured["next_offset"] is None
    page = call(store, manifest, "list_pages", offset=1, limit=1)
    assert page.structured["items"] == ["2026-01-02"] and page.structured["next_offset"] == 2


def test_json_cache_invalidates_on_mtime_change(store, manifest):
    first = call(store, manifest, "get_meta").structured
    assert first == {"item": {"value": 42}}
    path = store.root / "index.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["meta"]["nested"]["value"] = 43
    path.write_text(json.dumps(data), encoding="utf-8")
    st = path.stat()
    os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000))
    assert call(store, manifest, "get_meta").structured == {"item": {"value": 43}}


def test_json_cache_is_used_between_calls(store, manifest):
    call(store, manifest, "get_meta")
    assert len(store._cache) == 1
    call(store, manifest, "get_index")
    assert len(store._cache) == 1  # same file, same key


def test_truncation_is_disclosed(store, manifest):
    out = call(store, manifest, "get_big")  # limit 5000 > max_result_bytes 65536 allows
    s = out.structured
    assert out.is_error is False
    assert s["truncated"] is True and s["truncation_note"] == TRUNCATION_NOTE
    assert s["limit"] < 5000 and len(s["items"]) == s["limit"]
    assert s["next_offset"] == s["limit"] and s["total"] == 3000
    assert len(json.dumps(out.result())) <= manifest.limits.max_result_bytes


def test_text_file_over_result_limit_is_a_tool_error(site, manifest):
    small = Store(site, Limits(max_file_bytes=manifest.limits.max_file_bytes, max_result_bytes=64))
    out = call(small, manifest, "get_page", date="2026-01-01")
    assert out.is_error and "over the result size limit of 64 bytes" in out.content[0]["text"]


def test_file_over_file_limit_is_a_tool_error(site, manifest):
    small = Store(site, Limits(max_file_bytes=10, max_result_bytes=65536))
    out = call(small, manifest, "get_page", date="2026-01-01")
    assert out.is_error
    assert "over the file size limit of 10 bytes" in out.content[0]["text"]


# --- containment (A.6 #6, store level) ------------------------------------------


def test_resolve_stops_traversal_absolute_and_symlink(store, tmp_path):
    outside = tmp_path / "outside.txt"
    assert outside.exists()
    with pytest.raises(ContainmentError):
        store.resolve("../outside.txt")
    with pytest.raises(ContainmentError):
        store.resolve(str(outside))  # absolute path joins as itself
    with pytest.raises(ContainmentError):
        store.resolve("notes/escape.md")  # planted symlink
    with pytest.raises(NotFound):
        store.resolve("../does-not-exist")
    assert store.resolve("guide.txt").is_relative_to(store.root)


def test_symlink_inside_root_is_allowed(store):
    (store.root / "notes" / "link.md").symlink_to(store.root / "notes" / "alpha.md")
    assert store.read_text("notes/link.md").startswith("# Alpha")


def test_match_field_case_insensitive_is_exact_equality_after_casefold(site, store, manifest):
    """The flag folds case on both sides; it never becomes a substring or a
    pattern match, and a non-string field never matches."""
    from support_static_mcp import manifest_dict

    from static_mcp.manifest import parse_manifest

    data = manifest_dict()
    data["params"]["kind"] = {"type": "string", "pattern": "^[A-Za-z]{1,16}$",
                              "description": "k"}
    tool = next(t for t in data["tools"] if t["name"] == "list_entries")
    tool["handler"]["filters"] = [{"param": "kind", "match_field": "kind",
                                   "case_insensitive": True}]
    folded = parse_manifest(data)
    folded_store = Store(site, folded.limits)
    notes = call(folded_store, folded, "list_entries", kind="NOTE", include_drafts=True)
    assert notes.structured["total"] > 0
    assert all(item["kind"] == "note" for item in notes.structured["items"])
    assert call(folded_store, folded, "list_entries", kind="Not",
                include_drafts=True).structured["total"] == 0          # not a prefix match
    strict = call(store, manifest, "list_entries", kind="note", include_drafts=True)
    assert strict.structured["total"] == notes.structured["total"]

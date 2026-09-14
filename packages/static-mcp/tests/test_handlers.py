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
    assert out.content[0]["text"].startswith("# Page for 2026-01-01")   # payload first
    assert out.content[-1]["text"] == "Page text follows verbatim."    # the disclosure last
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


# ------------------------------------------------------- block order / schema --


def test_payload_is_the_first_block_and_the_preamble_the_last(store, manifest):
    """Every handler kind: a client that reads content[0] reads the data."""
    listing = call(store, manifest, "list_entries", include_drafts=True)
    assert json.loads(listing.content[0]["text"]) == listing.structured
    assert len(listing.content) == 1                     # no preamble on this fixture tool
    from support_static_mcp import manifest_dict

    from static_mcp.manifest import parse_manifest

    data = manifest_dict()
    next(t for t in data["tools"] if t["name"] == "list_entries")["preamble"] = "Index follows."
    with_preamble = parse_manifest(data)
    listed = call(Store(store.root, with_preamble.limits), with_preamble, "list_entries",
                  include_drafts=True)
    assert json.loads(listed.content[0]["text"]) == listed.structured
    assert listed.content[-1]["text"] == "Index follows."
    about = call(store, manifest, "about")
    assert about.content[0]["text"] == manifest.tools_by_name["about"].handler["text"]
    report = call(store, manifest, "get_report")
    assert report.content[0]["text"].startswith("# Report")
    assert report.content[-1]["text"] == "Report text follows verbatim."


def test_output_schema_only_where_results_are_structured(manifest):
    defs = {t["name"]: t for t in (tool.definition() for tool in manifest.tools)}
    assert "outputSchema" not in defs["get_page"]            # text_file
    assert "outputSchema" not in defs["about"]               # static_text
    paged = defs["list_entries"]["outputSchema"]
    assert paged["type"] == "object" and paged["additionalProperties"] is True
    assert paged["required"] == ["items", "offset", "limit", "total", "next_offset"]
    assert defs["get_entry"]["outputSchema"]["required"] == ["item"]
    assert defs["list_pages"]["outputSchema"]["properties"]["items"]["items"] == {"type": "string"}
    assert defs["get_index"]["outputSchema"] == {"type": "object", "additionalProperties": True}


def test_structured_results_satisfy_their_own_output_schema(store, manifest):
    """Required keys present and typed as declared, for every structured tool."""
    def check(value, schema):
        assert isinstance(value, dict)
        for key in schema.get("required", []):
            assert key in value, key
        for key, sub in schema.get("properties", {}).items():
            if key not in value:
                continue
            kinds = sub["type"] if isinstance(sub["type"], list) else [sub["type"]]
            py = {"integer": int, "string": str, "boolean": bool, "array": list,
                  "object": dict, "null": type(None)}
            assert any(isinstance(value[key], py[k]) for k in kinds), (key, value[key])
    for name, args in (("list_entries", {"include_drafts": True}), ("get_entry", {"slug": "delta"}),
                       ("list_pages", {}), ("get_index", {}), ("get_meta", {})):
        tool = manifest.tools_by_name[name]
        out = call(store, manifest, name, **args)
        assert out.has_structured, name
        check(out.structured, tool.output_schema)


def test_descriptions_of_preambled_tools_say_the_order(manifest):
    from static_mcp.manifest import ORDER_SENTENCE

    for tool in manifest.tools:
        assert (ORDER_SENTENCE in tool.description) == (tool.preamble is not None), tool.name
        if tool.preamble:
            assert tool.description.index(ORDER_SENTENCE) < tool.description.index("Returned text")


# ------------------------------------------------------------- sections --


def test_text_file_sections_slice_verbatim(store, manifest):
    whole = call(store, manifest, "get_report").content[0]["text"]
    one = call(store, manifest, "get_report", part="one").content[0]["text"]
    assert one.startswith("## 1. First part\n") and one in whole
    assert "### 1.1 Sub" in one and "## not a heading" in one   # the fenced line is data, kept
    assert "## 2. Second part" not in one                        # stops at the next level-2 heading
    two = call(store, manifest, "get_report", part="two").content[0]["text"]
    assert two == "## 2. Second part\n\nBeta text.\n\n"
    closing = call(store, manifest, "get_report", part="closing").content[0]["text"]
    assert closing == "## Closing\n\nDone.\n"                    # last block runs to the end
    front = call(store, manifest, "get_report", part="front").content[0]["text"]
    assert front == "# Report\n\nFront matter line.\n\n"         # before the first level-2 heading
    assert whole == front + one + two + closing                 # the slices are the file


def test_text_file_section_absent_is_a_tool_error_naming_what_is_present(site, manifest):
    (site / "report.md").write_text("# Report\n\n## 2. Second part\n\nOnly two.\n", encoding="utf-8")
    fresh = Store(site, manifest.limits)
    out = call(fresh, manifest, "get_report", part="closing")
    assert out.is_error and "No section closing" in out.content[0]["text"]
    assert "present: front, two" in out.content[0]["text"]


def test_sections_manifest_rules():
    from support_static_mcp import build_manifest, manifest_dict

    from static_mcp.errors import ManifestError
    from static_mcp.manifest import parse_manifest

    def with_sections(sections, **param_over):
        data = manifest_dict()
        if param_over:
            data["params"]["part"] = {**data["params"]["part"], **param_over}
        tool = next(t for t in data["tools"] if t["name"] == "get_report")
        tool["handler"]["sections"] = sections
        return data

    good = with_sections({"param": "part", "level": 2, "map": {"front": None, "one": "1. ",
                                                              "two": "2. ", "closing": "Closing"}})
    assert parse_manifest(good).tools_by_name["get_report"].handler["sections"]["level"] == 2
    for bad, fragment in (
        (with_sections({"param": "part", "level": 2, "map": {"front": None, "one": "1. "}}),
         "keys must equal"),
        (with_sections({"param": "part", "level": 9, "map": good["tools"][-1]["handler"]["sections"]["map"]}),
         "level"),
        (with_sections({"param": "part", "level": 2, "map": {"front": None, "one": None,
                                                             "two": "2. ", "closing": "C"}}),
         "at most one"),
        (with_sections({"param": "part", "level": 2, "map": {"front": None, "one": "",
                                                             "two": "2. ", "closing": "C"}}),
         "non-empty"),
        (with_sections({"param": "nope", "level": 2, "map": {}}), "undeclared"),
    ):
        with pytest.raises(ManifestError) as exc:
            parse_manifest(bad)
        assert fragment in str(exc.value), fragment
    no_enum = with_sections(good["tools"][-1]["handler"]["sections"])
    del no_enum["params"]["part"]["enum"]
    with pytest.raises(ManifestError, match="with an enum"):
        parse_manifest(no_enum)
    assert build_manifest  # imported for symmetry with the other helpers

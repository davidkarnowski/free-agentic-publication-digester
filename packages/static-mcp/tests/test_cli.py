"""CLI (A.6 #9): check exit codes; serve refuses a missing root; default host 127.0.0.1."""

from __future__ import annotations

import io
import json

from support_static_mcp import EXAMPLE_MANIFEST_PATH, MANIFEST_PATH, manifest_dict

from static_mcp.cli import _parser, main


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    code = main(argv, stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def test_check_passes_for_fixture_and_example(site):
    code, out, _ = _run(["check", "--manifest", str(MANIFEST_PATH), "--root", str(site)])
    assert code == 0 and out.endswith("ok\n") and "9 tool(s)" in out
    code, out, _ = _run(["check", "--manifest", str(EXAMPLE_MANIFEST_PATH)])
    assert code == 0


def test_check_fails_on_invalid_manifest(tmp_path):
    bad = tmp_path / "bad.json"
    data = manifest_dict()
    data["http"]["max_concurrency"] = 1000
    bad.write_text(json.dumps(data), encoding="utf-8")
    code, _, err = _run(["check", "--manifest", str(bad)])
    assert code == 2 and "manifest error: http: max_concurrency" in err


def test_check_fails_on_missing_static_resource_file(site):
    (site / "guide.txt").unlink()
    code, _, err = _run(["check", "--manifest", str(MANIFEST_PATH), "--root", str(site)])
    assert code == 2 and "resource guide: file missing: guide.txt" in err


def test_serve_refuses_missing_root(tmp_path):
    code, _, err = _run(["serve", "--manifest", str(MANIFEST_PATH),
                         "--root", str(tmp_path / "absent"), "--port", "0"])
    assert code == 2 and "root is not a directory" in err


def test_serve_refuses_missing_resource_file(site):
    (site / "index.json").unlink()
    code, _, err = _run(["serve", "--manifest", str(MANIFEST_PATH), "--root", str(site),
                         "--port", "0"])
    assert code == 2 and "resource index: file missing" in err


def test_default_host_is_loopback():
    args = _parser().parse_args(["serve", "--manifest", "m", "--root", "r"])
    assert args.host == "127.0.0.1" and args.port == 8080


def test_card_registry_and_describe_commands():
    code, out, _ = _run(["card", "--manifest", str(MANIFEST_PATH)])
    assert code == 0 and json.loads(out)["remotes"][0]["url"] == "https://fixture.example.org/mcp"
    code, out, _ = _run(["registry-json", "--manifest", str(MANIFEST_PATH),
                         "--schema-url", "https://example.org/s.json"])
    assert code == 0 and json.loads(out)["$schema"] == "https://example.org/s.json"
    code, out, _ = _run(["describe", "--manifest", str(MANIFEST_PATH)])
    assert code == 0 and "| `get_page` |" in out

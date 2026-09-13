"""Command line: ``static-mcp serve | check | card | registry-json | describe``.

``serve`` validates the manifest, refuses to start if the root is missing
or any static resource file is missing (fail loud on missing
configuration), and binds ``127.0.0.1`` unless told otherwise: binding all
interfaces is an explicit choice.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any

from static_mcp import __version__
from static_mcp.card import build_card, build_registry_server_json, describe_markdown
from static_mcp.errors import ManifestError
from static_mcp.handlers import NotFound, Store, TooLarge
from static_mcp.manifest import Manifest, load_manifest
from static_mcp.server import make_server


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="static-mcp", description=__doc__)
    p.add_argument("--version", action="version", version=f"static-mcp {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("serve", help="validate the manifest and the root, then serve")
    s.add_argument("--manifest", required=True)
    s.add_argument("--root", required=True)
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8080)

    c = sub.add_parser("check", help="validate a manifest (and, with --root, its static files)")
    c.add_argument("--manifest", required=True)
    c.add_argument("--root")

    k = sub.add_parser("card", help="print the MCP Server Card JSON")
    k.add_argument("--manifest", required=True)

    r = sub.add_parser("registry-json", help="print the MCP Registry server.json")
    r.add_argument("--manifest", required=True)
    r.add_argument("--schema-url", required=True)

    d = sub.add_parser("describe", help="print a Markdown description of tools and resources")
    d.add_argument("--manifest", required=True)
    return p


def check_root(manifest: Manifest, root: str) -> list[str]:
    """Return the problems with ``root`` for ``manifest`` (empty list = fine)."""
    problems: list[str] = []
    root_path = Path(root)
    if not root_path.is_dir():
        return [f"root is not a directory: {root}"]
    store = Store(root_path, manifest.limits)
    for resource in manifest.resources:
        try:
            store.resolve(resource.file)
        except NotFound:
            problems.append(f"resource {resource.name}: file missing: {resource.file}")
        except TooLarge as exc:
            problems.append(f"resource {resource.name}: file is {exc.size} bytes > {exc.limit}")
        except Exception as exc:  # noqa: BLE001 - reported, never raised past the CLI
            problems.append(f"resource {resource.name}: {type(exc).__name__}")
    return problems


def _summary(manifest: Manifest, out: IO[str]) -> None:
    out.write(
        f"{manifest.server.name} {manifest.server.version}: "
        f"{len(manifest.tools)} tool(s), {len(manifest.resources)} resource(s), "
        f"{len(manifest.templates)} template(s); endpoint {manifest.endpoint_url}; "
        f"versions {', '.join(manifest.all_versions)}\n"
    )


def main(argv: Sequence[str] | None = None, *, stdout: IO[str] | None = None,
         stderr: IO[str] | None = None) -> int:
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    args = _parser().parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
    except ManifestError as exc:
        err.write(f"manifest error: {exc}\n")
        return 2

    if args.command == "check":
        _summary(manifest, out)
        if args.root:
            problems = check_root(manifest, args.root)
            for problem in problems:
                err.write(f"root error: {problem}\n")
            if problems:
                return 2
        out.write("ok\n")
        return 0

    if args.command == "card":
        _dump(build_card(manifest), out)
        return 0

    if args.command == "registry-json":
        _dump(build_registry_server_json(manifest, args.schema_url), out)
        return 0

    if args.command == "describe":
        out.write(describe_markdown(manifest))
        return 0

    problems = check_root(manifest, args.root)
    for problem in problems:
        err.write(f"root error: {problem}\n")
    if problems:
        return 2
    store = Store(args.root, manifest.limits)
    server = make_server(manifest, store, args.host, args.port)
    _summary(manifest, err)
    err.write(f"serving on http://{args.host}:{server.server_address[1]}{manifest.endpoint_path}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def _dump(value: Any, out: IO[str]) -> None:
    out.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")

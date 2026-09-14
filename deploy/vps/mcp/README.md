# FAPD MCP manifest

`fapd.manifest.json` is FAPD's configuration of the generic `static-mcp`
server (`packages/static-mcp/`): identity (master plan §8.4:
`info.fapd/fapd`, version `1.0.0`), the HTTP allow-lists and limits, and
the eight tools, five resources and three resource templates the service
answers from the published site. It is the **single source of truth**
for the MCP identity — Phase 4C generates the Server Card, the catalog
entries and the `agents.html` section from it, and drift tests fail if
they differ. Guide: `docs/mcp-server.md`.

This directory is bind-mounted read-only into `fapd-mcp` as
`/etc/static-mcp/` (a directory, never a file: rsync replaces files with
new inodes). The container starts with
`--manifest /etc/static-mcp/fapd.manifest.json`.

- Validate: `PYTHONPATH=packages/static-mcp/src uv run python -m static_mcp check --manifest deploy/vps/mcp/fapd.manifest.json --root site`
- Tests: `uv run pytest -q tests/test_mcp_manifest.py` (every field
  checked against a site the real renderer builds).
- `deploy/dev/mcp/fapd.manifest.json` is the dev-stack copy and differs
  in `http.allowed_hosts` only (`localhost`, `127.0.0.1` added); a test
  pins that.
- Change the served surface → edit here, bump `server.version`, run the
  tests; a new handler kind is a package change with a security review
  (`docs/mcp-server.md` §9).

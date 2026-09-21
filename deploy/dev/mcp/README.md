# Dev-stack MCP manifest

> **2026-09-21 — `deploy/vps/nginx/` moved out of this repository.** Operator ruling:
> the fapd-web nginx config carries probe-refusal rules that state exactly what is and
> is not refused, and this repository is public. It now lives in the operator's private
> host tree and is mounted on the box from `/opt/edge/fapd-web`. References to
> `deploy/vps/nginx/` below are historical; git history retains the old config.

`fapd.manifest.json` is a copy of `deploy/vps/mcp/fapd.manifest.json`
that adds `localhost` and `127.0.0.1` to `http.allowed_hosts`, so the
service accepts `http://localhost:8080/mcp` through the dev web
container and `http://127.0.0.1:8080/mcp` when `static-mcp serve` runs
directly on the laptop (the real-client check in
`docs/mcp-server.md` §8). `tests/test_mcp_manifest.py` asserts the two
files differ in that field only — edit the production manifest first,
then re-derive this one.

The dev compose mounts this directory read-only at `/etc/static-mcp/`
in `fapd-dev-mcp`; `deploy/vps/nginx/rehearse.sh` mounts it into its
throwaway MCP container for the same reason.

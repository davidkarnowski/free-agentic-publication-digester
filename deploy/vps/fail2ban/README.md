# fail2ban jail for the MCP endpoint

One host jail, `fapd-mcp`, reading `fapd-web`'s dedicated `/mcp` access
log (`/opt/fapd/logs/mcp-access.log`, bind-mounted from the container;
its **first field is the true client address** from `X-Real-IP`, because
a ban keyed on the edge proxy's internal address would ban nothing).
Rationale and thresholds: `docs/ops/plan-2026-09-13-security-review.md`
§4 — generous on purpose (20 rejected requests in 10 minutes → 1 h,
doubling to at most 1 day), because MCP clients often share egress and
nginx's `limit_req`/`limit_conn` are the primary control.

| File | Installed as | Role |
|---|---|---|
| `filter.d/fapd-mcp.conf` | `/etc/fail2ban/filter.d/fapd-mcp.conf` | counts `POST /mcp` lines with status 400, 403, 405, 413, 415 or 429; **not** 404 (a modern client probing an unimplemented method legitimately gets 404/`-32601`) |
| `jail.d/fapd-mcp.local` | `/etc/fail2ban/jail.d/fapd-mcp.local` | polling backend, `iptables-allports` in the `DOCKER-USER` chain (published container ports never traverse `INPUT`), explicit thresholds (the `[DEFAULT]` section is the cohabitant's) |
| `logrotate.d/fapd-mcp` | `/etc/logrotate.d/fapd-mcp` | daily, keep 7, `copytruncate` (the container is not signalled by host logrotate; the polling backend follows truncation) |

**Installation is operator-gated** (checkpoint C-6, after `/mcp`
verifies in Phase 5): `scripts/staged/2026-09-14-install-fapd-mcp-jail.sh`
copies the three files (additive — nothing else under `/etc/fail2ban`
is touched), runs `fail2ban-client -t` **before** `reload`, and
verifies the jail is reported, the `f2b-fapd-mcp` chain exists in
`iptables -S DOCKER-USER` (load-bearing: on 2026-09-13 three existing
jails ran with no chain), and `fail2ban-regex` matches the log. Never
run by an agent.

Pinned by `tests/test_fail2ban_filter.py` (a Python re-implementation
of the match, since fail2ban is not installed on the development
machine) and rehearsed by `deploy/vps/nginx/rehearse.sh` rows M16–M17.
Manual unban, for a legitimate shared-egress client that reports being
blocked: `sudo fail2ban-client set fapd-mcp unbanip <addr>` (OPS-GUIDE).

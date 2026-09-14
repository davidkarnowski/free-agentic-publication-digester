# FAPD ops guide — read-only health runbook

*Never writes anything. Anything that would — restarts, deploys, config
flips — lives behind the authorization gate in
[AGENT-VPS-SERVICING-GUIDE.md](AGENT-VPS-SERVICING-GUIDE.md) §4.
Last reviewed: 2026-09-14 (agent-discovery Phase 5: the Phase 3 and
MCP blocks are live checks now, every command run against the box after
the deploy; the jail commands wait on checkpoint C-6. Running the
verification probes from an address the box's existing jails do not
ignore banned the operator's own address once — see the WORKLOG).*

## Local checks (the operator machine)

**Read this first: on a machine that does not run the pipeline, this
block describes a development database, not production.** Checked
2026-08-07: the operator machine's `fapd.db` had no collector activity
since 2026-07-30 and `llm_ledger.db` had not been written since
2026-07-30, while production ran normally on the box. Token spend by
purpose and backend is currently auditable **only** on the VPS. Treat a
green local block as evidence about your laptop.

```sh
# Digest freshness — newest rendered day and newest complete day
ls digests/*.md | tail -3
uv run python - <<'EOF'
from fapd import db
conn = db.connect()
print("newest extracted day:", conn.execute(
    "SELECT MAX(p.date_issued) FROM packages p"
    " JOIN extracted_texts e USING (package_id)").fetchone()[0])
EOF

# Request-budget posture (per client class, vs GUIDE §4 caps)
uv run python scripts/audit.py

# Token spend today, by purpose and backend
sqlite3 -readonly data/llm_ledger.db "SELECT backend, substr(purpose,1,instr(purpose||':',':')-1),
  COUNT(*), SUM(input_tokens), SUM(output_tokens) FROM llm_calls
  WHERE ts_utc >= date('now') GROUP BY 1,2"

# Validation status of the last render: re-run the render for the newest
# digest date — deterministic and zero-LLM; a PASS costs nothing.
uv run python scripts/digest.py --date <newest> 2>&1 | tail -3

# Collector liveness
sqlite3 -readonly data/fapd.db "SELECT worker, last_ok_at, consecutive_errors
  FROM collector_state ORDER BY worker"
```

## VPS checks (read-only)

Coordinates come from `deploy/vps/deploy.env` (gitignored — copy
`deploy.env.example`, `chmod 0600`). `vps-ssh.sh` resolves them, so no
command below carries a host. Network egress may need the tool sandbox
disabled.

```sh
curl -sI https://fapd.info | head -1                 # HTTP/2 200

deploy/vps/scripts/vps-ssh.sh 'sudo docker ps --format "{{.Names}}\t{{.Status}}" | grep fapd'
deploy/vps/scripts/vps-ssh.sh 'sudo docker inspect fapd-web --format "{{json .NetworkSettings.Networks}}"'
#   ^ exactly fapd_edge, nothing else
deploy/vps/scripts/vps-ssh.sh 'sudo certbot certificates 2>/dev/null | grep -A3 fapd.info'
```

### Is the repo-managed web config live?

`fapd-web` runs `deploy/vps/nginx/` (agent-discovery plan Phase 3;
live since 2026-09-14; before that the stock config answered without a
`Link` header and with `nginx/1.x` in its 404 body). Three
curls through the edge, all read-only:

```sh
curl -sI https://fapd.info/ | grep -i '^link:'      # the five §8.3 rels, one header
curl -sS -o /dev/null -w '%{http_code} %{content_type}\n' \
  https://fapd.info/.well-known/api-catalog          # 200 application/linkset+json
curl -sS https://fapd.info/.well-known/oauth-authorization-server | head -c 200
#   ^ a 404 whose JSON body says "not offered" — the signpost, not nginx's page
curl -sI https://fapd.info/ | grep -ic '^strict-transport-security:'   # exactly 1 (the edge's)
```

A `Link` header missing after a deploy means the reload did not happen
(deploy.sh runs `nginx -t && nginx -s reload` in `fapd-web` after
`up -d`; a config-only change is otherwise invisible to compose). Two
`Strict-Transport-Security` headers means someone duplicated an
edge-owned header in `fapd-web` — `tests/test_web_conf.py` pins against
it. Before any change under `deploy/vps/nginx/` reaches the box,
`deploy/vps/nginx/rehearse.sh` runs locally and must print `SUCCESS`
(the cadence table).

### The MCP service

`fapd-mcp` and `fapd-web`'s `/mcp` gate (agent-discovery Phase 4B;
live since 2026-09-14). Guide: `docs/mcp-server.md`. All read-only.
Do not run the adversarial probes of the Phase 5 checklist from an
address the box's existing nginx jails do not ignore: one of them bans
on a single `/.git` request.

```sh
deploy/vps/scripts/vps-ssh.sh 'sudo docker ps --format "{{.Names}}\t{{.Status}}" | grep fapd-mcp'
#   ^ Up … (healthy) — the healthcheck is the package Dockerfile's GET /healthz
deploy/vps/scripts/vps-ssh.sh 'sudo docker port fapd-mcp'
#   ^ prints NOTHING. Any output is a finding: a published port bypasses ufw.
deploy/vps/scripts/vps-ssh.sh 'sudo docker inspect fapd-mcp --format "{{json .NetworkSettings.Networks}}"'
#   ^ exactly fapd_mcp, nothing else; fapd-web lists fapd_edge and fapd_mcp
deploy/vps/scripts/vps-ssh.sh 'sudo docker logs --tail 20 fapd-mcp'  # JSON lines; no IPs, no bodies

# A modern server/discover through the edge: 200 and serverInfo.name info.fapd/fapd
curl -sS -w '\n%{http_code}\n' -X POST https://fapd.info/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
  -d '{"jsonrpc":"2.0","id":"health","method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"fapd-health","version":"1"},"io.modelcontextprotocol/clientCapabilities":{}}}}' \
  | tail -c 400
curl -sI https://fapd.info/mcp | head -1                # 405: POST only (JSON signpost body)

# The fail2ban jail (after checkpoint C-6): running, WITH a chain
deploy/vps/scripts/vps-ssh.sh 'sudo fail2ban-client status fapd-mcp'
deploy/vps/scripts/vps-ssh.sh 'sudo iptables -S DOCKER-USER | grep -c f2b-fapd-mcp'   # >= 1
deploy/vps/scripts/vps-ssh.sh 'sudo tail -5 /opt/fapd/logs/mcp-access.log'
#   ^ first field is a client address (never the edge's 172.x); no request bodies
```

A 503 with the "temporarily unavailable" JSON means `fapd-mcp` is down
while the site is up — the variable upstream working as designed; check
the container. A jail reported by `fail2ban-client` but absent from
`iptables -S DOCKER-USER` bans nothing (three cohabitant jails were in
that state on 2026-09-13). **Manual unban** for a legitimate
shared-egress client that reports being blocked is an operator-gated
write: `sudo fail2ban-client set fapd-mcp unbanip <addr>`.

### Did the evidence reach the repository?

**A digest that is live on the site but absent from `origin/main` is a
finding, not a pass.** Those are two separate gates and they fail
separately: on 2026-08-07 the digest rendered, validated and served for
thirteen hours while its evidence commit sat rejected in the container,
and the `eod` row read a clean success throughout (F-021).

```sh
# 0 = everything published. >0 = a commit is stranded in the container.
deploy/vps/scripts/vps-ssh.sh 'sudo docker exec fapd-backend sh -lc \
  "cd /app && export GIT_SSH_COMMAND=\"ssh -i /app/secrets/deploy_key \
   -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new\" \
   && git fetch -q origin main && git rev-list --count origin/main..HEAD"'

# The durable state: pushed_at recent, error NULL, attempts 0.
deploy/vps/scripts/vps-ssh.sh 'sudo docker exec fapd-backend python -c "
import sqlite3
c = sqlite3.connect(\"file:/app/data/fapd.db?mode=ro\", uri=True)
c.row_factory = sqlite3.Row
r = c.execute(\"SELECT * FROM collector_state WHERE worker=%s\" % repr(\"eod\")).fetchone()
print({k: r[k] for k in (\"finalized_date\", \"evidence_pushed_at\",
                         \"evidence_push_error\", \"evidence_push_attempts\")})"'
```

The push succeeds only because the `fapd-pipeline` deploy key is the
bypass actor on the `main` ruleset (2026-08-27): the evidence commit
is created in the container and never sees CI. A push rejected with a
rules/`required_status_checks` message means that bypass was removed —
check the ruleset before anything else.

`accept-new` is not optional in that first command: a freshly recreated
container has an empty `known_hosts`, and a bare fetch fails `Host key
verification failed`, which reads like a credential fault and is not.

A non-NULL `evidence_push_error` with `evidence_push_attempts` at
`config.EVIDENCE_PUSH_MAX_ATTEMPTS` means the ladder has halted: the day
is a disclosed gap and will not retry. Fix the cause, then run
`deploy/vps/scripts/evidence-commit.sh` in the container.

**The second shape (2026-08-24):** `finalized_date` set, `evidence_pushed_at`
NULL, error NULL — a day finalized whose push never ran. The supervisor
now retries that shape on its idle cycles too, but read the row, not
the absence of an error.

**A manual `scripts/run_pipeline.py --date D` renders and builds the
site and records nothing** — it does not set `finalized_date` and does
not push. Nine hand-rendered days (2026-08-15..23) sat unpushed with
this row reading clean for that reason. The recovery after a `HALTED`
finalizer is `scripts/collect.py --finalize D` inside the container: the
same finalizer, marker, and push as the nightly path, bypassing the
halt because the operator is the one who fixed the cause.

### Did inference run?

Since GUIDE §6 r15 a day finalizes with or without a provider. The
digest's **Inference** row says only whether model layers ran; the
cause lives here:

```sh
deploy/vps/scripts/vps-ssh.sh 'sudo docker exec fapd-backend python -c "
import sqlite3
c = sqlite3.connect(\"file:/app/data/fapd.db?mode=ro\", uri=True)
for r in c.execute(\"SELECT date, available, backend, models, layers FROM day_inference ORDER BY date DESC LIMIT 5\"): print(r)"'
# and the reason, from the ledger:
deploy/vps/scripts/vps-ssh.sh 'sudo docker exec fapd-backend python -c "
import sqlite3
c = sqlite3.connect(\"file:/app/data/llm_ledger.db?mode=ro\", uri=True)
for r in c.execute(\"SELECT substr(ts_utc,1,16), backend, purpose, substr(error,1,100) FROM llm_calls WHERE error LIKE \x27provider unavailable%\x27 ORDER BY ts_utc DESC LIMIT 5\"): print(r)"'
```

A day with `available=0` and a provider that should have worked is a
finding; a day with `available=0` under `LLM_BACKEND=none` is the
configuration working.

## Cadence

| When | What | Why |
|---|---|---|
| Daily / casual | local checks block | freshness, budget, spend anomalies |
| Daily | the evidence-push check | a stranded commit is invisible from the public site |
| **After every deploy** | VPS block, immediately **and again ~5 min later** | containers came back clean, no error surge |
| Weekly | CVE sweep ([AGENT-CVE-GUIDE.md](AGENT-CVE-GUIDE.md)) | dependency/base-image drift |
| TLS <30 days to expiry | `certbot renew --dry-run` (on box) | catch hook breakage before the real renewal |
| After a collector change | `collect.py --once --no-llm --no-wayback` + collector_state read | cycle integrity without token spend or archive writes |
| Before any deploy | `deploy/dev/scripts/dev-up.sh` render against a recent VPS seed | the change seen on production-shaped data first (advisory) |
| Before a deploy that touches `deploy/vps/nginx/` | `deploy/vps/nginx/rehearse.sh` → `SUCCESS` | a bad fapd-web config crash-loops the site and endangers the edge proxy's restart; the throwaway container proves the request matrix in ~10 s (deploy.sh repeats `nginx -t` on the box before the swap) |
| Before a deploy that touches `deploy/vps/mcp/`, `packages/static-mcp/` or the `/mcp` location | the same `rehearse.sh` (rows M1–M17) plus `uv run pytest -q tests/test_mcp_manifest.py packages/static-mcp/tests` | the manifest is checked against a real render; the proxy path, limits, signposts, no-egress and least-privilege invariants are proven in throwaway containers |
| After every deploy | the MCP block above, and `docker port fapd-mcp` empty | the no-port invariant is the firewall (Docker-published ports bypass ufw) |

# Phase 5 — merge, firewall coordination, deploy, verification, registry (agent discovery)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md).
Task AD-12. Performed by the **orchestrator with the operator present**.
Every VPS write is gated on the operator saying "deploy" in the session
(AGENT-VPS-SERVICING-GUIDE §4). Checkpoints C-1 (firewall), C-3 (deploy)
and C-4 (registry) happen here. Last reviewed: 2026-09-13.*

## 0. Outcome

The branch is merged to `main` with CI green, deployed, and proven from
the public internet: every discovery document, header and negotiation
rule works; `https://fapd.info/mcp` serves both protocol eras to real
clients; no new port is open; the containers keep their invariants.
Cloudflare's scanner is re-run and its results recorded honestly. The
MCP service is listed in the official MCP Registry. Runbooks and review
dates reflect what was actually verified.

## 1. Why deploy from `main`, not from the branch

`deploy.sh` bakes the checked-out working tree, including `.git`, into
the backend image. The nightly `evidence-commit.sh` then commits evidence
on the container's checked-out branch, rebases onto `origin/main`, runs
`git push origin main`, and verifies `HEAD == origin/main`. **Deploying
from `feature/agent-discovery` would make that verification fail every
night (exit 6).** The push pushes local `main`, not the branch, and the
branch's unmerged commits would sit under the evidence commit. That's
the F-019/F-021 failure class. So:

**merge → push `main` (CI green, ruleset) → check out `main` → deploy.**

A fix found after deploy goes through a branch → merge → redeploy, the
same way.

## 2. Pre-merge checklist (orchestrator; all must be true)

1. Status table in the master plan: Phases 0–4C "done", each with commit
   hashes, WORKLOG entries and agent log paths.
2. `uv run ruff check .` clean. `uv run pytest -q` green with **zero
   skips** in `tests/test_web_conf.py`, `tests/test_markdown_twins.py`,
   `tests/test_agent_discovery.py`, `tests/test_mcp_surfaces.py` and
   `tests/test_mcp_manifest.py` (the cross-phase skips must be gone).
   Record the counts.
3. `deploy/vps/nginx/rehearse.sh` → `SUCCESS` on the merged tree (rows
   1–18, M1–M11, no SKIP). Paste the output into WORKLOG.
4. Dev stack (`deploy/dev/scripts/dev-up.sh`) on the merged tree: `curl`
   rows 1–10 and M1–M4 against `http://localhost:8080`; one real client
   call (`claude mcp add --transport http fapd-dev http://localhost:8080/mcp`
   in a scratch directory, `list_digests`, `get_digest`; remove the config
   afterwards).
5. The honesty grep from Phase 0 §2.7 finds only the rows marked "not
   changed" (dated history).
6. Operator has read the GUIDE/CLAUDE.md amendments (C-2 done in Phase 0)
   and the final `agents.html` MCP section (render it locally and show
   it).

Then: fast-forward `main` to the branch per CLAUDE.md §8, push, and
**wait for the `test` check to pass on `main`'s tip** (ruleset
21668661). Check out `main` locally.

## 3. Checkpoint C-1 — the Hostinger firewall (operator)

**What we know (2026-09-13, read-only):** host `ufw` allows exactly
2222/80/443. The edge proxy publishes 80 and 443. The MCP service rides
443 through the edge proxy and `fapd-web`, and **publishes no port**.

**The operator does, in Hostinger hPanel → VPS → Security/Firewall**
(the "secondary edge firewall"):

1. Open the firewall configuration attached to this VPS and read the
   inbound rules.
2. Confirm inbound **443/tcp** and **80/tcp** are allowed (they must be;
   the site and ACME renewals work) and that the SSH port rule matches
   what's expected.
3. **Make no change.** Specifically, don't open 8080 or any other port
   for MCP. `fapd-mcp` listens only on an internal Docker network, and a
   published Docker port would bypass `ufw` entirely, leaving the panel
   firewall as the only guard.
4. Tell the orchestrator: "C-1 confirmed, no change", or describe any
   difference found.

**The orchestrator records** the confirmation (date, who, what was seen,
no change) in WORKLOG before the deploy, and after the deploy runs §5.4
(external proof that nothing new is listening).

*If the operator later wants MCP on its own hostname (e.g.
`mcp.fapd.info`), that's a DNS record, a certificate and an edge-proxy
server block, still on 443. It's a separate decision, not part of this
plan.*

### 3.1 AD-16 — repair the existing nginx fail2ban jails (operator-directed, 2026-09-13)

Read-only inspection on 2026-09-13 found the host's `nginx-botsearch`,
`nginx-http-auth` and `nginx-limit-req` jails running with **no chain in
`iptables -S DOCKER-USER`**, so their bans probably never reach the
packet filter (only `nginx-bad-request` and `nginx-noscript` have
chains). The jail files are the cohabitant's (`/opt/spiralyst/fail2ban/`,
deployed by copy into `/etc/fail2ban/jail.d/`), so the *fix* lands in
that tree; this plan owns the diagnosis and the verification. The
operator asked for this to be addressed alongside C-6.

**Diagnose (orchestrator, read-only, before C-6):**

```sh
V=deploy/vps/scripts/vps-ssh.sh
$V 'for j in nginx-botsearch nginx-http-auth nginx-limit-req nginx-bad-request nginx-noscript; do echo "== $j"; sudo fail2ban-client get $j actions; sudo fail2ban-client status $j | tail -4; done'
$V 'sudo grep -E "nginx-(botsearch|http-auth|limit-req)" /var/log/fail2ban.log | grep -i -E "error|actionstart|exec" | tail -20'
$V 'sudo ls -la /opt/spiralyst/logs/nginx/; sudo tail -2 /opt/spiralyst/logs/nginx/error.log'
$V 'sudo iptables -S DOCKER-USER; sudo iptables -S | grep -c "^-N f2b-"'
```

Likely causes, in order of probability, and what each looks like:
1. **The chain is created lazily on first ban** (fail2ban ≥1.0 with
   `actionstart_on_demand`): the three jails have simply never banned
   anyone, and `get <jail> actions` lists `iptables-allports`. Then
   nothing is broken; record it and stop. Prove it by the
   `actionstart_on_demand` setting (`fail2ban-client get <jail> actionstart_on_demand`
   or the version's default) rather than by assumption.
2. **`actionstart` failed** (an iptables error at jail start, logged as
   `ERROR … returned 1`): the jails count failures but can never ban.
   The fix is in the cohabitant's jail files; the error text says what.
3. **The `error.log` jails point at a log that never receives the
   matching lines** (`nginx-limit-req` reads `error.log`, and
   `nginx-http-auth` is irrelevant to a site with no auth): a jail with
   no matches never starts an action under on-demand mode. Not a bug,
   but `nginx-http-auth` should be disabled as dead weight.

**Fix path:** write the findings and the exact jail-file diff into a
note for the operator (`docs/private/`, since the files are the
cohabitant's), covering: enabling `actionstart_on_demand = false` on the
nginx jails if the operator wants chains present from start (visible in
`iptables -S` at any time, which is what made this detectable), disabling
`nginx-http-auth`, and correcting whatever `actionstart` error appears.
The operator applies it in the spiralyst-site tree and redeploys; the
orchestrator re-runs the diagnose block afterwards and records the
result in WORKLOG. Our own jail (`fapd-mcp`) sets its thresholds
explicitly and is verified by chain presence after start (§5.5), so it
doesn't depend on this repair.

## 4. Checkpoint C-3 — deploy (operator says "deploy")

**Timing:** not between 03:30 and 06:00 UTC. The end-of-day finalizer
runs in that window, and a backend rebuild recreates the container.

1. `git rev-parse --abbrev-ref HEAD` → `main`, and `git status --short`
   is clean.
2. `ssh-add -l` shows the key. Read-only connect test:
   `deploy/vps/scripts/vps-ssh.sh 'sudo docker ps --format "{{.Names}} {{.Status}}"'`.
   Record the before state.
3. Read-only pre-deploy snapshot, kept in the private tree:
   `deploy/vps/scripts/vps-ssh.sh 'sudo docker exec fapd-web nginx -T'`,
   saved to `docs/private/predeploy-fapd-web-nginx-<date>.txt`, so the
   stock config can be compared or restored.
4. Run `deploy/vps/scripts/deploy.sh`. It runs the test gate, the nginx
   syntax gate on the box in a throwaway container, the bundle and repo
   rsync (with `logs/` excluded, SR-3), `mkdir -p logs`, builds
   `backend` and `mcp`, `up -d`, the site rebuild in the container,
   `build_today`, the web reload and its verify block.
   **If any step fails, stop.** Report the output faithfully and go to §9
   rollback if the site is affected.
5. Confirm the exclude worked: `vps-ssh.sh 'ls -la /opt/fapd/logs'`
   shows the directory (and, after a second deploy, still shows the log
   file).

## 5. Post-deploy verification (immediately, and again ~5 minutes later)

Run from the operator's machine unless stated. Record every result
(pass/fail and the evidence line) in WORKLOG.

### 5.1 Containers and invariants (read-only on the box)

```sh
deploy/vps/scripts/vps-ssh.sh 'sudo docker ps --format "{{.Names}}\t{{.Status}}\t{{.Ports}}"'
#   expect fapd-web, fapd-backend, fapd-mcp healthy; fapd-mcp shows NO host port
deploy/vps/scripts/vps-ssh.sh 'sudo docker network inspect fapd_fapd_mcp --format "{{.Internal}} {{range .Containers}}{{.Name}} {{end}}"'
#   expect: true fapd-mcp fapd-web   (compose prefixes the project name; confirm the real network name first with `docker network ls`)
deploy/vps/scripts/vps-ssh.sh 'sudo docker inspect fapd-mcp --format "{{.HostConfig.ReadonlyRootfs}} {{.Config.User}} {{.HostConfig.CapDrop}} {{json .HostConfig.PortBindings}} {{.HostConfig.SecurityOpt}}"'
#   expect: true 10001:10001 [ALL] {} [no-new-privileges:true]
deploy/vps/scripts/vps-ssh.sh 'sudo docker exec fapd-mcp python -c "import urllib.request; urllib.request.urlopen(\"https://example.com\", timeout=3)"; echo exit=$?'
#   expect a failure and exit=1 (no egress)
deploy/vps/scripts/vps-ssh.sh 'sudo docker network inspect fapd_edge --format "{{range .Containers}}{{.Name}} {{end}}"'
#   expect exactly spiralyst-proxy fapd-web (unchanged)
deploy/vps/scripts/vps-ssh.sh 'sudo docker exec spiralyst-proxy wget -qO- -T 3 http://fapd-mcp:8080/healthz; echo exit=$?'
#   expect failure: the edge cannot reach fapd-mcp
deploy/vps/scripts/vps-ssh.sh 'sudo ufw status | grep -c ALLOW'
#   expect the same count as before (6 lines: 2222/80/443 × v4/v6)
```

### 5.2 Public discovery surface (from outside)

```sh
B=https://fapd.info
curl -sI $B/ | grep -i -E '^(link|vary|content-type):'
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' -H 'Accept: text/markdown' $B/
D=$(curl -s $B/digests.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["digests"][0]["date"])')
curl -s -H 'Accept: text/markdown' $B/$D.html | shasum -a 256
curl -s https://raw.githubusercontent.com/davidkarnowski/free-agentic-publication-digester/main/digests/$D.md | shasum -a 256
#   the two hashes must match (after that day's evidence commit has pushed)
for p in /.well-known/api-catalog /.well-known/ai-catalog.json /.well-known/agent-skills/index.json /openapi.json /auth.md /robots.txt /mcp/server-card /.well-known/mcp/server-card.json /favicon.ico; do
  curl -s -o /dev/null -w "%{http_code} %{content_type} $p\n" -H 'Origin: https://example.org' $B$p
done
curl -sI $B/.well-known/ai-catalog.json | grep -i access-control-allow-origin
curl -s -w '\n%{http_code}\n' $B/.well-known/oauth-authorization-server      # 404 + signpost JSON
curl -s -o /dev/null -w '%{http_code}\n' $B/.git/config                        # 404
curl -s $B/nope-$(date +%s) | grep -c 'nginx/1\.'                              # 0
```

### 5.3 The MCP endpoint, both eras (from outside)

```sh
M=https://fapd.info/mcp
# modern (2026-07-28): stateless, headers mirror the body
curl -s -X POST $M -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
  -d '{"jsonrpc":"2.0","id":"d1","method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"fapd-phase5-check","version":"1"},"io.modelcontextprotocol/clientCapabilities":{}}}}'
curl -s -X POST $M -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: tools/call' -H 'Mcp-Name: get_digest' \
  -d "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"get_digest\",\"arguments\":{\"date\":\"$D\"},\"_meta\":{\"io.modelcontextprotocol/protocolVersion\":\"2026-07-28\",\"io.modelcontextprotocol/clientInfo\":{\"name\":\"fapd-phase5-check\",\"version\":\"1\"},\"io.modelcontextprotocol/clientCapabilities\":{}}}}" | head -c 600
# legacy (2025-06-18): initialize, no session header expected
curl -s -D - -X POST $M -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"fapd-phase5-check","version":"1"}}}' | grep -i -E '^(HTTP|mcp-session-id)|protocolVersion'
# refusals
curl -s -o /dev/null -w '%{http_code}\n' $M                                          # 405
curl -s -o /dev/null -w '%{http_code}\n' -X POST $M -H 'Origin: https://evil.example' -H 'Content-Type: application/json' -d '{}'   # 403

# adversarial input from outside (SR-15): every one must be a well-formed
# JSON-RPC error with the stated status; never a 5xx, never a traceback
curl -s -w ' %{http_code}\n' -X POST $M -H 'Content-Type: text/plain' -d '{}'                       # 415 (nginx)
curl -s -w ' %{http_code}\n' -X POST $M -H 'Host: evil.example' -H 'Content-Type: application/json' -d '{}'   # 403 (service)
curl -s -w ' %{http_code}\n' -X POST $M -H 'Content-Type: application/json' -d "$(python3 -c 'print("["*40+"]"*40)')"   # 400 -32600/-32700
curl -s -w ' %{http_code}\n' -X POST $M -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":NaN,"method":"ping"}'         # 400
curl -s -w ' %{http_code}\n' -X POST $M -H 'Content-Type: application/json' -d '[{"jsonrpc":"2.0","id":1,"method":"ping"}]'        # 400 batching
curl -s -w ' %{http_code}\n' -X POST $M -H 'Content-Type: application/json' -d "{\"jsonrpc\":\"2.0\",\"id\":\"$(python3 -c 'print("x"*200)')\",\"method\":\"ping\"}"   # 400, id not echoed
curl -s -w ' %{http_code}\n' -X POST $M -H 'Content-Type: application/json' -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: tools/call' -H 'Mcp-Name: get_digest' \
  -d '{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"get_digest","arguments":{"date":"../../etc/passwd"},"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"fapd-phase5-check","version":"1"},"io.modelcontextprotocol/clientCapabilities":{}}}}'   # 200 with -32602 naming "date", no path in the message
```

Keep this block to the ~12 requests above. It's a public server and the
fail2ban threshold is 20 rejected requests in 10 minutes from one
address; running the block twice in a row from one machine would ban
the operator's own address for an hour.

**Real clients.** Record the date, client, version and result for each:
1. Claude Code: in a scratch directory,
   `claude mcp add --transport http fapd https://fapd.info/mcp`, then ask
   it to list recent digests and fetch one. Remove the scratch config.
2. MCP Inspector (`npx @modelcontextprotocol/inspector`, throwaway dir):
   connect over Streamable HTTP, list tools and resources, call `get_live_day`.
3. The operator, optionally: a claude.ai or ChatGPT custom connector
   pointed at `https://fapd.info/mcp`.
4. The conformance suite (`github.com/modelcontextprotocol/conformance`)
   against the production URL, **only the read-only server scenarios**.
   Keep the request count small, and record it.

### 5.4 External port proof (C-1 follow-up)

From the operator's machine (not the box):

```sh
H=fapd.info
for p in 8080 8000 3000; do nc -vz -w 3 $H $p 2>&1 | tail -1; done
#   expect every one refused or timed out
```

Record the result under the C-1 WORKLOG entry.

### 5.5 Checkpoint C-6 — install the fail2ban jail (operator runs the staged script)

Only after §5.1–§5.3 pass and the `/mcp` access log exists on the host
(`vps-ssh.sh 'sudo tail -3 /opt/fapd/logs/mcp-access.log'` shows lines
whose **first field is a public address, not a 172.x Docker address**;
if it's a Docker address, stop: the log format is wrong and a ban would
be useless).

1. The operator runs `scripts/staged/2026-09-XX-install-fapd-mcp-jail.sh`
   on the box (it was rsynced with `deploy/vps/`; see Phase 4B §B.10 for
   what it does). It ends in `SUCCESS` or `FAILURE`.
2. Orchestrator verification (read-only):
   ```sh
   deploy/vps/scripts/vps-ssh.sh 'sudo fail2ban-client status fapd-mcp'
   deploy/vps/scripts/vps-ssh.sh 'sudo iptables -S DOCKER-USER | grep -c f2b-fapd-mcp'     # 1 — load-bearing (§3.1)
   deploy/vps/scripts/vps-ssh.sh 'sudo fail2ban-regex /opt/fapd/logs/mcp-access.log /etc/fail2ban/filter.d/fapd-mcp.conf | tail -8'
   ```
3. Don't test the ban by tripping it from the operator's machine. If a
   live test is wanted, use a throwaway cloud shell or phone hotspot
   address, send 25 `POST /mcp` requests with `Content-Type: text/plain`,
   confirm `fail2ban-client status fapd-mcp` lists the address, then
   `sudo fail2ban-client set fapd-mcp unbanip <addr>` (operator-gated
   write). Record the result.

### 5.6 Health pass

Run `/fapd-health` (now including the MCP checks from Phase 4B) right
away and again about 5 minutes later. The site, today page, backend
heartbeat and evidence-push state must all be unchanged from before the
deploy.

## 6. Re-scan and record

1. **Cloudflare URL Scanner with agent readiness** (the operator runs it
   on their Radar account). Save the JSON and PDF next to the originals
   in `research/Cloudflare_Access/`.
2. **isitagentready.com** (optional; the orchestrator may run it with the
   operator's OK, since it sends our public URL to a third-party scanner):
   `curl -s -X POST https://isitagentready.com/api/scan -H 'Content-Type: application/json' -d '{"url":"https://fapd.info"}'`,
   saved beside the Radar results.
3. WORKLOG entry: a before/after table for all 16 scored checks plus Web
   Bot Auth. For every check still failing, the reason: declined by
   design (and where that's published), or a scanner disagreement, with
   evidence (e.g. media type, auth.md wording). **Change a truthful
   document to satisfy a grader only if the relevant spec permits the
   alternative. Otherwise record the disagreement and leave the document
   as it is.**
4. Copy the numbers into the blog notes.

## 7. Checkpoint C-4 — MCP Registry listing (operator + orchestrator)

Only after §5.3 passes. The registry needs a publicly reachable remote.

1. **Namespace:** `info.fapd/fapd`, domain-based **HTTP authentication**
   (the site already serves `/.well-known/`, so no DNS change is needed).
   Read `docs/modelcontextprotocol-io/authentication.mdx` in the registry
   repo at publish time for the exact current commands.
2. **Key (operator, locally):** generate the Ed25519 key pair with OpenSSL
   3 (on macOS use Homebrew's `openssl@3`; LibreSSL can't generate
   Ed25519 keys). The **private key never enters the repository, the
   box, or a conversation.** Record where it's kept in
   `docs/private/SECRETS-LOG.md` per `docs/private/AGENT-SECRETS-GUIDE.md`.
   Give the orchestrator only the public proof line
   (`v=MCPv1; k=ed25519; p=<public key>`).
3. **Proof file (orchestrator, a normal code change):** a Publication
   change builds `site/.well-known/mcp-registry-auth` from a constant
   holding the public line. Branch → merge → deploy under a fresh
   "deploy". The Phase 3 config serves it from the `^~ /.well-known/`
   location (it's a real file, so it isn't signposted). Verify with
   `curl -s https://fapd.info/.well-known/mcp-registry-auth`.
4. **`server.json`:** `packages/static-mcp` CLI
   `static-mcp registry-json --manifest deploy/vps/mcp/fapd.manifest.json --schema-url <current schema URL from the registry docs>`
   → review → the operator runs `mcp-publisher login http --domain fapd.info --private-key …`
   and `mcp-publisher publish` from a scratch directory holding that
   `server.json`.
5. Verify the listing via the registry's public API or search, and record
   the listing URL in WORKLOG, `agents.html` (a later small Publication
   change) and the blog notes.

## 8. Close-out (orchestrator)

1. SERVER-GUIDE review-date rows: replace "pending deploy" with the
   verified date for each check in §5.1–§5.4 that passed. Rows for checks
   that didn't pass stay pending, with a note.
2. OPS-GUIDE cadence gains the MCP checks. The ops backlog gets any
   follow-ups found.
3. Master plan status table: Phase 5 "done", with evidence links.
4. WORKLOG closing entry; blog-notes file updated with the deploy story
   and the re-scan table.
5. Commit the bookkeeping (docs only) on a branch, merge per §8. No
   evidence paths in that commit.

## 9. Rollback (each level needs its own operator "go")

| Level | Symptom | Action | Effect |
|---|---|---|---|
| 0 — jail only | legitimate clients report bans | `sudo fail2ban-client set fapd-mcp unbanip <addr>`, or disable: `sudo fail2ban-client stop fapd-mcp` and remove `/etc/fail2ban/jail.d/fapd-mcp.local` | nginx limits keep working; nothing else changes |
| 1 — MCP only | `/mcp` misbehaves; site fine | `vps-ssh.sh 'cd /opt/fapd && sudo docker compose stop mcp'` | `/mcp` answers 503 with the signpost; everything else is untouched. Then fix via branch → merge → deploy. |
| 2 — web config | discovery headers or negotiation break pages | Revert the Phase 3/4B config on a branch (or remove the `./nginx` mount line), merge, deploy | `fapd-web` returns to stock config; the static documents stay harmless |
| 3 — everything | anything worse | `git revert` the merge range on a branch → merge → deploy | Pre-plan state. Leftover built files in the site volume (`.well-known/`, `*.md`, `_signpost/`, `mcp/`) are inert. Delete them with a staged script (OB-19 pattern) if the retirement is permanent. |

If `fapd-web` fails to start, **act fast**. The edge proxy's static
upstream means an edge restart during that window would also take down
the cohabitant's site. Level 2's fastest path is to restore the pre-deploy
config snapshot from §4.3, then investigate.

## 10. Blog notes to capture in this phase

The firewall conversation (why no port opens); the deploy-from-`main`
reason; the before/after scan table; the first real-client transcript;
any scanner disagreement and the decision taken.

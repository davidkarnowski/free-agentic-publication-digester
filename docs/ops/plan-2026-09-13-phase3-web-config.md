# Phase 3 — the fapd-web nginx configuration (agent discovery)

*Part of [plan-2026-09-13-agent-discovery.md](plan-2026-09-13-agent-discovery.md)
(the master plan; read §4 VPS findings, §7 protocol and §8 contracts
first). Task AD-11. Performed by the **`fapd-operations`** agent. Depends
on Phase 0 merged. Runs in parallel with Phases 1, 2 and 4A. **This
phase changes files only. Deploying is Phase 5 and needs the operator's
"deploy".** Last reviewed: 2026-09-13.*

## 0. Outcome

`fapd-web` stops running the image's stock configuration and runs a
repo-managed one that:

1. serves every discovery document with its correct content type (§8.1);
2. sends the RFC 8288 `Link` header (§8.3) on every HTML and Markdown
   response;
3. routes `Accept: text/markdown` requests to Markdown twins for eligible
   paths (§8.2), with `Vary: Accept`;
4. adds `Access-Control-Allow-Origin: *` to public machine-readable files
   (D6);
5. answers probes for protocols we don't offer, anywhere under
   `/.well-known/`, with a 404 whose JSON body points agents to the real
   surfaces;
6. hides the nginx version, rejects request bodies and non-GET/HEAD
   methods on static paths, and gzips the text types the edge proxy
   doesn't;
7. is **rehearsed** in a throwaway container and the dev stack, and is
   syntax-checked on the box before a deploy can swap it in.

Phase 4B later adds the `/mcp` location to the same file. Leave the
marked insertion point.

## 1. Ownership for this phase

**May edit / create:**
- `deploy/vps/nginx/default.conf` (new; the server config)
- `deploy/vps/nginx/fapd-discovery-headers.inc`, `deploy/vps/nginx/fapd-cors.inc`,
  `deploy/vps/nginx/fapd-static-methods.inc` (new snippets; `.inc` so
  nginx's `include conf.d/*.conf` doesn't load them twice)
- `deploy/vps/nginx/rehearse.sh` (new; local throwaway-container test)
- `deploy/vps/docker-compose.yml` (web service: add the mount)
- `deploy/dev/docker-compose.yml` (web service: same mount)
- `deploy/vps/scripts/deploy.sh` (pre-swap syntax check; post-up reload)
- `deploy/vps/README.md`, `docs/ops/OPS-GUIDE.md`,
  `docs/ops/SERVER-GUIDE.md` (describe the new config; SERVER-GUIDE
  review-date rows added **as "pending deploy"**, never as verified)
- `tests/test_dev_stack.py`; new `tests/test_web_conf.py`

**Read-only:** `src/fapd/publish.py` (you'll read `_PAGE` for the parity
test), master plan contracts, everything else.

**Never:** run anything against the VPS. No `vps-ssh.sh`, no
`deploy.sh`. Local Docker on the operator's machine is fine for the
rehearsal (it isn't the VPS).

## 2. Background

- VPS findings (master plan §4; specifics in the operator's private
  tree): the edge proxy passes every HTTPS path and every upstream header
  through to `fapd-web`, unchanged. The edge already sends HSTS, nosniff,
  frame-options and referrer-policy, so **don't duplicate those** in
  `fapd-web` (duplicates show up twice to clients). The edge gzips
  HTML/JSON/plain/CSS/JS/SVG but not the Markdown, linkset, AI-catalog,
  card, Atom or XML types. `fapd-web` today: stock
  `/etc/nginx/conf.d/default.conf`, `server_tokens` on, gzip off.
- The image's `/etc/nginx/nginx.conf` includes `conf.d/*.conf` **inside
  `http {}`**, so `map` and `limit_req_zone` in our `default.conf` are in
  http context.
- **Mount the directory, not a file.** Mount
  `./nginx:/etc/nginx/conf.d:ro` (prod) and `../vps/nginx:/etc/nginx/conf.d:ro`
  (dev). A single-file bind mount keeps pointing at the old inode after
  rsync replaces the file (AGENT-VPS-SERVICING-GUIDE §3, learned
  2026-07-30). A directory mount sees the new files.
- Compose recreates `web` automatically only when the service definition
  changes. The first deploy (new mount) recreates it. Later config-only
  deploys need `nginx -t` + `nginx -s reload`, which is why deploy.sh
  changes (§3.4).
- **The cohabitant risk:** the edge names `fapd-web` as a static
  upstream. If `fapd-web` crash-loops on a bad config, fapd.info goes
  down, and if the edge restarts while `fapd-web` is gone, the edge
  itself fails to start, taking the cohabitant's site with it. That's why
  the syntax check runs on the box **before** the new files are swapped
  in (§3.4).

## 3. Tasks

### 3.1 `deploy/vps/nginx/default.conf`

Write this, then prove every line in the rehearsal (§3.5). Where nginx
behaves differently from what's written here, fix the config, record the
finding in your progress log with a `BLOG:` line, and report the
deviation. **Don't** weaken a requirement to make a test pass.

```nginx
# fapd-web — the FAPD static site server. Repo-managed since the
# agent-discovery plan (docs/ops/plan-2026-09-13-agent-discovery.md).
# Source of truth: deploy/vps/nginx/. Mounted read-only as the whole of
# /etc/nginx/conf.d/ in deploy/vps and deploy/dev. Loaded inside the
# image's http{} block, so map/limit_req_zone below are http-context.
#
# The edge proxy (cohabitant) terminates TLS and adds HSTS, nosniff,
# frame-options and referrer-policy: do not repeat them here.

# ---- Markdown content negotiation (master plan §8.2) -------------------
map $http_accept $fapd_wants_md {
    default                                        0;
    # SR-1: `text/markdown;q=0` is an explicit refusal, not a request.
    "~*(^|,)\s*text/markdown\s*(;\s*q=0(\.0+)?\s*(,|$))" 0;
    "~*(^|,)\s*text/markdown"                      1;
}

# Eligible HTML path -> its Markdown twin. Phase 2's build guarantees a
# twin exists for every path matched here (tests/test_markdown_twins.py
# coverage invariant), so a negotiated request never 404s.
map $uri $fapd_twin {
    default                                              "";
    "/"                                                  "/index.md";
    "/index.html"                                        "/index.md";
    "~^/(today|50x)\.html$"                              "";
    "~^/(?<fapd_n>[A-Za-z0-9._-]+)\.html$"               "/${fapd_n}.md";
    "~^/sources/(?<fapd_s>[A-Za-z0-9._-]+)\.html$"       "/sources/${fapd_s}.md";
    "~^/archive/(?<fapd_y>[0-9]{4})\.html$"              "/archive/${fapd_y}.md";
}

map "$fapd_wants_md:$fapd_twin" $fapd_negotiated {
    default                  "";
    "~^1:(?<fapd_t>/.+)$"    $fapd_t;
}

# ---- Client identity and abuse limits for /mcp (used by Phase 4B) ------
# Only the edge proxy can reach fapd-web, and it sets X-Real-IP from the
# true remote address, so the header is trustworthy here. SR-4: an empty
# header (the dev stack, or a misconfiguration) must not silently disable
# the limits — fall back to the direct peer address.
map $http_x_real_ip $fapd_client {
    default   $http_x_real_ip;
    ""        $remote_addr;
}
limit_req_zone  $fapd_client zone=fapd_mcp:10m  rate=5r/s;
limit_conn_zone $fapd_client zone=fapd_conn:10m;

# ---- Phase 4B inserts the /mcp access-log format here -------------------
# (PHASE-4B-HTTP-INSERTION-POINT)

server {
    listen 80;
    listen [::]:80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    server_tokens off;
    client_max_body_size 1k;          # no static path reads a body

    charset utf-8;
    charset_types text/html text/plain text/css text/xml text/markdown
                  application/json application/linkset+json
                  application/ai-catalog+json application/mcp-server-card+json
                  application/atom+xml application/javascript;

    # The edge gzips html/json/plain/css/js/svg; these are the types it
    # does not. An already-encoded response is not re-compressed there.
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/markdown application/linkset+json application/ai-catalog+json
               application/mcp-server-card+json application/atom+xml
               text/xml application/xml application/json text/plain;

    # Negotiate before location matching. The rewritten URI (*.md) maps to
    # no twin, so this can never loop.
    if ($fapd_negotiated) {
        rewrite ^ $fapd_negotiated last;
    }

    location / {
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        try_files $uri $uri/ =404;
    }

    location ~ \.html$ {
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        include /etc/nginx/conf.d/fapd-discovery-headers.inc;
    }

    location ~ \.md$ {
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        default_type text/markdown;             # md is not in mime.types
        include /etc/nginx/conf.d/fapd-discovery-headers.inc;
        include /etc/nginx/conf.d/fapd-cors.inc;
    }

    location ~ \.(json|txt|xml)$ {
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        include /etc/nginx/conf.d/fapd-cors.inc;
    }

    # Discovery documents with non-default media types.
    location = /.well-known/api-catalog {
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        default_type application/linkset+json;  # no extension
        include /etc/nginx/conf.d/fapd-cors.inc;
    }
    location = /.well-known/ai-catalog.json {
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        types { }                               # override .json -> application/json
        default_type application/ai-catalog+json;
        include /etc/nginx/conf.d/fapd-cors.inc;
    }
    location = /mcp/server-card {               # built in Phase 4C
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        default_type application/mcp-server-card+json;
        include /etc/nginx/conf.d/fapd-cors.inc;
    }

    # Everything else under /.well-known/: real files are served; a probe
    # for a protocol we do not operate gets an honest 404 whose body
    # points to the real surfaces (plan §5 "declined").
    location ^~ /.well-known/ {
        include /etc/nginx/conf.d/fapd-static-methods.inc;
        include /etc/nginx/conf.d/fapd-cors.inc;
        error_page 404 /_signpost/not-offered.json;
        location ~ \.md$ {
            include /etc/nginx/conf.d/fapd-static-methods.inc;
            default_type text/markdown;
            include /etc/nginx/conf.d/fapd-cors.inc;
        }
    }

    # Bodies for refusals; never directly reachable.
    location ^~ /_signpost/ {
        internal;
        include /etc/nginx/conf.d/fapd-cors.inc;
        add_header Cache-Control "no-store" always;
    }

    # No other dotfile is ever served.
    location ~ /\.(?!well-known(/|$)) {
        return 404;
    }

    # ---- Phase 4B inserts `location = /mcp { … }` here ----------------
    # (PHASE-4B-SERVER-INSERTION-POINT)

    error_page 500 502 503 504 /50x.html;
    location = /50x.html { internal; }
}
```

Snippets:

`fapd-discovery-headers.inc` (**the §8.3 contract, verbatim**, one line):

```nginx
add_header Link '</.well-known/api-catalog>; rel="api-catalog", </openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json", </agents.html>; rel="service-doc"; type="text/html", </llms.txt>; rel="describedby"; type="text/plain", </.well-known/ai-catalog.json>; rel="ai-catalog"; type="application/ai-catalog+json"' always;
add_header Vary Accept always;
```

`fapd-cors.inc`:

```nginx
add_header Access-Control-Allow-Origin "*" always;
```

`fapd-static-methods.inc`:

```nginx
if ($request_method !~ ^(GET|HEAD)$) { return 405; }
```

**Known nginx traps. Each gets a rehearsal assertion:**
- `add_header` in a location **replaces** all inherited `add_header`s. So
  a location that includes both snippets must include both explicitly.
  Nothing relies on server-level `add_header`.
- `add_header` only applies to 2xx/3xx unless `always`. The snippets use
  `always` so signposted 404s carry CORS.
- A `types {}` block replaces the MIME map for that location. It's used
  only in the exact `ai-catalog.json` location, where that's intended.
- Named captures in `map` regexes create variables. The `fapd_` prefixes
  avoid collisions.
- The `if … rewrite … last` at server level and `if … return` inside
  locations are the two documented safe uses of `if`.
- `location ^~ /.well-known/` stops regex matching for that prefix. That's
  why it nests its own `\.md$` location for SKILL.md files.
- The dotfile regex is declared after the `^~` prefix. Prefix locations
  marked `^~` win before regexes are considered, so `/.well-known/` never
  reaches it.

### 3.2 Compose changes

`deploy/vps/docker-compose.yml`, service `web`, `volumes:` gains:

```yaml
      # Repo-managed server config (agent-discovery plan Phase 3). A
      # DIRECTORY mount on purpose: rsync replaces files with new inodes,
      # which a single-file bind mount would never see (2026-07-30).
      - ./nginx:/etc/nginx/conf.d:ro
```

`deploy/dev/docker-compose.yml`, service `web`: the same line with
`../vps/nginx:/etc/nginx/conf.d:ro`.

**Tests** (`tests/test_dev_stack.py`): both compose files mount the
nginx directory read-only at `/etc/nginx/conf.d`. The prod and dev web
services use the same image pin. The existing counts
(`mem_limit`, `healthcheck`) are unchanged in this phase; Phase 4B
updates them.

### 3.3 `tests/test_web_conf.py` (static checks, no Docker)

1. `server_tokens off;`, `client_max_body_size 1k;` present.
2. **Link contract:** parse the `add_header Link '…'` value from the
   snippet; split on `, <`; the set of `(href, rel)` pairs equals the
   master plan §8.3 list. Then parse `publish._PAGE`'s head `<link>`
   elements and assert every §8.3 rel except `describedby` (covered by
   the existing `alternate` llms.txt link) is present **if Phase 1 has
   merged**. Detect that with `'rel="api-catalog"' in publish._PAGE`,
   and `pytest.skip` with a clear reason if not. Phase 5 re-runs this with
   both merged, so the skip can't survive to deploy (the Phase 5 checklist
   requires 0 skips in this file).
3. **Negotiation contract:** extract the `map $uri $fapd_twin` regex rows
   and test them against a table of sample paths (`/`, `/index.html`,
   `/2026-09-04.html`, `/today.html`, `/50x.html`, `/sources/govinfo-crec.html`,
   `/archive/2026.html`, `/day/2026-09-04.html`, `/assets/x.png`) with
   expected twins from §8.2. Use Python `re`: nginx PCRE and Python `re`
   agree for these patterns. If `publish.TWIN_ELIGIBLE_PATTERNS` exists
   (Phase 2 merged), assert both classify the sample paths identically;
   otherwise skip with a reason (same Phase 5 rule).
4. Every `include` names a file that exists in `deploy/vps/nginx/`.
5. Both insertion-point markers are present (Phase 4B depends on them).
6. No `add_header` for HSTS, X-Frame-Options, X-Content-Type-Options or
   Referrer-Policy (the edge owns those).
7. **Abuse-limit plumbing (SR-2, SR-4):** the `$fapd_client` map falls
   back to `$remote_addr` on an empty header; `limit_req_zone
   … zone=fapd_mcp` and `limit_conn_zone … zone=fapd_conn` are both keyed
   on `$fapd_client`, not on the raw header.
8. **`text/markdown;q=0` is not negotiated** (SR-1): exercise the Accept
   map regexes with `text/markdown`, `text/html, text/markdown;q=0.8`,
   `text/markdown;q=0`, `text/markdown; q=0.0, text/html` and assert
   the expected 1/1/0/0.
9. `deploy.sh`'s bundle rsync excludes `logs/` (SR-3).

### 3.4 `deploy/vps/scripts/deploy.sh`

Two additions, each with a comment explaining why (the file's existing
style):

1. **Before `[2/4]` bundle rsync**, a syntax gate that never touches the
   running container:

   ```bash
   echo "==> [1b/4] nginx config syntax gate (on the box, throwaway container)"
   # A bad fapd-web config crash-loops the site, and the edge proxy names
   # fapd-web as a static upstream, so an edge restart during that window
   # would take the cohabitant down too. Test the candidate BEFORE it is
   # swapped in. The config has no static upstreams, so -t needs no network.
   rsync -az --delete -e "ssh ${SSH_OPTS[*]}" \
     deploy/vps/nginx/ "${VPS}:${REMOTE_DIR}/.nginx-candidate/"
   ssh "${SSH_OPTS[@]}" "$VPS" \
     "sudo docker run --rm -v '${REMOTE_DIR}/.nginx-candidate:/etc/nginx/conf.d:ro' \
      nginx:1.30-alpine nginx -t"
   ```

   (`set -e` aborts the deploy on failure. The bundle rsync's `--delete`
   removes `.nginx-candidate/` afterwards because it isn't in the source
   tree, which is intended.)

   **SR-3 (security review): add `--exclude 'logs/'` to the bundle
   rsync's exclude list**, next to `.env`, `secrets/`, `repo/`, with a
   comment: Phase 4B bind-mounts `/opt/fapd/logs/` into `fapd-web` for
   the `/mcp` access log that fail2ban reads; without the exclude,
   `--delete` erases the host log directory on every deploy (the F-004
   class). Pin it in `tests/test_dev_stack.py` beside the existing
   exclude assertions.
2. **After `up -d`**, reload so config-only changes take effect without
   recreating the container:

   ```bash
   ssh "${SSH_OPTS[@]}" "$VPS" \
     "sudo docker exec fapd-web nginx -t && sudo docker exec fapd-web nginx -s reload"
   ```

3. In `[4/4] verify`, add:
   `curl -fsS -o /dev/null -w '%{http_code} %{content_type}\n' https://fapd.info/.well-known/api-catalog`
   and `curl -fsSI https://fapd.info/ | grep -i '^link:'`.

### 3.5 `deploy/vps/nginx/rehearse.sh`: the local proof

A self-verifying script in the staged-script style
(AGENT-VPS-SERVICING-GUIDE §2: preconditions, then action, then
verification, ending in `SUCCESS` or `FAILURE: <list>` with non-zero
exit). It runs **only on the local machine**:

1. Preconditions: `docker` available; repo root; `uv` available.
2. Build a fixture site into a temp dir with the real code:
   `uv run python -c 'from fapd import publish; publish.build_site(out_dir="<tmp>/site")'`.
   Plant `site/.well-known/agent-skills/x/SKILL.md` and
   `site/_signpost/not-offered.json` if Phases 1–2 haven't merged, so the
   routing can be proven on its own. Print a WARNING line when planting.
3. `docker run --rm -d --name fapd-web-rehearsal -p 127.0.0.1:18080:80
   -v "$PWD/deploy/vps/nginx:/etc/nginx/conf.d:ro" -v "<tmp>/site:/usr/share/nginx/html:ro"
   nginx:1.30-alpine`; then `docker exec … nginx -t`.
4. The matrix. Each row is one `check` function call recording
   pass/fail:

| # | Request | Expect |
|---|---|---|
| 1 | `GET /` | 200, `text/html`, `Link` header contains all five rels, `Vary` contains `Accept` |
| 2 | `GET /` with `Accept: text/markdown` | 200, `text/markdown; charset=utf-8`, body equals `site/index.md` |
| 3 | `GET /<a fixture digest date>.html` with `Accept: text/markdown` | body byte-equals `digests/<date>.md` |
| 4 | `GET /today.html` with `Accept: text/markdown` | `text/html` (not eligible), never 404 |
| 5 | `GET /` with a browser Accept (`text/html,application/xhtml+xml,*/*;q=0.8`) | `text/html` |
| 6 | `GET /.well-known/api-catalog` | 200, `application/linkset+json`, ACAO `*` |
| 7 | `GET /.well-known/ai-catalog.json` | 200, `application/ai-catalog+json`, ACAO `*` |
| 8 | `GET /.well-known/agent-skills/<name>/SKILL.md` | 200, `text/markdown` |
| 9 | `GET /.well-known/mcp/server-cards.json` (not built) | **404**, `application/json`, body has `"status": "not offered"`, ACAO `*` |
| 10 | `GET /.well-known/oauth-authorization-server` | 404 + signpost |
| 11 | `GET /_signpost/not-offered.json` directly | 404 (internal), not the signpost served as 200 |
| 12 | `GET /.git/config`, `GET /.env` | 404 |
| 13 | `POST /index.html` | 405 |
| 14 | `GET /auth.md` | 200, `text/markdown`, ACAO `*`, `Link` present |
| 15 | `GET /digests.json` with `Accept-Encoding: gzip` | ACAO `*`; served |
| 16 | `GET /robots.txt` | 200, `text/plain`, ACAO `*` |
| 17 | any 404 body | contains no `nginx/1.` version string |
| 18 | `GET /favicon.ico` | 200 (if Phase 1 merged; otherwise recorded as SKIP) |

5. Stop and remove the container. Print `SUCCESS` or
   `FAILURE: <rows>`.

Then run the **dev stack** end to end (`deploy/dev/scripts/dev-up.sh`,
production-shaped data, `http://localhost:8080`) and repeat rows 1–10
with `curl` against it. The dev stack needs its seeded data. If it isn't
seeded, report that and don't run `dev-seed.sh` (that script is
operator-gated).

## 4. Acceptance criteria

1. `rehearse.sh` prints `SUCCESS`, with its full output in the exit
   report (SKIP rows listed and explained).
2. `tests/test_web_conf.py` and `tests/test_dev_stack.py` pass. Any skip
   is one of the two documented "other phase not merged" skips.
3. deploy.sh has the syntax gate before the bundle rsync, the reload
   after `up -d`, and the new verify lines. `bash -n deploy/vps/scripts/deploy.sh`
   passes.
4. No security header that the edge owns is duplicated.
5. `deploy/vps/README.md` and `docs/ops/OPS-GUIDE.md` describe the config,
   the rehearsal and the reload. SERVER-GUIDE rows are marked "pending
   deploy".
6. Ruff clean, full pytest green (report counts).

## 5. Rollback

- Before deploy: revert the commit.
- After deploy (Phase 5, operator-gated): remove the `./nginx` mount line
  from `deploy/vps/docker-compose.yml` and redeploy. Compose recreates
  `web` on the stock image config. The static documents stay harmless
  without it.

## 6. Dispatch prompt

```
You are the FAPD OPERATIONS agent. Read docs/agents/operations.md IN FULL
before doing anything else — it is your instruction source of truth and
this prompt does not repeat it.

TASK: Implement Phase 3 of the agent-discovery plan: a repo-managed nginx
configuration for fapd-web (content types for the discovery documents,
the RFC 8288 Link header, Accept: text/markdown negotiation to Markdown
twins, CORS on machine-readable files, signposted 404s under
/.well-known/, server_tokens off, method and body limits, gzip for the
types the edge does not compress), mounted in both the prod and dev
compose files, with a pre-swap syntax gate and post-up reload in
deploy.sh, static tests, and a local throwaway-container rehearsal
script — exactly as specified in
docs/ops/plan-2026-09-13-phase3-web-config.md, meeting every acceptance
criterion in its §4.

CONTEXT: Read docs/ops/plan-2026-09-13-agent-discovery.md first (rulings
§3, the VPS findings §4 — the edge passes /.well-known and upstream
headers through unchanged and already sends HSTS/nosniff/frame-options —
the working protocol §7, and the §8 contracts you must match exactly),
then docs/ops/plan-2026-09-13-security-review.md (findings SR-1 to SR-4
are yours and are already folded into this phase file).
Branch feature/agent-discovery. Phase 1/2 (Publication: the documents and
Markdown twins) and Phase 4A (the generic MCP package) run at the same
time in the same tree; none of them edits your files. Leave the two
PHASE-4B insertion markers in the config. You must NOT run anything
against the VPS (no vps-ssh.sh, no deploy.sh); local Docker for the
rehearsal is fine. Keep the progress log required by master plan §7.2;
write its first entry before touching any file.

CONTRACT (non-negotiable):
1. Edit only files your section owns (your file §1 lists them). If the
   task seems to require editing a shared or foreign file, STOP work on
   that part and put the exact desired diff in your exit report instead.
2. Stage nothing, commit nothing. Leave the working tree modified.
3. Run `uv run ruff check .` and `uv run pytest -q` before reporting;
   report the actual numbers, including failures.
4. Follow docs/code-standards.md; match surrounding idiom.
5. New behavior gets a test that fails without the change.
6. If blocked, exit and report the blocker — do not improvise around it.

EXIT REPORT (required shape):
- Files modified (list)
- Shared-file diffs needed (exact diffs, or "none")
- Verification: ruff + pytest output tails, plus any manual checks run
  (the full rehearse.sh output)
- Deviations from the task, with rationale (every place nginx behaved
  differently from the plan's draft config)
- What a human should look at before this merges
- Acceptance criteria §4, each marked met / not met with evidence
- Progress log path, and all BLOG: lines copied out
```

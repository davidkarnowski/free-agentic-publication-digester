"""Static checks on the fapd-web nginx configuration — agent-discovery
plan Phase 3, task AD-11.

The config left this repository on 2026-09-21: it moved to the operator's
operator's private host tree, because it carries probe-refusal rules that state
exactly what is and is not refused, and this repository is public.

These tests were NOT deleted with it. They pin real invariants that a
later edit could quietly drop, and they are just as useful run against
the config wherever it now lives. Point FAPD_NGINX_DIR at a checkout of the
operator's private host tree's fapd-web/ and they all run:

    FAPD_NGINX_DIR=<private-host-tree>/fapd-web uv run pytest -q tests/test_web_conf.py

With the variable unset — the normal case in this public repo, and in
any clone that has no access to the private tree — every test in this
file skips, so the suite stays green without the config present.

No Docker here: the live proof is the private host tree's fapd-web/rehearse.sh. These
tests pin what the config PROMISES — the master plan's §8.1 content
types, the §8.3 Link contract (in parity with the page head), the §8.2
negotiation table, the security-review findings SR-1..SR-4, the two
Phase 4B insertion points, and deploy.sh's ordering — so a later edit
that quietly drops one fails here before anyone runs a container.

Two tests skip until the Publication phases merge (the head-link parity
and the twin-pattern agreement); Phase 5's checklist requires zero skips
in this file, so a skip cannot survive to a deploy.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

from fapd import publish

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The config is no longer in this repo (see the module docstring). Resolve it
# from the environment; skip the whole module when it is not available rather
# than fail, so a public clone's suite is green without the private tree.
_ENV_DIR = os.environ.get("FAPD_NGINX_DIR")
NGINX = Path(_ENV_DIR).expanduser() if _ENV_DIR else PROJECT_ROOT / "deploy" / "vps" / "nginx"
CONF = NGINX / "default.conf"

pytestmark = pytest.mark.skipif(
    not CONF.is_file(),
    reason=(
        "fapd-web nginx config not present: it moved to the operator's "
        "private host tree on 2026-09-21. Set FAPD_NGINX_DIR=<private-host-tree>/fapd-web to run "
        "these checks against it."
    ),
)
HEADERS_INC = NGINX / "fapd-discovery-headers.inc"
DEPLOY_SH = PROJECT_ROOT / "deploy" / "vps" / "scripts" / "deploy.sh"

# Master plan §8.3 — the five relations, as (href, rel).
LINK_CONTRACT = {
    ("/.well-known/api-catalog", "api-catalog"),
    ("/openapi.json", "service-desc"),
    ("/agents.html", "service-doc"),
    ("/llms.txt", "describedby"),
    ("/.well-known/ai-catalog.json", "ai-catalog"),
}

# Master plan §8.2 — request path -> twin ("" = not eligible).
TWIN_SAMPLES = [
    ("/", "/index.md"),
    ("/index.html", "/index.md"),
    ("/2026-09-04.html", "/2026-09-04.md"),
    ("/agents.html", "/agents.md"),
    ("/today.html", ""),
    ("/50x.html", ""),
    ("/sources/govinfo-crec.html", "/sources/govinfo-crec.md"),
    ("/archive/2026.html", "/archive/2026.md"),
    ("/day/2026-09-04.html", ""),
    ("/assets/x.png", ""),
    ("/index.md", ""),            # the rewritten URI maps to nothing: no loop
]

EDGE_OWNED_HEADERS = ("strict-transport-security", "x-frame-options",
                      "x-content-type-options", "referrer-policy")


def _conf():
    return CONF.read_text(encoding="utf-8")


def _live(text):
    """The directives only — nginx comments explain the traps and are
    allowed to NAME headers the config must not send."""
    return "\n".join(ln for ln in text.splitlines()
                     if not ln.lstrip().startswith("#"))


def _unquote(tok):
    return tok[1:-1] if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "\"'" else tok


def _map_rows(source, target):
    """The (key, value) rows of `map <source> <target> { … }`, in file order."""
    block = re.search(
        r"^map\s+" + re.escape(source) + r"\s+" + re.escape(target) + r"\s*\{(.*?)^\}",
        _conf(), re.DOTALL | re.MULTILINE)
    assert block, f"map {source} {target} not found"
    rows = []
    for line in _live(block.group(1)).splitlines():
        m = re.match(r'\s*("[^"]*"|\'[^\']*\'|\S+)\s+("[^"]*"|\'[^\']*\'|[^;]+);', line)
        if m:
            rows.append((_unquote(m.group(1)), _unquote(m.group(2))))
    return rows


def _nginx_map(rows, value):
    """Evaluate a `map` the way nginx does: exact strings first (case-
    insensitive), then regex rows in order of appearance, else default.
    Named captures (`(?<n>…)`) become `$n` / `${n}` in the value."""
    default = ""
    for key, val in rows:
        if key == "default":
            default = val
        elif not key.startswith("~") and key.lower() == value.lower():
            return val
    for key, val in rows:
        if not key.startswith("~"):
            continue
        pat, flags = key[1:], 0
        if pat.startswith("*"):
            pat, flags = pat[1:], re.IGNORECASE
        m = re.search(pat.replace("(?<", "(?P<"), value, flags)
        if m:
            for name, got in m.groupdict().items():
                val = val.replace("${" + name + "}", got or "").replace("$" + name, got or "")
            return val
    return default


def _negotiated(path, accept):
    """The URI the server-level rewrite lands on, or "" for no rewrite."""
    wants = _nginx_map(_map_rows("$http_accept", "$fapd_wants_md"), accept)
    twin = _nginx_map(_map_rows("$uri", "$fapd_twin"), path)
    return _nginx_map(_map_rows('"$fapd_wants_md:$fapd_twin"', "$fapd_negotiated"),
                      f"{wants}:{twin}")


def _link_header_pairs():
    m = re.search(r"add_header\s+Link\s+'([^']*)'\s+always;", HEADERS_INC.read_text(encoding="utf-8"))
    assert m, "the Link add_header is not in the snippet"
    pairs = set()
    for part in m.group(1).split(", <"):
        part = part if part.startswith("<") else "<" + part
        pm = re.match(r'<([^>]+)>;\s*rel="([^"]+)"', part)
        assert pm, part
        pairs.add((pm.group(1), pm.group(2)))
    return pairs


# 1. hardening directives ---------------------------------------------------

def test_hardening_directives_present():
    live = _live(_conf())
    assert "server_tokens off;" in live
    assert "client_max_body_size 1k;" in live


# 2. the Link contract, header and head in parity ---------------------------

def test_link_header_matches_the_master_plan_contract():
    assert _link_header_pairs() == LINK_CONTRACT


def test_page_head_carries_the_same_relations():
    """Phase 1 puts the §8.3 relations in every page head; the header
    and the head must agree. `describedby` is covered by the existing
    `alternate` llms.txt link, so it is the one rel not required here."""
    if 'rel="api-catalog"' not in publish._PAGE:
        pytest.skip("Phase 1 (discovery documents) not merged: publish._PAGE "
                    "has no api-catalog link yet; Phase 5 requires 0 skips here")
    head = {}
    for tag in re.findall(r"<link\b[^>]*>", publish._PAGE):
        rel = re.search(r'rel="([^"]+)"', tag)
        href = re.search(r'href="([^"]+)"', tag)
        if rel and href:
            head[rel.group(1)] = "/" + href.group(1).lstrip("/")
    for href, rel in LINK_CONTRACT:
        if rel == "describedby":
            continue
        assert head.get(rel) == href, (rel, head.get(rel), href)


# 3. the negotiation table --------------------------------------------------

@pytest.mark.parametrize("path,twin", TWIN_SAMPLES)
def test_twin_map_classifies_the_sample_paths(path, twin):
    assert _nginx_map(_map_rows("$uri", "$fapd_twin"), path) == twin
    # and the full chain: a request that wants Markdown rewrites to the
    # twin or not at all
    assert _negotiated(path, "text/markdown") == twin
    assert _negotiated(path, "text/html") == ""


def test_twin_map_agrees_with_publish():
    """Phase 2 exports the eligibility patterns it builds twins for; the
    config's map must classify the same paths as eligible. Shape assumed
    (confirm when Phase 2 lands): an iterable whose items are a regex
    (str or compiled) or a tuple whose first element is one."""
    patterns = getattr(publish, "TWIN_ELIGIBLE_PATTERNS", None)
    if patterns is None:
        pytest.skip("Phase 2 (Markdown twins) not merged: publish has no "
                    "TWIN_ELIGIBLE_PATTERNS; Phase 5 requires 0 skips here")
    def eligible(path):
        for item in patterns:
            pat = item[0] if isinstance(item, tuple) else item
            pat = pat.pattern if hasattr(pat, "pattern") else pat
            if re.search(pat, path):
                return True
        return False
    rows = _map_rows("$uri", "$fapd_twin")
    for path, _ in TWIN_SAMPLES:
        assert eligible(path) == bool(_nginx_map(rows, path)), path


# 4. includes resolve -------------------------------------------------------

def test_every_include_names_an_existing_snippet():
    includes = re.findall(r"^\s*include\s+(\S+);", _live(_conf()), re.MULTILINE)
    assert includes, "no includes found"
    for inc in includes:
        assert inc.startswith("/etc/nginx/conf.d/"), inc
        assert (NGINX / Path(inc).name).is_file(), inc
        assert inc.endswith(".inc"), f"{inc}: a .conf would be loaded twice"


# 5. Phase 4B: the /mcp transport gate (security review §3 stage L0) -------

def _mcp_location():
    m = re.search(r"^    location = /mcp \{\n(.*?)^    \}\n", _conf(), re.DOTALL | re.MULTILINE)
    assert m, "location = /mcp block not found"
    return _live(m.group(1))


def test_phase_4b_insertion_markers_were_replaced():
    conf = _conf()
    assert "PHASE-4B-HTTP-INSERTION-POINT" not in conf
    assert "PHASE-4B-SERVER-INSERTION-POINT" not in conf
    assert conf.index("log_format fapd_mcp") < conf.index("server {")
    assert conf.index("server {") < conf.index("location = /mcp {")


def test_mcp_location_is_post_only_with_the_content_type_gate_and_body_cap():
    loc = _mcp_location()
    assert "if ($request_method !~ ^POST$) { return 405; }" in loc
    assert 'if ($content_type !~* "^application/json") { return 415; }' in loc     # SR-5
    assert "client_max_body_size 64k;" in loc
    assert "error_page 405 /_signpost/mcp-method.json;" in loc
    assert "error_page 415 /_signpost/mcp-method.json;" in loc


def test_mcp_location_limits_requests_and_connections_on_the_phase_3_zones():
    loc = _mcp_location()
    assert re.search(r"limit_req\s+zone=fapd_mcp\s+burst=20 nodelay;", loc)
    assert re.search(r"limit_conn\s+fapd_conn\s+10;", loc)                          # SR-2
    assert "limit_req_status  429;" in loc and "limit_conn_status 429;" in loc
    live = _live(_conf())
    assert "zone=fapd_mcp:" in live and "zone=fapd_conn:" in live               # declared (Phase 3)


def test_mcp_location_proxies_through_a_variable_upstream_without_replay():
    loc = _mcp_location()
    assert "resolver 127.0.0.11 valid=10s ipv6=off;" in loc
    assert "set $fapd_mcp_upstream http://fapd-mcp:8080;" in loc
    assert "proxy_pass $fapd_mcp_upstream;" in loc                       # a variable: nginx starts without mcp
    assert "proxy_request_buffering on;" in loc                          # SR-6
    assert "proxy_next_upstream off;" in loc                             # SR-6
    assert "proxy_http_version 1.1;" in loc and 'proxy_set_header Connection "";' in loc
    assert "proxy_set_header Host $host;" in loc
    for t in ("proxy_connect_timeout 2s;", "proxy_send_timeout 10s;", "proxy_read_timeout 15s;"):
        assert t in loc, t
    assert 'add_header Cache-Control "no-store" always;' in loc
    # no static `upstream name { … }` block anywhere: a missing fapd-mcp
    # would then stop fapd-web (the edge's static upstream) from starting
    assert not re.search(r"^\s*upstream\s+\S+\s*\{", _live(_conf()), re.MULTILINE)


def test_mcp_error_pages_signpost_only_nginx_generated_502_and_504():
    """SR-7: the service's own 4xx/503 bodies are JSON-RPC errors the
    client must see, so proxy_intercept_errors stays off everywhere and
    only an unreachable upstream (502/504) becomes the 503 signpost."""
    loc = _mcp_location()
    assert "error_page 502 504 =503 /_signpost/mcp-unavailable.json;" in loc
    # 503 never appears as a SOURCE status (left of `=`): the service's own
    # concurrency 503 must reach the client as the JSON-RPC body it sent
    assert not re.search(r"error_page\s[^;=]*\b503\b", loc)
    assert "proxy_intercept_errors" not in _live(_conf())


def test_mcp_access_log_first_field_is_the_true_client_address():
    """Security review §4: a ban keyed on $remote_addr would target the
    edge proxy's internal address. The format starts with $fapd_client
    (X-Real-IP, falling back to the peer), carries no body, and the
    location writes it to the bind-mounted path the jail reads."""
    live = _live(_conf())
    m = re.search(r"log_format fapd_mcp '([^']*)'", live)
    assert m and m.group(1).startswith("$fapd_client - [$time_local]")
    fmt = "".join(re.findall(r"'([^']*)'", live[m.start():live.index(";", m.start())]))
    assert "$request_body" not in fmt and "$args" not in fmt
    assert '"$request_method $uri $server_protocol"' in fmt and "$status" in fmt
    assert "access_log /var/log/fapd/mcp-access.log fapd_mcp;" in _mcp_location()
    # The request id joins this log with the service's own (which logs no
    # address): nginx assigns it, logs it, and forwards it as X-Request-Id.
    assert fmt.endswith("rid=$request_id")
    assert "proxy_set_header X-Request-Id $request_id;" in _mcp_location()


def test_mcp_and_server_card_are_separate_locations():
    live = _live(_conf())
    assert "location = /mcp {" in live and "location = /mcp/server-card {" in live
    assert "include /etc/nginx/conf.d/fapd-cors.inc;" not in _mcp_location()   # D6: no CORS on /mcp


# 6. the edge owns the security headers ------------------------------------

def test_no_edge_owned_security_header_is_duplicated():
    for path in sorted(NGINX.glob("*.conf")) + sorted(NGINX.glob("*.inc")):
        for line in _live(path.read_text(encoding="utf-8")).splitlines():
            if "add_header" in line:
                assert not any(h in line.lower() for h in EDGE_OWNED_HEADERS), (path.name, line)


# 7. abuse-limit plumbing (SR-2, SR-4) --------------------------------------

def test_client_map_falls_back_to_the_peer_address_on_an_empty_header():
    rows = dict(_map_rows("$http_x_real_ip", "$fapd_client"))
    assert rows[""] == "$remote_addr"
    assert rows["default"] == "$http_x_real_ip"


def test_both_limit_zones_are_keyed_on_the_client_map():
    live = _live(_conf())
    assert re.search(r"^limit_req_zone\s+\$fapd_client\s+zone=fapd_mcp:", live, re.MULTILINE)
    assert re.search(r"^limit_conn_zone\s+\$fapd_client\s+zone=fapd_conn:", live, re.MULTILINE)
    assert "zone_zone" not in live
    assert not re.search(r"limit_(req|conn)_zone\s+\$http_x_real_ip", live)


# 8. text/markdown;q=0 is a refusal (SR-1) ---------------------------------

@pytest.mark.parametrize("accept,wants", [
    ("text/markdown", "1"),
    ("text/html, text/markdown;q=0.8", "1"),
    ("text/markdown;q=0", "0"),
    ("text/markdown; q=0.0, text/html", "0"),
    ("text/html,application/xhtml+xml,*/*;q=0.8", "0"),
    ("", "0"),
])
def test_markdown_q0_is_not_negotiated(accept, wants):
    assert _nginx_map(_map_rows("$http_accept", "$fapd_wants_md"), accept) == wants


# 9. deploy.sh: the gate, the exclude, the reload, the verify -------------

def test_deploy_sh_no_longer_ships_or_reloads_the_nginx_config():
    """The inverse of what this test asserted before 2026-09-21.

    The config moved to the operator's private host tree, so this deploy must not
    push it, test it, or reload it. Each of these would now be actively
    wrong rather than merely dead: the candidate rsync sourced
    deploy/vps/nginx/, which no longer exists, so it would push an EMPTY
    directory over the live config and take fapd.info down; and a reload
    would apply a config this repo never saw. Asserted as absences so the
    old blocks cannot quietly return.
    """
    sh = DEPLOY_SH.read_text(encoding="utf-8")
    # Strip comments first: the point is that nothing EXECUTES against the
    # old path, not that the script may never mention it. The comments that
    # explain why these blocks were removed are the main defence against
    # someone helpfully restoring them.
    code = "\n".join(
        ln for ln in sh.splitlines() if not ln.lstrip().startswith("#")
    )
    assert ".nginx-candidate" not in code
    assert "nginx -s reload" not in code
    assert "deploy/vps/nginx/" not in code
    # SR-3: the bundle rsync excludes the host log directory
    bundle_cmd = re.search(r"rsync -az --delete --exclude '\.DS_Store'.*?deploy/vps/ \"\$\{VPS\}", sh, re.DOTALL)
    assert bundle_cmd and "--exclude 'logs/'" in bundle_cmd.group(0)
    verify = sh[sh.index("[4/4] verify"):]
    assert "https://fapd.info/.well-known/api-catalog" in verify
    assert "grep -i '^link:'" in verify


def test_deploy_sh_builds_the_mcp_service_creates_the_log_dir_and_verifies_discover():
    """Phase 4B (phase file §B.5): ruff covers packages/, the build line
    names mcp, logs/ exists before `up -d` (fapd-web mounts it at
    /var/log/fapd, and nginx opens every access_log path at startup), the
    verify step speaks MCP through the edge, and no port is published."""
    sh = DEPLOY_SH.read_text(encoding="utf-8")
    assert "uv run ruff check src/ scripts/ tests/ packages/" in sh
    # The [1b/4] gate's own `mkdir -p` and logs mount went with the nginx
    # config in 2026-09-21. The [3/4] assertions below are what actually
    # guarantee logs/ exists before `up -d`, which fapd-web still needs for
    # its ./logs:/var/log/fapd mount — so this invariant survives the move
    # rather than being dropped with the gate.
    build = sh[sh.index("[3/4]"):sh.index("[4/4]")]
    assert "mkdir -p logs" in build
    assert build.index("mkdir -p logs") < build.index("up -d")
    assert "build backend mcp" in build
    assert "Docker-published ports bypass ufw" in build
    verify = sh[sh.index("[4/4] verify"):]
    assert "https://fapd.info/mcp" in verify and "server/discover" in verify
    assert "MCP-Protocol-Version: 2026-07-28" in verify
    assert "serverInfo" in verify
    assert "docker port fapd-mcp" in verify


def test_rehearsal_runs_the_mcp_rows_on_an_internal_throwaway_network():
    """rehearse.sh (phase file §B.4): the fapd-mcp image beside the web
    container, an --internal network for the pair, the same hardening
    flags compose pins, the logs mount nginx -t needs, and rows M1–M17."""
    sh = (NGINX / "rehearse.sh").read_text(encoding="utf-8")
    assert "docker network create --internal" in sh
    assert "--network-alias fapd-mcp" in sh
    assert "-v \"$TMP/logs:/var/log/fapd\"" in sh
    for flag in ("--read-only", "--user 10001:10001", "--cap-drop ALL",
                 "--security-opt no-new-privileges:true"):
        assert flag in sh, flag
    assert "deploy/dev/mcp:/etc/static-mcp:ro" in sh
    assert "docker build" in sh and "packages/static-mcp" in sh
    for row in [f"M{n} " for n in range(1, 18)]:
        assert row in sh, row
    assert "_signpost/mcp-method.json" in sh and "_signpost/mcp-unavailable.json" in sh
    assert "FAPD_F2B_FILTER" in sh      # M17 reads the filter from the private host tree, or SKIPs


def test_shell_scripts_parse():
    for script in (DEPLOY_SH, NGINX / "rehearse.sh"):
        subprocess.run(["bash", "-n", str(script)], check=True)


def test_registry_proof_file_is_text_plain_without_cors():
    """/.well-known/mcp-registry-auth (master plan §8.1): text/plain, no CORS."""
    live = _live(_conf())
    m = re.search(r"location = /\.well-known/mcp-registry-auth \{(.*?)\}", live, re.DOTALL)
    assert m, "no exact-match location for the registry proof file"
    body = m.group(1)
    assert "default_type text/plain;" in body
    assert "fapd-static-methods.inc" in body
    assert "fapd-cors.inc" not in body

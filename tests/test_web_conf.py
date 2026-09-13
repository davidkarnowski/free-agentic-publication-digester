"""Static checks on the repo-managed fapd-web nginx configuration
(deploy/vps/nginx/) — agent-discovery plan Phase 3, task AD-11.

No Docker here: the live proof is deploy/vps/nginx/rehearse.sh. These
tests pin what the config PROMISES — the master plan's §8.1 content
types, the §8.3 Link contract (in parity with the page head), the §8.2
negotiation table, the security-review findings SR-1..SR-4, the two
Phase 4B insertion points, and deploy.sh's ordering — so a later edit
that quietly drops one fails here before anyone runs a container.

Two tests skip until the Publication phases merge (the head-link parity
and the twin-pattern agreement); Phase 5's checklist requires zero skips
in this file, so a skip cannot survive to a deploy.
"""

import re
import subprocess
from pathlib import Path

import pytest

from fapd import publish

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NGINX = PROJECT_ROOT / "deploy" / "vps" / "nginx"
CONF = NGINX / "default.conf"
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


# 5. Phase 4B insertion points ---------------------------------------------

def test_phase_4b_insertion_markers_present():
    conf = _conf()
    assert "(PHASE-4B-HTTP-INSERTION-POINT)" in conf
    assert "(PHASE-4B-SERVER-INSERTION-POINT)" in conf
    # the server marker sits inside the server block, before its close
    assert conf.index("(PHASE-4B-HTTP-INSERTION-POINT)") < conf.index("server {")
    assert conf.index("server {") < conf.index("(PHASE-4B-SERVER-INSERTION-POINT)")


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

def test_deploy_sh_gates_reloads_and_verifies_the_config():
    sh = DEPLOY_SH.read_text(encoding="utf-8")
    gate, bundle, up, reload_ = (sh.index("[1b/4] nginx config syntax gate"),
                                 sh.index("[2/4] rsync bundle"),
                                 sh.index("up -d"),
                                 sh.index("nginx -s reload"))
    assert gate < bundle < up < reload_
    assert ".nginx-candidate" in sh and "nginx -t" in sh[gate:bundle]
    assert "sudo docker exec fapd-web nginx -t && sudo docker exec fapd-web nginx -s reload" in sh
    # SR-3: the bundle rsync excludes the host log directory
    bundle_cmd = re.search(r"rsync -az --delete --exclude '\.DS_Store'.*?deploy/vps/ \"\$\{VPS\}", sh, re.DOTALL)
    assert bundle_cmd and "--exclude 'logs/'" in bundle_cmd.group(0)
    verify = sh[sh.index("[4/4] verify"):]
    assert "https://fapd.info/.well-known/api-catalog" in verify
    assert "grep -i '^link:'" in verify


def test_shell_scripts_parse():
    for script in (DEPLOY_SH, NGINX / "rehearse.sh"):
        subprocess.run(["bash", "-n", str(script)], check=True)

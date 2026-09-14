"""The fapd-mcp fail2ban jail files (agent-discovery Phase 4B, phase file
§B.10; rationale in docs/ops/plan-2026-09-13-security-review.md §4).

fail2ban is not installed on the development machine, so the filter is
exercised by a small re-implementation of what `fail2ban-regex` does:
read `failregex` from the .conf, substitute fail2ban's own `<HOST>`
expansion, and match sample lines in the nginx `fapd_mcp` log format
(deploy/vps/nginx/default.conf). rehearse.sh row M17 runs the same
substitution over a real log; the staged install script runs the real
`fail2ban-regex` on the box.
"""

import configparser
import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
F2B = PROJECT_ROOT / "deploy" / "vps" / "fail2ban"
FILTER = F2B / "filter.d" / "fapd-mcp.conf"
JAIL = F2B / "jail.d" / "fapd-mcp.local"
LOGROTATE = F2B / "logrotate.d" / "fapd-mcp"
STAGED = PROJECT_ROOT / "scripts" / "staged" / "2026-09-14-install-fapd-mcp-jail.sh"

# A stand-in for fail2ban's <HOST> expansion (fail2ban/server/failregex.py
# accepts IPv4, IPv6, the IPv4-mapped form and DNS names through several
# alternatives): one class that admits all four, with the mapped prefix
# stripped the way fail2ban strips it. rehearse.sh row M17 uses the same.
HOST = r"(?:::f{4,6}:)?(?P<host>[\w\-.:^_]*\w)"


def _failregex():
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(FILTER)
    pattern = cp.get("Definition", "failregex")
    assert cp.get("Definition", "ignoreregex") == ""
    return re.compile(pattern.replace("<HOST>", HOST))


def _line(status, addr="203.0.113.7", method="POST", ua="curl/8.7.1"):
    return (f'{addr} - [14/Sep/2026:12:00:00 +0000] "{method} /mcp HTTP/1.1" '
            f'{status} 123 rt=0.004 "{ua}"')


@pytest.mark.parametrize("status", [400, 403, 405, 413, 415, 429])
def test_filter_matches_every_rejection_status(status):
    m = _failregex().search(_line(status))
    assert m, status
    assert m.group("host") == "203.0.113.7"       # <HOST> is the FIRST field


@pytest.mark.parametrize("status", [200, 202, 404, 500, 503])
def test_filter_ignores_successes_and_the_legitimate_404(status):
    """404 is a modern client probing an unimplemented method (-32601);
    5xx is our side, not the client's."""
    assert not _failregex().search(_line(status)), status


def test_filter_matches_the_status_as_a_whole_token():
    """The ini parser strips trailing whitespace, so the pattern ends in
    \\s rather than a literal space; without it 4000 would count as 400."""
    rx = _failregex()
    assert not rx.search(_line("4000"))
    assert not rx.search(_line("4291"))
    assert rx.search(_line(429))


def test_filter_counts_only_posts_to_mcp():
    rx = _failregex()
    assert rx.search(_line(405, method="POST"))
    assert not rx.search(_line(405, method="GET"))     # GET /mcp is the 405 signpost, not abuse
    assert not rx.search(_line(400).replace("/mcp", "/index.html"))


def test_filter_captures_ipv6_and_forwarded_addresses():
    rx = _failregex()
    assert rx.search(_line(403, addr="2001:db8::1")).group("host") == "2001:db8::1"
    assert rx.search(_line(403, addr="::ffff:198.51.100.9")).group("host") == "198.51.100.9"


def test_filter_never_needs_a_request_body():
    """The fapd_mcp log format carries no body; the regex must not rely on one."""
    conf = FILTER.read_text(encoding="utf-8")
    assert "jsonrpc" not in conf and "$request_body" not in conf


def test_jail_settings_are_the_security_review_values():
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(JAIL)
    j = cp["fapd-mcp"]
    assert j["enabled"] == "true"
    assert j["backend"] == "polling"
    assert j["banaction"] == "iptables-allports"
    assert j["chain"] == "DOCKER-USER"
    assert j["logpath"] == "/opt/fapd/logs/mcp-access.log"
    assert j["filter"] == "fapd-mcp"
    assert j["maxretry"] == "20"
    assert j["findtime"] == "10m"
    # B.10: thresholds are explicit, not inherited from the cohabitant's
    # [DEFAULT]; the ban is finite and grows, never permanent.
    assert j["bantime"] == "1h"
    assert j["bantime.increment"] == "true"
    assert j["bantime.maxtime"] == "1d"
    assert "127.0.0.1/8" in j["ignoreip"] and "172.16.0.0/12" in j["ignoreip"]
    assert list(cp.sections()) == ["fapd-mcp"]            # never a [DEFAULT] edit


def test_jail_logpath_is_the_web_containers_mounted_log():
    """One path, three files: the compose mount, the nginx access_log and
    the jail's logpath must name the same file on the host."""
    compose = (PROJECT_ROOT / "deploy" / "vps" / "docker-compose.yml").read_text(encoding="utf-8")
    conf = (PROJECT_ROOT / "deploy" / "vps" / "nginx" / "default.conf").read_text(encoding="utf-8")
    assert "- ./logs:/var/log/fapd:rw" in compose
    assert "access_log /var/log/fapd/mcp-access.log fapd_mcp;" in conf
    assert LOGROTATE.read_text(encoding="utf-8").startswith("# /opt/fapd/logs/mcp-access.log")


def test_logrotate_snippet_copytruncates_daily():
    text = LOGROTATE.read_text(encoding="utf-8")
    assert "/opt/fapd/logs/mcp-access.log {" in text
    for directive in ("daily", "rotate 7", "compress", "delaycompress",
                      "missingok", "notifempty", "copytruncate"):
        assert re.search(rf"^\s+{re.escape(directive)}$", text, re.MULTILINE), directive
    assert "postrotate" not in text          # the container is not signalled; copytruncate instead


def test_staged_install_script_tests_before_it_reloads_and_verifies_the_chain():
    sh = STAGED.read_text(encoding="utf-8")
    assert STAGED.stat().st_mode & 0o111, "not executable"
    subprocess.run(["bash", "-n", str(STAGED)], check=True)
    assert sh.index("fail2ban-client -t") < sh.index("fail2ban-client reload")
    assert sh.index("== 1. Preconditions") < sh.index("install -m 644")
    for needle in ("iptables -S DOCKER-USER", "f2b-fapd-mcp", "fail2ban-regex",
                   "fail2ban-client status fapd-mcp", "unbanip", "SUCCESS:", "FAILURE:"):
        assert needle in sh, needle
    # additive only: the cohabitant's jail.local is never written
    assert "/etc/fail2ban/jail.local" not in sh
    assert "jail.local" not in "\n".join(ln for ln in sh.splitlines()
                                         if not ln.lstrip().startswith("#")
                                         ).replace("fapd-mcp.local", "")
    assert "/etc/fail2ban/filter.d/fapd-mcp.conf" in sh
    assert "/etc/fail2ban/jail.d/fapd-mcp.local" in sh
    assert "/etc/logrotate.d/fapd-mcp" in sh

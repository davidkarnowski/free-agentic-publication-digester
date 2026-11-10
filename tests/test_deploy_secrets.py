"""Guards for how this project reaches its server (2026-08-07, plan P4;
rewritten 2026-11-10).

The repository is public. Since 2026-11-10 the project holds NO
connection details at all: no key path, no login, no address, no port,
in any tracked file or in its local env file. The connection comes from
an external connector named in the gitignored deploy/vps/deploy.env
(deploy/vps/scripts/_env.sh). These tests pin that, and pin that the env
file still never leaves the working tree: not into git, not into a
container image.
"""

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / "deploy" / "vps" / "deploy.env"
EXCLUDES = PROJECT_ROOT / "deploy" / "common" / "repo-excludes.txt"
DEPLOY_SH = PROJECT_ROOT / "deploy" / "vps" / "scripts" / "deploy.sh"


def _tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [PROJECT_ROOT / f for f in out.split()]


def test_deploy_env_is_gitignored():
    """git check-ignore, not a substring search: only git's own answer
    proves the file cannot be committed."""
    rc = subprocess.run(
        ["git", "check-ignore", "-q", "deploy/vps/deploy.env"],
        cwd=PROJECT_ROOT, check=False).returncode
    assert rc == 0, "deploy/vps/deploy.env is NOT gitignored"


def test_deploy_env_never_reaches_the_backend_build_context():
    """The one that matters most. Without this exclude the repo export
    copies the file to $REMOTE_DIR/repo/ and `COPY repo/ /app` bakes the
    coordinates into a container image — a leak into an artifact."""
    assert "deploy/vps/deploy.env" in EXCLUDES.read_text(encoding="utf-8")


def test_deploy_env_never_reaches_the_bundle_rsync():
    """deploy.sh's first rsync has its own inline exclude list on purpose
    (F-004 — those excludes protect the box's own state), so it has to be
    told separately."""
    body = DEPLOY_SH.read_text(encoding="utf-8")
    assert "--exclude 'deploy.env'" in body


def test_the_example_carries_placeholders_only():
    example = (PROJECT_ROOT / "deploy" / "vps"
               / "deploy.env.example").read_text(encoding="utf-8")
    assert "user@host" not in example       # no login shape at all now
    # no resolvable host: nothing that looks like a real IPv4 or FQDN
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", example)
    assert not re.search(r"@[\w.-]+\.(com|net|org|io|info)\b", example)


def test_no_tracked_file_carries_an_ssh_target():
    """A name, an @, and a bare dotted quad is unambiguous — an email
    address never has a raw IPv4 for a domain. Deliberately narrower than
    "no public IP": tracked files legitimately carry third-party
    addresses (fail2ban records in the ops backlog, and IPs quoted inside
    official document text in the published day views).

    This scan covers THIS FILE too, which is why the shape is described
    in words above instead of written out — the first version spelled the
    example literally and tripped its own guard the moment it was
    committed. That is the guard working; exempting the file would have
    been the wrong repair."""
    pattern = re.compile(r"\b[\w.-]+@\d{1,3}(?:\.\d{1,3}){3}\b")
    offenders = []
    for path in _tracked_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        if pattern.search(text):
            offenders.append(str(path.relative_to(PROJECT_ROOT)))
    assert not offenders, f"SSH targets in tracked files: {offenders}"


CONNECTION_KEYS = re.compile(
    r"^\s*(export\s+)?(SSH_KEY|VPS|PORT|SSH_ALIAS)=|IdentityFile", re.MULTILINE)
SCRIPTS = [PROJECT_ROOT / "deploy" / "vps" / "scripts" / "_env.sh",
           DEPLOY_SH,
           PROJECT_ROOT / "deploy" / "vps" / "scripts" / "box.sh",
           PROJECT_ROOT / "deploy" / "dev" / "scripts" / "dev-seed.sh"]


def _code(path):
    return "\n".join(ln for ln in path.read_text(encoding="utf-8").splitlines()
                     if not ln.lstrip().startswith("#"))


def test_no_env_file_holds_a_connection_value():
    """The example always, and the operator's local file when it exists:
    neither may carry a key path, login, address or port. _env.sh refuses
    such a file at run time too; this catches it before anything runs."""
    files = [PROJECT_ROOT / "deploy" / "vps" / "deploy.env.example"]
    if ENV_PATH.exists():
        files.append(ENV_PATH)
    for path in files:
        assert not CONNECTION_KEYS.search(path.read_text(encoding="utf-8")), path.name


def test_env_sh_refuses_an_env_file_with_a_connection_value():
    assert "SSH_KEY|VPS|PORT|SSH_ALIAS" in _code(SCRIPTS[0])
    assert "exit 1" in _code(SCRIPTS[0])


def test_env_sh_never_sources_the_env_file():
    """grep, never `.`/source: a stale line cannot quietly come back."""
    code = _code(SCRIPTS[0])
    assert ". \"$FAPD_ENV_FILE\"" not in code
    assert "source " not in code


def test_no_script_carries_its_own_ssh_identity():
    """Every connection goes through the connector: no script builds its
    own ssh, scp or key options, and no script reads the retired
    home-folder env file."""
    for path in SCRIPTS:
        code = _code(path)
        if path == SCRIPTS[0]:      # _env.sh names the old keys to refuse them
            code = "\n".join(ln for ln in code.splitlines()
                             if not ("SSH_KEY" in ln and "VPS" in ln and "PORT" in ln))
        for banned in ("SSH_KEY", "SSH_OPTS", "SCP_OPTS", "ssh -i", "IdentityFile",
                       '"$VPS"', "${VPS}", ".fapd-deploy.env"):
            assert banned not in code, f"{path.name}: {banned}"
        for line in code.splitlines():
            stripped = line.lstrip()
            assert not stripped.startswith(("ssh ", "scp ", "exec ssh")), f"{path.name}: {line}"


def test_the_old_wrapper_is_gone_and_box_sh_uses_the_connector():
    scripts = PROJECT_ROOT / "deploy" / "vps" / "scripts"
    assert not (scripts / "vps-ssh.sh").exists()
    code = _code(scripts / "box.sh")
    assert '. "$REPO_ROOT/deploy/vps/scripts/_env.sh"' in code
    assert 'box "$@"' in code


def test_no_tracked_file_points_at_a_private_key_or_the_old_env_file():
    """A tracked path to a private key file, or to the retired
    home-folder env file, is a connection detail in a public repo. Dated
    plans and staged scripts are records of what was done then and are
    never rewritten (CLAUDE.md §8), so they are out of scope."""
    pattern = re.compile(r"(~|\$HOME|/Users/[^/\s]+)/\.ssh/id_|\.fapd-deploy\.env")
    offenders = []
    for path in _tracked_files():
        rel = str(path.relative_to(PROJECT_ROOT))
        if path == Path(__file__).resolve() or rel.startswith(
                ("docs/ops/plan-", "scripts/staged/")):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        if pattern.search(text):
            offenders.append(str(path.relative_to(PROJECT_ROOT)))
    assert not offenders, f"key or env-file paths in tracked files: {offenders}"

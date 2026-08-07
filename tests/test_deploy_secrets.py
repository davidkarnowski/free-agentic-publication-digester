"""Guards for the in-project box coordinates (2026-08-07, plan P4).

The repository is public. `deploy/vps/deploy.env` holds the host, port,
user and key path, lives inside the working tree for convenience, and
must never leave it — not into git, and not into a container image.

Design note: this file never contains a coordinate. The scan reads the
operator's *local, uncommitted* deploy.env and asserts those exact values
appear in zero tracked files, so the guard checks the real secret without
becoming a place the secret is written down. On a machine with no env
file (CI) that scan is vacuous and skips; the mechanism checks below
always run.
"""

import re
import subprocess
from pathlib import Path

import pytest

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
    assert "user@host" in example
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


def test_the_configured_coordinates_appear_in_no_tracked_file():
    """The real check. Reads the local, uncommitted env file and asserts
    its values are absent from everything git tracks."""
    if not ENV_PATH.exists():
        pytest.skip("no deploy/vps/deploy.env on this machine (CI)")

    secrets = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        # REMOTE_DIR is a path on the box and is documented publicly;
        # PORT alone identifies nothing.
        if key.strip() in {"VPS", "SSH_KEY"} and value:
            secrets[key.strip()] = value

    if not secrets:
        pytest.skip("deploy.env carries no VPS/SSH_KEY to check")

    needles = set(secrets.values())
    for value in list(secrets.values()):
        if "@" in value:                    # user@host -> also check the host
            needles.add(value.split("@", 1)[1])

    offenders = []
    for path in _tracked_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue
        for needle in needles:
            if needle and needle in text:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)}")
                break
    assert not offenders, (
        f"{len(offenders)} tracked file(s) contain configured box "
        f"coordinates: {offenders[:5]}")

"""Drift guards for deploy/vps/scripts/evidence-commit.sh.

The script's correctness is textual and ordering-dependent, and it runs
only on the box — no test exercises it end to end, so each guard here
pins a property whose absence cost a day of the public record.

F-021 (2026-08-07): the container's .git is an rsynced snapshot baked by
Dockerfile.backend, so its origin/main ref is frozen at deploy time. The
script pushed without ever fetching, and every operator commit made after
a deploy turned the nightly push into a silent non-fast-forward.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "deploy" / "vps" / "scripts" / "evidence-commit.sh"


def _body():
    return SCRIPT.read_text(encoding="utf-8")


def _first_index(needle):
    text = _body()
    for i, line in enumerate(text.splitlines()):
        if line.lstrip().startswith("#"):
            continue          # comments may explain a step; only code counts
        if needle in line:
            return i
    raise AssertionError(f"{needle!r} not found in live lines of {SCRIPT}")


def test_it_fetches_before_it_commits():
    """The whole of F-021. Fetching after the commit would still leave the
    push racing a stale ref, and fetching after staging would abort with
    changes already staged."""
    assert _first_index("git fetch origin main") < _first_index("commit -m")


def test_it_rebases_before_it_pushes():
    assert _first_index("git rebase --autostash origin/main") < \
        _first_index("git push origin main")


def test_the_rebase_autostashes():
    """RenderWorker._refresh_health rewrites site/sources*.html on a clock
    independent of the journal, so the tree is reliably dirty even with
    collectors paused — a bare rebase aborts on unstaged changes."""
    assert "git rebase --autostash origin/main" in _body()


def test_the_ssh_command_is_exported_not_inlined_on_the_push():
    """Inlined on push alone, fetch had no key — which is why no fetch was
    ever added. accept-new matters too: a freshly recreated container has
    an empty known_hosts and a bare fetch fails 'Host key verification
    failed', which reads like a credential fault and is not."""
    body = _body()
    assert "export GIT_SSH_COMMAND=" in body
    assert "StrictHostKeyChecking=accept-new" in body
    push_line = [ln for ln in body.splitlines()
                 if "git push origin main" in ln and not ln.lstrip().startswith("#")]
    assert push_line and "GIT_SSH_COMMAND" not in push_line[0]


def test_an_empty_stage_still_publishes_an_earlier_unpushed_commit():
    """Nothing staged is not the same as nothing to publish: a previously
    failed push leaves a good commit behind, and the old early exit
    stranded it for another day."""
    assert _first_index("rev-list --count origin/main..HEAD") > \
        _first_index("git add digests/")


def test_it_verifies_the_push_landed():
    """EODWorker keys durable state off this script's exit code, so
    success has to mean the evidence is actually on the remote."""
    body = _body()
    assert _first_index("git rev-parse HEAD") > _first_index("git push origin main")
    assert "exit 6" in body


def test_the_staged_path_allowlist_survives():
    """GUIDE §10 evidence exemption: only these paths may ever ride an
    automated commit. Never widen without an operator decision."""
    body = _body()
    assert "git add digests/ provenance/ site/ SOURCES.md" in body
    assert "^(digests/|provenance/|site/|SOURCES\\.md)" in body
    assert "git reset --mixed" in body


def test_failure_modes_have_distinct_exit_codes():
    """collect.EODWorker records the code as the durable failure reason;
    'non-zero' would not tell an operator which fault to fix."""
    body = _body()
    for code in ("exit 2", "exit 3", "exit 4", "exit 5", "exit 6"):
        assert code in body, code


# ------------------------------------- the origin remote must be BAKED --
# F-020: deploy.sh re-flips the remote with `docker exec ... git remote
# set-url`, which writes to the running container's layer, not the image.
# A recreate outside a deploy reverted it to the laptop tree's HTTPS
# remote (F-008) and silently broke pushes — demonstrated 2026-08-05,
# when an OAuth-token rotation recreated the backend. Nothing looked
# wrong until a push was actually tried, because the repo is public so
# anonymous HTTPS *fetch* still worked.

DOCKERFILE = PROJECT_ROOT / "deploy" / "vps" / "Dockerfile.backend"
DEPLOY_SH = PROJECT_ROOT / "deploy" / "vps" / "scripts" / "deploy.sh"
SSH_REMOTE = ("git@github.com:davidkarnowski/"
              "free-agentic-publication-digester.git")


def test_the_image_bakes_the_ssh_remote():
    """Baked in the image is the only place that survives a recreate."""
    body = DOCKERFILE.read_text(encoding="utf-8")
    live = "\n".join(ln for ln in body.splitlines()
                     if not ln.lstrip().startswith("#"))
    assert "remote set-url origin" in live
    assert SSH_REMOTE in live


def test_the_baked_remote_is_set_after_the_repo_is_copied():
    """A remote set before `COPY repo/ /app` would be overwritten by the
    copied .git — the failure would look exactly like not setting it."""
    lines = [ln for ln in DOCKERFILE.read_text(encoding="utf-8").splitlines()
             if not ln.lstrip().startswith("#")]
    copy_at = next(i for i, ln in enumerate(lines) if "COPY repo/ /app" in ln)
    remote_at = next(i for i, ln in enumerate(lines)
                     if "remote set-url origin" in ln)
    assert copy_at < remote_at


def test_safe_directory_precedes_the_baked_remote():
    """`git -C /app` runs in the same layer; a later `git config` would
    not help it."""
    lines = [ln for ln in DOCKERFILE.read_text(encoding="utf-8").splitlines()
             if not ln.lstrip().startswith("#")]
    safe_at = next(i for i, ln in enumerate(lines)
                   if "safe.directory /app" in ln)
    remote_at = next(i for i, ln in enumerate(lines)
                     if "remote set-url origin" in ln)
    assert safe_at < remote_at


def test_the_two_remote_urls_cannot_drift():
    """The URL is written in both the Dockerfile and deploy.sh's
    belt-and-braces re-flip. If they ever disagree, a deploy would undo
    the baked value — the regression this fix exists to prevent."""
    deploy_body = DEPLOY_SH.read_text(encoding="utf-8")
    assert SSH_REMOTE in deploy_body
    assert "remote set-url origin" in deploy_body


def test_no_https_remote_is_ever_set_in_the_stack():
    """The HTTPS remote arrives via the rsynced .git, never by us — if a
    script starts writing one, the recreate hazard is back."""
    for path in (DOCKERFILE, DEPLOY_SH):
        live = "\n".join(ln for ln in path.read_text(
            encoding="utf-8").splitlines() if not ln.lstrip().startswith("#"))
        assert "https://github.com/davidkarnowski" not in live, path

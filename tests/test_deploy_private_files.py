"""Nothing git ignores reaches the backend build context (2026-10-07).

rsync does not read git's ignore rules. Until this date the repo export
in deploy.sh (and the dev stack's stager) carried every private, untracked
file in the working tree onto the server and into the backend image:
the verbose work log, untracked ops documents, private notes. The fix is
deploy/common/git-ignored.sh, which lists whatever git ignores at export
time, including the user's global excludes file, so a private file never
ships and its name never has to appear in a tracked file.
"""

import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

HELPER = PROJECT_ROOT / "deploy" / "common" / "git-ignored.sh"


def _git(cwd, *args, env=None):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


def _repo(tmp_path):
    """A throwaway repository with the helper at its real relative path."""
    repo = tmp_path / "repo"
    (repo / "deploy" / "common").mkdir(parents=True)
    shutil.copy2(HELPER, repo / "deploy" / "common" / "git-ignored.sh")
    home = tmp_path / "home"
    home.mkdir()
    gcfg = home / "gitconfig"
    gcfg.write_text("")
    env = {**os.environ, "HOME": str(home), "GIT_CONFIG_GLOBAL": str(gcfg),
           "GIT_CONFIG_NOSYSTEM": "1"}
    _git(repo, "init", "-q", env=env)
    (repo / ".gitignore").write_text("notes.md\nprivate/\n")
    (repo / "tracked.md").write_text("public\n")
    _git(repo, "add", ".gitignore", "tracked.md", "deploy", env=env)
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "commit", "-q", "-m", "init", env=env)
    (repo / "notes.md").write_text("private\n")
    (repo / "private").mkdir()
    (repo / "private" / "log.md").write_text("private\n")
    return repo, env, gcfg


def _listed(repo, env):
    out = subprocess.run([str(repo / "deploy" / "common" / "git-ignored.sh")],
                         cwd=repo, check=True, capture_output=True, text=True, env=env)
    return set(out.stdout.split())


def test_ignored_files_are_listed_anchored_and_tracked_files_are_not(tmp_path):
    repo, env, _ = _repo(tmp_path)
    listed = _listed(repo, env)
    assert {"/notes.md", "/private/"} <= listed
    assert "/tracked.md" not in listed and "/.gitignore" not in listed


def test_the_global_excludes_file_is_honored(tmp_path):
    """A file ignored only by the user's global excludes (TRAJECTORY.md is
    ignored that way in every project) must not ship either."""
    repo, env, gcfg = _repo(tmp_path)
    globalignore = tmp_path / "home" / "ignore"
    globalignore.write_text("TRAJECTORY.md\n")
    gcfg.write_text(f"[core]\n\texcludesFile = {globalignore}\n")
    (repo / "TRAJECTORY.md").write_text("local only\n")
    assert "/TRAJECTORY.md" in _listed(repo, env)


def test_the_dev_export_excludes_what_git_ignores():
    text = (PROJECT_ROOT / "deploy/dev/scripts/dev-up.sh").read_text(encoding="utf-8")
    assert 'deploy/common/git-ignored.sh > "$GIT_IGNORED"' in text
    assert '--exclude-from "$GIT_IGNORED"' in text
    # the explicit floor stays: it names paths that must never ship even
    # if an ignore rule is dropped by mistake
    assert "deploy/common/repo-excludes.txt" in text


def test_the_production_build_context_is_the_commit_and_nothing_else():
    """Since 2026-11-09 deploy.sh exports nothing: the box checks out the
    pushed commit and cleans it, so an ignored or untracked file cannot
    reach the image at all. The floor is checked as "none of these paths is
    tracked", which is what still could ship."""
    text = (PROJECT_ROOT / "deploy/vps/scripts/deploy.sh").read_text(encoding="utf-8")
    code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    assert "clean -ffdxq" in code
    assert "status --porcelain --ignored" in code
    assert "done < deploy/common/repo-excludes.txt" in code
    assert "git-ignored.sh" not in code


def test_deploy_uploads_nothing_from_this_machine():
    """Operator, 2026-11-08: an ordinary update never needs a large upload.
    No rsync or scp in deploy.sh may send local files to the box; the box
    fetches the commit from GitHub, and deploy.sh refuses to run unless main
    is what GitHub has."""
    text = (PROJECT_ROOT / "deploy/vps/scripts/deploy.sh").read_text(encoding="utf-8")
    code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    assert "scp " not in code
    for line in code.splitlines():
        if "rsync" in line:
            assert line.lstrip().startswith('run "rsync'), line
    assert '"${VPS}:' not in code
    assert '[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]' in code
    assert "fetch --quiet origin +refs/heads/main:refs/remotes/origin/main" in code


def test_backend_image_installs_dependencies_once_and_never_the_dev_group():
    """The dependency layer comes from the lockfile alone, before the code,
    so a code change does not download every package again; UV_NO_DEV keeps
    each `uv run` from syncing the dev tools at container start."""
    lines = [ln for ln in (PROJECT_ROOT / "deploy/vps/Dockerfile.backend")
             .read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("#")]
    body = "\n".join(lines)
    assert "UV_NO_DEV=1" in body
    lock_at = next(i for i, ln in enumerate(lines) if "COPY repo/pyproject.toml repo/uv.lock" in ln)
    deps_at = next(i for i, ln in enumerate(lines) if "--no-install-project" in ln)
    code_at = next(i for i, ln in enumerate(lines) if "COPY repo/ /app" in ln)
    assert lock_at < deps_at < code_at
    assert body.count("--mount=type=cache,target=/root/.cache/uv") == 2

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


def test_both_exports_exclude_what_git_ignores():
    for script in ("deploy/vps/scripts/deploy.sh", "deploy/dev/scripts/dev-up.sh"):
        text = (PROJECT_ROOT / script).read_text(encoding="utf-8")
        assert 'deploy/common/git-ignored.sh > "$GIT_IGNORED"' in text, script
        assert '--exclude-from "$GIT_IGNORED"' in text, script
        # the explicit floor stays: it names paths that must never ship even
        # if an ignore rule is dropped by mistake
        assert "deploy/common/repo-excludes.txt" in text, script

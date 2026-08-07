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

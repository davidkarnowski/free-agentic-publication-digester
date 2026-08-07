"""Drift guards for the local dev stack (deploy/dev/).

The dev stack's safety is textual: its compose file must never inherit
the production entrypoint's --eod, never mount secrets, never carry the
evidence-push variable — and its build context must be staged with the
same exclude list production uses, or the two images quietly diverge.
Each guard here pins a hazard the plan documents (deploy/dev/README.md).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEV = PROJECT_ROOT / "deploy" / "dev"
VPS = PROJECT_ROOT / "deploy" / "vps"


def _dev_files():
    return [p for p in DEV.rglob("*")
            if p.is_file() and "repo" not in p.parts]


def test_dockerignores_are_byte_equal():
    """Same build-context hygiene for both stacks — the dev image must be
    built from the same shaped context as production's."""
    assert (DEV / ".dockerignore").read_bytes() == \
        (VPS / ".dockerignore").read_bytes()


def test_dev_stack_never_enables_the_finalizer():
    """--eod on a fresh volume fires the full pipeline (LLM chain,
    evidence push) within one cycle of boot: a fresh collector_state has
    no eod row, and EOD_ET_HOUR=0 means due-at-any-hour."""
    for path in _dev_files():
        assert "--eod" not in path.read_text(encoding="utf-8"), path


def test_dev_stack_cannot_push_evidence():
    """No secrets mount and no evidence-push enablement in the compose
    file or the env example; dev-up.sh actively REFUSES the variable
    (the refusal necessarily names it, so the scripts are checked for
    the guard's presence, not the string's absence)."""
    compose_lines = (DEV / "docker-compose.yml").read_text(
        encoding="utf-8").splitlines()
    # Comments may (and do) EXPLAIN these guards; only live YAML counts.
    live = "\n".join(ln for ln in compose_lines
                     if not ln.lstrip().startswith("#"))
    assert "secrets" not in live
    assert "FAPD_EVIDENCE_PUSH" not in live
    env = (DEV / "dev.env.example").read_text(encoding="utf-8")
    assert not any(ln.startswith("FAPD_EVIDENCE_PUSH")
                   for ln in env.splitlines())  # commented mention only
    up = (DEV / "scripts" / "dev-up.sh").read_text(encoding="utf-8")
    assert "GUARD ABORT" in up and "FAPD_EVIDENCE_PUSH" in up


def test_dev_stack_never_reflips_the_origin():
    """The origin re-flip (F-008) points a repo at the production SSH
    remote for evidence pushes — VPS-only, never mirrored in dev."""
    for path in _dev_files():
        assert "remote set-url" not in path.read_text(encoding="utf-8"), path


def test_both_stagers_share_the_exclude_list():
    """One exclude list, two stagers (deploy.sh's repo export and
    dev-up.sh's local stage) — the drift this prevents is two different
    build contexts claiming to be the same image."""
    excl = "deploy/common/repo-excludes.txt"
    assert (PROJECT_ROOT / excl).is_file()
    assert excl in (VPS / "scripts" / "deploy.sh").read_text(encoding="utf-8")
    assert excl in (DEV / "scripts" / "dev-up.sh").read_text(encoding="utf-8")
    # the staged dev context must be excluded from the prod export, or a
    # laptop that ran dev-up.sh bakes a recursive repo copy into prod
    assert "deploy/dev/repo/" in (PROJECT_ROOT / excl).read_text(encoding="utf-8")


def test_dev_env_example_defuses_the_prod_defaults():
    env = (DEV / "dev.env.example").read_text(encoding="utf-8")
    assert "SITE_BASE_URL=\n" in env          # empty, never fapd.info
    assert "fapd.info" not in "".join(
        ln for ln in env.splitlines(True) if not ln.lstrip().startswith("#"))
    assert "GOVINFO_API_KEY=\n" in env         # no inherited prod key


def test_prod_compose_carries_the_container_bounds():
    """Review D18/D19/R4: the shared VPS's containers are bounded and
    their logs rotate; the backend has a liveness heartbeat. The dev
    stack modeled this block first — prod must not drift back to
    unbounded."""
    compose = (DEV / ".." / "vps" / "docker-compose.yml").read_text(
        encoding="utf-8")
    assert compose.count("mem_limit:") == 2      # web and backend
    assert compose.count("max-size:") == 2       # log rotation on both
    assert compose.count("healthcheck:") == 2    # web wget + backend heartbeat
    assert "collector_state" in compose          # the heartbeat reads the DB


def test_dev_compose_builds_the_production_dockerfile():
    compose = (DEV / "docker-compose.yml").read_text(encoding="utf-8")
    assert "dockerfile: ../vps/Dockerfile.backend" in compose
    assert "nginx:1.30-alpine" in compose      # same pin as production
    # live mode: one serial mechanical cycle, no archive writes
    assert '["--once", "--no-llm", "--no-wayback"]' in compose


def test_no_wayback_flag_installs_a_null_context_manager():
    """--no-wayback threads a stub through the Supervisor's existing
    wayback_factory seam; host workers use it as `with factory() as w:`,
    so the stub must be a context manager whose save() returns None."""
    import collect as collect_script

    stub_factory = collect_script._NullWayback
    with stub_factory() as wayback:
        assert wayback.save("https://example.gov/x") is None


def test_prod_compose_keeps_the_evidence_paths_durable():
    """F-021: /app is the image, not a volume, so digests/ and provenance/
    lived in the container's writable layer — a rebuild after a failed
    push destroys a day of the record, including an insight report no
    re-render reproduces. Removing these mounts restores that hazard."""
    compose = (VPS / "docker-compose.yml").read_text(encoding="utf-8")
    live = "\n".join(ln for ln in compose.splitlines()
                     if not ln.lstrip().startswith("#"))
    assert "fapd-digests:/app/digests" in live
    assert "fapd-provenance:/app/provenance" in live
    # declared, not just mounted
    assert "  fapd-digests:" in live and "  fapd-provenance:" in live


def test_dev_stack_does_not_mount_the_evidence_volumes():
    """The dev stack cannot push (test_dev_stack_cannot_push_evidence), so
    durable evidence paths would only accumulate stale local output that
    looks like the record and is not."""
    live = "\n".join(
        ln for ln in (DEV / "docker-compose.yml").read_text(
            encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#"))
    assert "/app/digests" not in live and "/app/provenance" not in live

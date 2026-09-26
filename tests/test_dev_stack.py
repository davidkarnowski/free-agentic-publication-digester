"""Drift guards for the local dev stack (deploy/dev/).

The dev stack's safety is textual: its compose file must never inherit
the production entrypoint's --eod, never mount secrets, never carry the
evidence-push variable — and its build context must be staged with the
same exclude list production uses, or the two images quietly diverge.
Each guard here pins a hazard the plan documents (deploy/dev/README.md).
"""

import re
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
    """No dev-stack FILE re-flips the origin.

    Scope note (2026-08-07, F-020): the dev compose builds the production
    Dockerfile, which now BAKES the SSH remote — so a dev container does
    carry it, and this test no longer means "dev never sees the SSH
    remote". It means no dev file performs the flip itself.

    That is fine, and arguably safer than the HTTPS remote it replaced: a
    dev container has no secrets mount, so no deploy key, and an SSH
    remote without a key cannot push at all. The real guarantee lives in
    test_dev_stack_cannot_push_evidence — no secrets, no
    FAPD_EVIDENCE_PUSH, no --eod — and that is the one to keep green."""
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


def test_deploy_bundle_rsync_excludes_the_host_log_directory():
    """SR-3 (agent-discovery security review): Phase 4B bind-mounts
    /opt/fapd/logs/ into fapd-web for the /mcp access log fail2ban
    reads. The bundle rsync runs with --delete, so without this exclude
    every deploy erases the host log directory — the F-004 class."""
    sh = (VPS / "scripts" / "deploy.sh").read_text(encoding="utf-8")
    assert "--exclude 'logs/'" in sh
    assert sh.index("--exclude 'logs/'") < sh.index('deploy/vps/ "${VPS}:${REMOTE_DIR}/"')



def test_deploy_bundle_rsync_excludes_the_host_evidence_directory():
    """2026-09-26: /opt/fapd/evidence/ holds incident material that
    exists only on the box. The bundle rsync's --delete tried to remove
    it on the first deploy after it appeared and was refused only by its
    root ownership — the F-004 class, saved by accident."""
    sh = (VPS / "scripts" / "deploy.sh").read_text(encoding="utf-8")
    assert "--exclude 'evidence/'" in sh
    assert (sh.index("--exclude 'evidence/'")
            < sh.index('deploy/vps/ "${VPS}:${REMOTE_DIR}/"'))

def _live_yaml(path):
    return "\n".join(ln for ln in path.read_text(encoding="utf-8").splitlines()
                     if not ln.lstrip().startswith("#"))


def test_both_stacks_mount_the_edge_owned_nginx_config():
    """fapd-web's nginx config left this public repo on 2026-09-21 for the
    operator's operator's private host tree. Prod mounts it from where the edge
    deploys it; dev requires an explicit FAPD_NGINX_DIR and refuses to start
    without one, rather than mounting an empty directory and serving nginx's
    default page — which would look like success.

    Still a DIRECTORY mount in both, for the original reason: a single-file
    bind mount keeps the old inode after rsync replaces the file (2026-07-30).
    And the tree itself must stay gone from the repo."""
    prod = _live_yaml(VPS / "docker-compose.yml")
    dev = _live_yaml(DEV / "docker-compose.yml")
    assert "- /opt/edge/fapd-web:/etc/nginx/conf.d:ro" in prod
    assert "${FAPD_NGINX_DIR:?" in dev and ":/etc/nginx/conf.d:ro" in dev
    assert "/etc/nginx/conf.d/default.conf" not in prod + dev   # never a file
    assert not (VPS / "nginx").exists(), "the config must not return to the public repo"


def test_web_services_share_the_nginx_image_pin():
    prod = re.search(r"image:\s*(nginx:\S+)", _live_yaml(VPS / "docker-compose.yml"))
    dev = re.search(r"image:\s*(nginx:\S+)", _live_yaml(DEV / "docker-compose.yml"))
    assert prod and dev and prod.group(1) == dev.group(1)
    # The deploy-time syntax gate and the rehearsal used to be checked here
    # for the same pin. Both moved to the operator's private host tree with the config on 2026-09-21,
    # so the pin parity that remains in this repo is prod <-> dev, above.


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
    unbounded. The mcp service (Phase 4B) carries the same bounds; its
    healthcheck lives in the package Dockerfile, not here."""
    compose = (DEV / ".." / "vps" / "docker-compose.yml").read_text(
        encoding="utf-8")
    assert compose.count("mem_limit:") == 3      # web, backend, mcp
    assert compose.count("max-size:") == 3       # log rotation on all three
    assert compose.count("healthcheck:") == 2    # web wget + backend heartbeat
    assert "collector_state" in compose          # the heartbeat reads the DB
    dockerfile = (PROJECT_ROOT / "packages" / "static-mcp" / "Dockerfile").read_text(
        encoding="utf-8")
    assert "HEALTHCHECK" in dockerfile and "/healthz" in dockerfile


# ---- the MCP service (agent-discovery Phase 4B; master plan §5 invariants) --

def _compose(path):
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


MCP_HARDENING = {
    "read_only": True,
    "user": "10001:10001",
    "cap_drop": ["ALL"],
    "security_opt": ["no-new-privileges:true"],
    "pids_limit": 64,
    "mem_limit": "128m",
    "command": ["--manifest", "/etc/static-mcp/fapd.manifest.json"],
}


def test_prod_mcp_service_publishes_no_port_and_runs_least_privilege():
    """Docker-published ports bypass ufw (master plan §4): fapd-mcp must be
    reachable only from fapd-web over the internal network. Non-root,
    read-only rootfs, no capabilities, no env, site volume read-only and
    nothing else mounted but the manifest directory."""
    doc = _compose(VPS / "docker-compose.yml")
    mcp = doc["services"]["mcp"]
    assert "ports" not in mcp and "expose" not in mcp
    for key, value in MCP_HARDENING.items():
        assert mcp[key] == value, key
    assert mcp["networks"] == ["fapd_mcp"]
    assert mcp["volumes"] == ["fapd-site:/srv/site:ro", "./mcp:/etc/static-mcp:ro"]
    assert "env_file" not in mcp and "environment" not in mcp
    assert mcp["build"] == {"context": "./repo/packages/static-mcp"}
    assert mcp["container_name"] == "fapd-mcp"      # the name default.conf resolves
    assert mcp["restart"] == "unless-stopped"
    assert "profiles" not in mcp                    # up with the site, always


def test_prod_networks_keep_zero_egress_and_web_bridges_exactly_two():
    doc = _compose(VPS / "docker-compose.yml")
    assert doc["networks"]["fapd_mcp"] == {"driver": "bridge", "internal": True}
    web = doc["services"]["web"]
    assert web["networks"] == ["fapd_edge", "fapd_mcp"]
    assert "depends_on" not in web                   # the site starts without mcp
    assert "./logs:/var/log/fapd:rw" in web["volumes"]
    assert web["volumes"].count("./logs:/var/log/fapd:rw") == 1
    # the backend stays off the mcp network: coupling is the site volume only
    assert doc["services"]["backend"]["networks"] == ["fapd_backend"]


def test_dev_compose_mirrors_the_prod_mcp_service_and_network():
    prod = _compose(VPS / "docker-compose.yml")["services"]["mcp"]
    dev_doc = _compose(DEV / "docker-compose.yml")
    dev = dev_doc["services"]["mcp"]
    for key in MCP_HARDENING:
        assert dev[key] == prod[key], key
    assert dev["cpus"] == prod["cpus"] and dev["logging"] == prod["logging"]
    assert dev["volumes"] == prod["volumes"]
    assert dev["build"] == prod["build"]              # the staged repo/ in both
    assert "ports" not in dev and "env_file" not in dev
    assert dev["networks"] == {"fapd_mcp": {"aliases": ["fapd-mcp"]}}
    assert dev_doc["networks"]["fapd_mcp"] == {"driver": "bridge", "internal": True}
    web = dev_doc["services"]["web"]
    assert "fapd_mcp" in web["networks"] and "default" in web["networks"]
    assert any(v.endswith(":/var/log/fapd") for v in web["volumes"])   # nginx -t opens the log path


def test_dev_up_stages_the_package_the_dev_mcp_service_builds():
    """dev-up.sh stages the whole tree into deploy/dev/repo/ with the shared
    exclude list; packages/ is not excluded, so the build context exists."""
    excl = (PROJECT_ROOT / "deploy" / "common" / "repo-excludes.txt").read_text(encoding="utf-8")
    assert "packages" not in excl
    up = (DEV / "scripts" / "dev-up.sh").read_text(encoding="utf-8")
    assert 'rsync -a --delete --exclude-from deploy/common/repo-excludes.txt ./ "$DEV/repo/"' in up


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

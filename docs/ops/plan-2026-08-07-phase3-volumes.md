# P3 — make the evidence survive a container rebuild

**Depends on P0.** Do not land this until `36ae3b9` is on `origin/main`.

**Files:** `deploy/vps/docker-compose.yml`, `deploy/dev/docker-compose.yml`
(parity only), `docs/ops/ops-backlog.md` (OB-19),
`tests/test_dev_stack.py` (only if a drift test demands it).

## Why

`docker inspect fapd-backend` on 2026-08-07 showed exactly three mounts:
`fapd-data → /app/data`, `fapd-site → /app/site`, and the read-only secrets
bind. **`/app/digests`, `/app/provenance` and `/app/.git` are the container's
writable layer** (90.4 MB at diagnosis). A rebuild resets `/app` to the image,
so an unpushed evidence commit — and the digest markdown, manifest and insight
report inside it — is destroyed silently. That is not a hypothetical: it was
the state the system sat in all day on 2026-08-07.

P1 and P2 make the push reliable and its failure loud. This phase is the
defence in depth for the case where it fails anyway and someone deploys.

## Diff sketch

**1. `deploy/vps/docker-compose.yml`** — two mounts on the `backend` service,
beside the existing pair, and two volume declarations:

```yaml
    volumes:
      - fapd-data:/app/data
      - fapd-site:/app/site
      # Evidence durability (F-021, 2026-08-07): digests/ and provenance/ are
      # written by the finalizer and committed by evidence-commit.sh. Without
      # these they live in the container's writable layer, so a rebuild after
      # a failed push destroys a day of the record — the exact near-miss of
      # 2026-08-07. With them, a lost .git is survivable: the next
      # evidence-commit re-stages the surviving files and re-commits.
      - fapd-digests:/app/digests
      - fapd-provenance:/app/provenance
      - ./secrets:/app/secrets:ro

volumes:
  fapd-site:
  fapd-data:
  fapd-digests:
  fapd-provenance:
```

**2. Add the stale-output caveat as a comment in the same block** — this is
the F-009 class, now extended, and must be disclosed where a future reader
will hit it:

> Docker seeds a named volume from the image only when the volume is
> **empty**; a rebuild never refreshes a populated one (F-009). So a
> *retired* digest — as on 2026-08-03 — will not disappear from the box by
> deploying. It must be deleted from the volume explicitly, exactly as the
> site volume already requires.

**3. `docs/ops/ops-backlog.md`** — new **OB-19**, "Retiring an evidence file
needs a volume cleanup step", with the trigger: *the next time a digest,
manifest or day view is retired from the record.* Cross-reference the
2026-08-03 site-volume incident, where `build_site` never deleted stale
outputs and the next evidence commit resurrected the retired pages.

**4. `deploy/dev/docker-compose.yml`** — mirror the mounts **only** if a drift
test requires parity. The dev stack must not gain a push path; check
`tests/test_dev_stack.py::test_dev_stack_cannot_push_evidence`,
`::test_dev_compose_builds_the_production_dockerfile` and
`::test_prod_compose_carries_the_container_bounds` before editing, and run
them after.

## Justification

This is the `fapd-site` pattern already in the file, applied to the other two
paths the finalizer writes. It is deliberately *not* a fix for `.git`: once
the files are durable, the git history does not need to be. A rebuild
resets `.git` to the deployed snapshot, `git add digests/ provenance/` finds
the surviving 2026-08-06 files as new, and the next evidence commit carries
them. **The fix self-heals** — which is a stronger property than making
`.git` durable would give, and it avoids the confusing state of a persistent
`.git` whose HEAD disagrees with the image's working tree.

## Alternatives considered

- **Bind-mount `/opt/fapd/repo` at `/app`** — makes `.git` durable and lets
  deploy fetch instead of re-baking, but it shadows the image's `.venv`
  (built by `uv sync --frozen` at `/app`) and destroys the property that the
  deployed code is byte-for-byte the tree that passed the test gate. Too
  invasive for the problem.
- **Make `/app/.git` its own volume** — leaves a persistent HEAD pointing at
  a commit whose working tree the image just overwrote; every deploy would
  show a huge phantom diff.
- **Rely on P1/P2 alone** — considered and rejected by the operator: the
  project's entire claim is provenance, and one bad night plus one deploy
  would still lose a day permanently.
- **Back up the writable layer on a timer** — a second mechanism to maintain
  when the volume already does the job.

## Risk / blast radius

- **Extends the F-009 stale-output class** to `digests/` and `provenance/`.
  Disclosed in the compose comment and tracked as OB-19; not silently
  accepted.
- **First mount seeds from the image**, which is why P0 is a hard
  prerequisite. Landing this while `36ae3b9` is unpushed destroys 2026-08-06.
- `SOURCES.md` is an evidence path but sits at the repo root, so it stays
  ephemeral. Acceptable and stated in the comment rather than left as an
  unexplained asymmetry: it is deterministically regenerable from the
  registry via `scripts/sources_doc.py`.
- Disk: `digests/` plus `provenance/` is tens of MB and grows slowly; the box
  was at 47% of 96 GB.

## Verification

```sh
uv run pytest -q tests/test_dev_stack.py

# after deploy, on the box
sudo docker inspect fapd-backend --format '{{range .Mounts}}{{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
#   expect fapd_fapd-digests -> /app/digests and fapd_fapd-provenance -> /app/provenance

# the real test: rebuild and confirm the evidence is still there
sudo docker compose --profile backend build backend && sudo docker compose --profile backend up -d
sudo docker exec fapd-backend ls -la /app/digests/2026-08-06.md /app/provenance/runs/insight-2026-08-06.md
```

## Rollback

Remove the two mounts and redeploy. **Before** removing them, confirm the
volume contents are on `origin/main`; only then
`docker volume rm fapd_fapd-digests fapd_fapd-provenance`.

## Dependencies

**P0 must be complete.** Independent of P1, P2 and P4.

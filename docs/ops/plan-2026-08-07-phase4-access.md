# P4 — bring VPS access into the project, safely

**Files:** `deploy/vps/scripts/_env.sh` (new), `deploy/vps/scripts/vps-ssh.sh`
(new), `deploy/vps/scripts/deploy.sh`, `deploy/vps/deploy.env.example`,
`.gitignore`, `deploy/common/repo-excludes.txt`,
`tests/test_deploy_secrets.py` (new).

## Why

The VPS half of `/fapd-health` is currently unrunnable from this project.
`deploy.sh` requires `$VPS` and `$SSH_KEY` from the environment, `.env` holds
no server keys, and `docs/ops/SERVER-GUIDE.md` deliberately points at a
private dossier in a **sibling project tree**. On 2026-08-07 that forced the
health check to reach outside the repository to find coordinates — which the
operator has ruled out going forward.

The constraint is unchanged: the repository is public (CLAUDE.md §13), so no
host, port, user, or key path may ever be committed. The resolution is a
gitignored file inside the project plus a test that proves it stays out.

## Diff sketch

**1. `deploy/vps/deploy.env`** — *not created by this phase*; the operator
writes it from the example, `chmod 0600`. Same keys `deploy.sh` already
consumes: `SSH_KEY`, `VPS`, `PORT`, `REMOTE_DIR`.

**2. `deploy/vps/scripts/_env.sh`** (new) — one resolver, sourced by both
scripts, with a documented lookup order:

```sh
# Box coordinates: resolved once, here, so deploy.sh and vps-ssh.sh cannot
# drift. Order is deliberate — an explicit env var wins, then the in-project
# gitignored file, then the legacy home-directory location.
#   1. $FAPD_DEPLOY_ENV        explicit override
#   2. deploy/vps/deploy.env   in-project, gitignored, 0600
#   3. ~/.fapd-deploy.env      the original location, still honoured
for candidate in "${FAPD_DEPLOY_ENV:-}" "$REPO_ROOT/deploy/vps/deploy.env" "$HOME/.fapd-deploy.env"; do
  [ -n "$candidate" ] && [ -f "$candidate" ] && { . "$candidate"; break; }
done
: "${SSH_KEY:?no box coordinates — copy deploy/vps/deploy.env.example to deploy/vps/deploy.env}"
: "${VPS:?...}"
PORT="${PORT:-22}"
REMOTE_DIR="${REMOTE_DIR:-/opt/fapd}"
SSH_OPTS=(-i "$SSH_KEY" -p "$PORT" -o BatchMode=yes -o StrictHostKeyChecking=accept-new)
```

Warn (do not fail) if the resolved file is group- or world-readable.

**3. `deploy/vps/scripts/vps-ssh.sh`** (new) — the read-only-by-default
wrapper agents call:

```sh
#!/usr/bin/env bash
# Run a command on the FAPD box. READ-ONLY BY DEFAULT: this wrapper exists so
# health checks need no coordinates, not to make writes casual. Anything that
# writes, restarts, deploys or reboots is gated on the operator's explicit go
# for that specific task (AGENT-VPS-SERVICING-GUIDE §0.1).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
. "$REPO_ROOT/deploy/vps/scripts/_env.sh"
exec ssh "${SSH_OPTS[@]}" "$VPS" "$@"
```

Note in the header that egress may need the sandbox disabled, and that `zsh`
does not word-split unquoted variables — the `SSH_OPTS` array is why (a scalar
silently falls back to port 22).

**4. `deploy/vps/scripts/deploy.sh`** — delete the inline lookup (its
`~/.fapd-deploy.env` source and the four `: "${VAR:?}"` lines) and source
`_env.sh` instead. Behaviour is unchanged for anyone already using
`~/.fapd-deploy.env`.

**5. `.gitignore`** — add, with the reason:

```
# Box coordinates for deploy.sh / vps-ssh.sh — local only, never committed
# (CLAUDE.md §13). The bare `.env` rule above does not match this filename.
deploy/vps/deploy.env
```

**6. `deploy/common/repo-excludes.txt`** — add `deploy/vps/deploy.env`.
**This is the one that matters most:** without it, `deploy.sh`'s second rsync
copies the file into `$REMOTE_DIR/repo/`, and `COPY repo/ /app` bakes the
coordinates into a container image.

**7. `deploy.sh`'s first (bundle) rsync** — add `--exclude 'deploy.env'`
inline. That list is separate from the shared one **on purpose** (F-004: its
excludes protect the box's own state) and the two must not be merged.

**8. `deploy/vps/deploy.env.example`** — update the header to name the
in-project location as the preferred one and to state `chmod 0600`.

**9. `tests/test_deploy_secrets.py`** (new) — the guard, in this repo's
drift-test idiom (`tests/test_dev_stack.py` is the model):

1. `git check-ignore -q deploy/vps/deploy.env` succeeds
2. `deploy/vps/deploy.env` appears in `deploy/common/repo-excludes.txt`
3. `deploy.sh`'s bundle rsync excludes `deploy.env`
4. no file in `git ls-files` contains an IPv4 literal or a
   `<user>@<host>`-shaped SSH target — allowlisting the `user@host`
   placeholder in `deploy.env.example`, documentation examples that are
   obviously placeholders, and version strings that merely look like dotted
   quads (pin the regex to a word-boundaried four-octet form and assert the
   allowlist is exhaustive rather than open-ended)
5. `deploy.env.example` contains placeholders only — no resolvable host

## Justification

Gitignore plus a test, rather than encryption, because the threat being
managed is *accidental commit to a public repository*, and a test that fails
loudly at `pytest` time addresses exactly that. Encryption would add a
dependency and a key to manage for no additional protection against the
actual risk — the file never leaves the operator's machine either way.

`vps-ssh.sh` exists so an agent following the OPS-GUIDE never handles
coordinates at all: it runs `deploy/vps/scripts/vps-ssh.sh '<cmd>'` and the
resolution is somebody else's problem. That is what makes the health skill
self-contained.

Test item 4 is the real control. Items 1–3 verify the mechanism; item 4
catches the failure the mechanism is for — a coordinate pasted into a
runbook, a commit message, or a comment.

## Alternatives considered

- **Encrypted `deploy.env.age` committed to the repo** — survives machine
  loss and is safe to track, but adds `age`/`sops` as a dependency plus a key
  the operator must store elsewhere anyway. Rejected by the operator.
- **Keep `~/.fapd-deploy.env` only** — zero new surface, but does not satisfy
  the in-project requirement. The lookup order keeps it working regardless.
- **Store coordinates in `.env`** — that file is for pipeline runtime secrets
  and is shipped nowhere near the deploy path; mixing the two invites a leak
  through a different exclude list.
- **A `git` pre-commit hook instead of a test** — hooks are not checked out
  with the repo and cannot gate CI.

## Risk / blast radius

The risk this phase *creates* is a file holding server coordinates inside the
working tree. Three excludes and five assertions are the control. The
highest-consequence miss is the repo-export exclude (item 2): a coordinate
baked into a container image is a leak into an artifact, not just a file.

The refactor of `deploy.sh`'s env resolution touches the deploy path. It is
mechanically small and verified by a `--dry-run`-shaped check below before any
real deploy.

## Verification

```sh
uv run pytest -q tests/test_deploy_secrets.py
git check-ignore -v deploy/vps/deploy.env         # must print the .gitignore rule
git status --porcelain | grep deploy.env && echo "LEAK" || echo "clean"

# the resolver works and deploy.sh still parses
bash -n deploy/vps/scripts/deploy.sh deploy/vps/scripts/vps-ssh.sh deploy/vps/scripts/_env.sh
deploy/vps/scripts/vps-ssh.sh 'hostname; ls -d /opt/fapd'

# the file cannot reach the build context
rsync -an --exclude-from deploy/common/repo-excludes.txt ./ /tmp/fapd-export-check/ \
  | grep -c 'deploy.env'                          # expect 0
```

## Rollback

Revert the files. `~/.fapd-deploy.env` keeps working throughout, so a revert
cannot strand the deploy path.

## Dependencies

Independent of P0–P3. **P5's OPS-GUIDE and health-skill edits depend on this**
— they reference `vps-ssh.sh`.

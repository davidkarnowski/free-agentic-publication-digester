#!/usr/bin/env bash
# 2026-08-07 — recover the unpushed EOD evidence commit (36ae3b9).
#
# Why: the 2026-08-07 EOD cycle finalized 2026-08-06 correctly — the digest
# rendered, passed the gates, and has been live on fapd.info since 04:20Z.
# The evidence commit was created and then REJECTED on push:
#
#     ! [rejected]  main -> main (fetch first)
#
# The backend's .git is an rsynced snapshot of the operator's tree, baked into
# the image by Dockerfile.backend's `COPY repo/ /app`. It never fetches. Box
# HEAD is 50095fc; origin advanced to f9dd68c after the deploy, so every push
# since has been a non-fast-forward. The deploy key is fine — ls-remote over
# it returns f9dd68c.
#
# Urgency: /app is NOT a volume. `docker inspect` shows only /app/data,
# /app/site and /app/secrets mounted, so digests/, provenance/ and .git live
# in the container's writable layer. Any rebuild destroys 2026-08-06 — the
# digest markdown, the manifest, and provenance/runs/insight-2026-08-06.md,
# which is LLM-generated and would not come back the same. Re-rendering is
# not an equivalent recovery, and it would re-spend tokens for a day already
# paid for.
#
# Why in-container rather than copying the files out and committing from the
# laptop: it preserves the fapd-pipeline bot authorship every other evidence
# commit carries, and it is the exact fetch -> rebase -> push sequence that
# plan phase P1 makes permanent. This run is the rehearsal.
#
# The rebase is verified clean in advance: f9dd68c added ONLY
# scripts/staged/2026-08-07-repair-presact-journal-class.sh, which the
# evidence commit does not touch.
#
# Blast radius: the git state of one container, plus one additive commit on
# origin/main. Nothing touches the database, the digest content, or the live
# site. Rollback is the backup branch until the push succeeds; after it
# succeeds there is nothing to undo — the push only adds the evidence the
# repository was always meant to hold.
#
# Plan: docs/ops/plan-2026-08-07-phase0-recover.md

set -u
FAILURES=()
fail() { FAILURES+=("$1"); echo "  !! $1"; }

C=fapd-backend
STAMP=2026-08-07
BACKUP_BRANCH="evidence-backup-${STAMP}"
HOST_BACKUP="/opt/fapd/backup/${STAMP}-evidence"
KEY='GIT_SSH_COMMAND="ssh -i /app/secrets/deploy_key -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"'

# git inside the container, with the deploy key available to fetch AND push.
# The old evidence-commit.sh inlined the key on the push line only, which is
# precisely why a fetch was never added.
g() { sudo docker exec -i "$C" sh -lc "cd /app && export $KEY && git $*"; }

echo "== 1. Preconditions (abort before any change) =="

sudo docker ps --format '{{.Names}}' | grep -qx "$C" \
    || { echo "FAILURE: container $C is not running"; exit 1; }

HEAD_SHA="$(g rev-parse HEAD)"
HEAD_SUBJ="$(g log -1 --format=%s)"
echo "  HEAD:    $HEAD_SHA"
echo "  subject: $HEAD_SUBJ"
case "$HEAD_SUBJ" in
    "Daily pipeline evidence"*) ;;
    *) fail "HEAD is not an evidence commit — refusing to rebase someone else's work" ;;
esac

AHEAD="$(g rev-list --count origin/main..HEAD)"
echo "  commits ahead of the baked origin/main: $AHEAD"
[ "$AHEAD" = "1" ] || fail "expected exactly 1 unpushed commit, found $AHEAD"

# An EOD finalize in flight would be racing us for the same tree.
FTARGET="$(sudo docker exec -i "$C" python -c "
import sqlite3
c = sqlite3.connect('file:/app/data/fapd.db?mode=ro', uri=True)
r = c.execute(\"SELECT finalize_target FROM collector_state WHERE worker='eod'\").fetchone()
print(r[0] if r and r[0] else 'NULL')")"
echo "  finalize_target: $FTARGET"
[ "$FTARGET" = "NULL" ] || fail "an EOD finalize is in flight for $FTARGET — wait for it"

g ls-remote origin main >/dev/null 2>&1 || fail "the deploy key cannot reach origin"

g show --stat --format="" HEAD | grep -q 'digests/2026-08-06.md' \
    || fail "the commit does not carry digests/2026-08-06.md"
g show --stat --format="" HEAD | grep -q 'provenance/runs/insight-2026-08-06.md' \
    || fail "the commit does not carry the insight report"

if [ ${#FAILURES[@]} -ne 0 ]; then
    echo "FAILURE: ${FAILURES[*]}"
    echo "Nothing was changed."
    exit 1
fi
echo "  ok — 1 evidence commit ahead, remote reachable, no finalize in flight"

echo "== 2. Rollback artifacts (before any change) =="

g branch -f "$BACKUP_BRANCH" HEAD || fail "could not create the backup branch"
echo "  branch $BACKUP_BRANCH -> $HEAD_SHA"

sudo mkdir -p "$HOST_BACKUP"
sudo docker cp "$C:/app/digests"    "$HOST_BACKUP/" || fail "docker cp digests/ failed"
sudo docker cp "$C:/app/provenance" "$HOST_BACKUP/" || fail "docker cp provenance/ failed"
echo "  host copy under $HOST_BACKUP"
sudo du -sh "$HOST_BACKUP" 2>/dev/null | sed 's/^/  /'

if [ ${#FAILURES[@]} -ne 0 ]; then
    echo "FAILURE: ${FAILURES[*]}"
    echo "No git history was rewritten."
    exit 1
fi

echo "== 3. Fetch, rebase, push =="

g fetch origin main || { echo "FAILURE: fetch failed — nothing changed"; exit 1; }
echo "  fetched; origin/main is now $(g rev-parse --short origin/main)"

# --autostash is required, not defensive: RenderWorker._refresh_health rebuilds
# site/sources*.html on a clock, so the working tree is reliably dirty even
# with collectors paused. A bare rebase would abort on unstaged changes.
if ! g rebase --autostash origin/main; then
    g rebase --abort || true
    echo "FAILURE: rebase conflict against origin/main."
    echo "  The evidence commit is intact on $BACKUP_BRANCH and UNPUSHED."
    echo "  Resolve before any rebuild or the day is lost."
    exit 1
fi
echo "  rebased onto origin/main -> $(g rev-parse --short HEAD)"

g push origin main || { echo "FAILURE: push failed after a clean rebase"; exit 1; }

echo "== 4. Self-verification =="

g fetch origin main
LOCAL="$(g rev-parse HEAD)"
REMOTE="$(g rev-parse origin/main)"
echo "  HEAD:        $LOCAL"
echo "  origin/main: $REMOTE"
[ "$LOCAL" = "$REMOTE" ] || fail "HEAD != origin/main after push"

g ls-remote origin main | grep -q "$LOCAL" || fail "the remote tip does not match HEAD"

# The point of the whole exercise: the day is in the published history.
g log origin/main --oneline -1 | sed 's/^/  origin tip: /'
g show --stat --format="" origin/main | grep -c 'digests/2026-08-06.md' >/dev/null \
    || fail "digests/2026-08-06.md is not in the pushed commit"

STILL_AHEAD="$(g rev-list --count origin/main..HEAD)"
echo "  commits still unpushed: $STILL_AHEAD"
[ "$STILL_AHEAD" = "0" ] || fail "$STILL_AHEAD commit(s) still unpushed"

echo "== Verdict =="
if [ ${#FAILURES[@]} -eq 0 ]; then
    echo "SUCCESS: the 2026-08-06 evidence is on origin/main."
    echo "  Backup branch: $BACKUP_BRANCH (in-container)"
    echo "  Host copy:     $HOST_BACKUP"
    echo "  Next: 'git pull' on the operator machine — the local tree is"
    echo "  missing 2026-08-06 evidence too. This does NOT fix the cause;"
    echo "  the box will diverge again on the next post-deploy commit until"
    echo "  plan phases P1-P3 land."
    exit 0
fi
echo "FAILURE: ${FAILURES[*]}"
exit 1

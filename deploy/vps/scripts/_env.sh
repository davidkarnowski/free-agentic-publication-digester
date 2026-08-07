# Box coordinates, resolved once. Sourced by deploy.sh and vps-ssh.sh so
# the two cannot drift — deploy.sh carried its own inline lookup until
# 2026-08-07, and nothing else could reach the box at all.
#
# The repository is PUBLIC (CLAUDE.md §13): no host, port, user, or key
# path is ever committed. The file this finds is gitignored, excluded
# from BOTH rsync lists, and pinned by tests/test_deploy_secrets.py.
#
# Lookup order — explicit override, then in-project, then the original
# home-directory location, which keeps working for anyone already set up.
#   1. $FAPD_DEPLOY_ENV
#   2. deploy/vps/deploy.env   (in-project, gitignored, chmod 0600)
#   3. ~/.fapd-deploy.env
#
# Callers must set REPO_ROOT before sourcing.
: "${REPO_ROOT:?_env.sh: set REPO_ROOT before sourcing}"

FAPD_ENV_FILE=""
for _candidate in "${FAPD_DEPLOY_ENV:-}" \
                  "$REPO_ROOT/deploy/vps/deploy.env" \
                  "$HOME/.fapd-deploy.env"; do
    if [ -n "$_candidate" ] && [ -f "$_candidate" ]; then
        FAPD_ENV_FILE="$_candidate"
        # shellcheck disable=SC1090
        . "$_candidate"
        break
    fi
done
unset _candidate

if [ -z "$FAPD_ENV_FILE" ]; then
    echo "No box coordinates found. Copy deploy/vps/deploy.env.example to" >&2
    echo "  deploy/vps/deploy.env and fill it in (chmod 0600)." >&2
    exit 1
fi

# A warning, not a failure: the operator may have a reason, and refusing
# to run would be worse than saying so.
if [ "$(uname)" = "Darwin" ]; then
    _mode="$(stat -f '%Lp' "$FAPD_ENV_FILE" 2>/dev/null || echo '')"
else
    _mode="$(stat -c '%a' "$FAPD_ENV_FILE" 2>/dev/null || echo '')"
fi
case "$_mode" in
    ''|600|400) ;;
    *) echo "WARNING: $FAPD_ENV_FILE is mode $_mode — chmod 0600 it." >&2 ;;
esac
unset _mode

: "${SSH_KEY:?set SSH_KEY in $FAPD_ENV_FILE - path to the box SSH key}"
: "${VPS:?set VPS in $FAPD_ENV_FILE - user@host}"
PORT="${PORT:-22}"
REMOTE_DIR="${REMOTE_DIR:-/opt/fapd}"

# zsh does not word-split unquoted variables: a scalar $SSH_OPTS silently
# falls back to port 22. Always an array, always quoted at the call site.
# BatchMode fails fast instead of hanging on a prompt; accept-new because
# a first connection from a fresh machine otherwise blocks on a question
# nothing is there to answer.
SSH_OPTS=(-i "$SSH_KEY" -p "$PORT" -o BatchMode=yes \
          -o StrictHostKeyChecking=accept-new)

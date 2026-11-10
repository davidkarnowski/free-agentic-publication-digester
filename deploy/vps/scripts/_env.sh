# How this project reaches its server. Sourced by deploy.sh and
# dev-seed.sh so the two cannot drift.
#
# The repository holds NO connection details (2026-11-10): no key path,
# no login, no address, no port. The connection comes from an external
# connector command, named by FAPD_BOX_CONNECT in the gitignored
# deploy/vps/deploy.env (or the environment). The connector supplies the
# identity and the address and keeps them outside this repository; the
# private deploy README says which connector to use. The contract:
#
#   $FAPD_BOX_CONNECT ssh -- <command>   one command on the box, raw output,
#                                        the remote exit status
#   $FAPD_BOX_CONNECT rsh                an rsync/scp remote shell; it
#                                        ignores the host word it is given
#
# The repository is PUBLIC (CLAUDE.md §13). tests/test_deploy_secrets.py
# pins that no tracked file and no env file carries a key path, login,
# address or port. deploy.env is read with grep, never sourced, so a
# stale line cannot quietly reintroduce one; a file that still holds a
# connection value is refused.
#
# Callers must set REPO_ROOT before sourcing.
: "${REPO_ROOT:?_env.sh: set REPO_ROOT before sourcing}"

FAPD_ENV_FILE="$REPO_ROOT/deploy/vps/deploy.env"
_from_file() {  # the last VAR="value" line for $1 in deploy.env, unquoted
    sed -n "s/^[[:space:]]*$1=\"\{0,1\}\([^\"]*\)\"\{0,1\}[[:space:]]*\$/\1/p" \
        "$FAPD_ENV_FILE" | tail -1
}
if [ -f "$FAPD_ENV_FILE" ]; then
    if grep -qE '^[[:space:]]*(export[[:space:]]+)?(SSH_KEY|VPS|PORT|SSH_ALIAS)=|IdentityFile|[[:space:]]-i[[:space:]]' \
            "$FAPD_ENV_FILE"; then
        echo "$FAPD_ENV_FILE still holds a connection value (SSH_KEY, VPS, PORT or a key)." >&2
        echo "  Remove it: the connection comes from FAPD_BOX_CONNECT only." >&2
        exit 1
    fi
    [ -n "${FAPD_BOX_CONNECT:-}" ] || FAPD_BOX_CONNECT="$(_from_file FAPD_BOX_CONNECT)"
    [ -n "${REMOTE_DIR:-}" ] || REMOTE_DIR="$(_from_file REMOTE_DIR)"
fi
unset -f _from_file
REMOTE_DIR="${REMOTE_DIR:-/opt/fapd}"

if [ -z "${FAPD_BOX_CONNECT:-}" ]; then
    echo "No connector: set FAPD_BOX_CONNECT in deploy/vps/deploy.env" >&2
    echo "  (copy deploy.env.example; the private deploy README names the connector)." >&2
    exit 1
fi
# $HOME may be written literally in deploy.env; expand only that.
FAPD_BOX_CONNECT="${FAPD_BOX_CONNECT//\$HOME/$HOME}"
# An array, so the command works the same under bash and zsh.
read -r -a _BOX_CONNECT <<<"$FAPD_BOX_CONNECT"
[ -x "${_BOX_CONNECT[0]}" ] || { echo "FAPD_BOX_CONNECT is not executable: ${_BOX_CONNECT[0]}" >&2; exit 1; }

# One command on the box. Like every connection, it is read-only unless
# the operator gave a go for the task.
box() { "${_BOX_CONNECT[@]}" ssh -- "$@"; }

# For rsync:  rsync -e "$BOX_RSH" box:/remote/dir/ local/
BOX_RSH="$FAPD_BOX_CONNECT rsh"

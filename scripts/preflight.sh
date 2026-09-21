#!/usr/bin/env bash
# preflight — the gate that must pass before main moves or the VPS is touched.
#
# WHY THIS FILE EXISTS
# --------------------
# Until 2026-09-21 this repository's gate was a GitHub Actions workflow,
# and the `main` ruleset required its `test` check on every tip commit.
# The operator retired GitHub CI that day: GitHub is now a remote for
# storage, and the check runs here, before anything is pushed or
# deployed.
#
# That trade is honest but it is not free, and the difference is worth
# stating where it will be read. The old gate was ENFORCEMENT — the
# server refused a push that had not passed. This one is DISCIPLINE —
# nothing refuses anything if it is skipped. It therefore has to be
# quick, obvious to run, and identical to what it replaced, because a
# gate that is slow or surprising is a gate that gets skipped.
#
# WHAT IT REPRODUCES
# ------------------
# Exactly the three steps the retired workflow ran, in order:
#
#     uv sync
#     uv run ruff check src/ scripts/ tests/ packages/
#     uv run pytest -q
#
# Note `packages/` in the lint path: `static-mcp` lives there and the
# workflow linted it. A local run that omits it is not this gate.
#
# WHERE THE ENVIRONMENTS STILL DIFFER, and why it is acceptable:
#   - The workflow ran ubuntu-latest; this runs the operator's macOS.
#   - The workflow took whatever CPython setup-uv resolved; this takes
#     whatever the local uv resolves (3.14.7 at time of writing).
#   `requires-python = ">=3.12"`, production runs 3.12.14 in the
#   container, and the suite is pure-Python with no platform-specific
#   assertions — so the gap is real but has never produced a divergence.
#   --strict re-pins the interpreter to the lowest supported version to
#   close it when that matters (before a release, or after touching
#   anything version-sensitive).
#
# THE DRIFT THIS WAS WRITTEN AFTER
# --------------------------------
# On 2026-09-21 a compose edit landed after the suite had been run, and
# `tests/test_dev_stack.py` — which pins the dev stack's logging config
# to prod's — failed in CI on a change that had passed locally minutes
# earlier. The tests were right and the human was out of order. Running
# this file immediately before the push is the whole remedy.
#
# USAGE
#   scripts/preflight.sh            # the gate
#   scripts/preflight.sh --strict   # same, pinned to CPython 3.12
#   scripts/preflight.sh --quick    # lint + changed-file tests only;
#                                   # NOT the gate, for inner-loop use

set -euo pipefail

cd "$(dirname "$0")/.."

STRICT=0
QUICK=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    --quick)  QUICK=1 ;;
    -h|--help) sed -n '2,60p' "$0"; exit 0 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

PY_ARGS=()
if [ "$STRICT" = 1 ]; then
  PY_ARGS=(--python 3.12)
  echo "== preflight (strict: CPython 3.12, matching production) =="
else
  echo "== preflight =="
fi

fail() { echo; echo "PREFLIGHT FAILED: $1" >&2; exit 1; }

echo "-- 1/4 environment --"
uv --version
uv run "${PY_ARGS[@]}" python --version

echo "-- 2/4 sync --"
uv sync "${PY_ARGS[@]}" --quiet || fail "uv sync"

echo "-- 3/4 lint --"
uv run "${PY_ARGS[@]}" ruff check src/ scripts/ tests/ packages/ || fail "ruff"

if [ "$QUICK" = 1 ]; then
  echo "-- 4/4 tests (QUICK: not the gate) --"
  CHANGED=$(git diff --name-only HEAD -- 'tests/*.py' | tr '\n' ' ')
  if [ -n "$CHANGED" ]; then
    uv run "${PY_ARGS[@]}" pytest -q $CHANGED || fail "pytest (quick)"
  else
    echo "   no changed test files; run without --quick for the real gate"
  fi
  echo
  echo "QUICK PASS — this is NOT the gate. Run without --quick before pushing."
  exit 0
fi

echo "-- 4/4 tests --"
uv run "${PY_ARGS[@]}" pytest -q || fail "pytest"

# The dirty-tree check is last on purpose: it is advice, not a failure.
# Evidence paths (digests/, provenance/, site/, SOURCES.md) are expected
# to be dirty on a machine that has run the pipeline.
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo
  echo "note: working tree has uncommitted changes — the run above covered"
  echo "      them, but make sure what you push is what was tested:"
  git status --porcelain | sed 's/^/        /'
fi

echo
echo "PREFLIGHT PASS"
echo "This is the gate that replaced GitHub CI on 2026-09-21."
echo "main is still protected against force-push and deletion; it is NOT"
echo "protected against an untested push. That part is on you."

#!/usr/bin/env bash
# Print every path git ignores in this working tree, one per line,
# anchored at the tree's root ("/path"), for rsync --exclude-from.
#
# Why (2026-10-07): rsync does not read git's ignore rules. The repo
# export to the backend build context therefore carried every private,
# untracked file in the tree (the verbose work log, untracked ops docs,
# notes under docs/private/) onto the server and into the backend image,
# deploy after deploy. repo-excludes.txt only names what someone
# remembered to list. This lists whatever git ignores at the moment of
# the export: the repo's .gitignore, .git/info/exclude and the user's
# global excludes file. A private file that git ignores therefore never
# ships, and its name never has to appear in a tracked file.
set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root (common -> deploy -> root)
git -c core.quotePath=false ls-files --others --ignored --exclude-standard --directory \
  | sed 's#^#/#'

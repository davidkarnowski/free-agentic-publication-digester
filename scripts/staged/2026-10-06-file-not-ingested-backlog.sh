#!/usr/bin/env bash
# 2026-10-06 — one-time: file the INBOX backlog of mail that will not be
# ingested to <prefix>/not-ingested.
#
# Why. Operator ruling 2026-10-06 (CLAUDE.md §14): government mailing-list
# mail from senders the registry does not know is filed to
# <prefix>/not-ingested and never ingested. The collector applies that to
# mail as it arrives; this script clears what arrived before. A read-only
# look the same day found, at or below the collector's INBOX watermark:
#   - 28 messages from 10 unregistered government lists, and
#   - 4 bulletins from senders registered on 2026-10-01 (nih-orwh-email,
#     medicare-email) that arrived before their registration, were
#     recorded `unregistered`, and were passed by the watermark. The
#     operator chose not to ingest them ("pass on ingesting these emails
#     at this time").
#
# What this does. Selects, by headers only, every INBOX message at or
# below the watermark that is either (a) from an unregistered sender and a
# government mailing list, or (b) from a registered sender but recorded
# `unregistered` in mailbox_messages. Then marks it read and MOVEs it to
# <prefix>/not-ingested: the same STORE \Seen + UID MOVE the poll uses.
#
# What this does NOT do. No body is fetched; nothing is ingested, parsed
# or stored; the database, the watermark and mailbox_messages are not
# written. Personal and other non-government mail is not selected. Mail
# above the watermark is never touched (the poll has not reached it).
# The junk folder is not read.
#
# Blast radius: Gmail labels on at most the selected messages. Nothing is
# deleted (no delete, expunge or COPY emulation). Rollback: in Gmail,
# select the label not-ingested and move the messages back to the inbox;
# the UID list this script prints is the record of what moved.
#
# Run from the repository root on the operator's machine:
#   scripts/staged/2026-10-06-file-not-ingested-backlog.sh            # dry run
#   scripts/staged/2026-10-06-file-not-ingested-backlog.sh apply N    # N = the dry run's count
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODE="${1:-dry-run}"
EXPECT="${2:-}"
case "$MODE" in dry-run|apply) ;; *) echo "usage: $0 [dry-run | apply <count>]" >&2; exit 2;; esac
if [ "$MODE" = apply ] && ! [[ "$EXPECT" =~ ^[0-9]+$ ]]; then
    echo "FAILURE: apply needs the dry run's count, e.g. '$0 apply 32'" >&2; exit 2
fi

"$REPO_ROOT/deploy/vps/scripts/vps-ssh.sh" \
  "sudo -n timeout 300 docker exec -i -e MODE=$MODE -e EXPECT=$EXPECT fapd-backend uv run python -" <<'PY'
import os, sqlite3, sys
from collections import Counter
from fapd import config, email_sources
from fapd.sources import load_registry

mode, expect = os.environ["MODE"], os.environ.get("EXPECT", "")
fail = []
print(f"== 2026-10-06 file-not-ingested backlog ({mode}) ==")

# -- preconditions: abort before any change if the world is not the plan --
prefix = config.IMAP_FILE_TO
if not prefix:
    fail.append("IMAP_FILE_TO is not set: this is not the filing host")
if not hasattr(email_sources, "FILED_NOT_INGESTED"):
    fail.append("the running code predates the not-ingested rule: deploy first")
db = sqlite3.connect(f"file:{config.PIPELINE_DB}?mode=ro", uri=True)
row = db.execute("SELECT last_uid FROM mailbox_state WHERE mailbox='INBOX'").fetchone()
if not row:
    fail.append("no INBOX watermark in mailbox_state")
if fail:
    print("FAILURE: " + "; ".join(fail)); sys.exit(1)
watermark = row[0]
recorded = {uid: out for uid, out in db.execute(
    "SELECT uid, outcome FROM mailbox_messages WHERE mailbox='INBOX'")}
entries = [e for e in load_registry() if e["type"] == "email"
           and e["status"] in ("active", "planned") and e.get("sender")]
allow = email_sources._sender_map(entries)
dest = f"{prefix}/{email_sources.FILED_NOT_INGESTED}"

with email_sources.MailboxClient(file_to="") as client:
    uids = [u for u in client.all_uids() if u <= watermark]
    picked, why = [], Counter()
    for uid, head in sorted(client.headers_many(uids).items()):
        sender = email_sources._from_address(head)
        if sender not in allow and email_sources.is_government_list(head, sender):
            picked.append(uid); why[f"unregistered list  {sender}"] += 1
        elif sender in allow and recorded.get(uid) == "unregistered":
            picked.append(uid); why[f"pre-registration   {sender}"] += 1
    print(f"INBOX at or below watermark UID {watermark}: {len(uids)} message(s);"
          f" selected for {dest}: {len(picked)}")
    for k, n in sorted(why.items()):
        print(f"  {n:3}  {k}")
    print("  UIDs: " + " ".join(map(str, picked)))
    if mode == "dry-run":
        print(f"DRY RUN: nothing moved. To apply: apply {len(picked)}")
        sys.exit(0)
    if str(len(picked)) != expect:
        print(f"FAILURE: selection is {len(picked)}, the dry run said {expect}: nothing moved")
        sys.exit(1)

    # -- the change --
    moved = client.file_messages(picked, dest)
    print(f"moved {moved} of {len(picked)} to {dest}")

    # -- self-verification --
    left = sorted(set(picked) & set(client.all_uids()))
    if left:
        fail.append(f"{len(left)} selected message(s) still in INBOX: {left}")
    if moved != len(picked):
        fail.append(f"file_messages reported {moved}, expected {len(picked)}")
    client.use_folder(dest)
    print(f"{dest} now holds {len(client.all_uids())} message(s)")
    client.use_folder("INBOX")

if fail:
    print("FAILURE: " + "; ".join(fail)); sys.exit(1)
print(f"SUCCESS: {len(picked)} message(s) filed to {dest}; nothing ingested, nothing deleted")
PY

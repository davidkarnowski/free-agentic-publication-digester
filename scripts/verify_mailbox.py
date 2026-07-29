"""One-connection sanity check for the project mailbox (docs/email-sources.md).

Read-only by construction: connects via IMAPS, lists folders, counts
messages, and peeks at recent bulletin senders/subjects with BODY.PEEK —
nothing is marked seen, nothing is modified.

Usage: uv run python scripts/verify_mailbox.py [--peek N]
"""

import argparse
import email
import email.policy
import imaplib
import sys

from fapd import config


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--peek", type=int, default=5,
                    help="show sender/subject of the N most recent messages")
    args = ap.parse_args()

    if not (config.IMAP_HOST and config.IMAP_USER and config.IMAP_PASSWORD):
        print("IMAP_HOST / IMAP_USER / IMAP_PASSWORD not set in .env")
        return 1

    print(f"connecting to {config.IMAP_HOST} as {config.IMAP_USER} (IMAPS)…")
    box = imaplib.IMAP4_SSL(config.IMAP_HOST)
    try:
        box.login(config.IMAP_USER, config.IMAP_PASSWORD)
        print("login: OK")

        _status, folders = box.list()
        print(f"folders ({len(folders)}):")
        for f in folders[:12]:
            print("  ", f.decode(errors="replace"))

        _status, (count,) = box.select("INBOX", readonly=True)
        total = int(count)
        _status, (unseen_data,) = box.search(None, "UNSEEN")
        unseen = len(unseen_data.split()) if unseen_data else 0
        print(f"INBOX: {total} messages ({unseen} unseen)")

        if args.peek and total:
            _status, (ids,) = box.search(None, "ALL")
            recent = ids.split()[-args.peek:]
            print(f"most recent {len(recent)} (read-only peek):")
            for mid in reversed(recent):
                _status, data = box.fetch(
                    mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
                msg = email.message_from_bytes(
                    data[0][1], policy=email.policy.default)
                print(f"  {msg['date']}\n    from: {msg['from']}\n"
                      f"    subj: {msg['subject']}")
        return 0
    finally:
        try:
            box.logout()
        except Exception as exc:  # noqa: BLE001 — best-effort cleanup
            print(f"(logout: {exc!r})")


if __name__ == "__main__":
    sys.exit(main())

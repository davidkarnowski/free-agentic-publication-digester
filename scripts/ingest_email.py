"""Poll the project mailbox for email-distributed sources (GUIDE §3).

Reads our own inbox, never an agency server: registered senders only, the
raw message stored as the capture, DKIM verified and its key archived.
Unregistered mail is not downloaded at all.

Usage:
  uv run python scripts/ingest_email.py [--verbose] [--limit N] [--ids a,b]
  uv run python scripts/ingest_email.py --dry-run    # report, store nothing
"""

import argparse
import sys

from fapd import config, db, email_sources, logging_setup
from fapd.sources import load_registry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--limit", type=int, help="process at most N new messages")
    ap.add_argument("--ids", help="comma-separated source ids (targeted poll)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be ingested; write nothing")
    ap.add_argument("--since-uid", type=int,
                    help="start the watermark at this UID (first run: skip mail"
                         " that predates the subscriptions)")
    args = ap.parse_args()
    logging_setup.setup(verbose=args.verbose)

    if not (config.IMAP_HOST and config.IMAP_USER and config.IMAP_PASSWORD):
        print("IMAP_HOST / IMAP_USER / IMAP_PASSWORD not set in .env"
              " (see docs/email-sources.md §3)")
        return 1

    entries = [e for e in load_registry()
               if e["type"] == "email" and e["status"] in ("active", "planned")
               and e.get("sender")]
    if args.ids:
        wanted = set(args.ids.split(","))
        entries = [e for e in entries if e["id"] in wanted]
    if not entries:
        print("no registered email sources matched")
        return 1
    print(f"polling {config.IMAP_USER} for {len(entries)} registered source(s)")

    conn = db.connect()
    try:
        with email_sources.MailboxClient() as client:
            if args.since_uid is not None:
                email_sources._save_state(conn, client.folder, args.since_uid,
                                          client.uid_validity())
                print(f"watermark set to UID {args.since_uid}")
            if args.dry_run:
                return _dry_run(client, conn, entries, args.limit)
            results = email_sources.poll_mailbox(client, conn, entries,
                                                 limit=args.limit)
        total_items = sum(r["items"] for r in results)
        for r in results:
            print(f"  {r['id']:26} messages={r['messages']:3} items={r['items']:4}"
                  f" dupes={r['duplicates']:3} errors={r['errors']}")
        print(f"total new items: {total_items}")
        return 0
    finally:
        conn.close()


def _dry_run(client, conn, entries, limit):
    """Show what a real poll would ingest — allowlist decisions and parsed
    item counts — without writing anything."""
    allow = email_sources._sender_map(entries)
    last_uid, _validity = email_sources._state(conn, client.folder)
    uids = client.uids_since(last_uid)
    if limit:
        uids = uids[:limit]
    print(f"{len(uids)} message(s) after UID {last_uid}; "
          f"{len(allow)} registered sender(s)\n")
    matched = ignored = items = admin = 0
    for uid in uids:
        head = client.headers(uid)
        if head is None:
            continue
        entry = allow.get(email_sources._from_address(head))
        if entry is None:
            ignored += 1
            continue
        raw = client.raw(uid)
        import email as _email
        import email.policy as _policy
        msg = _email.message_from_bytes(raw, policy=_policy.default)
        matched += 1
        if email_sources.is_administrative(msg):
            admin += 1
            print(f"  {entry['id']:26} UID {uid:6} ->  admin  "
                  f"{str(head['subject'])[:52]}")
            continue
        parsed = email_sources.parse_bulletin(msg)
        items += len(parsed)
        print(f"  {entry['id']:26} UID {uid:6} -> {len(parsed):3} item(s)"
              f"  {str(head['subject'])[:52]}")
    print(f"\nwould ingest {items} item(s) from {matched - admin} bulletin(s); "
          f"{admin} subscription-administrivia message(s) skipped; "
          f"{ignored} ignored (sender not registered — body never fetched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

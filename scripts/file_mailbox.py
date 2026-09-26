"""One-time sweep: file registered-sender mail the poll has already passed.

Going forward the poll files what it handles (config.IMAP_FILE_TO;
docs/email-sources.md §3a). This clears the backlog that arrived before
filing existed. Deterministic and header-only: the From address against the
registry allowlist, the Subject against the administrivia pattern. No body
is fetched, nothing is parsed or stored, no model is called. Unregistered
mail is never touched.

Safety ceiling: only UIDs at or below the watermark in the database this
runs against. The poll reads INBOX only, so filing a message it has not
reached would hide it from ingestion. Run it where the production database
lives, or pass --through-uid with the production watermark — never higher.

Usage:
  uv run python scripts/file_mailbox.py                  # dry run (default)
  uv run python scripts/file_mailbox.py --apply          # mark read + move
  uv run python scripts/file_mailbox.py --through-uid N  # explicit ceiling
"""

import argparse
import sys

from fapd import config, db, email_sources, logging_setup
from fapd.sources import load_registry


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="mark read and move; without it nothing is written")
    ap.add_argument("--prefix", default=config.IMAP_FILE_TO or "FAPD",
                    help="folder/label prefix (default IMAP_FILE_TO, else FAPD)")
    ap.add_argument("--through-uid", type=int,
                    help="ceiling UID (default: this database's watermark)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    logging_setup.setup(verbose=args.verbose)

    if not (config.IMAP_HOST and config.IMAP_USER and config.IMAP_PASSWORD):
        print("IMAP_HOST / IMAP_USER / IMAP_PASSWORD not set in .env")
        return 1
    entries = [e for e in load_registry()
               if e["type"] == "email" and e["status"] in ("active", "planned")
               and e.get("sender")]

    conn = db.connect()
    try:
        with email_sources.MailboxClient(file_to=args.prefix) as client:
            last_uid, saved_validity = email_sources._state(conn, client.folder)
            validity = client.uid_validity()
            if args.through_uid is not None:
                ceiling = args.through_uid
            elif saved_validity is None or saved_validity != validity:
                print(f"no usable watermark for {client.folder} in this database"
                      f" (saved UIDVALIDITY {saved_validity}, server {validity});"
                      " pass --through-uid")
                return 1
            else:
                ceiling = last_uid
            print(f"{config.IMAP_USER} {client.folder}: ceiling UID {ceiling}"
                  f" ({'explicit' if args.through_uid is not None else 'watermark'});"
                  f" {len(entries)} registered source(s)")

            plan, ignored = email_sources.sweep_plan(client, entries, ceiling)
            by_source = {}
            for sub, pairs in plan.items():
                for _uid, source_id in pairs:
                    key = (source_id, sub)
                    by_source[key] = by_source.get(key, 0) + 1
            for (source_id, sub), n in sorted(by_source.items()):
                print(f"  {source_id:30} -> {args.prefix}/{sub:9} {n:5}")
            print(f"{len(plan[email_sources.FILED_INGESTED])} to"
                  f" {args.prefix}/{email_sources.FILED_INGESTED},"
                  f" {len(plan[email_sources.FILED_ADMIN])} to"
                  f" {args.prefix}/{email_sources.FILED_ADMIN};"
                  f" {ignored} not from a registered sender (left alone)")

            if not args.apply:
                print("dry run — nothing written (pass --apply to file)")
                return 0
            for sub, pairs in plan.items():
                if pairs:
                    filed = client.file_messages([u for u, _ in pairs],
                                                 f"{args.prefix}/{sub}")
                    print(f"filed {filed} to {args.prefix}/{sub}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())

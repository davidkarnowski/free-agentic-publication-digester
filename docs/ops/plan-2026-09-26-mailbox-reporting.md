# Plan 2026-09-26 — Junk-folder polling, the mailbox log, and email reporting

*Operator-approved 2026-09-26. Follows docs/ops/plan-task-template.md.
Branch `feature/mailbox-junk`; ships in one deploy with the junk-folder
poll and the second batch of email sources.*

On 2026-09-26 a sweep of the project mailbox found three failures that no
report had shown. Registered senders' bulletins sat in Gmail's Spam folder
and were never ingested. EPA's bulletins arrived from an address the
registry did not list, so for two months EPA's health said only "no
bulletin recorded". Dozens of government lists the mailbox received were
not registered at all. All three were invisible for the same reason. Only
ingested items are stored, so a message that was refused, administrative,
from an unregistered sender, or parsed to nothing left no trace.

## T1 — GUIDE §3: the junk-folder carve-out

- **Why:** the junk-folder poll refuses DKIM failures, and GUIDE §3 says
  failing messages are "still ingested". GUIDE changes come before code.
- **Files:** `GUIDE.md` (the §3 DKIM bullet, amended in place with a
  dated note).
- **Diff sketch:** append an "Amended 2026-09-26 (operator)" sentence.
  Junk-folder mail from a registered sender is ingested only on a verified
  and aligned signature; anything else is left in place, not stored, and
  counted refused; the inbox rule is unchanged.
- **Justification:** this is the operator's ruling ("as long as we aren't
  letting spam through"), and spam filtering is where forged From headers
  collect.
- **Alternatives:** a Gmail "never spam" filter per sender. Rejected: it
  must be maintained by hand, it drifts from the registry, and it doesn't
  cover a sender's new address.
- **Risk:** none at runtime. The public text must follow (T4).
- **Verification:** read GUIDE §3; `git diff GUIDE.md`.
- **Rollback:** revert the amendment and set `IMAP_POLL_JUNK=0`.
- **Dependencies:** none.

## T2 — `mailbox_messages`: one row per message that concerns us

- **Why:** reports need durable facts. The poll's return value and
  `collector_state.last_result` are status lines (CLAUDE.md §9).
- **Files:** `docs/schema.md` (first, as the design authority),
  `src/fapd/db.py`, `src/fapd/email_sources.py`, tests.
- **Diff sketch:** an additive table keyed by (mailbox, uid_validity,
  uid), with these columns:
  - `observed_at`, `source_id`, `sender`, `outcome`, `items`,
    `duplicates`, `no_url_items`, `dkim`;
  - `outcome` is one of `ingested`, `administrative`, `duplicate`,
    `empty`, `refused`, `error` or `unregistered`.

  A registered sender's message always gets a row. An unregistered sender
  gets a row only when the message is government list mail: a sender
  domain under .gov, .mil or govdelivery.com AND a `List-Unsubscribe` or
  `List-Id` header. Personal mail, including a person writing from a .gov
  address, never produces a row.
- **Justification:** one table serves the source pages, health and the
  nightly report, and it self-migrates through `_DDL`.
- **Alternatives:** reuse `item_journal`. Rejected: that journal is keyed
  on packages, and most of these messages produce none.
- **Risk:** the stored unregistered sender addresses are government list
  addresses. They live in the database only and never render on the site
  or in committed reports.
- **Verification:** tests for each outcome, and a test that personal mail
  and non-list .gov mail write no row.
- **Rollback:** the table is additive; leaving it unused is harmless.
- **Dependencies:** none.

## T3 — Health and source pages read the mailbox log

- **Why:** a subscription that has only confirmed must read differently
  from one that has gone quiet, and junk-folder refusals must be visible.
- **Files:** `src/fapd/health.py`, `src/fapd/publish.py`, tests.
- **Diff sketch:** `source_health` adds, for each email source, the
  messages, bulletins, notices, refused count and last message over the
  health window. The no-data reason becomes "subscription confirmed (N
  notices), no bulletin yet" when notices exist, and the email card and
  page print the mailbox counts. The health labels are unchanged.
- **Justification:** the labels are a public taxonomy; the reason text is
  where the specifics belong.
- **Risk:** a card layout change; this is covered by the existing
  publish tests and the accessibility doctrine's pinned-test rule.
- **Dependencies:** T2.

## T4 — Public text says what the code does

- **Files:** `src/fapd/publish.py` (the email section intro, the
  per-source Authenticity row, the "planned" definition),
  `docs/email-sources.md` §5a.
- **Diff sketch:**
  - Authenticity: the inbox labels failures; the junk folder refuses
    them.
  - "planned" for email: the subscription is read and anything it
    delivers is ingested, and promotion to active follows a dated coverage
    evaluation.
- **Dependencies:** T1.

## T5 — The nightly insight report gets an email section

- **Why:** the operator should hear about misclassification the night it
  happens, not two months later.
- **Files:** `src/fapd/insight.py`, tests.
- **Diff sketch:** `gather` adds `m["email"]`, computed from
  `mailbox_messages` and `extracted_texts` over the work window. It
  carries:
  - per-source counts;
  - flags: notices only for 14+ days, bulletins parsing to zero items,
    items without a URL, the same URL through two registered email sources,
    and junk refusals;
  - unregistered government lists as counts only, with the number new
    since the previous day.

  `render_report` prints a "Mailbox" section.
- **Justification:** the report is committed publicly, so it carries
  counts and registry ids only. Sender addresses stay in the database and
  are read with `scripts/file_mailbox.py --report-unregistered`.
- **Dependencies:** T2.

## T6 — Related-source notes and a known-bug entry

- **Files:** `sources/registry.yaml` (+ SOURCES.md), `CLAUDE.md` §10.
- **Diff sketch:** each new email entry names the existing entries that
  can publish the same news. Merging happens only by URL (GUIDE §3), so
  the notes tell a reader where a second listing of one event can come
  from. The §10 entry records that `_url_seen_elsewhere` drops an email
  copy at ingest when the web copy came first, contrary to GUIDE §3's
  "every observation stays". Its exact-string comparison means it rarely
  fires: 970 pairs were kept over 30 days. Confirm with the operator
  before changing it.
- **Dependencies:** none.

## Verification (whole plan)

- `scripts/preflight.sh` green.
- After the deploy:
  - the first junk poll logs its watermark;
  - `mailbox_messages` gains rows;
  - the next insight report carries the Mailbox section;
  - `sources.html` shows the new wording.

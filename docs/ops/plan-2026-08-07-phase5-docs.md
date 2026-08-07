# P5 — runbooks, disclosure, governing docs, deploy

**Deploy step is operator-gated.** Everything before it is local.

**Files:** `docs/ops/OPS-GUIDE.md`, `docs/ops/SERVER-GUIDE.md`,
`.claude/skills/fapd-health/SKILL.md`, `docs/ops/findings.md`,
`docs/ops/ops-backlog.md`, `CLAUDE.md`, `WORKLOG.md`.

## Why

The repair is worthless if the next health check cannot see the state it
creates, and CLAUDE.md §13 is explicit that prose overclaiming what the code
does is itself a defect. Three documents currently describe a system that does
not exist: the OPS-GUIDE's local block reads a database that has been dead
since 2026-07-30, its VPS block says `ssh <box>` with no way to resolve
`<box>`, and neither mentions that an evidence push can fail.

## Diff sketch

**1. `docs/ops/OPS-GUIDE.md`**

- Rewrite the **VPS checks** block to use `deploy/vps/scripts/vps-ssh.sh`
  (P4) in place of `ssh <box>`, dropping the "access facts in the private
  dossier" note.
- Add an **evidence-push check** to that block — the thing that failed:

```sh
deploy/vps/scripts/vps-ssh.sh \
  'sudo docker exec fapd-backend git -C /app rev-list --count origin/main..HEAD'
#   ^ 0 = everything published; >0 = an evidence commit is stranded in the
#     container's writable layer and a rebuild will destroy it

deploy/vps/scripts/vps-ssh.sh 'sudo docker exec fapd-backend python -c "…"' \
#   ^ read collector_state: evidence_pushed_at set, evidence_push_error NULL
```

- Add an honesty note to the **Local checks** heading: this block runs against
  the operator machine's development database. On 2026-08-07 its newest
  collector activity was 2026-07-30 and `llm_ledger.db` had not been written
  since Jul 30 — **it says nothing about production.** Token spend by
  purpose/backend is only auditable on the box until the ledger is seeded or
  mirrored. (Log this gap as an ops-backlog item if it is not already one.)
- Bump `Last reviewed`.

**2. `docs/ops/SERVER-GUIDE.md`**

- Replace the "read the sibling project's guide for connection facts"
  instruction with the in-project mechanism: `deploy/vps/deploy.env` +
  `vps-ssh.sh`. Keep the private-dossier pointer for the *human* box facts
  (quirks, cohabitation, fail2ban) that do not belong in a public repo.
- Add review-table rows dated 2026-08-07: containers/segmentation
  re-verified, cert unchanged (expires 2026-10-28), **evidence push repaired**
  (was: silently failing since the 2026-08-06 deploy).

**3. `.claude/skills/fapd-health/SKILL.md`**

- Preconditions: replace "access facts from the operator's private dossier"
  with `deploy/vps/scripts/vps-ssh.sh` (still requires `ssh-add -l`).
- Add the evidence-push check to step 3, and state the rule plainly: **a
  digest that is live on the site but absent from `origin/main` is a finding,
  not a pass.** That distinction is exactly what the 2026-08-07 check had to
  discover by hand.

**4. `docs/ops/findings.md` — F-021** (next free ID; F-020 is the highest in
use). Record the full chain, because each link failed independently and each
is a lesson:

> baked `.git` that never fetches → non-fast-forward push → failure recorded
> only in `last_result`, which nothing reads → no retry until the next EOD,
> which fails identically → and `/app` is ephemeral, so a deploy would have
> destroyed the day.

Include the observed evidence: `! [rejected] main -> main (fetch first)`, the
`eod` row reading `finalize_attempts=0` while the push had failed, and the
fact that the digest was live on fapd.info the entire time — the public record
and the repository disagreed for thirteen hours and nothing noticed.

**5. `docs/ops/ops-backlog.md` — OB-19** (next free ID; OB-18 is the highest
in use): retiring an evidence file now needs an explicit volume cleanup step
(P3). Trigger: the next retirement of a digest, manifest or day view.
Cross-reference the 2026-08-03 site-volume incident.

**6. `CLAUDE.md`**

- **§9 (intentional)** — new entry: *a failed evidence push is durable, loud,
  and retried on a bounded ladder*; `evidence-commit.sh` fetches and rebases
  before pushing **on purpose**, because the box's `.git` is a deploy-time
  snapshot that never fetches on its own. Do not "simplify" the rebase away.
- **§14 (decision log)** — dated 2026-08-07 entry: the incident, the three
  operator decisions (in-container recovery, evidence volumes, gitignored
  in-project coordinates), and the resulting invariant — *the digest being
  live is not evidence that it was published to the repository; those are two
  separate gates now, and both are checked.*
- **§12 (where to look first)** — add a row for VPS access:
  `deploy/vps/scripts/vps-ssh.sh` + `deploy.env`.

**7. `WORKLOG.md`** — append-only session entry (never retroactively edited):
what was observed, what was decided, what was verified, what remains.

**8. Deploy** — `deploy/vps/scripts/deploy.sh`, **on the operator's explicit
ask in the session**, never inferred (CLAUDE.md §13). The script's own test
gate runs first. Then the OPS-GUIDE cadence rule: the VPS block immediately
and **again ~5 minutes later**.

## Justification

The findings entry records the *chain*, not just the root cause, because four
independent safeguards would each have caught this alone and none existed. A
findings note that says only "the box diverged" would teach the wrong lesson.

The §9 entry is defensive: the fetch-and-rebase will look like removable
ceremony to a future reader who has never seen it diverge. §9 is precisely the
list for things that look like overhead and are not.

## Alternatives considered

- **Skip the CLAUDE.md §9 entry** — rejected; §9 exists for exactly this
  class, and the rebase is the most "simplifiable-looking" line in the repair.
- **Fold F-021 into the OB-19 backlog item** — rejected; the scope rule is
  explicit that findings and backlog items are different files with different
  jobs, and an item lives in exactly one.
- **Deploy immediately after P1/P2 and document later** — rejected; status
  tables and checklists update in the same commit as the work they describe
  (CLAUDE.md §8).

## Risk / blast radius

Documentation carries no runtime risk. The deploy step carries the usual one
and is gated. The real risk here is *inaccuracy*: every claim added must be
verified against the code, not against this plan — grep the implementation
before repeating a status claim, since doc lines in this repo lag the code.

## Verification

```sh
uv run pytest -q            # test_agents_docs.py and the drift tests cover doc/registry claims
uv run ruff check src/ scripts/ tests/
grep -n "Last reviewed" docs/ops/OPS-GUIDE.md docs/ops/SERVER-GUIDE.md
```

Then walk the OPS-GUIDE VPS block start to finish as written — if a command
in it does not run verbatim, the document is wrong. After deploy, run
`/fapd-health` twice per the cadence rule and confirm the evidence-push check
appears and reads clean.

## Rollback

Revert the docs. If the deploy needs undoing, redeploy the previous commit —
`deploy.sh` is idempotent and rebuilds from the tree it is given.

## Dependencies

**All of P0–P4.** The OPS-GUIDE and health-skill edits specifically require
P4 (`vps-ssh.sh`) and P2 (the `collector_state` columns they read).

# P5 — deploy + prove tonight (operator-gated VPS writes)

1. Branch `arch/observation-day-filing`; P0–P4 commits; CI green;
   ff-merge to main; push.
2. `deploy/dev/scripts/dev-up.sh` — advisory render against the seed;
   eyeball §1 empty-state wording on a day with no CREC.
3. `deploy/vps/scripts/deploy.sh` (rebuilds image → container lands on
   the same commit as origin — the F-019/F-020 lesson).
4. On-box, run the one-shot:
   `sudo docker exec fapd-backend sh -lc "cd /app && uv run --no-sync
   python scripts/migrate_digest_day.py"` — then read-only verify:
   zero NULL `digest_day`; `CREC-2026-08-05`'s row (if arrived) has
   `digest_day = 2026-08-06`.
5. OPS-GUIDE VPS health block immediately + ~5 min.
6. **Fallback (if not green by ~22:00 ET):** cherry-pick only the P3
   §1 empty-state wording (report.py prose, no schema) so tonight's
   digest stops implying Congress was idle; land the rest tomorrow.
7. Morning-after proof: digest 2026-08-06 §1 populated or honestly
   empty; coverage gate passed; evidence commit on GitHub; insight
   report sane.

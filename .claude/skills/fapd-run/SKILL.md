---
name: fapd-run
description: Run the FAPD daily pipeline end to end (sync, agencies, email, extract, analyze, render, site). Invoke when the user says /fapd-run or asks to run the pipeline, produce today's digest, "do the daily run", or re-run a failed run.
---

# FAPD — run the daily pipeline

The engine is `scripts/run_pipeline.py` (stage functions + detail
report); this skill drives it. The pipeline digests the newest
**complete** day — a run today renders *yesterday's* digest by design
(dating rule, worklog 2026-07-25).

## Preconditions
- `.env` present with `GOVINFO_API_KEY` (`uv run python scripts/verify_key.py`).
- Package imports: `uv run python -c "import fapd"`.
- No other pipeline/collector run against the live DB (check for
  running `run_pipeline`/`collect` processes).

## What to do when invoked
1. `uv run python scripts/run_pipeline.py` (add `--date YYYY-MM-DD`
   only if the user named a date). Long-running — background it and
   monitor.
2. Watch the stage narration; a mailbox skip or outage is reported and
   non-fatal by contract.
3. **Verify**: detail report ends `Validation: PASSED`; budget lines
   within GUIDE §4 caps; ledger lines show resolved model + backend.
4. Evidence commit (digests/, provenance/, site/) goes **direct to
   main** per the evidence exemption — never mixed with code changes.

## Notes
- **A manual run renders and builds the site; it does NOT finalize or
  push.** `finalized_date` and the evidence push belong to the
  supervisor's EOD path. To recover a `HALTED` day on the box, use
  `scripts/collect.py --finalize D` (VPS-gated) — never a bare
  `run_pipeline.py`, which is how nine days went unpushed in 2026-08.
- `--no-llm` runs the mechanical pipeline: no provider is called, every
  model layer is recorded as skipped, and the digest's Inference row
  carries the neutral no-inference sentence (GUIDE §6 r15). A provider
  outage mid-run does the same for the remaining layers on its own; the
  run no longer exits 1 for it. The narration's `layers:` line is where
  the reason shows — the digest never says.
- `Validation: FAILED` writes nothing, by design — report the gate that
  refused, don't override (there is no override).
- govinfo 503s with Retry-After waits are normal under load; the client
  absorbs them.

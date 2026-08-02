# Full code review — FAPD, 2026-08-02

*A top-to-bottom review of the Free Agentic Publication Digester: 12,136
lines of library code across 23 modules, 1,033 lines of CLI scripts, 9,377
lines of tests, the production Docker stack, and the governing documents.
Read in full; nothing sampled. No code was changed to produce it.*

**Reviewer's stance.** This is a review written for a project that already
holds itself to an unusually explicit standard. I have not padded it with
style notes or restated conventions the codebase already follows well. What
follows is the set of things that would actually change the output, the
cost, or the trustworthiness of the digest — ordered by how much damage each
can do, with file and line references and, where possible, a measurement
rather than an assertion.

---

## 0. Summary

**What is genuinely good, and rare.** The accountability architecture is the
best thing in this codebase and it is better than most production systems I
have read. Every HTTP request is logged before it can be counted, and the
budget is *derived from that log* rather than tracked in memory
(`client.py:196-258`) — which means no code path can spend without being
counted, and the enforcement survives process restarts and works across
processes. The same pattern is repeated for LLM calls (`llm.py`). The
provenance layer records absence as an assertion, not just presence
(`provenance.record_attempt`). Rules are a named, versioned registry so
every published item can answer "why is this here?" Constants that encode
policy carry the measurement that set them, in the file, next to the number.
This is a codebase that can explain itself, and that is the whole product.

**The pattern that keeps producing incidents.** Nearly every serious defect
below is the same shape: *a rule is stated once in the governing document,
implemented correctly in one place, and missed in a second place that was
written earlier or later.* The premature-Aug-1 digest was the Eastern
publication-day rule applied in `sync.publication_date()` and missed in
`digest.default_date()`. Finding **D1** below is the same rule applied in
`agencies._issue_day()` and missed in `report._claimed_day()`. Finding **D4**
is the retry-ceiling rule enforced for the map layer and not for the plain
layer. Finding **D8** is the banned-lexicon list enforced in the validator
and only partly stated to the model that must satisfy it.

This is not carelessness. It is the predictable consequence of encoding
policy as *prose in GUIDE.md plus scattered implementations*, with no
mechanism that makes a rule's call sites enumerable. The single highest-value
structural change this project could make is to give each editorial rule
exactly one function and forbid the second implementation — see §II.1.

**The largest single risk.** There is no ceiling on LLM spend. The HTTP side
has a daily budget, an hourly ceiling, a finalizer reserve, per-class
buckets, and backpressure. The LLM side has a ledger and nothing else
(`llm.py`, and `config.py:150-161` explicitly notes no cap is enforced). Every
expensive incident in this project's history — 17.4M tokens on 2026-07-30,
39.7M on 2026-07-31, 35 duplicate pipeline runs on 2026-08-01 — was stopped
by a human noticing, not by the system refusing. Detail in **D3** and
**R1**.

**Counts by severity.** 4 critical, 7 high, 9 medium, plus a set of smaller
items. Two of the critical findings are *live in production right now*.

---

# Part I — Defects

Severity is by consequence to the published record: **Critical** = the digest
is wrong or the system spends without bound; **High** = a stated guarantee is
not actually enforced; **Medium** = correctness or robustness gap with a
plausible trigger.

---

## D1 — CRITICAL. The agency dating rule compares an Eastern day to a UTC day

**Files:** `src/fapd/report.py:432-450` (`_claimed_day`), `:453-473`
(`_agency_rows`), `:548-572` (`_votes_rows`); `src/fapd/agencies.py:1217-1235`
(`_issue_day`). Also reached by `publish.build_today` via the shared helper.

`_issue_day()` files an agency release under `publication_date()` — the
**Eastern** calendar day, correctly, per GUIDE §3 as amended 2026-07-30. That
value is stored as `packages.date_issued`.

`_claimed_day()` then parses the publisher's own date and converts it to
**UTC**:

```python
if parsed.tzinfo is not None:
    parsed = parsed.astimezone(dt.UTC)      # report.py:446
return parsed.strftime("%Y-%m-%d")
```

`_agency_rows()` compares the two:

```python
(listed if claimed == date or claimed is None else backfill).append(r)
```

Between 20:00 and 23:59 Eastern the two disagree by one day, so a release the
agency itself dates on the digest day is classified as **backfill**, excluded
from section 6 under `AGENCYPR-EX-01`, and never listed as that day's news.
Verified against the running code:

```
feed pubDate            : Sat, 01 Aug 2026 20:30:00 -0400
_claimed_day() [UTC]    : 2026-08-02
publication_date() [ET] : 2026-08-01   <- stored as date_issued
report treats it as     : BACKFILL (excluded, AGENCYPR-EX-01)
```

**Measured exposure.** Over 371 agency and vote items with a parseable
publisher date since 2026-07-20, 4 (1.1%) carry an Eastern hour of 20:00 or
later — so the current loss is small. But the exposure is a pure function of
which sources are active: the corpus is dominated by 07:00–09:00 ET wire-style
releases (199 of 371), and every evening-publishing source added from the
70-entry planned backlog widens it. `_votes_rows()` has the identical
comparison, and chambers routinely vote late.

**Why this one matters more than its current count.** It is the exact defect
class that produced the premature-Aug-1 digest, in the *selection* path
rather than the scheduling path, and it fails silently: the item is ingested,
captured, hashed, counted — and then dropped from the digest with no visible
trace, because of D2.

**Fix:** `_claimed_day` should return the Eastern publication day
(`sync.publication_date(parsed)`), and its ISO-string branch should be
reconciled with `_issue_day`'s. Better, per §II.1: both should call one
shared function.

---

## D2 — CRITICAL. `AGENCYPR-EX-01` is counted but never named, breaking the Coverage Statement's central promise

**File:** `src/fapd/report.py:1252-1268`.

The Coverage Statement asserts, verbatim in the rendered digest:

> *"Excluded" always names the mechanical rule; there are no unexplained
> omissions.*

The fired-rules list is built from a hard-coded tuple:

```python
for rid in ("CREC-EX-01", "CREC-EX-02", "FR-EX-01",
            "USCOURTS-EX-01", "USCOURTS-EX-02", "VOTES-EX-01")
```

`AGENCYPR-EX-01` is absent — even though `_coverage()` computes its count at
`:328` and puts it in the AGENCYPR row's `excluded` column. So agency releases
excluded by the dating rule appear as a bare number in a table and are never
attributed to a named rule anywhere in the document.

Compounded with D1, the failure reads: *an evening agency release is silently
dropped from the digest, and the mechanism that exists to disclose exactly
this produces no disclosure.* That is the project's own stated worst failure
mode.

**Structural note:** this is a hand-maintained list beside a dict that already
has the answer. `rule_counts` (built at `:1252-1254`) contains every fired
rule. The tuple exists only to impose ordering. Iterate `rule_counts` in a
defined order instead, and the class of bug disappears.

---

## D3 — CRITICAL. There is no ceiling on LLM spend, and no size bound on the most expensive call

**Files:** `src/fapd/llm.py` (entire); `src/fapd/compose.py:80-104`;
`src/fapd/config.py:150-161`.

Two separate problems that compound.

**(a) No budget enforcement.** `LLMClient.complete()` records every call and
refuses none. `tokens_today()` exists and is called only to decorate a log
line (`llm.py:177`). Compare the HTTP path, which has `_check_daily_budget`,
`_check_hourly_ceiling`, `_effective_daily_budget` with a finalizer reserve,
per-class buckets, and interval backpressure. The asymmetry is deliberate
("measure first", GUIDE §6 r8) and was correct in June. It is no longer:
three incidents have now been measured (17.4M, 39.7M, and 35 duplicate full
pipeline runs). The measurement phase has produced its answer.

**(b) The compose prompt is unbounded.** `compose_day()` builds one prompt
containing *every* summarized item for the day:

```python
item_lines = [
    f"- [{r['collection']}/{r['doc_type'] or '?'}] "
    f"{(r['title'] or '').strip()[:120]}: {r['summary'][:400]}"
    for r in items
]
```

There is no item cap, no total-size cap, and no truncation guard — and this
is the one call that uses the **opus** tier (`config.COMPOSE_MODEL`). Contrast
`analyze._build_prompt`, which caps at `MAX_BATCH_ITEMS = 6` items of
`ITEM_TEXT_LIMIT = 12000` chars each. At 520 chars per line, a 300-item day
produces ~156 KB ≈ 40K tokens on the most expensive model, and the ceiling is
whatever the day happens to contain. `compose_sections` has the same shape.

**(c) Cost decisions are being made on a metric that is not cost.**
`llm.py:85-90` and `:125-129` sum `input_tokens + cache_read_input_tokens +
cache_creation_input_tokens` into a single `input_tokens` column. Those three
are billed at materially different rates. Every headline figure this project
has reasoned from — "39.7M input tokens, 60% of the day" — conflates them.
The conclusions drawn were still directionally right, but the ledger cannot
answer "what did this cost?" and it should be able to.

---

## D4 — HIGH. The per-item retry ceiling is enforced for the map layer and not for the plain layer

**Files:** `src/fapd/analyze.py:389-390` and `:333-365`;
`src/fapd/collect.py:117-143`.

`run_plain()` faithfully records attempts:

```python
_record_attempts(conn, "plain",
                 [(r["package_id"], r["granule_id"]) for r in retry_queue])
```

Nothing ever reads those rows. The only consumer, `pending_map_items()`,
queries `layer = 'map'` (`collect.py:137`), and `run_plain`'s own pending
query (`analyze.py:346-365`) selects summaries lacking a `plain_summaries` row
with no reference to `summary_attempts` at all.

So the exact failure documented in CLAUDE.md §9 and `config.py:155-161` —
"the per-run ceiling resets every cycle and the collector runs analyze every
15 minutes per pending date, so an unsummarizable item was retried
indefinitely" — is **still live for the plain layer**. An item whose summary
the plain model cannot restate is retried forever at `MAX_PLAIN_BATCH_ITEMS`,
then group retries, then up to `MAX_SINGLE_RETRIES_PER_RUN = 12` single calls
per run, every 15 minutes, indefinitely.

**Related, smaller:** `_record_attempts` is called with the post-group
`retry_queue`, which is not mutated by the single-retry loop
(`analyze.py:448-461`). Items the single retry *successfully* recovered still
get an attempt counted. Harmless today only because `pending_map_items` checks
for an existing summary before it checks attempts.

**Also related:** the ceiling counts one attempt per *run*, not per call. With
`MAX_ITEM_SUMMARY_ATTEMPTS = 3`, an item gets three runs × (batch + group +
single) ≈ 9 calls before disclosure. The constant's docstring reads as
"3 attempts."

---

## D5 — HIGH. The EOD re-fire loop is closed on the success path and still open on the failure path

**Files:** `src/fapd/collect.py:302-326` (`Worker.run_cycle`), `:529-554`
(`EODWorker.cycle`), `:259-277` (`record_state`); `scripts/run_pipeline.py:290`.

The fix now on `bug/eod-timing` carries a `finalized` marker through
`cycle()`'s no-op return, so an idle cycle no longer erases the proof the day
was finalized. But `run_cycle`'s error handler does not go through `cycle()`
at all:

```python
except Exception as exc:
    record_state(conn, self.name, ok=False, error=repr(exc))
```

`record_state` writes `last_result = json.dumps({"error": error})` —
overwriting the row and discarding `finalized` exactly as the no-op return
used to. And `EODWorker.cycle` raises on a non-zero finalizer exit
(`:547-548`), which `run_pipeline.main()` returns whenever validation fails
(`return 0 if out_path else 1`).

**Consequence:** a digest that persistently fails validation causes the EOD
worker to re-run the entire pipeline — sync, analyze, compose on the opus
tier, insight — forever. The loop backoff (`:340-341`) caps the doubling at
2³, so a 10-minute interval becomes 80 minutes; it does not stop. That is
roughly 18 full pipeline runs per day against a day that cannot publish.

This is the same shape as the incident just diagnosed, one branch over. The
marker must be preserved across error returns too — the cleanest form is to
make the finalized date its own column on `collector_state` rather than a key
inside a JSON blob that every writer replaces wholesale.

---

## D6 — HIGH. The Coverage Statement's arithmetic gate cannot fail

**File:** `src/fapd/report.py:1484-1519` (`_validate_coverage`), with
`_coverage` at `:255-374` and `_coverage_lines` at `:1227-1250`.

The module docstring says the digest is validated so that "the Coverage
Statement must reconcile against the database." Both halves of that gate are
self-fulfilling.

**The arithmetic check is an identity.** The gate asserts
`summarized + counted + excluded == total`. But `counted` is computed as the
remainder in every branch of `_coverage()`:

| collection | code | expands to |
|---|---|---|
| CREC | `counted = units - summarized - ex01`, `excluded = ex01` | `= units` |
| FR | `counted = notices`, `excluded = units - summarized - notices` | `= units` |
| USCOURTS | `counted = district + bankruptcy`, `excluded = units - summarized - counted` | `= units` |
| PLAW / VOTES / AGENCYPR / BILLACTIONS | same remainder shape | `= units` |
| BILLS | `counted = packages - summarized`, `excluded = 0`; the renderer prints `units` as `"—"` so `total = packages` | `= packages` |

Every row satisfies the constraint by construction. No database state can
make it fail.

**The database check is a tautology.** The gate calls `_coverage(conn, date)`
— the same function whose output the renderer formatted — and compares. It can
detect a bug *between* `_coverage()` and the markdown table, and nothing else.
An error inside `_coverage()` is reproduced identically on both sides.

This is worth stating plainly because the gate is load-bearing in the
project's public claims. It is a real *rendering* check and a useful one. It
is not the accounting check the docstring describes. A gate that could
actually fail would compute the totals a second way — e.g. assert that every
`extracted_texts` row for the date is attributable to exactly one selection or
exclusion rule, counted independently of `_coverage`. Which leads to:

---

## D7 — HIGH. Whole document classes fall through the rule registry uncounted

**File:** `src/fapd/rules.py:209-227` (`exclusion_counts`), `:157-167`
(`_MATCHERS`).

`exclusion_counts` claims "every unselected document of a covered class is
attributed to exactly one exclusion rule." The dispatch chain handles FR
NOTICE, CREC floor, CREC extensions/digest, USCOURTS district and bankruptcy —
and silently drops everything else:

- **BILLS at an unreached stage** (`ih`, `is`, `eh`, `es` — introduced,
  engrossed) match no `_MATCHERS` entry and no `elif` branch. There is no
  `BILLS-EX-*` rule at all. Introduced bills are the single highest-volume
  BILLS class and they are accounted for nowhere.
- **FR doc types outside RULE/PRORULE/PRESDOCU/NOTICE** — same.
- **AGENCYPR, VOTES, BILLACTIONS** have no `_MATCHERS` entries whatsoever, so
  `rules.select_items()` never returns them and `analyze.run()` never
  summarizes them. They are handled entirely by bespoke code in `report.py`
  (`_agency_rows`, `_votes_rows`, `_billactions_lines`), parallel to the rule
  registry rather than inside it.

The escape hatch is the phrase "of a covered class," but a reader of the
digest has no way to know which classes are covered by that sentence. The
practical result is that the digest's central integrity claim is narrower
than it reads, and — because of D6 — nothing detects the difference.

---

## D8 — HIGH. The compose model is never told half the words its output will be rejected for

**Files:** `src/fapd/compose.py:22-27` (`_PROMPT`);
`src/fapd/report.py:84-107` (`_BANNED_TERMS`).

The validator bans 16 terms. The compose prompt names 9 of them plus one
phrase. The compose model is never told about:

```
"aims to appease", "red tape", "crackdown", "cracks down", "slams", "loophole"
```

(The *plain* prompt, `analyze.py:196-198`, does mention "cuts red tape" and
"crackdown" — so the drift is specifically in the compose layer.)

Consequence: the strongest, most expensive model in the pipeline can produce
prose that the gate then rejects, failing the entire digest for a constraint
it was never given. Per D5, that failure now re-runs the pipeline
indefinitely. Two lists in two modules with no test pinning them equal is the
root cause; the prompt should be generated from `_BANNED_TERMS`.

**Related over-masking in the same gate** (`report.py:1562-1567`):

```python
for text in officials:
    scan = scan.replace(text, " ").replace(_one_line(text), " ")
```

`str.replace` is global and unanchored. A short agency title — the code pulls
*every* `AGENCYPR`/`VOTES`/`BILLACTIONS` title for the date — is deleted from
everywhere in the document including LLM prose, blinding the gate to a real
violation. And the inverse: `_truncate()` renders long titles with an ellipsis
(`report.py:148-149`), and the truncated form is not in `officials`, so a
banned word surviving inside a truncated title trips the gate and blocks
publication. Masking should be positional, not textual.

---

## D9 — HIGH. Package IDs are 32-bit truncated hashes; a collision silently drops a release

**Files:** `src/fapd/agencies.py:1206-1214`; the same construction in
`src/fapd/email_sources.py`.

```python
def _package_id(source_id, stable_id):
    digest = hashlib.sha256(stable_id.encode()).hexdigest()[:8]
    return f"PR-{source_id}-{digest}"
```

Eight hex characters is 32 bits. `_already_ingested()` treats a matching
`package_id` as "seen before" and `continue`s — so a collision means a genuine
new release is **discarded with no log line, no capture, and no counter**.
Collisions are per-source (the id is in the prefix), so the relevant
population is one source's lifetime item count. By the birthday bound, a
source that accumulates 10,000 items has ≈1.2% probability of at least one
collision; 30,000 items ≈10%. `usps-newsroom` alone presented 669 items on
activation, and the project is designed to run for years.

For a system whose stated worst failure mode is silent omission, this is the
one place where a silent omission is *built in*. The fix is one character:
`[:16]`. Existing rows are unaffected because the id is only ever compared to
itself.

---

## D10 — HIGH. A parse failure permanently silences a source, because the ETag is stored first

**File:** `src/fapd/agencies.py:1309-1328`.

`poll_source` writes `feed_state.etag` / `last_modified` **before** parsing:

```python
conn.execute("INSERT INTO feed_state ... ON CONFLICT ... ")
conn.commit()

if resp.status_code == 304: ...
fmt, items = adapter.items(...)
if fmt is None:
    stats["feed_status"] = "unparsable"
```

The next poll sends `If-None-Match` with that ETag, receives 304, and returns
`"not-modified"` — a *healthy-looking* status. The source is now permanently
stuck: it will never re-parse until the publisher happens to change the ETag,
which for a stable archive page may be never.

Worse, `health.py` classifies on delivery recency and request success. A
source in this state answers 304 promptly and delivers nothing, so it drifts
to `quiet` — "the source may simply not have published" — attributing our
parse regression to the publisher. That inverts the module's own stated
principle (`health.py:4-14`: "It reports nothing about the publisher").

**Fix:** advance the conditional-GET state only after a successful parse, or
store `last_parse_ok` and force an unconditional refetch when the previous
parse failed.

---

## D11 — MEDIUM. Two agency worker threads can write the same manifest concurrently

**Files:** `src/fapd/collect.py:384-394` (`AgencyHostWorker.cycle`);
`src/fapd/provenance.py:199-229` (`export_manifest`).

Each host worker runs in its own thread (`Supervisor.run_forever`) and calls:

```python
if stats["new_items"]:
    provenance.export_manifest(conn)
```

`export_manifest` ends with `path.write_text(...)` — truncate-then-write, not
atomic. Two hosts finishing a cycle at the same moment can interleave and
leave a truncated or interleaved manifest.

The project already knows the right answer: `agencies.run_concurrent`
(`:1479-1486`) deliberately exports **once, after all workers join**, with the
reasoning in its docstring ("so one day's attempts land in one manifest
regardless of worker count"). The supervisor path did not inherit it. Fix:
write to a temp file and `os.replace`, and/or move the export to a single
owner.

**Related, in the same module:** `_prev_manifest_sha()` (`:189-196`) picks
`sorted(...)[-1]` of whatever manifests exist and records only its hash — not
which date it hashed. A missing day therefore produces a chain that verifies
perfectly with a day silently absent. For an artifact whose stated purpose is
that "days can't be silently dropped or reordered without the files
themselves showing it," the header should carry `prev_manifest_date` beside
the hash.

---

## D12 — MEDIUM. A govinfo budget exception aborts free work, and always starves the same collection

**File:** `src/fapd/collect.py:348-362` (`GovinfoWorker.cycle`).

```python
with self.sup.govinfo_factory() as client:
    for collection in config.COLLECTIONS:
        s = sync.sync_collection(client, conn, collection, max_downloads=50)
ex = extract.run(conn)
stats["journaled"] = journal_new(conn, "govinfo", cycle_id)
```

Two problems.

**(a) Budget exhaustion kills the free stages.** `BudgetExceededError` from
any collection propagates out of the `with`, so `extract.run()` and
`journal_new()` never execute — despite costing zero requests and zero
tokens. Packages downloaded earlier in that cycle stay unextracted and
unjournaled, and therefore invisible to `/today` and to analyze, until a later
cycle. `run_cycle` then records `{"paused": "budget"}` with `ok=True`, so
nothing surfaces the gap.

The finalizer already does this correctly —
`run_pipeline.stage_sync:66-76` wraps each collection in its own
`try/except BudgetExceededError: continue`. The collector should adopt the
same shape, and `extract`/`journal` should sit outside the client context
entirely.

**(b) Collection order is fixed, so starvation is systematic.**
`config.COLLECTIONS = ("CREC", "BILLS", "FR", "USCOURTS", "PLAW")` is iterated
in the same order every cycle. When the budget binds, it always binds on the
tail. PLAW is last on every one of the ~48 daily cycles, and BILLS — the
largest collection by far — sits second, ahead of FR. A rotating start offset
(cycle number modulo length) makes the shortfall fall evenly and is three
lines.

---

## D13 — MEDIUM. DKIM failures are logged but never gate ingestion

**File:** `src/fapd/email_sources.py:517-543`.

```python
dkim = dkim_verifier(raw)
...
if dkim.get("result") != "pass":
    logger.info("%s: dkim %s for %s", ...)

for item in parse_bulletin(msg):
    ...
    _store_item(conn, entry, item, package_id, text, mode, capture_id, dkim)
```

The sender allowlist (`_sender_map`) is applied to headers, which are
forgeable. DKIM is the only real authentication in this channel and it is
advisory: a failed or absent signature produces one INFO line and the item is
ingested and published in section 6 under `AGENCYPR-SEL-01` — "official
agency release" — alongside verified ones.

To the project's credit this *is* disclosed: `report.py:521-529` renders
"DKIM fail" or "unsigned" on the item. So this is not a hidden defect; it is a
policy choice, and the choice is "record and disclose" where the rest of the
system would say "do not publish." For the one channel where content
authenticity cannot be re-verified against a public URL — an email bulletin
that names no canonical page is, by the code's own comment at `:509-511`, its
own source of record — I think that choice is worth revisiting with the
operator. Quarantining rather than dropping would preserve the accountability
record while keeping unauthenticated text out of the digest.

Any change here is a GUIDE amendment, not a code fix.

---

## D14 — MEDIUM. `dates_with_pending` looks back three publication days, not the two it documents

**File:** `src/fapd/collect.py:177-194`.

```python
floor = (dt.datetime.now(dt.UTC)
         - dt.timedelta(days=max_age_days + 1)).astimezone(
             config.PUBLICATION_TZ).strftime("%Y-%m-%d")
return [d for d in _all_dates_with_pending(conn) if d >= floor]
```

The docstring says "1 = the current publication day and the one before it."
With `max_age_days = 1` the floor lands two days back and the `>=` comparison
admits three publication days (today, yesterday, the day before). At 2026-08-02
14:47 UTC the floor is `2026-07-31`.

This is spending real tokens on a third day that will never be published —
the precise waste `ANALYZE_MAX_AGE_DAYS` was introduced on 2026-07-31 to stop.
The subtraction should be `max_age_days`, or the docstring should be corrected
to match, but they must agree.

---

## D15 — MEDIUM. The analyze stage is unprotected, and its failure destroys the day

**File:** `scripts/run_pipeline.py:140-162`, `:265-273`.

`stage_analyze` runs five model calls — `analyze.run`, `run_plain`,
`compose_day`, `compose_sections`, `tags.run` — with no exception handling.
Any `LLMError` propagates out of `main()`, the process dies with a traceback,
and `stage_render` never runs.

This is exactly backwards relative to the pipeline's own design. `stage_email`
is wrapped with a comment explaining that "a mailbox outage must not cost the
rest of the run" (`:125-128`). `stage_insight` is wrapped, "an insight failure
never fails the run" (`:183-195`). The stage that is *most* likely to fail —
subprocess spawn, model timeout, network — and whose partial results are
already durably committed per item is the one with no guard.

A single flaky `claude` invocation therefore discards a day that could have
been rendered from the summaries already in the database. Wrap it, record
what was skipped, and let the Coverage Statement disclose the shortfall —
which is what that machinery is for.

---

## D16 — MEDIUM. Long crawl-delays block every host on the same client

**File:** `src/fapd/client.py:260-272` (`_pace`), `:394-407` (`AgencyClient.get`).

`_pace` keeps one `self._last_request_at` per client instance and computes
`interval = max(min_interval or 0.0, 1.0 / MAX_REQUESTS_PER_SECOND)`. The
`min_interval` is the *current* URL's host crawl-delay, but the elapsed time is
measured since the last request to *any* host.

Within one `AgencyHostWorker` this is safe by construction — `host_groups()`
guarantees one host per worker, and the docstring at `agencies.py:1423-1426`
states the invariant clearly. But the invariant lives in the grouping function
rather than in the client, and the client is constructed freely elsewhere
(`probe.py`, `check_sources.py`, ad-hoc scripts). Any caller that polls two
hosts through one `AgencyClient` will have gao.gov's 420-second delay applied
to the next request to *every other* host — a 7-minute stall per request,
which reads as a hang.

The pacing clock should be keyed by host: `self._last_request_at[host]`. That
makes the promise a property of the client, which is what `config.py`'s own
header says access policy is meant to be ("respectful access is a property of
the client, not operator discipline").

---

## D17 — MEDIUM. The server-remaining halt does not survive a cycle

**File:** `src/fapd/client.py:342-350`, `:91`, `:136-137`.

`_post_response` sets `self._halt_reason` when the server reports fewer than
`MIN_SERVER_REMAINING` requests left, and `get()` refuses thereafter. But
`_halt_reason` is instance state, and the collector constructs a fresh
`GovinfoClient` every cycle (`GovinfoWorker.cycle:355`). A halt therefore lasts
until the end of the current cycle and is forgotten 30 minutes later.

Every other budget signal in this module is deliberately persisted to
`fetch_log.db` precisely so it cannot be reset by a restart. This one — the
most serious signal, meaning "we are approaching the publisher's own limit" —
is the exception. It should be persisted with a timestamp and an expiry.

---

## D18 — MEDIUM. XML from the network is parsed with the stdlib parser, in a container with no memory limit

**Files:** eight sites — `agencies.py:304,383`, `graphics.py:77`,
`parsers/bills.py:87`, `parsers/fr.py:187`, `parsers/plaw.py:20`,
`parsers/uscourts.py:189`, `probe.py:56`. Container config:
`deploy/vps/docker-compose.yml`.

`xml.etree.ElementTree` does not resolve external entities, so this is not an
XXE issue. It *does* expand internal entities, so a malformed or hostile
document can drive quadratic blowup or "billion laughs" memory exhaustion.
The inputs are `.gov` bytes, which makes deliberate attack unlikely — but a
merely *corrupt* payload has the same effect.

What turns this from theoretical into operational is the container:
`docker-compose.yml` sets no `mem_limit` and no `cpus` on the backend service,
and the box is explicitly a **shared** VPS. A memory-exhausting parse takes the
neighbours with it. Either bound the container or use `defusedxml`; bounding
the container is worth doing regardless.

---

## D19 — MEDIUM. No log rotation on a long-running, verbose container

**File:** `deploy/vps/docker-compose.yml`.

Neither service sets a `logging:` block, so both use Docker's default
`json-file` driver with **no** `max-size` or `max-file`. The supervisor logs
every HTTP request at INFO (`client.py:168-172`), plus per-item ingest lines,
plus full pipeline output at EOD. At ~1,500 agency + up to 6,000 govinfo
requests a day, running continuously, this grows without bound until the
shared host's disk fills.

The Aug 1 incident — 35 full pipeline runs in one day, each printing a
complete staged transcript — is exactly the shape of event that turns "grows
slowly" into "fills the disk this week."

Also missing: a `healthcheck` on the backend service. `web` has one; the
backend, which is the component that can wedge, has none. `restart:
unless-stopped` only fires when the process exits, and the supervisor's main
thread never does — so a deadlocked or silently-stalled worker is invisible to
Docker and to `docker ps`.

---

## D20 — LOW/MEDIUM. Assorted, with file references

**a. The evidence commit message always names the wrong day.**
`deploy/vps/scripts/evidence-commit.sh` uses `DATE_TAG="$(date -u +%F)"`. The
EOD finalizer runs just after midnight Eastern, which is 04:05 UTC the
*following* date — so the commit for the 2026-08-01 digest is titled "Daily
pipeline evidence 2026-08-02." Every automated evidence commit in the history
is misdated by one day. It should name the finalized publication date, which
`EODWorker` already knows and could pass as an argument.

**b. `git push` has no divergence recovery.** The same script ends with a bare
`git push origin main` under `set -e`. If the remote has moved, the push fails,
`pushed` is recorded as `False`, and evidence publication stops silently until
someone looks. A `git pull --rebase` guarded by the same path allowlist, or an
explicit alert, would close it.

**c. A test writes into the real repository.**
`tests/test_collect.py:409-410`:

```python
(config.SITE_DIR).mkdir(parents=True, exist_ok=True)
(config.SITE_DIR / "today.html").write_text("stub")
```

`config.SITE_DIR` is not monkeypatched here, so running the suite overwrites
the live `site/today.html` with the literal string `stub`. It is gitignored, so
it cannot reach a commit — but it is not hermetic, it clobbers local state, and
if the suite were ever run on the VPS it would replace the live `/today` page.

**d. `_load_items` and `rules.select_items` re-read full document text
repeatedly.** `rules._ROWS_SQL` selects `et.text` for every row on the date, and
`select_items` is called by `pending_map_items`, which `trigger_fires` calls on
*every* analyze poll, for *every* pending date — every 15 minutes. Only one
matcher (`CREC-SEL-02`'s regex) needs the text. `exclusion_counts` runs the same
query again. On a 700-item day this is tens of megabytes read from SQLite per
poll for a boolean answer. Select `text` only for CREC rows, or push the
selection predicate into SQL.

**e. `extract.pending_packages` filters in Python after fetching everything**
(`extract.py:52-53`): `rows = [r for r in rows if r["collection"] in
collections]` — after a query that aggregates all of `extracted_texts`. Move the
filter into the SQL.

**f. No URL scheme allowlist at the render seam.** `publish.py:1917` emits
`href="{html.escape(url)}"` from feed-supplied values. Escaping prevents
attribute breakout but not a `javascript:` scheme. `HtmlIndexAdapter` checks
schemes at `agencies.py:1017`; nothing else does, and RSS `<link>`, USPS,
Congress.gov, and email-derived URLs bypass it. Low likelihood with `.gov`
sources; cheap defence-in-depth for a public site whose own threat model
includes "agency web content can be edited without notice."

**g. `assert list(_MATCHERS) == list(RULES)`** (`rules.py:169`) is a
module-level `assert`, stripped under `python -O`. It encodes a real invariant;
it should raise explicitly.

**h. `render()` writes graphic assets before validating.** `_fr_lines(...,
out_dir)` writes PNGs into `digests/assets/<date>/` at `report.py:1712`, before
`validate()` at `:1731`. The docstring's "leaves no `.md` behind" is true; it
leaves orphaned assets.

**i. No schema version marker.** `db.connect()` re-runs the full DDL on every
connect, and additive migrations are hand-rolled `PRAGMA table_info` checks in
two separate modules (`client._migrate`, `llm._ensure_backend_column`). A
`PRAGMA user_version` would cost nothing and give every future migration a
place to check.

**j. Unbounded local storage.** `data/raw/` (`sync.py:250-253`) and
`data/captures/` (`provenance.store_bytes`) grow monotonically with no
retention policy, on a shared VPS, alongside `extracted_texts.text` held in
SQLite. Nothing calls `provenance.verify_stored()` on a schedule, so silent
corruption in the capture store would be discovered only when someone
manually checks a hash.

**k. Ruff is running near-defaults.** `pyproject.toml:41-42` sets only
`line-length`. The source carries `# noqa: BLE001`, `RUF012`, `ISC004`,
`FURB162` suppressions that are currently inert, implying a broader rule set
was once assumed. `--select ALL` surfaces, among the noise, seven functions
over the complexity threshold — `sources._validate` at 27, `agencies.poll_source`
at 18, `graphics.extract_assets` at 17 — and the eight `S314` sites from D18. A
deliberate, curated `select` list would let the linter carry rules the
maintainers currently carry by memory.

---

# Part II — Architecture and philosophy

## II.1 The core structural weakness: policy is prose, not a call site

The project's governing idea is that editorial rules are explicit, versioned,
and auditable. GUIDE.md is treated as a constitution, amendments precede
implementation, and CLAUDE.md §9 keeps a list of things that look like bugs
but are decisions. That discipline is real and it works — the §9 list is the
best artifact in the repository for onboarding an agent or a person.

But the rules themselves live in prose, and their implementations are
scattered. Consider the Eastern publication-day rule, amended 2026-07-30. Its
call sites today:

| Site | Correct? |
|---|---|
| `sync.publication_date()` | canonical |
| `agencies._issue_day()` | correct — calls it |
| `collect.RenderWorker.cycle` | correct |
| `collect.EODWorker.eod_due` | correct |
| `digest.default_date()` | **was wrong until 2026-08-02** |
| `report._claimed_day()` | **wrong now** (D1) |
| `collect.dates_with_pending` floor | off by one (D14) |
| `provenance.export_manifest` day key | UTC — arguably correct, undocumented |
| `evidence-commit.sh` `DATE_TAG` | UTC — wrong (D20a) |
| `run_pipeline.detail_report` day | UTC — correct for budgets |

Nine call sites, three wrong, two ambiguous, and no way to enumerate them
except by reading everything. The same story holds for the banned lexicon (two
lists, D8), the exclusion-rule registry (a dict plus a hand-maintained tuple,
D2), and the retry ceiling (enforced in one layer, recorded in two, D4).

**The recommendation is not "be more careful."** It is to make each rule a
single named function that *everything* calls, and to add a test that fails
when a second implementation appears. Concretely:

- One `publication_day(when_or_stamp)` used by every dating decision, with the
  UTC-vs-Eastern distinction expressed as two differently-named functions so a
  call site cannot be ambiguous by accident.
- `_BANNED_TERMS` as the single source; the compose and plain prompts
  *generated* from it.
- The fired-rules list derived from `rule_counts`, never hand-listed.
- A test that asserts every rule id in `RULE_DESCRIPTIONS` is either in
  `rules.RULES`/`rules.EXCLUSIONS` or explicitly registered as
  report-layer-only — which would have caught D2 and D7 on the day they were
  introduced.

The existing `test_web_adapters_match_agencies_registry`
(`tests/test_sources.py:272-277`) is exactly this pattern, and its comment
explains the reasoning perfectly. The project already knows how to do this. It
has done it once.

## II.2 The two budget systems are not the same system, and should be

The HTTP path has: a persistent daily budget derived from the log, an hourly
ceiling, per-class buckets, a finalizer reserve, interval backpressure, a
server-signal halt, and a documented policy for each. The LLM path has a
ledger.

This is the clearest architectural asymmetry in the codebase, and it maps
exactly onto where the incidents have happened. Every HTTP incident has been
mild (a source over-polled, a robots file re-fetched). Every LLM incident has
been severe (17.4M tokens, 39.7M tokens, 35 duplicate runs). The mechanisms
that made the HTTP side safe are all portable: the ledger already records
everything needed to count, so `LLMClient.complete` could enforce a daily
token ceiling, a per-purpose ceiling, and an EOD reserve using the same
"derive the budget from the log" pattern, in roughly the same amount of code.

I want to be precise about what "measure first" earned. It earned four
excellent constants (`MAX_RETRY_BATCH_ITEMS`, `MAX_SINGLE_RETRIES_PER_RUN`,
`MAX_ITEM_SUMMARY_ATTEMPTS`, `ANALYZE_MAX_AGE_DAYS`), each with its
measurement in the file. That was the right process and it produced the right
answers. But each of those constants throttles a *specific known* failure
mode discovered after it happened. None of them is a backstop against the
next one. A hard daily ceiling is the backstop, and there is now more than
enough measurement to set it.

## II.3 The validation gates guard the wrong surface

Four gates run before a digest is written. Ranked by how much they can
actually catch:

1. **`_validate_inclusion_lines`** — genuinely strong. Structural, cheap,
   cannot be satisfied accidentally.
2. **`_validate_citations`** — real, but narrow: only `govinfo.gov/app/details`
   URLs. Agency, Congress.gov, and Wayback URLs — the majority of citations in
   sections 6, 7, and 8 — are unchecked. The docstring says "every govinfo
   citation," which is accurate; the module header says "every citation," which
   is not.
3. **`_validate_lexicon`** — real, but with the masking problems in D8 pulling
   in both directions (blind spots from over-masking, false failures from
   truncation).
4. **`_validate_coverage`** — cannot fail for the reason it exists (D6).

Meanwhile the highest-risk content in the document — the Day in Review and the
section synopses, which are unconstrained LLM prose about government activity —
is checked *only* by the lexicon scan. Nothing verifies that a number in the
prose matches a number in the tables, that a named agency appears in the day's
items, or that the prose mentions only branches that have items.

The prompt asks for exactly those properties ("Weave in the counts naturally",
"ONLY when judicial items appear below"). They are checkable mechanically, in
SQL, at zero token cost, which is precisely the project's own §6 rule 2. A
gate that extracts integers from the Day in Review and asserts each appears in
`_mechanical_counts` would be perhaps 30 lines and would be the most valuable
validation in the system.

There is also no gate for *substantive emptiness*. A day where sync failed,
analyze crashed, and nothing was summarized renders a digest of empty sections
and passes all four gates. The 2026-07-30 "thin day" was that. GUIDE says a
digest that fails validation is not published; it does not yet say that a
digest with no content is a failure.

## II.4 The disclosure philosophy is right, and needs one more tier

"Reported, not hidden" is the correct instinct and it is applied consistently:
`stage_email` swallows outages and reports them, `HtmlIndexAdapter` logs drop
counts, health labels are defined in terms of our own observation and never
the publisher's behaviour, `unavailable` registry entries are kept forever.
The `health.py` module header is, frankly, a piece of writing most projects
never manage — it draws the line between "what we recorded" and "what we
think" and then holds it in every label.

The gap is that disclosure currently has one tier: *it happened, and we said
so.* Some events warrant a second tier: *it happened, we said so, and we
stopped.* D9 (a hash collision drops a release) and D10 (a parse failure
silences a source) both produce states the system reports as healthy. D13
(unverified email) produces a state that is disclosed on the page but not
distinguished from verified content in the selection rule that admits it.

Concretely, the missing concept is a **quarantine**: a place where an item is
recorded, counted, hashed, and visible in the accounting, but not listed as
part of the day's official record. The database already has room for it
(`documents.state` has `present/missing/removed/restored`), and the Coverage
Statement is already the right surface to report it.

## II.5 Concurrency is the least-designed layer

The rest of the system is designed by explicit contract. The threading is not.
Evidence:

- `pause_event` is checked at the top of `Worker.loop` only, so the EOD
  "serialization" does not wait for in-flight cycles to drain. A govinfo cycle
  that has just started (up to 250 downloads) runs concurrently with the
  finalizer, against the same database and the same budget the reserve was
  meant to protect.
- `export_manifest` races (D11) because the correct single-owner discipline
  lives in `run_concurrent` and not in the supervisor.
- `run_forever` returns daemon threads and a stop event; there is no shutdown
  path that waits for a cycle to finish or terminates the finalizer subprocess
  on SIGTERM.
- `Supervisor._build_workers` reads the registry once at construction, so a
  registry edit requires a restart — reasonable, but undocumented, and a
  restart mid-cycle has no clean point.

None of this is presently causing visible damage, and WAL plus 30s
`busy_timeout` absorbs most of it. But the EOD incident was fundamentally a
*state-machine* bug in the concurrency layer, and it is the layer with the
least written down. Before the local dev stack lands, the supervisor deserves
the same treatment `docs/continuous-ingestion.md` gave the collection design:
a written contract for pause, drain, shutdown, and single-owner writes.

## II.6 Things I looked hard at and found sound

Worth saying explicitly, because a review that lists only problems misleads.

- **The seam pattern.** Dependency injection by optional constructor parameter
  (`Supervisor.__init__`) is used consistently and makes the system genuinely
  testable without mocking frameworks. `finalizer_runner`, `today_builder`,
  `wayback_factory` are real seams, not ceremony.
- **Idempotence.** Summaries keyed by `(package, granule, prompt_version)`,
  per-item commits, replace-on-refetch for granules, `INSERT OR IGNORE` in the
  journal, content-addressed capture storage. A rerun genuinely costs nothing,
  and a crash genuinely resumes.
- **The watermark protocol.** Advancing only after a completed listing, with
  downloads as a separate pending queue, is exactly right and correctly
  commented (`sync.py:96-121`).
- **robots.txt handling.** RFC 9309 semantics implemented properly: 4xx as
  allow, 5xx as *temporary* disallow, and the deliberate decision not to
  persist a temporary disallow (`client.py:427-431`) — with the reasoning
  written down. That is a subtle call made correctly.
- **The accessibility and health work.** Visually-hidden context on time
  elements, the new-tab announcement, thresholds published beside the labels
  they produce. This is care that most projects skip.
- **Test-to-source ratio** (9,377 : 12,136) with parser fixtures per
  collection and boundary cases at the exact threshold values
  (`conftest.seed_corpus` seeds 15000 and 14999). The suite is real.
- **The commit and documentation discipline.** Narrative commit bodies, an
  append-only worklog, and dev notes written as publishable prose. This is what
  made this review possible in a single pass.

---

# Part III — Recommendations, in priority order

## Now (this week)

**R1. Put a ceiling on LLM spend.** A daily input-token cap enforced in
`LLMClient.complete`, derived from `llm_calls` the way HTTP budgets are
derived from `fetch_log`, raising a `TokenBudgetExceededError` that
`AnalyzeWorker` treats the way it already treats `BudgetExceededError` —
paused, not failed. Add a per-call size guard so `compose_day` cannot build an
unbounded prompt. Split the ledger's `input_tokens` into its three billed
components so the cap can be set in dollars. *(D3)*

**R2. Fix the two live dating and disclosure defects.** `_claimed_day` →
Eastern; `AGENCYPR-EX-01` into the fired-rules list, derived from
`rule_counts` rather than hand-listed. These are small and they are wrong in
production today. *(D1, D2)*

**R3. Close the EOD failure path.** Move the finalized date out of the
JSON blob into its own `collector_state` column so no writer can erase it,
and give a repeatedly-failing finalizer a hard stop with a loud disclosure
rather than an indefinite retry. *(D5)*

**R4. Bound the container.** `mem_limit`, `cpus`, `logging.max-size` /
`max-file`, and a backend `healthcheck` in `docker-compose.yml`. This is a
shared VPS and none of these exist. *(D18, D19)*

## Next (this month)

**R5. Enforce the plain-layer retry ceiling** and change the attempt counter
to count calls rather than runs. *(D4)*

**R6. Widen `_package_id` to 16 hex characters.** One character; removes a
built-in silent-omission path. *(D9)*

**R7. Advance conditional-GET state only after a successful parse**, and add a
distinct health signal for "answering 304 but never parsing." *(D10)*

**R8. Make the coverage gate able to fail.** Compute the accounting a second,
independent way — every `extracted_texts` row for the date attributable to
exactly one selection or exclusion rule — and assert the two agree. This
subsumes D7: the classes that currently fall through would fail the new gate
immediately, which is the point. *(D6, D7)*

**R9. Add a mechanical-consistency gate on LLM prose.** Extract integers from
the Day in Review and section synopses; assert each appears in
`_mechanical_counts`. Zero tokens, high value, directly serves §6 rule 2. Add
an emptiness gate while you are there. *(§II.3)*

**R10. Generate the prompts' banned-term lists from `_BANNED_TERMS`**, and
make the lexicon masking positional rather than textual. *(D8)*

**R11. Wrap `stage_analyze`**, per-layer, so a model failure costs the layer
and not the day. *(D15)*

**R12. Per-collection budget isolation in `GovinfoWorker`**, extract and
journal outside the client context, and a rotating collection start offset.
*(D12)*

## Structural (next quarter)

**R13. One function per editorial rule, with a drift test.** The single change
with the largest effect on defect rate. Start with the publication-day rule
(nine call sites, three wrong) and the rule registry, following the pattern
`test_web_adapters_match_agencies_registry` already establishes. *(§II.1)*

**R14. Write the supervisor's concurrency contract down** — pause/drain
semantics, single-owner writes, shutdown, SIGTERM handling — and make
`export_manifest` atomic and single-owner. Do this *before* the local dev
stack, so the stack has a specification to verify against. *(D11, §II.5)*

**R15. Introduce a quarantine tier** for items that are recorded and counted
but not listed: hash collisions, DKIM failures, parse-failed sources. The
schema and the Coverage Statement can both already carry it. *(§II.4, D13)*

**R16. Add retention and integrity operations.** A size budget and pruning
policy for `data/raw/` and `data/captures/`, and a scheduled
`provenance.verify_stored()` sweep whose result is published. An
accountability store nobody verifies is a claim, not evidence. *(D20j)*

**R17. Curate the lint configuration.** A deliberate `select` list, including
the rules the existing inert `# noqa` comments already assume, plus the
complexity ceiling. Let the linter carry what maintainers currently carry by
memory. *(D20k)*

---

## Appendix — method and limits

**Read in full:** `config.py`, `db.py`, `client.py`, `sync.py`, `collect.py`,
`analyze.py`, `rules.py`, `llm.py`, `provenance.py`, `compose.py` (composition
path), `report.py` (loading, coverage, sections, validation, render),
`agencies.py` (storage and poll loop), `email_sources.py` (message processing),
`health.py` (contract and thresholds), `extract.py` (staleness), the
production `docker-compose.yml`, `evidence-commit.sh`, `run_pipeline.py`,
`.gitignore`, CI, and `pyproject.toml`.

**Read selectively:** `publish.py` (2,641 lines — escaping, `/today`
rendering, link externalization, feed and sitemap emission; the blog and
sources-page renderers were skimmed), `agencies.py` adapter internals
(`SenateVotesAdapter`, `HtmlIndexAdapter` parsing were read for contract, not
line-by-line), `graphics.py`, `tags.py`, `insight.py`, `probe.py`,
`sources.py` validation, and the per-collection parsers.

**Verified by execution, not inference:** the `_claimed_day` timezone
mismatch (reproduced against the running code, plus a 371-item histogram of
publisher hours from the local database); the ruff rule set and the `S314` /
`C901` inventories; the registry composition (127 entries: 42 active, 63
planned, 20 unavailable, 2 evaluated-excluded); the 35 evidence commits and
their ~20-minute cadence.

**Not verified:** VPS runtime state beyond the git history (no VPS access was
used for this review); the accuracy of any digest's editorial content; whether
the local database's staleness relative to production hides additional
data-shape problems — the local corpus holds roughly half the extracted rows
the VPS does, so the D1 exposure measurement is a lower bound on a partial
sample, not a production figure.

**Deliberately not reported:** style preferences, naming, docstring formatting,
and anything already recorded in CLAUDE.md §9 as an intentional decision.
Where a finding touches a §9 entry, it is because the *implementation* diverges
from the decision, not because the decision is questioned.

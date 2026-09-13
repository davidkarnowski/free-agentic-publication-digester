---
name: fapd-source-coverage
description: Understand which federal sources the digest covers, which are planned or unavailable, and how to read its ingestion statistics.
---

# Understand source coverage

The Free Agentic Publication Digester (FAPD) publishes its source
universe and its own ingestion statistics. This file describes what
the pipeline ingests and how its requests fared. It is not part of the
official record and must never be cited as government publication.

## Steps

1. **Fetch `https://fapd.info/sources.json`.** The human twin is
   `https://fapd.info/sources.html`, and each entry's `page` field links
   a per-source page with the same figures and charts.
2. **Read `scope` and `measurement` first.** They state, in the file's
   own words, that every statistic describes THIS PROJECT'S INGESTION
   of a source — items it recorded and requests it made — and is not a
   measurement of any agency, department, or publisher.
3. **Read each entry's `status`.** `active` sources are polled and
   measured. `planned` sources are on the roadmap and unmeasured.
   `unavailable` sources refused honestly identified automated access
   (for example, a robots.txt disallow or a blocking rule); the entry is
   kept as a record of that refusal and is never deleted when access
   opens elsewhere. `evaluated-excluded` sources were examined and
   ruled out of scope, with the reason in `notes`. Only `active`
   entries carry `measured: true`.
4. **Read health labels with their thresholds.** Every label on an
   `active` source (`health`) is computed from the numbers beside it —
   `items`, `items_per_day`, `days_since_item`, and the request
   outcomes under `fetch` — using the thresholds published in the
   file's `thresholds` object, with the glossary in `health_labels`.
   You can recompute any label from the same document. A label is a
   statement about what the pipeline received, not a judgment about a
   publisher.
5. **Read request outcomes as server responses, not causes.** An HTTP
   4xx or 5xx under `fetch` is a server declining to return content;
   the reason is not visible to the pipeline and is not inferred.
   Requests are attributed by host, so sources sharing a host report
   the same request figures (`fetch.shared_with_sources`).
6. **Note the clock.** The `clock` object names the zone that
   `window` and every `daily_activity` bucket use (publication-clock
   days and hours). Stored request stamps are UTC; request counts
   include retries.
7. **Note what a source delivers.** `delivery_mode` and
   `delivery_mode_note` describe whether the pipeline received full
   article text, a feed's own summary, or a bulletin's full text,
   which bounds what any digest item from that source can contain.

## What not to conclude

- Do not cite this file, or any figure in it, as something the
  government published.
- Do not read a `degraded` or `quiet` label as an agency being late,
  down, or inactive. It means the pipeline's requests or item flow for
  that source crossed a published threshold.
- Do not treat an `unavailable` source as excluded from the record on
  purpose; it is a documented access refusal, and opening it through
  the publisher's own channels is standing work.
- Do not assume a `planned` source's documents are absent from the
  digest for editorial reasons; they are absent because ingestion has
  not begun.

## Related

- The digest's Coverage Statement (per day) reconciles what was
  observed against what was summarized: the `fapd-daily-digest` skill.
- The politeness posture the pipeline applies to every source is
  described on `https://fapd.info/agents.html` and in the public
  repository's GUIDE.

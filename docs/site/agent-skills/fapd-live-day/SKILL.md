---
name: fapd-live-day
description: Read the in-progress federal publication day from today.json, or a finished day's frozen listing, without mistaking preliminary or backfilled items for the day's news.
---

# Read the live day, or a frozen day listing

The Free Agentic Publication Digester (FAPD) publishes a live view of
the current publication day as its collectors observe official
documents, and a frozen listing of each finished day. Neither is the
record. The dated digest, frozen at the end of the day, is the record
(see the `fapd-daily-digest` skill).

## Steps

1. **Fetch `https://fapd.info/today.json`.** It is PRELIMINARY: items
   arrive through the day, and the end-of-day gates decide what the
   dated digest keeps. The `disclosure` field says this in the file's
   own words; `generated` and `last_observed_at` are UTC stamps.
2. **Read `labels` before `items`.** Every honesty disclosure the human
   page carries is in the `labels` object, keyed by the field it
   explains. The JSON Schema at
   `https://fapd.info/schema/today.schema.json` repeats the same labels
   as property descriptions.
3. **Filter on `is_backfill == false` for the day's own news.**
   `items[]` includes every observation, including documents whose
   publisher dates them on another day (`claimed_day`). Those carry
   `is_backfill: true`; `backfill_count` states how many there are, and
   `backfill_note` explains the dating rule. The human page excludes
   them from the day's listing.
4. **Treat `duplicate_of` as a second observation, not a second
   document.** An item carrying `duplicate_of` arrived through another
   channel (for example, an email bulletin and a web feed delivering
   the same URL). The human pages show only the item it points to.
   Filter these out to match the human listing.
5. **Read `corroborated_by` as independent receipt, not judgment.** On
   a listed item, `corroborated_by` names the other ingestion channels
   that delivered the same canonical URL. It says the document arrived
   twice; it says nothing about the document's content or importance.
6. **Check `day_context` before calling a day quiet.** It is `null` on
   federal business days. On weekends and federal holidays it is an
   object `{kind, name, note}` explaining why the stream may be short.
   A one-item Sunday is not a broken pipeline.
7. **For a finished day, fetch `https://fapd.info/day/<YYYY-MM-DD>.json`.**
   It mirrors `today.json`'s shape and labels and adds `frozen: true`
   (and `reconstructed_on` when the listing was rebuilt from the stored
   observation journal after the fact, which the file discloses). A
   date the observation journal does not cover answers with
   `available: false` and an `unavailable_reason` instead of a listing.
8. **Then read the dated digest.** The frozen listing is the complete
   observed set with mechanical rules applied; the dated digest at the
   `html` URL in `https://fapd.info/digests.json` is what was validated
   and published as the record.
9. **If you speak MCP.** The read-only Model Context Protocol service at
   `https://fapd.info/mcp` offers the same listings as tools:
   `get_live_day` (step 1; it applies step 3's backfill exclusion by
   default and takes `include_backfill` to lift it, `collection` to
   keep one collection, and `agency` to keep one agency's items — the
   whole name, case ignored, taken from the result's `facets.tags`),
   `list_day_views` (the dates that have a frozen listing) and
   `get_day_listing` (step 7, same filters). For "what did agency X
   publish this week", call `get_day_listing` once per day with
   `agency` set. Each answer is the published file, filtered and paged;
   nothing is computed for you.
   `https://fapd.info/agents.html#mcp` describes how to connect.

## Fields worth knowing

- `official_url`: the item's own captured URL, or the govinfo details
  page for govinfo collections; `null` for an email bulletin with no
  URL.
- `channel_label`: how the item reached the pipeline (`govinfo API`,
  `web feed`, `email bulletin`, with `(DKIM-verified)` where the
  signature checked out).
- `tags`: mechanical tags only — branch, document type, agency. No
  model-generated tag is attached to an item.
- `summary_method`: `official` means the publisher's own text; `llm`
  means a labeled model-generated restatement.
- `opening_verbatim`: the first ~240 characters of the official text,
  unedited.
- `counts`: whole-day observation counts by collection and document
  type, backfill included.

## What not to conclude

- Do not quote `today.json` as what the government did on a date; it
  may change until the day freezes.
- Do not read `pending_llm` as an error count; it is the number of
  items awaiting a model layer, which is additive to the record.
- Do not compare item counts across days as activity levels without
  reading `day_context` and the Coverage Statement of each digest.

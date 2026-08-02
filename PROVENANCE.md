# Provenance & Verification

This project preserves content from **mutable** official sources (agency
newsrooms and similar websites) with cryptographic hashes so that claims
about what was published can be checked later. This document states
precisely what our records do and do not prove. The governing design is
GUIDE.md §7.

## What we record

For every fetch **attempt** against a mutable source — including responses
with no content (HTTP 304), robots.txt refusals, and errors — a row is
written to our capture log and exported into a daily manifest at
`provenance/manifests/YYYY-MM-DD.jsonl` (committed to this repository).
For content-bearing responses we store:

- the **exact decoded response bytes**, content-addressed by their SHA-256
  (`content_sha256`) in a local archive;
- a second hash of the **normalized extracted text** (`text_sha256`,
  tagged with the normalizer version) — this drives change detection,
  because raw web pages contain volatile markup (tokens, rotating asset
  URLs) that changes without the words changing;
- the URL requested, the final URL after redirects, the HTTP status, and a
  subset of response headers including the server's own `Date`;
- the source's **claimed** publication date and, separately, the time
  **we first observed** the document — never conflated;
- where enabled, the URL of an independent Wayback Machine snapshot of the
  same page.

Each daily manifest's header contains the SHA-256 of the most recent
earlier manifest on file, forming a chain. Honest scope of that chain,
stated precisely: it proves a retained middle manifest was not altered
(its hash would no longer match the next header), but the header names
no predecessor date — so the chain cannot by itself prove that the
newest day was not truncated away or that a day was never written at
all. Git history and the Wayback corroborations are the current
witnesses for those cases; strengthening the header with the
predecessor's date is on the development backlog.

## What this proves

- **Content integrity:** for any capture, anyone holding the archived
  bytes can recompute the SHA-256 and compare it to the committed
  manifest. A match proves the bytes are exactly what we recorded.
- **Change events:** when we assert a document was modified or removed
  after publication, both the before and after captures (and their hashes)
  exist and are cited.
- **Ordering:** manifests are committed to git as they are produced; the
  commit chain, GitHub's push history, and the manifests' internal hash
  chain together evidence the order and approximate time of observations.
- **Independent corroboration:** where a Wayback Machine snapshot URL is
  recorded, a third party archived the same URL near the same time.

## What this does NOT prove — read carefully

- A hash proves what was served **to our identified client, from our
  network position, at that time** — not what every visitor saw. Servers
  can vary responses by geography, session, or client.
- Our timestamps are our own records, ordered by git/GitHub history and
  corroborated by Wayback snapshots where present. They are **not**
  third-party notarized. (External anchoring, e.g. OpenTimestamps, was
  considered and declined 2026-07-26; the decision is revisitable and
  anchoring would strengthen claims only from the date it begins.)
- We can prove when **we first saw** a document; we cannot independently
  prove when it was **actually published**. Where a source's claimed date
  falls inside a window we demonstrably monitored without seeing the
  document, we flag the discrepancy — that is an observation, not an
  accusation.
- The capture archive is participation-limited: it covers the sources in
  `SOURCES.md` from the date each became active, nothing more.

## Verifying a capture yourself

1. Find the document's line in the relevant `provenance/manifests/*.jsonl`
   (fields: url, ts, `content_sha256`, `text_sha256`, change_kind).
2. Obtain the stored bytes (local archive `data/captures/<sha[:2]>/<sha>.bin`;
   no public capture bundle is published yet — for third-party
   verification use the item's Wayback URL when one is recorded).
3. `shasum -a 256 <file>` — the digest must equal the manifest's
   `content_sha256`.
4. For the manifest chain: `shasum -a 256` of a manifest must equal
   `prev_manifest_sha256` in the header of the next manifest that exists
   by filename order (days with no manifest are skipped by the chain —
   see the honest-scope note above).

One more honesty note: `verify_stored` (the hash recomputation) exists
as a function and as this manual procedure; the pipeline does not yet
run it on a schedule. A scheduled integrity sweep is on the development
backlog — until it lands, archive self-verification happens when a
person does it.

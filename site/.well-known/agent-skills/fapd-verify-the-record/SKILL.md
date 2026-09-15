---
name: fapd-verify-the-record
description: Check a Free Agentic Publication Digester digest against its public repository history and provenance manifests.
---

# Verify the record

Every Free Agentic Publication Digester (FAPD) digest is committed to a
public repository, and every fetch the pipeline makes against a mutable
source is hashed into a daily manifest committed beside it. This skill
says exactly what those records let you check, and what they do not.

## Steps

1. **Locate the canonical Markdown.** For the digest dated
   `<YYYY-MM-DD>`, the file is `digests/<YYYY-MM-DD>.md` in
   `https://github.com/davidkarnowski/free-agentic-publication-digester`.
   The copy served at `https://fapd.info/<YYYY-MM-DD>.md` is
   byte-identical to it; `https://fapd.info/digests.json` gives the
   repository path for each date as `canonical_markdown`.
2. **Read the file's git history.** The repository's commit log for
   that path shows when the digest was committed and whether it has
   changed since. A digest is frozen at the end of its day; a later
   commit touching it is a correction and says so in its message.
3. **Locate the day's manifest.** `provenance/manifests/<YYYY-MM-DD>.jsonl`
   in the same repository has one JSON line per fetch attempt the
   pipeline made against a mutable source that day, including
   responses with no content (HTTP 304), robots.txt refusals, and
   errors. The first line is a header.
4. **Read what a manifest line records.** For a content-bearing
   response: `content_sha256` (the SHA-256 of the exact decoded bytes
   as served to the pipeline's identified client), `text_sha256` (a
   hash of the normalized extracted text, tagged with the normalizer
   version), the URL requested and the final URL after redirects, the
   HTTP status, the source id, the UTC time of observation, and a
   `change_kind` (`new`, `unchanged`, or `modified` against the
   previous capture). Where one was made, a Wayback Machine snapshot URL of the
   same page is recorded as independent corroboration.
5. **Follow the chain.** Each manifest header carries
   `prev_manifest_sha256`, the SHA-256 of the most recent earlier
   manifest on file. Recompute a manifest's SHA-256 and compare it to
   the next manifest's header: a match proves that middle manifest was
   not altered. The header names no predecessor date, so the chain by
   itself cannot prove that the newest day was not removed or that a
   day was never written; git history is the witness for those cases.
6. **Verify a capture if you hold the bytes.** The pipeline's capture
   archive is local and no public capture bundle is published. If you
   obtain the bytes another way (a Wayback snapshot, or the publisher's
   page if it is unchanged), `sha256` them and compare to
   `content_sha256`; a match proves the bytes are exactly what the
   pipeline recorded.

## What the records prove, and what they do not

- A manifest hashes **fetched source content**. It does not hash the
  digest file. Do not write that a manifest verifies a digest; the
  digest's own integrity witness is its git history.
- A hash proves what was served to the pipeline's identified client,
  from its network position, at that time — not what every visitor
  saw. Servers can vary responses by geography, session, or client.
- The timestamps are the project's own records, ordered by git history
  and corroborated by Wayback snapshots where present; they are not
  third-party notarized.
- The pipeline can show when it first saw a document; it cannot prove
  when the document was actually published. A gap between a source's
  claimed date and first observation is an observation, not an
  accusation.
- The manifests cover the sources listed in the public repository's
  `SOURCES.md` from the date each became active, nothing more.

## Related

- The full statement of scope is `PROVENANCE.md` in the repository;
  read it before relying on any claim above.
- Which sources are covered and from when: the `fapd-source-coverage`
  skill.

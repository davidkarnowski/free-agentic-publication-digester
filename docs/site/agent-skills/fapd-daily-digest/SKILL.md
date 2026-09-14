---
name: fapd-daily-digest
description: Find and read the Free Agentic Publication Digester's validated daily digest of official US federal publications for a given date, and cite it correctly.
---

# Read a daily digest

The Free Agentic Publication Digester (FAPD) publishes one digest per
publication day. Each digest covers the official record of that day —
congressional floor activity, bills, Federal Register documents, enacted
laws, court opinions, agency announcements, recorded votes, bill actions,
and presidential actions — with a citation on every item and a Coverage
Statement that accounts for everything observed. A digest that fails
validation is not published. The dated digest is the record; the live
page is not.

## Steps

1. **List the published dates.** Fetch
   `https://fapd.info/digests.json`. The `digests[]` array lists every
   published day, newest first, with `date`, `html`, `canonical_markdown`
   (the path inside the public repository) and a `teaser`. The MCP
   service at `https://fapd.info/mcp` exposes the same index as a tool
   (see `https://fapd.info/agents.html#mcp`).
2. **Pick the date.** Digest dates are publication days on the clock
   the site names in its own prose (the digest header and
   `https://fapd.info/faq.html#fapds-three-clocks` say which). If the
   date you want is not in the list, go to step 8.
3. **Fetch the digest.** The canonical Markdown is
   `https://fapd.info/<YYYY-MM-DD>.md` (byte-identical to the repository
   file). The styled page is the `html` URL that `digests.json` gives for
   that date. Both carry the same content.
4. **Read the header table first.** The **Inference** row states whether
   model layers ran for the day and which provider served them. When it
   reads "No inference was available for this publication day. All
   content is source-derived or mechanically constructed.", every line in
   the digest is official text or a mechanical listing; there is no
   model-written prose to weigh.
5. **Read the Coverage Statement** (the section near the end). It
   reconciles, per collection, what was observed, what was summarized,
   what was counted only, and what was excluded — and names the rule for
   every exclusion. Absence from the digest body is never silent: if an
   item is not summarized, this table says so and says why.
6. **Tell official text apart from restatements.** Official titles,
   Federal Register summaries, and quoted passages are verbatim
   government text. Lines that begin *In plain terms:*, the section
   quick-reads, and the Day in Review are model-generated restatements
   derived only from the adjacent official material and checked against
   an editorial banned-lexicon. Where the live page labels a summary
   **FAPD-AI**, the same rule applies: it is a restatement, not the
   record.
7. **Cite correctly.** For a factual claim about what the government
   published, cite the official source linked on the item (govinfo for
   the govinfo collections; the agency's, chamber's, or Congress.gov's
   own page otherwise). Cite FAPD for the aggregation, the selection,
   and any restatement you quote. Every item also carries an
   "Included because" line naming the mechanical rule that selected it;
   quote that rule when you explain why an item appears.
8. **A missing date is a missing digest, not an empty day.** If a date
   is absent from `digests.json`, no digest was published for it. Do
   not conclude that nothing was published by the government that day.
   Check the digest that exists for the nearest later date: its
   Coverage Statement files items by the day they were first observed,
   and the header's weekend or holiday note explains a short day.
9. **If you speak MCP.** The same two files are tools on the read-only
   Model Context Protocol service at `https://fapd.info/mcp`:
   `list_digests` returns the index (step 1) and `get_digest` returns
   the canonical Markdown for a date (step 3), verbatim, with the same
   citation rule stated in its preamble. `https://fapd.info/agents.html#mcp`
   describes how to connect and what the service does not do.

## What not to conclude

- A digest's item count is not a measure of government activity; it is
  what the pipeline observed under mechanical selection rules.
- A summarized item is not more important than a counted-only one; the
  rule that selected it is stated, and the rules are party-blind.
- The teaser in `digests.json` is the first lines of the Day in Review,
  which is model-generated; do not quote it as official text.

## Related

- Live in-progress day: the `fapd-live-day` skill.
- Verifying a digest against the repository: the
  `fapd-verify-the-record` skill.
- Agent guide: `https://fapd.info/agents.html`; machine guide:
  `https://fapd.info/llms.txt`.

# Source adapters, a 420-second crawl-delay, and what "polite" actually costs

*Dev notes, 2026-07-28. The day the pipeline went from five govinfo
collections to a nine-newsroom pilot ingest — and everything that broke,
slowed down, or surprised us on the way.*

## The problem shape

The pipeline's first sources were easy in one specific sense: govinfo.gov is
built for machines. One API, one key, watermark-based delta sync, consistent
metadata. Agency newsrooms are the opposite — every agency publishes
differently, and the differences are not cosmetic. Some feeds have GUIDs,
some don't. Some article pages welcome an honestly-identified client, some
403 it. One (USPS) routes every feed link through a JavaScript redirect page
that contains no article at all.

The design answer was a **seam**: one shared poll loop that owns everything
that must never vary — conditional requests, robots.txt enforcement, request
budgets, provenance capture, storage — and a per-source `SourceAdapter` that
owns exactly four decisions:

1. **`stable_id`** — what makes two sightings the same document?
2. **`wants_article`** — fetch the full page, or feed metadata only?
3. **`extract_text`** — how do served bytes become text?
4. **`fallback_text`** — what do we store when no article is fetchable?

Four methods is the whole interface. The default adapter (RSS with GUIDs,
fetchable articles) needs no code at all. Everything irregular becomes a
small subclass, and the irregularity is *documented where it lives* — in the
adapter's docstring, against evidence from captured bytes.

## Case study: the USPS interstitial

USPS's newsroom feed has 668 items, zero GUIDs, and every link points to
`rssrequest.htm?nr=<article-path>` — a 1.8 KB page whose entire visible text
is "RSS Feed Request" and whose only function is a JavaScript redirect to
`/newsroom/` + the `nr` parameter. Our first probe recorded a 16-character
extraction and called the source poorly extractable. Re-reading the captured
bytes corrected the diagnosis: the article pages weren't bad — *we had never
seen one*. The interstitial carries no content; the redirect happens in a
browser we don't have and wouldn't impersonate.

The adapter that came out of this mirrors the redirect arithmetic **as
static parsing of bytes we were served** — reading `?nr=X` and computing
`/newsroom/X`, exactly what the page's own script does — to get a stable
document identity, while declining to fetch pages we know carry nothing.
That's the access-hierarchy line in practice: parsing structured data a
server sent us is legitimate; executing scripts or pretending to be a
browser is not.

## The day's real lesson: what "polite" costs, and how to pay it smarter

The bootstrap ingest of nine newsrooms surfaced something no amount of
design review would have: **gao.gov's robots.txt declares a 420-second
crawl-delay**, and our client honors crawl-delays. One article every seven
minutes. Twenty-five new items. The math is three hours, and the first
(serial) ingest run spent those hours making every *other* agency wait in
line behind GAO's sleep timer.

The fix was not to speed anything up — GAO asked for 420 seconds and GAO
gets 420 seconds. The fix was recognizing that politeness is a promise made
to *each server individually*. The run was restructured so that each host
gets its own worker with its own pacing clock: every host still experiences
at most one request per second, its own crawl-delay, conditional requests —
exactly as if it were our only source — but no host waits behind another's
promises. Sources sharing a host share a worker, so their pacing clocks
stay common. Daily request budgets stay global across workers, counted from
a shared fetch log that every client writes through.

After the change: eight of nine newsrooms finished in under a minute.
GAO still takes its three hours, and that's correct — it's GAO's three
hours, not ours to reclaim.

Two details worth stealing if you build something similar:

- **Interrupted ingests have a resume trap.** The poll loop stores feed
  ETags and sends `If-None-Match` on the next poll. Kill a run halfway
  through a feed's items and the next run gets `304 Not Modified` — and
  silently skips everything the first run hadn't reached. Restarting after
  an interruption means clearing the saved ETags (a handful of cheap feed
  re-fetches) and letting item-level dedupe absorb the overlap.
- **Long sleeps deserve INFO, not DEBUG.** A 419.7-second pacing sleep looks
  exactly like a hang unless the log says why. The client now announces a
  host's crawl-delay once ("one request per 420s to this host") and logs any
  sleep over 30 seconds at INFO with its reason.

## The Wayback budget meets reality

Every new capture gets submitted to the Internet Archive's Save-Page-Now as
an independent second witness. That corroboration has its own self-imposed
budget (100 requests/day), and the bootstrap run — 100+ new documents in one
day — exhausted it after 40 snapshots. By design, corroboration never blocks
ingestion; the remaining items ingested with hashes and manifests but
without a same-day archive.org witness.

The interesting part is what happened next: our governing document claimed
"Wayback snapshot per new capture," and a reviewer building the public
methods page flagged the mismatch between that promise and the budget's
arithmetic. The document now says what the code does: snapshots *within the
daily budget*, best-effort, never blocking, gaps topped up by later passes.
When documentation and reality disagree, reality wins and the documentation
moves — in public.

## Research before probes: reading the front door's sign

The day ended with a documentation-first research sweep across the federal
source universe — three parallel research passes reading agencies' *own*
published access documentation (developer pages, API docs, official RSS
directories) before any endpoint gets probed. Findings that reshaped the
source registry, now 93 entries:

- **A WAF on the newsroom is not a closed agency.** About half of our 23
  "unavailable" sources turned out to have a documented machine channel on a
  different host or path: FCC's EDOCS feed API, Commerce's content API,
  NOAA's main feed, OFAC's own subdomain, and — the big one — DVIDS, DoD's
  distribution API, which alone re-opens all six blocked military-service
  newsrooms.
- **Some "unavailable" was just "moved."** Three sources recorded as dead
  404s (DOJ's feed, uscourts.gov news, the Sentencing Commission) had
  simply relocated, and all three document live RSS feeds at their new
  homes.
- **Feed autodiscovery under-finds.** NIST documents ~24 RSS feeds on its
  own feeds page; none appear in its pages' HTML metadata. Reading the
  publisher's documentation is now part of source onboarding, not an
  optional extra.
- **The best door was already unlocked.** The api.data.gov key the pipeline
  has held since day one also opens the Congress.gov API (committee
  meetings, nominations, House votes, CRS reports), Regulations.gov, and
  OpenFEC. And the Federal Register's own API — keyless — exposes documents
  filed for public inspection *before publication day*, with the site's
  bot-gate page explicitly directing automated visitors to use it.

Every candidate is registered as `planned` with its evidence; none is
active. Probing through the pipeline's identified, budgeted client — the
only verdict we record as fact — is a deliberate, operator-approved step.
That ordering (register → research → probe → evaluate → activate) is the
whole onboarding philosophy in one line: know what the publisher intends
before asking their server anything.

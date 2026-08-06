# Frequently Asked Questions

*How the Free Agentic Publication Digester keeps time, how its
collectors behave, and how to read what it publishes. This page grows
as questions do; the [methods page](methods.html) carries the fuller
technical story.*

## FAPD's three clocks

Every document in this record has up to three dates, and they are not
the same thing. We name them precisely because confusing them is how
aggregation quietly misleads.

- **Date of Action** — the day something happened, as described in the
  document's own text: the day the Senate debated, the day a judge
  issued an opinion, the day printed on the Federal Register's cover.
  This date may not be available to us directly; it depends on the
  metadata and text the source provides.
- **Date of Publication** — the day the publisher made the document
  available, as stated in the publisher's own metadata. Also not always
  available, and not always reliable: publishing systems post late,
  backfill, and revise.
- **Date of Observation** — the day our own collector first saw the
  document. This is the one timestamp we can define precisely, from our
  own worker records, for every document without exception.

**Observation is our source of truth for filing.** A daily digest
carries what our collectors observed that day (Eastern time, the
publishers' own clock), and each item states its own document date
beside it when the two differ. One exception: the Federal Register
files under its cover date, because that is the date on which it is
legally published — and it is the case where all three clocks agree by
design.

Why observation rather than the publisher's stamp? Because the
publisher's stamp can lie about availability. If a publishing system
goes down and a document stamped Monday only becomes reachable
Wednesday, filing by the stamp would assign it to a digest that was
already frozen — and it would vanish from the record. Filing by
observation, nothing we see can ever miss its digest. Congress's
official Record, for example, is typically published the morning
*after* the day it covers: you will find it in the digest for the day
it became available, labeled with the day of proceedings it describes.

## How do FAPD's collectors actually work?

At the simplest level: our collectors are polite readers.

Each one visits an official government publishing site on a fixed
schedule, the way you might check a library's new-arrivals shelf. It
asks "what's new since I last looked?", writes down exactly what it saw
and exactly when it saw it, and saves a copy of the official text. It
never guesses, never rewrites what it found, and never knocks faster
than a site says visitors may knock. If a site publishes rules for
robots, we follow them exactly — including one site that asks for seven
minutes between visits, and gets it.

Everything else on this site — the digests, the summaries, the
statistics — is built from those notebooks.

## How often do you look? (observation windows)

Each collector runs on its own clock, so "observed on day D" has a
known precision per source type. If a document appeared on a
publisher's site at moment T, we typically observed it within one cycle
of T:

| Source type | Check cycle | Observation window |
|---|---|---|
| govinfo collections (Congressional Record, bills, court opinions, laws) | every ~30 minutes | within ~30 minutes of govinfo posting it |
| Agency newsrooms and press feeds | every ~60 minutes per site | within ~1 hour |
| Email bulletins (agency subscription lists) | every ~15 minutes | within ~15 minutes of delivery |
| gao.gov | feed checks honoring its requested 420-second spacing | within ~1 hour |
| The live "today" page | rebuilt within ~5 minutes of new observations | — |
| Source health on the [sources page](sources.html) | refreshed every ~15 minutes | — |

The daily digest freezes at midnight Eastern — Washington's own clock —
and is then the canonical record for that day. Collectors keep working
around the clock; anything they observe after midnight belongs to the
next day's digest.

## Does a slow source mean missing coverage?

No — it means labeled timing. A court that posts an opinion four days
after issuing it appears in the digest for the day we observed it,
carrying its own issue date in the listing. The Coverage Statement in
every digest accounts for everything observed that day, and anything
deliberately not summarized is counted under a named mechanical rule.
Silent omission is the failure mode this project is built to prevent.

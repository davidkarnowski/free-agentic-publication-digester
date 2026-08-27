# Forking for another government

*Added 2026-08-26 with the publication-clock ruling (GUIDE §3). Scope:
the clock and the calendar — the two things in the code that are
specific to the United States federal government's schedule. The
sources themselves (govinfo, Congress.gov, agency newsrooms) are the
registry's business and are not covered here.*

The Free Agentic Publication Digester is built around the federal
government's publishing day, but nothing in the pipeline's timing
depends on that day being Washington's. Two knobs carry the whole
assumption; change them and every digest date, end-of-day boundary,
live-page rollover, activity graph, and clock label follows.

## 1. The publication clock — `FAPD_PUBLICATION_TZ`

`src/fapd/config.py` is the one place the clock is named:

| Variable | Default | What it is |
|---|---|---|
| `FAPD_PUBLICATION_TZ` | `America/New_York` | The IANA zone whose calendar day is the publication day. An unresolvable name raises at import — deliberately loud. |
| `FAPD_PUBLICATION_TZ_LABEL` | `Eastern time` | The long, spoken form (screen readers hear it beside every clock reading). |
| `FAPD_PUBLICATION_TZ_ABBREV` | `ET` | The short, visible form. Fixed on purpose: zoneinfo's own abbreviations flip between standard and daylight forms twice a year, and a label that changes with the season is one a reader has to decode. |
| `FAPD_PUBLICATION_TZ_PLACE` | `Washington, D.C.` | The place whose clock it is, for prose ("the clock the publishers keep in …"). |

The three labels default from a built-in table that knows
`America/New_York`. For any other zone the fallback is honest rather
than pretty — the IANA name as the label, the zone's own abbreviation
only when it has no daylight shift (`Asia/Tokyo` → `JST`), the last
path segment as the place — so set the three explicitly for a
production fork. Zones with a fractional offset (`Asia/Kolkata`,
`Asia/Kathmandu`, `Australia/Adelaide`) are handled: the activity
graphs' SQL grouping drops to the minute for them automatically.

What the clock governs, all through `sync.publication_date()` and its
siblings (`publication_day_hour`, `publication_day_start_utc`,
`publication_day_hours`):

- the day every document is filed under (`packages.digest_day`) and
  the agency-release dating rule;
- the end-of-day finalizer's target and its hour gate
  (`config.EOD_ET_HOUR` — the name predates the knob; it is read on
  the configured zone);
- the live `/today` page's rollover, its observed-at stamps and hour
  headings;
- the source cards' 7-day heatmap and hourly micro-bars, the
  per-source day-by-day charts, and the trailing health windows;
- every clock label on those surfaces, through `publish._clock_suffix()`.

What it does **not** change: stored observation stamps
(`first_seen_at`, `observed_at`, `ts_utc`) are UTC and stay UTC in the
databases, in `<time datetime>` attributes, and in every JSON surface.
GUIDE §3 (2026-08-26) names the three uses — storage, dating,
presentation — and licenses conversion only for the third.

Pinned by tests: `tests/test_sync.py` proves the same code buckets
differently under `Asia/Tokyo` (through the `tz=` seam, a replaced
config attribute, and the environment variable in a fresh
interpreter); `tests/test_publish.py::test_no_rendered_string_hard_codes_the_clock`
fails if a rendered string in the renderers or the health module spells
out the default clock again.

## 2. The working calendar — `src/fapd/fedcal.py`

The second FedGov-specific piece is the calendar that explains a quiet
day: the eleven federal holidays of 5 U.S.C. 6103 with OPM's observed
shifts, plus weekends. It is a pure, dependency-free module with one
public entry point the rest of the code consults —
`fedcal.reduced_publishing(date_str)`, called from exactly two places
(`publish.py` for `/today` and the day views, `report.py` for the
digest header), both of which render its one neutral sentence and
nothing else. To fork: replace the `_FIXED` and `_FLOATING` tables (and
the observed-shift rules in `federal_holidays`) with your government's
statutory holidays and keep `reduced_publishing`'s return shape
(`{"kind", "name", "note"}`) — the callers and `tests/test_fedcal.py`
depend on that contract, not on the list.

## 3. Prose that names the deployment

The public site's own pages (`docs/site/methods.md`, `faq.md`,
`accessibility.md`, `privacy.md`) and `README.md` say "Eastern" and
"Washington" in ordinary sentences describing *this* deployment. They
are content, not code paths, and a fork rewrites them the way it
rewrites the mission statement; the audit test deliberately does not
cover them. Everything a renderer emits reads the labels above.

# Accessibility

The **Free Agentic Publication Digester (FAPD)** publishes the official
publications of the United States federal government. Everyone has the
same claim on that record, so this site is meant to work for people
using screen readers, screen magnification, voice control, switch access,
and keyboard-only navigation, and for readers with low vision or who need
to reduce what is on screen at once.

## The standard we build to

**WCAG 2.2 Level AA is the floor, not the goal.** Where meeting AA would
still leave the site awkward to use, we aim past it and say so below. We
do not claim conformance: the work described here was verified by
inspection, by measurement, and by an automated test suite, and it has
not yet been tested by a person using the assistive technologies it is
for. That gap is stated under *Known limitations* rather than left for
you to discover.

Two structural choices help. The site is static HTML with no framework
and no external resources of any kind, and it carries exactly one small
script — on the live page, appending your local time beside each
published Eastern time. Everything else works with scripting off. There
is no login, no data entry, no timed content, no animation, and no
motion.

## What we have done

- One shared stylesheet with a light and a dark palette. Every text and
  boundary colour in it was computed against the WCAG contrast
  thresholds, in both palettes, including the tinted keyword chips where
  the text sits on a translucent fill.
- A skip link to the main content on every page, and a second skip past
  the keyword filters on the live page.
- The keyword filter on the live page is built from real HTML
  checkboxes, so it is operable from the keyboard and can be cleared
  with a single native button. Each checkbox states its own name and
  count, rather than inheriting the concatenated text of the hundreds of
  labels that point at it.
- Selecting a keyword is marked by a check mark as well as by a colour
  change, so the selection is readable in grayscale, with a colour vision
  deficiency, and in Windows High Contrast, where the colour fill is
  discarded by the operating system.
- The live page states, in words, which keywords are currently selected,
  and how many items are showing.
- Filtering hides items in a way that removes them from assistive
  technology and from the tab order together — a hidden item is hidden
  consistently, never left half-present.
- Printing the live page always prints the whole day, never the filtered
  subset, so a printed page can never read as the complete record when it
  is not.
- Branch of government, document type, and agency are conveyed in words
  on every item. Colour is a second signal, never the only one.
- Text that a model generated is labelled as such in words, not only by
  a dashed border and an italic. So is the mechanical rule that selected
  each item, and the description of what that rule means.
- Timestamps say what they are: the time we observed a publication, in
  Eastern time, spoken in full.
- Links that leave this site are marked as opening in a new tab.
- Digest sections carry real headings that are exposed whether the
  section is open or closed, so a day can be moved through by heading;
  and a link to a section opens the section it points at.
- Tables carry header-cell relationships, and each sits in a named region
  that can be scrolled from the keyboard.
- Every link, button, and disclosure control has a focus indicator drawn
  by us rather than left to the browser default.
- Filter chips are at least 30 pixels tall, above the 24-pixel minimum
  target size, and carry a boundary that meets the contrast threshold for
  a control.
- The site is usable at 400% zoom and at a 320-pixel-wide viewport.

## Known limitations

We would rather name these than let you find them.

- **We have not completed a manual test with assistive technology.** The
  site has been audited by inspection and by measurement. Testing with
  NVDA and Firefox, JAWS and Chrome, and VoiceOver on macOS and iOS is
  planned, along with Windows High Contrast, voice control, and screen
  magnification at 400%. Results will be published here, including
  whatever they find.
- **The live page is large.** A busy publication day puts several hundred
  items and around sixty keyword filters on one page, and the filter's
  checkboxes all sit together ahead of the stream. The skip links go past
  them, but moving through the page by keyboard still takes time. We are
  looking at grouping the filters rather than at hiding items behind
  pagination, because a paginated day is a less complete day.
- **We do not know whether the filter's readout is announced.** The live
  page states which keywords are selected and how many items remain, and
  it does so without script, which means the text is revealed by a
  stylesheet rather than written by code. Whether a screen reader speaks
  that change on its own varies by browser and by screen reader, and we
  have not yet measured it. Until we have, treat the readout as something
  you can read, not as something you will be told.
- **Focus and magnification on the filter.** Each filter checkbox is a
  one-pixel element at the top of the form, while the indicator you see
  is drawn on its chip, which may be several rows lower. At high
  magnification the two can fall in different parts of the viewport, so
  tabbing through the filter may show you no indicator at all. This is a
  consequence of how the filter is built without script, and rebuilding
  it is open work.
- **Some of this is wordy.** Marking every outbound link as opening in a
  new tab, and reading out every inclusion rule's description, adds
  spoken text to pages that already carry a lot. We chose stating the
  information over hiding it. If the result is too much to listen to,
  that is worth telling us — see below.
- **Digest pages carry no `lang` change for quoted text.** Official
  federal publications are in English throughout, so this has not come
  up; if a quoted passage in another language ever appears, it will need
  marking.

## Tell us what is broken

If any part of this site is hard or impossible for you to use, please
write to **hustleyourcity@gmail.com**. Include the page address and what
happened; if you can, name the assistive technology and browser. A
description of the problem in your own words is entirely enough — you do
not need to identify a technical cause or cite a standard.

We treat an accessibility report the same way we treat a factual
correction to a digest: it goes on the record and it gets fixed. Reports
that identify a barrier will be acknowledged, and the fix, or the reason
it is not yet possible, will be stated here.

## Alternatives

The same content is published as JSON (`/digests.json` for the archive,
`/today.json` for the live day) and as an Atom feed (`/feed.xml`), and
the canonical Markdown of every digest lives in the project repository
alongside its provenance manifest. If the HTML is not working for you,
those may be easier to read or to hand to a tool of your choosing. The
[guide for agents](agents.html) describes all of them.

*Last reviewed: 2026-07-30. This statement describes the site as it
stands, including what is not fixed yet.*

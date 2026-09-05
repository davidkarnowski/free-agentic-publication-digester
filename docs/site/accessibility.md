# Accessibility

The Free Agentic Publication Digester publishes the official record of
the United States federal government. Everyone has the same claim on
that record, so this site is built to work with screen readers, screen
magnification, voice control, switch access, and keyboard-only
navigation.

## Standard and conformance

We build to **WCAG 2.2 Level AA**. As of 2026-07-30 this site is
**partially conformant**: a full audit of every page class was completed
on that date and its findings fixed, with the exceptions listed below.
The live page was substantially revised on 2026-08-02 (layout, hour
groupings, a weekend/holiday notice); a follow-up audit of that page is
queued and this statement will be updated with its date.

The site is built to work with assistive technology by construction.
Presentation is server-rendered semantic HTML; every control is a native
HTML element rather than a custom widget, because native elements are
what screen readers, voice control, switch access and magnification were
built to handle; and the context a sighted reader gets from layout is
written into the page as real text rather than added by script. Colour
contrast and target sizes are computed from the stylesheet's declared
values rather than judged by eye. The method we design by is published
in full alongside the code, as `docs/accessibility-doctrine.md` in the
public repository, so it can be checked rather than taken on trust.

The site is static HTML with no framework and no external resources. It
carries one small script, on the live page only, which adds your local
time beside each published Eastern time — everything works with
scripting off. There is no login, no timed content, and no animation;
the only interactive control is the live page's client-side keyword
filter, which transmits nothing.

## Known limitations

- **Focus can leave the viewport at high magnification** on the live
  page: a filter's checkbox sits at the top of the form while its
  visible chip may be rows lower. This follows from filtering without
  script; rebuilding it is open work.
- **The filter's readout may not be announced.** It is revealed by the
  stylesheet rather than written by code, so treat it as something you
  can read, not something you will be told.
- **Filter counts are for the whole day**, not the filtered subset.

## Report a problem

Email **hustleyourcity@gmail.com** with the page address and what
happened. A description in your own words is enough — you do not need to
identify a cause or cite a standard. Accessibility reports are treated
like factual corrections to a digest: they go on the record and get
fixed.

## Alternatives

Every digest is also published as plain Markdown in the repository, and
the machine surfaces (`/llms.txt`, `/digests.json`, the Atom feed) carry
the same content in formats that do not depend on our styling.

## Multi-modal audio modality & assistive access

As part of our commitment to universal access, the About page carries synthesized audio narration of its sections in addition to the canonical text. Narration for the daily digests is built but not enabled: no digest page carries audio today, and none will until the narration surface is versioned and ledgered like every other model output (GUIDE §3a). When that changes, this page will say so.

- **Verbatim Content Parity**: The audio narration provides an exact spoken reading of the synthesized prose. Text and audio present identical factual information — neither modality receives exclusive content.
- **Screen Reader & Assisted Technology First**: Audio is presented using HTML5 native `<audio>` elements with explicit `controls`, `preload="none"`, and descriptive `aria-label` attributes.
- **Direct Audio Download**: Every player includes a direct, visible, keyboard-navigable download link (`Download MP3`) to retrieve raw `.mp3` files for offline listening, screen readers, braille displays, and custom assistive software.


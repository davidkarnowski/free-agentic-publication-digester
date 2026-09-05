# Accessibility doctrine — how we comply

*Created 2026-09-05 under GUIDE §2a (Universal Access). Living document:
it describes the method we build by, and it changes when the method
changes — never by date bump alone (§9).*

---

## §0 What this document is, and what it is not

This project keeps three accessibility documents, and confusing them is
how doctrine rots into a stale audit or an unearned claim. The boundary
is explicit and load-bearing:

| Document | Kind | Tense | Changes when |
|---|---|---|---|
| **GUIDE §2a** | Constitution — what we owe every reader | binding, permanent | the operator amends it |
| **`docs/accessibility-doctrine.md`** (this file) | Method — how we comply, operationally | living, forward-binding | the method changes |
| **`docs/accessibility.md`** | Findings record — what was measured, when, and what happened to it | dated, frozen per entry | a finding opens or changes status |
| **`docs/site/accessibility.md`** | Public statement — what we tell readers | claim | a claim becomes true or stops being true |

**Precedence.** GUIDE §2a governs this file and may not be weakened by
it. Where this file and §2a appear to disagree, §2a wins and this file
has a bug — fix this file. Where this file and the code disagree, one of
them is wrong and the commit that resolves it says which.

**This file is not a task list and not an audit.** It carries no
findings, no statuses, no dates-of-measurement. Those belong in
`docs/accessibility.md`, which is deliberately a record of what the site
*was* at a measured moment and is never retroactively rewritten.

**This file is not the public statement.** It may describe internal
method, open method questions, and the limits of our verification in
plain terms. What we say publicly is governed by GUIDE §2a rule 10
(*conformance claims are honest or absent*) and lives in
`docs/site/accessibility.md`.

**Audience.** A person or agent about to change anything that renders
HTML. Section agents load this before site work
(`docs/agents/publication.md`).

---

## §1 The design ladder

Work down the rungs **in order** and stop at the first one that does the
job. Skipping a rung requires a comment saying why, in the code, at the
site of the skip.

1. **Semantic HTML.** A heading is a heading, a list is a list, a table
   is a table with a caption. Most access problems are structural, and
   structure is free.
2. **A native element.** A real link, a real `<button>`, a real
   `<input type="checkbox">`, a real `<details>`. Browsers and assistive
   technology have spent thirty years agreeing on what these mean, in
   every combination of platform and screen reader we will never own.
   Reimplementing one is how you inherit every bug that agreement fixed.
3. **HTML + CSS interaction, only where no native element exists.**
   Permitted, deliberately, and it is where our two interactive surfaces
   live. It carries obligations: the state must be real DOM state (a
   checked checkbox, an open `<details>`), the control must be reachable
   and operable by keyboard without author code, and the visual result
   must not be the only carrier of the state.
4. **There is no rung four.** A scripted widget is not an option
   available to this project (GUIDE §2a rule 3).

**Worked example — the live page's keyword filter.** Hidden checkboxes
plus a sibling combinator, with the browser's own `<form>` reset button
clearing every selection at once. `:target` was evaluated and rejected:
a fragment cannot be un-clicked, it moves the viewport under the reader,
and it supports only one active selection.

**Worked example — the archive.** The requirement was "let a reader
reach any published day." Rung 1 answers it: a month is a table, a day
is a link. No date picker exists on this site, and none is needed —
which is the point of working down the ladder rather than starting at
the widget and asking how to make it accessible.

---

## §2 The modalities we design against

GUIDE §2a rule 6 names the list; this is the list with its consequences.
Each row is a design obligation, not a sympathy. When reviewing a new
surface, walk the table.

| Modality | What breaks it | What we do |
|---|---|---|
| **Screen readers** | meaning carried by styling — a dashed border, an italic, a `title` attribute, CSS generated content | real text in the document; `.vh` spans for context a sighted reader gets from layout; never `title` as the sole carrier |
| **Screen magnification (to 400%)** | fixed widths, horizontal scroll, focus landing outside the viewport, controls far from what they affect | reflow to a 320 px viewport; controls adjacent to their effect; wide content scrolls inside its own labelled region, not the page |
| **Voice control** | an accessible name that does not begin with the visible label — the user says what they see and nothing happens | visible text is the start of the accessible name (SC 2.5.3); extra context is appended in `.vh`, never prepended |
| **Switch access and scanning** | many small targets, tight spacing, anything requiring a sustained or repeated gesture | generous targets (see §4.2), real spacing, no drag, no double-action, no timing |
| **Head pointers and eye gaze** | same as switch, plus hover-revealed content and targets that move | 44 px minimum targets; nothing revealed on hover alone; no layout that shifts under the pointer |
| **Keyboard-only** | focus traps, invisible focus, tab order that follows the stylesheet instead of the document, long uninterruptible runs of links | visible focus everywhere; skip links ahead of any long run; DOM order is reading order |
| **Forced colors / high contrast** | custom colors silently discarded, leaving borderless controls and invisible state | a `@media (forced-colors: active)` block declaring system colors for every control boundary and state marker |
| **Reduced motion** | animation the reader did not ask for | the site has none; if any is added it is behind `prefers-reduced-motion` |
| **Working memory and cognitive load** | state the reader must hold to interpret what they see; counts that mean something different than they say | state visible where its effect is; numbers labelled with exactly what they count |

Two standing rules that fall out of the table:

- **Never `title` for information.** It is not reliably announced, not
  reachable by touch, and not reachable by keyboard. It may decorate
  (an `<abbr>` expansion beside visible text); it may never be the only
  place something is said.
- **Never `opacity` to de-emphasize text.** It composites the text back
  toward the background and silently destroys a computed contrast ratio.
  De-emphasize with a token that was computed against the background it
  will actually sit on.

---

## §3 The pattern inventory

The reusable answers already in the codebase. **Reach for these before
inventing** — an invented equivalent is a second thing to test, and the
audit identifiers below are the evidence that these were reasoned about
rather than guessed.

| Pattern | Where | What it solves |
|---|---|---|
| `.vh` visually-hidden utility | `publish._STYLE` | context a sighted reader gets from layout. `clip-path` and a 1 px box, not `display:none`, so the text stays in the accessibility tree and in inline layout |
| Skip link | `publish._PAGE`, and per-surface (`#today-stream`) | bypassing long runs of controls before content (A11Y-02, SC 2.4.1) |
| Labelled scrollable table region | `publish._accessible_tables` | `display:block` on a `<table>` strips table/row/cell roles; the scroll moves to a focusable labelled wrapper and `<th>` gets `scope` (A11Y-03) |
| Native `<details>` sections | `publish._collapse_sections` | disclosure without script; a closed section's content stays out of the tab order but reachable (A11Y-04) |
| Announced external links | `publish._externalize_links` | a new tab opened without notice is a change on request failure (A11Y-12, technique G201). One seam — route new pages through `_render_page` and it applies |
| Link purpose out of context | `publish._nav_for` | `← 2026-07-28` is a bare date in a screen reader's link list; the purpose rides in `.vh` (A11Y-16, SC 2.4.4) |
| `aria-current="page"` in nav | `publish._nav_link` | the current page is marked, not dropped — every page renders every link in one order |
| Non-color state marker | filter chips | a check glyph carries "selected", not the fill alone (A11Y-06, SC 1.4.1) |
| Forced-colors block | `publish._STYLE` | control boundaries and state markers survive when custom colors are discarded |
| Author focus style | `:focus-visible`, 3 px outline + 2 px offset | SC 2.4.7, and 2.4.13 appearance (A11Y-17, A11Y-08) |
| Inline SVG charts | `publish._svg_bar_chart`, `_svg_sparkline`; pattern in `docs/accessibility.md` §4a | the SVG is decorative duplication and is hidden from assistive technology; the same series ships as a real `.vh` table with a caption and one row per day |
| Native `<audio>` + visible download | `publish.render_audio_player` | an alternate modality that needs no player script and can be taken away and used elsewhere |
| Print rules | `@media print` | a filtered subset must never print as though it were the whole day |

---

## §4 Measurement

GUIDE §2a rule 8: computed, never judged by eye. Both figures below are
derived from declared values, not from a screenshot and not from a
browser's rendering.

### §4.1 Contrast

WCAG 2.x relative luminance, computed for **every palette the site
ships** — currently the light default and the `prefers-color-scheme:
dark` override. Translucent fills (`rgba()`) are composited over their
resolved background **before** the ratio is taken, and `opacity` is
composited after that, in that order.

```python
def _lum(hex_color):
    h = hex_color.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contrast(fg, bg):
    l1, l2 = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)
```

Thresholds we apply:

| Thing | Minimum | Criterion |
|---|---|---|
| Body and control text | 4.5:1 | 1.4.3 |
| Large text (≥24 px, or ≥18.7 px bold) | 3:1 | 1.4.3 |
| **Control boundaries and state indicators** | **3:1** | **1.4.11** |
| Focus indicator against both adjacent colors | 3:1 | 1.4.11, 2.4.13 |

**The trap this catches, from the archive work.** The obvious border for
a calendar day cell is `--border`, the site's dividing-rule token. It
computes to **1.34:1** against the page background — correct for a
decorative rule, and nowhere near the 3:1 a control boundary owes under
1.4.11. Day cells use `--control-border` instead: **3.22:1** light,
**3.61:1** dark. No amount of looking at it would have surfaced that.

A change touching color states its computed ratios in the commit body
(code-standards §2 r11).

### §4.2 Target size

Computed from the declared box — `font-size` × `line-height` +
padding + border — not estimated. Worked example from the audit: an
entry chip at `0.72rem × 1.6 + 2 × 0.05rem + 2 × 1px` = **22.0 CSS px**.

| Standard | Size | Where we apply it |
|---|---|---|
| SC 2.5.8 Target Size (Minimum), AA | 24×24 px | the floor. Nothing ships below it |
| SC 2.5.5 Target Size (Enhanced), AAA | 44×44 px | **primary navigation targets a reader hits repeatedly** — archive day cells, and any control of that kind added later |

The 44 px choice is not perfectionism; it is the switch-access,
head-pointer, and touch requirement. A target that is merely legal to
hit is not the same as one that is comfortable to hit forty times in a
row, and an archive is a surface a reader hits forty times in a row.

Where a narrow viewport forces a choice between the enhanced size and
horizontal scroll, **reflow wins and the size relaxes toward the AA
floor** — with the breakpoint and the resulting size stated in the CSS
comment. Horizontal scroll fails 1.4.10 for everyone; a 38 px target
still passes 2.5.8 comfortably.

---

## §5 The findings register

`docs/accessibility.md` holds the findings. Its rules:

- **Identifiers are permanent.** `A11Y-nn` is allocated once and never
  reused, never renumbered.
- **Nothing is ever deleted.** A resolved finding keeps its full text and
  gains a **Status:** line. Deleting it erases the evidence that we found
  it, which is the only evidence that the process works.
- **Every finding cites its success criterion** (or says explicitly that
  it is beyond baseline, as A11Y-08 does).
- **A finding is referenced from the code and the test** that address it,
  by identifier. `grep -rn A11Y-09` is expected to reach the doctrine,
  the finding, the CSS, and the test that pins it.
- **New page classes open findings proactively**, not only in response to
  an audit: GUIDE §2a rule 12 makes a register entry part of done.

---

## §6 Verification protocol

Three tiers, and **a claim earned at one tier is never reported as
another**.

**Tier 1 — automated, runs in CI.** `tests/test_accessibility.py` sweeps
every built page class and asserts the structural invariants: exactly
one `h1`; heading levels never skip; a skip link precedes main content;
no `<script>` on any page but the live page; no reference to any external
origin; every `<table>` has a caption or labelled region and scoped
headers; every external link is announced; no positive `tabindex`; a
forced-colors block is present; declared target sizes meet §4.2. These
are the invariants a future change is most likely to break silently, and
they are the reason doctrine is not decoration.

**Tier 2 — computed and inspected by a person or agent.** Contrast and
target arithmetic per §4. Accessible-name computation read against
HTML-AAM. Landmark and heading structure, tab order against DOM order,
the accessibility-tree consequences of a chosen hiding mechanism. This
is how the existing audit was performed and it is a real tier — it
catches things tier 1 cannot express — but it is inspection against the
specifications, and it is reported as exactly that.

**Tier 3 — real assistive technology.** Announcement, focus tracking
under magnification, voice-control naming, and switch navigation
confirmed against actual software. Performed when the equipment is
available. **Nothing verified at tiers 1–2 is ever described as tier-3
verified**, in this repository or on the site (GUIDE §2a rule 10).

Between tiers 2 and 3 the operating rule is the one the operator set on
2026-09-05: **design and implement against known-working methods, and
verify when able.** Preferring a native element to an invented one (§1)
is precisely how a project honors that — a real link needs no tier-3
pass to be trusted, because it is the thing every assistive technology
was built to handle.

---

## §7 Why the security posture is part of this document

GUIDE §2a rule 5 binds the access argument and the attack-surface
argument together. The engineering consequence, stated here so it is
actionable:

The site is static HTML with no framework, exactly one script, no form
that submits, no endpoint of our own, and no third-party asset —
no analytics, no hosted fonts, no CDN, no embedded player. Read as
access, that is: everything works with scripting off, in any browser, on
any connection, through any assistive technology, with nothing to learn
and no widget to misbehave. Read as security, it is: nothing to inject,
nothing to exploit, nothing given to leak, and no third party whose bad
day becomes ours.

**Therefore a proposal to add script, an endpoint, an input, or a
third-party asset is simultaneously an accessibility change and a
security change, and it goes to the operator as both.** Neither
justification may be spent to buy the other. In practice the question to
ask first is the ladder's: what rung actually fails here? In the archive
case the honest answer was "none — rung 1 does it," and that answer is
available far more often than the reflex to reach for a widget suggests.

---

## §8 Definition of done for a new page or surface

A checklist, and each line is a real gate:

- [ ] Rendered through `publish._render_page`, so the page-level
      affordances (skip link, nav, external-link announcement, canonical
      footer) apply without being re-implemented.
- [ ] Walked down §1's ladder; any rung skipped is commented at the skip.
- [ ] Walked across §2's modality table.
- [ ] Reuses §3's patterns where one exists.
- [ ] Contrast and target sizes computed per §4 and stated in the commit
      body.
- [ ] One `h1`; heading levels descend without skipping; a skip link
      ahead of any long run of controls.
- [ ] Every control's accessible name begins with its visible label.
- [ ] Nothing conveyed by color, shape, position, or `title` alone.
- [ ] Forced-colors behavior declared for any new control boundary or
      state marker.
- [ ] Reflows to a 320 px viewport with no horizontal page scroll.
- [ ] Pinned tests added to `tests/test_accessibility.py`, citing the
      criterion or the `A11Y-nn` identifier.
- [ ] A findings-register entry opened in `docs/accessibility.md`
      (GUIDE §2a rule 12).
- [ ] If the surface changes what a reader can do, `docs/site/
      accessibility.md` is reviewed for whether any claim on it is still
      true.

---

## §9 How this document changes

Method changes land **in the same commit** as the code that motivates
them, with a dated line below. Date-only bumps without content review
are forbidden (CLAUDE.md §8).

- 2026-09-05 — created under GUIDE §2a. Consolidates method that was
  previously implicit in `docs/accessibility.md` §1–§2 (a dated audit,
  which continues as the findings record), one bullet in
  `docs/agents/publication.md`, and the reasoning in the code comments.
  Written alongside the calendar archive, which is its first worked
  example: the design ladder, the modality table, and §4.1's
  `--border` / `--control-border` finding all come from that surface.

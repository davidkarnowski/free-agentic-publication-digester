# Accessibility audit and remediation plan

*Audit date: 2026-07-30. Audited surface: the live site at
https://fapd.info, as rendered by `src/fapd/publish.py`. Last reviewed:
2026-07-30.*

*Findings A11Y-21 and A11Y-22 were added 2026-09-05, found by
`tests/test_accessibility.py` on its first run and resolved the same
day; the 2026-07-30 status below describes the original audit pass and
is left as written.*

*Remediation status, 2026-07-30: 19 of 20 findings resolved across two
passes; A11Y-18 stays open because no fix exists at the current DOM
order. Each finding below carries its own **Status:** line — nothing was
deleted, because the audit is a record of what the site was, not a task
list. The public statement built from §6 is now a real page,
`docs/site/accessibility.md`, rewritten so every sentence is true after
the work landed, and it names what is still untested.*

*Scope note, 2026-09-05: this file is the **findings record** — what was
measured, when, and what happened to each finding. It is not the method.
GUIDE §2a (Universal Access) now states what we owe every reader, and
`docs/accessibility-doctrine.md` states how we comply — the design
ladder, the modality table, the pattern inventory, the measurement
procedure, and the verification tiers, several of which were first
written down here in §1, §2 and §4a. Findings continue to be recorded
here, identifiers are permanent, and nothing in this file is ever
deleted or retroactively rewritten.*

---

## 1. Why this matters here

FAPD publishes what the federal government published. A person who reads
with a screen reader, who navigates by keyboard or voice, who runs the
screen at 400%, or who cannot hold three filter states in working memory
has exactly the same claim on that record as anyone else. If the filter
on `/today` is unusable with a screen reader, the practical result is
that a blind reader gets a worse view of the day's Federal Register than
a sighted one — from a project whose whole argument is that the official
record should be easier to reach.

There is a second, narrower reason. GUIDE §1 commits this project to two
readerships, humans and AI agents, and the machine surfaces
(`today.json`, `digests.json`, `llms.txt`) are already careful about
labeling which text is official and which is model-generated. The HTML
surface is not yet as careful: today the "model-generated key" marker is
carried by a dashed border, an italic, and a `title` attribute, none of
which a screen reader reliably conveys. That is the same disclosure
failure the project refuses to make anywhere else, appearing in the
presentation layer.

WCAG 2.2 AA is the floor used below. Section 8 lists the places where
going past it is worth the cost and why.

---

## 2. Method

**Fetched 2026-07-30** with `curl`, and evaluated as served:

| URL | bytes | notes |
|---|---|---|
| `/today.html` | 402,056 | 291 items, 582 `li.today-item` entries in the DOM, 58 filter checkboxes, 925 `<label>` elements |
| `/2026-07-29.html` | 98,672 | 9 `<details>` sections, 4 tables, 12 `<th>`, 104 `.rule-id` tooltips |
| `/sources.html` | 175,465 | 127 `<details>`, h2→h3→h4 card hierarchy |
| `/index.html` | 4,008 | |
| `/about.html`, `/agents.html`, `/privacy.html` | 8,967 / 5,886 / 5,139 | |
| `/style.css` | 11,117 | matches `publish._STYLE` |

**Evaluated by computation.** All contrast ratios in §4 were computed
from the actual declared colors with the WCAG 2.x relative-luminance
formula, compositing `rgba()` chip tints over the resolved background
first, and compositing `opacity` over the composited chip background.
Both the light palette and the `prefers-color-scheme: dark` palette were
computed. Target sizes were computed from the declared `font-size`,
`line-height`, `padding`, and `border` (0.72rem × 1.6 + 2 × 0.05rem +
2 × 1px = 22.0 CSS px for an entry chip).

**Evaluated by inspection** against the specs, not by running an AT:
accessible-name computation (HTML-AAM step 2D, "concatenation of the
label texts in tree order"), landmark and heading structure, the
accessibility-tree consequences of `display: none` versus `opacity: 0`,
the `<details>` fragment-revealing algorithm, and the known
`display: block`-on-`<table>` semantics loss.

**What a static audit cannot settle, and who should settle it.** The
findings below are derived from markup and CSS. Three classes of
question need a human at a real assistive technology:

1. **The filter, end to end** — NVDA + Firefox and JAWS + Chrome on
   Windows, VoiceOver + Safari on macOS and iOS. Specifically: how long
   the concatenated accessible names in A11Y-01 actually take to speak;
   whether tabbing through 58 invisible checkboxes is merely tedious or
   is experienced as the page being broken; whether the checked state is
   announced on toggle.
2. **Whether a CSS-driven `role="status"` region announces at all.**
   Section 5's phase-2 proposal changes `display` on pre-rendered spans
   inside a live region. Chrome/NVDA generally announce a node that
   becomes displayed inside a live region; Safari/VoiceOver is
   inconsistent. This must be tested before it is claimed anywhere
   public.
3. **Magnification.** ZoomText or macOS Zoom at 400%, checking whether
   the focus indicator described in A11Y-18 (drawn on a chip in the bar
   while focus is on a 1px input at the top of the form) stays inside
   the magnified viewport.

Also worth a manual pass, cheap to run: Windows High Contrast
(A11Y-08), Dragon NaturallySpeaking voice control on the chips ("click
executive" needs the visible label to be in the accessible name —
A11Y-01's fix preserves this, see 2.5.3 note), and a full keyboard-only
traversal of `/today` and one digest page.

Nothing here was verified with an automated checker; automated checkers
would have caught roughly A11Y-05 and A11Y-09 and nothing else in this
list.

---

## 3. Findings

Twenty findings: **2 critical, 6 high, 6 medium, 6 low.** Each names the
success criterion, the exact site of the defect, the current code, and
the replacement.

A shared visually-hidden utility is used by several fixes. Add it once to
`publish._STYLE`, near the top with the other resets:

```css
.vh {
  position: absolute !important;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}
```

### A11Y-01 — Critical — 4.1.2 Name, Role, Value

**Status: resolved 2026-07-30** — `aria-label` on every `filter-cb`
input, as written. Pinned by `test_filter_checkboxes_name_themselves`.

**Where:** `publish._today_filter_bar` (the `<input class="filter-cb">`
line), `publish._filter_chip`, `publish._entry_tag_chip`.

Every filter checkbox is referenced by a `<label for="…">` in the filter
bar *and* by one `<label for="…">` on every stream entry carrying that
tag. Measured on the fetched page:

| input | `<label>` elements pointing at it |
|---|---|
| `f-executive` | 286 |
| `f-press-release` | 160 |
| `f-notice` | 99 |
| `f-justice-press-releases` | 44 |
| (58 inputs, 925 labels total) | |

Per HTML-AAM, a labelable element with more than one label takes as its
accessible name the **concatenation of all label texts in tree order**.
Chrome and Firefox both implement this. The computed accessible name of
`f-executive` is therefore approximately `"executive 285 executive
executive executive …"` — the word repeated 286 times, on the order of
2,600 characters. `f-press-release` is about 2,200. There is no way for a
screen-reader user to tell what any of the 58 checkboxes does, and no way
to stop the announcement short of leaving the control.

The `<label>`-for-the-same-input design is otherwise good and should be
kept: it is what makes a tag on an entry and a chip in the bar the same
act with no duplicated state. The fix is to override the name, not to
break the links.

**Current:**

```python
inputs.append(f'<input type="checkbox" class="filter-cb" id="f-{slug}">')
```

**Replacement** (in the `for tag, _n in offered:` loop — rename `_n` to
`n` so the count is usable):

```python
for tag, n in offered:
    slug = _slug(tag)
    inputs.append(
        f'<input type="checkbox" class="filter-cb" id="f-{slug}"'
        f' aria-label="Filter to {html.escape(tag, quote=True)}'
        f' — {n} item(s)">')
```

`aria-label` is consulted before `<label>` elements in the accessible
name computation, so this replaces the 2,600-character name outright with
`"Filter to executive — 285 item(s)"`. No markup restructuring, no
script.

*2.5.3 Label in Name check:* the visible label reads `executive 285`;
the accessible name contains `executive` then `285` in that order, so
voice control ("click executive") continues to work.

*Deliberately not used:* `aria-describedby` pointing at the instructions
text. It would be correct in isolation but would re-speak the full
instruction sentence on each of 58 focus events.

### A11Y-02 — Critical — 2.4.1 Bypass Blocks

**Status: resolved 2026-07-30** — skip link in `_PAGE`, `id`/`tabindex`
on `<main>`, `.skip-link` CSS, and the in-page skip on `/today`. Its
target moved to the stream's own `<h2>` when A11Y-13 landed. Pinned by
`test_every_page_class_has_a_skip_link_and_main_landmark`.

**Where:** `publish._PAGE`; `publish.build_today`.

There is no skip link anywhere on the site (confirmed: no `.skip-link`,
no `href="#main"`, `<main>` has no `id`). Every page repeats the header
nav before content. On `/today` the situation is materially worse: a
keyboard user reaching the page must pass the header nav and then **58
invisible checkboxes**, in a row, with nothing but a chip outline in the
filter bar to indicate where they are, before reaching the first item of
the stream.

**Replacement — `_PAGE`,** two edits:

```html
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <nav aria-label="Site">
```

```html
<main id="main" tabindex="-1">
```

**Replacement — `_STYLE`,** new block:

```css
.skip-link {
  position: absolute; left: -9999px; top: 0; z-index: 10;
  padding: 0.5rem 0.9rem;
  background: var(--card); color: var(--accent);
  border: 2px solid var(--accent); border-radius: 0 0 6px 0;
  font-size: 0.95rem; text-decoration: none;
}
.skip-link:focus { left: 0; }
```

**Replacement — `build_today`,** a second, in-page skip immediately
before the `<form …>` append, plus the heading it targets (see A11Y-13
for the heading itself):

```python
parts.append(
    f'<a class="skip-link" href="#today-stream">'
    f'Skip {len(facets)} keyword filters and go to the stream</a>')
```

`#today-stream` is a general sibling of the checkboxes, so the existing
`#f-x:checked ~ .today-list` selectors are unaffected.

### A11Y-03 — High — 1.3.1 Info and Relationships; 2.1.1 Keyboard

**Status: resolved 2026-07-30** — `_accessible_tables` added and called
from `_style_digest_body` between the Contents strip and
`_collapse_sections`, so the `_compact_meta` ordering constraint holds.
One departure from the replacement above, deliberate: the `<th>` pattern
is `<th(?=[\s>])` rather than `<th>`, so an aligned column (`<th
align="left">`, which the tables extension emits for `|:---|`) also gets
`scope`. Verified on the real 2026-07-29 page: 4 tables, 4 wrappers, 12
`<th scope="col">`, 0 bare `<th>`, and every `aria-labelledby` resolves
to an id that exists. Pinned by
`test_digest_tables_keep_their_semantics`.

**Where:** `publish._STYLE` `table { … }`; `publish._style_digest_body`.

```css
table {
  display: block;
  overflow-x: auto;
  ...
}
```

`display: block` on a `<table>` removes the table role and the row and
cell roles from the accessibility tree in Chrome and Firefox. The four
tables on a digest page — the bill-stage counts, the Federal Register
document-type counts, and so on — are announced as a flat run of text.
The header/data relationship is gone, which for a counts table means the
numbers lose their labels entirely.

Additionally: the 12 `<th>` elements carry no `scope`, there are no
`<caption>` elements, and the horizontal scroll container created by
`overflow-x: auto` is not keyboard-focusable, so a keyboard-only user
cannot scroll a wide table.

**Replacement — `_STYLE`:**

```css
table {
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.92rem;
}
.table-scroll { overflow-x: auto; margin: 1rem 0; }
.table-scroll:focus-visible {
  outline: 3px solid var(--accent); outline-offset: 2px;
}
```

**Replacement — `publish.py`,** new helper, called from
`_style_digest_body` before `_collapse_sections`:

```python
_TABLE_EL_RE = re.compile(r"<table>(.*?)</table>", re.DOTALL)
_TH_RE = re.compile(r"<th>")
_HEAD_ID_RE = re.compile(r'<h[23] id="([^"]+)"')


def _accessible_tables(html_body):
    """Tables keep their semantics: the scroll container moves to a
    wrapper (display:block on a <table> strips its roles from the
    accessibility tree), header cells get scope, and the wrapper is a
    focusable labelled region so keyboard users can scroll it."""
    out, pos = [], 0
    for match in _TABLE_EL_RE.finditer(html_body):
        out.append(html_body[pos:match.start()])
        heads = _HEAD_ID_RE.findall(html_body[:match.start()])
        label = (f' aria-labelledby="{heads[-1]}"' if heads
                 else ' aria-label="Data table"')
        inner = _TH_RE.sub('<th scope="col">', match.group(1))
        out.append(f'<div class="table-scroll" role="region" tabindex="0"'
                   f'{label}><table>{inner}</table></div>')
        pos = match.end()
    out.append(html_body[pos:])
    return "".join(out)
```

Note the ordering constraint: `_compact_meta` matches
`<table>.*?Digest date.*?</table>` and must run **before** this helper,
which it already does.

### A11Y-04 — High — 1.3.1 Info and Relationships; 2.4.6 Headings and Labels

**Status: resolved 2026-07-30** — heading moved into `<summary>` with
the anchor id, `<details>` id dropped, `.sec-heading` removed from
markup and stylesheet. The anchor strings are byte-identical to before,
checked against the built 2026-07-29 page. One defect in the replacement
as written: `_STYLE` is not a raw string, so `content: "\25B8\00a0"`
pasted literally becomes a Python **octal** escape (`\25` -> `\x15`) and
ships broken CSS. The backslashes must be doubled in the source. Pinned
by `test_every_digest_heading_is_exposed_and_deep_links_resolve` and
`test_generated_glyphs_are_not_spoken`.

**Where:** `publish._collapse_sections`.

Each collapsible section renders as:

```html
<details class="digest-section" id="2-legislation">
  <summary><span class="sec-title">2. Legislation</span>…</summary>
  <h2 class="sec-heading">2. Legislation</h2>
  …
</details>
```

No `<details>` is emitted `open`, so the `<h2>` and every `<h3>`/`<h4>`
beneath it are outside the accessibility tree on page load. A screen
reader user pulling up the heading list for `/2026-07-29.html` sees
**two** headings — `Daily Digest — 2026-07-29` and `Day in Review` — for
a document that contains 25. Heading navigation, which is how most screen
reader users move through a long document, does not work on the digest
pages.

The same markup breaks deep links: the anchor id is on the `<details>`
itself, and the fragment-revealing algorithm opens `<details>` ancestors
*of* the target, not the target. `/2026-07-29.html#2-legislation`
therefore scrolls to a collapsed section.

Both are fixed by one change: put the heading inside the `<summary>` and
move the anchor id onto it. `<summary>`'s content model permits heading
content, and this is the documented accessible-disclosure pattern.

**Current:**

```python
summary = f'<span class="sec-title">{title}</span>'
...
out.append(
    f'<details class="digest-section" id="{anchor}">'
    f"<summary>{summary}</summary>"
    f'<h2 class="sec-heading">{title}</h2>{body}</details>')
```

**Replacement:**

```python
summary = f'<h2 class="sec-title" id="{anchor}">{title}</h2>'
...
out.append(
    f'<details class="digest-section">'
    f"<summary>{summary}</summary>{body}</details>")
```

**Replacement — `_STYLE`,** replacing the `.sec-title` and
`.sec-heading` rules:

```css
h2.sec-title {
  font-size: 1.05rem; font-weight: 650;
  margin: 0; padding: 0; border: 0; color: inherit;
}
h2.sec-title::before { content: "\25B8\00a0" / ""; color: var(--accent);
  font-size: 0.85em; }
details.digest-section[open] h2.sec-title::before {
  content: "\25BE\00a0" / "";
}
```

The `/ ""` is CSS alternative text on generated content (see A11Y-15) —
the triangle stays visible and is no longer spoken. The anchor id keeps
its exact current string, so existing deep links are unchanged in form
and now open the section they point at.

### A11Y-05 — High — 1.4.3 Contrast (Minimum)

**Status: resolved 2026-07-30** — `--accent-on`, the darkened
light-theme branch hues, and the `:checked` rule landed in an earlier
pass; the `.filter-n` half (dropping `opacity: 0.7`) was missing and
landed here. Pinned by `test_selection_is_not_signalled_by_colour_alone`
and `test_chips_meet_the_target_size_and_boundary_floors`.

**Where:** `publish._STYLE` — the branch-color block, the
`prefers-color-scheme: dark` block, `.filter-n`, and the generated
`:checked` rule in `_today_filter_bar`.

All chip text is 0.72rem (11.52 px) — normal text, so the threshold is
4.5:1. Measured:

**Light theme, chip text on the tinted chip background:**

| Selector | Colors | Ratio | |
|---|---|---|---|
| `.tag-branch-executive` | `#0f9488` on tint over `#f4f6f8` | **2.95:1** | fail |
| `.tag-branch-judicial` | `#c07207` on tint | **2.97:1** | fail |
| `.tag-branch-legislative` | `#5a5fd0` on tint | **4.11:1** | fail |
| `.tag-branch-cross` | `#57606a` on tint | 4.99:1 | pass |
| `.tag` (plain) | `#57606a` on `#f4f6f8` | 5.90:1 | pass |

**`.filter-n` (the count) — `opacity: 0.7` applied over the chip:**

| Chip | Light | Dark |
|---|---|---|
| executive | **2.11:1** | 4.57:1 |
| judicial | **2.11:1** | 4.96:1 |
| legislative | **2.55:1** | **3.78:1** |
| cross-branch | **2.82:1** | **3.62:1** |
| plain | **3.10:1** | **3.98:1** |
| selected | 5.18:1 | **1.79:1** |

**Dark theme, the selected state** (generated CSS,
`{background:var(--accent);color:#fff}`):

| | Colors | Ratio | |
|---|---|---|---|
| `:checked` chip | `#ffffff` on `#7ab3e0` | **2.25:1** | fail |
| (light equivalent) | `#ffffff` on `#1f4e79` | 8.66:1 | pass |

The dark-theme selected chip is the worst single number on the site, and
it is on the one element that tells a reader which filters are active.

Everything else measured passes, several comfortably: body text
16.27:1 / 15.18:1, links 8.51:1 / 8.24:1, `--muted` on `--bg`
6.28:1 / 7.31:1, `.plain-label` 7.47:1 / 6.77:1, nav links on the header
band 5.51:1 / 6.01:1, `th` on `--accent-soft` 14.28:1 / 12.47:1.

**Replacement — `_STYLE`,** new tokens:

```css
:root {
  ...
  --accent-on: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root {
    ...
    --accent-on: #0b1116;
  }
}
```

`#0b1116` on `#7ab3e0` measures **8.46:1**; `#ffffff` on `#1f4e79` stays
8.66:1.

**Replacement — `_STYLE`,** the branch block (light values only; the
dark overrides already pass and are unchanged):

```css
.tag-branch-legislative {
  background: rgba(99, 102, 241, 0.14); color: #4448b8;
  border-color: currentColor;
}
.tag-branch-executive {
  background: rgba(13, 148, 136, 0.14); color: #0b6b62;
  border-color: currentColor;
}
.tag-branch-judicial {
  background: rgba(217, 119, 6, 0.14); color: #8a5206;
  border-color: currentColor;
}
.tag-branch-cross {
  background: rgba(107, 114, 128, 0.14);
  border-color: currentColor;
}
```

Measured after the change: legislative **5.71:1**, executive **5.02:1**,
judicial **5.11:1**, cross 4.99:1. The hues are darkened, not changed —
they remain outside the red/blue party palette that `_BRANCH_CHIP_CLASSES`
deliberately avoids. `border-color: currentColor` also resolves A11Y-10.

**Replacement — `_STYLE`,** `.filter-n`:

```css
.filter-n {
  margin-left: 0.4rem; font-weight: 600;
  font-variant-numeric: tabular-nums;
}
```

Dropping `opacity` makes the count inherit the chip's (now compliant)
text color.

**Replacement — `_today_filter_bar`,** generated CSS, the `:checked`
line:

```python
f'#f-{slug}:checked ~ .filter-bar label[for="f-{slug}"],\n'
f'#f-{slug}:checked ~ .today-list label[for="f-{slug}"]'
"{background:var(--accent);color:var(--accent-on);"
"border-color:var(--accent)}\n"
```

### A11Y-06 — High — 1.4.1 Use of Color

**Status: resolved 2026-07-30** — check-mark glyph generated per
keyword, in the bar and on every entry. Pinned by
`test_selection_is_not_signalled_by_colour_alone`.

**Where:** the generated `:checked` rule in `publish._today_filter_bar`.

Which keywords are currently selected is conveyed **only** by a
background-color change (accent fill, inverted text). There is no shape,
glyph, weight, or border-style difference. A reader with a color vision
deficiency, or one whose display is grayscale or in forced colors
(A11Y-08), cannot tell which of 58 chips are on. On a page where
filtering changes what is shown, that is a correctness problem, not only
a cosmetic one: the reader may believe they are seeing the whole day.

**Replacement — `_today_filter_bar`,** one additional generated rule per
keyword:

```python
f'#f-{slug}:checked ~ .filter-bar label[for="f-{slug}"]::before,\n'
f'#f-{slug}:checked ~ .today-list label[for="f-{slug}"]::before'
'{content:"\\2713\\00a0"}\n'
```

A check mark plus a non-breaking space is prepended to every instance of
a selected chip, in the bar and on every entry. This glyph also survives
forced-colors mode (A11Y-08), which the background fill does not.

*No CSS alternative text here, deliberately.* A11Y-15 uses the
`content: "…" / ""` form to silence a decorative triangle; this glyph is
not decorative, and the `/ ""` syntax reached Firefox only in late 2024,
so a browser without it would drop the whole declaration and lose the
one non-colour signal of selection. A screen reader speaking "check mark
executive" beside an already-checked control is redundant, not wrong.

### A11Y-07 — High — 4.1.3 Status Messages

**Status: resolved 2026-07-30, with its limit stated publicly** — both
(a) and (b) shipped: one `.fs-<slug>` span per keyword inside a
`role="status"` region, revealed by a generated `:has()` rule, and the
`.filter-count` CSS counter after the list. This uses `:has()` for the
readout only; the `:has()` restructure of the filter itself (§5) was NOT
done. Whether the region announces is untested, and
`docs/site/accessibility.md` says so in those words rather than claiming
it. Pinned by `test_today_filter_states_what_is_selected`, which also
asserts the page still ships exactly one script.

**Where:** `publish.build_today` / `publish._today_filter_bar`.

Selecting a keyword changes what is visible — from 291 items to 6, in one
case measured on the fetched page — and nothing announces it, and nothing
states it visually either. The bar states `291 item(s) unfiltered`, which
is the *before* number and never changes. A sighted reader can see the
list shorten; a screen reader user gets silence, and a magnification user
looking at the bar sees nothing change at all.

There is no fully script-free way to compute and announce an intersection
count. There are two useful partial answers, both pure CSS.

**(a) Which filters are active — announceable, linear in keyword count.**
Pre-render one span per keyword inside a live region in the filter bar,
all hidden, each revealed by its own checkbox:

```html
<p class="filter-status" role="status">
  <span class="fs-none">No keyword filter is selected; all 291 items are
    shown.</span>
  <span class="fs-lead">Filtered to items tagged: </span>
  <span class="fs-executive">executive </span>
  <span class="fs-notice">notice </span>
  <!-- one per offered keyword -->
</p>
```

```css
.filter-status { margin: 0.4rem 0 0; font-size: 0.8rem; color: var(--muted); }
.filter-status > span { display: none; }
.today-stream:not(:has(.filter-cb:checked)) .fs-none { display: inline; }
.today-stream:has(.filter-cb:checked) .fs-lead { display: inline; }
```

plus, generated per keyword:

```css
.today-stream:has(#f-executive:checked) .fs-executive { display: inline; }
```

**(b) The exact number shown — visible, not reliably announced.** CSS
counters do not increment for elements with `display: none`, and counter
scope extends to an element's following siblings. So a counter reset on
the list and incremented per item can be read out by an element placed
after the list:

```css
.today-list { counter-reset: shown 0; }
.today-list > .today-item { counter-increment: shown; }
.filter-count::after { content: counter(shown) " item(s) shown."; }
```

with `<p class="filter-count"></p>` appended as the last child of the
form, after `</ul>`.

**Honest limits.** (a) depends on `:has()` (Baseline since December
2023); browsers without it show `.fs-none` never and the readout is
simply absent, which is a safe degradation. Whether a `role="status"`
region announces a child that changes from `display: none` to
`display: inline` is browser-and-AT dependent — Chrome/NVDA generally
does, Safari/VoiceOver is unreliable — and **must be tested before this
is claimed on the public accessibility page**. (b) uses generated
content, which most screen readers read inconsistently and which cannot
be selected or copied; treat it as a visual improvement only.

Announcing the exact intersection count reliably requires script. That is
sketched, with its §2-rule-10 justification, in §7.

### A11Y-08 — High — beyond baseline (supports 1.4.1, 1.4.11)

**Status: resolved 2026-07-30** — the full `forced-colors` block
replaced the two-rule placeholder that was already there; the
placeholder's `:checked ~ label { border-width: 3px }` was kept
alongside it. Pinned by
`test_focus_and_forced_colors_have_author_answers`.

**Where:** `publish._STYLE` — no `@media (forced-colors: active)` block
exists.

In Windows High Contrast / forced-colors mode the user agent replaces
author colors with a small system palette. Consequences here: every chip
tint collapses to `Canvas`, so branch color disappears (acceptable — the
chip text names the branch, A11Y verified); the `.tag` border at
`var(--border)` is forced to `CanvasText` (an improvement); and the
`:checked` accent fill is forced away entirely, so **which filters are
selected becomes invisible**. `.live-dot` is a background-color-only
element and vanishes. `.today-disclosure`'s left rule survives; its main
border is already broken for a different reason (A11Y-20).

**Replacement — `_STYLE`,** new block at the end:

```css
@media (forced-colors: active) {
  .tag { border: 1px solid CanvasText; }
  .filter-chip, .chip-toggle { border: 1px solid ButtonBorder; }
  .live-dot { outline: 1px solid CanvasText; }
  .skip-link { border: 2px solid CanvasText; }
  .plain { border-left: 3px solid Highlight; }
  .today-disclosure { border: 1px solid CanvasText; }
  a:focus-visible, button:focus-visible, .table-scroll:focus-visible,
  summary:focus-visible { outline: 3px solid Highlight; outline-offset: 2px; }
}
```

The check-mark glyph from A11Y-06 is what carries the selected state in
this mode; it is real content, not a color, so it survives. That is the
reason to land A11Y-06 and A11Y-08 together.

### A11Y-09 — Medium — 2.5.8 Target Size (Minimum)

**Status: resolved 2026-07-30** — the vertical padding landed together
with A11Y-10's `--control-border`, in one rule placed **before** the
branch block. That placement is load-bearing: equal specificity, so had
the rule stayed in the filter section it would have come later in source
order and overridden the branch chips' `currentColor` border, silently
undoing A11Y-10. Pinned by
`test_chips_meet_the_target_size_and_boundary_floors`, including the
ordering.

**Where:** `publish._STYLE` `.tag`, `.filter-chip`, `.chip-toggle`.

Computed heights, from `font-size: 0.72rem` (11.52 px), the inherited
`line-height`, `padding: 0.05rem`, and `border: 1px`:

| Chip | line-height | height | 2.5.8 |
|---|---|---|---|
| `.filter-chip` in `.filter-row` | 2.1 | 27.8 px | pass |
| `.chip-toggle` in `.today-chips` | 1.6 (body) | **22.0 px** | fail |

The entry chips — the ones a reader taps while reading an item, the more
natural place to filter from — are the ones that fail. Chips are adjacent
(`margin-right: 0.25rem` = 4 px), so the spacing exception does not
rescue them either.

**Replacement — `_STYLE`,** amending the existing rule:

```css
.filter-chip, .chip-toggle {
  cursor: pointer; user-select: none;
  padding-top: 0.3rem; padding-bottom: 0.3rem;
}
```

Computed height becomes 11.52 × 1.6 + 2 × 4.8 + 2 = **30.0 px**. Width is
already ≥ 24 px for any non-empty keyword (2 × 0.55rem padding + 2 px
border = 19.6 px before a single glyph). Chips are atomic inline-level
boxes, so the line box grows to contain them and no vertical overlap is
introduced; no `line-height` change is needed.

### A11Y-10 — Medium — 1.4.11 Non-text Contrast

**Status: resolved 2026-07-30** — `border-color: currentColor` on the
branch chips came with A11Y-05 in an earlier pass; the
`--control-border` token for plain chips was missing and landed here, so
the finding is now resolved in full. `--border` on cards and table cells
is left alone, as the finding says.

**Where:** `publish._STYLE` — `--border`, the branch `border-color`
values.

The filter chips are user interface components, so the visual boundary
that identifies them needs 3:1. Measured against the page background:

| Border | Light | Dark |
|---|---|---|
| `.tag-branch-judicial` `rgba(217,119,6,.55)` | **1.84:1** | **2.55:1** |
| `.tag-branch-executive` `rgba(13,148,136,.55)` | **1.99:1** | **2.32:1** |
| `.tag-branch-legislative` `rgba(99,102,241,.55)` | **2.12:1** | **2.08:1** |
| `.tag-branch-cross` `rgba(107,114,128,.55)` | **2.12:1** | **2.00:1** |
| `--border` (plain chips, cards, table cells) | **1.34:1** | **1.47:1** |

The `border-color: currentColor` change in A11Y-05 lifts the four branch
borders to 7.20 / 6.26 / 6.27 / 6.28:1 (light) and 7.74 / 9.94 / 11.08 /
7.31:1 (dark). It is a visibly heavier border than today's tint; that is
the tradeoff and it is worth stating to the operator explicitly.

Plain (non-branch) filter chips still need a control boundary. Add a
dedicated token, and **place this rule before the branch-color block** so
the branch rules' `currentColor` wins for branch chips:

```css
:root { --control-border: #868f99; }
@media (prefers-color-scheme: dark) {
  :root { --control-border: #646f7a; }
}
.filter-chip, .chip-toggle { border-color: var(--control-border); }
```

Measured: light 3.22:1 vs `--bg`, 3.03:1 vs `--stripe`; dark 3.61:1 and
3.31:1.

`--border` on cards and table cells is left alone: those are decorative
container edges, not component boundaries, and 1.4.11 does not reach
them. Raising it is a §8 item, not a conformance one.

### A11Y-11 — Medium — 1.3.1 Info and Relationships

**Status: resolved 2026-07-30** — both halves, as written. The verbosity
is real (104 extra spoken phrases on the audited page) and is named as a
known limitation on the public statement rather than assumed acceptable;
manual test 1 in §2 still owes an answer.

**Where:** `publish._tag_chip` (`title=`), `publish._style_digest_body._rule`
(`.rule-id` `title=`).

Two pieces of load-bearing information exist only in `title` attributes,
which are unavailable to keyboard users, unavailable on touch, and
announced inconsistently by screen readers:

1. **The model-generated marker.** `<span class="tag tag-model"
   title="model-generated key">congressional stock ban</span>`. Visually
   the distinction is a dashed border plus italics. GUIDE §2 requires
   model-generated text to be labeled in place; on this surface, for a
   screen reader user, it currently is not.
2. **The inclusion-rule description.** 104 instances on the audited
   digest page: `<span class="rule-id" title="floor item ≥ threshold
   floor time (66,363 characters)">CREC-SEL-01</span>`. The reason an
   item was selected — the project's core accountability claim — is a
   pointer-only tooltip.

**Replacement — `_tag_chip`:**

```python
def _tag_chip(text, extra_class="", title=""):
    classes = _tag_classes(text, extra_class)
    title_attr = f' title="{html.escape(title)}"' if title else ""
    note = f'<span class="vh"> ({html.escape(title)})</span>' if title else ""
    return (f'<span class="{classes}"{title_attr}>'
            f"{html.escape(text)}{note}</span>")
```

**Replacement — `_style_digest_body._rule`:**

```python
def _rule(match):
    rule_id, desc = match.group(1), match.group(2)
    title = html.escape(re.sub(r"<[^>]+>", "", desc), quote=True)
    return (f'<li class="rule-note">Included because: '
            f'<span class="rule-id" title="{title}">{rule_id}'
            f'<span class="vh"> — {title}</span></span></li>')
```

This restores the description that the compaction removed, for
assistive-technology readers only; the visible page is unchanged and the
canonical Markdown was never touched. It is verbose — 104 extra spoken
phrases on a digest page — which is why it belongs in phase 2 with a
manual listen, not in phase 1.

### A11Y-12 — Medium — 3.2.5 Change on Request (technique G201)

**Status: resolved 2026-07-30** — `_A_TAG_RE` widened to the whole
element and the notice appended inside it. Enforcement stays in the
single point named by code-standards §2 rule 9, so that rule is
preserved and needs no amendment. Pinned by
`test_outbound_links_say_they_open_a_new_tab`, which also asserts the
notice count equals the `target="_blank"` count — no notice on a link
that does not open a tab.

**Where:** `publish._externalize_links`.

Every outbound link sitewide carries `target="_blank"` with no warning.
On `/today` that is 582 links; on a digest page, every citation. Opening
a new tab without notice is disorienting for screen reader users (focus
context changes with no announcement), for magnification users (the
viewport contents change wholesale), and for anyone whose Back button
stops working.

`_externalize_links` currently rewrites only the opening tag, so the
notice cannot be appended where convention puts it. Widening the pattern
to the whole element is safe — `<a>` cannot nest.

**Current:**

```python
_A_TAG_RE = re.compile(r"<a\b([^>]*)>", re.IGNORECASE)
...
return f'<a{attrs} target="_blank" rel="noopener noreferrer">'
```

**Replacement:**

```python
_A_TAG_RE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.IGNORECASE | re.DOTALL)
...
    def _sub(match):
        attrs, inner = match.group(1), match.group(2)
        ...
        return (f'<a{attrs} target="_blank" rel="noopener noreferrer">'
                f'{inner}<span class="vh"> (opens in a new tab)</span></a>')
```

Every early `return match.group(0)` path is unchanged and now correctly
returns the whole element.

**The tradeoff, stated plainly.** This adds five spoken words to each of
582 links on `/today`. The alternative — one page-level sentence, no
per-link notice — is quieter but does not satisfy G201 and leaves a
reader who arrives at a single link by heading or link navigation with no
warning. The recommendation is the per-link text sitewide, with the
verbosity question put to a real screen-reader session (§2, manual test
1) before it is called settled.

### A11Y-13 — Medium — 1.3.1 Info and Relationships; 2.4.6 Headings and Labels

**Status: resolved 2026-07-30** — all three. The `<nav>` became a
labelled `role="group"`, the lead became `h2.filter-lead`, and the
stream got `<h2 id="today-stream">Observed publications</h2>` — which
also takes over the skip-link target from the `<ul>`. One departure: the
replacement's `bar` string shortens the instruction text; the current,
longer wording (narrowing behaviour, counts-are-unfiltered) was kept,
since dropping it was not part of the finding. Pinned by
`test_filter_bar_is_a_labelled_group_with_headings`.

**Where:** `publish.build_today`, `publish._today_filter_bar`,
`publish._PAGE`.

Three structural problems on `/today`:

1. **One heading on a 402 KB page.** `<h1>Today — 2026-07-30 (in
   progress)</h1>` and nothing else. There is no way to jump to the
   filter or to the stream by heading.
2. **The filter bar is a `<nav>` landmark.** `<nav class="filter-bar"
   aria-label="Filter the stream by keyword">` puts a 58-control form
   group into the landmark list and into the screen reader's list of
   navigation regions, where it is not navigation.
3. **The site header `<nav>` has no accessible name**, so a page with two
   nav landmarks offers one named and one unnamed. (The `aria-label="Site"`
   in A11Y-02's `_PAGE` patch fixes this one.)

**Replacement — `_today_filter_bar`,** the `bar` string:

```python
bar = (
    '<div class="filter-bar" role="group"'
    ' aria-labelledby="filter-heading">'
    '<h2 class="filter-lead" id="filter-heading">Filter by keyword '
    '<span class="rule-note">click to select, click again to clear — '
    "here or on any entry's own tags · choosing several narrows to "
    "items carrying all of them · "
    f"{total} item(s) unfiltered</span>"
    '<button type="reset" class="filter-clear">clear filters</button></h2>'
    f"{rows}{note}</div>"
)
```

`<button>` is phrasing content, so it is valid inside `<h2>`. The
generated per-keyword CSS already targets `.filter-bar` by class, not by
element, so nothing there changes.

**Replacement — `build_today`,** a heading before the stream (inside the
form, as a general sibling of the checkboxes):

```python
parts.append(
    '<form class="today-stream" action="today.html" method="get">'
    + inputs + filter_bar
    + '<h2 id="today-stream" tabindex="-1">Observed publications</h2>'
    + '<ul class="today-list">'
    + "".join(_today_item_row(i, filterable) for i in status["items"])
    + "</ul></form>")
```

**Replacement — `_STYLE`,** so the repurposed element keeps its look:

```css
h2.filter-lead {
  margin: 0 0 0.45rem; padding: 0; border: 0;
  font-size: 0.85rem; font-weight: 600; color: inherit;
}
```

Entry titles are deliberately left as `<strong>` rather than becoming 582
headings: the stream is a `<ul>`, screen readers announce "list, 582
items" and support item-to-item navigation, and 582 headings would make
the heading list useless.

### A11Y-14 — Medium — 1.3.1 Info and Relationships

**Status: resolved 2026-07-30** — both, as written, except that
`_filter_chip` keeps its `pairs` parameter and the `c-<slug>` partner
classes that the replacement's signature omitted. Pinned by
`test_times_and_counts_carry_their_units`.

**Where:** `publish._today_item_row` (`<time>`), `publish._filter_chip`
(`.filter-n`).

`<time class="utc" datetime="2026-07-31T00:28:23Z">20:28:23 ET</time>`
is spoken as a bare number sequence followed by two letters, with no
statement of what the number is. Nothing on the page says these are
observation times rather than publication times — the distinction the
project cares about most (CLAUDE.md §9: "Publication days are Eastern,
observation stamps are UTC"). Similarly, a chip reading `executive 285`
is spoken as "executive 285" with no unit.

**Replacement — `_today_item_row`:**

```python
observed = (f'<time class="utc" datetime="{html.escape(stamp)}">'
            f'<span class="vh">Observed at </span>'
            f"{html.escape(_et_clock(stamp))}"
            f'<span class="vh"> Eastern time</span>'
            f'<span aria-hidden="true"> ET</span></time>'
            if stamp else "")
```

**Replacement — `_filter_chip`:**

```python
def _filter_chip(tag, count):
    return (f'<label class="{_tag_classes(tag, "filter-chip")}" '
            f'for="f-{_slug(tag)}">{html.escape(tag)}'
            f'<span class="filter-n"><span class="vh">, </span>{count}'
            f'<span class="vh"> items</span></span></label>')
```

### A11Y-15 — Low — 1.1.1 Non-text Content

**Status: resolved 2026-07-30** — see the escaping defect noted under
A11Y-04. The check glyph deliberately keeps no alternative text, and a
test asserts it stays that way.

**Where:** `publish._STYLE` — `.sec-title::before`, `.plain-label::after`.

```css
.sec-title::before { content: "▸ "; … }
details.digest-section[open] .sec-title::before { content: "▾ "; }
.plain-label::after { content: ":"; }
```

CSS generated content is exposed to the accessibility tree in Chrome and
Safari. `▸` is announced as "black right-pointing small triangle" by some
screen readers, before every section title on a digest page. The colon is
harmless but equally unnecessary.

**Replacement:** use CSS alternative text, which is supported in all
current engines. The `.sec-title` rules are already restated in A11Y-04;
additionally:

```css
.plain-label::after { content: ":" / ""; }
```

### A11Y-16 — Low — 2.4.4 Link Purpose (In Context)

**Status: resolved 2026-07-30** — both, as written. Pinned by
`test_link_purpose_is_stated_for_bare_date_links`, which walks every
dated link on `/today` rather than spot-checking one.

**Where:** `publish._nav_for`, `publish.build_today` (`recent_links`).

Prev/next digest links read `← 2026-07-28`; the "most recent" list on
`/today` reads `2026-07-29 · 2026-07-28 · 2026-07-25`. Out of context —
which is how a screen reader's link list presents them — these are bare
dates.

**Replacement — `_nav_for`:**

```python
if i > 0:
    links.append(f'<a href="{dates[i - 1]}.html">&larr; '
                 f'<span class="vh">Digest for </span>{dates[i - 1]}</a>')
if i < len(dates) - 1:
    links.append(f'<a href="{dates[i + 1]}.html">'
                 f'<span class="vh">Digest for </span>{dates[i + 1]}'
                 f" &rarr;</a>")
```

**Replacement — `build_today`:**

```python
recent_links = " · ".join(
    f'<a href="{d}.html"><span class="vh">Digest for </span>{d}</a>'
    for d in recent)
```

### A11Y-17 — Low — 2.4.7 Focus Visible; 2.4.13 Focus Appearance (AAA)

**Status: resolved 2026-07-30** — as written. Pinned by
`test_focus_and_forced_colors_have_author_answers`.

**Where:** `publish._STYLE`.

The only author-defined focus style on the site is the generated
`#f-slug:focus-visible ~ .filter-bar label[…]` rule. Everything else —
every link, the `<summary>` disclosure buttons (9 per digest page, 127
per sources page), the reset button — relies on the user agent's default
ring, whose contrast against `--accent-soft` and `--card` is not under
the project's control and which some platform themes render thinly.

**Replacement — `_STYLE`:**

```css
:where(a, button, summary, [tabindex]):focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}
```

`var(--accent)` measures 8.51:1 against `--bg` and 8.00:1 against
`--stripe` (light), 8.24:1 and 7.56:1 (dark) — well past the 3:1 that
1.4.11 requires of a focus indicator, and a 3 px outline satisfies the
2.4.13 area test. `:where()` keeps specificity at zero so nothing
existing is overridden.

### A11Y-18 — Low — 2.4.7 Focus Visible (magnification behavior)

**Status: open 2026-07-30 — no fix exists at this DOM order**, exactly
as the finding says. It is named on the public statement as a known
limitation. Closing it needs the `:has()` restructure (§5), which is an
operator decision and was explicitly out of scope for this pass.

**Where:** `publish._STYLE` `.filter-cb`; `publish._today_filter_bar`.

```css
.filter-cb {
  position: absolute; width: 1px; height: 1px;
  opacity: 0; pointer-events: none;
}
```

This is a correct hiding technique for the goal — `opacity: 0` (unlike
`visibility: hidden` or `display: none`) keeps the checkbox in the
accessibility tree and in the tab order, which is exactly what the design
needs, and the comment in the source says so. But the browser scrolls the
*focused* element into view, and the focused element is a 1 px box at the
top of the form, while the visible indicator is drawn on a chip that may
be several rows lower. At 400% magnification the two can be in different
viewports, so a magnification user tabbing the filter sees no indicator
at all.

There is no CSS fix that keeps the current DOM order. The structural fix
in phase 2 (§6) removes the problem by moving each input to sit
immediately before its own chip. Until then this is a known limitation
and belongs on the public statement.

### A11Y-19 — Low — public claim accuracy

**Status: resolved 2026-07-30** — the revised wording is live in
`docs/site/privacy.md`.

**Where:** `docs/site/privacy.md`, "What this site does not do".

> **No accounts, no forms.** Nothing here accepts input, so nothing
> stores it.

`/today.html` ships `<form class="today-stream" action="today.html"
method="get">` containing 58 checkboxes. Nothing is submitted, nothing is
stored, and nothing leaves the browser — the claim's substance is intact
— but the sentence as written is now false, and it is the sentence a
reader would check first. Suggested wording:

> **No accounts, no data entry.** The live page's keyword filter is a
> plain HTML form whose state never leaves your browser: it is not
> submitted, not stored, and not readable by us. Nothing on this site
> collects, transmits, or retains anything you type or click.

This is a public-claim change and needs operator sign-off (§7).

### A11Y-20 — Low — CSS defects with accessibility bearing

**Status: resolved 2026-07-30** — all three: `var(--rule)` ->
`var(--border)`, the `.rule-note` selector split, and
`tag-status-planned`. Pinned by
`test_css_defects_found_by_the_audit_stay_fixed`.

**Where:** `publish._STYLE`.

Three latent defects found while auditing. None is an independent
conformance failure; all three make a remediation harder to verify.

1. `.today-disclosure { border: 1px solid var(--rule); … }` — `--rule` is
   **not defined** anywhere in the stylesheet, so the whole `border`
   declaration is invalid and dropped. The mandatory GUIDE §5 disclosure
   box has only its left rule. Fix: `var(--border)`.
2. `li.rule-note, li.source-note { font-size: 0.78rem; color: var(--muted); … }`
   — the selector requires an `<li>`, but `_today_item_row` and
   `_today_filter_bar` both emit `<span class="rule-note">`. Those spans
   get no styling and render at body size in `--fg`. (Contrast is fine;
   the visual hierarchy is not what the code intends.) Fix: split the
   `list-style: none` off and let `.rule-note, .source-note` carry the
   type styles.
3. `_STATUS_CHIPS` emits `tag-status-planned`, which has no rule in
   `_STYLE`. Planned sources render as plain chips. Cosmetic; noted so it
   is not mistaken for a deliberate difference.

---

### A11Y-21 — Medium — 1.3.1 Info and Relationships; 2.4.10 Section Headings

**Status: resolved 2026-09-05** — both sections gained the `<h3>`
subgroup heading the active/planned groups already had. Pinned by
`tests/test_accessibility.py::test_heading_levels_never_skip`, which
sweeps every built page class rather than this one.

**Where:** `publish._sources_body` — the "Unavailable sources" and
"Evaluated and excluded" sections.

Found 2026-09-05 by the new tier-1 sweep, on its first run, on a page
that had been live since 2026-08-03.

`_source_section` renders each source group as `h2` -> `h3`
(Active/Planned) -> `h4` (one per card). The two sections built outside
that helper appended their cards directly under the `h2`, so the heading
outline skipped a level for more than thirty consecutive cards. A screen
reader user navigating by heading — which is how a 175 KB page is read —
met a run of `h4`s under an `h2` with nothing explaining the jump, and
"unavailable" and "excluded" were never announced as the groupings they
are. The fix is the same subgroup heading the other groups carry, which
also gives each group a count in its own heading.

Not caught by the 2026-07-30 audit: heading structure was checked per
section rather than as a whole-document outline, and both sections are
far down a long page.

---

### A11Y-22 — Medium — 1.3.1 Info and Relationships; 2.1.1 Keyboard

**Status: resolved 2026-09-05** — the explanatory pages now render
through `_accessible_tables`, the same helper the digest and sources
pages use. Pinned by
`tests/test_accessibility.py::test_tables_keep_their_semantics`.

**Where:** `publish._build_doc_pages` — About, Methods, FAQ, Privacy,
Accessibility.

Also found by the tier-1 sweep on its first run. A11Y-03 gave the digest
pages scoped header cells and a focusable labelled scroll region for
wide tables; `_sources_body` was routed through the same helper on
2026-08-03. The doc pages went straight from `_MD.convert` to
`_render_page` and were the one page class that never met it, so their
markdown tables shipped bare `<th>` elements with no `scope` — including
the FAQ's three-column check-cycle table — and a wide table scrolled the
page rather than a labelled region a keyboard user can reach.

The lesson is the one the sweep was written for: a fix applied per page
class is a fix that a later page class silently misses. The test now
asserts the invariant across every page the build produces, so a new
page class inherits the requirement instead of having to remember it.

---

## 4. What is already right

Stated because a remediation pass should not undo any of it.

- **`display: none` filtering is correct.** Hidden `.today-item` elements
  leave the accessibility tree and the tab order together; no focusable
  link is left reachable inside a hidden entry. This is the property that
  makes the whole CSS-filter approach viable, and it holds.
- **The print rule is a genuine safeguard.** `@media print { .today-item
  { display: list-item !important } }` prevents a filtered subset from
  printing as if it were the whole day — the same disclosure instinct as
  the rest of the project, applied to presentation.
- **Colour is never the only carrier of branch.** Every branch chip's
  text is the branch name (`executive`, `judicial`, …). Verified across
  the entry chips, the filter bar, and the digest section summaries.
  (The *selected* state is a different matter — A11Y-06.)
- `lang="en"` on every page; a unique, specific, front-loaded `<title>`
  on every page; one `<h1>` per page.
- The viewport meta sets no `maximum-scale` and no `user-scalable=no`;
  pinch zoom works. `-webkit-text-size-adjust: 100%` does not block it.
- All type is sized in `rem`; 200% zoom and 320 px reflow both hold.
  `main { max-width: 46rem; padding: 1.2rem 1rem }` and
  `overflow-wrap: anywhere` on the long-string containers.
- `line-height: 1.6` on `body` already satisfies 1.4.12 Text Spacing; no
  fixed heights were found that would clip enlarged text.
- **No motion of any kind** — no animation, no transition, no
  `scroll-behavior: smooth`, no autoplay, no carousel. 2.2.2 Pause Stop
  Hide, 2.3.1 Three Flashes, and 2.3.3 Animation from Interactions are
  not applicable. If smooth scrolling is ever added it must be wrapped in
  `@media (prefers-reduced-motion: no-preference)`.
- **WCAG 2.2's other additions do not apply.** 2.5.7 Dragging Movements —
  no drag interaction exists. 3.3.7 Redundant Entry and 3.3.8 Accessible
  Authentication — no multi-step process, no login. 2.4.11 Focus Not
  Obscured — no sticky or fixed positioning anywhere in the stylesheet
  (verified: zero `position: sticky`, zero `position: fixed`).
- 3.2.3 Consistent Navigation holds: `_site_nav` emits the same links in
  the same relative order on every page and only omits the current page's
  own entry, which preserves relative order.
- The `.brand` link passes 2.5.3 Label in Name — visible text `FAPD`,
  accessible name `Free Agentic Publication Digester (FAPD)`.
- The sources page heading hierarchy (h1 → h2 group → h3 status → h4
  source name) is correct and complete, and its `<details>` cards hide
  only supplementary record detail, never a heading.

---

## 4a. Inline SVG charts — the standing pattern (added 2026-08-03)

The per-source pages carry small inline SVG charts (30-day request and
item bars, a response-time sparkline), generated by plain string
building in `publish.py` — no script, no external resource. The
accessibility contract for every such chart, present and future:

- **The SVG is decorative duplication, never the record.** It carries
  `aria-hidden="true" focusable="false"`; the accessible representation
  is a **visually-hidden `<table class="vh">`** beside it with one row
  per day, plus a visible `<figcaption>` stating the summary (total,
  peak, range) so sighted readers and AT users get the same headline.
- **One series per chart** (requests and items are separate charts, not
  a dual-axis pair); the figcaption names the series, so no legend is
  needed and identity never rides on colour.
- **Marks use the shared theme tokens** (`fill: var(--accent)`), so
  dark mode inherits correct ink; `@media (forced-colors: active)`
  re-inks marks in `CanvasText` (SVG fills are not force-adjusted by
  default), and `@media print` pins them to a dark grey so paper keeps
  the data.
- **Per-mark `<title>` children** give native hover values; they are a
  convenience layer only — the vh table is the guaranteed path.
- **An all-zero window renders prose, not an empty chart** — "nothing
  to chart" is stated, matching the project-wide explicit-absence rule.

---

## 5. Prioritized remediation plan

*Both phases have landed as of 2026-07-30 — phase 1 first, then phase 2
and A11Y-19 and the public statement together — except the `:has()`
restructure below, which was not done. Per-finding detail is on each
finding's **Status:** line in §3.*

### Phase 1 — do next (high value, low risk, no public-claim change)

Purely additive; each is testable and none changes page structure.

| Item | Change | Files |
|---|---|---|
| A11Y-01 | `aria-label` on the 58 filter inputs | `_today_filter_bar` |
| A11Y-02 | skip link in `_PAGE`, `id`/`tabindex` on `<main>`, in-page skip on `/today`, `.skip-link` CSS | `_PAGE`, `_STYLE`, `build_today` |
| A11Y-05 | `--accent-on`; darkened light branch hues; `.filter-n` opacity removed; `:checked` uses `var(--accent-on)` | `_STYLE`, `_today_filter_bar` |
| A11Y-06 | check-mark glyph on selected chips | `_today_filter_bar` |
| A11Y-08 | `@media (forced-colors: active)` block | `_STYLE` |
| A11Y-09 | chip vertical padding to reach 30.0 px | `_STYLE` |
| A11Y-10 | `--control-border`; `border-color: currentColor` on branch chips | `_STYLE` |
| A11Y-13 | `role="group"` replaces the `<nav>`; `aria-label="Site"` on the header nav; `<h2>` for the filter and the stream | `_PAGE`, `_today_filter_bar`, `build_today` |
| A11Y-14 | `<time>` and count labelling | `_today_item_row`, `_filter_chip` |
| A11Y-15 | CSS alt text on generated glyphs | `_STYLE` |
| A11Y-17 | site-wide `:focus-visible` | `_STYLE` |
| A11Y-20 | `var(--rule)` → `var(--border)`; `.rule-note` selector split | `_STYLE` |

**Verification for phase 1:** `uv run ruff check`, `uv run pytest -q`,
then rebuild the site and re-run the contrast computation to confirm the
measured ratios above. Add tests pinning (a) that every `filter-cb` input
carries a non-empty `aria-label`, (b) that `_PAGE` emits a skip link
whose `href` matches `<main>`'s `id`, (c) that no `<table>` remains
outside a `.table-scroll` wrapper once phase 2 lands. These are cheap
string assertions over rendered output and match the existing test
layering (§5 of code-standards).

### Phase 2 — structural (needs a rebuild and a manual AT pass)

- **A11Y-03** — table wrapper, `scope`, focusable scroll region.
- **A11Y-04** — headings into `<summary>`, anchor id onto the heading.
  This also repairs deep links into collapsed sections.
- **A11Y-11** — model-generated marker and inclusion-rule description as
  visually-hidden text. Land this *with* a screen-reader listen; it is
  the most verbose change proposed.
- **A11Y-12** — "(opens in a new tab)" in `_externalize_links`, with the
  widened regex. Note that code-standards §2 rule 9 names
  `_externalize_links` as the single enforcement point; this change stays
  inside it, so the rule is preserved and should be re-read, not amended.
- **A11Y-16** — link text on bare-date links.
- **A11Y-07 (a) and (b)** — the CSS-only status readout and the CSS
  counter. Ship the *visible* readout regardless; claim nothing about
  announcement until manual test 2 (§2) has been run.

**The `:has()` restructure.** Phase 2 is also the right moment to
consider replacing the sibling-combinator architecture. Today the
checkboxes must be siblings of both `.filter-bar` and `.today-list`,
which is what forces all 58 inputs to the top of the form and creates
A11Y-02's tab wall and A11Y-18's magnification gap. `:has()` removes the
constraint entirely:

```css
.today-stream:has(#f-executive:checked) .today-item:not(.k-executive)
  { display: none; }
.today-stream:has(#f-executive:checked) label[for="f-executive"]
  { background: var(--accent); color: var(--accent-on);
    border-color: var(--accent); }
.today-stream:has(#f-executive:checked) label[for="f-executive"]::before
  { content: "\2713\00a0" / ""; }
.today-stream:has(#f-executive:checked) .filter-clear
  { display: inline-block; }
#f-executive:focus-visible + label[for="f-executive"]
  { outline: 3px solid var(--accent); outline-offset: 2px; }
```

With that, each `<input>` can sit immediately before its own bar chip
inside a real `<fieldset><legend>Filter by keyword</legend>`, which
delivers: a named group for the checkboxes, focus adjacent to its
indicator, and the tab wall broken up by nothing more than the skip link.
`:has()` is Baseline as of December 2023; on an engine without it the
page degrades to **unfiltered**, which is the honest default state — the
whole day, never a silent subset. That degradation matters: it means the
change cannot produce a misleadingly partial view.

This is a real architectural change to the one interactive feature on the
site and should be proposed to the operator on its own, not folded into
an accessibility pass.

### Phase 3 — needs a decision, not just an edit

- **A11Y-19** — the privacy-page wording. Public claim; operator only.
- **The public accessibility page** (§6) — new site page, new nav entry,
  new published contact address. Operator only.
- **A11Y-18 / exact-count announcement** — if manual testing shows the
  CSS-only status region does not announce, the only remaining answer is
  a second inline script. Sketch, measured against code-standards §2 rule
  10: it would be inline (no external resource); make no network request;
  set no cookie and use no storage; be purely additive (the page filters
  correctly with it removed, exactly as today); and consist of one
  `change` listener on the form that writes a count into an existing,
  server-rendered `role="status"` element. It clears the bar on every
  clause. It nonetheless adds a second script to a site whose script
  count is currently a stated public property, and `docs/site/privacy.md`
  would have to be updated in the same commit. **That is an operator
  decision, and the recommendation here is to try phases 1–2 first and
  measure whether the gap is still real.**

### What can be applied without operator sign-off

All of phase 1 and all of phase 2 **except** the `:has()` restructure:
they are presentation-layer changes inside `publish.py`, they alter no
governing document, no public claim, and no editorial rule, and the
derived site is regenerable. They do change `site/*.html` output, so per
CLAUDE.md §8 the code commit and the regenerated-evidence commit stay
separate.

**Needs sign-off:** the `:has()` restructure (architecture of the one
interactive feature); A11Y-19 (public privacy claim); the accessibility
page and its published contact address; any new script (§2 rule 10 plus
the privacy page in the same commit).

**Governing-doc note.** None of phase 1 or 2 contradicts GUIDE or
code-standards. Two entries would be worth adding when the work lands:
a `docs/code-standards.md` §2 rule that presentation changes state their
success criterion and keep a measured contrast figure, and a
`CLAUDE.md` §9 entry recording that `.filter-cb`'s `opacity: 0` (rather
than `visibility: hidden`) is deliberate — it is the property that keeps
the checkbox announceable and focusable, and a future agent "tidying" it
to `display: none` would silently remove the filter from every keyboard
and screen-reader user.

---

## 6. Draft public accessibility statement

**Superseded 2026-07-30 by the real page.** The draft below states known
limitations as they stood **before** any remediation, and it required
revision in the same commit as the work it describes — which is what
happened. `docs/site/accessibility.md` now exists and differs from this
draft in several places, all in the direction of claiming less: it does
not claim conformance, it says plainly that no assistive technology has
yet been used on the site, and it says that the filter's readout is
something you can read rather than something you will be told, because
whether a CSS-revealed live region announces has not been measured. The
draft is kept here as written, unrevised, so the two can be compared.

```markdown
# Accessibility

The **Free Agentic Publication Digester (FAPD)** publishes the official
publications of the United States federal government. Everyone has the
same claim on that record, so this site is meant to work for people
using screen readers, screen magnification, voice control, switch access,
and keyboard-only navigation, and for readers with low vision or who need
to reduce what is on screen at once.

## The standard we hold ourselves to

**WCAG 2.2 Level AA is the floor, not the goal.** Where meeting AA would
still leave the site awkward to use, we aim past it and say so below.

Two structural choices help: the site is static HTML with no framework
and no external resources of any kind, and it carries exactly one small
script — on the live page, appending your local time beside each
published Eastern time. Everything else works with scripting off. There
is no login, no data entry, no timed content, no animation, and no
motion.

## What we have done

- One shared stylesheet with a light and a dark palette, both checked by
  measurement against the WCAG contrast thresholds.
- A skip link to the main content on every page, and a second skip past
  the keyword filters on the live page.
- The keyword filter on the live page is built from real HTML checkboxes,
  so it is operable from the keyboard, announces its state, and can be
  cleared with a single native button.
- Filtering hides items in a way that removes them from assistive
  technology and from the tab order together — a hidden item is hidden
  consistently, never left half-present.
- Printing the live page always prints the whole day, never the filtered
  subset, so a printed page can never read as the complete record when it
  is not.
- Branch of government, document type, and agency are conveyed in words
  on every item. Colour is a second signal, never the only one.
- Links that leave this site are marked as opening in a new tab.
- Digest sections carry real headings, so screen reader and
  keyboard users can move through a day by heading.
- Tables carry header-cell relationships and can be scrolled from the
  keyboard.
- The site is usable at 400% zoom and at a 320-pixel-wide viewport.

## Known limitations

We would rather name these than let you find them.

- **The live page is large.** A busy publication day puts several hundred
  items and around sixty keyword filters on one page. Even with the skip
  links, moving through it by keyboard takes time. We are looking at
  grouping the filters more usefully rather than at hiding items behind
  pagination, because a paginated day is a less honest day.
- **Filtering does not announce its result.** Selecting a keyword changes
  what is on the page, and we do not yet reliably tell a screen reader
  how many items remain. We show it visually; making the announcement
  dependable would require adding a second script, which we have not
  decided to do.
- **Focus and magnification on the filter.** At high magnification the
  focus indicator on a filter chip may sit outside your view. This is a
  known consequence of how the filter is built without script and we are
  working on it.
- **We have not yet completed a full manual test with every assistive
  technology.** The site has been audited by inspection and by
  measurement. Testing with NVDA, JAWS, and VoiceOver is planned and its
  results will be published here.

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

Every digest also exists as plain Markdown in the project's repository,
and the same data is published as JSON (`/digests.json`, `/today.json`)
and as an Atom feed (`/feed.xml`). If the HTML is not working for you,
those may be easier to read or to hand to a tool of your choosing.

*Last reviewed: [date]. This statement describes the site as it stands,
including what is not fixed yet.*
```

---

## 7. Open questions for the operator

*Answered 2026-07-30 where marked. The questions themselves are kept as
asked; the answers are appended, not substituted for them.*

1. **The `:has()` restructure (§5, phase 2).** Rebuilding the filter on
   `:has()` fixes the tab wall, the missing group label, and the
   magnification gap together, and degrades to "show everything" on older
   engines. It is also a rewrite of the one interactive feature on the
   site. Worth doing, or is the phase-1 patch enough for now?
   **Answered 2026-07-30: not now** — too large a change to fold into an
   accessibility pass, and it carries browser-support consequences. Still
   open as its own proposal; A11Y-18 stays open with it.
2. **A11Y-12 verbosity.** "(opens in a new tab)" on 582 links per live
   page is conventional and satisfies the technique. Is that acceptable,
   or do you want a single page-level statement instead, accepting that
   it does not meet G201?
   **Answered 2026-07-30: per-link, sitewide.** The verbosity is named on
   the public statement as a known limitation, with an invitation to say
   if it is too much — the question is not treated as settled, it is
   published.
3. **A11Y-11 verbosity.** Restoring the inclusion-rule description as
   audible text adds 104 spoken phrases to a digest page. The alternative
   is leaving the project's core accountability claim in a
   pointer-only tooltip. Which way?
   **Answered 2026-07-30: restore it**, on the same terms as question 2.
4. **Publishing a contact address.** The accessibility statement needs a
   reachable address. `docs/site/privacy.md` currently says the contact
   address "appears in every request our crawler makes and in the
   repository metadata" — it is not on the site. Publishing
   hustleyourcity@gmail.com on an accessibility page is a change to the
   site's contact posture, and would also engage 3.2.6 Consistent Help
   (the link must appear in the same relative order in the nav on every
   page — `_site_nav` already does this).
   **Answered 2026-07-30: publish it.** `hustleyourcity@gmail.com`, the
   address already in `SECURITY.md`, is on the statement.
5. **A11Y-19.** Approve the revised "No accounts, no forms" wording, or
   supply your own?
   **Answered 2026-07-30: approved as drafted**, and live in
   `docs/site/privacy.md`.
6. **Publishing `/<date>.md`.** The statement's "Alternatives" section
   points at the canonical Markdown, which currently lives only in a
   private repository. Should `publish.build_site` copy the Markdown
   beside each HTML digest? It costs nothing, it is genuinely the easiest
   form for some readers, and it removes a claim we cannot presently
   support.
   **Still open 2026-07-30** — it changes what the site publishes, which
   is an operator call. The statement's Alternatives section points at
   the repository copy, matching what `/agents.html` already says, rather
   than at a file the site does not serve.
7. **Minimum type size (beyond baseline).** Chips are 11.5 px and notes
   12.5 px. Both pass every AA criterion and both are small for the
   information they carry — the chips are the filter controls. Raising
   `.tag` to 0.8rem (12.8 px) and the notes to 0.875rem (14 px) would
   change the visual density of every page. Worth it?
   **Still open 2026-07-30** — left unchanged. Both sizes pass AA, so
   this is an aesthetic call on every page, not a conformance one.
8. **`aria-current="page"`.** `_site_nav` omits the current page's own
   link. That is valid and preserves consistent ordering, but a rendered
   link marked `aria-current="page"` gives better orientation, especially
   for screen reader users arriving mid-site. Change, or leave?
   **Answered 2026-07-30: change.** Every page now renders every nav
   link, in identical order, with its own marked `aria-current="page"`.
   Pinned by `test_nav_marks_the_current_page_instead_of_dropping_it`.
9. **Who runs the manual tests in §2?** The three test classes need a
   human with the actual assistive technology. If that is not available
   in-house, the honest options are to hire it before the launch
   checklist clears, or to publish the statement with the
   "not yet fully tested" limitation stated plainly. The second is
   acceptable; silently omitting it is not.
   **Answered 2026-07-30: the second, for now.** The public statement's
   first known limitation is that no assistive technology has been used
   on this site, and it names the specific pairings still owed. Who runs
   them, and when, remains an operator decision.

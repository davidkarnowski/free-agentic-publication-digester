# Built to Be Reachable

*Dev notes, 2026-09-05. Written by Claude, with direction from the
project's founder. On the principle that a public record has to be
reachable by everyone who has a claim on it — and on why the same
decisions that make a page reachable are the ones that make it safe.*

The Free Agentic Publication Digester publishes what the United States
federal government published. That is the whole product: the
Congressional Record, the Federal Register, enacted laws, court
opinions, agency releases — selected by mechanical rules, cited to the
official source, and frozen at the end of each publication day.

A record that a person cannot reach has not been published to that
person. Not in any sense that matters to them. Someone reading with a
screen reader, someone running the screen at four hundred percent,
someone navigating by voice, someone driving a browser with a switch or
a head pointer, someone who simply never uses a mouse — each of them has
exactly the same claim on the Federal Register as anyone else. If our
presentation is what stands between them and it, then we have taken a
public record and made it private to the people whose bodies and
equipment happen to match our assumptions.

So access is not a feature on our roadmap. It is an editorial
obligation, and as of today it is written into the project's governing
document alongside the rules about citation and provenance, where it
binds every change we make from here.

## Three readerships, one artifact

This project has always been explicit about serving two audiences:
people and AI agents. Working on access made us realize that framing was
one short.

There are three readerships — people reading in a browser, people
reading through assistive technology, and software reading
programmatically — and they are not three problems. They are one
problem, and it has one answer: **put the meaning in the markup.**

A heading that is a heading, not a bold paragraph. A table with a
caption that names it and column headers that scope. A link whose
purpose survives being read out of context, because a screen reader
lists links out of context. A label that says what a control does rather
than relying on where it sits. State that lives in the document instead
of in a script's memory.

Every one of those decisions is simultaneously an accessibility
decision, a semantics decision, and a machine-readability decision. The
structure that lets a screen reader announce our archive is the same
structure that lets a crawler enumerate it. We do not maintain an
accessible version and a normal version, or a human site and a machine
API. There is one artifact, built once, correctly, and the same care
serves all three readerships at the same time.

## The most secure page is often the most reachable one

Here is a convergence we did not expect and now treat as doctrine.

The site is static HTML. No framework. No build-time JavaScript
toolchain shipped to your browser. No third-party fonts, no analytics,
no content delivery network, no embedded players, no trackers. Exactly
one small script exists on the entire site, on the live in-progress
page, and it adds your local time beside our published Eastern time —
everything works with scripting switched off.

The site accepts no input. There is no login, no search box that queries
a server, no form that submits, no comment field, no API endpoint of our
own that takes a parameter.

We adopted those constraints for reachability. A control that requires
JavaScript to operate is a control that fails for some assistive
technology, and custom date pickers and dropdown widgets are among the
most reliably broken things on the web for exactly that reason. A page
that works with scripting off works everywhere — on a decade-old
browser, on a text browser, through a proxy, on a bad connection, inside
a screen reader's own rendering.

But run the same constraints through a security lens and you get the
same list. A page with no script has nothing to inject. A page with no
endpoint has nothing to exploit. A page that accepts no input cannot
leak what it was given, because it was never given anything. A page that
loads no third-party asset cannot be compromised by a third party's bad
day, and cannot report you to anyone.

Access and attack surface turn out to be the same measurement taken from
two directions. We are keeping both justifications written down, because
a rule with two independent reasons is a rule nobody will quietly trade
away later for convenience.

## How we actually design it

We work down a ladder, in order, and we stop at the first rung that
does the job.

Semantic HTML first. Then a native element — a real link, a real
checkbox, a real disclosure — because browsers and assistive technology
have spent thirty years agreeing on what those mean. Then, only where no
native element exists, an interaction built from HTML and CSS alone. A
scripted widget is not on the ladder.

The live page's keyword filter is the worked example: it is ordinary
checkboxes and a stylesheet, with a native reset button that clears
every selection at once. The digest archive is the newest one. Rather
than a date picker, earlier days are reached through month calendars in
which every published day is an ordinary link — nothing to learn,
nothing to trigger, nothing that behaves differently for you than it
does for us.

And we design against named modalities rather than a general good
intention, because "accessible" without a list quietly collapses into
"the keyboard works." The list is written down: screen readers, screen
magnification, voice control, switch access and scanning, head pointers
and eye gaze, keyboard-only navigation, forced-colors and high-contrast
modes, reduced motion, and readers for whom holding state in working
memory is the barrier.

Each one has a concrete design consequence. Voice control means the
visible text of a control has to be the beginning of its spoken name, so
that saying what you see actually works. Switch access and head pointers
mean targets are sized generously — the calendar's day cells are built
to the enhanced 44-pixel standard rather than the minimum, with real
spacing between them, because a target that is merely legal to hit is
not the same as a target that is comfortable to hit forty times.
Magnification means content reflows down to a narrow viewport without a
horizontal scrollbar, and where those two pull against each other the
cells take a share of the width they are given rather than a fixed
number of pixels, so both hold at once. Forced-colors means we declare how our elements
behave there instead of hoping.

## Measured, not eyeballed

Color contrast on this site is computed, not judged. Ratios come from
the declared color values through the standard relative-luminance
formula, with translucent fills composited over their real backgrounds
first, and they are computed for both the light and the dark palette.
Target sizes are computed from the actual box — font size, line height,
padding, border — rather than estimated from a screenshot. The numbers
live in the repository where anyone can check our arithmetic, which is
the same standard we hold ourselves to for every figure we publish about
our own ingestion.

That habit caught something while we were designing the archive. The
obvious border color for a calendar day would have been the one the site
already uses for dividing rules. Computed, it sits at 1.34 to 1 against
the page — fine for a decorative line, well under the 3 to 1 that a
control's boundary needs. We used the control border instead, at 3.22 to
1 in light and 3.61 to 1 in dark. Nobody would have caught that by
looking.

## Making it binding

A principle that is not enforced is decoration, and this project has a
consistent way of preventing that: a rule goes into the governing
document, the code implements it, a test pins it, and an audit records
what was measured and when.

Accessibility now runs that same ladder. There is a constitutional
section stating what we owe every reader. There is a doctrine document
stating how we comply — the design ladder, the modality list, the
measurement method, the reusable patterns. There is a rule for new code,
so that a new page cannot ship without an accessible name, an adequate
target, and a test. And there is a permanent findings register where
every accessibility identifier we have ever opened stays visible with
its status, because deleting a resolved finding erases the evidence that
we found it.

We build to WCAG 2.2 Level AA as a floor rather than a target, and we go
past it where going past it is cheap and matters to somebody — as with
those target sizes.

## Tell us what is broken

If something on this site does not work for you, email
**hustleyourcity@gmail.com** with the page address and what happened. A
description in your own words is enough. You do not need to identify a
cause, name a standard, or know why it went wrong.

Accessibility reports are handled exactly like factual corrections to a
digest: they go on the record and they get fixed. That is not a
courtesy. A person telling us they cannot reach the federal record
through our site is reporting a defect in the product, and it is the
most important kind of defect this project can have.

Every digest is also published as plain Markdown in the public
repository, and the machine surfaces — `/llms.txt`, `/digests.json`, the
Atom feed, the per-day JSON — carry the same content in formats that do
not depend on our styling at all. Those exist for AI agents. They work
just as well as an escape hatch for a person whose tools disagree with
our presentation, and we count that as part of the same commitment.

The official record belongs to everyone. Publishing it is only half of
the job; the other half is making sure that "everyone" was not a figure
of speech.
